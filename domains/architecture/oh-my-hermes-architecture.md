---
name: oh-my-hermes-architecture
tags: [oh-my-hermes, architecture, hermes-agent, plugin, multi-agent, orchestration, python, skills]
description: Oh My Hermes Architecture — Plugin hook system, composable skills, role prompts, and OMH state convention for Hermes Agent
source: sources/oh-my-hermes/
---

# Oh My Hermes Architecture
**Source:** `sources/oh-my-hermes/`

Oh My Hermes (OMH) is a multi-agent orchestration layer for Hermes Agent. It provides composable skills for consensus planning, requirements interviewing, and verified execution, plus an optional plugin that adds hook-based role injection, atomic state management, and evidence gathering.

## Architecture

### Plugin Hook System

The OMH plugin (`plugins/omh/`) registers three hooks and two tools:

| Component | Type | Purpose |
|-----------|------|---------|
| `pre_llm_call` | hook | Detects `[omh-role:NAME]` in subagent `user_message`; injects matching role prompt into system context |
| `pre_tool_call` | hook | Validates `[omh-role:NAME]` markers in `delegate_task` goals before subagents start |
| `on_session_end` | hook | Writes `_interrupted_at` to active mode state on unexpected exit |
| `omh_state` | tool (13 actions) | Atomic read/write/clear/check/cancel/lock/unlock + `load_role` for explicit role loading |
| `omh_gather_evidence` | tool | Runs build/test/lint commands from an allowlist, captures + truncates output |

### Role Injection Protocol

Skills use `[omh-role:NAME]` markers in `delegate_task` goal strings instead of embedding role prompt text inline:

```
delegate_task(
    goal="[omh-role:executor] Implement the following task:\n\n<task>...",
    context="<project context only>"
)
```

The `pre_llm_call` hook detects markers and injects matching role files into subagent system prompts. Fifteen shared role prompts cover Planner, Architect, Critic, Executor, Verifier, Analyst, and nine more specialized roles.

### Composable Skill Pipeline

Skills work standalone with zero dependencies. The full pipeline composes as:

```
omh-deep-interview → confirmed spec (.omh/specs/)
    ↓
omh-ralplan → consensus plan (.omh/plans/)
    ↓
omh-autopilot → detects existing spec/plan, skips completed phases
    ↓ (internally uses)
omh-ralph → one-task-per-invocation until verified complete
```

### OMH State Convention

State and artifacts live in `.omh/` within the project directory:

| Subdir | Tracked | Contents |
|--------|---------|----------|
| `state/` | No | Session state JSON (atomically written by `omh_state`) |
| `logs/` | No | Append-only event logs |
| `progress/` | No | Execution progress logs |
| `specs/` | Yes | Confirmed interview specs |
| `plans/` | Yes | Consensus plans (ADR-shaped) |
| `research/` | Yes | Research reports |

### omh_delegate Wrapper and Evidence Safety

`plugins/omh/omh_delegate.py` uses a prepare/finalize split: `prepare()` computes paths and injects contract; `finalize()` verifies file presence. The `omh_gather_evidence` tool enforces token-level allowlist checks, shell metacharacter rejection, output truncation (2K default, 50KB max), and timeout enforcement (120s default, 300s max).

## Key Components

| Component | Path | Role |
|-----------|------|------|
| Plugin hooks | `plugins/omh/hooks/` | pre_llm_call, pre_tool_call, on_session_end |
| State tool | `plugins/omh/omh_state.py` | 13 atomic state actions |
| Evidence tool | `plugins/omh/omh_gather_evidence.py` | Allowlisted command execution |
| Role prompts | `plugins/omh/roles/` | 15 behavioral role profiles |
| Delegate wrapper | `plugins/omh/omh_delegate.py` | Prepare/finalize delegation lifecycle |

## Related

- [[oh-my-hermes]] — Wiki entry
- [[hermes-agent]] — Core Hermes agent
- [[oh-my-openagent]] — OMH variant for OpenAgent
- [[oh-my-opencode-slim]] — OMH-style orchestration for OpenCode
- [[domains/architecture/hermes-agent-architecture.md]]
