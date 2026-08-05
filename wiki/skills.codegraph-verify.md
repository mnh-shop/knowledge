---
name: skills-codegraph-verify
tags: [skills, codegraph-verify, catalog]
description: "Codegraph Verification: skills"
source: sources/skills/
---

# Codegraph Verification: skills

**Date:** 2026-07-30

## Claim 1: 17 engineering skills and 5 productivity skills in a six-bucket skill registry
- **Wiki says:** The repo is organized as a skill registry with plugin manifest, with skills in bucket categories: engineering (daily code work), productivity (daily non-code workflow), misc, personal, in-progress, and deprecated. The engineering bucket holds 17 skills.

- **Source evidence:** The `skills/` directory contains 6 bucket folders. `skills/engineering/` contains exactly 17 skill directories: `ask-matt`, `code-review`, `codebase-design`, `diagnosing-bugs`, `domain-modeling`, `grill-with-docs`, `implement`, `improve-codebase-architecture`, `prototype`, `research`, `resolving-merge-conflicts`, `setup-matt-pocock-skills`, `tdd`, `to-spec`, `to-tickets`, `triage`, `wayfinder`. `skills/productivity/` contains 5: `grill-me`, `grilling`, `handoff`, `teach`, `writing-great-skills`. `.claude-plugin/plugin.json` (lines 21-44) lists exactly the 22 promoted skills (17 engineering + 5 productivity). CLAUDE.md lines 1-8 document the bucket organization.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None (previously stale: engineering was reported as 16 with `to-prd`/`to-issues` and missing `code-review`, `implement`, `research`, `to-spec`, `to-tickets`, `wayfinder`)

## Claim 2: /to-spec and /to-tickets replaced /to-prd and /to-issues
- **Wiki says:** /to-spec synthesizes the conversation into a spec (no interview) and publishes to the issue tracker; /to-tickets breaks plans/specs/conversations into tracer-bullet tickets declaring blocking edges.

- **Source evidence:** Commit `386d4ff` (2026-07-02) "refactor: unify planning skills into /to-spec + /to-tickets" deleted `to-prd`/`to-issues` — neither exists in `skills/engineering/`. `skills/engineering/to-spec/SKILL.md` line 5: "This skill takes the current conversation context and codebase understanding and produces a spec (you may know this document as a PRD). Do NOT interview the user — just synthesize what you already know." `skills/engineering/to-tickets/SKILL.md` line 3: "Break a plan, spec, or conversation into a set of **tickets** — tracer-bullet vertical slices, each declaring the tickets that **block** it." Both are user-invoked (`disable-model-invocation: true`) and registered in `.claude-plugin/plugin.json` lines 29-30. README.md lines 199-200 describe them identically.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None (previously stale: wiki and verify page listed `/to-prd` and `/to-issues`)

## Claim 3: Invocation model split into user-invoked and model-invoked skills, documented in .agents/invocation.md
- **Wiki says:** Skills are split on an invocation axis: user-invoked skills (orchestrators reachable only when typed by the user, e.g., /grill-me, /to-spec) and model-invoked skills (reachable by user or agent automatically when the task fits, e.g., /tdd, /domain-modeling, /codebase-design).

- **Source evidence:** CLAUDE.md line 20: "Every `SKILL.md` is either user-invoked (`disable-model-invocation: true` plus `policy.allow_implicit_invocation: false` in `agents/openai.yaml`...) or model-invoked (model- or user-reachable). See [.agents/invocation.md]." `.agents/invocation.md` lines 1-10 document the split: user-invoked skills are "reachable **only by the human typing its name**"; model-invoked are "reachable by **model or user**"; line 8: "A user-invoked skill may invoke model-invoked skills, but it can never reach another user-invoked skill." The `.claude-plugin/plugin.json` manifest lists all promoted skills; the distinction lives in each `SKILL.md` frontmatter + `agents/openai.yaml`. Commit `6e178c6` moved `docs/invocation.md` to `.agents/invocation.md`; `docs/` now mirrors only `engineering/` + `productivity/` (README.md lines 199-202 list the user-invoked engineering skills as examples).

- **Verdict:** ✅ CORRECT
- **Fix needed:** None (previously stale: linked `docs/invocation.md`, which no longer exists)

## Claim 4: Only promoted buckets (engineering/ + productivity/) get README refs and plugin.json entries
- **Wiki says:** Every skill in `engineering/` or `productivity/` (the promoted buckets) must have a reference in the top-level README.md and an entry in `.claude-plugin/plugin.json`'s skills array; skills in `misc/`, `personal/`, `in-progress/`, and `deprecated/` must not appear in either.

