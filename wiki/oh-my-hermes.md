---
name: oh-my-hermes
title: Oh My Hermes (OMH)
description: Multi-agent orchestration skills for Hermes Agent with consensus planning, requirements interviewing, and verified execution
tags: [hermes-agent, multi-agent, orchestration, planning, plugin, plugin-sdk, research, python]
source: sources/oh-my-hermes/
---

# Oh My Hermes (OMH)

Multi-agent orchestration skills for [Hermes Agent](https://github.com/NousResearch/hermes-agent), inspired by [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) and rebuilt natively for Hermes primitives.

## Overview

OMH provides composable skills for consensus planning, requirements interviewing, and verified execution, plus an optional plugin that adds hook-based role injection, atomic state management, and evidence gathering. Skills work standalone with zero dependencies.

## Skills

| Skill | What It Does |
|-------|--------------|
| **omh-deep-research** | Multi-phase web research: decompose → parallel search → synthesize → verify citations |
| **omh-ralplan** | Consensus planning: Planner → Architect → Critic debate until agreement |
| **omh-ralplan-driver** | Dispatcher's playbook for driving an `omh-ralplan` run |
| **omh-deep-interview** | Socratic requirements interview with coverage tracking |
| **omh-ralph** | Verified execution: implement → verify → iterate until done |
| **omh-ralph-driver** | Dispatcher's playbook for driving an `omh-ralph` run |
| **omh-ralph-task** | Executor's discipline for a single `omh-ralph` task |
| **omh-triage** *(v0.1)* | Multi-role consensus triage of an issue backlog |
| **omh-triage-driver** *(v0.1)* | Dispatcher's playbook for driving an `omh-triage` run |
| **omh-autopilot** | Full pipeline composing all three skills end-to-end |

### Composition Pipeline

```
omh-deep-interview  →  confirmed spec (.omh/specs/)
        ↓
omh-ralplan         →  consensus plan (.omh/plans/)
        ↓
omh-autopilot       →  detects existing spec/plan, skips completed phases
        ↓ (internally uses)
omh-ralph           →  one-task-per-invocation until verified complete
```

## Plugin Architecture (v2)

Install to `~/.hermes/plugins/omh/`. Requires Python 3.10+ and `pyyaml`.

### Components

| Component | What It Does | Status |
|-----------|-------------|--------|
| `omh_state` tool (8 actions) | Atomic read/write/check/cancel for `.omh/` state files; `load_role` action for explicit role loading | Shipped |
| `omh_gather_evidence` tool | Runs build/test/lint commands from an allowlist, captures + truncates output | Shipped |
| `pre_llm_call` hook | Detects `[omh-role:NAME]` in subagent `user_message`; injects matching role prompt into system context | Shipped |
| `pre_tool_call` hook | Validates `[omh-role:NAME]` markers in `delegate_task` goals before subagents start | Shipped |
| `on_session_end` hook | Writes `_interrupted_at` to active mode state on unexpected exit | Shipped |

### Role Prompts

Nine shared role prompts give subagents precise behavioral instructions:

| Role | Purpose | Used By |
|------|---------|---------|
| Planner | Task decomposition, sequencing, risk flags | ralplan |
| Architect | Structural review, boundary clarity, long-term maintainability | ralplan, ralph (final review) |
| Critic | Adversarial challenge, assumption testing, stress testing | ralplan |
| Executor | Code implementation, test-first, minimal changes | ralph |
| Verifier | Evidence-based completion checking, read-only, pass/fail | ralph |
| Analyst | Requirements extraction, hidden constraints, acceptance criteria | deep-interview, autopilot |
| Security Reviewer | Vulnerabilities, trust boundaries, injection vectors | autopilot (validation phase) |
| Test Engineer | Test strategy, coverage, edge cases, flaky test hardening | autopilot (QA phase) |
| Code Reviewer | Diff review, conventions, holistic quality | autopilot (validation phase) |
| Debugger | Root cause analysis, hypothesis testing, targeted fixes | ralph (error diagnosis) |
| Triage Maintainer | Code-anchored issue triage | omh-triage |
| Triage Skeptic | Pruning and prioritization | omh-triage |

### Role Injection

Skills use `[omh-role:NAME]` markers in the `delegate_task` goal string instead of embedding role prompt text inline:

```python
delegate_task(
    goal="[omh-role:executor] Implement the following task:\n\n<task>...",
    context="<project context only>"
)
```

The `pre_llm_call` hook detects the marker and injects the matching role file into the subagent's system prompt via `{"context": ...}`.

## State Convention

State and artifacts live in `.omh/` within the project directory:

| Subdir | Tracked? | Lifetime | Contents |
|--------|----------|----------|----------|
| `state/` | NO | per-session | Active mode state JSON (interview, ralplan, ralph, autopilot). Atomically written by `omh_state`. |
| `logs/` | NO | per-session | Append-only event logs — decisions and transitions |
| `progress/` | NO | per-session | Ralph execution progress logs |
| `specs/` | YES | durable | Confirmed interview specs. Decision inputs. |
| `plans/` | YES | durable | Consensus plans from ralplan (ADR-shaped). |
| `research/` | YES | durable | Research reports from `omh-deep-research`. |

## omh_delegate Wrapper

A hardened delegation wrapper at `plugins/omh/omh_delegate.py` addresses subagent output loss with a prepare/finalize split:

- **prepare()** — computes paths, writes dispatched breadcrumb, injects contract
- **finalize()** — verifies file present, writes completion breadcrumb

Artifacts land at: `.omh/research/{mode}/{phase}[-r{round}][-{slug}]-{ts}.md`

Breadcrumbs land at: `.omh/state/dispatched/{id}.dispatched.json` and `.omh/state/dispatched/{id}.completed.json`

## omh_gather_evidence Tool

Runs build/test/lint commands from a configured allowlist with safety rails:

- Token-level allowlist check prevents partial-word and argument-injection bypass
- Shell metacharacter rejection (`[\\n\\r;&|$\`<>(){}]`)
- Output truncation (default 2000 chars, max 50KB)
- Timeout enforcement (default 120s, max 300s)

Allowlist includes: `npm test`, `cargo test`, `python -m pytest`, `go test`, `ruff check`, and other common build/test tools.

## Known Gaps

- **wiki/fact_store/memory persistence** — research artifacts from `omh-deep-research` not integrated
- **Per-call subagent tool scoping** — READ-ONLY contract enforced by prose when unavailable

## Requirements

- Hermes Agent v0.7.0+
- Plugin requires Python 3.10+ and `pyyaml`

## Installation

```bash
hermes skills tap add witt3rd/oh-my-hermes
hermes skills install omh-deep-research omh-ralplan omh-ralplan-driver omh-deep-interview omh-ralph omh-ralph-driver omh-ralph-task omh-autopilot
```

Or copy `skills/<name>/` to `~/.hermes/skills/omh/` manually. Plugin: install `plugins/omh/` to `~/.hermes/plugins/omh/`.

## Source

## Related

- [[hermes-agent]] — Core Hermes agent
- [[plugin-sdk]] — Plugin development framework
- [[multi-agent]] — Multi-agent orchestration


`/Users/admin1/Documents/knowledge/sources/oh-my-hermes`