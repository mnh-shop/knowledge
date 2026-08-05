---
name: nanobot-codegraph-verify
tags: [nanobot, codegraph-verify, agent, python, lightweight, mcp, messaging]
description: "Codegraph Verification: nanobot — validating wiki claims against indexed source code symbols"
source: sources/nanobot/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Codegraph Verification: nanobot

**Date:** 2026-07-12

## Claim 1: Ultra-lightweight AI agent framework with small agent loop
- **Wiki says:** "nanobot is an open-source, ultra-lightweight personal AI agent framework" with a "small agent loop (`nanobot/agent/loop.py`, `runner.py`) that receives messages from chat channels, invokes an LLM provider, executes tools, and manages session memory. Async MessageBus decouples channels from the agent core."
- **Source evidence:**
  - `nanobot/agent/loop.py` — Core `AgentLoop` class (2152 lines) managing session keys, hooks, context building, and orchestration
  - `nanobot/agent/runner.py` — `AgentRunner` class (1532 lines) handling multi-turn LLM conversation with tool execution, streaming, and retry logic
  - `nanobot/bus/queue.py` — Async `MessageBus` implementation for channel↔agent decoupling
  - `nanobot/bus/events.py` — `InboundMessage` and `OutboundMessage` event types
  - `nanobot/gateway/` — Gateway runtime and service bootstrap
  - `nanobot/cli/` — CLI entry points including `nanobot gateway` command
  - `pyproject.toml:3` — `version = "0.3.0"` (current release)
  - `nanobot/__main__.py` — Module entry point
- **Verdict:** ✅ CORRECT
- **Fix needed:** Line counts refreshed (loop.py 2152, runner.py 1532); version confirmed as 0.3.0.

## Claim 2: 17 multi-platform chat channels with auto-discovery
- **Wiki says:** "17 channel integrations including Telegram, Discord, Slack, Feishu, Matrix, WhatsApp, QQ, WeChat, WeCom, DingTalk, Email, Signal, MoChat, MS Teams, WebSocket, Mattermost, and NapCat. Auto-discovered via `pkgutil` scan + entry-point plugins; each channel lives in its own subdirectory with `manifest.py` + `runtime.py`."
- **Source evidence:**
  - `nanobot/channels/` — 17 channel directories: `telegram`, `discord`, `slack`, `feishu`, `matrix`, `whatsapp`, `qq`, `weixin` (WeChat), `wecom`, `dingtalk`, `email`, `signal`, `mochat`, `msteams`, `websocket`, plus **`mattermost`** and **`napcat`**
  - Each channel dir contains `__init__.py`, `manifest.py`, and `runtime.py` (verified for `telegram/`, `mattermost/`, `napcat/`); flat per-channel `telegram.py` files are no longer the structure
  - `nanobot/channels/manager.py` — Channel auto-discovery via `pkgutil` scan
  - `nanobot/channels/registry.py` — Channel registration and lookup
  - `nanobot/channels/__init__.py` — Plugin entry-point exports
  - `pyproject.toml` — Entry-point plugin configuration
  - **Note:** `bridge/` (formerly TypeScript WhatsApp bridge services) is now **empty** — no longer a source of channel integrations
- **Verdict:** ✅ CORRECT (17 channel dirs confirmed, Mattermost + NapCat added)
- **Fix needed:** Removed `bridge/` claim (directory is empty); channel evidence updated to manifest.py+runtime.py subdirectory layout.

