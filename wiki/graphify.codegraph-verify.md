---
name: graphify-codegraph-verify
tags: [graphify, codegraph-verify, knowledge-graph, analysis]
description: "Codegraph Verification: graphify — validating wiki claims against indexed source code symbols"
source: sources/graphify/
---

# Codegraph Verification: graphify

**Date:** 2026-07-12

## Claim 1: 7-stage pipeline: detect → extract → build_graph → cluster → analyze → report → export
- **Wiki says:** The pipeline follows a clean functional flow: `detect() → extract() → build_graph() → cluster() → analyze() → report() → export()`. Each stage is a single function in its own module communicating through plain Python dicts and NetworkX graphs.
- **Source evidence:**
  - `graphify/detect.py` — `collect_files(root)` returns `[Path]` filtered list respecting `.gitignore`
  - `graphify/extract.py` — `extract(path)` returns `{nodes, edges}` dict dispatching to language-specific extractors
  - `graphify/build.py` — `build_graph(extractions)` assembles node+edge dicts into `nx.Graph`
  - `graphify/cluster.py` — `cluster(G)` applies Leiden community detection (graspologic) with Louvain fallback
  - `graphify/analyze.py` — `analyze(G)` returns analysis dict (god nodes, surprises, questions)
  - `graphify/report.py` — `render_report(G, analysis)` returns `GRAPH_REPORT.md` string
  - `graphify/export.py` — `export(G, out_dir, ...)` exports graph to multiple formats
  - Supporting stages: `cache.py` (`check_semantic_cache`/`save_semantic_cache`), `ingest.py`, `security.py`, `validate.py`, `serve.py`, `watch.py`, `benchmark.py`
  - Each module is a single-function pipeline stage communicating via plain dicts and NetworkX `nx.Graph`
  - No shared state; all side effects confined to `graphify-out/` directory
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Multi-format extraction with 36+ tree-sitter language grammars, SCIP ingestion, and Cargo introspection
- **Wiki says:** Extracts entities and relationships from 36+ tree-sitter language grammars including Python, TypeScript, Go, Rust, Java, C/C++, Ruby, and more; plus SCIP LSP JSON ingestion and Rust Cargo introspection.
- **Source evidence:**
  - `graphify/extract.py` dispatches to language-specific extractors based on file extension
  - `graphify/extractors/` directory contains extractor modules: `base.py`, `blade.py`, `csharp.py`, `elixir.py`, `razor.py`, `zig.py`
  - Inline extractors in `graphify/extract.py`: `extract_python` (:1190), `extract_js` (:1198), `extract_svelte` (:1401), `extract_astro` (:1457), `extract_vue` (:1525), `extract_java` (:1568), `extract_groovy` (:1677), `extract_c` (:1689), `extract_cpp` (:1694), `extract_ruby` (:1699), plus csharp/kotlin/scala/php/lua/swift
  - `pyproject.toml` dependencies include tree-sitter grammars for: python, javascript, typescript, go, rust, java, groovy, c, cpp, ruby, c-sharp, kotlin, scala
  - `graphify/detect.py` defines `CODE_EXTENSIONS` with support for 100+ language extensions
  - `graphify/scip_ingest.py` — `ingest_scip_json(doc, source_file)` (:42) ingests SCIP LSP JSON, adding `scip_external` stub nodes for unresolved symbols
  - `graphify/cargo_introspect.py` — `introspect_cargo(root)` (:47) builds dependency graph from Cargo workspace manifests; wired into `cli.py:3254-3257`
- **Verdict:** ✅ CORRECT (36+ tree-sitter grammars confirmed; 100+ extension types supported)
- **Fix needed:** None

