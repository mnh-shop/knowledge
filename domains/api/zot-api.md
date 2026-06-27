---
name: zot-api
description: "Zot API surfaces — Telegram bot polling API, JSON-RPC protocol, Go SDK, and CLI interface"
tags: [api, zot, telegram]
source: sources/zot/
---

# Zot API

Zot has **no REST/HTTP server** — it operates via CLI subcommands, stdin/stdout JSON-RPC, a Telegram poll-bot, and a Go SDK for programmatic embedding.

## CLI API

Invocation: `zot [subcommand] [flags]`

| Subcommand | Description |
|-----------|-------------|
| *(none)* | Interactive TUI mode (default) |
| `--print` | One-shot print mode — `echo "prompt" \| zot --print` |
| `rpc` | Persistent JSON-RPC over stdin/stdout |
| `telegram` | Start Telegram bot (long-running) |
| `ext` | Extension management subcommand |
| `--version` | Print version (with build ldflags) |
| `--help` | Print usage |

### CLI Flags (shared)

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--provider` | string | `anthropic` | LLM provider id |
| `--model` | string | *provider default* | Model identifier |
| `--api-key` | string | *env var* | API key (overrides env) |
| `--base-url` | string | *catalog default* | Provider base URL override |
| `--system-prompt` | string | *built-in* | Custom system prompt |
| `--reasoning` | string | `off` | Thinking level |
| `--temperature` | float | *catalog default* | Sampling temperature |
| `--max-steps` | int | 50 | Max tool-use iterations |
| `--no-tools` | flag | false | Disable all tools |
| `--sandbox` | flag | false | Enable execution sandbox |
| `--cwd` | string | `.` | Working directory |

## JSON-RPC Protocol (`zot rpc`)

The RPC mode accepts newline-delimited JSON commands on stdin and writes responses/events to stdout.

### Auth

If `$ZOTCORE_RPC_TOKEN` is set, the first command must authenticate:

```json
// Connect
{"type":"hello","token":"..."}
// Response
{"type":"response","id":"...","result":{"protocol_version":1,"version":"0.0.0","provider":"anthropic","model":"claude-opus-4-8"}}
```

### Commands

| Command | Direction | Description |
|---------|-----------|-------------|
| `hello` | client→zot | Authenticate (when token required) |
| `prompt` | client→zot | Submit a prompt, run model + tools, stream events |
| `compact` | client→zot | Trigger history compaction |
| `ext_notify` | zot→client | Extension-originated notification |
| `ext_display` | zot→client | Extension display event |
| `ext_clear_notes` | zot→client | Clear extension notes |

### Prompt Flow

```json
// Request
{"type":"prompt","id":"req-1","text":"list all .go files"}

// Events (streamed progressively)
{"type":"event","id":"req-1","event":{"stop":"",...},"content":[...]}
{"type":"event","id":"req-1","event":{"stop":"end_turn","step":3}}
```

## Telegram Bot API

Zot's Telegram bot uses **polling** (no webhook) — it connects to the Telegram Bot API via `getUpdates`:

### Environment
| Variable | Description |
|----------|-------------|
| `$ZOT_TELEGRAM_TOKEN` | Bot token from BotFather |

### Commands (in chat)

| Command | Description |
|---------|-------------|
| Any text | Submitted as prompt to the model |
| `/status` | Show active turn info (current step, timing) |
| `/cancel` | Cancel the currently running turn |
| File uploads | Files sent as attachments (images → vision context) |

### Features
- Per-chat turn queues (isolates conversations)
- Typing indicator during model inference
- Reply-to-message threading for responses
- File upload handling (MIME-type based)
- Long-running turn cancellation

## Go SDK

The Go SDK (`packages/agent/sdk/`) provides programmatic embedding:

```go
import "github.com/patriceckhart/zot/packages/agent/sdk"

// Create a runtime
rt, err := sdk.New(sdk.Config{
    Provider:     "anthropic",
    Model:        "claude-sonnet-4-6",
    APIKey:       "...",
    SystemPrompt: "You are a helpful coding assistant.",
    Temperature:  0.3,
    MaxSteps:     50,
    Tools:        []string{"read", "write", "edit", "bash"},
    CWD:          "/workspace",
})

// One-shot chat
resp, err := rt.Chat(ctx, "What files are in this directory?")

// Streaming chat
err := rt.ChatStream(ctx, "Explain this code", func(chunk string) {
    fmt.Print(chunk)
})

// Add custom tools
rt.AddTool(myTool)

// List available models
models := rt.ListModels()

// Switch model within same provider
rt.SetModel("claude-opus-4-8")

// Get state snapshot
state := rt.State()
fmt.Println(state.Step, state.Provider, state.Model)
```

SDK Features:
- Thread-safe (`mu.RLock`/`RUnlock` on all public methods)
- No session persistence (caller manages transcripts)
- Sandbox lock on startup (optional)
- File attachment support

## Integration Summary

| Interface | Protocol | Auth | Use Case |
|-----------|----------|------|----------|
| CLI | subprocess exit code + stdout | None | Interactive TUI, one-shot prompts |
| RPC | JSON over stdin/stdout | `$ZOTCORE_RPC_TOKEN` | Embedding via pipe (goclaw, agentfield) |
| Telegram | Polling HTTP | Bot token | Chat-based remote access |
| SDK | Go function calls | API key in config | Embedding in Go programs |

## Related Documentation

- [[zot-architecture]] — Full architecture doc
- [[zot-mcp-implementation]] — Extension protocol as MCP surface
- [[zot-deployment]] — Deployment patterns
- [[goclaw-api]] — GoClaw API (potential RPC consumer)
- Source: `sources/zot/packages/agent/rpc.go`, `sources/zot/packages/agent/sdk/`, `sources/zot/packages/agent/modes/telegram/`
