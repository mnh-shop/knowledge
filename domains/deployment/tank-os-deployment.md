---
name: tank-os-deployment
tags: [bootc, container, deployment, desktop, fedora, image-based, immutable-os, mcp, podman, quadlet, systemd, tank-os, virtualization]
description: Tank OS Deployment — Fedora 44 bootc image, OpenShell sandbox, KubeVirt containerDisk, secrets, updates
source: sources/tank-os/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Tank OS Deployment

This guide covers building, deploying, and managing a Tank OS instance — a Fedora 44 bootc appliance running OpenClaw as a rootless Podman workload with NVIDIA OpenShell sandboxing.

## Prerequisites

- **Podman** installed (4.x or later; rootful machine required on macOS for disk-image builds)
- **make** available
- **qemu-img** and **QEMU** (for local testing on macOS)
- **bootc-image-builder** (for QCOW2/ISO builds — run via the Makefile's container invocation)
- **cosign** (optional, for image verification)
- A container registry account (optional, for pushing images)

## Quick Start

### 1. Build the Derived OpenClaw+OpenShell Image First

The gateway container runs a derived image (OpenClaw + the `openshell` CLI + an SSH client), published to `quay.io/redhat-et/tank-claw-openshell:2026.7.1`. It must exist before the main image builds:

```bash
make build-openclaw-openshell
make push-openclaw-openshell      # publish to IMAGE_OPENCLAW_OPENSHELL_URI
```

### 2. Build the Image

```bash
cd sources/tank-os

# Build for host architecture
make build

# Build for a specific architecture
make build ARCH=arm64

# Build with a custom registry
IMAGE_REGISTRY=quay.io IMAGE_NAMESPACE=myuser make build
```

The `Makefile` auto-detects architecture: `x86_64` -> `amd64`, `aarch64` -> `arm64`. The base is **pinned to `quay.io/fedora/fedora-bootc:44`** (OpenShell RPMs are only published for `fc44`), and `OPENCLAW_REF`/`OPENSHELL_VERSION` (2026.7.1 / 0.0.92) are the single points of control for both Containerfiles.

### 3. Build a Bootable Disk Image

Produce a QCOW2 disk image for VM deployment:

```bash
make build-qcow2
```

This runs `bootc-image-builder` (`quay.io/centos-bootc/bootc-image-builder:latest`) in a privileged container with `--type qcow2` and `--rootfs xfs`. Output is written to `out-tank-os/qcow2/disk.qcow2`. For an ISO installer instead:

```bash
make build-iso
```

For KubeVirt/OpenShift Virtualization, wrap the qcow2 as a containerDisk:

```bash
make build-containerdisk        # quay.io/redhat-et/tank-os-containerdisk:latest
make push-containerdisk-arch    # push under an arch tag for safe multi-arch merging
```

On macOS the disk-image targets require a **rootful** Podman machine (`podman machine set --rootful`); on a bare Linux host run `sudo make build && sudo make build-qcow2` (rootless and rootful Podman keep separate image storage).

### 4. Push to Registry

```bash
IMAGE_REGISTRY=quay.io IMAGE_NAMESPACE=myuser make push
```

### 5. Deploy on a Server

On a target machine (bare metal or VM), switch to the registry-hosted image:

```bash
sudo bootc switch --apply quay.io/sallyom/tank-os:latest    # legacy namespace (README.md)
sudo bootc switch --apply quay.io/redhat-et/tank-os:latest  # current namespace (docs/build.md)
```

This downloads the image, creates a new deployment, and activates it on the next reboot. The repo is mid-namespace-migration (`sallyom` → `redhat-et`); the docs now publish to `quay.io/redhat-et/tank-os`.

## Secret Configuration

Secrets are managed via rootless Podman secrets — they are NOT baked into the image. On first boot, after the services start, inject secrets:

```bash
# SSH into the VM
ssh openclaw@<vm-ip>

# Inject secrets (runs as openclaw via sudo delegation)
tank-openclaw-secrets
```

`tank-openclaw-secrets` delegates into `sync-podman-secrets`, which:
1. Scans for existing Podman secrets (7 OpenClaw + 4 service-gator names)
2. Writes Quadlet drop-in files (`openclaw.container.d/10-secrets.conf`, `service-gator.container.d/10-secrets.conf`) mounting each detected secret
3. Rewrites `~/.openclaw/openclaw.json` — model-provider allowlist, primary model preference, provider `baseUrl`/`api` backfill, and the Telegram channel `botToken`
4. Reloads systemd user units

Secrets must be created before running `tank-openclaw-secrets`:

```bash
# OpenClaw (7): anthropic_api_key, openai_api_key, gemini_api_key, google_api_key,
#               openrouter_api_key, model_endpoint_api_key, telegram_bot_token
echo -n "sk-ant-..." | podman secret create anthropic_api_key -

# Service-gator (4): gh_token, gitlab_token, forgejo_token, jira_api_token
echo -n "ghp_..." | podman secret create gh_token -
```

## OpenShell Sandbox Architecture

OpenClaw's tool calls are sandboxed by NVIDIA OpenShell (`agents.defaults.sandbox.backend: "openshell"`), replacing OpenClaw's built-in Docker sandbox:

- **`openshell-gateway`** — runs on the VM host as a rootless systemd *user* service under `openclaw` (unit ships inside the `openshell-gateway` RPM). Creates and manages sandbox containers via the user's rootless Podman; binds loopback-only (`https://127.0.0.1:17670`).
- **`openshell` CLI** — lives inside the derived OpenClaw container (`tank-claw-openshell`); the OpenClaw plugin shells out to it and SSHes into the sandbox.
- **Sandbox** — pre-created as `tankos-openclaw` by `bootstrap-openshell-sandbox` (ExecStartPre), from a digest-pinned `ghcr.io/lobstertrap/openshell-hummingbird-images/sandboxes/openclaw` image.
- **First boot**: `bootstrap-openclaw` writes `openclaw.json` (gateway token, sandbox config, plugin entry) → `bootstrap-openshell-sandbox` installs `@openclaw/openshell-sandbox` into the persisted volume, registers the gateway, pre-creates the sandbox. Both idempotent; upgrades backfill the sandbox/plugin config in place.

This is why `openclaw.container` runs with **`Network=host`** — the CLI must reach the host gateway on loopback. Known limitation: the sandbox's OPA network supervisor needs `CAP_SYS_PTRACE`, which rootless Podman doesn't grant by default (verify egress denial on real hardware/OpenShift before relying on it).

## SSH Tunnel for Service Access

With `Network=host`, the OpenClaw gateway binds the host's loopback directly (ports 18789/18790); only service-gator publishes a mapped port (`PublishPort=127.0.0.1:8080:8080`). Access services via SSH tunnel:

```bash
# OpenClaw gateway (port 18789) + dashboard/streaming (18790)
ssh -N -L 18789:127.0.0.1:18789 -L 18790:127.0.0.1:18790 openclaw@<vm-ip>

# Service-gator MCP proxy (port 8080)
ssh -N -L 8080:127.0.0.1:8080 openclaw@<vm-ip>
```

## Updates

Transactional updates via bootc:

```bash
# Upgrade to latest published image
sudo bootc upgrade --apply

# Switch to a specific version
sudo bootc switch --apply quay.io/redhat-et/tank-os:v1.2.3

# Rollback to previous deployment
sudo bootc rollback
```

Both `upgrade` and `switch` stage the new deployment and activate it on next reboot. bootc automatically rolls back if the new deployment fails to boot.

## macOS Local Testing

Full workflow for testing on macOS with QEMU:

```bash
# 1. Build derived image + main image for ARM64
make build-openclaw-openshell ARCH=arm64
make build ARCH=arm64

# 2. Build QCOW2 (requires rootful Podman machine)
make build-qcow2

# 3. Resize the disk
qemu-img resize out-tank-os/qcow2/disk.qcow2 20G

# 4. Launch QEMU (install edk2-aarch64-code.fd via Homebrew first)
qemu-system-aarch64 \
  -machine virt,highmem=on \
  -accel hvf \
  -cpu host \
  -smp 4 \
  -m 4096 \
  -drive file=out-tank-os/qcow2/disk.qcow2,format=qcow2,if=virtio \
  -drive if=pflash,format=raw,readonly=on,file=/opt/homebrew/share/qemu/edk2-aarch64-code.fd \
  -drive if=pflash,format=raw,file=out-tank-os/qcow2/edk2-arm-vars.fd \
  -device virtio-net-pci,netdev=net0 \
  -netdev user,id=net0,hostfwd=tcp::2222-:22 \
  -nographic

# 5. SSH tunnel + open browser
ssh -N -L 18789:127.0.0.1:18789 -L 18790:127.0.0.1:18790 openclaw@localhost -p 2222
open http://127.0.0.1:18789
```

Alternatives: Lima configs (`examples/lima/tank-os-qemu.yaml`, `tank-os-krunkit.yaml`, `tank-os-vz.yaml`) boot a disk extracted from the containerDisk image — no Lima guest agent, works on macOS and Linux. First boot of `openclaw.service` pulls the derived image + sandbox image (several minutes); `TimeoutStartSec=900` covers it, and `systemctl --user start openclaw.service` may be needed once on first boot.

### UTM Alternative

For UTM on macOS, create a NoCloud seed ISO for cloud-init:

```bash
hdiutil makehybrid -o seed.iso -hfs -joliet -iso -default-volume-name cidata /path/to/user-data /path/to/meta-data
```

The cloud-init config at `sources/tank-os/examples/cloud-init/openclaw-user-data.yaml` creates the `openclaw` user with `wheel` group membership, passwordless sudo, locked password, SSH authorized keys, and `loginctl enable-linger`.

## OpenShift Virtualization (KubeVirt)

tank-os ships a per-user VM path under `deploy/`:

- `deploy/containerdisk/Containerfile` — wraps `out-tank-os/qcow2/disk.qcow2` as `/disk/disk.qcow2` (KubeVirt containerDisk convention)
- `deploy/base/virtualmachine.yaml` — KubeVirt `VirtualMachine` template (2 cores, 4Gi, virtio containerDisk + cloudInitNoCloud, masquerade pod network)
- `deploy/applicationset.yaml` — ArgoCD ApplicationSet (goTemplate engine, list generator): one entry per user → one Application syncing the Kustomize base with a per-user name/labels/hostname/userData patch into a `tank-<user>` namespace
- `qemu-guest-agent` is baked into the image for hypervisor integration

Build the containerDisk with `make build-qcow2 build-containerdisk`, then publish multi-arch with `make push-containerdisk-arch` per architecture and `podman manifest create`/`push --all`.

## Image Verification

Verify image signatures with cosign:

```bash
COSIGN_PUBLIC_KEY=/path/to/cosign.pub make verify
```

The Makefile uses a trap-based cleanup mechanism for the cosign public key.

## Managing Services

SSH into the VM and manage the rootless Podman services:

```bash
# Check service status
sudo -u openclaw XDG_RUNTIME_DIR=/run/user/1000 systemctl --user status openclaw
sudo -u openclaw XDG_RUNTIME_DIR=/run/user/1000 systemctl --user status service-gator
sudo -u openclaw XDG_RUNTIME_DIR=/run/user/1000 systemctl --user status openshell-gateway

# View logs
sudo -u openclaw XDG_RUNTIME_DIR=/run/user/1000 journalctl --user -u openclaw -f

# Restart a service
sudo -u openclaw XDG_RUNTIME_DIR=/run/user/1000 systemctl --user restart openclaw
```

Verify the sandbox is wired in: `podman exec openclaw openclaw sandbox explain` should report `backend: openshell`, `runtime: sandboxed`.

## Build-Time Configuration

For `bootc-image-builder`, provisioning is done via `bootc-config.toml` (see `examples/bootc-config.toml`):

```toml
[[users]]
name = "openclaw"
groups = ["wheel"]
ssh_authorized_keys = ["ssh-ed25519 AAAA..."]
```

## Related

- [[tank-os]] -- Wiki overview of the Tank OS project
- [[secureblue-deployment]] -- Sibling hardened Fedora bootc image family
- [[openclaw-deployment]] -- OpenClaw gateway deployment details
- [[quadlet-patterns]] -- General Quadlet deployment patterns
- [[tank-os-architecture]] -- Architecture overview
- [[tank-os-quadlet]] -- Quadlet file reference
