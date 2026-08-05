---
name: hermes-agent-cron
tags: [automation, cli, cron, gateway, hermes-agent, scheduler, scale-to-zero]
description: "Hermes Agent cron: scheduler internals, cronjob model tool, hermes cron CLI, and the scale-to-zero Chronos provider"
source: sources/hermes-agent/
---

# Hermes Agent Cron System

Hermes schedules unattended agent jobs with an internal, JSON-file-based
scheduler that runs **inside the gateway** — there is no standalone cron
daemon and no external `crontab` executable required. Agents schedule jobs via
the `cronjob` model tool; users via `hermes cron <verb>` or the `/cron` slash
command; and deployments needing scale-to-zero use the Chronos provider
(`plugins/cron_providers/chronos/`).

## Architecture Map

```
┌─ Trigger (Axis B) ────────────────────────────────┐
│  builtin ticker  (cron/scheduler.py, 60s loop,    │
│                   runs inside gateway/run.py)      │
│  chronos provider (plugins/cron_providers/chronos)│  ← scale-to-zero, NAS webhook
└───────────────┬───────────────────────────────────┘
                │ due job
┌───────────────▼───────────────────────────────────┐
│  Job store     cron/jobs.py        (create/edit)   │
│  Lifecycle     cron/lifecycle_guard.py (shared by   │
│                CLI + cronjob tool)                 │
│  Executions    cron/executions.py (run records)     │
└───────────────┬───────────────────────────────────┘
                │ spawns agent session (skip_memory=True)
┌───────────────▼───────────────────────────────────┐
│  Delivery      origin · local · platform:chat_id    │
│                mirror_delivery (continuable thread)  │
└────────────────────────────────────────────────────┘
```

| Module | Purpose |
|--------|---------|
| `cron/scheduler.py` | `tick()` loop; gateway calls it every 60s from a background thread; file-lock `~/.hermes/cron/.tick.lock` prevents duplicate ticks across processes |
| `cron/jobs.py` | Job store — create/list/update/pause/resume/remove, per-job field validation |
| `cron/executions.py` | Execution records and run history |
| `cron/lifecycle_guard.py` | Gateway-lifecycle guards shared by every job-creation path (CLI + model tool) |
| `cron/scheduler_provider.py` | `resolve_cron_scheduler()` — builtin vs installed provider (chronos) |
| `cron/scripts/` | Support scripts |
| `tools/cronjob_tools.py` | `cronjob` model tool (registry name `cronjob`, toolset `cronjob`) |
| `hermes_cli/cron.py` | `hermes cron` command handler (list/create/edit/pause/resume/run/remove) |
| `hermes_cli/subcommands/cron.py` | `hermes cron` argparse tree |
| `plugins/cron_providers/chronos/` | NAS-mediated managed cron provider (scale-to-zero) |

## The `cronjob` Model Tool

`tools/cronjob_tools.py` registers a single `cronjob` tool (`toolset="cronjob"`,
emoji ⏰) with a JSON schema of actions (`create`, `list`, `run`, `edit`,
`pause`, `resume`, `remove`, ...). It is gated by
`check_cronjob_requirements()` — available in interactive CLI mode and
gateway/messaging sessions, enabled by truthy `HERMES_INTERACTIVE`,
`HERMES_GATEWAY_SESSION`, or `HERMES_EXEC_ASK` env flags.

Design constraints worth knowing:

- **The agent cannot pin model/provider on job creation.** `model`, `provider`,
  and `base_url` are intentionally NOT read from agent arguments — per-job
  inference pins are user-owned (dashboard, `hermes cron create/edit --model`,
  or hand-edited jobs). This prevents unattended spend from being pointed at a
  different model.
- Cron prompts are hardened: the tool strips potentially hazardous constructs
  and invisible/zero-width unicode before scheduling (`_scan_cron_prompt`,
  `_strip_invisible_unicode`).

## CLI and Slash Command

```bash
hermes cron list [--all]                      # list jobs (incl. disabled)
hermes cron create '30m' 'Summarize the day' --name daily-summary --deliver telegram
hermes cron edit <id> --schedule '0 9 * * *'
hermes cron pause <id> | hermes cron resume <id>
hermes cron run <id>                           # fire now
hermes cron remove <id>
hermes cron status                             # active provider + ticker state
```

