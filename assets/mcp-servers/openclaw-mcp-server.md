---
name: openclaw-mcp-server
tags: [acp, agent-gateway, live-canvas, mcp, mcp-server, messaging, openclaw, personal-assistant, plugin-sdk, quadlet, systemd, typescript]
description: OpenClaw MCP Server
---

# OpenClaw MCP Server
**Source:** `sources/openclaw/`

Asset file for configuring OpenClaw as an MCP server for use with Claude Code and other MCP-compatible clients. OpenClaw provides **three distinct MCP servers**, each serving a different purpose.

## Server Identity

| Property | Value |
|----------|-------|
| Name | `openclaw-channel`, `openclaw-plugin-tools`, `openclaw-tools` |
| Transport | stdio (JSON-RPC over stdin/stdout) |
| Protocol | MCP (Model Context Protocol) v1.x |
| SDK | `@modelcontextprotocol/sdk` v1.x |
| Source | OpenClaw codebase, `src/mcp/` |

### Server Comparison

| Server | Purpose | SDK Class | Notifications |
|--------|---------|-----------|---------------|
| `openclaw-channel` | Bridges messaging channels (conversations, messages, approvals) via the Gateway | `McpServer` (high-level) | Yes |
| `openclaw-plugin-tools` | Exposes plugin-registered tools (memory recall, etc.) | `Server` (low-level) | No |
| `openclaw-tools` | Exposes built-in OpenClaw tools (cron) | `Server` (low-level) | No |

---

## Configuration for Claude Code

### Method 1: `claude mcp add` Command

```bash
# Channel MCP server (conversations, messages, approvals)
claude mcp add openclaw-channel -- openclaw mcp channel

# Plugin tools MCP server (memory_recall, memory_store, etc.)
claude mcp add openclaw-plugin-tools -- openclaw mcp plugin-tools

# OpenClaw built-in tools (cron)
claude mcp add openclaw-tools -- openclaw mcp openclaw-tools
```

### Method 2: `~/.claude/settings.json`

```json
{
  "mcpServers": {
    "openclaw-channel": {
      "command": "openclaw",
      "args": ["mcp", "channel"]
    },
    "openclaw-plugin-tools": {
      "command": "openclaw",
      "args": ["mcp", "plugin-tools"]
    },
    "openclaw-tools": {
      "command": "openclaw",
      "args": ["mcp", "openclaw-tools"]
    }
  }
}
```

### Method 3: Custom Source Path

```json
{
  "mcpServers": {
    "openclaw-channel": {
      "command": "node",
      "args": ["--import", "tsx", "/path/to/openclaw/src/mcp/channel-server.ts"]
    },
    "openclaw-plugin-tools": {
      "command": "node",
      "args": ["--import", "tsx", "/path/to/openclaw/src/mcp/plugin-tools-serve.ts"]
    },
    "openclaw-tools": {
      "command": "node",
      "args": ["--import", "tsx", "/path/to/openclaw/src/mcp/openclaw-tools-serve.ts"]
    }
  }
}
```

### Method 4: With Bun (Alternative Runtime)

```json
{
  "mcpServers": {
    "openclaw-tools": {
      "command": "bun",
      "args": ["/path/to/openclaw/src/mcp/openclaw-tools-serve.ts"]
    }
  }
}
```

### Method 5: Cursor IDE

```json
{
  "mcpServers": {
    "openclaw-channel": {
      "command": "openclaw",
      "args": ["mcp", "channel"]
    }
  }
}
```

---

## Tools Available

### Channel MCP Server

| Tool | Description | Parameters |
|------|-------------|------------|
| `conversations_list` | List channel-backed conversations | `{limit?, search?, channel?, includeDerivedTitles?, includeLastMessage?}` |
| `conversation_get` | Get one conversation by session key | `{session_key: string}` |
| `messages_read` | Read recent messages (max 200) | `{session_key: string, limit?}` |
| `messages_send` | Send a reply through a channel | `{session_key: string, text: string}` |
| `attachments_fetch` | List non-text attachments | `{session_key: string, message_id: string, limit?}` |
| `events_poll` | Poll queued events (non-blocking, max 200) | `{after_cursor?, session_key?, limit?}` |
| `events_wait` | Wait for next event (blocking, 300s max) | `{after_cursor?, session_key?, timeout_ms?}` |
| `permissions_list_open` | List open approval requests | `{}` |
| `permissions_respond` | Respond to a pending approval | `{kind: "exec"\|"plugin", id: string, decision: string}` |

