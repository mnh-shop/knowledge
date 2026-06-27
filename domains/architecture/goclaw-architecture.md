---
name: goclaw-architecture
description: "GoClaw architecture -- Go agent orchestration platform with tool bridge, webhooks, SSE streaming, MCP client/server"
tags: [architecture, goclaw, golang, orchestration]
source: sources/goclaw/
---

# GoClaw Architecture

## Overview

GoClaw is a Go-based agent orchestration platform providing multi-channel conversational AI agents with MCP (Model Context Protocol) tool integration, real-time SSE streaming, webhook provisioning, and audio processing. The platform exposes a unified gateway that routes messages through configurable channel adapters (Slack, Telegram, Discord, Facebook, Zalo, Bitrix24) into an agent loop that can invoke tools from external MCP servers, execute built-in capabilities, and produce streaming responses.

## High-Level Component Structure and Layers

```
+----------------------------------------------------------+
|                    UI Layer (Desktop + Web)                |
|  ui/desktop/ (Wails + React frontend)                     |
|  ui/web/ (React/TypeScript SPA)                           |
+----------------------------------------------------------+
                              |
+----------------------------------------------------------+
|                  Gateway / HTTP Layer                      |
|  cmd/gateway.go -- runGateway entry point                 |
|  internal/gateway/server.go -- Server (HTTP, WebSocket)   |
|    - MCP handler, OAuth, Webhook admin/message/LLM        |
|    - Channel instances, Providers, Secure CLI             |
|    - API keys, File upload, Health, Index                 |
|    - Gateway upgrade (Wails desktop IPC bridge)           |
+----------------------------------------------------------+
         |         |         |           |
         v         v         v           v
+-------------+ +-----------+ +--------+ +--------------+
|Channel Layer| |Agent Loop | |EventBus| | Skills Layer |
| Slack,Tele  | | internal/ | |internal/| | Python-based |
| Discord,FB  | | agent/    | |eventbus| | skills/     |
| Zalo,Bitrix | | loop_types| |domain  | | dep_install  |
+------+------+ +-----+-----+ +--------+ +--------------+
       |              |
       v              v
+-------------+ +--------------+ +-------------------+
| MCP Layer   | | Provider     | | Audio Layer       |
| internal/mcp| | Layer        | | internal/audio/   |
| - Manager   | | internal/    | | - TTS/STT (Edge,  |
| - BridgeTool| | providers/   | |   Gemini, MiniMax,|
| - Search    | | - Vertex AI  | |   OpenAI, Eleven) |
| - BM25Index | | - ACP        | +-------------------+
+-------------+ +--------------+
```

## Directory Structure

