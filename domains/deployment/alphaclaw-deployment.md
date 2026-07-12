---
name: alphaclaw-deployment
tags: [alphaclaw, deployment, openclaw, container]
description: AlphaClaw — Deployment
source: sources/alphaclaw/
---

# AlphaClaw — Deployment

**Source:** `sources/alphaclaw/` · `sources/alphaclaw/README.md` · `sources/alphaclaw/lib/server/`

## Overview

AlphaClaw is the ops and setup layer around OpenClaw. It provides a browser-based Setup UI, gateway lifecycle management, watchdog recovery, channel integrations, and an OpenAI-compatible `/v1` proxy. The primary deployment target is Docker/Linux; one-click templates exist for Railway and Render. macOS local development is not supported.

Deployment spins up two processes in one container (or two containers):
- **AlphaClaw server** (Express on port 3000) — Setup UI + Gateway Manager + Watchdog + Webhooks
- **OpenClaw gateway** (managed child process on 127.0.0.1:18789) — spawned, monitored, and proxied by AlphaClaw

## Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 4 GB | 8 GB (Railway Hobby plan+) |
| CPU | 1 core | 2 cores |
| Storage | 2 GB | 10 GB (workspace + SQLite DBs) |
| Container runtime | Docker or Podman | Docker CE 24+ |
| Node.js | 22.14+ | 22 LTS |

## Deployment Steps

### 1. Quick Deploy (One-Click Templates)

