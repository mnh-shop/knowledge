---
title: Hermes Agent REST API
tags: [ai-llm, cli, dashboard, git, plugin-sdk, rest-api]
  - api
  - rest
  - hermes
  - openai-compatible
  - agent
created: 2026-06-24
description: Complete REST API documentation for the Hermes Agent gateway, covering the OpenAI-compatible Chat/Responses APIs, custom Runs API, Sessions/Jobs control plane, skills/toolsets discovery, health probes, and the Dashboard auth API.
---

# Hermes Agent REST API

The Hermes Agent exposes several HTTP API surfaces. The primary one is the **API Server** (OpenAI-compatible HTTP endpoint) that runs inside the gateway process. There is also a **Dashboard API** (FastAPI/Starlette) for web-based administration and a **Proxy Server** for upstream credential brokering.

---

## 1. API Server (OpenAI-Compatible Gateway)

Port: **8642** (default, configurable via `API_SERVER_PORT`)
Host: **127.0.0.1** (default, configurable via `API_SERVER_HOST`)
Auth: **Bearer token** (required, set via `API_SERVER_KEY` env var)

All endpoints are served by `gateway/platforms/api_server.py` (class `APIServerAdapter`) using **aiohttp**.

### 1.1 Health & Discovery

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/health` | No | Simple health check; returns `{"status":"ok","platform":"hermes-agent","version":"<version>"}` |
| `GET` | `/health/detailed` | No | Rich status: gateway state, connected platforms, PID, uptime |
| `GET` | `/v1/health` | No | OpenAI-compatible health check alias |
| `GET` | `/v1/models` | Yes | List available models (advertises the configured profile name or `hermes-agent`) |
| `GET` | `/v1/capabilities` | Yes | Machine-readable feature discovery for orchestrators |
| `GET` | `/v1/skills` | Yes | List installed skills (name, description, category) visible to the API-server agent |
| `GET` | `/v1/toolsets` | Yes | List toolsets and their resolved tools for the `api_server` platform |

**`GET /v1/capabilities` response:**

```json
{
  "object": "hermes.api_server.capabilities",
  "platform": "hermes-agent",
  "model": "hermes-agent",
  "auth": { "type": "bearer", "required": true },
  "runtime": {
    "mode": "server_agent",
    "tool_execution": "server",
    "split_runtime": false,
    "description": "The API server creates a server-side Hermes AIAgent; tools execute on the API-server host unless a future explicit split-runtime mode is enabled."
  },
  "features": {
    "chat_completions": true,
    "chat_completions_streaming": true,
    "responses_api": true,
    "responses_streaming": true,
    "run_submission": true,
    "run_status": true,
    "run_events_sse": true,
    "run_stop": true,
    "run_approval_response": true,
    "tool_progress_events": true,
    "approval_events": true,
    "session_resources": true,
    "session_chat": true,
    "session_chat_streaming": true,
    "session_fork": true,
    "admin_config_rw": false,
    "jobs_admin": false,
    "memory_write_api": false,
    "skills_api": true,
    "audio_api": false,
    "realtime_voice": false,
    "session_continuity_header": "X-Hermes-Session-Id",
    "session_key_header": "X-Hermes-Session-Key",
    "cors": false
  },
  "endpoints": {
    "health": { "method": "GET", "path": "/health" },
    "health_detailed": { "method": "GET", "path": "/health/detailed" },
    "models": { "method": "GET", "path": "/v1/models" },
    "chat_completions": { "method": "POST", "path": "/v1/chat/completions" },
    "responses": { "method": "POST", "path": "/v1/responses" },
    "runs": { "method": "POST", "path": "/v1/runs" },
    "run_status": { "method": "GET", "path": "/v1/runs/{run_id}" },
    "run_events": { "method": "GET", "path": "/v1/runs/{run_id}/events" },
    "run_approval": { "method": "POST", "path": "/v1/runs/{run_id}/approval" },
    "run_stop": { "method": "POST", "path": "/v1/runs/{run_id}/stop" },
    "skills": { "method": "GET", "path": "/v1/skills" },
    "toolsets": { "method": "GET", "path": "/v1/toolsets" },
    "sessions": { "method": "GET", "path": "/api/sessions" },
    "session_create": { "method": "POST", "path": "/api/sessions" },
    "session": { "method": "GET", "path": "/api/sessions/{session_id}" },
    "session_update": { "method": "PATCH", "path": "/api/sessions/{session_id}" },
    "session_delete": { "method": "DELETE", "path": "/api/sessions/{session_id}" },
    "session_messages": { "method": "GET", "path": "/api/sessions/{session_id}/messages" },
    "session_fork": { "method": "POST", "path": "/api/sessions/{session_id}/fork" },
    "session_chat": { "method": "POST", "path": "/api/sessions/{session_id}/chat" },
    "session_chat_stream": { "method": "POST", "path": "/api/sessions/{session_id}/chat/stream" }
  }
}
```

**`GET /v1/skills` response:**

```json
{
  "object": "list",
  "data": [
    { "name": "github-pr-workflow", "description": "...", "category": "development" },
    { "name": "web-research", "description": "...", "category": "research" }
  ]
}
```

**`GET /v1/toolsets` response:**

```json
{
  "object": "list",
  "platform": "api_server",
  "data": [
    {
      "name": "core",
      "label": "Core Tools",
      "description": "Essential file and terminal tools",
      "enabled": true,
      "configured": true,
      "tools": ["read_file", "write_file", "terminal", "web_search"]
    }
  ]
}
```

### 1.2 Chat Completions API

OpenAI Chat Completions format. Stateless -- the full conversation is included in each request.

**`POST /v1/chat/completions`**

Auth: Bearer token
Content-Type: `application/json`

**Request body:**

```json
{
  "model": "hermes-agent",
  "messages": [
    { "role": "system", "content": "You are a Python expert." },
    { "role": "user", "content": "Write a fibonacci function" }
  ],
  "stream": false,
  "temperature": 0.7,
  "tools": [],
  "tool_choice": "auto"
}
```

- `model`: Ignored for routing; all requests are handled by hermes-agent. The advertised model name is configurable via `API_SERVER_MODEL_NAME`.
- `messages[].content` can be a string or an array of content parts.
- **Image input:** user messages may contain `image_url` parts with remote `http(s)://` or `data:image/...` URLs. Non-image `data:` URLs and `file` / `input_file` / `file_id` parts return `400 unsupported_content_type`.
- `stream: true`: Returns SSE with `chat.completion.chunk` events plus custom `event: hermes.tool.progress` for tool-start visibility.

