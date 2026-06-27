---
name: hermes-caduceus
tags: [acp, agent, cli, dashboard, desktop, docker, git, mcp, messaging, multi-agent, orchestration, plugin-sdk, workflows, python, typescript, nix]
description: "Wiki entry for Hermes-caduceus: a reversible fork of Hermes Agent adding deep-planning mode, deterministic multi-agent workflows (the Loom), and Auto Router model routing"
source: sources/Hermes-caduceus/
---

# Hermes-caduceus

| Field | Value |
|---|---|
| **Origin** | [OnlyTerp/Hermes-caduceus](https://github.com/OnlyTerp/Hermes-caduceus) (fork of [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)) |
| **License** | MIT |
| **Source** | `sources/Hermes-caduceus/` |
| **Profile** | `sources/Hermes-caduceus/AGENTS.md` |
| **Upstream** | [[hermes-agent]] |

## What is it?

A reversible fork of Hermes Agent that adds the **Caduceus** mode — an optional deep-planning layer. With one switch (`/caduceus on`), Hermes turns into a senior-engineer planner: it drives a visible to-do plan, raises reasoning effort, delegates where helpful, and escalates to a **deterministic multi-agent workflow engine** (the *Loom*). An optional **Auto Router** sends each delegated worker to the cheapest configured model capable of that subtask.

Off by default, session-scoped, additive, fully reversible, and fully tested (357 passing tests).

## Architecture layers

| Layer | What it does | Entry point |
|---|---|---|
| **Deep-planning loop** | Plans with a live `todo` list, drives one step at a time, verifies before claiming done, right-sizes trivial asks | `agent/caduceus.py` |
| **The Loom** | Deterministic async workflow engine — `agent()` / `parallel()` / `pipeline()` primitives, structured output, shared budgets, per-run caching + resume | `agent/workflow/` |
| **Auto Router** | Routes each delegated worker to the cheapest capable model; orchestrator always keeps the session model | `agent/auto_router.py` |
| **Local GPU workers** | Run workflow workers on local models on GPU, hot-swapped on demand, parallelized to serving slots | `agent/local_manager.py` |

## Key modules

### Agent core

| File | Description |
|---|---|
| `run_agent.py` | `AIAgent` class — the main conversation loop (~12k LOC) |
| `model_tools.py` | Tool orchestration, `discover_builtin_tools()`, `handle_function_call()` |
| `toolsets.py` | Toolset definitions and the `_HERMES_CORE_TOOLS` list |
| `cli.py` | `HermesCLI` class — interactive CLI orchestrator (~11k LOC) |
| `hermes_state.py` | `SessionDB` — SQLite session store with FTS5 full-text search |
| `hermes_logging.py` | Structured logging infrastructure |
| `hermes_constants.py` | Shared constants and configuration defaults |
| `hermes_time.py` | Time utilities for scheduling and session management |
| `utils.py` | General utility functions |
| `hermes_bootstrap.py` | First-run bootstrap and setup logic |
| `batch_runner.py` | Batch execution for bulk agent runs |
| `mcp_serve.py` | MCP server — messaging bridge exposing Hermes conversations as tools |
| `trajectory_compressor.py` | Conversation trajectory compression |
| `toolset_distributions.py` | Toolset distribution management |
| `toolsets.py` | Toolset definitions |

### Agent internals (`agent/`)

| File | Description |
|---|---|
| `caduceus.py` | Caduceus deep-planning mode — the core new feature of this fork |
| `auto_router.py` | Capability-based model router for subagent cost optimization |
| `local_manager.py` | Local GPU worker management |
| `workflow/` | The Loom workflow engine — DSL, scheduler, agent abstractions |
| `transports/` | Transport layer (Codex event projector, app server sessions) |
| `LSP/` | Language Server Protocol integration |
| `secret_sources/` | Credential source providers |

**Per-module highlights:**

| Module | Responsibility |
|---|---|
| `agent_init.py` | Agent initialization, provider setup |
| `agent_runtime_helpers.py` | Runtime helper functions |
| `anthropic_adapter.py` | Anthropic API adapter |
| `auxiliary_client.py` | Auxiliary model client for subagents |
| `azure_identity_adapter.py` | Azure Identity adapter |
| `background_review.py` | Background memory review |
| `bedrock_adapter.py` | AWS Bedrock adapter |
| `browser_provider.py` / `browser_registry.py` | Browser automation registry |
| `chat_completion_helpers.py` | Chat completion utilities |
| `codex_responses_adapter.py` | Codex Responses API adapter |
| `codex_runtime.py` | Codex runtime (for editor integration) |
| `context_compressor.py` | Context window compression |
| `context_engine.py` | Context management engine |
| `conversation_compression.py` | Conversation compression strategies |
| `conversation_loop.py` | Main conversation loop logic |
| `copilot_acp_client.py` | ACP client for GitHub Copilot integration |
| `credential_persistence.py` / `credential_pool.py` / `credential_sources.py` | Credential management |
| `curator.py` / `curator_backup.py` | Skill curation and backup |
| `display.py` | Terminal display formatting |
| `error_classifier.py` | Error classification and recovery |
| `file_safety.py` | File operation safety checks |
| `gemini_*` | Google Gemini API adapters (Cloud Code + native) |
| `google_code_assist.py` / `google_oauth.py` | Google integration |
| `i18n.py` | Internationalization support |
| `image_gen_provider.py` / `image_gen_registry.py` | Image generation |
| `image_routing.py` | Image routing to subagents |
| `insights.py` | Usage insights and analytics |
| `memory_manager.py` / `memory_provider.py` | Memory management |
| `message_sanitization.py` | Message sanitization |
| `model_metadata.py` | Model metadata management |
| `models_dev.py` | Model development utilities |
| `plugin_llm.py` | Plugin LLM integration |
| `prompt_builder.py` | Prompt construction |
| `prompt_caching.py` | Prompt caching strategies |
| `redact.py` | Content redaction |
| `skill_*` | Skill management (bundles, commands, preprocessing, utils) |
| `system_prompt.py` | System prompt management |
| `think_scrubber.py` | Reasoning token scrubbing |
| `tool_dispatch_helpers.py` / `tool_executor.py` / `tool_guardrails.py` | Tool execution pipeline |
| `usage_pricing.py` | Usage pricing and cost tracking |

### Tools (`tools/`)

Over 80 tool implementations:

| File | Description |
|---|---|
| `terminal_tool.py` | Terminal execution (local, Docker, SSH, etc.) |
| `file_operations.py` / `file_tools.py` / `file_state.py` | File system tools |
| `browser_tool.py` / `browser_cdp_tool.py` / `browser_supervisor.py` | Web browsing |
| `mcp_tool.py` | MCP client — consumes MCP servers |
| `code_execution_tool.py` | Code execution sandbox |
| `delegate_tool.py` | Subagent delegation |
| `send_message_tool.py` | Multi-platform messaging |
| `skills_tool.py` / `skill_manager_tool.py` / `skills_hub.py` / `skills_sync.py` | Skill system |
| `vision_tools.py` | Vision/image understanding |
| `web_tools.py` | Web search and extraction |
| `voice_mode.py` / `tts_tool.py` / `transcription_tools.py` | Voice and speech |
| `image_generation_tool.py` | Image generation (Fal, etc.) |
| `memory_tool.py` | Memory storage and retrieval |
| `checkpoint_manager.py` | Session checkpointing |
| `computer_use/` | Computer use backend (CUA driver, macOS) |
| `environments/` | Sandboxed execution environments |

### Gateway (`gateway/`)

Multi-platform messaging bridge with ~20+ platform adapters:

| File | Description |
|---|---|
| `run.py` | Gateway runtime and event loop |
| `session.py` | Gateway session management |
| `config.py` | Multi-profile configuration system |
| `stream_consumer.py` / `stream_dispatch.py` | Stream processing |
| `platforms/` | Platform-specific adapters |
| `channel_directory.py` | Channel routing directory |
| `hooks.py` | Gateway hooks |
| `delivery.py` | Message delivery infrastructure |

### CLI (`hermes_cli/`)

| File | Description |
|---|---|
| `main.py` | CLI entry point — all `hermes` subcommands |
| `commands.py` | Command registry |
| `config.py` | Configuration management |
| `install.py` | Installation utilities |
| `plugins.py` | Plugin management |
| `skills.py` | Skill management |
| `profiles.py` | Profile management |

### Web dashboard (`web/`)

React + TypeScript SPA (Vite-built):

| Area | Description |
|---|---|
| `src/` | React application source |
| `src/lib/api.ts` | API client for all backend endpoints |
| `src/i18n/` | Internationalization for 16 locales |
| `src/components/` | UI components |
| `package.json` | Node dependencies |
| `vite.config.ts` | Vite build config |

### Desktop app (`apps/desktop/`)

Electron-based desktop application:

| Area | Description |
|---|---|
| `src/lib/session-export.ts` | Session export functionality |
| `src/components/workflow/` | Orchestration Theater UI (AgentCard, TheaterPanels) |
| `src/app/chat/` | Chat composer, sidebar, session management |
| `src/app/artifacts/` | Artifact management |
| `src/app/right-sidebar/` | Files, project tree |

### TUI (`ui-tui/`)

Terminal UI using React Ink:

| Area | Description |
|---|---|
| `packages/hermes-ink/src/ink/` | Custom Ink-compatible renderer |
| `packages/hermes-ink/src/ink/parse-keypress.ts` | Terminal keypress parsing |
| `packages/hermes-ink/src/ink/termio/osc.ts` | OSC terminal sequences |

### Other support

| Area | Description |
|---|---|
| `plugins/` | Plugins (messaging platforms, dashboard, skills) |
| `providers/` | External service providers |
| `skills/` / `optional-skills/` | Bundled skills |
| `tests/` | Test suite |
| `scripts/` | Build, release, CI scripts |
| `docker/` | Dockerfiles and compose |
| `nix/` | Nix flake packaging |
| `cron/` | Cron scheduler integration |
| `acp_adapter/` | ACP server (editor integration) |
| `acp_registry/` | ACP agent registry |
| `apps/bootstrap-installer/` | Self-contained installer packages |
| `apps/shared/` | Shared code between apps |
| `tui_gateway/` | TUI gateway bridge |
| `optional-mcps/` | Optional MCP server manifests |
| `optional-skills/` | Community-contributed optional skills |
| `locales/` | Localization files |
| `docs/` / `website/` | Documentation site |

## Install

```bash
git clone -b caduceus https://github.com/OnlyTerp/Hermes-caduceus.git
python3 Hermes-caduceus/install_caduceus.py --with-desktop
```

The installer (`install_caduceus.py`) auto-detects the existing Hermes install, backs up every file it touches, and can be fully undone with `--uninstall`. Pure-Python stdlib — no pip dependencies needed.

## MCP

Hermes is both an **MCP client** (consumes MCP servers) and an **MCP server** (messaging bridge):

- **MCP Server** (`mcp_serve.py`): messaging bridge exposing 10 tools for listing/sending conversations
- **MCP Client** (`tools/mcp_tool.py`): `MCPServerTask` — consumes external MCP servers
- Optional MCP manifests in `optional-mcps/` (linear, n8n, unreal-engine)
- MCP OAuth in `tools/mcp_oauth_manager.py`

## ACP

Agent Communication Protocol:

- **ACP Server** (`acp_adapter/server.py`): `HermesACPAgent` — drives Hermes from editors (Zed, Claude Code, etc.)
- **ACP Client** (`agent/copilot_acp_client.py`): talks to GitHub Copilot
- ACP agent registry in `acp_registry/agent.json`

## Related vault pages

- [[hermes-agent]] — upstream project this fork extends
- [[hermes-mcp-serve]] — MCP server deep-dive
- [[hermes-mcp-implementation]] — MCP implementation patterns
- [[hermes-acp-agent]] — ACP server details
- [[hermes-acp-implementation]] — ACP implementation patterns
- [[hermes-startup-architect]] — Hermes startup and architecture
- [[opencode-hermes-multiagent]] — multi-agent orchestration patterns
