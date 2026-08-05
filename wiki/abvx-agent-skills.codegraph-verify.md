---
name: abvx-agent-skills-codegraph-verify
tags: [abvx-agent-skills, codegraph-verify, skills, python, cli, validation, skillpack]
description: "Codegraph Verification: abvx-agent-skills — validating wiki claims against indexed source code symbols"
source: sources/abvx-agent-skills/
---

# Codegraph Verification: abvx-agent-skills

**Date:** 2026-07-30

## Claim 1: 81 individual skills
- **Wiki says:** ABVX Agent Skills is a small, auditable skillpack of 81 individually installable skills (alphabetically `agent-friction-ledger` through `workflow-policy-layering`), designed for Codex-style project work. Each skill includes frontmatter, attribution, risk notes, and validation gates.
- **Source evidence:**
  - `skills/` contains exactly 81 skill directories (`ls skills/ | wc -l` → 81; first: `agent-friction-ledger`, last: `workflow-policy-layering`), verified from directory listing
  - `CATALOG.md` enumerates all 81 skills (`grep -c "^| \`" CATALOG.md` → 81) with category, eval tier, use case, and install command
  - `pyproject.toml` line 8: `description = "Small, reviewable, validation-gated agent skills for Codex-style project work."`
  - `README.md` line 17: "These are not prompt dumps. They are compact `SKILL.md` workflows with clear triggers, attribution, risk notes, and validation."
  - Each skill directory follows the `SKILL.md` + `SKILL_CARD.md` + `agents/openai.yaml` shape
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (previously stale: 58 was reported from an outdated directory listing; current source has 81)

## Claim 2: 12 README category sections (77 categorized + 4 uncategorized = 81)
- **Wiki says:** Skills are organized by job function across 12 category sections in the README, plus 4 catalog-listed "Uncategorized" entries; all enumerated in CATALOG.md.
- **Source evidence:**
  - `README.md` has 12 skill-category `###` sections (line numbers): Token Economy & Context Control (154), Coding, Debugging & Architecture (168), Frontend, UX & Product Surfaces (186), HTML Artifacts & Visual Deliverables (203), Project Context & Onboarding (210), Discovery, Planning & Delivery (222), Research, Knowledge & Reusable Methods (233), Product Context & Responsible Growth (252), Workflow, Handoffs & Multi-Track Work (259), Long-Run Delivery Control (270), Security & Defensive Review (281), Structured Data & Spreadsheet Work (287)
  - Skill counts per README category table: Token Economy 9, Coding/Debugging 13, Frontend/UX 12, HTML Artifacts 2, Project Context 5, Discovery/Planning 6, Research/Knowledge 14, Product Context 2, Workflow/Handoffs 6, Long-Run Delivery 6, Security 1, Structured Data 1 → 77 categorized skills
  - `CATALOG.md` lists 4 additional `Uncategorized` skills (agent-operations-contract, bounded-orchestration-contract, git-native-context-contract, knowledge-base-enrichment) → 77 + 4 = 81
  - "Product Context & Responsible Growth" was added in commit `5d5983f` (2026-07-26) "feat: add product context and bounded growth loop skills (#50)" adding `product-context` and `bounded-growth-loop`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (previously stale: 11 categories reported)

## Claim 3: Token economy layer lists 9 skills including context-degradation-review
- **Wiki says:** The token-economy layer is intentionally listed first, containing 9 skills: rtk-assisted-shell, shell-output-compaction, graph-guided-code-reading, context-degradation-review, token-efficient-execution, token-frugal-mode, lean-context-layout, compaction-survival, and token-usage-audit.
- **Source evidence:**
  - `README.md` "Token Economy & Context Control" table (lines 154-166) lists exactly 9 skill rows: `rtk-assisted-shell`, `shell-output-compaction`, `graph-guided-code-reading`, `context-degradation-review`, `token-efficient-execution`, `token-frugal-mode`, `lean-context-layout`, `compaction-survival`, `token-usage-audit`
  - `README.md` line 161: "`context-degradation-review` | Reviews context poisoning, lost-in-the-middle failures, distraction, context clash, and stale carryover before they degrade agent behavior."
  - `README.md` line 109 (Start Here): "**Need to check whether context is hurting the run?** Start with `context-degradation-review` before trusting long handoffs, memory summaries, or bloated SET bundles."
  - `CATALOG.md` lists `context-degradation-review` under Token Economy & Context Control
  - `README.md` lines 150-152: "These skills are grouped by the job they do. The token-economy layer is intentionally visible first: for many teams, the easiest win is not 'a smarter prompt', but less wasted context."
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (previously stale: 8 skills reported; `context-degradation-review` was missing)

