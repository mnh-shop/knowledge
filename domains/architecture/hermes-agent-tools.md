---
name: hermes-agent-tools
description: "Hermes Agent tool system — the full core-tool inventory, toolset layering, dispatch internals, tool-search bridge, and the MCP client"
tags: [hermes-agent, architecture, tools, mcp, agent-gateway]
source: sources/hermes-agent/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Hermes Agent Tools

**Source:** `sources/hermes-agent/`

Hermes ships ~75 registered core tools. The always-on surface is deliberately
small — `_HERMES_CORE_TOOLS` (`toolsets.py:31-82`) pins **55 tools** that are
sent on every API call (the "narrow waist"). Everything else is a gated,
toolset-scoped, or dynamically-discovered capability. See
[[hermes-agent-architecture]] for how the tool layer fits into the overall
system.

## Tool registry

`tools/registry.py` defines the `ToolRegistry` singleton (`ToolRegistry` at
`:290`). Every tool registers a schema + handler via `registry.register()`
(`:438`), and entries are stored as `ToolEntry` (`:160`) with:

- `name`, `toolset`, schema and handler
- `check_fn` — an environment predicate that decides whether the tool is
  exposed at all (e.g. desktop-only tools are hidden unless
  `HERMES_DESKTOP` is set)
- thread-safe mutations (an `RLock` serializes register/deregister/MCP
  refresh, `:317-331`) and a monotonically-increasing generation counter
  (`:334`) so readers can memoize snapshots

The registry is mutated at runtime too: MCP dynamic refresh can add tools
between turns, and plugins can register additional toolsets
(`register_toolset_alias`, `:363`; plugin overrides gated by
`register_plugin_override_policy`, `:389`).

## Tool layers

### 1. Core tools — 55 always-on (`_HERMES_CORE_TOOLS`)

Defined once in `toolsets.py:31-82` and reused across CLI, TUI, gateway,
cron, and webhook surfaces. The canonical set by family:

| Family | Tools |
|---|---|
| Web | `web_search`, `web_extract` |
| Terminal/process | `terminal`, `process` |
| Desktop GUI (gated on `HERMES_DESKTOP` via `check_fn`) | `read_terminal`, `close_terminal`, `open_preview`, `focus_pane`, `react_to_message` |
| File manipulation | `read_file`, `write_file`, `patch`, `search_files` |
| Vision + image gen | `vision_analyze`, `image_generate` |
| Skills | `skills_list`, `skill_view`, `skill_manage` |
| Browser automation (12) | `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`, `browser_scroll`, `browser_back`, `browser_press`, `browser_get_images`, `browser_vision`, `browser_console`, `browser_cdp`, `browser_dialog` |
| Text-to-speech | `text_to_speech` |
| Planning & memory | `todo`, `memory` |
| Session history | `session_search` |
| Clarifying questions | `clarify` |
| Code execution + delegation | `execute_code`, `delegate_task` |
| Cron | `cronjob` |
| Home Assistant (gated on `HASS_TOKEN`) | `ha_list_entities`, `ha_get_state`, `ha_list_services`, `ha_call_service` |
| Kanban (gated: `HERMES_KANBAN_TASK` or profile toolset) | `kanban_show`, `kanban_list`, `kanban_complete`, `kanban_block`, `kanban_heartbeat`, `kanban_comment`, `kanban_create`, `kanban_link`, `kanban_unblock`, `kanban_attach`, `kanban_attach_url`, `kanban_attachments` |
| Computer use (gated on `cua-driver` installed) | `computer_use` |

Note the deliberate non-members: the desktop Project tools
(`project_list`/`project_create`/`project_switch`) are **not** in
`_HERMES_CORE_TOOLS` — they only make sense where a GUI can follow the move,
so they live in the `project` toolset, enabled solely by the GUI gateway
(`tui_gateway/server.py::_load_enabled_toolsets`, `:3779`) — keeping them off
every CLI/messaging/cron schema (narrow waist). Same reasoning gates the
desktop pane tools, `kanban_*`, `ha_*`, and `computer_use`.

