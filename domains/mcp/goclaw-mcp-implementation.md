---
name: goclaw-mcp
description: "GoClaw MCP client/server implementation — bridge tools, connection pool, OAuth"
tags: [ai-llm, cli, documentation, mcp, security, storage]
---
# GoClaw MCP Implementation

**Source:** `/Users/admin1/Documents/knowledge/raw/goclaw/goclaw.xml`  
**Generated:** 2026-06-25

---

## Overview

GoClaw implements MCP (Model Context Protocol) in two complementary directions:

1. **MCP Client** (`internal/mcp/`) -- Connect to external MCP servers, discover and invoke their tools as GoClaw-native tools via the `tools.Registry`.
2. **MCP Server** (`internal/mcp/bridge_server.go`) -- Expose GoClaw's own built-in tools as an MCP server that other MCP clients can connect to.

The implementation uses the `github.com/mark3labs/mcp-go` Go library for both client and server.

---

## 1. MCP Client Implementation (`internal/mcp/`)

### Package Files

| File | Purpose |
|------|---------|
| `manager.go` | Core `Manager` type -- lifecycle, server state, connection orchestration |
| `manager_connect.go` | `connectAndDiscover()`, `connectServer()`, `connectViaPool()`, health loops, reconnection with exponential backoff |
| `manager_tools.go` | Tool registration (`registerBridgeTools`, `registerPoolBridgeTools`), `DiscoverTools()`, `UserCredServers()` |
| `bridge_tool.go` | `BridgeTool` type -- wraps an MCP tool as a GoClaw `tools.Tool` with `Execute()` method |
| `bridge_server.go` | MCP server that exposes GoClaw's built-in tools as MCP tools |
| `pool.go` | Connection pool for shared MCP server connections across agents |
| `grant_checker.go` | Checks agent-level access grants for MCP servers |
| `mcp_tool_search.go` | BM25-based search tool for lazy/discoverable MCP tools |
| `tool_filter.go` | `IsToolAllowed()` allow/deny list filtering |
| `session_reset.go` | Session uninitialized error detection and force reconnect |
| `validation.go` | MCP command/URL validation and allowlisting |
| `oauth/` | OAuth 2.0 client credential flow, DCR (Dynamic Client Registration), token refresh |

### Manager Architecture

```
Manager
├── servers map[string]*serverState    -- Per-agent connections
├── poolServers map[string]struct{}    -- Pool-managed connections
├── registry *tools.Registry           -- GoClaw's central tool registry
├── store MCPServerStore               -- Persistent server configs
├── grantChecker GrantChecker          -- Agent-level access control
├── pool *Pool                         -- Connection pool
├── configs map[string]*config.MCPServerConfig
└── deferredTools []*BridgeTool        -- Lazy activation (search mode)
```

### Server State (per connection)

```go
type serverState struct {
    name       string
    transport  string            // "stdio" or "streamable-http" (SSE)
    client     *mcpclient.Client
    clientPtr  atomic.Pointer[mcpclient.Client]
    connected  atomic.Bool
    toolNames  []string
    timeoutSec int
    cancel     context.CancelFunc
    conn       connParams        // command, args, env, url, headers
    reconnAttempts int
    healthFailures int
    lastErr        string
    reconnPending  atomic.Bool
}
```

### Lifecycle

1. **`NewManager(registry, opts...)`** -- Create manager with configs, store, pool, grant checker, OAuth provider
2. **`Start(ctx)`** -- Load MCP server configs from store, connect all enabled servers
3. **`LoadForAgent(ctx, agentID, userID)`** -- Connect servers accessible by a specific agent; clears and reloads all MCP tools
4. **`Stop()`** -- Disconnect all servers, unregister all MCP tools

### Connection Details

#### `connectAndDiscover()`

- Supports two transports: `stdio` (command+args+env) and `streamable-http` (URL+headers)
- Retries initialization up to `maxInitAttempts = 4` times
- Timeout per server configurable via `timeoutSec`
- Returns discovered `[]mcpgo.Tool` list and a `*serverState`

