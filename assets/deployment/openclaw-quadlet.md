---
name: openclaw-quadlet
tags: [acp, agent-gateway, cli, container, deployment, docker, live-canvas, mcp, messaging, openclaw, orchestration, personal-assistant, podman, quadlet, security, storage, systemd, typescript]
description: OpenClaw Quadlet Deployment (Rootless Podman)
---

# OpenClaw Quadlet Deployment (Rootless Podman)
**Source:** `sources/openclaw/`

This asset file provides production-ready Quadlet configurations for deploying OpenClaw under Rootless Podman with systemd-native lifecycle management.

Quadlet converts `.container`, `.volume`, `.network`, and `.secret` files into systemd unit files, giving OpenClaw the same service management as a native application. This is the recommended deployment method on [[tank-os]] Fedora bootc images and any system with Podman 4.0+.

---

## File Index

| File | Purpose |
|------|---------|
| `openclaw-gateway.container` | Main gateway container |
| `openclaw-cli.container` | Ephemeral CLI container (shares gateway network) |
| `openclaw-gateway.secret` | Gateway token secret |
| `openclaw-auth-profiles.volume` | Persistent volume for auth profile encryption keys |
| `openclaw.pod` | Pod definition for multi-service orchestration |
| `ollama.container` | Ollama LLM server (optional) |
| `qdrant.container` | Qdrant vector database (optional) |

---

## Prerequisites

```bash
# Podman 4.0+ with Quadlet support
podman version

# Enable podman-user service
systemctl --user enable --now podman.socket

# Verify Quadlet directory exists
mkdir -p ~/.config/containers/systemd/
```

---

## Gateway Container

**File:** `~/.config/containers/systemd/openclaw-gateway.container`

```ini
[Unit]
Description=OpenClaw Gateway
Documentation=https://github.com/openclaw/openclaw
After=network-online.target
Wants=network-online.target

[Container]
Image=ghcr.io/openclaw/openclaw:latest
ContainerName=openclaw-gateway

# Ports
PublishPort=18789:18789
PublishPort=18790:18790

# Volumes (rootless Podman -- :Z for SELinux relabeling)
Volume=%h/.openclaw:/home/node/.openclaw:Z
Volume=%h/.openclaw/workspace:/home/node/.openclaw/workspace:Z
Volume=%h/.openclaw-auth-profile-secrets:/home/node/.config/openclaw:Z

# Environment
Environment=HOME=/home/node
Environment=OPENCLAW_HOME=/home/node
Environment=OPENCLAW_STATE_DIR=/home/node/.openclaw
Environment=OPENCLAW_CONFIG_PATH=/home/node/.openclaw/openclaw.json
Environment=OPENCLAW_GATEWAY_BIND=lan
Environment=NODE_ENV=production
Environment=TZ=UTC
Secret=openclaw-gateway-token,type=env,target=OPENCLAW_GATEWAY_TOKEN

# Run as non-root (match image user)
User=1000
Group=1000

# Security
DropCapability=NET_RAW
DropCapability=NET_ADMIN
NoNewPrivileges=true

# Gateway command
Exec=node openclaw.mjs gateway --port 18789 --bind lan

# Health check (via container exec)
HealthCmd=node -e "fetch('http://127.0.0.1:18789/healthz').then(r => process.exit(r.ok?0:1))"
HealthInterval=180s
HealthTimeout=10s
HealthRetries=3
HealthStartPeriod=30s

[Service]
Restart=always
TimeoutStartSec=120

[Install]
WantedBy=default.target
```

### Installation

```bash
# Write the container file (after editing paths as needed)

# Pull the image
podman pull ghcr.io/openclaw/openclaw:latest

# Create the gateway token secret (see Secrets section)
openssl rand -hex 32 > /tmp/gateway-token
podman secret create openclaw-gateway-token /tmp/gateway-token
rm /tmp/gateway-token

# Reload systemd and start
systemctl --user daemon-reload
systemctl --user start openclaw-gateway.service

# Check status
systemctl --user status openclaw-gateway.service

# Enable on boot
systemctl --user enable openclaw-gateway.service

# View logs
journalctl --user -u openclaw-gateway.service -f
```

---

## CLI Sidecar Container

**File:** `~/.config/containers/systemd/openclaw-cli.container`

