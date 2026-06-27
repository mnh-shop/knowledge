---
name: zot-architecture
description: "Zot coding agent harness — Go single-binary architecture, run modes, tool system, extension protocol, swarm mode, SDK"
tags: [architecture, zot, golang, coding-agent]
source: sources/zot/
---

# Zot Architecture

**Zot** (`github.com/patriceckhart/zot`) is an ultra-lightweight Go coding agent harness — a single static binary with 25+ LLM providers, 4 built-in tools, a JSON-RPC extension system, swarm multi-agent mode, a Telegram bot, and a Go SDK for embedding. Designed as a minimal, composable alternative to heavier agent frameworks.

## Repository Layout

```
cmd/zot/main.go          # Entry point (version ldflags, delegates to agent.Run)
packages/agent/           # Core agent: CLI, build, config, RPC, model sync
  modes/                  # Run modes: interactive (TUI), telegram, RPC, JSON
    interactive.go        # Full TUI with bubbletea (dialog, editor, scroll)
    telegram/bot.go       # Telegram poll-loop bot
  tools/                  # Tool implementations
    read.go, write.go, edit.go, bash.go
    telegram_send.go      # telegram_send_image, telegram_send_file
    sandbox.go            # Path-jailing for bash tool
  ext/                    # Extension side library (subprocess authoring SDK)
  extproto/               # Extension wire protocol frame types
  extensions/             # Extension host manager (subprocess lifecycle)
  skills/                 # SKILL.md-based tool system
  swarm/                  # Multi-agent subprocess orchestration
  sdk/                    # Go SDK for embedding zot in other programs
packages/core/            # Provider-agnostic agent loop, tool runtime, session persistence
  tool.go, agent.go
packages/provider/        # LLM provider clients and model catalog
  anthropic.go, openai.go, gemini.go, openai_codex.go
  extra_providers.go, catalog_builtin.go, models.go
  amazon_bedrock.go, google_vertex.go, azure_openai.go
  github_copilot.go, sse.go
  reasoning.go            # Thinking/reasoning budget normalization
```

## Run Modes

Zot has three primary execution modes, selected via subcommand:

| Mode | Command | Description |
|------|---------|-------------|
| **Interactive (TUI)** | `zot` (default) | Full bubbletea TUI with scrollable chat, file suggestions, dialogs, panels, inline editor, image clipboard |
| **Print** | `zot --print` | One-shot: accepts a prompt via `echo "prompt" \| zot --print`, prints model + tool output to stdout, exits |
| **JSON RPC** | `zot rpc` | Persistent JSON-RPC over stdin/stdout with auth token support (`$ZOTCORE_RPC_TOKEN`) — designed for embedding via pipe |
| **Telegram** | `zot telegram` | Long-running Telegram bot with per-chat turn queues and typing indicator |

## Core Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      zot binary                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Interactive  │  │   RPC Mode   │  │  Telegram Bot  │  │
│  │   (TUI)      │  │  (stdin/out) │  │ (poll-loop)    │  │
│  └──────┬───────┘  └──────┬───────┘  └───────┬────────┘  │
│         │                 │                   │           │
│  ┌──────┴─────────────────┴───────────────────┴────────┐  │
│  │               Agent Build (build.go)                 │  │
│  │  - ResolvArgs → provider, model, tools, sandbox     │  │
│  │  - Merge extension tools into tool registry          │  │
│  │  - Build provider.Client from credential resolution  │  │
│  └──────────────────────┬──────────────────────────────┘  │
│  ┌──────────────────────┴──────────────────────────────┐  │
│  │               core.Agent (agent.go)                 │  │
│  │  - Turn loop: user msg → LLM → tool calls → repeat  │  │
│  │  - Hooks: BeforeToolExecute, BeforeTurn, OnEvent    │  │
│  │  - History compaction, tool result repair            │  │
│  └──────────────────────┬──────────────────────────────┘  │
│  ┌──────────────────────┴──────────────────────────────┐  │
│  │            Tool Registry (4 built-in)               │  │
│  │  read │ write │ edit │ bash + extension tools       │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │   Provider Clients (25+ providers)                  │  │
│  │   anthropic │ openai │ gemini │ groq │ xai │ ...   │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │   Extension Manager (subprocess JSON-RPC)           │  │
│  │   + Swarm Manager (multi-agent subprocess)          │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Tool System

