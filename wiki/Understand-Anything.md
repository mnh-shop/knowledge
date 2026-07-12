---
name: Understand-Anything
tags: [understand-anything, code-analysis, research, ai-agents, code-comprehension]
description: "Universal codebase comprehension and analysis tool for AI"
source: sources/Understand-Anything/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Understand-Anything

| Field | Value |
|---|---|
| **Origin** | [uwejav/Understand-Anything](https://github.com/uwejav/Understand-Anything) |
| **Source** | `sources/Understand-Anything/` |
| **Repomix** | `raw/Understand-Anything/Understand-Anything.xml` |
| **Codegraph** | `graphs/Understand-Anything/` |

## Overview

Understand-Anything is an open-source codebase comprehension tool (originally by Egonex-AI / Lum1104) that combines LLM intelligence with tree-sitter-based static analysis to turn any codebase, knowledge base, or documentation set into an interactive knowledge graph. It functions as a **Claude Code Plugin** and also supports 17+ AI coding platforms through a universal install script — Codex, OpenCode, OpenClaw, Gemini CLI, Cursor, VS Code Copilot, Copilot CLI, Pi Agent, Vibe CLI, Hermes, Cline, KIMI CLI, Trae, Nanobot, Kiro, and Antigravity.

The core idea is to address the fundamental onboarding problem: when joining a new team or revisiting a project after months away, developers face hundreds of thousands of lines of code with no structured map. Understand-Anything builds exactly that map — a knowledge graph where every file, function, class, and dependency is a searchable, clickable node with plain-English summaries, architectural layer assignments, and guided learning tours.

The project targets a hybrid analysis model: **tree-sitter (deterministic)** for structural facts (imports, exports, definitions, call sites) and **LLM (semantic)** for what parsers cannot produce — code intent, architectural role, business-domain mapping, and natural-language explanations. This split means the graph's structural edges are reproducible (same code yields the same graph), while its semantic content captures developer intent.

## Key Features

- **Multi-Language Parsing** — AST-based analysis via tree-sitter WASM supporting Python, JavaScript, TypeScript, Go, Rust, Java, and more. Uses `web-tree-sitter` (WASM) instead of native bindings to avoid platform compatibility issues on darwin/arm64 + Node 24
- **Interactive Knowledge Graph Dashboard** — A React + TypeScript web dashboard (React Flow, Zustand, TailwindCSS v4) with a dark luxury theme, 75% graph + 360px sidebar layout, color-coded by architectural layer, with fuzzy and semantic search
- **Multi-Agent Analysis Pipeline** — `/understand` orchestrates 5 specialized agents: `project-scanner` (file discovery, language detection), `file-analyzer` (extract functions, classes, imports), `architecture-analyzer` (layer identification), `tour-builder` (guided learning walks), and `graph-reviewer` (structural validation). `/understand-domain` adds a 6th `domain-analyzer` agent for business domain extraction. `/understand-knowledge` adds an article-analyzer for wiki relationship extraction
- **Incremental Analysis** — Subsequent runs only re-analyze changed files using fingerprint-based change detection. Intermediate results are cached in the data directory's `intermediate/` subdirectory and cleaned up after graph assembly
- **Diff Impact Analysis** — Visualizes which parts of the system changes affect before committing, showing ripple effects across the codebase
- **Knowledge Base Analysis** — The `/understand-knowledge` command accepts a Karpathy-pattern LLM wiki directory, deterministically extracts wikilinks and categories from `index.md`, then uses LLM agents to discover implicit relationships, extract entities, and surface claims
- **Persona-Adaptive UI** — The dashboard adjusts detail level based on viewer role (junior dev, PM, power user) through adjustable personas
- **Multi-Platform Support** — Works across 17+ AI coding platforms via a universal install script, with platform-specific invocation prefixes (e.g., `/understand` on Claude Code, `$understand` on Codex)
- **Team Sharing** — The knowledge graph is just JSON. Committing it to the repository lets teammates skip the analysis pipeline, suitable for onboarding, PR reviews, and docs-as-code. Large graphs (10MB+) can use git-lfs

## Architecture

Understand-Anything is a pnpm monorepo with three main packages:

```
understand-anything-plugin/
├── packages/core/          — Shared analysis engine
│   ├── src/search/         — Graph search implementation
│   ├── src/schema/         — Graph schema and validation
│   ├── src/tree-sitter/    — WASM-based parser integration
│   └── src/tours/          — Guided tour generation
├── packages/dashboard/     — React + TypeScript web dashboard
│   ├── src/                — React Flow graph, Zustand state, sidebar panels
│   └── vite.config.ts      — Dev server with file-content middleware
├── src/                    — Skill TypeScript source
│   ├── understand-chat/    — `/understand-chat` command
│   ├── understand-diff/    — `/understand-diff` command
│   └── understand-explain/ — `/understand-explain` command
├── skills/                 — Skill definitions
│   ├── understand.json     — `/understand` command
│   ├── understand-dashboard.json
│   └── ...
├── agents/                 — Agent definitions
│   ├── project-scanner.json
│   ├── file-analyzer.json
│   ├── architecture-analyzer.json
│   ├── tour-builder.json
│   └── graph-reviewer.json
└── viewer/                 — Standalone graph viewer (npx-publishable)
```

### Hybrid Analysis Pipeline

The `/understand` command runs in two phases:

**Phase 1 — Deterministic parsing:** Tree-sitter parses every source file into a concrete syntax tree. Structural facts (imports, exports, function/class definitions, call sites, inheritance) are extracted deterministically. An `importMap` is pre-resolved during scanning and passed to file analyzers to avoid re-deriving imports from source. Fingerprint-based change detection enables incremental re-analysis.

**Phase 2 — Semantic enrichment:** LLM agents read the parsed structures alongside source code to produce plain-English summaries, tags, architectural layer assignments, file responsibilities, business-domain mapping, guided tours, and programming-language concept callouts. File analyzers run in parallel (up to 5 concurrent, 20-30 files per batch).

### Knowledge Graph Format

The graph is saved to `.ua/knowledge-graph.json` (or legacy `.understand-anything/` directory when present). Each node represents a file, function, class, or architectural concept with edges encoding imports, calls, inheritance, and containment. The format includes schema validation on load with an error banner for corruption detection.

## Installation

Claude Code native installation:
```
/plugin marketplace add Egonex-AI/Understand-Anything
/plugin install understand-anything
```

Universal installation for all other platforms:
```bash
curl -fsSL https://raw.githubusercontent.com/Egonex-AI/Understand-Anything/main/install.sh | bash -s <platform>
```

Supported platforms: `codex`, `opencode`, `openclaw`, `gemini`, `pi`, `vibe`, `vscode`, `hermes`, `cline`, `kimi`, `trae`, `nanobot`, `kiro`, `antigravity`.

Cursor and VS Code Copilot auto-discover the plugin via `.cursor-plugin/` and `.copilot-plugin/` directories when the repo is cloned.

## Usage Commands

| Command | Purpose |
|---|---|
| `/understand` | Run the full multi-agent analysis pipeline (incremental by default) |
| `/understand --full` | Force a full re-analysis from scratch |
| `/understand --language zh` | Generate localized content (en, zh, zh-TW, ja, ko, ru) |
| `/understand --auto-update` | Install a post-commit hook for automatic incremental updates |
| `/understand src/frontend` | Scope analysis to a subdirectory (for monorepos) |
| `/understand-dashboard` | Open the interactive web dashboard |
| `/understand-chat How does X work?` | Ask questions about the analyzed codebase |
| `/understand-diff` | Analyze the impact of current uncommitted changes |
| `/understand-explain src/auth/login.ts` | Deep-dive into a specific file or function |
| `/understand-onboard` | Generate an onboarding guide for new team members |
| `/understand-domain` | Extract business domain knowledge (domains, flows, steps) |
| `/understand-knowledge ~/path/to/wiki` | Analyze a Karpathy-pattern LLM wiki |

## Related

- [[graphify]] — Knowledge graph construction from codebases and documents, a complementary approach to codebase comprehension
- [[openclaw]] — AI coding agent platform that can consume Understand-Anything's graph output for context-aware task execution
- [[opencode]] — AI coding agent that directly integrates as a supported platform via the universal install script
- [[hermes-agent]] — Multi-platform agent gateway with skill-based execution, supported as a platform target
- [[llmtrim]] — Tool for compressing LLM context that complements graph-based code understanding
- [[codebase-memory]] — Skill for structural code queries using knowledge graphs