```ini
[Unit]
Description=OpenClaw CLI (ephemeral sidecar)
PartOf=openclaw-gateway.service
After=openclaw-gateway.service

[Container]
Image=ghcr.io/openclaw/openclaw:latest
ContainerName=openclaw-cli

# Share gateway network namespace
Network=container:openclaw-gateway

# Volumes
Volume=%h/.openclaw:/home/node/.openclaw:Z
Volume=%h/.openclaw-auth-profile-secrets:/home/node/.config/openclaw:Z

# Environment
Environment=HOME=/home/node
Environment=OPENCLAW_HOME=/home/node
Environment=OPENCLAW_STATE_DIR=/home/node/.openclaw
Environment=OPENCLAW_CONFIG_PATH=/home/node/.openclaw/openclaw.json
Environment=OPENCLAW_GATEWAY_BIND=lan

# Security
DropCapability=NET_RAW
DropCapability=NET_ADMIN
NoNewPrivileges=true

# Default to CLI help
Exec=node openclaw.mjs --help

# CLI is ephemeral -- no restart
[Service]
Type=oneshot
RemainAfterExit=no

[Install]
WantedBy=default.target
```

### Usage

```bash
# Run with custom command
podman run --rm --network=container:openclaw-gateway \
  -v ~/.openclaw:/home/node/.openclaw:Z \
  ghcr.io/openclaw/openclaw:latest \
  node openclaw.mjs gateway status

# Or using podman exec on a running container
podman exec -it openclaw-gateway node openclaw.mjs gateway status
```

---

## Secrets

**File:** `~/.config/containers/systemd/openclaw-gateway.secret`

```ini
# openclaw-gateway.secret
[Secret]
Label=openclaw-gateway-token
```

### Create the Secret

```bash
# Generate a random token
openssl rand -hex 32 > /tmp/gateway-token

# Create Podman secret
podman secret create openclaw-gateway-token /tmp/gateway-token

# Clean up
rm /tmp/gateway-token

# Verify
podman secret list
podman secret inspect openclaw-gateway-token
```

### Usage in the Container

The `.container` file references the secret via:

```ini
Secret=openclaw-gateway-token,type=env,target=OPENCLAW_GATEWAY_TOKEN
```

This injects the secret value as the `OPENCLAW_GATEWAY_TOKEN` environment variable inside the container.

---

## Volume Definitions

For explicit volume management with Quadlet:

**File:** `~/.config/containers/systemd/openclaw-auth-profiles.volume`

```ini
[Volume]
Label=openclaw-auth-profiles
```

Reference in container definition:

```ini
Volume=openclaw-auth-profiles.volume:/home/node/.config/openclaw:Z
```

---

## Pod Networking

For an isolated pod with multiple containers sharing the same network namespace:

**File:** `~/.config/containers/systemd/openclaw.pod`

```ini
[Pod]
PodName=openclaw
PublishPort=18789:18789
PublishPort=18790:18790

[Service]
Restart=always

[Install]
WantedBy=default.target
```

Then reference the pod in the gateway container:

```ini
[Container]
Pod=openclaw.pod
# ... (no PublishPort needed -- handled by pod)
```

---

## Multi-Service Orchestration

### OpenClaw + Ollama (Local LLM)

```ini
# openclaw-gateway.container addition
[Container]
AddHost=ollama:host-gateway
Environment=OLLAMA_HOST=http://ollama:11434
```

```ini
# ~/.config/containers/systemd/ollama.container
[Unit]
Description=Ollama LLM Server

[Container]
Image=docker.io/ollama/ollama:latest
ContainerName=ollama
PublishPort=11434:11434
Volume=ollama-models:/root/.ollama:Z
Environment=OLLAMA_HOST=0.0.0.0

[Service]
Restart=always

[Install]
WantedBy=default.target
```

```ini
# ~/.config/containers/systemd/ollama-models.volume
[Volume]
Label=ollama-models
```

### OpenClaw + Qdrant (Vector Store)

```ini
# ~/.config/containers/systemd/qdrant.container
[Unit]
Description=Qdrant Vector Database

[Container]
Image=docker.io/qdrant/qdrant:latest
ContainerName=qdrant
PublishPort=6333:6333
PublishPort=6334:6334
Volume=qdrant-storage:/qdrant/storage:Z

[Service]
Restart=always

[Install]
WantedBy=default.target
```

