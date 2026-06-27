---
name: graphify
description: "Knowledge graph generator — turns any input into a persistent knowledge graph with community detection and query tools"
tags: [wiki, python]
source: sources/graphify/
---

# graphify

**graphify** turns any input — code, docs, PDFs, images, videos — into a persistent knowledge graph with community detection, god-node ranking, and query tools. Type `/graphify .` in any AI coding assistant and get `graphify-out/` with an interactive HTML visualization, a queryable JSON graph, and a human-readable report.

## Description

graphify is a Python library and cross-platform AI coding skill backed by Y Combinator (S26). It extracts entities (functions, classes, concepts) and relationships (calls, imports, references) from 36+ tree-sitter language grammars, then applies Leiden community detection to identify architectural clusters. The output includes an interactive HTML visualization (`graph.html`), a queryable JSON graph (`graph.json`), and a report (`GRAPH_REPORT.md`) highlighting god nodes, surprising connections, and suggested questions.

Works in Claude Code, Codex, OpenCode, Kilo Code, Cursor, Gemini CLI, GitHub Copilot CLI, VS Code Copilot Chat, Aider, Amp, OpenClaw, Factory Droid, Trae, Hermes, Kimi Code, Kiro, Pi, Devin CLI, and Google Antigravity — 20+ platforms supported.

## Key Features

