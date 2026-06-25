---
name: openclaw-mcp-implementation
tags: [acp, agent-gateway, ai-llm, cli, live-canvas, mcp, messaging, openclaw, personal-assistant, plugin-sdk, quadlet, security, systemd, typescript]
description: OpenClaw MCP Implementation
source: sources/openclaw/
---

# OpenClaw MCP Implementation
**Source:** `sources/openclaw/`

OpenClaw implements three distinct Model Context Protocol (MCP) servers, each serving a different purpose: channel bridging, plugin tool exposure, and built-in tool exposure. This document details the architecture, implementation, and configuration of all three MCP surfaces.

---

## Architecture Overview

OpenClaw provides three MCP server implementations in `src/mcp/`:

| Server | Source File | SDK Class | Purpose |
|--------|-------------|-----------|---------|
| Channel Bridge | `src/mcp/channel-server.ts` | `McpServer` (high-level) | Bridges messaging channels (conversations, messages, approvals) via the OpenClaw Gateway |
| Plugin Tools | `src/mcp/plugin-tools-serve.ts` | `Server` (low-level) | Exposes plugin-registered tools (memory recall, etc.) |
| OpenClaw Tools | `src/mcp/openclaw-tools-serve.ts` | `Server` (low-level) | Exposes built-in OpenClaw agent tools (cron) |

### SDK Versions

All three servers use `@modelcontextprotocol/sdk` v1.x for MCP protocol implementation.

### Transport

All three servers use **stdio transport only** (JSON-RPC over stdin/stdout). No SSE, HTTP, or WebSocket transports are provided. This is by design -- the servers are intended to run as child processes of MCP clients (Claude Code, etc.).

---

## Channel Bridge MCP Server

The channel bridge (`src/mcp/channel-server.ts`) is the most feature-rich MCP server. It uses the high-level `McpServer` class from the SDK, which supports notifications in addition to tools.

### Implementation

`createOpenClawChannelMcpServer()` sets up an `McpServer` instance with `StdioServerTransport`. It uses an `OpenClawChannelBridge` to communicate with the OpenClaw Gateway over WebSocket.

```
MCP Client <-> stdio <-> OpenClawChannelMcpServer <-> OpenClawChannelBridge <-> WebSocket <-> OpenClaw Gateway
```

### Architecture

- The channel server reads `openclaw.json` for Gateway connection details (gateway URL, token/password)
- Gateway URL is auto-resolved from `~/.openclaw/credentials/` if not explicitly provided
- The `OpenClawChannelBridge` establishes a WebSocket connection to the Gateway after MCP initialize
- The bridge translates MCP tool calls into Gateway RPC methods and translates Gateway events back into MCP notifications

### Available Tools

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

### Notifications

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

### ClaudePermissionRequestSchema Handling

The channel server handles `ClaudePermissionRequestSchema` notifications from MCP requests, translating Claude-specific permission schemas into OpenClaw's own permission flow.

### Event Loops

The channel server maintains two event loops:

- **Poll loop**: Periodically checks for new events from the Gateway
- **Notification loop**: Forwards events to the MCP client as notifications

Both loops are started after MCP initialize completes and are stopped on server shutdown.

### Configuration

| Config Option | Purpose |
|---------------|---------|
| `gatewayUrl` | Gateway WebSocket URL (auto-resolved if absent) |
| `gatewayToken` | Gateway auth bearer token |
| `gatewayPassword` | Alternative gateway auth password |
| `claudeChannelMode` | `"off"` = no channel features, `"on"` = always, `"auto"` = default |

---

## Plugin Tools MCP Server

The plugin tools server (`src/mcp/plugin-tools-serve.ts`) uses the low-level `Server` SDK class (tools/list and tools/call only, no notifications).

### Implementation

- Connects to the OpenClaw Gateway via WebSocket
- Reads tool allow/deny policy from `openclaw.json`
- Discovers all registered plugin tools at startup
- Serves `tools/list` with the resolved tool set
- Serves `tools/call` by dispatching to the Gateway's plugin tool executor

