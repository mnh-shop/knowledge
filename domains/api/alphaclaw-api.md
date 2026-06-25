---
name: alphaclaw-api
description: "AlphaClaw REST API — gateway management, agent configuration, MCP and channel setup"
tags: [acp, ai-llm, cli, documentation, git, mcp, rest-api, security, webhook]
---
# AlphaClaw API

**Source repo:** `@chrysb/alphaclaw` (v0.9.18)
**Framework:** Express 4.x (`express@^4.21.0`) with `http-proxy@^1.18.1` reverse proxy
**Default port:** 3000
**Auth:** Password-protected (`SETUP_PASSWORD`) with brute-force lockout (exponential backoff)

## Architecture

```
Setup UI (Preact + htm) --> Express Server --> Proxy --> OpenClaw Gateway (child process, 127.0.0.1:18789)
                              |                    |
                          JSON APIs            /v1/* proxy
                       (status, envars,         (chat, models,
                        channels, webhooks,      embeddings)
                        cron, watchdog,
                        usage, etc.)
```

AlphaClaw runs a single Express server that serves:
1. The Setup UI (Preact SPA with Wouter routing) plus static assets
2. JSON management APIs (password-authenticated)
3. An **optional** OpenAI-compatible `/v1` proxy to the OpenClaw gateway child process
4. Server-Sent Events (SSE) for real-time status updates
5. WebSocket-based interactive terminal sessions (watchdog)

## OpenAI-Compatible `/v1` Proxy

Disabled by default. Toggled via Setup UI (General -> Features -> API). Persisted in `alphaclaw.json`.

| Endpoint | Method | Notes |
|---|---|---|
| `/v1/chat/completions` | POST | Streams when `stream: true`. Use `model: "openclaw/default"` or `openclaw/<agentId>`. 50 MB body limit. |
| `/v1/responses` | POST | Routes to OpenClaw's `/v1/responses` surface. |
| `/v1/embeddings` | POST | Routes to OpenClaw's embeddings endpoint. |
| `/v1/models` | GET | Lists OpenClaw agent targets. |
| `/v1/models/:id` | GET | Single model info. |

**Auth:** `Authorization: Bearer <OPENCLAW_GATEWAY_TOKEN>` required. Failed attempts are rate-limited. Setup-UI cookie is stripped before forwarding. Hop-by-hop response headers are not passed through.

**Security:** A valid `OPENCLAW_GATEWAY_TOKEN` grants full operator access -- the caller can run any tool the configured agent profile allows. Intended for trusted server-to-server callers only.

## Management API Endpoints (Authenticated)

All endpoints served under the Setup UI route and protected by session password auth.

### Status & Health
| Endpoint (inferred from `api.js`) | Method | Description |
|---|---|---|
| `/api/status` | GET | Gateway status, channel health, feature health, version info |
| `/api/gateway/restart` | POST | Restart the OpenClaw gateway |
| `/api/restart-status` | GET | Check gateway restart progress |
| `/api/restart-status/dismiss` | POST | Clear restart notification |

### Environment Variables
| Endpoint | Method | Description |
|---|---|---|
| `/api/env` | GET | List environment variables |
| `/api/env` | PUT | Save environment variables to `/data/.env` |

### Channel Pairings
| Endpoint | Method | Description |
|---|---|---|
| `/api/pairings` | GET | List pending pairings |
| `/api/pairings/approve` | POST | Approve a channel pairing |
| `/api/pairings/reject` | POST | Reject a channel pairing |

### Google Workspace
| Endpoint | Method | Description |
|---|---|---|
| `/api/google/accounts` | GET | List connected Google accounts |
| `/api/google/status` | GET | Google OAuth integration status |
| `/api/google/credentials` | GET/POST | Google OAuth client credentials |
| `/api/google/check` | GET | Check enabled Google APIs |
| `/api/google/accounts/save` | POST | Save Google account config |
| `/api/google/disconnect` | POST | Disconnect Google account |
| `/api/gmail/config` | GET/POST | Gmail watch configuration |
| `/api/gmail/watch/start` | POST | Start Gmail Pub/Sub watch |
| `/api/gmail/watch/stop` | POST | Stop Gmail watch |
| `/api/gmail/watch/renew` | POST | Renew Gmail watch |

