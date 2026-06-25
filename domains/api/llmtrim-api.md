---
name: llmtrim-api
description: "llmtrim API surfaces — stdin/pipe, MCP proxy, and SSE-based streaming callback"
tags: [ai-llm, cli, documentation, mcp, optimization, rest-api]
---
# llmtrim API Documentation

llmtrim does not expose a traditional REST API with endpoints like FastAPI/Actix. Instead, it provides three API surfaces:

1. **Upstream Provider API Transport** - HTTP client for forwarding requests to LLM providers
2. **MITM Reverse Proxy** - Intercepts and compresses LLM API traffic in-flight
3. **CLI Command API** - Command-line interface for compression, proxy, and MCP operations

---

## 1. Upstream Provider API Transport (`transport.rs`)

Source: `crates/llmtrim-cli/src/transport.rs`

### Endpoint Struct

Represents an authenticated connection to an LLM provider API:

```rust
pub struct Endpoint {
    base_url: String,   // e.g. https://api.openai.com
    api_key: String,    // Provider API key
}
```

Construction:
```rust
Endpoint::from_env(provider: ProviderKind) -> Result<Self>
```
- Reads API key from environment: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`
- Reads base URL from environment or uses provider default
- OpenAI default: `https://api.openai.com`
- Anthropic default: `https://api.anthropic.com`
- Google default: `https://generativelanguage.googleapis.com`

### Provider-Specific API URLs

| Provider | URL Pattern |
|---|---|
| OpenAI | `{base}/v1/chat/completions` |
| Anthropic | `{base}/v1/messages` |
| Google | `{base}/v1beta/models/gemini-2.0-flash:generateContent` |

### Authentication Headers

| Provider | Header |
|---|---|
| OpenAI | `Authorization: Bearer {key}` |
| Anthropic | `x-api-key: {key}`, `anthropic-version: 2023-06-01` |
| Google | `x-goog-api-key: {key}` |

All providers: `content-type: application/json`

### HTTP Client Methods

```rust
// Blocking POST - sends request and returns response body
pub fn send(&self, request_json: &str, proxy_url: Option<&str>) -> Result<String>

// Streaming POST forwarder for reverse proxy
pub fn forward_post(url, headers, body, proxy_url) -> Result<Upstream>

// Streaming GET forwarder for reverse proxy
pub fn forward_get(url, proxy_url) -> Result<Upstream>
```

Key behavior of `send()`:
- Suppresses ambient `HTTPS_PROXY` by default (looping back through daemon)
- Uses explicit upstream proxy when provided
- 30-second global timeout (`UPSTREAM_TIMEOUT`)
- Uses `ureq` HTTP library (blocking)

### Upstream Struct (Streaming)

```rust
pub struct Upstream {
    pub status: u16,
    pub content_type: Option<String>,
    pub reader: Box<dyn Read + Send>,
}
```
- Used by the reverse proxy to stream responses through
- Content-type is echoed so SSE clients see `text/event-stream`
- Supports chunked/streaming transfer

### Proxy URL Utilities

- `redact_proxy_url(url)` - Strips credentials from proxy URLs for logging
- `upstream_proxy_url()` - Gets configured upstream proxy from env
- `validate_proxy_url()` - Validates proxy URL, rejects loopback self-reference
- `make_proxy()` - Creates `ureq::Proxy` from URL string

---

## 2. MITM Reverse Proxy (`serve.rs`)

Source: `crates/llmtrim-cli/src/serve.rs`

### Overview

An HTTPS reverse proxy that intercepts LLM API traffic, compresses request bodies on-the-fly, and forwards them to upstream providers.

### Implementation

Uses the `hudsucker` crate for HTTPS interception:
- `hudsucker::certificate_authority::CertificateAuthority`
- `hudsucker::rustls` for TLS
- `hyper_util::client::legacy::connect::HttpConnector`
- `bytes::Bytes`

