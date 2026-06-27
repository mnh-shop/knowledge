---
name: zot
description: "Ultra-lightweight Go coding agent harness — single static binary, 25+ LLM providers, built-in tools, Telegram bot, extension protocol"
tags: [cli, coding-agent, wiki, zot, golang]
source: sources/zot/
---

# Zot

**Zot** (`github.com/patriceckhart/zot`) is an ultra-lightweight Go coding agent harness designed for composable deployment alongside other Go-based agent infrastructure like [[agentfield]] and [[goclaw]]. It produces a single static binary with zero runtime dependencies.

## Features

- **Single static binary** — ~20MB, Go, zero runtime dependencies, no database
- **25+ LLM providers** — Anthropic, OpenAI, Gemini, Groq, xAI, OpenRouter, Together, Bedrock, Vertex AI, GitHub Copilot, DeepSeek, and more
- **4 built-in tools** — `read`, `write`, `edit`, `bash` with sandbox path-jailing
- **3 run modes** — Interactive TUI (`zot`), one-shot print (`zot --print`), JSON RPC (`zot rpc`)
- **Telegram bot** — Built-in (`zot telegram`), polling-based, per-chat queues, file uploads
- **Extension system** — Subprocess JSON-RPC protocol for tool/command registration, event interception, and interactive panels
- **Swarm mode** — Multi-agent subprocess orchestration with JSONL event protocol
- **Go SDK** — Embeddable in Go programs (`packages/agent/sdk/`)
- **SKILL.md support** — File-based tool definitions for collaborative workflows
- **Sandbox** — Path-jailing for safe bash execution
- **Model auto-discovery** — Background refresh from provider `/v1/models` endpoints

## Go Ecosystem Integration

Zot is written entirely in Go, making it a natural companion to other Go-based services in the vault:

- [[agentfield]]: Embed zot via SDK inside micro-VM sandboxes for isolated code execution
- [[goclaw]]: Wire zot as an RPC tool bridge for lightweight coding workers
- [[hermes-agent]]: Delegate coding subtasks to zot via the extension protocol or SKILL.md

## Domain Docs

- [[zot-architecture]] — Go architecture, run modes, tool system, extension protocol, swarm
- [[zot-mcp-implementation]] — Extension protocol as MCP-adjacent tool surface
- [[zot-acp-implementation]] — Swarm multi-agent orchestration
- [[zot-api]] — Telegram bot API, JSON-RPC protocol, Go SDK
- [[zot-deployment]] — Single-binary deployment, container images, systemd, Podman Quadlet

## Quick Start

```bash
# Build
cd sources/zot && go build -o zot ./cmd/zot

# Interactive TUI
./zot --provider anthropic --model claude-sonnet-4-6

# One-shot
echo "list all go files" | ./zot --print --provider anthropic --model claude-sonnet-4-6

# Telegram bot
export ZOT_TELEGRAM_TOKEN="..."
./zot telegram --provider anthropic --model claude-opus-4-8

# RPC mode (for goclaw/agentfield integration)
export ZOTCORE_RPC_TOKEN="secret"
./zot rpc --provider anthropic --model claude-sonnet-4-6

# Install an extension
./zot ext install ./examples/extensions/secret
```

## Links

- **Source**: `sources/zot/` in the vault (`.codegraph/` indexed)
- **Website**: [www.zot.sh](https://www.zot.sh)
- **Repository**: [patriceckhart/zot](https://github.com/patriceckhart/zot)
