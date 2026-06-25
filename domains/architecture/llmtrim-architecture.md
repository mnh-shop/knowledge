---
name: llmtrim-architecture
tags: [ai-llm, architecture, cli, container, dashboard, llmtrim, mcp, optimization, quadlet, rust, systemd]
description: "Deep architecture of llmtrim: 10-stage compression pipeline, proxy internals, quality gating, and polyglot bindings"
---

# llmtrim Architecture

llmtrim compresses LLM API requests before they reach the provider, reducing token consumption without changing answers. This document covers the internal architecture of its 10-stage compression pipeline, proxy design, quality gates, and polyglot binding system.

## Workspace Structure

```
llmtrim/                          # Cargo workspace root
├── crates/
│   ├── llmtrim-cli/              # Binary: proxy, MCP server, CLI, benchmarks
│   ├── llmtrim-core/             # Library: compression pipeline, tokenizers, IR
│   ├── llmtrim-uniffi/           # Bindings: Python, Ruby, Swift, Kotlin
│   └── llmtrim-wasm/             # Bindings: JavaScript/TypeScript/WASM
├── tools/                        # npm packaging, CI checks, license generation
├── assets/                       # Logo, status dashboard SVGs
├── Formula/                      # Homebrew formula
└── Dockerfile                    # Container build
```

## Proxy Architecture

llmtrim operates as a local HTTPS intercepting proxy:

```
AI Tool  ─── HTTPS ──▶  llmtrim proxy  ── HTTPS ──▶  LLM Provider
(Claude Code,         (127.0.0.1:43117)           (OpenAI/Anthropic/...)
 Hermes, Cursor)
```

### Interception Mechanism

1. **HTTPS Proxy Mode:** The proxy listens on `127.0.0.1:43117`. Tools are configured to use it via `HTTPS_PROXY`. llmtrim generates its own CA certificate (via `llmtrim setup`) which the tool must trust so the proxy can decrypt and re-encrypt the TLS stream.
2. **Host Discovery:** Automatically intercepts known provider hosts (Anthropic, OpenAI, Google, OpenRouter). Custom endpoints added via `extra_hosts` in config or `LLMTRIM_EXTRA_HOSTS` env var. Only exact hostnames are intercepted (not wildcards) to keep CA scope narrow.
3. **Request Flow:**
   - Tool sends HTTPS request to provider
   - Proxy intercepts, decrypts, runs compression pipeline on request body
   - Compressed request is re-encrypted and forwarded to provider
   - Response passes through unchanged
   - Provider rejection triggers automatic retry with original uncompressed request

### Daemon Lifecycle

The proxy runs as a long-lived daemon:
- `llmtrim setup` -- installs CA cert, starts daemon, configures shell profile
- `llmtrim status` -- queries daemon for live metrics (tokens saved, dollars saved)
- `llmtrim doctor` -- runs end-to-end connectivity and TLS diagnostics
- `llmtrim uninstall` -- stops daemon, removes CA cert, reverts shell config

## Compression Pipeline (10 Stages)

Stages run in savings order (most impactful first). Each stage independently measures its token savings using the provider's real tokenizer before committing. If zero savings, the stage is skipped for that request. Content under `cache_control` markers is never rewritten.

### 1. Tool Output Folding
```
Input:  [58 lines, 4,662 chars] build log with 2 errors + 56 INFO lines
Output: [5 lines, 978 chars] 2 errors verbatim, 56 INFO lines folded to template
Savings: ~79% on this example
```
- Sub-stages: `detect`, `diff`, `generated`, `grep`, `log`, `normalize`, `plaintext`, `signals`, `template`
- Lossless template folding for repetitive tool output (build logs, test output, etc.)
- Regular patterns (timestamps, counters, sequential IDs) are collapsed into compact templates with range notation

### 2. Cache Discipline
- Mark + stabilize the invariant prefix of requests
- Sort tool definitions and schemas alphabetically for stable cache keys
- Set `cache_control` markers on unchanged prefix portions
- Preserves provider prompt-cache discounts

### 3. Lexical Retrieval (BM25+)
- BM25+ ranking with RM3 relevance feedback
- TextTiling topic segmentation for long documents
- Budgeted non-redundant selection of relevant chunks
- The user's question/protected content is always preserved

### 4. Skeletonization
- Uses tree-sitter to parse code blocks (14 languages supported)
- Keeps function bodies for relevant functions (matching the query)
- Drops bodies of irrelevant functions to just their signatures
- Preserves type signatures, exports, and module structure

