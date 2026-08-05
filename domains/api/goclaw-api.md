---
name: goclaw-api
tags: [goclaw, api, rest, websocket]
description: "GoClaw API — REST API and WebSocket RPC protocol"
source: sources/goclaw/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# GoClaw — API Reference

**Source:** `sources/goclaw/` · v3.15.0-beta.181 · [docs.goclaw.sh/reference/rest-api](https://docs.goclaw.sh/reference/rest-api.md) · [docs.goclaw.sh/reference/websocket-protocol](https://docs.goclaw.sh/reference/websocket-protocol.md)

## Overview

GoClaw exposes both a **REST API** (at `/v1/*`, ~375 routes across `internal/http/` handlers) and a **WebSocket RPC** (at `/ws`, protocol v3, **144 RPC methods** — 157 method-name constants in `pkg/protocol/methods.go`) on the same port (default 18790). Interactive docs at `/docs` (Swagger UI) and raw spec at `/v1/openapi.json` (`internal/http/openapi.go`).

## Authentication

```http
Authorization: Bearer YOUR_GATEWAY_TOKEN
X-GoClaw-User-Id: user123    # Per-user session scoping (optional for API)
X-GoClaw-Tenant-Id: <uuid-or-slug>   # Tenant scoping for owner/system keys
```

The gateway token (`GOCLAW_GATEWAY_TOKEN`) is validated with timing-safe comparison (`crypto/subtle.ConstantTimeCompare`). Auth resolution priority (`internal/http/auth.go:169-265`): **gateway token → API key → browser pairing → no-auth fallback (dev only)**. Token scoping supports three tiers: **viewer** (read-only), **operator** (+ chat/sessions/cron), **admin** (+ config/agents/channels); configured owner IDs get `owner` scope.

### API Keys

Format `goclaw_<32hex>` (`internal/crypto/apikey.go:10-22`), stored as SHA-256 hash, AES-256-GCM encrypted, **tenant-bound**, cached with 5-min TTL + pubsub invalidation. Six scopes (`internal/permissions/policy.go:41-46`): `operator.admin`, `operator.read`, `operator.write`, `operator.approvals`, `operator.pairing`, `operator.provision`. CRUD at `/v1/api-keys`.

### Webhook Auth

Webhook endpoints accept either `Authorization: Bearer wh_<secret>` (SHA-256 stored) or HMAC: headers `X-Webhook-Id` + `X-GoClaw-Signature: t=<unix_ts>,v1=<hmac_hex>` over payload `"{ts}.{body}"`, key = `hex(SHA-256(secret))`, 300s skew window, replay nonce cache (docs/webhooks.md).

## REST API — Endpoint Families

Only ~20 of ~375 routes are itemized below; groups are the documented catalog (all under `internal/http/`).

| Endpoint family | Description |
|-----------------|-------------|
| `GET /health` | Health check `{"status":"ok","protocol":N}` — the only health endpoint is `/health` (`server.go:202,604-609`) |
| `GET /` | Service info + endpoint list (`server.go:625`) |
| `POST /v1/chat/completions` | OpenAI-compatible chat API (`model: "goclaw:<agent-key>"`) |
| `POST /v1/responses` | OpenAI Responses-style API (`internal/http/responses.go`) |
| `POST /v1/tools/invoke` | Direct tool invocation (with `dryRun` support) |
| `GET /v1/openapi.json` · `GET /docs` | Raw OpenAPI spec + Swagger UI (`internal/http/openapi.go`) |
| `GET /v1/agents` · `POST /v1/agents` | List/create agents; `{id}` GET/PUT/DELETE, shares, regenerate/resummon, system-prompt-preview, export/import (`agents.go`, ~30 routes) |
| `GET /v1/providers` · `POST /v1/providers` | LLM provider CRUD |
| `GET /v1/skills` · `POST /v1/skills/upload` | Skills + upload (.zip, max 20 MB) |
| `GET /v1/traces` | Run traces (filterable by agent, user, status) |
| `GET /v1/mcp/servers` · `POST /v1/mcp/servers` | MCP server configurations |
| `GET /v1/tools/builtin` | Built-in tools (47: 46 seeded + `telegram_manager`) |
| `GET /v1/memory` | Query episodic memory |
| `GET /v1/vault` | Knowledge Vault entries |
| `POST /v1/auth/login` | Login (API key, session token) |
| `POST /v1/webhooks` + `{id}` GET/PATCH/DELETE/rotate/revoke/calls | Webhook admin CRUD (tenant-admin) |
| `POST /v1/webhooks/llm` | Invoke agent (sync 600s default / async w/ outbound callbacks) |
| `POST /v1/webhooks/message` | Send channel message (Standard only) |
| `GET/POST /v1/cli-credentials` (+ `presets`, `{id}` GET/PUT/DELETE/test) | Credentialed CLI (gh/gcloud/aws/kubectl/terraform/gws) |
| `GET /v1/api-keys` · `POST /v1/api-keys` · `POST /v1/api-keys/{id}/revoke` | API key management |
| `GET /v1/usage/*` | `timeseries`, `breakdown`, `summary`, `events/*` usage analytics (`usage.go`) |
| `GET /v1/auth/chatgpt/{provider}/quota` · `/v1/auth/openai/quota` | OAuth pool quota (chatgpt_oauth/codex) |
| `POST /v1/system/backup` (+ `preflight`, `download/{token}`) | System backup |
| `GET /v1/files/{path...}` · `POST /v1/files/sign` | Workspace file serving (2-layer path isolation) |
| `GET /v1/logs/runtime/aggregate` | Runtime log aggregation |
| `GET /v1/activity` · `/v1/activity/aggregate` | Activity feed |
| `GET /v1/agents/{id}/episodic` (+ `/search`) | Episodic memory per agent |
| `POST /v1/branding/assets` | Branding asset upload |
| `POST /v1/agents/import` / `POST /v1/teams/import` | Agent/team import |
| `/api/mcp/` | **CRUD MCP server** — agent/cron/tool/exec-approval management as MCP tools; gated by `gateway.mcp_server_token`, optional `X-GoClaw-Tenant-Id` scoping (`internal/mcp/crud_server.go`, `server.go:337`) |

### OpenAI-Compatible Chat Completions

```bash
curl -X POST http://localhost:18790/v1/chat/completions \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "goclaw:my-agent-key",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'
```

The `model` field uses format `goclaw:<agent-key>` (or `agent:<agent-key>`) to route to a specific agent — resolved in `extractAgentID` (`internal/http/auth.go:59-73`), falling back to `X-GoClaw-Agent-Id` / `X-GoClaw-Agent` headers and finally `"default"`. The same key-format convention routes API-key auth: a bearer token that is a valid `goclaw_` API key resolves to its tenant-bound role. Set `"stream": true` for SSE streaming chunks terminated by `data: [DONE]`.

## WebSocket Protocol (v3)

Connect at `ws://<host>:<port>/ws`. First frame must be `connect` for authentication:

```json
{"type":"req","id":"1","method":"connect","params":{"token":"TOKEN","user_id":"system","protocol":3}}
```

### 144 RPC Methods

Defined as 157 method-name constants in `pkg/protocol/methods.go` (some constants are aliases/unregistered); dispatched by `MethodRouter` (`internal/gateway/router.go`).

| Method group | Key methods |
|---|---|
| **Core** | `connect`, `health`, `status` |
| **Chat** | `chat.send`, `chat.history`, `chat.abort`, `chat.inject`, `chat.session.status` |
| **Agents** | `agents.list`, `agents.create`, `agents.update`, `agents.delete`, `agents.files.*`, `agents.links.*` |
| **Sessions** | `sessions.list`, `sessions.preview`, `sessions.patch`, `sessions.reset`, `sessions.compact` |
| **Config** | `config.get`, `config.apply`, `config.patch`, `config.schema`, `config.defaults`, `config.permissions.*`, `chat_behavior.preview` |
| **Cron** | `cron.list`, `cron.create`, `cron.update`, `cron.delete`, `cron.toggle`, `cron.status`, `cron.run`, `cron.runs` |
| **Skills** | `skills.list`, `skills.get`, `skills.update` |
| **Tools** | `tool.invoke`, `send`, `llm.complete` |
| **Teams** | `teams.*` ×22 (list, create, tasks.*, members.*, workspace.*, events.list) |
| **Tenants** | `tenants.*` ×8 (list, get, create, update, users.*, mine) |
| **Workstations** | `workstations.*` ×14 (CRUD, testConnection, linkAgent/unlinkAgent, permissions.*, activity.list) |
| **Hooks** | `hooks.*` ×7 (list, create, update, delete, toggle, test, history) |
| **API keys** | `api_keys.*` ×3 (list, create, revoke) |
| **Bitrix24** | `bitrix.portals.*` ×4 (list, create, get_install_url, delete) |
| **Usage / Quota** | `usage.get`, `usage.summary`, `quota.usage` |
| **TTS** | `tts.status`, `tts.enable`, `tts.disable`, `tts.convert`, `tts.setProvider`, `tts.providers` |
| **Run timeline** | `run.timeline.get` |
| **Exec approval** | `exec.approval.list`, `exec.approval.approve`, `exec.approval.deny` |
| **Pairing** | `device.pair.*` (request/approve/deny/list/revoke), `browser.pairing.status` |
| **Heartbeat** | `heartbeat.*` ×8 (get, set, toggle, test, logs, checklist.get/set, targets) |
| **Channels** | `channels.list`, `channels.status`, `channels.toggle`, `channels.instances.*` ×5 |
| **Browser** | `browser.act`, `browser.snapshot`, `browser.screenshot` |
| **Voices / Logs** | `voices.list`, `voices.refresh`, `logs.tail` |
| **Zalo / WhatsApp** | `zalo.personal.qr.start`, `zalo.personal.contacts`, `whatsapp.qr.start` |

### Channel Adapters

RPC/channel surface covers 10 channel adapter types (`internal/channels/channel.go:76-85`): `bitrix24`, `discord`, `facebook`, `feishu` (Larksuite = international domain), `pancake`, `slack`, `telegram`, `whatsapp`, `zalo_oa`, `zalo_personal` — plus raw WebSocket and browser pairing.

### Server-Push Events

Agent responses stream as `"event"` frames with types `chat.chunk` (streaming text), `chat.thinking` (reasoning output), `agent.*` (run lifecycle), `tool.*` (call/result), and `delegation.*` (subagent events).

## Related

- [[goclaw]] — GoClaw wiki entry
- [[goclaw-architecture]] — GoClaw architecture overview
- [[openclaw-api]] — OpenClaw REST API (similar pattern)
- [[hermes-gateway-api]] — Hermes REST API
