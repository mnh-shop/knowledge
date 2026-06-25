---
name: hermes-mcp-implementation
tags: [hermes, mcp, typescript, agent-gateway, messaging, multi-platform]
description: Hermes MCP implementation: MCP client consuming external tools and MCP server exposing Hermes capabilities
---

# Hermes MCP Implementation — Two Modes

Hermes implements MCP in two directions:

1. **MCP Client** (`tools/mcp_tool.py`) — Hermes *consumes* external MCP
   servers as tool providers. The agent can call tools exposed by any MCP
   server.
2. **MCP Server** (`mcp_serve.py`) — Hermes *serves* itself as an MCP
   server, but only as a **messaging bridge** (not a tool exporter). Other
   MCP clients can list conversations, read messages, and send messages
   across Hermes's connected platforms.

These two uses are independent and unrelated in the codebase.

---

## 1. MCP Client — `tools/mcp_tool.py`

### `MCPServerTask`

The core class managing a single MCP server connection. Manages lifecycle:
connect, tool discovery, keepalive, reconnection, shutdown.

**Transport modes:**
- `_run_stdio` — launches a subprocess and communicates via stdio pipes
- `_run_http` — connects to remote MCP servers via HTTP (SSE or
  streamable HTTP transport)

**Key methods:**

| Method | Purpose |
|---|---|
| `start()` | Connect and initialize the server |
| `_discover_tools()` | Fetch tool definitions from connected server |
| `_refresh_tools()` | Periodic refresh of tool list |
| `_keepalive_probe()` | Health check for long-running connections |
| `_preflight_content_type()` | HTTP transport: validate Content-Type before connecting |
| `shutdown()` | Graceful disconnect |

**Rate limiting / retry:**
- Max initial connect retries: 3
- Max reconnect retries: 2
- Max backoff seconds: exponential
- Default tool timeout: configurable

**Handlers:**
- `SamplingHandler` — server-initiated LLM sampling requests
- `ElicitationHandler` — server-initiated prompt elicitation

### MCP OAuth — `tools/mcp_oauth_manager.py`

`MCPOAuthManager` — manages OAuth flows for remote MCP servers that require
authentication. Handles token storage, refresh, and consent flows.

---

## 2. MCP Server — `mcp_serve.py`

See [[hermes-mcp-serve]] for the full asset reference. Key points:

- Uses `mcp.server.fastmcp.FastMCP`
- Exposes 10 tools (matching OpenClaw's 9-tool surface + 1 Hermes extra)
- NOT a generic tool exporter — it's a conversation bridge
- Backed by polling `SessionDB` (SQLite) via EventBridge

---

## 3. Optional MCP Servers (`optional-mcps/`)

Bundleable MCP server manifests that can be installed on demand:

| Manifest | Target Platform |
|---|---|
| `linear/manifest.yaml` | Linear (project management) |
| `n8n/manifest.yaml` | n8n (workflow automation) |
| `unreal-engine/manifest.yaml` | Unreal Engine |

These are YAML manifest files describing how to configure and connect to
these services as MCP servers. They're optional — not shipped or loaded by
default.

---

## CLI integration

```bash
hermes mcp             # MCP commands
hermes mcp serve       # Run Hermes as an MCP server
```

## Related

- [[hermes-mcp-serve]] -- MCP server asset
- [[hermes-agent]] -- Core agent runtime
- [[hermes-agent-architecture]] -- System architecture
- [[hermes-acp-implementation]] -- ACP implementation (related protocol)

## Links

- MCP server (serve side): `sources/hermes-agent/mcp_serve.py`
- MCP client (consume side): `sources/hermes-agent/tools/mcp_tool.py`
- MCP OAuth: `sources/hermes-agent/tools/mcp_oauth_manager.py`
- Optional MCP manifests: `sources/hermes-agent/optional-mcps/`
- CLI entry: `sources/hermes-agent/hermes_cli/main.py` → `cmd_mcp`