**Non-streaming response** (200):

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1710000000,
  "model": "hermes-agent",
  "choices": [{
    "index": 0,
    "message": { "role": "assistant", "content": "Here's a fibonacci function..." },
    "finish_reason": "stop"
  }],
  "usage": { "prompt_tokens": 50, "completion_tokens": 200, "total_tokens": 250 }
}
```

**Streaming SSE events:**

```
data: {"id":"chatcmpl-...","object":"chat.completion.chunk","choices":[{"index":0,"delta":{"role":"assistant"},"finish_reason":null}]}

data: {"id":"chatcmpl-...","object":"chat.completion.chunk","choices":[{"index":0,"delta":{"content":"Here "},"finish_reason":null}]}

event: hermes.tool.progress
data: {"type":"tool.started","tool":"read_file","emoji":"📖","label":"Reading file...","toolCallId":"call_1","status":"running"}

event: hermes.tool.progress
data: {"type":"tool.completed","tool":"read_file","emoji":"📖","label":"Reading file...","toolCallId":"call_1","status":"completed"}

data: {"id":"chatcmpl-...","object":"chat.completion.chunk","choices":[{"index":0,"delta":{"content":" done."},"finish_reason":null}]}

data: [DONE]
```

**Error response** (4xx/5xx):

```json
{
  "error": { "message": "Unsupported content type: file", "type": "unsupported_content_type", "code": "unsupported_content_type" }
}
```

### 1.3 Responses API

OpenAI Responses API format with server-side conversation state.

**`POST /v1/responses`**

Auth: Bearer token

**Request body:**

```json
{
  "model": "hermes-agent",
  "input": "What files are in my project?",
  "instructions": "You are a helpful coding assistant.",
  "store": true,
  "stream": false,
  "previous_response_id": null,
  "conversation": null
}
```

| Field | Type | Description |
|-------|------|-------------|
| `input` | string or array | User input; can be a plain string or an array of `{role, content}` objects |
| `instructions` | string | System prompt layered on top of Hermes' core prompt |
| `store` | boolean | Whether to persist the response for chaining (default: `true`) |
| `previous_response_id` | string | Chain to a previous response; server reconstructs full context |
| `conversation` | string | Named conversation; server auto-chains to the latest response in that name |
| `conversation_history` | array | Explicit history override (takes precedence over `previous_response_id`) |
| `stream` | boolean | Use SSE streaming with Responses event types |

**Response** (non-streaming):

```json
{
  "id": "resp_abc123",
  "object": "response",
  "status": "completed",
  "model": "hermes-agent",
  "created_at": 1710000000,
  "output": [
    { "type": "function_call", "name": "terminal", "arguments": "{\"command\": \"ls\"}", "call_id": "call_1" },
    { "type": "function_call_output", "call_id": "call_1", "output": "README.md src/ tests/" },
    { "type": "message", "role": "assistant", "content": [{ "type": "output_text", "text": "Your project has..." }] }
  ],
  "usage": { "input_tokens": 50, "output_tokens": 200, "total_tokens": 250 }
}
```

**Streaming SSE events** (Responses format):

```
event: response.created
data: {"type":"response.created","response":{"id":"resp_...","status":"in_progress",...}}

