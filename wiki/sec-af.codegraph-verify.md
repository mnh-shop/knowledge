---
name: sec-af-codegraph-verify
tags: [sec-af, codegraph-verify, agentfield, security, python, fastapi]
description: "Codegraph Verification: SEC-AF — validating wiki claims against indexed source code symbols"
source: sources/sec-af/
---

# Codegraph Verification: SEC-AF

**Date:** 2026-07-12

## Claim 1: Multi-reasoner DAG with 4-phase audit pipeline (Recon → Hunt → Prove → Remediation)
- **Wiki says:** SEC-AF implements a 4-phase audit pipeline: Reconnaissance (architecture/dependency/config scanning), Hunt (strategy-based vulnerability finding), Prove (adversarial verification), and Remediation (fix generation). The pipeline is orchestrated as a multi-reasoner DAG.
- **Source evidence:**
  - `src/sec_af/app.py` lines 119-231 define the `audit` reasoner that calls the 4 phases sequentially via `app.call()`:
    - Line 174-176: `app.call(f"{NODE_ID}.recon_phase", ...)`
    - Line 184-186: `app.call(f"{NODE_ID}.hunt_phase", ...)`
    - Line 194-196: `app.call(f"{NODE_ID}.prove_phase", ...)`
    - Line 210-212: `app.call(f"{NODE_ID}.remediation_phase", ...)`
  - `src/sec_af/reasoners/phases.py` contains the implementation for all 4 phases:
    - `recon_phase()` (line 153) — runs architecture mapper, dependency auditor, config scanner in parallel
    - `hunt_phase()` (line 243) — runs strategy-based vulnerability hunters with AI gate strategy selection
    - `prove_phase()` (line 416) — runs adversarial verification via `run_verifier`
    - `remediation_phase()` (line 529) — generates fixes for confirmed/likely findings
  - `src/sec_af/orchestrator.py` — Orchestrator managing the full pipeline with checkpointing
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Hunt phase with 10+ strategy-based security hunters
- **Wiki says:** The hunt phase runs 10+ strategy-based hunters (injection, auth, crypto, SSRF, XSS, DOS, data exposure, config/secrets, supply chain, API security, business logic) against the target repository.
- **Source evidence:**
  - `src/sec_af/reasoners/phases.py` lines 214-240: `_default_strategies()` returns strategies including `INJECTION`, `DOS`, `SSRF`, `AUTH`, `DATA_EXPOSURE`, `CONFIG_SECRETS`, `XSS`, `CRYPTO`, `SUPPLY_CHAIN`, `API_SECURITY`, `BUSINESS_LOGIC` (11 total)
  - `src/sec_af/agents/hunt/` directory contains hunter agent implementations
  - Hunt strategies are dispatched via `_run_and_enqueue()` (line 289) which calls `run_{strategy_name}_hunter` for each strategy
  - AI gate (`select_strategy`) further refines strategy selection based on recon context
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Prove phase with 4-agent adversarial verification chain
- **Wiki says:** The Prove phase uses a 4-agent adversarial chain (Tracer → Sanitization Analyzer → Exploit Hypothesizer → Verdict Agent) to verify exploitability of findings, with verdicts of `confirmed` / `likely` / `inconclusive` / `not_exploitable`.
- **Source evidence:**
  - `src/sec_af/reasoners/phases.py` lines 416-521: `prove_phase()` prioritizes findings, dispatches them to `run_verifier` via `app.call()`
  - `src/sec_af/agents/prove/verifier.py` — Contains the verifier implementation with 4-agent chain
  - `src/sec_af/agents/prove/` directory exists for prove-agent implementations
  - `src/sec_af/schemas/prove.py` — Defines `Verdict` enum with `confirmed`, `likely`, `inconclusive`, `not_exploitable` values
  - `src/sec_af/schemas/prove.py` — Defines `VerifiedFinding` with evidence_level, data_flow_trace, and proof objects
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: AgentField-based architecture with @app.reasoner() decorators and harness integration
- **Wiki says:** SEC-AF is built on the AgentField platform using `@app.reasoner()` decorators for AI reasoning functions, `app.call()` for cross-reasoner routing, and `app.harness()` for coding agent dispatch. It imports from `agentfield` Python SDK.
- **Source evidence:**
  - `src/sec_af/app.py` line 13: `import agentfield as _agentfield`
  - `src/sec_af/app.py` line 21: `from agentfield import Agent, AIConfig`
  - `src/sec_af/app.py` lines 35-55: `Agent()` instantiated with `harness_config`, `ai_config`, callback URL, and node ID
  - `src/sec_af/app.py` line 119: `@app.reasoner()` decorator on the `audit` reasoner
  - `src/sec_af/harness.py` lines 214-367: `HarnessWrapper` class that wraps `app.harness()` calls with retry logic, schema validation, cost tracking, and phase-guidance prompt construction
  - `src/sec_af/reasoners/__init__.py` — Exports `router` for reasoner registration
  - `pyproject.toml` line 14: Dependency on `"agentfield>=0.1.0"`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: SARIF 2.1.0 native output and compliance framework integration