### Common Plugin Tools

Plugin tools vary based on installed plugins. Common examples include:

| Tool | Plugin | Description |
|------|--------|-------------|
| `memory_recall` | memory plugin | Recall memories from vector store |
| `memory_store` | memory plugin | Store a memory |
| `memory_forget` | memory plugin | Forget a memory |
| Additional tools from 85+ bundled extensions |

### Configuration

| Config | Purpose |
|--------|---------|
| `tools.profile` | Tool profile selection (which tools are visible) |
| `tools.alsoAllow` | Additional allowed tools beyond the profile |
| `tools.deny` | Denied tool list (overrides profile and allow) |

### Approval Handling

When a plugin tool requires user approval, the MCP bridge reports it as an error rather than opening an approval flow. Approval flows are not supported over the MCP bridge for plugin tools -- this is a known limitation.

---

## OpenClaw Tools MCP Server

The OpenClaw tools server (`src/mcp/openclaw-tools-serve.ts`) also uses the low-level `Server` SDK class.

### Implementation

- Connects to the OpenClaw Gateway via WebSocket
- Discovers built-in OpenClaw tools at startup
- Serves `tools/list` with available built-in tools
- Serves `tools/call` by dispatching to the Gateway's built-in tool executor

### Available Tools

| Tool | Description |
|------|-------------|
| `cron` | Schedule recurring tasks via the OpenClaw cron tool system |

Additional built-in tools are added as the OpenClaw tool system evolves.

---

## Common Implementation Details

### Logging

All three MCP servers call `routeLogsToStderr()` to keep stdout clean. Stderr is used for all log output. Clients should read stderr for diagnostics; stdout must never be parsed for log content.

### Lifecycle

- Servers are designed as child processes of an MCP client
- Auto-shutdown when stdin closes or on SIGINT/SIGTERM
- Shutdown guards prevent double-close errors
- `StdioServerTransport` provides the transport layer

### Startup Sequence

1. Load configuration (from `openclaw.json` or environment)
2. Route logging to stderr
3. Establish WebSocket connection to Gateway
4. Advertise capabilities on MCP `initialize` request
5. Start event loops (channel server only)
6. Serve tool requests until stdin closes

### Security

- Gateway token must be provided (via config, env var, or auto-resolve)
- Token is sent during Gateway WebSocket handshake
- Plugin tool approval requests are reported as errors (not relayed via approval flow)
- Stdio transport means the MCP client's parent process controls access

### Error Handling

- Tool calls that fail on the Gateway side return MCP error responses with descriptive messages
- Plugin tools requiring approval return errors rather than blocking on permission
- Connection errors to the Gateway are reported via stderr logging
- Server crashes are handled by the parent process (MCP client auto-restart)

---

## Configuration Examples

### Claude Code Settings

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

### Custom Source Path

```json
{
  "mcpServers": {
    "openclaw-channel": {
      "command": "node",
      "args": ["--import", "tsx", "/path/to/openclaw/src/mcp/channel-server.ts"]
    }
  }
}
```

### Bun Runtime

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

---

## Known Limitations

1. **Plugin tool approval over MCP** -- Plugin tools that require user approval report errors rather than opening approval flows. This is a MCP protocol limitation (no bidirectional approval flow in standard MCP).
2. **Stdio transport only** -- No SSE/HTTP/WebSocket MCP transport. Servers must run as child processes.
3. **Single-process design** -- Each MCP server is a single Node.js process. Scalability is limited by process resources.
4. **Channel server startup latency** -- The channel server must establish a Gateway WebSocket connection before serving tools, adding latency to first request.
5. **No outbound MCP client** -- OpenClaw cannot connect as a client to external MCP servers. It only serves MCP to clients.

---

## Key Source Files

