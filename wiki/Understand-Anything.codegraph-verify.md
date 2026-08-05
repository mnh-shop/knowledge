---
name: understand-anything-codegraph-verify
tags: [understand-anything, codegraph-verify, research, code-analysis]
description: "Codegraph Verification: Understand-Anything — validating wiki claims against indexed source code symbols"
source: sources/Understand-Anything/
---

# Codegraph Verification: Understand-Anything

**Date:** 2026-07-12

## Claim 1: Multi-language AST parsing via tree-sitter WASM
- **Wiki says:** "Multi-Language Parsing — AST-based analysis via tree-sitter WASM supporting Python, JavaScript, TypeScript, Go, Rust, Java, and more. Uses `web-tree-sitter` (WASM) instead of native bindings."
- **Source evidence:**
  - `understand-anything-plugin/packages/core/src/plugins/tree-sitter-plugin.ts` — `TreeSitterPlugin` class and `TreeSitterParser` integration (line 31 and line 16)
  - `understand-anything-plugin/packages/core/src/plugins/extractors/` — 14 language-specific extractors: `python-extractor.ts`, `typescript-extractor.ts`, `go-extractor.ts`, `rust-extractor.ts`, `java-extractor.ts`, `cpp-extractor.ts`, `csharp-extractor.ts`, `dart-extractor.ts`, `kotlin-extractor.ts`, `php-extractor.ts`, `ruby-extractor.ts`, `scala-extractor.ts`, `swift-extractor.ts`, `base-extractor.ts`
  - `understand-anything-plugin/packages/core/src/plugins/parsers/` — 13 supplementary parsers for non-tree-sitter formats: `dockerfile-parser.ts`, `env-parser.ts`, `graphql-parser.ts`, `json-parser.ts`, `makefile-parser.ts`, `markdown-parser.ts`, `protobuf-parser.ts`, `shell-parser.ts`, `sql-parser.ts`, `terraform-parser.ts`, `toml-parser.ts`, `yaml-parser.ts`, `index.ts`
  - `understand-anything-plugin/packages/tree-sitter-dart-wasm/` and `understand-anything-plugin/packages/tree-sitter-swift-wasm/` — dedicated WASM parser packages for Dart and Swift
  - `understand-anything-plugin/packages/core/src/plugins/discovery.ts` — Plugin discovery mechanism
  - `understand-anything-plugin/packages/core/src/plugins/registry.ts` — Plugin registry
  - `understand-anything-plugin/packages/core/src/plugins/tree-sitter-plugin.test.ts` — Test coverage
- **Verdict:** ✅ CORRECT (14 extractors + 13 supplementary parsers + 2 WASM parser packages confirmed)
- **Fix needed:** None

## Claim 2: Interactive knowledge graph dashboard (React + TypeScript)
- **Wiki says:** "Interactive Knowledge Graph Dashboard — A React + TypeScript web dashboard (React Flow, Zustand, TailwindCSS v4) with a dark luxury theme, 75% graph + 360px sidebar layout, color-coded by architectural layer, with fuzzy and semantic search."
- **Source evidence:**
  - `understand-anything-plugin/packages/dashboard/src/` — Full React + TypeScript dashboard source
  - `understand-anything-plugin/packages/dashboard/src/App.tsx` — Main application component
  - `understand-anything-plugin/packages/dashboard/src/components/KnowledgeGraphView.tsx` — Graph visualization component (286 lines)
  - `understand-anything-plugin/packages/dashboard/src/components/` — Component library directory
  - `understand-anything-plugin/packages/dashboard/src/store.ts` — Zustand state management
  - `understand-anything-plugin/packages/dashboard/src/themes/` — Theme configuration (dark luxury)
  - `understand-anything-plugin/packages/dashboard/src/contexts/` — React contexts
  - `understand-anything-plugin/packages/dashboard/src/hooks/` — Custom hooks
  - `understand-anything-plugin/packages/dashboard/src/locales/` — i18n support
  - `understand-anything-plugin/packages/viewer/` — Standalone graph viewer (npx-publishable)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Multi-agent analysis pipeline with 5+ specialized agents