#### `createClient()`

- **stdio**: Uses `mcpclient.NewClientWithCommand()` with StdioOptions (command, args, env)
- **streamable-http**: Uses `mcpclient.NewStreamableHTTPClient()` with StreamableHTTPOptions (URL, headers)

### Health & Reconnection

- Health check every 30s via `healthLoop()`
- After 3 consecutive failures, enters reconnection with exponential backoff:
  - `initialBackoff = 2s`, `maxBackoff = 60s`
  - Max 10 attempts, then 5min cooldown
- Session uninitialized errors trigger immediate force reconnect (`requestForceReconnect`)
- Pool-managed connections use `poolHealthLoop()` and `poolTryReconnect()`

### Tool Registration

#### Per-Agent Mode (`registerBridgeTools()`)
- Wraps each MCP tool in a `BridgeTool` with MCP prefix (e.g. `server_name--tool_name`)
- Applies allow/deny filtering upfront -- non-allowed tools never reach the registry
- Registers in `tools.Registry` for LLM consumption
- Configurable `ToolHints` (global prompt hint, per-tool hints)

#### Pool Mode (`registerPoolBridgeTools()`)
- Similar wrapping but uses shared pool connection
- Multiple agents share one connection via `pool.Acquire()`

### Bridge Tool Execution

`BridgeTool` implements `tools.Tool`:
- `Name()` -- Returns prefixed name
- `Description()` -- Returns MCP tool description (truncated to `mcpToolDescMaxLen = 200`)
- `Parameters()` -- JSON Schema from MCP tool input schema
- `Execute(ctx, args)` -- Calls MCP server via `mcpgo.ToolCallRequest`, returns result

Tool execution supports:
- Text content
- Image content (base64, forwarded as media attachments via MessageBus)
- Embedded resources
- Error handling (isError flag)

### Lazy Activation / Search Mode

When an agent has access to more than `mcpToolInlineMaxCount = 40` MCP tools, GoClaw enters "search mode":
- Only `<40` tools are inlined in the system prompt
- Remaining tools are deferred in `deferredTools`
- An `mcp_tool_search` tool is registered that uses a BM25 index to search for tools
- `ActivateTools(names)` and `ActivateToolIfDeferred(name)` promote deferred tools to active

### Connection Pool

```go
type PoolConfig struct {
    MaxSize            int           // Max pooled connections
    MaxIdle            int           // Max idle connections
    IdleTTL            time.Duration // Idle timeout before eviction
    AcquireTimeout     time.Duration // Timeout acquiring a pooled connection
    MaxUserConns       int           // Per-user connection limit
    UserIdleTTL        time.Duration
    UserAcquireTimeout time.Duration
}
```

- `Acquire(ctx, tenantID, name, ...)` -- Get or create pooled connection
- `AcquireUser(ctx, tenantID, name, userID, ...)` -- Per-user isolated connection
- `Release(key)` / `ReleaseUser(key)` -- Return to pool
- `Evict()` / `EvictServer()` / `EvictAllUsers()` -- Force eviction
- Background eviction loop removes idle connections

### OAuth Support (`internal/mcp/oauth/`)

- **Discovery** -- OAuth authorization server metadata (RFC 8414)
- **DCR** -- Dynamic Client Registration (RFC 7591)
- **Flow** -- Authorization code + token exchange
- **Refresher** -- Token refresh with in-memory cache

### Grant Checker

```go
type GrantChecker interface {
    CheckAccess(ctx context.Context, agentID, serverID uuid.UUID) (bool, error)
}
```

Filters which agents can access which MCP servers. Applied at connection time.

### Validation & Security

- `Validation` package checks command allowlisting and URL allowlisting
- Host validation exempts private IPs for local MCP servers (but never metadata endpoints)
- Tool allow/deny filtering per server via server grants

---

## 2. MCP Server Implementation (`internal/mcp/bridge_server.go`)

