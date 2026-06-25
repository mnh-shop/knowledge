---
name: hermes-workspace-swarm-architecture
tags: [hermes, architecture, typescript, agent-gateway, messaging, multi-platform]
description: "Hermes Workspace swarm architecture: multi-agent orchestration via swarm.yaml and swarm-* server modules"
---

# Hermes Workspace — Swarm Architecture

**Source:** `sources/hermes-workspace/`
**Key files:** `swarm.yaml`, `src/server/swarm-*.ts`, `docs/swarm/`

## What it is

The Swarm control plane turns Hermes Workspace into a multi-agent
orchestrator with persistent workers, role-based dispatch, checkpoint
contracts, and a human-in-the-loop review gate.

## The flow

```
User → Orchestrator Chat → Mission Brief
  → Orchestrator routes to role worker(s)
  → Workers execute in persistent tmux sessions
  → Workers checkpoint with proof evidence
  → Orchestrator decides: continue / repair / escalate / inbox
  → Greenlight Gate for risky actions (merge, destructive, external)
```

## Semantic roster (from `swarm.yaml`)

10 workers with defined roles, tools, skills, and MCP servers:

| Worker | Role | Mode | Wrapper | Tools |
|---|---|---|---|---|
| `orchestrator` | Orchestrator / Greenlight Gate | `plan` | `orchestrator:plan` | todo, kanban, delegation, gbrain, etc. |
| `km-agent` | RAZSOC / GBrain Steward | `health` | `km:health` | gbrain, file, obsidian, etc. |
| `builder` | Scoped Implementation | `task` | `builder:task` | terminal, file, browser, gbrain, etc. |
| `reviewer` | Independent Review / Merge Gate | `gate` | `reviewer:gate` | terminal, file, gbrain, etc. |
| `qa` | Browser / Smoke Verification | `smoke` | `qa:smoke` | browser, terminal, vision, gbrain |
| `researcher` | Brain-first Research | `quick` / `autoresearch` | `researcher:quick` | gbrain, web, browser, gbrain |
| `ops-watch` | Local Infra / Health Watch | `health` | `ops:health` | terminal, cronjob, gbrain |
| `maintainer` | Upstream / Patch Hygiene | `check` | `maintainer:check` | terminal, file, web, gbrain |
| `strategist` | Wedges / Bets / Kill Criteria | `review` | `strategist:review` | gbrain, web, gbrain |
| `inbox-triage` | Capture / Discard / Route | `triage` | `inbox:triage` | gbrain, web, file, gbrain |

All workers share:
- Model: GPT-5.5
- MCP server: gbrain (shared)
- Max concurrent tasks: 1
- Accepts broadcast: true
- Greenlight required for destructive/merge/external actions

## Key server modules

| Module | What it does |
|---|---|
| `swarm-mode.ts` | Auto/manual control mode toggle |
| `swarm-lifecycle.ts` | Worker lifecycle (spawn, kill, restart) |
| `swarm-foundation.ts` | Swarm base infrastructure |
| `swarm-roster.ts` | Worker roster management |
| `swarm-missions.ts` | Mission creation and tracking |
| `swarm-checkpoints.ts` | Proof-bearing checkpoint contracts |
| `swarm-memory.ts` | Swarm-specific memory (separate from agent memory) |
| `swarm-notifications.ts` | Notification routing |
| `swarm-chat-reader.ts` | Swarm chat transcript reader |
| `swarm-kanban-store.ts` | Kanban integration for swarm tasks |
| `swarm-profile-config.ts` | Hermes profile config management |
| `swarm-model-resolver.ts` | Model resolution per worker |
| `swarm-runtime-reset.ts` | Runtime state reset |
| `swarm-environment.ts` | Environment path constants |

## Core concepts

### Workers
Named, persistent Hermes Agent instances running inside tmux sessions.
Each worker has a profile, role, mission, skills, tools, and runtime state.

### Greenlight Gate
Risky actions (merge, publish, destructive, credential change) require
human approval. Workers cannot perform these without the orchestrator
escalating to the user.

### Checkpoints
Workers produce proof-bearing checkpoints after each task. The orchestrator
reads checkpoints to decide next action. Format: evidence, blockers,
human-judgment-needed flags.

### Lanes
Workers are organized into lanes by role. The orchestrator routes tasks
to the appropriate lane. Lanes can be inspected from the Swarm UI.

### Repair Playbook
When a worker fails or drifts, the orchestrator can repair via re-prompt,
context refresh, or worker restart — tracked in the playbook.

## Relationship to hermes-agent

The swarm uses `hermes-agent` Hermes Agent instances as workers. Each
worker is a `hermes` CLI process with a Hermes profile configured to the
worker's tools, skills, and MCP servers. The workspace manages these
processes through tmux sessions.

## Related

- [[hermes-workspace]] -- Wiki entry
- [[hermes-workspace-architecture]] -- System architecture
- [[hermes-workspace-api]] -- REST API reference
- [[hermes-workspace-profile]] -- Agent profile
- [[hermes-workspace-deployment]] -- Deployment guide

## Links

- Swarm YAML: `sources/hermes-workspace/swarm.yaml`
- Swarm docs: `sources/hermes-workspace/docs/swarm/`
- Key server: `sources/hermes-workspace/src/server/swarm-*.ts`
- Swarm v2 spec: `sources/hermes-workspace/docs/swarm2-*-spec.md`
- AGENTS.md (worker contract): `sources/hermes-workspace/AGENTS.md`
