---
name: pr-af-codegraph-verify
tags: [pr-af, code-review, martian-bench, agentfield, python, ai, scoring, wiki]
description: "Codegraph Verification: pr-af — validating wiki claims against indexed source code symbols"
source: sources/pr-af/
---

# Codegraph Verification: pr-af

**Date:** 2026-07-30

## Claim 1: #1 open-source code reviewer on Martian Code-Review-Bench
- **Wiki says:** PR-AF is the #1 open-source code reviewer on the Martian Code-Review-Bench, with 0.706 golden recall across 42 compared tools.
- **Source evidence:**
  - `README.md` line 23 states: "PR-AF is the **#1 open-source code reviewer on Martian Code-Review-Bench**"
  - `README.md` line 36-37 states: "PR-AF with GLM-5.2 is the #1 open-source reviewer in golden recall: 0.706 across 42 compared tools"
  - `README.md` line 45 confirms: "0.706 golden recall — #1 open source across 42 compared tools"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Built on AgentField framework
- **Wiki says:** PR-AF is built on the AgentField framework for agentic orchestration.
- **Source evidence:**
  - `README.md` line 5 states: "### Open-Source Agentic Code Review Built on [AgentField](https://github.com/Agent-Field/agentfield)"
  - `README.md` line 9 shows the AgentField badge
  - The project uses decorator-based reasoner patterns consistent with AgentField architecture
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: 7-phase review pipeline via ReviewOrchestrator
- **Wiki says:** PR-AF uses a 7-phase review pipeline coordinated by a ReviewOrchestrator.
- **Source evidence:**
  - `src/pr_af/orchestrator.py` lines 1-7 document: "Coordinates the 7-phase review pipeline. Manages budget, streaming queues, and phase transitions."
  - `src/pr_af/orchestrator.py` imports evidence, scoring, reasoner harnesses, and HITL modules
  - The orchestration controls intake, anatomy, coverage, evidence, adversary, compound, and dedup phases
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Deterministic scoring engine separated from LLM agents
- **Wiki says:** Scoring is intentionally separated from LLM agents so it can be modified without touching agent code.
- **Source evidence:**
  - `src/pr_af/scoring.py` lines 1-7 document: "Deterministic scoring engine for PR-AF. LLMs reason about issues; this code computes scores. Same findings always produce same scores. Auditable, testable, tunable."
  - `src/pr_af/scoring.py` line 6-7 states: "Follows the Contract-AF / SEC-AF pattern: scoring is intentionally separated from agents so it can be modified without touching agent code."
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: File-read cache eliminating redundant disk reads
- **Wiki says:** A shared file-read cache eliminates redundant disk reads, shared across meta-selectors, reviewers, evidence extract/verify, adversary, compound, and consistency phases.
- **Source evidence:**
  - `src/pr_af/evidence.py` line 15-19 implement `_FILE_CACHE` with comment: "Shared file-read cache: the same files are read 8+ times per review"
  - `src/pr_af/evidence.py` line 19: `_FILE_CACHE: dict[tuple[str, float], list[str]] = {}` keyed by (abspath, mtime)
  - `src/pr_af/evidence.py` line 22 defines `_read_file_lines()` which uses the cache
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Model-flexible supporting GLM-5.2/DeepSeek/Opus
- **Wiki says:** PR-AF supports multiple model tiers: cheaper models for routine PRs, GLM-5.2 for open-model CI gates, and Opus-class frontier models for highest-stakes reviews.
- **Source evidence:**
  - `README.md` line 48 states: "**Model-flexible** | Use cheaper models for regular PRs, GLM-5.2 for open-model CI gates, and Opus-class frontier models for highest-stakes reviews"
  - `README.md` line 27-28 also mentions: "DeepSeek-class models for routine PRs, GLM-5.2 for deep open-model reviews, or Opus-class frontier models for major PRs"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Human-in-the-loop approval with webhook integration
- **Wiki says:** PR-AF supports human-in-the-loop approval via webhook integration before final review submission.
- **Source evidence:**
  - `src/pr_af/orchestrator.py` line 25 imports: `from .hitl import (approval_webhook_url, build_hax_client_from_env, request_review_approval)`
  - `src/pr_af/orchestrator.py` lines 26-28 confirm HITL webhook infrastructure
  - The hitl module provides `request_review_approval` for human approval gates
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: Origin org, Apache 2.0 license, and GH_TOKEN env var
- **Wiki says:** Origin is `Agent-Field/pr-af`, license is Apache 2.0, and the GitHub env var is `GH_TOKEN` (a personal access token with `repo` scope).
- **Source evidence:**
  - `README.md` line 198: `af install https://github.com/Agent-Field/pr-af`; line 231: `git clone https://github.com/Agent-Field/pr-af.git`; line 292: checkout `repository: Agent-Field/pr-af` in the workflow
  - `README.md` line 7 shows the Apache 2.0 badge; `pyproject.toml` line 10 declares `license = "Apache-2.0"`
  - `README.md` lines 216-217 and 256-257 document `GH_TOKEN` ("GitHub personal access token with `repo` scope"); `.env.example` uses the same name; git remote confirms `https://github.com/Agent-Field/pr-af.git`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 8 key claims from the pr-af wiki have been verified against the source code:
- ✅ #1 on Martian Code-Review-Bench: Benchmark position confirmed in README
- ✅ AgentField framework: Attribution confirmed in README
- ✅ 7-phase pipeline: ReviewOrchestrator with phase orchestration confirmed
- ✅ Deterministic scoring: Scoring engine separated from agents confirmed
- ✅ File-read cache: Shared cache eliminating redundant disk reads confirmed
- ✅ Model-flexible: Multi-tier model support (DeepSeek/GLM-5.2/Opus) confirmed
- ✅ Human-in-the-loop: Webhook-based approval system confirmed
- ✅ Origin/license/env: Agent-Field org, Apache 2.0, and GH_TOKEN confirmed

## Related

- [[pr-af]] -- Main wiki entry

## Cross-project

- [[agentfield.codegraph-verify]] -- Similar codegraph verification for AgentField
- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for Hermes Agent
