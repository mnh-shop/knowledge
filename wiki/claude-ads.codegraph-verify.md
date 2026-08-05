---
name: claude-ads-codegraph-verify
tags: [codegraph-verify, claude-ads, agent-skills, advertising, paid-media, ppc]
description: "Codegraph Verification: claude-ads v2.0.1 — Paid Advertising Audit & Optimization Skill"
source: sources/claude-ads/
date: 2026-07-30
---

# Codegraph Verification: claude-ads

**Date:** 2026-07-30
**Verified version:** v2.0.1 (git `669c760`, CHANGELOG [2.0.1]-2026-07-13)
**Supersedes:** the 2026-07-12 verification page, which reflected v1.7.1 counts.

## Claim 1: Version — v2.0.1

- **Wiki says:** The skill is at version v2.0.1 (pyproject.toml carries `2.0.0`, plugin manifest carries `2.0.1`).

- **Source evidence:**
  - Git log: `669c760 release: v2.0.1 - public mirror release` (HEAD of `sources/claude-ads`).
  - `CHANGELOG.md` line 8: `## [2.0.1] - 2026-07-13` and line 33: `## [2.0.0] - 2026-07-12` (with `[1.8.1]` at line 112, confirming 2.0.x supersedes 1.x).
  - `pyproject.toml` line 7: `version = "2.0.0"` (packaging version tracks the 2.0.x line).
  - `.claude-plugin/plugin.json` line 3: `"version": "2.0.1"` with the 12-platform description at line 4.
  - CHANGELOG 2.0.1 entry (lines 9-31) documents the public mirror release: README/SUPPORT/SECURITY/CONTRIBUTING links, installer default clone source, PDF footer, and dual-distribution note.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None (was `v1.7.1` — corrected).

## Claim 2: Platform surface — 12 platforms (was 8)

- **Wiki says:** The skill covers twelve ad platforms: Google, Meta, YouTube, LinkedIn, TikTok, Microsoft, Apple, Amazon, Reddit, Pinterest, Snapchat, and X.

- **Source evidence:**
  - `README.md` lines 44-46 (platform-coverage table): "Search, video, and social — Google Ads, Meta Ads, YouTube Ads, LinkedIn Ads, TikTok Ads, Microsoft Advertising, Reddit Ads, Snapchat Ads, X Ads" and "Commerce and retail media — Apple Ads, Amazon Ads, Pinterest Ads".
  - `CHANGELOG.md` line 37 (2.0.0 Added): "First-class platform contracts for Reddit, Pinterest, Snapchat, and X, bringing the platform surface to twelve dedicated skills, references, audit workers, and catalog entries."
  - `skills/` directory contains platform sub-skills for all twelve: `ads-google`, `ads-meta`, `ads-youtube`, `ads-linkedin`, `ads-tiktok`, `ads-microsoft`, `ads-apple`, `ads-amazon`, `ads-reddit`, `ads-pinterest`, `ads-snapchat`, `ads-x`.
  - `claude_ads_core/workflow_contracts.py` lines 13-15: `PLATFORMS = {"google", "meta", "youtube", "linkedin", "tiktok", "microsoft", "apple", "amazon", "reddit", "pinterest", "snapchat", "x"}`.
  - `control-plane/manifests/capability-manifest.json`: platform blocks for all twelve (e.g. `"id": "google"` with `"target_tier": "first-class"`).
  - `tests/fixtures/check-catalog.yaml` lines 21-499: twelve platform blocks (`google` through `x`).

- **Verdict:** ✅ CORRECT
- **Fix needed:** None (was "8 platforms" — corrected).

## Claim 3: Composition — 33 sub-skills + 25 agents + 38 RAG references (was 22/10/26)

- **Wiki says:** The skill comprises 33 specialized sub-skills, 25 agents, 12 industry templates, and 38 RAG reference files.

