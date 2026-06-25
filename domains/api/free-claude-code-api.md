---
name: free-claude-code-api
description: "REST API endpoints and usage for free-claude-code"
source: sources/free-claude-code/
tags: [cli, documentation, messaging, rest-api]
---
# free-claude-code API

## Overview

The "free-claude-code" project implements an Anthropic Messages API-compatible proxy gateway and an OpenAI Responses API adapter. It runs as a FastAPI application behind uvicorn.

## Base URL

Default: `http://localhost:8082/v1`

## Authentication

Authentication uses an Anthropic-style API key. Set via the `ANTHROPIC_AUTH_TOKEN` environment variable. Auth is **disabled** when this value is empty.

**Checking mechanism** (file: `api/dependencies.py`, function `require_api_key`):
1. Check `x-api-key` header
2. Check `Authorization: Bearer <token>` header (strips "Bearer " prefix)
3. Check `anthropic-auth-token` header
4. Token comparison uses `secrets.compare_digest()` to prevent timing attacks (CWE-208)
5. Supports colons in tokens for model name appending (strips after first colon)
6. Returns 401 with "Missing API key" or "Invalid API key" on failure

## Core Endpoints

### POST /v1/messages

Anthropic Messages API-compatible chat completion. **Always streaming** (SSE). `stream=true` is the default.

**Route:** `api/routes.py`

```python
@router.post("/v1/messages")
async def create_message(
    request_data: MessagesRequest,
    pipeline: ApiRequestPipeline = Depends(get_request_pipeline),
    _auth=Depends(require_api_key),
):
    return pipeline.create_message(request_data)
```

**Response:** Server-Sent Events (SSE) stream with `text/event-stream` content type.

**Request Schema** (`api/models/anthropic.py` -- `MessagesRequest`):

| Field | Type | Required | Description |
|---|---|---|---|
| `model` | string | Yes | Model ID (see model listing below) |
| `messages` | Message[] | Yes | Array of user/assistant messages |
| `max_tokens` | int | No | Maximum tokens to generate |
| `system` | string \| SystemContent[] | No | System prompt |
| `stop_sequences` | string[] | No | Custom stop sequences |
| `stream` | bool | No | Defaults to true |
| `temperature` | float | No | Sampling temperature |
| `top_p` | float | No | Nucleus sampling |
| `top_k` | int | No | Top-k sampling |
| `metadata` | dict | No | Request metadata |
| `tools` | Tool[] | No | Tool definitions |
| `tool_choice` | dict | No | Tool choice configuration |
| `thinking` | ThinkingConfig | No | Thinking/output configuration |
| `context_management` | dict | No | Claude Code context management hints |
| `output_config` | dict | No | Claude Code output configuration |
| `mcp_servers` | dict[] | No | MCP server config (passthrough) |
| `extra_body` | dict | No | Extra body fields for native providers |

**Message Content Blocks:**

- `text` -- text content
- `image` -- image with source
- `document` -- document block (PDF via Files API)
- `tool_use` -- tool invocation
- `tool_result` -- tool execution result
- `thinking` -- thinking block (with signature)
- `redacted_thinking` -- redacted thinking block
- `server_tool_use` -- server-side tool invocation (web_search / web_fetch)
- `web_search_tool_result` -- web search result
- `web_fetch_tool_result` -- web fetch result

### POST /v1/responses

OpenAI Responses API-compatible chat completion (streaming only via SSE).

**Route:** `api/routes.py`

```python
@router.post("/v1/responses")
async def create_response(
    request_data: OpenAIResponsesRequest,
    pipeline: ApiRequestPipeline = Depends(get_request_pipeline),
    _auth=Depends(require_api_key),
):
    return await pipeline.create_response(request_data)
```

**Request Schema** (`api/models/openai_responses.py` -- `OpenAIResponsesRequest`):

