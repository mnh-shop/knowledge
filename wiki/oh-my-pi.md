---
name: oh-my-pi
description: "Coding agent with the IDE wired in — fork of Mario Zechner's Pi with batteries-included coding workflow"
tags: [wiki, pi, coding-agent, orchestration, python, rust, typescript]
source: sources/oh-my-pi/
---

# oh-my-pi

oh-my-pi (omp) is a coding agent with the IDE wired in — a fork of Mario Zechner's Pi with batteries-included coding workflow. It provides an interactive terminal-first UX with practical built-ins: sessions, subagents, slash commands, and extensibility.

## Description

A coding agent that runs natively on macOS, Linux, and Windows without WSL. Built on ~55,000 lines of Rust for in-process text/grep/shell operations with Bun runtime for TypeScript orchestration. Fork of [pi-mono](https://github.com/badlogic/pi-mono) with cross-architecture support and advanced features like LSP integration, debugger driving, and time-traveling stream rules.

## Key Features

### Tool Surface
- **32 built-in tools** in unified namespace: read, write, edit, bash, lsp, debug, task, web_search, browser, and more
- **Hashline editing** — content-hash anchored patches with stale-anchor recovery
- **AST rewriting** via ast-grep for structural code changes
- **LSP wired to writes** — renames update re-exports, barrel files, aliased imports

### Runtime Features
- **Persistent eval sessions** — Python and JavaScript kernels with tool re-entry
- **Real debugger driving** — DAP sessions for lldb, dlv, debugpy
- **Time-traveling stream rules** — abort and inject corrections mid-stream
- **First-class subagents** with typed results and workspace isolation
- **Advisor model** — second model watching every turn with inline notes

### Provider Support
- **40+ providers** across frontier APIs (Anthropic, OpenAI, Google, xAI, etc.), coding plans (Cursor, Copilot, GLM, etc.), and local (Ollama, vLLM, etc.)
- **Path-scoped models** and **fallback chains** for resilient routing
- **Round-robin credentials** for quota management

### Collaboration & Portability
- **Collab live sessions** via relay with QR codes
- **ACP support** — Agent Client Protocol for editor integration
- **Config inheritance** — reads existing rules from .claude, .cursor, .windsurf, .github/copilot, etc.

### Internals
- **In-process Rust** — ripgrep, bash, tree-sitter in the process via N-API
- **Four entry points** — interactive TUI, one-shot, RPC, and ACP
- **Hindsight memory** — SQLite-based session compression and recall

## Architecture

### Monorepo Structure

| Package | Description |
|---------|-------------|
| `@oh-my-pi/pi-ai` | Multi-provider LLM client with streaming support |
| `@oh-my-pi/pi-catalog` | Bundled model database, provider descriptors, identity |
| `@oh-my-pi/pi-agent-core` | Agent runtime with tool calling and state management |
| `@oh-my-pi/pi-coding-agent` | Main CLI application (primary focus) |
| `@oh-my-pi/pi-tui` | Terminal UI library with differential rendering |
| `@oh-my-pi/pi-natives` | N-API bindings for grep, shell, image, text, highlighting |
| `@oh-my-pi/omp-stats` | Local observability dashboard for AI usage statistics |
| `@oh-my-pi/pi-utils` | Shared utilities (logging, streams, dirs, process helpers) |
| `@oh-my-pi/pi-wire` | Shared collab live-session protocol types |
| `@oh-my-pi/hashline` | Line-anchored patch language and applier |
| `@oh-my-pi/pi-mnemopi` | Local SQLite memory engine |

### Rust Crates (~55k lines)

| Crate | Purpose | Lines |
|-------|---------|-------|
| `pi-natives` | Core N-API addon aggregating all Rust modules | - |
| `pi-shell` | Embedded bash/PTY/process management (brush-shell fork) | ~3,700 |
| `pi-ast` | tree-sitter-based code summarization (50+ grammars) | ~1,000 |
| `pi-iso` | Task isolation backend (APFS clones, btrfs reflinks, overlayfs) | ~250 |

### Entry Points

1. **Interactive TUI** (`omp`) — default terminal surface with card-based rendering
2. **One-shot** (`omp -p`) — single prompt and exit
3. **RPC** (`omp --mode rpc`) — NDJSON over stdio for non-Node embedders
4. **ACP** (`omp acp`) — Agent Client Protocol for editor integration

## Quick Start

```sh
# Install (macOS · Linux)
curl -fsSL https://omp.sh/install | sh

# Or Homebrew
brew install can1357/tap/omp

# Or Bun
bun install -g @oh-my-pi/pi-coding-agent

# Use from Node/TS
import { createAgentSession, ModelRegistry, SessionManager } from "@oh-my-pi/pi-coding-agent";

const auth = await discoverAuthStorage();
const models = new ModelRegistry(auth);
await models.refresh();

const { session } = await createAgentSession({
  sessionManager: SessionManager.inMemory(),
  authStorage: auth,
  modelRegistry: models,
});
await session.prompt("list .ts files");
```

### Shell Completions

```sh
# zsh
eval "$(omp completions zsh)"

# bash
eval "$(omp completions bash)"

# fish
omp completions fish > ~/.config/fish/completions/omp.fish
```

### Development

```sh
bun setup    # Install workspaces, build Rust/N-API addon
bun dev      # Run from source

# Smoke test
bun dev -- --version
```

## Related

- [[oh-my-pi-architecture]] — Architecture documentation
- [[oh-my-pi-api]] — API reference
- [[oh-my-pi-mcp-implementation]] — MCP server implementation
- [[oh-my-pi-acp-implementation]] — ACP implementation details
- [[oh-my-hermes|Oh My Hermes]] — Multi-agent orchestration skills for Hermes

## Links

- [omp.sh](https://omp.sh) — Website and documentation
- [GitHub](https://github.com/can1357/oh-my-pi) — Source repository
- [npm](https://www.npmjs.com/package/@oh-my-pi/pi-coding-agent) — npm package
- [Discord](https://discord.gg/4NMW9cdXZa) — Community chat
- MIT License