| File | Purpose |
|------|---------|
| `src/mcp/channel-server.ts` | Channel bridge MCP server (McpServer SDK) |
| `src/mcp/plugin-tools-serve.ts` | Plugin tools MCP server (Server SDK) |
| `src/mcp/openclaw-tools-serve.ts` | Built-in tools MCP server (Server SDK) |
| `src/mcp/channel-bridge.ts` | Gateway WebSocket bridge for channel server |
| `src/mcp/mcp-helpers.ts` | Shared MCP utilities (logging, etc.) |
| `src/gateway/server-ws-runtime.ts` | Gateway WebSocket runtime that MCP servers connect to |

## Related

- [[openclaw-acp-agent]] -- ACP agent asset registration (companion protocol)
- [[openclaw-deployment]] -- Full deployment guide
- [[openclaw-profile]] -- Quick reference profile
- [[openclaw]] -- Main wiki entry

---

## Related

- [[domains/architecture/openclaw-architecture.md]] -- Gateway architecture
- [[domains/acp/openclaw-acp-implementation.md]] -- ACP protocol (companion protocol)
- [[assets/mcp-servers/openclaw-mcp-server.md]] -- MCP server asset registration
- [[domains/api/openclaw-api.md]] -- API reference
# OpenClaw MCP Implementation

