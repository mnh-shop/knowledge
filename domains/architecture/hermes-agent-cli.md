---
name: hermes-agent-cli
tags: [architecture, cli, hermes-agent, tui, terminal]
description: "Hermes Agent CLI: 68 builtin subcommands, 90 slash commands, skin engine, profiles, TUI console REPL, and the subcommands/ refactor of the 12k-line main.py god file"
source: sources/hermes-agent/
---

# Hermes Agent CLI

**Codegraph:** `graphs/hermes-agent`
**Source:** `sources/hermes-agent/hermes_cli/`

The CLI is the primary user-facing entry point to Hermes. Historically a
~12,400-line god file (`hermes_cli/main.py`) it is being refactored into
modular subcommand modules under `hermes_cli/subcommands/`. Command surface
splits into **subcommands** (`hermes <cmd>`) and **slash commands** (`/<cmd>`
inside an active session).

## Subcommands (68 builtin)

The authoritative list is the `_BUILTIN_SUBCOMMANDS` frozenset
(main.py:10455), kept in sync with the `subparsers.add_parser("NAME", ...)`
calls in `main()`. It also powers the plugin-import fast-path: `main()` uses
`_first_positional_argv` (main.py:10525) to detect the first positional and
skip eager plugin discovery when the invocation clearly needs no
plugin-registered subcommand.

```
acp            approvals      auth           backup         bundles
chat           checkpoints    claw           completion     computer-use
config         console        cron           curator        dashboard
debug          desktop        doctor         dump           egress
fallback       gateway        gui            help           hooks
import         import-agent   insights       journey        kanban
learning       login          logout         logs           lsp
mcp            memory         memory-graph   migrate        moa
model          monitoring     pairing        pets           plugins
portal         profile        project        prompt-size    proxy
secrets        security       send           serve          sessions
setup          skills         skin           slack          status
sync           tools          uninstall      update         version
webhook        whatsapp       whatsapp-cloud
```

### Gateway subcommands (`hermes_cli/subcommands/gateway.py`)

`run` (foreground, recommended for WSL/Docker/Termux), `start`/`stop`/
`restart` (systemd/launchd service), `status`, `install`, `uninstall`,
`list` (per-profile gateway status), `setup` (configure messaging
platforms), `migrate-legacy`, and `enroll`.

### Notable specialized commands

- `egress` — manages **iron-proxy**, the optional TLS-intercepting outbound
  credential-injection firewall (main.py:11188).
- `secrets` — credential stores `bitwarden` and `op` (1Password)
  (main.py:11143-11161).
- `lsp` — language server tooling (`agent/lsp/cli.py`; client, install,
  manager, protocol, servers, workspace).
- `sessions` — list/export/delete/prune/archive/optimize-storage/repair/
  recover/stats/rename/retitle/browse.
- `moa` — Mixture-of-Agents model slots: list/configure/delete presets.
- `fallback` — provider fallback configuration.
- `computer-use` — desktop automation with install/doctor/perms subcommands.

## Slash commands (90)

Defined declaratively in `COMMAND_REGISTRY` at `hermes_cli/commands.py:101`
(90 `CommandDef` entries). Each entry declares name, help text, category,
aliases, an `execute` handler, and optional flags (e.g. `cli_only`,
`gateway_config_gate`). Commands are resolved by `resolve_command` and
exposed to `--help`, gateway help lines, and the TUI footer.

Representative registry (commands.py:101-330):

