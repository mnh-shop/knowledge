---
name: llmtrim
tags: [cli, dashboard, developer-tools, mcp, monitoring, optimization, rust]
description: "Local proxy that compresses LLM API requests to reduce token costs with no change in answer quality"
source: sources/llmtrim/
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
- **Live Dashboard:** `llmtrim status --watch` shows a real-time dashboard with tokens trimmed, dollars saved, input/output savings bars, and per-model breakdown.
- **Hermes Integration:** Ships a dedicated `HERMES.md` guide for seamless setup with Hermes Agent via `HTTPS_PROXY` environment variables and CA certificate trust.
- **Benchmark Suite:** Includes a comprehensive benchmarking system (`llmtrim-cli bench/`) with named benchmarks (BFCL, SQuAD, TruthfulQA), A/B comparisons vs. competitors (caveman, entroly, headroom, leanctx), and per-agent scenario tests.

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

The project is organized as a Rust workspace with four crates:

1. **`llmtrim-cli`** -- The CLI binary with proxy, MCP server, compress, status, doctor, setup, uninstall, and benchmark subcommands.
2. **`llmtrim-core`** -- The library with the compression pipeline, provider tokenizers, quality gating, IR (internal representation), and all 10 compressor stages. Tests include conformance suites against Anthropic and OpenAI request formats.
3. **`llmtrim-uniffi`** -- UniFFI bindings for Python, Ruby, Swift, Kotlin with packaging scripts for gems, Maven, wheels, and XCFrameworks.
4. **`llmtrim-wasm`** -- WebAssembly bindings for JavaScript/TypeScript.

### Key Source Directories

| Directory | Purpose |
|---|---|
| `crates/llmtrim-cli/src/` | CLI: proxy daemon, MCP server, monitor, quality checks, doctor, setup |
| `crates/llmtrim-cli/bench/` | Benchmark suite (7 competitors, 3 named benchmarks, agent scenarios) |
| `crates/llmtrim-core/src/` | Core compression engine, pipeline, 10 compressor stages, tokenizers |
| `crates/llmtrim-core/src/stages/toolout/` | Tool output compressors (detect, diff, generated, grep, log, normalize, plaintext, signals, template) |
| `crates/llmtrim-uniffi/` | Polyglot bindings (Python, Ruby, Swift, Kotlin) |
| `crates/llmtrim-wasm/` | WASM/JS/TS bindings |
| `tools/` | npm package builder, CI checker, third-party license generator |

## Interfaces

### Proxy

Sits between AI tools and LLM providers as a local HTTPS proxy. Set `HTTPS_PROXY=http://127.0.0.1:43117` and trust the CA certificate via `llmtrim setup`.

### CLI

| Command | Description |
|---|---|
| `llmtrim setup` | Start proxy, install CA cert, configure shell profile |
| `llmtrim status` | Live dashboard of tokens saved and dollars trimmed |
| `llmtrim status --watch` | Interactive real-time dashboard |
| `llmtrim compress < <request.json>` | Compress a single request body |
| `llmtrim doctor` | End-to-end diagnostic of proxy setup |
| `llmtrim serve` | Run as MCP server |
| `llmtrim uninstall` | Reverse all setup changes |
| `llmtrim monitor` | Track compression savings over time |

### MCP Server

Runs as an MCP server providing compression tools to MCP-compatible agents.

### Library

Available via UniFFI bindings in Python (`pip install llmtrim`), Ruby (gem), Swift (SPM), Kotlin (Maven), and WASM (npm `@llmtrim/cli`).

## Related

- [[hermes-agent]] -- Ships dedicated integration guide; llmtrim compresses Hermes API calls via HTTPS_PROXY
- [[n8n]] -- Could compress outgoing LLM API calls from n8n AI nodes
- [[openclaw]] -- Compatible with any OpenAI-compatible provider
- [[nix-podman-stacks]] -- Nix-based infrastructure for deploying llmtrim as a system service
