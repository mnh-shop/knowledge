---
name: ECC-codegraph-verify
tags: [codegraph-verify, ecc, agent, harness]
description: "Codegraph Verification: ECC"
source: sources/ECC/
date: 2026-07-12
---

# Codegraph Verification: ECC

**Date:** 2026-07-12

## Claim 1: Version 2.1.0 with 67 agents, 281 skills, 94 command shims
- **Wiki says:** ECC v2.1.0 ships 67 specialized agents, 281 workflow skills, and 94 legacy command shims.

- **Source evidence:** `package.json` declares `"version": "2.1.0"`; `AGENTS.md` line 5 states "**Version:** 2.1.0"; the `VERSION` file contains `2.1.0`. `AGENTS.md` line 3 states "67 specialized agents, 281 skills, 94 commands, and automated hook workflows." `README.md` line 119 states "Access to 67 agents, 281 skills, and 94 legacy command shims," and lines 123-124 tabulate "67 agents" and "281 skills." `docs/releases/2.1.0/release-notes.md` closes with "The catalog now stands at **67 agents, 281 skills, and 94 command shims** (2.0.0 shipped 64/261/84)." On disk: `agents/` contains 67 `.md` files, `skills/` contains 281 SKILL.md directories, `commands/` contains 94 `.md` files.

- **Verdict:** ✅ CORRECT (wiki corrected from 2.0.0/271 skills/92 commands)
- **Fix needed:** None

## Claim 2: 122 rules across 22 packs (common + 21 language packs)
- **Wiki says:** ECC ships 122 always-follow rules across 22 packs: `common/` plus 21 language-specific packs.

- **Source evidence:** The `rules/` directory contains exactly 22 pack directories — `common` plus `typescript`, `python`, `golang`, `swift`, `php`, `arkts`, `cpp`, `csharp`, `dart`, `fsharp`, `java`, `kotlin`, `perl`, `ruby`, `rust`, `vue`, `react`, `react-native`, `angular`, `nuxt`, `web` — plus a top-level `README.md`. `find rules -name "*.md"` returns 122 files total. No source text claims "250+ multi-language rules"; the earlier wiki figure was unsupported.

- **Verdict:** ✅ CORRECT (wiki corrected from unsupported "250+ rules")
- **Fix needed:** None

## Claim 3: 21 hook automations with per-event breakdown
- **Wiki says:** ECC ships 21 trigger-based hook automations across PreToolUse, Stop, PostToolUse, SessionStart, PostToolUseFailure, PreCompact, and SessionEnd.

- **Source evidence:** `hooks/hooks.json` defines: `PreToolUse` 8 (bash dispatcher, doc-file-warning, suggest-compact, observe-runner, governance-capture, config-protection, mcp-health-check, gateguard-fact-force), `Stop` 6 (format-typecheck, check-console-log, session-end, evaluate-session, cost-tracker, desktop-notify), `PostToolUse` 2 (sync + async dispatchers), `SessionStart` 2 (session start bootstrap, plan-canvas-sessions), `PostToolUseFailure` 1, `PreCompact` 1, `SessionEnd` 1 — 21 total.

- **Verdict:** ✅ CORRECT (wiki corrected from "20+")
- **Fix needed:** None

## Claim 4: Cross-harness support — 11 install targets plus Cursor's 15 hook events
- **Wiki says:** ECC installs into Cursor (15 hook events), OpenCode, Gemini, Zed, Antigravity, Qwen, Hermes, OpenClaw, Kimi, CodeBuddy, and JoyCode, with GitHub Copilot support built in.

- **Source evidence:** `README.md` lines 253-266 tabulate the install targets: Cursor, OpenCode, Gemini CLI, Zed, Antigravity, Qwen CLI, Hermes, OpenClaw, Kimi Code CLI, CodeBuddy, JoyCode — each with an `./install.sh --target <name>` command — and the following lines document built-in GitHub Copilot support via `.github/copilot-instructions.md` and `.github/prompts/`. `.cursor/hooks.json` defines 15 distinct hook event types (sessionStart, sessionEnd, beforeShellExecution ×2, afterShellExecution, afterFileEdit, beforeMCPExecution, afterMCPExecution, beforeReadFile, beforeSubmitPrompt, subagentStart, subagentStop, beforeTabFileRead, afterTabFileEdit, preCompact, stop).

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Selective install with 7 profiles including opencode
- **Wiki says:** Manifest-driven selective install exposes 7 profiles: minimal, opencode, core, developer, security, research, and full.

