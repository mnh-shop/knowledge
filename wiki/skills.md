---
name: skills
description: "Installable agent skill registry and SDK for extending Claude Code with domain-specific capabilities"
tags: [claude-code, plugin, skills, skills-platform, wiki]
source: sources/skills/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Skills For Real Engineers

Skills is Matt Pocock's collection of installable agent skills for Claude Code (and other coding agents like Codex CLI). It addresses common failure modes in agent-assisted development — misalignment, verbosity, lack of feedback loops, and software entropy — through composable, model-agnostic slash commands and behaviors.

## Description

The repo is organized as a skill registry with a plugin manifest (`plugin.json`) that agents load at startup. Skills are structured as individual `SKILL.md` files grouped into category buckets. The registry is installable in seconds via `npx skills@latest add mattpocock/skills` (editable copies) or as a managed Claude Code plugin from the official marketplace (`claude plugins install mattpocock-skills` / `/plugin install mattpocock-skills`). A setup wizard (`/setup-matt-pocock-skills`) configures per-repo issue tracking and documentation layout.

## Key Features

- **`/grill-me` and `/grill-with-docs`**: Relentless pre-build interviewing to align on requirements before coding. `grill-with-docs` additionally builds a shared domain model in `CONTEXT.md` and records architectural decisions as ADRs — reducing verbosity and improving naming consistency.
- **`/tdd`**: Red-green-refactor test-driven development loop for features and bug fixes, with guidance on test quality and deep-module design.
- **`/diagnosing-bugs`**: Disciplined bug diagnosis loop: reproduce, minimize, hypothesize, instrument, fix, regression-test.
- **`/improve-codebase-architecture`**: Scans a codebase for design deepening opportunities, presents an HTML report, then grills through selected improvements using the shared `codebase-design` vocabulary.
- **`/domain-modeling`** and **`/codebase-design`**: Shared model-invoked skills providing a ubiquitous language and deep-module vocabulary reused across all engineering skills.
- **`/to-spec`**: Synthesizes the current conversation into a spec and publishes it to the issue tracker — no interview, just synthesis of what was already discussed.
- **`/to-tickets`**: Breaks any plan, spec, or conversation into tracer-bullet tickets, each declaring its blocking edges — written as text in a local file or as native blocking links on a real tracker.
- **`/wayfinder`**: Plans a chunk of work too big for one agent session as a shared map of decision tickets on the issue tracker, resolved one at a time until the way to the destination is clear.
- **`/implement`**: Builds the work described by a spec or ticket set, driving `/tdd` at pre-agreed seams and closing out with `/code-review` before committing.
- **`/research`**: Investigates a question against high-trust primary sources and captures findings as a cited Markdown file, run as a background agent.
- **`/code-review`**: Two-axis review of a diff since a fixed point — Standards (repo standards + Fowler smell baseline) and Spec (faithful to the originating issue/PRD) — run as parallel sub-agents.
- **`/triage`**: State-machine-based issue triage with configurable label roles (GitHub, Linear, or local markdown).
- **`/setup-matt-pocock-skills`**: One-time per-repo configuration for issue tracker, triage labels, and domain doc layout.
- **`/handoff`**: Compact a conversation into a handoff document for another agent to continue.
- **`/prototype`**: Build throwaway prototypes (terminal or multi-variant web) to flesh out designs.
- **`/teach`**: Multi-session teaching of new skills or concepts using reusable lesson components.

## Architecture

Skills are split on an invocation axis:

- **User-invoked skills** (e.g., `/grill-me`, `/to-spec`) — reachable only when typed by the user. Their job is to orchestrate. A user-invoked skill may invoke model-invoked skills but never another user-invoked one.
- **Model-invoked skills** (e.g., `/tdd`, `/domain-modeling`, `/codebase-design`) — can be invoked by the user _or_ reached automatically by the agent when the task fits. They hold the reusable discipline.

The distinction lives in each `SKILL.md` frontmatter (`disable-model-invocation: true` plus `policy.allow_implicit_invocation: false` in `agents/openai.yaml` for user-invoked skills) and is documented in `.agents/invocation.md`.

