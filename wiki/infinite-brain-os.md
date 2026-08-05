---
name: infinite-brain-os
tags: [infinite-brain-os, ai-agents, memory, knowledge-graph, agent-memory]
description: "Infinite memory and knowledge system for AI agents"
source: sources/infinite-brain-os/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Infinite Brain OS

| Field | Value |
|---|---|
| **Origin** | [thejosephov/infinite-brain-os](https://github.com/thejosephov/infinite-brain-os) |
| **Source** | `sources/infinite-brain-os/` |
| **Repomix** | `raw/infinite-brain-os/infinite-brain-os.xml` |
| **Codegraph** | `graphs/infinite-brain-os/` |

## Overview

Infinite Brain OS is a git-backed operating system for running a business with AI agents. It uses plain Markdown and YAML files organized into a typed entity graph — commands, agents, skills, rules, workflows, tools, knowledge namespaces, data pointers, memory nodes, projects, and departments — that any file-reading AI agent can navigate, read, and write. No database, no server, no vendor lock-in.

The system addresses a fundamental problem in agent-driven business operations: how do AI agents reliably access the knowledge, decisions, rules, and procedures they need to act on behalf of a business, and how do they record what they did? Infinite Brain OS structures this as a **knowledge OS** with namespaced knowledge that follows a strict promotion path (from raw source through synthesis to operator-approved canon), a contract layer (`_system/`) with schema validation, and a session audit trail that registers every agent interaction.

The project ships with a complete fictional worked example — Emberline Studio, a candle business — that demonstrates every entity type working together through cross-linked files. Eight namespace profile references serve as copyable scaffolds for building real business knowledge structures. The full reference architecture is documented in `knowledge/ai-architecture/`.

## Key Features

- **Git-Backed Persistence** — The entire operating state is a git repository. Every file is versioned, diffs show what changed, and branches enable experimentation. Agents read files directly via Read, Grep, and Glob — no external index required
- **Namespace-First Knowledge Architecture** — Knowledge is organized into namespaces (`knowledge/<namespace>/`), each with a standard base structure: `INDEX.md`, `canon/` (operator-approved truth), `playbooks/` (procedures), `support/` (provenance), and `synthesis/` (derived thinking). Eight namespace profiles provide templates for doctrine, data-systems, design-systems, content-strategy, tool-contracts, and more
- **Typed Entity System** — Eleven entity types (Command, Agent, Skill, Rule, Workflow, Tool, Knowledge, Data, Memory, Output, Project) each with canonical locations, typed YAML frontmatter, and lifecycle states: `scratch` → `research` → `candidate` → `canon`. Promotion requires operator approval — agents cannot self-promote
- **Contract Layer with Validation** — `_system/` holds schemas, rules, registries, and `validate.sh`. Every node-bearing file carries typed YAML frontmatter with minimum required fields (`id`, `type`, `namespace`, `lifecycle_state`). Running `bash _system/validate.sh` verifies the entire graph is consistent and all wikilinks resolve
- **Session Audit Trail** — Every non-trivial agent session is registered under `sessions/active/`, with transcript logs under `sessions/logs/`, running notes, and closeout reviews under `sessions/reviews/`. Completed sessions are moved to `sessions/closed/`
- **Dual-Adapter Architecture** — Executable entities (commands, agents, skills, rules) live canonically in `entities/` and are loaded through runtime adapter shims (`.claude/`, `.codex/`). Editing the canonical file then running `bash sync-adapters.sh` keeps shims in sync — agents never edit shims directly
- **Obsidian Integration** — Ships `.obsidian/` vault configuration, making the entire knowledge OS browsable as an Obsidian vault with wikilinks, graph view, and visual navigation
- **Decision Documentation** — The `docs/` directory includes onboarding walkthroughs, an architecture overview, and an onboarding interview (`docs/onboard-business.md`) that maps real business operations onto the OS structure

## Architecture

Infinite Brain OS follows a flat git-repository structure with typed subdirectories:

```
_system/           The operative contract: schemas, rules, registries, validate.sh
├── namespaces/    — Namespace registration and profile assignments
├── session-ledger-rules.md
└── validate.sh    — Frontmatter and wikilink validation script

knowledge/         Namespace-first knowledge graph (the doctrine and your domains)
├── ai-architecture/  — Full reference architecture (read-first doctrine)
├── personal-operator/ — Operator's own reduced skeleton
├── emberline-studio/  — Worked example namespace (fictional candle studio)
└── _examples/        — 8 unregistered profile reference scaffolds

entities/          Canonical executable entities
├── commands/      — Reusable agent commands
├── agents/        — Agent definitions with tool assignments
├── skills/        — Reusable skill definitions
└── rules/         — Business rules and constraints

.claude/           — Runtime adapter shims for Claude Code
.codex/            — Runtime adapter shims for Codex

workflows/         Agentic reasoning pipelines (Markdown)
automations/n8n/   Deterministic workflows (JSON + brain-record companion)

tools/             Pointer nodes over bounded capabilities
departments/       Assemblies over entities: one folder per operating lane
projects/          One PLAN.md per project with inline tasks
intake/            Inbound flow: source captures, routing, processed receipts
data/              Pointers to where live numbers live (never the numbers themselves)
memory/            Reviewed learnings from past sessions
outputs/           Produced artifacts with lineage metadata
sessions/          The full audit trail of AI work sessions
parties/           Registered parties: brands/ and clients/ (party registry + template)
swarms/            Multi-agent execution sprints (Sprints/)
secrets/           Pointers/references to secrets — never secret values
synthesis/         Derived thinking surfaces
repo-registry/     Registered external repositories (template + registry rules)
docs/              Setup, retrieval, and onboarding documentation

PROVENANCE.yml         Repo-level provenance declaration
OBSIDIAN-DASHBOARD.md  Obsidian dashboard entry point
```

### The Entity Lifecycle

Every entity progresses through four lifecycle states:

1. **scratch** — New, possibly wrong, unvalidated
2. **research** — Validated, worth refining
3. **candidate** — Nominated for promotion, under review
4. **canon** — Promoted, operator-approved. Canon is never self-approved by an agent

Promotion moves forward through review, never by an agent's own declaration. In multi-repo deployments (a company canon repo plus personal working repos), `canon` lives upstream; the standalone starter holds all four states locally with the same discipline.

### The Contract Rules

The system is governed by explicit rules that `validate.sh` enforces:

- Every node-bearing file carries typed YAML frontmatter with at minimum `id`, `type`, `namespace`, and `lifecycle_state`. Ids are kebab-case and stable
- Wikilinks must resolve within the repository
- Canon is operator-approved, always. Agents draft; the operator signs
- The repo never stores live numbers, live queues, or secrets — pointers only
- Sessions that touch the repo are registered, logged, and closed out in `sessions/`
- No em dashes or en dashes anywhere in any file (enforced by validator)

### Frontmatter Contract

Every node-bearing file requires frontmatter with:
```yaml
---
id: kebab-case-id
type: command|agent|skill|rule|workflow|tool|knowledge|data|memory|output|project
namespace: namespace-name
lifecycle_state: scratch|research|candidate|canon
---
```

Serious nodes add `summary`, `confidence`, `retrieval_class`, `export_class`, `edges`, and `created` fields for richer graph traversal.

## Getting Started

```bash
git clone <this-repo> my-brain && cd my-brain
bash _system/validate.sh     # Verifies contract: zero errors on fresh clone
claude                       # Or any agent of choice; CLAUDE.md orients it
```

Then say to your agent: "Read START-HERE.md and give me the tour." The fifteen-minute tour walks through eight files across the entity types:

1. `knowledge/emberline-studio/canon/brand-essentials.md` — A canon knowledge node
2. `entities/rules/studio-brand-voice.md` — A rule derived from canon
3. `entities/skills/write-product-description.md` — A skill applying the rule
4. `entities/agents/studio-inbox-triage.md` — An agent using both
5. `workflows/weekly-studio-review.md` — A workflow reading data pointers and memory
6. `outputs/2026-06-05-spring-collection-brief.md` — A produced artifact with lineage
7. `projects/_example/PLAN.md` — The work container
8. `departments/example-studio-ops/INDEX.md` — The assembly of all above

## Related

- [[Mnemosyne]] — Agent memory system that complements Infinite Brain OS's knowledge namespace architecture
- [[materia]] — Agent framework with memory primitives that can integrate with Infinite Brain OS's entity graph
- [[hermes-agent]] — Multi-platform agent gateway with skill system, a natural runtime for Infinite Brain OS's entities
- [[openclaw]] — Personal AI agent platform that can consume Infinite Brain OS's structured knowledge
- [[n8n]] — Workflow automation platform, used by Infinite Brain OS for deterministic workflows stored in `automations/n8n/`
- [[graphify]] — Knowledge graph construction that shares Infinite Brain OS's emphasis on typed relationships between entities
