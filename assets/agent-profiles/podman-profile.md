---
title: Podman
category: container-engine
tags: [podman, containers, container-engine, oci, systemd, quadlet, rootless, deployment]
repo: https://github.com/containers/podman
license: Apache-2.0
maturity: stable
language: Go (primary), C (rootless reexec), Rust (netavark)
status: active
source: sources/podman/
---

# Podman Profile

## Executive Summary

Podman is a daemonless, rootless-first container engine fully compliant with the OCI runtime spec. It manages pods, containers, images, volumes, and networks through a single CLI and integrates deeply with systemd via Quadlet generators. The architecture has no central daemon -- each invocation either links directly to libpod (ABI mode) or connects to a lightweight REST API service (`podman system service`).

## Key Facts

| Fact | Detail |
|------|--------|
| **Type** | Daemonless container engine |
| **Version** | Active development (v5.x, v6.x) |
| **OCI Compliance** | Full OCI runtime + image spec |
| **License** | Apache-2.0 |
| **Language** | Go (core), C (rootless reexec), Rust (netavark) |
| **Backend Storage** | `containers/storage` (overlayfs, fuse-overlayfs, VFS) |
| **Network Backend** | Netavark (bridge) + aardvark-dns; pasta (rootless) |
| **OCI Runtime** | crun (default) or runc |
| **State Store** | SQLite (BoltDB removed in v6.0) |
| **Systemd Integration** | Quadlet systemd generator (.container, .volume, .network, .pod, .kube, .build, .image) |
| **Rootless Execution** | Default; uses user namespaces + newuidmap/newgidmap |
| **macOS/Windows** | Podman Machine (libkrun/applehv/QEMU/WSL2 VM) |

## Architecture Highlights

- **Three-layer design**: CLI (`cmd/podman/`) -> Domain Engine Factory (`pkg/domain/infra/`) -> libpod library. ABI mode calls libpod directly; Tunnel mode calls REST API.
- **Rootless via C reexec**: C constructor in `pkg/rootless/rootless_linux.c` forks into a new user+mount namespace before Go `init()` runs. A pause process (catatonit) keeps the namespace alive.
- **Quadlet**: Systemd generator translates Quadlet files into `.service` units at `daemon-reload`. Search paths follow XDG spec. Supports drop-in directories, template units, and automatic cross-unit dependencies.
- **Networking**: Netavark (Rust) manages bridges/firewall; aardvark-dns provides per-container DNS on custom networks. Rootless uses pasta (from passt, no NAT).
- **Storage**: `containers/storage` with overlayfs. Volumes managed in `libpod/volume*.go`. Secrets managed by `secrets.SecretsManager` at `$graphroot/secrets`.

## CLI Quick Reference

```bash
# Container lifecycle
podman run -d --name myapp -p 8080:80 myimage
podman ps -a
podman stop myapp && podman rm myapp

# Pods
podman pod create --name mypod -p 8080:80
podman run --pod mypod myimage

# Images
podman pull docker.io/library/alpine
podman build -t myapp .
podman push myapp registry.example.com/myapp

# Networks
podman network create --subnet 10.89.0.0/24 mynet
podman network ls

# Volumes
podman volume create mydata
podman volume ls

# Secrets
podman secret create apikey ./key.txt
podman secret ls

# System
podman info
podman system prune
podman system reset
```

## Systemd Integration

Primary deployment mechanism. Example workflow:

```bash
# Write Quadlet file
cat > ~/.config/containers/systemd/myapp.container << 'EOF'
[Unit]
Description=My App

[Container]
Image=myapp:latest
PublishPort=127.0.0.1:8080:8080
HealthCmd=curl -f http://localhost:8080/health
Notify=healthy

[Install]
WantedBy=default.target
EOF

# Deploy
systemctl --user daemon-reload
systemctl --user start myapp.service
journalctl --user -u myapp.service -f
```

## Important Paths

| Path | Purpose |
|------|---------|
| `~/.config/containers/systemd/` | User Quadlet files (rootless) |
| `/etc/containers/systemd/` | System Quadlet files (rootful) |
| `~/.local/share/containers/storage/` | Rootless image/layer storage |
| `$XDG_RUNTIME_DIR/containers/` | Rootless runtime data |
| `/var/lib/containers/storage/` | Rootful image/layer storage |
| `/run/user/$UID/podman/podman.sock` | Rootless Podman API socket |

## References

- **Source code**: https://github.com/containers/podman
- **Documentation**: https://docs.podman.io/
- **Man pages**: `podman-systemd.unit.5`, `podman-run.1`, `podman-machine.1`
- **Quadlet format**: `man podman-systemd.unit`
- **Rootless tutorial**: `docs/tutorials/rootless_tutorial.md`
- **Troubleshooting**: `troubleshooting.md` in the source tree

## Skills (Agent Capabilities)

A "podman agent" (AI or human) managing deployment should have these skills:

### 1. Quadlet Authoring
- Write `.container`, `.volume`, `.network`, `.pod`, `.kube`, `.build`, `.image`, `.artifact` files.
- Structure secrets in `.container.d/` drop-in directories (never committed).
- Use `UserNS=keep-id`, `Notify=healthy`, `PublishPort=127.0.0.1:` for rootless.
- Set `TimeoutStartSec=900` for services that pull images at start.
- Add `AutoUpdate=registry` for automatic container updates.

