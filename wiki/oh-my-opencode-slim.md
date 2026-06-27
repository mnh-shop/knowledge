---
name: oh-my-opencode-slim
description: "Lightweight OpenCode-compatible agent runtime optimized for slim deployments"
tags: [wiki, agent-runtime, opencode, typescript, oh-my-opencode-slim]
source: sources/oh-my-opencode-slim/
---

# oh-my-opencode-slim

## Description

oh-my-opencode-slim (omos) is an agent orchestration plugin for [[opencode]]. Instead of forcing one model to do everything, it routes each part of the job to a specialist agent best suited for the task, balancing quality, speed, and cost. It includes a built-in pantheon of themed agents -- Orchestrator, Explorer, Oracle, Council, Librarian, Designer, Fixer, and Observer -- plus optional agents for visual analysis.

## Key Features

- **Agent Pantheon** -- Specialized agents (Orchestrator, Explorer, Oracle, Council, Librarian, Designer, Fixer, Observer) with themed prompts and configurable models
- **Background Orchestration** -- V2 scheduler-first workflow: Orchestrator dispatches specialists as background tasks, tracks task/session IDs, waits for completion, and reconciles results
- **Companion** -- Optional floating desktop status window showing live agent activity (Rust/egui)
- **Deepwork** -- Structured workflow for large, multi-file, risky, or phased coding work using persistent plan files and Oracle review gates
- **Reflect** -- Reviews repeated work patterns and suggests reusable skills, agents, commands, config rules, or project playbooks
- **Worktrees** -- Manages Git worktrees as isolated coding lanes under `.slim/worktrees/` with safety protocols
- **Council** -- Multiple models run in parallel, judgment synthesized into a single verdict
- **Multiplexer Integration** -- Watch agents work live in Tmux or Zellij panes
- **Preset Switching** -- Switch agent model presets at runtime with `/preset`
- **LazySkills** -- Terminal UI for managing agent skills (companion project)
- **Skills** -- Bundled skills: `simplify`, `codemap`, `clonedeps`, `deepwork`, `reflect`, `worktrees`, `oh-my-opencode-slim`
- **ACP Agents** -- Connect external ACP-compatible agents (Claude Code ACP, Gemini ACP) as delegatable subagents
- **Interview** -- Turn rough ideas into structured markdown specs through a browser-based Q&A flow

## Architecture

oh-my-opencode-slim is a TypeScript plugin for OpenCode, built with Bun and Biome.

### Project Structure

```
oh-my-opencode-slim/
├── src/
│   ├── agents/         # Agent factories (orchestrator, explorer, oracle, council, etc.)
│   ├── cli/            # CLI entry point
│   ├── config/         # Constants, schemas, MCP defaults
│   ├── council/        # Council manager (multi-LLM session orchestration)
│   ├── hooks/          # OpenCode lifecycle hooks
│   ├── mcp/            # MCP server definitions
│   ├── multiplexer/    # Tmux/Zellij pane integration for child sessions
│   ├── skills/         # Skill definitions (included in package publish)
│   ├── tools/          # Tool definitions (council, webfetch, AST-grep, etc.)
│   └── utils/          # Shared utilities (tmux, session helpers)
├── companion/          # Rust/egui desktop companion app
├── docs/               # User-facing documentation
├── dist/               # Built JavaScript and declarations
├── biome.json          # Biome configuration
└── tsconfig.json       # TypeScript configuration
```

### Agent Pantheon

| Agent | Role | Default Model |
|-------|------|--------------|
| **Orchestrator** | Master delegator and strategic coordinator | `openai/gpt-5.5 (medium)` |
| **Explorer** | Codebase reconnaissance | `openai/gpt-5.4-mini` |
| **Oracle** | Strategic advisor and debugger of last resort | `openai/gpt-5.5 (high)` |
| **Council** | Multi-LLM consensus and synthesis | Config-driven |
| **Librarian** | External knowledge retrieval | `openai/gpt-5.4-mini` |
| **Designer** | UI/UX implementation and visual excellence | `openai/gpt-5.4-mini` |
| **Fixer** | Fast implementation specialist | `openai/gpt-5.5 (low)` |
| **Observer** (optional) | Read-only visual analysis (images, PDFs) | `openai/gpt-5.4-mini` |

### Tmux Session Lifecycle

The multiplexer integration manages tmux/zellij pane lifecycles carefully:
- Task launch: session creation, tmux pane spawned, task runs
- Normal completion: status check (idle), extract results, session abort, pane closed (Ctrl+C before kill-pane)
- Cancellation: abort triggers deleted event, pane closed
- External deletion: deleted event triggers cleanup

### Verification Scripts

Two release verification scripts ensure artifact quality:
- `verify-release-artifact.ts` -- Checks dist for leaked machine paths, packs npm artifact, verifies fresh install
- `verify-opencode-host-smoke.ts` -- Stands up a real OpenCode server in an isolated temp root, loads the plugin, checks health endpoint and plugin load errors

## Quick Start

```bash
bunx oh-my-opencode-slim@latest install
```

The installer generates both OpenAI and OpenCode Go presets, with OpenAI active by default. After installation:

1. Log in to providers: `opencode auth login`
2. Refresh models: `opencode models --refresh`
3. Edit plugin config at `~/.config/opencode/oh-my-opencode-slim.json`
4. Update models for each agent
5. Verify with: `ping all agents`

Disable the plugin at any time: `OH_MY_OPENCODE_SLIM_DISABLE=1 opencode`

## Related

- [[opencode]] -- The CLI coding agent that hosts this plugin
- [[api/hermes-agent-api]] -- ACP agent protocol (for ACP agent integration)

## Links

- GitHub: <https://github.com/alvinunreal/oh-my-opencode-slim>
- LazySkills: <https://github.com/alvinunreal/lazyskills>
- Boring Dystopia Development: <https://boringdystopia.ai/>
- Discord: <https://t.me/boringdystopiadevelopment>