### 2. Toolsets — 33 named bundles (`TOOLSETS`, `toolsets.py:97`)

`web`, `search`, `x_search`, `vision`, `video`, `image_gen`, `video_gen`,
`computer_use`, `terminal`, `skills`, `browser`, `cronjob`, `file`, `tts`,
`todo`, `memory`, `context_engine`, `session_search`, `project`, `clarify`,
`code_execution`, `delegation`, `homeassistant`, `kanban`, `discord`,
`discord_admin`, `yuanbao`, `feishu_doc`, `feishu_drive`, `spotify`,
`debugging`, `safe`, `coding`.

Resolution helpers: `resolve_toolset()` (`:692`), `resolve_multiple_toolsets()`
(`:774`), `get_all_toolsets()` (`:819`), `get_toolset_names()` (`:844`),
`validate_toolset()` (`:867`), `create_custom_toolset()` (`:887`),
`bundle_non_core_tools()` (`:664`). `_HERMES_WEBHOOK_SAFE_TOOLS`
(`toolsets.py:87`) is a purpose-built restricted set for webhook events —
untrusted third-party content (PR titles/comments) must not be able to trigger
local file/system execution.

### 3. Extended families (non-core, toolset-scoped)

| Family | Files | Tools |
|---|---|---|
| Browser (CDP + dialog) | `browser_tool.py`, `browser_cdp_tool.py`, `browser_dialog_tool.py`, `browser_camofox.py`, `browser_supervisor.py` | 12 core browser tools + CDP/dialog extensions |
| Code execution | `code_execution_tool.py` | `execute_code` |
| Computer use | `computer_use/` + `computer_use_tool.py` | `computer_use` (macOS, cua-driver MCP backend) |
| Delegation | `delegate_tool.py`, `async_delegation.py` | `delegate_task`, async subagent fan-out |
| Files | `file_tools.py`, `file_operations.py`, `file_state.py` | `read_file`, `write_file`, `patch`, `search_files` |
| MCP client | `mcp_tool.py`, `mcp_oauth_manager.py`, `mcp_stdio_watchdog.py` | dynamically injected per configured server |
| Memory | `memory_tool.py` | `memory` |
| Skills | `skills_hub.py`, `skills_tool.py` | `skills_list`, `skill_view`, `skill_manage` |
| Terminal | `terminal_tool.py` | `terminal` |
| Vision | `vision_tools.py` | `vision_analyze` |
| Web | `web_tools.py` | `web_search`, `web_extract` |
| Cron | `cronjob_tools.py` | `cronjob` |
| TTS | `tts_tool.py`, `tts_streaming.py`, `neutts_synth.py` | `text_to_speech` |
| Transcription | `transcription_tools.py` | audio transcription |
| Image gen | `image_generation_tool.py` | `image_generate` |
| Video | `video_generation_tool.py`, `xai_video_tools.py` | `video_generate`, `video_analyze`, `xai_video_edit`/`extend` |
| X search | `x_search_tool.py` | `x_search` |
| Yuanbao | `yuanbao_tools.py` | 5 `yb_*` tools |
| Feishu | `feishu_doc_tool.py`, `feishu_drive_tool.py` | 5 `feishu_*` tools |
| Discord | `discord_tool.py` | `discord`, `discord_admin` |
| Projects (desktop) | `project_tools.py` | `project_list`, `project_create`, `project_switch` |
| Clarify | `clarify_tool.py`, `clarify_gateway.py` | `clarify` |
| Todo | `todo_tool.py` | `todo` |
| Kanban | `kanban_tools.py` | 13 `kanban_*` tools (12 worker ops + toolset) |
| Home Assistant | `homeassistant_tool.py` | 4 `ha_*` tools |
| Desktop pane | `read_terminal`/`close_terminal`/`open_preview`/`focus_pane`/`react_to_message` tools | desktop GUI affordances |
| Approvals | `approval.py`, `tool_backend_helpers.py` | approval gating + backend hooks |
| Guardrails | `tool_output_limits.py`, `tool_result_storage.py`, `hook_output_spill.py`, `write_approval.py` | output truncation, spill, write gates |

## Tool dispatch

