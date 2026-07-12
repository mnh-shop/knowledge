---
name: opencode-architecture
tags: [opencode, architecture, coding-agent, typescript, effect-ts, monorepo, multi-agent, cli, plugin-sdk]
description: OpenCode Architecture — Effect-TS monorepo with V2 Session model, multi-agent system, and plugin SDK
source: sources/opencode/
---

# OpenCode Architecture
**Source:** `sources/opencode/`

OpenCode is an open-source AI coding agent and multi-platform CLI. Built as a large Effect-TS monorepo, it provides a CLI client, TUI, desktop app, web app, session server, plugin SDK, and generated HTTP client — all sharing domain and schema packages.

## Architecture

### Monorepo Layering

The monorepo at `packages/` enforces strict dependency direction: **Schema → Core → Protocol → Server → Client**.

| Layer | Directory | Role |
|-------|-----------|------|
| Schema | `packages/schema` | Shared domain types, events, filesystem, errors |
| Core | `packages/core` | Sessions, filesystem, config, permissions, tools, skills, system context |
| Protocol | `packages/protocol` | Public HTTP API definitions, endpoint construction |
| Server | `packages/server` | HTTP server hosting the OpenCode API |
| Client | `packages/client` | Generated HTTP client (Effect and Promise variants) |
| LLM | `packages/llm` | Provider abstractions and protocol adapters |
| Plugin | `packages/plugin` | Plugin SDK: agents, context sources, hooks, MCP, skills, tools |

Surface packages (`packages/opencode` CLI, `packages/console/app` TUI, `packages/desktop`, `packages/app` web) compose these layers.

All runtime logic uses Effect-TS for typed, composable, testable effects with structured concurrency.

### V2 Session Runtime

The V2 Session architecture replaces the legacy loop with a durable, event-sourced model:

- **System Context** — Composable typed context sources (project instructions, tool results, agent skills, date, PTY env) assembled at provider-turn boundaries
- **Context Epoch** — Immutable provider-cache baseline prefix; ends at compaction or incompatible transition
- **Mid-conversation System Message** — Chronological instruction when a context source changes mid-session, without replacing the baseline
- **Session Drain** — Process-local execution span promoting admitted inputs through provider turns until idle
- **Admitted Prompt** — Durable user input accepted into the session inbox but not yet model-visible
- **Prompt Promotion** — Durable transition from inbox to session history at safe provider-turn boundaries

### Multi-Agent System

Three built-in agents, switchable mid-session via Tab or API:

| Agent | Mode | Description |
|-------|------|-------------|
| **build** | Full-access | Default development agent with file read/write, tool execution |
| **plan** | Read-only | Analysis and code exploration; file edits denied |
| **general** | Subagent | Internal multistep search and complex tasks |

### Plugin SDK

The `packages/plugin` SDK allows plugins to register configuration presets, custom agents with provider/model selection, context sources for System Context composition, lifecycle hooks (init, agent-start, agent-end), MCP server definitions, permission-checked skills, and tools. Plugins like [[oh-my-opencode-slim]] add agent orchestration layers.

### Tool Registry

A descriptor-driven planner evaluates tool availability against runtime context (auth providers, config, env vars, enabled plugins). Tools have typed schemas, owner references (core/plugin/channel/MCP), and availability expressions. Output is bounded with managed file fallback for oversized results.

### Session Event Architecture

Durable session events with instance-wide live event streams. EventV2 supports replay owner claims separate from clustered session execution ownership.

## Key Components

| Package | Purpose |
|---------|---------|
| `packages/opencode` | Main CLI, session runtime, agents, commands, MCP integration |
| `packages/core` | Domain logic, V2 session algebra, filesystem, permission, tools |
| `packages/server` | HTTP server with middleware, routing, handlers |
| `packages/schema` | Shared Effect Schema definitions for all domain types |
| `packages/plugin` | Plugin SDK entry point for third-party extensions |
| `packages/client` | Generated HTTP client (Promise + Effect variants) |
| `packages/llm` | LLM provider abstraction and adapter layer |

## Related

- [[opencode]] — Wiki entry
- [[oh-my-opencode-slim]] — Agent orchestration plugin
- [[free-claude-code]] — Free tier MCP wrapper
- [[zot]] — Go coding agent with MCP tools
- [[oh-my-opencode-slim]] — OMOS plugin architecture
