---
name: hermes-agent-kanban
tags: [agent-workflow, cli, dashboard, dispatcher, hermes-agent, kanban, multi-agent, sqlite, systemd]
description: "Hermes Agent kanban: durable SQLite multi-agent board, 12 kanban_* tools, dispatcher, dashboard, and systemd unit"
source: sources/hermes-agent/
---

# Hermes Agent Kanban (Multi-Agent Work Queue)

Hermes kanban is a **durable, SQLite-backed board** that lets multiple
profiles / worker agents collaborate on shared tasks. Users drive it via
`hermes kanban <verb>`; workers spawned by the dispatcher drive it through a
dedicated `kanban_*` model-tool set, so their schema footprint is zero when
they are not inside a kanban task.

## Architecture Map

```
                    ┌─────────────────────────────────────┐
                    │  hermes kanban CLI (hermes_cli/      │
                    │  kanban.py + subcommands)            │
                    └──────────────┬──────────────────────┘
                                   │
        ┌──────────────────────────▼──────────────────────┐
        │  Dispatcher (reclaims stale claims, promotes     │
        │  ready tasks, atomically claims, spawns workers) │
        │  • inside gateway by default (kanban.dispatch_   │
        │    in_gateway: true, tick ~60s)                  │
        │  • standalone systemd unit (DEPRECATED, requires │
        │    --force) plugins/kanban/systemd/              │
        └───────┬──────────────────────────────┬───────────┘
                │ spawns assigned profiles      │ env-pins board
┌───────────────▼────────────────┐  ┌───────────▼─────────────┐
│  Worker agents (profiles)      │  │  Board DB                │
│  kanban_* toolset              │  │  kanban.db (SQLite)      │
│  HERMES_KANBAN_BOARD pinned    │  │  tasks, runs, comments,  │
└────────────────────────────────┘  │  attachments, events     │
                                    └─────────────────────────┘
        plugins/kanban/dashboard/  →  web UI (manifest.json + dist/)
```

## Model Tools (`tools/kanban_tools.py`)

Twelve `kanban_*` tools are registered with `registry.register(...)`
(`toolset="kanban"`):

| Tool | Access | Purpose |
|------|--------|---------|
| `kanban_show` | worker | View a task with comments + events |
| `kanban_complete` | worker | Mark a task done (validates declared artifacts) |
| `kanban_block` | worker | Mark a task blocked |
| `kanban_heartbeat` | worker | Extend the worker's claim (soft liveness) |
| `kanban_comment` | worker | Append a comment / hand off info |
| `kanban_attach` | worker | Attach a local file to a task |
| `kanban_attach_url` | worker | Attach a URL to a task |
| `kanban_attachments` | worker | List a task's attachments |
| `kanban_create` | worker | Spawn follow-up work from within a task |
| `kanban_link` | worker | Add a parent→child dependency |
| `kanban_list` | orchestrator | Board routing (requires `kanban` toolset outside a dispatcher task) |
| `kanban_unblock` | orchestrator | Unblock a task (requires `kanban` toolset outside a dispatcher task) |

### Access Control Model

- **`_check_kanban_mode`** — worker tools require the profile to have the
  `kanban` toolset enabled.
- **`_check_kanban_orchestrator_mode`** — board-routing tools
  (`kanban_list`, `kanban_unblock`) are intentionally reserved: a plain worker
  must use `kanban_complete`, `kanban_block`, `kanban_heartbeat`, or
  `kanban_comment` for its assigned task.
- **`_enforce_worker_task_ownership`** — mutating run-lifecycle tools
  (`kanban_complete`, `kanban_block`, `kanban_heartbeat`) reject calls for a
  task id the worker does not own; a buggy or malicious worker cannot complete
  another worker's task. It must use `kanban_comment` to hand off or
  `kanban_create` to spawn follow-ups.
- **`_reject_delegated_child_mutation`** — delegation children may not mutate
  the board.
- **`kanban_goal_loop` / `kanban_mode` / `kanban_notify` / `kanban_notify_subs`**
  are internal helpers (goal-loop judging, mode checks, subscription
  notifiers), not registered as model tools.

### Claim / Liveness Semantics

- Workers hold **claims** on their task id; `kanban_heartbeat` extends the
  claim so long-running tasks are not reclaimed. Heartbeat can also be driven
  from the environment (`heartbeat_current_worker_from_env`).
- If a claim goes stale, the dispatcher reclaims it and re-promotes the task
  (default tick every 60s).
