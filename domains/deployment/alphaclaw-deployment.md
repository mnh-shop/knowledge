---
name: alphaclaw-deployment
tags: [alphaclaw, deployment, openclaw, container]
description: AlphaClaw — Deployment
source: sources/alphaclaw/
---

# AlphaClaw — Deployment

**Source:** `sources/alphaclaw/` · `sources/alphaclaw/README.md` · `sources/alphaclaw/lib/server/`

## Overview

AlphaClaw is the ops and setup layer around OpenClaw. It provides a browser-based Setup UI, gateway lifecycle management, watchdog recovery, channel integrations, and an OpenAI-compatible `/v1` proxy. The primary deployment target is Docker/Linux; one-click templates exist for Railway and Render (Render's template is maintained in the official `render-examples/openclaw-render-template` repo, `README.md:65`). A macOS desktop app (DMG) is also published at `updates.alphaclaw.md` (`README.md:23`). macOS local *development* is not supported (`README.md:28`).

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
| Node.js | 22.22.3+ (22.x), 24.15.0+ (24.x), or 25.9.0+ (25.x) per `engines` gate (`package.json:53-54`) | 22 LTS |

## Deployment Steps

### 1. Quick Deploy (One-Click Templates)

| Platform | URL | Notes |
|----------|-----|-------|
| Render | [Deploy Button](https://render.com/templates/alphaclaw) | Official template maintained at `render-examples/openclaw-render-template`. Render sponsors AlphaClaw — use code `RENDER-ALPHACLAW` for $50 in credits (`README.md:26,63-65`) |
| Railway | [Deploy Button](https://railway.com/deploy/openclaw-fast-start?referralCode=jcFhp_) | Upgrade to Hobby plan (8 GB RAM) post-deploy; Trial-plan memory limits cause OOM crashes during normal operation (`README.md:73`) |

Set `SETUP_PASSWORD` at deploy time. The welcome wizard handles provider credentials, GitHub repo pairing, and channel configuration on first visit.

A macOS desktop app is available for local use: `https://updates.alphaclaw.md/desktop/prod/alphaclaw-mac-latest.dmg` (`README.md:23`).

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
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - GITHUB_WORKSPACE_REPO=${GITHUB_WORKSPACE_REPO}
      # Optional integrations
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-}
      - DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN:-}
      - SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN:-}
      - REMOTE_MCP_URL=${REMOTE_MCP_URL:-}
      - REMOTE_MCP_API_TOKEN=${REMOTE_MCP_API_TOKEN:-}
      - REMOTE_MCP_NAME=${REMOTE_MCP_NAME:-remote}
      - REMOTE_MCP_PROXY_URL=${REMOTE_MCP_PROXY_URL:-}
      - ALPHACLAW_GIT_SHIM_PATH=${ALPHACLAW_GIT_SHIM_PATH:-/usr/local/bin/git}
      - ALPHACLAW_GIT_ASKPASS_PATH=${ALPHACLAW_GIT_ASKPASS_PATH:-}
      - ALPHACLAW_SKIP_SYSTEM_CRON_INSTALL=${ALPHACLAW_SKIP_SYSTEM_CRON_INSTALL:-}
      - WATCHDOG_AUTO_REPAIR=${WATCHDOG_AUTO_REPAIR:-}
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

**Official image base** (`README.md:84-95`): `node:22-slim` plus `git`, `curl`, `procps`, `cron`, `tini`; entrypoint `tini -- alphaclaw start` with `ALPHACLAW_ROOT_DIR=/data`.

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

Full source of truth: `sources/alphaclaw/README.md:154-174`.

