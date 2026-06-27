---
name: hermes-workspace-api
tags: [agent-gateway, api, cli, dashboard, desktop, hermes-agent, mcp, messaging, multi-platform, orchestration, plugin-sdk, quadlet, rest-api, systemd, typescript]
description: Hermes Workspace API reference for the web/desktop command center
source: sources/hermes-workspace/
---

# Hermes Workspace API
**Source:** `sources/hermes-workspace/`

## Overview

Hermes-workspace uses TanStack Start server functions for all API routes. Routes live under `src/routes/api/` and are server-side handlers compiled by Vite, served via the `server-entry.js` Node HTTP wrapper. All API routes require authentication (`isAuthenticated()` middleware) except where noted.

## REST API Surface

### Session Management

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/sessions` | List all Hermes gateway sessions + local portable sessions |
| POST | `/api/sessions` | Create a new session (`label?`, `friendlyId?`, `model?`) |
| PATCH | `/api/sessions` | Update session (rename, `sessionKey`, `label`) |
| DELETE | `/api/sessions?sessionKey=...` | Delete session from gateway or local store |
| POST | `/api/send-stream` | Streaming chat endpoint (SSE) — primary communication channel |
| POST | `/api/send` | Non-streaming send |
| POST | `/api/session-send` | Alternative send endpoint |
| GET | `/api/session-status` | Session status checks |
| GET | `/api/session-history` | Session message history |
| GET | `/api/chat-events` | Real-time chat event bus |

The streaming endpoint (`/api/send-stream`) accepts `{ sessionKey?, friendlyId?, message, attachments?, history?, model?, thinking?, temperature?, locale? }` and returns `text/event-stream` with events: `started`, `chunk`, `thinking`, `tool` (start/calling/complete/error), `artifact`, `memory.updated`, `skill.loaded`, `error`, `done`, `hb_signal`, `heartbeat`.

### Agent/Gateway Control

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/start-agent` | Start a hermes-agent process |
| POST | `/api/start-claude` | Legacy alias for start-agent |
| POST | `/api/claude-update` | Trigger agent update/restart |
| GET | `/api/gateway-status` | Current gateway connection state |
| POST | `/api/gateway-reprobe` | Force re-probe of gateway capabilities |
| GET | `/api/connection-status` | Overall connection status |
| GET/PUT | `/api/connection-settings` | Gateway connection URL/token settings |

### Config & Providers

| Method | Path | Description |
|--------|------|-------------|
| GET/PATCH | `/api/hermes-config` | Read/write `~/.hermes/config.yaml` and `.env` |
| GET | `/api/claude-config` | Legacy alias for hermes-config |
| POST | `/api/config-patch` | Alternative config patching endpoint |
| GET | `/api/local-providers` | Discovered local LLM providers (Ollama, LM Studio) |
| GET | `/api/models` | Available models from providers |
| GET | `/api/provider-usage` | Usage/cost analytics per provider |

Config PATCH accepts action-based patches: `set-default-model`, `set-api-key`, `remove-api-key`, `set-custom-provider`, `remove-custom-provider`. Also accepts legacy `{ config, env }` body format. All validated with Zod schemas.

### Memory & Skills

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/memory` | Memory browser/CRUD |
| GET | `/api/memory` | Browse memory files |
| GET | `/api/knowledge` | Knowledge browser |
| GET | `/api/skills` | Skills catalog |
| GET | `/api/profiles` | Hermes agent profiles |
| POST | `/api/plugins` | Plugin browser |
| GET | `/api/integrations` | Integration detection |

### Swarm Control Endpoints (20+ endpoints)

The swarm system provides extensive control over multi-worker agent orchestration:

**Core Dispatch:**
- `POST /api/swarm-dispatch` — Core dispatch endpoint. Accepts `{ assignments: [{workerId, task, rationale?}], workerIds?, prompt?, timeoutSeconds?, waitForCheckpoint?, checkpointPollSeconds?, missionId?, missionTitle?, direct?, notifySessionKey? }`.
- `POST /api/swarm-orchestrator-loop` — Automatic orchestrator loop. Reads worker checkpoints, auto-continues tasks, generates review assignments.

**Worker Lifecycle:**
- `GET/POST /api/swarm-lifecycle` — Worker lifecycle: GET (status all or `?workerId=...`) and POST with actions (`auto-sweep`, `request-handoff`, `renew`, `notify-handoff-written`).
- `GET/POST /api/swarm-roster` — Read/update `swarm.yaml` roster.
- `POST /api/swarm-tmux-start` — Start tmux session for worker.
- `POST /api/swarm-tmux-stop` — Stop tmux session.
- `POST /api/swarm-tmux-scroll` — Capture tmux pane output.

**Missions & Tasks:**
- `GET/POST /api/swarm-missions` — Mission CRUD/cancel.
- `POST /api/swarm-decompose` — Task decomposition.
- `POST /api/swarm-direct-chat` — Direct chat with a worker.
- `GET /api/swarm-checkpoint` — Checkpoint reading.
- `GET/POST /api/swarm-kanban` — Kanban board CRUD.
- `POST /api/swarm-reports` — Swarm reports.
- `POST /api/swarm-project` — Project context management.

**State & Health:**
- `GET /api/swarm-runtime` — Worker runtime state.
- `POST /api/swarm-runtime.reset` — Reset worker runtime.
- `GET /api/swarm-environment` — Swarm environment paths/configuration.
- `GET /api/swarm-chat` — Swarm chat reading.
- `GET/POST /api/swarm-memory` — Swarm memory CRUD/search.
- `GET /api/swarm-health` — Swarm worker health checks.

### MCP Hub Management

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/mcp` | List MCP servers with search (`?search=...&category=...`) |
| POST | `/api/mcp` | Add/configure MCP server (accepts `McpServerInput`) |
| GET | `/api/mcp` (hub) | Unified search across Smithery registry + local config (`?query=...&sources=...&limit=...&offset=...`) |

