---
name: hermes-suite
tags: [agent, hermes-agent, agent-gateway, container, dashboard, docker, messaging, multi-platform, orchestration, podman, wiki, hermes-suite]
description: "Wiki entry for Hermes Suite: all-in-one Hermes container combining gateway, built-in dashboard, and browser-based WebUI (MIT)"
source: sources/hermes-suite/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Hermes Suite — All-in-One Hermes Container Image

| Field | Value |
|---|---|
| **Origin** | [sunnysktsang/hermes-suite](https://github.com/sunnysktsang/hermes-suite) |
| **License** | MIT |
| **Stack** | Docker/Podman, Python, Supervisor, Hermes Agent, Hermes WebUI |
| **Source** | `sources/hermes-suite/` |
| **Wanted** | Single-container deployment combining Hermes gateway, built-in dashboard, and browser-based WebUI |

## What it is

Hermes Suite packages three Hermes services into a single Docker/Podman container managed by supervisord:

| Service | Port | Description |
|---|---|---|
| hermes-gateway | 8642 | Agent gateway (CLI, Telegram, cron, tools) |
| hermes-dashboard | 9119 | Monitoring/analytics dashboard (built-in) |
| hermes-webui | 8787 | Browser-based chat interface |

Pre-built multi-arch images are available on [Docker Hub](https://hub.docker.com/r/ascensionoid/hermes-suite) (ascensionoid/hermes-suite). Automatic runtime detection — the same image works on both Podman and Docker CE without separate builds. Since hermes-agent v2026.7.1 the dashboard requires authentication; Hermes Suite wires this up via `DASHBOARD_CREDENTIAL` (default `admin:admin`).

## Why It Exists

Podman v3.4.4 cannot share UID/GID between multiple containers easily. The standard multi-container setup (hermes-agent + hermes-webui + hermes-dashboard) requires each container to run as the same user to share `~/.hermes`. Hermes Suite solves this by running all three services in **one container** via supervisord, with automatic UID/GID remapping.

## Architecture

```
┌─────────────────────────────────────────────┐
│           hermes-suite container             │
│  ┌────────── supervisord (PID 1) ─────────┐ │
│  │                                        │ │
│  │  [hermes-gateway]   port 8642          │ │
│  │    hermes gateway run                  │ │
│  │                                        │ │
│  │  [hermes-dashboard] port 9119          │ │
│  │    hermes dashboard --host 0.0.0.0     │ │
│  │                                        │ │
│  │  [hermes-webui]     port 8787          │ │
│  │    python server.py                    │ │
│  │                                        │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  Volumes:                                    │
│  ~/.hermes  →  /opt/data                     │
│  ~/workspace → /workspace                    │
│  /etc/localtime                              │
└──────────────────────────────────────────────┘
```

The 7-stage Dockerfile builds on the `nousresearch/hermes-agent` base: base image → system packages (sudo, git, curl, nano, net-tools, procps…) → Playwright Chromium for the browser toolset (+ optional WhatsApp bridge) → supervisord in a dedicated venv at `/opt/supervisor` → hermes-webui cloned at a pinned tag into `/opt/hermes-webui/venv` → supervisord config + `start.sh` + **SSO middleware patch** → env/labels/runtime config.

The SSO patch (`Dockerfile:111`) disables the dashboard's auto-SSO redirect in `hermes_cli/dashboard_auth/middleware.py`: upstream auto-redirects to `/auth/login` (OAuth start) when a single provider is registered, but BasicAuthProvider is password-only and raises `NotImplementedError` there. Patching `auto = None` sends unauthenticated requests straight to the password form at `/login`.

### Startup Sequence

1. `start.sh` entrypoint runs — detects Docker vs Podman via `is_docker()` (checks `/.dockerenv` first, then `/proc/1/cgroup`, start.sh:23-27)
2. Privilege model diverges: Docker keeps supervisord as root (children drop to hermes via `user=`), Podman drops to hermes via `s6-setuidgid` re-exec (start.sh:128-146)
3. Bootstraps config: copies default `.env`, `config.yaml`, `SOUL.md` from Hermes Agent examples if empty, syncs bundled skills, cleans stale `gateway.pid`/`gateway.lock` (setup_hermes, start.sh:43-90)
4. Sets up dashboard basic auth from `DASHBOARD_CREDENTIAL` (setup_dashboard_auth, start.sh:34-40)
5. Launches supervisord (PID 1) which manages all three services with automatic restart

## Build

```bash
# Using build helper (reads versions.env)
./build.sh

# Manual with pinned versions
podman build \
  --build-arg AGENT_VERSION=v2026.7.7.2 \
  --build-arg HERMES_WEBUI_VERSION=v0.52.76 \
  -t hermes-suite:2026.7.7.2-0.52.76 .
```

`build.sh` flags (build.sh:38-59):

| Flag | Effect |
|---|---|
| `--agent vX.Y.Z` | Override `AGENT_VERSION` |
| `--webui vX.Y.Z` | Override `WEBUI_VERSION` |
| `--podman` / `--docker` | Force the build runtime |
| `--docker-nolog` | Build with docker, supervisord logs patched to `/dev/null` (restored after build) |
| `--sudo` / `--no-sudo` | Toggle rootful sudo prefix |
| `--whatsapp` | Set `ENABLE_WHATSAPP_BRIDGE=true` — include WhatsApp bridge in the image (default excluded) |

CI (`.github/workflows/build.yml`) builds and pushes multi-arch images (`linux/amd64,linux/arm64`) to Docker Hub on `v*` tag pushes; the agent/webui versions are parsed from the compound tag.

## Run

```bash
# Create network
podman network create --subnet 10.99.0.0/24 agent_net

# Start
podman-compose up -d

# Or with helper
./up.sh

# View logs
./logs.sh

# Check service status (troubleshooting)
podman exec hermes-suite supervisorctl status

# Stop
./down.sh
```

## Configuration

All config stored in `~/.hermes/` on the host (mounted as `/opt/data` inside container):

```
~/.hermes/
  .env            — API keys (OPENAI_API_KEY, TELEGRAM_TOKEN, etc.)
  config.yaml     — Model, toolsets, agent settings
  SOUL.md         — Agent personality
  skills/         — Custom skills
  memories/       — Persistent memory
  webui/          — WebUI state (sessions, workspace)
```

### Version Management

Edit `versions.env` to pin specific versions:

```
AGENT_VERSION=v2026.7.7.2
WEBUI_VERSION=v0.52.76
CONTAINER_RUNTIME=auto      # auto, podman, docker, docker-nolog
USE_SUDO=false
DASHBOARD_CREDENTIAL=admin:admin    # admin:admin | auto | user:password
ENABLE_WHATSAPP_BRIDGE=false
```

| Setting | Options | Default | Description |
|---|---|---|---|
| `AGENT_VERSION` | date-based (`v2026.7.7.2`) | pinned | hermes-agent image tag |
| `WEBUI_VERSION` | semver (`v0.52.76`) | pinned | hermes-webui git tag |
| `CONTAINER_RUNTIME` | `auto`, `podman`, `docker`, `docker-nolog` | `auto` | which runtime helper scripts use |
| `USE_SUDO` | `true`, `false` | `false` | run commands with sudo (rootful mode) |
| `DASHBOARD_CREDENTIAL` | `admin:admin`, `auto`, `user:pass` | `admin:admin` | dashboard login credential |
| `ENABLE_WHATSAPP_BRIDGE` | `true`, `false` | `false` | include WhatsApp bridge in built image |

### Dashboard Authentication

Since hermes-agent v2026.7.1 the dashboard requires authentication (the old `--insecure` flag is a no-op). Set `DASHBOARD_CREDENTIAL` in `versions.env` (versions.env:56):

- `admin:admin` — default, works immediately (change for internet exposure)
- `auto` — auto-generate a random password, persisted to `.dashboard_credential` (in the repo dir) and printed by `./up.sh` (up.sh:24-34)
- `user:password` — your own credentials

`start.sh` parses the credential and exports `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` / `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` for the dashboard's BasicAuthProvider (start.sh:34-40). The login is printed in the startup banner and in `./up.sh` output.

### WhatsApp Bridge (opt-in)

The WhatsApp bridge is **not included** in the image by default — it uses [Baileys](https://github.com/WhiskeySockets/Baileys) to emulate a WhatsApp Web session, and without proper configuration **anyone who messages your number gets full agent access** (terminal, filesystem, browser). See upstream [hermes-agent#15108](https://github.com/NousResearch/hermes-agent/issues/15108).

```bash
# Option 1: CLI flag
./build.sh --whatsapp

# Option 2: set in versions.env
ENABLE_WHATSAPP_BRIDGE=true
./build.sh
```

> **Warning:** If you enable the bridge you **must** configure `WHATSAPP_ALLOWED_USERS` in `~/.hermes/.env` before starting the gateway — otherwise the bridge denies all incoming messages by default (README.md:305-307).

## Migration from Multi-Container Setup

1. Stop the existing containers (hermes-agent + hermes-webui)
2. Build and start hermes-suite: `./build.sh && ./up.sh`
3. Existing `~/.hermes/` data is reused automatically — no migration needed

## Tested Platforms

| Platform | Arch | OS | Runtime | Status |
|---|---|---|---|---|
| x86_64 (WSL2) | amd64 | Ubuntu 22.04 | Podman 3.4.4 | All 3 services running |
| x86_64 (WSL2) | amd64 | Ubuntu 22.04 | Docker CE 29.4.2 | All 3 services running |
| Jetson Orin NX 16GB | arm64 | Ubuntu 22.04 | Podman 3.4.4 | All 3 services running |

The `nousresearch/hermes-agent` base image ships multi-arch manifests (amd64 + arm64); the Dockerfile builds identically on both architectures (README.md:436-446).

## Troubleshooting

- **Service status:** `podman exec hermes-suite supervisorctl status` — verify gateway/dashboard/webui are all RUNNING (README.md:241)
- **Permission errors on `~/.hermes`:** container runs as UID 10000, which maps to a host subuid (e.g. 109999) per `/etc/subuid` under rootless Podman → `sudo chown -R 109999:109999 ~/.hermes`. Rootful Podman/Docker auto-correct ownership; if needed `sudo chown -R 10000:10000 ~/.hermes` (README.md:339-352)
- **Dashboard asks for a login:** expected since v2026.7.1 — use the `DASHBOARD_CREDENTIAL` you configured (README.md:378-382)
- **Dashboard connection error:** dashboard needs the gateway running first — check `supervisorctl status`

## Integration with Core Systems

- **[[hermes-agent]]** — The agent runtime this suite packages (gateway, dashboard)
- **[[hermes-agent-docker]]** — Simpler Docker packaging (single service) compared to the all-in-one suite approach
- **[[clawpier]]** — Desktop GUI alternative for managing Hermes containers
- **[[hermzner]]** — Production deployment blueprint for Hermes on Hetzner (multi-container Podman, not suite)

## Related

- [Architecture](domains/architecture/hermes-suite-architecture.md) — Container layout, supervisord program map, runtime/privilege model, build flags
- [Deployment](domains/deployment/hermes-suite-deployment.md) — Build/run workflows, dashboard auth, WhatsApp bridge, CI
- [[hermes-agent]] -- Core agent runtime
- [[hermes-agent-docker]] -- Simpler Docker packaging
- [Agent deployment guide](domains/deployment/hermes-agent-deployment.md) -- Hermes agent deployment
- [[clawpier]] -- Desktop GUI alternative
- [[hermzner]] -- Production Hermes on Hetzner
- [[mission-control]] -- Web-based dashboard alternative

## Cross-project

- [[openclaw]] -- Comparable all-in-one agent suite
- [[podman]] -- Container runtime for suite deployment
- [[tank-os]] -- Bootc OS pattern comparable to suite approach
- [[n8n]] -- Workflow automation for Hermes suite integration
