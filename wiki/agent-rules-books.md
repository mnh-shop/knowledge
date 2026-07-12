---
name: agent-rules-books
tags: [agent-rules-books, ai-llm, agent, coding-agent, claude-code, documentation, skill]
description: "Universal MIT-licensed project rules for AI coding agents, distilled from classic software engineering books (Clean Code, DDD, Refactoring, etc.) in mini/nano/full variants"
source: sources/agent-rules-books/
---

# Agent Rules Books

A MIT-licensed collection of ready-to-use rule sets for AI coding agents, distilled from well-known software engineering books covering design, architecture, refactoring, legacy code, reliability, and data-intensive systems.

## What it does

Provides compressed, decision-equivalent rule files that can be attached to AI agents (Claude Code, Codex, Cursor) to constrain their behavior and improve code quality. Each rule set ships in three versions optimized for different context budgets.

## Key features

- Three-tier compression: `mini` (recommended), `nano` (tight budgets), `full` (reference)
- 13 book sources: Clean Code, Clean Architecture, DDD, Refactoring, DDIA, and more
- Editor-specific delivery patterns for Claude Code, Codex, and Cursor
- Conflict-aware loading: recommends one primary always-on set, on-demand for others
- Deterministic release process with traceability mapping
- Task-scoped loading to prevent overengineering

## Rule sets available

- Clean Code — Readability, naming, small functions, testing discipline
- Domain-Driven Design — Domain modeling, bounded contexts, tactical patterns
- Refactoring — Safe code improvement, smell detection, behavior preservation
- Clean Architecture — Stable boundaries, dependency rule, framework isolation
- Designing Data-Intensive Applications — Reliability, scalability, consistency semantics
- Working Effectively with Legacy Code — Characterization tests, seams, risk reduction
- The Pragmatic Programmer — Orthogonality, automation, fast feedback
- Code Complete — Routine design, defensive programming, coding standards
- A Philosophy of Software Design — Deep modules, simplicity, complexity fight
- Patterns of Enterprise Application Architecture — Enterprise patterns, layers, repositories
- Refactoring.Guru — Practical refactoring catalog, code smells
- Release It! — Production survival, circuit breakers, observability
- DDD Distilled / Implementing DDD — DDD entry and practice

## Architecture notes

Rules are compressed via a formal process (`PROCESS.md`) that preserves decision-changing content while dropping framing prose. Each book has a `_rule-workbench/` directory containing:

- `full.md` — Canonical source by symlink
- `mini.md` — On-demand compressed version
- `nano.md` — Compact always-on fallback
- `traceability.md` — What was kept, merged, or omitted with source references

## Use with Claude Code

Add `@sources/agent-rules-books/clean-code/clean-code.mini.md` to your `CLAUDE.md` for repo-wide engineering bias, or import specific rule sets on demand for targeted tasks like refactoring or architecture reviews. See USAGE.md for delivery patterns and version recommendations.

## Related

- [[skills]] — Agent skill frameworks that can integrate rule sets
- [[hermes-agent]] — Agent platform that can consume rule files via CLAUDE.md imports
- [[free-claude-code]] — CLI agent that can apply these rule sets through FCC proxy