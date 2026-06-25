---
name: nanobot-architecture
tags: [ai-llm, architecture, cli, dashboard, event-bus, mcp, messaging, monitoring, multi-platform, nanobot, plugin-sdk, security, webhook]
description: "Deep architecture of nanobot: MessageBus, agent loop, channel system, provider abstraction, and tool framework"
---

# nanobot Architecture

nanobot is an ultra-lightweight personal AI agent framework built in Python 3.11+ with asyncio. This document covers its internal architecture: event bus, agent loop, channel system, provider abstraction, tool framework, memory, and WebUI.

## Core Architecture

```
                     ┌─────────────────────────────────────┐
                     │          Gateway Process              │
                     │                                       │
                     │  ┌─────────────────────────────────┐  │
                     │  │         MessageBus               │  │
                     │  │  (Async pub/sub queue)           │  │
                     │  │                                   │  │
                     │  │    InboundMessage events          │  │
                     │  │    OutboundMessage events          │  │
                     │  │    RuntimeEvent events             │  │
                     │  └──────┬───────────────────────┬───┘  │
                     │         │                       │      │
                     │  ┌──────▼──────┐    ┌──────────▼───┐  │
                     │  │  Channels   │    │  AgentLoop    │  │
                     │  │  (N x N)    │◄──►│  + Runner     │  │
                     │  └─────────────┘    └──────┬────────┘  │
                     │                            │          │
                     │  ┌─────────────────────────▼────────┐  │
                     │  │     Provider (LLM API)            │  │
                     │  └──────────────────────────────────┘  │
                     └─────────────────────────────────────┘
```

## MessageBus (`nanobot/bus/queue.py`)

The MessageBus is the central event hub that decouples all components. It uses `asyncio.Queue` for event distribution:

- **InboundMessage:** Published by channels when a message arrives from an external platform. Consumed by AgentLoop.
- **OutboundMessage:** Published by AgentLoop when a response is ready. Consumed by the appropriate channel for delivery.
- **RuntimeEvent:** Internal lifecycle events (gateway start/stop, config reload, etc.).
- **ProgressEvent:** Progress updates from long-running tool executions.

The bus supports multiple subscribers per event type, allowing features like WebUI streaming, logging, and telemetry to observe message flow without modifying the core loop.

## Agent Loop (`nanobot/agent/loop.py`)

The `AgentLoop` is the main coordination component:

1. **Session Resolution:** Maps incoming messages to the correct session (per-channel, per-user), creating or loading session state.
2. **Context Building:** Assembles the full context for the LLM call:
   - System prompt (from agent configuration)
   - Session memory (compressed history)
   - Active goal state (sustained objectives)
   - Skill definitions
   - Tool schemas
   - Current turn messages
3. **Turn Coordination:** Calls `AgentRunner` to execute the LLM conversation, passing in context and processing tool calls/streaming responses.
4. **Hook System:** Pre/post-turn hooks for instrumentation, logging, Langfuse observability, and progress tracking.
5. **Auto-Compaction:** After each turn, automatically compacts session history when token count exceeds thresholds (`autocompact.py`).

### Agent Loop Lifecycle

```
Message arrives → Session resolve → Context build → AgentRunner turn
                                                      │
                                          ┌───────────┴───────────┐
                                          ▼                       ▼
                                    Provider call           Tool calls
                                    (LLM stream)         (execute tools)
                                          │                       │
                                          └───────────┬───────────┘
                                                      ▼
                                              Response stream
                                          (publish OutboundMessage)
                                                      │
                                                      ▼
                                              Auto-compact check
                                                      │
                                                      ▼
                                              Post-turn hooks
```

## Agent Runner (`nanobot/agent/runner.py`)

The `AgentRunner` manages the multi-turn LLM conversation within a single user turn:

1. Sends the initial message to the provider
2. Receives streaming text and tool call requests
3. Executes requested tools via the tool registry
4. Sends tool results back to the provider
5. Repeats until the provider produces a final text response
6. Streams the response back to the caller

