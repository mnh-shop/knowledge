---
name: goclaw-architecture
description: "GoClaw enterprise AI agent gateway — multi-tenant architecture, 8-stage pipeline, Go internals"
tags: [goclaw, architecture, agent-gateway, go]
source: sources/goclaw/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# GoClaw Architecture
**Source:** `sources/goclaw/` · v3.15.0-beta.181 (Go 1.26)

GoClaw is an enterprise AI agent gateway written in Go. Multi-tenant, PostgreSQL/SQLite-backed, with 27 provider types and 10 messaging channel adapters. Designed as a faster, lighter alternative to [[openclaw]] and [[hermes-agent]], compiling to a ~25 MB static binary with <1s startup.

## Core Architecture

- **Language**: Go (1.26+, single binary, ~25 MB)
- **Database**: PostgreSQL 15+ with pgvector (production) or SQLite via `modernc.org/sqlite` (desktop/Lite edition)
- **API Surface**: REST API (`/v1/*`, OpenAI-compatible; ~375 routes across `internal/http/` handlers) + WebSocket (`/ws`, 144 RPC methods — 157 method-name constants in `pkg/protocol/methods.go`)
- **Config**: JSON5 `config.json` with `env:` prefix for secrets, fsnotify hot-reload (300ms debounce)
- **Port**: 18790 (default)
- **Auth**: Gateway bearer token, API keys (`goclaw_<32hex>`, SHA-256 hashed, 6 scopes), RBAC (admin/operator/viewer)
- **Editions**: Standard (unlimited) vs Lite (desktop; 5 agents, `MaxChannels {"telegram":1,"discord":1}`)
- **Docker Image**: `ghcr.io/nextlevelbuilder/goclaw:latest` (also Docker Hub `digitop/goclaw`)

## 8-Stage Agent Pipeline

The core of every agent interaction (`internal/pipeline/`). All agents always use this pipeline v3 (`NewDefaultPipeline`, `pipeline.go:32-50`):

| Phase | Stage | Purpose |
|-------|-------|---------|
| **Setup** | ContextStage | Inject agent/user/workspace context; resolve per-user files |
| **Iteration** | PruneStage | Soft/hard context trim when ≥30%/≥50% full (cache-ttl mode); owns the shared `MemoryFlushStage` (created at `pipeline.go:34`) |
| | ThinkStage | Build system prompt (15+ sections), call LLM, emit streaming |
| | ToolStage | Execute tool calls (read-only in bounded parallel, others sequential) |
| | ObserveStage | Process tool results, handle silent completion |
| | CheckpointStage | Track iterations, check exit conditions |
| **Finalize** | FinalizeStage | Output sanitization; flush messages; update session metadata |

The iteration loop runs up to `max_tool_iterations` (default 20) per turn. Pipeline is fully stateless — all mutable state lives in `RunState`, passed by pointer through stages. **Marketing names differ from code**: the README (`README.md:63`) advertises `context → history → prompt → think → act → observe → memory → summarize`; the code-stage order is Context → Prune → Think → Tool → Observe → Checkpoint, with `MemoryFlushStage` shared by Prune and Finalize.

## Key Architectural Components

### Gateway (`internal/gateway/server.go`)
HTTP + WebSocket server decomposed into 7 modules (deps, http_wiring, events, lifecycle, tools_wiring, methods, router). Uses `net.http.ServeMux` with standard library only (no framework). Rate limiting via `RateLimiter` (default 20 RPM/user), WS client management, method routing via `MethodRouter` (144 RPC methods). Routes: `/ws` + `/health` at `server.go:199-202`; `/v1/chat/completions`, `/v1/responses`, `/v1/tools/invoke`; CRUD MCP server at `/api/mcp/` gated by `gateway.mcp_server_token` (`server.go:337`).

### Scheduler Lanes
Four semaphore-gated concurrency lanes: `main` (30), `subagent` (50), `team` (100), `cron` (30). Prevents cron from starving user messages.

### Provider Layer (`internal/providers/`, `internal/store/provider_store.go`)
27 provider types (`ValidProviderTypes`, `provider_store.go:71-99`): Anthropic native (HTTP+SSE), OpenAI-compat (HTTP+SSE), Gemini native, OpenRouter, AIML API, Groq, DeepSeek, Mistral, xAI, MiniMax, Cohere, Perplexity, DashScope (Qwen), Bailian, ChatGPT OAuth (pooled), Claude CLI, YesScale, Zai, Zai Coding, Ollama, Ollama Cloud, ACP (JSON-RPC 2.0 stdio), Novita AI, BytePlus, BytePlus Coding, Vertex AI (GCP OAuth2 + OpenAI-compat), Kimi Coding. All use `RetryDo()` for retries; shared `SSEScanner` for streaming. ChatGPT OAuth providers route through **OAuth pools** (chatgpt_oauth / codex: round-robin member pools with failover and observation tracking).