Four built-in tools all implement the `core.Tool` interface (`Name()`, `Description()`, `Schema()`, `Execute()`):

| Tool | Name | Description |
|------|------|-------------|
| **Read** | `read` | Read files with offset/limit, returns text content |
| **Write** | `write` | Write to files with full content replacement |
| **Edit** | `edit` | Search-and-replace edits with old_string/new_string |
| **Bash** | `bash` | Execute shell commands (with sandbox path-jailing) |
| **Telegram Send Image** | `telegram_send_image` | Send an image to a Telegram chat |
| **Telegram Send File** | `telegram_send_file` | Send a file to a Telegram chat |

The bash tool includes a **Sandbox** (`packages/agent/tools/sandbox.go`) that jails the working directory — prevents `rm -rf /`, restricts `cd` to within the sandbox root, and blocks destructive commands. Toggle with `/jail` and `/unjail` in TUI mode.

### Skill Tool

Zot supports **SKILL.md**-based tool definitions (`packages/agent/skills/tool.go`). A `SKILL.md` file in the workspace root or `$ZOT_HOME/skills/` defines a structured prompt that zot registers as a callable `skill` tool. The file format includes `name:`, `description:`, `schema:`, and instruction blocks the model reads when the skill is invoked.

## Provider System

Zot supports **25+ LLM providers** via a unified `provider.Client` interface (`Stream(ctx, Request) → <-chan Event`):

### Primary Providers (native wire format)
- **Anthropic** — Messages API with extended thinking, extended thinking budget, prompt caching
- **OpenAI** — Chat Completions API
- **OpenAI Responses** — Responses API (api.openai.com/v1/responses)
- **OpenAI Codex** — ChatGPT Codex backend (OAuth subscription)
- **Gemini** — Google AI API
- **Amazon Bedrock** — Converse Stream API (SigV4 signing, hand-rolled parser)
- **Google Vertex AI** — Vertex AI with ADC authentication
- **GitHub Copilot** — Copilot token exchange + Chat Completions

### OpenAI-Compat Providers (reuse openaiClient with renamed base URL)
- **Groq** — LPU inference, Llama/Kimi/Qwen models
- **xAI** — Grok models
- **Together** — model aggregation
- **OpenRouter** — 200+ model aggregation
- **Cerebras** — ultra-fast inference
- **HuggingFace** — inference router
- **Moonshot** (global + CN) — Kimi-K2 family
- **Mistral** — Le Chat/Models API via OpenAI compat
- **Z.AI** — GLM family
- **Xiaomi MiMo** (global + 3 regional token plans)
- **DeepSeek** — R1/V3 models
- **Cloudflare Workers AI** + **AI Gateway**

### Anthropic-Compat Providers (reuse anthropicClient)
- **Kimi Coding** — Kimi behind Messages API
- **MiniMax** (global + CN) — both OpenAI and Anthropic flavors
- **Fireworks** — both OpenAI and Anthropic flavors
- **Vercel AI Gateway** — both OpenAI and Anthropic flavors

### Reasoning / Thinking
The `Reasoning` level maps across six tiers (`minimum`/`low`/`medium`/`high`/`maximum`/`off`) and normalizes to each provider's native format:
- **Budget-based** (Claude Opus <4.x): explicit thinking budget tokens (1k–32k)
- **Adaptive effort** (Claude 4.7+, Gemini): `low`/`medium`/`high`/`xhigh` effort enum
- **OpenAI reasoning**: `minimal`/`low`/`medium`/`high` for o-series models
- Reasoning disabled by default

### Model Discovery
- **Built-in catalog**: ~400 hand-curated model entries across all providers in `catalog_builtin.go` and `models.go`
- **Live discovery**: Background refresh from each provider's `/v1/models` endpoint (cached 6h)
- **User overrides**: `$ZOT_HOME/models.json` for custom providers, base URLs, and models

## Extension System

Zot's most distinctive architectural feature is its **subprocess extension system** — extensions are standalone Go binaries that communicate with the zot host via JSON-RPC over stdin/stdout.