The `/cron` slash command is registered in
`hermes_cli/commands.py` (`CommandDef("cron", "Manage scheduled tasks", "Tools & Skills")`).

## Supported Schedule Formats

| Format | Example |
|--------|---------|
| Duration | `30m`, `2h`, `1d` |
| "every" phrase | `every 2h`, `every monday 9am` |
| 5-field cron expression | `0 9 * * *` |
| ISO timestamp (one-shot) | `2026-06-01T09:00:00Z` |

## Per-Job Fields

| Field | Purpose |
|-------|---------|
| `skills` / `skill` | Load specific skills into the job session |
| `model` / `provider` | Inference pin (user-owned, per above) |
| `script` | Pre-run data-collection script; stdout injected into the prompt |
| `no_agent` | `True` turns the script into the entire job (no agent run) |
| `context_from` | Chain job A's last output into job B's prompt |
| `workdir` | Run in a directory (its `AGENTS.md`/`CLAUDE.md` loads) |
| `deliver` | Delivery target: `origin`, `local`, `telegram`, `discord`, `signal`, or `platform:chat_id` |
| `mirror_delivery` | Continuable jobs — user can reply to the delivery; opens a dedicated thread on thread-capable platforms (Telegram topics, Discord/Slack threads), mirrors brief into DM on DM-only platforms. Overrides global `cron.mirror_delivery` per job |
| `reason` | Justification string for the schedule |

## Hardening Invariants

From `docs/automation/` and the scheduler implementation:

- **3-minute hard interrupt** on cron sessions — runaway agent loops cannot
  monopolize the scheduler.
- **Catchup window:** half the job's period, clamped to 120s–2h.
- **Grace window:** 120s for one-shot jobs whose fire time was missed.
- **File lock** at `~/.hermes/cron/.tick.lock` prevents duplicate ticks across
  processes.
- Cron sessions pass `skip_memory=True` by default — memory providers
  intentionally do not run during cron.
- **Deliveries are not mirrored into the target gateway session** — they land
  in their own cron session with a header/footer frame so the main
  conversation's message-role alternation stays intact.
- `mark_running_jobs_interrupted()` handles gateway shutdown so running jobs
  are recorded as interrupted, not silently "ok" (`cron/scheduler.py`).
- Per-job toolset resolution: `_resolve_cron_enabled_toolsets()` merges
  per-job lists with MCP-derived toolsets at fire time.

## Cron Config Section (`cron:`)

Defined in `hermes_cli/config_defaults.py` (verified at line 2052):

| Key | Purpose |
|-----|---------|
| `model_drift_guard` | Fail closed when an unpinned job's current global model/provider differs from its creation-time snapshot — prevents unattended jobs silently inheriting a paid default |
| `model` | Default inference model for cron jobs (Axis A — WHAT model runs). Resolution: per-job pin > `cron.model` > global `model.default` |
| `model_provider` | Inference provider paired with `cron.model` |
| `provider` | Active cron **scheduler** provider (Axis B — WHEN a job fires). Empty = built-in in-process 60s ticker; name an installed provider (`plugins/cron_providers/<name>/`) |
| `mirror_delivery` | Global default for continuable deliveries |

Axis A (inference model) and Axis B (scheduler trigger) are deliberately
independent — swapping the scheduler provider never changes what model jobs
run on.

## Chronos: Scale-to-Zero Provider

`plugins/cron_providers/chronos/` implements the `CronScheduler` interface for
NAS-mediated managed cron. See `docs/chronos-managed-cron-contract.md` and the
[[hermes-agent-deployment]] page for deployment details. Key contract:

- Agent computes next-fire time and asks NAS to arm a one-shot.
- NAS calls the agent back over an authenticated webhook — the machine wakes
  only on a NAS→agent fire (never a periodic wake loop, which would negate
  scale-to-zero).
- Inert unless `cron.provider=chronos`.
- `plugins/cron_providers/chronos/_nas_client.py` is the webhook client;
  `verify.py` validates the contract.

## Related

- [[hermes-agent-deployment]] -- Deployment incl. scale-to-zero section
- [[hermes-agent-configuration]] -- `cron.*` config keys
- [[hermes-agent-kanban]] -- Sibling multi-agent work queue
- [[hermes-agent-observability]] -- Job failure/delivery telemetry surface