| Category | Commands |
|---|---|
| Session | `start`, `new`, `topic`, `clear`, `redraw`, `history`, `save`, `retry`, `prompt`, `undo`, `title`, `handoff`, `branch`, `compress`, `rollback`, `snapshot`, `stop`, `resume`, `sessions`, `background` |
| Approval | `approve`, `deny`, `approvals` |
| Agents | `agents`, `journey` (aliases: `learning`, `memory-graph`), `queue`, `steer`, `goal`, `moa`, `subgoal`, `delegate` |
| Tools & Skills | `tools`, `toolsets`, `skills`, `bundles` (alias `/<name>` for multiple skills), `curator`, `reload` (alias `reload_mcp`), `reload-skills`, `browser`, `plugins` |
| Memory | `memory` (review pending writes / toggle approval gate), `learn`, `init` |
| Info | `status`, `context`, `whoami`, `profile`, `sethome`, `config`, `model`, `usage`, `subscription`, `topup`, `insights`, `platforms`, `platform`, `commands`, `help` |
| Appearance | `skin`, `indicator`, `statusbar`, `footer`, `timestamps`, `diff`, `verbose`, `focus`, `fast`, `yolo`, `personality`, `reasoning`, `battery`, `busy`, `wake` |
| Media | `copy`, `paste`, `image` |
| Cron | `cron`, `suggestions`, `blueprint`, `kanban` |
| System | `codex-runtime`, `update`, `version`, `debug`, `restart`, `quit` |

## Skin engine — `hermes_cli/skin_engine.py` (1,068 lines)

Skins are YAML files in `~/.hermes/skins/` or built-in presets
(skin_engine.py:5). Built-in skins: **default** (line 203), **ares** (287),
**mono** (364), **slate** (408). Fields are optional — missing values inherit
from the `default` skin; paired `light_colors`/`dark_colors` palettes merge
over the default block. Activate with `/skin <name>` or `display.skin: <name>`
in config.yaml. Custom YAML skins are loaded via `_load_skin_from_yaml`
(skin_engine.py:793).

## Profiles

- `-p`/`--profile` is consumed by `_apply_profile_override` (main.py:511,
  runs **before** argparse) — it resolves the active profile, re-routes the
  Hermes root, and re-executes as needed (main.py:684).
- Profiles isolate config, memory, sessions, and credentials per identity
  (the gateway reads `active_profile` from the default root to avoid
  redirecting a running gateway into another profile, main.py:640).
- `hermes profile` manages profiles; `gateway enroll` ties profiles to
  gateway routing.

## TUI console REPL — `hermes_cli/console_engine.py`

A safe command console (`hermes console` / `cmd_console`): `HermesConsoleEngine`
(console_engine.py:481) with `ConsoleCommand` definitions and
`run_console_repl` (1581). Distinct from the TUI itself — it exposes a
curated command subset with its own error handling.

## Modular subcommands refactor

`hermes_cli/subcommands/` now holds: acp, approvals, auth, backup, claw,
config, console, cron, curator, dashboard, debug, doctor, dump, gateway,
gui, hooks, import_agent, import_cmd, insights, login, logout, logs, mcp,
memory, model, monitoring, pairing, plugins, profile, prompt_size, security,
setup, skills, skin, slack, status, sync, tools, uninstall. `main.py`
delegates to these via thin `cmd_*` wrappers (e.g. `cmd_logs` →
`hermes_cli.logs`, `cmd_console` → `run_console_repl`).

## Related

- [[hermes-agent-architecture]] -- Overall architecture; CLI as the primary presentation layer
- [[hermes-agent-plugins]] -- Plugins may register subcommands (`register_cli_command`) and slash commands
- [[hermes-agent-skills]] -- `hermes skills` CLI + `/skills`, `/reload-skills` commands
- [[hermes-agent-memory]] -- `hermes memory` CLI + `/memory`, `/journey` commands

## Links

- Main parser: `sources/hermes-agent/hermes_cli/main.py` (`build_top_level_parser`)
- Slash registry: `sources/hermes-agent/hermes_cli/commands.py`
- Skins: `sources/hermes-agent/hermes_cli/skin_engine.py`
- Console: `sources/hermes-agent/hermes_cli/console_engine.py`
- Subcommands: `sources/hermes-agent/hermes_cli/subcommands/`