Key design decisions:
- **Exponential Backoff:** On provider errors, retries with increasing delays
- **Token Budgeting:** Respects per-model context windows with safety margins
- **Streaming:** All responses are streamed; the WebUI and channels receive tokens incrementally

## Channel System (`nanobot/channels/`)

Channels implement platform-specific adapters that normalize external messages to `InboundMessage` events and deliver `OutboundMessage` events to the platform.

### Channel Discovery

Channels are auto-discovered via:
1. `pkgutil` scan of the `nanobot.channels` package
2. Entry-point plugins (`nanobot.channels` group)

### Channel Manager

The `manager.py` module:
- Discovers and initializes configured channels at startup
- Registers channel event handlers with the MessageBus
- Manages channel lifecycle (start, stop, restart)
- Provides per-channel health status

### Supported Channels (17+)

| Channel | Protocol | Special Features |
|---|---|---|
| Telegram | Bot API | Inline buttons, webhooks/polling, topic groups |
| Discord | Gateway API | Thread sessions, allow-lists |
| Slack | Events API + WebSocket | Allow-listed channels, mention-only |
| Feishu/Lark | Card API | Streaming, done-emoji, threads |
| Matrix | Client-Server API | Verification, room state |
| WeChat | WeChat SDK | Multimodal, voice, QR auth |
| WhatsApp | Bridge + Cloud API | Media, pairing |
| Signal | Signal CLI | E2E encryption |
| Email | IMAP/SMTP | Attachments, threads |
| QQ | NapCat | Pairing, media |
| DingTalk | Webhook | Media links |
| WeCom | Bot API | Enterprise features |
| MoChat | Custom | Chinese market |
| MS Teams | Bot Framework | Adaptive cards |
| WebSocket | Custom protocol | Bidirectional JSON |

## Provider System (`nanobot/providers/`)

LLM providers implement a common base (`base.py`) defining the provider interface. The Provider Registry (`registry.py`) discovers and manages providers.

### Provider Base Interface
```python
class Provider:
    async def chat(self, messages, tools, ...) -> AsyncIterator[StreamEvent]: ...
    async def models(self) -> list[ModelInfo]: ...
```

### Built-in Providers

- Anthropic (Claude models, adaptive thinking)
- OpenAI-compatible (generic, any OpenAI-compatible API)
- OpenAI Responses API
- Azure OpenAI (with AAD support)
- AWS Bedrock (Claude, Llama, Mistral)
- GitHub Copilot (GPT-5, o-series)
- OpenCode
- Google Gemini
- Kimi (K2.x)
- MiniMax
- DeepSeek
- StepFun
- Zhipu
- NVIDIA NIM
- Ollama (local models)
- LM Studio (local OpenAI-compatible)

### Model Routing

`factory.py` handles provider selection with:
- Primary/fallback model configuration
- Per-request model override
- `fallback_models` list for automatic failover
- `model_presets.py` for saved model configurations in WebUI

## Tool System (`nanobot/agent/tools/`)

Tools are the agent's capabilities exposed to the LLM. Each tool implements a base interface with:
- Name, description, and JSON Schema parameters
- `__call__` method for execution
- Optional lifecycle hooks (before/after execute)

### Tool Discovery

Same pattern as channels: `pkgutil` scan + entry-point plugins.

### Built-in Tools (30+)

| Tool | Purpose |
|---|---|
| `filesystem` | Read/write/edit/list project files with diff tracking |
| `shell` | Execute shell commands with sandbox backends |
| `web` | HTTP fetch, web search (multiple providers) |
| `mcp` | Connect to MCP servers as tools |
| `cron` | Schedule recurring tasks |
| `exec_session` | Persistent REPL sessions |
| `long_task` | Long-running background tasks |
| `spawn` | Spawn subagents |
| `search` | Codebase search (grep, glob) |
| `image_generation` | Generate images via provider APIs |
| `apply_patch` | Apply structured patches |
| `message` | Send messages to other channels |
| `self` | Self-modification tools |
| `sandbox` | Isolated execution environments |
| `context` | Context management tools |
| `runtime_state` | Runtime state introspection |

