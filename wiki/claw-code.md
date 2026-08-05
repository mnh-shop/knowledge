---
name: claw-code
tags: [claw-code, cli, developer-tools, openclaw, agent-gateway]
description: "Command-line tool for OpenClaw agent interaction and management"
source: sources/claw-code/
verification_date: 2026-07-12
verified_by: codegraph-verify
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
- **Permission Modes** — Five-mode security: `read-only`, `workspace-write`, `danger-full-access`, plus `prompt` (interactive approval) and `allow` (unconditional grant), with a `PermissionPrompter` decision layer for interactive approval
- **Model Aliases** — Built-in aliases for `opus`, `sonnet`, `haiku`, `grok`, `grok-3`, `grok-mini`, `grok-2`, `kimi` (note: `qwen-plus` is NOT a builtin alias — it is a DashScope model name routed by prefix), with user-defined alias support in settings JSON
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
- **ACP Status Surface** — `claw acp` (or `claw --acp`) reports the current ACP/Zed status; no ACP daemon/JSON-RPC entrypoint ships yet, so the command is status-only until real ACP support lands
- **RAG Service** — `claw-rag-service` HTTP daemon for repository indexing (chunking + embeddings in SQLite, optional Qdrant), semantic search, and a minimal web UI
- **Containerized Deploy** — `Containerfile`, `docker-compose.yml` (qdrant + rag-serve + rag-ingest), and `install.sh` for reproducible installs

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

Model selection follows a cascading priority: CLI flag → environment variable → config file → built-in default. The runtime detects the provider via model-name prefix **before** falling back to credential sniffing (`metadata_for_model` in `rust/crates/api/src/providers/mod.rs`):

| Prefix | Provider | Auth env var |
|--------|----------|--------------|
| `claude` / `anthropic/` | Anthropic | `ANTHROPIC_API_KEY` |
| `grok` | xAI | `XAI_API_KEY` |
| `openai/` / `gpt-` | OpenAI-compatible | `OPENAI_API_KEY` |
| `local/` | OpenAI-compatible (local) | `OPENAI_API_KEY` |
| `qwen/` / `qwen-` | DashScope (compatible-mode) | `DASHSCOPE_API_KEY` |
| `kimi/` / `kimi-` | DashScope (compatible-mode) | `DASHSCOPE_API_KEY` |

Prefix routing wins over the auth-sniffer so explicit provider-namespaced models (e.g. `openai/gpt-4.1-mini`) are never misrouted to Anthropic when `ANTHROPIC_API_KEY` is also present.

### Permission System

The `PermissionMode` enum (`rust/crates/runtime/src/permissions.rs`) supports **five** levels: `read-only` (file reads, glob/grep, local skills, status reporting only), `workspace-write` (adds write/edit/notebook/config/plan-mode updates while gating network tools and shell execution), `danger-full-access` (every registered tool including arbitrary commands, web fetch, subagents, and subprocess REPLs), plus:

- `prompt` — requires interactive approval via the `PermissionPrompter` trait (`decide(&mut self, request: &PermissionRequest) -> PermissionPromptDecision`), which evaluates an `allow`/`deny` decision per `PermissionRequest`
- `allow` — unconditional grant for the tool invocation

`PermissionPolicy` evaluates a `PermissionOverride` (Allow/Deny/Ask) supplied by hooks, per-tool mode requirements, allow/deny/ask rule lists, and an unconditional `denied_tools` list — the prompter is the decision layer used when policy requires interactive approval, and `PermissionOutcome` (Allow/Deny) is the final result.

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
| `claw acp` | Report ACP/Zed status (status-only; no ACP daemon yet) |
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

User settings live at **`~/.claw/settings.json`** — the config home resolves from `$CLAW_CONFIG_HOME` when set, otherwise `~/.claw` (`default_config_home()` in `config.rs`). The 5-file discovery chain (`ConfigManager::discover()`), in ascending precedence order:

1. `~/.claw.json` (legacy user-level file)
2. `~/.claw/settings.json` (user settings; `$CLAW_CONFIG_HOME/settings.json` when the env var is set)
3. `<repo>/.claw.json`
4. `<repo>/.claw/settings.json`
5. `<repo>/.claw/settings.local.json`

