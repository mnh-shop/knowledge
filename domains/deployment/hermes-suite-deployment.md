---
name: hermes-suite-deployment
tags: [agent-gateway, container, dashboard, deployment, docker, git, hermes-agent, messaging, multi-platform, podman, security, typescript]
description: Hermes Suite deployment guide for the all-in-one Hermes container image combining gateway, dashboard, and WebUI
source: sources/hermes-suite/
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
podman pull ascensionoid/hermes-suite:2026.7.7.2-0.52.76

# 3. Create network
podman network create --subnet 10.99.0.0/24 agent_net

# 4. Start
./up.sh
```

`./up.sh` prints the dashboard login at startup (from `DASHBOARD_CREDENTIAL`, default `admin:admin`).

## Docker Compose

```yaml
services:
  hermes-suite:
    build:
      context: .
      dockerfile: Dockerfile
    image: ascensionoid/hermes-suite:${HERMES_SUITE_IMAGE_TAG}
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
      - DASHBOARD_CREDENTIAL=${DASHBOARD_CREDENTIAL:-admin:admin}
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G

networks:
  agent_net:
    external: true
```

Note: `up.sh` derives `HERMES_SUITE_IMAGE_TAG` from `versions.env` and exports `DASHBOARD_CREDENTIAL` into compose (up.sh:56-66).

## Version Management

### Use Pre-Built Images (Recommended)

```bash
podman pull ascensionoid/hermes-suite:2026.7.7.2-0.52.76
```

### Build with Pinned Versions

Edit `versions.env` (the single source of truth for the image):

```
AGENT_VERSION=v2026.7.7.2
WEBUI_VERSION=v0.52.76
CONTAINER_RUNTIME=auto
USE_SUDO=false
DASHBOARD_CREDENTIAL=admin:admin
ENABLE_WHATSAPP_BRIDGE=false
```

Then:

```bash
./build.sh
# Or manually:
podman build \
  --build-arg AGENT_VERSION=v2026.7.7.2 \
  --build-arg HERMES_WEBUI_VERSION=v0.52.76 \
  -t hermes-suite:2026.7.7.2-0.52.76 .
```

`build.sh` also accepts per-build overrides: `--agent`, `--webui`, `--podman`, `--docker`, `--docker-nolog`, `--sudo`, `--whatsapp`. Suite tags follow `{agent_date}-{webui_semver}` (e.g. `2026.7.7.2-0.52.76`).

## CI Pipeline (build.yml)

`.github/workflows/build.yml` automates multi-arch publishing:

- **Trigger:** push of a `v*` git tag
- **Version parsing:** the compound tag is split back into agent/webui versions (`2026.7.7.2-0.52.76` → `v2026.7.7.2` + `v0.52.76`) and passed as build args (build.yml:23-41)
- **Platforms:** `linux/amd64,linux/arm64` via QEMU + Docker Buildx (build.yml:43-47, 59)
- **Output:** pushed to `docker.io/ascensionoid/hermes-suite` under the cleaned tag **and** `latest`
- **Cache:** GitHub Actions cache (`type=gha`, mode=max) for incremental builds

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

On first start, default `.env`, `config.yaml`, and `SOUL.md` are copied from hermes-agent examples if missing; stale `gateway.pid`/`gateway.lock` from previous runs are cleaned (start.sh:43-90).

## Dashboard Authentication

Since hermes-agent **v2026.7.1** the dashboard requires authentication — the upstream `--insecure` flag is now a no-op. Configure the login via `DASHBOARD_CREDENTIAL` in `versions.env`:

```env
DASHBOARD_CREDENTIAL=admin:admin   # default; change for internet exposure
DASHBOARD_CREDENTIAL=auto          # random password, persisted to .dashboard_credential
DASHBOARD_CREDENTIAL=myuser:secret # custom pair
```

How it flows:

1. `up.sh` reads `DASHBOARD_CREDENTIAL` and exports it into compose (up.sh:17-36); `auto` mode generates `secrets.token_urlsafe(16)` and persists it to `.dashboard_credential` (chmod 600)
2. `start.sh` parses it and exports `HERMES_DASHBOARD_BASIC_AUTH_USERNAME`/`HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` (start.sh:34-40)
3. The dashboard program inherits those env vars; the SSO middleware auto-redirect is patched out at image build (Dockerfile:111) so login goes to the password form at `/login`

The resolved credentials are printed by `./up.sh` and in the container's startup banner.

## WhatsApp Bridge (opt-in, security-sensitive)

The WhatsApp bridge is **excluded** from the image by default (Dockerfile:57 removes `/opt/hermes/scripts/whatsapp-bridge`). It uses [Baileys](https://github.com/WhiskeySockets/Baileys) to emulate a WhatsApp Web session — **anyone who messages your number gets full agent access** (terminal, filesystem, browser) without proper restrictions. See [upstream issue #15108](https://github.com/NousResearch/hermes-agent/issues/15108).

Enable at build time:

```bash
# Option 1: CLI flag
./build.sh --whatsapp

