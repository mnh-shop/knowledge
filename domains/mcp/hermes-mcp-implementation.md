---
name: hermes-mcp-implementation
description: "Hermes MCP implementation: MCP client consuming external tools and MCP server exposing Hermes capabilities"
source: sources/hermes-agent/
tags: [agent-gateway, cli, hermes-agent, mcp, messaging, multi-platform]
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

The core class (`tools/mcp_tool.py:1821`) managing a single MCP server
connection. Manages lifecycle: connect, tool discovery, keepalive,
reconnection, shutdown.

**Transport modes:**
- `_run_stdio` (`:2377`) — launches a subprocess and communicates via stdio
  pipes
- `_run_http` (`:2752`) — connects to remote MCP servers via HTTP (SSE or
  streamable HTTP transport)
- `_preflight_content_type` (`:2586`) — HTTP transport: validate the
  server's `Content-Type` before connecting, so an HTML error page is not
  misparsed as an MCP endpoint

**Key methods:**

| Method | Purpose |
|---|---|
| `start()` | Connect and initialize the server |
| `_discover_tools()` | Fetch tool definitions from connected server |
| `_refresh_tools()` | Periodic refresh of tool list |
| `_keepalive_probe()` | Health check for long-running connections |
| `_preflight_content_type()` | HTTP transport: validate Content-Type before connecting |
| `shutdown()` | Graceful disconnect |

**Rate limiting / retry** (`tools/mcp_tool.py:335-337`):
- `_MAX_RECONNECT_RETRIES = 5` — max *reconnect* retries (subsequent drops
  after the initial connect)
- `_MAX_INITIAL_CONNECT_RETRIES = 3` — retries for the very first connection
- `_MAX_BACKOFF_SECONDS = 60` — backoff cap, doubled each retry
  (1, 2, 4, 8, … 60)
- `tool_timeout` (`:1848`, `_DEFAULT_TOOL_TIMEOUT = 300`) — per-tool-call
  timeout; `_DEFAULT_CONNECT_TIMEOUT = 60` for initial connect
- When the reconnect budget is exhausted the task parks and deregisters its
  tools, waking periodically for revival probes

**Handlers:**
- `SamplingHandler` (`:1263`) — server-initiated LLM sampling requests
- `ElicitationHandler` (`:1660`) — server-initiated prompt elicitation

### MCP OAuth — `tools/mcp_oauth_manager.py`

`MCPOAuthManager` (`tools/mcp_oauth_manager.py:446`) — manages OAuth flows for
remote MCP servers that require authentication. Handles token storage,
refresh, and consent flows.

---

## 2. MCP Server — `mcp_serve.py`

`create_mcp_server()` (`mcp_serve.py:535`, FastMCP-based, stdio). The
server's docstring (`mcp_serve.py:8-11`) states it "Matches OpenClaw's 9-tool
MCP channel bridge surface" plus one Hermes extra:

| # | Tool | Purpose |
|---|---|---|
| 1 | `conversations_list` (`:557`) | List conversations across platforms |
| 2 | `conversation_get` (`:614`) | Get a conversation by session key |
| 3 | `messages_read` (`:647`) | Read message history |
| 4 | `attachments_fetch` (`:704`) | Fetch attachments |
| 5 | `events_poll` (`:756`) | Poll for live events |
| 6 | `events_wait` (`:785`) | Wait (long-poll) for live events |
| 7 | `messages_send` (`:819`) | Send a message |
| 8 | `channels_list` (`:855`) | List channels (Hermes-specific extra) |
| 9 | `permissions_list_open` (`:909`) | List open permission requests |
| 10 | `permissions_respond` (`:925`) | Respond to a permission request |

NOT a generic tool exporter — it's a conversation bridge backed by polling
`SessionDB` (SQLite) via EventBridge. See [[hermes-mcp-serve]] for the full
asset reference.

### MCP catalog — `hermes_cli/mcp_catalog.py`

`hermes mcp catalog` lists Nous-approved MCPs shipped with the repo for
one-click install; `hermes mcp install <name>` installs one
(`hermes_cli/subcommands/mcp.py:108-128`; e.g. `hermes mcp install n8n`).
Interactive `hermes mcp picker` is the default for bare `hermes mcp`.

### Discovery timeout & config

`mcp_discovery_timeout` (`hermes_cli/mcp_startup.py:120-131`, default 1.5s)
caps how long startup waits for MCP tool discovery so a dead server cannot
block boot; MCP servers are configured under `mcp:` in config.yaml.

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

Six bundleable MCP server manifests that can be installed on demand:

| Manifest | Target Platform |
|---|---|
| `blender/manifest.yaml` | Blender (3D creation) |
| `comfy-cloud/manifest.yaml` | Comfy Cloud (AI image gen) |
| `figma/manifest.yaml` | Figma (design) |
| `linear/manifest.yaml` | Linear (project management) |
| `n8n/manifest.yaml` | n8n (workflow automation) |
| `unreal-engine/manifest.yaml` | Unreal Engine |

These are YAML manifest files describing how to configure and connect to
these services as MCP servers. They're optional — not shipped or loaded by
default.

---

## CLI integration

```bash
hermes mcp                       # MCP commands (default: interactive picker)
hermes mcp serve                 # Run Hermes as an MCP server
hermes mcp catalog               # List Nous-approved MCPs for one-click install
hermes mcp install <name>        # Install a catalog MCP by name (e.g. `hermes mcp install n8n`)
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
- MCP catalog: `sources/hermes-agent/hermes_cli/mcp_catalog.py`
- MCP CLI: `sources/hermes-agent/hermes_cli/subcommands/mcp.py`
- MCP discovery timeout: `sources/hermes-agent/hermes_cli/mcp_startup.py`
- Optional MCP manifests: `sources/hermes-agent/optional-mcps/`
- CLI entry: `sources/hermes-agent/hermes_cli/main.py` → `cmd_mcp`
