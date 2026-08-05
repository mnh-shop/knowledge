---
name: hermes-api-server
description: "Hermes API Server surfaces: OpenAI-compatible REST API (port 8642), web dashboard (port 9119), JSON-RPC TUI/desktop gateway, and the hermes proxy OAuth shim"
source: sources/hermes-agent/
tags: [agent-gateway, api, cli, dashboard, desktop, hermes-agent, json-rpc, openai, rest-api, websocket]
---

# Hermes API Server — HTTP & JSON-RPC Surfaces

Hermes exposes several programmatic surfaces beyond the messaging gateway.
They are all launched through the same CLI but serve different consumers:

1. **OpenAI-compatible REST API** (`gateway/platforms/api_server.py`) — the
   "API Server" platform adapter; lets OpenAI-SDK clients drive a Hermes agent.
2. **Web Dashboard backend** (`hermes_cli/web_server.py`) — FastAPI serving
   the Vite/React web UI plus a large `/api/*` REST + WebSocket surface.
3. **TUI/desktop JSON-RPC gateway** (`tui_gateway/server.py`) — newline-framed
   JSON-RPC over stdio, consumed by the ink TUI and desktop apps.
4. **`hermes proxy`** — a local OpenAI-compatible proxy that forwards requests
   to upstream OAuth providers.

---

## 1. OpenAI-Compatible REST API — `gateway/platforms/api_server.py`

Served by the `APIServerAdapter` (an `api_server` platform inside the gateway;
`DEFAULT_PORT = 8642`, `gateway/platforms/api_server.py:124`, class at
`:1168`). Feature docs: `website/docs/user-guide/features/api-server.md`.

Default port **8642** (override via `API_SERVER_PORT`); Bearer auth via
`API_SERVER_KEY`. Primary endpoints:

| Method | Path | Description |
|---|---|---|
| `POST` | `/v1/chat/completions` | OpenAI Chat Completions format (stateless; opt-in session continuity via `X-Hermes-Session-Id`, long-term memory scoping via `X-Hermes-Session-Key`) |
| `POST` | `/v1/responses` | OpenAI Responses API format (stateful via `previous_response_id`; `X-Hermes-Session-Key` supported) |
| `GET` / `DELETE` | `/v1/responses/{response_id}` | Retrieve / delete a stored response |
| `POST` | `/v1/runs` | Start a run; returns `run_id` immediately (HTTP 202) |
| `GET` | `/v1/runs/{run_id}` | Current run status |
| `GET` | `/v1/runs/{run_id}/events` | SSE stream of structured lifecycle events |
| `POST` | `/v1/runs/{run_id}/approval` | Resolve a pending run approval |
| `POST` | `/v1/runs/{run_id}/stop` | Interrupt a running agent |
| `GET`/`POST` | `/api/sessions` | List / create Hermes sessions |
| `GET`/`PATCH`/`DELETE` | `/api/sessions/{session_id}` | Read / update / delete a session |
| `GET` | `/api/sessions/{session_id}/messages` | Session message history |
| `POST` | `/api/sessions/{session_id}/fork` | Branch a session via SessionDB lineage |
| `POST` | `/api/sessions/{session_id}/chat[/stream]` | Chat with a persisted session |
| `GET` | `/health` / `/health/detailed` | Liveness + rich status |

Multi-profile mode: when `gateway.multiplex_profiles` is on, secondary
profiles are reached under a URL prefix (`/p/<profile>/v1/models`,
`/p/<profile>/v1/chat/completions`, …) — the same contract as the webhook
adapter. See also [[hermes-agent-api]] for the full per-endpoint reference.

---

## 2. Web Dashboard backend — `hermes_cli/web_server.py`

