---
name: hermes-agent-acp-skill
description: "Hermes agent ACP skill: agent-to-agent delegation via Agent Communication Protocol"
source: sources/hermes-agent-acp-skill/
verification_date: 2026-07-12
verified_by: codegraph-verify
tags: [hermes-agent-acp-skill, hermes-agent, acp, skill, orchestration, delegation, codex, claude-code]
---

# Hermes ACP Agent Skill

## Overview

A production-oriented [[hermes-agent]] skill for ACP-style multi-agent delegation, authored by Rainhoole under the MIT license. The skill standardizes how work is delegated across three agent targets — Hermes internal subagents, Codex CLI, and Claude Code CLI — through a unified API with runtime safety controls. It solves three core concerns of multi-agent orchestration in a single Hermes skill: clear agent routing via an `agent=` parameter on each task, context isolation so delegated work does not pollute the parent agent's context, and safety controls including configurable timeouts and output size limits for external agents. The skill is registered under the name `hermes-acp-orchestrator` and is activated when the orchestrator needs to distribute engineering workflows across specialized sub-agents.

## Key Features

- **Three-target delegation** — routes tasks to `hermes` (default in-process subagent), `codex` (external Codex CLI), or `claude-code` (external Claude Code CLI). Each target uses the same `delegate_task()` API with the same parameter structure, so switching agents for a task is a one-line change. This enables deterministic routing: implementation goes to Codex, risk analysis to Claude Code, and integration summaries to Hermes.

- **Parallel batch delegation with per-task overrides** — the skill supports submitting multiple tasks in a single call with per-task agent routing, toolsets, and goals. For example, a batch pipeline can delegate regression finding to `claude-code` (with `file` tools only), fix implementation to `codex` (with `terminal` and `file` tools), and merge-ready summary production to `hermes` (with `file` tools). Tasks run independently and results are collected as structured summaries.

- **Safety guardrails for external agents** — the skill enforces configurable bounds on external agents: `external_timeout_seconds` (recommended 900s/15min) prevents runaway tasks, and `external_max_output_chars` (recommended 24,000) limits response size to keep costs predictable and output manageable. A `max_iterations` setting (default 50) caps the total delegation loop depth. These parameters are configured in the Hermes `delegation` block in `config.yaml`.

- **Context isolation and structured output** — tasks receive explicit `context` parameters (file paths, constraints, expected output format) that serve as isolation boundaries. The skill mandates structured summaries from all agents: what changed, what passed, what failed. This pattern ensures that each delegated task returns actionable, merge-ready information rather than raw logs or conversational output.

- **Narrow task discipline** — the skill's operating rules enforce splitting large objectives into narrow batch tasks, using `toolsets` to reduce accidental side effects (e.g., a review task gets only `file` tools, not `terminal`). This follows the agentic principle of least privilege and makes delegation predictable and debuggable.

## Delegation Patterns

### Single task with explicit target

```python
delegate_task(
    goal="Implement the bugfix and run tests",
    context="Keep patch minimal and include changed files in the summary.",
    agent="codex"
)
```

### Parallel batch with per-task agent override

```python
delegate_task(tasks=[
    {"goal": "Find regressions",          "agent": "claude-code", "toolsets": ["file"]},
    {"goal": "Implement fix and validate", "agent": "codex",      "toolsets": ["terminal", "file"]},
    {"goal": "Produce merge-ready summary","agent": "hermes",     "toolsets": ["file"]}
])
```

### Reliability-focused run with capped iterations

```python
delegate_task(
    goal="Refactor auth middleware",
    context="Run focused tests and report failures only.",
    agent="claude-code",
    max_iterations=30
)
```

## Recommended Configuration

```yaml
delegation:
  max_iterations: 50
  default_toolsets: ["terminal", "file", "web"]
  external_timeout_seconds: 900
  external_max_output_chars: 24000
```

## Troubleshooting

| Symptom | Resolution |
|---|---|
| Unsupported agent error | Use only `hermes`, `codex`, or `claude-code` as the `agent=` value |
| External agent timeout | Increase `delegation.external_timeout_seconds` or split the task further |
| Oversized responses | Lower verbosity in the delegated goal, rely on concise structured summaries |
| Weak results | Provide stronger context, acceptance criteria, and exact file paths to touch |

## Related

- [[hermes-agent]] — The Hermes agent orchestration platform that executes this skill
- [[hermes-agent-docker]] — Docker deployment for Hermes agents using ACP delegation
- [[hermes-agent-template]] — Template for deploying Hermes agents that can leverage ACP delegation
- [[hermes-workspace]] — Hermes workspace that can host multi-agent ACP workflows
- [[opencode]] — AI coding agent that ACP delegation can route tasks to via Codex CLI
- [[hermes-plugins]] — Plugin system that can extend ACP routing targets
- [[n8n]] — Workflow automation platform that could trigger ACP delegation pipelines