### ACP Provider (`internal/providers/acp/`)
Orchestrates Claude Code, Codex CLI, Gemini CLI as subprocesses via JSON-RPC 2.0 over stdin/stdout. Configurable permission modes (`approve-all`, `approve-reads`, `deny-all`), idle TTL, per-agent work dirs.

### Channel Layer (`internal/channels/channel.go`)
10 adapter types (`channel.go:76-85`): `bitrix24`, `discord`, `facebook`, `feishu`, `pancake`, `slack`, `telegram`, `whatsapp`, `zalo_oa`, `zalo_personal`. Translating platform-specific events to `InboundMessage`:
- Telegram (long polling), Discord (Gateway API), WhatsApp (native via whatsmeow v3), Slack (Socket Mode), Zalo OA + Zalo Personal, Feishu/Lark (WebSocket + webhook — "Larksuite" is the Feishu international-domain variant), Bitrix24 (webhook with portal self-service), Facebook (Graph API; **dynamically registered** instance factory at `cmd/gateway.go:902-919`), Pancake (multi-platform proxy), plus a raw WebSocket channel and browser pairing.

### Tool System (`internal/tools/`)
47 built-in tools: 46 seeded via `builtinToolSeedData` (`cmd/gateway_builtin_tools.go:15-143`) + `telegram_manager` wired at `cmd/gateway.go:879-880`. Organized by category (filesystem, runtime, web, memory, vault, media, browser, sessions, messaging, scheduling, subagents, skills, teams). Policy-based access control with per-agent allow/deny lists. `PolicyEngine` handles permission resolution, credential gating, and shell deny groups. Exec approval flow: `ExecApprovalConfig` (`tools/exec_approval.go`) gates `exec`/`workstation_exec`; credentialed binaries auto-bypass it.

### Credentialed CLI (Direct Exec Mode)
Secure execution of external CLIs with auto-injected, encrypted credentials (`docs/19-credentialed-exec.md`, `internal/tools/credentialed_exec.go`). Commands run via `exec.Command(binary, args...)` — **no shell** — eliminating injection. Presets for `gh`, `gcloud`, `aws`, `kubectl`, `terraform` (`credential_presets.go`); pluggable credential **adapters** extend coverage to `git`, `psql`, `docker`, `gws` (Google Workspace CLI, `docs/google-workspace-cli.md`; adapter playbook in `docs/credential-adapter-playbook.md`, per-binary deny patterns in `docs/git-credential-adapter.md`). AES-256-GCM at rest, credential-value scrubbing in all output, TOOLS.md context injection, optional Docker sandbox with per-command env isolation. CRUD API at `/v1/cli-credentials` (dry-run test endpoint included).

### Workstations (`internal/workstation/`)
Remote workstation management (Standard edition only — gated at router, `methods.go:216-235`): allowlisted command exec via `workstation_exec` / `claude_remote` tools, `testConnection`, agent linking, permission allowlist CRUD, and an activity audit log (`workstations.activity.list`).

### Webhooks (`docs/webhooks.md`)
Tenant-scoped registry (admin CRUD at `/v1/webhooks` + rotate/revoke/calls) feeding two runtime endpoints: `POST /v1/webhooks/llm` (invoke agent, sync 600s default or async with outbound HMAC-signed callbacks) and `POST /v1/webhooks/message` (Standard only). Bearer `wh_` secrets (SHA-256 stored) or HMAC `X-GoClaw-Signature` (t+v1, 300s skew, replay nonce). Idempotency-Key support, two-tier rate limiting, SSRF protection, async worker with 5-step retry schedule → `dead`.

### API Keys (`internal/crypto/apikey.go`, `internal/http/api_keys.go`)
Format `goclaw_<32hex>` (16 random bytes); stored as SHA-256 hash, AES-256-GCM encrypted, tenant-bound, cached with pubsub invalidation. 6 scopes (`internal/permissions/policy.go:41-46`): `operator.admin`, `operator.read`, `operator.write`, `operator.approvals`, `operator.pairing`, `operator.provision`. Resolved in `internal/http/auth.go` with priority: gateway token → API key → browser pairing → no-auth fallback.

### MCP Integration (`internal/mcp/`)
Full Model Context Protocol client and server via `github.com/mark3labs/mcp-go`. `Manager` handles server lifecycle (connect, tool discovery, keepalive, reconnection with exponential backoff). Connection pooling for shared servers. OAuth 2.0 with DCR and token refresh. `BridgeTool` wraps MCP tools as GoClaw-native tools. BM25 search (`mcp_tool_search.go`) for lazy tool discovery. CRUD MCP server at `/api/mcp/` (`crud_server.go`) exposes agent/cron/tool management as MCP tools, gated by `gateway.mcp_server_token` (`cmd/gateway.go:554`).