## Claim 4: LoopOps promotion ladder is Prompt → Checklist → Skill → Script → Loop/workflow
- **Wiki says:** LoopOps is the framework layer deciding when repeated agent work should remain a prompt and when it should become a checklist, skill, script, or bounded loop. The promotion ladder progresses Prompt → Checklist → Skill → Script → Loop/workflow.
- **Source evidence:**
  - `docs/loopops-guide.md` lines 9-27 define the 5-rung promotion ladder in order: 1. **Prompt** ("one-off task, low cost of repetition"), 2. **Checklist** ("same task repeats, sequence matters"), 3. **Skill** ("workflow is reusable and procedural"), 4. **Script** ("a deterministic step keeps getting rewritten"), 5. **Loop / workflow** ("the task spans multiple cycles; a bounded evaluator, memory policy, and stop rule are needed")
  - `docs/loopops-guide.md` lines 28-35 contain decision heuristics; lines 36-43 anti-patterns
  - `skills/loopops-protocol/SKILL.md` implements the LoopOps Protocol with Artifact Ladder, Loop Suitability Gate, and Open vs Closed Loop sections
  - `README.md` lines 85-96: "LoopOps is the framework layer in this repo: it decides when a repeated prompt should remain a prompt and when it should become a checklist, skill, script, or bounded loop" with companion skills `dynamic-workflow-packets` and `skillopt-evolve-skills`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (previously mis-ordered in the verify page as "prompt → skill → checklist → script → workflow → loop"; corrected to Prompt → Checklist → Skill → Script → Loop/workflow)

## Claim 5: diagnose implements a 5-phase debugging loop
- **Wiki says:** The `diagnose` skill implements a reproducible debugging loop with ranked hypotheses, instrument-first approach, and narrow verification, not speculative guessing. README "Start Here" recommends diagnose first for repo debugging.
- **Source evidence:**
  - `skills/diagnose/SKILL.md` defines 5 phases: Phase 1 Feedback Loop (line 14), Phase 2 Reproduce (line 28), Phase 3 Hypothesize (line 34, ranked hypotheses), Phase 4 Instrument (line 48), Phase 5 Fix And Regression Test (line 55)
  - `skills/diagnose/SKILL.md` frontmatter: `description: "Debug coding failures through reproduction, ranked hypotheses, narrow fixes, and verification."`
  - `skills/diagnose/SKILL_CARD.md` provides attribution, risks, evaluation, and version metadata; `skills/diagnose/agents/openai.yaml` provides Codex UI metadata
  - `README.md` line 111 (Start Here): "**Need to debug a repo?** Start with `diagnose`, `repo-debugging-ledger`, and `graph-guided-code-reading`."
  - `docs/demos/diagnose.md` provides a worked example
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Frontend verification stack
- **Wiki says:** The frontend skills group includes `browser-verification` for real browser testing, `frontend-product-builder` for product-first frontend implementation, plus design critique, taste layer, motion review, design register, brand kit, web quality audit, and prototype lab. These form a complete frontend workflow stack.
- **Source evidence:**
  - `README.md` "Frontend, UX & Product Surfaces" section (lines 186-201) lists 12 skills including: `design-register-bootstrap` (190), `frontend-taste-layer` (191), `fluid-interaction-review` (192), `anti-slop-review` (193), `design-critique-polish` (194), `frontend-product-builder` (195), `lottie-motion-builder` (196), `motion-review-gate` (197), `designmd-brand-kit` (198), `browser-verification` (199), `web-quality-audit` (200), `prototype-lab` (201)
  - `skills/browser-verification/SKILL.md` has a 10-step verification loop, Common Assertions section, and Guardrails ("Trust the browser, not static guesses")
  - `skills/frontend-product-builder/SKILL.md` has Start With A Short Thesis, Product Surface Rules, Implementation Loop, and Copy Rules sections
  - All 12 skill directories exist under `skills/` (verified from directory listing)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: CLI packaging with validation pipeline and CI/CD
