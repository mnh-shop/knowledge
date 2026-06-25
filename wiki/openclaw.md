---
name: openclaw
tags: [openclaw, agent-gateway, wiki]
description: OpenClaw — Personal AI Assistant
---

# OpenClaw — Personal AI Assistant

| Field | Value |
|---|---|
| **Origin** | [openclaw/openclaw](https://github.com/openclaw/openclaw) |
| **License** | MIT |
| **Stack** | TypeScript, Node.js 22.19+/24, pnpm workspace |
| **Source** | `sources/openclaw/` |
| **Wanted** | Personal AI assistant on your own devices — full agent platform with multi-channel messaging, ACP, MCP, Live Canvas, plugin system |

## What it is

OpenClaw is a **personal AI assistant** you run on your own devices. It answers you on the channels you already use (WhatsApp, Telegram, Discord, iMessage, Signal, Slack, IRC, Matrix, and 20+ more). The Gateway is the control plane — it routes inbound messages to isolated agent workspaces, manages sessions, runs tools, and exposes ACP and MCP surfaces for external agent communication.

At architecture level, OpenClaw and [[hermes-agent]] occupy the same category: **agent gateways**. Both act as the runtime/control-plane for personal AI agents with multi-platform messaging, plugin systems, and external protocol surfaces (ACP, MCP). They are likely competing implementations of the same concept, not complementary systems.

**Key differentiator vs Hermes:** OpenClaw has a larger official channel ecosystem (30+ vs ~20), a Live Canvas (A2UI) for agent-driven visual workspaces, and is built as a single-instance personal assistant rather than a multi-platform gateway that also supports workspaces. Hermes, by contrast, has a dedicated workspace/web dashboard ([[hermes-workspace]]) and a startup architect skill ([[hermes-startup-architect]]).

## Architecture

### Core Runtime

```
Runtime: Node 24 (recommended) or Node 22.19+
Package manager: pnpm workspace
CLI: npm install -g openclaw@latest → openclaw command
Daemon: launchd/systemd user service (via openclaw onboard --install-daemon)
```

### Key Source Directories (`src/`)

| Directory | Purpose |
|---|---|
| `gateway/` | Control plane — auth, sessions, commands, agent lifecycle |
| `agents/` | Agent management, spawning, per-workspace isolation |
| `channels/` | Channel bridge, channel-server, protocol adapters |
| `mcp/` | MCP server — channel-bridge, plugin-tools-serve, stdio-server |
| `acp/` | Agent Communication Protocol — approval-classifier, event-ledger, client, control-plane |
| `plugin-sdk/` | Public SDK for building plugins and extensions |
| `plugins/` | Plugin loader, activation, state |
| `extensions/` | Bundled official plugins (WhatsApp, Telegram, Discord, Slack, etc.) |
| `skills/` | Skills system |
| `tools/` | Tool system (browser, canvas, cron, nodes, etc.) |
| `memory/` | Memory subsystem |
| `llm/` | LLM runtime and model integration |
| `config/` | Configuration management |
| `cli/` | CLI command definitions |
| `state/` | State management |
| `security/` | Security controls |
| `ui/` | Control UI |

### Multi-Channel Support

30+ messaging channels including: WhatsApp, Telegram, Slack, Discord, Google Chat, Signal, iMessage, IRC, Microsoft Teams, Matrix, Feishu, LINE, Mattermost, Nextcloud Talk, Nostr, Synology Chat, Tlon, Twitch, Zalo, Zalo Personal, WeChat, QQ, WebChat. Each is a plugin under `extensions/`.

### State and Storage

- **Shared state DB**: `state/openclaw.sqlite` — global runtime state
- **Per-agent DB**: `agents/<agentId>/agent/openclaw-agent.sqlite` — agent-scoped data
- **Config file**: `~/.openclaw/openclaw.json`
- **Secrets**: `~/.openclaw/credentials/`
- **Cache/transient state**: SQLite — no JSON/TXT sidecar files in runtime

## Interfaces

### ACP (Agent Communication Protocol)

OpenClaw implements an Agent Communication Protocol surface at `src/acp/`:

- **Approval Classifier**: `approval-classifier.ts` — determines whether agent actions need human approval
- **Event Ledger**: `event-ledger.ts` — tamper-proof audit trail of agent events
- **Control Plane**: `control-plane/` — cross-agent coordination
- **Client**: `client.ts` — ACP client for connecting to other agent systems
- **Commands**: `commands.ts` — ACP command definitions
- **Conversation ID**: `conversation-id.ts` — stable conversation identity

This means OpenClaw can participate in the same ACP ecosystem as Hermes — they could theoretically route agent-to-agent operations through the same protocol.

### MCP (Model Context Protocol)

OpenClaw implements MCP at `src/mcp/`:

- **Channel Bridge**: `channel-bridge.ts` — MCP tools bridge to messaging channels
- **Plugin Tools Serve**: `plugin-tools-serve.ts` — serve plugin tools as MCP tools
- **Tools STDIO Server**: `tools-stdio-server.ts` — stdio-based MCP server
- **OpenClaw Tools Serve**: `openclaw-tools-serve.ts` — expose MCP tools as OpenClaw tools

### Gateway Protocol

The Gateway runs on port **18789** by default (loopback bind). Health endpoints: `/healthz`, `/readyz`, `/health`, `/ready`. Supports Tailscale integration and remote exposure.

### CLI

```
openclaw gateway ...    — gateway management
openclaw agent ...      — agent operations
openclaw message ...    — message sending
openclaw secrets ...    — credential management
openclaw browser ...    — browser automation
openclaw nodes ...      — node operations
openclaw onboard        — guided setup wizard
openclaw doctor         — system diagnostics
openclaw dashboard      — launch control UI
openclaw devices        — device management
```

## Deployment

### npm Global Install (dev/personal)

```bash
npm install -g openclaw@latest
openclaw onboard --install-daemon
```

### Docker (production)

OpenClaw publishes multi-stage Docker builds with a minimal runtime image (~183MB). Base: `node:24-bookworm-slim`. Runs as `node` (uid 1000). Health check every 3 minutes.

```bash
# From source:
docker build -t openclaw .

# Or use published image:
docker pull ghcr.io/openclaw/openclaw:latest
```

### Container host management

- **System**: OpenClaw publishes a `service` command for systemd user service
- **macOS**: launchd daemon via `openclaw onboard`
- **Tank OS**: Fedora bootc image with rootless Podman (see [[tank-os]])

### Requirements

- No external database needed (SQLite only)
- No Redis needed
- Node 24 or Node 22.19+
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
| **Channels** | 30+ | ~20 |
| **ACP** | ✅ (`src/acp/`) | ✅ (ACP server + client) |
| **MCP** | ✅ (`src/mcp/`) | ✅ (MCP client + server) |
| **Gateway** | Port 18789, health endpoints | Ports vary by gateway |
| **Storage** | SQLite (shared + per-agent) | SQLite (state), files (cache) |
| **Plugin System** | Plugin SDK (`src/plugin-sdk/`), extensions dir | Plugin system, skills |
| **UI** | Built-in control UI | Hermes Workspace (separate project) |
| **Live Canvas** | ✅ Built-in (A2UI) | ❌ (via workspace) |
| **Daemon** | Systemd/launchd via onboard | Systemd via hermes-install |
| **Docker** | Multi-stage, 183MB, slim | Docker published |
| **Sponsors** | OpenAI, GitHub, NVIDIA, Vercel, Convex | Nous Research |

## Domain docs & assets

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
- [[openclaw-profile]] -- Quick reference profile
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
