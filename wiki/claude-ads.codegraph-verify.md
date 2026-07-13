---
name: claude-ads-codegraph-verify
tags: [codegraph-verify, claude-ads, agent-skills, advertising, paid-media, ppc]
description: "Codegraph Verification: claude-ads — Paid Advertising Audit & Optimization Skill"
source: sources/claude-ads/
date: 2026-07-12
---

# Codegraph Verification: claude-ads

**Date:** 2026-07-12

## Claim 1: Architecture — 22 sub-skills + 10 agents + 12 industry templates + 25+ reference files

- **Wiki says:** The skill comprises 22 specialized sub-skills, 10 agents (6 audit + 4 creative), 12 industry templates, and 26 RAG reference files organized in a 3-layer architecture (directive, orchestration, execution).

- **Source evidence:**
  - `CLAUDE.md` lines 7-10 state: "22 sub-skills, 10 agents (6 audit + 4 creative), and 12 industry templates".
  - `CLAUDE.md` lines 14-63 list the full architecture tree including all 22 sub-skills (lines 22-43: `ads-audit` through `ads-photoshoot`), all 10 agents (lines 44-54: `audit-google.md` through `format-adapter.md`).
  - Directory listing of `skills/` confirms exactly 22 entries (`ads-amazon/` through `ads-youtube/`).
  - Directory listing of `agents/` confirms exactly 10 agent files.
  - Directory listing of `skills/ads-plan/assets/` confirms exactly 12 industry template files: `agency.md`, `b2b-enterprise.md`, `ecommerce-creative.md`, `ecommerce.md`, `finance.md`, `generic.md`, `healthcare.md`, `info-products.md`, `local-service.md`, `mobile-app.md`, `real-estate.md`, `saas.md`.
  - `ads/SKILL.md` lines 176-207 list 26 reference files under `references/`. Directory listing of `ads/references/` confirms exactly 26 `.md` files: `additional-platforms.md`, `benchmarks.md`, `bidding-strategies.md`, `brand-dna-template.md`, `budget-allocation.md`, `compliance.md`, `conversion-tracking.md`, `copy-frameworks.md`, `gaql-notes.md`, `google-audit.md`, `google-creative-specs.md`, `image-providers.md`, `linkedin-audit.md`, `linkedin-creative-specs.md`, `mcp-integration.md`, `meta-audit.md`, `meta-creative-specs.md`, `microsoft-audit.md`, `microsoft-creative-specs.md`, `platform-specs.md`, `scoring-system.md`, `thinking-framework.md`, `tiktok-audit.md`, `tiktok-creative-specs.md`, `voice-to-style.md`, `youtube-creative-specs.md`.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Platform coverage — Google, Meta, YouTube, LinkedIn, TikTok, Microsoft, Apple, Amazon

- **Wiki says:** The skill covers eight ad platforms: Google, Meta, YouTube, LinkedIn, TikTok, Microsoft, Apple, and Amazon Ads.

- **Source evidence:**
  - `CLAUDE.md` lines 7-10: "cover Google, Meta, YouTube, LinkedIn, TikTok, Microsoft, Apple, and Amazon Ads with 250+ weighted audit checks".
  - `CLAUDE.md` lines 22-30 list sub-skills for all eight platforms: `ads-google`, `ads-meta`, `ads-youtube`, `ads-linkedin`, `ads-tiktok`, `ads-microsoft`, `ads-apple`, `ads-amazon`.
  - Directory listing of `skills/` confirms all eight platform-specific sub-skill directories exist.
  - `ads/SKILL.md` lines 12-13: "Comprehensive ad account analysis across all major platforms (Google, Meta, LinkedIn, TikTok, Microsoft, Apple, Amazon)." (Note: YouTube is covered but the summary line references its inclusion via other means — `ads-youtube/SKILL.md` exists as a standalone sub-skill.)
  - `ads/SKILL.md` lines 242-250 list all eight platform sub-skills by number and description.
  - `tests/fixtures/check-catalog.yaml` lines 21-25 define check IDs for five platforms: `google`, `meta`, `linkedin`, `tiktok`, `microsoft` with bidirectionally verified checks (Apple and Amazon checks will land in Wave 3 catalog expansion per README.md lines 341-342).

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Image generation — multi-provider support (Gemini, OpenAI, Stability, Replicate)

