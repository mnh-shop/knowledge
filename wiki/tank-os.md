---
name: tank-os
tags: [bootc, cli, container, dashboard, deployment, fedora, git, image-based, immutable-os, mcp, podman, quadlet, systemd, tank-os, virtualization, wiki]
description: Tank OS — Fedora Bootc Image for OpenClaw
source: sources/tank-os/
---

# Tank OS — Fedora Bootc Image for OpenClaw

| Field | Value |
|---|---|
| **Origin** | [LobsterTrap/tank-os](https://github.com/LobsterTrap/tank-os) |
| **License** | Not specified (likely MIT) |
| **Stack** | Bootc (container→bootable OS), Fedora 41, Rootless Podman 5, Quadlet |
| **Source** | `sources/tank-os/` |
| **Wanted** | Bootable Linux appliance running OpenClaw as rootless Podman |

## What it is

tank-os turns [[openclaw]] into a **bootable Linux appliance** using [bootc](https://bootc-dev.github.io/bootc/). bootc packages Fedora + rootless OpenClaw service + Quadlet units into one OCI container image that can be built into VM disks, QCOW2, or ISO images. The result: a machine that boots into a running OpenClaw gateway with zero manual OS setup.

This is an exemplar of the [[deployment-architecture]] pattern: the host OS plus agent stack travel together as one deployable, updateable, rollbackable unit.

## Containerfile Details

Based on `quay.io/fedora/fedora-bootc:latest` (Fedora bootc base):

### Packages Installed

```
cloud-init          — First-boot initialization (SSH keys, user-data)
openssh-server      — SSH daemon for remote access
podman              — Rootless container runtime
```

Notably minimal — only 3 packages beyond the bootc base, keeping the image small.

### User Setup

- Creates `openclaw` user (UID 1000, matching the OpenClaw container's `node` user)
- Sets up passwordless sudo via `/etc/sudoers.d/openclaw`
- Home directory at `/home/openclaw/`

### Quadlet Files

Two systemd user services defined as Quadlet `.container` files in `/etc/containers/systemd/`:

#### `openclaw.container`

Runs the official OpenClaw container image:

```ini
[Unit]
Description=OpenClaw service
After=network-online.target
Wants=network-online.target

[Container]
Image=ghcr.io/openclaw/openclaw:latest
ContainerName=openclaw
PullPolicy=newer
RunInit=true
UserNS=keep-id
Volume=%h/.openclaw:/home/node/.openclaw
PublishPort=127.0.0.1:18789:18789
PublishPort=127.0.0.1:18790:18790
Exec=node dist/index.js gateway --allow-unconfigured --bind lan --port 18789
HealthCmd=curl -f http://localhost:18789/healthz
HealthInterval=30s
HealthRetries=3
Notify=healthy

[Service]
Restart=on-failure
TimeoutStartSec=300

[Install]
WantedBy=default.target
```

Key Quadlet patterns:
- `UserNS=keep-id` — maps host UID 1000 into the container (avoids file permission issues with mounted volumes)
- `Volume=%h/.openclaw` — stores OpenClaw state persistently under the user's home
- All ports bind to `127.0.0.1` (rootless Podman constraint — cannot bind to 0.0.0.0)
- `PullPolicy=newer` — auto-updates container image on restart
- `HealthCmd` + `Notify=healthy` — systemd healthcheck integration

#### `service-gator.container`

Runs the service-gator MCP proxy (Go-based, exposes scoped tool access):

```ini
[Unit]
Description=Service Gator MCP server
After=network-online.target openclaw.service

[Container]
Image=ghcr.io/cgwalters/service-gator:latest
ContainerName=service-gator
PullPolicy=newer
RunInit=true
UserNS=keep-id
Volume=%h/.config/service-gator/:/etc/service-gator:ro
Volume=%h/.openclaw/:/workspaces:ro
PublishPort=127.0.0.1:8080:8080
Exec=--mcp-server 0.0.0.0:8080 --scope-file /etc/service-gator/scopes.json
HealthCmd=curl -f http://localhost:8080/health
HealthInterval=30s
HealthRetries=3
Notify=healthy

[Service]
Restart=on-failure
TimeoutStartSec=300

[Install]
WantedBy=default.target
```

### CLI Integration

A host-level `openclaw` command delegates into the running container:

```bash
#!/bin/sh
# /usr/local/bin/openclaw
exec podman exec -it openclaw node dist/index.js "$@"
```

This means from the host shell (SSH'd in as `openclaw`), you run `openclaw gateway status --deep`, `openclaw doctor`, `openclaw dashboard --no-open` etc. and it executes inside the container.

### Secret Management

APIs keys are stored in rootless Podman secrets (never baked into the image):

```bash
# Create a secret
printf '%s' "$ANTHROPIC_API_KEY" | podman secret create anthropic_api_key -

# Generate Quadlet drop-in secrets and update openclaw.json
tank-openclaw-secrets    # Custom script — generates config from active secrets

# Restart services
systemctl --user restart openclaw.service service-gator.service
```

Supported secret names: `anthropic_api_key`, `openai_api_key`, `gemini_api_key`, `google_api_key`, `openrouter_api_key`.

## Build

```bash
make build                  # Build container image locally (localhost/tank-os:latest)
make build-qcow2            # Build QCOW2 disk image (requires bootc-image-builder)
make build-iso              # Build ISO installer
```

The Makefile uses `pyproject.toml` for tool dependencies. The examples/ directory provides QEMU boot scripts and bootc config templates.

## Cloud-Init

Tank OS includes cloud-init for first-boot configuration:
- Injects SSH public key 
- The `openclaw` user is pre-configured in the image
- Additional customization via bootc-config.toml

## Updates

Transactional OS updates via bootc:

```bash
bootc switch --apply quay.io/sallyom/tank-os:latest
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
