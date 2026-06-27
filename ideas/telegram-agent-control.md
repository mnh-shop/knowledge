---
name: telegram-agent-control
description: "Deterministic Telegram-controlled automation stack — n8n control, AgentField execution, Hermes advisory. Workspace prototype."
tags: [ideas, deployment, telegram, n8n, agentfield, hermes, control-plane]
source: workspace/deployment-setup-automation/agent-control-stack/
---

> **⚠️ Idea / Prototype — not production-grade.**
> This is a synthesized summary of the agent-control-stack workspace prototype
> (README, ROADMAP, ONBOARDING). Not yet battle-tested.

## Architecture

**Authoritative control path:**
```
Telegram → n8n → PostgreSQL ops ledger → AgentField API → n8n → Telegram
```

**Advisory path:**
```
Hermes → advisory output → PostgreSQL ops ledger → n8n/operator review
```

## Design Principles

- Keep the control path deterministic
- Use APIs, not implicit database coupling, between systems
- Treat Hermes as a generator/reviewer, not the workflow source of truth
- Keep generated candidates separate from canonical deployment assets

## Deployment Targets

| Target | Runtime | Purpose |
|---|---|---|
| Local | OrbStack + Compose | Prove contracts and control loops |
| Production | Rootless Podman + Quadlet | Full service isolation, systemd lifecycle |
| Pi lite | Reduced stack | Control/relay node |

## Default Baseline Stack

1. `postgres` — Durable state
2. `n8n` — Authoritative workflow controller
3. `agentfield` — Multi-agent execution

Optional layers: hermes, af-deep-research, swe-af, browser-worker, redis

## Use-Case Packs

| Pack | Services |
|---|---|
| core-control | Postgres + n8n + AgentField + Telegram bot |
| research | + af-deep-research |
| swe | + swe-af |
| browser-osint | + browser-worker |
| architecture-review | Hermes architect profile |
| grill-me | Hermes interview profile |
| adversarial-review | Hermes challenger profile |
| kanban-orchestration | Hermes local-admin + planner |
| nightly-candidates | Bounded overnight generation |
| pi-lite-relay | Small-footprint control |

## Build Phases

| Phase | Goal |
|---|---|
| 0 | Contracts: status model, Telegram commands, ops ledger, API contracts |
| 1 | Core local substrate: postgres + n8n + agentfield in OrbStack |
| 2 | Ops ledger: task/run/checkpoint/approval models in PostgreSQL |
| 3 | Telegram control loop: command vocabulary, approval flows |
| 4 | Research lane: af-deep-research first real workload |
| 5 | Hermes advisory: local-admin, researcher, architect-reviewer profiles |
| 6 | SWE lane: swe-af as second workload |
| 7 | Overnight candidate loop: bounded automated generation |
| 8 | Linux Quadlet target: production service graph |
| 9 | Pi lite target: reduced stack for small hardware |

## Key Rule

`n8n` owns official workflow state. `AgentField` executes. `Hermes` critiques.

## Related

- [[setup-factory/v1-stack-architecture|V1 Stack Architecture]] — Related security-boundary architecture pattern
- [[hermes-local-admin-setup|Hermes Local-Admin Setup]] — Hermes multi-profile pattern
- [[setup-factory/README|Setup Factory]] — The manifest-driven generator subsuming this pattern
