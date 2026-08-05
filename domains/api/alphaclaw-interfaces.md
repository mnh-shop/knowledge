---
name: alphaclaw-interfaces
tags: [alphaclaw, api, rest-api, websocket, sse, oauth, mcp, proxy, security, cli]
description: "AlphaClaw Interfaces — REST API prefixes, SSE/WebSocket streams, /v1 proxy, Codex OAuth, Remote MCP injection"
source: sources/alphaclaw/
---

# AlphaClaw Interfaces

**Source:** `sources/alphaclaw/` · `sources/alphaclaw/README.md` · `sources/alphaclaw/lib/server/`

AlphaClaw runs a single Express server (port `3000`, `constants.js:15`) that multiplexes five surfaces:

1. The **Setup UI** (Preact + htm SPA) and its JSON management APIs
2. **SSE + WebSocket streams** for real-time status, operations, chat, and terminal
3. An optional **OpenAI-compatible `/v1` proxy** to the OpenClaw gateway child process
4. **Codex OAuth** (PKCE) for OpenAI Codex CLI model access
5. **Remote MCP injection** into `openclaw.json`

Per-endpoint request/response details for the management APIs are in [[alphaclaw-api]]; this page catalogs the interface surface and its security boundaries.

## REST API Surface

`SETUP_API_PREFIXES` (`lib/server/constants.js:469-490`) enumerates 25 password-protected `/api/*` prefixes. Session auth is backed by `SETUP_PASSWORD` with exponential-backoff brute-force lockout (`auth.js:62-154`; `/api` and `/auth` are guarded by `requireAuth` at `auth.js:152-154`).

| Prefix | Area |
|---|---|
| `/api/status` | Gateway/channel/feature health, version |
| `/api/pairings` | Channel pairing approval/rejection |
| `/api/google` | Google Workspace OAuth accounts, scopes, credentials |
| `/api/codex` | Codex OAuth status, exchange, disconnect |
| `/api/models` | Model/provider listings |
| `/api/browse` | File explorer (workspace browsing, edits, diff) |
| `/api/chat` | Chat history for agent sessions |
| `/api/gateway` | Gateway control (dashboard URL, restart) |
| `/api/restart-status` | Gateway restart progress |
| `/api/onboard` | Onboarding wizard status/execution |
| `/api/env` | Environment variable read/write (`.env`) |
| `/api/auth` | Login, session status, logout |
| `/api/openclaw` | OpenClaw config/CLI operations |
| `/api/devices` | Device pairing approval/rejection |
| `/api/sync-cron` | Git sync cron schedule |
| `/api/telegram` | Telegram topic/group management |
| `/api/webhooks` | Webhook endpoints, requests, OAuth callbacks |
| `/api/gmail` | Gmail watch config and lifecycle |
| `/api/watchdog` | Watchdog status, events, logs, repair, terminal |
| `/api/usage` | Token/cost summaries and sessions |
| `/api/cron` | Cron job CRUD, runs, trends |
| `/api/agents` | Agent lifecycle (19 handlers — the largest module) |
| `/api/channels` | Channel bindings |
| `/api/operations` | Long-running operation progress (SSE) |
| `/api/nodes` | Remote node setup/routing |

Route module count: **19 modules** (18 `.js` + `browse/`) with **~154 handlers** (`agents.js` 19, `system.js` 18, `watchdog.js` 12, `cron.js` 12, `telegram.js` 11, `nodes.js` 11, `webhooks.js` 10, `models.js` 9, `google.js` 9, `doctor.js` 9, `gmail.js` 7, `pairings.js` 6, `onboarding.js` 6, `codex.js` 5, `usage.js` 4, `pages.js` 3, `auth.js` 3, `proxy.js` middleware; `browse/index.js` adds 13 more).

## Real-Time Streams

| Stream | Type | Path | Source |
|---|---|---|---|
| Status | SSE | `/api/events/status` | `routes/system.js:616` — `text/event-stream` push of the `/api/status` payload |
| Operations | SSE | `/api/operations/:operationId/events` | `routes/agents.js:91,95` — progress events for long-running agent operations |
| Chat | WebSocket | `/api/ws/chat` | `lib/server/chat-ws.js` — interactive chat with an agent session; agent `tool-events` capability (`chat-ws.js:633`); 1 MB max payload; degraded to HTTP 503 when `ws` is unavailable (`chat-ws.js:337-347`) |
| Watchdog terminal | WebSocket | `/api/watchdog/terminal/ws` | `watchdog-terminal-ws.js:3` — live interactive gateway terminal; REST fallbacks at `/api/watchdog/terminal/{session,output,input,close}` (`routes/watchdog.js:94-141`) |
| Gateway dashboard passthrough | WebSocket | `/openclaw*` | `watchdog-terminal-ws.js:87` — the gateway's own dashboard WS endpoints are proxied through |

All WebSocket upgrades are authorized via the same `isAuthorizedRequest()` gate (session cookie) before `handleUpgrade` (`watchdog-terminal-ws.js:89-116`); unauthorized upgrades receive HTTP 401 and are destroyed.

## OpenAI-Compatible `/v1` Proxy

Disabled by default; toggled in the Setup UI (General → Features → API), persisted in `alphaclaw.json` via `isOpenAiCompatApiEnabled()` (`alphaclaw-config.js:63`). When disabled or absent, `/v1` requests return 404 (`routes/proxy.js:227-228`).

