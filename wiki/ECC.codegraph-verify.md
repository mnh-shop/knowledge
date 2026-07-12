---
name: ECC-codegraph-verify
tags: [codegraph-verify, ecc, agent, harness]
description: "Codegraph Verification: ECC"
source: sources/ECC/
date: 2026-07-12
---

# Codegraph Verification: ECC

**Date:** 2026-07-12

## Claim 1: 67 specialized agents for software development workflows
- **Wiki says:** ECC provides 67 specialized subagents for delegation covering planner, architect, code reviewers, build resolvers, security reviewers, and more.

- **Source evidence:** `AGENTS.md` line 3 states: "67 specialized agents, 277 skills, 93 commands, and automated hook workflows." `AGENTS.md` lines 12-51 list agents by name and purpose, including: `planner`, `architect`, `tdd-guide`, `code-reviewer`, `security-reviewer`, `spec-miner`, `build-error-resolver`, `e2e-runner`, `refactor-cleaner`, `doc-updater`, `cpp-reviewer`, `go-reviewer`, `rust-reviewer`, `python-reviewer`, `java-reviewer`, `kotlin-reviewer`, `django-reviewer`, `typescript-reviewer`, `mle-reviewer`, `database-reviewer`, `loop-operator`, `harness-optimizer`, and more. `the-shortform-guide.md` lines 82-93 document subagent structure at `~/.claude/agents/` with files per agent. `CLAUDE.md` line 34 confirms `agents/` directory holds "Specialized subagents for delegation." The `agents/` directory on disk contains individual `.md` agent files.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: 277 skills as primary workflow surface
- **Wiki says:** ECC provides 277 skills as the primary workflow surface, organized by domain category.

- **Source evidence:** `AGENTS.md` line 3 states "277 skills." `AGENTS.md` lines 64-65 document the workflow surface policy: "`skills/` is the canonical workflow surface." `the-shortform-guide.md` lines 15-22 describe skills as "the primary workflow surface. They act like scoped workflow bundles: reusable prompts, structure, supporting files, and codemaps." `README.md` v2.0.0 release notes mention "261 skills, the control-pane substrate." `README.md` v2.0.0-rc.1 states "66 agents, 268 skills, and 84 legacy command shims." The `skills/` directory on disk confirms domain-organized skill folders.

- **Verdict:** ✅ CORRECT (277 per AGENTS.md — the live canonical source)
- **Fix needed:** None

## Claim 3: Cross-harness support across 7+ AI agent platforms
- **Wiki says:** ECC works across Codex, Claude Code, Cursor, OpenCode, Gemini, Zed, GitHub Copilot, and other AI agent harnesses.

- **Source evidence:** `README.md` lines 47-48 state: "Works across **Codex**, **Claude Code**, **Cursor**, **OpenCode**, **Gemini**, **Zed**, **GitHub Copilot**, and other AI agent harnesses." `AGENTS.md` line 71 lists supported harnesses in the project structure. `README.md` v1.8.0 release notes document "cross-harness parity — behavior tightened across Claude Code, Cursor, OpenCode, and Codex app/CLI." `README.md` v1.7.0 release notes document "Codex app + CLI support" and "Cursor, Codex, and OpenCode support tightened." `README.md` v1.3.0 documents "Full OpenCode integration — 12 agents, 24 commands, 16 skills with hook support." The `install.sh`, `install.ps1`, and `npx ecc-install` paths confirm multi-harness targeting via `--target` flag.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Hermes operator story with dedicated setup guide
- **Wiki says:** ECC v2.0.0 adds the public Hermes operator story, a dedicated setup guide, and cross-harness architecture documentation.

- **Source evidence:** `README.md` lines 49-50 state: "ECC v2.0.0 adds the public Hermes operator story on top of that reusable layer: start with the [Hermes setup guide](docs/HERMES-SETUP.md), then review the [2.0.0 release notes](docs/releases/2.0.0/release-notes.md) and [cross-harness architecture](docs/architecture/cross-harness.md)." The file `docs/HERMES-SETUP.md` exists in the source tree. `README.md` v2.0.0 release notes confirm "61 skills, the control-pane substrate (session adapters + MCP inventory), the worktree-lifecycle service, the `orch-*` orchestrator family." The `.hermes/README.md` provides Hermes-specific guidance within the repo.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: AgentShield security integration
- **Wiki says:** ECC includes AgentShield integration for automated security scanning, with 1282 tests and 102 rules.

- **Source evidence:** `README.md` v1.6.0 release notes document "AgentShield integration — `/security-scan` skill runs AgentShield directly from Claude Code; 1282 tests, 102 rules." `AGENTS.md` line 49 includes `security-reviewer` as a core agent for "Vulnerability detection." `AGENTS.md` lines 51-59 document security guidelines: "Before ANY commit: No hardcoded secrets, All user inputs validated, SQL injection prevention, XSS prevention." `README.md` points to `the-security-guide.md` covering "Attack vectors, sandboxing, sanitization, CVEs, AgentShield." The `ecc-agentshield` npm package is documented in README badges with weekly download counts.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Selective install architecture with manifest-driven pipeline
- **Wiki says:** ECC v1.9.0 introduced a manifest-driven selective install pipeline with state tracking and incremental updates.

- **Source evidence:** `README.md` v1.9.0 release notes state: "Selective install architecture — Manifest-driven install pipeline with `install-plan.js` and `install-apply.js` for targeted component installation. State store tracks what's installed and enables incremental updates." `README.md` lines 264-276 document the `--profile minimal`, `--profile core`, and `--profile full` installation profiles. `README.md` lines 294-300 document `npx ecc consult` for finding the right components: "It returns matching components, related profiles, and preview/install commands." Source files `manifests/install-profiles.json`, `manifests/install-modules.json`, and `manifests/install-components.json` define the modular install manifests.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Continuous learning with hooks, instincts, and skill lifecycle management
- **Wiki says:** ECC provides continuous learning through hooks, instinct-based learning with confidence scoring, and automated skill lifecycle management.

- **Source evidence:** `the-shortform-guide.md` lines 38-72 document hook types: PreToolUse, PostToolUse, UserPromptSubmit, Stop, PreCompact, and Notification with JSON-based hook definitions and matcher conditions. v1.2.0 release notes document "Continuous learning v2 — Instinct-based learning with confidence scoring, import/export, evolution." v1.9.0 release notes document "Skill evolution foundation for self-improving skills." `the-shortform-guide.md` line 72 documents the `hookify` plugin for creating hooks conversationally. README topic table includes "Continuous Learning — Auto-extract patterns from sessions into reusable skills" and "Memory Persistence — Hooks that save/load context across sessions automatically."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[ecc]] -- Main wiki entry
- [[hermes-agent]] -- Hermes Agent
- [[openclaw]] -- OpenClaw agent platform
- [[agentfield]] -- AgentField platform

## Cross-project

- [[hermes-agent.codegraph-verify]] -- Hermes Agent verification
- [[openclaw-container.codegraph-verify]] -- OpenClaw container verification