### Public API

```rust
pub fn run(_port: u16, _force: bool) -> anyhow::Result<()>
pub fn run_supervised(_port: u16, _force: bool) -> anyhow::Result<()>
pub fn ca_cert_path() -> anyhow::Result<PathBuf>
pub fn ensure_ca() -> anyhow::Result<(String, String)>
```

### Traffic Interception Strategy

#### Domain Detection

The proxy automatically discovers LLM provider domains from `llm_providers` data, detecting which hosts to intercept:

```rust
fn is_extra_host(host: &str) -> bool
fn intercept_domains() -> Vec<String>
fn host_covered(host, domains) -> bool
```

#### Provider Identification from Hostname

```rust
fn provider_for_host(host: &str) -> Option<ProviderKind>
```
- `*.anthropic.com` -> `Anthropic`
- Google API hosts -> `Google`
- Known LLM domains / extra hosts -> `OpenAi`

#### Compressible Path Detection

```rust
fn is_compressible_path(path: &str) -> bool
```

Compression is applied to these API paths:
- `/chat/completions` (OpenAI / OpenAI-compatible)
- `/responses` (OpenAI Responses API)
- `/messages` (Anthropic Messages API)
- `:generateContent` / `:streamGenerateContent` (Google Gemini)
- `:rawPredict` / `:streamRawPredict` (Vertex AI Anthropic)
- **Excluded**: `count_tokens`, `:countTokens` (always passed through)

#### Vertex AI Provider Detection

```rust
fn vertex_kind(path: &str) -> Option<ProviderKind>
```
- `openapi` or `/chat/completions` -> OpenAI
- `:rawPredict` or `:streamRawPredict` -> Anthropic
- `:generateContent` or `:streamGenerateContent` -> Google

### Request/Response Handling

#### Interceptor (`imp::Interceptor`)

```rust
impl HttpHandler for Interceptor {
    async fn should_intercept(&mut self, _ctx, req) -> bool
    async fn handle_request(...) -> Result<RequestOrResponse>
    async fn handle_response(...) -> Result<Response<Body>>
}
```

1. **Request interception** (`handle_request_inner`):
   - Captures original request body for possible replay
   - Detects `is_body_signed()` (AWS4-HMAC-SHA256 -> pass through)
   - Passes through if not compressible path
   - Runs gated compression pipeline via `llmtrim_core::pipeline::run()`
   - Streams compressed request upstream
   - Uses `Memo` (prefix-based compression caching) for cross-turn dedup

2. **Response interception** (`handle_response_inner`):
   - Feeds response through `upstream()` stream
   - Captures response body bytes
   - Records usage: tracks `input_tokens_before/after`, `output_tokens`, `cache_read/write`
   - Handles response expansion (reverses output shaping)
   - Builds breakdown/cost analysis

3. **Error Recovery** (`should_replay`, `replay_original`):
   - On 400/422 responses: replays original (uncompressed) request
   - Ensures compression errors don't break LLM calls

### Streaming

- Uses `Upstream` struct for streaming response forwarding
- Content-type headers preserved so SSE (`text/event-stream`) works transparently
- Response body streamed byte-by-byte as it arrives from upstream

### Cost Attribution

```rust
struct BreakdownPayload {
    blocks: Vec<BreakdownBlock>,  // Per-message token attribution
    window,                        // Context window for the model
    fresh, cache_read, cache_write, output,  // Token counts
    cost_usd,                      // Calculated cost
    // Plus agent/project metadata
}
```

Each `BreakdownBlock` tracks:
- `zone`: input/output
- `section`: system/messages
- `bucket`: text/tool_use/tool_result
- `group_label`: e.g. "System", "Messages", "Tools"
- `label`: readable summary
- `mcp_server`, `tool_name`: MCP server and tool (if applicable)
- `role`: message role
- `msg_index`: message index in conversation
- `tokens`, `fresh_tok`, `cache_read_tok`, `cache_write_tok`
- `cost_usd`, `input_cost`, `output_cost`