| Path | Method | Notes |
|---|---|---|
| `/v1/chat/completions` | POST | Streams when `stream: true`; `model: "openclaw/default"` or `openclaw/<agentId>`; 50 MB body limit |
| `/v1/responses` | POST | OpenClaw's `/v1/responses` surface |
| `/v1/embeddings` | POST | Routes to OpenClaw embeddings |
| `/v1/models`, `/v1/models/<id>` | GET | Lists OpenClaw agent targets |

Routing regex: `/^\/v1\/(?:chat\/completions|responses|embeddings|models(?:\/[^/?#]+)?)$/` (`routes/proxy.js:6`). Requests are reverse-proxied to the loopback gateway (`proxy.js:89-190`).

**Auth + security boundary** (`README.md:187-195`):

- Requires `Authorization: Bearer <OPENCLAW_GATEWAY_TOKEN>`; rejected pre-forward when the token is missing or mismatched. Failed attempts are rate-limited before proxying.
- Setup-UI cookie stripped before forwarding; hop-by-hop response headers not passed through.
- **Full operator access:** a valid token can run any tool the configured agent profile allows. Treat it as an owner credential — trusted server-to-server callers only, never end-user clients. With a public front door, keep `SETUP_PASSWORD` strong and hold the token in exactly one trusted backend.

## Codex OAuth Flow

Built-in PKCE flow for OpenAI Codex CLI model access (`README.md:46`). Constants at `constants.js:31-38`: client `app_EMoamEEZ73f0CkXaXp7hrann`, authorize `https://auth.openai.com/oauth/authorize`, token `https://auth.openai.com/oauth/token`, redirect `http://localhost:1455/auth/callback`, scope `openid profile email offline_access`, OAuth state TTL 10 min.

| Path | Method | Role |
|---|---|---|
| `/auth/codex/start` | GET | Builds authorize URL with `code_challenge_method=S256`, `codex_cli_simplified_flow=true`, `originator=pi`; redirects to OpenAI (`routes/codex.js:47-72`) |
| `/auth/codex/callback` | GET | Exchanges `code` + stored verifier at the token URL; upserts profile via `authProfiles.upsertCodexProfile()`; `postMessage` back to opener and closes (`routes/codex.js:74-140`) |
| `/api/codex/status` | GET | `{ connected, profileId, accountId, expires }` (`routes/codex.js:36`) |
| `/api/codex/exchange` | POST | Manual fallback — paste the full redirect URL; validates state, exchanges, upserts (`routes/codex.js:142-199`) |
| `/api/codex/disconnect` | POST | Removes stored Codex profiles (`routes/codex.js:201`) |

Profile ID `openai:codex-cli` (`constants.js:31`); token expiry is computed as `Date.now() + expires_in * 1000`. The Setup UI uses `<ActionButton />`-driven flows per the project's UI conventions.

## Remote MCP Injection

When `REMOTE_MCP_URL` + `REMOTE_MCP_API_TOKEN` are set, AlphaClaw writes a managed `mcp.servers.<REMOTE_MCP_NAME>` block (default key `remote`) into `openclaw.json` on every gateway start (`README.md:171-174`). The token is persisted as the `${REMOTE_MCP_API_TOKEN}` env reference — never plaintext in the config. `REMOTE_MCP_PROXY_URL` redirects OpenClaw to a same-host scanning proxy instead of `REMOTE_MCP_URL` (implementation is proxy-agnostic; e.g. `pipelock mcp proxy --listen <REMOTE_MCP_PROXY_URL> --upstream <REMOTE_MCP_URL>`). Proxy configuration is applied by `ensureGatewayProxyConfig()` during gateway startup (`gateway.js:501-700`).

This lets the agent call *back into* a remote MCP server — e.g. a SaaS MCP (Notion, Sure) exposed through the same container.

## CLI

`bin/alphaclaw.js` — see [[alphaclaw-deployment]] §10 for the full table. Notable interface-relevant behaviors:

- `start` verifies the Node engine floor, refuses port `18789` (reserved for the gateway), requires `SETUP_PASSWORD`, installs the git auth shim + askpass, and reconciles channels/plugins into `openclaw.json`.
- `git-sync -m <msg> [-f <path>]` commits/pushes the workspace via `GITHUB_TOKEN` through a per-PID askpass script (`bin/alphaclaw.js:325-357`).
- `telegram topic add --thread <id> --name <text> [--system] [--agent] [--group]` maps a Telegram thread and recomputes concurrency.

## Key Source Files

- `lib/server/routes/proxy.js` — `/v1` OpenAI-compatible proxy + registration
- `lib/server/routes/codex.js` — Codex OAuth flow
- `lib/server/routes/system.js` — status + `/api/events/status` SSE
- `lib/server/routes/agents.js` — agent CRUD + `/api/operations/:id/events` SSE
- `lib/server/chat-ws.js` — `/api/ws/chat` WebSocket
- `lib/server/watchdog-terminal-ws.js` — terminal WS bridge + `/openclaw*` passthrough
- `lib/server/operation-events.js` — operation event store
- `lib/server/constants.js` — `SETUP_API_PREFIXES`, Codex constants, gateway port/host
- `lib/server/alphaclaw-config.js` — `/v1` enablement flag

## Related

- [[alphaclaw]] — Main wiki entry (architecture, features)
- [[alphaclaw-api]] — Per-endpoint REST reference for the management APIs
- [[alphaclaw-deployment]] — Render/Railway/Docker deployment, env vars, git shim
- [[openclaw]] — The gateway AlphaClaw wraps and proxies
- [[goclaw]] — Go MCP gateway (alternative)
