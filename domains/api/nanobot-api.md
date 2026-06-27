---
name: nanobot-api
description: "Nanobot OpenAI-compatible REST API — chat completions, agent sessions, tool execution"
source: sources/nanobot/
tags: [agent-profile, cli, documentation, rest-api]
---
# Nanobot REST API (OpenAI-Compatible)

Source repository: `nanobot` (https://github.com/HKUDS/nanobot)
Primary file: `nanobot/api/server.py`
Supporting files: `nanobot/cli/commands.py`, `nanobot/config/schema.py`, `nanobot/agent/loop.py`
Documentation: `docs/openai-api.md`

## Overview

Nanobot exposes a minimal **OpenAI-compatible REST API** for local integrations. It is **not** a full REST framework -- it provides exactly three endpoints mimicking the OpenAI Chat Completions API format, powered by nanobot's internal agent loop. API requests run in a synthetic `api` channel, so the `message` tool does not automatically deliver to external chat platforms unless an explicit channel is specified.

## Framework

The API is built on **`aiohttp`** (`aiohttp.web`):
- Uses `web.Application(client_max_size=20 * 1024 * 1024)` for the WSGI application.
- Routes are defined as bare handler functions (no `aiohttp` route table is used; handlers are registered via `app.router.add_get()` and `app.router.add_post()`).
- No FastAPI / Pydantic-based request validation -- JSON parsing is manual via `request.json()`.
- Streaming uses `web.StreamResponse` for chunked SSE output.

## Endpoints

### `GET /health`
- Returns `{"status": "ok"}` as a simple liveness check.
- Used by gateway monitoring and process health checks.

### `GET /v1/models`
- Returns a static model list containing one model (the configured model name, defaults to `"nanobot"`).
- Response format follows OpenAI's `/v1/models` shape.

### `POST /v1/chat/completions`
The main endpoint. Supports two content types:

#### JSON mode (`Content-Type: application/json`)
Accepts OpenAI-compatible request body:
- `messages` -- array with exactly one `user` message (required).
- `model` -- optional model identifier (ignored; always uses the configured model).
- `stream` -- boolean, enables SSE streaming (default: `false`).
- `session_id` -- optional string for session isolation. Omit for shared default (`api:default`).
- Multimodal content: supports `type: "text"` and `type: "image_url"` content parts; base64 images are saved to the media directory and passed to the agent as file references.

#### Multipart mode (`Content-Type: multipart/form-data`)
For file uploads:
- `message` -- text prompt (first part).
- `session_id` -- optional session identifier (second part).
- `model` -- optional model name (third part).
- Additional parts as files: images (PNG, JPEG, GIF, WebP), documents (PDF, Word, Excel, PowerPoint), text files.
- File size limit: 10 MB per file (enforced by `client_max_size=20 * 1024 * 1024` total).
- Fallback prompt for Chinese users when only a file is uploaded: `"请分析上传的文件"`.

#### Response (Non-Streaming)
Returns a JSON response compatible with OpenAI format:
- `choices[0].message.content` -- the full text response.
- `usage` -- token usage (prompt_tokens, completion_tokens, total_tokens).
- `model` -- model name.

#### Response (Streaming, `stream=true`)
Returns `text/event-stream` with OpenAI-compatible Server-Sent Events:
- Each chunk: `data: {"choices": [{"delta": {"content": "..."}}]}`.
- Termination: `data: [DONE]`.
- Delta chunks emitted via `_on_stream` callback from the agent runner.
- Streaming handles tool-backed requests: stream-end marks segment boundaries but the SSE stream stays open until `process_direct` returns.

## Internal Architecture

### `create_app(agent_loop, *, model_name, request_timeout)` (exported in `__all__`)
Factory function that builds the `web.Application`:
- Takes an `AgentLoop` instance for processing requests.
- `model_name` controls the model identifier returned by `/v1/models` and used in response metadata (default: `"nanobot"`).
- `request_timeout` controls the per-request timeout (default: `120.0` seconds).
- Registers three routes: `/health`, `/v1/models`, `/v1/chat/completions`.
- Stores shared state in `request.app`: `agent_loop`, `session_locks` (per-session asyncio locks), `request_timeout`, `model_name`.
- Convenience `on_startup`/`on_cleanup` hooks for lifecycle management.

### Session Management
- Session key format: `api:{session_id}`, or `api:default` when no session_id is provided.
- Each session has an `asyncio.Lock` to prevent concurrent requests on the same session.
- Locks are stored in `request.app["session_locks"]`.
- Sessions are persisted across requests (managed by the `SessionManager` passed to the agent loop).

### Error Handling
- `_error_json(status, message, err_type)` -- formats OpenAI-compatible error JSON responses.
- Error types: `"invalid_request_error"` (status 400 for bad input), with appropriate status codes for timeouts and internal errors.
- `_response_text(value)` -- extracts text from agent responses (handles both string and structured response formats).

## Configuration (`config.json`)

The API section in the config file:
```json
{
  "api": {
    "host": "127.0.0.1",
    "port": 8900,
    "timeout": 120
  }
}
```

Default binding: `127.0.0.1:8900`. Bind to `0.0.0.0` for network access.

## CLI Command

The API is started via `nanobot serve` (defined in `nanobot/cli/commands.py`):
- Accepts `--config`, `--workspace`, `--host`, `--port`, `--timeout`, `--model` options.
- Creates a `MessageBus`, `SessionManager`, and `AgentLoop`.
- Calls `create_app()` and starts `web.run_app(api_app, host=host, port=port)`.
- Separate from `nanobot gateway` -- does not start channels, cron, or WebUI.

## Tests

| Test File | Covers |
|-----------|--------|
| `tests/test_openai_api.py` | API endpoint behavior, request parsing, error handling |
| `tests/utils/test_restart.py` | API server restart functionality |

## Key Files Reference

| File | Purpose |
|------|---------|
| `nanobot/api/server.py` | Core API implementation (routes, handlers, SSE helpers) |
| `nanobot/api/__init__.py` | Package init (empty) |
| `nanobot/cli/commands.py` | CLI `serve` command parsing and app bootstrap |
| `nanobot/config/schema.py` | API config model (host, port, timeout) |
| `nanobot/agent/loop.py` | AgentLoop used by the API to process requests |
| `docs/openai-api.md` | User-facing API documentation |
| `tests/api/` | API server tests |

## Related

- [[api]]
- [[nanobot]]