### 5. Serialize + Hygiene
- Minify JSON (remove whitespace, shorten key names where possible)
- Encode record arrays to [TOON](https://crates.io/crates/toon-format) format (compact table encoding)
- Fall back to CSV for simpler arrays
- Unicode normalization (NFKC)
- Always lossless

### 6. JSON Sampling
- Down-sample large record arrays when they exceed budget
- Strategy: first/last N elements + statistical outliers + query-biased diverse sample
- Only fires on JSON arrays with many records

### 7. Dedup
- Collapse duplicate and near-duplicate lines in prose content
- Uses edit-distance based near-duplicate detection
- Only applies to natural language, not code

### 8. Output Control
- Terse instruction appended to the system prompt asking for shorter output
- Chain-of-Draft formatting instruction
- Token budget specification
- Native JSON schema enforcement
- Configurable: `auto` (default), `safe` (lossless only), `off`

### 9. Tool Layer
- Static tool selection: removes unused tool definitions from the request
- Description trimming: shortens verbose tool descriptions
- Keeps the tool schema cache prefix stable

### 10. Multimodal
- Downscale images to the provider's resolution cap
- Only fires on base64-encoded or URL-referenced images in the request

## Quality Gating

llmtrim has two quality assurance mechanisms:

### Tokenizer Verification
Each compression step is validated against the provider's actual tokenizer before being committed. If the compressed version is not strictly smaller in real token count, the step is reverted for that request.

### Provider Rejection Handling
If the provider returns an error for the compressed request (e.g., malformed response, invalid schema), llmtrim automatically resends the original uncompressed request. The tool receives the response as if compression never happened.

## Polyglot Binding Architecture (UniFFI)

The `llmtrim-uniffi` crate exposes the core compression library through Mozilla's UniFFI:

```
                     ┌───────────────────┐
                     │  llmtrim-core     │
                     │  (Rust library)   │
                     └────────┬──────────┘
                              │ UniFFI
              ┌───────────────┼───────────────┐
              │               │               │
         ┌────▼────┐   ┌─────▼─────┐   ┌─────▼────┐
         │ Python  │   │  Ruby     │   │  Swift    │
         │ .whl    │   │  .gem     │   │ .xcframework
         └─────────┘   └───────────┘   └──────────┘

         ┌─────────┐   ┌───────────┐
         │ Kotlin  │   │ JS/TS     │
         │ .jar    │   │ (WASM)    │
         └─────────┘   └───────────┘
```

- **Python:** PyPI package via `pyproject.toml` + maturin
- **Ruby:** Ruby gem via native extension build
- **Swift:** Swift Package Manager + XCFramework
- **Kotlin:** Maven package via Gradle
- **JS/TS:** WebAssembly via `wasm-pack`

## Benchmark System

The `llmtrim-cli/bench/` subsystem (Python) provides offline benchmarking:

```
bench/
├── data/               # Fixture download, pricing data
├── tools/              # Chart generation, README synthesis
├── competitors/        # Competitor wrappers (caveman, entroly, headroom, leanctx, rtk, snip)
└── agents/             # Benchmark corpora (bfcl, squad2, truthfulqa)
```

Competition benchmarks measure compression ratio, throughput, and answer quality preservation against 7 alternative tools.

## IR (Internal Representation)

Between pipeline stages, the request exists in an intermediate representation (`ir.rs`) that:
- Tracks which content is protected (user query, cache_control markers)
- Maintains original byte offsets for error reporting
- Preserves request structure (messages, tools, system prompt)
- Allows independent stage execution without serialization round-trips between stages

## Configuration System

Config is loaded from `~/.config/llmtrim/config.toml` (or `$XDG_CONFIG_HOME`) with env var overrides:

| Config Key | Env Var | Description |
|---|---|---|
| `mode` | `LLMTRIM_MODE` | `auto` (default), `safe`, or `off` |
| `port` | `LLMTRIM_PORT` | Proxy listen port (default 43117) |
| `extra_hosts` | `LLMTRIM_EXTRA_HOSTS` | Additional provider hosts to intercept |
| `capture_dir` | `LLMTRIM_CAPTURE_DIR` | Directory to save before/after request bodies |
| `upstream_proxy` | `LLMTRIM_UPSTREAM_PROXY` | Secondary proxy for corporate gateways |
| `status` | — | Show live savings dashboard |

## Related

- [[llmtrim]] -- Overview wiki entry
- [[hermes-agent]] -- Primary integration target; Hermes calls OpenAI-compatible APIs that llmtrim intercepts
- [[buildah]] -- Build llmtrim as a container image
- [[podman]] -- Run llmtrim as a Quadlet service alongside other containers