Pricing rates are model-aware:
- Claude, Opus, Sonnet models use larger context windows
- GPT-5, Codex use specific windows

### Certificate Management

```rust
pub fn ensure_ca() -> Result<(String, String)>     // cert_pem, key_pem
pub fn ca_cert_path() -> Result<PathBuf>             // Path to CA cert file
```
- Generates local CA certificate for HTTPS interception
- The proxy generates per-host certificates signed by this CA
- `llmtrim setup` command exposes certificate installation steps

### Staged Compression Pipeline

The interceptor builds stages from `DenseConfig` and runs them in order:

| Stage | Purpose |
|---|---|
| ToolOutput | Compress tool result blocks (diff, grep, log output) |
| Retrieve | MMR-based content retrieval subset selection |
| Skeleton | Extract code skeletons (strip bodies, keep signatures) |
| MinifyCode | Minify embedded code blocks |
| Image | Downscale image data URLs |
| Hygiene | Normalize whitespace, Unicode |
| JsonCrush | Compress large JSON arrays using TOON format |
| Serialize | Serialize/format messages |
| Dedup | Collapse repeated lines |
| Ngram | N-gram based compaction |
| ToolSchema | Minify tool definitions |
| OutputControl | Add output shaping instructions (terse, draft, etc.) |
| Cache | Provider prompt caching awareness |

### Recording and Tracking

After each request, the interceptor records a `Record` containing:
- `provider`, `model`, `tokenizer` labels
- `input_before`, `input_after` token counts
- `output_before`, `output_after` token counts
- `cache_read_tokens`, `cache_write_tokens`
- `frozen_input_tokens` (prompt cache breakpoint)
- `stages` list of applied stages
- `output_shaped` flag
- `compress_micros` timing

Records are sent over an mpsc channel to a ledger thread for SQLite persistence.

---

## 3. CLI Command API (`main.rs`)

Source: `crates/llmtrim-cli/src/main.rs`

### Command Structure

```
llmtrim <COMMAND> [ARGS]

Commands:
  compress   Read provider request JSON from stdin, compress it, forward to provider
  serve      Start the HTTPS reverse proxy daemon
  wrap       Launch an agent under the compression proxy
  mcp        MCP protocol subcommands (run, install)
  status     Show daemon status and usage statistics
  stop       Stop the running daemon
  doctor     Run diagnostics and print report
  setup      Generate and print CA certificate setup instructions
  autostart  Enable/disable daemon auto-start
  bench      Run benchmarks (quality, suite, agent, latency, compare)
  update     Self-update
```

### Compress Command

```
llmtrim compress [--provider <provider>] [--model <model>]
```

- Reads a provider request JSON body from stdin
- Optionally parses `--provider` (openai|anthropic|google)
- Compresses using `llmtrim_core::compress()`
- Writes compressed request JSON to stdout
- Optionally forwards to provider API and prints response

### Serve Command

```
llmtrim serve [--port <port>] [--force]
```

- Starts the hudsucker-based MITM proxy
- `--port` specifies listen port
- `--force` forces re-generation of CA cert
- Daemonizes automatically

### Wrap Command

```
llmtrim wrap <agent> [-- <agent_args>...]
```
Source: `crates/llmtrim-cli/src/wrap.rs`

Supported agents: `claude`, `aider`, `goose`, `mcp-cli` (and any other binary)

Behavior:
- Checks daemon is running, starts if needed
- Verifies HTTPS_PROXY env points at daemon
- Executes the agent with inherited env vars

```rust
struct WrapInvocation {
    agent: String,    // e.g. "claude"
    args: Vec<String>, // e.g. ["chat", "--model", "x"]
}

fn parse_invocation(raw: &[String]) -> Result<WrapInvocation>
fn exec_agent(inv: &WrapInvocation) -> Result<()>
```