| Variable | Required | Description |
|----------|----------|-------------|
| `SETUP_PASSWORD` | **Yes** | Password for the Setup UI (single-user auth) |
| `OPENCLAW_GATEWAY_TOKEN` | Auto-generated | Auth token for gateway proxy communication |
| `GITHUB_TOKEN` | **Yes** (for git sync) | GitHub PAT for the workspace repo |
| `GITHUB_WORKSPACE_REPO` | **Yes** (for git sync) | GitHub repo for workspace sync (e.g. `owner/repo`) |
| `TELEGRAM_BOT_TOKEN` | No | Telegram bot token for channel pairing |
| `DISCORD_BOT_TOKEN` | No | Discord bot token for channel pairing |
| `SLACK_BOT_TOKEN` | No | Slack bot token for channel pairing (Socket Mode) |
| `WATCHDOG_AUTO_REPAIR` | No | Enable auto-repair on crash (`true`/`false`) |
| `WATCHDOG_NOTIFICATIONS_DISABLED` | No | Disable watchdog notifications (`true`/`false`) |
| `PORT` | No | Server port (default `3000`; port `18789` is refused — reserved for the OpenClaw gateway) |
| `ALPHACLAW_ROOT_DIR` | No | Override root directory (default: `/data` in containers, `~/.alphaclaw` locally) |
| `ALPHACLAW_SKIP_SYSTEM_CRON_INSTALL` | No | Skip writes to `/etc/cron.d` while keeping cron config (`true`/`false`) |
| `ALPHACLAW_GIT_SHIM_PATH` | No | Install the managed git auth shim at this path and prepend its dir to runtime `PATH` (default `/usr/local/bin/git`) |
| `ALPHACLAW_GIT_ASKPASS_PATH` | No | Install the git askpass helper at this path (default `$TMPDIR/alphaclaw-git-askpass.sh`) |
| `TRUST_PROXY_HOPS` | No | Trusted proxy hop count for correct client IP |
| `REMOTE_MCP_URL` | No | Remote MCP server URL (writes managed `mcp.servers.<name>` entry in `openclaw.json` on gateway start when paired with `REMOTE_MCP_API_TOKEN`) |
| `REMOTE_MCP_API_TOKEN` | No | Bearer token for the remote MCP server (persisted in `openclaw.json` as `${REMOTE_MCP_API_TOKEN}` reference, never plaintext) |
| `REMOTE_MCP_NAME` | No | Key under `mcp.servers.<name>` (default `remote`; e.g. `sure`, `notion`) |
| `REMOTE_MCP_PROXY_URL` | No | Same-host scanning proxy URL for MCP callbacks (e.g. `pipelock mcp proxy --listen <url> --upstream <url>`) |
| `GOOGLE_CLIENT_ID` | No | Google OAuth client ID for Workspace integration |
| `GOOGLE_CLIENT_SECRET` | No | Google OAuth client secret for Workspace integration |

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

### 8. Git Auth Shim + Askpass

AlphaClaw installs a managed **git shim** so workspace repo pushes authenticate with `GITHUB_TOKEN` without storing credentials on disk. On `start`, `bin/alphaclaw.js:953-991`:

1. Copies `lib/scripts/git-askpass` to `ALPHACLAW_GIT_ASKPASS_PATH` (default `$TMPDIR/alphaclaw-git-askpass.sh`).
2. Renders `lib/scripts/git` to `ALPHACLAW_GIT_SHIM_PATH` (default `/usr/local/bin/git`), substituting the resolved real git path, the OpenClaw repo root, and the askpass path.
3. Prepends the shim's directory to runtime `PATH` so all child processes use it.

The askpass helper answers username/password prompts with `x-access-token` / `${GITHUB_TOKEN:-}`. The `git-sync` CLI additionally writes a per-PID askpass script and runs git with `GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=...` (`bin/alphaclaw.js:325-357`). No PAT is ever embedded in the remote URL — tokenized origins are scrubbed on boot (`bin/alphaclaw.js:771-788`).

### 9. Hourly Git Sync (cron)

AlphaClaw ships `lib/setup/hourly-git-sync.sh` and installs a system cron entry `/etc/cron.d/openclaw-hourly-sync` (`bin/alphaclaw.js:694-732`) with a default schedule of `0 * * * *` (hourly), configurable via the cron config JSON (`<root>/.openclaw/cron/system-sync.json`, schedule + enabled flags). Behavior:

- The script sources `<root>/.env` for cron's minimal environment, so persisted envars (including `GITHUB_TOKEN`, `GITHUB_WORKSPACE_REPO`) are honored.
- Disable writes to `/etc/cron.d` with `ALPHACLAW_SKIP_SYSTEM_CRON_INSTALL=true` (the managed script still exits cleanly when sync is disabled).
- The sync schedule is also editable from the Setup UI (General tab → repo sync schedule) via `/api/sync-cron`.
- Logs land in `/var/log/openclaw-hourly-sync.log`.

### 10. CLI Reference (`bin/alphaclaw.js`)

| Command | Description |
|---|---|
| `alphaclaw start [--root-dir <path>] [--port <number>]` | Start the server (Setup UI + gateway manager); verifies Node floor, requires `SETUP_PASSWORD`, refuses port `18789` |
| `alphaclaw git-sync -m "message" [-f <path>]` | Commit and push the OpenClaw workspace via `GITHUB_TOKEN` (optional `--file` to sync a single file) |
| `alphaclaw telegram topic add --thread <id> --name <text> [--system <text>] [--agent <id>] [--group <id>]` | Register a Telegram topic mapping and update concurrency |
| `alphaclaw doctor finding complete --id <id> --run <run-id> --token <token>` | Mark a queued Doctor finding fixed after verification |
| `alphaclaw version` / `alphaclaw help` | Print version / show help |

On boot `start` also: symlinks `~/.openclaw` → `<root>/.openclaw`, seeds `.env` from `lib/setup/env.template`, installs the `gog` CLI for Google Workspace if missing, installs a `systemctl` shim in Docker, reconciles channels/plugins into `openclaw.json`, and applies legacy-config migrations.

### 11. macOS Desktop App

A native desktop app is distributed as a DMG: `https://updates.alphaclaw.md/desktop/prod/alphaclaw-mac-latest.dmg` (`README.md:23`). The desktop app wraps the same AlphaClaw server locally. Note: macOS **local development from source** is not supported (`README.md:28`) — the Docker/Linux deployment path remains the primary target.

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
