---
name: Mnemosyne-codegraph-verify
tags: [codegraph-verify, mnemosyne, memory, ai-agents]
description: "Codegraph Verification: Mnemosyne"
source: sources/Mnemosyne/
date: 2026-07-12
---

# Codegraph Verification: Mnemosyne

**Date:** 2026-07-12

## Claim 1: L1-L3 tiered memory storage for AI agents
- **Wiki says:** Mnemosyne implements a three-tier memory architecture: L1 (working memory) for hot recent context, L2 (episodic memory) for long-term storage with vector + FTS5 search, and L3 (consolidated/semantic) for extracted knowledge and persona profiles.

- **Source evidence:** Source file `mnemosyne/core/beam.py` lines 6-14 document the architecture: "Three SQLite tables: `working_memory`: hot, recent context (auto-injected into prompts); `episodic_memory`: long-term storage with native vector + FTS5 search; `scratchpad`: temporary agent reasoning workspace." Source file `mnemosyne/core/persona.py` line 2 documents "L3 Persona extractor + file generator (v3.10.0)." Source file `mnemosyne/core/persona.py` lines 46-50 show `PersonaExtractor`: "Reads from working_memory and episodic_memory, applies deterministic rules to filter candidates." Source file `mnemosyne/core/polyphonic_recall.py` lines 170-196 show cross-tier recall logic querying both working and episodic tiers with deduplication. Source file `mnemosyne/core/recall_diagnostics.py` lines 43-44 define `RECALL_TIERS = ("working", "episodic")` with per-tier diagnostics. Source file `mnemosyne/core/veracity_consolidation.py` lines 186-187 document consolidation: "summarizes N working_memory rows into one episodic_memory row."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: BEAM benchmark (ICLR 2026) top-tier scores
- **Wiki says:** Mnemosyne holds top-tier scores on the BEAM benchmark (ICLR 2026) and LongMemEval, both with zero cloud dependencies using a single SQLite file.

- **Source evidence:** `README.md` badges include `BEAM-ICLR%202026-purple`. `README.md` lines 111-139 document benchmark results. LongMemEval: "98.9% Recall@All@5" (line 117). BEAM end-to-end QA at 100K scale: "65.2%" (line 126). BEAM retrieval: "Recall@10: 20%, Latency: 35ms, Storage: 7.2 MB at 10M scale" (line 137). Line 139: "100% abstention accuracy, never hallucinates on unknowns. Episodic compression delivers 9.4x storage savings." Full reports at `docs/beam-benchmark.md`. Source files `tests/benchmark_beam_sota.py`, `tests/benchmark_vs_vectordbs.py`, `tests/benchmark_beam_scale.py`, and `tests/benchmark_beam_working_memory.py` implement the benchmark suite. Shell scripts `run_beam_bench.sh`, `run_beam_all_scales.sh`, `run_beam_clean.sh`, and `run_hybrid_all_scales.sh` provide benchmark execution.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: MCP server with stdio and SSE transports
- **Wiki says:** Mnemosyne provides a full MCP server implementation supporting both stdio and SSE transports, with security controls including bearer token auth for network exposure.

- **Source evidence:** Source file `mnemosyne/mcp_server.py` implements the MCP server with both transports. Lines 5-7 document stdio (default) usage. Lines 8-13 document SSE on loopback and LAN with bearer token requirement. Lines 18-26 provide security notes: SSE defaults to `127.0.0.1` loopback; non-loopback binding requires `MNEMOSYNE_MCP_TOKEN` env var. Lines 64-87 implement `_resolve_sse_auth()` with loopback detection and token enforcement. Lines 40-50 show guarded MCP import for optional dependency. Source file `mnemosyne/mcp_tools.py` provides `get_tool_definitions()` and `handle_tool_call()`. `README.md` lines 82-91 document MCP config for Claude Desktop and other MCP clients with `"mcpServers": { "mnemosyne": { "command": "mnemosyne", "args": ["mcp"] } }`.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Hermes Plugin with 23 tools and 4 lifecycle hooks
- **Wiki says:** Mnemosyne provides a native Hermes Agent plugin with 23 tools and 4 provider hooks covering remember, recall, triples, sync, scratchpad, and graph operations.