| Platform | URL | Notes |
|----------|-----|-------|
| Railway | [Deploy Button](https://railway.com/deploy/openclaw-fast-start?referralCode=jcFhp_) | Upgrade to Hobby plan (8 GB RAM) post-deploy |
| Render | [Deploy Button](https://render.com/deploy?repo=https://github.com/chrysb/openclaw-render-template) | Manual deploy, full stack |

Set `SETUP_PASSWORD` at deploy time. The welcome wizard handles provider credentials, GitHub repo pairing, and channel configuration on first visit.

### 2. Docker Compose

```yaml
version: '3.8'
services:
  alphaclaw:
    image: ghcr.io/chrysb/alphaclaw:latest
    container_name: alphaclaw
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - SETUP_PASSWORD=${SETUP_PASSWORD:?required}
      - OPENCLAW_GATEWAY_TOKEN=${OPENCLAW_GATEWAY_TOKEN}
      # Optional integrations
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-}
      - DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN:-}
      - SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN:-}
      - REMOTE_MCP_URL=${REMOTE_MCP_URL:-}
      - REMOTE_MCP_API_TOKEN=${REMOTE_MCP_API_TOKEN:-}
    volumes:
      - alphaclaw_data:/data
      # Mount workspace for Git sync
      - alphaclaw_workspace:/workspace
    healthcheck:
      test: ["CMD", "curl", "-f", "http://127.0.0.1:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

volumes:
  alphaclaw_data:
    driver: local
  alphaclaw_workspace:
    driver: local
```

### 3. Quadlet Unit (Podman)

Save as `~/.config/containers/systemd/alphaclaw.container`:

```ini
[Container]
Image=ghcr.io/chrysb/alphaclaw:latest
ContainerName=alphaclaw
PublishPort=3000:3000
Volume=alphaclaw-data:/data
Volume=alphaclaw-workspace:/workspace
Environment=SETUP_PASSWORD=%%
Environment=OPENCLAW_GATEWAY_TOKEN=%%
Environment=TELEGRAM_BOT_TOKEN=%%
Environment=DISCORD_BOT_TOKEN=%%
Environment=SLACK_BOT_TOKEN=%%
HealthCmd=curl -f http://127.0.0.1:3000/health
HealthInterval=30s
HealthRetries=3
AutoUpdate=registry

[Install]
WantedBy=default.target
```

Create the systemd service:

```bash
systemctl --user daemon-reload
systemctl --user enable --now alphaclaw.service
```

### 4. Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SETUP_PASSWORD` | **Yes** | Password for the Setup UI (single-user auth) |
| `OPENCLAW_GATEWAY_TOKEN` | Auto-generated | Auth token for gateway proxy communication |
| `TELEGRAM_BOT_TOKEN` | No | Telegram bot token for channel pairing |
| `DISCORD_BOT_TOKEN` | No | Discord bot token for channel pairing |
| `SLACK_BOT_TOKEN` | No | Slack bot token for channel pairing |
| `REMOTE_MCP_URL` | No | Remote MCP server URL (registered as `mcp.servers.remote` in OpenClaw) |
| `REMOTE_MCP_API_TOKEN` | No | Auth token for the remote MCP server |
| `REMOTE_MCP_PROXY_URL` | No | Same-host scanning proxy URL for MCP callbacks |
| `GOOGLE_CLIENT_ID` | No | Google OAuth client ID for Workspace integration |
| `GOOGLE_CLIENT_SECRET` | No | Google OAuth client secret for Workspace integration |
| `ALPHACLAW_ROOT_DIR` | No | Override root directory (default: `/data`) |

### 5. Runtime Architecture

```
┌─────────────────────────────────────────────────────┐
│                   AlphaClaw                         │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │          Express Server (port 3000)             │ │
│  │  ┌─────────┐ ┌──────────┐ ┌───────────────┐   │ │
│  │  │  Setup  │ │Watchdog  │ │  Webhooks     │   │ │
│  │  │  UI API │ │Manager   │ │  API + Logs   │   │ │
│  │  └────┬────┘ └────┬─────┘ └───────┬───────┘   │ │
│  │       │           │               │            │ │
│  │  ┌────▼───────────▼───────────────▼────────┐   │ │
│  │  │        Auth  ·  Proxy  ·  Routers       │   │ │
│  │  └────────────────────┬────────────────────┘   │ │
│  └───────────────────────┼────────────────────────┘ │
│                          │                          │
│           http-proxy     │  child process            │
│                          ▼                          │
│              ┌─────────────────────┐                │
│              │ OpenClaw Gateway    │                │
│              │ 127.0.0.1:18789    │                │
│              └──────────┬──────────┘                │
│                         │                           │
│              ┌──────────▼──────────┐                │
│              │  /data/.openclaw/   │                │
│              │  .env               │                │
│              │  logs/   alphaclaw.json              │
│              └─────────────────────┘                │
└─────────────────────────────────────────────────────┘
```

The container mounts `/data` for all persistent state. Everything that must survive redeploys (OpenClaw workspace, SQLite databases, credentials, logs) lives under `/data`.

### 6. Watchdog Behavior

AlphaClaw runs a watchdog that:
- Periodically checks gateway health via `openclaw health`
- Detects crashes and manages crash-loop thresholds (default: 3 crashes in 300s)
- Optionally runs `openclaw doctor --fix --yes` for auto-repair
- Logs all incidents to a SQLite-backed event log
- Sends notifications to configured channels (Telegram, Discord, Slack)

### 7. Upgrades

```bash
# In-place update via Setup UI
# Or manually:
docker compose pull alphaclaw
docker compose up -d alphaclaw

# Via Quadlet (AutoUpdate=registry):
systemctl --user restart alphaclaw.service
```

## Persistent Storage

| Path | Contents |
|------|----------|
| `/data/.openclaw/` | OpenClaw workspace (Git-managed) |
| `/data/.env` | Environment variables |
| `/data/alphaclaw.json` | AlphaClaw configuration |
| `/data/logs/` | Gateway and watchdog logs |
| `/data/*.db` | SQLite databases (watchdog events, webhooks, usage, Gmail) |

## Related

- [[alphaclaw]] — AlphaClaw wiki entry (architecture, features, interfaces)
- [[openclaw]] — The AI assistant platform AlphaClaw wraps and manages
- [[podman]] — Container runtime for Quadlet deployment
- [[openclaw-container]] — OpenClaw container image
- [[clawpier]] — Desktop GUI for managing OpenClaw Docker containers
- [[tank-os]] — Fedora bootc image deployment for OpenClaw
- [[mission-control]] — Dashboard that can connect to OpenClaw as a gateway
