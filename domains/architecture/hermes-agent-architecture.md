---
name: hermes-agent-architecture
tags: [acp, agent-gateway, ai-llm, architecture, cli, desktop-app, hermes, mcp, messaging, multi-platform, plugin-sdk, typescript]
description: "Hermes Agent architecture: multi-platform personal AI agent by Nous Research with 3,726 files and 257 indexed symbols"
source: sources/hermes-agent/
---

# Hermes Agent Architecture

**Codegraph:** `graphs/hermes-agent` (3,726 files, 257 symbols indexed)

## What is Hermes?

A personal AI agent from Nous Research. It runs the same agent core across
multiple surfaces: CLI, TUI, Electron desktop, and a messaging gateway
connecting ~20+ chat platforms.

Key architectural properties:
- **Narrow waist, broad edges.** The core agent (conversation loop, tool
  dispatch, model providers) is deliberately compact. Capability grows at
  the edges via skills, plugins, and MCP servers.
- **Prompt caching is sacred.** Long-lived conversations reuse a cached
  prefix every turn. Mid-turn mutations that invalidate the cache are
  avoided.
- **SDK, not framework.** Users interact through CLI commands, not library
  imports. Extension is through skills (directory-based) and plugins
  (code-based subsystems), not subclassing.

## Layer Architecture

```
                ┌──────────────────────────────────┐
                │         Presentation              │
                │  CLI · TUI · Desktop · Gateway    │
                │  (hermes_cli/ · ui-tui/ · apps/)  │
                └──────────────┬───────────────────┘
                               │
                ┌──────────────▼───────────────────┐
                │     Messaging Gateway              │
                │  Gateway (gateway/)                │
                │  ~20 platform adapters             │
                │  Webhook, stream dispatch          │
                └──────────────┬───────────────────┘
                               │
                ┌──────────────▼───────────────────┐
                │     Agent Core                     │
                │  agent/ · providers/               │
                │  Conversation loop, tool dispatch  │
                │  Memory, context management        │
                │  Model adapters (Anthropic, Gemini,│
                │  Bedrock, OpenAI, etc.)            │
                └──┬──────────┬──────────┬──────────┘
                   │          │          │
    ┌──────────────▼──┐ ┌────▼────┐ ┌───▼────────────┐
    │  Tools (~90+)   │ │  Skills │ │  Plugins        │
    │  tools/         │ │ skills/ │ │  plugins/        │
    │  Browser, code  │ │ optional│ │  Subsystems:     │
    │  exec, file ops │ │ -skills/│ │  memory, web,    │
    │  MCP client,    │ │         │ │  cron, kanban,   │
    │  web search,    │ │         │ │  model-providers │
    │  vision, etc.   │ │         │ │  observability   │
    └─────────────────┘ └─────────┘ └─────────────────┘

    Agent Communication Protocol (ACP)
    ┌──────────────────────────────────────────────┐
    │  acp_adapter/  ·  acp_registry/agent.json    │
    │  → Zed, Claude Code, Codex, OpenCode, Pi     │
    └──────────────────────────────────────────────┘

    Model Context Protocol (MCP)
    ┌──────────────────────────────────────────────┐
    │  mcp_serve.py  (Bridge: list conversations,  │
    │                 read messages, send messages) │
    │  tools/mcp_tool.py  (Client: consume MCP     │
    │                 servers as tool providers)    │
    └──────────────────────────────────────────────┘
```

## Key source map

### `agent/` — Agent Core

| File | Class/Function | What it does |
|---|---|---|
| `conversation_loop.py` | `AIAgent.run_conversation()` | Main conversation turn — the core loop |
| `tool_dispatch_helpers.py` | Tool dispatch routing | Routes tool calls to their implementations |
| `tool_executor.py` | Tool execution | Runs tool calls with timeout and error handling |
| `memory_manager.py` | Memory management | Cross-session memory persistence and recall |
| `prompt_builder.py` | System prompt construction | Builds the cached system prompt prefix |
| `prompt_caching.py` | Cache management | Prompt cache lifecycle |
| `context_compressor.py` | Context compression | Compresses when context grows too large |
| `coding_context.py` | `detect_project_facts` | Auto-detects project structure, dependencies |
| `models_dev.py` | Model routing | Model selection and routing |
| `turn_context.py` | `TurnContext` | Per-turn state container |
| `turn_finalizer.py` | Turn finalization | Post-turn processing |