# Option 2: versions.env
ENABLE_WHATSAPP_BRIDGE=true
./build.sh
```

> **Warning:** If enabled, you **must** configure `WHATSAPP_ALLOWED_USERS` in `~/.hermes/.env` before starting the gateway — otherwise the bridge denies all incoming messages by default (README.md:305-307).

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

All three services are managed by supervisord as PID 1; `supervisorctl status` should show `hermes-gateway`, `hermes-dashboard`, `hermes-webui` all RUNNING (README.md:241).

## Access

| Service | URL | Description |
|---|---|---|
| Gateway | http://localhost:8642 | Agent gateway (CLI, Telegram, cron, tools) |
| WebUI | http://localhost:8787 | Browser-based chat interface |
| Dashboard | http://localhost:9119 | Monitoring/analytics (login: `DASHBOARD_CREDENTIAL`) |

## Migration from Multi-Container Setup

1. Stop the existing containers (hermes-agent + hermes-webui): `podman-compose down` / `docker compose down`
2. Build and start hermes-suite:
   ```bash
   cd hermes-suite
   ./build.sh
   ./up.sh
   ```
3. Existing `~/.hermes/` data is reused automatically — no migration needed (README.md:318-331)

## Tested Platforms

| Platform | Arch | OS | Runtime | Status |
|---|---|---|---|---|
| x86_64 (WSL2) | amd64 | Ubuntu 22.04 | Podman 3.4.4 | All 3 services running |
| x86_64 (WSL2) | amd64 | Ubuntu 22.04 | Docker CE 29.4.2 | All 3 services running |
| Jetson Orin NX 16GB | arm64 | Ubuntu 22.04 | Podman 3.4.4 | All 3 services running |

The `nousresearch/hermes-agent` base image provides multi-arch manifests; the same Dockerfile builds identically on both architectures (README.md:436-446).

## Troubleshooting

### Permission Errors on ~/.hermes

The container's `hermes` user is **UID 10000**. Under rootless Podman it maps to a host subuid (e.g. 109999) per `/etc/subuid`; under rootful Podman/Docker it is used directly.

**Rootless Podman:**
```bash
sudo chown -R 109999:109999 ~/.hermes
```

**Rootful Podman or Docker:**
```bash
sudo chown -R 10000:10000 ~/.hermes
```

Ownership is auto-corrected at startup when running as root; these commands are the fallback when warnings persist (README.md:339-352).

### WebUI Not Loading

```bash
podman exec hermes-suite /opt/hermes-webui/venv/bin/python -c "import yaml; print('OK')"
```

### Dashboard Connection Error

Ensure gateway is running with:
```bash
podman exec hermes-suite supervisorctl status
```

### Dashboard Asks for a Login

Expected since agent v2026.7.1. Use the `DASHBOARD_CREDENTIAL` you configured (or the value printed by `./up.sh`). Change it in `versions.env` and re-run `./up.sh`.

## Security

- WhatsApp bridge disabled by default (requires explicit opt-in via `--whatsapp` / `ENABLE_WHATSAPP_BRIDGE=true`; must set `WHATSAPP_ALLOWED_USERS`)
- Dashboard requires authentication since v2026.7.1 — change the default `admin:admin` before internet exposure
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