### Agent Management
| Endpoint | Method | Description |
|---|---|---|
| `/api/agent/sessions` | GET | List agent sessions |
| `/api/agent/message` | POST | Send a message to an agent session |
| `/api/agents` | CRUD | Agent lifecycle (create, read, update, delete) |

### Usage & Sessions
| Endpoint | Method | Description |
|---|---|---|
| `/api/usage/summary?days=N` | GET | Token/cost summary |
| `/api/usage/sessions?limit=N` | GET | Session list |
| `/api/usage/sessions/:id` | GET | Session detail |
| `/api/usage/session/:id/timeseries` | GET | Session time-series data |

### Doctor
| Endpoint | Method | Description |
|---|---|---|
| `/api/doctor/status` | GET | `openclaw doctor` status |
| `/api/doctor/run` | POST | Start a doctor diagnostic run |
| `/api/doctor/runs` | GET | List doctor runs |
| `/api/doctor/runs/:id` | GET | Single doctor run detail |
| `/api/doctor/runs/:id/cards` | GET | Doctor fix cards for a run |
| `/api/doctor/cards/:id/status` | POST | Update card status |
| `/api/doctor/findings/:id/fix` | POST | Send a fix prompt |
| `/api/doctor/import` | POST | Import raw doctor output |

### Webhooks
| Endpoint | Method | Description |
|---|---|---|
| `/api/webhooks` | GET | List webhooks |
| `/api/webhooks/:name` | GET | Webhook detail |
| `/api/webhooks` | POST | Create webhook |
| `/api/webhooks/:name` | DELETE | Delete webhook |
| `/api/webhooks/:name/requests` | GET | Request history |
| `/api/webhooks/:name/requests/:rid` | GET | Single request detail |
| `/api/webhooks/:name/oauth-callback` | POST | Create OAuth callback |
| `/api/webhooks/:name/oauth-callback` | GET | Get OAuth callback |
| `/api/webhooks/:name/oauth-callback/rotate` | POST | Rotate OAuth callback token |
| `/api/webhooks/:name/oauth-callback` | DELETE | Delete OAuth callback |

### Cron Jobs
| Endpoint | Method | Description |
|---|---|---|
| `/api/cron/jobs` | GET | List cron jobs |
| `/api/cron/status` | GET | Cron service status |
| `/api/cron/jobs/:id/runs` | GET | Run history for a job |
| `/api/cron/jobs/:id/usage` | GET | Usage data for a job |
| `/api/cron/jobs/:id/trends` | GET | Trend analytics |
| `/api/cron/jobs/:id/trigger` | POST | Trigger manual run |
| `/api/cron/jobs/:id/toggle` | POST | Enable/disable job |
| `/api/cron/jobs/:id/prompt` | PUT | Update job prompt |
| `/api/cron/jobs/:id/routing` | PUT | Update routing config |
| `/api/cron/bulk-usage` | GET | Bulk usage across jobs |
| `/api/cron/bulk-runs` | GET | Bulk runs across jobs |

### Watchdog
| Endpoint | Method | Description |
|---|---|---|
| `/api/watchdog/status` | GET | Watchdog health and state |
| `/api/watchdog/events?limit=N` | GET | Recent watchdog events |
| `/api/watchdog/logs?tail=N` | GET | Gateway log tail |
| `/api/watchdog/repair` | POST | Trigger auto-repair |
| `/api/watchdog/settings` | GET/PUT | Watchdog configuration |
| `/api/watchdog/resources` | GET | System resource usage |
| `/api/watchdog/terminal` | POST | Create interactive terminal session |
| `/api/watchdog/terminal/:id/output` | GET | Terminal output since cursor |
| `/api/watchdog/terminal/:id/input` | POST | Send terminal input |
| `/api/watchdog/terminal/:id/close` | POST | Close terminal session |