### Plugin Tools MCP Server

Tools are dynamic based on registered OpenClaw plugins. Common plugin tools include:

| Tool | Description |
|------|-------------|
| `memory_recall` | Recall memories from vector store |
| `memory_store` | Store a memory |
| `memory_forget` | Forget a memory |

Additional plugin-registered tools are discovered at startup based on installed plugins.

### OpenClaw Tools MCP Server

| Tool | Description |
|------|-------------|
| `cron` | Schedule recurring tasks via the OpenClaw cron tool system |

---

## Notifications (Channel Server Only)

When `claudeChannelMode` is not `"off"` (default: `"auto"`):

- `notifications/claude/channel` -- New user message on a Claude channel
- `notifications/claude/channel/permission` -- Claude permission reply detected

The server advertises these capabilities:

```json
{
  "experimental": {
    "claude/channel": {},
    "claude/channel/permission": {}
  }
}
```

---

## Environment and Configuration

### Channel MCP Server

The channel server reads `openclaw.json` for Gateway connection details, or accepts explicit config:

| Variable/Config | Purpose |
|-----------------|---------|
| `gatewayUrl` | Gateway WebSocket URL (auto-resolved from `~/.openclaw/credentials/`) |
| `gatewayToken` | Gateway auth token |
| `gatewayPassword` | Gateway auth password (alternative to token) |
| `claudeChannelMode` | `"off"` = no channel features, `"on"` = always, `"auto"` = default |

### Plugin Tools MCP Server

Reads `openclaw.json` for tool allow/deny policy:

| Config | Purpose |
|--------|---------|
| `tools.profile` | Tool profile selection |
| `tools.alsoAllow` | Additional allowed tools |
| `tools.deny` | Denied tool list |

---

## Important Integration Details

1. **Stdio transport only** -- No SSE, HTTP, or WebSocket. All communication via stdin/stdout JSON-RPC.

2. **Log routing is critical** -- All servers call `routeLogsToStderr()` to keep stdout clean. Read stderr for diagnostics; never parse stdout for logs.

3. **Lifecycle** -- Servers are designed as child processes. They auto-shutdown when stdin closes or on SIGINT/SIGTERM.

4. **Shutdown safety** -- Shutdown guards prevent double-close errors.

5. **Channel vs. tools servers** -- The channel server uses the high-level `McpServer` SDK class (supports notifications). The plugin-tools and openclaw-tools servers use the low-level `Server` SDK class (tools/list and tools/call only, no notifications).

6. **Plugin tools approval** -- When a plugin tool requires approval, the MCP bridge reports it as an error. Approval flows are not supported over the MCP bridge for plugin tools.

7. **Connection latency** -- The channel server must establish a WebSocket connection to the Gateway before serving tools. Operation latency is bounded by Gateway round-trip time.

## Related

- [[openclaw-acp-agent]] -- ACP agent asset registration (companion protocol)
- [[openclaw-api]] -- REST and WebSocket API reference
- [[openclaw-deployment]] -- Full deployment guide
- [[openclaw]] -- Main wiki entry

---

## Related

- [[domains/mcp/openclaw-mcp-implementation.md]] -- Comprehensive MCP implementation document
- [[domains/architecture/openclaw-architecture.md]] -- Gateway architecture
- [[domains/acp/openclaw-acp-implementation.md]] -- ACP protocol (companion protocol)
- [[assets/deployment/openclaw-quadlet.md]] -- Quadlet deployment patterns
- [[assets/agent-profiles/openclaw-profile.md]] -- Quick reference profile