event: response.output_item.added
data: {"type":"response.output_item.added","item":{"type":"function_call","name":"terminal","call_id":"call_1",...},"output_index":0}

event: response.output_text.delta
data: {"type":"response.output_text.delta","delta":"Here ","item_id":"msg_..."}

event: response.output_item.done
data: {"type":"response.output_item.done","item":{"type":"function_call","name":"terminal","arguments":"{\"command\":\"ls\"}",...}}

event: response.output_item.added
data: {"type":"response.output_item.added","item":{"type":"function_call_output","call_id":"call_1","output":"README.md..."}}

event: response.completed
data: {"type":"response.completed","response":{"id":"resp_...","status":"completed",...}}

event: response.failed
data: {"type":"response.failed","response":{"id":"resp_...","status":"failed","error":{"code":"...","message":"..."}}}
```

**`GET /v1/responses/{response_id}`**

Retrieve a previously stored response by ID.

**`DELETE /v1/responses/{response_id}`**

Delete a stored response.

### 1.4 Runs API

Long-form session API with subscription-style progress events.

**`POST /v1/runs`**

Auth: Bearer token

**Request:**

```json
{
  "input": "hello",
  "model": "hermes-agent",
  "instructions": "Optional system prompt",
  "session_id": "optional-existing-session",
  "conversation_history": [],
  "previous_response_id": null
}
```

**Response** (202):

```json
{
  "run_id": "run_abc123",
  "status": "started"
}
```

**`GET /v1/runs/{run_id}`**

Poll current run state. Retained briefly after terminal states.

```json
{
  "object": "hermes.run",
  "run_id": "run_abc123",
  "status": "completed",
  "session_id": "space-session",
  "model": "hermes-agent",
  "output": "Done.",
  "usage": { "input_tokens": 50, "output_tokens": 200, "total_tokens": 250 }
}
```

| Status | Meaning |
|--------|---------|
| `started` | Run created, waiting for agent |
| `running` | Agent is processing |
| `completed` | Agent finished successfully |
| `failed` | Agent encountered an error |
| `cancelled` | Run was interrupted by stop request |

**`GET /v1/runs/{run_id}/events`**

SSE stream of run progress: tool-call events, token deltas, lifecycle events.

**`POST /v1/runs/{run_id}/stop`**

Interrupt a running agent turn. Returns `{"status": "stopping"}`.

**`POST /v1/runs/{run_id}/approval`**

Resolve a pending approval. Body carries the approval decision.

```json
{
  "decision": "approve",
  "tool_call_id": "call_1"
}
```

### 1.5 Sessions API

CRUD for agent sessions over REST. All gated by `API_SERVER_KEY`.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/sessions` | List sessions (paginated; query: `limit`, `offset`, `source`, `include_children`) |
| `POST` | `/api/sessions` | Create an empty session |
| `GET` | `/api/sessions/{session_id}` | Read session metadata |
| `PATCH` | `/api/sessions/{session_id}` | Update title or `end_reason` |
| `DELETE` | `/api/sessions/{session_id}` | Delete a session |
| `GET` | `/api/sessions/{session_id}/messages` | Message history for a session |
| `POST` | `/api/sessions/{session_id}/fork` | Branch the session via SessionDB lineage |
| `POST` | `/api/sessions/{session_id}/chat` | Run one synchronous agent turn |
| `POST` | `/api/sessions/{session_id}/chat/stream` | SSE stream over a single turn |

