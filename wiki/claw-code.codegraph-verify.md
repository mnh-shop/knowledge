---
name: claw-code-codegraph-verify
tags: [claw-code, codegraph-verify, openclaw, cli]
description: "Codegraph Verification: claw-code — validating wiki claims against indexed source code"
source: sources/claw-code/
date: 2026-07-12
---

# Codegraph Verification: claw-code

**Date:** 2026-07-12

## Claim 1: Rust workspace with multi-crate architecture and `claw` binary
- **Wiki says:** "Claw Code is a Rust workspace located in `rust/` with 11 crates: rusty-claude-cli (main CLI), api, runtime, tools, commands, plugins, telemetry, claw-analog, claw-rag-service, mock-anthropic-service, compat-harness."

- **Source evidence:**
  - `rust/Cargo.toml` lines 1-3: `[workspace]` with `members = ["crates/*"]` and `resolver = "2"`.
  - `rust/crates/` contains exactly 11 crate subdirectories: `api/`, `claw-analog/`, `claw-rag-service/`, `commands/`, `compat-harness/`, `mock-anthropic-service/`, `plugins/`, `runtime/`, `rusty-claude-cli/`, `telemetry/`, `tools/` — matching the wiki's 11-crate list.
  - `rust/crates/rusty-claude-cli/Cargo.toml` lines 8-9: `[[bin]]` with `name = "claw"` — the CLI binary is `claw`.
  - `rust/crates/runtime/src/` — 47+ source files covering config, permissions, session, MCP, hooks, etc.
  - README.md lines 106-111: "`rust/` — canonical Rust workspace and the `claw` CLI binary".

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Multi-provider routing via model-name prefix + env-credential detection
- **Wiki says:** "The runtime detects the provider via model name prefix (claude/anthropic/ → Anthropic, grok → xAI, openai//gpt- → OpenAI-compatible, qwen/|kimi/ → DashScope) before falling back to credential-based detection. Prefix routing wins over the auth-sniffer."

- **Source evidence:**
  - `rust/crates/api/src/providers/mod.rs` lines 236-243: `metadata_for_model()` routes `canonical.starts_with("claude") || starts_with("anthropic/")` → Anthropic (`ANTHROPIC_API_KEY`)
  - `mod.rs` line 245: `starts_with("grok")` → Xai (`XAI_API_KEY`); line 257: `starts_with("openai/") || starts_with("gpt-")` → OpenAi (`OPENAI_API_KEY`); line 265: `local/` → OpenAi
  - `mod.rs` lines 278-284: `starts_with("qwen/") || starts_with("qwen-")` → DashScope compatible-mode (`DASHSCOPE_API_KEY`); lines 288-294: `kimi/` / `kimi-` → DashScope
  - `mod.rs` lines 253-256: comment explicitly states the prefix branch exists so `detect_provider_kind`'s auth-sniffer order cannot misroute `openai/gpt-4.1-mini` to Anthropic when `ANTHROPIC_API_KEY` is present
  - `rust/crates/api/src/providers/openai_compat.rs` lines 21-23: `DEFAULT_XAI_BASE_URL`, `DEFAULT_OPENAI_BASE_URL`, `DEFAULT_DASHSCOPE_BASE_URL`

- **Verdict:** ✅ CORRECT (expanded with exact prefix/credential pairs)
- **Fix needed:** None

## Claim 3: Five-mode permission system with PermissionPrompter decision layer
- **Wiki says:** "`PermissionMode` has five levels: read-only, workspace-write, danger-full-access, plus prompt (interactive approval) and allow (unconditional grant), evaluated by `PermissionPolicy` with a `PermissionPrompter` decision layer."

- **Source evidence:**
  - `rust/crates/runtime/src/permissions.rs` lines 9-15: `PermissionMode` enum with `ReadOnly`, `WorkspaceWrite`, `DangerFullAccess`, `Prompt`, `Allow` variants
  - `permissions.rs` lines 19-27: `as_str()` returns `"read-only"`, `"workspace-write"`, `"danger-full-access"`, `"prompt"`, `"allow"`
  - `permissions.rs` lines 85-88: `pub trait PermissionPrompter { fn decide(&mut self, request: &PermissionRequest) -> PermissionPromptDecision; }`; lines 78-83 define `PermissionPromptDecision` (Allow / Deny { reason })
  - `permissions.rs` lines 30-36: `PermissionOverride` (Allow/Deny/Ask) hook-provided pre-evaluation override; lines 97-109: `PermissionPolicy` fields (`active_mode`, `tool_requirements`, allow/deny/ask rules, unconditional `denied_tools`)
  - Python tree `src/permissions.py` lines 9-39 also implements `ToolPermissionContext` with `deny_names`/`deny_prefixes`
  - README.md documents permission usage at lines 120-125 (CLI `--permission-mode` examples)