- **Wiki says:** The `abvx-skills` CLI provides install, list, validate, and audit commands. The validation pipeline includes structural validation, static security audit with SkillSpector, and GitHub Actions CI/CD.
- **Source evidence:**
  - `pyproject.toml` line 37: `abvx-skills = "abvx_agent_skills.cli:main"` defines the CLI entry point
  - `src/abvx_agent_skills/cli.py`, `src/abvx_agent_skills/validator.py`, `src/abvx_agent_skills/packaged.py`, `src/abvx_agent_skills/catalog.py` implement CLI commands, structural validation, package management, and catalog generation
  - `scripts/validate.py` provides the validation gate; `scripts/evaluate_skillspector.py` evaluates SkillSpector security audit reports; `scripts/generate_catalog.py` regenerates the catalog
  - `.github/workflows/validate.yml`, `.github/workflows/security-audit.yml`, `.github/workflows/publish.yml` provide CI/CD (README.md lines 9-11 show the Validate, Security Audit, and PyPI badges)
  - `README.md` lines 389-399 document `abvx-skills validate` and `abvx-skills audit-security ./skills --no-llm`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: Quick-start gh skill flow, catalog, and package metadata
- **Wiki says:** Preview via `gh skill preview`, install via `gh skill install markoblogo/abvx-agent-skills <skill> --agent codex --scope user`; catalog at lab.abvx.xyz + CATALOG.md generated from docs/catalog.json; package is MIT, v0.12.0.
- **Source evidence:**
  - `README.md` lines 23-39 document `gh skill preview markoblogo/abvx-agent-skills minimal-diff-builder` and `gh skill install markoblogo/abvx-agent-skills minimal-diff-builder --agent codex --scope user`
  - `README.md` lines 53-57: catalog at [lab.abvx.xyz/tools/abvx-agent-skills/](https://lab.abvx.xyz/tools/abvx-agent-skills/) "powered by the generated catalog data in docs/catalog.json"; CATALOG.md is the scan-friendly text catalog
  - `src/abvx_agent_skills/catalog.py` line 67 `build_catalog()` and line 130 render "Generated from `docs/catalog.json`" — CATALOG.md header confirms this
  - `pyproject.toml` line 7: `version = "0.12.0"`, line 11: `license = "MIT"`, line 8: `description = "Small, reviewable, validation-gated agent skills for Codex-style project work."`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 8 key claims from the abvx-agent-skills wiki have been verified against source:
- ✅ 81 skills confirmed from `skills/` directory listing and `CATALOG.md` (was 58)
- ✅ 12 README categories confirmed (was 11); 77 categorized + 4 uncategorized = 81
- ✅ Token economy 9 skills confirmed including `context-degradation-review` (was 8)
- ✅ LoopOps ladder order corrected: Prompt → Checklist → Skill → Script → Loop/workflow
- ✅ diagnose 5-phase loop confirmed in `skills/diagnose/SKILL.md`
- ✅ Frontend verification stack confirmed (12 skills, README lines 186-201)
- ✅ CLI validation pipeline confirmed with `src/abvx_agent_skills/*` and `.github/workflows/*`
- ✅ gh skill quick start + catalog + pyproject metadata (v0.12.0, MIT) confirmed

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