### Memory System (`internal/memory/`)
3-tier with consolidation workers:
- **L0 (Working)**: Current conversation buffer, auto-injected into prompts
- **L1 (Episodic)**: Session summaries pushed by consolidation workers
- **L2 (Semantic)**: Abstracted facts with vector embeddings (pgvector)

Workers: episodic, semantic, dreaming, dedup — driven by `DomainEventBus`. Usage caps (`internal/usage/caps/`) bound context/token budgets for background workers.

### Agent Teams (`internal/tools/team_tool_*.go`)
Task board with priorities, dependencies, blockers. Delegation modes (auto/explicit/manual). Task lifecycle (create, claim, complete, review). `BatchQueue[T]` for parallel wait aggregation. Team workspace + events via dedicated RPC families.

### Knowledge Vault (`internal/vault/`)
Wikilink document mesh with LLM auto-summary + semantic auto-linking. Hybrid BM25 + vector search. L0 auto-injection into prompts. FS sync for external document management.

### Knowledge Graph (`internal/knowledgegraph/`)
LLM-powered entity/relationship extraction with graph traversal. Entities and relationships extracted from conversations at runtime.

### Hook System (`internal/hooks/`)
8 lifecycle events (`types.go:23-39` + `config.go:30-38`): `session_start`, `user_prompt_submit` (blocking), `pre_tool_use` (blocking), `post_tool_use`, `stop`, `subagent_start` (blocking), `subagent_stop`, `post_model_response` (blocking). Handler types: command, http, prompt, ES5.1 script (sandboxed goja). Sync/async dispatch with allow/block decisions (fail-closed), CEL matchers, if-exprs, priorities, dedup, SSRF hardening, circuit breaker, audit logging.

### Media (`internal/media/`, `internal/audio/`)
`read_image`/`read_document`/`create_image`/`read_audio`/`read_video`/`create_video`/`create_audio` tools backed by provider chains. `internal/audio/manager.go` handles STT (ElevenLabs Scribe or proxy) and music/sound generation; `internal/media/store.go` persists media. TTS config (`internal/config/config_channels.go:578`, `TtsConfig`): providers openai, openai_compat, elevenlabs, edge, minimax, gemini with auto mode (off/always/inbound/tagged) and per-provider settings.

### Browser Cookie Sync (`internal/http/browser_cookies.go`, `docs/browser-cookie-sync-threat-model.md`)
Selected cookie sync lets a user copy Chrome cookies into a server-side Rod browser session (caps: 200 items, 1 MB body, 16 KB/value) with tenant/user/agent isolation and audit logging.

### Store Layer (`internal/store/`)
Interface-based with dual-DB pattern. Shared `Dialect` interface in `store/base/`. PostgreSQL (`store/pg/`, `pgx/v5`) for production. SQLite (`store/sqlitestore/`, `modernc.org/sqlite`) for desktop. 71+ store types (session, agent, memory, team, cron, vault, etc.).

## Config Sections (`internal/config/config.go:44-66`)

| Section | Purpose |
|---------|---------|
| `agents` | `agents.defaults` (workspace, provider, model, sandbox, memory, compaction, contextPruning) + `agents.list` per-agent overrides |
| `channels` | Channel instance configs, per-channel DM/group policies, chat_behavior overrides, quotas |
| `providers` | LLM provider definitions + encrypted API keys |
| `gateway` | `token`, `owner_ids`, `allowed_origins`, `rate_limit_rpm`, `injection_action`, `mcp_server_token`, `quota` (`QuotaConfig`: per-user/group windows), `chat_behavior`, `max_message_chars`, webhook timeouts |
| `tools` | `mcp_servers`, `shellDenyGroups`, `execApproval`, `web_fetch` domain policy, browser, allow/deny/byProvider profiles |
| `skills` | storage dir, max upload size, slash commands |
| `sessions` | session management defaults |
| `database` | DSNs from env only (`GOCLAW_POSTGRES_DSN`, `GOCLAW_REDIS_DSN`) |
| `tts` / `audio` | TTS providers + STT/Music defaults |
| `cron` | retry/backoff/timezone/timeout, command payloads |
| `telemetry` | OTLP export + `model_pricing` (`ModelPricing`: input/output/cache/reasoning per-million rates) |
| `tailscale` | optional tsnet listener (`-tags tsnet`, auth key from env) |
| `bindings` | channel/peer → agent routing |
| `hooks` | script concurrency caps, builtin disable list |
| `packages` | runtime package management (GitHub updater) |
| `system_messages` | localized operator-facing message templates |