```
goclaw/
  main.go                          # Root entry point
  cmd/
    gateway.go                     # Gateway server bootstrap (runGateway)
    gateway_deps.go                # Gateway dependency list
    gateway_http_client.go         # HTTP client helpers
    gateway_providers.go           # Provider registration (ACP, Claude CLI, Vertex)
    pkg-helper/
      main.go                      # Package management helper (Unix socket IPC)
      main_windows.go              # Windows variant
  internal/
    config/
      config.go                    # Core Config struct, Clone, ReplaceFrom
      config_channels.go           # Channel-specific configs (Slack, Zalo, ACP, TTS, Quota)
      config_audio.go              # Audio configuration
    gateway/
      server.go                    # HTTP/WS Server with all handler registrations
      router.go                    # Router wiring
      server_test.go               # Gateway tests
    agent/
      loop_types.go                # Loop struct -- main agent execution loop
      toolloop.go                  # Tool execution sub-loop
      systemprompt.go              # System prompt generation
      systemprompt_sections.go     # Context section builders (project, etc.)
    tools/
      types.go                     # Tool, ContextualTool, AsyncTool interfaces
      team_tool_manager.go         # Team-level tool management
      subagent_spawn_tool.go       # Subagent spawning tool
      workspace_resolver.go        # Workspace/project/team/user resolution
    mcp/
      manager.go                   # MCP Manager -- server lifecycle, connection, filtering
      bridge_tool.go               # BridgeTool -- wraps MCP tool as agent Tool
      bridge_server.go             # Bridge server for MCP
      mcp_tool_search.go           # MCPToolSearchTool -- search/filter over MCP tools
      manager_tools.go             # ToolInfo, DiscoverTools -- MCP tool discovery
      bm25_index.go                # BM25-ranked search index for MCP tools
    providers/
      types.go                     # Provider interface (LLM abstraction)
      registry.go                  # Provider registry (singleton, per-tenant registration)
      vertex.go                    # Vertex AI provider
      acp/
        helpers.go                 # ACP session context helpers
        session.go                 # ACP session management
        tool_bridge.go             # ToolBridge -- ACP tool bridge
      acp_provider.go              # ACP LLM provider (Chat, ChatStream)
      capabilities.go              # Provider capability descriptors
    channels/
      channel.go                   # Core Channel, StreamingChannel, WebhookChannel interfaces
      quota.go                     # Rate limiting / quota enforcement
      slack/
        channel.go                 # Slack channel adapter
        stream.go                  # Slack SSE stream integration
        factory.go                 # Slack factory
      telegram/
        channel.go                 # Telegram channel adapter
      discord/
        discord.go                 # Discord channel adapter
      facebook/
        facebook.go                # Facebook Messenger adapter
      zalo/
        personal/channel.go        # Zalo personal channel adapter
      bitrix24/
        channel.go                 # Bitrix24 channel adapter
    audio/
      types.go                     # Audio interfaces (STTProvider, TTSProvider)
      types_capabilities.go        # Audio capability descriptors
      edge/tts.go                  # Edge TTS provider
      gemini/tts.go                # Gemini TTS provider
      minimax/tts.go               # MiniMax TTS provider
      openai/tts.go                # OpenAI TTS provider
      elevenlabs/                   # ElevenLabs TTS + STT
      proxy_stt/provider.go        # Proxy STT provider
    http/
      tools_invoke.go              # ToolsInvokeHandler -- HTTP tool invocation
      gateway_upgrade.go           # Desktop gateway upgrade runner
      mcp_tools.go                 # MCP tool HTTP handlers
    eventbus/
      domain_event_bus.go          # Domain event bus infrastructure
    hooks/
      builtin/seed.go              # Built-in hook seeding
    store/
      pg/                          # PostgreSQL store
    skills/
      package_lister.go            # Installed package listing (pip, npm, apk)
      dep_installer.go             # Dependency installer (calls pkg-helper)
      system_package_records.go    # System package record tracking
    tracing/
      snapshot_worker.go           # Tracing snapshot loop
  ui/
    desktop/
      main.go                      # Desktop app entry point
      app.go                       # Desktop App struct (Wails lifecycle)
      frontend/                    # React/TypeScript frontend
    web/                           # Web UI (React/TypeScript SPA)
  skills/
    skill-creator/scripts/
      run_eval.py                  # Skill evaluation runner
      run_loop.py                  # Skill loop runner
    _shared/office/
      validate.py                  # Office document validation
```

## Build System

- **Language**: Go (module-based). The `go.mod` file at the repo root defines the Go module.
- **Desktop App**: Uses the Wails framework (`ui/desktop/app.go`) to bundle the Go backend with a React/TypeScript frontend (`ui/desktop/frontend/`). The `App` struct manages the desktop application lifecycle (startup, shutdown, update checking, gateway process management).
- **Web UI**: Separate React/TypeScript application in `ui/web/`.
- **Package Helper**: A separate binary (`cmd/pkg-helper/main.go`) communicates via Unix domain sockets. It handles package installation, removal, upgrades, and index updates for skills dependencies. Uses APK on Alpine-based systems.
- **Document Validation**: Python scripts in `skills/_shared/office/` handle DOCX/PPTX schema validation.
- **Testing**: Standard Go `_test.go` files; integration tests in `tests/integration/`.

## Configuration (config.yaml)

Configuration is parsed into the `Config` struct defined at `internal/config/config.go:45` with cloning and replacement support (methods `Clone`, `ReplaceFrom`, `ShellDenyGroupsSnapshot`). Config is split across multiple files by domain:

### Core Config (`internal/config/config.go`)
- `Config` -- top-level struct with all sub-configs embedded
- `HooksConfig` (line 106) -- hook event subscriptions and pipeline configuration
- `CronConfig` (line 477) -- scheduled job configuration with timeout settings (`JobTimeoutDuration`, `CommandTimeoutDuration`, `ToRetryConfig`)
- Replace/Clone helper methods for hot-reload

