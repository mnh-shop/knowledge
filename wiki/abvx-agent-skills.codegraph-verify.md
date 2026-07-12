---
name: abvx-agent-skills-codegraph-verify
tags: [abvx-agent-skills, codegraph-verify, skills, python, cli, validation, skillpack]
description: "Codegraph Verification: abvx-agent-skills — validating wiki claims against indexed source code symbols"
source: sources/abvx-agent-skills/
---

# Codegraph Verification: abvx-agent-skills

**Date:** 2026-07-12

## Claim 1: Small auditable skillpack with 58 individual skills
- **Wiki says:** ABVX Agent Skills is a small, auditable skillpack of 58 individually installable skills across 11 categories, designed for Codex-style project work. Each skill includes frontmatter, attribution, risk notes, and validation gates.
- **Source evidence:**
  - `skills/` contains exactly 58 skill directories (agent-learning-layer-triage through workflow-policy-layering), verified from directory listing
  - `CATALOG.md` enumerates all 58 skills with category, use case, and install command
  - `README.md` describes the repo as "small, reviewable, validation-gated agent skills" with 11 named categories (Token Economy, Coding/Debugging, Frontend/UX, HTML Artifacts, Project Context, Discovery/Planning, Research/Knowledge, Workflow/Handoffs, Long-Run Delivery, Security, Structured Data)
  - `pyproject.toml` at line 8: `description = "Small, reviewable, validation-gated agent skills for Codex-style project work."`
  - `README.md` line 17: "These are not prompt dumps. They are compact SKILL.md workflows with clear triggers, attribution, risk notes, and validation."
  - Each skill directory follows the `SKILL.md` + `SKILL_CARD.md` + `agents/openai.yaml` shape per README.md Repository Profile section
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: LoopOps framework for artifact promotion
- **Wiki says:** LoopOps is the framework layer deciding when repeated agent work should remain a prompt and when it should become a checklist, skill, script, or bounded loop. Documented in `docs/loopops-guide.md` and implemented in `skills/loopops-protocol/`.
- **Source evidence:**
  - `docs/loopops-guide.md` defines the 5-rung promotion ladder: prompt → skill → checklist → script → workflow → loop (line 9-27)
  - `docs/loopops-guide.md` includes decision heuristics (line 28-35) and anti-patterns (line 36-43)
  - `skills/loopops-protocol/SKILL.md` is a 157-line skill implementing the LoopOps Protocol with Artifact Ladder (line 19-30), Loop Suitability Gate (line 32-42), and Open vs Closed Loop (line 44-50+)
  - `README.md` at line 63-75: "LoopOps is the framework layer in this repo: it decides when a repeated prompt should remain a prompt and when it should become a checklist, skill, script, or bounded loop"
  - `skills/dynamic-workflow-packets/` and `skills/skillopt-evolve-skills/` are companion skills referenced in the LoopOps section
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Debugging skills with disciplined diagnosis loop
- **Wiki says:** The `diagnose` skill implements a reproducible debugging loop with ranked hypotheses, instrument-first approach, and narrow verification, not speculative guessing.
- **Source evidence:**
  - `skills/diagnose/SKILL.md` defines 5 phases: Phase 1 Feedback Loop (line 14-26), Phase 2 Reproduce (line 28-32), Phase 3 Hypothesize (line 34-47) with ranked hypotheses template, Phase 4 Instrument (line 49-50+), and verification
  - `skills/diagnose/SKILL.md` frontmatter: `description: "Debug coding failures through reproduction, ranked hypotheses, narrow fixes, and verification."`
  - `skills/diagnose/SKILL_CARD.md` provides attribution, risks, evaluation, and version metadata
  - `skills/diagnose/agents/openai.yaml` provides Codex UI metadata
  - `README.md` "Start Here" section: "Need to debug a repo? Start with `diagnose`, `repo-debugging-ledger`, and `graph-guided-code-reading`."
  - `docs/demos/diagnose.md` provides a worked example of the diagnose skill
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Frontend verification with browser-verification and frontend-product-builder skills
- **Wiki says:** The frontend skills group includes `browser-verification` for real browser testing, `frontend-product-builder` for product-first frontend implementation, plus design critique, taste layer, and motion review. These form a complete frontend workflow stack.
- **Source evidence:**
  - `skills/browser-verification/SKILL.md` has a 10-step verification loop (line 23-33), Common Assertions section (line 35-43), and Guardrails (line 45-50): "Trust the browser, not static guesses"
  - `skills/frontend-product-builder/SKILL.md` has Start With A Short Thesis (line 14-24), Product Surface Rules (line 26-35), Implementation Loop (line 37-44), Copy Rules (line 46-50+)
  - `skills/design-critique-polish/` exists with SKILL.md
  - `skills/frontend-taste-layer/` exists with SKILL.md
  - `skills/motion-review-gate/` exists with SKILL.md
  - `skills/design-register-bootstrap/` exists with SKILL.md
  - `skills/designmd-brand-kit/` exists with SKILL.md
  - `skills/web-quality-audit/` exists with SKILL.md
  - `skills/prototype-lab/` exists with SKILL.md
  - `README.md` groups them under "Frontend, UX & Product Surfaces" with 10 skills listed (lines 137-150)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: CLI packaging with validation pipeline and CI/CD
