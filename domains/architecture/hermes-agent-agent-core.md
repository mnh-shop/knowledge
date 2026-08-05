---
name: hermes-agent-agent-core
description: "Hermes Agent core — AIAgent lifecycle, conversation loop, context management (memory/compression/prompt caching), budgets, model adapters, and delegation"
tags: [hermes-agent, architecture, agent, context, memory, delegation]
source: sources/hermes-agent/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Hermes Agent — Agent Core

**Source:** `sources/hermes-agent/`

The agent core is the narrow waist of Hermes: one conversation engine shared
by every surface (CLI, TUI, desktop, gateway). Everything else — tools,
skills, plugins, platform adapters — is an edge. See
[[hermes-agent-architecture]] for the system-level view.

## AIAgent lifecycle

`AIAgent` (`run_agent.py:409`) is the interactive agent class. It wraps the
per-turn engine and owns the session state.

| Method | Line | Role |
|---|---|---|
| `AIAgent` | `run_agent.py:409` | Class constructor — model + provider resolution, tool loading, memory, skills |
| `run_conversation()` | `run_agent.py:7012` | The main conversation turn (mirrors `agent/conversation_loop.py:1084`, the module-level `run_conversation`) |
| `chat()` | `run_agent.py:7167` | Synchronous convenience wrapper (`message`, `stream_callback`) |

The shared turn machinery lives in `agent/conversation_loop.py` (module-level
`run_conversation` at `:1084`) — the same code path is driven by the CLI
(`cli.py` `HermesCLI.process_command`, `cli.py:9560`), the gateway
(`GatewayRunner`, `gateway/run.py:5399`), and the TUI backend
(`tui_gateway/server.py`).

Supporting lifecycle modules in `agent/`:

- `agent_init.py`, `agent_runtime_helpers.py` — deferred agent build (MCP
  discovery, model metadata, skills scan; bounded by `agent.build_wait_timeout`
  600s, `config_defaults.py`)
- `turn_context.py` — per-turn state container; between-turns MCP refresh
- `turn_finalizer.py` — post-turn processing (usage, memory writes, caching)
- `coding_context.py` — `detect_project_facts`: auto-detects project
  structure/dependencies (AGENTS.md, CLAUDE.md, SOUL.md, etc.)
- `backend_identity.py`, `bounded_response.py`, `error_classifier.py` —
  provider identity, response bounds, error routing
- `iteration_budget.py` — `IterationBudget` (`:17`): parent capped at
  `agent.max_iterations` (default 500), each subagent capped at
  `delegation.max_iterations` (default 50); `consume()`/`refund()`/`used()`/
  `remaining()`

## Context management

The conversation never re-reads what it can cache, compress, or forget:

- **Prompt construction** — `agent/prompt_builder.py` builds the cached system
  prompt prefix (the sacred cached prefix — mid-turn mutation is avoided).
- **Prompt caching** — `agent/prompt_caching.py` manages cache lifecycle;
  config section `prompt_caching` (`config_defaults.py:678`). Cache keys are
  model- and account-specific, so fallback/credential rotation forces a full
  re-read at full price.
- **Compression** — `agent/context_compressor.py`,
  `agent/conversation_compression.py` (head+tail ~75%/25% windowing), and
  `agent/manual_compression_feedback.py`; config section `compression`
  (`config_defaults.py:525`). Also `agent/context_breakdown.py`,
  `agent/context_engine.py`, `agent/context_references.py`.
- **Trajectory** — `agent/trajectory.py` (`save_trajectory` `:30`,
  `convert_scratchpad_to_think` `:16`) records turn trajectories;
  `trajectory_compressor.py` (repo root) post-processes them.
- **Memory** — `agent/memory_manager.py` (cross-session persistence/recall),
  `agent/learning_graph.py` + `learning_mutations.py` +
  `learning_graph_render.py` (graph memory), `agent/curator.py` +
  `curator_backup.py` (background self-improvement review); config section
  `memory` (`config_defaults.py:1531`): `memory_enabled`, `write_approval`
  gate, `memory_char_limit` 2200, `user_char_limit` 1375, external provider
  plugin (`openviking`, `mem0`, `hindsight`, `holographic`, `retaindb`,
  `byterover` — one at a time).

## Budgets and concurrency

- **Session caps** — `max_concurrent_sessions` (None = unbounded) and
  `max_live_sessions` (16, soft LRU eviction of detached sessions) —
  `config_defaults.py:25-30`.
- **Turn budget** — `agent.max_turns` (500), `delegation.max_iterations` (50)
  (`agent/iteration_budget.py`).
- **Timeouts** — `agent.gateway_timeout` (1800s inactivity),
  `agent.restart_drain_timeout` (0 = interrupt immediately on gateway
  restart), `agent.build_wait_timeout` (600s) — `config_defaults.py:31-49`.
