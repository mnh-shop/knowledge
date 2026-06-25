---
name: mission-control-api
tags: [mission-control, api, typescript, nextjs, react, dashboard, orchestration, monitoring, rest-api, acp, ai-llm, automation, event-bus, git, mcp, messaging, optimization, plugin-sdk, security, storage, webhook]
description: Mission Control API
---

# Mission Control API
**Source:** `sources/mission-control/`

## Overview

Mission Control exposes a comprehensive REST API (approximately 101 endpoints), an MCP server (35 tools), a CLI (60+ subcommands), a webhook delivery system, and an SSE event stream. All interfaces are backed by the same auth layer and data store.

---

## REST API

**Spec**: OpenAPI 3.1.0 at `/openapi.json`, version 1.3.0. Interactive docs at `/docs` when running.

**Authentication**: Two security schemes in parallel -- `sessionCookie` (browser dashboard, cookie-based) and `apiKey` (agent/headless access via `x-api-key` header or `Authorization: Bearer`).

### Endpoint Groups

| Tag | Endpoints | Purpose |
|-----|-----------|---------|
| Auth | login, logout, me, users, google, access-requests | Session management, user CRUD, role-based access |
| Agents | CRUD + register, sync, heartbeat, wake, diagnostics, attribution, memory, soul, keys, files, hide, comms, message, evals, optimize | Full agent lifecycle, memory/soul as sub-resources, inter-agent messaging |
| Tasks | CRUD + queue, broadcast, comments, outcomes, regression, branch/PR | Task lifecycle with priority-driven queue, threaded comments, analytics |
| Sessions | list, continue, transcript, control (pause/resume/kill) | Gateway (OpenClaw + Hermes) and local (Claude Code, Codex) session management |
| Webhooks | CRUD + deliveries, retry, test, verify-docs | Outbound webhook delivery with circuit breaker, retry, HMAC signing |
| Alerts | CRUD | Alert rule configuration |
| Workflows | CRUD | Workflow template management |
| Pipelines | CRUD + run | Pipeline orchestration |
| Monitoring | activities, events (SSE), logs, notifications, health, status, system-monitor, workload | Real-time and historical monitoring |
| Admin | gateways, gateway-config, cron, scheduler, memory, memory/search, memory/graph, memory/links, memory/process, skills, skills/registry, export, backup, settings, integrations, github, gnap, security-audit, security-scan, cleanup, audit, spawn, standup | System administration, knowledge base, external tool integration |
| Tokens | list, stats, by-agent, agent-costs, task-costs, trends, export, rotate | Token usage tracking and cost analysis |
| Connections | register, list, disconnect | Direct CLI tool-to-agent connections |
| Projects | CRUD + agent assignments, task listing | Project management |
| Quality | list, review | Quality review gate for tasks |
| Releases | check, update | Release checking and self-update |
| Docs | catalog, content, search, tree | API documentation viewer |
| Super Admin | tenants, provision-jobs, os-users | Multi-tenant provisioning |
| Mentions | autocomplete | User and agent mention autocomplete |
| Chat | conversations, messages, session-prefs | Chat/messaging |

### Architectural Patterns

- All routes are Next.js App Router `route.ts` handlers (`src/app/api/**/route.ts`)
- Auth checked at top of each handler via `requireRole(request, minimumRole)` -- roles: viewer, operator, admin
- `/api/hermes/*` and `/api/openclaw/*` are dedicated interop namespaces
- Workspace-scoping applied throughout via `requireWorkspaceId`
- Rate limiting on mutation endpoints via `mutationLimiter`

---

## MCP Server

**Script**: `scripts/mc-mcp-server.cjs`

**Protocol**: JSON-RPC 2.0 over stdio transport, implementing the MCP specification (protocol version 2024-11-05). Capabilities declared: `{ tools: {} }`.

**Addition to Claude Code**:
```bash
claude mcp add mission-control -- node /path/to/mission-control/scripts/mc-mcp-server.cjs
```