```ini
# ~/.config/containers/systemd/qdrant-storage.volume
[Volume]
Label=qdrant-storage
```

### OpenClaw + PostgreSQL (Alternative State Backend)

```ini
# ~/.config/containers/systemd/postgres-openclaw.container
[Unit]
Description=PostgreSQL for OpenClaw

[Container]
Image=docker.io/postgres:16-alpine
ContainerName=postgres-openclaw
PublishPort=5432:5432
Volume=postgres-openclaw-data:/var/lib/postgresql/data:Z
Environment=POSTGRES_DB=openclaw
Environment=POSTGRES_USER=openclaw
Secret=postgres-openclaw-password,type=env,target=POSTGRES_PASSWORD

[Service]
Restart=always

[Install]
WantedBy=default.target
```

---

## All-in-One Quadlet Directory

Create all files in `~/.config/containers/systemd/openclaw/` for organized management:

```
~/.config/containers/systemd/openclaw/
  openclaw.pod
  openclaw-gateway.container
  openclaw-cli.container
  openclaw-gateway.secret
  ollama.container
  ollama-models.volume
  qdrant.container
  qdrant-storage.volume
```

Enable all at once:

```bash
systemctl --user daemon-reload
systemctl --user start openclaw.target
systemctl --user enable openclaw.target
```

---

## Troubleshooting Quadlet

### Check Unit Status

```bash
systemctl --user status openclaw-gateway.service
journalctl --user -u openclaw-gateway.service -f
```

### View Generated Unit

Quadlet auto-generates systemd units from `.container` files. View the generated service:

```bash
systemctl --user cat openclaw-gateway.service
```

### Common Issues

| Issue | Solution |
|-------|----------|
| `:Z` SELinux label fails | Remove `:Z` from volume mounts on non-SELinux systems (macOS) |
| Port already in use | Change `PublishPort` or stop existing service on that port |
| Secret not found | Verify with `podman secret inspect openclaw-gateway-token` |
| Volume permission denied | `chown -R 1000:1000 ~/.openclaw` (match container uid) |
| Podman DNS resolution | Set `--dns` or add `AddHost` entries for `host.docker.internal` |
| Container not restarting | Check `journalctl --user -u openclaw-gateway.service` for errors |
| mDNS not working | Podman bridge does not forward multicast. Set `OPENCLAW_DISABLE_BONJOUR=1` |
| Image pull failures | Run `podman pull ghcr.io/openclaw/openclaw:latest` manually first |

### Log Management

```bash
# Read container logs via podman
podman logs openclaw-gateway

# Read via journald
journalctl --user -u openclaw-gateway.service -f

# Follow logs
podman logs -f openclaw-gateway
```

---

## Migration from Docker Compose

If you have an existing Docker Compose deployment and want to migrate to Quadlet:

```bash
# 1. Stop Compose
docker compose down

# 2. Extract current configuration
docker compose config

# 3. Create Quadlet files (see templates above)

# 4. Create secrets
podman secret create openclaw-gateway-token /path/to/your/gateway-token

# 5. Start
systemctl --user daemon-reload
systemctl --user start openclaw-gateway.service
systemctl --user enable openclaw-gateway.service

# 6. Verify
systemctl --user status openclaw-gateway.service
```

## Related

- [[openclaw-acp-agent]] -- ACP agent asset registration
- [[openclaw-acp-implementation]] -- ACP protocol implementation
- [[openclaw-mcp-implementation]] -- MCP server implementation
- [[openclaw-api]] -- API reference
- [[openclaw]] -- Main wiki entry

---

## Related

- [[domains/deployment/openclaw-deployment.md]] -- Full deployment guide
- [[domains/architecture/openclaw-architecture.md]] -- Architecture overview
- [[domains/deployment/quadlet-patterns.md]] -- General Quadlet deployment patterns
- [[assets/mcp-servers/openclaw-mcp-server.md]] -- MCP server configuration
- [[assets/profiles/openclaw-profile.md]] -- Quick reference profile
- [[tank-os]] -- Fedora bootc image for deploying OpenClaw as a bootable appliance
