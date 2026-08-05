---
name: alphaclaw
tags: [bootc, cli, dashboard, desktop, git, mcp, messaging, monitoring, openclaw, orchestration, rest-api, storage, webhook, agent, javascript, alphaclaw]
description: "Setup UI, gateway manager, and onboarding wrapper for OpenClaw"
source: sources/alphaclaw/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# AlphaClaw

**Source:** `sources/alphaclaw/`

AlphaClaw is the ops and setup layer around OpenClaw. It provides a browser-based setup UI, gateway lifecycle management, watchdog recovery flows, and integrations (Telegram, Discord, Slack, Google Workspace, webhooks) so users can operate OpenClaw without manual server intervention. Published as `@chrysb/alphaclaw` on npm. Deploy via Render/Railway one-click templates, Docker, or the macOS desktop app.

| Field | Value |
|---|---|
| **Origin** | [chrysb/alphaclaw](https://github.com/chrysb/alphaclaw) |
| **License** | MIT |
| **Stack** | Node.js 22.22.3+ (22.x), 24.15.0+ (24.x), or 25.9.0+ (25.x) per `engines` gate; Express 4, Preact + htm + esbuild |
| **npm** | `npm install @chrysb/alphaclaw` |
| **Source** | `sources/alphaclaw/` |

First deploy to first message in under five minutes.

## Key Features

- **Setup UI:** Password-protected web dashboard for onboarding, configuration, and day-to-day management. Tabs for General, Browse (file explorer), Usage analytics, Cron jobs, Nodes, Watchdog, Providers, Environment variables, and Webhooks.
- **Guided Onboarding:** Step-by-step setup wizard -- model selection, provider credentials, GitHub repo pairing, channel pairing.
- **Multi-Agent Management:** Sidebar-driven agent navigation with create, rename, and delete flows. Per-agent overview cards, channel bindings, and URL-driven agent selection.
- **Gateway Manager:** Spawns, monitors, restarts, and proxies the OpenClaw gateway as a managed child process on loopback.
- **Watchdog:** Crash detection, crash-loop recovery, auto-repair (`openclaw doctor --fix`), and Telegram/Discord/Slack notifications. Includes a live interactive terminal in the browser for monitoring gateway output.
- **Channel Orchestration:** Telegram, Discord, and Slack bot pairing with per-agent channel bindings, credential sync, and a guided wizard for splitting Telegram into multi-threaded topic groups.
- **Google Workspace:** OAuth integration for Gmail, Calendar, Drive, Docs, Sheets, Tasks, Contacts, and Meet. Guided Gmail watch setup with Google Pub/Sub topic, subscription, and push endpoint handling.
- **Cron Jobs:** Dedicated cron tab with job management, interactive rolling calendar, run-history drilldowns, trend analytics, and per-run usage breakdowns.
- **Nodes:** Guided local-node setup for VPS deployments with per-node browser attach checks, reconnect commands, and routing/pairing controls.
- **Webhooks:** Named webhook endpoints with per-hook transform modules, request logging, payload inspection, editable delivery destinations, and OAuth callback support.
- **File Explorer:** Browser-based workspace explorer with file visibility, inline edits, diff view, and Git-aware sync -- no SSH needed for quick fixes.
- **Prompt Hardening:** Ships anti-drift bootstrap prompts (`AGENTS.md`, `TOOLS.md`) injected into the agent's system prompt on every message, enforcing safe practices and change summaries.
- **Git Sync:** Automatic hourly commits of the OpenClaw workspace to GitHub with configurable cron schedule.
- **Version Management:** In-place updates for both AlphaClaw and OpenClaw with in-app release notes and one-click apply.
- **Codex OAuth:** Built-in PKCE flow for OpenAI Codex CLI model access — `/auth/codex/start` → OpenAI authorize → token exchange → server-side profile, managed via `/api/codex/*` endpoints (`README:46`, `constants.js:31-38`).
- **Remote MCP Injection:** When `REMOTE_MCP_URL` + `REMOTE_MCP_API_TOKEN` are set, AlphaClaw writes a managed `mcp.servers.<REMOTE_MCP_NAME>` entry into `openclaw.json` on every gateway start; `REMOTE_MCP_PROXY_URL` routes callbacks through a same-host scanning proxy (`README:171-174`).
- **Git Auth Shim:** Installs a managed git shim + askpass helper so the workspace repo can push to GitHub using `GITHUB_TOKEN` without storing credentials (`ALPHACLAW_GIT_SHIM_PATH`, `ALPHACLAW_GIT_ASKPASS_PATH`; `README:168-169`).
- **OpenAI-compatible /v1 Proxy:** Optional `/v1/chat/completions`, `/v1/responses`, `/v1/embeddings`, `/v1/models` endpoints on the same port as the Setup UI (disabled by default).

## Architecture

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
│           http-proxy     │  child process           │
│                          ▼                          │
│              ┌─────────────────────┐                │
│              │ OpenClaw Gateway    │                │
│              │ 127.0.0.1:18789    │                │
│              └──────────┬──────────┘                │
│                         │                           │
│              ┌──────────▼──────────┐                │
│              │  ALPHACLAW_ROOT_DIR │                │
│              │  .openclaw/  .env    │                │
│              │  logs/   alphaclaw.json              │
│              └─────────────────────┘                │
└─────────────────────────────────────────────────────┘
```

The runtime model has four layers:

1. **Express Server** -- serves the Setup UI frontend (Preact + htm bundle built via esbuild), exposes JSON APIs for all management operations, and proxies gateway traffic to the OpenClaw child process. Authentication is gated behind a single `SETUP_PASSWORD` with exponential-backoff brute-force protection.
2. **Gateway Manager** -- spawns OpenClaw as a managed child process bound to `127.0.0.1:18789` (`spawn("openclaw", ["gateway", "run"])`). Monitors its health, restarts it on exit, and injects runtime environment (workspace repo, channel tokens, credential files). The manager writes managed `mcp.servers` entries into `openclaw.json` when `REMOTE_MCP_URL` is configured.
3. **Watchdog** -- periodically runs `openclaw health`, detects crashes, manages crash-loop thresholds (default: 3 crashes in 300s), and optionally runs `openclaw doctor --fix --yes` for auto-repair. All incidents are logged to a SQLite-backed event log and surfaced through the Setup UI and notification channels.
4. **Codex OAuth Store** -- PKCE flow (`S256`) against OpenAI's auth endpoints for Codex CLI model access. Profiles are persisted server-side via `authProfiles.upsertCodexProfile()` and surfaced through `/api/codex/status`, `/api/codex/exchange`, and `/api/codex/disconnect` (`routes/codex.js`).

The Setup UI frontend is an SPA built with Preact + htm (no JSX compilation needed) and bundled through esbuild. Components follow a consistent pattern: feature folders with `index.js` shells, `use-*` hooks, and shared utilities in `lib/public/js/lib/`. Routing is via wouter-preact with URL-driven agent selection.

### Key Source Directories (`lib/`)

| Directory | Purpose |
|---|---|
| `lib/server/` | Express server, route modules (19 modules, ~154 handlers), gateway manager, watchdog, webhooks, integrations |
| `lib/server/routes/` | API route definitions (19 modules: agents 19, system 18, watchdog 12, cron 12, telegram 11, nodes 11, webhooks 10, models 9, google 9, doctor 9, gmail 7, pairings 6, onboarding 6, codex 5, usage 4, pages 3, auth 3, proxy middleware, plus `browse/`) |
| `lib/server/doctor/` | Gateway repair scripts (`openclaw doctor --fix` wrappers) |
| `lib/server/db/` | SQLite database layer (watchdog events, webhooks, usage, gmail) |
| `lib/server/onboarding/` | Setup wizard step definitions |
| `lib/server/init/` | Bootstrap and initialization logic |
| `lib/server/agents/` | Agent lifecycle management sub-modules |
| `lib/public/js/` | Setup UI frontend (Preact components, hooks, lib utilities) |
| `lib/public/css/` | Tailwind CSS source and theme tokens |
| `lib/setup/` | Prompt hardening templates (`AGENTS.md`, `TOOLS.md`), env template, git sync script |
| `lib/cli/` | CLI sub-commands (git sync, openclaw config restore) |
| `lib/scripts/` | Scripts invoked during setup wizard steps |
| `lib/plugin/` | Usage tracker plugin for OpenClaw |
| `bin/` | CLI entrypoint (`alphaclaw.js`) |

## Interfaces

### CLI

| Command | Description |
|---|---|
| `alphaclaw start` | Start the server (Setup UI + gateway manager) |
| `alphaclaw git-sync -m "message"` | Commit and push the OpenClaw workspace |
| `alphaclaw telegram topic add --thread <id> --name <text>` | Register a Telegram topic mapping |
| `alphaclaw version` | Print version |
| `alphaclaw help` | Show help |

### REST API

The Express server exposes JSON APIs under `/api/` for all management operations. `SETUP_API_PREFIXES` (`constants.js:469-490`) enumerates 25 protected prefixes: status, pairings, google, codex, models, browse, chat, gateway, restart-status, onboard, env, auth, openclaw, devices, sync-cron, telegram, webhooks, gmail, watchdog, usage, cron, agents, channels, operations, nodes. Authenticated via session cookie (backed by `SETUP_PASSWORD`) with exponential-backoff brute-force lockout.

### Codex OAuth

Built-in PKCE (`S256`) flow for OpenAI Codex CLI model access. Constants in `constants.js:31-38`: authorize at `https://auth.openai.com/oauth/authorize`, token at `https://auth.openai.com/oauth/token`, redirect URI `http://localhost:1455/auth/callback`, scope `openid profile email offline_access`, OAuth state TTL 10 minutes.

| Path | Method | Purpose |
|---|---|---|
| `/auth/codex/start` | GET | Redirects to OpenAI authorize with PKCE challenge (`routes/codex.js:47`) |
| `/auth/codex/callback` | GET | Token exchange + profile upsert, `postMessage` back to opener (`routes/codex.js:74`) |
| `/api/codex/status` | GET | Connection/profile status (`routes/codex.js:36`) |
| `/api/codex/exchange` | POST | Manual code/state paste exchange fallback (`routes/codex.js:142`) |
| `/api/codex/disconnect` | POST | Remove stored Codex profiles (`routes/codex.js:201`) |

### Real-Time Streams

- **SSE** `/api/events/status` -- gateway/channel health status stream (`routes/system.js:616`).
- **SSE** `/api/operations/:operationId/events` -- long-running operation progress events (`routes/agents.js:91,95`).
- **WebSocket** `/api/ws/chat` -- interactive chat with an agent session, agent tool events included (`lib/server/chat-ws.js`).
- **WebSocket** `/api/watchdog/terminal/ws` -- live interactive gateway terminal (`lib/server/watchdog-terminal-ws.js:3`), with REST fallbacks `/api/watchdog/terminal/{session,output,input,close}`.
- **WebSocket passthrough** `/openclaw*` -- the gateway's own dashboard WS endpoints are proxied through (`lib/server/watchdog-terminal-ws.js:87`).

### Remote MCP Injection

When `REMOTE_MCP_URL` and `REMOTE_MCP_API_TOKEN` are set, AlphaClaw writes a managed `mcp.servers.<REMOTE_MCP_NAME>` block (default key `remote`) into `openclaw.json` on every gateway start. The token is persisted as the `${REMOTE_MCP_API_TOKEN}` env reference, never plaintext. `REMOTE_MCP_PROXY_URL` redirects OpenClaw to a same-host scanning proxy (e.g. `pipelock mcp proxy --listen <url> --upstream <url>`) for outbound callbacks (`README:171-174,195`).

### Webhook Endpoints

Named webhook endpoints accept inbound HTTP requests, run transform modules, log payloads, and forward to configured destinations. Support query-string token auth for providers without `Authorization` headers.

### OpenAI-compatible /v1 Proxy

When enabled in the Setup UI (persisted to `alphaclaw.json`), the server exposes OpenAI-compatible endpoints on the same public port:

| Path | Method | Notes |
|---|---|---|
| `/v1/chat/completions` | POST | Streams when `stream: true`. Uses `model: "openclaw/default"` or `openclaw/<agentId>`. |
| `/v1/responses` | POST | OpenClaw's responses surface |
| `/v1/embeddings` | POST | Routes to OpenClaw embeddings |
| `/v1/models`, `/v1/models/<id>` | GET | Lists OpenClaw agent targets |

Auth required: `Authorization: Bearer <OPENCLAW_GATEWAY_TOKEN>`. Requests are reverse-proxied to the loopback OpenClaw gateway.

### Gateway Proxy

AlphaClaw proxies the OpenClaw gateway on the same port via `http-proxy`. The gateway's own dashboard and WebSocket endpoints are accessible at their standard paths. Cookie stripping and hop-by-hop header filtering are applied before forwarding.

## Related

- [[openclaw]] -- The AI assistant platform that AlphaClaw wraps and manages
- [[hermes-agent]] -- Competing agent gateway (Python-based)
- [[clawpier]] -- Desktop GUI for managing OpenClaw Docker containers
- [[tank-os]] -- Fedora bootc image deployment for OpenClaw
- [[mission-control]] -- Dashboard that can connect to OpenClaw as a gateway
- [[gogs]] -- Self-hosted Git backend for OpenClaw configuration
