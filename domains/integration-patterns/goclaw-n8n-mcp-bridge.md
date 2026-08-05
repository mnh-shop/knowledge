---
name: goclaw-n8n-mcp-bridge
type: integration-pattern
tag: [goclaw, n8n, mcp, integration-patterns, workflow-automation]
description: "MCP integration surfaces between GoClaw (Go agent gateway) and n8n workflow automation — MCP client, goclaw-bridge server, CRUD MCP server, webhooks, OpenAI-compatible API"
---

# Integration Pattern: GoClaw ↔ n8n — Real Integration Surfaces

> **Correction notice:** An earlier version of this document described GoClaw as a
> Python SDK (a Python `import` of a goclaw package with an `Agent` constructor), a
> dedicated MCP port environment variable, and a separate "mcp-bridge" container
> image. **None of these exist.** GoClaw is a Go application (v3.15.0-beta.181,
> `sources/goclaw/`) that is an **MCP client** and exposes **two MCP servers**
> plus HTTP/webhook/OpenAI-compatible surfaces. This page documents the actual,
> verifiable integration points.

## Overview

GoClaw is an enterprise AI agent gateway written in Go. It integrates with n8n as a workflow-automation platform through four real surfaces:

1. **MCP client** — GoClaw connects *to* external MCP servers (including one n8n may expose) via `tools.mcp_servers` config.
2. **MCP bridge server** — GoClaw exposes its own tools as the MCP server `goclaw-bridge` (streamable-http) at `/mcp/bridge`, which any MCP client holding the gateway token — n8n MCP client nodes included — can call.
3. **CRUD MCP server** — a second MCP server at `/api/mcp/` exposing GoClaw's resource-management surface (agents, sessions, skills, cron, config, …), gated by its own token `gateway.mcp_server_token`.
4. **HTTP surfaces n8n can target directly** — webhooks (`/v1/webhooks/llm`, `/v1/webhooks/message`) and an OpenAI-compatible API (`/v1/chat/completions`, `/v1/responses`, `/v1/tools/invoke`) consumable by n8n's OpenAI / HTTP Request nodes.

No separate bridge service, broker container, or Python package is involved — GoClaw *is* the bridge.

## 1. GoClaw as an MCP Client (GoClaw → n8n)

GoClaw's MCP integration lives in `internal/mcp/` (`manager.go`, `manager_connect.go`, `pool.go`). The `Manager` handles server lifecycle: connect, tool discovery, keepalive, reconnection with exponential backoff, connection pooling, and OAuth 2.0 with DCR + token refresh. `createClient` (`internal/mcp/manager_connect.go:313-326`) supports three transports:

| Transport | Construction |
|---|---|
| `stdio` | `mcpclient.NewStdioMCPClient(command, envSlice, args...)` |
| `sse` | `mcpclient.NewSSEMCPClient(url, opts...)` (optional headers) |
| `streamable-http` | `mcpclient.NewStreamableHttpClient(url, opts...)` (optional headers) |

External MCP servers are declared under **`tools.mcp_servers`** in the JSON5 config (`internal/config/config_channels.go:465`, `MCPServerConfig` at `config_channels.go:480-503`): `transport`, `command`/`args`/`env` (stdio), `url`/`headers` (sse/streamable-http), `enabled` (default true), `tool_prefix` (collision avoidance), `timeout_sec` (default 60). MCP tools are wrapped as GoClaw-native tools via `BridgeTool` and filtered per agent (`tool_filter.go`), with BM25 search for lazy discovery (`mcp_tool_search.go`).

To let a GoClaw agent call n8n workflow endpoints, register n8n's MCP server endpoint (if n8n exposes one) as a streamable-http or SSE server:

```json5
{
  tools: {
    mcp_servers: {
      n8n: {
        transport: "streamable-http",
        url: "http://n8n:5678/mcp",           // n8n-hosted MCP endpoint
        headers: { Authorization: "Bearer <n8n-mcp-token>" },
        tool_prefix: "n8n_",                   // avoid tool-name collisions
        timeout_sec: 60
      }
    }
  }
}
```

