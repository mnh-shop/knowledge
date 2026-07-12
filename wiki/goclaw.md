---
name: goclaw
tags: [ai-llm, cli, container, gateway, golang, mcp, acp, orchestration, plugin-sdk, quadlet, security, systemd, webhook, wiki, goclaw]
description: "GoClaw — Go-based enterprise AI agent gateway with multi-tenant isolation, 22 LLM providers, 12 messaging channels, and 50+ built-in tools"
source: sources/goclaw/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# GoClaw — Enterprise AI Agent Gateway

| Field | Value |
|---|---|
| **Origin** | [nextlevelbuilder/goclaw](https://github.com/nextlevelbuilder/goclaw) |
| **License** | CC BY-NC 4.0 |
| **Stack** | Go 1.26, PostgreSQL 18+ with pgvector, SQLite (desktop), WebSocket RPC, React 19 SPA |
| **Container** | `ghcr.io/nextlevelbuilder/goclaw:latest` |
| **Port** | 18790 |
| **Binary Size** | ~25 MB static Go binary, <1s startup |
| **Documentation** | [docs.goclaw.sh](https://docs.goclaw.sh/) |

## What It Is

GoClaw is an **open-source enterprise AI agent gateway** written in Go. It connects LLM providers to messaging channels (Telegram, Discord, WhatsApp, Slack, Zalo, Feishu/Lark) and provides 50+ built-in tools, multi-tenant isolation, agent teams, knowledge management, and a full web dashboard — all as a single ~25 MB binary that starts in under a second.

It is a production-tested alternative to [[openclaw]] (TypeScript) and [[hermes-agent]] (Python), with a focus on performance, low resource footprint, and an 8-stage agent pipeline.

## Key Features

| Category | What GoClaw Provides |
|----------|----------------------|
| **Multi-Tenant v3** | Per-user isolation for context, sessions, memory, traces; RBAC with admin/operator/viewer roles; compound `tenant.{id}.user.{id}` identity model |
| **8-Stage Pipeline** | context → history → prompt → think → act → observe → memory → summarize; pluggable stages with always-on execution |
| **22 Provider Types** | OpenAI, Anthropic, Google Gemini, Groq, DeepSeek, Mistral, xAI (Grok), OpenRouter, MiniMax, Cohere, Perplexity, DashScope (Qwen), Bailian, ZAI, Ollama (local), Ollama Cloud, Vertex AI, Claude CLI, Codex/ChatGPT, ACP, Suno, Novita AI, YesScale, Custom |
| **ACP Provider** | Orchestrates Claude Code, Codex CLI, Gemini CLI as subprocess agents via JSON-RPC 2.0 over stdio |
| **12 Messaging Channels** | Telegram, Discord, WhatsApp (native via whatsmeow), Zalo OA, Zalo Personal, Slack, Feishu/Lark, Larksuite, WebSocket, Browser Pairing, Pancake, Bitrix24 |
| **50+ Built-in Tools** | Filesystem (read/write/edit/search), web search, browser automation, code execution, memory search, knowledge graph, knowledge vault, skills, TTS/audio, cron, subagent delegation, teams |
| **64+ WebSocket RPC Methods** | Real-time control via `/ws` — chat, agent management, sessions, traces, config, skills, cron, pairing |
| **3-Tier Memory** | L0 (working/conversation) → L1 (episodic/session summaries) → L2 (semantic/knowledge graph); consolidation workers for episodic, semantic, dreaming, and dedup |
| **Knowledge Vault** | Document registry with `[[wikilinks]]` for bidirectional linking; hybrid BM25 + pgvector search; filesystem sync |
| **Knowledge Graph** | LLM-powered entity/relationship extraction with graph traversal |
| **Agent Teams** | Lead + member agents with shared task board, inter-agent delegation (sync/async), handoff, 3 orchestration modes |
| **Hooks System** | 7 lifecycle events: SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Stop, SubagentStart/SubagentStop; sync/async, SSRF-hardened HTTP handlers, audit logging |
| **MCP Integration** | Connect to any MCP server (stdio/SSE/HTTP); expose GoClaw tools as an MCP server via bridge |
| **Skills System** | SKILL.md-based knowledge packages with BM25 + semantic hybrid search; publishing, grants, evolution-driven drafts |
| **Agent Evolution** | 3-stage guardrailed pipeline: metrics → suggestion analysis → auto-adaptation; agents refine SOUL.md/CAPABILITIES.md without changing identity |
| **Extended Thinking** | Per-provider reasoning modes (Anthropic, OpenAI, DashScope); streaming support |
| **Prompt Caching** | Up to ~90% cost reduction on repeated prefixes; v3 cache-boundary markers |
| **4-Mode Prompt System** | Full / Task / Minimal / None with section gating, cache boundary optimization, per-session mode resolution |
| **Single Binary** | ~25 MB static binary, no Node.js runtime, <1s startup, runs on a $5 VPS |
| **Dual-DB** | PostgreSQL 15+ with pgvector (full multi-tenant production); SQLite (desktop/lite, single-user) via unified store Dialect pattern |
| **Web Dashboard** | React 19 SPA (Vite, Tailwind CSS, Radix UI, Zustand) for visual agent/provider/channel/vault management |
| **Desktop Edition** | Wails v2 native app (~30 MB) with SQLite, chat UI, Kanban board, auto-update; max 5 agents, 1 team |
| **Observability** | Built-in LLM call tracing with spans and prompt cache metrics; optional OpenTelemetry OTLP export via Jaeger |
| **Security** | Rate limiting, SSRF protection, prompt injection detection, credential scrubbing, RBAC, AES-256-GCM encryption, session IDOR hardening |

## Architecture

GoClaw follows a **modular layered architecture** with a Go backend, WebSocket/HTTP gateways, and a React frontend.

```
                          ┌──────────────┐
  Telegram ──────────────▶│  Channel     │
  Discord ───────────────▶│  Manager     │
  WhatsApp ──────────────▶│              │
  Slack / Zalo / Feishu ─▶└──────┬───────┘
                          ┌──────▼───────┐   ┌─────────────┐
  WebSocket Clients ─────▶│  Gateway     │──▶│  8-Stage    │
  HTTP API Clients ──────▶│  Server      │   │  Pipeline   │
                          │  (WS + HTTP) │   │             │
                          └──────┬───────┘   │ context→    │
                                 │           │ history→    │
                          ┌──────▼───────┐   │ prompt→     │
                          │  Method      │   │ think→      │
                          │  Router      │   │ act→        │
                          └──────┬───────┘   │ observe→    │
                                 │           │ memory→     │
                          ┌──────▼───────┐   │ summarize   │
                          │  Agent Loop  │   └──────┬──────┘
                          │  (Think/Act/ │          │
                          │   Observe)   │   ┌──────▼───────┐
                          └──────┬───────┘   │  LLM         │
                                 │           │  Providers   │
                          ┌──────▼───────┐   │  (22 types)  │
                          │  Tool        │   └──────────────┘
                          │  Registry    │
                          │  (50+ tools) │
                          └──────┬───────┘
                          ┌──────▼───────┐
                          │  Store Layer │
                          │  (PG/SQLite) │
                          └──────────────┘
```

### 8-Stage Agent Pipeline

| Stage | Phase | Description |
|-------|-------|-------------|
| ContextStage | Setup | Inject agent/user/workspace context, compute per-user files, calculate token overhead |
| ThinkStage | Iteration | Build system prompt, filter tools by policy, call LLM |
| PruneStage | Iteration | Context pruning (2-pass: soft trim → hard clear), memory flush on compaction |
| ToolStage | Iteration | Execute tool calls (parallel goroutines for multiple calls) |
| ObserveStage | Iteration | Process tool results, append to messages |
| CheckpointStage | Iteration | Track iteration state, check loop exit conditions |
| FinalizeStage | Finalize | Sanitize output, flush messages, update session metadata |

### Key Internal Modules

| Module | Description |
|--------|-------------|
| `internal/gateway/` | WebSocket + HTTP server, client lifecycle, method router (64+ RPC methods) |
| `internal/agent/` | Agent loop (think/act/observe), router, resolver, system prompt builder |
| `internal/pipeline/` | 8-stage pluggable agent pipeline implementation |
| `internal/providers/` | LLM adapters: Anthropic (native HTTP+SSE), OpenAI-compatible (12+), ACP (JSON-RPC 2.0) |
| `internal/tools/` | Tool registry with 50+ built-in tools, policy engine, MCP bridge |
| `internal/channels/` | Channel adapters: Telegram, Discord, Feishu, Zalo, WhatsApp, Slack |
| `internal/store/` | Dual-DB store interfaces (PostgreSQL + SQLite via Dialect pattern) |
| `internal/scheduler/` | 4-lane concurrency (main/subagent/team/cron) with per-session queues |
| `internal/vault/` | Knowledge Vault: wikilinks, hybrid BM25+vector search |
| `internal/consolidation/` | Memory workers: episodic, semantic, dreaming, dedup |
| `internal/hooks/` | Lifecycle hooks: 7 events, sync/async, SSRF-hardened HTTP handlers |

## Provider Ecosystem

22 provider types unified through a single adapter interface with capability-based routing and encrypted API keys:

| Provider | Type | Notes |
|----------|------|-------|
| Anthropic | Native HTTP+SSE | Prompt caching, extended thinking |
| OpenAI | OpenAI-compatible | Azure-compatible |
| OpenRouter | Routing | Route to ~200+ models via single API key |
| Google Gemini | OpenAI-compatible | Extended thinking |
| Groq | OpenAI-compatible | Fast inference |
| DeepSeek | OpenAI-compatible | — |
| Mistral | OpenAI-compatible | — |
| xAI (Grok) | OpenAI-compatible | — |
| MiniMax | OpenAI-compatible | — |
| Vertex AI | OpenAI-compatible | GCP OAuth2 + service account |
| Ollama / Ollama Cloud | Local / API | No API key for local |
| Claude CLI / Codex | Subprocess | Runs `claude` or `codex` binary |
| ACP (Agentic Claude Protocol) | JSON-RPC 2.0 | Orchestrates Claude Code, Codex CLI, Gemini CLI as subprocess agents |
| Custom / Others | OpenAI-compatible | Any OpenAI-compatible endpoint; also Suno, Novita AI, YesScale |

## Channel Ecosystem

12 messaging channels with per-channel DM/group policies, media handling, and streaming:

| Channel | Protocol | Features |
|---------|----------|----------|
| Telegram | Bot API | Forum topics, STT, bot commands, streaming, reactions, link previews, per-group agent bindings |
| Discord | Bot API | Streaming, voice messages (STT), media handling |
| WhatsApp | Native (whatsmeow) | QR auth, media, group support, no WhatsApp Business API dependency |
| Slack | Socket Mode | Thread context, native streaming, debounce, reaction levels |
| Zalo OA | Official API | Vietnamese messaging platform |
| Zalo Personal | Personal API | Session-based credentials, group support |
| Feishu / Lark | API | Streaming cards, media |
| Larksuite | API | International version of Feishu |
| WebSocket | Raw WS | 64+ RPC methods, full gateway control |
| Browser Pairing | Proxy | Pair browser sessions to gateway |
| Pancake | API | Vietnamese POS/messaging |
| Bitrix24 | API | CRM/messaging platform |

## Configuration

GoClaw uses JSON5 config files with environment variable overlay and hot-reload via `fsnotify` (300ms debounce).

**Required environment variables:**
- `GOCLAW_GATEWAY_TOKEN` — Bearer token for API/WS auth
- `GOCLAW_ENCRYPTION_KEY` — AES-256-GCM key for credential encryption
- `GOCLAW_POSTGRES_DSN` — PostgreSQL connection string

**Key config sections:**
- `gateway` — host, port, token, rate limits, CORS, prompt injection handling
- `agents.defaults` — default provider, model, temperature, max tool iterations
- `agents.list` — per-agent overrides for model, tools, workspace, skills
- `memory` — embedding provider/model, vector/text search weights, chunk sizes
- `compaction` — context compaction thresholds, memory flush
- `context_pruning` — soft trim and hard clear policies for tool results
- `subagents` — max concurrency, spawn depth, TTL
- `sandbox` — Docker isolation: memory, CPU, network, timeout
- `tools` — tool profiles, allow/deny lists, exec approval, MCP servers
- `channels` — per-channel: token, DM/group policy, allowlist, media limits

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

Full comparison: Desktop supports 5 agents/1 team with SQLite; Standard supports unlimited agents/teams with PostgreSQL + pgvector.

## API Surface

- **REST API** — `POST /v1/chat/completions` (OpenAI-compatible), `/v1/agents`, `/v1/skills`, `/v1/traces`, `/v1/mcp`, webhooks
- **WebSocket** — `/ws` with 64+ RPC methods: `connect`, `chat.send`, `agents.*`, `sessions.*`, `skills.*`, `cron.*`, `traces.*`, `config.*`, `pairing.*`
- **Webhooks** — Trigger agents or send channel messages from external systems without gateway token; Bearer + HMAC auth, async callbacks with exponential retry
- **OpenAI-compatible chat/completions** — Pass `goclaw:<agent-key>` as model name

## Related

- [[openclaw]] — TypeScript-based agent gateway (inspired GoClaw's architecture)
- [[hermes-agent]] — Python-based agent gateway
- [[alphaclaw]] — Setup UI and gateway manager for OpenClaw
- [[tank-os]] — Fedora bootc deployment OS
- [[mission-control]] — Dashboard and management plane for agent gateways
- [[goclaw]] — MCP implementation details (client + bridge server)
- [[podman]] / [[podman-compose]] — Container runtime for Quadlet deployment
- [[materia]] — Alternative agent framework
- [[nanobot]] — Alternative agent framework