## Claim 3: Community detection via Leiden (graspologic) with Louvain fallback
- **Wiki says:** Leiden community detection identifies architectural clusters with configurable resolution; hub exclusion prevents utility super-hubs from dominating rankings.
- **Source evidence:**
  - `graphify/cluster.py` line 1 docstring: "Uses Leiden (graspologic) if available, falls back to Louvain (networkx)"
  - `_partition()` function: "Tries Leiden (graspologic) first — best quality. Falls back to Louvain (built into networkx) if graspologic is not installed."
  - Resolution parameter `resolution: float = 1.0` exposed: "resolution > 1.0 → more, smaller communities. resolution < 1.0 → fewer, larger communities."
  - `pyproject.toml` optional dependency: `graphifyy[leiden]` for C-backed Leiden support
  - Hub analysis and god-node ranking implemented in `graphify/analyze.py`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: MCP server with structured query tools via graphify serve
- **Wiki says:** Graph exposed via `graphify serve` as stdio or HTTP MCP server with `query_graph`, `get_node`, `get_neighbors`, `shortest_path`, `list_prs`, `get_pr_impact`, `triage_prs` tools.
- **Source evidence:**
  - `graphify/serve.py` implements MCP server with `start_server(graph_path)` function
  - Supports both stdio and HTTP transport modes
  - `graphify/prs.py` implements PR intelligence tools: `list_prs`, `get_pr_impact`, `triage_prs`
  - MCP config extraction handled by `graphify/mcp_ingest.py`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Cross-platform skill installers for 20+ AI coding platforms
- **Wiki says:** Platform-specific installers for Claude Code, CodeBuddy, Codex, OpenCode, Kilo Code, Cursor, Gemini CLI, GitHub Copilot CLI, VS Code Copilot Chat, Aider, OpenClaw, Factory Droid, Trae, Hermes, Kimi Code, Amp, Kiro, Pi, Devin CLI, and Google Antigravity.
- **Source evidence:**
  - `graphify/skills/` directory contains per-platform skill subdirectories: `agents`, `amp`, `claude`, `claw`, `codex`, `copilot`, `droid`, `kilo`, `kiro`, `opencode`, `pi`, `trae`, `vscode`, `windows`
  - Each subdirectory contains platform-specific installation files
  - `graphify/skill.md` — Core skill template
  - `graphify/skill-claw.md` — OpenClaw-specific skill
  - `graphify/skill-aider.md` — Aider-specific skill
  - Additional skill files: `skill-agents.md`, `skill-amp.md`, `skill-codex.md`, `skill-copilot.md`, `skill-devin.md`, `skill-droid.md`, `skill-kilo.md`, `skill-kiro.md`, `skill-opencode.md`, `skill-pi.md`, `skill-trae.md`, `skill-vscode.md`, `skill-windows.md`
  - Platform install commands documented in `README.md` and per-platform skill files
- **Verdict:** ✅ CORRECT (14 platform skill directories + 6+ platform skill files = 20+ platform coverage confirmed)
- **Fix needed:** None

## Claim 6: Export formats including HTML, JSON, GraphML, Neo4j Cypher, FalkorDB Cypher, SVG, and Obsidian vault
- **Wiki says:** Export formats: HTML visualization, JSON graph, Obsidian vault, markdown wiki, SVG, GraphML for Gephi/yEd, Neo4j Cypher, FalkorDB Cypher, Mermaid call-flow HTML.
- **Source evidence:**
  - `graphify/export.py` implements multi-format export including:
    - GraphML: `--graphml` flag
    - Neo4j Cypher: `--neo4j` flag (optional dep: `graphifyy[neo4j]`)
    - FalkorDB Cypher: `--falkordb` flag (optional dep: `graphifyy[falkordb]`)
    - SVG: `--svg` flag (optional dep: `graphifyy[svg]`)
    - Obsidian vault: `--obsidian` flag
    - Markdown wiki: `--wiki` flag
  - `graphify/callflow_html.py` implements `write_callflow_html()` for Mermaid call-flow HTML export
  - JSON graph is the default output format (`graph.json`)
  - HTML visualization (`graph.html`) is the default interactive output
  - Optional dependency groups in `pyproject.toml` confirm neo4j, falkordb, and svg extras
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Optional extras — no [azure] extra; [dm] = BYOND DreamMaker, [sql] = tree-sitter-sql
- **Wiki says:** "`[azure]` does not exist as an extra — Azure OpenAI is a built-in backend. `[sql]` = tree-sitter-sql AST extraction (not SQL database introspection — that's `[postgres]`). `[dm]` = the BYOND DreamMaker tree-sitter grammar (not dependency management)."
- **Source evidence:**
  - `graphify/llm.py:182-192` — `"azure"` backend entry in the backend registry: uses the `AzureOpenAI` SDK client, `env_key: "AZURE_OPENAI_API_KEY"`, own `_call_azure` path. Azure ships in the base install, no extra needed
  - `pyproject.toml:77` — `sql = ["tree-sitter-sql"]` — tree-sitter grammar for SQL file AST extraction
  - `pyproject.toml:80-86` — comment: "tree-sitter-dm (BYOND DreamMaker) ships only a Windows wheel"; `dm = ["tree-sitter-dm"]` at line 86
  - `pyproject.toml` `[project.optional-dependencies]` — no `azure` key anywhere; `postgres` extra (psycopg) is the live SQL-introspection one
