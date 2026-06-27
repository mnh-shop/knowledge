---
name: skills
description: "Installable agent skill registry and SDK for extending Claude Code with domain-specific capabilities"
tags: [claude-code, plugin, skills, skills-platform, wiki]
source: sources/skills/
---

# Skills For Real Engineers

Skills is Matt Pocock's collection of installable agent skills for Claude Code (and other coding agents like Codex CLI). It addresses common failure modes in agent-assisted development — misalignment, verbosity, lack of feedback loops, and software entropy — through composable, model-agnostic slash commands and behaviors.

## Description

The repo is organized as a skill registry with a plugin manifest (`plugin.json`) that agents load at startup. Skills are structured as individual `SKILL.md` files grouped into category buckets. The registry is installable in seconds via `npx skills@latest add mattpocock/skills`, and a setup wizard (`/setup-matt-pocock-skills`) configures per-repo issue tracking and documentation layout.

## Key Features

- **`/grill-me` and `/grill-with-docs`**: Relentless pre-build interviewing to align on requirements before coding. `grill-with-docs` additionally builds a shared domain model in `CONTEXT.md` and records architectural decisions as ADRs — reducing verbosity and improving naming consistency.
- **`/tdd`**: Red-green-refactor test-driven development loop for features and bug fixes, with guidance on test quality and deep-module design.
- **`/diagnosing-bugs`**: Disciplined bug diagnosis loop: reproduce, minimize, hypothesize, instrument, fix, regression-test.
- **`/improve-codebase-architecture`**: Scans a codebase for design deepening opportunities, presents an HTML report, then grills through selected improvements using the shared `codebase-design` vocabulary.
- **`/domain-modeling`** and **`/codebase-design`**: Shared model-invoked skills providing a ubiquitous language and deep-module vocabulary reused across all engineering skills.
- **`/to-prd`** and **`/to-issues`**: Synthesize conversation into PRDs and break them into independently-grabbable vertical-slice issues.
- **`/triage`**: State-machine-based issue triage with configurable label roles (GitHub, Linear, or local markdown).
- **`/setup-matt-pocock-skills`**: One-time per-repo configuration for issue tracker, triage labels, and domain doc layout.
- **`/handoff`**: Compact a conversation into a handoff document for another agent to continue.
- **`/prototype`**: Build throwaway prototypes (terminal or multi-variant web) to flesh out designs.
- **`/teach`**: Multi-session teaching of new skills or concepts using reusable lesson components.

## Architecture

Skills are split on an invocation axis:

- **User-invoked skills** (e.g., `/grill-me`, `/to-prd`) — reachable only when typed by the user. Their job is to orchestrate. A user-invoked skill may invoke model-invoked skills but never another user-invoked one.
- **Model-invoked skills** (e.g., `/tdd`, `/domain-modeling`, `/codebase-design`) — can be invoked by the user _or_ reached automatically by the agent when the task fits. They hold the reusable discipline.

Bucket categories under `skills/`:

| Bucket | Contents |
|--------|----------|
| `engineering/` | Daily code work — `grill-with-docs`, `tdd`, `diagnosing-bugs`, `codebase-design`, `domain-modeling`, `improve-codebase-architecture`, `triage`, `to-prd`, `to-issues`, `prototype`, `setup-matt-pocock-skills`, `resolve-merge-conflicts`, `ask-matt` |
| `productivity/` | Non-code workflow — `grill-me`, `handoff`, `teach`, `writing-great-skills`, `grilling` |
| `misc/` | Rarely used — `git-guardrails`, `migrate-to-shoehorn`, `scaffold-exercises`, `setup-pre-commit` |
| `personal/` | Author-specific setups, not promoted |
| `in-progress/` | Draft skills not yet ready to ship |
| `deprecated/` | Removed skills kept for reference |

Every skill in `engineering/`, `productivity/`, or `misc/` must have a reference in `README.md` and an entry in `.claude-plugin/plugin.json`.

The domain model (defined in `CONTEXT.md`) uses: **Issue tracker** (the tool hosting issues), **Issue** (a single tracked work unit), and **Triage role** (state-machine label applied during triage).

## Quick Start

```bash
# Install the skill registry (30-second setup)
npx skills@latest add mattpocock/skills

# Select skills and install. Then run the setup wizard:
/setup-matt-pocock-skills

# Choose your issue tracker and labels, then start using skills:
/grill-with-docs
/tdd
/improve-codebase-architecture
```

## Related

- [[abvx-agent-skills]] — Agent skills ecosystem
- [[agentfield]] — Agent orchestration field
- **codebase-design** — Shared vocabulary for deep module design (skill in this repo)

## Links

- [GitHub: mattpocock/skills](https://github.com/mattpocock/skills)
- [skills.sh badge/status](https://skills.sh/mattpocock/skills)
- [Newsletter](https://www.aihero.dev/s/skills-newsletter)
- [Invocation model docs](https://github.com/mattpocock/skills/blob/main/docs/invocation.md)