### 2. Rootless Debugging
- Diagnose subuid/subgid mismatches (`/etc/subuid`, `/etc/subgid`).
- Check cgroup delegation (`cat /sys/fs/cgroup/user.slice/.../cgroup.controllers`).
- Verify systemd lingering (`loginctl show-user $USER | grep Linger`).
- Test user namespace health (`podman run --rm alpine echo ok`).
- Inspect pasta/slirp4netns networking (`podman info | grep -A5 network`).

### 3. Podman Machine Management
- Initialize VMs with appropriate resources (`--cpus 4 --memory 8192`).
- Switch between rootful and rootless modes.
- Monitor VM state and recover after host sleep.
- Export/forward ports via gvproxy configuration.

### 4. Secret Management
- Create, list, inspect, and replace secrets.
- Structure secret drop-in files for Quadlet containers.
- Implement secret rotation without downtime (`--replace` flag).
- Understand secret scope (per-container at creation time, not updated in running containers).

### 5. Systemd Integration
- Debug Quadlet file parsing failures (`/usr/lib/systemd/system-generators/podman-system-generator --user --dryrun`).
- Configure drop-in directories for hierarchical overrides.
- Set up socket-activated API services.
- Manage template unit instances (`worker@8080.service`).

### 6. Production Operations
- Implement auto-updates with `podman auto-update` and the systemd timer.
- Back up and restore volumes (`podman volume export/import`).
- Set up healthcheck-driven self-healing (`HealthOnFailure=kill` + `Restart=on-failure`).
- Migrate containers between hosts (Quadlet files + volume export + secret recreation).

## Integration Knowledge

### SSH Tunnel Access Pattern

Since rootless Podman ports bind to `127.0.0.1` only, SSH port forwarding is the standard access method:

```bash
# Single port forward
ssh -N -L 8080:127.0.0.1:8080 user@host.example.com

# Multiple ports (all services on the host)
ssh -N \
  -L 18789:127.0.0.1:18789 \   # OpenClaw API
  -L 3000:127.0.0.1:3000 \     # Mission Control
  -L 5678:127.0.0.1:5678 \     # n8n
  user@host.example.com

# Persistent tunnel with auto-reconnect (autossh)
sudo apt install autossh
autossh -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" \
  -N -L 8080:127.0.0.1:8080 user@host.example.com

# Systemd service for persistent tunnel
# /etc/systemd/system/podman-tunnel.service
[Unit]
Description=Podman Tunnel to Remote Host
After=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/ssh -N -L 18789:127.0.0.1:18789 user@host.example.com
Restart=on-failure
RestartSec=10
User=tunnel

[Install]
WantedBy=multi-user.target
```

### Reverse Proxy Pattern

For services that need HTTP/HTTPS access without SSH, deploy a reverse proxy on a public-facing host that proxies to the Podman host's loopback ports:

```
Internet → Reverse Proxy (nginx/Caddy) → SSH Tunnel → Podman Host:127.0.0.1:18789
```

```nginx
# nginx reverse proxy configuration
server {
    listen 443 ssl;
    server_name openclaw.example.com;
    
    location / {
        proxy_pass http://127.0.0.1:18789;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### CI/CD Integration

Podman works directly in CI/CD pipelines (GitHub Actions, GitLab CI, etc.):

```yaml
# .github/workflows/deploy.yml
- name: Deploy via Podman
  run: |
    podman build -t myapp:${{ github.sha }} .
    podman push myapp:${{ github.sha }} ghcr.io/myorg/myapp
```

For remote deployment to a Podman host:
```bash
# Option A: SSH + podman commands
ssh user@host "podman pull ghcr.io/myorg/myapp:latest && \
  systemctl --user restart myapp.service"

# Option B: Use the Podman API over SSH
podman --connection prod pull ghcr.io/myorg/myapp:latest
podman --connection prod system restart myapp
```

### Multi-Host Orchestration

Podman does not have a built-in orchestrator (use Kubernetes for that). Patterns for multi-host deployment with Podman:

1. **SSH-based**: Ansible playbooks that rsync Quadlet files, SSH in, `systemctl --user daemon-reload`.
2. **Podman API**: Each host runs `podman system service`; automation connects via SSH tunnels to each socket.
3. **Terraform/Ansible** (see [[hermzner]]): Provision VMs, install Podman, deploy Quadlet files.
4. **bootc images** (see [[tank-os]]): Bundle Podman + Quadlet files + application into a bootable OS image.

### Volume Migration Between Hosts

```bash
# Source: export volumes
for vol in $(podman volume ls -q); do
  podman volume export "$vol" > "${vol}.tar"
done

# Source: save Quadlet files
tar czf quadlet-backup.tar.gz -C ~/.config/containers/systemd/ .

# Target: restore
tar xzf quadlet-backup.tar.gz -C ~/.config/containers/systemd/
for tar in *.tar; do
  vol="${tar%.tar}"
  podman volume create "$vol"
  podman volume import "$vol" < "$tar"
done
systemctl --user daemon-reload
systemctl --user start *.service
```

## Related Knowledge Base Pages

- [[podman-architecture]] -- Deep-dive into architecture
- [[podman-deployment]] -- Deployment guide
- [[podman-quadlet-examples]] -- Production Quadlet files