- **Wiki says:** `scripts/generate_image.py` supports four image generation providers: Gemini (default), OpenAI, Stability AI, and Replicate, with functions `generate_gemini`, `generate_openai`, `generate_stability`, `generate_replicate`.

- **Source evidence:**
  - `scripts/generate_image.py` lines 12-13: "Supports Gemini (default), OpenAI, Stability AI, and Replicate."
  - `scripts/generate_image.py` lines 25-29: Environment variable documentation for `GOOGLE_API_KEY`, `OPENAI_API_KEY`, `STABILITY_API_KEY`, `REPLICATE_API_TOKEN`.
  - `scripts/generate_image.py` lines 75-79: Default model constants for all four providers: `DEFAULT_PROVIDER = "gemini"`, `DEFAULT_MODEL_GEMINI = "gemini-2.5-flash-image"`, `DEFAULT_MODEL_OPENAI = "gpt-image-1"`, `DEFAULT_MODEL_STABILITY = "stable-diffusion-3.5-large"`, `DEFAULT_MODEL_REPLICATE = "black-forest-labs/flux-1.1-pro"`.
  - `scripts/generate_image.py` lines 116-147: `_get_api_key()` function maps all four providers with their respective env vars and key retrieval URLs.
  - `scripts/generate_image.py` lines 168-240: `generate_gemini()` function implementation using `google-genai` package.
  - `scripts/generate_image.py` lines 242-271: `generate_openai()` function implementation using `openai` package.
  - `scripts/generate_image.py` lines 274-296: `generate_stability()` function implementation using `requests` to Stability AI API.
  - `scripts/generate_image.py` lines 314-352: `generate_replicate()` function implementation using `replicate` package with SSRF validation.
  - `scripts/generate_image.py` lines 355-410: `generate_image()` dispatcher routes to the correct provider based on the `provider` argument.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Cross-runtime installer — install.sh/install.ps1 with multi-target support

- **Wiki says:** The skill ships with Unix (`install.sh`) and Windows PowerShell (`install.ps1`) cross-platform installers supporting six CLI hosts: Claude Code, Codex CLI, Cursor, Windsurf, Gemini CLI, and Goose.

- **Source evidence:**
  - `install.sh` lines 14-20: Usage header documents all six targets: `--target=claude`, `--target=codex`, `--target=cursor`, `--target=windsurf`, `--target=gemini`, `--target=goose`.
  - `install.sh` lines 42-86: `resolve_target_paths()` maps all six targets to their respective skill roots, agent directories, and PIP install flags with strict whitelist validation (lines 91-100: `validate_install_path()` rejects shell metacharacters, `..` segments, UNC paths, leading dashes).
  - `install.ps1` lines 1-18: `<#` comment header documents all six targets identically to install.sh: `claude`, `codex`, `cursor`, `windsurf`, `gemini`, `goose`.
  - `README.md` lines 40-41: "Cross-runtime install matrix: `install.sh` / `install.ps1 --target=<host>` with whitelist validation for Claude Code, Codex CLI, Cursor, Windsurf, Gemini CLI, Goose."
  - `README.md` lines 148-175: Full cross-host install documentation with per-host path table.
  - `CLAUDE.md` lines 61-62: "install.sh / install.ps1" and "uninstall.sh / uninstall.ps1" in the architecture listing.
  - Files `install.sh` (314 lines), `install.ps1`, `uninstall.sh`, `uninstall.ps1` all exist in the repo root.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: PDF report generation — scripts/generate_report.py with charts and formatting

- **Wiki says:** The skill includes `scripts/generate_report.py` for professional PDF audit report generation with health score gauge, platform bar charts, pass/fail distribution chart, formatted tables, and zero-overlap layout.

