---
name: nanobot
tags: [ai-llm, cli, dashboard, desktop-app, docker, event-bus, mcp, messaging, monitoring, multi-platform, plugin-sdk, rest-api, security, webhook]
description: "Open-source ultra-lightweight personal AI agent with WebUI, chat channels, tools, and memory"
---

# Nanobot

**Source:** `sources/nanobot/`

nanobot is an open-source, ultra-lightweight personal AI agent framework from HKUDS (University of Hong Kong). It provides a small, readable agent core with WebUI, multi-platform chat channels (Telegram, Discord, WeChat, Slack, and 15+ more), tools, memory, MCP support, model routing, automation, and deployment. Written in Python with a React/TypeScript WebUI.

| Field | Value |
|---|---|
| **Origin** | [HKUDS/nanobot](https://github.com/HKUDS/nanobot) |
| **License** | MIT |
| **Stack** | Python 3.11+ (asyncio), React/TypeScript (Vite), WebSocket |
| **PyPI** | `pip install nanobot-ai` |
| **Docs** | https://nanobot.wiki |
| **Source** | `sources/nanobot/` |

## Key Features

- **Lightweight Agent Core:** Small agent loop (`nanobot/agent/loop.py`, `runner.py`) that receives messages from chat channels, invokes an LLM provider, executes tools, and manages session memory. Async MessageBus decouples channels from the agent core.
- **Multi-Platform Channels:** 17+ channel integrations including Telegram, Discord, Slack, Feishu, Matrix, WhatsApp, QQ, WeChat, WeCom, DingTalk, Email, Signal, MoChat, MS Teams, and WebSocket. Auto-discovered via `pkgutil` scan + entry-point plugins.
- **Broad Provider Support:** Anthropic, OpenAI-compatible, OpenAI Responses API, Azure, Bedrock, GitHub Copilot, OpenCode, Kimi, MiniMax, DeepSeek, Google Gemini, and more. Provider `factory.py` and `registry.py` handle instantiation and model discovery. Includes image generation and audio transcription.
- **Rich Tool System:** Filesystem (read/write/edit/list), shell execution (with sandbox backends), web search/fetch, MCP server integration, cron scheduling, notebook editing, subagent spawning, long-running tasks/sustained goals (`long_task.py`), image generation, and self-modification. Tools auto-discovered via plugins.
- **Built-in WebUI:** Vite-based React SPA shipped inside the Python wheel. Speaks to the gateway over WebSocket multiplex protocol. Features live chat, file editing, model controls, project workspaces, token heatmaps, and more.
- **Dream Memory:** Two-phase memory consolidation with atomic writes and fsync durability. Sessions auto-compact by default.
- **Sustained Goals (`/goal`):** Long-running objectives persist across conversational turns using goal state tracking.
- **OpenAI-Compatible API:** Exposes `/v1/chat/completions` and `/v1/models` endpoints for programmatic access.
- **MCP Support:** Connect multiple MCP servers as tool providers.
- **Security:** PTH file guard, shell sandbox, pairing/DM approval store, and other measures activated at CLI entry.
- **Docker & Deployment:** Official Docker image, `docker-compose.yml`, macOS LaunchAgent support.
- **Active Development:** Nearly daily releases (v0.1.4 through v0.2.2), 100+ documented releases.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    nanobot Gateway                        │
│                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │Telegram  │  │ Discord  │  │  WeChat  │  │   ...    │ │
│  │ Channel  │  │ Channel  │  │ Channel  │  │ Channels │ │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘ │
│        │              │              │              │      │
│  ┌─────▼──────────────▼──────────────▼──────────────▼──┐  │
│  │               MessageBus (async queue)               │  │
│  │     InboundMessage  /  OutboundMessage events        │  │
│  └───────────────────────┬─────────────────────────────┘  │
│                          │                                 │
│  ┌───────────────────────▼─────────────────────────────┐  │
│  │              AgentLoop + AgentRunner                  │  │
│  │  Context building, LLM conversation, tool execution  │  │
│  └──────┬──────────────────────┬──────────────────────┘  │
│         │                      │                          │
│  ┌──────▼──────┐     ┌─────────▼─────────┐               │
│  │  Providers  │     │      Tools        │               │
│  │  (LLM API)  │     │  (Shell, FS, Web, │               │
│  └─────────────┘     │   MCP, Cron, ...) │               │
│                      └───────────────────┘               │
│                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │  Memory  │  │ Sessions │  │  WebUI   │               │
│  │ (Dream)  │  │ Manager  │  │  (React) │               │
│  └──────────┘  └──────────┘  └──────────┘               │
└─────────────────────────────────────────────────────────┘
```

The data flow: Chat channels receive messages and publish `InboundMessage` events to the async MessageBus. `AgentLoop` consumes inbound messages, builds context, and coordinates the turn. `AgentRunner` handles the LLM conversation loop (send to provider, receive tool calls, execute tools, stream responses). Responses are published as `OutboundMessage` events back to the appropriate channel.

### Key Source Directories

| Directory | Purpose |
|---|---|
| `nanobot/agent/` | Agent core: loop, runner, memory, context, hooks, skills, tools, cron |
| `nanobot/agent/tools/` | 30+ tool implementations (shell, filesystem, web, MCP, cron, spawn, etc.) |
| `nanobot/providers/` | LLM provider implementations (Anthropic, OpenAI, Azure, Bedrock, Gemini, and more) |
| `nanobot/channels/` | 17+ chat channel integrations |
| `nanobot/api/` | OpenAI-compatible HTTP API server |
| `nanobot/config/` | Pydantic-based configuration |
| `nanobot/session/` | Session history, context compaction, goal state |
| `nanobot/bus/` | Async MessageBus with events |
| `nanobot/gateway/` | Gateway runtime and service |
| `nanobot/cli/` | CLI commands and gateway |
| `nanobot/command/` | Slash command routing |
| `nanobot/security/` | PTH file guard and security |
| `nanobot/cron/` | Cron scheduling and automation |
| `nanobot/pairing/` | DM sender approval store |
| `bridge/` | TypeScript bridge services (e.g., WhatsApp) |
| `webui/` | Vite/React SPA bundled into the Python wheel |
| `docs/` | Full documentation suite (20+ docs in multiple languages) |
| `tests/` | Test suite mirroring the `nanobot/` package structure |

## Interfaces

### CLI

| Command | Description |
|---|---|
| `nanobot gateway` | Start the nanobot gateway |
| `nanobot models` | List available AI models |
| `nanobot --help` | Full CLI reference |

### REST API

OpenAI-compatible API served by the gateway:

| Path | Method | Description |
|---|---|---|
| `/v1/chat/completions` | POST | Chat completions (streaming supported) |
| `/v1/models` | GET | List available models |

Also serves `/webui/`, `/api/`, `/auth/`, and WebSocket for the browser UI.

### WebSocket

Multiplexed WebSocket protocol for WebUI communication with the gateway.

### Chat Channels

Messages arrive via platform-specific APIs (Telegram Bot API, Discord gateway, WeChat SDK, etc.) and are normalized to the internal event format.

### MCP

Connects to MCP servers as tool providers. Multiple MCP servers supported simultaneously.

## Related

- [[hermes-agent]] -- Competing Python agent framework with similar architecture
- [[openclaw]] -- Competing agent gateway (TypeScript, MIT)
- [[clawpier]] -- Desktop manager for OpenClaw/Hermes Docker containers
- [[n8n]] -- Workflow engine that can trigger nanobot via webhooks
- [[mission-control]] -- Dashboard that can monitor nanobot