## Memory System (`nanobot/agent/memory.py`)

Two-phase memory consolidation (Dream):

1. **Working Memory:** Active session conversation history kept in memory for the current turn
2. **Consolidated Memory:** Periodically summarized and compacted to prevent unbounded growth

Implementation details:
- Atomic writes with `fsync()` for crash safety
- Auto-repair on corruption detection
- Token-based compaction triggers
- Session-aware (per-channel, per-user)

## Session Management (`nanobot/session/`)

Sessions track per-user, per-channel conversation state:

- **`manager.py`** -- Session lifecycle, history persistence, TTL-based auto-expiry, compaction
- **`goal_state.py`** -- Sustained goal tracking (`/goal` command), multi-turn objective persistence with progress tracking
- Context window management with configurable token limits

## WebUI (`webui/`)

Vite-based React SPA compiled and bundled into the Python wheel via `hatch_build.py`:

- **Transport:** WebSocket multiplex protocol to the gateway
- **Dev server:** Proxies `/api`, `/webui`, `/auth`, and WebSocket to the gateway at `:8765`
- **Build output:** Goes to `nanobot/web/dist/` then bundled into the wheel
- **Key views:** Chat timeline, file editor, model selection, settings, project workspace
- **Themes:** Dark/light mode, locale selector (i18n)

### WebUI ↔ Gateway Protocol

```
WebUI ─── WebSocket ──▶ Gateway
            │
            ├── /api/* (REST for settings, config)
            ├── WebSocket multiplex (chat sessions per channel)
            └── SSE stream (live response display)
```

## Config System (`nanobot/config/`)

Pydantic-based configuration loaded from `~/.nanobot/config.json`:

- **`schema.py`** -- Pydantic models with camelCase aliases for JSON compatibility
- **`loader.py`** -- Config file loading, defaults, validation
- **`paths.py`** -- Path resolution for config, data, sessions

## Gateway (`nanobot/gateway/`)

The gateway is the main process that ties everything together:

- Starts the HTTP/WebSocket server
- Initializes MessageBus
- Discovers and starts channels
- Initializes the agent loop
- Serves WebUI static files
- Exposes OpenAI-compatible API endpoints
- Manages process lifecycle

## API Server (`nanobot/api/server.py`)

OpenAI-compatible HTTP API for programmatic access:

| Route | Description |
|---|---|
| `POST /v1/chat/completions` | Chat completions (streaming via SSE) |
| `GET /v1/models` | List available models |

## Security Architecture

- **PTH Guard:** Blocks dangerous filesystem operations outside allowed paths
- **Shell Sandbox:** Isolates shell execution with configurable allow-lists
- **Pairing Store:** DM sender approval with persistent pairing codes per channel
- **Environment Isolation:** No autonomous code runs on the host OS

## Startup Sequence

```
1. CLI entry point (nanobot.cli.commands)
2. Load config from ~/.nanobot/config.json
3. Initialize MessageBus
4. Discover and initialize channels
5. Discover and register tools
6. Initialize AgentLoop with session manager
7. Start HTTP/WS gateway server
8. Connect channels to MessageBus
9. Start WebUI dev/build server (if applicable)
10. Handle incoming messages (event loop)
```

## Related

- [[nanobot]] -- Overview wiki entry
- [[hermes-agent]] -- Similar architecture (Python agent with channels/tools/providers)
- [[openclaw]] -- Competing agent platform (TypeScript with different channel architecture)
- [[n8n]] -- Workflow engine that integrates via webhooks
- [[agentfield]] -- Control plane that can orchestrate nanobot agents
- [[mission-control]] -- Dashboard that can monitor nanobot gateway