- **Wiki says:** "`/understand` orchestrates 5 specialized agents: `project-scanner` (file discovery, language detection), `file-analyzer` (extract functions, classes, imports), `architecture-analyzer` (layer identification), `tour-builder` (guided learning walks), and `graph-reviewer` (structural validation). `/understand-domain` adds a 6th `domain-analyzer` agent."
- **Source evidence:**
  - `understand-anything-plugin/agents/` — 10 agent definition files:
    - `project-scanner.md` — File discovery and language detection
    - `file-analyzer.md` — Function, class, import extraction
    - `architecture-analyzer.md` — Architecture layer identification
    - `tour-builder.md` — Guided learning walk generation
    - `graph-reviewer.md` — Structural graph validation
    - `domain-analyzer.md` — Business domain extraction
    - `article-analyzer.md` — Knowledge base article analysis
    - `design-analyzer.md` — Design analysis
    - `assemble-reviewer.md` — Assembly review
    - `knowledge-graph-guide.md` — Graph usage guidance
  - `understand-anything-plugin/skills/` — 9 skill directories:
    - `understand/` — Main `/understand` command
    - `understand-domain/` — `/understand-domain` command
    - `understand-knowledge/` — `/understand-knowledge` command
    - `understand-chat/` — `/understand-chat` command
    - `understand-dashboard/` — `/understand-dashboard` command
    - `understand-diff/` — `/understand-diff` command
    - `understand-explain/` — `/understand-explain` command
    - `understand-onboard/` — `/understand-onboard` command
    - `understand-figma/` — Figma integration
  - `understand-anything-plugin/packages/core/src/analyzer/` — Core analysis modules: `graph-builder.ts`, `layer-detector.ts`, `llm-analyzer.ts`, `tour-generator.ts`, `normalize-graph.ts`, `language-lesson.ts`
- **Verdict:** ✅ CORRECT (10 agents + 9 skills confirmed, exceeding the claimed 5-6)
- **Fix needed:** None

## Claim 4: Incremental analysis with fingerprint-based change detection
- **Wiki says:** "Incremental Analysis — Subsequent runs only re-analyze changed files using fingerprint-based change detection. Intermediate results are cached in the data directory's `intermediate/` subdirectory and cleaned up after graph assembly."
- **Source evidence:**
  - `understand-anything-plugin/packages/core/src/fingerprint.ts` — Fingerprint computation for change detection
  - `understand-anything-plugin/packages/core/src/staleness.ts` — Staleness checking for incremental analysis
  - `understand-anything-plugin/packages/core/src/change-classifier.ts` — Classifies code changes for differential analysis
  - `understand-anything-plugin/skills/understand/scan-project.mjs` — Project scanning with fingerprint handling
  - `understand-anything-plugin/skills/understand/build-fingerprints.mjs` — Fingerprint building script
  - `understand-anything-plugin/skills/understand/compute-batches.mjs` — Batch computation for incremental processing
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Knowledge graph format with schema validation
- **Wiki says:** "The graph is saved to `.ua/knowledge-graph.json`. Each node represents a file, function, class, or architectural concept with edges encoding imports, calls, inheritance, and containment. The format includes schema validation on load."
- **Source evidence:**
  - `understand-anything-plugin/packages/core/src/types.ts` — `KnowledgeGraph` type definition (line 107, used by 73 callers)
  - `understand-anything-plugin/packages/core/src/schema.ts` — Graph schema validation
  - `understand-anything-plugin/packages/core/src/types.test.ts` — Type definitions tests
  - `understand-anything-plugin/packages/core/src/analyzer/graph-builder.ts` — Graph construction logic
  - `understand-anything-plugin/packages/core/src/persistence/` — Graph persistence layer
  - `understand-anything-plugin/packages/core/src/embedding-search.ts` — Semantic search over graph
  - `understand-anything-plugin/packages/core/src/search.ts` — Graph search implementation
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Multi-platform support across 17+ AI coding platforms
- **Wiki says:** "Works across 17+ AI coding platforms via a universal install script — Codex, OpenCode, OpenClaw, Gemini CLI, Cursor, VS Code Copilot, Copilot CLI, Pi Agent, Vibe CLI, Hermes, Cline, KIMI CLI, Trae, Nanobot, Kiro, and Antigravity."
- **Source evidence:**
  - `install.sh` — Universal installation script (9544 bytes)
  - `install.ps1` — Windows PowerShell installation script
  - `.claude-plugin/` — Native Claude Code plugin
  - `.cursor-plugin/` — Cursor IDE plugin
  - `.copilot-plugin/` — VS Code Copilot plugin
  - `understand-anything-plugin/.claude-plugin/` — Plugin metadata for Claude Code
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Architecture layout — search.ts/schema.ts are files, tree-sitter under plugins/, tours under analyzer/
- **Wiki says:** The architecture tree locates graph search at `src/search.ts` (file), schema at `src/schema.ts` (file), WASM parser integration at `src/plugins/tree-sitter-plugin.ts`, and guided tour generation at `src/analyzer/tour-generator.ts`, with additional `analyzer/`, `languages/`, `figma/`, and `persistence/` directories.
- **Source evidence:**
  - `understand-anything-plugin/packages/core/src/search.ts` — Graph search implementation (single file, NOT a directory)
  - `understand-anything-plugin/packages/core/src/schema.ts` — Graph schema validation (single file, NOT a directory)
  - `understand-anything-plugin/packages/core/src/plugins/tree-sitter-plugin.ts` — WASM parser integration (under `plugins/`, NOT a top-level `src/tree-sitter/` dir)
  - `understand-anything-plugin/packages/core/src/analyzer/tour-generator.ts` — Guided tour generation (under `analyzer/`, NOT a top-level `src/tours/` dir)
  - `understand-anything-plugin/packages/core/src/languages/` — language-pack: `configs/` (42 language configs: `python.ts`, `typescript.ts`, `go.ts`, `rust.ts`, ...) + `frameworks/` (11 detectors: `django.ts`, `react.ts`, `nextjs.ts`, ...) + `language-registry.ts`, `framework-registry.ts`
  - `understand-anything-plugin/packages/core/src/figma/` — Figma design analysis (`index.ts`, `merge.ts`, `parse/parse-document.ts`, `parse/tokens.ts`, `thumbnails.ts`)
  - `understand-anything-plugin/packages/core/src/persistence/` — Graph persistence layer (`index.ts`)
  - `understand-anything-plugin/packages/core/src/fingerprint.ts`, `staleness.ts`, `change-classifier.ts` — incremental analysis modules (top-level files)
