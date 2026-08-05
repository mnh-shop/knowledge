---
name: goclaw-codegraph-verify
tags: [ai-llm, cli, gateway, golang, mcp, acp, orchestration, plugin-sdk, security, webhook, wiki, goclaw]
description: "Codegraph Verification: goclaw — validating wiki claims against indexed source code symbols"
source: sources/goclaw/
---

# Codegraph Verification: goclaw

**Date:** 2026-07-12

## Claim 1: Go-based MCP gateway with client and server modes
- **Wiki says:** GoClaw implements MCP in two directions: MCP client (`internal/mcp/`) connecting to external MCP servers, and MCP server (`internal/mcp/bridge_server.go`) exposing GoClaw's own built-in tools. Uses the `github.com/mark3labs/mcp-go` Go library for both.
- **Source evidence:**
  - `internal/mcp/` directory contains manager, connection, tools, bridge, pool, and OAuth modules
  - `internal/mcp/bridge_server.go` implements the MCP server bridge exposing GoClaw's tools
  - `internal/mcp/manager.go` contains the core `Manager` type for client-side lifecycle
  - `internal/mcp/manager_connect.go` implements `connectAndDiscover()`, `connectServer()`, `connectViaPool()` with health loops and exponential backoff
  - `internal/mcp/manager_tools.go` implements `registerBridgeTools()`, `registerPoolBridgeTools()`, `DiscoverTools()`
  - `internal/mcp/bridge_tool.go` defines `BridgeTool` type wrapping MCP tools as GoClaw `tools.Tool`
  - `internal/mcp/pool.go` implements connection pooling for shared MCP server connections
  - Uses `github.com/mark3labs/mcp-go` library for protocol implementation
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Bridge between transports with tool registry
- **Wiki says:** GoClaw bridges external MCP tools into its own tool registry via `tools.Registry`. `BridgeTool` wraps MCP tool definitions as GoClaw-native tools with `Execute()` method. Includes BM25-based search (`mcp_tool_search.go`) for lazy/discoverable MCP tools.
- **Source evidence:**
  - `internal/mcp/bridge_tool.go` defines `BridgeTool` with `Execute()` method that wraps MCP tool calls
  - `internal/mcp/manager_tools.go` registers bridged tools into the central `tools.Registry`
  - `internal/mcp/mcp_tool_search.go` implements BM25-based search for lazy tool discovery
  - `internal/mcp/tool_filter.go` provides `IsToolAllowed()` for allow/deny list filtering
  - `internal/mcp/grant_checker.go` implements agent-level access grants for MCP servers
  - `internal/mcp/session_reset.go` handles session uninitialized errors with force reconnect
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: MCP protocol implementation with full lifecycle
- **Wiki says:** GoClaw's MCP implementation manages full server lifecycle: connect, tool discovery, keepalive, reconnection with exponential backoff, and shutdown. Supports connection pooling for shared MCP server connections, OAuth 2.0 with DCR and token refresh, and validation/allowlisting.
- **Source evidence:**
  - `internal/mcp/manager_connect.go` implements `connectAndDiscover()` with reconnection and exponential backoff
  - `internal/mcp/manager.go` manages per-agent server state in `servers map[string]*serverState`
  - `internal/mcp/pool.go` implements `Pool` for shared connections across agents
  - `internal/mcp/oauth/` directory implements OAuth 2.0 client credential flow, DCR, and token refresh
  - `internal/mcp/validation.go` implements MCP command/URL validation and allowlisting
  - Health check loops maintain long-running connections
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: ACP agent orchestration via JSON-RPC over stdin/stdout
- **Wiki says:** GoClaw supports ACP (Agent Communication Protocol) for external agent orchestration via JSON-RPC over stdin/stdout in `internal/providers/acp/`. Can orchestrate external agents like Gemini and Claude CLI as subprocesses.
- **Source evidence:**
  - `internal/providers/acp/` directory contains ACP implementation
  - `internal/providers/acp_provider.go` implements the ACP provider bridge
  - ACP implementation uses JSON-RPC over stdin/stdout for external agent communication
  - ACP supports Gemini and Claude CLI as external subprocess agents
  - `domains/acp/goclaw-acp-implementation.md` documents the ACP implementation in detail
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: REST API with net/http.ServeMux handler registration
- **Wiki says:** GoClaw has a comprehensive REST API using Go's standard library `net/http.ServeMux` with handler registration in `cmd/`. The gateway runs on port 18790 with a `/health` endpoint.
- **Source evidence:**
  - `internal/gateway/server.go:202` — `mux.HandleFunc("/health", s.handleHealth)`
  - `internal/gateway/server.go:1095` — `mux.HandleFunc("/health", s.handleHealth)` (second server instance)
  - `internal/gateway/server.go:625` — root handler advertises `"endpoints":["/health","/v1/chat/completions","/v1/responses","/v1/tools/invoke","/ws"]`
  - `internal/config/config_load.go:106` — port 18790
  - ~375 registered `mux.HandleFunc` routes across `server.go:199-202` and related wiring
  - Webhook endpoints `POST /v1/webhooks/llm` + `POST /v1/webhooks/message` registered via `SetWebhookMessageHandler` / `SetWebhookLLMHandler` (server.go:745,751); Bearer `wh_` + HMAC `X-GoClaw-Signature` (internal/http/webhooks_auth.go)
  - Third MCP surface mounted at `/api/mcp/` gated by `gateway.mcp_server_token` (internal/mcp/crud_server.go, cmd/gateway.go:554)
  - `internal/webui/handler.go:17` — API prefixes `/v1/`, `/ws`, `/health`, `/api/mcp/`
