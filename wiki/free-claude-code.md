---
name: free-claude-code
description: "Open-source proxy routing Claude Code/Codex traffic to 17 provider backends with multi-model routing"
tags: [wiki, cli, code-assistant, multi-provider, open-source, coding-agent, proxy, python, free-claude-code]
source: sources/free-claude-code/
---

# free-claude-code

> **FCC** is a local proxy that routes Anthropic Messages API traffic (from Claude Code CLI/VS Code/JetBrains ACP) and OpenAI Responses API traffic (from Codex CLI/VS Code) to 17 provider backends. It preserves each client's wire protocol while letting users choose free, paid, or local models through the same proxy and Admin UI.

## Description

Free Claude Code sits as a local proxy between a user's coding agent (Claude Code, Codex, or their VS Code extensions) and an upstream AI provider. It accepts both Anthropic Messages (`/v1/messages`) and OpenAI Responses (`/v1/responses`) protocols, routes requests through a configurable model router, and supports streaming, tool use, thinking/reasoning blocks, and token counting.

The project provides launcher wrappers (`fcc-claude`, `fcc-codex`) that automatically configure the client to target the proxy, stripping inherited credentials and injecting the necessary environment variables. An optional Discord or Telegram messaging bridge turns chat messages into managed CLI sessions.

## Key Features

- **Drop-in proxy** for Claude Code (`/v1/messages`) and Codex (`/v1/responses`)
- **20+ providers**: NVIDIA NIM, OpenRouter, Google AI Studio (Gemini), DeepSeek, Mistral La Plateforme, Mistral Codestral, OpenCode Zen, OpenCode Go, Wafer, Kimi, Cerebras Inference, Groq, Fireworks AI, Z.ai, LM Studio, llama.cpp, and Ollama
- **Per-model tier routing** via `MODEL_OPUS`, `MODEL_SONNET`, `MODEL_HAIKU` overrides with separate thinking toggles per tier
- **Native model picker** support for both Claude Code (`/model`) and Codex (`/model`)
- **Streaming, tool use, thinking/reasoning** block handling with protocol normalization
- **Local Admin UI** at `/admin` for settings, validation, and diagnostics (loopback-only)
- **Optional Discord and Telegram bots** for remote Claude Code sessions with reply-based branching, stop/clear commands, and session persistence
- **Optional voice-note transcription** via local Whisper or NVIDIA NIM Riva gRPC
- **Server-tool support**: local `web_search` and `web_fetch` handling for compatible providers
- **Request optimizations** that short-circuit trivial client probes (quota checks, title generation, suggestion mode) to save latency and quota

## Architecture

FCC has three runtime surfaces:

1. **HTTP proxy** -- FastAPI application exposing Anthropic-compatible routes (`/v1/messages`, `/v1/messages/count_tokens`, `/v1/models`) and OpenAI Responses routes (`/v1/responses`), plus health, stop, and admin endpoints
2. **CLI launchers** -- `fcc-claude` and `fcc-codex` wrapper entrypoints that prepare client environments to target the local proxy
3. **Messaging bridge** -- optional Discord/Telegram adapters that turn chat messages into managed Claude Code CLI sessions

**Request flow**: Claude Code sends Anthropic Messages; Codex sends OpenAI Responses SSE. Responses requests convert to Anthropic Messages internally, then share the same model router, normalizer, and provider adapters. The `ApiRequestPipeline` coordinates routing, message-only intercepts (server tools and optimizations), provider execution, and SSE streaming back to the caller.

**Model routing**: The `ModelRouter` resolves incoming model names. Direct provider refs (`provider/model`) are routed immediately; Claude tier names (`opus`, `sonnet`, `haiku`) use tier-specific overrides; all others fall back to `MODEL`. Thinking can be controlled per tier or globally.

**Provider architecture**: Two transport families exist -- `OpenAIChatTransport` for providers with OpenAI-compatible `/chat/completions` APIs, and `AnthropicMessagesTransport` for providers with Anthropic-compatible `/messages` APIs. Provider metadata is centralized in `config/provider_catalog.py`. Factories live in `providers/registry.py`.

**Package layout**:

| Package | Responsibility |
|---|---|
| `api/` | FastAPI app, routes, request pipeline, model catalog, admin APIs |
| `cli/` | Console entrypoints, client launchers, managed sessions |
| `config/` | Settings, provider metadata, paths, logging |
| `core/` | Provider-neutral protocol logic (Anthropic conversion, SSE, OpenAI Responses) |
| `messaging/` | Discord/Telegram platforms, trees, persistence, voice |
| `providers/` | Provider factories, transports, rate limiting, model listing |
| `tests/` | Deterministic unit and contract tests |
| `smoke/` | Live and local product smoke tests |

## Quick Start

```bash
# Install (macOS/Linux)
curl -fsSL "https://github.com/Alishahryar1/free-claude-code/blob/main/scripts/install.sh?raw=1" | sh

# Start the proxy
fcc-server

# Open the Admin UI at http://127.0.0.1:8082/admin
# Configure a provider (e.g. NVIDIA NIM, OpenRouter, Gemini)

# Launch Claude Code through the proxy
fcc-claude

# Or launch Codex through the proxy
fcc-codex
```

The installer provisions Claude Code and Codex when missing. `fcc-claude` sets `ANTHROPIC_BASE_URL`, gateway model discovery, and a 190k-token auto-compact window. `fcc-codex` injects an ephemeral `fcc` provider with `wire_api = "responses"` targeting the local proxy.

Run from source:
```bash
git clone https://github.com/Alishahryar1/free-claude-code.git
cd free-claude-code
uv run uvicorn server:app --host 0.0.0.0 --port 8082
```

## Domain Docs

No dedicated domain documentation found at [[domains/free-claude-code/]]. See the [[sources/free-claude-code/README.md]] for comprehensive usage documentation.

## Related

- [[mcp]] -- Model Context Protocol for extending agent capabilities
- [[api]] -- HTTP API integration patterns

## Links

- **Source**: [[sources/free-claude-code/]]
- **GitHub**: [Alishahryar1/free-claude-code](https://github.com/Alishahryar1/free-claude-code)
- **License**: MIT
- **Tech stack**: Python 3.14, FastAPI, Uvicorn, Pydantic, Loguru, Ruff, ty