**`POST /api/sessions`** request body:

```json
{
  "id": "optional-custom-id",
  "title": "Mobile chat",
  "model": "test-model",
  "system_prompt": "Optional system prompt snapshot"
}
```

**`POST /api/sessions/{session_id}/chat`** request body:

```json
{
  "message": "What files changed?",
  "input": "Alternative to `message`",
  "system_message": "Per-turn system prompt override",
  "instructions": "Alternative to `system_message`"
}
```

**SSE events for `/api/sessions/{session_id}/chat/stream`:**

| Event type | Description |
|-----------|-------------|
| `assistant.delta` | Token-by-token text delta |
| `tool.started` | Tool execution started |
| `tool.completed` | Tool execution completed |
| `run.completed` | Final turn transcript + usage |

**`POST /api/sessions/{session_id}/fork`** request body:

```json
{
  "title": "Alternative exploration",
  "id": "optional-fork-id"
}
```

### 1.6 Jobs API

Background scheduled agent runs.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/jobs` | List all scheduled jobs |
| `POST` | `/api/jobs` | Create a new scheduled job |
| `GET` | `/api/jobs/{job_id}` | Fetch a job's definition and last-run state |
| `PATCH` | `/api/jobs/{job_id}` | Update fields on an existing job (partial merge) |
| `DELETE` | `/api/jobs/{job_id}` | Remove a job and cancel in-flight run |
| `POST` | `/api/jobs/{job_id}/pause` | Pause a job without deleting |
| `POST` | `/api/jobs/{job_id}/resume` | Resume a paused job |
| `POST` | `/api/jobs/{job_id}/run` | Trigger immediate execution |
| `POST` | `/api/cron/fire` | Internal: fire a job by `job_id` (uses `API_SERVER_KEY` or a dedicated cron token) |

**`POST /api/jobs`** request body shares the same shape as `hermes cron`:

```json
{
  "name": "daily-summary",
  "prompt": "Summarize today's changes",
  "schedule": "0 9 * * *",
  "skills": ["github-pr-workflow"],
  "provider": "anthropic",
  "deliver": { "platform": "slack", "channel": "#general" },
  "repeat": true,
  "idempotency_key": "optional-dedup-key"
}
```

Prompt injection protection: malicious prompts (e.g., those containing encoded data exfiltration commands) are rejected at creation/update time with a 4xx response.

### 1.7 Authentication & Request Headers

**Bearer token authentication:**

```
Authorization: Bearer <API_SERVER_KEY>
```

Configured via `API_SERVER_KEY` env var (required for every deployment).

**Session continuity headers:**

| Header | Description |
|--------|-------------|
| `X-Hermes-Session-Id` | Transcript-scoped session identifier (rotates on `/new`). Server loads conversation history from `state.db` when provided. Requires API key auth. |
| `X-Hermes-Session-Key` | Stable per-channel identifier for long-term memory providers (Honcho). Independent of session id. Max 256 chars, no control characters. |
| `Idempotency-Key` | Deduplication for chat completions. Responses are cached by key for 5 minutes. |

**Response headers:**

- `X-Hermes-Session-Id`: Echoes the session ID back on chat/runs/responses endpoints
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: no-referrer`