Bucket categories under `skills/`:

| Bucket | Contents |
|--------|----------|
| `engineering/` | Daily code work — 17 skills: `ask-matt`, `code-review`, `codebase-design`, `diagnosing-bugs`, `domain-modeling`, `grill-with-docs`, `implement`, `improve-codebase-architecture`, `prototype`, `research`, `resolving-merge-conflicts`, `setup-matt-pocock-skills`, `tdd`, `to-spec`, `to-tickets`, `triage`, `wayfinder` |
| `productivity/` | Daily non-code workflow — `grill-me`, `grilling`, `handoff`, `teach`, `writing-great-skills` |
| `misc/` | Kept around but rarely used, not promoted — `git-guardrails-claude-code`, `migrate-to-shoehorn`, `scaffold-exercises`, `setup-pre-commit` |
| `personal/` | Tied to the author's own setup, not promoted |
| `in-progress/` | Draft skills not yet ready to ship |
| `deprecated/` | Removed skills kept for reference |

Every skill in `engineering/` or `productivity/` (the **promoted** buckets) must have a reference in the top-level `README.md` and an entry in `.claude-plugin/plugin.json`'s `skills` array — the Claude Code plugin ships exactly the promoted set (22 skills: 17 engineering + 5 productivity). Skills in `misc/`, `personal/`, `in-progress/`, and `deprecated/` must **not** appear in either. The repo is also its own single-plugin Claude Code marketplace: `.claude-plugin/marketplace.json` lists the one `mattpocock-skills` plugin, and the plugin `version` must stay in sync with `package.json`'s.

The domain model (defined in `CONTEXT.md`) uses:

- **Issue tracker** — the tool that hosts a repo's issues (GitHub Issues, Linear, or a local `.scratch/` markdown convention). Skills like `to-tickets`, `to-spec`, and `triage` read from and write to it.
- **Issue** — a single tracked unit of work inside an Issue tracker: a bug, task, spec, or slice produced by `to-tickets`.
- **Decision ticket** — a `wayfinder` unit: a child Issue of a `wayfinder:map` holding a *question* whose resolution is a decision, not a slice of a build to execute.
- **Triage role** — a canonical state-machine label applied to an Issue during triage (e.g. `needs-triage`, `ready-for-afk`), mapped to a real label string in the Issue tracker.

**Relationships:** An Issue tracker holds many Issues; an Issue carries one Triage role at a time; a Decision ticket is an Issue (a child of a `wayfinder:map`).

**Flagged ambiguities:** "backlog" previously meant both the tool hosting issues and the body of work inside it — resolved: the tool is the Issue tracker and "backlog" is no longer a domain term; "backlog backend" / "backlog manager" collapsed into Issue tracker.

## Quick Start

```bash
# Route A — managed Claude Code plugin (official marketplace, auto-updating):
claude plugins install mattpocock-skills
# or, inside a session:
/plugin install mattpocock-skills

# Route B — editable skill copies via skills.sh (any agent, 30-second setup):
npx skills@latest add mattpocock/skills

# Then run the setup wizard (pick your issue tracker and triage labels):
/setup-matt-pocock-skills

# Start using skills:
/grill-with-docs
/tdd
/improve-codebase-architecture
```

## Related

- [[abvx-agent-skills]] — Agent skills ecosystem
- [[superpowers]] — Agent development methodology skills
- [[agentfield]] — Agent orchestration field
- **codebase-design** — Shared vocabulary for deep module design (skill in this repo)

## Links

- [GitHub: mattpocock/skills](https://github.com/mattpocock/skills)
- [skills.sh badge/status](https://skills.sh/mattpocock/skills)
- [Claude Code plugin (official marketplace)](https://code.claude.com/docs/en/plugins)
- [Newsletter](https://www.aihero.dev/s/skills-newsletter)
- [Invocation model docs](https://github.com/mattpocock/skills/blob/main/.agents/invocation.md)