- **Source evidence:**
  - `scripts/generate_report.py` lines 1-14: Docstring describes "Generate professional PDF audit report from markdown audit results" with health score gauge, platform bar charts, pass/fail distribution chart, formatted tables, zero overlap.
  - `scripts/generate_report.py` lines 33-47: Imports `reportlab` library components for PDF construction: `SimpleDocTemplate`, `Paragraph`, `Table`, `HRFlowable`, `Image`, etc.
  - `scripts/generate_report.py` lines 49-55: Imports `matplotlib` with `Agg` backend for chart generation.
  - `scripts/generate_report.py` lines 258-283: `build_gauge_chart()` — generates health score donut gauge chart using Matplotlib.
  - `scripts/generate_report.py` lines 286-322: `build_platform_chart()` — generates horizontal bar chart of platform scores.
  - `scripts/generate_report.py` lines 325-363: `build_result_distribution_chart()` — generates pass/warning/fail donut chart.
  - `scripts/generate_report.py` lines 490-638: `build_pdf()` — complete PDF builder that assembles charts, tables, sections, critical issues, quick wins, and formatting into a `SimpleDocTemplate`.
  - `scripts/generate_report.py` lines 645-692: `check_content()` — quality gate that validates report content completeness before delivery (health score present, no empty tables, no overflow risks).
  - `scripts/generate_report.py` lines 699-752: `main()` — CLI entry point with `--output`, `--brand`, `--check`, `--json` flags.
  - `scripts/generate_report.py` line 31: Version stamped as `1.7.0`.
  - File exists at `scripts/generate_report.py` (752 lines total).

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Test harness — 41-test pytest suite with conftest.py and check-catalog.yaml

- **Wiki says:** The skill includes a 41-test pytest eval harness in `tests/` with routing snapshots, bidirectional 209-check catalog coverage, scoring math determinism, and SSRF regression testing. Shared fixtures in `tests/conftest.py` and canonical catalog in `tests/fixtures/check-catalog.yaml`.

- **Source evidence:**
  - `README.md` line 39: "41-test pytest eval harness in `tests/`".
  - `README.md` lines 435-443: Describes four test categories: Routing snapshots, Check-catalog coverage, Scoring math, SSRF regression.
  - `CLAUDE.md` lines 55-60: Architecture shows `tests/` with `conftest.py`, `fixtures/check-catalog.yaml`, `routing/`, `audit/`, `scripts/`.
  - `tests/conftest.py` (81 lines): Provides session-scoped fixtures `repo_root`, `check_catalog`, `creative_evals`, `skill_descriptions`.
  - `tests/fixtures/check-catalog.yaml` (277 lines): Defines `version: "1.0"`, 209 check IDs across 5 platforms (Google 80, Meta 50, LinkedIn 27, TikTok 28, Microsoft 24), severity multipliers (`critical: 5.0`, `high: 3.0`, `medium: 1.5`, `low: 0.5`), and result point mappings.
  - `tests/conftest.py` lines 30-36: `check_catalog()` fixture loads the YAML catalog.
  - `tests/conftest.py` lines 70-81: `skill_descriptions()` fixture parses frontmatter from all SKILL.md files.
  - `tests/routing/` directory contains `test_creative_routing.py` for trigger→skill snapshot tests.
  - `tests/audit/` directory contains `test_check_coverage.py` and `test_scoring_math.py`.
  - `tests/scripts/` directory contains `test_url_utils.py` for SSRF regression.
  - `tests/audit/__init__.py`, `tests/routing/__init__.py`, `tests/scripts/__init__.py` confirm Python package structure.
  - `tests/fixtures/check-catalog.yaml` lines 1-14: "Canonical catalog of every audit check ID" enforced bidirectionally — no orphan catalog entries and no untracked checks.
  - `tests/fixtures/check-catalog.yaml` lines 265-277: Severity multipliers and result-to-points mapping for scoring math tests.
  - Bash `grep -c "^      - [A-Z]"` on `tests/fixtures/check-catalog.yaml` returns 209 check IDs.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: 10-Principle Thinking Framework

- **Wiki says:** The skill operates under a 10-Principle Thinking Framework: OBSERVE (External + Internal), LISTEN, THINK, CONNECT (Lateral + System), FEEL, ACCEPT, CREATE, GROW. Defined in `ads/references/thinking-framework.md` and loaded at the start of every audit, plan, or creative output.