### Sync & Version
| Endpoint | Method | Description |
|---|---|---|
| `/api/sync-cron` | GET/PUT | Git sync cron schedule |
| `/api/alphaclaw/version` | GET | AlphaClaw version info |
| `/api/alphaclaw/release-notes` | GET | Fetch release notes |
| `/api/alphaclaw/update` | POST | Apply update |

### Feature Flags
| Endpoint | Method | Description |
|---|---|---|
| `/api/alphaclaw/config/features/openai-compat-api` | PUT | Enable/disable `/v1` proxy |
| `/api/gateway/dashboard` | GET | OpenClaw dashboard URL |
| `/api/onboard/status` | GET | Onboarding progress |
| `/api/onboard` | POST | Execute onboarding setup |
| `/api/onboard/github/verify` | POST | Verify GitHub repo access |

### Nodes
| Endpoint | Method | Description |
|---|---|---|
| `/api/nodes/status` | GET | Node status |
| `/api/nodes/:id/approve` | POST | Approve a node |
| `/api/nodes/:id` | DELETE | Remove a node |
| `/api/nodes/:id/route-exec` | POST | Route exec to a node |
| `/api/nodes/connect-info` | GET | Node connection details |
| `/api/nodes/:id/browser-status` | GET | Browser attach status |
| `/api/nodes/exec-config` | GET/PUT | Execution configuration |
| `/api/nodes/exec-approvals` | GET | Pending exec approvals |
| `/api/nodes/exec-approvals/allowlist` | POST | Add allowlist pattern |
| `/api/nodes/exec-approvals/allowlist/:id` | DELETE | Remove allowlist pattern |

### Auth
| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/status` | GET | Session auth status |
| `/api/auth/logout` | POST | Logout |

### Device Pairings
| Endpoint | Method | Description |
|---|---|---|
| `/api/devices` | GET | List device pairings |
| `/api/devices/:id/approve` | POST | Approve device |
| `/api/devices/:id/reject` | POST | Reject device |

## Real-Time Events

- **SSE** (`/api/status/events`): Server-Sent Events for status updates -- gateway health, restart progress, login events
- **WebSocket** (watchdog terminal): Interactive terminal sessions for live gateway log monitoring

## Key Dependencies

| Package | Version | Purpose |
|---|---|---|
| `express` | ^4.21.0 | HTTP server framework |
| `http-proxy` | ^1.18.1 | Reverse proxy to OpenClaw gateway |
| `ws` | ^8.19.0 | WebSocket for interactive terminal |
| `openclaw` | 2026.5.28 | Managed child process (gateway + CLI) |

## Core Source Files

- `lib/server.js` -- Express app setup, middleware, server lifecycle
- `lib/server/routes/system.js` -- `registerSystemRoutes()`: envars, status, version, auth profiles
- `lib/server/routes/proxy.js` -- `registerProxyRoutes()`: `/v1/*` OpenAI-compatible proxy
- `lib/server/init/register-server-routes.js` -- `registerServerRoutes()`: aggregates all route modules
- `lib/server/gateway.js` -- Gateway child process lifecycle, proxy config, channel sync
- `lib/server/openclaw-config.js` -- `readOpenclawConfig` / `writeOpenclawConfig` helpers
- `lib/public/js/lib/api.js` -- Frontend API client (all exported functions listed above)
- `lib/server/webhook-middleware.js` -- Webhook delivery middleware
- `lib/server/oauth-callback-middleware.js` -- OAuth callback handling for webhooks
- `lib/server/operation-events.js` -- SSE operation event streaming