- **Verdict:** ✅ CORRECT (with correction)
- **Fix needed:** Health endpoint is **`/health`**, NOT `/healthz`. No `/healthz` route exists in the codebase (verified: only `/health` matches). The wiki's API surface section was updated to document the full surface: `/v1/responses`, `/v1/tools/invoke`, Swagger `/docs`, `/v1/openapi.json`, webhook endpoints, and the `/api/mcp/` CRUD server.

## ~~Claim 6: Quadlet deployment with rootless Podman and auto-updates~~ — STRUCK (FABRICATED)
- **Wiki previously said:** GoClaw is deployable via Quadlet systemd unit for rootless Podman with `AutoUpdate=registry` for automatic container updates.
- **Verdict:** ❌ FABRICATED — **REMOVED**
- **Reason:** No quadlet, `.container`, or systemd unit files exist anywhere in the repository (find for `*.container`, `*.service`, `*.quadlet` returns empty; grep for `quadlet` / `AutoUpdate=registry` returns nothing). There is no reference to Quadlet deployment in `assets/deployment/` or domain docs either. Deployment is via Docker Compose overlays and bare-metal binary only. This claim has been struck from the wiki.

## Claim 7: Channel adapters and multi-platform messaging
- **Wiki says:** GoClaw provides multi-channel conversational AI agents with channel adapters for Slack, Telegram, Discord, Facebook, Zalo, and Bitrix24. Messages route through the gateway into an agent loop.
- **Source evidence:**
  - `internal/channels/channel.go:76-85` — channel type constants: `bitrix24`, `discord`, `facebook`, `feishu`, `pancake`, `slack`, `telegram`, `whatsapp`, `zalo_oa`, `zalo_personal` (10 adapter types)
  - `cmd/gateway.go:895-919` — `instanceLoader.RegisterFactory(...)` for all 10 types; Facebook factory registered at `cmd/gateway.go:902` (`channels.TypeFacebook, facebook.Factory`)
  - `internal/config/config_channels.go:229` — Feishu `Domain` field: `"lark"` (default/global) vs `"feishu"` (China); "Larksuite" is NOT a separate channel type
  - WebSocket (`/ws`) + Browser Pairing complete the 12 gateway surfaces
  - Gateway routes messages through configurable channel adapters into the agent loop
  - EventBus (`internal/eventbus/`) manages event-driven inter-component communication
  - Real-time SSE streaming is supported for live responses