- **Credential pool** — `agent/credential_pool.py` (`PooledCredential`
  `:165`, `runtime_api_key` `:243`, `runtime_base_url` `:265`) rotates API
  keys across accounts; config `credential_pool_strategies`
  (`config_defaults.py:11`) and `agent/credential_sources.py` +
  `credential_persistence.py`.
- **Auxiliary (side-LLM) client** — `agent/auxiliary_client.py` (`_create_openai_client`
  `:205`, `aux_interrupt_protection` `:237`) runs cheap parallel LLM tasks
  (labeling, verification, summaries) without touching the main model; config
  section `auxiliary` (`config_defaults.py:749`).

## Model adapters and providers

In-`agent/` adapters:

| Adapter | File | Notes |
|---|---|---|
| Anthropic | `agent/anthropic_adapter.py` | primary provider family |
| Gemini native | `agent/gemini_native_adapter.py` + `gemini_schema.py` | native generation API |
| AWS Bedrock | `agent/bedrock_adapter.py` | AWS-hosted Anthropic models |
| Codex | `agent/codex_responses_adapter.py`, `agent/codex_runtime.py` | OpenAI Codex responses API |
| Azure identity | `agent/azure_identity_adapter.py` | Entra/AD token auth |
| LM Studio reasoning | `agent/lmstudio_reasoning.py` | local reasoning models |

Provider discovery is plugin-driven: `plugins/model-providers/` ships 33
provider modules (anthropic, gemini, bedrock, openrouter, openai-codex, nous,
deepseek, kimi-coding, vertex, xai, zai, alibaba, minimax, upstage, novita,
nvidia, qwen-oauth, ollama-cloud, custom, …) that register via
`providers.register_provider(profile)`; `providers/__init__.py`
`_discover_providers()` scans the plugin dir and `$HERMES_HOME/plugins/
model-providers/`. `providers/base.py` defines the profile contract.

Runtime model routing: `agent/models_dev.py` (model selection/routing),
`agent/chat_completion_helpers.py`, `hermes_cli/config.py` `providers` /
`fallback_providers` / `model_catalog` sections. `agent/account_usage.py`,
`agent/credits_tracker.py`, `agent/billing_usage.py` track spend across
accounts; `agent/billing_links.py`/`billing_view.py` surface it.

## Delegation

- `tools/delegate_tool.py` — `delegate_task`: spawns child agents on a
  different provider/model (`delegation` config, `config_defaults.py:1560`).
  Roles normalize to `leaf` or `orchestrator` (`:464`); nested
  delegation requires `_get_orchestrator_enabled()` (`:632`) and role
  `"orchestrator"` re-adds the delegate tool (`:115`).
- `tools/async_delegation.py` — fire-and-forget fan-out with live logs
  (`delegation_live_log.py`).
- `agent/delegation_context.py` — child-agent context assembly.
- **Mixture of Agents** — config `moa` (`config_defaults.py:1645`):
  `default_preset`/`active_preset`, `save_traces`, `privacy_filter`, and
  `presets.default` (2 reference models + 1 aggregator). Available via the
  `/moa <prompt>` slash command (`hermes_cli/main.py:11094`).

## Agent lifecycle features

- **Goals** — config `goals.max_turns` (20 auto-pause guard,
  `config_defaults.py:1634`); `/goal` commands with judge-based continuation.
- **Personality** — `personalities` config key; `hermes_cli/default_soul.py`;
  automatic context files (SOUL.md, AGENTS.md, CLAUDE.md, .hermes.md,
  .cursorrules) bounded by `context_file_max_chars` (None = scales with model
  window, floor 20K / ceiling 500K).
- **Profiles** — `hermes_cli/profiles.py`: `_get_profiles_root` (`:264`),
  `_get_active_profile_path` (`:289`), `normalize_profile_name` (`:303`);
  `hermes_constants.py` `get_hermes_home()` (`:106`).
- **Checkpoints / rollback / snapshot** — filesystem checkpoint store at
  `~/.hermes/checkpoints/` managed by `tools/checkpoint_manager.py` (bare-git
  shadow repo, `_init_store` `:421`, `_index_path` `:223`, `_run_git` `:301`);
  CLI surface `hermes_cli/checkpoints.py` (`status`/`list`/`prune`/`clear`,
  `register_cli` `:242`); config `checkpoints` (`config_defaults.py:397`):
  `max_snapshots` 20, `max_total_size_mb` 500, `max_file_size_mb` 10,
  `auto_prune` with 7-day retention. `/rollback` and `/snapshot` slash
  commands surface these to the agent.
- **Sessions** — SQLite-backed SessionDB (`hermes_state*.py`), session search
  via `session_search` tool, session indexing in `hermes_cli/active_sessions.py`.

## Related

- [[hermes-agent-architecture]] — system architecture, entry points, config
- [[hermes-agent-tools]] — tool inventory and dispatch
- [[hermes-agent]] — Wiki entry
- [[hermes-profiles]] — agent profile / development guidelines