- **Source evidence:** `manifests/install-profiles.json` defines exactly seven profiles — `minimal`, `opencode`, `core`, `developer`, `security`, `research`, `full` — each mapping to a module list (e.g., `opencode` = commands-core + platform-configs + workflow-quality, intentionally excluding hooks-runtime). `README.md` lines 264-276 document the `--profile` install flow and line 324 documents `npx ecc consult "security reviews" --target claude`. The runner lives at `scripts/consult.js`.

- **Verdict:** ✅ CORRECT (wiki corrected from 6 profiles — `opencode` was omitted)
- **Fix needed:** None

## Claim 6: orch-* is a skill/workflow family, not part of ecc2
- **Wiki says:** The `orch-*` orchestrator family is a skill/workflow family (`orch-add-feature`, `orch-build-mvp`, `orch-change-feature`, `orch-fix-defect`, `orch-refine-code`, `orch-review`) with dynamic workflow team orchestration — separate from the `ecc2/` Rust prototype.

- **Source evidence:** `agent.yaml` lines 214-219 list the `orch-*` entries alongside other skills/commands; the workflow driver exists at `workflows/orch-review.workflow.js`; `docs/releases/2.0.0/release-notes.md` line 11 lists "`orch-*` orchestrator skill family plus dynamic workflow team orchestration" as a 2.0.0 highlight. `ecc2/README.md` opens "ECC 2.0 Alpha — the current Rust-based ECC 2.0 control-plane scaffold" with 16 `.rs` files in `ecc2/src/` (session, worktree, tui, observability, comms) — no `orch-*` code lives in `ecc2/`.

- **Verdict:** ✅ CORRECT (wiki corrected — previously misattributed `orch-*` to `ecc2/`)
- **Fix needed:** None

## Claim 7: 2.1 features — Plan Canvas, Unified Memory Vault, Itô RFQ bridge
- **Wiki says:** ECC 2.1 adds Plan Canvas, the Unified Memory Vault (`ecc memory` + optional `ecc-memory-mcp`), and the guarded Itô RFQ bridge (`ecc ito find`), plus the Kimi install target.

- **Source evidence:** `docs/releases/2.1.0/release-notes.md` lines 1-18 document Plan Canvas ("review plans by pointing, not retyping," `ecc-plan-canvas` CLI, CONFIRM-gate mapping); `README.md` lines 643-654 describe Plan Canvas with the demo plan at `docs/releases/2.1.0/plan-canvas-demo.plan.md`. `README.md` lines 663-665 and 815-829 document "Current development: Unified Memory Vault" — `ecc memory init --scope project`, `ecc memory search ... --target-harness codex`, `ecc memory doctor`, and the optional `ecc-memory-mcp` stdio server that "does not enable itself by default." `README.md` line 466 and `docs/releases/2.1.0/release-notes.md` lines 29-37 document `ecc ito find`: an opt-in bridge invoking the canonical Itô CLI to submit a live authenticated RFQ (no capacity reservation; credential-bearing CLI shims rejected).

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: AgentShield, dashboard, and consult verified
- **Wiki says:** AgentShield has 1282 tests, 98% coverage, and 102 static analysis rules; the 3-Opus pipeline runs via `--opus --stream`; the Tkinter dashboard is 956 lines; `npx ecc consult` is the component finder.

- **Source evidence:** `README.md` line 1196: "Built at the Claude Code Hackathon (Cerebral Valley x Anthropic, Feb 2026). 1282 tests, 98% coverage, 102 static analysis rules." `skills/security-scan/SKILL.md` line 98 documents `npx ecc-agentshield scan --opus --stream` and lines 100-106 the Attacker/Defender/Auditor (red/blue/auditor) roles — the pipeline itself executes in the external `agentshield` repo (`npx ecc-agentshield`). `package.json` line 456 defines `"dashboard": "python3 ./ecc_dashboard.py"` and `ecc_dashboard.py` is 956 lines. `scripts/consult.js` exists with `SUPPORTED_INSTALL_TARGETS` and `listInstallComponents`. Plugin-hook convention: `README.md` line 409 — "Claude Code v2.1+ already auto-loads plugin `hooks/hooks.json`"; do not duplicate in `settings.json`.

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
