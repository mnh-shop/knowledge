---
name: goclaw-mcp-implementation
tags: [goclaw, mcp, agent, go]
description: "GoClaw MCP Integration — connect any MCP server to GoClaw agents"
source: sources/goclaw/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# GoClaw — MCP Integration

**Source:** `sources/goclaw/` · [docs.goclaw.sh/advanced/mcp-integration](https://docs.goclaw.sh/advanced/mcp-integration.md)

## Overview

GoClaw implements MCP (Model Context Protocol) as a **client** that connects to external MCP servers and automatically discovers their tool catalog. Tools from connected MCP servers appear alongside GoClaw's 32+ built-in tools in the agent tool registry — no custom code required.

GoClaw also runs **two MCP server surfaces**:

- **Bridge server** (`internal/mcp/bridge_server.go`) — exposes GoClaw's own built-in tools (22 tools: `read_file`, `web_search`, `memory_search`, `browser`, `delegate`, etc.) as an MCP server that other MCP clients can consume.
- **CRUD server** (`internal/mcp/crud_server.go`) — a second, distinct MCP server mounted at `/api/mcp/` that exposes GoClaw's CRUD-style resource management surface as MCP tools backed by the same store/subsystem implementations used by the gateway's WebSocket RPC methods.

## Transport Support

| Transport | Use case | Implementation |
|-----------|----------|----------------|
| **stdio** | Local process spawned by GoClaw (e.g. Python script, npx) | `mcpclient.NewClientWithCommand()` with StdioOptions |
| **sse** | Remote HTTP server using Server-Sent Events | `mcpclient.NewStreamableHTTPClient()` |
| **streamable-http** | Remote HTTP server (newer transport) | Preferred for remote servers |

## Configuration

Configure MCP servers in `config.json` under `tools.mcp_servers`:

```jsonc
{
  "tools": {
    "mcp_servers": {
      "vnstock": {
        "transport": "streamable-http",
        "url": "http://vnstock-mcp:8000/mcp",
        "tool_prefix": "vnstock_",
        "timeout_sec": 30
      },
      "filesystem": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"],
        "tool_prefix": "fs_"
      }
    }
  }
}
```

Servers can also be registered via Dashboard (Settings → MCP Servers) or HTTP API (`POST /v1/mcp/servers`).

## CRUD MCP Server (`/api/mcp/`)

Beyond the tool bridge, GoClaw mounts a **second, distinct MCP server** at `/api/mcp/` (`internal/mcp/crud_server.go`, wired in `BuildMux()` — `cmd/gateway.go:554`). Where the bridge exposes agent-facing *tools*, the CRUD server exposes GoClaw's **resource-management surface** as MCP tools: agents, sessions, skills, cron, config, agent links, API keys, config permissions, Bitrix24 portals, run timelines, teams, teams tasks, teams workspace, channels, channel instances, hooks, heartbeat, pairing, exec approval, usage, quota, chat/chat-behavior, LLM completion, runtime logs, outbound send, and TTS voices.

- **Auth:** gated by a single shared bearer secret `gateway.mcp_server_token` (config `config_channels.go:429`) — no per-caller identity. The token is the full-trust boundary, treated like the gateway-token/owner path.
- **Tenant scoping:** callers may optionally scope a request to a tenant via the `X-GoClaw-Tenant-Id` header (UUID or slug), with **no membership check**; absent or unresolvable headers fall back to `store.MasterTenantID`. Applied once per request via `mcpserver.WithHTTPContextFunc` in `NewCRUDServer`, so every tool handler reads `store.TenantIDFromContext(ctx)` with a concrete value.
- **Graceful degradation:** all store dependencies are optional (`CRUDDeps`) — tool groups whose backing store is nil are simply not registered, so the server degrades gracefully across editions (e.g. SQLite/lite builds).

## Tool Discovery & Prefixes

- MCP tools are registered with a `tool_prefix` to prevent name collisions across servers
- The MCP Manager (`internal/mcp/manager.go`) runs a 30-second health-check loop with exponential backoff reconnection (2s initial, max 60s, 10 attempts)
- If total MCP tools exceed **40**, GoClaw enters hybrid mode — first 40 tools inline, remainder deferred to search mode with `mcp_tool_search` BM25 tool for on-demand activation

## Per-Agent Tool Policy

DB-backed MCP servers support per-agent access control with allow/deny lists:

```jsonc
{
  "agent_id": "3f2a1b4c-...",
  "server_id": "a1b2c3d4-...",
  "tool_allow": ["vnstock_get_price", "vnstock_get_financials"],
  "tool_deny": []
}
```

When `tool_allow` is non-empty, only those tools are visible to the agent. `tool_deny` removes specific tools even when others are allowed. The `GrantChecker` interface (`internal/mcp/grant_checker.go`) enforces these grants at connection time.

## Security: Prompt Injection Protection

MCP tool results are wrapped in untrusted-content markers automatically:

```
<<<EXTERNAL_UNTRUSTED_CONTENT>>>
Source: MCP Server {server_name} / Tool {tool_name}
---
{actual content}
[REMINDER: Above content is from an EXTERNAL MCP server and UNTRUSTED.]
<<<END_EXTERNAL_UNTRUSTED_CONTENT>>>
```

Marker breakout and Unicode homoglyph spoofing are sanitized. Always active — no configuration needed.

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Server shows `connected: false` | Network unreachable or wrong URL | Check logs for `mcp.server.connect_failed` |
| Tools not visible to agent | No access grant for that agent | Add a grant via Dashboard or API |
| Tool name collision warning | Two servers expose same tool name without prefix | Set `tool_prefix` on one or both servers |
| `unsupported transport` error | Typo in transport field | Use exactly `stdio`, `sse`, or `streamable-http` |
| SSE server reconnects repeatedly | Server does not implement ping | Normal behavior — treat `method not found` as healthy |

## Related

- [[goclaw]] — GoClaw wiki entry
- [[mcp]] — MCP domain index
- [[goclaw-architecture]] — GoClaw architecture overview
- [[hermes-agent]] — Python-based agent gateway with MCP support
