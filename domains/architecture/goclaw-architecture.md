---
name: goclaw-architecture
description: "GoClaw enterprise AI agent gateway — multi-tenant architecture, 8-stage pipeline, Go internals"
tags: [goclaw, architecture, agent-gateway, go]
source: sources/goclaw/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# GoClaw Architecture
**Source:** `sources/goclaw/`

GoClaw is an enterprise AI agent gateway written in Go. Multi-tenant, PostgreSQL/SQLite-backed, with 22 provider types and 12 messaging channels. Designed as a faster, lighter alternative to [[openclaw]] and [[hermes-agent]], compiling to a ~25 MB static binary with <1s startup.

## Core Architecture

- **Language**: Go (1.26+, single binary, ~25 MB)
- **Database**: PostgreSQL 15+ with pgvector (production) or SQLite via `modernc.org/sqlite` (desktop/Lite edition)
- **API Surface**: REST API (`/v1/*`, OpenAI-compatible) + WebSocket (`/ws`, 64+ RPC methods)
- **Config**: JSON5 `config.json` with `env:` prefix for secrets, fsnotify hot-reload (300ms debounce)
- **Port**: 18790 (default)
- **Auth**: Bearer token, API keys, RBAC (admin/operator/viewer)
- **Docker Image**: `ghcr.io/nextlevelbuilder/goclaw:latest` (also Docker Hub `digitop/goclaw`)

## 8-Stage Agent Pipeline

The core of every agent interaction (`internal/pipeline/`). All agents always use this pipeline v3:

| Phase | Stage | Purpose |
|-------|-------|---------|
| **Setup** | ContextStage | Inject agent/user/workspace context; resolve per-user files |
| **Iteration** | ThinkStage | Build system prompt (15+ sections), call LLM, emit streaming |
| | PruneStage | Soft/hard context trim when ≥30%/≥50% full; trigger memory flush |
| | ToolStage | Execute tool calls (read-only in bounded parallel, others sequential) |
| | ObserveStage | Process tool results, handle silent completion |
| | CheckpointStage | Track iterations, check exit conditions |
| **Finalize** | FinalizeStage | 7-step output sanitization; flush messages; update session metadata |

The iteration loop runs up to `max_tool_iterations` (default 20) per turn. Pipeline is fully stateless — all mutable state lives in `RunState`, passed by pointer through stages.

## Key Architectural Components

### Gateway (`internal/gateway/server.go`)
HTTP + WebSocket server decomposed into 7 modules (deps, http_wiring, events, lifecycle, tools_wiring, methods, router). Uses `net.http.ServeMux` with standard library only (no framework). Rate limiting via `RateLimiter`, WS client management, method routing via `MethodRouter` (64+ RPC methods).

### Scheduler Lanes
Four semaphore-gated concurrency lanes: `main` (30), `subagent` (50), `team` (100), `cron` (30). Prevents cron from starving user messages.

### Provider Layer (`internal/providers/`)
22+ provider implementations via unified `Provider` interface. Covers Anthropic (native HTTP+SSE), OpenAI-compat (HTTP+SSE), Google Gemini, Groq, DeepSeek, Mistral, xAI, MiniMax, Cohere, Perplexity, DashScope (Qwen), Bailian, Zai, Ollama, Ollama Cloud, Claude CLI, ACP (JSON-RPC 2.0 stdio), Vertex AI, Suno, YesScale, Novita AI, Codex/ChatGPT. Each uses `RetryDo()` for retries; shared `SSEScanner` for streaming.

### ACP Provider (`internal/providers/acp/`)
Orchestrates Claude Code, Codex CLI, Gemini CLI as subprocesses via JSON-RPC 2.0 over stdin/stdout. Configurable permission modes (`approve-all`, `approve-reads`, `deny-all`), idle TTL, per-agent work dirs.

### Channel Layer (`internal/channels/`)
12 channel adapters translating platform-specific events to `InboundMessage`: Telegram (long polling), Discord (Gateway API), WhatsApp (native via whatsmeow v3), Slack (Socket Mode), Zalo OA, Zalo Personal, Feishu/Lark (WebSocket + webhook), Bitrix24 (webhook), Facebook (Graph API), Pancake (multi-platform proxy), WebSocket (direct RPC), Browser Pairing.

### Tool System (`internal/tools/`)
50+ built-in tools organized by category (filesystem, web search, browser, code execution, memory, knowledge graph, knowledge vault, vault, skills, subagent spawn, delegation, teams). Policy-based access control with per-agent allow/deny lists. `PolicyEngine` handles permission resolution, credential gating, and shell deny groups.

