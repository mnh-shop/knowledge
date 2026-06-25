---
name: hermes-mcp-implementation
description: "Hermes MCP implementation: MCP client consuming external tools and MCP server exposing Hermes capabilities"
source: sources/hermes-agent/
tags: [agent-gateway, cli, hermes, mcp, messaging, multi-platform]
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
- Max *reconnect* retries: 5 (subsequent connection drops after initial connect)
- Max backoff seconds: 60 (doubled each retry: 1, 2, 4, 8, ... 60 cap)
- Default tool timeout: configurable (`_DEFAULT_TOOL_TIMEOUT`)

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

## 3. Codex Runtime MCP Server — `agent/transports/hermes_tools_mcp_server.py`

When Hermes runs under a Codex app-server runtime, Codex owns the agent loop
and needs a tool surface. This module exposes a curated subset of Hermes tools
to the spawned Codex subprocess via stdio MCP.

**Exposed tools (25):**
- `web_search`, `web_extract` — Firecrawl web search/extraction
- `browser_navigate`, `browser_click`, `browser_type`, `browser_press`,
  `browser_snapshot`, `browser_scroll`, `browser_back`, `browser_get_images`,
  `browser_console`, `browser_vision` — Camofox/Browserbase automation
- `vision_analyze` — image inspection by vision model
- `image_generate` — image generation
- `skill_view`, `skills_list` — Hermes skill library
- `text_to_speech` — TTS
- `kanban_complete`, `kanban_block`, `kanban_comment`, `kanban_heartbeat`,
  `kanban_show`, `kanban_list`, `kanban_create`, `kanban_unblock`,
  `kanban_link` — Kanban worker handoff tools

**Deliberately not exposed** (covered by Codex's own built-ins): terminal,
shell, file read/write/patch, search_files, process, clarify. Also excluded:
delegate_task, memory, session_search, todo (require AIAgent loop context).

This server is distinct from `mcp_serve.py` — it's a *tool gateway* for the
Codex runtime, not a messaging bridge.

---

## 4. Optional MCP Servers (`optional-mcps/`)

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
- Codex runtime MCP server: `sources/hermes-agent/agent/transports/hermes_tools_mcp_server.py`
- MCP client (consume side): `sources/hermes-agent/tools/mcp_tool.py`
- MCP OAuth: `sources/hermes-agent/tools/mcp_oauth_manager.py`
- Optional MCP manifests: `sources/hermes-agent/optional-mcps/`
- CLI entry: `sources/hermes-agent/hermes_cli/main.py` → `cmd_mcp`