- **Source evidence:**
  - Directory listing of `skills/` shows exactly **33** entries: the original 22 (`ads-audit` … `ads-photoshoot`) plus 11 new v2.0 skills — `ads-launch`, `ads-monitor`, `ads-optimize`, `ads-pinterest`, `ads-reddit`, `ads-report`, `ads-research`, `ads-setup`, `ads-snapchat`, `ads-validate`, `ads-x`.
  - Directory listing of `agents/` shows exactly **25** files: 17 audit agents (`audit-google`, `audit-meta`, `audit-youtube`, `audit-linkedin`, `audit-tiktok`, `audit-microsoft`, `audit-apple`, `audit-amazon`, `audit-reddit`, `audit-pinterest`, `audit-snapchat`, `audit-x`, `audit-creative`, `audit-tracking`, `audit-budget`, `audit-policy-compliance`, `audit-regulatory-compliance`), 4 creative (`creative-strategist`, `visual-designer`, `copy-writer`, `format-adapter`), and 4 verifier/research (`source-verifier`, `research-worker`, `skill-reviewer`, `release-verifier`).
  - Directory listing of `ads/references/` shows exactly **38** `.md` files — the 26 v1.x files plus `amazon-audit.md`, `apple-audit.md`, `automation-tier-classifier.md`, `compliance-requirements.md`, `creative-source-registry.md`, `meta-ai-stack.md`, `pinterest-audit.md`, `prompt-patterns.md`, `reddit-audit.md`, `snapchat-audit.md`, `status-contract.md`, `x-audit.md`, `youtube-audit.md`.
  - Directory listing of `skills/ads-plan/assets/` confirms exactly 12 industry template files (`saas.md`, `ecommerce.md`, `local-service.md`, `b2b-enterprise.md`, `info-products.md`, `mobile-app.md`, `real-estate.md`, `healthcare.md`, `finance.md`, `agency.md`, `marketplace-seller.md`, `generic.md`).
  - `README.md` line 228: `agents/` described as "platform, cross-platform, research, and verifier workers".

- **Verdict:** ✅ CORRECT
- **Fix needed:** None (was "22 sub-skills / 10 agents / 26 references" — corrected).

## Claim 4: Check catalog — version 2.0, 412 check IDs across 12 platforms (was 209)

- **Wiki says:** The canonical catalog (`tests/fixtures/check-catalog.yaml`) is version "2.0" with 412 check IDs across 12 platform blocks (Google 95, Meta 72, LinkedIn 46, TikTok 46, Microsoft 41, and 16 each for YouTube/Apple/Amazon/Reddit/Pinterest/Snapchat/X).

- **Source evidence:**
  - `tests/fixtures/check-catalog.yaml` line 17: `version: "2.0"`; line 18: `last_updated: "2026-07-11"`.
  - Platform blocks at lines 21 (`google:`), 124 (`meta:`), 204 (`linkedin:`), 258 (`tiktok:`), 312 (`microsoft:`), 361 (`youtube:`), 384 (`apple:`), 407 (`amazon:`), 430 (`reddit:`), 453 (`pinterest:`), 476 (`snapchat:`), 499 (`x:`).
  - Check-ID counts per block (verified with `awk` on `^\s+- [A-Z]`): google 95, meta 72, linkedin 46, tiktok 46, microsoft 41, and 16 each for the remaining seven platforms = **412 total** (grep count confirms 412).
  - `CLAUDE.md` lines 1-9 header comment: "Canonical catalog of every audit check ID across all platforms" with the bidirectional no-orphan/no-untracked enforcement rule.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None (was "209 check IDs / 5 platforms" — corrected).

## Claim 5: Severity multipliers — 5.0 / 3.0 / 1.0 / 0.0 (was 5.0/3.0/1.5/0.5)

- **Wiki says:** Scoring uses severity multipliers critical 5.0×, high 3.0×, medium 1.0×, informational 0.0×.