### Extension Protocol (`extproto`)
Each extension binary starts as a subprocess managed by the `Extension Manager`. The protocol uses newline-delimited JSON frames:

```
Extension → Host:  hello, register_tool, register_command, subscribe, ready
Host → Extension:  hello_ack, command_invoked, tool_call, event, shutdown
Extension → Host:  command_response, tool_result, notify, display, submit_slash, open_panel
```

### Extension Capabilities
- **Register tools**: Extensions define `Tool(name, description, schema, handler)` — these fold into the agent's core tool registry
- **Register slash commands**: Extensions define `Command(name, description, handler)` — appear as `/command` in the TUI
- **Intercept tool calls**: Block, allow, or rewrite tool arguments mid-flight (before the tool executes)
- **Intercept turns**: Guard before each model call (deny-by-default gates, usage quotas)
- **Intercept assistant messages**: Suppress or rewrite model output before display
- **Subscribe to events**: Receive agent event stream (turn_start, tool_call, assistant_message)
- **Open/Panel/Key**: Render interactive panels with masked input, keyboard handlers, close callbacks
- **Spontaneous frames**: Extensions can push `notify`, `display`, `submit_slash`, `open_panel` frames at any time

Extensions are discovered from `$ZOT_HOME/extensions/` and can be hot-reloaded without restarting zot.

## Swarm Multi-Agent Mode

Zot includes a **swarm subsystem** (`packages/agent/swarm/`) for multi-agent orchestration:

- **Swarm** manages multiple zot subprocess agents as independent workers
- Each agent runs in its own directory with its own session
- Agents communicate status via JSONL event protocol over stdout
- A supervisor component manages agent lifecycle (spawn, cancel, shutdown)
- Designed for parallel task execution with subprocess isolation

## SDK (`packages/agent/sdk/`)

Zot provides a Go SDK (`sdk.New(cfg) → *Runtime`) for embedding the agent in other Go programs:

```go
rt, err := sdk.New(sdk.Config{
    Provider: "anthropic",
    Model:    "claude-opus-4-8",
    APIKey:   "...",
    Tools:    []string{"read", "write", "bash"},
})
resp, err := rt.Chat(context.Background(), "list all .go files")
```

SDK features:
- Headless execution (JSON mode internally)
- Lock sandbox to jail bash tool
- Chat / ChatStream conversation methods
- Add user-defined tools
- Switch models within same provider
- List available models
- Session state snapshot
- File attachment support

## Telegram Bot

Built-in Telegram bot mode (`zot telegram`):
- Polling-based (no webhook HTTP server needed)
- Per-chat turn queues — isolates conversations
- Typing indicator during model inference
- `/status` command for active turn info
- `/cancel` to stop a running turn
- File upload support (images auto-sent as vision context)
- Multi-chat isolation

## Persistence

- **Session transcripts**: JSONL-based transcript files in `$ZOT_HOME/sessions/`
- **Config**: `$ZOT_HOME/config.json` (provider, model, system prompt, temperature, etc.)
- **Model cache**: `$ZOT_HOME/models-cache.json` (live-discovered models, 6h TTL)
- **User models**: `$ZOT_HOME/models.json` (custom provider/model definitions)

## Integration Points

- **agentfield**: Zot's Go SDK (`packages/agent/sdk/`) enables direct embedding in agentfield sandboxes — agentfield can spawn zot as a coding sub-agent within a micro-VM for isolated code execution
- **goclaw**: Zot's RPC mode (`zot rpc --ext`) and extension protocol provide a clean subprocess interface. goclaw can wire zot as a lightweight coding worker behind GoClaw's tool bridge
- **hermes-agent**: Zot can run as a `skill` tool via SKILL.md or be embedded via the SDK as a coding specialist in hermes-agent's multi-platform setup

## Related Documentation

- [[zot-mcp-implementation]] — Extension protocol as MCP-adjacent tool surface
- [[zot-api]] — Telegram bot and JSON-RPC API surfaces
- [[zot-acp-implementation]] — Swarm mode as ACP-adjacent multi-agent orchestration
- [[zot-deployment]] — Single-binary deployment patterns
- Source: `sources/zot/` with `.codegraph/` index
