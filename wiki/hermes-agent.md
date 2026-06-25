---
name: hermes-agent
tags: [hermes, wiki, typescript, agent-gateway, messaging, multi-platform]
description: Wiki entry for Hermes Agent: self-improving AI agent by Nous Research with multi-platform messaging (MIT)
---

# Hermes Agent

| Field | Value |
|---|---|
| **Origin** | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) |
| **License** | MIT |
| **Source** | `sources/hermes-agent/` |
| **Repomix** | `raw/hermes-agent/hermes-agent.xml` (35MB) |
| **Codegraph** | `graphs/hermes-agent/` (3,726 files) |
| **Profile** | `sources/hermes-agent/AGENTS.md` |

## What is it?

A self-improving personal AI agent built by Nous Research. Runs the same
core across CLI, TUI, Electron desktop, and ~20+ messaging platforms
(Telegram, Discord, Slack, WhatsApp, Signal, etc.).

Key features:
- Multi-platform messaging gateway
- Closed learning loop (memory, skills, self-improvement)
- Scheduled automations (cron)
- Subagent delegation and parallelization
- MCP client + server
- ACP server for editor integration (Zed, Claude Code, etc.)
- Six terminal backends (local, Docker, SSH, Singularity, Modal, Daytona)

---

## Where to find things

### Architecture & Design

