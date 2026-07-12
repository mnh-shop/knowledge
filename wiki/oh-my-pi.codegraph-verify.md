---
title: oh-my-pi.codegraph-verify
description: "Source-level verification of oh-my-pi — Fork of pi-mono with additional features"
date: 2026-07-12
tags: [oh-my-pi, codegraph-verify, pi, agent, rust, typescript]
verified_by: codegraph-explore
source: sources/oh-my-pi/
---

# oh-my-pi — CodeGraph Verification

**Claim-1: oh-my-pi (omp) is a fork of pi-mono by Mario Zechner, extended with a batteries-included coding agent surface featuring 40+ providers, 32 built-in tools, and ~55k lines of Rust core.**

- **Evidence:** `README.md` line 22 states "Fork of [Pi](https://github.com/badlogic/pi-mono) by [@mariozechner](https://github.com/mariozechner)." Line 27 summarizes: "**40+** providers · **32** built-in tools · **14** lsp ops · **28** dap ops · **~55k** lines of Rust core." Line 31 documents the Rust core: "Four crates, one platform-tagged N-API addon. Search, shell, AST, highlight, PTY, image decode, BPE counting — all in-process." The `crates/` directory contains 8 items: `pi-natives`, `pi-shell`, `pi-ast`, `pi-iso`, `pi-uu-grep`, `pi-uutils-ctx`, `pi-walker`, and `vendor/`.
- **Source path:** `sources/oh-my-pi/README.md`, `sources/oh-my-pi/crates/`

**Claim-2: omp implements 20 documented features including code execution with tool-calling (Python + Bun kernels), LSP integration, DAP debugging, time-traveling stream rules, subagents, advisor model, and collaborative sessions.**

- **Evidence:** `README.md` lists 20 numbered features (lines 99-218): "01 · Code execution w/ tool-calling" (persistent Python and Bun workers with loopback bridge to agent tools), "02 · LSP wired into every write" (workspace/willRenameFiles, references, rename), "03 · Drives a real debugger" (lldb-dap, dlv, debugpy), "04 · Time-traveling stream rules" (regex match aborts stream, injects rule, retries), "05 · First-class subagents" (fan-out into isolated worktrees with typed results), "06 · A second model, watching every turn" (advisor/reviewer model on separate context), "07 · Hand someone the link, they're in" (`/collab` with QR code), "08 · Read a pdf on arxiv" (web_search chains 18 providers), and more through feature 20. Each feature is accompanied by screenshots and detailed explanations.
- **Source path:** `sources/oh-my-pi/README.md`

**Claim-3: omp bundles ~55k lines of Rust across 4 core crates for in-process grep, shell, AST analysis, syntax highlighting, PTY, and image decoding — avoiding fork/exec on the hot path.**

- **Evidence:** `README.md` lines 364-396 provide a detailed per-module breakdown of the Rust crates. Key modules: `shell` (3,700 LoC, embedded bash via brush-shell vendored), `grep` (1,900 LoC, regex search with glob/type filters), `keys` (1,490 LoC, Kitty keyboard protocol), `text` (1,450 LoC, ANSI-aware width/wrap), `summary` (1,040 LoC, tree-sitter structural summaries), `ast` (1,000 LoC, ast-grep pattern matching), `highlight` (470 LoC, syntect-based syntax highlighting), `pty` (455 LoC, native PTY allocation), `glob` (410 LoC), and an `appearance` module (270 LoC) using CoreFoundation FFI for macOS dark/light mode detection. The `pi-natives` crate aggregates these into a platform-tagged N-API addon for darwin-arm64, darwin-x64, linux-x64, linux-arm64, and win32-x64.
- **Source path:** `sources/oh-my-pi/README.md`

**Claim-4: omp ships with 32 built-in tools including hashline (content-hash anchored edits), ast_grep (tree-sitter structural rewrites), web_search (18 providers), browser (Puppeteer), and hindsight memory (SQLite-based durable facts).**

- **Evidence:** `README.md` lines 224-275 enumerate 32 tools organized by category: **Files & search** (read, write, edit, ast_edit, ast_grep, search, find), **Runtime** (bash, eval, ssh), **Code intelligence** (lsp, debug), **Coordination** (task, irc, todo, job, ask), **Outside the box** (browser, web_search, github, generate_image, inspect_image, tts), **Memory & state** (checkpoint, rewind, retain, recall, reflect), and **Misc** (resolve, search_tool_bm25). The `ast_edit` tool uses hashline patches with content-hash anchors and stale-anchor recovery. The `edit` tool uses "hashline patches with content-hash anchors and stale-anchor recovery."
- **Source path:** `sources/oh-my-pi/README.md`

**Claim-5: omp supports four entry points — interactive TUI, one-shot mode, RPC over stdio (NDJSON), and ACP (Agent Client Protocol) for editor integration.**

- **Evidence:** `README.md` lines 398-462 document the four entry points. **Interactive TUI** (line 404): "The TUI is the default surface." **One-shot** (line 400): "`omp -p` answers a single prompt and exits." **RPC** (lines 438-448): "`omp --mode rpc` — NDJSON commands in, response and event frames out" with example protocol shown. **ACP** (lines 452-462): "`omp acp` — The Agent Client Protocol over JSON-RPC" with a table showing tool mapping (bash → `terminal/create + terminal/output`, read → `fs/read_text_file`, write → `fs/write_text_file`). The `AGENTS.md` confirms the SDK embedding pattern: `@oh-my-pi/pi-coding-agent` exposes `ModelRegistry`, `SessionManager`, `createAgentSession`, and `discoverAuthStorage`.
- **Source path:** `sources/oh-my-pi/README.md`

**Claim-6: omp includes monorepo packages for model catalog, native N-API bindings, collab web, hashline, mnemopi (SQLite memory), snapcompact (context compression), and swarm extension.**

- **Evidence:** `README.md` lines 522-539 list 14 monorepo packages: `@oh-my-pi/collab-web` (browser guest client and relay), `@oh-my-pi/pi-ai` (multi-provider LLM client), `@oh-my-pi/pi-catalog` (bundled model database and provider descriptors), `@oh-my-pi/pi-agent-core` (agent runtime), `@oh-my-pi/pi-coding-agent` (CLI and SDK), `@oh-my-pi/pi-tui` (terminal UI), `@oh-my-pi/pi-natives` (N-API bindings for grep, shell, image, text), `@oh-my-pi/omp-stats` (observability dashboard), `@oh-my-pi/pi-utils` (shared utilities), `@oh-my-pi/pi-wire` (collab protocol types), `@oh-my-pi/hashline` (patch language), `@oh-my-pi/pi-mnemopi` (SQLite memory engine), `@oh-my-pi/snapcompact` (context compression), and `@oh-my-pi/swarm-extension`. The `packages/` directory in source confirms all 14 packages exist with individual `package.json` files.
- **Source path:** `sources/oh-my-pi/README.md`, `sources/oh-my-pi/packages/`

**Related:** [[oh-my-pi]], [[pi]], [[nanobot]], [[hermes-agent]]
