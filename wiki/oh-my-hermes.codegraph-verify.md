---
name: oh-my-hermes-codegraph-verify
tags: [hermes-agent, multi-agent, orchestration, planning, plugin, plugin-sdk, python, oh-my-hermes, wiki]
description: "Codegraph Verification: oh-my-hermes — validating wiki claims against indexed source code symbols"
source: sources/oh-my-hermes/
---

# Codegraph Verification: oh-my-hermes

**Date:** 2026-07-12

## Claim 1: OMH plugin system with hook-based role injection
- **Wiki says:** OMH provides a Hermes plugin at `plugins/omh/` with hook-based components: `pre_llm_call` hook (detects `[omh-role:NAME]` markers, injects role prompt), `pre_tool_call` hook (validates role markers in delegation goals), `on_session_end` hook (writes interrupted state on crash). Also includes `omh_state` tool (13 actions) and `omh_gather_evidence` tool.
- **Source evidence:**
  - `plugins/omh/` directory exists with plugin implementation
  - Plugin hooks: `pre_llm_call` hook injects role prompts based on `[omh-role:NAME]` markers
  - `pre_tool_call` hook validates role markers in `delegate_task` goals
  - `on_session_end` hook writes `_interrupted_at` on unexpected exit
  - `omh_state` tool provides 13 atomic actions: read/write/clear/check/cancel/lock/unlock + `load_role`
  - `omh_gather_evidence` tool runs build/test/lint commands from allowlist
  - Plugin installs to `~/.hermes/plugins/omh/` and requires Python 3.10+ and `pyyaml`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: 15 shared role prompts with specific behavioral instructions
- **Wiki says:** Fifteen shared role prompts give subagents precise behavioral instructions: Planner, Architect, Critic, Executor, Verifier, Analyst, Security Reviewer, Test Engineer, Code Reviewer, Debugger, Triage Maintainer, Triage Skeptic, Researcher, Research Synthesist, Research Verifier. Each has a defined purpose and skill assignment.
- **Source evidence:**
  - Role definition files exist in the plugin for each listed role
  - Role prompts include specific behavioral instructions per role
  - Roles are organized by skill (ralplan uses Planner/Architect/Critic, ralph uses Executor/Verifier, etc.)
  - Role injection uses `[omh-role:NAME]` markers in `delegate_task` goal strings
  - The `pre_llm_call` hook detects markers and injects matching role file into subagent's system prompt
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: 10 composable skills with defined composition pipeline
- **Wiki says:** OMH provides 10 skills: omh-deep-research, omh-ralplan, omh-ralplan-driver, omh-deep-interview, omh-ralph, omh-ralph-driver, omh-ralph-task, omh-triage (v0.1), omh-triage-driver (v0.1), and omh-autopilot. They compose into a pipeline: deep-interview → ralplan → autopilot → ralph.
- **Source evidence:**
  - `skills/` directory contains per-skill subdirectories
  - `skills/omh-deep-research/` implements multi-phase web research
  - `skills/omh-ralplan/` implements consensus planning with Planner → Architect → Critic
  - `skills/omh-ralplan-driver/` implements dispatcher's playbook
  - `skills/omh-deep-interview/` implements Socratic requirements interview
  - `skills/omh-ralph/` implements verified execution cycle
  - `skills/omh-ralph-driver/` and `skills/omh-ralph-task/` provide execution support
  - `skills/omh-triage/` and `skills/omh-triage-driver/` (v0.1) for issue triage
  - `skills/omh-autopilot/` composes all three phases end-to-end
  - Skills work standalone with zero dependencies (no plugin required)
  - Skills can be installed via `hermes skills tap add witt3rd/oh-my-hermes` and `hermes skills install <name>`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: State convention with `.omh/` directory
- **Wiki says:** State and artifacts live in `.omh/` within the project directory with subdirectories: `state/` (per-session, not tracked), `logs/` (per-session, not tracked), `progress/` (per-session, not tracked), `specs/` (durable, tracked), `plans/` (durable, tracked), `research/` (durable, tracked).
- **Source evidence:**
  - State management uses `.omh/` directory convention for all skill artifacts
  - `state/` contains active mode state JSON, atomically written by `omh_state`
  - `logs/` contains append-only event logs
  - `progress/` contains ralph execution progress logs
  - `specs/` contains confirmed interview specs (durable, git-tracked)
  - `plans/` contains consensus plans from ralplan (ADR-shaped, durable)
  - `research/` contains research reports from omh-deep-research (durable)
  - The `omh_delegate` wrapper uses `.omh/state/dispatched/` for breadcrumbs
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: `omh_delegate` wrapper with prepare/finalize split
- **Wiki says:** The `omh_delegate.py` at `plugins/omh/omh_delegate.py` implements a prepare/finalize split pattern: `prepare()` computes paths, writes dispatched breadcrumb, injects contract; `finalize()` verifies file present, writes completion breadcrumb.
- **Source evidence:**
  - `plugins/omh/omh_delegate.py` exists with the `omh_delegate` module
  - `prepare()` method computes artifact paths, writes `.dispatched.json` breadcrumb, injects contract
  - `finalize()` method verifies artifact file exists, writes `.completed.json` breadcrumb
  - Artifacts land at `.omh/research/{mode}/{phase}[-r{round}][-{slug}]-{ts}.md`
  - Breadcrumbs land at `.omh/state/dispatched/{id}.dispatched.json` and `.omh/state/dispatched/{id}.completed.json`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: `omh_gather_evidence` tool with safety rails
- **Wiki says:** The `omh_gather_evidence` tool runs build/test/lint commands from a configured allowlist with token-level allowlist check, shell metacharacter rejection, output truncation (default 2000 chars, max 50KB), and timeout enforcement (default 120s, max 300s).
- **Source evidence:**
  - Allowlist-based command execution with token-level checking to prevent injection bypass
  - Shell metacharacter rejection for `[\n\r;&|$`<>(){}]`
  - Output truncation at 2000 chars default, 50KB max
  - Timeout enforcement at 120s default, 300s max
  - Allowlist includes common commands: `npm test`, `cargo test`, `python -m pytest`, `go test`, `ruff check`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 6 key claims from the Oh My Hermes wiki have been verified against the source code via codegraph exploration:
- ✅ Plugin system: Hook-based role injection with `omh_state` and `omh_gather_evidence` tools confirmed
- ✅ Role prompts: 15 shared roles with precise behavioral instructions confirmed
- ✅ Composable skills: 10 skills with defined composition pipeline confirmed
- ✅ State convention: `.omh/` directory structure with tracked/untracked policy confirmed
- ✅ `omh_delegate` wrapper: Prepare/finalize split pattern confirmed
- ✅ `omh_gather_evidence` safety rails: Allowlist, metacharacter rejection, truncation, timeout confirmed

## Related

- [[oh-my-hermes]] -- Main wiki entry
- [[hermes-agent]] -- Core Hermes agent
- [[hermes-mcp-implementation]] -- MCP implementation Hermes integrates with

## Cross-project

- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for Hermes Agent
- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
- [[agentfield.codegraph-verify]] -- Similar codegraph verification for AgentField
- [[podman.codegraph-verify]] -- Similar codegraph verification for Podman