### Model adapters

| File | Purpose |
|---|---|
| `anthropic_adapter.py` | Anthropic API adapter |
| `gemini_native_adapter.py` | Gemini API adapter |
| `bedrock_adapter.py` | AWS Bedrock adapter |
| `auxiliary_client.py` | Secondary/fallback model client |

### `tools/` — Model Tools (90+)

All tools are loaded on every API call (the narrow waist). Priority order for
new capabilities: extend existing → CLI + skill → gated tool → plugin →
MCP server → new core tool (last resort).

Key tool categories:

| Area | Key Files |
|---|---|
| Browser | `browser_tool.py`, `browser_cdp_tool.py`, `browser_camofox.py` |
| Code execution | `code_execution_tool.py` |
| File operations | `file_tools.py`, `file_operations.py`, `file_state.py` |
| MCP client | `mcp_tool.py` (MCPServerTask), `mcp_oauth_manager.py` |
| Web search | `web_tools.py` |
| Terminal | `terminal_tool.py` |
| Delegation | `delegate_tool.py`, `async_delegation.py` |
| Skills | `skills_hub.py`, `skills_tool.py`, `skill_manager_tool.py` |
| Memory | `memory_tool.py` |
| Vision | `vision_tools.py` |
| Cron | `cronjob_tools.py` |
| Social | `discord_tool.py`, `x_search_tool.py` |
| Kanban | `kanban_tools.py` |

### `hermes_cli/` — CLI

| File | What it does |
|---|---|
| `main.py` | ~12000+ line god file — all `hermes` commands |
| Models | Model catalog and management |

The CLI is the primary user-facing entry point. It's a known god file that
is in the process of being refactored (listed in AGENTS.md as wanted work).

### `gateway/` — Messaging Layer

See the [[hermes-gateway-platforms]] asset for the full platform adapter
reference. The gateway runs as a long-lived process that binds multiple
platform adapters, routes messages to the agent core, and delivers
responses back.

### `acp_adapter/` — ACP Protocol

See [[hermes-acp-agent]] for full details.

### `mcp_serve.py` — MCP Bridge

See [[hermes-mcp-serve]] for full details.

## Design principles (from `AGENTS.md`)

1. **Per-conversation prompt caching is sacred.** Long-lived conversations
   reuse a cached prefix every turn. Anything that mutates past context,
   swaps toolsets, or rebuilds the system prompt mid-conversation
   invalidates caching and multiplies cost.
2. **The core is a narrow waist; capability lives at the edges.** Every
   model tool is sent on every API call. Most new capability should arrive
   as a CLI command + skill, a service-gated tool, or a plugin.
3. **Expansive at the edges, conservative at the waist.** New platform
   adapters, channels, providers, models are welcome. New core model tools
   are high-bar.
4. **Extend, don't duplicate.** Before adding a new module/manager/hook,
   check if existing infrastructure covers the use case.

## Key dependencies

| Type | Technologies |
|---|---|
| Runtime | Python 3.11+ |
| Package | `pyproject.toml` with uv, optional extras (`[all]`, `[acp]`, `[termux]`) |
| Desktop | Electron (apps/desktop/) |
| Database | SQLite via SessionDB (hermes_state) |
| Config | TOML (config.yaml in ~/.hermes) |
| MCP | `mcp` package (FastMCP) |
| ACP | `acp` package |
| Models | Anthropic, Gemini, Bedrock, OpenAI, OpenRouter, NovitaAI, NVIDIA NIM, etc. |

## Related

- [[hermes-agent]] -- Wiki entry
- [[hermes-agent-profile]] -- Agent profile / development guidelines
- [[hermes-agent-deployment]] -- Deployment guide
- [[hermes-acp-implementation]] -- ACP implementation patterns
- [[hermes-mcp-implementation]] -- MCP implementation patterns

## Links

- Source: `sources/hermes-agent/`
- Repomix: `raw/hermes-agent/hermes-agent.xml`
- Profile (AGENTS.md): `sources/hermes-agent/AGENTS.md`
- Wiki: [[hermes-agent]]