---

## 2. Dashboard API (FastAPI)

The Hermes Dashboard runs a **FastAPI** / **Starlette** server (port 9119, enabled via `HERMES_DASHBOARD=1`). It serves both the SPA frontend and a set of backend API routes for authentication, plugin APIs, memory OAuth flows, and achievements.

### 2.1 Auth Routes (`hermes_cli/dashboard_auth/routes.py`)

All auth routes use `APIRouter()`.

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/login` | No | Server-rendered login page (HTML, no SPA bundle) |
| `GET` | `/api/auth/providers` | No | List configured auth providers |
| `GET` | `/auth/login` | No | Redirect to OAuth provider (query: `provider`, `next`) |
| `GET` | `/auth/callback` | No | OAuth callback handler |
| `POST` | `/auth/password-login` | Rate-limited | Password-based login (10 attempts / 60s per IP) |
| `POST` | `/auth/logout` | Yes | Logout, clear session |
| `GET` | `/api/auth/me` | Yes | Return current session info |
| `POST` | `/api/auth/ws-ticket` | Yes | Mint a 30-second WebSocket auth ticket |

**`POST /auth/password-login`** request:

```json
{
  "provider": "basic",
  "username": "admin",
  "password": "***",
  "next": "/sessions"
}
```

**`POST /auth/password-login`** response:

```json
{ "ok": true, "next": "/sessions" }
```

### 2.2 Memory OAuth Routes (`hermes_cli/memory_oauth.py`)

Fronts OAuth flows for memory providers.

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/memory/providers/{provider}/oauth/start` | Yes | Start memory provider OAuth flow |
| `GET` | `/api/memory/providers/{provider}/oauth/status` | Yes | Poll OAuth status |

### 2.3 Plugin API Routes

Each dashboard plugin can register its own API routes via `APIRouter()`.

**Example fixture** (`/hello`):

```python
router = APIRouter()
@router.get("/hello")
async def hello(): ...
```

### 2.4 Achievement Routes (`plugins/hermes-achievements/`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/achievements` | List all achievements with unlock status |
| `GET` | `/scan-status` | Scanning progress |
| `GET` | `/recent-unlocks` | Recently unlocked achievements |
| `GET` | `/sessions/{session_id}/badges` | Badges for a specific session |
| `POST` | `/rescan` | Trigger a rescan |
| `POST` | `/reset-state` | Reset achievement state |

### 2.5 Task/Kanban Routes (`plugins/hermes-kanban/`)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/tasks` | Create a new kanban task. Supports `parents`, `triage`, `idempotency_key`, `max_runtime_seconds`, `skills`, `goal_mode`, `goal_max_turns`. |

---

## 3. Proxy Server (aiohttp)

Port: **8645** (default)
Host: **127.0.0.1**

A lightweight reverse proxy for upstream API credentials (e.g., Nous Portal, xAI OAuth).

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `*` | `/v1/{tail:.*}` | Proxy upstream — passes all paths/methods to the configured upstream adapter |

**Catch-all proxy behavior:** strips hop-by-hop headers, adds bearer auth from the upstream credential store, streams request/response body bidirectionally.