- **Source evidence:** CLAUDE.md line 10: "Every skill in `engineering/` or `productivity/` (the **promoted** buckets) must have a reference in the top-level `README.md` and an entry in `.claude-plugin/plugin.json`'s `skills` array... Skills in `misc/`, `personal/`, `in-progress/`, and `deprecated/` must not appear in either." CLAUDE.md line 18 extends the rule to docs pages: non-promoted buckets get **no** docs page. `.claude-plugin/plugin.json` lines 21-44 contain exactly the 22 promoted skills; `misc/` (e.g. `git-guardrails-claude-code`, `migrate-to-shoehorn`), `personal/`, `in-progress/` (e.g. `batch-grill-me`, `to-questionnaire`), and `deprecated/` (e.g. `qa`, `design-an-interface`) are absent.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None (previously INVERTED: wiki claimed misc/ skills also require README ref + plugin.json entry)

## Claim 5: Domain model in CONTEXT.md includes Decision ticket, Relationships, and Flagged ambiguities
- **Wiki says:** The domain model uses Issue tracker, Issue, Decision ticket, and Triage role, plus documented Relationships and Flagged ambiguities.

- **Source evidence:** CONTEXT.md defines **Issue tracker** (line 7-8), **Issue** (line 11-13), **Decision ticket** (line 15-16: "A `wayfinder` unit — a child **Issue** of a `wayfinder:map` holding a *question* whose resolution is a decision, not a slice of a build to execute"), and **Triage role** (line 18-19). The **Relationships** section (lines 21-25) states: an Issue tracker holds many Issues; an Issue carries one Triage role at a time; a Decision ticket is an Issue (a child of a `wayfinder:map`). The **Flagged ambiguities** section (lines 27-30) resolves "backlog" and "backlog backend"/"backlog manager" into the Issue tracker term. `skills/engineering/wayfinder/SKILL.md` line 3 confirms the decision-ticket vocabulary: "questions whose resolution is a decision, not slices of a build to execute."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None (Decision ticket + Relationships + Flagged ambiguities newly added to wiki)

## Claim 6: ask-matt is the router and ships first in the plugin manifest
- **Wiki says:** ask-matt is the router that maps every user-reachable skill and how they relate, updated whenever skills are added, renamed, or removed.

- **Source evidence:** CLAUDE.md line 22: "[`ask-matt`](./skills/engineering/ask-matt/SKILL.md) is the router that maps every user-reachable skill and how they relate... a new skill it never mentions, or a stale one it still routes to, is a router that lies." `.claude-plugin/plugin.json` line 22 registers `./skills/engineering/ask-matt` as the **first** entry in the `skills` array. `skills/engineering/README.md` lists `ask-matt` first. README.md line 194: "**ask-matt** — Ask which skill or flow fits your situation. A router over the user-invoked skills in this repo."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Two install routes — managed Claude Code plugin and npx skills.sh
- **Wiki says:** The registry installs via `npx skills@latest add mattpocock/skills` (editable copies) or as a managed Claude Code plugin from the official marketplace (`claude plugins install mattpocock-skills` / `/plugin install mattpocock-skills`).

- **Source evidence:** README.md line 27: "**The [Claude Code plugin](https://code.claude.com/docs/en/plugins)** installs the whole set as a managed, read-only bundle... **[skills.sh](https://skills.sh/mattpocock/skills)** copies editable skill files into your project." README.md lines 34-44 document `claude plugins install mattpocock-skills` and `/plugin install mattpocock-skills` from the official marketplace ("there's nothing to add first, and updates arrive automatically"). README.md lines 51-57 document `npx skills@latest add mattpocock/skills` for Codex and other agents. `.claude-plugin/marketplace.json` (lines 1-23) makes the repo its own single-plugin marketplace listing the one `mattpocock-skills` plugin; CLAUDE.md line 12 documents the version-sync rule between `plugin.json` and `package.json`. The `/setup-matt-pocock-skills` wizard (README.md lines 74-82) configures issue tracker, triage labels, and docs location.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None (Claude Code official-marketplace route + marketplace.json newly added to wiki)

## Related

- [[skills]] -- Main wiki entry
- [[abvx-agent-skills]] -- Agent skills ecosystem
- [[slavinga-skills]] -- Community skill collection
- [[openai-skills]] -- OpenAI skill collections

## Cross-project

- [[pydantic-ai-skills.codegraph-verify]] -- Pydantic AI skills verification
- [[reverse-skill.codegraph-verify]] -- Reverse engineering skill verification
- [[hermes-agent.codegraph-verify]] -- Hermes agent verification