Tool calls land in `agent/tool_dispatch_helpers.py` (routing) and execute in
`agent/tool_executor.py` (timeout + error handling). The assembly point for
the schema sent to the model is `model_tools.get_tool_definitions()`
(`model_tools.py:288`), which merges core + toolset + plugin + MCP tools and
honors `check_fn` gating (`tools/registry.py` `_toolset_has_exposable_tools`
and per-tool `check_fn`).

### Tool-search bridge (`tools/tool_search.py`)

To keep a >55-tool schema small, long-tail tools are **deferred**: the model
sees three bridge tools — `tool_search`, `tool_describe`, and `tool_call`
(`TOOL_SEARCH_NAME`/`TOOL_DESCRIBE_NAME`/`BRIDGE_TOOL_NAMES`, `:55-59`). The
model searches the deferred catalog, asks for a full schema, then invokes.
`assemble_tool_defs()` (`:772`) decides what to inline vs. defer based on
`tool_search` config (`load_config` `:172`, `should_activate` `:275`,
`listing_token_budget` `:298`); `model_tools.py:553-564` wires the bridge in
when `enabled != "off"`. `classify_tools()` (`:230`) and
`estimate_tokens_from_schemas()` (`:258`) drive the split.

### Loop guardrails

- `tool_loop_guardrails` config (`config_defaults.py:498`) and
  `agent/turn_context.py` guard against runaway tool loops.
- `tool_output` config (`config_defaults.py:489`): `max_bytes` (50_000 ≈
  12-15K tokens) caps terminal output; `max_lines` (2000) and
  `max_line_length` clamp `read_file` pagination.
- `tools/tool_output_limits.py` and `tools/tool_result_storage.py` enforce
  the caps; oversized terminal output is head+tail truncated, `read_file`
  pages instead.

## MCP client tool (`tools/mcp_tool.py`)

The MCP client consumes external MCP servers as tool providers. Core pieces:

| Symbol | Line |
|---|---|
| `SamplingHandler` | `:1263` |
| `ElicitationHandler` | `:1660` |
| `MCPServerTask` | `:1821` |
| `_MAX_RECONNECT_RETRIES = 5` | `:335` |
| `_MAX_INITIAL_CONNECT_RETRIES = 3` | `:336` |
| `_MAX_BACKOFF_SECONDS = 60` | `:337` |
| `_run_stdio` | `:2377` |
| `_preflight_content_type` | `:2586` |
| `_run_http` | `:2752` |

Transport support:

- **stdio** — `_run_stdio` (`:2377`) spawns the server subprocess (with
  `mcp_stdio_watchdog.py` guarding hangs).
- **HTTP / SSE / streamable** — `_run_http` (`:2752`) with
  `_preflight_content_type` (`:2586`) validating the endpoint's content-type
  before streaming.
- **Reconnect** — exponential backoff capped at `_MAX_BACKOFF_SECONDS` (60s),
  first-connect retries capped at `_MAX_INITIAL_CONNECT_RETRIES` (3), then
  reconnect attempts capped at `_MAX_RECONNECT_RETRIES` (5) before the server
  is marked failed (enforcement at `:3184`, `:3298`, `:3337`).
- **OAuth** — `mcp_oauth_manager.py`, `mcp_oauth.py`,
  `mcp_dashboard_oauth.py` handle OAuth flows for remote servers.
- **Sampling/elicitation** — `SamplingHandler` (`:1263`) and
  `ElicitationHandler` (`:1660`) implement MCP sampling and elicitation so a
  server can request model calls or user input mid-turn.

MCP tool schemas are injected into the registry dynamically and refreshed
between turns (`agent/turn_context.py`); `mcp_discovery_timeout` (1.5s,
`config_defaults.py`) bounds first-turn discovery without freezing startup.

## Related

- [[hermes-agent-architecture]] — system architecture, entry points, config
- [[hermes-agent-agent-core]] — AIAgent loop, context, delegation
- [[hermes-mcp-serve]] — the MCP *messaging bridge* (`mcp_serve.py`, 10 tools)
- [[hermes-agent]] — Wiki entry
