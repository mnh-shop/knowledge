---
title: hermes-agent-acp-skill
subtitle: CodeGraph Verification
date: 2026-07-12
tags: [hermes-agent-acp-skill, codegraph-verify, hermes-agent, acp]
suffix: .codegraph-verify
source: sources/hermes-agent-acp-skill/
related: [[hermes-agent-acp-skill]], [[hermes-agent]], [[domains/acp/INDEX|acp]], [[openclaw-acp-agent]]
verified-by: codegraph-explore
---

# hermes-agent-acp-skill — CodeGraph Verification

**Verification date:** 2026-07-12
**Verified by:** codegraph-explore
**Source reference:** `sources/hermes-agent-acp-skill/`

## Claim-1: ACP-style multi-agent delegation skill for Hermes

The repository contains a production-oriented Hermes skill (`hermes-acp-orchestrator`) that standardizes delegation across three agent targets — Hermes internal subagents, Codex CLI, and Claude Code CLI — via a unified `delegate_task()` API.

**Source evidence:** SKILL.md lines 1-9 (frontmatter):
```
---
name: hermes-acp-orchestrator
description: Use when you need ACP-style delegation in Hermes with explicit agent routing to hermes, codex, or claude-code...
version: 1.0.0
author: Rainhoole
license: MIT
metadata:
  hermes:
    tags: [acp, delegation, orchestration, codex, claude-code]
---
```

**Supporting detail:** SKILL.md lines 38-45 show the three-target routing pattern:
```python
delegate_task(
    goal="Implement the bugfix and run tests",
    context="Keep patch minimal and include changed files in the summary.",
    agent="codex"
)
```

## Claim-2: Supports parallel batch delegation with per-task agent override

The skill exposes a single-call batch API that accepts multiple tasks with independent `goal`, `agent`, and `toolsets` fields, enabling mixed-agent pipelines.

**Source evidence:** SKILL.md lines 49-55:
```python
delegate_task(tasks=[
    {"goal": "Find regressions", "agent": "claude-code", "toolsets": ["file"]},
    {"goal": "Implement fix and validate", "agent": "codex", "toolsets": ["terminal", "file"]},
    {"goal": "Produce merge-ready summary", "agent": "hermes", "toolsets": ["file"]}
])
```

**Supporting detail:** README.md lines 27-33 demonstrate the same parallel batch pattern with explicit agent routing for risk review, patch implementation, and integration summary.

## Claim-3: Safety guardrails with configurable timeouts and output limits

The skill enforces runtime safety controls for external agents: configurable timeout (recommended 900s), response size cap (recommended 24,000 chars), and max iteration depth (default 50).

**Source evidence:** SKILL.md lines 78-84 (Recommended Delegation Config):
```yaml
delegation:
  max_iterations: 50
  default_toolsets: ["terminal", "file", "web"]
  external_timeout_seconds: 900
  external_max_output_chars: 24000
```

**Supporting detail:** SKILL.md lines 88-91 list troubleshooting entries for external agent timeout ("increase `delegation.external_timeout_seconds` or split the task") and oversized responses ("lower verbosity in the delegated goal and rely on concise summaries").

## Claim-4: Context isolation and structured output discipline

The skill mandates that each delegated task receives explicit `context` parameters (file paths, constraints, formatting rules) which serve as isolation boundaries. Tasks return structured summaries rather than raw logs.

**Source evidence:** SKILL.md lines 70-74 (Operating Rules):
```
1. Always provide concrete `context` (file paths, constraints, expected output).
2. Keep tasks narrow; split large objectives into batch tasks.
3. Use `toolsets` to reduce accidental side effects.
4. Ask for structured summaries (what changed, what passed, what failed).
```

**Supporting detail:** README.md lines 13-15 state the skill "standardizes how you delegate work across" the three targets, focusing on "context isolation (delegated work does not pollute the parent context)" and "Safety controls (timeouts + output limits for external agents)."

## Claim-5: Three supported agents with deterministic routing

The skill restricts delegation targets to exactly three options — `hermes`, `codex`, and `claude-code` — with a troubleshooting entry for unsupported agents.

**Source evidence:** SKILL.md lines 18-22:
```
Targets supported by delegation:
- `hermes` (default in-process subagent)
- `codex` (external Codex CLI)
- `claude-code` (external Claude Code CLI)
```

**Supporting detail:** SKILL.md line 88 troubleshooting: "**Unsupported agent**: use only `hermes`, `codex`, `claude-code`."

## Claim-6: Narrow task discipline with least-privilege tool access

The skill enforces that tasks use `toolsets` to restrict which capabilities the delegated agent can access, following the principle of least privilege.

**Source evidence:** SKILL.md line 73: "Use `toolsets` to reduce accidental side effects." The batch example shows `"toolsets": ["file"]` for a review task (read-only) vs `"toolsets": ["terminal", "file"]` for implementation tasks.

**Supporting detail:** `max_iterations=30` in the reliability-focused run example (SKILL.md line 65) demonstrates capping total delegation loop depth to prevent runaway tasks.

## Dependency Map

```
hermes-agent-acp-skill
  └─► hermes-agent (Hermes agent runtime that executes this skill)
  └─► opencode (Codex CLI target — routes tasks via ACP to opencode)
  └─► openclaw-acp-agent (alternative ACP agent implementation)
  └─► hermes-agent-template (template agents can use this skill for ACP delegation)
```
