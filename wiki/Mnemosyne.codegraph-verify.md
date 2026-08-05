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

- **Source evidence:** Source file `mnemosyne/core/beam.py` lines 6-14 document the architecture (BEAM = Bilevel Episodic-Associative Memory): "Three SQLite tables: `working_memory`: hot, recent context (auto-injected into prompts); `episodic_memory`: long-term storage with native vector + FTS5 search; `scratchpad`: temporary agent reasoning workspace." Source file `mnemosyne/core/persona.py` line 2 documents "L3 Persona extractor + file generator (v3.10.0)." Source file `mnemosyne/core/persona.py` lines 46-50 show `PersonaExtractor`: "Reads from working_memory and episodic_memory, applies deterministic rules to filter candidates." Source file `mnemosyne/core/polyphonic_recall.py` lines 170-196 show cross-tier recall logic querying both working and episodic tiers with deduplication. Source file `mnemosyne/core/recall_diagnostics.py` lines 43-44 define `RECALL_TIERS = ("working", "episodic")` with per-tier diagnostics. Source file `mnemosyne/core/veracity_consolidation.py` lines 186-187 document consolidation: "summarizes N working_memory rows into one episodic_memory row."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: BEAM benchmark (ICLR 2026) top-tier scores
- **Wiki says:** Mnemosyne holds top-tier scores on the BEAM benchmark (ICLR 2026) and LongMemEval, both with zero cloud dependencies using a single SQLite file.

- **Source evidence:** `README.md` badges include `BEAM-ICLR%202026-purple`. `README.md` lines 111-141 document benchmark results. LongMemEval: "98.9% Recall@All@5" (line 118). BEAM end-to-end QA at 100K scale: "65.2%" (line 127). BEAM retrieval table (header line 133): "Recall@10: 20%, Latency: 35ms, Storage: 7.2 MB at 10M scale" (line 138). Line 140: "100% abstention accuracy, never hallucinates on unknowns. Episodic compression delivers 9.4x storage savings." Full reports at `docs/beam-benchmark.md`. Source files `tests/benchmark_beam_sota.py`, `tests/benchmark_vs_vectordbs.py`, `tests/benchmark_beam_scale.py`, and `tests/benchmark_beam_working_memory.py` implement the benchmark suite. Shell scripts `run_beam_bench.sh`, `run_beam_all_scales.sh`, `run_beam_clean.sh`, and `run_hybrid_all_scales.sh` provide benchmark execution.

- **Verdict:** ✅ CORRECT
- **Fix needed:** README line refs updated (117→118, 126→127, 137→138, 139→140)

## Claim 3: MCP server with stdio and SSE transports + centralized tool schemas
- **Wiki says:** Mnemosyne provides a full MCP server implementation supporting both stdio and SSE transports, with security controls including bearer token auth for network exposure, and 36 tool schemas centralized in `mnemosyne/tool_schemas.py`.

- **Source evidence:** Source file `mnemosyne/mcp_server.py` implements the MCP server with both transports. Lines 5-7 document stdio (default) usage. Lines 8-13 document SSE on loopback and LAN with bearer token requirement. Lines 18-26 provide security notes: SSE defaults to `127.0.0.1` loopback; non-loopback binding requires `MNEMOSYNE_MCP_TOKEN` env var. Lines 64-87 implement `_resolve_sse_auth()` with loopback detection and token enforcement. Lines 40-50 show guarded MCP import for optional dependency. Source file `mnemosyne/mcp_tools.py` provides `get_tool_definitions()` and `handle_tool_call()`. Source file `mnemosyne/tool_schemas.py` is documented as the "Single source of truth for all Mnemosyne MCP tool schemas" and defines `ALL_TOOL_SCHEMAS` with 36 schema entries (REMEMBER, RECALL, SHARED_*, SLEEP, STATS, INVALIDATE, VALIDATE, GET, TRIPLE_*, CANONICAL_*, SCRATCHPAD_*, EXPORT, UPDATE, FORGET, BATCH, IMPORT, DIAGNOSE, GRAPH_*, SYNC_*, PERSONA_*, HYGIENE_*), with a comment noting the migration to "the ``mcp`` SDK 2.x ``Tool.input_schema`` model field." `README.md` lines 82-91 document MCP config for Claude Desktop and other MCP clients with `"mcpServers": { "mnemosyne": { "command": "mnemosyne", "args": ["mcp"] } }`.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Hermes Plugin provides 20 tools and 3 lifecycle hooks
- **Wiki says:** Mnemosyne provides a native Hermes Agent plugin with 20 tools and 3 provider hooks covering remember, recall, triples, sync, scratchpad, graph, and stats operations.

