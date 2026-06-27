---
name: opencode
description: "Multi-platform CLI coding agent with extensible provider and toolchain support"
tags: [cli, code-assistant, coding-agent, multi-provider, wiki, typescript, nix]
source: sources/opencode/
---

# opencode

## Description

OpenCode is an open-source AI coding agent that runs in the terminal. It is a large monorepo split into many packages -- a CLI client, a core domain library, a server that hosts sessions, a TUI, a desktop app, a web app, SDKs, and more. It uses the [Effect-TS](https://effect.website/) library for typed, composable, testable runtime logic throughout.

## Key Features

- **Multi-platform CLI** -- macOS, Linux, Windows (via npm, Homebrew, Scoop, Chocolatey, pacman, nix)
- **Desktop App** (BETA) -- Native macOS (Apple Silicon + Intel), Windows, and Linux builds
- **Multi-provider** -- Extensible provider system supporting OpenAI, Anthropic, Google, and custom providers
- **Plugin System** -- Load external plugins (e.g., [[oh-my-opencode-slim]]) for added agent orchestration
- **Background Subagents** -- Experimental V2 API for delegating work to background agents
- **Session Runtime** -- Durable conversational history with System Context architecture
- **System Context** -- Composable typed context sources (project instructions, tool results, agent skills, date, etc.) with epoch-based baseline management and differential mid-conversation updates
- **Built-in Agents** -- `build` (full-access dev agent), `plan` (read-only analysis agent), `general` (multistep search agent)
- **Built-in Skills** -- Plugin-defined skills with permission-checked execution
- **SDK / SDK-Next** -- Generated TypeScript SDK with Promise and Effect clients, plus embedded in-process hosting
- **Plugin SDK** -- `packages/plugin` with configuration, agent, context source, hook, MCP, skill, and tool APIs
- **Tool Registry** -- Bounded tool output with managed file fallback for oversized results
- **Server Mode** -- Headless OpenCode server with HTTP API (`opencode serve`)
- **AGENTS.md Driven** -- Project-level agent instructions honored globally and per-workspace
- **Event Architecture** -- Durable session events and instance-wide live event streams

## Architecture

OpenCode is a monorepo with many packages under `packages/`:

### Key Packages

| Package | Purpose |
|---------|---------|
| `packages/opencode` | Main CLI entry point, session runtime, agents, commands, MCP integration |
| `packages/core` | Domain logic: sessions, filesystem, config, permissions, tools, skills, system context |
| `packages/server` | HTTP server hosting the OpenCode API with middleware, routing, and handlers |
| `packages/protocol` | Public HTTP API definitions, endpoint construction, middleware placement |
| `packages/schema` | Shared Schema definitions for domain types, events, filesystem, errors |
| `packages/client` | Generated HTTP client (Promise and Effect variants via `/effect`) |
| `packages/sdk` | Legacy JavaScript SDK |
| `packages/sdk-next` | In-process embedded OpenCode: client + core + server in one process |
| `packages/plugin` | Plugin SDK: configuration, agent, context source, hook, MCP, skill, tool APIs |
| `packages/app` | Web application (frontend) |
| `packages/console/app` | TUI (terminal UI) application |
| `packages/desktop` | Desktop Electron app |
| `packages/web` | Marketing/site web app |
| `packages/llm` | LLM provider abstractions and protocol adapters |
| `packages/identity` | Authentication and identity |
| `packages/tui` | TUI component library |
| `packages/ui` | Shared UI components |

### Session Runtime

The V2 Session architecture is based on durable conversational history with a structured System Context:

- **System Context** -- A collection of typed Context Sources (project instructions, tool results, agent skills, date, PTY environment) composed at provider-turn boundaries
- **Context Epoch** -- The span during which one Baseline System Context remains the immutable provider-cache prefix; ends at compaction or incompatible transition
- **Mid-Conversation System Message** -- A chronological instruction emitted when a Context Source changes, without replacing the full baseline
- **Session Drain** -- A process-local execution span that promotes eligible input through provider turns until idle
- **Admitted Prompt** -- Durable user input accepted into the session inbox but not yet model-visible
- **Prompt Promotion** -- The durable transition from inbox to Session History at safe provider-turn boundaries

### Agent Architecture

- **build** -- Default full-access agent for development work
- **plan** -- Read-only agent for analysis and code exploration; denies file edits
- **general** -- Subagent for complex searches and multistep tasks (internal)
- Agents are switchable during a session with the Tab key or API calls
- Selected-agent available-skill guidance is a composable Context Source

### Plugin System

Plugins register through the `packages/plugin` SDK and can contribute:
- Configuration presets and schema
- Custom agents with provider/model selection
- Context Sources that contribute to System Context
- Lifecycle hooks (init, agent-start, agent-end, etc.)
- MCP server definitions
- Skills (permission-checked composable capabilities)
- Tools

## Quick Start

```bash
# One-liner install
curl -fsSL https://opencode.ai/install | bash

# Or via package manager
npm i -g opencode-ai@latest
brew install anomalyco/tap/opencode

# Start coding
opencode
```

Tab switches between `build` (default) and `plan` agents. Use `@general` for multistep search tasks.

## Related

- [[oh-my-opencode-slim]] -- Agent orchestration plugin for OpenCode
- [[api/hermes-agent-api]] -- ACP agent protocol
- [[domains/mcp/INDEX]] -- MCP tool standard used by OpenCode

## Links

- Website: <https://opencode.ai>
- GitHub: <https://github.com/anomalyco/opencode>
- Discord: <https://discord.gg/opencode>
- Documentation: <https://opencode.ai/docs>
- Download: <https://opencode.ai/download>
- X.com: <https://x.com/opencode>