Environment config: `MC_URL` (default http://127.0.0.1:3000), `MC_API_KEY`, `MC_COOKIE`. Profile support reads from `~/.mission-control/profiles/default.json`.

### 35 Tools -- Categorized

**Agents (5 tools)**: `mc_list_agents`, `mc_get_agent`, `mc_heartbeat`, `mc_wake_agent`, `mc_agent_diagnostics`, `mc_agent_attribution`

**Agent Memory (3 tools)**: `mc_read_memory`, `mc_write_memory`, `mc_clear_memory`

**Knowledge Base (7 tools)**: `mc_search_knowledge` (FTS5/BM25), `mc_read_knowledge_file`, `mc_write_knowledge_file`, `mc_knowledge_health`, `mc_rebuild_search_index`, `mc_knowledge_gaps` (broken links, orphans, stale content), `mc_knowledge_consolidate` (graph analysis, hub/bridge/cluster detection)

**Agent Soul (3 tools)**: `mc_read_soul`, `mc_write_soul` (inline content or template), `mc_list_soul_templates`

**Tasks (7 tools)**: `mc_list_tasks` (with status/assignee/priority/search/limit filters), `mc_get_task`, `mc_create_task`, `mc_update_task`, `mc_poll_task_queue` (poll by agent name and capacity), `mc_broadcast_task`, `mc_list_comments`, `mc_add_comment`

**Sessions (4 tools)**: `mc_list_sessions`, `mc_control_session` (monitor/pause/terminate), `mc_continue_session` (send follow-up prompt), `mc_session_transcript`

**Connections (2 tools)**: `mc_list_connections`, `mc_register_connection`

**Tokens and Costs (3 tools)**: `mc_token_stats`, `mc_agent_costs`, `mc_costs_by_agent`

**Skills (1 tool)**: `mc_list_skills`, `mc_read_skill`

**Cron (1 tool)**: `mc_list_cron`

**Status (3 tools)**: `mc_health`, `mc_dashboard`, `mc_status`

**Runs (7 tools)**: `mc_list_runs`, `mc_get_run`, `mc_create_run`, `mc_update_run`, `mc_run_provenance` (hash chain, model version, config hash), `mc_attach_eval`, `mc_eval_leaderboard`

### Implementation

Zero dependencies (Node.js built-ins only). Uses `fetch()` with a 30-second timeout. Stdio line-based transport -- each line parsed as JSON-RPC 2.0, dispatched to `handleMessage` switch (initialize, tools/list, tools/call, ping). Results JSON-stringified and written to stdout. Errors surface as MCP error content vs. JSON-RPC errors based on code path.

---

## CLI Interface

**Script**: `scripts/mc-cli.cjs`

**Design**: Zero heavy dependencies (Node.js built-ins only). API-key first for agent automation. JSON mode via `--json` flag. Stable exit codes.

**Profile system**: `~/.mission-control/profiles/default.json` stores URL, API key, and session cookie. Profiles loaded with `--profile <name>`, overridable per flag.

### Exit Code Contract

| Code | Meaning |
|------|---------|
| 0 | Success |
| 2 | Usage error |
| 3 | Auth error (401) |
| 4 | Permission error (403) |
| 5 | Network/timeout |
| 6 | Server error (5xx) |

### Command Groups (13 groups, 60+ subcommands)

- **auth**: login (with credential save), logout, whoami
- **agents**: list, get, create, update, delete, wake, diagnostics, heartbeat, attribution, memory (get/set/clear), soul (get/set/templates)
- **tasks**: list, get, create, update, delete, queue, broadcast, comments (list/add)
- **sessions**: list, control, continue, transcript
- **connect**: register, list, disconnect
- **tokens**: list, stats, by-agent, agent-costs, task-costs, trends, export, rotate
- **skills**: list, content, upsert, delete, check
- **cron**: list, create, update, pause, resume, remove, run
- **events**: watch (SSE streaming to stdout, NDJSON in --json mode)
- **status**: health, overview, dashboard, gateway, models, capabilities
- **export**: audit, tasks, activities, pipelines (JSON/CSV format)
- **raw**: HTTP passthrough (--method, --path, --body)

### SSE Event Streaming

The `events watch` command opens a `text/event-stream` connection via `sseStream()` (fetch + ReadableStream.getReader). Parses standard SSE frames, emits NDJSON in `--json` mode or human-readable lines otherwise. Heartbeat events silently dropped. SIGINT/SIGTERM triggers graceful shutdown via AbortController.

---

## Webhook System

### Architecture

The webhook system bridges the server-side `eventBus` to external HTTP endpoints. When a database mutation event fires on the event bus, `initWebhookListener()` checks an `EVENT_MAP` to see if it maps to a webhook event type:

| Bus Event | Webhook Event Type |
|-----------|-------------------|
| activity.created | activity.{data.type} |
| notification.created | notification.{data.type} |
| agent.status_changed | agent.status_change (also agent.error on error) |
| audit.security | security.{data.action} |
| task.created | activity.task_created |
| task.updated | activity.task_updated |
| task.deleted | activity.task_deleted |
| task.status_changed | activity.task_status_changed |

### Delivery Payload

```json
{
  "event": "activity.task_created",
  "timestamp": 1717000000,
  "data": { ... }
}
```

Headers: `Content-Type: application/json`, `User-Agent: MissionControl-Webhook/1.0`, `X-MC-Event` (event type), `X-MC-Signature` (HMAC-SHA256 if secret configured).

### Retry and Circuit Breaker

- **Backoff schedule** (seconds): 30, 300 (5m), 1800 (30m), 7200 (2h), 28800 (8h)
- Configurable via `MC_WEBHOOK_MAX_RETRIES` (default 5)
- **Jitter**: +/- 20% on each retry delay
- **Circuit breaker**: After max retries exhausted, webhook automatically disabled (`enabled = 0`)
- **Retry scheduling**: Stored in `webhook_deliveries.next_retry_at` column; processed by scheduler via `processWebhookRetries()`

### Management

- **Create**: Admin-only, requires `name`, `url`, `events` (array or `["*"]`). Generates random 32-byte hex secret. SSRF protection blocks private IPs, localhost, `.local` domains, and metadata endpoints.
- **Update**: name, url, events, enabled, regenerate secret, reset circuit breaker
- **Delete**: Cascading delete of delivery history
- **Test**: Fires immediately without retry, returns delivery result
- **History**: Paginated delivery log with status codes, response bodies (truncated to 1000 chars), and retry attempt tracking
- **Retry**: Manual retry of a specific failed delivery

### Verification

Consumers verify webhooks by computing `sha256=HMAC-SHA256(secret, rawBody)` and comparing with `X-MC-Signature` header using constant-time comparison (`timingSafeEqual`). A dummy buffer comparison is used when lengths differ to prevent timing attacks.

---

## SSE Event System

### Server Event Bus

Singleton `ServerEventBus` class extends Node.js `EventEmitter` (max 50 listeners). Uses `globalThis` to survive HMR. Event types include: `task.*`, `chat.message`, `notification.*`, `agent.*`, `audit.security`, `security.event`, `connection.*`, `github.synced`, `run.*`, `session.updated`, `activity.*`.

### SSE Connection

`GET /api/events` -- requires viewer role. Returns a `ReadableStream` with SSE framing:

1. Connection event sent immediately: `{ type: "connected", data: null, timestamp }`
2. Event forwarding: All `ServerEvent` objects forwarded as `data: { type, data, timestamp }` frames
3. Workspace scoping: Events with `workspace_id` that don't match viewer's workspace are filtered server-side
4. Heartbeat: Every 30 seconds, a comment line (`: heartbeat`) to keep proxies alive
5. Cleanup: On stream cancellation or request abort, listener properly removed

Response headers: `Content-Type: text/event-stream`, `Cache-Control: no-cache, no-transform`, `Connection: keep-alive`, `X-Accel-Buffering: no`.

### Event Producers

Events broadcast by:
- Framework adapters on agent register/heartbeat/task updates
- Hermes hook events handler (`/api/hermes/events`)
- Database mutation handlers throughout `src/app/api/` routes
- Webhook listener subscribes to the same bus for `activity.*`, `notification.*`, `agent.*`, `task.*`, and `security.*` events

### Consumers

- SSE clients: browser dashboards, CLI `events watch` command, any `EventSource` consumer
- Webhook dispatcher: `initWebhookListener()` subscribes to `server-event` and dispatches to configured webhooks

---

## Integration Patterns

### Mission Control to Hermes Agent

**Three-layer connection:**

1. **Co-located file system access** -- MC reads Hermes state directly from disk: `~/.hermes/` for installation detection, `~/.hermes/cron/` for cron jobs, `~/.hermes/memory/` for memory entries
2. **Process execution** -- MC can run `hermes` CLI commands via `POST /api/hermes` with `action: "run-command"`, OAuth device-code flows via `action: "run-oauth-model"`, set env vars via `action: "set-env"`, set SOUL.md via `action: "set-soul"`
3. **Hook-based telemetry** -- MC installs a Hermes hook at `~/.hermes/hooks/mission-control/` containing `HOOK.yaml` (event subscriptions: agent:start, agent:end, session:start) and `handler.py`. The hook fires events to MC's `/api/hermes/events` endpoint on agent start/end and session start.

**API routes**: `/api/hermes` (GET=status, POST=actions), `/api/hermes/events` (POST=receive telemetry), `/api/hermes/tasks` (GET=read cron jobs), `/api/hermes/memory` (GET=read memory files)

### Mission Control to OpenClaw ACP

**Gateway-Aware Architecture:**

MC connects to OpenClaw through a **gateway abstraction**. An OpenClaw instance runs as a gateway server (default port 18789) exposing a WebSocket endpoint for agent sessions. MC manages gateway registrations and mediates the browser-to-gateway WebSocket connection.

- **Gateway Registry** (`/api/gateways`) -- SQLite-backed table storing gateway name, host, port, token, status, is_primary flag
- **Gateway Health Probing** (`POST /api/gateways/health`) -- Server-side probes each gateway's `/health` endpoint, updates status/latency/last_seen
- **Gateway Auto-Discovery** (`GET /api/gateways/discover`) -- Scans systemd service files for running gateway instances
- **OpenClaw Doctor** (`GET/POST /api/openclaw/doctor`) -- Runs `openclaw doctor` as subprocess with TTL caching and single-flight to prevent concurrent invocations
- **Session Continuation** (`/api/sessions/continue`) -- Unified endpoint for sending follow-up prompts to OpenClaw, Hermes, or Claude Code sessions

**API routes**: `/api/openclaw/*` (doctor, update, version), `/api/gateways/*` (CRUD, connect, health, control, discover)

### Mission Control to n8n

There is **no first-party n8n integration**. Viable integration points:

1. **Webhooks (outbound)**: MC fires webhooks on event types (task.created, agent.status_changed, etc.) to an n8n webhook trigger. Payloads signed with HMAC-SHA256.
2. **REST API**: n8n HTTP Request node can call any MC endpoint with `x-api-key` auth.
3. **SSE Event Stream**: n8n could connect to `GET /api/events` as an EventSource client.
4. **Plugin route**: MC has a plugin system (`src/lib/plugins.ts`) supporting `PluginIntegrationDef` with custom `testHandler` functions.

For first-party integration, the architecturally consistent approach would be to add n8n as a new `FrameworkAdapter` implementation (matching the existing pattern: OpenClawAdapter, GenericAdapter, CrewAIAdapter, etc.).

### Mission Control to Agentfield

There is **no first-party Agentfield integration**. Integration patterns available:

1. **Framework Adapter pattern**: Add `AgentfieldAdapter` implementing `FrameworkAdapter` interface in `src/lib/adapters/index.ts`
2. **API bridge namespace**: Create `/api/agentfield/*` namespace following the `/api/hermes/*` pattern
3. **Hook/Webhook pattern**: Install a hook that fires Agentfield events to MC, or have Agentfield consume MC webhooks
4. **Gateway registration**: Register Agentfield gateways in MC's `/api/gateways` system
5. **Direct API consumption**: Agentfield can call any MC REST API endpoint with `x-api-key` auth

Recommended architecture: A dedicated `AgentfieldAdapter` (framework adapter pattern) plus an `/api/agentfield/*` route namespace with webhook/hook mechanism similar to Hermes.

## Related

- [[mission-control]] -- Project overview
- [[mission-control-architecture]] -- API design patterns and routing structure
- [[mission-control-mcp-server]] -- MCP server that wraps these endpoints
- [[mission-control-deployment]] -- Deploying the API server
- [[mission-control-profile]] -- Quick reference for API usage