### NewBridgeServer()

Creates an MCP server (`mcpserver.StreamableHTTPServer`) that exposes GoClaw's built-in tools:

```go
func NewBridgeServer(reg *tools.Registry, version string, msgBus *bus.MessageBus) *mcpserver.StreamableHTTPServer
```

### BridgeToolNames

The following GoClaw built-in tools are exposed as MCP tools (24 tools):

| Tool | Tool |
|------|------|
| `read_file` | `write_file` |
| `list_files` | `edit` |
| `exec` | `web_search` |
| `web_fetch` | `memory_search` |
| `memory_get` | `skill_search` |
| `read_image` | `create_image` |
| `tts` | `browser` |
| `cron` | `message` |
| `sessions_list` | `session_status` |
| `sessions_history` | `sessions_send` |
| `team_tasks` | `delegate` |

### convertToMCPTool()

Converts a GoClaw `tools.Tool` into an `mcpgo.Tool`:
- Name preserved
- Description taken from tool
- Parameters converted from JSON Schema map to `mcpgo.ToolInputSchema`

### makeToolHandler()

Creates a handler function that:
1. Deserializes MCP call arguments
2. Delegates to the GoClaw tool's `Execute(ctx, args)`
3. Forwards media attachments (images) via MessageBus
4. Returns text content and embedded resources as `mcpgo.CallToolResult`

### Media Forwarding

When a tool result contains images (base64), the bridge server:
1. Decodes the image data
2. Determines MIME type from extension
3. Creates `mcpgo.ImageContent` or `mcpgo.EmbeddedResource` 
4. Forwards via `bus.MediaAttachment` for streamable HTTP transport

---

## 3. Database Schema

Relevant migrations:
- `000084_mcp_oauth_tokens.up.sql` / `.down.sql` -- OAuth token storage
- `000023_agent_hard_delete_and_file_writer_merge` -- Agent-config permissions with `idx_acp_lookup` index

Key tables:
- `mcp_servers` -- Server name, transport type, command, args, env, URL, headers, settings (OAuth config, tool hints)
- `mcp_servers_access` -- Agent-server grant mappings (allow/deny)
- `mcp_oauth_tokens` -- OAuth access/refresh tokens per server+user
- `mcp_user_credentials` -- Per-user credential overrides for MCP servers

---

## 4. Configuration

```go
type MCPServerConfig struct {
    Name        string
    Transport   string              // "stdio" or "streamable-http"
    Command     string
    Args        []string
    Env         map[string]string
    URL         string
    Headers     map[string]string
    TimeoutSec  int
    Settings    json.RawMessage     // OAuth, tool_hints, require_user_credentials
}
```

Tool hints can provide global or per-tool prompt guidance to the LLM:

```go
type ToolHints struct {
    Global string            `json:"global,omitempty"`
    Tools  map[string]string `json:"tools,omitempty"`
}
```

---

## 5. Related Files

- `cmd/gateway_http_wiring.go` -- HTTP handler wiring including MCP handler and MCP pool
- `cmd/gateway_http_handlers.go` -- `wireHTTP()` creates `*httpapi.MCPHandler` with pool evictor and OAuth provider
- `internal/http/mcp.go` -- MCP REST API handler (CRUD for servers, grants, OAuth, tools)
- `internal/http/mcp_oauth.go` -- MCP OAuth token endpoints
- `internal/http/mcp_tools.go` -- MCP tool access listing
- `internal/http/mcp_grants.go` -- MCP grant (agent permission) CRUD
- `internal/http/mcp_export.go` / `mcp_import.go` -- MCP server export/import
- `internal/http/mcp_user_credentials.go` -- User credential management
- `internal/http/chat_completions.go` -- Chat completions endpoint that routes to agents
- `internal/agent/loop_lazy_mcp_test.go` -- Tests for lazy MCP tool activation
- `internal/agent/loop_mcp_user.go` -- MCP user-context tool loop integration
