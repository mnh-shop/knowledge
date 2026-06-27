---
name: pi
description: "Agent orchestration toolkit — predecessor to oh-my-pi with tool bridge and provider routing"
tags: [agent-runtime, cli, coding-agent, orchestration, pi, typescript, wiki]
source: sources/pi/
---

# Pi Agent Harness

Pi is a self-extensible coding agent harness and orchestration toolkit built as a TypeScript monorepo. It provides a unified multi-provider LLM API, an agent runtime with tool calling and state management, an interactive coding agent CLI, and a terminal UI library — serving as the architectural predecessor to oh-my-pi.

## Description

Pi is organized as a multi-package monorepo under the `@earendil-works` npm scope. It is designed to give developers a programmable agent runtime with pluggable LLM providers, session persistence, and an interactive TUI mode. The project emphasizes supply-chain hardening with pinned dependencies, lockfile-as-ground-truth, and release smoke testing.

## Key Features

- **Unified Multi-Provider LLM API** (`@earendil-works/pi-ai`): Common interface across OpenAI, Anthropic, Google, Amazon Bedrock, DeepSeek, NVIDIA NIM, and more — with provider-specific auth, streaming, and transport (`sse`, `websocket`, `auto`).
- **Agent Runtime** (`@earendil-works/pi-agent-core`): Core agent loop with tool calling, session state management, message compaction, branch summarization, and harness support for testing.
- **Interactive Coding Agent CLI** (`@earendil-works/pi-coding-agent`): Full interactive mode with session resume, provider configuration, and an extensible extension system (`~/.pi/extensions/`).
- **Terminal UI** (`@earendil-works/pi-tui`): Differential-rendering TUI library powering the interactive mode.
- **Session Management**: Persistent session storage via JSONL with branching, summarization, and CWD tracking.
- **Containerization Support**: Three isolation patterns — Gondolin (micro-VM), plain Docker, and OpenShell sandbox.
- **Supply-Chain Hardening**: Pinned direct deps, lockfile-as-ground-truth, shrinkwrap for published CLI, CI with `--ignore-scripts`, and scheduled `npm audit`.

## Architecture

Pi follows a layered architecture:

- **`packages/ai/`** — Abstraction layer over LLM providers. Defines `Provider`, `Model`, `StreamOptions`, and auth resolution. Each provider (Anthropic, OpenAI, Google, Bedrock, etc.) implements a common interface. Transport negotiation (SSE vs WebSocket) is handled per-provider.
- **`packages/agent/`** — Agent runtime core. Owns the agent loop (`agent-loop.ts`), tool execution, message conversion, session management (`session/`), harness for test/CI (`harness/`), and state types (`types.ts`). The `AgentTool` type has 58 callers across the codebase, making it a central abstraction.
- **`packages/coding-agent/`** — CLI layer exposing the interactive coding agent. Handles session runtime (`agent-session-runtime.ts`), interactive mode (`interactive-mode.ts`), extensions (`extensions/`), and entry points (`main.ts`).
- **`packages/tui/`** — Terminal UI library with differential rendering for the interactive interface.

Data flows: User input → CLI (`coding-agent`) → Agent Runtime (`agent`) → AI Provider (`ai`) → LLM response → tool execution loop → session persistence.

## Quick Start

```bash
# Install from npm
npm install -g @earendil-works/pi-coding-agent

# Run interactively
pi

# Run with a prompt
pi -p "Explain the architecture of this project"

# Run from source
git clone https://github.com/earendil-works/pi-mono
cd pi-mono
npm install --ignore-scripts
npm run build
./pi-test.sh
```

## Related

- [[abvx-agent-skills]] — Skills ecosystem for agent-based development
- [[Hermes-caduceus]] — Agent tool bridge pattern
- [[Mnemosyne]] — Memory and state management for agents

## Links

- [GitHub: earendil-works/pi-mono](https://github.com/earendil-works/pi-mono)
- [pi.dev](https://pi.dev)
- [Documentation](https://pi.dev/docs/latest)
- [RFCs](https://rfc.earendil.com/keyword/pi/)
- [npm: @earendil-works/pi-coding-agent](https://www.npmjs.com/package/@earendil-works/pi-coding-agent)
- [Containerization Guide](packages/coding-agent/docs/containerization.md)
