---
name: hermes-agent-plugins
tags: [architecture, hermes-agent, plugin-sdk, plugins, mcp, model-providers]
description: "Hermes Agent plugin framework: PluginManager hooks, 18 bundled plugin subsystems (memory, web, image/video gen, model-providers, platforms), plugins-vs-core policy"
source: sources/hermes-agent/
---

# Hermes Agent Plugins

**Codegraph:** `graphs/hermes-agent`
**Source:** `sources/hermes-agent/plugins/` · `sources/hermes-agent/hermes_cli/plugins.py`

Plugins are the code-based extension mechanism for Hermes. Unlike skills
(directory-based content loaded on demand), plugins are installable Python
packages that register lifecycle hooks, CLI commands, and tool schemas into
the running agent. They sit at priority position four in the capability
hierarchy: extend existing → CLI + skill → gated tool → **plugin** → MCP
server → new core tool (last resort).

## Plugin framework — `hermes_cli/plugins.py`

The framework lives in a single module (2,485 lines):

| Symbol | Line | Role |
|---|---|---|
| `VALID_HOOKS` | 135 | The complete set of hook names a plugin may register for |
| `register_cli_command` | 523 | Lets plugins add top-level `hermes` subcommands |
| `PluginManager` | 1267 | Loads plugins, validates their hooks against `VALID_HOOKS`, dispatches hook callbacks |
| `discover_plugins` | 2059 | Scans installed plugins and registers them (eager import skipped unless the invoked subcommand needs it) |

### Hook surface

The `VALID_HOOKS` set (plugins.py:135) includes:

- **Tool lifecycle:** `pre_tool_call`, `post_tool_call`, `transform_tool_result`
- **LLM lifecycle:** `pre_llm_call`, `post_llm_call`, `transform_llm_output`
  (plugins return a string to replace the response, first non-None wins),
  `pre_api_request`, `post_api_request`, `api_request_error`
- **Terminal:** `transform_terminal_output`
- **Session lifecycle:** `on_session_start`, `on_session_end`,
  `on_session_finalize`, `on_session_reset`
- **Subagents:** `subagent_start`, `subagent_stop`
- **Gateway:** `pre_gateway_dispatch` — fired per incoming `MessageEvent`
  after the internal-event guard but before auth/pairing; may return
  `{"action": "skip"|"rewrite"|"allow", ...}` to influence dispatch
- **Approvals:** `pre_approval_request`, `post_approval_response`
- **Verification loop:** `pre_verify` — a stop-gate that can return
  `{"action": "continue", "message": "..."}` to keep the agent going
- **Kanban:** `kanban_task_claimed`, `kanban_task_completed`,
  `kanban_task_blocked`

### Loading semantics

- **Opt-in by default.** Only plugins named in `config.yaml` under
  `plugins.enabled` are loaded (`_get_enabled_plugins`, plugins.py:229). A
  `plugins.disabled` deny-list also exists for explicit exclusion.
- **Registration is lazy.** `main.py` keeps a `_BUILTIN_SUBCOMMANDS`
  frozenset and a `_first_positional_argv` fast-path so invocations that
  clearly need no plugin command skip eager imports entirely (plugin imports
  can cost 500ms+ pulling in `google.cloud.pubsub_v1`, `aiohttp`, `grpc`).
- **Hook registration is validated.** Unknown hook names are rejected with
  the sorted `VALID_HOOKS` list (plugins.py:1183-1189).

### Authoring helper — `plugins/plugin_utils.py`

Shared concurrency primitives for plugin authors (135 lines):
`lazy_singleton` (thread-safe decorator for zero-arg accessor singletons) and
`SingletonSlot` (manual slot for config/key-dependent instances). Both are
stdlib-`threading`-only so plugins can import them without dragging in heavy
host modules — protects against the TOCTOU double-init race in
multi-threaded agent sessions.

## Bundled plugins (18 dirs + `plugin_utils.py`)

```
plugins/
├── browser/           browser_use · browserbase · firecrawl
├── context_engine/    context engine plugin
├── cron_providers/    chronos
├── dashboard_auth/    basic · drain · nous · self_hosted
├── disk-cleanup/      disk_cleanup.py + plugin.yaml
├── google_meet/       audio_bridge, meet_bot, realtime, SKILL.md
├── hermes-achievements/  dashboard + docs + tests
├── image_gen/         7: deepinfra · fal · krea · openai · openai-codex · openrouter · xai
├── kanban/            dashboard + systemd dispatcher
├── memory/            8 providers (see below)
├── model-providers/   33 providers (see below)
├── observability/     langfuse · nemo_relay
├── platforms/         21 platform adapters (see below)
├── security-guidance/ patterns.py + plugin.yaml
├── spotify/           client.py + tools.py + plugin.yaml
├── teams_pipeline/    cli, meetings, pipeline, runtime, subscriptions
├── video_gen/         3: deepinfra · fal · xai
└── web/               8 search providers (see below)
```

### `model-providers/` (33)

ai-gateway, alibaba, alibaba-coding-plan, anthropic, arcee, azure-foundry,
bedrock, copilot, copilot-acp, custom, deepinfra, deepseek, fireworks,
gemini, gmi, huggingface, kilocode, kimi-coding, minimax, nous, novita,
nvidia, ollama-cloud, openai-codex, opencode-zen, openrouter, qwen-oauth,
stepfun, upstage, vertex, xai, xiaomi, zai.

### `web/` (8 search providers)

brave_free, ddgs, exa, firecrawl, parallel, searxng, tavily, xai.

### `image_gen/` (7) and `video_gen/` (3)

image_gen: deepinfra, fal, krea, openai, openai-codex, openrouter, xai.
video_gen: deepinfra, fal, xai.

### `platforms/` (21 — the plugin platform adapters)

telegram, discord, slack, whatsapp, email, sms, matrix, mattermost, teams,
feishu, wecom, dingtalk, google_chat, homeassistant, irc, line, ntfy, photon,
raft, simplex, buzz.

### `memory/` (8 providers)

honcho, mem0, supermemory, byterover, hindsight, holographic, openviking,
retaindb. See [[hermes-agent-memory]].

## Plugins-vs-core policy

The distinction is explicit in `AGENTS.md`:

- Plugins live in their **own directory** and work within the ABCs/hooks the
  core provides; if a plugin needs more, the guidance is to widen the generic
  plugin surface rather than special-case it in core (AGENTS.md:123-125).
- Third-party integrations ("someone else's product" plugins) do NOT land
  under `plugins/` in core.
- Built-in gateway behavior that ships with Hermes lives in
  `gateway/builtin_hooks/` ("Built-in gateway hooks that are always
  registered") — distinct from user-facing plugin hooks.

## Related

- [[hermes-agent-architecture]] -- Overall architecture (layer diagram shows plugins as an edge subsystem)
- [[hermes-agent-cli]] -- CLI (plugins may register subcommands + slash commands)
- [[hermes-agent-memory]] -- Memory subsystem (8 memory provider plugins)
- [[hermes-agent-skills]] -- Skills (directory-based extension; plugins can also provide skills, e.g. `superpowers:skill-name`)

## Links

- Framework: `sources/hermes-agent/hermes_cli/plugins.py`
- Plugins: `sources/hermes-agent/plugins/`
- Policy: `sources/hermes-agent/AGENTS.md`
