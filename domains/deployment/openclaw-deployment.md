---
name: openclaw-deployment
tags: [acp, agent-gateway, ai-llm, cli, container, deployment, desktop-app, docker, git, live-canvas, mcp, messaging, openclaw, personal-assistant, plugin-sdk, podman, quadlet, storage, systemd, typescript]
description: OpenClaw Deployment Guide
---

# OpenClaw Deployment Guide

**Source:** `sources/openclaw/`
**Raw:** `raw/openclaw/openclaw.xml` (49M)
**Codegraph:** `graphs/openclaw/` (1.0G DB)

Comprehensive deployment and operations guide for OpenClaw -- a self-hosted AI agent gateway and runtime, written in TypeScript on Node.js.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Docker Deployment](#docker-deployment)
- [Quadlet Deployment (Rootless Podman)](#quadlet-deployment-rootless-podman)
- [Configuration](#configuration)
- [Secrets and Credentials](#secrets-and-credentials)
- [Daemon Management](#daemon-management)
- [Workspace Setup](#workspace-setup)
- [Updates and Migrations](#updates-and-migrations)
- [Backup and Restore](#backup-and-restore)
- [Troubleshooting](#troubleshooting)
- [Key Source Files](#key-source-files)

---

## System Requirements

### Runtime

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Node.js | v22.19+ | Node 24 |
| Runtime engine | Node.js (primary) | Bun (supported but not production target) |
| Package manager | pnpm (via Corepack in Docker) | pnpm |

### Memory

| Context | Requirement |
|---------|-------------|
| Docker build (pnpm install) | 2 GB RAM minimum (1 GB may OOM-kill) |
| Production steady-state | 1-2 GB RAM |
| Docker low-memory VM | `NODE_OPTIONS=--max-old-space-size=1536` |
| Gateway default heap | 256 MB |

### Disk

| Path | Notes |
|------|-------|
| Container image | ~1 GB |
| `~/.openclaw` state | Grows with sessions, media, SQLite DBs, rolling logs |
| Key hotspots | `media/`, session JSONL files, SQLite DBs, plugin roots, `/tmp/openclaw/` logs |

### OS Support

- Linux (amd64, arm64)
- macOS (Intel and Apple Silicon)
- Windows (primary and WSL)

### Docker

- Docker Engine or Docker Desktop with Compose v2
- BuildKit enabled (Dockerfile uses `RUN --mount=type=cache` BuildKit-only syntax)
- Podman 4.0+ supported as alternative, including Quadlet

### Networking

| Port | Purpose | Note |
|------|---------|------|
| 18789 | Gateway WebSocket/HTTP | Configurable via `--port` or `gateway.port` |
| 18790 | Bridge port | Secondary internal port |
| 3978 | MSTeams channel port | Only needed if Teams channel is active |
| 5353 (UDP) | Bonjour/mDNS discovery | Auto-disabled in Docker (bridge networking does not forward mDNS multicast) |

---

## Installation

### via npm/pnpm/bun

```bash
# Global npm install
npm install -g openclaw@latest

# Or via pnpm
pnpm add -g openclaw@latest

# Or via bun
bun add -g openclaw@latest
```

The CLI binary is registered as `openclaw` via the `bin.openclaw` field in `package.json`, pointing to `openclaw.mjs`. The npm package ships as ECMAScript modules (`"type": "module"`) and includes `npm-shrinkwrap.json` for reproducible dependency installs.

### Post-Install

```bash
# Run the interactive setup wizard
openclaw onboard

# Or validate/repair existing configuration
openclaw doctor

# Register as a system service
openclaw gateway install
```

### Updating

```bash
# Recommended: auto-detect install type and update
openclaw update

# Switch to beta channel
openclaw update --channel beta

# Switch to git checkout (dev)
openclaw update --channel dev
```

`openclaw update` coordinates package swap with Gateway service lifecycle. Direct npm/pnpm/bun global updates may leave the running Gateway in an inconsistent state -- stop the Gateway service first if using manual package manager commands.

### Docker Images

Pre-built Docker images are published at `ghcr.io/openclaw/openclaw`:

| Tag | Description |
|-----|-------------|
| `latest` | Latest stable release |
| `main` | Latest from main branch |
| `<version>` | Specific version (e.g. `2026.2.26`) |

### Pre-built Images for Alternative Platforms

OpenClaw builds for linux/amd64 and linux/arm64. Check `ghcr.io/openclaw/openclaw` for available tags.

---

## Docker Deployment

### Image Details

- **Base**: `docker.io/library/node:24-bookworm-slim` (pinned to SHA256 digest)
- **Entrypoint**: `tini -s --` (init system for signal handling and zombie reaping)
- **Default command**: `node openclaw.mjs gateway`
- **User**: Non-root `node` user (uid 1000)
- **Labels**: `org.opencontainers.image.source=https://github.com/openclaw/openclaw`
- **Healthcheck**: Every 3 minutes, timeout 10s, start-period 15s, 3 retries

### Dockerfile Build Stages

The multi-stage Dockerfile (`Dockerfile`) has:

1. **`base` stage**: Node 24 bookworm-slim, installs pnpm, system dependencies
2. **`build` stage**: Installs all dependencies, runs TypeScript build
3. **`runtime` stage**: Minimal image with pnpm, tini, node user, and application files

### Build Arguments

| Argument | Effect |
|----------|--------|
| `OPENCLAW_EXTENSIONS` | Space/comma-separated plugin dirs (e.g. "diagnostics-otel,matrix") |
| `OPENCLAW_INSTALL_BROWSER=1` | Adds Chromium + Xvfb for browser automation (~300 MB) |
| `OPENCLAW_INSTALL_DOCKER_CLI=1` | Adds Docker CLI for sandbox container management (~50 MB) |
| `OPENCLAW_IMAGE_APT_PACKAGES` | Extra apt packages at build time |
| `OPENCLAW_IMAGE_PIP_PACKAGES` | Extra Python packages at build time |

### docker-compose.yml Structure

Two services:

1. **`openclaw-gateway`** -- Long-running daemon
2. **`openclaw-cli`** -- Ephemeral CLI sidecar sharing gateway network namespace

```yaml
services:
  openclaw-gateway:
    image: ghcr.io/openclaw/openclaw:latest
    container_name: openclaw-gateway
    ports:
      - "18789:18789"
      - "18790:18790"
    volumes:
      - ~/.openclaw:/home/node/.openclaw
      - ~/.openclaw/workspace:/home/node/.openclaw/workspace
      - ~/.openclaw-auth-profile-secrets:/home/node/.config/openclaw
    environment:
      - OPENCLAW_GATEWAY_BIND=lan
      - NODE_ENV=production
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - NET_RAW
      - NET_ADMIN
    init: true
    extra_hosts:
      - "host.docker.internal:host-gateway"
    restart: unless-stopped

  openclaw-cli:
    image: ghcr.io/openclaw/openclaw:latest
    profiles: ["cli"]
    network_mode: "service:openclaw-gateway"
    volumes:
      - ~/.openclaw:/home/node/.openclaw
      - ~/.openclaw-auth-profile-secrets:/home/node/.config/openclaw
    environment:
      - OPENCLAW_GATEWAY_BIND=lan
    command: ["node", "openclaw.mjs"]
```

### Volumes (Three Bind Mounts)

1. `~/.openclaw:/home/node/.openclaw` -- config, state, sessions, plugins
2. `~/.openclaw/workspace:/home/node/.openclaw/workspace` -- agent workspaces
3. `~/.openclaw-auth-profile-secrets:/home/node/.config/openclaw` -- auth profile encryption keys (**CRITICAL** -- without these, OAuth tokens cannot be decrypted)

For sandbox: mount `/var/run/docker.sock` when `OPENCLAW_INSTALL_DOCKER_CLI=1`.

### Health Check

The Dockerfile includes:

```
HEALTHCHECK --interval=3m --timeout=10s --start-period=15s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:18789/healthz').then((r) => process.exit(r.ok ? 0 : 1)).catch(() => process.exit(1))"
```

### Deployment Platforms

| Platform | Config |
|----------|--------|
| Fly.io | `fly.toml` -- shared-cpu-2x, 2048 MB, persistent volume `/data` |
| Render.com | `render.yaml` -- starter plan, `/health` probe, 1 GB disk |
| Kubernetes | `docs/install/kubernetes.md` |
| Railway | `docs/install/railway.mdx` |
| Northflank | `docs/install/northflank.mdx` |
| GCP, Oracle, Hetzner, Raspberry Pi | Dedicated install docs in source tree |

---

## Quadlet Deployment (Rootless Podman)

For Quadlet (Podman systemd-native) deployment, see the comprehensive asset at [[assets/deployment/openclaw-quadlet.md]].

Summary:

```bash
# Create Quadlet directory
mkdir -p ~/.config/containers/systemd/

# Create .container file (see quadlet asset for full content)
# Reload and start
systemctl --user daemon-reload
systemctl --user start openclaw-gateway.service
systemctl --user enable openclaw-gateway.service
```

### Key Differences from Docker Compose

| Aspect | Docker Compose | Quadlet |
|--------|---------------|---------|
| Lifecycle | `docker compose` CLI | systemd units |
| Secrets | `.env` file or Docker secrets | `podman secret create` + `Secret=` directive |
| Networking | Compose network | `Network=container:` or pod networking |
| Logging | `docker compose logs` | `journalctl --user` |

---

## Configuration

### Config File

Default: `~/.openclaw/openclaw.json5` (JSON5 format -- supports comments, trailing commas)

Legacy fallback paths (in order):
- `~/.openclaw/clawdbot.json`
- `~/.clawdbot/openclaw.json`
- `~/.clawdbot/clawdbot.json`

Config path overrides (highest priority): `OPENCLAW_CONFIG_PATH` env var, derived from `OPENCLAW_STATE_DIR`.

### State Directory

Default: `~/.openclaw` (overridable via `OPENCLAW_STATE_DIR`)

Contains:
- Config file (`openclaw.json5`)
- Agent auth profiles (`agents/<agentId>/agent/auth-profiles.json`)
- Session transcripts (JSONL files)
- SQLite databases (shared state + per-agent)
- Media files
- Plugin package roots
- OAuth credentials (`credentials/oauth.json`)
- Rolling logs

### Config Structure (openclaw.json5)

```json5
{
  gateway: {
    port: 18789,
    bind: "lan",              // lan | loopback | tailnet | auto | custom
    auth: { mode: "token" },  // token | password | none | trusted-proxy
    controlUi: { allowedOrigins: [] },
    customBindHost: "0.0.0.0",
    tailscale: { mode: "off" },
    mode: "local",
  },
  agents: {
    // Agent definitions, defaults (model, workspace, sandbox), CLI backends
  },
  channels: {
    // Channel plugin configurations (Telegram bot token, Discord token, etc.)
    defaults: { allowFrom: "all", dmPolicy: "open" },
  },
  plugins: {
    // Installed plugin entries, plugin-scoped config, allowlist/denylist
  },
  models: {
    // Model provider configurations with auth, endpoints, model lists
    providers: {},
  },
  secrets: {
    // Secret provider configurations (file, exec, env providers)
    providers: {},
  },
  env: {
    // Environment variable definitions applied at load time
  },
  update: {
    channel: "stable",
    auto: { enabled: true, stableDelayHours: 6, stableJitterHours: 12 },
  },
  diagnostics: {
    // Diagnostic flags (timeline, OpenTelemetry, Prometheus)
  },
  hooks: {
    // Config hooks for lifecycle events
  },
  meta: {
    // Auto-generated: lastTouchedVersion, lastTouchedAt
  },
}
```

### Config Loading Flow

See `src/config/io.ts` (2984 lines):

1. Load `.env` files (process env, `./.env`, `~/.openclaw/.env`)
2. Resolve config path from env or default
3. Read file (JSON or JSON5), parse
4. Resolve `$include` directives (modular composition across files; restricted to config directory or `OPENCLAW_INCLUDE_ROOTS`)
5. Apply `config.env` block to `process.env` BEFORE `${VAR}` substitution
6. Resolve `${VAR}` env references (missing vars become warnings, not fatal)
7. Strip shipped plugin install records (migrated to plugin index)
8. Validate against Zod schemas
9. Load shell env fallback if configured
10. Materialize runtime config

### Config Write Safety

- **Atomic file replacement** via temp file + rename (`replaceFileAtomic`)
- **SHA256 hash-based conflict detection** -- rejects concurrent writes
- **Backup rotation** before writes (`maintainConfigBackups`)
- **Audit logging** for every write (path, hash, size, timestamp, process info)
- **`${VAR}` reference preservation** -- does not replace `${ANTHROPIC_API_KEY}` with resolved value
- **Clobber protection** -- rejects writes that shrink config >50%, remove `gateway.mode`, or lack metadata

### Env File Precedence (highest to lowest)

1. Process environment
2. `./.env` (CWD)
3. `~/.openclaw/.env`
4. `openclaw.json` `env` block

Existing non-empty process env vars are NOT overridden by dotenv loading.

### Key Environment Variables

| Variable | Purpose |
|----------|---------|
| `OPENCLAW_GATEWAY_TOKEN` | Gateway auth token (auto-generated if empty) |
| `OPENCLAW_GATEWAY_PASSWORD` | Alternative password auth |
| `OPENCLAW_GATEWAY_PORT` | Listen port (default 18789) |
| `OPENCLAW_GATEWAY_BIND` | Bind mode (lan/loopback/tailnet/auto/custom) |
| `OPENCLAW_STATE_DIR` | State directory override |
| `OPENCLAW_CONFIG_PATH` | Explicit config file path |
| `OPENCLAW_HOME` | Home directory override (tilde expansion) |
| `OPENCLAW_INCLUDE_ROUTES` | Colon-separated path list for `$include` resolution |
| `OPENCLAW_LOAD_SHELL_ENV` | Import keys from login shell profile |
| `OPENCLAW_AUTH_PROFILE_SECRET_DIR` | Docker host-side encryption key directory |
| Provider API keys | `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, etc. |
| Channel tokens | `TELEGRAM_BOT_TOKEN`, `DISCORD_BOT_TOKEN`, `SLACK_BOT_TOKEN`, etc. |

### CLI Config Mutation

```bash
openclaw config set agents.defaults.model "claude-sonnet-4-20250514"
openclaw config unset channels.telegram
openclaw config set --batch-json '[{"path":"gateway.bind","value":"lan"}]'
```

---

## Secrets and Credentials

### Storage Locations

| Content | Location |
|---------|----------|
| Auth profiles (OAuth tokens, API keys) | `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` (SQLite for newer installs) |
| Gateway auth token/password | `openclaw.json` or env vars |
| Channel credentials | `openclaw.json` or env vars |
| OAuth credentials | `~/.openclaw/credentials/oauth.json` |
| Auth profile encryption keys | `~/.config/openclaw/` (separate mount for Docker) |

### Secret Providers (SecretRef System)

Three provider types for resolving secrets at runtime (`src/secrets/`):

1. **File provider** (`type: "file"`): Read secret from a file path
2. **Exec provider** (`type: "exec"`): Execute a command to resolve secret (e.g., `op read`, `doppler run`)
3. **Env provider** (`type: "env"`): Resolve from an environment variable name

### Example: Exec Provider with 1Password

```json5
{
  secrets: {
    providers: {
      "my-vault": {
        type: "exec",
        command: ["op", "read", "op://vault/item/credential"],
      },
    },
  },
  gateway: {
    auth: {
      token: { $secret: { provider: "my-vault" } },
    },
  },
}
```

### Secrets Configuration

```bash
# Interactive walk through all secret sources
openclaw secrets configure

# Apply secrets to config, auth stores, env files
openclaw secrets apply
```

The `configure` command builds a `SecretsApplyPlan` describing every target and the value to write. The plan is preflighted by resolving all SecretRefs first, then applied atomically.

### Best Practices

- For Docker deployments, prefer env var injection for secrets
- Use `--password-file` for Gateway CLI password arguments to avoid process-list exposure
- Auth profile encryption key directory must be persisted separately from the state directory in Docker
- SecretRef-based exec providers (e.g., 1Password CLI) are recommended for production

---

## Daemon Management

OpenClaw manages the Gateway as a platform-native service.

### Service Lifecycle Commands

```bash
openclaw gateway install      # Register the service
openclaw gateway start        # Start the service
openclaw gateway stop         # Stop the service (--disable for persistent stop)
openclaw gateway restart      # Restart the service
openclaw gateway uninstall    # Remove the service
openclaw gateway status       # Query service state
openclaw gateway health       # Health check via WebSocket
```

### Platform Support

| Platform | Mechanism | Config Path |
|----------|-----------|-------------|
| Linux | systemd user service | `~/.config/systemd/user/openclaw-gateway.service` |
| macOS | LaunchAgent | `~/Library/LaunchAgents/ai.openclaw.gateway.<profile>.plist` |
| Windows | Scheduled Task | Via `schtasks` |

### macOS LaunchAgent Details

- Plist: `~/Library/LaunchAgents/ai.openclaw.gateway.<profile>.plist`
- Environment file: `<stateDir>/service-env/<label>.env` (mode 0600)
- Env wrapper script: `<stateDir>/service-env/<label>-env-wrapper.sh`
- Uses `launchctl bootstrap` / `launchctl bootout` for lifecycle
- `RunAtLoad` + `KeepAlive` for automatic restart
- Stderr to `/dev/null`, stdout to `<stateDir>/logs/gateway.log`

### Gateway Restart Behavior

| Command | Behavior |
|---------|----------|
| `--safe` | Preflights active work, defers restart until completion |
| `--safe --skip-deferral` | Same preflight but bypasses deferral (escape hatch) |
| `--force` | Immediate restart, no active-work drain |
| `SIGUSR1` | In-process restart (when `commands.restart` enabled) |
| `SIGINT`/`SIGTERM` | Graceful stop (no terminal state restoration) |

### Gateway Status

| Flag | Behavior |
|------|----------|
| (default) | Service state + WebSocket connect + auth capability |
| `--require-rpc` | Full read-scope RPC probe (non-zero on failure) |
| `--no-probe` | Service-only view (no connectivity check) |
| `--deep` | System-level scan, config validation, plugin manifest warnings |
| `--json` | Machine-readable output |

---

## Workspace Setup

### Onboarding Wizard

The `openclaw onboard` command (see `src/wizard/setup.ts`) orchestrates initial configuration:

1. Risk acknowledgment
2. Config snapshot read
3. Existing config handling (keep/modify/reset)
4. Flow selection: QuickStart or Advanced
5. Gateway mode (local or remote)
6. Workspace directory (default `~/.openclaw/workspace`)
7. Auth provider selection (OpenAI, Anthropic, Google, OpenRouter, etc.)
8. Model selection
9. Gateway configuration (port, bind, auth, Tailscale)
10. Channel setup (Telegram, Discord, Slack, WhatsApp, etc.)
11. Search configuration (Brave, Perplexity, Firecrawl, etc.)
12. Skills configuration
13. Plugin configuration
14. Hooks setup

### Channel Setup

```bash
openclaw channels add --channel telegram --token "<bot-token>"
openclaw channels add --channel discord --token "<bot-token>"
openclaw channels login    # Interactive QR login (WhatsApp, Signal)
```

### Workspace Directory

- Default: `~/.openclaw/workspace` (or `$OPENCLAW_WORKSPACE_DIR`)
- Holds agent session data, file attachments, temporary files
- Must be writable by the gateway process user (uid 1000 in Docker)
- Persisted via Docker bind mount in container deployments

---

## Updates and Migrations

### Update Methods

| Method | Command |
|--------|---------|
| Recommended | `openclaw update` |
| Re-run installer | `curl -fsSL https://openclaw.ai/install.sh \| bash` |
| Manual npm | `npm install -g openclaw@latest` (stop gateway first) |
| Docker | `docker pull ghcr.io/openclaw/openclaw:latest && docker compose up -d` |

### Update Channels

| Channel | Behavior |
|---------|----------|
| `stable` | Default. `stableDelayHours` (6) + `stableJitterHours` (12) for spread rollout |
| `beta` | Every `betaCheckIntervalHours` (1 hour), applies immediately |
| `dev` | Git checkout from `main`, no automatic apply |

### Auto-Update Configuration

```json5
{
  update: {
    channel: "stable",
    auto: {
      enabled: true,
      stableDelayHours: 6,
      stableJitterHours: 12,
      betaCheckIntervalHours: 1,
    },
  },
}
```

Disable: `OPENCLAW_NO_AUTO_UPDATE=1`.

### Migration Paths

| Migration | Description |
|-----------|-------------|
| Config version detection | `meta.lastTouchedVersion` compared on read; warning if version difference is significant |
| Plugin index migration | Shipped `plugins.installs` records auto-migrated to plugin index (v2026.4+) |
| Legacy entries | `plugins.entries` migrated to Canonical Install Record (v2026.x) |
| Legacy config paths | `.clawdbot/` paths detected and migrated on first read |
| Provider auth | Legacy `provider.<id>` format migrates to `models.providers.<id>` |
| `openclaw doctor` auto-fixes | Legacy config keys, service env drift, plugin compatibility, auth profile upgrades, dead channel cleanup |

### Rollback

```bash
# npm
npm install -g openclaw@<previous-version>

# Git
git checkout <previous-commit> && pnpm install && pnpm build

# Docker
docker pull ghcr.io/openclaw/openclaw:<previous-version> && docker compose up -d

# After rollback
openclaw doctor && openclaw gateway restart
```

---

## Backup and Restore

### Built-in Backup Command

```bash
openclaw backup create                          # Full backup
openclaw backup create --output ~/Backups       # Custom output dir
openclaw backup create --dry-run --json         # Preview only
openclaw backup create --verify                 # Verify archive after creation
openclaw backup create --no-include-workspace   # State only, no workspace files
openclaw backup create --only-config            # Config file only
openclaw backup verify ./archive.tar.gz          # Validate existing archive
```

### What Gets Backed Up

1. State directory (`~/.openclaw/`) -- agent auth profiles, session state, installed plugins (minus `node_modules/`), config files
2. Active config file (`openclaw.json`) -- separate entry, deduplicated if inside state dir
3. Credentials directory (`~/.openclaw/credentials/`) -- OAuth tokens when outside state dir
4. Workspace directories (from config `agents.*.workspace`) -- opt-out via `--no-include-workspace`

### Excluded from Backup

- Active agent session transcripts
- Cron run logs and rolling logs
- Delivery queues, socket/pid/temp files
- Live-mutation durable queue temp files
- Plugin `node_modules/` directories (rebuildable)

### Archive Format

- Timestamped `.tar.gz` (ISO 8601 local time in filename)
- Includes embedded `manifest.json` with resolved source paths and archive layout
- Never overwrites existing archives (hard-link publish or exclusive copy)

### Restore Procedure

1. Restore config file: extract `openclaw.json` to `~/.openclaw/`
2. Restore state directory: extract `~/.openclaw/` contents
3. Restore workspace directories as needed
4. Reinstall plugins with missing dependencies: `openclaw plugins update <id>` or `openclaw plugins install <spec> --force`
5. Restore auth profile encryption keys from `~/.config/openclaw/` (**critical path** -- without encryption keys, OAuth tokens cannot be decrypted)
6. Run `openclaw doctor` to validate config and repair migration gaps
7. Restart gateway: `openclaw gateway restart`

### Manual Backup (Non-Docker)

```bash
tar -czf openclaw-backup.tar.gz \
  ~/.openclaw/ \
  ~/.config/openclaw/ \
  ~/.openclaw/workspace/
```

### Manual Backup (Docker)

```bash
tar -czf openclaw-backup.tar.gz \
  ~/.openclaw/ \
  ~/.openclaw/workspace/ \
  ~/.openclaw-auth-profile-secrets/
```

---

## Troubleshooting

### Primary Diagnostics

```bash
# Comprehensive health check and repair
openclaw doctor

# Machine-readable config validation
openclaw doctor --lint --json
```

### Gateway Health Commands

```bash
openclaw gateway status                       # Service state + connectivity
openclaw gateway status --deep                # System scan + plugin validation
openclaw gateway health                       # Liveness/readiness check
openclaw gateway probe                        # Network connectivity debug
openclaw gateway stability                    # Recent diagnostic stability events
openclaw gateway diagnostics export           # Shareable diagnostics zip
```

### Log Locations

| Platform | Location |
|----------|----------|
| macOS LaunchAgent | `~/.openclaw/logs/gateway.log` |
| Linux systemd | `journalctl --user -u openclaw-gateway` |
| Docker | `docker compose logs openclaw-gateway` |
| Rolling logs | `<stateDir>/logs/` |
| Stability bundles | `<stateDir>/logs/stability/openclaw-stability-*.json` |

### Startup Profiling

```bash
OPENCLAW_GATEWAY_STARTUP_TRACE=1 openclaw gateway
OPENCLAW_GATEWAY_RESTART_TRACE=1 openclaw gateway restart
OPENCLAW_DIAGNOSTICS=timeline OPENCLAW_DIAGNOSTICS_TIMELINE_PATH=/tmp/timeline.jsonl openclaw gateway
```

### Common Issues

#### EACCES on config file (Docker)
Host bind mount owned by wrong uid. The image runs as `node` (uid 1000).
```bash
sudo chown -R 1000:1000 /path/to/openclaw-config
```

#### Gateway unreachable from host (Docker bridge)
Gateway binds to loopback by default. With port mapping, set:
```bash
OPENCLAW_GATEWAY_BIND=lan
```

#### Bonjour/mDNS crash loops in Docker
Docker bridge does not forward mDNS multicast. OpenClaw auto-sets `OPENCLAW_DISABLE_BONJOUR=1` in Docker.

#### OOM-killed during build (exit 137)
Needs 2 GB+ RAM. Use larger VM. The Dockerfile sets `NODE_OPTIONS=--max-old-space-size=2048`.

#### Config missing `gateway.mode` startup refusal
```bash
openclaw config set gateway.mode local
```

#### Cannot find module after npm update
Stop the gateway first, then run `npm install -g openclaw@latest`.

#### Plugin blocked: suspicious ownership (Docker)
Docker volume ownership mismatch (expected uid 1000, got root).
```bash
chown -R 1000:1000 /path/to/mounted/config
```

#### Auth profile encryption key missing
Ensure all three Docker volumes are mounted, especially the auth-profile-secrets directory.

#### Config write rejected
Clobber protection blocked the write (>50% size drop, gateway.mode removed). Use `openclaw doctor` to repair.

#### Docker Desktop DNS failures in CLI container
`EAI_AGAIN` errors when dropping `NET_RAW` capability. Use a temporary override restoring default capabilities for the CLI container.

### Support Diagnostics Export

```bash
openclaw gateway diagnostics export --output ~/openclaw-diagnostics.zip
```

Creates a sanitized zip with config shape, log summaries, health snapshots, stability bundle, and manifest. Safe for sharing (redacts secrets, chat text, hostnames).

---

## Key Source Files

| File | Purpose |
|------|---------|
| `src/config/io.ts` | Config load/write with atomic safety (2984 lines) |
| `src/daemon/gateway-entrypoint.ts` | Gateway startup sequence |
| `src/daemon/launchd.ts` | macOS LaunchAgent management |
| `src/daemon/service-layout.ts` | Service layout inspection |
| `src/secrets/configure.ts` | Secrets configuration wizard |
| `src/secrets/apply.ts` | Secrets plan application |
| `src/secrets/runtime.ts` | Runtime secret resolution |
| `src/wizard/setup.ts` | Onboarding wizard implementation |
| `src/state/openclaw-state-db.ts` | Shared SQLite state DB |
| `src/state/openclaw-agent-db.ts` | Per-agent SQLite DB |
| `scripts/docker/setup.sh` | Docker setup automation |
| `Dockerfile` | Multi-stage Docker build |

## Related

- [[openclaw-acp-agent]] -- ACP agent asset registration
- [[openclaw-mcp-server]] -- MCP server asset configuration

---

## Related

- [[domains/architecture/openclaw-architecture.md]] -- System architecture
- [[domains/mcp/openclaw-mcp-implementation.md]] -- MCP implementation
- [[domains/acp/openclaw-acp-implementation.md]] -- ACP protocol implementation
- [[domains/api/openclaw-api.md]] -- API reference
- [[assets/deployment/openclaw-quadlet.md]] -- Quadlet deployment patterns
- [[assets/agent-profiles/openclaw-profile.md]] -- Quick reference profile
- [[wiki/openclaw.md]] -- Wiki entry
