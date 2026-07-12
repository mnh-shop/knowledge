---
title: free-claude-code.codegraph-verify
description: "Source-level verification of free-claude-code — Free tier MCP wrapper for Claude Code"
date: 2026-07-12
tags: [free-claude-code, codegraph-verify, claude-code, mcp, proxy]
verified_by: codegraph-explore
source: sources/free-claude-code/
---

# free-claude-code — CodeGraph Verification

**Claim-1: Free Claude Code is a middleware proxy that routes Anthropic Messages API traffic (Claude Code) and OpenAI Responses API traffic (Codex) to third-party providers.**

- **Evidence:** `README.md` lines 15-16 state: "Free Claude Code routes Anthropic Messages API traffic from Claude Code (CLI and VS Code extension) and OpenAI Responses API traffic from Codex (CLI and VS Code extension) to any provider." The How It Works section (lines 559-575) explains: "FastAPI exposes Anthropic-compatible routes such as `/v1/messages`, `/v1/messages/count_tokens`, and `/v1/models`, plus OpenAI Responses at `/v1/responses`." The project structure at lines 582-593 confirms the architecture includes `api/` (FastAPI routes), `providers/` (transports and adapters), and `core/openai_responses/` (Responses-to-Anthropic conversion).
- **Source path:** `sources/free-claude-code/README.md`

**Claim-2: The proxy supports 18 provider backends including NVIDIA NIM, OpenRouter, Google AI Studio, DeepSeek, Mistral, Groq, and local models via LM Studio, llama.cpp, and Ollama.**

- **Evidence:** `README.md` lines 60-61 list "18 provider backends: NVIDIA NIM, OpenRouter, Google AI Studio (Gemini), DeepSeek, Mistral La Plateforme, Mistral Codestral, OpenCode Zen, OpenCode Go, Wafer, Kimi, Cerebras Inference, Groq, Fireworks AI, Cloudflare, Z.ai, LM Studio, llama.cpp, and Ollama." The `providers/` directory in source contains 21 subdirectories including `nvidia_nim/`, `open_router/`, `gemini/`, `deepseek/`, `mistral/`, `codestral/`, `opencode/`, `wafer/`, `kimi/`, `cerebras/`, `groq/`, `fireworks/`, `cloudflare/`, `zai/`, `llamacpp/`, `lmstudio/`, and `ollama/`, each with dedicated adapters.
- **Source path:** `sources/free-claude-code/README.md`, `sources/free-claude-code/providers/`

**Claim-3: Free Claude Code provides launcher scripts (`fcc-claude` and `fcc-codex`) that automatically configure Claude Code and Codex to route through the local proxy.**

- **Evidence:** `pyproject.toml` lines 28-33 define entry points: `fcc-server = "cli.entrypoints:serve"`, `fcc-claude = "cli.launchers.claude:launch"`, `fcc-codex = "cli.launchers.codex:launch"`. `README.md` lines 139-151 document the launchers: "`fcc-claude` reads the current configured port and auth token each time it starts, sets the Claude Code environment variables... and then launches the real `claude` command." `fcc-codex` "registers an ephemeral `fcc` model provider that points at the local proxy's `/v1/responses` endpoint, generates a Codex model catalog from the proxy's `/v1/models` response... and then launches the real `codex` command."
- **Source path:** `sources/free-claude-code/pyproject.toml`, `sources/free-claude-code/README.md`

**Claim-4: The proxy supports per-model tier routing for Claude Code (Opus, Sonnet, Haiku) to different providers with a native `/model` picker.**

- **Evidence:** `README.md` lines 359-363 document the mixing feature: "Each model tier can use a different provider by setting `MODEL_OPUS`, `MODEL_SONNET`, and `MODEL_HAIKU in the Admin UI. Leave a tier blank to inherit `MODEL`." Lines 62-63 confirm "Native Claude Code `/model` picker support through the proxy's `/v1/models` endpoint." The README provides a concrete example: "Opus to `nvidia_nim/moonshotai/kimi-k2.6`, Sonnet to `open_router/openrouter/free`, Haiku to `lmstudio/qwen3.5-coder`."
- **Source path:** `sources/free-claude-code/README.md`

**Claim-5: Free Claude Code includes Discord and Telegram bot wrappers for remote Claude Code sessions, plus optional voice-note transcription.**

- **Evidence:** `README.md` lines 481-515 document the messaging integration: "The bot wrapper runs Claude Code sessions remotely, streams progress, supports reply-based conversation branches, and can stop or clear tasks." Configuration requires bot tokens and channel IDs for each platform. Lines 519-555 document optional voice-note transcription via NVIDIA NIM (Riva gRPC) or local Whisper (CPU/CUDA), installable via `--voice-nim`, `--voice-local`, or `--voice-all` flags. The Admin UI includes a dedicated **Messaging** view for configuring both bots and voice. The `messaging/` directory in source confirms the platform-specific runtime implementations.
- **Source path:** `sources/free-claude-code/README.md`

**Claim-6: Free Claude Code runs as a FastAPI/ASGI server with a local Admin UI at `/admin` for configuration management, validation, and provider testing.**

- **Evidence:** `README.md` lines 69-70 state: "Local **Admin UI** at `/admin` to edit supported proxy settings, validate changes, and check providers (loopback access only)." Line 113 shows the startup log output: `INFO:     Admin UI: http://127.0.0.1:8082/admin (local-only)`. The `api/admin_routes.py`, `api/admin_config/`, and `api/admin_static/` modules in the source implement the Admin UI backend. Line 479 confirms "change managed proxy settings only in the **Admin UI** at `/admin`: edit fields, click **Validate**, then **Apply**."
- **Source path:** `sources/free-claude-code/README.md`, `sources/free-claude-code/api/`

**Related:** [[free-claude-code]], [[opencode]], [[claude-code]], [[zot]]
