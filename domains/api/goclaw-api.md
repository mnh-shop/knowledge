---
name: goclaw-api
tags: [goclaw, api, rest, websocket]
description: "GoClaw API — REST API and WebSocket RPC protocol"
source: sources/goclaw/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# GoClaw — API Reference

**Source:** `sources/goclaw/` · [docs.goclaw.sh/reference/rest-api](https://docs.goclaw.sh/reference/rest-api.md) · [docs.goclaw.sh/reference/websocket-protocol](https://docs.goclaw.sh/reference/websocket-protocol.md)

## Overview

GoClaw exposes both a **REST API** (at `/v1/*`) and a **WebSocket RPC** (at `/ws`, protocol v3) on the same port (default 18790). Interactive docs at `/docs` (Swagger UI) and raw spec at `/v1/openapi.json`.

## Authentication

```http
Authorization: Bearer YOUR_GATEWAY_TOKEN
X-GoClaw-User-Id: user123    # Per-user session scoping (optional for API)
```

The gateway token (`GOCLAW_GATEWAY_TOKEN`) is validated with timing-safe comparison (`crypto/subtle.ConstantTimeCompare`). Token scoping supports three tiers: **viewer** (read-only), **operator** (+ chat/sessions/cron), **admin** (+ config/agents/channels).

## REST API — Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check (`{"status":"ok"}`) |
| `POST /v1/chat/completions` | OpenAI-compatible chat API (`model: "goclaw:<agent-key>"`) |
| `GET /v1/agents` | List agents (tenant-scoped) |
| `POST /v1/agents` | Create agent (with optional LLM summoning) |
| `GET /v1/providers` | List LLM providers |
| `POST /v1/providers` | Add LLM provider |
| `GET /v1/skills` | List skills |
| `POST /v1/skills/upload` | Upload skill (.zip, max 20 MB) |
| `GET /v1/traces` | List run traces (filterable by agent, user, status) |
| `GET /v1/mcp/servers` | List MCP server configurations |
| `POST /v1/mcp/servers` | Register MCP server |
| `GET /v1/tools/builtin` | List built-in tools |
| `POST /v1/tools/invoke` | Direct tool invocation (with `dryRun` support) |
| `GET /v1/memory` | Query episodic memory |
| `GET /v1/vault` | Knowledge Vault entries |
| `POST /v1/auth/login` | Login (API key, session token) |

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

The `model` field uses format `goclaw:<agent-key>` to route to a specific agent. Set `"stream": true` for SSE streaming chunks terminated by `data: [DONE]`.

## WebSocket Protocol (v3)

Connect at `ws://<host>:<port>/ws`. First frame must be `connect` for authentication:

```json
{"type":"req","id":"1","method":"connect","params":{"token":"TOKEN","user_id":"system","protocol":3}}
```

### 64+ RPC Methods

| Method group | Key methods |
|---|---|
| **Core** | `connect`, `health`, `status` |
| **Chat** | `chat.send`, `chat.history`, `chat.abort`, `chat.inject`, `chat.session.status` |
| **Agents** | `agents.list`, `agents.create`, `agents.update`, `agents.delete`, `agents.files.*` |
| **Sessions** | `sessions.list`, `sessions.preview`, `sessions.patch`, `sessions.reset`, `sessions.compact` |
| **Config** | `config.get`, `config.apply`, `config.patch`, `config.permissions.*` |
| **Cron** | `cron.list`, `cron.create`, `cron.update`, `cron.delete`, `cron.run` |
| **Skills** | `skills.list`, `skills.get`, `skills.update` |
| **Tools** | `tool.invoke` |
| **Teams** | `teams.*` (list, create, tasks, members, workspace) |
| **Hooks** | `hooks.list`, `hooks.create`, `hooks.update`, `hooks.delete`, `hooks.test` |
| **Pairing** | `device.pair.*`, `browser.pairing.status` |
| **Logs** | `logs.tail` (live log streaming) |

### Server-Push Events

Agent responses stream as `"event"` frames with types `chat.chunk` (streaming text), `chat.thinking` (reasoning output), `agent.*` (run lifecycle), `tool.*` (call/result), and `delegation.*` (subagent events).

## Related

- [[goclaw]] — GoClaw wiki entry
- [[openclaw-api]] — OpenClaw REST API (similar pattern)
- [[hermes-gateway-api]] — Hermes REST API
- [[goclaw-architecture]] — GoClaw architecture overview
