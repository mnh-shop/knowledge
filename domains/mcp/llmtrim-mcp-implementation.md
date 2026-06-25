---
name: llmtrim-mcp
description: "llmtrim MCP proxy server — request compression, tool calling, SSE streaming"
source: sources/llmtrim/
tags: [ai-llm, cli, documentation, mcp]
---
# llmtrim MCP Implementation

Source: `crates/llmtrim-cli/src/mcp.rs` (50KB XML offset: 40336)
Test: `crates/llmtrim-cli/tests/mcp_protocol.rs`

## Overview

llmtrim provides an MCP (Model Context Protocol) server that exposes LLM request compression as MCP tools. The server uses the `rmcp` crate (Rust MCP Protocol library) and communicates over stdio transport using JSON-RPC.

## Server Architecture

### Main Entry Points (public module API)

```
pub fn run() -> anyhow::Result<()>       # Run MCP server over stdio
pub fn install(_print, _force) -> anyhow::Result<()>  # Install MCP config into Claude
pub fn test_server(db: PathBuf) -> impl rmcp::ServerHandler + Clone  # Test helper
```

### Internal Module (`mod imp`)

The implementation lives in a private `imp` submodule with these imports:
- `rmcp::handler::server::wrapper::Parameters`
- `llmtrim_core::CompressResult`, `DenseConfig`, `ProviderKind`, `tokenizer`
- `serde::Deserialize`, `serde_json::Value`

### Data Structures

```rust
struct CompressArgs {
    request: RequestArg,       // The request body to compress
    provider: Option<String>,  // Optional provider override
}

enum RequestArg {
    Json(Map<String, Value>),   // JSON object input
    String(String),             // Raw string body
}
// into_body(self) -> String serializes either variant
```

```rust
struct CompressTextArgs {
    text: String,  // Plain text to compress
}
```

```rust
struct StatsArgs {}  // No parameters needed
```

### Server Handler (`LlmtrimServer`)

- Implements `ServerHandler` + `Clone`
- Optional SQLite-based `Tracker` for recording usage stats
- `server()` -> Default handler with no DB
- `server_at(db: PathBuf)` -> Handler with tracking DB at given path

#### Tool Handler Methods

1. **`llmtrim_compress`**
   - Parses `CompressArgs` from tool call parameters
   - Delegates to internal `compress()` function
   - Records result in tracker via `ledger_record()`
   - Returns `compress_payload()` as JSON

2. **`llmtrim_compress_text`**
   - Parses `CompressTextArgs` from tool call parameters
   - Wraps text in a minimal OpenAI-shaped JSON body
   - Uses `DenseConfig::preset("safe")` for deterministic compression
   - Returns `{text, tokens_before, tokens_after, tokens_saved}`

3. **`llmtrim_stats`**
   - Opens the tracker database
   - Calls `crate::monitor::stats_json()` to aggregate stats
   - Returns JSON with `requests`, `by_model`, etc.

### Compression Functions (internal)

```rust
fn compress(request: &str, provider: Option<&str>) -> Result<CompressResult, McpError>
```
- Optionally parses provider string into `ProviderKind`
- Loads config from `DenseConfig::load()` (reads `~/.llmtrim/config`)
- Calls `llmtrim_core::compress()`
- Maps errors to `McpError::invalid_params()` or `McpError::internal_error()`

```rust
fn compress_text(text: &str) -> Result<(Value, Record), McpError>
```
- Constructs minimal JSON body: `{"model": "gpt-4o", "messages": [{"role": user, "content": text}]}`
- Uses `DenseConfig::preset("safe")` -- no environment dependency
- Calls `llmtrim_core::compress_with_config()`
- Extracts user content from compressed result
- Counts tokens using `tokenizer::counter_for(OpenAi, gpt-4o-mini)`
- Returns payload with `text`, `tokens_before`, `tokens_after`, `tokens_saved`

### Response Helpers

```rust
fn ok_json(payload: &Value) -> Result<CallToolResult, McpError>
```
- Wraps any JSON value as `CallToolResult::success(vec![Content::text(json_string)])`

```rust
fn internal(e: anyhow::Error) -> McpError
```
- Converts internal errors to `McpError::internal_error()`

## Runtime

The server uses a **current-thread** async runtime (tokio), confined locally so the CLI command dispatch in `main.rs` stays synchronous:

```rust
pub fn run() -> Result<()> {
    let rt = tokio::runtime::Builder::new_current_thread()
        .enable_all()
        .build()?;
    rt.block_on(async {
        let service = server().serve(stdio())?;
        service.waiting().await?;
        Ok(())
    })
}
```

Rationale: a single stdio client needs no parallelism. The proxy (`serve`) uses multi-thread since it handles many connections.

## Client Configuration

### Config JSON Generation (`client_config_json`)

Generates a Claude Code MCP client config:

```json
{
  "mcpServers": {
    "llmtrim": {
      "command": "llmtrim",
      "args": ["mcp"],
      // additional transport config
    }
  }
}
```

### Installation Flow (`install_with`)

- With `--print` flag: prints config JSON to stdout
- With `--force` or no existing config: removes existing config, adds new one via `claude mcp add`
- Detects `claude` CLI availability for auto-install
- If `claude` is not installed, falls back to printing

## MCP Protocol Tests (`mcp_protocol.rs`)

End-to-end integration tests using `rmcp::ServiceExt`:

1. **`initialize_list_and_call_over_jsonrpc`**:
   - Creates temp DB for tracker
   - Spawns server and client over stdio transport within same process
   - `client.list_all_tools()` -> verifies 3 tools exist
   - Validates tool input schemas are present

2. **Tool tests**:
   - `llmtrim_compress`: sends realistic request body, verifies `request_json` is string, `input_tokens_before > 0`, `stages` non-empty, `provider == "openai"`
   - `llmtrim_compress_text`: sends `"repeat me\nrepeat me\ntail words here"`, verifies response has `text`, `tokens_saved` integer
   - `llmtrim_stats`: verifies `requests` and `by_model` in response

### Test Infrastructure

```rust
async fn call(client, name, args) -> Value
```
- Constructs `CallToolRequestParams` with tool name and arguments
- Calls `client.call_tool()`, asserts no error
- Extracts text content from first content item
- Parses as JSON and returns

## CLI Integration

The MCP module is exposed through the CLI as subcommands:

```
llmtrim mcp run       # Start the MCP stdio server
llmtrim mcp install   # Install MCP config into Claude Code
```

Defined as `McpAction` enum in `main.rs` (variant details not visible in compressed output).

## Dependencies

- `rmcp` - Rust MCP Protocol implementation
- `serde` / `serde_json` - Serialization/deserialization
- `llmtrim_core` - Core compression library
- `tokio` - Async runtime (current-thread)
- `anyhow` - Error handling