| Field | Type | Required | Description |
|---|---|---|---|
| `model` | string | Yes | Model ID |
| `input` | any | No | Input content (multi-modal or text) |
| `instructions` | string | No | System instructions |
| `tools` | dict[] | No | Tool definitions |
| `tool_choice` | any | No | Tool choice configuration |
| `parallel_tool_calls` | bool | No | Allow parallel tool calls |
| `stream` | bool | No | Defaults to true (non-streaming returns 400) |
| `temperature` | float | No | Sampling temperature |
| `top_p` | float | No | Nucleus sampling |
| `max_output_tokens` | int | No | Maximum output tokens |
| `metadata` | dict | No | Request metadata |
| `reasoning` | dict | No | Reasoning configuration (maps to thinking) |
| `previous_response_id` | string | No | For multi-turn continuation |
| `store` | bool | No | Store the response |

The adapter converts OpenAI Responses payloads to Anthropic Messages format internally, sends through the provider, and converts the SSE output back to OpenAI Responses format.

### POST /v1/messages/count_tokens

Counts input tokens without generating a response.

```python
@router.post("/v1/messages/count_tokens")
async def count_tokens(
    request_data: TokenCountRequest,
    pipeline: ApiRequestPipeline = Depends(get_request_pipeline),
    _auth=Depends(require_api_key),
):
    return pipeline.count_tokens(request_data)
```

**Response:**
```json
{"input_tokens": 42}
```

### GET /v1/models

Lists advertised model IDs for Claude-compatible clients (including Codex).

```python
@router.get("/v1/models", response_model=ModelsListResponse)
async def list_models(request, settings, _auth):
    return build_models_list_response(settings, provider_registry)
```

**Response Schema** (`api/models/responses.py` -- `ModelsListResponse`):
```json
{
  "object": "list",
  "data": [
    {
      "id": "anthropic/nvidia_nim/nvidia/nemotron-3-super-120b-a12b",
      "object": "model",
      "created": 0,
      "owned_by": "free-claude-code",
      "created_at": "2025-05-14T00:00:00Z",
      "display_name": "Claude Opus 4",
      "type": "model"
    }
  ],
  "first_id": "...",
  "has_more": false,
  "last_id": "..."
}
```

Model IDs are generated using the gateway model ID scheme (file: `api/gateway_model_ids.py`):

- Standard: `anthropic/{provider_id}/{model_name}` (e.g., `anthropic/deepseek/deepseek-chat`)
- No-thinking variant: `claude-3-freecc-no-thinking/{provider_id}/{model_name}`

The model list includes:
1. **Provider-configured models** from `MODEL`, `MODEL_OPUS`, `MODEL_SONNET`, `MODEL_HAIKU` settings
2. **Discovered provider models** from cached model listings
3. **Built-in Claude model IDs** (standard compatibility IDs)

### GET /health

Health check endpoint.

```python
@router.get("/health")
async def health():
    return {"status": "healthy"}
```

### GET /

Root endpoint with current configuration.

**Response:**
```json
{
  "status": "ok",
  "provider": "nvidia_nim",
  "model": "nvidia_nim/nvidia/nemotron-3-super-120b-a12b"
}
```

### POST /stop

Emergency stop for all CLI sessions and pending messaging tasks.

```python
@router.post("/stop")
async def stop_cli(request, _auth):
    workflow = getattr(request.app.state, "messaging_workflow", None)
    count = await workflow.stop_all_tasks()
    return {"status": "stopped", "cancelled_count": count}
```

## Admin Endpoints

All admin endpoints are **local-only** (loopback IP required). They share the `require_loopback_admin` dependency that checks the client host and origin headers.

### GET /admin

Serves the admin UI HTML page.

### GET /admin/assets/{filename}

Serves admin static assets (`admin.css`, `admin.js`).

### GET /admin/api/config

Returns the current configuration as a structured config form response.

### POST /admin/api/config/validate

Validates config field updates without applying.

**Request:** `{"values": {"PROVIDER_API_KEY": "new-key", ...}}`

