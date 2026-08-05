---
name: opencode-hermes-multiagent
tags: [agent, cli, developer-tools, mcp, optimization, orchestration, security, opencode-hermes-multiagent]
description: "Multi-agent system configuration for OpenCode/Hermes with 17 specialized subagents"
source: sources/opencode-hermes-multiagent/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# OpenCode Hermes Multiagent

**Source:** `sources/opencode-hermes-multiagent/`

A multi-agent system configuration for OpenCode and Hermes Agent that defines 17 specialized subagents organized into an orchestrated pipeline. The master orchestrator agent (Hermes) classifies requests, selects agent pipelines, and manages handoffs between research, planning, implementation, quality, documentation, and infrastructure agents.

| Field | Value |
|---|---|
| **Origin** | [ChromaBrain/opencode-hermes-multiagent](https://github.com/ChromaBrain/opencode-hermes-multiagent) |
| **License** | MIT (README.md:9 badge, README.md:489) |
| **Stack** | OpenCode + Hermes Agent agent runtime |
| **Subagents** | 17 specialized agents |
| **Source** | `sources/opencode-hermes-multiagent/` |

## Key Features

- **17 Specialized Subagents** across 6 domains: Research (finder, analyst, researcher), Planning (architect, planner), Implementation (coder, editor, fixer, refactorer), Quality (reviewer, tester, debugger, security), Documentation (documenter, commenter), and Infrastructure (devops, optimizer).
- **Mandatory Quality Gates:** After any code change, reviewer and tester agents are ALWAYS called -- no exceptions. Security agent is mandatory for auth, credentials, payment processing, or personal data.
- **Trigger Rules:** Keyword-based routing to the correct subagent. @finder always runs first. Specific keywords map each agent (e.g., "debug" -> @debugger, "design" -> @architect).
- **Task Tracking:** Master orchestrator tracks progress with `task` and `todowrite`/`todoread` tools in OpenCode.
- **OpenCode Configuration:** Ships `opencode.json` configuration defining the agent swarm structure.
- **Hermes Core Definition:** Primary orchestrator agent using `openai/gpt-5.2-high` model with no execution tools -- pure dispatch.
- **Pipeline Chains:** 10 defined execution chains (hermes.md:143-175) — 7 named in the README (New Feature, New Feature Security-Related, Bug Fix Unknown Cause, Bug Fix Known Cause, Refactoring, Performance Optimization, Infrastructure Changes) plus Analysis Only, Documentation Only, and Comments Only — each with required agent sequences.

## Architecture

```
                     ┌─────────────────────────────┐
                     │   Hermes (Master Orchestrator)│
                     │   openai/gpt-5.2-high        │
                     │   Dispatches, tracks, never  │
                     │   executes directly           │
                     └──────┬──────┬──────┬────────┘
                            │      │      │
          ┌─────────────────┘      │      └─────────────────┐
          ▼                        ▼                        ▼
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│  RESEARCH        │   │  PLANNING        │   │  IMPLEMENTATION  │
│  @finder         │   │  @architect      │   │  @coder          │
│  @analyst        │   │  @planner        │   │  @editor         │
│  @researcher     │   │                  │   │  @fixer          │
└──────────────────┘   └──────────────────┘   │  @refactorer     │
                                               └──────┬───────────┘
                                                      │
          ┌───────────────────────────────────────────┘
          ▼
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│  QUALITY         │   │  DOCUMENTATION   │   │  INFRASTRUCTURE  │
│  @reviewer MUST  │   │  @documenter     │   │  @devops         │
│  @tester MUST    │   │  @commenter      │   │  @optimizer      │
│  @debugger       │   │                  │   │                  │
│  @security       │   │                  │   │                  │
└──────────────────┘   └──────────────────┘   └──────────────────┘
```

The master orchestrator (Hermes) is configured with `mode: primary` and has no execution tools enabled (all tools like write, edit, bash are false). It only has `task`, `todowrite`, and `todoread` for tracking. The orchestrator:

1. Classifies incoming requests using keyword-based trigger rules
2. Selects appropriate agent pipelines
3. Passes context between agents
4. Handles errors and conflicts
5. Ensures mandatory quality chains are never skipped

### Agent Registry

| Domain | Agent | Trigger Keywords |
|---|---|---|
| Research | @finder | ALWAYS FIRST |
| Research | @analyst | "how", "why", "depends", "impact", "risk" |
| Research | @researcher | "best practice", "how to", new libraries |
| Planning | @architect | "design", "structure", "approach" |
| Planning | @planner | "plan", "steps", complex task |
| Implementation | @coder | "create", "add", "implement" |
| Implementation | @editor | "change", "update", "modify" |
| Implementation | @fixer | "fix" with known location |
| Implementation | @refactorer | "refactor", "clean", "simplify" |
| Quality | @reviewer | AFTER any code change (MANDATORY) |
| Quality | @tester | AFTER any code change (MANDATORY) |
| Quality | @debugger | "debug", "trace", "why fails" |
| Quality | @security | auth, password, token, secrets (MANDATORY) |
| Documentation | @documenter | new API, README changes |
| Documentation | @commenter | complex logic, public interfaces |
| Infrastructure | @devops | CI/CD, docker, deploy |
| Infrastructure | @optimizer | "slow", "performance", "optimize" |

## Source Layout

| Path | Purpose |
|---|---|
| `agent/core/hermes.md` | Master orchestrator agent definition with rules, agent registry, security rules, and mandatory chains |
| `agent/subagents/` | 17 subagent definitions organized by domain |
| `agent/subagents/research/` | analyst.md, finder.md, researcher.md |
| `agent/subagents/planning/` | architect.md, planner.md |
| `agent/subagents/implementation/` | coder.md, editor.md, fixer.md, refactorer.md |
| `agent/subagents/quality/` | debugger.md, reviewer.md, security.md, tester.md |
| `agent/subagents/documentation/` | commenter.md, documenter.md |
| `agent/subagents/infrastructure/` | devops.md, optimizer.md |
| `opencode.json` | OpenCode swarm configuration |
| `README.md` | Project documentation |

## Interfaces

- **OpenCode Configuration:** Ships `opencode.json` (18 agent entries: `hermes` as `default_agent`/`mode: primary` + 17 subagents in `mode: subagent`) defining the agent topology for OpenCode AI's multi-agent runtime
- **Activation:** The system activates **automatically when you use OpenCode AI** — Hermes analyzes the request and routes it to the appropriate pipeline (README.md:190). No special CLI flag; deploy by copying `agent/` into `~/.config/opencode/` (README.md:176) and setting `default_agent: hermes` in `opencode.json`
- **Agent Markdown Files:** Each subagent is defined in a markdown file consumable by the Hermes/OpenCode agent system
- **MCP (for @researcher):** Context7 for library documentation (`npx -y @upstash/context7-mcp`) plus web-page fetch (`uvx mcp-server-fetch`) — README.md:179-186

### Per-Agent Model Map

Models are assigned per agent in README.md:64-110 (mirrored in `opencode.json`):

| Agent | Model |
|---|---|
| @finder / @planner | `google/gemini-3-flash` |
| @analyst | `google/gemini-claude-sonnet-4-5-thinking-high` |
| @researcher | `google/gemini-claude-sonnet-4-5-thinking-low` |
| @architect | `google/gemini-claude-opus-4-5-thinking-medium` |
| @coder / @editor | `google/gemini-claude-opus-4-5-thinking-high` |
| @fixer / @refactorer / @debugger | `google/gemini-claude-sonnet-4-5-thinking-high` |
| @reviewer / @tester / @security | `openai/gpt-5.2-codex-xhigh` |
| @documenter / @devops | `google/gemini-claude-sonnet-4-5-thinking-medium` |
| @commenter | `google/gemini-claude-sonnet-4-5-thinking-low` |
| @optimizer | `google/gemini-claude-sonnet-4-5-thinking-high` |
| Hermes (orchestrator) | `openai/gpt-5.2-high` |

### Tool Scoping

Tool scoping is per-role rather than per-domain. In `opencode.json`:

- **Hermes (primary):** only `task`, `todowrite`, `todoread` enabled — pure dispatch, no execution tools
- **Implementation** (coder, editor, fixer, refactorer): full toolset — `bash`/`read`/`write`/`edit`/`list`/`glob`/`grep`/`lsp` + `todoread`
- **Research/Planning** (finder, analyst, researcher, architect, planner): `read`/`list`/`glob`/`grep` (+ `lsp` for analyst, `webfetch` for researcher) — no `bash` or `write`/`edit`
- **Quality:** NOT uniformly read-only — `@tester` has the full implementation toolset (`bash`/`write`/`edit`, opencode.json:213-226); `@debugger` has `bash` but **no** `write`/`edit` (opencode.json:232-245, diagnosis-only); only `@reviewer` and `@security` are fully read-only (`read`/`list`/`glob`/`grep`/`lsp`/`todoread`, no `bash`/`write`/`edit`)
- **Documentation/Infrastructure:** `@documenter` has `write`/`edit` (no `bash`); `@commenter` has `edit` only; `@devops`/`@optimizer` have the full implementation toolset

## Related

- [[hermes-agent]] -- The agent runtime that executes these multi-agent configurations
- [[hermes-workspace]] -- Provides MCP Hub and agent coordination infrastructure
- [[hermes-suite]] -- All-in-one Hermes container that could run this multi-agent setup