- **Verdict:** ✅ CORRECT (previously described as "three-tier" — fixed to five modes + prompter)
- **Fix needed:** Wiki updated

## Claim 4: Config home `~/.claw` + 5-file hierarchy + builtin model aliases
- **Wiki says:** "User settings live at `~/.claw/settings.json` ($CLAW_CONFIG_HOME when set); 5-file discovery chain; builtin aliases opus/sonnet/haiku/grok/grok-3/grok-mini/grok-2/kimi (qwen-plus NOT a builtin alias)."

- **Source evidence:**
  - `rust/crates/runtime/src/config.rs` lines 1102-1109: `default_config_home()` = `$CLAW_CONFIG_HOME` or `$HOME/.claw` (fallback `.claw`)
  - `config.rs` lines 436-463: `discover()` returns the 5-file chain — `~/.claw.json` (legacy user), `<config_home>/settings.json`, `<cwd>/.claw.json`, `<cwd>/.claw/settings.json`, `<cwd>/.claw/settings.local.json`
  - `config.rs` lines 1111-1113: `save_user_provider_settings()` writes "user-level `~/.claw/settings.json`" with mode `0o600`
  - `rust/crates/api/src/providers/mod.rs` lines 121-203: `MODEL_REGISTRY` builtin aliases — `opus`, `sonnet`, `haiku`, `grok`, `grok-3`, `grok-mini`, `grok-2`, `kimi`
  - `mod.rs` lines 673-676: `"qwen-plus"` appears only in `model_token_limit()` (8,192 max output / 131,072 context) — it is a DashScope model name, not a registry alias
  - `mod.rs` lines 206-231: `resolve_model_alias()` maps aliases to concrete models (e.g. `sonnet` → `claude-sonnet-4-6`, `grok-mini` → `grok-3-mini`, `kimi` → `kimi-k2.5`)
- **Verdict:** ✅ CORRECT (new claim; corrects previous `~/.config/claw/settings.json` and missing-alias errors)
- **Fix needed:** Wiki updated

## Claim 5: Session persistence with `.claw/sessions/<workspace_hash>/` and `--resume latest`
- **Wiki says:** "Conversations saved under `.claw/sessions/<workspace_hash>/` with `--resume latest` support."

- **Source evidence:**
  - `rust/crates/runtime/src/session_control.rs` lines 33-47 (`from_cwd`): on-disk layout `<cwd>/.claw/sessions/<workspace_fingerprint>/`, canonicalized cwd so symlink/relative paths hash identically; lines 55+ `from_data_dir` for `--data-dir`
  - `rust/crates/runtime/src/session.rs` — full session management (`SESSION_VERSION`, `ROTATE_AFTER_BYTES`, `MessageRole` enum)
  - USAGE.md lines 556-557: `./target/debug/claw --resume latest` and `--resume latest /status /diff`; line 552: "REPL turns are persisted under `.claw/sessions/`"
  - `rust/README.md` line 135: `--resume [SESSION.jsonl|session-id|latest]`
  - Python tree `src/session_store.py` mirrors the concept (`StoredSession`, `save_session`/`load_session`)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: MCP per-entry validation and `claw acp` status-only surface
- **Wiki says:** "Loads mcpServers with per-entry validation distinguishing valid/invalid entries; `claw acp` is a status-only discoverability surface until real ACP lands."

- **Source evidence:**
  - `rust/crates/runtime/src/mcp_client.rs` lines 9-16: `McpClientTransport` enum with `Stdio`, `Sse`, `Http`, `WebSocket`, `Sdk`, `ManagedProxy` variants
  - USAGE.md lines 576-596: `claw mcp --output-format json` envelope with `configured_servers`, `valid_count`, `invalid_count`, and `invalid_servers[]` (each with `name`, `error_field`, `reason`); `status` mirrors as `mcp_validation`, `doctor` includes an `mcp validation` check
  - `rust/README.md` line 158: partial MCP config success — valid servers stay in `servers[]`, malformed siblings appear in `invalid_servers[]`
  - `rust/README.md` line 154: "`claw acp` is a local discoverability surface ... reports the current ACP/Zed status without starting the runtime ... `claw acp serve` is only a status alias"; README.md line 102: "claw-code does not ship an ACP/Zed daemon or JSON-RPC entrypoint yet"
  - `rust/README.md` line 144: top-level command list includes `acp [serve]`
