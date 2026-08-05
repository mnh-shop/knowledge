---
name: openclaw-automation
tags: [agent-gateway, automation, cli, cron, hooks, openclaw, sqlite, taskflow, typescript, webhooks]
description: OpenClaw Automation
source: sources/openclaw/
---

# OpenClaw Automation
**Source:** `sources/openclaw/`

OpenClaw runs background work through tasks, scheduled jobs, event hooks, and standing instructions. The decision guide lives in `docs/automation/index.md`; the scheduler implementation is `src/cron/`, and the CLI exposes `cron`, `hooks`, `webhooks`, `tasks`, and `commitments` subcommands.

## Cron (Scheduled Tasks)

Cron is the Gateway's built-in scheduler (`docs/automation/cron-jobs.md`, `src/cron/`):

- Runs **inside the Gateway process** — the Gateway must be running for schedules to fire.
- Job definitions, runtime state, and run history persist in the shared SQLite state DB (`openclaw-state-db`), so restarts do not lose schedules.
- Every cron execution creates a background task record.
- One-shot jobs (`--at`) auto-delete after success by default; `--keep-after-run` keeps them.
- Per-run wall-clock budgets: `--timeout-seconds` for isolated agent-turn jobs (plus cron's 60-minute watchdog), 10 minutes for command jobs, 5 minutes for script payloads.
- On Gateway startup, overdue isolated agent-turn jobs are rescheduled instead of replayed immediately.

`src/cron/` key modules: `schedule.ts`, `parse.ts`, `service.ts` (+ `service.*.test.ts` covering restart catch-up, duplicate-timer prevention, top-of-hour stagger), `delivery.ts`/`delivery-plan.ts`/`delivery-target-validation.ts` (output to chat channel, webhook, or nowhere), `isolated-agent/` (detached agent-turn runs), `heartbeat-*.ts`, `session-reaper.ts`, `pacing.ts`, `stagger.ts`, `active-jobs.ts`, `store.ts`.

### Webhooks

Webhook documentation moved into `docs/automation/cron-jobs.md#webhooks` (the old `docs/automation/webhook.md` is a redirect). Webhook triggers wake the scheduler via the Gateway. Related trigger surfaces: **poll** (`docs/automation/poll.md` → `openclaw message poll`) and **Gmail PubSub** (`docs/automation/gmail-pubsub.md` → `docs/automation/cron-jobs.md#gmail-pubsub-integration`).

## Tasks (Activity Ledger)

Background tasks (`docs/automation/tasks.md`) track work that runs outside the main conversation session: ACP runs, subagent spawns, cron job executions, and CLI-initiated operations. Tasks are **records, not schedulers** — cron and heartbeat decide when work runs; tasks track what happened.

- State machine: `queued → running → terminal` (succeeded, failed, timed_out, cancelled, or lost).
- Not every agent run creates a task — heartbeat turns and normal interactive chat do not; all cron executions, ACP spawns, subagent spawns, gateway-dispatched CLI agent commands, and agent-started background `exec` commands do.
- Completion is push-driven: detached work can notify directly or wake the requester session/heartbeat.
- `openclaw tasks list` and `openclaw tasks audit`; terminal records pruned after 7 days (`lost` records after 24 hours).

**TaskFlow** (`docs/automation/taskflow.md`) is the durable multi-step orchestration layer: revision-tracked, multi-step research-then-summarize style flows (Task Flow = orchestration; tasks = ledger).

## Hooks

Two hook surfaces exist:

- **Plugin hooks** (`docs/plugins/hooks.md`, `src/plugins/hooks.ts`) — in-process `api.on(...)` extension points with phase hooks (`before_tool_call`, `after_tool_call`, `before_agent_reply`, etc.). See the plugins domain doc.
- **Internal hooks** (`docs/automation/hooks.md`) — small operator-installed `HOOK.md` scripts reacting to command and Gateway events such as `/new`, `/reset`, `/stop`, `agent:bootstrap`, or `gateway:startup`. Managed via the `openclaw hooks` CLI (`src/cli/hooks-cli.ts`).

## Standing Intents, Commitments, and Standing Orders

- **Standing intents** (`docs/concepts/standing-intents.md`) — prospective memory compiled out of the model: time-based intents become cron jobs; event-based intents go into a per-agent SQLite table via the `intent` tool with machine-checkable trigger fields (keywords, trigger embedding, channel/sender scope, expiry, fire budget, cooldown). Lifecycle states: pending, armed, fired, done, cancelled, expired. Anti-nagging defaults: 24h cooldown, budget of 3 fires, 90-day expiry, at most 3 intents injected per turn.
- **Commitments** — CLI surface `openclaw commitments` (registered in `src/cli/command-catalog.ts`; `src/cli/commands/commitments.ts` implements list/dismiss commands).
- **Standing orders** (`docs/automation/standing-orders.md`) — permanent operating authority defined in the agent workspace (`AGENTS.md` or a referenced `standing-orders.md`): scope, triggers, approval gates, escalation rules.
- **Heartbeat** — periodic context-aware awareness checks, distinct from exact-timing cron; see `docs/automation/cron-vs-heartbeat.md` and `heartbeat-monitor.ts` in `src/cron/`.

## CLI Subcommands

| Command | Purpose | Source |
|---------|---------|--------|
| `openclaw cron` | create/list/get/show/runs for scheduled jobs | `src/cli/cron-cli.ts` |
| `openclaw hooks` | manage internal `HOOK.md` hooks | `src/cli/hooks-cli.ts` |
| `openclaw webhooks` | manage webhook triggers | `src/cli/webhooks-cli.ts` |
| `openclaw tasks` | list/audit background tasks | `src/cli/commands/tasks.ts` |
| `openclaw commitments` | list/dismiss commitments | `src/cli/commands/commitments.ts` |
| `openclaw message poll` | interactive polls | `docs/cli/message` |

## Key Source Files

| File | Purpose |
|------|---------|
| `docs/automation/index.md` | Automation decision guide (cron vs heartbeat vs hooks vs standing orders) |
| `docs/automation/cron-jobs.md` | Scheduled tasks, webhooks, Gmail PubSub |
| `docs/automation/tasks.md` | Background task ledger |
| `docs/automation/taskflow.md` | Task Flow orchestration |
| `src/cron/service.ts` | Cron scheduler service |
| `src/cron/schedule.ts`, `parse.ts` | Schedule parsing and normalization |
| `src/cron/delivery.ts` | Job output delivery (channel/webhook/none) |
| `src/cron/isolated-agent.ts` | Detached agent-turn runs |
| `src/cron/heartbeat-monitor.ts` | Heartbeat machinery |
| `src/cli/cron-cli.ts` | cron CLI |

## Related

- [[domains/architecture/openclaw-architecture.md]] — Overall system architecture
- [[domains/plugins/openclaw-plugins.md]] — Plugin hooks (in-process phase hooks)
- [[domains/memory/openclaw-memory.md]] — Standing intents as prospective memory
- [[wiki/openclaw.md]] — Wiki entry
