---
name: tank-os-deployment
tags: [tank-os, deployment, bootc, fedora, immutable-os, container-os, image-based, container, security, automation, desktop-app, mcp, quadlet, systemd, virtualization]
description: Tank OS Deployment
---

# Tank OS Deployment

This guide covers building, deploying, and managing a Tank OS instance.

## Prerequisites

- **Podman** installed (4.x or later)
- **make** available
- **qemu-img** and **QEMU** (for local testing on macOS)
- **bootc-image-builder** (for QCOW2/ISO builds)
- **cosign** (optional, for image verification)
- A container registry account (optional, for pushing images)

## Quick Start

### 1. Build the Image

Clone the repository and build the bootc image:

```bash
cd sources/tank-os

# Build for host architecture
make build

# Build for a specific architecture
make build ARCH=arm64

# Build with a custom registry
IMAGE_REGISTRY=quay.io IMAGE_NAMESPACE=myuser make build
```

The `Makefile` auto-detects architecture: `x86_64` -> `amd64`, `aarch64` -> `arm64`.

### 2. Build a Bootable Disk Image

Produce a QCOW2 disk image for VM deployment:

```bash
make build-qcow2
```

This runs `bootc-image-builder` (`quay.io/centos-bootc/bootc-image-builder:latest`) in a privileged container with `--type qcow2` and `--rootfs xfs`. Output is written to `out-tank-os/`.

For an ISO installer instead:

```bash
make build-iso
```

### 3. Push to Registry

Push the image for deployment on remote hosts:

```bash
IMAGE_REGISTRY=quay.io IMAGE_NAMESPACE=myuser make push
```

### 4. Deploy on a Server

On a target machine (bare metal or VM), switch to the registry-hosted image:

```bash
sudo bootc switch --apply quay.io/sallyom/tank-os:latest
```

This downloads the image, creates a new deployment, and activates it on the next reboot.

## Secret Configuration

Secrets are managed via rootless Podman secrets -- they are NOT baked into the image. On first boot, after the services start, inject secrets:

```bash
# SSH into the VM
ssh openclaw@<vm-ip>

# Inject secrets (runs as openclaw via sudo delegation)
tank-openclaw-secrets
```

This command triggers `sync-podman-secrets` which:
1. Checks for existing Podman secrets
2. Writes Quadlet drop-in files to mount secrets into both `openclaw` and `service-gator` containers
3. Rewrites `~/.openclaw/openclaw.json` with provider configurations
4. Reloads systemd user units

Secrets must be created as rootless Podman secrets before running `tank-openclaw-secrets`:

```bash
# As the openclaw user
echo -n "sk-ant-..." | podman secret create anthropic_api_key -
echo -n "sk-proj-..." | podman secret create openai_api_key -
echo -n "ghp_..." | podman secret create gh_token -
```

## SSH Tunnel for Service Access

All service ports bind to `127.0.0.1` only. Access services via SSH tunnel:

```bash
# OpenClaw gateway (port 18789)
ssh -N -L 18789:127.0.0.1:18789 openclaw@<vm-ip>

# OpenClaw additional port (18790)
ssh -N -L 18790:127.0.0.1:18790 openclaw@<vm-ip>

# Service-gator MCP proxy (port 8080)
ssh -N -L 8080:127.0.0.1:8080 openclaw@<vm-ip>
```

## Updates

Transactional updates via bootc:

```bash
# Upgrade to latest published image
sudo bootc upgrade --apply

# Switch to a specific version
sudo bootc switch --apply quay.io/sallyom/tank-os:v1.2.3

# Rollback to previous deployment
sudo bootc rollback
```

Both `upgrade` and `switch` stage the new deployment and activate it on next reboot. bootc automatically rolls back if the new deployment fails to boot.

## macOS Local Testing

Full workflow for testing on macOS with QEMU:

```bash
# 1. Build for ARM64
make build ARCH=arm64

# 2. Build QCOW2 (requires rootful Podman machine)
make build-qcow2

# 3. Resize the disk
qemu-img resize out-tank-os/disk.qcow2 20G

# 4. Launch QEMU (install edk2-aarch64-code.fd via Homebrew first)
qemu-system-aarch64 \
  -machine virt,highmem=on \
  -accel hvf \
  -cpu host \
  -smp 4 \
  -m 4096 \
  -drive if=pflash,format=raw,readonly=on,file=/opt/homebrew/share/qemu/edk2-aarch64-code.fd \
  -drive if=virtio,format=qcow2,file=out-tank-os/disk.qcow2 \
  -netdev user,id=net0,hostfwd=tcp::2222-:22 \
  -device virtio-net-pci,netdev=net0

# 5. Find SSH port (on macOS host)
# For QEMU hostfwd: port 2222
# For Podman Desktop VM: find from gvproxy process
ps aux | grep gvproxy

# 6. SSH tunnel
ssh -N -L 18789:127.0.0.1:18789 -L 18790:127.0.0.1:18790 openclaw@localhost -p 2222

# 7. Open browser
open http://127.0.0.1:18789
```

### UTM Alternative

For UTM on macOS, create a NoCloud seed ISO for cloud-init:

```bash
# Create seed ISO
hdiutil makehybrid -o seed.iso -hfs -joliet -iso -default-volume-name cidata /path/to/user-data /path/to/meta-data
```

The cloud-init config at `sources/tank-os/examples/cloud-init/openclaw-user-data.yaml` creates the `openclaw` user with:
- `wheel` group membership
- Passwordless sudo
- Locked password
- SSH authorized keys
- `loginctl enable-linger` via `runcmd`

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

# View logs
sudo -u openclaw XDG_RUNTIME_DIR=/run/user/1000 journalctl --user -u openclaw -f
sudo -u openclaw XDG_RUNTIME_DIR=/run/user/1000 journalctl --user -u service-gator -f

# Restart a service
sudo -u openclaw XDG_RUNTIME_DIR=/run/user/1000 systemctl --user restart openclaw
```

## Cloud-Init Configuration

The cloud-init user-data file configures first-boot setup:

```yaml
# openclaw-user-data.yaml
users:
  - name: openclaw
    groups: wheel
    sudo: ALL=(ALL) NOPASSWD:ALL
    lock_passwd: true
    ssh_authorized_keys:
      - ssh-ed25519 AAAA...
runcmd:
  - loginctl enable-linger openclaw
```

## Build-Time Configuration

For `bootc-image-builder`, equivalent provisioning can be done via `bootc-config.toml`:

```toml
[[users]]
name = "openclaw"
groups = ["wheel"]
ssh_authorized_keys = ["ssh-ed25519 AAAA..."]

## Related

- [[tank-os]] -- Wiki overview of the Tank OS project
- [[tank-os-architecture]] -- Architecture overview
- [[tank-os-quadlet]] -- Quadlet file reference
```