---

## 4. Core Compression Library (`llmtrim-core`)

Source: `crates/llmtrim-core/src/lib.rs`

### Public API

```rust
// Auto-detect config from env/file
pub fn compress(input: &str, provider: Option<ProviderKind>) -> Result<CompressResult>

// Explicit config (deterministic, no env access)
pub fn compress_with_config(input: &str, provider: Option<ProviderKind>, config: &DenseConfig) -> Result<CompressResult>

// Route detection: return preset name based on request shape
pub fn route(req: &Request, provider: &dyn Provider) -> &'static str
```

### CompressResult

```rust
pub struct CompressResult {
    pub request_json: String,        // Compressed request body
    pub provider: ProviderKind,      // Detected provider
    pub model: String,               // Target model
    pub input_tokens_before: Tokens, // Token count before compression
    pub input_tokens_after: Tokens,  // Token count after compression
    pub frozen_input_tokens: Tokens, // Frozen prefix tokens (cache)
    pub output_shaped: bool,         // Output shaping was applied
    pub tokenizer_label: String,     // Tokenizer used for counting
    pub tokenizer_exact: bool,       // Exact or estimated tokenizer
    pub stages: Vec<String>,         // Names of stages that applied
    pub report: Vec<StageReport>,    // Per-stage details
}
```

### Route Auto-Detection

```rust
pub fn route(req, provider) -> &'static str
```
Heuristics:
- Has tools array -> "agent" preset
- Has code fences (```) -> "code" preset
- 2+ turns with 1200+ chars -> "rag" or "auto" preset

### Configuration Presets

| Preset | Description |
|---|---|
| `auto` | Default adaptive configuration |
| `safe` | Conservative, minimal compression |
| `rag` | Optimized for RAG contexts |
| `agent` | Optimized for agent tool-calling patterns |
| `code` | Code-heavy content optimization |
| `aggressive` | Maximum compression |
| `cache` | Prompt-cache aware optimization |
| `reasoning` | Preserve reasoning chains |

---

## 5. Multi-Language Bindings

### UniFFI Bindings (`llmtrim-uniffi`)

- Python: `examples/compress_then_send.py`, `tests/python/test_llmtrim.py`
- Ruby: `examples/compress_then_send.rb`, `tests/ruby/test_llmtrim.rb`
- Swift: `tests/swift/smoke.swift`, `tests/LlmtrimTests/CompressTests.swift`
- Kotlin: `tests/kotlin/Smoke.kt`

### WASM Bindings (`llmtrim-wasm`)

- `crates/llmtrim-wasm/src/lib.rs`
- `smoke.mjs` for Node.js testing

---

## CLI Module Structure

```
crates/llmtrim-cli/src/
  main.rs       - CLI entry point with clap argument parsing
  lib.rs        - Module declarations (re-exports all submodules)
  mcp.rs        - MCP server implementation
  serve.rs      - MITM reverse proxy
  transport.rs  - Upstream provider HTTP transport
  wrap.rs       - Agent wrapping/subprocess execution
  daemon.rs     - Background daemon management
  discover.rs   - Runtime discovery of daemon instances
  doctor.rs     - Diagnostic reporting
  monitor.rs    - Usage monitoring and statistics
  tracking.rs   - SQLite tracking/recording
  breakdown/    - Cost attribution breakdown module
    app.rs      - Application-level breakdown
    db.rs       - Breakdown database
    export.rs   - Breakdown export
    palette.rs  - Visualization palette
    tree.rs     - Tree rendering
  bench/        - Benchmarking harness
    agent.rs    - Agent benchmark runner
    envelope.rs - Benchmark envelope/context
  ui.rs         - Terminal UI (colored output, error rendering)
  setup.rs      - CA cert setup
  autostart.rs  - Autostart configuration
  update.rs     - Self-update
  quality.rs    - Quality assessment
```
