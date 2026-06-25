# Mission Control Quadlet Configuration
**Source:** `sources/mission-control/`

## Overview

Mission Control does not ship native Quadlet `.container` files, but the existing Docker Compose infrastructure translates directly to Podman Quadlet. This file provides a working `.container` definition and guidance for rootless Quadlet deployment.

## Prerequisites

- Podman 4.0+ with Quadlet support (enabled by default in most distributions)
- Rootless Podman for the `nextjs` user (uid 1001 inside container, mapped to host user)
- An OCI image (build from Dockerfile or pull from GHCR)
- `.env` file with required configuration (see `/Users/admin1/Documents/knowledge/domains/deployment/mission-control-deployment.md`)

## .container Unit

Save as `~/.config/containers/systemd/mission-control.container`:

```container
[Unit]
Description=Mission Control Dashboard
Documentation=https://github.com/mission-control/mission-control
After=network-online.target
Wants=network-online.target

[Container]
# Image
Image=ghcr.io/mission-control/mission-control:latest

# Environment
EnvironmentFile=%h/.config/mission-control/.env

# Ports
PublishPort=3000:3000

# Volumes
Volume=mc-data:/app/.data:U

# Tmpfs for writable directories (required because read_only=true)
Tmpfs=/tmp:size=64M
Tmpfs=/app/.next/cache:size=128M

# Gateway connectivity (uncomment if using OpenClaw gateway on host)
# AddHost=host.docker.internal:host-gateway

# Container hardening
DropCapability=all
AddCapability=NET_BIND_SERVICE
NoNewPrivileges=true
ReadOnly=true
SecurityLabelDisable=false

# Resource limits (minimum recommended)
Memory=512M
CPUQuota=100%
PidsLimit=256

# Health check (matches Dockerfile)
HealthCmd=/(which curl || which wget || echo) -f http://localhost:3000/api/status?action=health || exit 1
HealthInterval=30s
HealthTimeout=5s
HealthRetries=3
HealthStartPeriod=10s

# Container configuration
ContainerName=mc
User=1001:1001
WorkingDir=/app
Exec=/app/server.js
Timezone=local

# Logging
LogDriver=k8s-file
LogOpt=max-size=10m
LogOpt=max-file=3

[Service]
Restart=always
RestartSec=10s

[Install]
WantedBy=default.target
```

## Hardened Profile Overlay

For production use, create a hardened profile by adding the following to `[Container]`:

```container
# Internal-only network (requires a reverse proxy on an external-facing container)
Network=mc-internal:internal=true
```

In this mode, all external access (including the browser dashboard) must go through a reverse proxy (nginx, Caddy, Traefik) that sits on an external network.

## Enabling and Starting

```bash
# Reload systemd user units
systemctl --user daemon-reload

# Create the named volume if not using auto-creation
podman volume create mc-data

# Start the service
systemctl --user start mission-control

# Enable on boot (lingering must be enabled for the user)
loginctl enable-linger $(whoami)
systemctl --user enable mission-control

# Check status
systemctl --user status mission-control

# View logs
journalctl --user -u mission-control -f
```

## Notes

- The `:U` flag on the volume mount tells Podman to recursively chown the volume contents to the container's UID (1001). Remove `:U` if the volume is pre-seeded from a Docker deployment.
- For agent runtime provisioning (Git, Python, curl, etc.), the image already ships these tools. Verify they are present if using a custom slim image.
- If running with an OpenClaw gateway, the `AddHost=host.docker.internal:host-gateway` line is required for the container to reach the host's gateway process.
- The memory limit of 512MB is the recommended minimum. Increase to 2GB if using the `/chat` panel with `node-pty` terminal emulation.
- For Tailscale Serve mode, map ports accordingly and set `NEXT_PUBLIC_GATEWAY_URL` to the Tailscale funnel URL.
- The hardened with internal-only network requires a reverse proxy to terminate TLS and forward to the internal mc-internal network. Without this, the dashboard UI itself will be unreachable.