OpenClaw implements **three distinct MCP server surfaces**, all using the `@modelcontextprotocol/sdk` (v1.x) library and all operating over **stdio transport only** (no SSE, no HTTP). They share a common stdio connection utility but serve different purposes. Additionally, a fourth surface is represented by the **channel bridge** that sits between the MCP layer and the Gateway.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Channel MCP Server](#channel-mcp-server)
- [Plugin Tools MCP Server](#plugin-tools-mcp-server)
- [OpenClaw Tools MCP Server](#openclaw-tools-mcp-server)
- [Shared Tools Stdio Server](#shared-tools-stdio-server)
- [Claude Code Integration](#claude-code-integration)
- [Configuration Reference](#configuration-reference)

---

## Architecture Overview

The MCP subsystem lives in `src/mcp/` and contains these key files:

| File | Lines | Purpose |
|------|-------|---------|
| `channel-server.ts` | -- | Channel MCP server lifecycle |
| `channel-bridge.ts` | 652 | Gateway-to-MCP bridge runtime |
| `channel-tools.ts` | -- | MCP tool schemas/handlers for channels |
| `channel-shared.ts` | -- | Shared channel MCP types |
| `plugin-tools-serve.ts` | 88 | Plugin tools MCP server |
| `plugin-tools-handlers.ts` | -- | Plugin tool MCP handlers |
| `openclaw-tools-serve.ts` | 37 | OpenClaw built-in tools MCP server |
| `tools-stdio-server.ts` | 49 | Shared stdio framework |

All three servers share these patterns:

- `tools-stdio-server.ts` provides `createToolsMcpServer()` and `connectToolsMcpServerToStdio()` reused by plugin-tools and openclaw-tools servers
- Logs are always routed to stderr via `routeLogsToStderr()` so stdout stays protocol-clean
- Shutdown is handled via stdin `end`/`close` and `SIGINT`/`SIGTERM`
- Plugin tools enforce the `before_tool_call` hook with `approvalMode: "report"` (reports approval requirements but does not open Gateway approval flows from the MCP bridge)

---

## Channel MCP Server

**File:** `src/mcp/channel-server.ts`

The channel MCP server bridges messaging channel conversations via the OpenClaw Gateway. It is the richest MCP surface -- it supports bidirectional communication where the server can push notifications to the client for incoming messages and permission resolution.

### Transport

- stdio via `StdioServerTransport` from `@modelcontextprotocol/sdk`
- Uses the **high-level `McpServer` class** (not the low-level `Server` class)
- Runs as a standalone child process

### Architecture

The channel server is built on two key components:

**`OpenClawChannelBridge`** (`src/mcp/channel-bridge.ts`):
- Connects to the OpenClaw Gateway via WebSocket (`GatewayClient` from `src/gateway/client.js`)
- Manages Gateway lifecycle, event cursoring, pending approvals state
- Narrow request methods that channel MCP tools expose

**`registerChannelMcpTools()`** (`src/mcp/channel-tools.ts`):
- Registers MCP tool schemas and handlers
- Wires each tool to the bridge's underlying Gateway RPC call

### Tools Exposed

| Tool Name | Schema | Description |
|-----------|--------|-------------|
| `conversations_list` | `{limit?, search?, channel?, includeDerivedTitles?, includeLastMessage?}` | List OpenClaw channel-backed conversations |
| `conversation_get` | `{session_key: string}` | Get one conversation by session key |
| `messages_read` | `{session_key: string, limit?}` | Read recent messages for a conversation (max 200) |
| `messages_send` | `{session_key: string, text: string}` | Send a reply through the same channel route |
| `attachments_fetch` | `{session_key: string, message_id: string, limit?}` | List non-text attachments for a message |
| `events_poll` | `{after_cursor?, session_key?, limit?}` | Poll queued events since a cursor (non-blocking, max 200) |
| `events_wait` | `{after_cursor?, session_key?, timeout_ms?}` | Wait for next queued event (blocking, max 300s timeout) |
| `permissions_list_open` | `{}` | List open exec or plugin approval requests |
| `permissions_respond` | `{kind: "exec"|"plugin", id: string, decision: "allow-once"|"allow-always"|"deny"}` | Allow or deny a pending approval |

### Notifications (Server-to-Client)

When `claudeChannelMode` is `"on"` or `"auto"`:

- `notifications/claude/channel` -- new user message on a Claude channel (includes content + meta with session_key, channel, to, account_id, thread_id, message_id)
- `notifications/claude/channel/permission` -- Claude permission reply detected (includes request_id + behavior: `"allow"` | `"deny"`)

### Capabilities Advertised

When `claudeChannelMode !== "off"`:

```json
{
  "experimental": {
    "claude/channel": {},
    "claude/channel/permission": {}
  }
}
```

### Bridge Internals

**Gateway connection lifecycle:**
- `constructor()` -- accepts `OpenClawConfig`, optional explicit `gatewayUrl`/`gatewayToken`/`gatewayPassword`, `claudeChannelMode`, and `verbose` flag
- `start()` -- creates `GatewayClient` with scopes `[READ_SCOPE, WRITE_SCOPE, APPROVALS_SCOPE]`, subscribes to session events
- `close()` -- stops Gateway IO, clears pending maps, releases event waiters, clears sweeper interval
- `waitUntilReady()` -- resolves once subscribed to Gateway session events

**Event management:**
- In-memory event ring buffer: `queue: QueueEvent[]` (max 1000 entries)
- `pendingWaiters: Set<PendingWaiter>` -- long-poll waiters awaiting events
- `pendingApprovals: Map<string, PendingApprovalEntry>` -- tracked approval requests with 30-min default TTL
- A 5-minute pending sweep interval evicts expired entries and self-terminates when both maps are empty

**Gateway event handling:**
- Dispatches on `session.message`, `exec.approval.requested`, `exec.approval.resolved`, `plugin.approval.requested`, `plugin.approval.resolved`
- Detects Claude permission replies (pattern: `yes/no <5-char-code>`)
- Emits MCP notifications for user messages when `claudeChannelMode` is not "off"

---

## Plugin Tools MCP Server

**File:** `src/mcp/plugin-tools-serve.ts` (88 lines)

### Purpose

Standalone MCP server that exposes OpenClaw **plugin-registered tools** (e.g. memory-lancedb's `memory_recall`, `memory_store`, `memory_forget`) so external ACP sessions running Claude Code can use them.

### Transport

- stdio via `StdioServerTransport`
- Uses the **low-level `Server` class** (not `McpServer`)
- Runs as a standalone child process

### How It Works

1. Calls `routeLogsToStderr()` before any tool discovery
2. Loads config via `getRuntimeConfig()`
3. Resolves plugin tools:
   - `resolvePluginToolPolicy(config)` -- merges tool profiles, `alsoAllow`, and sandbox policies into allow/deny lists
   - `ensureStandalonePluginToolRegistryLoaded()` -- ensures the standalone plugin tool registry is initialized
   - `resolvePluginTools()` -- resolves available plugin tools, respecting allow/deny lists, with `suppressNameConflicts: true`
4. Creates the MCP server via `createToolsMcpServer({name: "openclaw-plugin-tools", tools})`
5. Connects to stdio via `connectToolsMcpServerToStdio()`

### Entry Points

- `createPluginToolsMcpServer({config?, tools?})` -- factory for testing/embedding (returns `Server`)
- `servePluginToolsMcp()` -- the main entry point that runs the server to completion

### Configuration

Reads `openclaw.json` config for:

- `tools.profile` -- tool profile selection
- `tools.alsoAllow` -- additional allowed tools
- `tools.deny` -- denied tools

Plugin tools are run through `wrapToolWithBeforeToolCallHook` with `approvalMode: "report"` -- the MCP bridge reports approval requirements as errors (does not open Gateway approval flows from MCP side).

### Tools Exposed

Dynamic based on registered plugins. Tool names, descriptions, and schemas come from plugin registrations.

Standard `tools/list` and `tools/call` request handlers.

---

## OpenClaw Tools MCP Server

**File:** `src/mcp/openclaw-tools-serve.ts` (37 lines)

### Purpose

Standalone MCP server exposing **built-in OpenClaw agent tools** (not plugin tools) as MCP tools.

### Transport

- stdio via the shared `connectToolsMcpServerToStdio()` function
- Uses the **low-level `Server` class**

### Tools Exposed

Currently only exposes the `cron` tool:

| Tool Name | Description |
|-----------|-------------|
| `cron` | Schedule recurring tasks via the OpenClaw cron tool system |

### Key Characteristics

- No Gateway dependency -- operates without any Gateway connection
- No approval flow -- built-in tools run directly
- Uses `createOpenClawToolsMcpServer({tools?})` factory
- Detects if running as entry point via `import.meta.url === pathToFileURL(process.argv[1])`

### Standalone Invocation

```bash
node --import tsx src/mcp/openclaw-tools-serve.ts
# or
bun src/mcp/openclaw-tools-serve.ts
```

---

## Shared Tools Stdio Server

**File:** `src/mcp/tools-stdio-server.ts` (49 lines)

### Purpose

Shared stdio-based MCP server framework used by both `plugin-tools-serve.ts` and `openclaw-tools-serve.ts`.

### Functions

**`createToolsMcpServer(params: { name: string; tools: AnyAgentTool[] })`**
- Creates an MCP `Server` instance with `{ capabilities: { tools: {} } }`
- Creates tool handlers via `createPluginToolsMcpHandlers(tools)` (shared with `plugin-tools-handlers.ts`)
- Registers `ListToolsRequestSchema` and `CallToolRequestSchema` request handlers
- Returns the raw `Server` object (low-level SDK `Server`, not the high-level `McpServer` wrapper)

**`connectToolsMcpServerToStdio(server: Server)`**
- Calls `routeLogsToStderr()` to ensure all application logging goes to stderr
- Creates `StdioServerTransport`
- Sets up lifecycle handlers:
  - stdin `end` and `close` events trigger graceful shutdown
  - `SIGINT` and `SIGTERM` also trigger graceful shutdown
- Calls `server.connect(transport)`
- The shutdown guard (`shuttingDown` bool) prevents double-close

---

## Claude Code Integration

Since all three MCP servers use **stdio transport**, integration with Claude Code is done via the `claude mcp add` command or by editing `~/.claude/settings.json`.

### Channel MCP Server

```json
{
  "mcpServers": {
    "openclaw-channel": {
      "command": "node",
      "args": ["--import", "tsx", "/path/to/openclaw/src/mcp/channel-server.ts"]
    }
  }
}
```

```bash
claude mcp add openclaw-channel -- node --import tsx /path/to/openclaw/src/mcp/channel-server.ts
```

### Plugin Tools MCP Server

```json
{
  "mcpServers": {
    "openclaw-plugin-tools": {
      "command": "node",
      "args": ["--import", "tsx", "/path/to/openclaw/src/mcp/plugin-tools-serve.ts"]
    }
  }
}
```

```bash
claude mcp add openclaw-plugin-tools -- node --import tsx /path/to/openclaw/src/mcp/plugin-tools-serve.ts
```

### OpenClaw Tools MCP Server

```json
{
  "mcpServers": {
    "openclaw-tools": {
      "command": "node",
      "args": ["--import", "tsx", "/path/to/openclaw/src/mcp/openclaw-tools-serve.ts"]
    }
  }
}
```

```bash
claude mcp add openclaw-tools -- node --import tsx /path/to/openclaw/src/mcp/openclaw-tools-serve.ts
```

---

## Configuration Reference

### Channel MCP Server

| Parameter | Default | Description |
|-----------|---------|-------------|
| `gatewayUrl` | (auto-resolved) | Gateway WebSocket URL |
| `gatewayToken` | (auto-resolved) | Gateway auth token |
| `gatewayPassword` | (auto-resolved) | Gateway auth password |
| `claudeChannelMode` | `"auto"` | Controls channel notifications: `"off"`, `"on"`, `"auto"` |
| Gateway scopes | `[READ_SCOPE, WRITE_SCOPE, APPROVALS_SCOPE]` | Required Gateway method scopes |
| Gateway client mode | `CLI` | Client mode with display name "OpenClaw MCP" |
| Request timeout | 180s | Gateway request timeout |
| Event queue limit | 1000 | Max events in ring buffer |
| Events poll max | 200 | Max returned per poll |
| Events wait timeout | 300s | Max wait for event |
| Conversation list max | 500 | Max conversations returned |
| Messages read max | 200 | Max messages returned |

### Plugin Tools MCP Server

| Parameter | Source | Description |
|-----------|--------|-------------|
| `tools.profile` | `openclaw.json` | Tool profile selection |
| `tools.alsoAllow` | `openclaw.json` | Additional allowed tools |
| `tools.deny` | `openclaw.json` | Denied tool list |
| Approval mode | `"report"` | Reports approval requirements as errors |

### OpenClaw Tools MCP Server

| Parameter | Source | Description |
|-----------|--------|-------------|
| `creatorToolAllowlist` | Code | Allowlist passed to `createCronTool()` |

---

## Integration Details

1. **Stdio transport only** -- all servers communicate via stdin/stdout using JSON-RPC. No SSE or HTTP transport option.

2. **Log routing** -- all servers call `routeLogsToStderr()` which ensures stdout stays protocol-clean. Application logs go to stderr.

3. **Lifecycle** -- the MCP servers are designed as child processes spawned by the MCP client (Claude Code). They automatically shut down when stdin closes or on SIGINT/SIGTERM.

4. **The channel MCP server uses the high-level `McpServer` SDK class** (with notifications, tool registration wrapping, capability announcements). This is the richest server.

5. **The plugin-tools and openclaw-tools servers use the lower-level `Server` SDK class** -- simpler, just tools/list and tools/call request handlers. No notifications.

6. **Plugin tools enforce `approvalMode: "report"`** -- when a plugin tool requires approval, the MCP bridge reports it as an error rather than attempting to open an approval dialog through the Gateway.

7. **Channel MCP notifications work only when `claudeChannelMode` is not "off"** -- defaults to `"auto"`. In `"on"` or `"auto"` mode, the server advertises `experimental.claude/channel` capabilities and sends notifications for new messages and permission responses.

8. **Shutdown safety** -- both server implementations have shutdown guards preventing double-close. The channel server has a dedicated test verifying that rejection during shutdown does not cause unhandled rejection errors.

---

## Related

- [[domains/architecture/openclaw-architecture.md]] -- Overall system architecture
- [[domains/acp/openclaw-acp-implementation.md]] -- ACP agent protocol (related MCP-adjacent protocol)
- [[assets/mcp-servers/openclaw-mcp-server.md]] -- MCP server config asset file
- [[assets/deployment/openclaw-quadlet.md]] -- Quadlet deployment patterns
