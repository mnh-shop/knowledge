---
name: hermes-workspace-deployment
tags: [hermes, workspace, deployment, system-requirements]
description: Hermes Workspace deployment guide with system requirements and runtime configuration
---

# Hermes Workspace Deployment

## System Requirements

### Runtime

| Requirement | Minimum | Production Target |
|-------------|---------|-------------------|
| Node.js | 22+ | `node:22-slim` container |
| Python 3 | any modern 3.x | Required for PTY terminal helper (`scripts/pty-helper.py`) |
| tmux | recent | Required for swarm worker sessions on Linux/macOS |
| pnpm | latest | For building from source |
| Memory | 2GB heap | `--max-old-space-size=2048` |
| Disk | ~200MB | Installed (node_modules + dist) |

### Platform Support

- **Linux**: Full support (tmux, Python, Docker, Nix, systemd)
- **macOS**: Full support (tmux, Python, launchd, Homebrew)
- **Windows**: Partial (no tmux — uses native child processes for workers)

## Build Steps

```bash
pnpm install --frozen-lockfile
pnpm build     # Vite builds client + server into dist/
```

## Docker Setup

### Dockerfile (`sources/hermes-workspace/Dockerfile`)

- Multi-stage build with `node:22-slim`.
- Runtime includes python3, curl, tini, gosu for privilege drop.
- Entry point: `docker/entrypoint.sh` (handles UID/GID remapping via `HERMES_UID`/`HERMES_GID`, drops root via `gosu`).
- Command: `node --max-old-space-size=2048 server-entry.js`.
- Exposes port 3000.
- HEALTHCHECK: `curl -fsS http://localhost:3000/` every 30s.

### docker-compose.yml (`sources/hermes-workspace/docker-compose.yml`)

Two services:

1. **hermes-agent**: `nousresearch/hermes-agent:latest`, runs `gateway run`, exposes `127.0.0.1:8642:8642`.
2. **hermes-workspace**: `ghcr.io/outsourc-e/hermes-workspace:latest`, exposes `127.0.0.1:3000:3000`.

Volumes: `hermes-agent-data` (shared) and `hermes-workspace-files`. Internal Docker network DNS (`hermes-agent:8642`) for inter-service communication. `docker-compose.dev.yml` overlay for building workspace from source.

### Docker Networking

In the default docker-compose setup:
- All services on a shared Docker bridge network.
- Workspace reaches agent at `http://hermes-agent:8642` (Docker DNS).
- Agent dashboard at `http://hermes-agent:9119`.
- Both agent ports are only reachable within the Docker network (no host publish for :9119).
- Workspace port :3000 is published on `127.0.0.1:3000` (host loopback only).

For multi-host setups:
- Agent must set `API_SERVER_HOST=0.0.0.0` and `API_SERVER_KEY=<secret>`.
- Workspace must set `HERMES_API_URL=http://<agent-ip>:8642` and `HERMES_API_TOKEN=<same-secret>`.
- Workspace password required for remote access.
- Dashboard must also be reachable at the remote agent IP.

## Nix Support

- **package.nix**: Nix derivation using `stdenv.mkDerivation` with pnpm fetching, builds into `$out/lib/hermes-workspace`, creates `hermes-workspace` wrapper script.
- **module.nix**: NixOS module (`services.hermes-workspace`) with config options: port, host, hermesApiUrl, hermesDashboardUrl, passwordFile, cookieSecure, trustProxy, user/group, dataDir, extraEnvironment, environmentFile.

## macOS launchd

Template plist at `sources/hermes-workspace/macos/com.hermes.workspace.plist.template` with placeholders for NODE_BIN, INSTALL_DIR, PORT, HERMES_API_URL, HERMES_API_TOKEN. KeepAlive with restart on non-successful exit. Logs to `/tmp/hermes-workspace.{out,err}.log`.

## Electron

Desktop builds for macOS (DMG) and Windows (EXE) via electron-builder (`electron-builder.config.cjs`). Electron auto-update via `electron-updater`. Electron builds bundle the server as a single CJS file via esbuild.

## DevContainer

VSCode dev container support at `.devcontainer/devcontainer.json`.

## Configuration

### Config File Architecture

