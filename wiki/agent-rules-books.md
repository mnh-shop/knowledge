---
name: agent-rules-books
tags: [agent-rules-books, ai-llm, agent, coding-agent, claude-code, documentation, skill]
description: "Universal MIT-licensed project rules for AI coding agents, distilled from classic software engineering books (Clean Code, DDD, Refactoring, etc.) in mini/nano/full variants"
source: sources/agent-rules-books/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Agent Rules Books

A MIT-licensed collection of ready-to-use rule sets for AI coding agents, distilled from well-known software engineering books covering design, architecture, refactoring, legacy code, reliability, and data-intensive systems. Created by Maciej Ciemborowicz.

## Overview

This repository contains compressed, decision-equivalent rule files that can be attached to AI agents (Claude Code, OpenAI Codex CLI, Cursor) to constrain their behavior and improve code quality. Each rule set is inspired by (not a substitute for) the original books and ships in three versions optimized for different context budgets. The project includes a formal compression process (`PROCESS.md`), conflict-aware loading guidance (`COMPATIBILITY.md`), constructive criticism documentation (`CRITICISM.md`), editor-specific delivery instructions (`USAGE.md`), and a full release matrix with metrics.

## Key Features

- **Three-tier compression**: `mini` (recommended default, optimal decision pressure), `nano` (compact fallback for tight context budgets), `full` (canonical complete reference with traceability)
- **13 book sources**: Clean Code (297 lines full, 47 mini), Clean Architecture (515 full, 49 mini), Domain-Driven Design (979 full, 48 mini), Refactoring (433 full, 49 mini), Designing Data-Intensive Applications (393 full, 55 mini), Working Effectively with Legacy Code (371 full, 50 mini), The Pragmatic Programmer (359 full, 65 mini), Code Complete (354 full, 56 mini), A Philosophy of Software Design (370 full, 46 mini), Patterns of Enterprise Application Architecture (404 full, 54 mini), Refactoring.Guru (765 full, 64 mini), Release It! (382 full, 48 mini), DDD Distilled (317 full, 56 mini), and Implementing DDD (337 full, 57 mini)
- **Editor-specific delivery patterns**: Claude Code (`CLAUDE.md` with `@import`, `.claude/rules/`, `.claude/skills/`), Codex (`AGENTS.md`, `.codex/config.toml`, skills), Cursor (`.cursor/rules/*.mdc` with Always/Auto Attached/Agent Requested/Manual types)
- **Conflict-aware loading**: COMPATIBILITY.md documents which rule sets are compatible or conflicting when loaded together; recommends one primary always-on set with on-demand loading for others
- **Task-scoped loading guidance**: Rules organized by use case — everyday code quality (Clean Code, Code Complete), architecture (Clean Architecture, DDD), refactoring (Refactoring, A Philosophy of Software Design), legacy code (Working Effectively with Legacy Code), production systems (Release It!), data systems (DDIA), general engineering (The Pragmatic Programmer)
- **Deterministic release process**: Each book has a `_rule-workbench/` directory containing `full.md` (canonical source), `mini.md` (compressed), `nano.md` (ultra-compact), and `traceability.md` (what was kept, merged, or omitted with source references)
- **Rule metrics release matrix**: Lines, rules count, and byte size tracked per rule set per version, enabling context-budget-aware selection

## Usage

### Start here

```text
project/
  AGENTS.md              # cross-tool base layer (one mini rule set)
  CLAUDE.md              # @import AGENTS.md for Claude Code
  .cursor/rules/         # per-topic scoped rules for Cursor
  .agents/skills/        # multi-step procedures as skills for Codex
```

Add `@sources/agent-rules-books/clean-code/clean-code.mini.md` to your `CLAUDE.md` for repo-wide engineering bias, or import specific rule sets on demand for targeted tasks like refactoring or architecture reviews.

### Delivery pattern selection

| Pattern | Best for | Version |
|---|---|---|
| Always-on project rule | Stable defaults affecting most tasks | `mini` |
| Scoped rule | One directory, file type, or subsystem | `mini` or `nano` |
| On-demand rule | Refactoring passes, reviews, migrations | `mini` |
| Skill or command | Multi-step procedures, checklists | Derived from `mini` |
| Retrieval or MCP | Large reference material, changing docs | `full` |

### Available rule sets

- **Clean Code** — Readability, naming, small functions, testing discipline (220 rules full)
- **Domain-Driven Design** — Domain modeling, bounded contexts, tactical patterns (523 rules full)
- **Refactoring** — Safe code improvement, smell detection, behavior preservation (242 rules full)
- **Clean Architecture** — Stable boundaries, dependency rule, framework isolation (289 rules full)
- **Designing Data-Intensive Applications** — Reliability, scalability, consistency (205 rules full)
- **Working Effectively with Legacy Code** — Characterization tests, seams, risk reduction (193 rules full)
- **The Pragmatic Programmer** — Orthogonality, automation, fast feedback (179 rules full)
- **Code Complete** — Routine design, defensive programming, coding standards (180 rules full)
- **A Philosophy of Software Design** — Deep modules, simplicity, complexity fight (177 rules full)
- **Patterns of Enterprise Application Architecture** — Enterprise patterns, layers (196 rules full)
- **Refactoring.Guru** — Refactoring catalog, code smells (478 rules full)
- **Release It!** — Production survival, circuit breakers, observability (204 rules full)
- **DDD Distilled / Implementing DDD** — DDD entry and practice (158/177 rules full)

## Related

- [[skills]] — Agent skill frameworks that can integrate rule sets as always-on or on-demand instructions
- [[abvx-agent-skills]] — Auditable skillpack for coding agents with complementary rule patterns
- [[reverse-skill]] — Skill that can reverse-engineer codebases using these rule sets for compliance analysis
- [[hermes-agent]] — Agent platform that can consume rule files via CLAUDE.md imports and skill-based workflows
- [[free-claude-code]] — CLI agent that can apply these rule sets through the FCC proxy and CLAUDE.md integration
