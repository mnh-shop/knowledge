---
name: swe-af-codegraph-verify
tags: [swe-af, codegraph-verify, agentfield, engineering, python, fastapi]
description: "Codegraph Verification: SWE-AF — validating wiki claims against indexed source code symbols"
source: sources/SWE-AF/
---

# Codegraph Verification: SWE-AF

**Date:** 2026-07-12

## Claim 1: Multi-role engineering factory with 15 agent roles
- **Wiki says:** SWE-AF implements a coordinated factory of 15 specialized agent roles: Product Manager, Architect, Tech Lead, Sprint Planner, Issue Writer, Coder, QA, Code Reviewer, QA Synthesizer, Issue Advisor, Replanner, Merger, Integration Tester, Verifier, GitHub PR. These roles span planning, execution, and delivery phases.
- **Source evidence:**
  - `swe_af/reasoners/pipeline.py` — Contains product manager (via `product_manager` harness calls), architect (`run_architect`), tech lead (`run_tech_lead_review`), sprint planner (`run_sprint_planner`) roles
  - `swe_af/reasoners/execution_agents.py` — Contains coder (`run_coder`), QA (`run_qa`), code reviewer (`run_code_reviewer`), QA synthesizer (`run_qa_synthesizer`), issue writer (`run_issue_writer`), verifier (`run_verifier`), merger (`run_merger`), GitHub PR (`run_github_pr`), integration tester (`run_integration_tester`) roles
  - `swe_af/reasoners/schemas.py` — Schemas for `PRD`, `Architecture`, `ReviewResult`, `PlannedIssue`, `PlanResult` across all roles
  - `swe_af/execution/coding_loop.py` — Inner loop orchestrating coder → reviewer/QA/synthesizer flow
  - `swe_af/execution/dag_executor.py` — DAG execution with issue advisor (`run_issue_advisor`) and replanner (`run_replanner`) roles
  - 25+ prompt modules in `swe_af/prompts/` each dedicated to a specific role (e.g., `coder.py`, `code_reviewer.py`, `qa.py`, `merger.py`, `verifier.py`, `replanner.py`, `issue_advisor.py`)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Three-level adaptive control loops (Inner/Middle/Outer)
