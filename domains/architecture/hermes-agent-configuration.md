---
name: hermes-agent-configuration
tags: [cli, config, configuration, hermes-agent, secrets, yaml, env]
description: "Hermes Agent configuration reference: 81 top-level config keys, env vars, secrets management, profiles, and config loaders"
source: sources/hermes-agent/
---

# Hermes Agent Configuration Reference

Hermes Agent configuration is layered: a pure-data defaults module
(`hermes_cli/config_defaults.py`), a user YAML file (`~/.hermes/config.yaml`),
a secrets-only env file (`~/.hermes/.env`), and CLI overrides. This page
documents the 81 top-level config keys and the resolution order.

## Config File Architecture

| File | Format | Purpose |
|------|--------|---------|
| `~/.hermes/config.yaml` | YAML | All behavioral settings (model, providers, tools, gateway, security, cron, kanban, ...) |
| `~/.hermes/.env` | `KEY=value` | **Secrets only** — API keys, tokens, passwords |
| `~/.hermes/auth-profiles.json` | JSON | Multiple API credential sets |

**House rule (from the repo's AGENTS.md):** `.env` is for secrets only. All
behavioral settings — timeouts, thresholds, feature flags, display prefs — go
in `config.yaml`. New `HERMES_*` env vars for non-secret config are rejected;
internal env mirrors (e.g. `terminal.cwd` → `TERMINAL_CWD`) are bridged from
`config.yaml` in code, not the other way.

## Config Loaders

Three load paths — know which one you're in when adding a key:

| Loader | Used by | Merges |
|--------|---------|--------|
| `load_cli_config()` | CLI mode (`cli.py`) | CLI-specific defaults + user YAML |
| `load_config()` | `hermes tools`, `hermes setup`, most subcommands (`hermes_cli/config.py`) | `DEFAULT_CONFIG` + user YAML |
| Direct YAML load | Gateway runtime (`gateway/run.py`, `gateway/config.py`) | Reads user YAML raw |

Resolution order everywhere: **defaults → config file → env → CLI flags.**
New keys in an existing section are absorbed automatically by deep-merge; a
`_config_version` bump (`_config_version` key) is only needed for active
migrations that transform existing user config.

## The 81 Top-Level Config Keys

Source of truth: `DEFAULT_CONFIG` in `hermes_cli/config_defaults.py`. Keys are
grouped below by concern (the file order is alphabetical).

### Core / Model

| Key | Purpose |
|-----|---------|
| `model` | Default model id (empty → resolved from provider later) |
| `model_catalog` | Model catalog overrides / additions |
| `vertex` | Google Vertex AI provider settings |

### Providers & Routing

| Key | Purpose |
|-----|---------|
| `providers` | Provider profiles (base_url, api_key refs, api_mode) |
| `fallback_providers` | Ordered failover list when the primary errors |
| `credential_pool_strategies` | Rotation/selection strategy across pooled credentials |
| `openrouter` | OpenRouter provider settings (routing, app tags) |
| `bedrock` | AWS Bedrock provider settings |
| `auxiliary` | Per-task overrides for side-LLM work (curator, vision, embeddings, title gen, session search) — each task pins its own provider/model/base_url/max_tokens (`agent/auxiliary_client.py::_resolve_auto`) |

### Agent Loop & Sessions

| Key | Purpose |
|-----|---------|
| `agent` | Loop limits: `max_turns`, `gateway_timeout`, `restart_drain_timeout`, `build_wait_timeout`, `api_max_retries`, `service_tier`, `tool_use_enforcement`, intent-ack nudges |
| `max_concurrent_sessions` | Global active chat session cap (None/0 = unbounded) |
| `max_live_sessions` | Soft LRU cap on in-memory TUI/desktop/dashboard sessions (default 16); gateway evicts least-recently-active detached sessions |
| `streaming` | Streaming/token-delivery behavior |
| `human_delay` | Simulated human-typing delay between messages |
| `prefill_messages_file` | File with prefill (assistant warm-up) messages |
| `moa` | Mixture-of-Agents settings |
| `delegation` | Subagent controls: `max_concurrent_children`, `max_spawn_depth`, `child_timeout_seconds`, `orchestrator_enabled`, `subagent_auto_approve`, `inherit_mcp_toolsets`, `max_iterations` |
| `tool_loop_guardrails` | Guards against runaway tool-call loops |
| `tool_output` | Tool output capture/truncation policy |

### Tools & Execution

| Key | Purpose |
|-----|---------|
| `toolsets` | Default enabled toolsets (e.g. `["hermes-cli"]`) |
| `tools` | Per-platform `enabled`/`disabled` toolset lists |
| `mcp` | MCP client settings (timeouts, stdio watchdog, OAuth) |
| `mcp_discovery_timeout` | Cap on MCP server discovery during agent build |
| `web` | Web tool settings |
| `browser` | Browser automation settings (Camoufox/CDP) |
| `computer_use` | Computer-use tool gating |
| `code_execution` | Sandboxed code execution settings |
| `lsp` | LSP integration settings |
| `x_search` | X/Twitter search settings |
| `terminal` | Terminal backend + cwd (`terminal.cwd` — the gateway's working dir, bridged to `TERMINAL_CWD`) |
| `paste_collapse_threshold`, `paste_collapse_threshold_fallback`, `paste_collapse_char_threshold` | Long-paste collapsing behavior |

### Memory & Context

| Key | Purpose |
|-----|---------|
| `memory` | Memory backend (sqlite, mnemosyne, honcho, mem0, ...) via `memory.provider` |
| `context` | Context window management |
| `checkpoints` | Checkpointing of sessions/turns |
| `context_file_max_chars` | Truncation cap for context files |
| `file_read_max_chars` | Truncation cap for `read_file` |
| `compression` | Context compression (the one permitted mid-conversation mutation) |
| `prompt_caching` | Prompt-cache reuse policy (cache safety is sacred) |
| `goals` | Persistent goal tracking |
| `skills` | Skill loading + per-skill config (`skills.config.<key>`) |
| `curator` | Background skill-maintenance: `enabled`, `interval_hours`, `min_idle_hours`, `stale_after_days`, `archive_after_days`, `backup.*` |
| `honcho` | Honcho memory-provider settings |

### Gateway & Platforms

| Key | Purpose |
|-----|---------|
| `gateway` | Gateway: dashboard flags, api_server host/port/enabled, api key |
| `dashboard` | Dashboard-specific settings |
| `slack`, `discord`, `whatsapp`, `telegram`, `mattermost`, `matrix` | Per-platform adapter settings |
| `platform_hints` | Platform behavior hints |
| `sessions` | Session lifecycle settings |
| `timezone` | Timezone used by cron scheduling and logs |
| `display` | CLI/TUI display, skins (`display.skin`), background-process notification verbosity |

### Security & Approvals

| Key | Purpose |
|-----|---------|
| `security` | Security posture (path security, advisory checks) |
| `approvals` | Approval workflow defaults (which actions need approval) |
| `command_allowlist` | Allowed shell commands for the terminal tool |
| `quick_commands` | User-defined slash commands |
| `hooks_auto_accept` | Auto-accept policy for hook actions |
| `privacy` | Privacy/redaction settings |
| `proxy` | Outbound proxy settings |
| `secrets` | Secrets-manager integration (`secrets.bitwarden.*`, 1Password) |
| `desktop` | Electron desktop app settings |
| `personalities` | Named persona definitions |

### Automation (cron / kanban / hooks)

| Key | Purpose |
|-----|---------|
| `cron` | Scheduler: `model`, `model_provider`, `model_drift_guard`, scheduler `provider` (builtin ticker vs chronos), delivery/mirror defaults |
| `kanban` | Board dispatcher: `auto_subscribe_on_create`, `dispatch_in_gateway`, `dispatch_interval_seconds`, `failure_limit` |
| `hooks` | Lifecycle hook configuration |

### Observability, Logging & Updates

| Key | Purpose |
|-----|---------|
| `monitoring` | Gateway health & diagnostics OTLP export endpoint + redaction posture |
| `telemetry` | Telemetry/analytics opt-in gates |
| `logging` | Log levels, rolling logs (`agent.log`, `errors.log`, `gateway.log`) |
| `updates` | Auto-update policy |
| `onboarding` | First-run onboarding flow settings |
| `_config_version` | Config schema version (bumped only for active migrations) |

### Voice / TTS / STT

| Key | Purpose |
|-----|---------|
| `tts` | Text-to-speech settings |
| `stt` | Speech-to-text settings |
| `voice` | Voice session settings |
| `wake_word` | Wake-word detection |

## Environment Variables (`.env.example`)

`hermes_cli/config_defaults.py` also exports `OPTIONAL_ENV_VARS` (line 3018) —
a metadata registry feeding user-facing surfaces (dashboard keys page, `hermes
setup` prompts). The template lives at `.env.example` (496 lines).

Each entry carries: `description`, `prompt` (display name), `url`, `password`
(bool), and `category` — one of `provider`, `tool`, `messaging`, `setting`.

```yaml
# .env.example categories (abridged)
ANTHROPIC_API_KEY=            # provider
OPENAI_API_KEY=               # provider
GEMINI_API_KEY=               # provider
TELEGRAM_BOT_TOKEN=           # messaging
DISCORD_BOT_TOKEN=            # messaging
SLACK_BOT_TOKEN=              # messaging
BRAVE_API_KEY=                # tool
```

Provider keys are documented in [[hermes-agent-deployment]]; the full list is
the template itself. The convention: new secrets are added to
`OPTIONAL_ENV_VARS` **only**; new behavior goes to `DEFAULT_CONFIG`.

## Profiles (multi-instance)

Profiles give fully isolated instances, each with its own `HERMES_HOME`
(config, API keys, memory, sessions, skills, gateway). Mechanism:
`_apply_profile_override()` in `hermes_cli/main.py` sets `HERMES_HOME` before
any module imports; `get_hermes_home()` / `display_hermes_home()` in
`hermes_constants.py` resolve profile-aware paths.

```bash
hermes -p client-a                      # run under a profile
hermes setup --profile client-b         # create + setup
hermes -p client-a config set provider anthropic
```

Profile roots are HOME-anchored (`~/.hermes/profiles/<name>`, not
HERMES_HOME-anchored) so `hermes -p x profile list` sees all profiles. Code
that touches state must use `get_hermes_home()`, never `Path.home() / ".hermes"`.

## Secrets Management

Two layers:

### 1. Env-file secrets

`~/.hermes/.env` holds credentials; `${VAR}` references in `config.yaml`
resolve at runtime. The Quadlet deployment injects them via `EnvironmentFile=`
(see [[hermes-agent-deployment]]).

### 2. Secrets managers (`hermes secrets`)

`hermes_cli/secrets_cli.py` wires the `hermes secrets` CLI tree; backends live
in `agent/secret_sources/`:

| Backend | Source module | Typical use |
|---------|---------------|-------------|
| Bitwarden | `agent/secret_sources/bitwarden.py` | Vault sync into `.env` |
| 1Password | `agent/secret_sources/onepassword.py` | 1Password vault secrets |
| Command | `agent/secret_sources/command.py` | Shell-out secret provider |
| Registry | `agent/secret_sources/registry.py` | Backend discovery/registration |

```bash
hermes secrets bitwarden setup --server-url https://vault.bitwarden.com
hermes secrets bitwarden sync      # fetch secrets now, report what changed
hermes secrets bitwarden status
hermes secrets bitwarden disable   # flips secrets.bitwarden.enabled to False
```

The `secrets.*` config section gates each manager. 1Password support exists
(`hermes secrets op ...`) with the same enable/sync/status/disable surface.

## Verification Notes

- **Key count:** 81 top-level keys in `DEFAULT_CONFIG`
  (`hermes_cli/config_defaults.py`), verified by extracting the top-level
  string keys.
- **`.env.example`:** 496 lines (verified `wc -l`).
- **`OPTIONAL_ENV_VARS`:** defined at `hermes_cli/config_defaults.py:3018`.

## Related

- [[hermes-agent-deployment]] -- Deployment & env var reference
- [[hermes-agent-architecture]] -- System architecture
- [[hermes-agent-cron]] -- Cron scheduler (cron.* config)
- [[hermes-agent-kanban]] -- Multi-agent kanban (kanban.* config)
- [[hermes-agent-observability]] -- OTLP monitoring (monitoring.* config)
- [[hermes-agent-research-tools]] -- Curator + data-gen tooling