- **Wiki says:** The `abvx-skills` CLI provides install, list, validate, and audit commands. The validation pipeline includes structural validation (required files, frontmatter, no TODO placeholders), static security audit with SkillSpector, and GitHub Actions CI/CD.
- **Source evidence:**
  - `pyproject.toml` at line 37: `abvx-skills = "abvx_agent_skills.cli:main"` defines the CLI entry point
  - `src/abvx_agent_skills/cli.py` implements the CLI commands
  - `src/abvx_agent_skills/validator.py` provides structural validation logic
  - `src/abvx_agent_skills/packaged.py` handles package management
  - `src/abvx_agent_skills/catalog.py` generates the skill catalog
  - `scripts/validate.py` provides the validation gate: "Validates required files, frontmatter, directory/name alignment, TODO placeholders, cards, UI metadata, and basic secret patterns"
  - `scripts/evaluate_skillspector.py` evaluates SkillSpector security audit reports
  - `.github/workflows/validate.yml` and `.github/workflows/security-audit.yml` badges in README.md show CI status
  - `README.md` lines 389-421 document validate and audit-security commands
  - `README.md` line 423-425: "Benchmark scaffolding now lives under `benchmarks/`. It documents how to measure skill impact"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Token economy skills for context optimization
- **Wiki says:** The token economy layer is intentionally listed first, containing 8 skills for reducing wasted context: RTK-assisted shell, shell-output-compaction, graph-guided code reading, token-efficient execution, token-frugal mode, lean-context-layout, compaction-survival, and token-usage-audit.
- **Source evidence:**
  - `skills/rtk-assisted-shell/SKILL.md` — Routes noisy shell workflows through RTK-style filtering
  - `skills/shell-output-compaction/SKILL.md` — Shrinks logs, diffs, and search output
  - `skills/graph-guided-code-reading/SKILL.md` — Replaces broad repo reading with entrypoints and symbols
  - `skills/token-efficient-execution/SKILL.md` — Cuts waste from repeated reads and broad rewrites
  - `skills/token-frugal-mode/SKILL.md` — Compresses final answers without losing signal
  - `skills/lean-context-layout/SKILL.md` — Shrinks always-loaded agent docs
  - `skills/compaction-survival/SKILL.md` — Preserves working state across session compaction
  - `skills/token-usage-audit/SKILL.md` — Diagnoses where token budget is being wasted
  - `README.md` lines 108-119: "These skills are grouped by the job they do. The token-economy layer is intentionally visible first"
  - `README.md` line 120: "for many teams, the easiest win is not 'a smarter prompt', but less wasted context"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 6 key claims from the abvx-agent-skills wiki have been verified against source code:
- ✅ 58-skill auditable skillpack confirmed from `skills/` directory listing and `CATALOG.md`
- ✅ LoopOps framework confirmed in `docs/loopops-guide.md` and `skills/loopops-protocol/SKILL.md`
- ✅ Debugging discipline confirmed in `skills/diagnose/SKILL.md` with 5-phase diagnosis loop
- ✅ Frontend verification stack confirmed with 8+ skills including `browser-verification` and `frontend-product-builder`
- ✅ CLI validation pipeline confirmed with `src/abvx_agent_skills/cli.py` and `scripts/validate.py`
- ✅ Token economy skills confirmed with 8 skill directories under the Token Economy & Context Control category

## Related

- [[abvx-agent-skills]] — Main wiki entry
- [[skills]] — Agent skills overview
- [[reverse-skill]] — Related skill repository
- [[slavinga-skills]] — Related skill repository

## Cross-project

- [[n8n.codegraph-verify]] — Similar codegraph verification for n8n
- [[openai-skills.codegraph-verify]] — Similar codegraph verification for OpenAI Skills
- [[drawio-skill.codegraph-verify]] — Similar codegraph verification for drawio-skill
- [[agentfield.codegraph-verify]] — Similar codegraph verification for AgentField