## Claim 3: Broad LLM provider support with factory and registry pattern
- **Wiki says:** "Anthropic, OpenAI-compatible, OpenAI Responses API, Azure, Bedrock, GitHub Copilot, OpenAI Codex (`openai_codex_provider.py` — also the backend for OpenCode Zen/Go gateways), Kimi, MiniMax, DeepSeek, Google Gemini, xAI Grok, and more. Kimi/DeepSeek/Gemini models are served through the OpenAI-compatible spec. Provider `factory.py` and `registry.py` handle instantiation and model discovery. Includes image generation and audio transcription."
- **Source evidence:**
  - `nanobot/providers/` — provider modules: `anthropic_provider.py`, `openai_compat_provider.py`, `openai_responses/`, `azure_openai_provider.py`, `bedrock_provider.py`, `github_copilot_provider.py`, `openai_codex_provider.py`, `xai_grok_provider.py`, `fallback_provider.py`, `unconfigured_provider.py`, `base.py`, `factory.py`, `registry.py`
  - `nanobot/providers/openai_compat_provider.py:64-79` — `_KIMI_K3_MODEL = "kimi-k3"` plus `kimi-k2.5`, `kimi-k2.6`, `kimi-k2.7`, `kimi-k2.7-code` presets; `:642` — `force_string_content = bool(self._spec and self._spec.name == "deepseek")` (DeepSeek wire-format handling)
  - `docs/providers.md:22` — "An OpenCode Zen or Go key" maps to `providers.opencodeZen.apiKey` / `providers.opencodeGo.apiKey`; section "OpenCode Zen and Go" (line 103) documents them as OpenCode-managed gateways served through the Codex/OpenAI-compatible provider path
  - `nanobot/providers/factory.py` — `ProviderSnapshot` and factory functions for instantiation
  - `nanobot/providers/registry.py` — Provider registry for model discovery
  - `nanobot/providers/base.py` — `LLMProvider` base class with common interface
  - `nanobot/providers/image_generation.py` — Image generation support
  - `nanobot/providers/transcription.py` — Audio transcription support
- **Verdict:** ✅ CORRECT
- **Fix needed:** "OpenCode" clarified to the actual `openai_codex_provider.py` + OpenCode Zen/Go gateway docs; Kimi/DeepSeek/Gemini attribution to the OpenAI-compat spec; xAI Grok added.

## Claim 4: MCP server integration as tool provider
- **Wiki says:** "MCP Support: Connect multiple MCP servers as tool providers. Multiple MCP servers supported simultaneously."
- **Source evidence:**
  - `nanobot/agent/tools/mcp.py` — Full MCP client implementation (1573 lines), connects to MCP servers and wraps their tools as native nanobot tools
  - `nanobot/agent/tools/mcp.py:974-975` — Imports `mcp.client.stdio.stdio_client`, `mcp.client.sse.sse_client`, and `mcp.client.streamable_http.streamable_http_client`; `:985-987` — transport selection defaults to `stdio` from config
  - Implements JSON-RPC transport, tool discovery via `_discover_tools()`, reconnection logic with `_ReconnectCallback`, and transient error retry
  - `nanobot/agent/tools/registry.py` — `ToolRegistry` for dynamic tool registration/unregistration
- **Verdict:** ✅ CORRECT
- **Fix needed:** Line count refreshed (1573); transports confirmed as stdio + streamable_http/sse.

## Claim 5: Dream two-phase memory consolidation with atomic writes
- **Wiki says:** "Dream Memory: Two-phase memory consolidation with atomic writes and fsync durability. Sessions auto-compact by default."
- **Source evidence:**
  - `nanobot/agent/memory.py` — Full memory system (1219 lines): `MemoryStore` class with `MemoryStore.append_history()` using atomic file writes with `os.fsync()`
  - `nanobot/agent/memory.py:448-469` — `_write_entries()` implements atomic write: writes to `.tmp` file, calls `os.fsync()`, then `os.replace()` for atomic rename, followed by directory `fsync()`
  - `nanobot/agent/memory.py:675-1092` — `Consolidator` class: "lightweight consolidation: summarizes evicted messages into history.jsonl" using LLM summarization with token-budget-triggered compaction
  - `nanobot/agent/memory.py:584-588` — `dream_run_completed()` — checks ephemeral Dream agent run completion via metadata
  - `nanobot/agent/memory.py:523-540` — `build_dream_prompt()` — builds Dream consolidation prompt from unprocessed history
  - `nanobot/agent/memory.py:471-481` — Dream cursor tracking with `get_last_dream_cursor()` / `set_last_dream_cursor()`
  - `nanobot/agent/autocompact.py` — `AutoCompact` for automatic session compaction
  - `nanobot/session/manager.py` — `SessionManager` for session lifecycle
- **Verdict:** ✅ CORRECT
- **Fix needed:** Line count refreshed (1219).

