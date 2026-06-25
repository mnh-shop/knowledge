---
name: hermes-suite
tags: [agent-gateway, ai-llm, container, dashboard, docker, hermes, messaging, multi-platform, podman, typescript, wiki]
description: "Wiki entry for Hermes Suite: all-in-one Hermes container combining gateway, built-in dashboard, and browser-based WebUI (MIT)"
source: sources/hermes-suite/
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

Pre-built multi-arch images are available on [Docker Hub](https://hub.docker.com/r/ascensionoid/hermes-suite) (ascensionoid/hermes-suite). Automatic runtime detection — the same image works on both Podman and Docker CE without separate builds.

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

### Startup Sequence

1. `start.sh` entrypoint runs — handles UID/GID remapping for rootless Podman
2. Bootstraps config: copies default `.env` and `config.yaml` from Hermes Agent examples if empty
3. Launches supervisord (PID 1)
4. Supervisord manages all three services with automatic restart

## Build

```bash
# Using build helper (reads versions.env)
./build.sh

# Manual with pinned versions
podman build \
  --build-arg AGENT_VERSION=v2026.6.19 \
  --build-arg HERMES_WEBUI_VERSION=v0.51.625 \
  -t hermes-suite:2026.6.19-0.51.625 .
```

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
AGENT_VERSION=v2026.6.19
WEBUI_VERSION=v0.51.625
CONTAINER_RUNTIME=auto      # auto, podman, docker, docker-nolog
USE_SUDO=false
ENABLE_WHATSAPP_BRIDGE=false
```

## Integration with Core Systems

- **[[hermes-agent]]** — The agent runtime this suite packages (gateway, dashboard)
- **[[hermes-agent-docker]]** — Simpler Docker packaging (single service) compared to the all-in-one suite approach
- **[[clawpier]]** — Desktop GUI alternative for managing Hermes containers
- **[[hermzner]]** — Production deployment blueprint for Hermes on Hetzner (multi-container Podman, not suite)

## Related

- [[hermes-suite-architecture]] -- System architecture
- [[hermes-suite-deployment]] -- Deployment guide
- [[hermes-agent]] -- Core agent runtime
- [[hermes-agent-docker]] -- Simpler Docker packaging
- [[hermes-agent-deployment]] -- Agent deployment guide
- [[clawpier]] -- Desktop GUI alternative
- [[hermzner]] -- Production Hermes on Hetzner
- [[mission-control]] -- Web-based dashboard alternative

## Cross-project

- [[openclaw]] -- Comparable all-in-one agent suite
- [[podman]] -- Container runtime for suite deployment
- [[tank-os]] -- Bootc OS pattern comparable to suite approach
- [[n8n]] -- Workflow automation for Hermes suite integration
