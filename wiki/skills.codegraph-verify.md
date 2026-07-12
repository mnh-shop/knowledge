---
name: skills-codegraph-verify
tags: [skills, codegraph-verify, catalog]
description: "Codegraph Verification: skills"
source: sources/skills/
---

# Codegraph Verification: skills

**Date:** 2026-07-12

## Claim 1: 16 engineering skills and 5 productivity skills in a composable, pluggable skill registry
- **Wiki says:** The repo is organized as a skill registry with plugin manifest, with skills in bucket categories: engineering (daily code work), productivity (non-code workflow), misc, personal, in-progress, and deprecated.

- **Source evidence:** The `skills/` directory contains 6 bucket folders: `engineering/` (16 skills), `productivity/` (5 skills), `misc/` (4 skills), `personal/`, `in-progress/`, `deprecated/`. The `engineering/` bucket includes: `ask-matt`, `code-review`, `codebase-design`, `diagnosing-bugs`, `domain-modeling`, `grill-with-docs`, `implement`, `improve-codebase-architecture`, `prototype`, `research`, `resolving-merge-conflicts`, `setup-matt-pocock-skills`, `tdd`, `to-issues`, `to-prd`, `triage`. The `productivity/` bucket includes: `grill-me`, `grilling`, `handoff`, `teach`, `writing-great-skills`. `.claude-plugin/plugin.json` lists 22 promoted skills across `engineering/` and `productivity/`. CLAUDE.md (the project CLAUDE.md file) lines 1-7 document the bucket organization. README.md confirms 30-second install via `npx skills@latest add mattpocock/skills`.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Invocation model split into user-invoked and model-invoked skills
- **Wiki says:** Skills are split on an invocation axis: user-invoked skills (orchestrators reachable only when typed by the user, e.g., /grill-me, /to-prd) and model-invoked skills (reachable by user or agent automatically when the task fits, e.g., /tdd, /domain-modeling, /codebase-design).

- **Source evidence:** CLAUDE.md lines 7-14 document the invocation model: "User-invoked skills (e.g., /grill-me, /to-prd) — reachable only when typed by the user. Their job is to orchestrate. A user-invoked skill may invoke model-invoked skills but never another user-invoked one. Model-invoked skills (e.g., /tdd, /domain-modeling, /codebase-design) — can be invoked by the user or reached automatically by the agent when the task fits. They hold the reusable discipline." The `.claude-plugin/plugin.json` manifest lists all promoted skills without distinguishing invocation — that distinction lives in each SKILL.md via `disable-model-invocation: true` frontmatter. `docs/invocation.md` provides extended documentation. `docs/engineering/` directory mirrors the skill structure.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Deep-module vocabulary shared across all engineering skills via domain-modeling and codebase-design
- **Wiki says:** Domain-modeling and codebase-design skills provide shared vocabulary (ubiquitous language and deep-module vocabulary) reused across all engineering skills.

- **Source evidence:** `skills/engineering/domain-modeling/SKILL.md` and `skills/engineering/codebase-design/SKILL.md` define the shared vocabulary. README.md documents codebase-design as providing "Shared vocabulary for designing deep modules" and domain-modeling as "Build and sharpen a project's domain model." CLAUDE.md states model-invoked skills "hold the reusable discipline." Every engineering skill can reference these shared patterns. The `CONTEXT.md` file defines the domain model vocabulary used across skills: "Issue tracker" (the tool), "Issue" (a single tracked work unit), and "Triage role" (state-machine label). The `handoff` skill compacts conversations using this shared vocabulary.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Plugin manifest auto-discovered by agent harnesses with documentation site and human-facing docs
- **Wiki says:** The registry is installable via `npx skills@latest add mattpocock/skills` and a setup wizard configures per-repo issue tracking and documentation layout.

- **Source evidence:** `.claude-plugin/plugin.json` registers 22 skills for auto-discovery. `docs/` directory contains `engineering/` and `productivity/` subdirectories with human-facing docs pages for each promoted skill (matching the standard URL pattern `https://aihero.dev/skills-<skill-name>`). CLAUDE.md lines 19-21: "Skills in engineering/ and productivity/ also have a human-facing docs page at docs/<bucket>/<skill-name>.md. The published URL is https://aihero.dev/skills-<skill-name> regardless of bucket." README.md documents the 30-second install flow. The `setup-matt-pocock-skills` skill (`skills/engineering/setup-matt-pocock-skills/SKILL.md`) configures per-repo issue tracker selection, triage labels, and doc layout on first run. `scripts/link-skills.sh` provides local symlinking for development. `.agents/writing-docs.md` documents the docs page creation process.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Bug diagnosis loop and TDD skills with discipline-gated workflows
- **Wiki says:** The diagnosing-bugs skill implements a disciplined bug diagnosis loop (reproduce, minimize, hypothesize, instrument, fix, regression-test) and the tdd skill provides red-green-refactor test-driven development with guidance on deep-module design.

- **Source evidence:** `skills/engineering/diagnosing-bugs/SKILL.md` exists implementing the diagnosis loop described in README.md line 14: "Diagnosis loop for hard bugs and performance regressions." README.md documents it as: "Disciplined bug diagnosis loop: reproduce, minimize, hypothesize, instrument, fix, regression-test." `skills/engineering/tdd/SKILL.md` implements test-driven development. README.md lines 14-15 document tdd: "Red-green-refactor test-driven development loop for features and bug fixes, with guidance on test quality and deep-module design." The `improve-codebase-architecture` skill (`skills/engineering/improve-codebase-architecture/SKILL.md`) scans for deepening opportunities and uses the codebase-design vocabulary — linking these as a coherent discipline stack.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Ask-matt router serving as the skill discovery entry point across all flows
- **Wiki says:** Ask-matt is the router that maps every user-reachable skill and how they relate, updated whenever skills are added, renamed, or removed.

- **Source evidence:** `skills/engineering/ask-matt/SKILL.md` is the router skill. CLAUDE.md lines 26-28 state: "ask-matt is the router that maps every user-reachable skill and how they relate. The same trigger that re-syncs a docs page applies to it: whenever you add, rename, remove, or change how a user-reachable skill fits the flows, re-read ask-matt's SKILL.md and update it so the map stays accurate." The plugin.json registers `ask-matt` as the first skill. The `skills/engineering/README.md` lists `ask-matt` as the first entry. README.md promotes `/grill-me` and `/improve-codebase-architecture` as example entry points that are routed through ask-matt.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[skills]] -- Main wiki entry
- [[abvx-agent-skills]] -- Agent skills ecosystem
- [[slavinga-skills]] -- Community skill collection
- [[openai-skills]] -- OpenAI skill collections

## Cross-project

- [[pydantic-ai-skills.codegraph-verify]] -- Pydantic AI skills verification
- [[reverse-skill.codegraph-verify]] -- Reverse engineering skill verification
- [[hermes-agent.codegraph-verify]] -- Hermes agent verification
