---
name: nanobot-mcp
description: "Nanobot MCP server — tool registration, resource model, agent capability exposure"
tags: [ai-llm, cli, documentation, mcp]
---
# Nanobot MCP Implementation

Source repository: `nanobot` (https://github.com/HKUDS/nanobot)
Primary file: `nanobot/agent/tools/mcp.py`
Supporting files: `nanobot/webui/mcp_presets_api.py`, `nanobot/webui/mcp_presets_runtime.py`, `nanobot/cli/gateway.py`

## Architecture Overview

Nanobot treats MCP servers as an external tool provider. The agent loop calls tools through a unified `ToolRegistry`, and MCP tools are wrapped into the same interface as built-in tools. There is no standalone MCP client or server; MCP is consumed as a **tool backend**.

## Core Classes (`nanobot/agent/tools/mcp.py`)

### `_MCPWrapperBase(Tool)`
Abstract base class for all MCP wrappers. Provides:
- `_set_mcp_connection(session, server_name)` -- binds an MCP `ClientSession` to the wrapper.
- `set_reconnect_handler(reconnect)` -- registers a `_ReconnectCallback` for transient failure recovery; on transient error, the wrapper attempts session refresh by calling back into the connection manager to obtain a fresh `ClientSession` and retry the call.
- `_plugin_discoverable = False` -- MCP wrappers are never exported as plugin entry points.

### `MCPToolWrapper(_MCPWrapperBase)`
Wraps a single MCP tool definition:
- Constructor accepts `(session, server_name, tool_def, tool_timeout=30)`.
- `name` read from `tool_def.name`, `description` from `tool_def.description`, `inputSchema` is translated into nanobot's parameter schema via `_normalize_schema_for_openai()`.
- `execute(**kwargs)` calls `session.call_tool(tool_def.name, arguments=kwargs)` with `asyncio.wait_for(timeout=tool_timeout)`.
- On transient errors (`_is_transient`), retries once using the same session with a 1-second backoff.
- On timeout, surfaces a `CancelledError` from the SDK's anyio cancel scopes.
- Implements `session.list_tools()` under the hood during server connection to discover tool definitions.

### `MCPResourceWrapper(_MCPWrapperBase)`
Wraps MCP resources:
- Constructor accepts `(session, server_name, resource_def, resource_timeout=30)`.
- `name` prefixed with `mcp_{server_name}_resource_{resource_name}`.
- `execute()` calls `session.read_resource(resource_def.uri)`.
- `read_only = True` -- resources are not writable.

### `MCPPromptWrapper(_MCPWrapperBase)`
Wraps MCP prompts:
- Constructor accepts `(session, server_name, prompt_def, prompt_timeout=30)`.
- `execute()` calls `session.get_prompt(prompt_def.name, arguments=...)`.
- Only registered when `allow_all_tools` is true (no tool allowlist restriction active), because prompts have no per-name filtering equivalent.

## Server Connection (`connect_single_server`)

```python
async def connect_single_server(name: str, cfg) -> tuple[str, AsyncExitStack | None]
```

Lifecycle:
1. Creates an `AsyncExitStack` for managing server resources.
2. Determines transport type from `cfg.type`:
   - `"stdio"` -- creates `StdioServerParameters` from `cfg.command` and `cfg.args`. On Windows, wraps shell launchers (npx, npm, etc.) for reliability.
   - `"streamableHttp"` -- creates `httpx.AsyncClient` with configurable headers and base URL. Uses `streamable_http_client()` for streaming transport.
   - `"sse"` -- creates `httpx.AsyncClient` with SSRF validation. Uses `sse_client()` for server-sent events transport.
   - `"oauth"` -- similar to streamable HTTP but with OAuth-based auth flows.
3. Wraps the read stream with `_filter_malformed_mcp_progress_notifications()` to strip malformed progress notifications.
4. Creates `ClientSession(read, write)` and enters it on the stack.
5. Calls `session.initialize()` to perform the MCP initialization handshake.
6. Discovers tools via `session.list_tools()` and creates `MCPToolWrapper` instances.
7. If no tool allowlist restriction is active, discovers resources via `session.list_resources()` and prompts via `session.list_prompts()`, wrapping each.
8. Returns the `(stack, success_message)` tuple.

## Tool Discovery and Registration

MCP tools are integrated into the `ToolRegistry` (`nanobot/agent/tools/registry.py`):

- `ToolRegistry.mcp_tools: list[dict[str, Any]]` -- reserved list for MCP tool schemas.
- `get_definitions()` returns built-in tools sorted first, then MCP tools appended with stable ordering for cache-friendly prompts.
- Tool names are sanitized: `mcp_{server_name}_{tool_name}` via `_sanitize_name()` which replaces non-alphanumeric characters with underscores and deduplicates.

## Config-Driven MCP (`MCPServerConfig`)

Configuration is defined in `nanobot/config/schema.py`:
- `tools.mcp_servers` -- a dict of server name to `MCPServerConfig`.
- Each `MCPServerConfig` has: `type` (transport), `command`, `args`, `env`, `url`, `headers`, `enabled_tools`, `tool_timeout`, etc.
- `enabled_tools` is a list of allowed tool names; `["*"]` means allow all.

## Hot Reload

- `reload_servers(state, registry)` compares current live connections against config, adds/removes/changes as needed. Returns a status dict.
- Runtime control via `RUNTIME_CONTROL_MCP_RELOAD` (`_runtime_control` message type) allows the agent to trigger a reload mid-session.
- `request_mcp_reload(bus, *, timeout=15.0)` publishes a runtime control message and waits for an ack.

## MCP Presets (WebUI)

The WebUI (`nanobot/webui/mcp_presets_runtime.py`) provides a preset system for popular MCP servers:
- `McpPreset` -- dataclass describing a known MCP server (display name, category, description, transport type, brand info, install support).
- `McpPresetField` -- describes a configurable field (env var, URL param, CLI arg, HTTP header) with secrets support.
- `MCP_PRESETS` -- tuple of built-in presets for services like filesystem, GitHub, Slack, etc.
- `mcp_presets_action(action, query)` -- WebUI API action for managing presets.
- `custom_mcp_action(action, query)` -- WebUI API action for adding custom MCP servers.
- `mcp_presets_test_action(query)` -- tests an MCP server connection.

## SDI Client

Nanobot includes an SDK-based MCP client in `nanobot/sdk/`:
- `nanobot/sdk/clients.py` -- provides `MCPClient` class that connects via stdio transport, calls `list_tools()` and `call_tool()`.
- `nanobot/sdk/runtime.py` -- runtime management for the SDK client integration.
- `nanobot/sdk/streaming.py` -- streaming support for MCP client calls.

## Key Files Reference

| File | Purpose |
|------|---------|
| `nanobot/agent/tools/mcp.py` | Core MCP integration: wrappers, connection, reload |
| `nanobot/agent/tools/registry.py` | ToolRegistry with MCP tool support |
| `nanobot/webui/mcp_presets_runtime.py` | MCP preset management for WebUI |
| `nanobot/webui/mcp_presets_api.py` | WebUI API endpoints for MCP presets |
| `nanobot/config/schema.py` | MCP server config schema |
| `nanobot/sdk/clients.py` | SDK-based MCP client |
| `nanobot/sdk/runtime.py` | SDK MCP runtime |
| `tests/agent/test_mcp_connection.py` | MCP connection tests |
| `tests/agent/test_mcp_transient_retry.py` | Transient error retry tests |
| `tests/tools/test_mcp_tool.py` | MCP tool execution tests |
| `tests/tools/test_mcp_probe.py` | MCP probe tests |
