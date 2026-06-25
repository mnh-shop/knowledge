---
name: mission-control-deployment
tags: [mission-control, deployment, dashboard]
description: Mission Control Deployment
---

# Mission Control Deployment
**Source:** `sources/mission-control/`

## Overview

Mission Control is fully self-contained with no external service dependencies. It can be deployed via local install, Docker Compose, hardened Docker overlay, or standalone Next.js export. The data store is SQLite (no Postgres, no Redis, no S3 required).

---

## Requirements

### Runtime

- **Node.js >= 22** (engines field in package.json; .nvmrc pins the version)
- **pnpm 10.29.3** (pinned via package.json#packageManager and Dockerfile corepack)
- **Native compilation toolchain**: python3, make, g++ (for better-sqlite3 and node-pty native addons)
- better-sqlite3 must be compiled for the exact Node.js version -- switching Node versions requires `pnpm rebuild better-sqlite3`

### Docker

- Docker with BuildKit support (docker compose v2)
- Docker 20.10+ on Linux for `host-gateway` extra_hosts support
- Multi-arch image building via buildx for non-amd64 targets

### External Dependencies

Zero. Mission Control has no required external services. OpenClaw gateway is optional -- in standalone mode, core CRUD features work and direct API dispatch handles task execution using provider API keys (Anthropic, OpenAI, or local LLM endpoints).

---

## Local Install

```bash
bash install.sh [--docker|--local] [--port PORT] [--data-dir DIR] [--dir INSTALL_DIR] [--skip-openclaw]
```

The installer auto-detects the OS (Linux/macOS) and prerequisites (Docker or Node 20+), then auto-selects Docker over local when available. It clones the repo from GitHub (or updates an existing clone via `git fetch --tags`), generates a secure `.env` via `scripts/generate-env.sh`, and deploys in the chosen mode.

### --local Mode

1. Runs `pnpm install --frozen-lockfile`
2. Rebuilds `better-sqlite3` native addon
3. Runs `pnpm build`
4. Launches `node .next/standalone/server.js` via nohup with PID tracking

On Linux with systemctl, creates a systemd unit at `/etc/systemd/system/mission-control.service` pointing at the standalone server, with `Restart=on-failure` and `EnvironmentFile` pointing to `.env`.

### --docker Mode

1. Runs `docker compose up -d --build`
2. Polls for health via `docker compose ps` or HTTP `GET /login` (up to 60s timeout)

### Secret Auto-Generation

On first run, `generate-env.sh` creates a `.env` with random `AUTH_PASS` (24-char alphanumeric), `API_KEY` (32-char hex), and `AUTH_SECRET` (32-char alphanumeric), `chmod 600`. In Docker, `docker-entrypoint.sh` also auto-generates `AUTH_SECRET` and `API_KEY` at container start if missing, persisting them to `/app/.data/.generated-secrets` for container restarts.

---

## Docker Deployment

### Basic

```bash
docker compose up -d
```

To run without a gateway (standalone mode):

```bash
docker compose --profile standalone up -d
```

### Dockerfile Structure

Multi-stage build from `node:22.22.0-slim`:

- **base**: pins pnpm 10.29.3 via corepack
- **deps**: copies only package.json + pnpm-lock.yaml, installs native compilation toolchain, runs `pnpm install --frozen-lockfile`
- **build**: copies deps and source, sets ARG/ENV pairs for all `NEXT_PUBLIC_*` variables, runs `pnpm build`
- **runtime**: fresh `node:22.22.0-slim`, installs curl/ca-certificates/python3/git/make/g++/procps for agent runtime installers and system-monitor APIs. Creates non-root user `nextjs` (uid 1001). Copies `.next/standalone`, `.next/static`, `public/`, `schema.sql`, and node-pty native artifacts. Creates `/app/.data` with correct ownership.

Healthcheck: inline script hitting `/api/status?action=health` on localhost:3000 every 30s, 5s timeout, 10s start period, 3 retries.

Entrypoint: `docker-entrypoint.sh` sources `.env`, loads persisted secrets, auto-generates missing `AUTH_SECRET`/`API_KEY`, persists to `.data/.generated-secrets` with chmod 600, then `exec node server.js`.

### docker-compose.yml Key Configuration

- Port mapping: `MC_PORT` defaults to 3000, mapped to container PORT
- Gateway host: defaults to `host.docker.internal:18789` with `extra_hosts` mapping on Linux
- Volumes: `mc-data` named volume at `/app/.data`, optional read-only OpenClaw mount
- Container hardening: `read_only: true`, tmpfs for `/tmp` and `.next/cache`, `cap_drop ALL` plus `cap_add NET_BIND_SERVICE`, `security_opt no-new-privileges:true`
- Resource limits: 512MB memory, 1.0 CPU, 256 pids
- `restart: unless-stopped`
- Separate `mission-control-standalone` service (`--profile standalone`) with `NEXT_PUBLIC_GATEWAY_OPTIONAL=true`
- `mc-net` bridge network

### Published Image

Published to GHCR with multi-arch support (linux/amd64, linux/arm64) via Docker buildx. OCI labels include source repo URL, description, MIT license, and version.

---

## Hardened Docker Deployment

```bash
docker compose -f docker-compose.yml -f docker-compose.hardened.yml up -d
```

This overlay stack adds three production hardening layers:

1. **Structured logging**: JSON-file log driver with `max-size 10m`, `max-file 3` (log rotation)

2. **Security environment variables**:
   - `MC_ALLOWED_HOSTS=localhost,127.0.0.1` -- strict hostname allowlist
   - `MC_COOKIE_SECURE=1` -- HTTPS-only cookies
   - `MC_COOKIE_SAMESITE=strict` -- CSRF protection
   - `MC_ENABLE_HSTS=1` -- HTTP Strict-Transport-Security header

3. **Internal-only network**: Replaces default bridge with `mc-internal` (internal: true). Service moves from `mc-net` (external-accessible) to `mc-internal` with no external connectivity. A reverse proxy must sit on an external-facing network for gateway access.

### Host-Level Hardening (Recommended)

- ufw firewall (allow SSH only)
- NTP time sync via systemd-timesyncd
- unattended-upgrades for automatic security patches
- fail2ban for brute-force protection
- `/tmp` mounted noexec
- LUKS-encrypted data volume
- AppArmor or SELinux MAC framework

---

## Standalone Mode

Next.js is configured with `output: 'standalone'` in `next.config.js`. This produces a self-contained bundle in `.next/standalone/` containing only production JS, necessary node_modules, and a minimal `server.js`.

### Management Scripts

**start-standalone.sh**: Sources `.env`, copies `.next/static` and `public/` into the standalone bundle, then `exec node server.js` with `HOSTNAME=0.0.0.0` and `MISSION_CONTROL_DATA_DIR` defaulting to project-root `.data`.

**deploy-standalone.sh**: Full zero-downtime in-place update:
1. Fetches target branch (`git fetch` + `--ff-only merge`)
2. Stops existing server (lsof/ss/pgrep)
3. Removes `.next`
4. Runs `pnpm install --frozen-lockfile` and `pnpm build` with temporary build-runtime data directory
5. Starts new server and verifies by fetching login page, extracting CSS asset path, confirming CSS file exists on disk, and verifying Content-Type is text/css

### Usage

```bash
pnpm start:standalone          # local launch
BRANCH=xyz PORT=3000 pnpm deploy:standalone  # in-place update
```

Direct execution `node .next/standalone/server.js` works after build, but `start-standalone.sh` is preferred because it syncs static assets into the standalone bundle.

### Important Note

`outputFileTracingExcludes` in `next.config.js` explicitly excludes `.data/` and `.git/` from the trace. Without this, Git treats the standalone directory as its own working tree, causing `git status --porcelain` to fail during self-update (every unbundled file shows as deleted).

### Security Headers (next.config.js)

`X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy: camera/microphone/geolocation all denied`. HSTS is conditional on production mode and `MC_DISABLE_HSTS` or `MC_ENABLE_HSTS`. CSP is set dynamically per-request in `src/proxy.ts` with a nonce.

---

## Configuration

### Env File

Environment variables are documented in `.env.example` (160+ lines). Secret auto-generation on first run handles `AUTH_PASS`, `API_KEY`, and `AUTH_SECRET`.

### Key Environment Groups

**Authentication:**
- `AUTH_USER` / `AUTH_PASS` -- admin credentials (seed from env or `/setup` UI)
- `AUTH_PASS_B64` -- base64-encoded password override (handles passwords with `#`)
- `AUTH_SECRET` -- NextAuth encryption key
- `API_KEY` -- bearer token for headless/REST/MCP access via `x-api-key` header
- `GOOGLE_CLIENT_ID` / `NEXT_PUBLIC_GOOGLE_CLIENT_ID` -- optional Google OAuth

**Network Security:**
- `MC_ALLOWED_HOSTS` -- strict hostname allowlist (default: localhost,127.0.0.1,::1)
- `MC_ALLOW_ANY_HOST` -- override to allow any host (production: not recommended)
- `MC_COOKIE_SECURE` -- HTTPS-only cookies
- `MC_COOKIE_SAMESITE` -- CSRF protection (default: strict)
- `MC_ENABLE_HSTS` -- HTTP Strict-Transport-Security activation
- `MC_PROXY_AUTH_HEADER` / `MC_PROXY_AUTH_DEFAULT_ROLE` / `MC_PROXY_AUTH_TRUSTED_IPS` -- trusted reverse proxy header auth

**OpenClaw Gateway Connectivity (two sets):**
- Server-side: `OPENCLAW_GATEWAY_HOST`/`PORT`/`TOKEN` -- MC backend reaches the gateway
- Browser-side: `NEXT_PUBLIC_GATEWAY_HOST`/`PORT`/`PROTOCOL`/`URL`/`REVERSE_PROXY`/`CLIENT_ID` -- user browser connects for WebSocket
- `NEXT_PUBLIC_GATEWAY_OPTIONAL=true` -- run without gateway (standalone mode)
- IMPORTANT: `NEXT_PUBLIC_*` values are baked into the client JS bundle at build time. Changing them requires `pnpm rebuild`. For runtime gateway URL configuration, Advanced Settings on the login page stores the URL in localStorage.
- MC auto-detects Docker-internal hostnames (host.docker.internal, host-gateway) and rewrites WebSocket URLs to the browser's own hostname, so no `NEXT_PUBLIC_GATEWAY_HOST` is needed for local Docker usage.

**Data Paths:**
- `MISSION_CONTROL_DATA_DIR` -- default `.data/`, can be absolute path (recommended for standalone to survive rebuilds)
- `MISSION_CONTROL_TOKENS_PATH` -- tokens file location
- `OPENCLAW_STATE_DIR` -- preferred, exact path to OpenClaw state (avoids double-nesting bug with `OPENCLAW_HOME`)
- `OPENCLAW_HOME` -- legacy, appends `.openclaw` automatically

**Direct API Dispatch (gateway-free task execution):**
- `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `LOCAL_LLM_ENDPOINT`, `LOCAL_LLM_API_KEY`
- `MC_HOST_SESSION_MODE` -- coexisting with host Claude Code sessions (coexist/block-active/nudge)

**Data Retention (all optional, in days, 0 = forever):**
- `MC_RETAIN_ACTIVITIES_DAYS`, `MC_RETAIN_AUDIT_DAYS`, `MC_RETAIN_LOGS_DAYS`, `MC_RETAIN_NOTIFICATIONS_DAYS`, `MC_RETAIN_PIPELINE_RUNS_DAYS`, `MC_RETAIN_TOKEN_USAGE_DAYS`

**Self-Contained Operator Paths (Linux host):**
- docker-compose.yml bind-mounts `$HOME/.local/bin`, `$HOME/.bun`, `$HOME/.claude`, `$HOME/.claude.json`, `$HOME/.local/share/claude` into the container
- Container runs as uid 1000 (nextjs user) to match typical Linux host uid
- Host `~/.local/bin` takes PATH precedence over baked-in fallback copies

---

## Data Directory

### Location

Defaults to `.data/` in the project root (host) or Docker named volume `mc-data` at `/app/.data`. Gitignored. Overridable via `MISSION_CONTROL_DATA_DIR`.

### Contents

- `mission-control.db` -- SQLite database (WAL mode) with all application state
- `mission-control-tokens.json` -- runtime token storage (optional)
- `.generated-secrets` -- auto-generated AUTH_SECRET and API_KEY (Docker only, chmod 600)
- `mc.log` / `mc-err.log` -- standalone server logs (local deployment)
- `mc.pid` -- process ID for standalone server management
- `backups/` -- automatic daily backups (enabled via `MC_AUTO_BACKUP=1` or UI toggle)

### Database Path Resolution

1. Defaults to `MISSION_CONTROL_DATA_DIR/mission-control.db`
2. If `MISSION_CONTROL_DATA_DIR` differs from `.data/` and the target DB doesn't exist but source does, it migrates the database (sqlite3 .backup or rsync), plus migrates tokens.json and backups/
3. Schema bootstrapped from `src/lib/schema.sql` (copied into Docker image at build time)

### Backup Configuration

Automatic daily backups if `MC_AUTO_BACKUP=1` is set. Data retention variables control pruning of old records. In Docker, the named volume `mc-data` persists across container restarts and rebuilds.

---

## Quadlet Deployment Notes

Mission Control does not ship native Quadlet `.container` files, but the existing Docker infrastructure translates directly to Quadlet because the image is a standard OCI-compliant container.

### Key Translation Points

- **Image**: The multi-arch OCI image from the Dockerfile uses `node:22.22.0-slim`, runs as non-root user `nextjs` (uid 1001)
- **Port**: 3000
- **Volume**: Named volume for `/app/.data`
- **Capabilities**: `NET_BIND_SERVICE` required; `no-new-privileges`; drop all other capabilities
- **Rootfs**: `read_only` with tmpfs for `/tmp` and `.next/cache`
- **Environment**: `AUTH_USER`, `AUTH_PASS` or `AUTH_PASS_B64`, `API_KEY`, `AUTH_SECRET`, `OPENCLAW_GATEWAY_*`
- **Gateway connectivity**: Requires `--add-host=host.docker.internal:host-gateway`
- **Resource limits**: 512MB memory recommended minimum (2GB if using /chat with node-pty), 1.0 CPU, 256 pids
- **Health check**: HEALTHCHECK from Dockerfile maps to Quadlet `HealthCmd`, `HealthInterval` (30s), `HealthTimeout` (5s), `HealthRetries` (3), `HealthStartPeriod` (10s)
- **Hardened profile**: Internal-only network, JSON logging rotation, strict hostname allowlist, secure cookies, HSTS
- **Agent runtime provisioning**: Container needs curl, python3, git, make, g++ (installed in runtime stage)

### Basic Quadlet .container Reference

```container
[Unit]
Description=Mission Control
After=network-online.target

[Container]
Image=ghcr.io/mission-control/mission-control:latest
EnvironmentFile=/path/to/.env
ContainerName=mc
PublishPort=3000:3000
Volume=mc-data:/app/data:Z
Volume=%h/.config/mc:/app/.config:ro
AddHost=host.docker.internal:host-gateway
Exec=node /app/server.js
HealthCmd=curl -f http://localhost:3000/api/status?action=health
HealthInterval=30s
HealthTimeout=5s
HealthRetries=3
HealthStartPeriod=10s

[Service]
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

A full Quadlet `.container` file for this project is available at `/Users/admin1/Documents/knowledge/assets/deployment/mission-control-quadlet.md`.

## Related

- [[mission-control]] -- Project overview
- [[mission-control-architecture]] -- Architecture context for deployment
- [[mission-control-quadlet]] -- Quadlet container configuration
- [[mission-control-profile]] -- Deployment quick reference
- [[mission-control-api]] -- API reference for the deployed service