A FastAPI/Starlette app (17,333 LOC) that serves the Vite/React dashboard and
a REST/WebSocket control plane. Default port **9119** (module docstring:
`python -m hermes_cli.main web` → http://127.0.0.1:9119).

- **~120 unique `/api/*` routes** (auth-guarded except a small public set;
  `/api/plugins/` paths serve dashboard-plugin assets).
- **6 WebSocket routes**: `/api/pty` (PTY-over-WebSocket for the Chat tab),
  `/api/console` (Hermes Console command WS), `/api/ws` (JSON-RPC sidecar for
  the Chat tab), `/api/pub`, `/api/events`, `/api/audio/speak-stream`.
- **Dashboard plugin API**: `_discover_dashboard_plugins()`
  (`hermes_cli/web_server.py:16295`) loads plugins from `plugins/` that register
  their own UI routes, API paths, and assets.
- **`dashboard-auth` plugin family** (`plugins/dashboard_auth/`): four auth
  modes — `basic` (secret/token), `drain` (token routes), `nous` (Nous Portal
  OAuth client), `self_hosted` (self-hosted OAuth client registration via
  `hermes dashboard register`).

Launch: `hermes dashboard` (browser UI) or `hermes serve` (same gateway,
headless — what the desktop app and remote backends run;
`hermes_cli/subcommands/dashboard.py`). `--stop` / `--status` manage running
dashboard processes.

---

## 3. TUI / Desktop JSON-RPC gateway — `tui_gateway/server.py`

The backend that powers the ink TUI, the web Chat tab, and the desktop app.

- **Wire protocol**: newline-framed JSON-RPC 2.0 over stdio
  (`{"jsonrpc": "2.0", ...}` frames; `tui_gateway/event_publisher.py:10`
  "Wire protocol: newline-framed JSON dicts"). stdout is reserved for
  JSON-RPC; Python stdout is redirected to stderr.
- **~130 JSON-RPC handlers** in `server.py` (split across
  `methods_session.py`, `methods_config.py`, `methods_prompt.py`,
  `methods_complete.py`).
- **Transport variants**: stdio (TUI), plus WebSocket transports for the
  dashboard/desktop (`tui_gateway/ws.py` — identical framing over WS).
- **Client package**: `apps/shared/src/json-rpc-gateway.ts` — the shared
  TypeScript JSON-RPC/event client (gateway events: message deltas, tool
  progress, approvals, status updates).

### Frontends

| Frontend | Location | Stack |
|---|---|---|
| Ink TUI | `ui-tui/packages/hermes-ink` | TypeScript/Ink |
| Web dashboard | `web/` | Vite + React |
| Desktop app | `apps/desktop/` | Electron shell (spawns `hermes serve`) |
| Installer | `apps/bootstrap-installer/` | Tauri (`src-tauri/`) |

---

## 4. `hermes proxy` — OpenAI-Compatible OAuth proxy

`hermes proxy` (`hermes_cli/subcommands/gateway.py:311-326`) is a local
OpenAI-compatible proxy that attaches the user's upstream OAuth credentials:
apps point at the proxy with any bearer token and the proxy brokers to the
real provider. Subcommands: `run`/`start`/`status` (`hermes_cli/main.py` →
`cmd_proxy`).

---

## Related

- [[hermes-agent-api]] -- Full REST endpoint reference
- [[hermes-gateway-api]] -- Multi-platform gateway
- [[hermes-workspace-api]] -- Workspace web/desktop command center
- [[hermes-agent]] -- Core agent runtime

## Links

- API server adapter: `sources/hermes-agent/gateway/platforms/api_server.py`
- Feature docs: `sources/hermes-agent/website/docs/user-guide/features/api-server.md`
- Dashboard backend: `sources/hermes-agent/hermes_cli/web_server.py`
- Dashboard subcommands: `sources/hermes-agent/hermes_cli/subcommands/dashboard.py`
- Dashboard auth plugins: `sources/hermes-agent/plugins/dashboard_auth/`
- JSON-RPC gateway: `sources/hermes-agent/tui_gateway/server.py`
- JSON-RPC client: `sources/hermes-agent/apps/shared/src/json-rpc-gateway.ts`
- Proxy CLI: `sources/hermes-agent/hermes_cli/subcommands/gateway.py`
