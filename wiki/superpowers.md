---
name: superpowers
tags: [cli, coding-agent, development-methodology, javascript, markdown, plugin, skills, software-development, tdd, workspace, wiki, superpowers]
description: "Complete software development methodology for coding agents with composable skills — auto-triggering for brainstorming, TDD, subagent-driven dev, and code review"
source: sources/superpowers/
verification_date: 2026-07-30
verified_by: codegraph-verify
---

# Superpowers — Agent Dev Methodology

| Field | Value |
|---|---|
| **Origin** | [obra/superpowers](https://github.com/obra/superpowers) |
| **License** | MIT (© 2025 Jesse Vincent) |
| **Stack** | Markdown skills, JavaScript/TypeScript plugins |
| **Deployment** | Plugin marketplace install per harness |
| **Source** | `sources/superpowers/` |

## What is it?

A complete software development methodology packaged as composable skills for AI coding agents. Superpowers provides auto-triggering workflows for the entire development lifecycle — brainstorming, test-driven development (TDD), subagent-driven implementation, and code review — all as drop-in skill files.

The methodology chains skills together into a coherent development pipeline: brainstorm requirements → plan in small readable chunks → implement via subagents → review output. Each skill auto-triggers based on context, guiding the agent through professional software engineering practices without manual prompting. Superpowers is built by [Jesse Vincent](https://blog.fsck.com) and the rest of the team at [Prime Radiant](https://primeradiant.com) (README:277).

## Key Features

- **Auto-Triggering Workflows:** Skills activate automatically based on agent context — no manual invocation needed.
- **Complete Dev Lifecycle:** Covers brainstorming, planning, TDD, implementation, and code review in a coherent pipeline.
- **Subagent-Driven Development:** Leverages subagent delegation for parallel implementation tasks.
- **TDD-First Methodology:** Built on test-driven development principles — write tests before implementation code.
- **Composable Skills:** Skills chain together; output from one skill feeds into the next.
- **Plugin Architecture:** JavaScript/TypeScript plugins extend skill behavior for custom harness integration.
- **Multi-Harness Support:** Works with 11 harnesses: Claude Code, Antigravity, Codex App, Codex CLI, Cursor, Factory Droid, Gemini CLI, GitHub Copilot CLI, Kimi Code, OpenCode, and Pi.

## Basic Workflow

The documented workflow (README:196-212) has 7 phases:

| Phase | Skill | Description |
|---|---|---|
| 1 | `brainstorming` | Activates before writing code. Refines rough ideas through questions, explores alternatives, presents the design in sections for validation. Saves a design document. |
| 2 | `using-git-worktrees` | Activates after design approval. Creates an isolated workspace on a new branch, runs project setup, verifies a clean test baseline. |
| 3 | `writing-plans` | Activates with an approved design. Breaks work into bite-sized tasks (2-5 minutes each); every task has exact file paths, complete code, verification steps. |
| 4 | `subagent-driven-development` or `executing-plans` | Activates with a plan. Dispatches a fresh subagent per task with two-stage review (spec compliance, then code quality), or executes in batches with human checkpoints. |
| 5 | `test-driven-development` | Activates during implementation. Enforces RED-GREEN-REFACTOR: write failing test, watch it fail, write minimal code, watch it pass, commit. Deletes code written before tests. |
| 6 | `requesting-code-review` | Activates between tasks. Reviews against the plan, reports issues by severity; critical issues block progress. |
| 7 | `finishing-a-development-branch` | Activates when tasks complete. Verifies tests, presents options (merge/PR/keep/discard), cleans up the worktree. |

The agent checks for relevant skills before any task — mandatory workflows, not suggestions.

## Skill Library (14 skills)

- **Testing:** `test-driven-development` — RED-GREEN-REFACTOR cycle (includes testing anti-patterns reference)
- **Debugging:** `systematic-debugging` — 4-phase root cause process; `verification-before-completion` — ensure it's actually fixed
- **Collaboration:** `brainstorming`, `writing-plans`, `executing-plans`, `dispatching-parallel-agents`, `requesting-code-review`, `receiving-code-review`, `using-git-worktrees`, `finishing-a-development-branch`, `subagent-driven-development`
- **Meta:** `writing-skills`, `using-superpowers` (the bootstrap skill injected at session start)

## Tech Stack

| Component | Technology |
|---|---|
| **Skill Format** | Markdown (structured skill files) |
| **Plugins** | JavaScript / TypeScript |
| **Auto-Trigger** | Context-aware agent hooks |
| **Deployment** | Plugin marketplace per harness |

## Deployment

Installation differs by harness — install Superpowers separately for each one.

### Claude Code (official marketplace)

```bash
# From Anthropic's official plugin marketplace:
/plugin install superpowers@claude-plugins-official

# Or register the Superpowers marketplace first, then install:
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

### Other harnesses

- **Antigravity:** `agy plugin install https://github.com/obra/superpowers`
- **Codex App / Codex CLI:** available via the official Codex plugin marketplace (`/plugins`, search `superpowers`)
- **Cursor:** `/add-plugin superpowers` in Cursor Agent chat
- **Factory Droid:** `droid plugin marketplace add https://github.com/obra/superpowers` then `droid plugin install superpowers@superpowers`
- **Gemini CLI:** `gemini extensions install https://github.com/obra/superpowers`
- **GitHub Copilot CLI:** `copilot plugin marketplace add obra/superpowers-marketplace` then `copilot plugin install superpowers@superpowers-marketplace`
- **Kimi Code:** plugin manager → Marketplace > Superpowers, or `/plugins install https://github.com/obra/superpowers`
- **OpenCode:** tell OpenCode to "Fetch and follow instructions from https://raw.githubusercontent.com/obra/superpowers/refs/heads/main/.opencode/INSTALL.md"
- **Pi:** `pi install git:github.com/obra/superpowers` (loads skills + a small extension injecting the `using-superpowers` bootstrap at session startup)

### Manual skill-file copying is not supported

Manually copying skill files into a harness (`cp -r skills/* ~/.your-agent/skills/`) is explicitly **not a real integration**: AGENTS.md (lines 84-90) lists "Manually copying skill files into the harness" under "These are not real integrations and will be closed", along with `npx skills` wrappers and anything where `brainstorming` does not auto-trigger on the acceptance test. A real integration loads the `using-superpowers` bootstrap at session start — that is what causes skills to auto-trigger; without it the skills are dead weight on disk.

## Related

- [[opencode]] — AI coding agent that can consume superpowers skills
- [[agent-rules-books]] — Rule-based agent guidance, complementary approach
- [[skills]] — General skills repository with similar skill formats
- [[hermes-agent]] — MCP hub with its own skills system
- [[test-driven-development]] — TDD methodology skill (part of this knowledge base's own skills)
