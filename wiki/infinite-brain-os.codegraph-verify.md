---
name: infinite-brain-os-codegraph-verify
tags: [infinite-brain-os, codegraph-verify, memory, ai-agents]
description: "Codegraph Verification: infinite-brain-os — validating wiki claims against indexed source code"
source: sources/infinite-brain-os/
date: 2026-07-12
---

# Codegraph Verification: infinite-brain-os

**Date:** 2026-07-12

## Claim 1: Git-backed persistence with zero external services
- **Wiki says:** "The entire operating state is a git repository. Every file is versioned, diffs show what changed, and branches enable experimentation. Agents read files directly via Read, Grep, and Glob — no external index required."

- **Source evidence:**
  - `.git/` directory confirmed — the repo is a git repository.
  - `README.md` lines 1-14: "A git-backed operating system for running a business with AI agents. Plain Markdown and YAML, readable by any file-reading agent, owned by you. No database, no server, no vendor lock-in."
  - `AGENTS.md` (Codex orientation) line 5: "Agents read git directly via Read, Grep, and Glob. The working tree is the retrieval surface; no external index is required."
  - No Dockerfile, docker-compose.yml, or database config found. The entire state is files in a git repo.
  - Full top-level surface confirmed by listing: `parties/` (brands/, clients/), `swarms/` (Sprints/), `secrets/`, `synthesis/`, `repo-registry/`, plus root files `PROVENANCE.yml` and `OBSIDIAN-DASHBOARD.md` alongside `_system/`, `knowledge/`, `entities/`, `sessions/`, `docs/`, `automations/`, `sync-adapters.sh`, `.claude/`, `.codex/`, `.obsidian/`.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Namespace-first knowledge architecture with promotion path
- **Wiki says:** "Knowledge is organized into namespaces (`knowledge/<namespace>/`), each with a standard base structure. Eight namespace profiles provide templates. Promotion path: raw source → support/ → synthesis/ → canon-candidate → canon."

- **Source evidence:**
  - `knowledge/` directory contains 4 entries: `ai-architecture/`, `emberline-studio/`, `personal-operator/`, `_examples/`.
  - `_system/namespace-profiles.md` — namespace profile definitions.
  - `_system/namespaces/` — namespace registration directory.
  - `knowledge/emberline-studio/` has `INDEX.md`, `canon/`, `concepts/` — confirming base structure.
  - `knowledge/emberline-studio/INDEX.md` lines 5-6: "It carries only INDEX.md, canon/, and concepts/: the smallest namespace the contract allows."
  - `knowledge/_examples/` — 8 unregistered profile reference scaffolds.
  - `AGENTS.md` (Codex orientation) documents promotion: "raw source to support/, to synthesis/, to canon-candidate, to canon on operator approval."
  - `_system/promotion-path-rules.md` — explicit promotion path rules file.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Eleven typed entity types with lifecycle states
- **Wiki says:** "Eleven entity types (Command, Agent, Skill, Rule, Workflow, Tool, Knowledge, Data, Memory, Output, Project) each with canonical locations, typed YAML frontmatter, and lifecycle states: scratch → research → candidate → canon."

- **Source evidence:**
  - `entities/` directory with 5 subdirectories: `agents/`, `commands/`, `rules/`, `skills/`, `README.md`.
  - `entities/agents/` contains 12 agent definitions (e.g., `studio-inbox-triage.md`).
  - `workflows/` directory — agentic reasoning pipelines.
  - `tools/` directory — pointer nodes over bounded capabilities.
  - `data/` directory — pointers, never live numbers.
  - `memory/` directory — reviewed learnings.
  - `outputs/` directory — produced artifacts with lineage.
  - `projects/` directory — project plans with inline tasks.
  - `entities/agents/studio-inbox-triage.md` lines 1-5 show typed YAML frontmatter: `type: "Agent"`, `lifecycle_state: "research"`, `namespace: "emberline-studio"`.
  - `AGENTS.md` (Codex orientation) documents all 11 entity types in a table: "Command, Agent, Skill, Rule, Workflow, Tool, Knowledge, Data, Memory, Output, Project" and the lifecycle: "scratch, research, candidate, canon". Confirms "Canon is never self-approved by an agent."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Contract layer with schema validation (`_system/validate.sh`)
- **Wiki says:** "`_system/` holds schemas, rules, registries, and `validate.sh`. Every node-bearing file carries typed YAML frontmatter with minimum required fields. Running `bash _system/validate.sh` verifies the entire graph is consistent and all wikilinks resolve."