Project-local files override user-level files. `claw --output-format json config` reports each file's `precedence_rank`, `wins_for_keys`, and `shadowed_keys` so automation can see which file controls each effective key. `save_user_provider_settings()` writes `~/.claw/settings.json` with mode `0o600` to protect stored API keys.

### Dual-Language Repository

The repo contains two parallel implementations:

- **Python reference tree (`src/`)** — ~100 files: `main.py` (argparse entrypoint: `summary`, `manifest`, `parity-audit`, `setup-report`, `command-graph`, `tool-pool`, `bootstrap-graph`), `permissions.py` (`ToolPermissionContext` with `deny_names`/`deny_prefixes`), `session_store.py`, `query_engine.py` (`QueryEnginePort`), `tool_pool.py`, `tools.py`, `hooks/`, `voice/`, `vim/`, `server/`, `remote/`, `bootstrap_graph.py`, `command_graph.py`, `parity_audit.py`. Described in `CLAUDE.md` as the companion/reference workspace — **not the primary runtime surface**.
- **Rust rewrite (`rust/`)** — the canonical implementation per `CLAUDE.md`/README ("The canonical implementation lives in `rust/`"), producing the `claw` binary. `PARITY.md` tracks port parity between the two surfaces; `tests/` contains the Python-side validation suite.

The Python tree is a porting/reference workspace (audit helpers and parity harnesses); all active development targets the Rust workspace.

## RAG Service (`claw-rag-service`)

A separate HTTP service (crate `claw-rag-service`, port **8787**) for repository indexing and semantic search, keeping heavy embedding storage out of the main agent process:

- **SQLite index** (`db.rs`): `chunks`, `embeddings`, and `files` tables; chunk/embedding blobs stored as f32 vectors; `file_is_unchanged`/`upsert_file_meta`/`delete_file_and_chunks` for incremental re-ingest
- **Embeddings** (`embed.rs`): `EmbedConfig::from_env()` with provider support plus a deterministic `mock_vector_for_text()` for offline dev (`CLAW_RAG_MOCK_PROVIDERS=1`)
- **Routes** (`main.rs`): `GET /` (embedded web UI via `static/index.html`), `GET /health`, `GET /v1/stats` (chunk count, phase), `POST /v1/query` (semantic search → `QueryResponse` with `hits[]` with path/snippet/score)
- **Ingest**: `claw-rag-service ingest --db ...` CLI walks a workspace root, chunks files, embeds, upserts; query phase reports `1-sqlite` vs `1-sqlite-no-db`/`1-sqlite-empty`
- **Qdrant optional**: `--features qdrant-index` enables the Qdrant vector index (used by the compose stack)

## Deployment

- **`Containerfile`** (repo root): `rust:bookworm` build image, installs ca-certificates/git/libssl-dev/pkg-config, `WORKDIR /workspace`, `CMD ["bash"]`
- **`docker-compose.yml`**: three services — `qdrant` (vector store on 6333/6334), `rag-serve` (`claw-rag-service serve --db /data/index.sqlite` on 8787, mock embeddings by default), and `rag-ingest` (one-shot `ingest` over the mounted workspace `./:/workspaces/main:ro`)
- **`install.sh`**: OS-detecting installer (Linux/macOS/WSL) that verifies the Rust toolchain, builds the `claw` binary from `rust/`, and runs post-install verification; flags `--release`, `--no-verify`, env overrides `CLAW_BUILD_PROFILE`/`CLAW_SKIP_VERIFY`
- **Windows**: PowerShell-first path documented in `docs/windows-install-release.md` (`claw.exe`)

## Related

- [[openclaw]] — The agent gateway ecosystem that claw-code manages
- [[goclaw]] — Go-based alternative agent gateway
- [[clawpier]] — Desktop GUI for managing OpenClaw Docker containers
- [[hermes-agent]] — Alternative agent gateway with its own CLI
- [[alphaclaw]] — OpenClaw agent harness
- [[oh-my-openagent]] — Multi-agent coordination layer for claw-code
- [[claw-code.python-legacy]] — Companion: Python reference tree map, Rust-rewrite relationship, correction appendix