- **Source evidence:**
  - `tests/fixtures/check-catalog.yaml` lines 524-528: `critical: 5.0`, `high: 3.0`, `medium: 1.0`, `informational: 0.0`.
  - `ads/references/scoring-system.md` lines 28-38: "## Severity weights" table — critical 5 ("Immediate material revenue, data, account, privacy, or policy risk"), high 3, medium 1, informational 0 ("Context or unscored opportunity"). Note the v2.0 severity taxonomy replaced v1.x's low/0.5 with `informational/0`.
  - `ads/references/scoring-system.md` line 33 onwards: "Severity represents impact if the control fails. It must not be inflated because a feature is new or strategically interesting."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None (was "5.0/3.0/1.5/0.5" — corrected).

## Claim 6: Test harness — 315 test functions (was 41)

- **Wiki says:** The eval harness comprises 315 test functions across routing, audit, core, references, release, and scripts areas.

- **Source evidence:**
  - `grep -rc '^def test_\|^    def test_'` over all `tests/**/*.py` files sums to **315** test functions.
  - `tests/` directory gained three new areas in v2.0 beyond v1.x's `routing/`, `audit/`, `scripts/`: `tests/core/` (14 files: `test_adapters.py`, `test_cli.py`, `test_contracts.py`, `test_control_registry.py`, `test_data_lifecycle_policy.py`, `test_native_exports.py`, `test_platform_report_contracts.py`, `test_product_status.py`, `test_reporting.py`, `test_scoring_engine.py`, `test_workflow_contracts.py`), `tests/references/` (`test_cross_platform_references.py`), `tests/release/` (`test_release.py`, `test_repository_review_release_gate.py`, `test_review_contracts.py`, `test_target_lock_verifier.py`).
  - `tests/routing/` expanded with `test_behavior_eval_contract.py`, `test_canonical_behavior_surfaces.py`, `test_forward_eval_summary.py`, `test_model_eval_gate.py`, `test_platform_workflow_routing.py`.
  - `tests/scripts/` expanded with `test_generate_image_provider_selection.py`, `test_installer_security.py`, `test_privacy_outputs.py`.
  - `tests/conftest.py` provides shared fixtures (`repo_root`, `check_catalog`, `creative_evals`, `skill_descriptions`).

- **Verdict:** ✅ CORRECT
- **Fix needed:** None (was "41-test" — corrected).

## Claim 7: Control plane + deterministic Python core (v2.0 addition)

- **Wiki says:** v2.0 added a control plane (`control-plane/`) with product/capability/safety/data-lifecycle manifests, claim ledger and review policy, plus a deterministic Python package (`claude_ads_core/`) implementing a conductor→bounded-worker model.

- **Source evidence:**
  - `control-plane/README.md` line 3: "This directory is the public-safe contract layer for Claude Ads v2" — "It records what the product is allowed to claim, what it can actually do, which evidence supports it, how work is coordinated, and what must pass before release."
  - `control-plane/manifests/` contains `capability-manifest.json`, `safety-policy.json`, `data-lifecycle-policy.json`, `product-manifest.json`, `claim-ledger.json`, `control-registry.json`, `scoring-profiles.json`, `orchestration-policy.json`, `review-policy.json`, `source-ledger.json`, `repository-review-ledger.json`, `maturity-status.json`, plus dependency/ecosystem/runtime manifests.
  - `control-plane/manifests/capability-manifest.json`: `"default_mutation_mode": "read-only"`; per-platform capabilities with `mode` (`export-read`/`live-write`) and `status` (`implemented`/`fixture-verified`/`disabled`), e.g. `"account-mutation"` is `"disabled"` with `"No approved v2 write adapter lifecycle."`
  - `claude_ads_core/orchestration.py` line 1: "Immutable file-backed orchestration packets and artifact-only gates."
  - `claude_ads_core/workflow_contracts.py` lines 8-10: "Strict dependency-free validators for workflow and orchestration artifacts. These validators intentionally check structural truth only."
  - `CLAUDE.md` line 13: "`agents/`: bounded workers that return results to the conductor."
  - `ads/SKILL.md` lines 127-130: "Use one conductor and bounded workers. Fan out platform slices, source checks, … and final acceptance in the conductor context."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None (new claim added).