The MCP Hub is a server-side search aggregator that provides a unified catalog for discovering and installing MCP servers. It does NOT proxy MCP tool calls or maintain persistent connections — actual MCP execution happens through the Hermes agent's own MCP runtime.

Sources include:
- **mcp-get**: Fetches `https://registry.smithery.ai/servers` (Smithery MCP registry) with conditional-GET/ETag caching.
- **local-file**: Reads MCP server configs from local config.yaml `mcp_servers` section.
- **generic-json** (Phase 3.2): Fetches any user-supplied HTTPS URL returning a JSON MCP catalog, with SSRF guard (DNS resolution validates no private IPs, 5MB response cap, no redirects).

Caching: In-memory Map + optional disk persistence. Cache keys are per-source (user sources use `{sourceId}:{url}` so URL changes auto-invalidate).

Trust model: `official`, `community`, `unverified` levels. User-source entries are capped at `community`.

### File Browser API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/files` | File browser |
| GET/POST | `/api/artifacts` | Tool artifacts |
| GET | `/api/artifacts/$artifactId` | Specific artifact |
| GET | `/api/preview-file` | File preview |

### Terminal API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/terminal-input` | Send input to terminal |
| POST | `/api/terminal-resize` | Resize terminal |
| POST | `/api/terminal-close` | Close terminal |
| GET | `/api/terminal-stream` | PTY terminal streaming |

The terminal system uses a Python helper (`scripts/pty-helper.py`) for PTY management.

### Tasks & Conductor

| Method | Path | Description |
|--------|------|-------------|
| GET/POST/PATCH/DELETE | `/api/claude-tasks` | Claude Tasks (Conductor) CRUD |
| GET/POST/PATCH/DELETE | `/api/claude-tasks/$taskId` | Individual task operations |
| GET/POST/PATCH/DELETE | `/api/hermes-tasks` | Native Hermes tasks |
| GET/POST/PATCH/DELETE | `/api/hermes-tasks/$taskId` | Individual task ops |
| POST | `/api/conductor-spawn` | Spawn conductor mission |
| POST | `/api/conductor-stop` | Stop conductor mission |

### Jobs & Cron

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/claude-jobs` | Job listing |
| GET/POST/PATCH/DELETE | `/api/claude-jobs/$jobId` | Job operations |

### Dashboard & Metrics

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/dashboard` | Dashboard service proxy |
| GET | `/api/context-usage` | Context window token usage |
| GET | `/api/system-metrics` | System resource metrics |
| GET | `/api/dashboard-aggregator` | Aggregated dashboard data |

### Update System

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/update/status` | Version/install/update state for workspace + agent |
| POST | `/api/update/workspace` | Apply workspace update |
| POST | `/api/update/agent` | Apply agent update |

### Auth

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth` | Login (password verification, returns session cookie) |
| GET | `/api/auth-check` | Check if authenticated |
| POST | `/api/commands` | CLI command endpoint |

### Other Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/ping` | Health check |
| GET | `/api/workspace` | Workspace metadata (version, capabilities) |
| GET | `/api/transcribe` | STT transcription (speech-to-text) |
| GET | `/api/crew-status` | Crew agent status |
| GET | `/api/media` | Media file serving |
| GET | `/api/paths` | Resolved workspace paths |
| GET | `/api/events` | Server-sent events for real-time updates |
| POST | `/api/playground-npc` | HermesWorld NPC endpoint |
| POST | `/api/playground-admin` | Playground admin |
| POST | `/api/oauth/device-code` | OAuth device code flow |
| POST | `/api/oauth/poll-token` | OAuth token polling |

### Auth Model

- Cookie-based session tokens with 30-day TTL, stored in `~/.hermes/workspace-sessions.json`.
- Password protection via `HERMES_PASSWORD` (or legacy `CLAUDE_PASSWORD`). Tokens compared with timing-safe comparison.
- Session cookie: `claude-auth=<token>` with `HttpOnly`, `Secure`, `SameSite=Strict`, `Path=/`, `Max-Age=2592000`.
- No password configured = no auth (local-only safe default). Server refuses to start on non-loopback host without a password.
- Auth middleware (`isAuthenticated()`) checks cookie on every request.
- Some endpoints also use `requireJsonContentType()` for CSRF protection on mutating POST requests.
- Gateway bearer token via `HERMES_API_TOKEN` for calls to the agent gateway.
- Dashboard auth via ephemeral session token scraped from dashboard root HTML (auto-refreshed on 401).