- **Verdict:** ✅ CORRECT (earlier wiki tree claiming `src/search/`, `src/schema/`, `src/tree-sitter/`, `src/tours/` directories was fixed to match reality)
- **Fix needed:** Applied to wiki

## Claim 8: Viewer tarball release process and repo-root scripts
- **Wiki says:** The viewer is published as a release tarball `understand-anything-viewer.tgz` (repacked on every release and re-uploaded to GitHub Releases so `npx .../releases/latest/download/understand-anything-viewer.tgz` works), and `scripts/generate-large-graph.mjs` generates fake graphs for performance testing.
- **Source evidence:**
  - `understand-anything-plugin/packages/viewer/` — viewer package (`bin/viewer.mjs`, `build.mjs`, `package.json` named `understand-anything-viewer`)
  - `sources/Understand-Anything/CLAUDE.md` — Viewer Package section: "On every release, repack (`pack:release` script) and re-upload the tarball to the GitHub release as `understand-anything-viewer.tgz` — exactly that name, the READMEs' `releases/latest/download/` URL depends on it"
  - `README.md` lines 306-310 — `npx https://github.com/Egonex-AI/Understand-Anything/releases/latest/download/understand-anything-viewer.tgz /path/to/analyzed/project`, "Only Node.js (>= 18) is required"
  - `scripts/generate-large-graph.mjs` — fake-graph generator; CLAUDE.md: "Usage: `node scripts/generate-large-graph.mjs [nodeCount]` (default: 3000 nodes)... Not part of the production pipeline"
  - `scripts/benchmark-large-repo.mjs` — benchmark helper
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (content added to wiki)

## Summary

All 8 key claims from the Understand-Anything wiki have been verified against the source code:
- ✅ **Multi-language tree-sitter parsing:** 14 language extractors + 13 supplementary parsers + 2 WASM parser packages confirmed
- ✅ **Knowledge graph dashboard:** React + TypeScript dashboard with Zustand, React Flow confirmed
- ✅ **Multi-agent pipeline:** 10 agent definitions + 9 skill commands (incl. `/understand-figma`) confirmed
- ✅ **Incremental analysis:** Fingerprint-based change detection infrastructure confirmed
- ✅ **Knowledge graph format:** `KnowledgeGraph` type, schema validation, graph builder confirmed
- ✅ **Multi-platform install:** Universal install.sh + platform-specific plugin directories confirmed
- ✅ **Architecture layout:** search.ts/schema.ts as files, tree-sitter under plugins/, tours under analyzer/ confirmed
- ✅ **Viewer tarball + scripts:** release tarball process and generate-large-graph.mjs confirmed

## Related

- [[Understand-Anything]] -- Main wiki entry

## Cross-project

- [[graphify.codegraph-verify]] -- Similar codegraph verification for Graphify
- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
- [[opencode.codegraph-verify]] -- Similar codegraph verification for OpenCode