- `kanban_complete` preserves declared artifacts and can be blocked by
  unresolved `created_cards` — the follow-up cards the worker declared must
  exist before completion succeeds.

## Dispatcher

Long-lived loop that every `dispatch_interval_seconds` (default 60):

1. Reclaims stale claims.
2. Promotes ready (scheduled/unblocked) tasks.
3. Atomically claims a task.
4. Spawns the assigned profile as a worker.

**Default placement: inside the gateway** (`kanban.dispatch_in_gateway: true`
in `hermes_cli/config_defaults.py`) — the cost is ~300µs per idle tick, and
the gateway is the supervisor users already have. A standalone systemd
dispatcher exists for hosts that cannot run the gateway.

## Standalone systemd Unit

`plugins/kanban/systemd/hermes-kanban-dispatcher.service`:

```ini
[Service]
Type=simple
ExecStart=/usr/bin/env hermes kanban daemon --force --interval 60 --pidfile %t/hermes-kanban-dispatcher.pid
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
```

**Marked DEPRECATED** — running it alongside a gateway with
`dispatch_in_gateway=true` is unsupported (two dispatchers racing on the same
`kanban.db`). It now requires `--force` so nobody accidentally double-dispatches.
Per-task worker output lands in `$HERMES_HOME/kanban/logs/<task>.log`.

## CLI (`hermes kanban`)

`hermes_cli/kanban.py` wires the command tree (verified parser verbs):

| Group | Verbs |
|-------|-------|
| Board | `init`, `boards create|list|rm|switch|rename|set-wd` |
| Tasks | `create`, `list` (alias `ls`), `show`, `assign`, `set-model`, `reclaim`, `reassign`, `edit`, `complete`, `block`, `schedule`, `unblock`, `promote`, `archive`, `tail` |
| Dependencies | `link`, `unlink` |
| Attachments | `attach`, `attachments`, `attach-rm` |
| Comments | `comment` |
| Ops | `dispatch`, `daemon` (standalone), `watch`, `stats`, `notify-subscribe`/`notify-list`, `swarm` |
| GC / claims | `gc`, `claim`, `diag` |

Example:

```bash
hermes kanban init
hermes kanban create "Fix flaky test" --assign coder --board default
hermes kanban list
hermes kanban dispatch           # force a dispatch pass
hermes kanban daemon --interval 60   # standalone daemon (needs --force w/ gateway)
```

## Isolation Model

- **Board** is the hard boundary — workers are spawned with
  `HERMES_KANBAN_BOARD` pinned in their env, so they cannot see other boards.
- **Tenant** is a soft namespace *within* a board — one specialist fleet can
  serve multiple businesses with workspace-path + memory-key isolation.
- After `kanban.failure_limit` consecutive non-success attempts on the same
  task (default 2), the dispatcher auto-blocks it to prevent spin loops.

## Kanban Config Section (`kanban:`)

Defined in `hermes_cli/config_defaults.py` (verified at line 2142):

| Key | Default | Purpose |
|-----|---------|---------|
| `auto_subscribe_on_create` | `true` | Auto-subscribe the originating gateway/TUI session to task completion + block events when `kanban_create` is called from a session with a persistent delivery channel — the dispatching agent gets notified instead of polling |
| `dispatch_in_gateway` | `true` | Run the dispatcher inside the gateway process |
| `dispatch_interval_seconds` | `60` | Seconds between dispatcher ticks (lower = snappier pickup; higher = less SQL pressure) |
| `failure_limit` | `2` | Auto-block after this many consecutive non-success attempts |

## Dashboard Plugin

`plugins/kanban/dashboard/` ships a web UI (`manifest.json` + `plugin_api.py`
+ compiled `dist/index.js` + `style.css`) that renders the board and task
streams. Like all plugins, it registers through the PluginManager discovery
path (`hermes_cli/plugins.py`).

## Worker Toolsets

Workers are spawned with the `kanban` toolset so their model-tool schema is
zero when idle (outside a kanban task). Profiles that explicitly enable the
`kanban` toolset outside a dispatcher-spawned task additionally receive the
board-routing tools (`kanban_list`, `kanban_unblock`). Toolset wiring is in
`toolsets.py`; enable/disable per platform via `hermes tools` or
`tools.<platform>.enabled/disabled` in `config.yaml`.

## Related

- [[hermes-agent-architecture]] -- Plugin layer (kanban among subsystems)
- [[hermes-agent-configuration]] -- `kanban.*` config keys
- [[hermes-agent-cron]] -- Sibling scheduler for time-based jobs
- [[hermes-agent-deployment]] -- Profiles enable worker fleets