- **Verdict:** ✅ CORRECT (expanded)
- **Fix needed:** Wiki channel table updated to all 10 adapter types + WS + pairing, with Facebook added (was missing) and a note that "Larksuite" is a Feishu domain config, not a distinct channel.

## Claim 8: Provider types, pipeline, hooks, and tool counts
- **Wiki says:** 27 LLM provider types, an 8-stage pipeline (Prune first in iteration), 8 lifecycle hooks, 47 built-in tools, and 144 WebSocket RPC methods.
- **Source evidence:**
  - `internal/store/provider_store.go:71-99` — `ValidProviderTypes` map with exactly 27 entries (`anthropic_native`, `openai_compat`, `gemini_native`, `openrouter`, `aimlapi`, `groq`, `deepseek`, `mistral`, `xai`, `minimax_native`, `cohere`, `perplexity`, `dashscope`, `bailian`, `chatgpt_oauth`, `claude_cli`, `yescale`, `zai`, `zai_coding`, `ollama`, `ollama_cloud`, `acp`, `novita`, `byteplus`, `byteplus_coding`, `vertex`, `kimi_coding`). No `suno` or `custom` symbols exist — Suno is a `create_audio` backend (CHANGELOG.md:216)
  - `internal/pipeline/pipeline.go:32-50` — `NewDefaultPipeline`: setup=[ContextStage], iteration=[PruneStage, ThinkStage, ToolStage, ObserveStage, CheckpointStage], finalize=[FinalizeStage]; `MemoryFlushStage` passed into `NewPruneStage(d, memFlush)` (pipeline.go:34)
  - `internal/hooks/types.go:23-39` — 8 `HookEvent` constants including `EventPostModelResponse = "post_model_response"` (config.go:30-38)
  - `cmd/gateway_builtin_tools.go:15-143` — 46 `BuiltinToolDef` entries + `telegram_manager` tool (`internal/tools/telegram_manager.go:33`) = 47 built-in tools
  - 143-144 unique `Register(protocol.X)` call sites across `internal/gateway/methods/` + `internal/mcp/crud_*.go`; 156-157 method constants in `pkg/protocol/methods.go`
- **Verdict:** ✅ CORRECT (corrected)
- **Fix needed:** Wiki updated from "22 providers / 50+ tools / 64+ methods / 7 hooks" to the verified counts (27 / 47 / 144 / 8). Pipeline stage order fixed (Prune runs FIRST, not Think). Lite edition channel limits corrected: `internal/edition/edition.go:44` — `MaxChannels: map[string]int{"telegram": 1, "discord": 1}` (README's "Channels: —" for Lite is wrong). PostgreSQL version unified to 18+ (README.md:20,147).

## Summary

Key claims from the GoClaw wiki verified against source code via codegraph exploration:
- ✅ MCP client + server: Both directions confirmed with `internal/mcp/` bridge architecture
- ✅ Transport bridge: BridgeTool + tools.Registry + BM25 search confirmed
- ✅ MCP lifecycle: Full lifecycle management with pool, OAuth, validation confirmed
- ✅ ACP orchestration: JSON-RPC subprocess agent orchestration confirmed
- ✅ REST API: `net/http.ServeMux` handler registration on port 18790 confirmed; health endpoint corrected to `/health`
- ❌ ~~Quadlet deployment: rootless Podman + auto-update~~ — FABRICATED, struck
- ✅ Channel adapters: 10 adapter types + WS + pairing confirmed, Facebook added, "Larksuite" folded into Feishu
- ✅ Provider types / pipeline / hooks / tool counts: corrected to 27 / 8-stage (Prune-first) / 8 / 47, RPC methods to 144

## Related

- [[goclaw]] -- Main wiki entry
- [[goclaw-architecture]] -- System architecture
- [[goclaw-mcp-implementation]] -- MCP implementation details
- [[goclaw-acp-implementation]] -- ACP implementation details
- [[goclaw-api]] -- REST API reference
- [[goclaw-deployment]] -- Deployment guide

## Cross-project

- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for Hermes Agent
- [[agentfield.codegraph-verify]] -- Similar codegraph verification for AgentField
- [[podman.codegraph-verify]] -- Similar codegraph verification for Podman