- **Verdict:** ✅ CORRECT (expanded; `claw acp` status-only previously unmentioned)
- **Fix needed:** None

## Claim 7: Three-part coordination system (PHILOSOPHY.md) + dual-language repository
- **Wiki says:** "The project is built around OmX (oh-my-codex), clawhip (event and notification router), and OmO (oh-my-openagent); the repo is dual-language — a large Python src/ tree plus the canonical Rust rewrite."

- **Source evidence:**
  - `PHILOSOPHY.md` (uppercase filename, 114 lines) — lines 29-38: OmX (`oh-my-codex`) workflow layer; lines 40-50: clawhip event/notification router; lines 52-57: OmO (`oh-my-openagent`) multi-agent coordination with Architect/Executor/Reviewer convergence loops
  - `PHILOSOPHY.md` lines 21-25: "The real human interface is a Discord channel" / "humans set direction; claws perform the labor"
  - README.md lines 106-111: "`src/` + `tests/` — companion Python/reference workspace and audit helpers; not the primary runtime surface"
  - `src/` on disk contains 100 files: `main.py` (argparse entrypoint with `summary`/`manifest`/`parity-audit`/`setup-report`/`command-graph`/`tool-pool`/`bootstrap-graph` subcommands), `permissions.py`, `session_store.py`, `query_engine.py`, `tool_pool.py`, `tools.py`, `hooks/`, `voice/`, `vim/`, `server/`, `remote/`, `bootstrap_graph.py`, `command_graph.py`, `parity_audit.py`
  - Repo root `CLAUDE.md`: "`rust/` contains the Rust workspace and active CLI/runtime implementation" — Rust is canonical; `PARITY.md` tracks port parity
- **Verdict:** ✅ CORRECT (filename corrected from `philosophy.md` to `PHILOSOPHY.md`; dual-language structure added)
- **Fix needed:** Wiki updated

## Claim 8: Doctor diagnostics, RAG service, and deployment assets
- **Wiki says:** "`claw doctor` preflight writes `.claw/worker-state.json`; claw-rag-service provides SQLite chunking/embeddings + `/v1/stats`/`/v1/query` + web UI; Containerfile, docker-compose.yml, and install.sh exist for deployment."

- **Source evidence:**
  - `rust/crates/runtime/src/worker_boot.rs` lines 928-931: `emit_state_file(worker)` called on state transitions; lines 931-933: "Write current worker state to `.claw/worker-state.json` under the worker's cwd" — the file-based observability surface external observers (clawhip, orchestrators) poll
  - `rust/crates/claw-rag-service/src/main.rs` lines 65-70: `rag_router()` routes `GET /` (embedded `static/index.html` web UI), `GET /health`, `GET /v1/stats`, `POST /v1/query`; port 8787
  - `rust/crates/claw-rag-service/src/db.rs` lines 8-21: SQLite `chunks`, `embeddings`, `files` tables; `embed.rs` lines 7-36: `EmbedConfig::from_env()` + `mock_vector_for_text()` for offline dev
  - `rust/crates/claw-rag-service/Dockerfile`: builder `rust:1.91-bookworm` → `cargo build -p claw-rag-service --release --features qdrant-index` → slim runtime, `EXPOSE 8787`
  - Root `Containerfile`: `rust:bookworm` dev image; `docker-compose.yml`: `qdrant` (6333/6334) + `rag-serve` (8787) + `rag-ingest` with `CLAW_RAG_MOCK_PROVIDERS: "1"`
  - Root `install.sh` lines 6-18: OS-detecting installer (Linux/macOS/WSL) building `claw` from `rust/` with `--release`/`--no-verify` flags and `CLAW_BUILD_PROFILE`/`CLAW_SKIP_VERIFY` overrides
  - README.md lines 96-100: `./target/debug/claw doctor` as first health check; USAGE.md documents `claw doctor` preflight scope
- **Verdict:** ✅ CORRECT (expanded with worker-state file, RAG endpoints, and deployment assets)
- **Fix needed:** None

## Related

- [[claw-code]] -- Main wiki entry
- [[claw-code.python-legacy]] -- Companion: Python reference tree map + correction appendix
- [[openclaw]] -- Agent gateway ecosystem
- [[clawpier]] -- Desktop GUI
- [[goclaw]] -- Go-based agent gateway

## Cross-project

- [[openclaw.codegraph-verify]] -- OpenClaw verification
- [[clawpier.codegraph-verify]] -- Desktop GUI verification
- [[goclaw.codegraph-verify]] -- Go gateway verification
- [[oh-my-openagent.codegraph-verify]] -- Multi-agent coordination verification
