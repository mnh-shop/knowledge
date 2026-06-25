---
name: hermes-suite-deployment
tags: [hermes, suite, deployment, all-in-one]
description: Hermes Suite deployment guide for the all-in-one Hermes container image combining gateway, dashboard, and WebUI
---

# Hermes Suite — Deployment

| Field | Value |
|---|---|
| **Source** | `sources/hermes-suite/` |
| **Type** | Docker/Podman single-container image |

## Prerequisites

- Podman v3.4.4+ or Docker CE
- podman-compose or docker-compose
- ~10GB disk space for image
- Network access during build (for git clone and pip install)
- Works on amd64 (x86_64) and arm64 (ARMv8)

## Quick Start

```bash
# 1. Clone
git clone https://github.com/sunnysktsang/hermes-suite.git
cd hermes-suite

# 2. Build
chmod +x *.sh
./build.sh

# Or use pre-built image:
podman pull ascensionoid/hermes-suite:2026.6.19-0.51.625

# 3. Create network
podman network create --subnet 10.99.0.0/24 agent_net

# 4. Start
./up.sh
```

## Docker Compose

```yaml
services:
  hermes-suite:
    build:
      context: .
      dockerfile: Dockerfile
    image: ascensionoid/hermes-suite:local
    container_name: hermes-suite
    networks:
      agent_net:
        ipv4_address: 10.99.0.11
    ports:
      - "8642:8642"   # Gateway
      - "8787:8787"   # WebUI
      - "9119:9119"   # Dashboard
    volumes:
      - ~/.hermes:/opt/data:Z
      - ~/workspace:/workspace:z
      - /etc/localtime:/etc/localtime:ro
    environment:
      - NODE_ENV=production
      - HERMES_HOME=/opt/data
      - HERMES_DATA_DIR=/opt/data
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G

networks:
  agent_net:
    external: true
```

## Version Management

### Use Pre-Built Images (Recommended)

```bash
podman pull ascensionoid/hermes-suite:2026.6.19-0.51.625
```

### Build with Pinned Versions

Edit `versions.env`:

```
AGENT_VERSION=v2026.6.19
WEBUI_VERSION=v0.51.625
CONTAINER_RUNTIME=auto
USE_SUDO=false
ENABLE_WHATSAPP_BRIDGE=false
```

Then:

```bash
./build.sh
# Or manually:
podman build \
  --build-arg AGENT_VERSION=v2026.6.19 \
  --build-arg HERMES_WEBUI_VERSION=v0.51.625 \
  -t hermes-suite:2026.6.19-0.51.625 .
```

## Configuration

All configuration lives in `~/.hermes/` on the host:

```
~/.hermes/
  .env            — API keys (OPENAI_API_KEY, TELEGRAM_TOKEN, etc.)
  config.yaml     — Model, toolsets, agent settings
  SOUL.md         — Agent personality
  skills/         — Custom skills
  memories/       — Persistent memory
  webui/          — WebUI state (sessions, workspace)
```

On first start, default `.env` and `config.yaml` are copied from hermes-agent examples.

## Management

```bash
# Start
./up.sh             # or podman-compose up -d

# View logs
./logs.sh           # or podman-compose logs -f
podman logs hermes-suite

# Stop
./down.sh           # or podman-compose down

# Check service status
podman exec hermes-suite supervisorctl status

# Restart a single service
podman exec hermes-suite supervisorctl restart hermes-gateway
```

## Access

| Service | URL | Description |
|---|---|---|
| Gateway | http://localhost:8642 | Agent gateway (CLI, Telegram, cron, tools) |
| WebUI | http://localhost:8787 | Browser-based chat interface |
| Dashboard | http://localhost:9119 | Monitoring/analytics |

## Migration from Multi-Container Setup

1. Stop existing containers
2. Build and start hermes-suite
3. Existing `~/.hermes/` data reused automatically

## Troubleshooting

### Permission Errors on ~/.hermes

**Rootless Podman:**
```bash
sudo chown -R 109999:109999 ~/.hermes
```

**Rootful Podman or Docker:**
```bash
sudo chown -R 10000:10000 ~/.hermes
```

### WebUI Not Loading

```bash
podman exec hermes-suite /opt/hermes-webui/venv/bin/python -c "import yaml; print('OK')"
```

### Dashboard Connection Error

Ensure gateway is running with:
```bash
podman exec hermes-suite supervisorctl status
```

### WhatsApp Bridge

Enable by setting `ENABLE_WHATSAPP_BRIDGE=true` in `versions.env` before build.
Must configure `WHATSAPP_ALLOWED_USERS` in `~/.hermes/.env` to restrict access.

## Security

- WhatsApp bridge disabled by default (requires explicit opt-in due to security implications)
- All ports bound to container namespace, host mapping controlled via compose
- Resource limits via Docker/Podman cgroups

## Related

- [[hermes-suite]] — Wiki entry
- [[hermes-suite-architecture]] — System architecture
- [[hermes-agent]] — Core agent runtime
- [[hermes-agent-docker]] — Simpler single-service Docker packaging
- [[hermes-agent-deployment]] — Agent deployment guide
- [[clawpier]] — Desktop GUI for managing Hermes/OpenClaw containers
- [[hermzner]] — Production Hermes on Hetzner