- **Multi-format extraction** — Code (36 tree-sitter grammars including Python, TypeScript, Go, Rust, Java, C/C++, CUDA, Ruby, C#, Kotlin, Scala, PHP, Swift, Lua, Zig, Elixir, Erlang, Julia, Vue, Svelte, Astro, Groovy, Dart, Verilog, Fortran, Pascal, SQL, shell/bash, Terraform/HCL, Salesforce Apex, and more), docs (.md .mdx .html .txt .rst .yaml .qmd), Office (.docx .xlsx), PDFs, images (.png .jpg .webp .gif), video/audio (.mp4 .mov .mp3 .wav via faster-whisper + yt-dlp), YouTube URLs, Google Workspace (.gdoc .gsheet .gslides), SQL schemas, PostgreSQL live introspection, BYOND DreamMaker (.dm/.dme), package manifests (pyproject.toml, go.mod, pom.xml, apm.yml), MCP configs
- **Cross-platform skill** — Platform-specific installers for Claude Code, CodeBuddy, Codex, OpenCode, Kilo Code, Cursor, Gemini CLI, GitHub Copilot CLI, VS Code Copilot Chat, Aider, OpenClaw, Factory Droid, Trae, Hermes, Kimi Code, Amp, Kiro, Pi, Devin CLI, Google Antigravity, and Agent Skills (cross-framework)
- **Always-on integration** — Installs PreToolUse hooks (Claude Code, Codex, CodeBuddy, Gemini CLI), native plugins (Kilo Code, OpenCode), instruction files (Cursor .mdc rules, Copilot skill file, Aider AGENTS.md, OpenClaw AGENTS.md, etc.), or persistent `AGENTS.md`/`GEMINI.md`/`CODEBUDDY.md` instructions that guide assistants toward graph-based queries
- **Community detection** — Leiden clustering identifies architectural modules with configurable resolution; god-node ranking surfaces the most-connected concepts; hub exclusion prevents utility super-hubs from dominating rankings
- **Confidence scoring** — Every relationship labeled `EXTRACTED` (explicitly stated), `INFERRED` (reasonable deduction), or `AMBIGUOUS` (uncertain, flagged for review)
- **MCP server** — Graph exposed via `graphify serve` as stdio or HTTP MCP server with structured query tools: `query_graph`, `get_node`, `get_neighbors`, `shortest_path`, `list_prs`, `get_pr_impact`, `triage_prs`
- **Git integration** — `graphify hook install` auto-rebuilds on commit (AST-only, no API cost); merge driver (`graphify merge`) prevents conflict markers in `graph.json` when two devs commit in parallel
- **PR intelligence** — `graphify prs` dashboard shows CI state, review status, worktree mapping; `graphify prs --triage` AI-ranks review queue; `graphify prs --conflicts` surfaces PRs sharing graph communities for merge-order risk analysis
- **Headless extraction** — `graphify extract` for CI pipelines with configurable backend (Claude, Gemini, OpenAI, DeepSeek, Ollama, Bedrock, Azure, Kimi, Claude CLI)
- **Cross-project global graph** — `graphify global add` registers project graphs into a unified global graph; `graphify global query` queries across all registered repos
- **Local-first** — Code extracted via tree-sitter AST (fully offline). Video/audio via faster-whisper (offline). Only docs, PDFs, images require LLM API calls
- **Export formats** — HTML visualization, JSON graph, Obsidian vault (`--obsidian`), markdown wiki (`--wiki`), SVG (`--svg`), GraphML for Gephi/yEd (`--graphml`), Neo4j Cypher (`--neo4j`), FalkorDB Cypher (`--falkordb`), Mermaid call-flow HTML (`graphify export callflow-html`)
- **Watch mode** — `graphify watch` auto-syncs the graph as files change using watchdog file system notifications
- **Query logging** — Every `graphify query`, `path`, `explain`, and MCP `query_graph` call logged to `~/.cache/graphify-queries.log` (JSON Lines); opt-out via `GRAPHIFY_QUERY_LOG_DISABLE=1`

## Architecture

The pipeline follows a clean functional flow — each stage is a single function in its own module communicating through plain Python dicts and NetworkX graphs. No shared state, no side effects outside `graphify-out/`.

```
detect()  →  extract()  →  build_graph()  →  cluster()  →  analyze()  →  report()  →  export()
```

**Core modules:**

| Module | Function | Input → Output |
|--------|----------|----------------|
| `detect.py` | `collect_files(root)` | directory → `[Path]` filtered list (respects `.gitignore` and `.graphifyignore`) |
| `extract.py` | `extract(path)` | file path → `{nodes, edges}` dict (dispatches to language-specific extractors) |
| `build.py` | `build_graph(extractions)` | list of extraction dicts → `nx.Graph` |
| `cluster.py` | `cluster(G)` | graph → graph with `community` attr on each node (Leiden clustering) |
| `analyze.py` | `analyze(G)` | graph → analysis dict (god nodes, surprises, questions) |
| `report.py` | `render_report(G, analysis)` | graph + analysis → `GRAPH_REPORT.md` string |
| `export.py` | `export(G, out_dir, ...)` | graph → Obsidian vault, graph.json, graph.html, graph.svg, GraphML |
| `callflow_html.py` | `write_callflow_html(...)` | graphify-out files → Mermaid architecture/call-flow HTML |
| `ingest.py` | `ingest(url, ...)` | URL → file saved to corpus dir (arXiv, YouTube, etc.) |
| `cache.py` | `check_semantic_cache / save_semantic_cache` | files → (cached, uncached) split for incremental extraction |
| `security.py` | validation helpers | URL / path / label → validated or raises (blocks file:// redirects, size caps) |
| `validate.py` | `validate_extraction(data)` | extraction dict → raises on schema errors |
| `serve.py` | `start_server(graph_path)` | graph file path → MCP stdio/HTTP server |
| `watch.py` | `watch(root, flag_path)` | directory → writes flag file on change (watchdog-based) |
| `benchmark.py` | `run_benchmark(graph_path)` | graph file → corpus vs subgraph token comparison |

**Extraction output schema:**

```json
{
  "nodes": [
    {"id": "unique_string", "label": "human name", "source_file": "path", "source_location": "L42"}
  ],
  "edges": [
    {"source": "id_a", "target": "id_b", "relation": "calls|imports|uses|...", "confidence": "EXTRACTED|INFERRED|AMBIGUOUS"}
  ]
}
```

**Supported backends** for headless semantic extraction: Gemini, Kimi, Claude, OpenAI, DeepSeek, Azure, AWS Bedrock (IAM-based, no API key), Ollama (fully local), Claude CLI binary. Auto-detected from environment variables; `--backend` flag for explicit selection.

## Quick Start

```bash
# Install
uv tool install graphifyy

# Register skill with Claude Code
graphify install

# Build graph for current project
/graphify .

# Query the graph
graphify query "what connects auth to the database?"
graphify path "UserService" "DatabasePool"
graphify explain "RateLimiter"

# Export Mermaid call-flow HTML
graphify export callflow-html

# Start MCP server (stdio)
python -m graphify.serve graphify-out/graph.json

# HTTP server for team sharing
python -m graphify.serve graphify-out/graph.json --transport http --host 0.0.0.0 --port 8080
```

Optional extras for specific capabilities (from `pyproject.toml`):
```bash
uv tool install "graphifyy[pdf]"         # PDF extraction
uv tool install "graphifyy[video]"       # Video/audio transcription + yt-dlp
uv tool install "graphifyy[neo4j]"       # Neo4j push support
uv tool install "graphifyy[ollama]"      # Ollama local inference backend
uv tool install "graphifyy[anthropic]"   # Claude backend via Anthropic API
uv tool install "graphifyy[postgres]"    # Live PostgreSQL introspection
uv tool install "graphifyy[terraform]"   # Terraform/HCL AST extraction
uv tool install "graphifyy[office]"      # Office document extraction
uv tool install "graphifyy[google]"      # Google services integration
uv tool install "graphifyy[mcp]"         # MCP server extras
uv tool install "graphifyy[falkordb]"    # FalkorDB support
uv tool install "graphifyy[svg]"         # SVG rendering support
uv tool install "graphifyy[leiden]"      # Leiden community detection (C backend)
uv tool install "graphifyy[openai]"      # OpenAI backend
uv tool install "graphifyy[gemini]"      # Google Gemini backend
uv tool install "graphifyy[bedrock]"     # AWS Bedrock backend
uv tool install "graphifyy[azure]"       # Azure OpenAI backend
uv tool install "graphifyy[sql]"         # SQL database introspection
uv tool install "graphifyy[dm]"          # Dependency management extras
uv tool install "graphifyy[chinese]"     # Chinese language support
uv tool install "graphifyy[all]"         # Everything
```

## Domain Docs

- [[domains/architecture]] — Architecture domain docs
- [[domains/integration-patterns]] — Integration pattern docs
- [[mcp]] — MCP server configuration extraction and serving graph as MCP tools

## Related

- [[openclaw]] — OpenClaw agent platform; graphify skill installable via `graphify install --platform claw`
- [[hermes-agent]] — Hermes agent; graphify integration via `graphify install --platform hermes`
- [[goclaw]] — Go agent orchestration; integrates graphify for knowledge graph support
- [[zot]] — Go coding agent harness; used with goclaw for agent infrastructure
- [[mission-control]] — Mission control dashboard; graphify supports PR triage and merge conflict detection
- [[podman]] — Podman container engine; graphify supports MCP config extraction from `.mcp.json` files

## Links

- Source: `/Users/admin1/Documents/knowledge/sources/graphify/`
- GitHub: https://github.com/safishamsi/graphify
- Website: https://graphifylabs.ai
- PyPI: https://pypi.org/project/graphifyy/
- Y Combinator: https://www.ycombinator.com/companies/graphify
- Book (The Memory Layer): https://safishamsi.gumroad.com/l/qetvlo
