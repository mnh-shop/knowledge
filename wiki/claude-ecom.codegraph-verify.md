---
name: claude-ecom-codegraph-verify
tags: [claude-ecom, codegraph-verify, claude-code, ecommerce]
description: "Codegraph Verification: claude-ecom — validating wiki claims against indexed source code"
source: sources/claude-ecom/
date: 2026-07-12
---

# Codegraph Verification: claude-ecom

**Date:** 2026-07-12

## Claim 1: Hybrid architecture — Python computes KPIs, Claude interprets them
- **Wiki says:** "It follows a hybrid architecture where Python handles deterministic computation (KPIs, health checks, scoring) and Claude handles business interpretation and narrative generation."

- **Source evidence:**
  - `CLAUDE.md` lines 10-17 document the architecture: "Order CSV Data → Python CLI (ecom review) [Deterministic: KPI calc, scoring, check evaluation] → review.json → Claude (SKILL.md) → REVIEW.md." With the key principle: "Python computes the numbers. Claude interprets them."
  - `skills/ecom/SKILL.md` line 29: "Key principle: Python computes the numbers. Claude interprets them. Never present raw numbers without business context."
  - `claude_ecom/review_engine.py` — Python engine producing review.json with KPI data.
  - `claude_ecom/report.py` — `generate_review_json()` and `review_json_filename()` for JSON output.
  - Python package `claude_ecom/` with 11 modules vs skill layer `skills/ecom/` with SKILL.md + 9 reference files — confirming the hybrid split.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Plugin-first distribution with self-bootstrapping Python backend
- **Wiki says:** "Ships as a Claude Code plugin (`claude-ecom@claude-ecom`) with a self-bootstrapping Python backend installed into `~/.local/share/claude-ecom/`."

- **Source evidence:**
  - `.claude-plugin/plugin.json` — Plugin manifest with name `claude-ecom`, version `0.2.0`, author `Hajime Takeda`.
  - `.claude-plugin/marketplace.json` — Marketplace manifest.
  - `bin/ecom` — Self-bootstrapping launcher (referenced in `hook.json` and plugin manifest).
  - `hooks/hooks.json` lines 1-17: Defines `SessionStart` hook with command `"${CLAUDE_PLUGIN_ROOT}"/bin/ecom --bootstrap-only` and 300s timeout.
  - README.md lines 27-42: Plugin install path: `/plugin marketplace add takechanman1228/claude-ecom` then `/plugin install claude-ecom@claude-ecom`. Documents: "The Python backend installs itself into a private venv (`~/.local/share/claude-ecom/`) on session start and survives plugin updates."
  - CHANGELOG.md 0.2.0 lines 15-18: "New self-bootstrapping launcher bin/ecom: installs the Python backend into a persistent venv at ~/.local/share/claude-ecom/ that survives plugin updates."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Multi-period analysis (30d/90d/365d) with trailing windows
- **Wiki says:** "Automatically selects 30-day / 90-day / 365-day trailing windows. Each period gets its own review JSON and markdown report."

- **Source evidence:**
  - `claude_ecom/periods.py` — Defines `trailing_window()` function (line 20) for N-day trailing windows. Line 36 defines `COVERAGE_THRESHOLDS = {"30d": 45, "90d": 120, "365d": 400}`.
  - `claude_ecom/periods.py` — `compute_data_coverage()` checks which trailing periods have enough data.
  - `claude_ecom/review_engine.py` — `build_review_data()` generates per-period review data for 30d, 90d, 365d windows.
  - `cli.py` line 34: `click.Choice(["30d", "90d", "365d"])` — CLI period selection.
  - `skills/ecom/SKILL.md` line 6: "KPI trees, ~30 pass/watch/fail health checks, 30d/90d/365d windows."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: KPI decomposition engine with health checks (pass/watch/fail)
- **Wiki says:** "Python engine (`review_engine.py`) computes trailing-window KPIs including revenue trends, order counts, AOV, customer acquisition, repeat purchase rates, and cohort behavior. Health checks classify signals as pass/watch/fail with impact estimation."

- **Source evidence:**
  - `claude_ecom/review_engine.py` (988 lines) — Unified period-based review builder computing revenue, orders, AOV, customer metrics per period.
  - `claude_ecom/metrics.py` (192 lines) — `compute_revenue_kpis()`, `compute_customer_kpis()`, and other core metric computations. Functions include `compute_revenue_kpis()` (line 18), which computes revenue trends, order counts, AOV, and new vs repeat customer breakdowns.
  - `claude_ecom/checks.py` (194 lines) — `CheckResult` dataclass with `result: str  # pass, watch, fail, na` (line 16), `category: str`, `severity: str`. Functions for `estimate_revenue_impact()` and `build_action_candidates()`.
  - `claude_ecom/cohort.py` (44 lines) — `rfm_segmentation()` for customer lifecycle and retention cohort analysis.
  - `claude_ecom/product.py` (130 lines) — `abc_analysis()` for product performance.
  - CLAUDE.md line 6-7 confirms health checks: "each check returns pass / watch / fail (no numeric scores). 3 categories: Revenue, Customer, Product."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Natural language queries routed through the Python compute engine
- **Wiki says:** "Ask questions like 'how was retention last month?' and Claude invokes the skill automatically, routing the question through the Python compute engine."

- **Source evidence:**
  - `skills/ecom/SKILL.md` frontmatter line 12: `when_to_use` includes "questions over order data like 'how was last month', 'how's retention', 'why did revenue drop'."
  - `skills/ecom/SKILL.md` lines 9-10: "interpretation: either a full narrative business review written to REVIEW.md, or an inline answer to a focused question."
  - `skills/ecom/SKILL.md` line 14: `argument-hint: "review [30d|90d|365d] [question]"` — confirming the question parameter support.
  - README.md line 80: `/claude-ecom:ecom review How's retention?` command example.
  - CLAUDE.md architecture diagram shows "Claude interprets the numbers" as the final stage after Python computes KPIs, confirming the engine supports both full reports and focused Q&A.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: SessionStart hook for auto-bootstrapping
- **Wiki says:** "Includes SessionStart hook for auto-bootstrapping."

- **Source evidence:**
  - `hooks/hooks.json` lines 1-17: Defines `SessionStart` hook with `"matcher": "startup|resume"` and command `"${CLAUDE_PLUGIN_ROOT}"/bin/ecom --bootstrap-only`.
  - README.md lines 40-42: "The Python backend installs itself into a private venv (~/.local/share/claude-ecom/) on session start and survives plugin updates."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Cohort analysis for customer lifecycle behavior
- **Wiki says:** "The `cohort.py` module provides retention cohort tracking to understand customer lifecycle behavior and repeat purchase patterns over time."

- **Source evidence:**
  - `claude_ecom/cohort.py` (44 lines) — `rfm_segmentation()` function implementing Recency-Frequency-Monetary scoring with quintile segmentation and customer segment labels.
  - `claude_ecom/review_engine.py` imports and uses cohort analysis as part of the unified review builder.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[claude-ecom]] -- Main wiki entry
- [[claude-seo]] -- SEO skills for Claude Code
- [[claude-ai-music-skills]] -- AI music generation skills
- [[openai-skills]] -- OpenAI skills collection

## Cross-project

- [[claude-seo.codegraph-verify]] -- SEO skills verification
- [[ai-marketing-claude-code-skills.codegraph-verify]] -- Marketing skills verification
- [[openai-skills.codegraph-verify]] -- OpenAI skills verification