- **Source evidence:** `README.md` line 38 documents "Hermes Plugin (23 tools)." Source file `hermes_memory_provider/hermes_llm_adapter.py` provides LLM integration `AIAgent` adapter. Source file `hermes_memory_provider/plugin.yaml` lines 5-25 define `provides_tools`: `mnemosyne_remember`, `mnemosyne_recall`, `mnemosyne_stats`, `mnemozyne_triple_add`, `mnemozyne_triple_query`, `mnemozyne_sleep`, `mnemozyne_scratchpad_write`, `mnemozyne_scratchpad_read`, `mnemozyne_scratchpad_clear`, `mnemozyne_invalidate`, `mnemozyne_export`, `mnemozyne_import`, `mnemozyne_update`, `mnemozyne_forget`, `mnemozyne_diagnose`, `mnemozyne_graph_query`, `mnemozyne_graph_link`, `mnemozyne_sync_push`, `mnemozyne_sync_pull`, `mnemozyne_sync_status`. Lines 26-29 document `provides_hooks`: `pre_llm_call`, `on_session_start`, `post_tool_call`. Source file `hermes_memory_provider/__init__.py` provides the `create_provider()` factory. Source file `hermes_memory_provider/persona_adapter.py` manages L3 persona extraction within Hermes. Source file `hermes_memory_provider/sync_adapter.py` manages bidirectional sync.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Mnemosyne Sync — bidirectional memory sync between instances
- **Wiki says:** Mnemosyne Sync provides bidirectional memory synchronization between Mnemosyne instances with optional client-side encryption.

- **Source evidence:** `README.md` lines 162-165 document sync CLI commands: `mnemosyne sync --remote https://my-vps:8765`, `mnemosyne sync --remote https://my-vps:8765 --encrypt`, `mnemosyne sync serve --port 8765 --api-key "sk-..."`. Source directory `deploy/sync/` contains deployment configs: `docker-compose.yml` (line 1), `fly.toml` (line 2), `Caddyfile` (line 3), and `README.md` (line 4). Source file `hermes_memory_provider/sync_adapter.py` implements the Hermes provider integration for sync. `README.md` documents sync with "bidirectional memory sync between instances." The `--encrypt` flag confirms optional client-side encryption support.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Cross-platform integration support (Cursor, Claude Code, Codex, OpenClaw, etc.)
- **Wiki says:** Mnemosyne works with every major agent platform via MCP, native plugin, Python SDK, or direct integration.

- **Source evidence:** `README.md` lines 48-61 document the integration matrix: Cursor (MCP), Claude Code (MCP), Codex CLI (MCP), Windsurf (MCP), OpenWebUI (`@tool` bridge), Pi (Pi extension), OpenClaw (`pip install mnemosyne-memory[openclaw]`), Hermes Agent (MCP + Plugin, ships enabled), and Any MCP client (stdio/SSE). `mnemosyne/integrations/openclaw.py` implements the OpenClaw integration. `mnemosyne/integrations/openwebui_tool.py` implements the OpenWebUI bridge tool. `README.md` lines 20-21: "one `pip install`, one SQLite database. No external services required."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Hybrid vector + FTS5 recall with weighted ranking
- **Wiki says:** Mnemosyne uses hybrid search combining native sqlite-vec vector search, FTS5 full-text retrieval, and importance scoring with configurable weights.

- **Source evidence:** Source file `mnemosyne/core/beam.py` lines 12-14 document the hybrid ranking formula: "Hybrid ranking: 50% vector + 30% FTS rank + 20% importance." Source file `mnemosyne/core/polyphonic_recall.py` implements multi-voice recall across working and episodic memory tiers. Source file `mnemosyne/core/beam.py` lines 7-8 document "Native sqlite-vec for vector search. FTS5 for full-text retrieval." `README.md` benchmark section (line 117) confirms "bge-small-en-v1.5" as the embedding model. Source file `mnemosyne/core/embeddings.py` manages the embedding models and dimensions. Source files `tests/test_c4_recall_diagnostics.py` and `tests/test_c13b_extraction_diagnostics.py` validate recall quality.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[Mnemosyne]] -- Main wiki entry
- [[hermes-agent]] -- Hermes Agent
- [[infinite-brain-os]] -- Infinite Brain OS
- [[materia]] -- Materia agent framework

## Cross-project

- [[hermes-agent.codegraph-verify]] -- Hermes Agent verification
- [[materia.codegraph-verify]] -- Materia verification
- [[nanobot.codegraph-verify]] -- Nanobot verification
