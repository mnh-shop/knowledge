---
name: goclaw
tags: [ai-llm, cli, container, gateway, golang, mcp, acp, orchestration, plugin-sdk, security, systemd, webhook, wiki, goclaw]
description: "GoClaw — Go-based enterprise AI agent gateway with multi-tenant isolation, 27 LLM providers, 12 messaging channels, and 47 built-in tools"
source: sources/goclaw/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# GoClaw — Enterprise AI Agent Gateway

| Field | Value |
|---|---|
| **Origin** | [nextlevelbuilder/goclaw](https://github.com/nextlevelbuilder/goclaw) |
| **License** | CC BY-NC 4.0 (README.md:369) |
| **Stack** | Go 1.26 (go.mod:3), PostgreSQL 18+ with pgvector, SQLite (desktop), WebSocket RPC, React 19 SPA |
| **Version** | v3.15.0-beta.181 |
| **Container** | `ghcr.io/nextlevelbuilder/goclaw:latest` |
| **Port** | 18790 (config_load.go:106) |
| **Binary Size** | Single static Go binary with <1s startup (the ~25 MB figure is a marketing claim, not a guaranteed size) |
| **Documentation** | [docs.goclaw.sh](https://docs.goclaw.sh/) |

## What It Is

GoClaw is an **open-source enterprise AI agent gateway** written in Go. It connects LLM providers to messaging channels (Telegram, Discord, WhatsApp, Slack, Zalo, Feishu, Facebook, Pancake, Bitrix24) and provides 47 built-in tools, multi-tenant isolation, agent teams, knowledge management, and a full web dashboard — all as a single Go binary that starts quickly.

It is a production-tested alternative to [[openclaw]] (TypeScript) and [[hermes-agent]] (Python), with a focus on performance, low resource footprint, and an 8-stage agent pipeline.

## Key Features

| Category | What GoClaw Provides |
|----------|----------------------|
| **Multi-Tenant v3** | Per-user isolation for context, sessions, memory, traces; RBAC with admin/operator/viewer roles; compound `tenant.{id}.user.{id}` identity model |
| **8-Stage Pipeline** | Setup: Context → Iteration: Prune → Think → Tool → Observe → Checkpoint → Finalize: Finalize; plus MemoryFlushStage injected into Prune. Pluggable stages with always-on execution |
| **27 Provider Types** | Anthropic, OpenAI-compatible, Gemini, OpenRouter, AIMLAPI, Groq, DeepSeek, Mistral, xAI, MiniMax, Cohere, Perplexity, DashScope (Qwen), Bailian, ChatGPT OAuth, Claude CLI, YesScale, ZAI, ZAI Coding, Ollama (local), Ollama Cloud, ACP, Novita AI, BytePlus, BytePlus Coding, Vertex AI, Kimi Coding |
| **ACP Provider** | Orchestrates Claude Code, Codex CLI, Gemini CLI as subprocess agents via JSON-RPC 2.0 over stdio |
| **12 Gateway Surfaces** | 10 channel adapters (Telegram, Discord, WhatsApp, Zalo OA, Zalo Personal, Slack, Feishu/Lark, Facebook, Pancake, Bitrix24) + WebSocket + Browser Pairing |
| **47 Built-in Tools** | 46 in `builtinToolSeedData()` + `telegram_manager`; filesystem, web, memory, vault, media, browser, sessions, messaging, scheduling, subagents, skills, teams (README advertises "30+"; composite `goclaw` group lists 42) |
| **144 WebSocket RPC Methods** | Real-time control via `/ws` — chat, agents, sessions, traces, config, skills, cron, pairing, teams (×22), tenants (×8), workstations (×14), hooks (×7), api_keys (×3), bitrix.portals (×4), usage, tts, run.timeline (157 constants in `pkg/protocol/methods.go`) |
| **3-Tier Memory** | L0 (working/conversation) → L1 (episodic/session summaries) → L2 (semantic/knowledge graph); 4 consolidation workers (episodic, semantic, dreaming, dedup) |
| **Knowledge Vault** | Document registry with `[[wikilinks]]` for bidirectional linking; hybrid BM25 + pgvector search; filesystem sync |
| **Knowledge Graph** | LLM-powered entity/relationship extraction with graph traversal |
| **Agent Teams** | Lead + member agents with shared task board, inter-agent delegation (sync/async), handoff, 3 orchestration modes (sequential/iterative/mixed) |
| **Hooks System** | 8 lifecycle events: SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PostModelResponse, Stop, SubagentStart/SubagentStop; sync/async, SSRF-hardened HTTP handlers, audit logging |
| **MCP Integration** | Connect to any MCP server (stdio/SSE/HTTP); expose GoClaw tools as an MCP server via bridge; third surface: CRUD MCP server at `/api/mcp/` |
| **Skills System** | SKILL.md-based knowledge packages with BM25 + semantic hybrid search; publishing, grants, evolution-driven drafts |
| **Agent Evolution** | 3-stage guardrailed pipeline: metrics → suggestion analysis → auto-adaptation; agents refine SOUL.md/CAPABILITIES.md without changing identity |
| **Extended Thinking** | Per-provider reasoning modes (Anthropic, OpenAI, DashScope); streaming support |
| **Prompt Caching** | v3 cache-boundary markers and cost reduction on repeated prefixes (the "~90%" figure is a marketing claim) |
| **4-Mode Prompt System** | Full / Task / Minimal / None with section gating, cache boundary optimization, per-session mode resolution |
| **Single Binary** | Static Go binary, no Node.js runtime, fast startup, runs on a small VPS |
| **Dual-DB** | PostgreSQL 18+ with pgvector (full multi-tenant production); SQLite (desktop/lite, single-user) via unified store Dialect pattern |
| **Web Dashboard** | React 19 SPA (Vite, Tailwind CSS, Radix UI, Zustand) for visual agent/provider/channel/vault management |
| **Desktop Edition** | Wails v2 native app (~30 MB) with SQLite, chat UI, Kanban board, auto-update; max 5 agents, 1 team (5 members), 1 Telegram + 1 Discord channel |
| **Observability** | Built-in LLM call tracing with spans and prompt cache metrics; optional OpenTelemetry OTLP export via Jaeger |
| **Security** | Rate limiting, SSRF protection, prompt injection detection, credential scrubbing, RBAC, AES-256-GCM encryption, session IDOR hardening |
| **i18n** | en/vi/zh message catalogs; WS `connect` locale param + HTTP `Accept-Language` header |
| **Credentialed Exec** | git/gh/gcloud/kubectl/terraform/psql/AWS/GWS credential adapters; credentials injected via exec env, never exposed to LLM |
| **Workstations** | Remote allowlisted exec + audit trail (Standard-only) |

## Architecture

GoClaw follows a **modular layered architecture** with a Go backend, WebSocket/HTTP gateways, and a React frontend.

```
                          ┌──────────────┐
  Telegram ──────────────▶│  Channel     │
  Discord ───────────────▶│  Manager     │
  WhatsApp ──────────────▶│              │
  Slack / Zalo / Feishu ─▶└──────┬───────┘
  Facebook / Pancake /    ┌──────▼───────┐   ┌─────────────┐
  Bitrix24 ──────────────▶│  Gateway     │──▶│  8-Stage    │
  WebSocket Clients ─────▶│  Server      │   │  Pipeline   │
  HTTP API Clients ──────▶│  (WS + HTTP) │   │             │
                          └──────┬───────┘   │ context→    │
                                 │           │ prune→think→│
                          ┌──────▼───────┐   │ tool→observe│
                          │  Method      │   │ →checkpoint │
                          │  Router      │   │ →finalize   │
                          └──────┬───────┘   └──────┬──────┘
                                 │                  │
                          ┌──────▼───────┐   ┌──────▼───────┐
                          │  Agent Loop  │   │  LLM         │
                          │  (Think/Act/ │   │  Providers   │
                          │   Observe)   │   │  (27 types)  │
                          └──────┬───────┘   └──────────────┘
                          ┌──────▼───────┐
                          │  Tool        │
                          │  Registry    │
                          │  (47 tools)  │
                          └──────┬───────┘
                          ┌──────▼───────┐
                          │  Store Layer │
                          │  (PG/SQLite) │
                          └──────────────┘
```

### 8-Stage Agent Pipeline

The real pipeline (pipeline.go:32-50) is: **Setup** = ContextStage; **Iteration** = PruneStage → ThinkStage → ToolStage → ObserveStage → CheckpointStage; **Finalize** = FinalizeStage. A **MemoryFlushStage** is constructed and passed into PruneStage (pipeline.go:34), flushing memory when the context compacts.

Note: the marketing names (README.md:63 — context → history → prompt → think → act → observe → memory → summarize) differ from the real stage names; the verified names below are the source of truth.

| Stage | Phase | Description |
|-------|-------|-------------|
| ContextStage | Setup | Inject agent/user/workspace context, compute per-user files, calculate token overhead |
| PruneStage | Iteration | **Runs FIRST in the iteration loop** — context pruning (2-pass: soft trim → hard clear), runs MemoryFlushStage on compaction |
| ThinkStage | Iteration | Build system prompt, filter tools by policy, call LLM |
| ToolStage | Iteration | Execute tool calls (parallel goroutines for multiple calls) |
| ObserveStage | Iteration | Process tool results, append to messages |
| CheckpointStage | Iteration | Track iteration state, check loop exit conditions |
| FinalizeStage | Finalize | Sanitize output, flush messages, update session metadata |

The pipeline runs a configurable iteration loop (`DefaultMaxIterations = 30`, internal/config/defaults.go:10). Loop control uses two exit signals: **BreakLoop** — complete remaining stages in this iteration (ObserveStage must capture FinalContent), then exit; **AbortRun** — exit the inner loop immediately (unrecoverable, e.g. over budget after compaction) (pipeline.go:68-80).

### Key Internal Modules

| Module | Description |
|--------|-------------|
| `internal/gateway/` | WebSocket + HTTP server, client lifecycle, method router (144 RPC methods in `internal/gateway/methods/` + `internal/mcp/crud_*.go`) |
| `internal/agent/` | Agent loop (think/act/observe), router, resolver, system prompt builder |
| `internal/pipeline/` | 8-stage pluggable agent pipeline implementation |
| `internal/providers/` | LLM adapters: Anthropic (native HTTP+SSE), OpenAI-compatible (many), ACP (JSON-RPC 2.0), Vertex AI, ChatGPT OAuth router, Codex |
| `internal/tools/` | Tool registry with 47 built-in tools, policy engine, MCP bridge, credential adapters |
| `internal/channels/` | Channel adapters: Telegram, Discord, Feishu, Zalo, WhatsApp, Slack, Facebook, Pancake, Bitrix24 |
| `internal/store/` | Dual-DB store interfaces (PostgreSQL + SQLite via Dialect pattern) |
| `internal/scheduler/` | Lane-based concurrency (main/subagent/team/cron) with per-session queues |
| `internal/vault/` | Knowledge Vault: wikilinks, hybrid BM25+vector search |
| `internal/consolidation/` | Memory workers: episodic, semantic, dreaming, dedup |
| `internal/hooks/` | Lifecycle hooks: 8 events, sync/async, SSRF-hardened HTTP handlers |
| `internal/oauth/` | OAuth 2.0 pools for ChatGPT OAuth / Codex provider types |
| `internal/usagecaps/` | Usage caps / quotas per tenant, model pricing sync |
| `internal/i18n/` | Message catalog: T(locale, key, args...) + per-locale catalogs (en/vi/zh) |
| `internal/mcp/` | MCP client, bridge server, and CRUD server (`crud_server.go`) |
| `internal/eventbus/` | Typed domain event bus with worker pool, dedup, retry (v3) |
| `internal/upgrade/` | Database schema version tracking |

## Built-in Tools Catalog

47 built-in tools seeded via `builtinToolSeedData()` (cmd/gateway_builtin_tools.go:15-143) + the `telegram_manager` tool (internal/tools/telegram_manager.go:33). Seeding is idempotent — user-customized `enabled`/`settings` values survive upgrades. Disabled tools are unregistered from the registry at startup and on cache invalidation (applyBuiltinToolDisables, gateway_builtin_tools.go:263-283).

| Category | Tools |
|----------|-------|
| Filesystem (4) | `read_file`, `write_file`, `list_files`, `edit` (search-and-replace) |
| Runtime (5) | `exec` (shell, 60s default timeout), `wait`, `datetime`, `workstation_exec` (remote, requires workstation), `claude_remote` (Claude Code CLI on remote) |
| Web (2) | `web_search` (Brave/DuckDuckGo), `web_fetch` (Defuddle extractor chain + html-to-markdown) |
| Memory (4) | `memory_search` (semantic), `memory_get`, `memory_expand`, `knowledge_graph_search` (requires knowledge_graph) |
| Vault (2) | `vault_search` (wikilinks + episodic + KG fan-out), `vault_read` |
| Media (9) | `read_image`, `read_document`, `create_image`, `read_audio`, `read_video`, `create_video`, `create_audio` (all disabled by default — require provider chains), `tts`, `stt` |
| Browser (1) | `browser` (Rod + CDP automation: navigate, click, fill, screenshot) |
| Sessions (4) | `sessions_list`, `session_status`, `sessions_history`, `sessions_send` |
| Messaging (5) | `message` (proactive), `send_file`, `create_forum_topic` (Telegram), `list_group_members`, `zalo_list_groups` |
| Scheduling (2) | `cron` (at/every/cron expr), `heartbeat` (recurring self-check-in) |
| Subagents (2) | `spawn` (self-clone background subagent), `delegate` (linked-agent orchestration, requires agent_links) |
| Skills (5) | `skill_search`, `use_skill`, `publish_skill`, `skill_manage`, `mcp_tool_search` (deferred-load MCP tools) |
| Teams (1) | `team_tasks` (task board CRUD, requires managed_mode + teams) |
| Telegram manager (+1) | `telegram_manager` (internal/tools/telegram_manager.go — Telegram channel administration; only available inside Telegram runs) |

**Lite edition:** `skill_manage` and `publish_skill` are removed (gateway_builtin_tools.go:145-155). `team_tasks` requires `managed_mode`; Lite blocks comment/review/approve/reject/attach/ask_user via `TeamActionPolicy` (internal/tools/team_action_policy.go).

**Tool policy engine** (tools/policy.go:27-41): the composite `goclaw` tool group lists 42 tools; per-agent allow/deny lists and tool profiles are enforced by `IsToolAllowed()` (internal/mcp/tool_filter.go) and the policy engine. Exec runs through shell-deny-pattern validation and the exec approval flow.

## Provider Ecosystem

27 provider types (internal/store/provider_store.go:71-99 — `ValidProviderTypes`) unified through a single adapter interface with capability-based routing and encrypted API keys:

| Provider | Type | Notes |
|----------|------|-------|
| Anthropic | `anthropic_native` | Native HTTP+SSE; prompt caching, extended thinking |
| OpenAI | `openai_compat` | OpenAI-compatible; Azure-compatible |
| OpenRouter | `openrouter` | Route to many models via single API key |
| Google Gemini | `gemini_native` | Extended thinking |
| AIMLAPI | `aimlapi` | Multi-model aggregator |
| Groq | `groq` | Fast inference |
| DeepSeek | `deepseek` | — |
| Mistral | `mistral` | — |
| xAI (Grok) | `xai` | — |
| MiniMax | `minimax_native` | Default model MiniMax-M3 |
| Cohere | `cohere` | — |
| Perplexity | `perplexity` | — |
| DashScope (Alibaba Qwen) | `dashscope` | Alibaba Qwen |
| Bailian | `bailian` | Alibaba Bailian |
| ChatGPT OAuth | `chatgpt_oauth` | OAuth pool; router with failover across authenticated sessions |
| Claude CLI | `claude_cli` | Runs `claude` binary as subprocess |
| YesScale | `yescale` | — |
| ZAI | `zai` | Z.AI PaaS (GLM models) |
| ZAI Coding | `zai_coding` | Z.AI Coding plan |
| Ollama | `ollama` | Local or self-hosted; no API key |
| Ollama Cloud | `ollama_cloud` | Bearer token required |
| ACP | `acp` | Agent Client Protocol subprocess orchestration |
| Novita AI | `novita` | OpenAI-compatible endpoint |
| BytePlus | `byteplus` | BytePlus ModelArk (Seed 2.0 models) |
| BytePlus Coding | `byteplus_coding` | BytePlus ModelArk Coding Plan |
| Vertex AI | `vertex` | GCP OAuth2 service account + ADC; OpenAI-compat endpoint |
| Kimi Coding | `kimi_coding` | Moonshot Kimi (OpenAI-compat, fixed User-Agent) |

> **Not provider types:** Suno and "Custom" are NOT LLM provider types. Suno is a `create_audio` media backend (CHANGELOG.md:216) — there is no `suno` symbol in the Go source. Any OpenAI-compatible endpoint is configured via `openai_compat`, not a separate "Custom" type.

### Provider Architecture

Providers implement a `ProviderAdapter` interface with a `ModelRegistry` forward-compat resolver (internal/providerresolve/). Capability flags gate features: vision, document analysis, image/audio/video generation, TTS/STT, extended thinking, and prompt caching. All providers share:

- `RetryDo()` — retry-wrapped HTTP transport
- `SSEScanner` (providers/sse_reader.go) — shared streaming scanner for SSE-based providers
- Encrypted API keys at rest (AES-256-GCM)
- OpenAI-compat providers accept `WithExtraHeaders` and custom base URLs

## Channel Ecosystem

12 gateway surfaces: 10 channel adapter types (internal/channels/channel.go:76-85) + WebSocket + Browser Pairing. Each channel has per-channel DM/group policies, media handling, and streaming:

| Channel | Protocol | Features |
|---------|----------|----------|
| Telegram | Bot API | Forum topics, STT, bot commands, streaming, reactions, link previews, per-group agent bindings |
| Discord | Bot API | Streaming, voice messages (STT), media handling |
| WhatsApp | Native (whatsmeow) | QR auth, media, group support, no WhatsApp Business API dependency |
| Slack | Socket Mode | Thread context, native streaming, debounce, reaction levels |
| Zalo OA | Official API | Vietnamese messaging platform |
| Zalo Personal | Personal API | Session-based credentials, group support |
| Feishu / Lark | API | Streaming cards, media; domain config selects `lark` (global) vs `feishu` (China) |
| Facebook | Messenger API | Registered via factory (cmd/gateway.go:902) |
| Pancake | API | Vietnamese POS/messaging |
| Bitrix24 | API | CRM/messaging platform; portal instances + MCP integration |
| WebSocket | Raw WS | 144 RPC methods, full gateway control |
| Browser Pairing | Proxy | Pair browser sessions to gateway |

> **Note on "Larksuite":** Larksuite is NOT a separate channel type. It is Feishu's international domain configuration — `config_channels.go:229` defines a `Domain` field (`"lark"` default/global vs `"feishu"` China). The channel type is `feishu` regardless.

### Channel Behavior

- **DM/Group policies** per channel: `open`, `allowlist`, `disabled` (channel.go:60-72)
- **Media handling** — images, documents, audio (STT) and voice messages routed through the media pipeline with persistent MediaRef storage (internal/media/store.go)
- **Telegram formatting chain** — `SanitizeAssistantContent()` → `markdownToTelegramHTML()` → `chunkHTML()` → `sendHTML()`; tables rendered as ASCII inside `<pre>` blocks
- **Chat debounce** — message coalescing for rapid bursts (chat_debounce.go)
- **Streaming** — native streaming per channel with reaction/typing indicators where supported

## Configuration

GoClaw uses JSON5 config files with environment variable overlay and hot-reload via `fsnotify` (300ms debounce — config_load.go:129, hotreload.go:36).

**Required environment variables:**
- `GOCLAW_GATEWAY_TOKEN` — Bearer token for API/WS auth (required unless `GOCLAW_ALLOW_INSECURE_NO_AUTH=1`, config_load.go:18,38)
- `GOCLAW_ENCRYPTION_KEY` — AES-256-GCM key for credential encryption (missing key → warn only; credentials stored UNENCRYPTED, cmd/bitrix_portal.go:94-96)
- `GOCLAW_POSTGRES_DSN` — PostgreSQL connection string

**Key config sections:**
- `gateway` — host, port, token, rate limits, CORS, prompt injection handling, `mcp_server_token` (gates `/api/mcp/`)
- `agents.defaults` — default provider, model, temperature, max tool iterations
- `agents.list` — per-agent overrides for model, tools, workspace, skills
- `memory` — embedding provider/model, vector/text search weights, chunk sizes
- `compaction` — context compaction thresholds, memory flush
- `context_pruning` — soft trim and hard clear policies for tool results
- `subagents` — max concurrency, spawn depth, TTL
- `sandbox` — Docker isolation: memory, CPU, network, timeout
- `tools` — tool profiles, allow/deny lists, exec approval, MCP servers
- `channels` — per-channel: token, DM/group policy, allowlist, media limits

Secrets live in `.env.local` or environment variables — never in `config.json`. The `onboard` command (cmd/tui_onboard.go) is an interactive Bubble Tea setup wizard that generates `.env.local` and seeds the master tenant.

### Prompt System & Caching

- **4-mode prompt system** — Full / Task / Minimal / None with per-section gating, cache-boundary optimization, and per-session mode resolution
- **Prompt caching** — v3 cache-boundary markers inserted at section boundaries to maximize cache hits across the iteration loop; the "~90% cost reduction" is a marketing claim, not a measured guarantee
- **Bootstrap identity** — SOUL.md, IDENTITY.md system prompts seeded via `internal/bootstrap/`; per-user seed files
- **Context propagation** — `store.WithAgentType(ctx)`, `WithUserID(ctx)`, `WithAgentID(ctx)`, `WithLocale(ctx)`, `WithTenantID(ctx)` compose the run context; `ContextFileInterceptor` routes agent-level vs user-level context files

### Scheduling & Cron

Cron tool (internal/cron/) supports three syntaxes: `at` (one-shot absolute time), `every` (relative interval), and full cron expressions. Scheduled runs enter the scheduler's lane system and respect subagent concurrency/depth limits. Heartbeat scheduling (`heartbeat.*` RPC) is a separate recurring self-check-in mechanism with wake-on-demand support.

### CLI Reference

Cobra-based CLI (cmd/root.go:25):

| Command | Purpose |
|---------|---------|
| `goclaw onboard` | Interactive Bubble Tea setup wizard; generates `.env.local`, seeds master tenant |
| `goclaw migrate up` | Run PostgreSQL migrations (golang-migrate) |
| `goclaw upgrade` | Database schema version tracking / upgrades |
| `goclaw backup` | Full backup; `--upload-s3` uploads to S3 (requires s3 config in config_secrets) |
| `goclaw restore` | Restore from backup |
| `goclaw tenant backup` / `tenant restore` | Per-tenant backup/restore |
| `goclaw doctor` | Deployment health diagnostics |
| `goclaw agent chat` | Headless agent chat from CLI |
| `goclaw channels` / `providers` / `sessions` / `traces` / `cron` / `config` / `pairing` / `auth` | Management subcommands |
| `goclaw skills` / `skills deps` / `skills access` / `skills grant` / `skills revoke` / `skills evolution` | Skill lifecycle management |
| `goclaw bitrix portal` | Bitrix24 portal instance management |
| `goclaw version` | Version (set via `-ldflags` at build) |

### Sandbox

Docker-based code-execution sandbox (internal/sandbox/, SandboxConfig at config.go:411-438):

- Default image `goclaw-sandbox:bookworm-slim`; configurable memory, CPU, network, timeout
- Execution via `docker exec -e CRED=... containerID args...` — works with Credentialed Exec
- Config-driven pruning of stale sandbox resources (`SandboxPruneSettings`)

### Knowledge Vault

Document knowledge base layered above the store (internal/vault/):

- **Registry** — documents with metadata; `[[wikilinks]]` provide bidirectional links between documents
- **Hybrid search** — BM25 text + pgvector semantic with configurable weights; fan-out across episodic summaries and the knowledge graph
- **FS sync** — bidirectional filesystem synchronization for vault documents
- **Tools** — `vault_search`, `vault_read` built-in tools; delegation auto-links vault documents to run context (DelegationID, store/run_context.go:63)
- **Graph extraction** — LLM entity/relationship extraction feeds `knowledge_graph_search`

## Deployment

### Docker Compose (Recommended)

```bash
git clone https://github.com/nextlevelbuilder/goclaw.git
cd goclaw
./prepare-env.sh
# Add GOCLAW_OPENROUTER_API_KEY or similar to .env
docker compose -f docker-compose.yml -f docker-compose.postgres.yml up -d --build
```

Dashboard at `http://localhost:18790` (login: `system` / `GOCLAW_GATEWAY_TOKEN`).

**Optional overlays** (append `-f`):
- `docker-compose.sandbox.yml` — Docker sandbox for code execution
- `docker-compose.tailscale.yml` — Tailscale private network
- `docker-compose.otel.yml` — Jaeger OTel tracing
- `docker-compose.redis.yml` — Redis caching layer
- `docker-compose.browser.yml` — Headless Chrome for browser automation
- `docker-compose.selfservice.yml` — Nginx + separate UI at port 3000

### Container Image Variants

Published to GHCR (`ghcr.io/nextlevelbuilder/goclaw`) and Docker Hub (`digitop/goclaw`):

| Variant | Tag | Contents |
|---------|-----|----------|
| latest | `:latest`, `:vX.Y.Z` | Backend + web UI + Python |
| base | `:base`, `:vX.Y.Z-base` | Backend only, no UI/runtimes |
| full | `:full`, `:vX.Y.Z-full` | All runtimes + skills pre-installed |
| web | `-web:latest` | Standalone web UI (Nginx) |
| beta | `:beta`, `:vX.Y.Z-beta.N` | Beta builds from dev |

OTel and Tailscale variants are not pre-built — build from source with `--build-arg ENABLE_OTEL=true` or `-tags tsnet`.

### Bare Metal

```bash
go build -tags embedui -o goclaw .
./goclaw onboard   # interactive setup wizard
source .env.local && ./goclaw
```

### Desktop (Lite Edition)

Single native app (~30 MB) with SQLite, no Docker, no PostgreSQL:

```bash
curl -fsSL https://raw.githubusercontent.com/nextlevelbuilder/goclaw/main/scripts/install-lite.sh | bash
```

> **Correction:** Lite is NOT channel-less. `internal/edition/edition.go:44` sets `MaxChannels: {"telegram": 1, "discord": 1}` — the desktop edition supports 1 Telegram + 1 Discord instance. The README's "Channels: —" is outdated.

### Edition Comparison

| Feature | Lite (Desktop) | Standard (Server) |
|---------|---------------|-------------------|
| Agents | Max 5 | Unlimited |
| Teams | Max 1 (5 members) | Unlimited |
| Channels | 1 Telegram + 1 Discord | Unlimited, all 10 adapter types |
| Subagents | Max 2 concurrent, depth 1 | Unlimited |
| Database | SQLite (FTS5 text search) | PostgreSQL 18+ (pgvector semantic) |
| Knowledge Graph | — | Full |
| RBAC / Multi-tenant | — | Full |
| Vector search | — (FTS5 only) | Full (pgvector) |
| Workstations | — | Full (allowlisted exec + audit) |
| Package runtime | — (no pip/npm/apk) | Full |
| Auto-update | GitHub Releases (`lite-v*` tags) | Docker / binary |

## API Surface

- **REST API** — `POST /v1/chat/completions` (OpenAI-compatible, pass `goclaw:<agent-key>` as model name), `/v1/responses`, `/v1/tools/invoke`, `/v1/agents`, `/v1/skills`, `/v1/traces`, `/v1/mcp`, webhooks
- **Health** — `GET /health` (server.go:202, 1095; `/healthz` does NOT exist). The root handler advertises: `/health`, `/v1/chat/completions`, `/v1/responses`, `/v1/tools/invoke`, `/ws` (server.go:625)
- **Docs** — Swagger UI at `/docs` and OpenAPI JSON at `/v1/openapi.json`
- **WebSocket** — `/ws` with 144 RPC methods: `connect`, `chat.send`, `agents.*`, `sessions.*`, `skills.*`, `cron.*`, `traces.*`, `config.*`, `pairing.*`, `teams.*`, `tenants.*`, `workstations.*`, `hooks.*`, `api_keys.*`, `bitrix.portals.*`, `usage.*`, `tts.*`, `run.timeline.get`
- **Webhooks** — `POST /v1/webhooks/llm` (trigger an agent) + `POST /v1/webhooks/message` (send a channel message) from external systems; Bearer token prefixed `wh_` + HMAC `X-GoClaw-Signature` header; async worker with retry schedule, HMAC nonce/timestamp validation, idempotency, per-webhook + per-tenant two-tier token-bucket rate limiting (webhooks_ratelimit.go:11-23, default tenant 600 req/min)
- **MCP CRUD Server** — third MCP surface mounted at `/api/mcp/` (internal/mcp/crud_server.go, cmd/gateway.go:554), gated by `gateway.mcp_server_token`; separate from the bridge server; no per-caller identity (shared secret)
- **OpenAI-compatible chat/completions** — Pass `goclaw:<agent-key>` as model name

### WebSocket RPC Protocol

The WS protocol (pkg/protocol/) uses frame types `req` / `res` / `event`. The **first request must be `connect`** (client.go:156-157) — it authenticates the session; `browser.pairing.status` is the only method accepted for pending clients. Method handlers live one-per-family in `internal/gateway/methods/`, all registered on a `MethodRouter` (router.go:49). Representative families:

- `chat.*` — send, history, abort, inject, session.status, behavior.preview
- `agents.*` — list, create, update, delete, files.{list,get,set}, wait, identity.get
- `sessions.*` — list, preview, patch, delete, reset, compact
- `teams.*` — 22 methods (task board, members, workspace)
- `tenants.*` — 8 methods (multi-tenant admin)
- `workstations.*` — 14 methods (remote exec + permissions + activity audit)
- `hooks.*` — 7 methods (lifecycle hook admin CRUD + test + history)
- `api_keys.*` — 3 methods (scoped key management)
- `bitrix.portals.*` — 4 methods (portal instances + install URL)
- `usage.*`, `tts.*`, `run.timeline.get` — quotas, speech, per-run debug timeline
- `exec_approval.*` / `approvals.*` — shell command approval workflow
- `heartbeat.*` — recurring agent self-check-in (get/set/toggle/test/logs/checklist)

### Webhook Security Model

Webhooks authenticate with a `wh_`-prefixed secret (Bearer) plus HMAC-SHA256 signatures in `X-GoClaw-Signature` with timestamp-based nonce validation. The dispatcher runs an async worker with exponential retry and idempotency keys; a two-tier token-bucket rate limiter (per-webhook, then per-tenant) protects the endpoints (webhooks_ratelimit.go:11-23). Rate-limit responses set `Retry-After`.

### API Keys & Auth (docs/20-api-keys-auth.md)

Two auth mechanisms: the single gateway token (startup-configured) and scoped API keys. API keys are tenant-bound, prefixed `goclaw_` + 32 hex chars (128-bit entropy), and stored **only as SHA-256 hashes** (raw key never persisted — same pattern as GitHub PATs). Six RBAC scopes:

| Scope | Description |
|-------|-------------|
| `operator.admin` | Full access — equivalent to gateway token; manages API keys and SecureCLI configs |
| `operator.read` | Read-only: agents, sessions, skills, chat history, metadata |
| `operator.write` | Read + write: send chat, manage sessions, trigger cron |
| `operator.approvals` | Manage shell command execution approvals |
| `operator.pairing` | Manage browser device pairings |
| `operator.sessions` | Session-scoped access |

Highest scope derives the effective role (admin → RoleAdmin; write/approvals/pairing → RoleOperator; read → RoleViewer), used by `PolicyEngine.CanAccess()` to gate RPC methods. Both mechanisms work over HTTP REST and WebSocket RPC.

## Memory System

Three-tier progressive memory (internal/memory/):

- **L0 (working)** — current conversation context, auto-injected into the system prompt when relevant (auto_injector.go:8-13; budget ~200 tokens of L0 summaries)
- **L1 (episodic)** — per-session summaries written by the consolidation pipeline
- **L2 (semantic)** — knowledge-graph-backed long-term knowledge

Consolidation runs asynchronously through the typed domain event bus (internal/eventbus/) with 4 workers (internal/consolidation/):

| Worker | Function |
|--------|----------|
| `episodic_worker` | Summarizes completed sessions (SessionCompleted event) into L1 episodic memory |
| `semantic_worker` | Extracts entities/relationships into the L2 knowledge graph |
| `dreaming_worker` | Synthesizes cross-session insights from episodic summaries |
| `dedup` | Removes redundant memory entries |

All workers resolve the configured provider/model at runtime and are driven by `eventbus.DomainEvent` messages with a worker pool, dedup, and retry.

## Agent Teams & Orchestration

Teams (docs/11-agent-teams.md) are lead + member agent collectives:

- **Lead-centric**: only the lead receives `TEAM.md` with full orchestration instructions; members discover context on demand through tools (no idle-token waste)
- **Task-board dispatch**: lead creates tasks with an assignee; the system auto-dispatches to the assigned member via the message bus (the legacy `spawn(agent=...)` team flow was removed — `spawn` now only supports self-clone subagents)
- **Three orchestration patterns** (TEAM.md): **Sequential** (A finishes → lead reviews → delegates to B with A's output), **Iterative** (A drafts → B reviews → back to A with feedback), **Mixed** (A+B in parallel → lead reviews → delegates to C)
- **Escalation modes**: `notify_lead` or `fail_task` for stale tasks
- **Workspace scope**: `isolated` (default) or `shared` file scope per member
- **Negative context injection**: agents outside any team get explicit "You are NOT part of any team" prompt sections to prevent wasted iterations
- **Delegation** (inter-agent): auto / explicit / manual modes with agent_links, token-aware work distribution, `BatchQueue[T]` generic for result aggregation

## Skills System

SKILL.md-based knowledge packages (internal/skills/):

- **Hybrid search** — BM25 index (internal/skills/search.go) + semantic vector search, configurable weights
- **Lifecycle** — `skill_search`, `use_skill`, `publish_skill`, `skill_manage` built-in tools; `skill-creator` workflow for drafting from conversation
- **Grants** — per-agent/team grants control which skills are usable
- **Evolution integration** — the agent-evolution pipeline can propose skill drafts; not auto-applied (guardrailed)

## Agent Evolution

3-stage guardrailed self-improvement pipeline:

1. **Metrics collection** — agent run statistics, tool success/failure rates
2. **Suggestion analysis** — LLM-generated improvement suggestions from metrics
3. **Auto-adaptation** — guardrail-protected apply with rollback; agents refine `SOUL.md` / `CAPABILITIES.md` without changing their identity

## MCP Integration

Three MCP surfaces (internal/mcp/):

1. **MCP client** — connects to external MCP servers (stdio / SSE / HTTP) via `Manager` with per-agent server state, health loops, exponential-backoff reconnection, and connection pooling (`Pool`) for shared servers across agents. OAuth 2.0 client-credential flow with DCR and token refresh (internal/mcp/oauth/). Validation and allowlisting (internal/mcp/validation.go)
2. **Bridge server** — `BridgeTool` wraps MCP tool definitions as GoClaw-native `tools.Tool` with `Execute()`; registered into the central `tools.Registry`. BM25-based lazy tool discovery (`mcp_tool_search.go`); agent-level grants (`grant_checker.go`)
3. **CRUD server** — mounted at `/api/mcp/`, gated by `gateway.mcp_server_token`, shared-secret (no per-caller identity). Used by Bitrix24 portal integration and external CRUD clients

## Hooks System

8 lifecycle events (internal/hooks/types.go:23-39):

| Event | Value | Blocking |
|-------|-------|----------|
| SessionStart | `session_start` | no |
| UserPromptSubmit | `user_prompt_submit` | **yes** (fail-closed) |
| PreToolUse | `pre_tool_use` | **yes** (fail-closed) |
| PostToolUse | `post_tool_use` | no |
| **PostModelResponse** | `post_model_response` | **yes** (fail-closed) |
| Stop | `stop` | no |
| SubagentStart | `subagent_start` | **yes** (fail-closed) |
| SubagentStop | `subagent_stop` | no |

Handler types: `command` (shell with event data on stdin), `http` (SSRF-hardened endpoints), `prompt` (LLM-routed), `script` (sandboxed ES5.1 goja). Scopes: global (master tenant), tenant, agent. Decisions: allow/block/error/timeout/ask/defer; blocking events that timeout yield Decision=block (fail-closed). Every execution is audited to `hook_executions` with canonical-JSON input hash for dedup.

## Security

- **Rate limiting** — per-route token buckets (`rate_limit_rpm` config, server.go:152-155), webhook two-tier limiter
- **SSRF protection** — internal/security/ssrf.go URL validation for fetch tools and webhooks
- **Prompt injection detection** — 6 injection patterns (input_guard.go:49-75), detection-only
- **Credential scrubbing** — output redaction of secrets from LLM/tool output
- **RBAC** — admin/operator/viewer roles + RoleOwner; tenant-scope guards on admin writes (`store.IsMasterScope(ctx)` for global tables, `requireTenantAdmin` + SQL `WHERE tenant_id = $N` for tenant tables)
- **Encryption** — AES-256-GCM (crypto/aes.go) for API keys and OAuth credentials at rest. **Warning:** if `GOCLAW_ENCRYPTION_KEY` is missing, startup warns and credentials are stored UNENCRYPTED (cmd/bitrix_portal.go:94-96)
- **Exec security** — shell deny patterns, Credentialed Exec direct-exec mode (no shell), exec approval flow for risky commands
- **Session IDOR hardening** — tenant/user scoping on all session access; all security events logged as `slog.Warn("security.*")`

## Credentialed Exec / Secure CLI (docs/19-credentialed-exec.md)

Agents can use external CLIs with auto-injected credentials: `git`, `gh`, `gcloud`, `aws`, `kubectl`, `terraform`, `psql`, plus Google Workspace adapters. Credentials are AES-256-GCM encrypted at rest and injected **directly into child process env** via `exec.Command(binary, args...)` — never through a shell (`sh -c`), never exposed to the LLM. Shell operators (`;`, `&&`, `|`, `$()`, backticks) are rejected with structured errors when credentials are present; binary path must match the allowlist; output is scrubbed before returning to the agent. Works in sandbox mode via `docker exec -e CRED=...`. Lookup is binary-based (`parseCommandBinary()` → `LookupByBinary()` → `resolveAndMatchBinary()`), with a `matchesBinaryDeny()` blocklist. API keys with `operator.admin` scope can manage SecureCLI configs.

## Workstations (Standard-only)

Remote allowlisted execution: agents can run `workstation_exec` and `claude_remote` on linked remote workstations via SSH. RPC surface: `workstations.*` (14 methods) — list/get/create/update/delete, `testConnection`, `linkAgent`/`unlinkAgent`, `permissions.*` (4), `activity.list`. Every execution is audited; only allowlisted commands run.

## Lifecycle & Operations

- **Backup/restore** — `goclaw backup` CLI command with optional S3 upload (cmd/backup.go:18,79-93, `--upload-s3` flag), per-tenant backup (tenant_backup.go); schema version tracking via `internal/upgrade/`
- **Migrations** — dual migration systems: SQL in `migrations/` for PG (bumped via `RequiredSchemaVersion`), `schema.sql` + incremental patches for SQLite (bumped via `SchemaVersion`)
- **Packages runtime** — runtime package management for apk / pip+npm / GitHub release assets (docs/packages-*.md), gated by edition (`SupportsPipNpm`, `SupportsApk`)
- **Heartbeat system** — recurring agent self-check-in (`heartbeat.*` RPC: get/set/toggle/test/logs/checklist), wake function for immediate runs (heartbeat.go:22-52)
- **Run timeline** — `run.timeline.get` returns per-run step timelines for debugging agent runs
- **Exec approval flow** — `exec_approval.*` RPC (approvals.approve/deny/list) for risky shell commands; gated by `operator.approvals` scope
- **Browser cookie sync** — signed-in browser sessions sync cookies to the gateway's browser automation tool (threat model in docs/browser-cookie-sync-threat-model.md)
- **Chat behavior** — quick-ack/intermediate replies (`chat_behavior.preview`), message debounce, per-channel formatting (Telegram HTML sanitization → chunked send)
- **OAuth pools** — OAuth 2.0 client-credential pools for `chatgpt_oauth` (router with failover across authenticated sessions, chatgpt_oauth_router.go:145-185) and Codex
- **Model pricing** — usage pricing service syncs OpenRouter model catalog (`usagepricing.StartOpenRouterCatalogAutoSync`), feeds usage caps
- **Usage caps/quotas** — per-tenant usage caps enforced during intent classification (usage_caps.go, `ClassifyIntentWithUsageCaps`)
- **Media** — audio STT (ElevenLabs Scribe / proxy) + TTS (OpenAI, ElevenLabs, Edge, MiniMax), image/document/video/audio generation backends (DashScope, MiniMax, Veo, Suno for `create_audio`); persistent MediaRef storage
- **i18n** — en/vi/zh catalogs; WS `connect` locale param, HTTP `Accept-Language` header, propagated via `store.WithLocale(ctx)`

## Web Dashboard

React 19 SPA in `ui/web/` (Vite 6, TypeScript, Tailwind CSS 4, Radix UI, Zustand, React Router 7):

- Visual management of agents, providers, channels, vault documents, skills, cron jobs, hooks, and API keys
- Chat interface with streaming, run timeline viewer, trace inspection
- i18n via `i18next` with namespace-split locale files in `ui/web/src/i18n/locales/{en,vi,zh}/`
- Mobile-first responsive rules: `h-dvh` viewports, 16px inputs (`text-base md:text-sm`), safe-area insets, ≥44px touch targets
- Dev: `pnpm install && pnpm dev` (uses `pnpm`, not npm)

## Desktop Edition (Lite)

Wails v2 native app in `ui/desktop/` (build tag `//go:build sqliteonly`; entry `ui/desktop/main.go` + `app.go`):

- **Embedded gateway** — the full gateway runs in-process with SQLite backend; React frontend embedded in the binary
- **Data dirs** — `~/.goclaw/data/` (SQLite DB, configs), `~/.goclaw/workspace/` (agent files, team workspace); OS keyring (`go-keyring`) with file fallback `~/.goclaw/secrets/`
- **Auto-update** — `internal/updater/` checks GitHub Releases for `lite-v*` tags; `UpdateBanner` shows the notification; release flow via `release-desktop.yaml` (macOS arm64+amd64, Windows)
- **Install scripts** — `scripts/install-lite.sh` (macOS), `scripts/install-lite.ps1` (Windows)
- **Versioning** — `cmd.Version` set via `-ldflags`; frontend calls `wails.getVersion()`
- **WS params** — all WebSocket method params use camelCase (`teamId`, `taskId`, `sessionKey`) matching Go `json:"..."` tags

## Versioning & Releases

- **Tag patterns** — `vX.Y.Z` (clean semver → stable release), `v*-beta*`/`v*-rc*` (beta), `lite-v*` (desktop). Tag patterns are mutually exclusive so workflows never overlap
- **CI** — `ci.yaml` (push main / PR→main/dev): Go build+test+vet, Web build
- **Releases** — `release.yaml` (binaries + Docker 4 variants + web + Discord announce), `release-beta.yaml` (beta binaries + GH prerelease), `release-desktop.yaml` (desktop)
- **Docker** — `latest`/`base`/`full`/`web`/`beta` variants on GHCR + Docker Hub
- **Integration tests** — require pgvector pg18 on port 5433 (`docker run -d --name pgtest -p 5433:5432 -e POSTGRES_PASSWORD=test -e POSTGRES_DB=goclaw_test pgvector/pgvector:pg18`), run with `-tags integration`

## Observability

Built-in LLM call tracing with spans, prompt cache metrics, and per-run timelines; optional OpenTelemetry OTLP export (build-tag gated) via Jaeger (`docker-compose.otel.yml`). All security events logged with `slog.Warn("security.*")` for consistent greppability.

## Multi-Tenancy

- **Identity** — compound `tenant.{id}.user.{id}` model; dual-identity pattern (agent_key vs UUID) applies to agents, teams, tenants (UUID for DB/FK/events, agent_key for logs/paths/UI)
- **Isolation** — per-user context files, sessions, memory, traces; `store.WithAgentType(ctx)`, `WithUserID(ctx)`, `WithTenantID(ctx)` context propagation; `BuildScopeClause()` SQL helper enforces tenant scoping at the query layer
- **Master scope** — global tables (builtin_tools, disk config, package mgmt) write-gated with `requireMasterScope(requireOwner(...))`; tenant tables with `requireTenantAdmin`
- **Lite edition** — single-user, RBAC and multi-tenant disabled

## Related

- [[openclaw]] — TypeScript-based agent gateway (inspired GoClaw's architecture)
- [[hermes-agent]] — Python-based agent gateway
- [[alphaclaw]] — Setup UI and gateway manager for OpenClaw
- [[tank-os]] — Fedora bootc deployment OS
- [[mission-control]] — Dashboard and management plane for agent gateways
- [[goclaw]] — MCP implementation details (client + bridge server + CRUD server)
- [[podman]] / [[podman-compose]] — Container runtime
- [[materia]] — Alternative agent framework
- [[nanobot]] — Alternative agent framework