The workspace manages three configuration files under `~/.hermes/` (or `$HERMES_HOME`):

| File | Format | Purpose |
|------|--------|---------|
| `config.yaml` | YAML | Hermes agent configuration: provider, model, MCP servers, custom providers |
| `.env` | KEY=value | API keys and environment settings |
| `auth-profiles.json` | JSON | Authentication profiles (for multiple API credential sets) |

### Workspace Configuration Methods

1. **Environment variables** (set at workspace startup):
   - Workspace-specific settings (PORT, HOST, HERMES_PASSWORD, HERMES_API_URL, etc.)

2. **Config PATCH API** (`POST /api/hermes-config`):
   - Action-based patches: `set-default-model`, `set-api-key`, `remove-api-key`, `set-custom-provider`, `remove-custom-provider`.
   - Legacy format: `{ config: { ... }, env: { ... } }` — deep-merges into config.yaml and .env.

3. **MCP Server API** (`POST /api/mcp`):
   - Accepts `McpServerInput` with name, transportType, command/url, args, env, headers, auth, includeTools/excludeTools.
   - Written into `config.yaml mcp_servers.<name>`.

4. **Runtime Overrides** (persistent JSON at `~/.hermes/workspace-overrides.json`):
   - `claudeApiUrl` / `claudeDashboardUrl` — Set via UI connection settings, survives server restarts.

### Workspace Session Store

- Path: `~/.hermes/workspace-sessions.json`
- Format: `{ "tokens": { "<hex_token>": <expiry_unix_ms> } }`
- 30-day TTL, auto-expired on read, periodic sweep every 10 minutes.
- Persisted to file with mode 0600.

### Swarm Configuration Files

| File | Path | Purpose |
|------|------|---------|
| `swarm.yaml` | Project root | Worker roster (10 workers with roles, tools, skills) |
| `runtime.json` | `~/.hermes/profiles/<workerId>/runtime.json` | Per-worker runtime state |
| `swarm-mode.json` | `$(cwd)/.runtime/swarm-mode.json` | Auto/manual control mode toggle |
| Worker profiles | `~/.hermes/profiles/<workerId>/` | Per-worker Hermes Agent config |

## Ports and Network

| Port | Service | Default Bind | Protocol | Purpose |
|------|---------|--------------|----------|---------|
| 3000 | Hermes Workspace | `127.0.0.1` | HTTP | Web UI + API server |
| 8642 | Hermes Agent Gateway | `127.0.0.1` | HTTP | Gateway HTTP API |
| 9119 | Hermes Agent Dashboard | `127.0.0.1` | HTTP | Dashboard API |
| 18789 | Hermes Agent Gateway WebSocket | `127.0.0.1` | WebSocket | Messaging bus for live events |
| 10280 | Cloudflare Tunnel (optional) | `127.0.0.1` | HTTP | Remote-managed ingress point |

### Network Architecture

```
Internet / LAN
    |
    |-- Browser (HTTP to :3000)
    |-- Reverse Proxy (Traefik/Nginx) -> :3000 (optional, for TLS/domain)
    |-- Cloudflare Tunnel -> localhost:10280 -> workspace :3000 (optional)
    |-- Tailscale -> direct to :3000 (optional, with password)

Workspace Server (:3000)
    |
    |-- Hermes Agent Gateway (:8642 via HTTP)
    |   |-- /health, /v1/models, /v1/chat/completions
    |   |-- /api/mcp (when native)
    |
    |-- Hermes Agent Dashboard (:9119 via HTTP)
    |   |-- /api/sessions, /api/skills, /api/config
    |   |-- /api/jobs, /api/conductor, /api/plugins/kanban
    |   |-- /api/mcp (primary MCP path)
    |
    |-- Hermes Agent Gateway (:18789 via WebSocket)
    |   |-- RPC methods: sessions.usage, sessions.costs, etc.
    |   |-- Live event stream
    |
    |-- Direct subprocess (tmux/child_process) -> hermes workers
```

### Reverse Proxy Recommendations