- **Source evidence:**
  - `_system/` directory contains 49 entries including `validate.sh`, multiple schema/rule files, `namespaces/` directory, `checks/`, and `surface-registry/`.
  - `_system/validate.sh` (1436 lines) — comprehensive validation checking frontmatter keys, wikilink resolution, and consistency. Line 3: "Checks every node-bearing file in this repository for required frontmatter keys."
  - `_system/namespace-index-schema.md` — index schema definitions.
  - `_system/canon-layer-schema.md` — canon schema definitions.
  - `_system/session-ledger-rules.md` — session audit trail rules.
  - `_system/stable-id-and-alias-rules.md` — ID stability rules.
  - `_system/validate.sh` line 1325: "Checking for em dashes and en dashes..." — the em/en dash contract check.
  - README.md line 90-91: "Every node-bearing file carries typed YAML frontmatter; `bash _system/validate.sh` must exit 0."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Session audit trail for agent work
- **Wiki says:** "Every non-trivial agent session is registered under `sessions/active/`, with transcript logs under `sessions/logs/`, running notes, and closeout reviews under `sessions/reviews/`. Completed sessions are moved to `sessions/closed/`."

- **Source evidence:**
  - `sessions/` directory with 6 subdirectories: `active/`, `closed/`, `logs/`, `README.md`, `reviews/`, `templates/`.
  - `_system/session-ledger-rules.md` — explicit session ledger rules.
  - README.md line 93: "Sessions that touch the repo are registered, logged, and closed out in `sessions/`."
  - AGENTS.md (Codex orientation) documents: "Register under sessions/active/, declare a transcript path under sessions/logs/, keep running notes, write a closeout review under sessions/reviews/, then move the record to sessions/closed/."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Dual-adapter architecture with sync-adapters.sh
- **Wiki says:** "Executable entities (commands, agents, skills, rules) live canonically in `entities/` and are loaded through runtime adapter shims (`.claude/`, `.codex/`). Editing the canonical file then running `bash sync-adapters.sh` keeps shims in sync — agents never edit shims directly."

- **Source evidence:**
  - `.claude/` directory — runtime adapter shims for Claude Code.
  - `.codex/` directory — runtime adapter shims for Codex.
  - `sync-adapters.sh` — shell script that copies canonical entities to adapter directories. Line 3: "Regenerate .claude/ and .codex/ adapter shims from canonical entities/ files."
  - AGENTS.md (Codex orientation): "Executable entities live canonically in entities/ and are loaded through .claude/ and .codex/ shims: edit the canonical file, then run bash sync-adapters.sh. Never edit a shim."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Obsidian vault integration
- **Wiki says:** "Ships `.obsidian/` vault configuration, making the entire knowledge OS browsable as an Obsidian vault with wikilinks, graph view, and visual navigation."

- **Source evidence:**
  - `.obsidian/` directory exists with `app.json`, `graph.json`, `README.md`.
  - README.md lines 29-30: "Or open the folder as an Obsidian vault (config ships in .obsidian/) and read START-HERE.md yourself."
  - Wikilink syntax confirmed in entity files (e.g., `edges: [[rule-studio-brand-voice]]` in `studio-inbox-triage.md`).

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: Additional repo surface — parties/, swarms/, secrets/, synthesis/, repo-registry/, PROVENANCE.yml, OBSIDIAN-DASHBOARD.md
- **Wiki says:** The architecture tree includes parties (brands, clients), swarms (Sprints), secrets, synthesis, repo-registry, plus root files PROVENANCE.yml and OBSIDIAN-DASHBOARD.md.

- **Source evidence:**
  - `parties/` contains `brands/`, `clients/`, `README.md`, `_template.md`.
  - `swarms/` contains `Sprints/` and `README.md` (execution artifacts and receipts; referenced by `AGENTS.md` line 38: "trail, `swarms/Sprints/...` for execution artifacts and receipts").
  - `secrets/` — pointer/reference surface, never secret values (backed by `_system/secret-reference-schema.md` and `_system/secret-registry-rules.md`).
  - `synthesis/` — derived thinking surface with `README.md`.
  - `repo-registry/` — `README.md` + `_template.md`, backed by `_system/repo-registry-rules.md`.
  - `PROVENANCE.yml` (145 bytes) and `OBSIDIAN-DASHBOARD.md` present at repo root.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[infinite-brain-os]] -- Main wiki entry
- [[Mnemosyne]] -- Agent memory system
- [[hermes-agent]] -- Multi-platform agent gateway
- [[materia]] -- Agent framework

## Cross-project

- [[Mnemosyne.codegraph-verify]] -- Memory system verification
- [[hermes-agent.codegraph-verify]] -- Hermes Agent verification
- [[materia.codegraph-verify]] -- Materia verification