- **Source evidence:** Source file `hermes_memory_provider/plugin.yaml` lines 5-25 define `provides_tools` — exactly 20 tools: `mnemosyne_remember`, `mnemosyne_recall`, `mnemosyne_stats`, `mnemozyne_triple_add`, `mnemozyne_triple_query`, `mnemozyne_sleep`, `mnemozyne_scratchpad_write`, `mnemozyne_scratchpad_read`, `mnemozyne_scratchpad_clear`, `mnemozyne_invalidate`, `mnemozyne_export`, `mnemozyne_import`, `mnemozyne_update`, `mnemozyne_forget`, `mnemozyne_diagnose`, `mnemozyne_graph_query`, `mnemozyne_graph_link`, `mnemozyne_sync_push`, `mnemozyne_sync_pull`, `mnemozyne_sync_status`. Lines 26-29 define `provides_hooks` — exactly 3 hooks: `pre_llm_call`, `on_session_start`, `post_tool_call`. Note: `README.md` line 38 TOC heading still reads "Hermes Plugin (23 tools)" — a stale badge; `plugin.yaml` is authoritative. Source file `hermes_memory_provider/__init__.py` provides the `create_provider()` factory. Source file `hermes_memory_provider/persona_adapter.py` manages L3 persona extraction within Hermes. Source file `hermes_memory_provider/sync_adapter.py` manages bidirectional sync.

- **Verdict:** ✅ CORRECT (wiki corrected from 23 tools / 4 hooks)
- **Fix needed:** None

## Claim 5: Mnemosyne Sync — bidirectional memory sync between instances
- **Wiki says:** Mnemosyne Sync provides bidirectional memory synchronization between Mnemosyne instances with optional client-side encryption.

- **Source evidence:** `README.md` line 165 headers the sync section: "# Sync (bidirectional memory sync between instances)" and line 166 documents `mnemosyne sync --db-path /path/to/mnemosyne.db --remote https://my-vps:8765`. Line 424 documents `mnemosyne sync serve --port 8765 --api-key "your-secret-key"`. Lines 290-302 document optional client-side encryption: XChaCha20-Poly1305 authenticated encryption where the key never leaves the machine; the remote server sees only metadata. Source directory `deploy/sync/` contains deployment configs: `docker-compose.yml`, `fly.toml`, `Caddyfile`, and `README.md`. Source file `hermes_memory_provider/sync_adapter.py` implements the Hermes provider integration for sync.

- **Verdict:** ✅ CORRECT
- **Fix needed:** README line refs updated (162-165 → 165-166, 424)

## Claim 6: Cross-platform integration support (Cursor, Claude Code, Codex, Pi, OpenClaw, Hermes Tweet, etc.)
- **Wiki says:** Mnemosyne works with every major agent platform via MCP, native plugin, Python SDK, or direct integration — including Pi and the Hermes Tweet companion.

- **Source evidence:** `README.md` lines 47-63 document the integration matrix: Cursor (MCP), Claude Code (MCP), Codex CLI (MCP), Windsurf (MCP), OpenWebUI (`@tool` bridge), Pi (Pi extension + skill — `pi install npm:@mnemosyne-oss/pi-mnemosyne`, line 57), OpenClaw (Native provider — `pip install mnemosyne-memory[openclaw]`), Hermes Agent (MCP + Plugin, ships enabled), Hermes Tweet (Companion plugin for X/Twitter post/account/trend/search context, line 59), Any MCP client (stdio/SSE), and Any Python agent (`import mnemosyne`). `mnemosyne/integrations/openclaw.py` implements the OpenClaw integration. `mnemosyne/integrations/openwebui_tool.py` implements the OpenWebUI bridge tool. `README.md` line 20: "One `pip install`, one SQLite database. No external services required." Line 7: "Zero-dependency AI memory that works everywhere. SQLite-backed. Sub-millisecond."

- **Verdict:** ✅ CORRECT
- **Fix needed:** Platform matrix expanded with Pi + Hermes Tweet rows

## Claim 7: Hybrid vector + FTS5 recall with weighted ranking
- **Wiki says:** Mnemosyne uses hybrid search combining native sqlite-vec vector search, FTS5 full-text retrieval, and importance scoring with configurable weights.

- **Source evidence:** Source file `mnemosyne/core/beam.py` lines 12-14 document the hybrid ranking formula: "Hybrid ranking: 50% vector + 30% FTS rank + 20% importance." Source file `mnemosyne/core/polyphonic_recall.py` implements multi-voice recall across working and episodic memory tiers. Source file `mnemosyne/core/beam.py` lines 7-8 document "Native sqlite-vec for vector search. FTS5 for full-text retrieval." `README.md` benchmark section (line 118) confirms "bge-small-en-v1.5" as the embedding model. Source file `mnemosyne/core/embeddings.py` manages the embedding models and dimensions. Source files `tests/test_c4_recall_diagnostics.py` and `tests/test_c13b_extraction_diagnostics.py` validate recall quality.

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
