---
name: claw-code
tags: [claw-code, cli, developer-tools, openclaw, agent-gateway]
description: "Command-line tool for OpenClaw agent interaction and management"
source: sources/claw-code/
---

# Claw Code

| Field | Value |
|---|---|
| **Origin** | [ultraworkers/claw-code](https://github.com/ultraworkers/claw-code) |
| **Source** | `sources/claw-code/` |
| **Repomix** | `raw/claw-code/claw-code.xml` |
| **Codegraph** | `graphs/claw-code/` |

## Overview

Claw Code is a public Rust implementation of the `claw` CLI agent harness, developed by UltraWorkers. It provides a full-featured terminal-based agent with REPL, OAuth, extensive tooling (bash, MCP, plugins), streaming, and integration with Anthropic, OpenAI-compatible APIs, xAI, and DashScope providers. Unlike a conventional application repository, Claw Code is operated as an **agent-managed exhibit** — the harnesses plan, execute, verify, label, and preserve the artifact autonomously, with humans providing direction through a Discord channel rather than a terminal.

The project is built around a three-part coordination system: **OmX** (oh-my-codex, workflow layer providing planning keywords, execution modes, and verification loops), **clawhip** (event and notification router watching git commits, tmux sessions, GitHub issues, and agent lifecycle events), and **OmO** (oh-my-openagent, handling multi-agent coordination with architect/executor/reviewer loops). The philosophy centers on humans setting direction while autonomous "claws" perform the labor.

## Key Features

- **Multi-Provider Support** — Targets Anthropic, OpenAI-compatible, xAI, and DashScope/Qwen backends via model-name prefix routing, with automatic provider detection fallback
- **Interactive REPL** — Full conversational REPL with advanced slash commands (`/ultraplan`, `/teleport`, `/bughunter`, `/skills`, `/doctor`)
- **One-Shot Prompts** — Direct `claw prompt "text"` execution for scripting and CI pipelines, with `--output-format json` support
- **Session Persistence** — Conversations saved under `.claw/sessions/` with `--resume latest` support
- **Permission Modes** — Three-tier security: `read-only` (inspection only), `workspace-write` (safe default with file editing), `danger-full-access` (arbitrary execution)
- **Model Aliases** — Built-in aliases for `opus`, `sonnet`, `haiku`, `grok`, `qwen-plus`, with user-defined alias support in settings JSON
- **Skills System** — Install, list, and invoke skills from disk or companion repositories (`/skills install`, `/skills list`)
- **MCP Server Integration** — Loads `mcpServers` from config with per-entry validation, distinguishing valid/invalid entries with structured JSON output
- **Hook Configuration** — Pre/post tool-use hooks with matcher-based filtering, supporting legacy and object-style hook entries
- **Rule Loading** — Multi-source rules from `CLAUDE.md`, `CLAW.md`, `AGENTS.md`, `.claw/rules/`, plus imported rules from Cursor, Copilot, Windsurf, and Plandex frameworks
- **Proxy Support** — Standard `HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY` env vars plus programmatic `proxy_url` config
- **Local Model Support** — Works with Ollama, llama.cpp, vLLM, or any OpenAI-compatible local endpoint
- **Doctor Diagnostics** — `claw doctor` preflight health check validates API keys, model access, tool configuration, MCP servers, hooks, and project memory files
- **Workspace Init** — `claw init` scaffolds `.claw/settings.json`, `.claw.json`, `.gitignore`, and `CLAUDE.md` with idempotent tracking
- **JSON Output** — Machine-readable structured output for `doctor`, `status`, `config`, `state`, `init`, `mcp`, and diagnostic commands
- **Agent Authoring** — `claw agents create <name>` scaffolds local agent definitions as `.toml` files

## Architecture

Claw Code is a Rust workspace located in `rust/` with the following crate structure:

| Crate | Role |
|---|---|
| `rusty-claude-cli` | Main CLI binary (`claw`) — full user-facing product |
| `api` | Provider clients (Anthropic, OpenAI, xAI, DashScope), streaming, request/response types |
| `runtime` | Sessions, config, `PermissionPolicy`, `PermissionEnforcer`, prompts, MCP integration |
| `tools` | Built-in tool implementations for the full CLI |
| `commands` | Slash commands and operational command routing |
| `plugins` | Plugin system for extensibility |
| `telemetry` | Observability, logging, and diagnostics |
| `claw-analog` | Minimal agent loop with restricted tool surface (read/search/write only) for automation/CI |
| `claw-rag-service` | Separate HTTP service for repository indexing (chunking + embeddings in SQLite), semantic search API, and minimal web UI |
| `mock-anthropic-service` | Deterministic mock for reproducible testing |
| `compat-harness` | Compatibility verification harness |

The logical architecture follows a layered design: a provider abstraction layer at the bottom (Anthropic Messages API, OpenAI Chat Completions wire format), a runtime layer in the middle (session management, config merging, permission enforcement), and the CLI/REPL surface at the top. The RAG service is a separate process communicating over HTTP, keeping heavy indexing and embedding storage out of the main agent process.

### Provider Routing

Model selection follows a cascading priority: CLI flag → environment variable → config file → built-in default. The runtime detects the provider via model name prefix (`claude` → Anthropic, `grok` → xAI, `openai/`/`gpt-` → OpenAI-compatible, `qwen/`/`kimi/` → DashScope) before falling back to credential-based detection.

### Permission System

The `PermissionMode` enum supports three levels: `read-only` (file reads, glob/grep, local skills, status reporting only), `workspace-write` (adds write/edit/notebook/config/plan-mode updates while gating network tools and shell execution), and `danger-full-access` (every registered tool including arbitrary commands, web fetch, subagents, and subprocess REPLs).

## Usage

### Build from Source

```bash
git clone https://github.com/ultraworkers/claw-code
cd claw-code/rust
cargo build --workspace
```

### Quick Start

```bash
# Set API key
export ANTHROPIC_API_KEY="sk-ant-..."

# First-run health check
./target/debug/claw doctor

# One-shot prompt
./target/debug/claw prompt "summarize this repository"

# Interactive REPL
./target/debug/claw
```

### Key Commands

| Command | Description |
|---|---|
| `claw doctor` | Preflight health check (API key, model, tools, MCP) |
| `claw prompt "text"` | One-shot non-interactive prompt |
| `claw init` | Scaffold workspace configuration |
| `claw status` | View workspace state and config |
| `claw state` | Read `.claw/worker-state.json` |
| `claw config` | Show merged config with provenance |
| `claw agents list/create` | Manage local agent definitions |
| `claw skills install/list` | Manage installed skills |
| `claw mcp` | Validate MCP server entries |
| `claw sandbox` | Open sandboxed workspace |
| `claw system-prompt` | Print the resolved system prompt |

### Session Resume

```bash
./target/debug/claw --resume latest
./target/debug/claw --resume latest /status /diff
```

### Permission Mode Selection

```bash
./target/debug/claw --permission-mode read-only prompt "summarize Cargo.toml"
./target/debug/claw --permission-mode workspace-write prompt "update README.md"
./target/debug/claw --permission-mode danger-full-access prompt "run deployment script"
```

### Config File Resolution

Config is loaded in ascending precedence order: `~/.claw.json` → `~/.config/claw/settings.json` → `<repo>/.claw.json` → `<repo>/.claw/settings.json` → `<repo>/.claw/settings.local.json`. Project-local files override user-level files.

## Related

- [[openclaw]] — The agent gateway ecosystem that claw-code manages
- [[goclaw]] — Go-based alternative agent gateway
- [[clawpier]] — Desktop GUI for managing OpenClaw Docker containers
- [[hermes-agent]] — Alternative agent gateway with its own CLI
- [[alphaclaw]] — OpenClaw agent harness
- [[oh-my-openagent]] — Multi-agent coordination layer for claw-code
