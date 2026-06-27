---
name: hermes-agent-acp-skill
description: "Hermes agent ACP skill: agent-to-agent delegation via Agent Communication Protocol"
source: sources/hermes-agent-acp-skill/
tags: [acp, hermes-agent, orchestration, claude-code, plugin]
---
# Hermes ACP Agent Skill

A production-oriented [[hermes-agent]] skill for ACP-style multi-agent delegation. Standardizes how work is delegated across Hermes internal subagents, Codex, and Claude Code.

## Overview

- **Source**: `/Users/admin1/Documents/knowledge/sources/hermes-agent-acp-skill/`
- **Skill name**: `hermes-acp-orchestrator`
- **License**: MIT
- **Author**: Rainhoole

## What It Solves

Provides a consistent delegation pattern across three agent targets:

1. **hermes** — default in-process subagent
2. **codex** — external Codex CLI
3. **claude-code** — external Claude Code CLI

The skill focuses on three core concerns:

| Concern | Mechanism |
|---|---|
| Clear agent routing | `agent=` parameter on each task |
| Context isolation | Delegated work does not pollute the parent context |
| Safety controls | Timeouts + output size limits for external agents |

## Usage Pattern

Tasks are delegated with explicit routing, context, and tool constraints:

```python
delegate_task(
    goal="Implement the bugfix and run tests",
    context="Keep patch minimal and include changed files in the summary.",
    agent="codex"
)
```

For parallel batch delegation with per-task agent overrides:

```python
delegate_task(tasks=[
    {"goal": "Find regressions",          "agent": "claude-code", "toolsets": ["file"]},
    {"goal": "Implement fix and validate", "agent": "codex",      "toolsets": ["terminal", "file"]},
    {"goal": "Produce merge-ready summary","agent": "hermes",     "toolsets": ["file"]}
])
```

## Key Files

| File | Purpose |
|---|---|
| `SKILL.md` | Skill instructions and workflow patterns |
| `README.md` | Repository overview and usage guidance |

## Operating Rules

1. Always provide concrete `context` (file paths, constraints, expected output).
2. Keep tasks narrow; split large objectives into batch tasks.
3. Use `toolsets` to reduce accidental side effects.
4. Ask for structured summaries (what changed, what passed, what failed).
5. For external agents, keep outputs concise and action-oriented.

## Recommended Delegation Config

```yaml
delegation:
  max_iterations: 50
  default_toolsets: ["terminal", "file", "web"]
  external_timeout_seconds: 900
  external_max_output_chars: 24000
```

## See Also

- [[hermes-agent]] — the Hermes agent orchestration platform
