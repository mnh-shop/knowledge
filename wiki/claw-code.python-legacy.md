---
name: claw-code.python-legacy
description: "Python legacy companion for claw-code — the src/ reference tree map, its relationship to the canonical Rust rewrite, and the correction appendix (config home, five-mode permissions, alias list, acp status, rag-service, deployment)"
source: sources/claw-code/
parent: claw-code
verification_date: 2026-07-12
verified_by: codegraph-verify
tags: [claw-code, python, rust, legacy, openclaw, cli, reference]
---

# claw-code — Python Reference Tree (Legacy Companion)

Companion to [[claw-code]]. Documents the Python `src/` tree that lives alongside the canonical Rust workspace, and records the corrections applied to the main wiki against source truth.

## Dual-Language Layout

```
claw-code/
├── rust/          ← canonical implementation (Rust workspace, `claw` binary)
├── src/           ← Python reference/porting workspace (~100 files)  ← this doc
├── tests/         ← Python-side validation surface (mirrors src/)
├── Containerfile  ← rust:bookworm dev image
├── docker-compose.yml
├── install.sh
├── PHILOSOPHY.md  ← project intent (OmX / clawhip / OmO)
├── PARITY.md      ← Rust-port parity status
└── ROADMAP.md
```

README.md lines 106-111 are explicit: "`rust/` — canonical Rust workspace and the `claw` CLI binary" and "`src/` + `tests/` — companion Python/reference workspace and audit helpers; not the primary runtime surface." Repo-root `CLAUDE.md` repeats the split: "`rust/` contains the Rust workspace and active CLI/runtime implementation." The Python tree is a **porting workspace** used to model behavior that the Rust port then implements; it is not the product.

## Python Tree Map

100 files under `src/`, centered on an argparse entrypoint and a set of "port" modules:

| Path | Role |
|------|------|
| `main.py` | Argparse entrypoint — subcommands: `summary`, `manifest`, `parity-audit`, `setup-report`, `command-graph`, `tool-pool`, `bootstrap-graph` |
| `bootstrap_graph.py` | Mirrors the bootstrap/runtime graph stages (mirrors Rust `worker_boot.rs`) |
| `command_graph.py` | Command graph segmentation (mirrors Rust `commands` crate) |
| `commands.py` | `execute_command`, `get_command`, `get_commands`, `render_command_index` |
| `permissions.py` | `ToolPermissionContext` — frozen dataclass with `deny_names` (frozenset) + `deny_prefixes` (tuple) `blocks(tool_name)` check, plus `WorkspacePathScope` from `path_scope.py` |
| `session_store.py` | `StoredSession` dataclass (`session_id`, `messages`, `input_tokens`, `output_tokens`); `save_session`/`load_session` as JSON under `.port_sessions/` |
| `query_engine.py` | `QueryEnginePort` + `QueryEngineConfig` (`max_turns` 8, `max_budget_tokens` 2000, `compact_after_turns` 12); `TurnResult` with `matched_commands`/`matched_tools`/`permission_denials` |
| `tool_pool.py` | `ToolPool` + `assemble_tool_pool(simple_mode, include_mcp)` — markdown render of tool inventory |
| `tools.py` | `execute_tool`, `get_tool`, `get_tools`, `render_tool_index`; `build_tool_backlog` |
| `prefetch.py` | Preflight checks / setup report (mirrors `claw doctor` surface) |
| `parity_audit.py` | `run_parity_audit()` — compares Python workspace against the archived TypeScript surface |
| `port_manifest.py` | `PortManifest`, `build_port_manifest` |
| `runtime.py` / `remote_runtime.py` | `PortRuntime`; `run_remote_mode` / `run_ssh_mode` / `run_teleport_mode` |
| `hooks/`, `voice/`, `vim/`, `server/`, `remote/`, `assistant/`, `entrypoints/` | Package dirs (each with `__init__.py`) |
| `models.py`, `transcript.py`, `history.py`, `context.py`, `cost_tracker.py`, `execution_registry.py`, `migrations/`, `schemas/`, `types/`, `utils/`, `state/`, `services/`, `skills/`, `plugins/`, `bootstrap/`, `buddy/`, `bridge/`, `cli/`, `components/`, `coordinator/`, `keybindings/`, `memdir/`, `moreright/`, `native_ts/`, `outputStyles/`, `reference_data/`, `screens/`, `setup.py`, `system_init.py`, `task.py`, `tasks.py`, `upstreamproxy/`, `dialogLaunchers.py`, `direct_modes.py`, `ink.py`, `interactiveHelpers.py`, `path_scope.py`, `projectOnboardingState.py`, `replLauncher.py`, `_archive_helper.py`, `costHook.py`, `deferred_init.py`, `query.py` | Supporting port-modeling modules |