## How the Workspace Communicates with Hermes Agent

### Protocol Architecture

```
Workspace Server
    |
    |-- Gateway WebSocket (:18789) -- RPC with device identity auth
    |-- Gateway HTTP API (:8642)    -- /health, /v1/models, capabilities
    |-- Dashboard HTTP API (:9119)  -- sessions, skills, config, jobs, MCP
    |-- OpenAI-Compatible API      -- /v1/chat/completions, /v1/responses
    |-- Direct subprocesses         -- tmux sessions, child_process for workers
```

### Gateway WebSocket Protocol (`src/server/gateway.ts`)

- Connects to `ws://127.0.0.1:18789` (configurable via `CLAUDE_GATEWAY_URL`).
- Custom JSON-based RPC framing: `{ type: 'req', id, method, params }` -> `{ type: 'res', id, ok, payload }`.
- Receives events: `{ type: 'event', event, payload }`.
- Protocol version 3 with device identity authentication (Ed25519 keypair).
- RPC methods include `sessions.usage`, `sessions.costs`, `usage.analytics`, `usage.summary`, and standard `connect`.
- Circuit breaker pattern: opens after 15 consecutive failures, 10s cooldown, exponential backoff reconnect.
- Heartbeat: 30s ping interval, 20s timeout.
- Singleton client survives Vite SSR module reloads.

### Gateway HTTP API (`src/server/gateway-capabilities.ts`)

- Probes `GET /health` and `GET /v1/models` on the gateway (default `http://127.0.0.1:8642`).
- Dashboard API at `http://127.0.0.1:9119` for sessions, skills, config, jobs, MCP.
- Bearer token auth via `HERMES_API_TOKEN`.
- Dashboard auth via ephemeral session token scraped from root HTML.
- Auto-detects gateway URLs on startup and probes periodically (2min TTL healthy, 15s TTL disconnected).
- Full capability probing on startup: health, chatCompletions, models, sessions, enhancedChat, skills, memory, config, jobs, mcp, conductor, kanban.

### OpenAI-Compatible API (`src/server/openai-compat-api.ts`)

- `POST /v1/chat/completions` for the "portable" chat backend (Ollama, LM Studio, vLLM).
- `POST /v1/responses` for the newer Responses API (hermes-agent >= 0.12.x).

## Swarm Worker Communication

The workspace does NOT use ACP (Agent Communication Protocol) for worker management. Instead:

- Workers are `hermes` CLI processes with specific profiles, run inside tmux sessions or as child processes.
- Prompts are sent via `tmux send-keys` (paste-buffer to the TUI) or `child_process.stdin.write()`.
- Workers respond in a structured checkpoint format: `STATE: DONE|BLOCKED|NEEDS_INPUT|HANDOFF|IN_PROGRESS / FILES_CHANGED: ... / COMMANDS_RUN: ... / RESULT: ... / BLOCKER: ... / NEXT_ACTION: ...`
- The workspace polls the worker's `runtime.json` file on disk and reads chat transcripts from the profile's `state.db` SQLite database via a Python one-liner.
- Polling interval: 2s, default timeout: 90s.

### Worker Lifecycle

1. **Profile Setup** — `ensureSwarmProfileConfig(profilePath)` creates the worker's Hermes profile directory under `~/.hermes/profiles/<workerId>/` with `config.yaml`, `MEMORY.md`, `SOUL.md`, `USER.md`, `runtime.json`.

2. **Session Start** — Two modes:
   - **tmux**: `tmux new-session -d -s swarm-<workerId> '<launch command>'` where launch command is `HERMES_HOME=<profilePath> HERMES_CLI_BIN=<hermesBin> 'hermes' chat --tui`.
   - **Native (Windows)**: `spawn('hermes', ['--tui', '--profile', workerId])` with stdin/stdout/stderr pipes.

3. **Dispatch** — The orchestrator sends prompts to workers via tmux paste-buffer or stdin.write(). One-shot fallback executes `hermes chat -q <prompt> -Q --yolo --ignore-rules --source swarm-dispatch` as a subprocess with timeout (default 240s, max 600s).

4. **Checkpoint Polling** — After dispatch, polls for fresh checkpoints by reading `runtime.json` and `state.db` from the worker's profile directory.

5. **Lifecycle Management** — `autoSweepLifecycle()` handles context window management with thresholds: softTokens (250k), handoffTokens (400k), hardTokens (500k). States: healthy < watch < handoff_required < renew_required.

## Related

- [[hermes-workspace]] -- Wiki entry for Hermes Workspace
- [[hermes-workspace-architecture]] -- System architecture
- [[hermes-workspace-deployment]] -- Deployment guide
- [[hermes-workspace-profile]] -- Agent profile
- [[hermes-workspace-mcp-hub]] -- MCP hub implementation
- [[hermes-workspace-swarm-architecture]] -- Swarm architecture
- [[hermes-workspace-quadlet]] -- Quadlet deployment