Config hot-reloads (fsnotify, ~300ms debounce), but MCP server connections are lifecycle-managed by the `Manager` — see `manager.go` for reconnection behavior after config changes.

## 2. GoClaw's Bridge MCP Server (`goclaw-bridge`) — n8n → GoClaw

GoClaw exposes its tool registry as an MCP server named **`goclaw-bridge`** (`mcpserver.NewMCPServer("goclaw-bridge", version, ...)` in `internal/mcp/bridge_server.go:135`), served over **streamable-http in stateless mode** (`NewStreamableHTTPServer(..., mcpserver.WithStateLess(true))`, `bridge_server.go:133-146`). Tools are read from the registry, filtered to `BridgeToolNames`, and every call is additionally checked against the calling agent's policy allowlist (`bridge_server.go:120-131`).

It is mounted on the gateway HTTP server at **`/mcp/bridge`** (`internal/gateway/server.go:248-258`) behind `tokenAuthMiddleware(s.cfg.Gateway.Token, ...)`:

- **Auth:** requires `Authorization: Bearer <GOCLAW_GATEWAY_TOKEN>` (constant-time comparison).
- **Fail-safe:** when no gateway token is configured, the bridge is **disabled** — the route returns `403 {"error":"mcp bridge disabled: set GOCLAW_GATEWAY_TOKEN to enable"}` (`server.go:254-258`) so an exposed port can never serve unauthenticated tool invocations.
- **Primary consumer today:** the Claude CLI subprocess (ACP provider) running on the same machine (`bridge_server.go:123`, "All MCP bridge traffic originates from the Claude CLI subprocess").

An n8n workflow with an **MCP client node** can call GoClaw tools the same way: point it at `http://<goclaw-host>:18790/mcp/bridge` with the gateway token as bearer, and any registered bridge-capable tool appears (per-caller filtering still applies per agent context).

## 3. CRUD MCP Server (`/api/mcp/`) — Admin/Automation Surface

Distinct from the tool bridge, the CRUD MCP server (`NewCRUDServer`, `internal/mcp/crud_server.go:107`) exposes GoClaw's **resource-management surface as MCP tools backed by the real stores** — the same stores the gateway's own WebSocket RPC uses. Tool families include agents, sessions, skills, cron, config, agent links, API keys, config permissions, Bitrix24 portals, run timelines, teams (+ tasks/workspace), channels (+ instances), hooks, heartbeat, pairing, **exec approval**, usage/quota, chat/chat-behavior, LLM completion, runtime logs, outbound send, and TTS voices (tool names use the `goclaw_*` prefix, e.g. `goclaw_agent_get`, `goclaw_chat_send`, `goclaw_llm_complete` — see `crud_server.go` package comment and `CRUDDeps`).

- **Gating:** its own bearer token `gateway.mcp_server_token` (env: `GOCLAW_MCP_SERVER_TOKEN`), independent from the gateway token so it can be rotated/disabled separately (`internal/config/config_channels.go:429`, `internal/config/config_secrets.go:181`).
- **Mounting:** at `/api/mcp/` behind `mcpServerTokenAuthMiddleware` (`internal/gateway/server.go:281-337`). When the token is unset the route is **not mounted at all** — no 403 handler, the endpoint simply does not exist.
- **Tenant scoping:** callers may pass an optional `X-GoClaw-Tenant-Id` header (UUID or slug) to scope a request to a tenant; absent/unresolvable → master tenant. No membership check — the token is the full-trust boundary.

n8n workflows (HTTP Request → MCP over streamable-http, or an MCP client node) can drive GoClaw administration/automation through this endpoint with the dedicated token.

## 4. Direct HTTP Surfaces for n8n

### Webhooks — trigger agents from n8n (`docs/webhooks.md`)

GoClaw webhooks let external systems trigger agents or deliver messages:

| Kind | Endpoint | Purpose | Edition |
|---|---|---|---|
| `llm` | `POST /v1/webhooks/llm` | Invoke an agent with a user prompt (sync or async) | Standard + Lite |
| `message` | `POST /v1/webhooks/message` | Send a message to a user on a channel | Standard only |

Webhooks are tenant-scoped registry entries (`POST /v1/webhooks` admin CRUD). Two auth modes:

- **Bearer:** `Authorization: Bearer wh_...` (secret returned once at creation; `secret_prefix` like `wh_ABCD`).
- **HMAC:** header `X-GoClaw-Signature: t=<unix_seconds>,v1=<hmac_hex>` (`internal/http/webhooks_auth.go:238`, `docs/webhooks.md:171-198`). Signature = `HMAC_SHA256(key=hex.Decode(hmac_signing_key), payload="{ts}.{body}")` where `hmac_signing_key = hex(SHA-256(secret))`. Replay protection: the gateway records `sha256(tenant_id + "|" + signature_hex)` in a nonce cache with 320s TTL and rejects replays with `401` + `security.webhook.hmac_replay` (`docs/webhooks.md:196-198`). `require_hmac=true` on the webhook row disables bearer auth.

An n8n **Webhook node** pattern: n8n workflow → `POST /v1/webhooks/llm` (Bearer `wh_...` or signed `X-GoClaw-Signature`) → GoClaw agent runs → response streamed/returned to n8n.

### OpenAI-compatible API — n8n's OpenAI node can target GoClaw

| Endpoint | Purpose | Source |
|---|---|---|
| `POST /v1/chat/completions` | OpenAI-compatible chat completions | `internal/http/chat_completions.go:20` |
| `POST /v1/responses` | OpenResponses protocol | `internal/http/responses.go:19` |
| `POST /v1/tools/invoke` | Direct tool invocation | `internal/http/tools_invoke.go:14` |

These accept the gateway token or an API key as `Authorization: Bearer`, so n8n's **OpenAI node** (custom base URL + model) or **HTTP Request node** can drive GoClaw agents and even invoke tools directly without any MCP setup. Gateway rate limiting (`gateway.rate_limit_rpm`) applies to `/v1/chat/completions` as well (`docs/09-security.md:272`).

## 5. Which Surface to Use

| Need | Use |
|---|---|
| n8n triggers a GoClaw agent with a prompt | `POST /v1/webhooks/llm` (Bearer or HMAC) |
| n8n sends a message out through a GoClaw channel | `POST /v1/webhooks/message` |
| n8n workflow calls GoClaw as an LLM (OpenAI node) | `/v1/chat/completions` or `/v1/responses` |
| n8n invokes a single GoClaw tool | `/v1/tools/invoke` |
| GoClaw agent calls tools exposed by n8n's MCP server | `tools.mcp_servers` (MCP client) |
| n8n calls GoClaw's tools as an MCP client | `/mcp/bridge` (bearer = gateway token) |
| n8n automates GoClaw administration (agents/sessions/skills/cron/config) | `/api/mcp/` (bearer = `gateway.mcp_server_token`) |

## Security Notes

- Every inbound surface is authenticated: gateway token (constant-time) for `/mcp/bridge` and the OpenAI-compatible API, `wh_` bearer or HMAC `X-GoClaw-Signature` (with 320s replay protection) for webhooks, `mcp_server_token` for `/api/mcp/`.
- SSRF-safe HTTP clients are required for outbound calls (`internal/security/ssrf.go`); MCP server configs are validated by `internal/mcp.ValidateServerConfig()` with stdio restricted to bare allowlisted runtime names (`docs/09-security.md:80`).
- `message`-kind webhooks and several CRUD MCP tool families require the Standard edition; the `llm` webhook and the bridge server work in Lite too.

## Related Documentation

- [[goclaw]] — GoClaw platform wiki
- [[goclaw-architecture]] — gateway architecture, ports, config
- [[goclaw-security-and-credentials]] — injection guard, SSRF, exec approval, MCP server token gating
- [[n8n]] — n8n workflow automation platform
- [[mcp]] — Model Context Protocol ecosystem
- [[integration-patterns]] — integration patterns index

## Verification

- Corrected hallucinated content: no Python SDK API surface, no dedicated MCP port environment variable, no "mcp-bridge" container image — all removed and replaced with the real surfaces cited above.
- All facts cited against `sources/goclaw/` source files and `docs/` references (see inline citations).
- **Status:** REWRITTEN — reflects the real GoClaw v3.15.0-beta.181 integration surfaces.