| What | Where |
|---|---|
| Full architecture | [[hermes-agent-architecture]] (`domains/architecture/`) |
| Design principles | `sources/hermes-agent/AGENTS.md` |
| Source map | `domains/architecture/hermes-agent-architecture.md` (#key-source-map) |

### MCP

Hermes is both an MCP client (consumes MCP servers) and an MCP server
(messaging bridge for other agents).

| What | Where |
|---|---|
| **MCP Server (bridge)** | [[hermes-mcp-serve]] (`assets/mcp-servers/`) |
| **MCP Client (consumer)** | `sources/hermes-agent/tools/mcp_tool.py` → `MCPServerTask` |
| MCP implementation patterns | [[hermes-mcp-implementation]] (`domains/mcp/`) |
| MCP OAuth | `sources/hermes-agent/tools/mcp_oauth_manager.py` |
| Optional MCP manifests | `sources/hermes-agent/optional-mcps/` (linear, n8n, unreal-engine) |
| CLI | `hermes mcp serve` → `hermes_cli/main.py` `cmd_mcp` |

**Important:** The MCP server (`mcp_serve.py`) is a *messaging bridge*,
not a generic tool exporter. It exposes 10 tools for listing/sending
conversations — matching OpenClaw's 9-tool surface. It does NOT expose
Hermes's 90+ model tools as MCP tools.

### ACP

Hermes is an ACP server (driven by editors) and has an ACP client (talks
to Copilot).

| What | Where |
|---|---|
| **ACP Server** | [[hermes-acp-agent]] (`assets/acp-agents/`) |
| ACP implementation patterns | [[hermes-acp-implementation]] (`domains/acp/`) |
| ACP server source | `sources/hermes-agent/acp_adapter/server.py` → `HermesACPAgent` |
| ACP agent registry | `sources/hermes-agent/acp_registry/agent.json` |
| ACP client (Copilot) | `sources/hermes-agent/agent/copilot_acp_client.py` |
| CLI | `hermes acp serve` → `hermes_cli/main.py` `cmd_acp` |

### Gateway (Messaging Platforms)

The gateway connects ~20+ messaging platforms through a unified adapter
pattern.

| What | Where |
|---|---|
| **Platform adapters** | [[hermes-gateway-platforms]] (`assets/api-clients/`) |
| Gateway API architecture | [[hermes-gateway-api]] (`domains/api/`) |
| Base adapter class | `gateway/platforms/base.py` → `BasePlatformAdapter` |
| Gateway bootstrap | `gateway/run.py` |
| Stream dispatch | `gateway/stream_dispatch.py` → `GatewayEventDispatcher` |
| Platform registry | `gateway/platform_registry.py` → `PlatformRegistry` |
| Webhook adapter | `gateway/platforms/webhook.py` → `WebhookAdapter` |
| Plugin platforms | `plugins/platforms/` (IRC, SMS, LINE, Ntfy, Raft, Photon) |

### Core Agent

| What | Source |
|---|---|
| Conversation loop | `agent/conversation_loop.py` → `AIAgent.run_conversation()` |
| Tool dispatch | `agent/tool_dispatch_helpers.py` |
| Tool executor | `agent/tool_executor.py` |
| Memory manager | `agent/memory_manager.py` |
| Context compressor | `agent/context_compressor.py` |
| System prompt | `agent/prompt_builder.py` |
| Prompt caching | `agent/prompt_caching.py` |
| Model adapters | `agent/anthropic_adapter.py`, `agent/gemini_native_adapter.py`, `agent/bedrock_adapter.py` |
| Tracks | `agent/trajectory.py` |

### Skills System

| What | Source |
|---|---|
| Skills hub (search) | `tools/skills_hub.py` (multiple sources: GitHub, Claude Marketplace, LobeHub, Browse.sh, etc.) |
| Skills tool | `tools/skills_tool.py` |
| Skill manager | `tools/skill_manager_tool.py` |
| Skill bundles | `tools/skills_hub.py` → `SkillBundle` |
| Built-in skills | `skills/` (18 categories) |
| Optional skills catalog | `optional-skills/` (19 categories) |

### Plugin System

| What | Source |
|---|---|
| Browser | `plugins/browser/` |
| Context engine | `plugins/context_engine/` |
| Cron providers | `plugins/cron_providers/` |
| Dashboard auth | `plugins/dashboard_auth/` |
| Memory | `plugins/memory/` |
| Model providers | `plugins/model-providers/` |
| Observability | `plugins/observability/` |
| Platforms | `plugins/platforms/` (IRC, SMS, LINE, Ntfy, Raft, Photon) |
| Security | `plugins/security-guidance/` |

### Tools (90+ model tools)

All tools loaded on every API call. See `tools/` directory.

Key tools:

| Tool | Source |
|---|---|
| Browser | `tools/browser_tool.py`, `tools/browser_cdp_tool.py` |
| Code execution | `tools/code_execution_tool.py` |
| Computer use | `tools/computer_use/`, `tools/computer_use_tool.py` |
| Delegation | `tools/delegate_tool.py`, `tools/async_delegation.py` |
| File operations | `tools/file_tools.py`, `tools/file_operations.py` |
| MCP client | `tools/mcp_tool.py` |
| Memory | `tools/memory_tool.py` |
| Skills | `tools/skills_hub.py`, `tools/skills_tool.py` |
| Terminal | `tools/terminal_tool.py` |
| Vision | `tools/vision_tools.py` |
| Web search | `tools/web_tools.py` |
| Cron | `tools/cronjob_tools.py` |
| Voice/TTS | `tools/transcription_tools.py`, `tools/tts_tool.py` |
| Image gen | `tools/image_generation_tool.py` |
| LinkedIn/Twitter | `tools/x_search_tool.py` |

### Deployment

| What | Where |
|---|---|
| Dockerfile | `sources/hermes-agent/Dockerfile` |
| Docker Compose | `sources/hermes-agent/docker-compose.yml` |
| Nix | `sources/hermes-agent/flake.nix` |
| Script | `sources/hermes-agent/setup-hermes.sh` |
| Install (end-user) | `curl -fsSL https://hermes-agent.nousresearch.com/install.sh \| bash` |
| **Deployment guide** | `domains/deployment/hermes-agent-deployment.md` |
| **Quadlet** | `assets/deployment/hermes-agent-quadlet.md` |

### Desktop & UI

| What | Source |
|---|---|
| Electron desktop | `apps/desktop/` |
| TUI | `ui-tui/` |
| Web | `web/` |
| Documentation website | `website/` |

---

## CLI reference

The CLI is the main entry point (`hermes_cli/main.py`, ~12k lines). Major
commands:

| Command | What it does |
|---|---|
| `hermes` | Start chat (CLI or TUI) |
| `hermes model` | Switch models/providers |
| `hermes mcp` | MCP management (`serve`, etc.) |
| `hermes acp` | ACP management (`serve`, etc.) |
| `hermes gateway` | Start messaging gateway |
| `hermes skills` | Install/browse skills |
| `hermes plugins` | Plugin management |
| `hermes tools` | List available tools |
| `hermes cron` | Manage scheduled jobs |
| `hermes sessions` | Manage sessions |
| `hermes setup` | First-time setup |
| `hermes doctor` | Diagnostics |

---

## Related

- [[hermes-agent-profile]] -- Agent profile / development guidelines
- [[hermes-agent-architecture]] -- System architecture
- [[hermes-agent-deployment]] -- Deployment guide
- [[hermes-agent-docker]] -- Docker packaging
- [[hermes-agent-docker-deployment]] -- Docker deployment guide
- [[hermes-agent-quadlet]] -- Quadlet deployment
- [[hermes-acp-agent]] -- ACP agent configuration
- [[hermes-acp-implementation]] -- ACP implementation
- [[hermes-gateway-api]] -- Gateway API reference
- [[hermes-gateway-platforms]] -- Gateway platform adapters
- [[hermes-mcp-serve]] -- MCP messaging bridge
- [[hermes-mcp-implementation]] -- MCP implementation

## Related

| Repo | Relationship |
|---|---|
| [[openclaw]] | Another agent framework — MCP bridge surface is intentionally compatible |
| [[agentfield]] | ✅ MCP bridge | AgentField MCP bridge (`assets/mcp-servers/agentfield-mcp-server.md`) wraps AgentField REST API as MCP tools for Hermes. AgentField `app.harness()` could dispatch to Hermes for LLM execution |
| [[hermes-workspace]] | Hermes workspace environment (isolated dev/testing workspace) |
| [[hermes-startup-architect]] | Startup architect skill for Hermes |
| [[hermes-agent]] profile | `assets/agent-profiles/hermes-agent-profile.md` (dev guidelines from AGENTS.md) |

## Cross-project

- [[openclaw]] — Competing agent gateway (TypeScript, MIT)
- [[agentfield]] — Control plane that can orchestrate Hermes agents via MCP
- [[mission-control]] — Dashboard that can connect to Hermes gateway
- [[podman]] — Container runtime Hermes agents run inside
- [[n8n]] — Workflow engine callable from Hermes MCP tools
- [[hermzner]] — Deployment blueprint for Hermes on Hetzner
- [[tank-os]] — Bootc OS pattern applicable to Hermes deployment
- [[clawpier]] — Desktop GUI for managing Hermes Docker containers
- [[buildah]] — Builds the container images Hermes agents run inside
- [[nix-podman-stacks]] — Declarative Nix-based container infrastructure
- [[sablier]] — Scale-to-zero for Hermes agent services
- [[gogs]] — Self-hosted Git backend for agent code repositories