### MCP Integration (`internal/mcp/`)
Full Model Context Protocol client and server via `github.com/mark3labs/mcp-go`. `Manager` handles server lifecycle (connect, tool discovery, keepalive, reconnection with exponential backoff). Connection pooling for shared servers. OAuth 2.0 with DCR and token refresh. `BridgeTool` wraps MCP tools as GoClaw-native tools. BM25 search (`mcp_tool_search.go`) for lazy tool discovery.

### Memory System (`internal/memory/`)
3-tier with consolidation workers:
- **L0 (Working)**: Current conversation buffer, auto-injected into prompts
- **L1 (Episodic)**: Session summaries pushed by consolidation workers
- **L2 (Semantic)**: Abstracted facts with vector embeddings (pgvector)

Workers: episodic, semantic, dreaming, dedup — driven by `DomainEventBus`.

### Agent Teams (`internal/tools/team_tool_*.go`)
Task board with priorities, dependencies, blockers. Delegation modes (auto/explicit/manual). Task lifecycle (create, claim, complete, review). `BatchQueue[T]` for parallel wait aggregation.

### Knowledge Vault (`internal/vault/`)
Wikilink document mesh with LLM auto-summary + semantic auto-linking. Hybrid BM25 + vector search. L0 auto-injection into prompts. FS sync for external document management.

### Knowledge Graph (`internal/knowledgegraph/`)
LLM-powered entity/relationship extraction with graph traversal. Entities and relationships extracted from conversations at runtime.

### Hook System (`internal/hooks/`)
7 lifecycle events: SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Stop, SubagentStart, SubagentStop. Sync/async HTTP handlers. SSRF-hardened. Circuit breaker pattern. Audit logging.

### Store Layer (`internal/store/`)
Interface-based with dual-DB pattern. Shared `Dialect` interface in `store/base/`. PostgreSQL (`store/pg/`, `pgx/v5`) for production. SQLite (`store/sqlitestore/`, `modernc.org/sqlite`) for desktop. 71+ store types (session, agent, memory, team, cron, vault, etc.).

## Data Flow

```
User → Channel (Telegram/Discord/WS) → Gateway → Scheduler → Pipeline
→ Provider (LLM call) → Tools/MCP/Memory → Finalize → Channel → User
```

## Key Source Components

| File | Purpose |
|------|---------|
| `main.go` | Entry point |
| `internal/pipeline/pipeline.go` | 8-stage pipeline orchestrator |
| `internal/pipeline/stage.go` | Stage interface (stateless, RunState-based) |
| `internal/gateway/server.go` | HTTP/WS server, handler registration |
| `internal/gateway/router.go` | MethodRouter: 64+ RPC method dispatch |
| `internal/agent/loop.go` | Agent execution loop |
| `internal/agent/systemprompt.go` | System prompt builder (15+ sections) |
| `internal/providers/types.go` | Provider interface (22+ implementations) |
| `internal/providers/acp/` | ACP JSON-RPC 2.0 subprocess provider |
| `internal/tools/registry.go` | Tool registry with policy-based access |
| `internal/tools/policy.go` | Tool policy engine (allow/deny/credential) |
| `internal/mcp/manager.go` | MCP server lifecycle manager |
| `internal/mcp/bridge_tool.go` | BridgeTool wraps MCP tools as native tools |
| `internal/channels/channel.go` | Channel interface + adapters |
| `internal/memory/` | 3-tier episodic/semantic/dreaming memory |
| `internal/vault/` | Knowledge Vault with wikilinks + hybrid search |
| `internal/knowledgegraph/` | Entity/relationship graph extraction |
| `internal/hooks/` | 7 lifecycle event hooks |
| `internal/eventbus/domain_event_bus.go` | Typed event bus with worker pool |
| `internal/store/` | Dual-DB store layer (PG + SQLite) |
| `internal/config/config.go` | Config struct + JSON5 loading |
| `internal/scheduler/` | 4-lane concurrency scheduler |
| `internal/edition/edition.go` | Edition system (Lite/Standard) |
| `internal/sandbox/` | Docker-based code execution isolation |
| `internal/orchestration/batch_queue.go` | `BatchQueue[T]` generic for parallel waits |
| `pkg/protocol/` | Wire types (frames, methods, errors, events) |
| `ui/web/` | React/TypeScript SPA dashboard |
| `ui/desktop/` | Wails v2 desktop app (Lite edition) |

## Related

- [[goclaw]] — GoClaw wiki
- [[goclaw.codegraph-verify]] — Codegraph verification
- [[goclaw-mcp-implementation]] — MCP implementation details
- [[goclaw-api]] — REST API reference
- [[goclaw-acp-implementation]] — ACP agent protocol implementation
- [[goclaw-deployment]] — Deployment and operations
- [[openclaw-architecture]] — OpenClaw architecture (related Go→TS comparison)
- [[hermes-agent]] — Hermes Agent (competing agent platform)
- [[mcp]] — Model Context Protocol
- [[podman]] — Container runtime for deployment
