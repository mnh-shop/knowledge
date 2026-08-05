---
name: tank-os
tags: [bootc, cli, container, dashboard, deployment, fedora, git, image-based, immutable-os, mcp, podman, quadlet, systemd, tank-os, virtualization, wiki]
description: Tank OS — Fedora Bootc Image for OpenClaw
source: sources/tank-os/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Tank OS — Fedora Bootc Image for OpenClaw

| Field | Value |
|---|---|
| **Origin** | [LobsterTrap/tank-os](https://github.com/LobsterTrap/tank-os) |
| **License** | MIT (`LICENSE:1`) |
| **Stack** | Bootc (container→bootable OS), Fedora 44 (pinned), Rootless Podman, Quadlet, NVIDIA OpenShell sandboxing |
| **Source** | `sources/tank-os/` |
| **Wanted** | Bootable Linux appliance running OpenClaw as rootless Podman |

## What it is

tank-os turns [[openclaw]] into a **bootable Linux appliance** using [bootc](https://bootc-dev.github.io/bootc/). bootc packages Fedora + rootless OpenClaw service + Quadlet units into one OCI container image that can be built into VM disks, QCOW2, or ISO images. The result: a machine that boots into a running OpenClaw gateway with zero manual OS setup.

This is an exemplar of the [[deployment-architecture]] pattern: the host OS plus agent stack travel together as one deployable, updateable, rollbackable unit.

## Containerfile Details

Based on `quay.io/fedora/fedora-bootc:44` — **pinned to Fedora 44, not `latest`**, because the OpenShell RPM filenames are hardcoded to the `fc44` build (the only Fedora release OpenShell currently publishes RPMs for) (`bootc/Containerfile:1-6`). The image is marked with `LABEL containers.bootc=1` (`bootc/Containerfile:8`).

### Packages Installed

10 packages installed via dnf (`bootc/Containerfile:34-44`):

```
cloud-init          — First-boot initialization (SSH keys, user-data)
curl                — Download tooling (OpenShell RPMs at build time)
openssh-server      — SSH daemon for remote access
podman              — Rootless container runtime
python3             — Config-rewrite engine for sync-podman-secrets / bootstrap scripts
qemu-guest-agent    — VM guest agent for hypervisor integration (KubeVirt, QEMU)
shadow-utils        — useradd/groupadd for the openclaw user + subuid/subgid
sudo                — Passwordless sudo for the openclaw user
vim-enhanced        — Basic editor
```

Plus **NVIDIA OpenShell RPMs** (`openshell` + `openshell-gateway`, version `0.0.92`) downloaded from GitHub releases and **checksum-verified** against the published `openshell-checksums-sha256.txt` before install (`bootc/Containerfile:45-54`).

### Derived OpenClaw Image

The gateway no longer runs the stock OpenClaw image. A derived image — **OpenClaw + the `openshell` CLI + an SSH client**, published to `quay.io/redhat-et/tank-claw-openshell:2026.7.1` — is built first (`bootc/openclaw-openshell/Containerfile:15-44`, `make build-openclaw-openshell`), and the main image's Quadlet `Image=` line is rewritten to it at build time via sed (`bootc/Containerfile:28,82-83`). Pinned to `OPENCLAW_REF=2026.7.1` (fixes CVE-2026-27002 and the sandbox bind-mount escape chain; 2026.7.2 exists but is still beta).

### User Setup

- Creates `openclaw` user (UID/GID 1000, matching the OpenClaw container's `node` user), home at `/var/home/openclaw` (`bootc/Containerfile:57-59`)
- Sets up passwordless sudo via `/etc/sudoers.d/openclaw`
- Allocates **subuid/subgid ranges** `100000-65536` for rootless Podman (`bootc/Containerfile:61-64`)
- Enables **linger** for the user so rootless systemd services start at boot (`bootc/Containerfile:66-67`)

### Quadlet Files

Two systemd user services defined as Quadlet `.container` files in `/etc/containers/systemd/users/1000/`:

#### `openclaw.container`

```ini
[Unit]
Description=OpenClaw gateway (rootless Podman)
After=openshell-gateway.service
Wants=openshell-gateway.service

[Container]
Image=ghcr.io/openclaw/openclaw:latest   # rewritten at build → quay.io/redhat-et/tank-claw-openshell:2026.7.1
ContainerName=openclaw
Pull=newer
RunInit=true
UserNS=keep-id
Network=host
User=%U:%G
Volume=%h/.openclaw:/home/node/.openclaw:Z
Environment=HOME=/home/node
Environment=TERM=xterm-256color
Environment=NPM_CONFIG_CACHE=/home/node/.openclaw/.npm
Environment=OPENCLAW_NO_RESPAWN=1
EnvironmentFile=%h/.openclaw/openclaw.env
Exec=node dist/index.js gateway --allow-unconfigured --bind lan --port 18789

[Service]
ExecStartPre=/usr/libexec/tank-os/bootstrap-openclaw
ExecStartPre=/usr/libexec/tank-os/bootstrap-openshell-sandbox
TimeoutStartSec=900
Restart=on-failure

[Install]
WantedBy=default.target
```

Key Quadlet patterns (`bootc/rootfs/etc/containers/systemd/users/1000/openclaw.container`):
- **`Network=host`** — required so the `openshell` CLI inside the container can reach the host-side `openshell-gateway` at `https://127.0.0.1:17670` (a container-namespaced network can't see the host loopback). Trade-off documented in `docs/openshell.md`: the OpenClaw container gets the host network namespace, but untrusted tool-call code is sandboxed by OpenShell inside the sandbox container instead.
- `UserNS=keep-id` + `User=%U:%G` — maps host UID 1000 into the container (avoids file permission issues with mounted volumes)
- `Volume=%h/.openclaw:...:Z` — persistent OpenClaw state under the user's home, SELinux-relabeled
- `Pull=newer` — auto-updates container image on restart
- **Two `ExecStartPre` bootstrap scripts**: `bootstrap-openclaw` (writes `openclaw.json` + gateway token) and `bootstrap-openshell-sandbox` (installs the OpenShell plugin, registers the gateway, pre-creates the sandbox)
- `TimeoutStartSec=900` — generous timeout for first-boot image/sandbox pulls
- `After=openshell-gateway.service` — the sandbox gateway must be up first

#### `service-gator.container`

```ini
[Unit]
Description=service-gator scoped service MCP server (rootless Podman)
After=network-online.target

[Container]
Image=ghcr.io/cgwalters/service-gator:latest
ContainerName=service-gator
Pull=newer
RunInit=true
Volume=%h/.config/service-gator:/etc/service-gator:Z
Volume=%h/.openclaw:/workspaces:Z
Environment=GH_TOKEN_FILE=/run/secrets/gh_token
Environment=GITLAB_TOKEN_FILE=/run/secrets/gitlab_token
Environment=FORGEJO_TOKEN_FILE=/run/secrets/forgejo_token
Environment=JIRA_API_TOKEN_FILE=/run/secrets/jira_api_token
PublishPort=127.0.0.1:8080:8080
Exec=--mcp-server 0.0.0.0:8080 --scope-file /etc/service-gator/scopes.json

[Service]
ExecStartPre=/usr/libexec/tank-os/bootstrap-service-gator
TimeoutStartSec=300
Restart=on-failure

[Install]
WantedBy=default.target
```

Note: **only `service-gator` binds to loopback** (`PublishPort=127.0.0.1:8080:8080`). `openclaw` runs with `Network=host`, so the old "all ports bind to 127.0.0.1" claim applies only to service-gator (and to the OpenShell gateway, which binds loopback-only by design). `service-gator` mounts scoped token files via `Environment=*_TOKEN_FILE=/run/secrets/...` and has its own `bootstrap-service-gator` ExecStartPre that writes a default `scopes.json`.

### CLI Integration

A host-level `openclaw` command delegates into the running container — but it is now a **sudo-delegating wrapper** (`bootc/rootfs/usr/local/bin/openclaw`):

- Runs as the `openclaw` user if invoked by that user; otherwise re-executes via `sudo -iu openclaw` (so any admin user can use it)
- Supports a `--container` flag (`--container NAME` or `--container=NAME`) to target a differently-named container; `OPENCLAW_CONTAINER` env var overrides the default
- Checks the container is actually running (`podman inspect ... .State.Running`) before delegating, with a hint to start `openclaw.service`
- Executes the container's own `openclaw` binary: `podman exec [-it] <container> openclaw "$@"`

From the host shell you run `openclaw gateway status --deep`, `openclaw doctor`, `openclaw dashboard --no-open` etc. and it executes inside the container.

### Secret Management

API keys are stored in rootless Podman secrets (never baked into the image). **7 OpenClaw secrets** and **4 service-gator secrets** are supported:

```bash
# Create a secret (as the openclaw user)
printf '%s' "$ANTHROPIC_API_KEY" | podman secret create anthropic_api_key -

# Regenerate Quadlet drop-ins + rewrite openclaw.json
tank-openclaw-secrets    # sudo-delegating wrapper → sync-podman-secrets

# Restart services
systemctl --user restart openclaw.service service-gator.service
```

OpenClaw secret names: `anthropic_api_key`, `openai_api_key`, `gemini_api_key`, `google_api_key`, `openrouter_api_key`, `model_endpoint_api_key`, `telegram_bot_token`.

Service-gator secret names: `gh_token`, `gitlab_token`, `forgejo_token`, `jira_api_token`.

`sync-podman-secrets` (`bootc/rootfs/usr/libexec/tank-os/sync-podman-secrets`) does two jobs:
1. **Writes Quadlet drop-ins** (`~/.config/containers/systemd/openclaw.container.d/10-secrets.conf` and `service-gator.container.d/10-secrets.conf`) mounting each detected secret as `Secret=<name>,type=env,target=<ENV>`.
2. **Rewrites `~/.openclaw/openclaw.json`** via an embedded python3 script (`sync-podman-secrets:65-211`): builds the model-provider allowlist (`anthropic/claude-sonnet-4-6`, `openai/gpt-5.4`, `google/gemini-3.1-pro-preview`, `openrouter/google/gemma-4-26b-a4b-it`), picks the primary model by preference order, backfills provider `baseUrl`/`api` (anthropic, openai, google, openrouter), and wires the Telegram channel `botToken` when `telegram_bot_token` is present.

## NVIDIA OpenShell Integration

tank-os uses [NVIDIA OpenShell](https://github.com/NVIDIA/OpenShell) as OpenClaw's native sandbox backend — application-layer filesystem/network/process policy on top of the VM's kernel isolation, replacing OpenClaw's built-in Docker sandbox (`agents.defaults.sandbox.backend: "openshell"`):

- **`openshell-gateway`** runs on the VM host as a rootless systemd *user* service under the `openclaw` user. Its unit ships inside the `openshell-gateway` RPM (not checked into the repo); the Containerfile symlinks it into `default.target.wants` (`bootc/Containerfile:88-89`). It manages the sandbox containers using the user's rootless Podman.
- **The `openshell` CLI** lives inside the derived OpenClaw container (`bootc/openclaw-openshell/Containerfile`) — OpenClaw's plugin shells out to it and opens an SSH session into the sandbox. This is why `openclaw.container` uses `Network=host`.
- **The sandbox** is pre-created under the fixed name `tankos-openclaw` by `bootstrap-openshell-sandbox`, from a digest-pinned image `ghcr.io/lobstertrap/openshell-hummingbird-images/sandboxes/openclaw@sha256:...` (Project Hummingbird-based, rebased from NVIDIA's Ubuntu community sandbox images).
- **First-boot sequence**: `bootstrap-openclaw` writes `openclaw.json` (gateway token, sandbox config, openshell plugin entry) → `bootstrap-openshell-sandbox` installs the `@openclaw/openshell-sandbox` plugin into the persisted volume, waits for `openshell-gateway.service`, registers the local gateway with `openshell gateway add`, and pre-creates the sandbox. Both idempotent.
- **Config backfill**: on upgrade from a pre-OpenShell config, `bootstrap-openclaw` backfills the `agents.defaults.sandbox` + `plugins.entries.openshell` blocks in place, preserving user customizations (`bootstrap-openclaw:71-109`).
- **Known limitation**: the sandbox's OPA-based network supervisor needs `CAP_SYS_PTRACE` for `/proc/<pid>/root` binary-path resolution, which rootless Podman doesn't grant by default — egress denial was not fully verified fail-closed in nested-virtualization test environments (`docs/openshell.md:171-194`).

## Cloud-Init

Tank OS includes cloud-init for first-boot configuration (`bootc/Containerfile:90-101` enables `cloud-init-local`, `cloud-init-network`, `cloud-init`, `cloud-config`, `cloud-final`, `cloud-init.target`):
- Injects SSH public key
- The `openclaw` user is pre-configured in the image
- Additional customization via `bootc-config.toml` (`examples/bootc-config.toml`, `examples/cloud-init/`)

## Build

```bash
make build-openclaw-openshell     # Build the derived OpenClaw+openshell image FIRST
make push-openclaw-openshell      # Push it to quay.io/redhat-et/tank-claw-openshell
make build                        # Build container image locally (localhost/tank-os:latest)
make build-qcow2                  # Build QCOW2 disk image (requires bootc-image-builder + config.toml)
make build-containerdisk          # Wrap qcow2 as a KubeVirt containerDisk (run build-qcow2 first)
make push-containerdisk           # Push containerDisk to quay.io/redhat-et/tank-os-containerdisk
make push-containerdisk-arch      # Push containerDisk under arch tag (safe for multi-arch merge)
make build-iso                    # Build ISO installer
make verify COSIGN_PUBLIC_KEY=... # Verify image signature with cosign
```

The Makefile (`Makefile:89-208`) auto-detects architecture (`uname -m` → amd64/arm64), drives multi-arch `bootc-image-builder` (QCOW2 `--type qcow2`, ISO `--type anaconda-iso`, both `--rootfs xfs`), and requires a rootful Podman machine on macOS for disk-image builds (`docs/build.md`). `OPENCLAW_REF` (2026.7.1) and `OPENSHELL_VERSION` (0.0.92) are the single points of control for both Containerfiles. CI/CD: PR validation, `python-semantic-release` versioning (VERSION file), cosign signing + SBOM + provenance + Trivy in the release workflow, OpenSSF Scorecard weekly.

## KubeVirt / OpenShift Virtualization

A per-user VM deployment path is provided under `deploy/`:
- `deploy/applicationset.yaml` — ArgoCD ApplicationSet (one Application per user, goTemplate engine, list generator) patching a shared Kustomize base per user
- `deploy/base/virtualmachine.yaml` — KubeVirt `VirtualMachine` with `containerDisk` (tank-os qcow2 wrapped as `/disk/disk.qcow2`, `deploy/containerdisk/Containerfile`) + `cloudInitNoCloud` user-data
- `examples/lima/{tank-os-qemu,tank-os-krunkit,tank-os-vz}.yaml` — Lima configs (QEMU on macOS/Linux, libkrun, Apple Virtualization.framework) for local prebuilt-disk testing, all confirmed on Lima 2.2.0 / macOS M3
- `qemu-guest-agent` included in the image for hypervisor integration

## Updates

Transactional OS updates via bootc:

```bash
sudo bootc status
sudo bootc switch --apply quay.io/sallyom/tank-os:latest   # README.md:90 (legacy namespace)
sudo bootc switch --apply quay.io/redhat-et/tank-os:latest # docs/build.md:21,407 (mid-namespace-migration)
sudo bootc upgrade --apply                                 # future updates against tracked tag
```

The new bootc image is pulled, staged, and applied on next reboot. On failure, bootc rollback restores the previous image.

## macOS Development Workflow

Developing and testing tank-os on macOS requires:

1. **Podman Machine** with rootful mode (for bootc-image-builder):
   ```bash
   brew install podman qemu
   podman machine init --cpus 4 --memory 8192 tank-os-dev
   podman machine set --rootful
   podman machine start
   ```

2. **Build** the bootc image for arm64:
   ```bash
   make build ARCH=arm64
   ```

3. **Build QCOW2** for VM testing:
   ```bash
   cp examples/bootc-config.toml config.toml  # Add SSH public key
   make build-qcow2 ARCH=arm64
   ```

4. **Boot locally with QEMU + HVF**:
   ```bash
   qemu-system-aarch64 -machine virt,highmem=on -accel hvf -cpu host \
     -smp 4 -m 4096 \
     -drive file=out-tank-os/qcow2/disk.qcow2,format=qcow2,if=virtio \
     -drive if=pflash,...,readonly=on -device virtio-net-pci,netdev=net0 \
     -netdev user,id=net0,hostfwd=tcp::2222-:22 -nographic
   ```

5. **SSH tunnel for dashboard access**:
   ```bash
   ssh -N -p 2222 -L 18789:127.0.0.1:18789 -L 18790:127.0.0.1:18790 openclaw@localhost
   ```

## Relation to Core Systems

tank-os packages [[openclaw]] as a bootable OS. It does not deploy [[hermes-agent]], [[agentfield]], or [[n8n]], but the bootc pattern generalizes — a similar containerfile could be built for Hermes (see [[hermzner]] for the current Ansible-based approach).

- [[crun-vm]] — Can run tank-os bootc images as containers: `podman run --runtime crun-vm tank-os:latest`
- [[podman]] — Foundation runtime inside the bootc image (rootless, Quadlet)
- [[deployment-architecture]] — The defense-in-depth model tank-os exemplifies
- [[buildah]] — Builds the bootc container image
- [[podlet]] — Could generate Quadlet files for customization

## Related

- [Architecture](domains/architecture/tank-os-architecture.md) — Bootc Containerfile analysis, Quadlet files, secret sync engine, build system
- [Deployment](domains/deployment/tank-os-deployment.md) — QEMU boot, cloud-init, SSH tunnel, bootc updates
- [Quadlet Config](assets/deployment/tank-os-quadlet.md) — OpenClaw + service-gator Quadlet files, secrets, CLI integration

## Related

- [[tank-os-architecture]] — Overall architecture description
- [[tank-os-deployment]] — Deployment guide
- [[tank-os-quadlet]] — Quadlet unit file configuration

## Cross-project

- [[openclaw]] -- Agent gateway packaged as bootc OS image
- [[podman]] -- Foundation runtime inside the bootc image
- [[hermzner]] -- Alternative deployment approach (Terraform + Ansible)
- [[crun-vm]] -- Runs tank-os bootc images as containers
- [[buildah]] -- Builds the bootc container image
- [[podlet]] -- Generates Quadlet files for customization
- [[nix-podman-stacks]] -- Alternative declarative container management
- [[gogs]] -- Self-hosted Git service for bootc build configs
- [[hermes-agent]] -- Comparable agent deployment pattern
