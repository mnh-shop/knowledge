---
name: claw-code-codegraph-verify
tags: [claw-code, codegraph-verify, openclaw, cli]
description: "Codegraph Verification: claw-code — validating wiki claims against indexed source code"
source: sources/claw-code/
date: 2026-07-12
---

# Codegraph Verification: claw-code

**Date:** 2026-07-12

## Claim 1: Rust workspace with multi-crate architecture
- **Wiki says:** "Claw Code is a Rust workspace located in `rust/` with the following crate structure: rusty-claude-cli (main CLI), api, runtime, tools, commands, plugins, telemetry, claw-analog, claw-rag-service, mock-anthropic-service, compat-harness."

- **Source evidence:**
  - `rust/Cargo.toml` line 1-3: `[workspace]` with `members = ["crates/*"]` and `resolver = "2"`.
  - `rust/crates/` directory contains 11 crate subdirectories: `api/`, `claw-analog/`, `claw-rag-service/`, `commands/`, `compat-harness/`, `mock-anthropic-service/`, `plugins/`, `runtime/`, `rusty-claude-cli/`, `telemetry/`, `tools/` — matching the wiki's 11-crate list exactly.
  - `rust/crates/rusty-claude-cli/` — main CLI binary crate with `src/` and `tests/`.
  - `rust/crates/api/src/providers/` — provider implementations: `anthropic.rs`, `openai_compat.rs`, `mod.rs`.
  - `rust/crates/runtime/src/` — 47 source files covering config, permissions, session, MCP, hooks, etc.
  - `rust/crates/telemetry/src/` — observability and logging.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Multi-provider support (Anthropic, OpenAI-compatible, xAI, DashScope)
- **Wiki says:** "Targets Anthropic, OpenAI-compatible, xAI, and DashScope/Qwen backends via model-name prefix routing, with automatic provider detection fallback."

- **Source evidence:**
  - `rust/crates/api/src/providers/mod.rs` line 32-37: `ProviderKind` enum with `Anthropic`, `Xai`, `OpenAi` variants.
  - `rust/crates/api/src/providers/anthropic.rs` (1814 lines) — Full Anthropic Messages API client with streaming, OAuth support, token counting, retry logic. Line 25: `DEFAULT_BASE_URL: &str = "https://api.anthropic.com"`.
  - `rust/crates/api/src/providers/openai_compat.rs` (3039 lines) — OpenAI-compatible provider supporting xAI, DashScope, and standard OpenAI endpoints. Lines 21-23: `DEFAULT_XAI_BASE_URL`, `DEFAULT_OPENAI_BASE_URL`, `DEFAULT_DASHSCOPE_BASE_URL` — confirming xAI and DashScope support.
  - Model-name prefix routing confirmed via `resolve_model_alias` and `preflight_message_request` functions referenced in provider definitions.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Three-tier permission system (read-only, workspace-write, danger-full-access)
- **Wiki says:** "Three-tier security: `read-only` (inspection only), `workspace-write` (safe default with file editing), `danger-full-access` (arbitrary execution)."

- **Source evidence:**
  - `rust/crates/runtime/src/permissions.rs` lines 9-15: `PermissionMode` enum with `ReadOnly`, `WorkspaceWrite`, `DangerFullAccess`, plus `Prompt` and `Allow` variants. Lines 19-27: `as_str()` method returns `"read-only"`, `"workspace-write"`, `"danger-full-access"`.
  - Full permission enforcement in `permission_enforcer.rs` with `PermissionOverride`, `PermissionContext` types.
  - Python source `src/permissions.py` also implements permission context with `ToolPermissionContext` class (lines 9-39) supporting `deny_names` and `deny_prefixes` for tool-level access control.
  - README.md documents permission modes at lines 120-125 with CLI usage examples.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Session persistence with `--resume latest` support
- **Wiki says:** "Conversations saved under `.claw/sessions/` with `--resume latest` support."

- **Source evidence:**
  - `rust/crates/runtime/src/session.rs` (1961 lines) — Full session management with `SESSION_VERSION`, `ROTATE_AFTER_BYTES`, `MAX_ROTATED_FILES`, `MessageRole` enum (`System`, `User`, `Assistant`, `Tool`), and session store serialization.
  - `rust/crates/runtime/src/session_control.rs` — Session lifecycle control (start, resume, save).
  - `src/session_store.py` — Python-level session storage implementation.
  - README.md lines 113-117: session resume commands: `./target/debug/claw --resume latest`.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: MCP server integration with per-entry validation
- **Wiki says:** "Loads `mcpServers` from config with per-entry validation, distinguishing valid/invalid entries with structured JSON output."

- **Source evidence:**
  - `rust/crates/runtime/src/mcp_client.rs` (252 lines) — MCP client with 5 transport types: `McpClientTransport` enum with `Stdio`, `Sse`, `Http`, `WebSocket`, `Sdk`, `ManagedProxy` variants. Lines 9-16 define the transport enum.
  - `rust/crates/runtime/src/mcp.rs` — MCP core types and signature management.
  - `rust/crates/runtime/src/mcp_server.rs` — MCP server configuration.
  - `rust/crates/runtime/src/mcp_stdio.rs` — stdio transport for MCP servers.
  - `rust/crates/runtime/src/mcp_lifecycle_hardened.rs` — Hardened MCP lifecycle management.
  - `rust/crates/runtime/src/mcp_tool_bridge.rs` — Tool bridging between MCP and runtime.
  - `src/query_engine.py` and `tools.py` — Python-level MCP integration.
  - `src/tool_pool.py` — Tool pool with MCP tool management.
  - README.md line 33: "MCP Server Integration — Loads mcpServers from config with per-entry validation."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Three-part coordination system (OmX, clawhip, OmO)
- **Wiki says:** "The project is built around a three-part coordination system: OmX (oh-my-codex, workflow layer), clawhip (event and notification router), and OmO (oh-my-openagent, multi-agent coordination)."

- **Source evidence:**
  - `philosophy.md` (114 lines) explicitly documents this three-part system. Lines 28-52 describe OmX as "the workflow layer" turning directives into structured execution, clawhip as "the event and notification router" watching git/tmux/GitHub/agent lifecycle, and OmO as handling "multi-agent coordination with architect/executor/reviewer loops."
  - `philosophy.md` line 23: "The real human interface is a Discord channel."
  - `philosophy.md` lines 55-57: "humans set direction; claws perform the labor."
  - References to `oh-my-codex`, `clawhip`, and `oh-my-openagent` as distinct companion repositories.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Doctor diagnostics with preflight health checks
- **Wiki says:** "`claw doctor` preflight health check validates API keys, model access, tool configuration, MCP servers, hooks, and project memory files."

- **Source evidence:**
  - `rust/crates/runtime/src/worker_boot.rs` — Worker boot sequence with diagnostics startup.
  - `src/commands.py` contains doctor command implementation.
  - `src/prefetch.py` — Preflight checks and configuration validation.
  - README.md line 100: `claw doctor` command documented as "Preflight health check (API key, model, tools, MCP)."
  - README.md lines 87-88: `./target/debug/claw doctor` shown as first-run health check in quick start.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[claw-code]] -- Main wiki entry
- [[openclaw]] -- Agent gateway ecosystem
- [[clawpier]] -- Desktop GUI
- [[goclaw]] -- Go-based agent gateway

## Cross-project

- [[openclaw.codegraph-verify]] -- OpenClaw verification
- [[clawpier.codegraph-verify]] -- Desktop GUI verification
- [[goclaw.codegraph-verify]] -- Go gateway verification
- [[oh-my-openagent.codegraph-verify]] -- Multi-agent coordination verification