- **Wiki says:** SEC-AF produces SARIF 2.1.0 native output for GitHub Code Scanning integration, and supports compliance frameworks mapping.
- **Source evidence:**
  - `src/sec_af/schemas/output.py` — Security audit output schema with SARIF-compatible fields
  - `src/sec_af/schemas/compliance.py` — Compliance framework definitions
  - `src/sec_af/compliance/mapping.py` — Compliance framework mapping implementations
  - `src/sec_af/app.py` line 129: `compliance_frameworks` parameter on the `audit` reasoner
  - `src/sec_af/app.py` line 150: `scan_types` parameter defaults to `["sast", "sca", "secrets", "config"]`
  - `src/sec_af/schemas/hunt.py` — Defines CWE IDs per finding for SARIF compliance
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Checkpoint-based execution with resume capability
- **Wiki says:** SEC-AF supports checkpointed execution with the ability to resume from saved checkpoints after interruption, writing checkpoints to `.sec-af/` in the workspace.
- **Source evidence:**
  - `src/sec_af/app.py` line 166: `orchestrator.checkpoint_dir = orchestrator.repo_path / ".sec-af"`
  - `src/sec_af/app.py` lines 168-169: `resume_from_checkpoint` parameter triggers `orchestrator.run_from_checkpoint()`
  - `src/sec_af/app.py` line 182: `orchestrator._write_checkpoint("recon", recon)` — writes checkpoint after recon
  - `src/sec_af/app.py` line 192: `orchestrator._write_checkpoint("hunt", hunt)` — writes checkpoint after hunt
  - `src/sec_af/app.py` line 203: `orchestrator._write_checkpoint("prove", verified)` — writes checkpoint after prove
  - `src/sec_af/orchestrator.py` — Orchestrator manages checkpoint lifecycle
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 6 key claims from the SEC-AF wiki have been verified against the source code via codegraph exploration:
- ✅ 4-phase audit pipeline: Recon → Hunt → Prove → Remediation phases confirmed in `phases.py` with parallel dispatch
- ✅ 10+ strategy hunters: 11 strategy types confirmed in `_default_strategies()` with AI gate strategy selection
- ✅ 4-agent adversarial verification: Prove phase with verdict types confirmed in `phases.py` and `schemas/prove.py`
- ✅ AgentField integration: `@app.reasoner()`, `app.harness()`, `app.call()` usage confirmed across codebase
- ✅ SARIF/compliance: Output schemas and compliance mapping modules confirmed
- ✅ Checkpoint execution: Resume capability with `.sec-af/` checkpoint files confirmed

## Related

- [[sec-af]] -- Main wiki entry
- [[agentfield]] -- Core AgentField platform
- [[swe-af]] -- Sibling autonomous engineering factory

## Cross-project

- [[swe-af.codegraph-verify]] -- Companion verification for SWE-AF
- [[af-deep-research.codegraph-verify]] -- Companion verification for AF Deep Research
- [[agentfield.codegraph-verify]] -- Similar codegraph verification for AgentField