## Claim 8: Dual-home distribution + model eval gate (v2.0.1 addition)

- **Wiki says:** The skill ships from two homes — public `AgriciDaniel/claude-ads` and `AI-Marketing-Hub/claude-ads` mirror — and includes a fail-closed model evaluation gate in `evals/`.

- **Source evidence:**
  - `README.md` lines 15-21: "Claude Ads ships from two homes: the **public release** at `AgriciDaniel/claude-ads` (MIT, no membership required) and the **community mirror** at `AI-Marketing-Hub/claude-ads`" (AI Marketing Hub Pro members get early access).
  - `CHANGELOG.md` 2.0.1 entry (lines 9-13): "**Public release surface**: user-facing repository links in the README install paths, SUPPORT.md, SECURITY.md, CODE_OF_CONDUCT.md, CONTRIBUTING.md, the issue templates, CITATION.cff, and the plugin and marketplace manifests now point to the public repository."
  - `evals/v2-behavior-evals.json`: behavior eval entries with `risk` (`P0`/`P1`), `expected_skill`, `required_behaviors`, `forbidden_behaviors` (e.g. `safety-pause-missing`, `safety-export-injection`, `privacy-report`, `install-curl`).
  - `evals/model_eval_gate.py` lines 3-10: "This tool never invokes a model and never manufactures model-run evidence. The `plan` command emits immutable task packets for an external Claude Code runner. The `assess` command consumes two independently evaluated, private run artifacts and emits only a deterministic, machine-readable gate summary."
  - `evals/model-eval-contract.json` exists alongside `v2-behavior-evals.json`, `creative-evals.json`, and `evals/schemas/`.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None (new claim added).

## Stable claims re-verified (unchanged from v1.7.1)

- **10-Principle Thinking Framework** — `ads/references/thinking-framework.md` (291 lines) defines OBSERVE×2 / LISTEN / THINK / CONNECT×2 / FEEL / ACCEPT / CREATE / GROW; `ads/SKILL.md` lines 66-77 mandates loading it before producing any audit, plan, or creative output.
- **12 industry templates** — `skills/ads-plan/assets/` contains exactly 12 template files.
- **6-host cross-runtime installer** — `install.sh` lines 14-20 document `--target=claude|codex|cursor|windsurf|gemini|goose`; `install.ps1` header mirrors it; `README.md` lines 112-113 show `--target=codex` / `--target=gemini` usage.
- **PDF report generation** — `scripts/generate_report.py` (752 lines) with `build_gauge_chart()` (lines 258-283), `build_platform_chart()` (286-322), `build_result_distribution_chart()` (325-363), `build_pdf()` (490-638), `check_content()` quality gate (645-692).
- **Image generation** — `scripts/generate_image.py` with `DEFAULT_PROVIDER = "gemini"`, `DEFAULT_MODEL_GEMINI = "gemini-2.5-flash-image"`, `DEFAULT_MODEL_OPENAI = "gpt-image-1"`, `DEFAULT_MODEL_STABILITY = "stable-diffusion-3.5-large"`, `DEFAULT_MODEL_REPLICATE = "black-forest-labs/flux-1.1-pro"` (lines 75-79).
- **SSRF protection** — `scripts/url_utils.py` validated by `tests/scripts/test_url_utils.py` (IPv4/IPv6 blocklist, non-HTTP scheme blocks, DNS fail-closed).

## Related

- [[claude-ads]] — Main wiki entry
- [[skills]] — Agent Skills ecosystem
- [[claude-seo]] — Companion SEO analysis skill

## Cross-project

- [[skills.codegraph-verify]] — Skills ecosystem verification
