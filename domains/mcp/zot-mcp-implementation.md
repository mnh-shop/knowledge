---
name: zot-mcp-implementation
description: "Zot extension system as MCP-adjacent tool surface — JSON-RPC subprocess protocol, tool registration, events, and panels"
tags: [mcp, zot]
source: sources/zot/
---

# Zot MCP Implementation

Zot does **not** implement the standard Model Context Protocol (MCP) — there is no stdio MCP server, no HTTP SSE transport, and no MCP-style resource/prompt definitions. However, the zot **extension system** provides an equivalent tool surface using a custom JSON-RPC protocol over subprocess stdin/stdout, serving the same function as an MCP server from the agent's perspective.

## Extension System as MCP-Adjacent Surface

| Capability | MCP Standard | Zot Extension Protocol |
|------------|-------------|----------------------|
| Tool Discovery | `tools/list` | `register_tool` frame at startup |
| Tool Execution | `tools/call` | `tool_call` / `tool_result` frames |
| Tool Schema | JSON Schema in `tools/list` | JSON Schema in `register_tool` |
| Resource Access | `resources/*` | Not supported |
| Prompts | `prompts/*` | Not supported |
| Transport | stdio or HTTP/SSE | Subprocess stdin/stdout (JSON-RPC) |
| Event Stream | Notifications | `event`, `notify`, `display`, `submit_slash` frames |
| Tool Intercept | N/A | `event_intercept` for block/allow/rewrite mid-flight |
| Auth | x-api-key / Bearer | OS-level subprocess isolation |

## Protocol Details

The extension protocol (`packages/agent/extproto/`) uses **newline-delimited JSON frames** over the extension subprocess's stdin/stdout:

```json
// Extension registers a tool (sent during startup)
{"type":"register_tool","name":"fetch_with_password","description":"Fetch a URL...","schema":{...}}

// Host invokes the tool
{"type":"tool_call","id":"corr-001","name":"fetch_with_password","args":{"url":"..."}}

// Extension responds
{"type":"tool_result","id":"corr-001","content":[{"type":"text","text":"fetched..."}]}
```

### Frame Types

**Extension → Host:**
- `hello` — announce name, version, capabilities
- `register_tool` — register an LLM-callable tool with JSON Schema
- `register_command` — register a `/command` for the TUI
- `subscribe` — subscribe to agent events and/or intercepts
- `ready` — all initial registrations flushed
- `command_response` — response to a `/command` invocation
- `tool_result` — response to a tool_call
- `notify` — push a note into the TUI
- `display` — append a styled note to chat
- `submit_slash` — programmatic `/command` submission
- `open_panel` / `panel_render` / `panel_close_spontaneous` — interactive panels
- `shutdown_ack` — confirm clean shutdown

**Host → Extension:**
- `hello_ack` — protocol version, zot version, provider, model
- `command_invoked` — execute a registered command
- `tool_call` — execute a registered tool
- `event` — agent lifecycle event notification
- `event_intercept` — intercept tool_call/turn_start/assistant_message
- `panel_key` / `panel_close` — user interaction with a panel
- `shutdown` — terminate the extension

## Extension Manager Architecture

```
Zot Host Process
├── Extension Manager (packages/agent/extensions/manager.go)
│   ├── Extension "secret" (subprocess)
│   │   ├── stdin → JSON frames from host
│   │   ├── stdout ← JSON frames to host
│   │   └── registered tools: [fetch_with_password]
│   ├── Extension "lint" (subprocess)
│   │   └── registered tools: [lint_file, format_code]
│   └── Extension "..." (subprocess)
│       └── registered tools: [...]
├── Tool Registry (core.Registry)
│   └── Built-in: [read, write, edit, bash]
│   └── Extension tools merged in at build time
└── Agent Loop
    └── Intercept pipeline → extensions can block/modify tool calls
```

## Key Differences from MCP

1. **Transport**: MCP uses a standardized JSON-RPC 2.0 transport. Zot uses a custom JSON frame protocol — functionally equivalent but not interoperable with MCP clients.

2. **No Resource or Prompt models**: Zot extensions can only register tools and slash commands. There is no equivalent to MCP's `resources/*` (readable documents/resources) or `prompts/*` (prompt templates).

3. **Interception hooks**: Zot extensions can intercept tool calls, turns, and assistant messages in real-time — a feature MCP does not define. This enables deny-by-default gates, usage quotas, and sensitive-data masking.

4. **Interactive panels**: Zot extensions can render interactive TUI panels (masked password fields, progress displays) — an MCP-extensions concept not in the standard protocol.

5. **No discovery protocol**: Zot extensions are discovered from the filesystem (`$ZOT_HOME/extensions/`) rather than through a dynamic protocol negotiation.

## Example: Secret Extension

The `examples/extensions/secret` extension demonstrates the MCP-adjacent pattern:

```go
e := ext.New("secret", "1.0.0")

e.Tool("fetch_with_password",
    "Fetch a URL that requires a password...",
    schemaJSON,
    func(args json.RawMessage) ext.ToolResult {
        // Tool handler logic — password is collected via panel,
        // used directly, and never exposed to the model
    })

e.Run() // blocks, processes host frames
```

Build: `go build -o secret .` → Install: `zot ext install .`

## Summary

Zot's extension system is **MCP-adjacent**: it solves the same problem (extending an agent with tool capabilities) using a different protocol (custom JSON frames vs JSON-RPC 2.0). For integration with MCP-native tools, consider [[goclaw-mcp-implementation]] which implements full MCP client/server with OAuth, or [[alphaclaw-mcp-implementation]] which writes `mcp.servers` blocks for any external MCP server.

## Related Documentation

- [[zot-architecture]] — Full architecture doc
- [[zot-api]] — Telegram bot and RPC API
- [[zot-acp-implementation]] — Swarm multi-agent orchestration
- [[zot-deployment]] — Deployment patterns
- Source: `sources/zot/packages/agent/ext/`, `sources/zot/packages/agent/extproto/`