- **Tailscale**: Direct connect to workspace :3000 with password auth.
- **Traefik/Nginx**: HTTPS termination, proxy to `http://127.0.0.1:3000`. Set `TRUST_PROXY=1` for IP classification. Set `COOKIE_SECURE=1` for Secure cookies.
- **Cloudflare Tunnel**: Connect to `http://localhost:10280`. Workspace auto-listens on `::1` for IPv6 compatibility.
- **Tailscale Funnel**: Works with password auth and `COOKIE_SECURE=1` for public HTTPS.

### Security

- **Default: loopback-only** (`HOST=127.0.0.1`). Server REFUSES to start on any non-loopback host without `HERMES_PASSWORD` set.
- **CSRF protection**: `requireJsonContentType()` on mutating POST requests.
- **Auth bypass**: Can be overridden with `HERMES_ALLOW_INSECURE_REMOTE=1` (not recommended).
- **Plain HTTP warning**: When running over plain HTTP in production mode, warns about Secure cookies being dropped by browsers. Set `COOKIE_SECURE=0` for LAN deployments.
- **SSRF protection**: MCP Hub generic-json source validates no private IPs via DNS resolution.
- **Gateway auth**: Bearer token via `HERMES_API_TOKEN`.
- **Dashboard auth**: Ephemeral session token scraped from dashboard root HTML (auto-refresh on 401).

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `3000` | Server listen port |
| `HOST` | `127.0.0.1` | Bind address (loopback default) |
| `HERMES_API_URL` | `http://127.0.0.1:8642` | Hermes Agent gateway URL |
| `HERMES_DASHBOARD_URL` | `http://127.0.0.1:9119` | Hermes Agent dashboard URL |
| `HERMES_API_TOKEN` | (empty) | Gateway bearer auth token |
| `HERMES_PASSWORD` | (empty) | Session password; REQUIRED on non-loopback |
| `HERMES_HOME` | `~/.hermes` | Hermes config directory |
| `HERMES_CLI_PATH` | `hermes` | Path to the `hermes` CLI binary |
| `HERMES_TMUX_BIN` | (detected) | Path to tmux binary |
| `COOKIE_SECURE` | auto | Force Secure flag on session cookies |
| `TRUST_PROXY` | 0 | Trust X-Forwarded-For headers |
| `HERMES_ALLOW_INSECURE_REMOTE` | 0 | Bypass password guard on non-loopback host |
| `HERMES_USE_RESPONSES` | 0 | Use `/v1/responses` Responses API streaming |
| `NODE_ENV` | `production` | Production mode |
| `VITE_HERMESWORLD_ENABLED` | 1 | Show HermesWorld link |
| `VITE_PLAYGROUND_WS_URL` | (public worker) | HermesWorld WebSocket hub URL |
| `STREAM_ACCEPTED_TIMEOUT_MS` | 120000 | SSE accepted state timeout |
| `STREAM_HANDOFF_TIMEOUT_MS` | 300000 | SSE handoff state timeout |

## Key Deployment Considerations

1. **tmux requirement**: The swarm worker system relies on tmux running inside the container. The `node:22-slim` image does NOT include tmux. To support swarm, either install tmux in the image, run workers outside the container, or deploy the workspace outside the container for full swarm support.

2. **Python requirement**: Needed for the PTY terminal helper (`scripts/pty-helper.py`). Ensure the image has python3 or set `PYTHON3_BIN` environment variable.

3. **SSE stability**: The workspace uses SSE (Server-Sent Events) for streaming. Host networking or proper reverse proxy SSE configuration (no buffering, `Connection: keep-alive`) is recommended to avoid connection drops.

4. **Privilege considerations**: Rootless Podman means UID/GID mapping must match the workspace container user (`workspace`, UID 10010). The entry point script auto-remaps UID/GID via `HERMES_UID`/`HERMES_GID`.

## Related

- [[hermes-workspace]] — Wiki entry
- [[hermes-workspace-architecture]] — System architecture
- [[hermes-workspace-api]] — REST API reference
- [[hermes-workspace-profile]] — Agent profile
- [[hermes-workspace-quadlet]] — Quadlet deployment
- [[hermes-workspace-mcp-hub]] — MCP hub implementation
- [[hermes-workspace-swarm-architecture]] — Swarm architecture
- [[hermes-agent-deployment]] — Agent deployment guide