---

## 4. Common Schemas

### 4.1 Error Response

```json
{
  "error": {
    "message": "Human-readable error description",
    "type": "error_type",
    "code": "error_code"
  }
}
```

### 4.2 Session Object

```json
{
  "id": "api_1710000000_a1b2c3d4",
  "source": "api_server",
  "model": "hermes-agent",
  "title": "Mobile chat",
  "started_at": 1710000000,
  "ended_at": null,
  "last_active": 1710000100,
  "end_reason": null,
  "message_count": 5,
  "input_tokens": 250,
  "output_tokens": 600,
  "total_tokens": 850
}
```

### 4.3 Job Object

```json
{
  "id": "job_a1b2c3d4",
  "name": "daily-summary",
  "prompt": "Summarize today's changes",
  "enabled": true,
  "schedule": "0 9 * * *",
  "skills": ["github-pr-workflow"],
  "provider": null,
  "last_run_at": 1710000000,
  "next_run_at": 1710086400,
  "created_at": 1709913600
}
```

### 4.4 Capability Feature Flags

All boolean flags in `/v1/capabilities.features`:

| Feature | Type | Description |
|---------|------|-------------|
| `chat_completions` | bool | OpenAI Chat Completions endpoint |
| `chat_completions_streaming` | bool | SSE streaming for Chat Completions |
| `responses_api` | bool | OpenAI Responses API endpoint |
| `responses_streaming` | bool | SSE streaming for Responses API |
| `run_submission` | bool | Runs API submission |
| `run_status` | bool | Run status polling |
| `run_events_sse` | bool | Run event SSE stream |
| `run_stop` | bool | Run cancellation |
| `run_approval_response` | bool | Run approval resolution |
| `tool_progress_events` | bool | Tool lifecycle SSE events |
| `approval_events` | bool | Approval-related SSE events |
| `session_resources` | bool | Session CRUD endpoints |
| `session_chat` | bool | Session synchronous chat |
| `session_chat_streaming` | bool | Session SSE chat |
| `session_fork` | bool | Session fork/branch |
| `admin_config_rw` | bool | Admin configuration (read/write) |
| `jobs_admin` | bool | Jobs API endpoints |
| `memory_write_api` | bool | Memory provider write API |
| `skills_api` | bool | Skills listing |
| `audio_api` | bool | Audio/whisper API |
| `realtime_voice` | bool | Realtime voice API |
| `session_continuity_header` | string | Header name for session continuity (`X-Hermes-Session-Id`) |
| `session_key_header` | string | Header name for stable memory scope (`X-Hermes-Session-Key`) |
| `cors` | bool | CORS is configured |

---

## 5. Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_SERVER_ENABLED` | `false` | Enable the API server |
| `API_SERVER_PORT` | `8642` | HTTP server port |
| `API_SERVER_HOST` | `127.0.0.1` | Bind address |
| `API_SERVER_KEY` | _(required)_ | Bearer token for authentication |
| `API_SERVER_CORS_ORIGINS` | _(none)_ | Comma-separated allowed browser origins |
| `API_SERVER_MODEL_NAME` | _(profile name)_ | Model name advertised on `/v1/models` |

### Implementation Details

- Framework: **aiohttp** (`web.Application`)
- Streaming: **Server-Sent Events** (SSE) with `text/event-stream`
- All CORS preflight responses include `Access-Control-Max-Age: 600`
- SSE headers include `Cache-Control: no-cache` and `X-Accel-Buffering: no`
- Concurrent run cap: configurable via `gateway.api_server.max_concurrent_runs` in `config.yaml` (default: 10, 0 = disabled)
- Sessions persisted to `state.db`
- Code location: `gateway/platforms/api_server.py` (class `APIServerAdapter`)
- Dashboard server: port 9119, enabled by `HERMES_DASHBOARD=1`
- Proxy server: port 8645, started via `hermes proxy start`