### Channel Configs (`internal/config/config_channels.go`)
- `SlackConfig` (line 158) -- Slack app credentials, workspace configuration
- `ZaloConfig` (line 191) -- Zalo messenger integration
- `ACPConfig` (line 300) -- Adobe Commerce Platform configuration
- `QuotaConfig` (line 404) -- Rate limiting and usage quotas
- `TtsConfig` (line 564) -- TTS provider settings (voice, model, credentials)

### Audio Config (`internal/config/config_audio.go`)
- `AudioConfig` (line 10) -- Audio system configuration (provider selection, default parameters)

The config system supports hot-reload via a `ReplaceFrom` method that swaps configs atomically. The `ShellDenyGroupsSnapshot` method captures a snapshot of shell deny-group rules for consistent policy enforcement across reloads.

## Tool Bridge Management

The tool system is built around a layered abstraction:

### Core Tool Interface (`internal/tools/types.go:14`)
```go
interface Tool {
    Name() string
    Description() string
    Parameters() json.RawMessage
    Execute(ctx, params) (result, error)
}
```
Extended by:
- `ContextualTool` -- adds context-awareness for tool execution
- `AsyncTool` -- supports long-running tool execution with progress callbacks

### MCP Tool Bridge (`internal/mcp/bridge_tool.go:40`)
`BridgeTool` wraps a remote MCP server tool as a local `Tool`. Key capabilities:
- `Name()`, `Description()`, `Parameters()` -- delegates to the MCP tool definition
- `Execute()` -- calls the remote MCP server to execute the tool
- `WithForceReconnect()` -- forces reconnection to the MCP server before execution
- `WithHints()` -- attaches search/discovery hints to the bridge tool
- `ServerName()`, `OriginalName()` -- preserves original server/tool identity
- `IsConnected()` -- checks connectivity status
- `stripEmptyOptionalArgs()`, `propertyType()` -- parameter normalization helpers

### ACP Tool Bridge (`internal/providers/acp/tool_bridge.go:18`)
`ToolBridge` provides tool bridge integration specifically for Adobe Commerce Platform:
- `NewToolBridge()` -- creates a new bridge instance
- `Handle()` -- routes tool calls to ACP
- `readFile()`, `writeFile()` -- file I/O helpers for ACP tool data

### MCP Manager (`internal/mcp/manager.go:98`)
The `Manager` struct is the central MCP server lifecycle manager:

```go
struct Manager {
    ManagerOption options (WithConfigs, WithStore, WithPool, WithGrantChecker, WithOAuthTokenProvider)
}
```

Key methods:
- `NewManager()` -- creates manager with dependency injection options
- `Start()` -- boots the MCP server management loop
- `connectAndFilter()` -- connects to MCP servers and filters tools by permissions
- `LoadForAgent()` -- loads MCP tools for a specific agent context
- `ActivateTools()` / `ActivateToolIfDeferred()` -- lazy activation of MCP tools
- `ServerStatus()` -- status of connected MCP servers
- `DeferredToolInfos()` -- returns deferred tool info for lazy loading
- `IsSearchMode()` / `maybeEnterSearchMode()` -- BM25 search toggling
- `Stop()` -- graceful shutdown of all MCP connections
- `DiscoverTools()` -- builds `ToolInfo` structs from MCP server responses (`manager_tools.go`)
- `resolveServerCredentials()` -- credential resolution per MCP server

### Tool Discovery (`internal/mcp/manager_tools.go:111`)
`ToolInfo` and `DiscoverTools` provide MCP tool discovery, listing available tools from all registered MCP servers.

### MCP Tool Search (`internal/mcp/mcp_tool_search.go:16`)
`MCPToolSearchTool` provides BM25-ranked search across available MCP tools:
- `rebuildIndex()` -- rebuilds the search index from tool descriptions
- `Execute()` -- runs a search query against the tool index

### Built-in Tools (`internal/tools/subagent_spawn_tool.go:16`)
`SpawnTool` allows the agent to spawn sub-agents:
- `executeSpawn()` -- spawns a new agent instance
- `executeSubagentAsync()` -- runs a sub-agent asynchronously

### Team Tool Management (`internal/tools/team_tool_manager.go:30`)
`TeamToolManager` provides team-level tool backend management, implementing `TeamToolBackend`.

## Webhook Provisioning

Webhook support is baked into the gateway server at multiple levels:

### Gateway Webhook Handlers (`internal/gateway/server.go`)
The `Server.BuildMux()` registers:
- `SetWebhooksAdminHandler()` (line 548) -- administrative webhook CRUD operations
- `SetWebhookMessageHandler()` (line 554) -- handles incoming webhook message delivery
- `SetWebhookLLMHandler()` (line 561) -- LLM-triggered webhook callbacks

### Channel Webhook Integration
The `WebhookChannel` interface (`internal/channels/channel.go:184`) extends the base `Channel` interface:
```go
interface WebhookChannel extends Channel {
    WebhookHandler() http.Handler
}
```
Implemented by channel adapters that support webhook-based message delivery:
- `internal/channels/bitrix24/channel.go:290` (`WebhookHandler`) -- Bitrix24 webhook handler
- `internal/channels/slack/channel.go` -- Slack Events API via webhooks
- `internal/channels/telegram/channel.go` -- Telegram bot webhook
- `internal/channels/discord/discord.go` -- Discord interactions webhook
- `internal/channels/facebook/facebook.go` -- Facebook Messenger webhook
- `internal/channels/zalo/personal/channel.go` -- Zalo webhook

Each channel implements `provisionIfMissing()` (called from the message handling flow) to auto-provision webhook subscriptions when a channel is activated.

### Hook System (`internal/config/config.go:106`)
`HooksConfig` defines event subscriptions and pipeline configuration for hook-driven webhook actions, including seed data for built-in hooks (`internal/hooks/builtin/seed.go`).

## SSE Streaming

SSE streaming is provided through the `StreamingChannel` interface and per-channel stream implementations.

### StreamingChannel Interface (`internal/channels/channel.go:115`)
```go
interface StreamingChannel extends Channel {
    CreateStream(ctx, msgID) (StreamWriter, error)
    FinalizeStream(ctx, msgID) error
    ReasoningStreamEnabled(ctx) bool
}
```

### Stream Support by Channel
- **Slack** (`internal/channels/slack/stream.go:72`) -- `StreamEnabled()` method with per-channel stream configuration
- **Telegram** (`internal/channels/telegram/channel.go:352`) -- `StreamEnabled()` returns streaming capability
- **All channels** that implement `StreamingChannel` can deliver real-time streaming responses.

The `StreamEnabled()` method (base at `internal/channels/channel.go:126`) is the query point that the agent loop checks before deciding whether to stream responses.

### Desktop Streaming
The Wails desktop app (`ui/desktop/app.go`) also bridges streaming responses from the gateway to the desktop frontend via WebSocket or Wails runtime events.

## MCP Client/Server Integration

### MCP Manager -- Client Side (`internal/mcp/manager.go:98`)
The `Manager` acts as an MCP **client** that connects to external MCP servers and exposes their tools as local tools:
- Connects to MCP servers defined in configuration
- Resolves credentials per server (OAuth tokens, API keys)
- Filters tools by grant/permission policies
- Supports lazy activation (deferred loading until first use)
- Integrates with BM25 search for tool discovery
- Manages connection lifecycle (connect, reconnect, stop)
- `Implements`: `gatewayUpgradeRunner`, `MCPToolLister`

### BridgeTool -- Server Adapter (`internal/mcp/bridge_tool.go:40`)
`BridgeTool` adapts a remote MCP server's tool into the local `Tool` interface:
- Preserves the original MCP tool name and server identity
- Handles parameter schema translation (MCP JSON Schema to internal)
- Supports force-reconnect for stale connections
- Validates and strips empty optional arguments before sending

### MCP Tool Search (`internal/mcp/mcp_tool_search.go:16`)
`MCPToolSearchTool` provides a built-in search across all available MCP tools using a BM25 ranking algorithm (`internal/mcp/bm25_index.go:45`). This allows agents to discover and filter relevant tools dynamically during execution.

### ACP Provider Integration (`internal/providers/acp_provider.go`)
The ACP provider implements MCP-style tool bridges for the Adobe Commerce Platform, with session management (`internal/providers/acp/session.go`) and tool call routing (`internal/providers/acp/tool_bridge.go`).

## Agent Loop

### Main Loop (`internal/agent/loop_types.go:74`)
The `Loop` struct is the core agent execution engine:
- Implements the `Agent` interface (`deliveryPersonaProvider`, `agentUUIDProvider`)
- Manages conversation turns, tool calls, and response generation
- `NewLoop()` -- constructor with dependency injection
- `effectiveMaxTokens()`, `resolveReserveTokens()` -- token budget management