## Relationship to the Rust Rewrite

- **Rust is canonical.** Active development, the `claw` binary (`rusty-claude-cli/Cargo.toml:8-9`), and the product surface all live in `rust/` (11 crates).
- The Python tree is a **reference/porting surface**: each module models a behavior the Rust port reimplements (permissions → `permissions.rs`, sessions → `session.rs`/`session_control.rs`, tool registry → `tools` crate, doctor → `worker_boot.rs`, MCP → `mcp_client.rs`).
- `tests/` (Python) contains validation surfaces kept consistent with `src/`; `PARITY.md` tracks Rust-port parity; `scripts/` (`fmt.sh`) formats the Rust side; `mock-anthropic-service` crate gives the Rust port deterministic test responses.
- **Practical consequence:** when reading this repo, treat `rust/` as the source of truth for behavior and `src/` as the historical/reference model. Do not patch `src/` to fix product behavior — port the change into the Rust workspace.

## Correction Appendix

Errors fixed in the main wiki ([[claw-code]]) against source truth:

| # | Old (incorrect) | New (verified) | Evidence |
|---|---|---|---|
| 1 | Config home `~/.config/claw/settings.json` | User settings at `~/.claw/settings.json`; `$CLAW_CONFIG_HOME` overrides | `config.rs:1104-1109` `default_config_home()` |
| 2 | "Three-tier" permissions (read-only / workspace-write / danger-full-access) | **Five** modes: `ReadOnly`, `WorkspaceWrite`, `DangerFullAccess`, `Prompt`, `Allow` + `PermissionPrompter` trait | `permissions.rs:9-15`, `:85-88` |
| 3 | Aliases "opus, sonnet, haiku, grok, qwen-plus" | Builtin aliases: `opus`, `sonnet`, `haiku`, `grok`, `grok-3`, `grok-mini`, `grok-2`, `kimi`; `qwen-plus` is a DashScope **model name** (token limits only, `mod.rs:673`), not an alias | `providers/mod.rs:121-203` `MODEL_REGISTRY` |
| 4 | (missing) | `claw acp` is **status-only** until real ACP/Zed lands; `claw acp serve` is a discoverability alias | `rust/README.md:154`, README.md:102 |
| 5 | (missing) | `claw-rag-service`: SQLite `chunks`/`embeddings`/`files` tables, routes `GET /` (web UI) `/health` `/v1/stats` `POST /v1/query`, port 8787, optional Qdrant feature | `claw-rag-service/src/main.rs:65-70`, `db.rs:8-21` |
| 6 | (missing) | Deployment assets: `Containerfile` (rust:bookworm), `docker-compose.yml` (qdrant + rag-serve + rag-ingest), `install.sh` (Linux/macOS/WSL builder) | repo root files |
| 7 | Provider routing vague | Prefix table: `claude`/`anthropic/`→Anthropic, `grok`→Xai, `openai/`/`gpt-`→OpenAi, `local/`→OpenAi, `qwen/`/`qwen-`+`kimi/`/`kimi-`→DashScope; prefix wins over auth-sniffer | `providers/mod.rs:236-294` |
| 8 | (missing) | Dual-language repo: Python `src/` tree (~100 files) + canonical Rust rewrite | README.md:106-111, root `CLAUDE.md` |

## Related

- [[claw-code]] — Main wiki entry
- [[claw-code.codegraph-verify]] — Source-verified claims
- [[openclaw]] — Agent gateway ecosystem
- [[oh-my-openagent]] — Multi-agent coordination layer
- [[clawpier]] — Desktop GUI for OpenClaw containers