### POST /admin/api/config/apply

Applies config updates and optionally restarts the server.

**Response:**
```json
{
  "applied": true,
  "errors": {},
  "pending_fields": ["HOST"],
  "restart": {"required": true, "automatic": true, "admin_url": "...", "fields": ["HOST"]}
}
```

### GET /admin/api/status

Returns server runtime status.

**Response:**
```json
{
  "status": "running",
  "host": "0.0.0.0",
  "port": 8082,
  "model": "nvidia_nim/...",
  "provider": "nvidia_nim",
  "pending_fields": [],
  "provider_status": {...},
  "cached_models": {"nvidia_nim": ["model1", "model2"]}
}
```

### GET /admin/api/providers/local-status

Checks connectivity to local providers (LM Studio, llama.cpp, Ollama).

### POST /admin/api/providers/{provider_id}/test

Tests a provider connection and lists available models.

**Response (success):**
```json
{"provider_id": "ollama", "ok": true, "models": ["llama3.2:1b", ...]}
```

### POST /admin/api/models/refresh

Refreshes the cached model list from all active providers.

## Provider Architecture

The API routes through a pipeline architecture (`api/request_pipeline.py` -- `ApiRequestPipeline`):

1. **Route resolution** -- `ModelRouter` maps Claude model names to provider-specific models
2. **Message routing policies** -- safety classifier thinking policy
3. **Interception** -- web server tools, local optimizations
4. **Provider stream** -- stream through the resolved provider

### Supported Providers (from `config/provider_catalog.py`)

**Native Anthropic Messages transport:**
- `open_router`, `deepseek`, `wafer`, `kimi`, `fireworks`, `zai`, `lmstudio`, `llamacpp`, `ollama`

**OpenAI Chat Completions transport:**
- `nvidia_nim`, `gemini`, `mistral`, `mistral_codestral`, `opencode`, `opencode_go`, `cerebras`, `groq`

## Configuration

Key environment variables (from `.env.example` and `config/settings.py`):

| Variable | Default | Description |
|---|---|---|
| `MODEL` | nvidia_nim/... | Primary model reference |
| `ANTHROPIC_AUTH_TOKEN` | (empty) | Server API key |
| `HOST` | 0.0.0.0 | Server bind host |
| `PORT` | 8082 | Server bind port |
| `PROVIDER_RATE_LIMIT` | 1 | Requests per window |
| `PROVIDER_RATE_WINDOW` | 3 | Rate limit window (seconds) |
| `ENABLE_WEB_SERVER_TOOLS` | true | Enable local web_search/web_fetch |
| `HTTP_READ_TIMEOUT` | 300 | Provider request read timeout |
| `MESSAGING_PLATFORM` | discord | "telegram", "discord", or "none" |
| `DEBUG_SUBAGENT_STACK` | false | Verbose subagent stack logging |

## Key Files

| File | Role |
|---|---|
| `api/routes.py` | Core API endpoint definitions |
| `api/admin_routes.py` | Admin UI and API endpoints |
| `api/app.py` | FastAPI application factory and error handlers |
| `api/request_pipeline.py` | Request routing, interception, and provider execution |
| `api/models/anthropic.py` | MessagesRequest, Tool, ContentBlock models |
| `api/models/openai_responses.py` | OpenAI Responses API request model |
| `api/models/responses.py` | Response models (TokenCount, Model, Messages) |
| `api/dependencies.py` | Auth, settings, provider resolution |
| `api/model_router.py` | Model name resolution and routing |
| `api/model_catalog.py` | Model listing construction |
| `api/gateway_model_ids.py` | Gateway model ID encoding/decoding |
| `api/web_tools/` | Web search/fetch tool streaming |
| `config/settings.py` | Centralized Settings model |
| `config/provider_catalog.py` | Provider metadata and defaults |
| `config/paths.py` | Filesystem paths for config and logs |
