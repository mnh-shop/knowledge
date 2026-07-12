---
name: graphify-architecture
tags: [graphify, architecture, knowledge-graph, analysis, tree-sitter, mcp, community-detection]
description: Architecture of graphify — 7-stage knowledge graph pipeline from any input with Leiden community detection and MCP query server
source: sources/graphify/
---

# Graphify Architecture

## Overview

graphify turns any input — code, docs, PDFs, images, videos — into a persistent knowledge graph with community detection, god-node ranking, and query tools. It extracts entities (functions, classes, concepts) and relationships (calls, imports, references) from 36+ tree-sitter language grammars, then applies Leiden community detection to identify architectural clusters. Output includes interactive HTML visualization, queryable JSON graph, and human-readable report. The project is backed by Y Combinator (S26) and works across 20+ AI coding platforms.

## Architecture

The pipeline follows a clean functional flow — each stage is a single function in its own module communicating through plain Python dicts and NetworkX graphs:

```
detect() → extract() → build_graph() → cluster() → analyze() → report() → export()
```

### Stage Details

1. **detect** (`detect.py`) — `collect_files(root)` walks a directory, returns a filtered `[Path]` list respecting `.gitignore` and `.graphifyignore`. Handles code files, docs, PDFs, images, videos, and binary formats.

2. **extract** (`extract.py`) — `extract(path)` dispatches to language-specific extractors (tree-sitter AST for code, LLM for docs/PDFs/images). Returns `{nodes, edges}` dict with confidence labels: `EXTRACTED` (explicit), `INFERRED` (deduced), `AMBIGUOUS` (flagged).

3. **build_graph** (`build.py`) — `build_graph(extractions)` merges all extraction dicts into a single `nx.Graph`. Deduplicates nodes by ID, merges edges with confidence scoring.

4. **cluster** (`cluster.py`) — `cluster(G)` applies **Leiden community detection** with configurable resolution. Adds `community` attribute to each node. Optional hub exclusion prevents utility super-hubs from dominating.

5. **analyze** (`analyze.py`) — `analyze(G)` computes god-node ranking (most-connected entities), surprising connections (cross-community edges), and suggested research questions.

6. **report** (`report.py`) — `render_report(G, analysis)` generates a `GRAPH_REPORT.md` string with architecture summary, key entities, cluster breakdown, and questions.

7. **export** (`export.py`) — `export(G, out_dir, ...)` writes to multiple formats: HTML visualization, JSON graph, Obsidian vault, markdown wiki, SVG, GraphML, Neo4j Cypher, FalkorDB Cypher, and Mermaid call-flow HTML.

### MCP Server

`serve.py` exposes the graph as an MCP server (stdio or HTTP) with structured query tools:

| Tool | Description |
|------|-------------|
| `query_graph` | Natural language graph queries |
| `get_node` | Full node details with neighbors |
| `get_neighbors` | Direct connections of a node |
| `shortest_path` | Path between any two nodes |
| `list_prs` | PR dashboard with CI state |
| `get_pr_impact` | Impact analysis for a PR |
| `triage_prs` | AI-ranked review queue |

## Key Components

- **tree-sitter extractors** — 36+ language grammars for offline, offline-capable AST extraction. No API calls needed for code analysis.
- **Leiden community detection** — Identifies architectural modules with configurable resolution. C backend (`graphifyy[leiden]`) for performance.
- **Multi-format ingestion** — Code, Markdown, Office docs, PDFs, images (LLM-described), video/audio (faster-whisper + yt-dlp), SQL schemas, PostgreSQL live introspection, package manifests.
- **Semantic cache** (`cache.py`) — Incremental extraction: unchanged files skip re-processing. Check `check_semantic_cache` before extraction.
- **Git integration** — `graphify hook install` auto-rebuilds on commit; merge driver prevents conflicts in `graph.json`.
- **Cross-project global graph** — `graphify global add` unifies multiple project graphs into a single queryable graph.

## Related

- [[graphify]] — Wiki overview of the project
- [[Understand-Anything]] — Related analysis tool
- [[Mnemosyne]] — Memory system (complementary knowledge persistence)
- [[openclaw]] — Agent platform that hosts graphify as a skill
- [[hermes-agent]] — Agent platform with graphify integration
- [[mcp]] — MCP protocol used by graphify's query server