## RPC Families (`pkg/protocol/methods.go`)

- **teams.*** — 22 methods (list/create/get/delete/update, known_users, scopes, tasks.* ×13, members.add/remove) + workspace.* (3) + events.list
- **tenants.*** — 8 (list/get/create/update, users.list/add/remove, mine)
- **workstations.*** — 14 (CRUD, testConnection, linkAgent/unlinkAgent, permissions.* ×4, activity.list)
- **hooks.*** — 7 (list/create/update/delete/toggle/test/history)
- **api_keys.*** — 3 (list/create/revoke)
- **bitrix.portals.*** — 4 (list/create/get_install_url/delete)
- **usage.*** — usage.get, usage.summary + quota.usage
- **tts.*** — 6 (status/enable/disable/convert/setProvider/providers)
- **run.timeline.get** — run execution timeline
- **exec.approval.*** — 3 (list/approve/deny)
- Plus: agents.* (incl. files.*, links.*), sessions.*, config.* (+ permissions.*, schema/defaults, chat_behavior.preview), cron.* (8), channels.* (incl. instances.*), skills.*, pairing (device.pair.*, browser.pairing.status), heartbeat.* (8), voices.*, browser.*, logs.tail, send, llm.complete

## CLI (`cmd/root.go:39-59`)

21 root commands: `onboard`, `version`, `pairing`, `agent`, `doctor`, `config`, `providers`, `channels`, `bitrix-portal`, `cron`, `skills`, `sessions`, `traces`, `migrate`, `upgrade` (`--status` / `--dry-run`), `backup`, `restore`, `tenant-backup`, `tenant-restore`, `auth`, `setup`. Remote gateway operations via persistent `--server` / `--token` flags; `goclaw update --apply` applies pending upgrades.

## Data Flow

```
User → Channel (Telegram/Discord/WS) → Gateway → Scheduler → Pipeline
→ Provider (LLM call) → Tools/MCP/Memory → Finalize → Channel → User
```

## Key Source Components

| File | Purpose |
|------|---------|
| `main.go` | Entry point |
| `internal/pipeline/pipeline.go` | 8-stage pipeline orchestrator (`NewDefaultPipeline` :32-50) |
| `internal/pipeline/stage.go` | Stage interface (stateless, RunState-based) |
| `internal/gateway/server.go` | HTTP/WS server, handler registration |
| `internal/gateway/router.go` | MethodRouter: 144 RPC method dispatch |
| `internal/agent/loop.go` | Agent execution loop |
| `internal/agent/systemprompt.go` | System prompt builder (15+ sections) |
| `internal/store/provider_store.go` | Provider types (27, :71-99) |
| `internal/providers/acp/` | ACP JSON-RPC 2.0 subprocess provider |
| `internal/providers/chatgpt_oauth*` | ChatGPT OAuth pool routing (chatgpt_oauth/codex) |
| `internal/tools/registry.go` | Tool registry with policy-based access |
| `internal/tools/policy.go` | Tool policy engine (allow/deny/credential) |
| `internal/tools/credentialed_exec.go` | Direct Exec engine for credentialed CLIs |
| `internal/tools/credential_adapter_*.go` | git/psql/etc. credential adapters |
| `internal/mcp/manager.go` | MCP server lifecycle manager |
| `internal/mcp/crud_server.go` | CRUD MCP server at `/api/mcp/` |
| `internal/channels/channel.go` | Channel interface + 10 adapters (:76-85) |
| `internal/memory/` | 3-tier episodic/semantic/dreaming memory |
| `internal/vault/` | Knowledge Vault with wikilinks + hybrid search |
| `internal/knowledgegraph/` | Entity/relationship graph extraction |
| `internal/hooks/` | 8 lifecycle event hooks |
| `internal/eventbus/domain_event_bus.go` | Typed event bus with worker pool |
| `internal/store/` | Dual-DB store layer (PG + SQLite) |
| `internal/config/config.go` | Config struct + JSON5 loading |
| `internal/scheduler/` | 4-lane concurrency scheduler |
| `internal/edition/edition.go` | Edition system (Lite/Standard) |
| `internal/sandbox/` | Docker-based code execution isolation |
| `internal/orchestration/batch_queue.go` | `BatchQueue[T]` generic for parallel waits |
| `internal/workstation/` | Remote workstation exec + audit (Standard) |
| `internal/audio/manager.go` | STT / music generation manager |
| `internal/usage/caps/` | Usage caps / quotas for LLM calls |
| `internal/i18n/` | Message catalog (en/vi/zh) |
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
