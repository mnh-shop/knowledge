---
name: openclaw
tags: [acp, agent, agent-gateway, bootc, cli, container, dashboard, docker, git, live-canvas, mcp, messaging, openclaw, orchestration, personal-assistant, podman, quadlet, security, storage, systemd, typescript, wiki]
description: OpenClaw — Personal AI Assistant
source: sources/openclaw/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# OpenClaw — Personal AI Assistant

| Field | Value |
|---|---|
| **Origin** | [openclaw/openclaw](https://github.com/openclaw/openclaw) |
| **License** | MIT |
| **Stack** | TypeScript, Node.js 22.22.3+ / 24.15.0+ / 25.9.0+ (Node 26 recommended), pnpm workspace |
| **Source** | `sources/openclaw/` |
| **Wanted** | Personal AI assistant on your own devices — full agent platform with multi-channel messaging, ACP, MCP, Live Canvas, plugin system |

## What it is

OpenClaw is a **personal AI assistant** you run on your own devices. It answers you on the channels you already use (WhatsApp, Telegram, Discord, iMessage, Signal, Slack, IRC, Matrix, and 20+ more). The Gateway is the control plane — it routes inbound messages to isolated agent workspaces, manages sessions, runs tools, and exposes ACP and MCP surfaces for external agent communication.

At architecture level, OpenClaw and [[hermes-agent]] occupy the same category: **agent gateways**. Both act as the runtime/control-plane for personal AI agents with multi-platform messaging, plugin systems, and external protocol surfaces (ACP, MCP). They are likely competing implementations of the same concept, not complementary systems.

**Key differentiator vs Hermes:** OpenClaw has a larger official channel ecosystem (~30-32 channels vs ~20), a Live Canvas (A2UI) for agent-driven visual workspaces, and is built as a single-instance personal assistant rather than a multi-platform gateway that also supports workspaces. Hermes, by contrast, has a dedicated workspace/web dashboard ([[hermes-workspace]]) and a startup architect skill ([[hermes-startup-architect]]).

## Architecture

### Core Runtime

```
Runtime: Node 26 (recommended); floors 22.22.3+ / 24.15.0+ / 25.9.0+
Package manager: pnpm workspace
CLI: npm install -g openclaw@latest → openclaw command
Daemon: openclaw daemon sub-CLI — launchd (macOS), systemd (Linux), schtasks (Windows)
```

### Key Source Directories (`src/`)

| Directory | Purpose |
|---|---|
| `gateway/` | Control plane — auth, sessions, commands, agent lifecycle |
| `agents/` | Agent management, spawning, per-workspace isolation; **tool system lives in `agents/tools/` (~100+ files)** |
| `channels/` | Channel framework — plugin registry, adapters, bindings, catalog |
| `mcp/` | MCP surface — client registry + channel MCP server (20 files including tests) |
| `acp/` | Agent Communication Protocol — server bridge, translator, client, approval-classifier, event-ledger, control-plane (~100 files) |
| `plugin-sdk/` | Public SDK for building plugins and extensions |
| `plugins/` | Plugin loader, activation, state |
| `extensions/` | Bundled official plugins (channels, providers, memory, skills, voice, etc.) |
| `skills/` | Skills system — loading, discovery, workshop, ClawHub |
| `tools/` | **Only `types.ts`** — the tool system itself lives in `src/agents/tools/` |
| `memory/` | **Only `root-memory-files.ts`** — the memory subsystem lives in `src/memory-host-sdk/` + `extensions/memory-core/` |
| `llm/` | LLM runtime and model integration |
| `config/` | Configuration management (JSON5, hot reload) |
| `cli/` | CLI command definitions (~55 commands) |
| `state/` | State management |
| `security/` | Security controls |
| `ui/` | Control UI |
| `daemon/` | Gateway service management — launchd/systemd/schtasks implementations |
| `tasks/` | TaskFlow — cron, detached/background tasks, task registry |
| `commitments/` | Standing commitments system |
| `memory-host-sdk/` | Memory host SDK — event store, QMD engine, dreaming, queries |

### Multi-Channel Support

The README advertises **"25+ channels"**; the actual ecosystem is roughly 30-32 channels, tiered:

- **Core channels (not extension plugins):** Telegram, iMessage, and the built-in WebChat are part of the core runtime (`src/channels/`), not installable extensions.
- **~23 official channel plugins in `extensions/`:** Buzz, ClickClack, Discord, Feishu, Google Chat, IRC, LINE, Matrix, Mattermost, Microsoft Teams, Nextcloud Talk, Nostr, QQ Bot, Raft, Signal, Slack, SMS/Twilio, Synology Chat, Tlon, Twitch, WhatsApp, Zalo, Zalo Personal.
- **External npm plugins (not in this repo):** WeChat (`@tencent-weixin/openclaw-weixin`), Yuanbao, Zalo ClawBot, WeCom.
- **Voice/meeting extensions:** `voice-call`, `google-meet`, `teams-meetings`, `zoom-meetings`.

### Memory System

Memory is a first-class subsystem, not a single concept:

- **5-tier memory model:** Instructions / Curated Core / Episodic / Prospective / Review.
- **Dreaming consolidation:** periodic offline consolidation (`dreaming.ts`, `dreaming-consolidation.ts`) that distills experiences into durable memories, with **REM** support (`cli-rem.runtime.ts`).
- **QMD engine:** query/merge/decay engine (`src/memory-host-sdk/engine-qmd.ts`) over a typed event store (`event-store.ts`, `event-types.ts`).
- **Surfaces:** `MEMORY.md`, `USER.md`, and `DREAMS.md` files per agent.
- **Implementation split:** `src/memory-host-sdk/` (host SDK, ~12 modules) + `extensions/memory-core/` (89+ file plugin: manager, embeddings, hybrid search, temporal decay, migration) + companion plugins `active-memory`, `memory-lancedb`, `memory-wiki`.

### Skills

- **Format:** each skill is a directory with a `SKILL.md` frontmatter file (name + description).
- **6-tier loading precedence:** workspace > `.agents/skills` > `~/.agents/skills` > managed > bundled > `extraDirs`.
- **ClawHub marketplace:** search/install/verify/update/publish skills via the bundled `clawhub` skill.
- **Skill Workshop:** `src/skills/workshop/` — auto-apply, curator, experience review.
- **Scale:** ~60 bundled skills in the repo's `skills/` directory (51 `SKILL.md` files; 117 `SKILL.md` files repo-wide counting extension skill sets).

### State and Storage

- **Shared state DB**: `state/openclaw.sqlite` — global runtime state
- **Per-agent DB**: `agents/<agentId>/agent/openclaw-agent.sqlite` — agent-scoped data
- **Config file**: `~/.openclaw/openclaw.json` (JSON5, hot-reloaded)
- **Secrets**: `~/.openclaw/credentials/` is now **legacy** — model auth profiles live in `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- **Cache/transient state**: SQLite — no JSON/TXT sidecar files in runtime

## Interfaces

### ACP (Agent Communication Protocol)

OpenClaw implements an Agent Communication Protocol surface at `src/acp/` (~100 files, 57 non-test) using `@agentclientprotocol/sdk` with `PROTOCOL_VERSION` 4:

- **Core bridge**: `server.ts` — ACP stdio server bridging Agent Client Protocol to the Gateway
- **Translator**: `translator.ts` — maps ACP sessions/messages/events to gateway sessions, with replay and session-list/update support
- **Client**: `client.ts` — ACP client for connecting to other agent systems
- **Approval Classifier**: `approval-classifier.ts` — determines whether agent actions need human approval
- **Event Ledger**: `event-ledger.ts` — SQLite-backed tamper-proof audit trail of agent events, with session rehydration and hard caps (200 sessions / 5000 events per session / 16MB serialized)
- **Control Plane**: `control-plane/` — cross-agent coordination (session manager, failover, identity reconcile)
- **Commands**: `commands.ts` — ACP command definitions
- **Conversation ID**: `conversation-id.ts` — stable conversation identity

This means OpenClaw can participate in the same ACP ecosystem as Hermes — they could theoretically route agent-to-agent operations through the same protocol.

### MCP (Model Context Protocol)

MCP is **bidirectional** — OpenClaw is both an MCP client and an MCP server:

- **As a client:** a registry of external MCP servers configured under `mcp.servers`, managed via `openclaw mcp add/set/list/show/status/probe/doctor/configure/login/logout/reload/unset`. The `mcp` CLI provides OAuth auth, diagnostics, and server testing.
- **As a server:** `openclaw mcp serve` exposes OpenClaw channel tools and agent capabilities to external MCP clients. Implementation in `src/mcp/` (20 files including tests): `channel-bridge.ts` (MCP tools ↔ messaging channels), `channel-server.ts`, `plugin-tools-serve.ts` (serve plugin tools as MCP tools), `tools-stdio-server.ts` (stdio-based MCP server), `openclaw-tools-serve.ts` (expose MCP tools as OpenClaw tools), plus `codex-supervision-tools-serve.ts`.

### Gateway Protocol

The Gateway runs on port **18789** by default (loopback bind). Health endpoints: `/healthz`, `/readyz`, `/health`, `/ready`. WebSocket protocol **v4** (`@openclaw/gateway-protocol`, `PROTOCOL_VERSION = 4`). Supports **Tailscale** integration plus the `openclaw dns` sub-CLI for remote exposure.

### CLI

The CLI surface is ~55 commands. Core commands: `setup`, `onboard`, `configure`, `config`, `claws`, `backup`, `migrate`, `doctor`, `dashboard`, `reset`, `uninstall`, `message`, `mcp`, `transcripts`, `agent`, `agents`, `status`, `health`, `audit`, `sessions`, `commitments`, `tasks`.

Sub-CLIs and specialized groups: `acp`, `gateway`, `daemon`, `logs`, `system`, `models`, `promos`, `infer`, `capability`, `approvals`, `exec-approvals`, `exec-policy`, `nodes`, `devices`, `users`, `node`, `worker`, `sandbox`, `fleet`, `worktrees`, `attach`, `tui`, `terminal`, `chat`, `cron`, `dns`, `docs`, `qa`, `proxy`, `hooks`, `webhooks`, `qr`, `clawbot`, `pairing`, `plugins`, `channels`, `directory`, `security`, `secrets`, `skills`, `update`, `completion`, `browser`.

### Automation

- **Cron:** scheduled jobs (`openclaw cron`, `src/cron/`) with history retention and continuation cleanup.
- **Webhooks:** inbound/outbound webhook integration (`openclaw webhooks`).
- **Hooks:** plugin hook phases — `before-tool-call`, `before-agent-reply`, `after-tool-call` (`src/plugins/hook-types.ts`).
- **TaskFlow:** `src/tasks/` — task registry, detached/background task contracts, harness-owned subagent tasks.
- **Standing intents & commitments:** `src/commitments/` — extraction, storage, model selection; commitments surface as first-class CLI commands.

## Deployment

### npm Global Install (dev/personal)

```bash
npm install -g openclaw@latest
openclaw onboard --install-daemon
```

### Docker (production)

OpenClaw publishes multi-stage Docker builds (a minimal runtime image without build tools, source code, or Bun — the exact image size is **not** documented in the repo or Dockerfile, so any specific size figure is approximate/external). Base: `node:24-bookworm-slim`. Runs as `node` (uid 1000). Health check every 3 minutes. Entrypoint: `tini`.

**Registries:** primary on GHCR (`ghcr.io/openclaw/openclaw`) plus a Docker Hub mirror (`openclaw/openclaw`). **Variant tags:** `slim`, `*-browser`, and `extended-stable` release channel. **Default images bundle** the `codex` and `diagnostics-otel` plugins.

```bash
# From source:
docker build -t openclaw .

# Or use published image:
docker pull ghcr.io/openclaw/openclaw:latest
```

### Container host management

- **Linux**: systemd user service via the `openclaw daemon` sub-CLI (`openclaw daemon install/start/stop/restart/status`)
- **macOS**: launchd daemon via `openclaw daemon`
- **Windows**: Scheduled Task (schtasks) via `openclaw daemon`
- **Tank OS**: Fedora bootc image with rootless Podman (see [[tank-os]])

### Requirements

- No external database needed (SQLite only)
- No Redis needed
- Node 22.22.3+ / 24.15.0+ / 25.9.0+ (Node 26 recommended)
- npm/pnpm/bun for install

## Compatibility with Core Systems

| System | Can it work with OpenClaw? | How |
|---|---|---|
| [[hermes-agent]] | ⚠️ Competing | Both are agent gateways with ACP + MCP. They serve the same role and likely shouldn't both be in one stack. However, their ACP implementations could theoretically interop for cross-platform agent-to-agent operations. |
| [[agentfield]] | ✅ | OpenClaw exposes MCP that AgentField could consume. AgentField's `app.harness()` could dispatch to OpenClaw agents. |
| [[n8n]] | ✅ | n8n webhooks could trigger OpenClaw actions. OpenClaw MCP tools could call n8n workflows. Same pattern as Hermes + n8n. |

## Comparison to Hermes

| Dimension | OpenClaw | Hermes Agent |
|---|---|---|
| **License** | MIT | MIT |
| **Language** | TypeScript | Python |
| **Channels** | ~30-32 (tiered: core + 23 official plugins + external) | ~20 |
| **ACP** | ✅ (`src/acp/`, ~100 files) | ✅ (ACP server + client) |
| **MCP** | ✅ (client registry + `mcp serve`) | ✅ (MCP client + server) |
| **Gateway** | Port 18789, health endpoints, WS protocol v4 | Ports vary by gateway |
| **Storage** | SQLite (shared + per-agent) | SQLite (state), files (cache) |
| **Plugin System** | Plugin SDK (`src/plugin-sdk/`), extensions dir | Plugin system, skills |
| **UI** | Built-in control UI | Hermes Workspace (separate project) |
| **Live Canvas** | ✅ Built-in (A2UI) | ❌ (via workspace) |
| **Daemon** | `openclaw daemon` — launchd/systemd/schtasks | Systemd via hermes-install |
| **Docker** | Multi-stage, GHCR + Docker Hub mirror, slim | Docker published |
| **Sponsors** | OpenAI, GitHub, NVIDIA, Vercel, Blacksmith, Convex | Nous Research |

## Related

- [Architecture](domains/architecture/openclaw-architecture.md) — 753-line deep dive: 8-phase startup, WebSocket runtime, A2UI, plugins
- [API](domains/api/openclaw-api.md) — 90+ RPC methods, WebSocket streaming, TypeScript/Python clients
- [MCP Implementation](domains/mcp/openclaw-mcp-implementation.md) — 3 MCP server surfaces (channel bridge, plugin tools, built-in tools)
- [ACP Implementation](domains/acp/openclaw-acp-implementation.md) — Stdio-to-Gateway bridge, 11 ACP RPCs, security model
- [Deployment](domains/deployment/openclaw-deployment.md) — Rootless Podman, Docker Compose, secrets, troubleshooting
- [MCP Server Config](assets/mcp-servers/openclaw-mcp-server.md) — Tool parameters, Cursor IDE config, Bun runtime
- [ACP Agent Config](assets/acp-agents/openclaw-acp-agent.md) — 7 registration methods, CLI flags, REPL pattern
- [Quadlet Config](assets/deployment/openclaw-quadlet.md) — Complete pod networking, Ollama + Qdrant + PostgreSQL stack

## Related

- [[openclaw-architecture]] -- System architecture deep dive
- [[openclaw-api]] -- REST and WebSocket API reference
- [[openclaw-mcp-implementation]] -- MCP server implementation details
- [[openclaw-acp-implementation]] -- ACP protocol implementation details
- [[openclaw-deployment]] -- Full deployment and operations guide
- [[openclaw-mcp-server]] -- MCP server asset configuration
- [[openclaw-acp-agent]] -- ACP agent asset registration
- [[openclaw-quadlet]] -- Quadlet deployment patterns
- [[hermes-profiles]] -- Quick reference profile
- [[openclaw.codegraph-verify]] -- Codegraph verification document
- [[tank-os]] — Fedora bootc image to deploy OpenClaw as a bootable appliance
- [[hermes-agent]] — Competing agent gateway (Python, MIT)
- [[mission-control]] — Dashboard that can connect to OpenClaw as a gateway
- [[agentfield]] — Control plane that could orchestrate OpenClaw agents via MCP
- [[n8n]] — Workflow engine that can be called from OpenClaw MCP tools

## Cross-project

- [[hermes-agent]] — Competing agent gateway (Python, MIT)
- [[agentfield]] — Control plane that orchestrates OpenClaw agents via MCP
- [[mission-control]] — Dashboard that monitors OpenClaw gateway
- [[podman]] — Container runtime for OpenClaw deployment
- [[tank-os]] — Fedora bootc image packaging OpenClaw
- [[clawpier]] — Desktop GUI for managing OpenClaw Docker containers
- [[buildah]] — Builds container images for OpenClaw channels/plugins
- [[nix-podman-stacks]] — Declarative Nix-based container deployment
- [[sablier]] — Scale-to-zero for OpenClaw services
- [[gogs]] — Self-hosted Git backend for OpenClaw configuration
- [[hermzner]] — Comparable deployment blueprint (Hermes-focused)
- [[crun-vm]] — Extra isolation for OpenClaw deployment on bare metal