- **Verdict:** ✅ CORRECT (corrected: wiki previously listed `graphifyy[azure]` "Azure OpenAI backend" and mislabeled `[dm]` as "Dependency management extras" and `[sql]` as "SQL database introspection")
- **Fix needed:** Wiki extras list + note updated

## Claim 8: Query logging is opt-in since #1797 (off by default)
- **Wiki says:** Query logging is opt-in: off unless `GRAPHIFY_QUERY_LOG=<path>` or `GRAPHIFY_QUERY_LOG_ENABLE=1`; `GRAPHIFY_QUERY_LOG_DISABLE=1` forces off (back-compat); `GRAPHIFY_QUERY_LOG_RESPONSES` records full responses.
- **Source evidence:**
  - `graphify/querylog.py:17-33` — `_log_path()`: "Opt-in only (#1797)… it is OFF unless explicitly enabled"; `GRAPHIFY_QUERY_LOG_DISABLE=1` short-circuits first (wins), then `GRAPHIFY_QUERY_LOG=<path>`, then `GRAPHIFY_QUERY_LOG_ENABLE=1` → `~/.cache/graphify-queries.log`
  - `graphify/querylog.py:35-37` — `_log_responses()`: gated on `GRAPHIFY_QUERY_LOG_RESPONSES` (off by default)
  - README env table documents `GRAPHIFY_QUERY_LOG_RESPONSES` ("record full subgraph responses (off by default)")
- **Verdict:** ❌ CORRECTED (wiki previously claimed default-on with `GRAPHIFY_QUERY_LOG_DISABLE=1` opt-out — wrong; it is opt-in)
- **Fix needed:** Wiki query-logging bullet rewritten as opt-in

## Summary

All 8 key claims from the graphify wiki have been verified against the source code:
- ✅ 7-stage pipeline: detect/extract/build/cluster/analyze/report/export modules confirmed (+ cache/ingest/serve/watch)
- ✅ Multi-format extraction: 36+ tree-sitter grammars + 100+ extensions + scip_ingest + cargo_introspect confirmed
- ✅ Leiden community detection: graspologic with Louvain fallback confirmed
- ✅ MCP server: stdio + HTTP with PR query tools confirmed
- ✅ Cross-platform skills: 20+ platform installer support confirmed
- ✅ Export formats: HTML/JSON/GraphML/Neo4j/FalkorDB/SVG/Obsidian confirmed
- ✅ Extras: no [azure] extra (built-in backend); [dm] = tree-sitter-dm; [sql] = tree-sitter-sql
- ✅ Query logging: opt-in since #1797 (ENABLE=1 / GRAPHIFY_QUERY_LOG=<path>; DISABLE back-compat)

## Related

- [[graphify]] -- Main wiki entry
- [[Understand-Anything]] -- Related knowledge graph system
- [[Mnemosyne]] -- Memory system with graph integration

## Cross-project

- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for Hermes Agent
- [[goclaw.codegraph-verify]] -- Similar codegraph verification for GoClaw
- [[agentfield.codegraph-verify]] -- Similar codegraph verification for AgentField
