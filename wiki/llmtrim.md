---
name: llmtrim
tags: [cli, dashboard, developer-tools, mcp, monitoring, optimization, rust, llmtrim]
description: "Local proxy that compresses LLM API requests to reduce token costs with no change in answer quality"
source: sources/llmtrim/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# llmtrim

**Source:** `sources/llmtrim/`

llmtrim is a local proxy that compresses LLM API requests before they reach the provider, reducing token consumption by a measured average of 31% input tokens and 74% output tokens with no change in answer quality. Written in Rust with bindings for Python, Ruby, Swift, Kotlin, JavaScript, TypeScript, and WASM.

| Field | Value |
|---|---|
| **Origin** | [fkiene/llmtrim](https://github.com/fkiene/llmtrim) |
| **License** | MPL-2.0 |
| **Stack** | Rust 1.88+, tree-sitter, WebAssembly, UniFFI |
| **Packages** | `llmtrim` (crate), `@llmtrim/cli` (npm), Homebrew Formula, Docker image |
| **Source** | `sources/llmtrim/` |

## Key Features

- **10-Stage Compression Pipeline:** Each stage fires only where it saves meaningful tokens. Includes tool-output folding, cache discipline, lexical retrieval (BM25+), skeletonization (tree-sitter for 14 languages), JSON minification/TOON encoding, dedup, output control, tool-layer trimming, image downscaling, and record array sampling.
- **Lossless Guarantee:** Every compression step is re-measured with the provider's real tokenizer. If a step does not actually save tokens, it is reverted. If the provider rejects the compressed request, the original is resent verbatim. Worst case is zero savings, never a worse outcome.
- **Multi-Form Usage:** Runs as a local HTTPS proxy (intercepting proxy), MCP server, CLI tool (`llmtrim compress`), or library via UniFFI bindings. ~5 ms overhead per call with no model to load.
- **Provider Support:** Intercepts Anthropic, OpenAI, Google, OpenRouter, and any custom OpenAI-compatible endpoint. Preserves prompt-cache discounts.
- **Live Dashboard:** `llmtrim status` shows a real-time dashboard with tokens trimmed, dollars saved, input/output savings bars, and per-model breakdown (aliases: `monitor`, `gain`).
- **Hermes Integration:** Ships a dedicated `HERMES.md` guide for seamless setup with Hermes Agent via `HTTPS_PROXY` environment variables and CA certificate trust.
- **Benchmark Suite:** Includes a comprehensive benchmarking system (`crates/llmtrim-cli/bench/`) with named benchmarks (BFCL, SQuAD v2, TruthfulQA), A/B comparisons vs. 4 competitors (caveman, entroly, headroom, leanctx), and per-agent scenario tests.
- **System Tray:** `llmtrim-tray` — a Tauri system-tray app (macOS + Windows) showing per-agent compression savings, backed by the shared ledger.

## Architecture

```
                    ┌─────────────────────────────┐
                    │       AI Tool / Agent        │
                    │  (Claude Code, Cursor,       │
                    │   Hermes, custom app)        │
                    └──────────────┬──────────────┘
                                   │ full request
                                   ▼
                    ┌─────────────────────────────┐
                    │         llmtrim             │
                    │  (local proxy, ~5ms/call)   │
                    │                             │
                    │  ┌───────────────────────┐  │
                    │  │ Compression Pipeline   │  │
                    │  │ 1. Tool output folding │  │
                    │  │ 2. Cache discipline    │  │
                    │  │ 3. Lexical retrieval   │  │
                    │  │ 4. Skeletonization     │  │
                    │  │ 5. Serialize + hygiene │  │
                    │  │ 6. JSON sampling       │  │
                    │  │ 7. Dedup               │  │
                    │  │ 8. Output control      │  │
                    │  │ 9. Tool layer          │  │
                    │  │ 10. Multimodal         │  │
                    │  └───────────────────────┘  │
                    └──────────────┬──────────────┘
                                   │ compressed request
                                   ▼
                    ┌─────────────────────────────┐
                    │     LLM Provider API         │
                    │  (OpenAI / Anthropic / ... )  │
                    └─────────────────────────────┘
```

The project is organized as a Rust workspace with six crates (`Cargo.toml:3-10`):

1. **`llmtrim-core`** -- The library with the compression pipeline, provider tokenizers, quality gating, IR (internal representation), and all 10 compressor stages. Tests include conformance suites against Anthropic and OpenAI request formats.
2. **`llmtrim-cli`** -- The CLI binary with proxy daemon, MCP server, compress, status dashboard, doctor, setup, ensure, update, bench, and subscription-reroute subcommands.
3. **`llmtrim-ledger`** -- SQLite ledger (data layer) shared by `llmtrim-cli` and `llmtrim-tray`; tracks sessions, tokens, and savings.
4. **`llmtrim-uniffi`** -- UniFFI bindings for Python, Ruby, Swift, Kotlin with packaging scripts for gems, Maven, wheels, and XCFrameworks.
5. **`llmtrim-wasm`** -- WebAssembly bindings for JavaScript/TypeScript.
6. **`llmtrim-tray`** -- Tauri system-tray app (macOS + Windows) showing per-agent compression savings; compiled only by `cargo build -p llmtrim-tray` or the dedicated `tray.yml` CI workflow (needs webkit2gtk / WKWebView, absent on Linux CI).

### Key Source Directories

| Directory | Purpose |
|---|---|
| `crates/llmtrim-core/src/` | Core compression engine, pipeline, 10 compressor stages, tokenizers |
| `crates/llmtrim-core/src/stages/` | Stage modules: cache, dedup, hygiene, image, jsoncrush, ngram, output, retrieve (BM25), serialize, skeleton (tree-sitter), tool_schema, tools |
| `crates/llmtrim-core/src/stages/toolout/` | Tool output compressors (detect, diff, generated, grep, log, normalize, plaintext, signals, template) |
| `crates/llmtrim-cli/src/` | CLI: proxy daemon, MCP server, monitor, quality checks, doctor, setup, ensure, update |
| `crates/llmtrim-cli/src/reroute/` | Subscription reroute subsystem (`sub` command: codex, grok, kimi backends) |
| `crates/llmtrim-cli/bench/` | Benchmark suite (4 competitors, 3 named benchmarks, agent scenarios) |
| `crates/llmtrim-ledger/` | SQLite ledger data layer |
| `crates/llmtrim-tray/` | Tauri system-tray app |
| `crates/llmtrim-uniffi/` | Polyglot bindings (Python, Ruby, Swift, Kotlin) |
| `crates/llmtrim-wasm/` | WASM/JS/TS bindings |
| `docs/tray-app/` | Tray app documentation |
| `tools/` | npm package builder, CI checker, third-party license generator |

## Interfaces

### Proxy

Sits between AI tools and LLM providers as a local HTTPS proxy. Set `HTTPS_PROXY=http://127.0.0.1:43117` and trust the CA certificate via `llmtrim setup`.

### CLI

| Command | Description |
|---|---|
| `llmtrim setup` | Start proxy, install CA cert, configure shell profile |
| `llmtrim status` | Live dashboard of tokens saved and dollars trimmed (aliases: `monitor`, `gain`) |
| `llmtrim compress < <request.json>` | Compress a single request body |
| `llmtrim doctor` | End-to-end diagnostic of proxy setup |
| `llmtrim serve` | Run as MCP server |
| `llmtrim uninstall` | Reverse all setup changes |
| `llmtrim compact` | Configure cheaper models for Claude Code `/compact` |
| `llmtrim recall` | Recall previously compressed requests |
| `llmtrim sub` | Subscription reroute: use another subscription's backend (codex, grok, kimi) for Claude Code |
| `llmtrim window_sub` | Window-level subscription routing controls |
| `llmtrim autostart` | Manage autostart of the proxy daemon |
| `llmtrim tray` | Run the system-tray app |
| `llmtrim ensure` | Bring the machine to the recommended current state |
| `llmtrim update` | Update to the latest release and refresh integrations |
| `llmtrim bench` | Run the benchmark suite |

### MCP Server

Runs as an MCP server providing compression tools to MCP-compatible agents (`llmtrim mcp` over stdio, or `llmtrim mcp install` to register it with a client).

### Library

Available via UniFFI bindings in Python (`pip install llmtrim`), Ruby (gem), Swift (SPM), Kotlin (Maven), and WASM (npm `@llmtrim/cli`).

## Related

- [[hermes-agent]] -- Ships dedicated integration guide; llmtrim compresses Hermes API calls via HTTPS_PROXY
- [[n8n]] -- Could compress outgoing LLM API calls from n8n AI nodes
- [[openclaw]] -- Compatible with any OpenAI-compatible provider
- [[nix-podman-stacks]] -- Nix-based infrastructure for deploying llmtrim as a system service