### Tool Loop (`internal/agent/toolloop.go:61`)
The `toolLoopState` manages tool execution within the agent loop:
- `record()`, `recordResult()` -- tracks tool call history
- `detect()` -- detects tool patterns in model responses

### System Prompt Building
- `internal/agent/systemprompt.go:233` (`BuildSystemPrompt`) -- constructs the system prompt from sections, personas, and context
- `internal/agent/systemprompt_sections.go:392` (`buildProjectContextSection`) -- adds project/workspace context

## Provider Layer

### LLM Provider Interface (`internal/providers/types.go:53`)
```go
interface Provider {
    Name() string
    // Provider-specific chat completion methods
}
```
Extended by `STTProvider`, `TTSProvider`, `DescribableProvider`, `CapabilitiesAware`.

### Provider Registry (`internal/providers/registry.go:19`)
The `Registry` struct manages provider lifecycle:
- `Register()` -- registers a provider linked to a tenant or globally
- `RegisterForTenant()` -- tenant-scoped registration
- `MasterTenantID` -- singleton constant for global providers

### Supported Providers
- **Vertex AI** (`internal/providers/vertex.go`) -- Google Vertex AI integration (model, project, region validation)
- **ACP** (`internal/providers/acp_provider.go`) -- Adobe Commerce Platform provider (Chat, ChatStream)
- **Claude CLI** (`cmd/gateway_providers.go:443`) -- Claude CLI invocation
- Provider capabilities are described via `CapabilitiesAware` (`internal/providers/capabilities.go:21`)

### Audio Providers (`internal/audio/`)
- **Edge TTS** (`internal/audio/edge/tts.go`)
- **Gemini TTS** (`internal/audio/gemini/tts.go`)
- **MiniMax TTS** (`internal/audio/minimax/tts.go`)
- **OpenAI TTS** (`internal/audio/openai/tts.go`)
- **ElevenLabs** (TTS + STT)
- **Proxy STT** (`internal/audio/proxy_stt/provider.go`)

## Event Bus (`internal/eventbus/domain_event_bus.go:28`)

The domain event bus provides decoupled pub/sub for internal events, with `Config` for event type filtering and subscription management.

## Skills System (`internal/skills/`)

- `package_lister.go:38` (`InstalledPackages`, `ListInstalledPackages`) -- lists system/user installed packages (pip, npm, apk, debian)
- `dep_installer.go:354` (`pkgHelperResponse`, `parsePkgHelperResponse`) -- dependency installation bridge to the pkg-helper binary
- `system_package_records.go` -- persistent tracking of installed system packages

## Desktop Application (`ui/desktop/`)

The `App` struct (`ui/desktop/app.go:24`) wraps the Go backend in a Wails desktop application:
- `startup()`, `shutdown()` -- lifecycle hooks
- `startGateway()` -- spawns the gateway process as a child
- `waitForGateway()` -- health-check polling
- `GetGatewayURL()`, `GetGatewayToken()` -- IPC bridge to gateway
- `CheckForUpdate()`, `ApplyUpdate()` -- auto-update mechanism
- `ResetDatabase()` -- data reset
- `DownloadURL()` -- file download capability
- `updateLoop()`, `checkAndEmitUpdate()` -- background update monitoring

## Key Data Flow

```
1. External message arrives via Channel webhook or WebSocket
2. Gateway Server routes to channel adapter (internal/channels/)
3. Channel adapter converts to internal message format
4. Message enters Agent Loop (internal/agent/loop_types.go)
5. Loop builds system prompt (internal/agent/systemprompt.go)
6. Loop invokes LLM Provider (internal/providers/) for response
7. LLM may request tool calls -- routed through tool loop (toolloop.go)
8. Tool calls pass to MCP Manager (internal/mcp/manager.go)
9. Manager dispatches to BridgeTool (internal/mcp/bridge_tool.go) for remote MCP servers
10. Results stream back through channels via SSE (StreamingChannel.CreateStream)
11. Gateway relays streamed response to the external channel
```

## Testing

- Unit tests are co-located with source files (`*_test.go`)
- Integration tests in `tests/integration/`
- Mock servers and helpers for testing gateway/server interactions
- Config-level fuzz testing for channel factory behaviors
- Audio provider golden tests for response consistency
- BM25 search index tests for MCP tool search quality

## Related

- [[architecture]]
- [[goclaw]]
- [[podman]]