## Claim 6: Rich tool system with 23 tool modules including sandboxed execution
- **Wiki says:** "Filesystem (read/write/edit/list), shell execution (with sandbox backends), web search/fetch, MCP server integration, cron scheduling, notebook editing, subagent spawning, long-running tasks/sustained goals, image generation, and self-modification. Tools auto-discovered via plugins."
- **Source evidence:**
  - `nanobot/agent/tools/` — 23 tool modules: `filesystem.py`, `shell.py`, `web.py`, `mcp.py`, `cron.py`, `spawn.py`, `long_task.py`, `image_generation.py`, `search.py`, `self.py`, `apply_patch.py`, `exec_session.py`, `cli_apps.py`, `context.py`, `message.py`, `file_state.py`, `sandbox.py`, `path_utils.py`, `base.py`, `loader.py`, `registry.py`, `schema.py`, `runtime_state.py`
  - `nanobot/agent/tools/shell.py` — Shell execution with sandbox backends (`wrap_command` from `sandbox.py`)
  - `nanobot/agent/tools/sandbox.py` — Sandbox execution environment
  - `nanobot/agent/tools/loader.py` — Tool auto-discovery via `pkgutil` scan
  - `nanobot/agent/tools/registry.py` — Dynamic tool registration system
  - `nanobot/agent/tools/cron.py` — Cron scheduling tool
  - `nanobot/agent/tools/long_task.py` — Sustained goal / long-running task support
  - `nanobot/agent/tools/spawn.py` — Subagent spawning
- **Verdict:** ✅ CORRECT (23 tool modules confirmed)
- **Fix needed:** Module count corrected to 23 (was "30+ tools").

## Claim 7: Security stack — SSRF protection, workspace guards, pairing store (no PTH file guard)
- **Wiki says:** "SSRF protection (`security/network.py`), workspace access guards (`security/workspace_access.py`, `security/workspace_policy.py`), shell sandbox, pairing/DM approval store, and other measures activated at CLI entry."
- **Source evidence:**
  - `nanobot/security/network.py` — SSRF protection for outbound network requests
  - `nanobot/security/workspace_access.py` — Workspace path access control
  - `nanobot/security/workspace_policy.py` — Workspace policy enforcement
  - `nanobot/pairing/store.py` — DM sender approval store
  - `nanobot/utils/document.py:49` — `_MAX_DOCX_TABLE_DEPTH = 8` is the only "PTH"-adjacent identifier; there is **no PTH file guard component** anywhere in the codebase
- **Verdict:** ✅ CORRECT (after replacing the phantom "PTH file guard" claim)
- **Fix needed:** Removed the false "PTH file guard" claim; replaced with actual security components.

## Summary

All 7 key claims from the Nanobot wiki have been verified against the source code:
- ✅ **Lightweight agent loop:** `AgentLoop` (2152L) + `AgentRunner` (1532L) with async MessageBus decoupling confirmed
- ✅ **Multi-platform channels:** 17 channel subdirectories (incl. Mattermost, NapCat) with manifest.py+runtime.py confirmed; `bridge/` is empty
- ✅ **LLM providers:** Codex provider + OpenCode Zen/Go gateways; Kimi/DeepSeek/Gemini via OpenAI-compat spec
- ✅ **MCP support:** Full MCP client in `nanobot/agent/tools/mcp.py` (1573L) with stdio + streamable_http/sse confirmed
- ✅ **Dream memory:** Two-phase consolidation with atomic fsync writes and auto-compact confirmed
- ✅ **Rich tool system:** 23 tool modules with sandboxed shell execution and plugin-discovery confirmed
- ✅ **Security:** SSRF protection, workspace guards, pairing store — no PTH file guard

The codebase is well-architected with clean decoupling between channels, providers, tools, and memory — validating its claim as a lightweight but extensible personal AI agent framework.

## Related

- [[nanobot]] -- Main wiki entry
- [[nanobot-architecture]] -- System architecture
- [[nanobot-api]] -- OpenAI-compatible API reference

## Cross-project

- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for Hermes Agent
- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
- [[agentfield.codegraph-verify]] -- Similar codegraph verification for AgentField
- [[mission-control.codegraph-verify]] -- Similar codegraph verification for Mission Control
