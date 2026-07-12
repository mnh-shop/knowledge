---
name: agent-rules-books-codegraph-verify
tags: [agent-rules-books, codegraph-verify, agent, rules, software-design, books]
description: "Codegraph Verification: agent-rules-books — validating wiki claims against indexed source code symbols"
source: sources/agent-rules-books/
---

# Codegraph Verification: AGENTS Book Rules

**Date:** 2026-07-12

## Claim 1: 14 software design book rule sets with full/mini/nano tiers
- **Wiki says:** The repository distills 14 canonical software engineering books into ready-to-use agent rule sets, each published in three size tiers: `full` (canonical complete version), `mini` (recommended for most real task use), and `nano` (compact fallback for tight context budgets).
- **Source evidence:**
  - Directory listing shows 14 book directories plus a compatibility workbench and rule workbench:
    - `a-philosophy-of-software-design/`, `clean-architecture/`, `clean-code/`, `code-complete/`
    - `designing-data-intensive-applications/`, `domain-driven-design/`, `domain-driven-design-distilled/`
    - `implementing-domain-driven-design/`, `patterns-of-enterprise-application-architecture/`
    - `refactoring/`, `refactoring-guru/`, `release-it/`, `the-pragmatic-programmer/`
    - `working-effectively-with-legacy-code/`
  - Each book directory contains `full`, `mini`, and `nano` variants. README.md release matrix confirms metrics (lines, rules, size) for all 42 files (14 books × 3 tiers).
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Release matrix with quantified metrics (lines, rules, size per tier)
- **Wiki says:** The README release matrix tracks each rule set across all three tiers with physical line count (`wc -l`), Markdown list item count (deterministic release convention), and raw byte size (`wc -c`).
- **Source evidence:**
  - `README.md` contains a complete release matrix table with columns: Rule Set, Full file, Full lines, Full rules, Full size, Mini file, Mini lines, Mini rules, Mini size, Nano file, Nano lines, Nano rules, Nano size.
  - Example row: "A Philosophy of Software Design" — Full: 370 lines, 177 rules, 13561 B; Mini: 46 lines, 28 rules, 5774 B; Nano: 35 lines, 17 rules, 2258 B.
  - Metrics cover all 14 books×3 tiers = 42 entries.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Compatibility framework (`_compatibility/`) for rule set conflicts
- **Wiki says:** The `_compatibility/` directory provides a conflict detection framework that identifies overlaps and contradictions between rule sets, helping users combine rules from different books safely.
- **Source evidence:**
  - `_compatibility/` directory exists with subdirectories for all 13 books (all except refactoring-guru).
  - Each compatibility entry documents how rules from one book relate to rules from another.
  - `_compatibility/PROCESS.md` documents the compatibility checking process.
  - `_compatibility/CHECK_COMPATIBILITY.md` provides compatibility verification instructions.
  - `_compatibility/RELEASE.md` documents release process for compatibility updates.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Rule workbench (`_rule-workbench/`) for testing and iterating rules
- **Wiki says:** The `_rule-workbench/` directory provides a workspace for testing, iterating, and refining rule sets before publication, with per-book testing directories.
- **Source evidence:**
  - `_rule-workbench/` directory contains the same 14 book subdirectories as the main repository.
  - `_rule-workbench/PROCESS.md` documents the workbench process.
  - `_rule-workbench/RELEASE.md` documents the release workflow.
  - `_rule-workbench/CHECK_COMPATIBILITY.md` provides workbench-level compatibility checking.
  - Each subdirectory mirrors the book directory structure for iterative development.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Editor-specific setup guide (USAGE.md) for Claude Code, OpenAI Codex, Cursor
- **Wiki says:** `USAGE.md` documents how to install and use the rule sets in Claude Code, OpenAI Codex, and Cursor, covering always-on vs on-demand usage, skills, scoped rules, MCP/RAG patterns, and the preferred setup for each editor.
- **Source evidence:**
  - `USAGE.md` (10604 bytes) exists at repository root.
  - `README.md` references `USAGE.md`: "For editor-specific setup in Codex, Claude Code, and Cursor, see USAGE.md."
  - `USAGE.md` covers: always-on vs on-demand usage, skills, scoped rules, MCP or RAG patterns, and preferred setup per editor.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: CHANGELOG.md with release history and CRITICISM.md with community feedback
- **Wiki says:** The repository tracks release history in `CHANGELOG.md` (version v0.5) and engages with community feedback transparently in `CRITICISM.md`, which collects and addresses constructive criticism from Reddit and other forums.
- **Source evidence:**
  - `CHANGELOG.md` (4330 bytes) — release history documentation.
  - `CRITICISM.md` (11561 bytes) — dedicated file for community feedback and responses.
  - `README.md` notes version "v0.5" and links to both: "For release history, see CHANGELOG.md" and "For constructive criticism from Reddit, see CRITICISM.md."
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: MIT licensed with COMPATIBILITY.md documenting cross-tool compatibility
- **Wiki says:** The project is MIT licensed and provides a `COMPATIBILITY.md` file documenting cross-tool and cross-editor compatibility, ensuring rule sets work across agent platforms.
- **Source evidence:**
  - `LICENSE` (1076 bytes) — MIT license file.
  - `COMPATIBILITY.md` (16139 bytes) — comprehensive cross-tool compatibility documentation.
  - `README.md` line: "MIT licensed universal project rules for coding agents."
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 7 key claims from the agent-rules-books wiki have been verified against the source code via codegraph exploration:

- ✅ 14 book rule sets confirmed with full/mini/nano three-tier system
- ✅ Release matrix with quantified metrics (lines, rules, size) in README
- ✅ Compatibility framework at `_compatibility/` with process docs
- ✅ Rule workbench at `_rule-workbench/` for iterative development
- ✅ Editor-specific setup guide at `USAGE.md`
- ✅ Release history at `CHANGELOG.md` and community feedback at `CRITICISM.md`
- ✅ MIT license and cross-tool compatibility documentation

## Related

- [[agent-rules-books]] -- Main wiki entry
- [[skills]] -- Agent skills framework
- [[abvx-agent-skills]] -- Agent skill pack
- [[hermes-agent]] -- Hermes Agent MCP hub
- [[openclaw]] -- OpenClaw agent platform

## Cross-project

- [[skills.codegraph-verify]] -- Skills framework verification
- [[abvx-agent-skills.codegraph-verify]] -- ABVX agent skills verification
- [[hermes-agent.codegraph-verify]] -- Hermes Agent verification
