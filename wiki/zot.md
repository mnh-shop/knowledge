---
name: zot
description: "Ultra-lightweight Go coding agent harness — single static binary, 4 run modes, 30+ LLM providers, built-in tools, Telegram bot, extension protocol"
tags: [cli, coding-agent, wiki, zot, golang]
source: sources/zot/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

| Field | Value |
|---|---|
| **License** | MIT |
| **Source** | `sources/zot/` |

# Zot

**Zot** (`github.com/patriceckhart/zot`) is an ultra-lightweight Go coding agent harness designed for composable deployment alongside other Go-based agent infrastructure like [[agentfield]] and [[goclaw]]. It produces a single static binary with zero runtime dependencies, built-in providers for 30+ LLM services, and an extensible subprocess JSON-RPC protocol for adding tools and commands.

## Overview

Zot is a coding agent harness written entirely in Go that packs a full agent runtime into a ~20MB static binary. It supports interactive TUI, one-shot print mode, JSON event streaming, and long-running RPC mode for embedding in third-party applications. The harness includes built-in LLM providers for Anthropic, OpenAI/Codex/Responses, Google Gemini/Vertex, DeepSeek, GitHub Copilot, Amazon Bedrock, Groq, OpenRouter, Mistral, Ollama, and more. It ships with four core tools (`read`, `write`, `edit`, `bash`), a sandbox jail mechanism, Telegram bot integration, session persistence, portable "zotfile" agents, and an extension system that lets you register custom slash commands and tools in any language.

## Key Features

- **Single static binary** — ~20MB Go binary (Go 1.25+), zero runtime dependencies, no database required
- **30+ LLM providers** — Anthropic, OpenAI Chat/Codex/Responses, DeepSeek, Google Gemini/Vertex, GitHub Copilot, Amazon Bedrock, Azure OpenAI, Groq, Cerebras, xAI, Together AI, Hugging Face Router, OpenRouter, Mistral, Z.AI, Xiaomi, MiniMax, Fireworks, Vercel AI Gateway, OpenCode, Cloudflare AI, Ollama/llama.cpp/local models, and Kimi/Moonshot
- **4 built-in tools** — `read` (text/files/images), `write` (create/overwrite), `edit` (exact-match replacements), `bash` (shell commands with timeout)
- **4 run modes** — Interactive TUI (`zot`), Print mode (`zot -p`), JSON streaming (`zot --json`), and RPC daemon (`zot rpc`) for embedding in any language
- **Telegram bot** — Built-in bridge (`zot telegram` or `/telegram` in TUI), polling-based with per-chat queues, file upload support, and automatic token refresh
- **Extension system** — Subprocess JSON-RPC protocol for registering slash commands, exposing tools to the model, intercepting tool calls, gating turns, and rewriting assistant output; extensions in any language
- **Swarm mode** — Multi-agent subprocess orchestration with dashboard, persistent session files, auto-swarm tool for model-driven delegation
- **Go SDK** — Embeddable `packages/agent/sdk/` for Go programs; `Runtime` per project with `Prompt(ctx, text, images)` returning event channels
- **SKILL.md support** — File-based tool definitions for collaborative workflows, discovered at startup and hot-reloadable; ships `examples/skills/` (code-review, test-fix) and a superpowers-style plans/specs pack in `docs/superpowers/`
- **Sandbox path-jailing** — `/jail` command confines read/write/edit/bash to the session cwd; blocks `sudo`, `rm -rf /`, `cd /`, `cd ..`, and similar escapes; persist across launches via the **`jail_by_default`** setting in `/settings`
- **Model auto-discovery** — Background refresh from provider `/v1/models` endpoints, cached for 6h in `$ZOT_HOME/models-cache.json`
- **Custom models/providers** — `models.json` in `$ZOT_HOME` for user-defined models with custom `baseUrl` and API wire format (OpenAI or Anthropic); `--insecure` skips TLS verification for self-signed endpoints
- **`--no-yolo` tool gate** — Confirm every tool call before it runs (interactive TUI only), with per-tool/session persist choices and diff preview for `edit` calls
- **Zotfiles** — Portable agent packages (`.zot` files) bundling instructions, skills, assets, and metadata (runtime, model, permissions); run local dirs/archives or agent directories straight from GitHub without cloning (`docs/zotfiles.md`)
- **Themes** — JSON theme files (user `$ZOT_HOME/themes/*.json` or bundled with extensions) overriding any subset of the built-in light/dark TUI theme (`docs/themes.md`)

## Usage

```bash
# Install (macOS/Linux one-liner)
curl -fsSL https://www.zot.sh/install.sh | bash

# Build from source
git clone https://github.com/patriceckhart/zot
cd zot && make build   # produces ./bin/zot

# Interactive TUI
zot --provider anthropic --model claude-sonnet-4-6

# One-shot (print mode)
echo "list all go files" | zot -p --provider deepseek --model deepseek-v4-pro

# Resume last session
zot --continue

# Telegram bot (standalone daemon)
export ZOT_TELEGRAM_TOKEN="..."
zot telegram --provider anthropic --model claude-opus-4-8

# Embedding (Go in-process)
import "github.com/patriceckhart/zot/packages/agent/sdk"
// One Runtime per project; Prompt(ctx, text, images) returns event channel

# Extensions
zot ext install ./examples/extensions/secret
zot ext list
zot ext doctor   # diagnose load, registration, and conflict issues
```

Slash commands in the TUI include `/login` (API key or OAuth subscription flow for Anthropic, OpenAI Codex, Kimi Code, GitHub Copilot), `/model` (model picker with fuzzy search), `/swarm` (background subagent orchestration), `/jail`/`/unjail` (sandbox toggles), `/compact` (transcript summarization), `/skills` (discovered SKILL.md files), `/session` (export/import/fork/tree), and `/btw` (side chat that doesn't bloat main context).

## Related

- [[opencode]] — Go-based AI coding agent with MCP support and multi-agent orchestration
- [[goclaw]] — Go MCP gateway that can embed zot as an RPC tool bridge
- [[claude-code]] — Anthropic's official coding agent CLI with OAuth protocol reused by zot
- [[free-claude-code]] — Free tier MCP wrapper for Claude Code that can be used alongside zot
- [[agentfield]] — Firecracker micro-VM platform that can embed zot via SDK inside sandboxed environments
- [[hermes-agent]] — Competing agent platform that can delegate coding subtasks to zot via extension protocol