- **Source evidence:**
  - `ads/references/thinking-framework.md` (291 lines) exists at the documented path.
  - `ads/references/thinking-framework.md` lines 1-13: Title and description — "The shared cognitive discipline that runs underneath every claude-ads command" — and names all 10 principles: "OBSERVE × 2 (looking out and looking in), one LISTEN mode, one THINK mode, two CONNECT modes, one FEEL mode, one ACCEPT mode, one CREATE mode, one GROW mode".
  - `ads/references/thinking-framework.md` lines 20-40: Principle 1 — OBSERVE External: "Thinking begins with data collection. Look at the environment, analyze the landscape."
  - `ads/references/thinking-framework.md` lines 44-64: Principle 2 — OBSERVE Internal: "Observe yourself. Audit how you are thinking. Are you operating on assumptions?"
  - `ads/references/thinking-framework.md` lines 68-90: Principle 3 — LISTEN: "Shut down the ego and absorb external feedback."
  - `ads/references/thinking-framework.md` lines 94-116: Principle 4 — THINK: "Break the problem down to first principles."
  - `ads/references/thinking-framework.md` lines 119-140: Principle 5 — CONNECT Associative: "Take two seemingly unrelated concepts and link them."
  - `ads/references/thinking-framework.md` lines 143-165: Principle 6 — CONNECT System: "How do individual thoughts, tools, and agents plug into one another?"
  - `ads/references/thinking-framework.md` lines 169-192: Principle 7 — FEEL: "Factor in the human element: emotional resonance of messaging."
  - `ads/references/thinking-framework.md` lines 195-218: Principle 8 — ACCEPT: "Embrace constraints, acknowledge when a hypothesis failed."
  - `ads/references/thinking-framework.md` lines 221-241: Principle 9 — CREATE: "At some point you stop strategizing and start producing."
  - `ads/references/thinking-framework.md` lines 245-269: Principle 10 — GROW: "Thinking is not a straight line; it is a feedback loop."
  - `ads/references/thinking-framework.md` lines 276-288: Workflow map table mapping each stage to its dominant principles.
  - `ads/SKILL.md` lines 66-77: References the framework and mandates loading it "Before producing any audit, plan, or creative output."
  - `ads/SKILL.md` line 68: Names the full sequence: "OBSERVE × 2 (External + Internal) → LISTEN → THINK → CONNECT × 2 (Lateral + System) → FEEL → ACCEPT → CREATE → GROW".

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: Quality gates and scoring methodology

- **Wiki says:** The skill enforces 10 hard quality gates during every audit (never recommend Broad Match without Smart Bidding, 3× Kill Rule, budget sufficiency, learning phase protection, compliance, Andromeda creative diversity, privacy infrastructure gate, PDF report quality gate) and uses a weighted scoring algorithm with severity multipliers to produce the Ads Health Score (0-100).

- **Source evidence:**
  - `ads/SKILL.md` lines 125-137: Lists all 10 quality gates verbatim. Gate 1: "Never recommend Broad Match without Smart Bidding (Google)". Gate 2: "3x Kill Rule: flag any ad group/campaign with CPA >3x target for pause". Gate 3: "Budget sufficiency: Meta ≥5x CPA per ad set, TikTok ≥50x CPA per ad group". Gate 4: "Learning phase: never recommend edits during active learning phase". Gate 5: "Compliance: always check Special Ad Categories". Gate 6: "Creative: never run silent video ads on TikTok". Gate 7: "Attribution: default to 7-day click / 1-day view (Meta), data-driven (Google)". Gate 8: "Andromeda creative diversity: Flag Meta accounts with <10 genuinely distinct creatives". Gate 9: "Privacy infrastructure gate: Always verify tracking stack (Consent Mode V2, CAPI, Events API, AdAttributionKit)". Gate 10: "PDF report quality gate".
  - `ads/SKILL.md` lines 210-228: Scoring methodology with Ads Health Score (0-100), per-platform weighted algorithm, cross-platform aggregate weighted by budget share, and grading thresholds (A 90-100, B 75-89, C 60-74, D 40-59, F <40).
  - `tests/fixtures/check-catalog.yaml` lines 265-270: Severity multipliers encoded: `critical: 5.0`, `high: 3.0`, `medium: 1.5`, `low: 0.5`.
  - `tests/fixtures/check-catalog.yaml` lines 272-277: Result-to-points mapping: `pass: 1.0`, `warning: 0.5`, `fail: 0.0`, `na: null`.
  - `README.md` lines 351-362: Grade thresholds documented with descriptions.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[claude-ads]] — Main wiki entry
- [[skills]] — Agent Skills ecosystem
- [[claude-seo]] — Companion SEO analysis skill

## Cross-project

- [[skills.codegraph-verify]] — Skills ecosystem verification