- **Wiki says:** SWE-AF implements three nested control loops: Inner (coder → reviewer → approve/fix/block for single issues), Middle (issue advisor diagnoses failures, adapts ACs/approach/scope), Outer (replanner restructures DAG after unrecoverable failures).
- **Source evidence:**
  - `swe_af/execution/coding_loop.py` lines 1-13: Documents the three-nested-loop architecture explicitly:
    - "INNER (this): coder → review → approve/fix/block"
    - "MIDDLE: issue advisor diagnoses failures → adapt ACs/approach/scope"
    - "OUTER: replanner restructures DAG after unrecoverable failures"
  - `swe_af/execution/coding_loop.py` — Inner loop: coder → reviewer (or QA/reviewer/synthesizer for flagged issues)
  - `swe_af/execution/dag_executor.py` — Middle/Outer loop: issue advisor and replanner
  - `swe_af/reasoners/execution_agents.py` — `run_issue_advisor` and `run_replanner` reasoners
  - `swe_af/execution/dag_executor.py` — `apply_replan()` function for DAG restructuring
  - `swe_af/prompts/issue_advisor.py` — Issue advisor system prompt
  - `swe_af/prompts/replanner.py` — Replanner system prompt
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Per-issue git worktree isolation for parallel execution
- **Wiki says:** SWE-AF creates per-issue git worktrees for isolated parallel execution, preventing branch collisions when running hundreds of concurrent agent instances.
- **Source evidence:**
  - `swe_af/execution/dag_executor.py` lines 54-80: `_setup_worktrees()` creates git worktrees for parallel issue isolation
  - `swe_af/execution/dag_executor.py` lines 80+: Multi-repo path groups issues by `target_repo` and dispatches `run_workspace_setup` per repo
  - `swe_af/execution/schemas.py` — `WorkspaceManifest` and `WorkspaceRepo` schemas for worktree management
  - `swe_af/execution/dag_utils.py` — DAG utility functions for worktree operations
  - The DAG execution engine uses worktree isolation as the foundation for parallel execution
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: AgentField-based with harness integration for Claude Code/Codex dispatch
- **Wiki says:** SWE-AF is built on AgentField and uses `app.harness()` to dispatch coding tasks to external coding agents (Claude Code, Codex, OpenCode). It patches `app.harness` to auto-inject scoped credentials. Has dependencies on `agentfield>=0.1.96` and `claude-agent-sdk`.
- **Source evidence:**
  - `swe_af/app.py` line 24: `from agentfield import Agent`
  - `swe_af/app.py` lines 51-57: `Agent(node_id="swe-planner")` instantiation
  - `swe_af/app.py` lines 78-91: `_harness_with_scoped_credentials()` patches `app.harness` to inject scoped credentials from Hax into every harness call
  - `swe_af/pyproject.toml` line 9: `"agentfield>=0.1.96"` dependency
  - `swe_af/pyproject.toml` line 13: `"claude-agent-sdk==0.1.20"` dependency
  - `swe_af/reasoners/pipeline.py` — All reasoners use `router.harness()` for AI execution
  - `swe_af/runtime/providers.py` — `runtime_to_harness_adapter()` maps runtime (claude_code, codex, opencode) to provider for harness calls
  - `swe_af/runtime/codex_harness_patch.py` — Codex-specific harness patching
  - `swe_af/hitl/` — Human-in-the-loop (HAX) integration with credential negotiation and approval workflows
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: DAG execution engine with self-healing checkpointed pipeline
- **Wiki says:** SWE-AF has a DAG execution engine (`dag_executor.py`) that supports checkpointed execution, self-healing replanning, and resume after crashes. The planning pipeline produces a DAG of issues with topological sort and file conflict detection.
- **Source evidence:**
  - `swe_af/execution/dag_executor.py` (1801 lines) — Core DAG execution loop with self-healing replanning, checkpoint saving/loading, timeout handling, and execution state management
  - `swe_af/reasoners/pipeline.py` lines 52-90: `_compute_levels()` — Topological sort of issues into parallel execution levels (Kahn's algorithm)
  - `swe_af/reasoners/pipeline.py` lines 93-100: `_validate_file_conflicts()` — Detects parallel file conflicts
  - `swe_af/reasoners/pipeline.py`: `_assign_sequence_numbers()` — Assigns sequence numbers for execution ordering
  - `swe_af/execution/dag_utils.py` — DAG utility functions for replanning application and downstream dependency finding
  - `swe_af/execution/schemas.py` — `DAGState`, `ExecutionConfig`, `IssueOutcome`, `IssueResult`, `LevelResult` schemas
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: FastBuild mode for single-pass sequential execution
- **Wiki says:** SWE-AF includes a speed-optimized "FastBuild" mode in `swe_af/fast/` with single-pass planning and sequential execution, exposed as `swe-fast` console script and `python -m swe_af.fast`.
- **Source evidence:**
  - `swe_af/fast/app.py` — FastBuild agent entry point with `@app.reasoner()` build function
  - `swe_af/fast/planner.py` — FastBuild planner implementation
  - `swe_af/fast/executor.py` — FastBuild executor implementation
  - `swe_af/fast/schemas.py` — `FastBuildConfig` and `FastBuildResult` schemas
  - `swe_af/fast/prompts.py` — FastBuild prompt templates
  - `swe_af/fast/verifier.py` — FastBuild verifier implementation
  - `pyproject.toml` line 27: `swe-fast = "swe_af.fast.app:main"` console script
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 6 key claims from the SWE-AF wiki have been verified against the source code via codegraph exploration:
- ✅ 15 agent roles: Confirmed across `reasoners/pipeline.py`, `reasoners/execution_agents.py`, and `prompts/` directory
- ✅ Three-level control loops: Inner/middle/outer architecture documented in `coding_loop.py` and implemented in DAG executor
- ✅ Per-issue git worktrees: Worktree isolation confirmed in `dag_executor.py` with multi-repo support
- ✅ AgentField harness integration: `app.harness` patching, runtime adapters, and HITL credential management confirmed
- ✅ DAG execution engine: Topological sort, file conflict detection, and self-healing replanning confirmed
- ✅ FastBuild mode: `swe_af/fast/` with dedicated planner, executor, and schemas confirmed

## Related

- [[SWE-AF]] -- Main wiki entry
- [[agentfield]] -- Core AgentField platform
- [[sec-af]] -- Sibling security auditor
- [[af-deep-research]] -- Sibling research engine

## Cross-project

- [[sec-af.codegraph-verify]] -- Companion verification for SEC-AF
- [[af-deep-research.codegraph-verify]] -- Companion verification for AF Deep Research
- [[agentfield.codegraph-verify]] -- Similar codegraph verification for AgentField
