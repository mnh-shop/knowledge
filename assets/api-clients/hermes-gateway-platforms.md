---
name: hermes-gateway-platforms
tags: [agent-gateway, ai-llm, api-client, cli, hermes, messaging, multi-platform, plugin-sdk, rest-api, typescript, webhook]
description: "Gateway platform adapter reference for Hermes Agent: 20+ messaging platforms through the BasePlatformAdapter pattern"
---

# Gateway Platforms — Platform Adapter Reference

**Source:** `sources/hermes-agent/gateway/`, `sources/hermes-agent/plugins/platforms/`
**Base class:** `gateway/platforms/base.py:BasePlatformAdapter`

## What it is

Hermes connects to ~20+ messaging platforms through a unified adapter
pattern. Each platform has an adapter class that extends
`BasePlatformAdapter` and implements platform-specific logic for
connecting, authenticating, receiving messages, sending responses, and
handling media.

## Core Platform Adapters (`gateway/platforms/`)

| Platform | Class | File | Async delivery | Splits messages |
|---|---|---|---|---|
| Telegram | Telegram adapter | `telegram/` | Yes | Yes |
| Discord | Discord adapter | `discord/` | Yes | Yes |
| Slack | Slack adapter | `slack/` | Yes | No |
| WhatsApp Cloud | `WhatsAppCloudAdapter` | `whatsapp_cloud.py` | Yes | No |
| Webhook | `WebhookAdapter` | `webhook.py` | No | No |
| QQ Bot | `QQAdapter` | `qqbot/adapter.py` | Yes | No |

**WhatsApp shared logic:** `gateway/platforms/whatsapp_common.py`
→ `WhatsAppBehaviorMixin` (access policy, reply prefix, chunk limits)

## Plugin Platforms (`plugins/platforms/`)

| Platform | Class | File |
|---|---|---|
| IRC | `IRCAdapter` | `irc/adapter.py` |
| SMS | `SmsAdapter` | `sms/adapter.py` |
| LINE | `LineAdapter` | `line/adapter.py` |
| Ntfy | `NtfyAdapter` | `ntfy/adapter.py` |
| Raft | `RaftAdapter` | `raft/adapter.py` |

**Photon sidecar CLI:** `plugins/platforms/photon/cli.py` — manages
Photon gateway-sidecar deployment (status, setup, install, telemetry).

## `BasePlatformAdapter` key interface

```python
class BasePlatformAdapter(ABC):
    supports_code_blocks: bool = False       # Renders markdown fences
    supports_async_delivery: bool = True     # Can push notifications after turn
    splits_long_messages: bool = False       # Chunks in send()
    typed_command_prefix: str = "/"          # "/" or "!" for Matrix/Slack

    def __init__(self, config, platform):
        # Per-session state tracking
        self._active_sessions: Dict[str, asyncio.Event]
        self._session_tasks: Dict[str, asyncio.Task]
        self._post_delivery_callbacks: Dict[str, Any]
```

### Capability flags

| Flag | What it controls |
|---|---|
| `supports_code_blocks` | Whether `format_message` renders triple-backtick as real code blocks. Telegram, Discord → True; plain-text → False |
| `supports_async_delivery` | Whether the adapter can push background completions (terminal notify, subagent results) after a turn. Stateless adapters (API server) → False |
| `splits_long_messages` | Whether `send()` splits into multiple messages natively. Discord, Telegram → True (avoids gateway-level truncation) |
| `typed_command_prefix` | Command prefix users see in prompts. `/` for most platforms, `!` for Slack threads and Matrix |
| `enforces_own_access_policy` | Whether adapter gates access before dispatch (WeCom, Weixin, QQBot, WhatsApp) |

### Key properties

- **`message_len_fn`** — override for platforms that count characters
  differently (Telegram returns `len` in UTF-16 code units)

### Feature detection

- **`supports_draft_streaming()`** — whether adapter supports native
  streaming-draft updates (Telegram → True for DMs; uses `sendMessageDraft`)
- **`prefers_fresh_final_streaming()`** — whether to send a fresh final
  message (deleting the preview) instead of editing the preview. Telegram
  returns True because `sendRichMessage` is richer than the edit path

## Gateway infrastructure (`gateway/`)

| File | Purpose |
|---|---|
| `run.py` | Gateway bootstrap, platform binding, runner loop |
| `config.py` | `Platform` enum, config loading, env overrides |
| `platform_registry.py` | `PlatformRegistry` — dynamic platform discovery |
| `stream_dispatch.py` | `GatewayEventDispatcher` — routes streaming events |
| `delivery.py` | Message delivery routing and rate limiting |
| `session.py` | Session keying and management |
| `slash_commands.py` | Platform-level slash commands |
| `hooks.py` | Gateway lifecycle hook system |
| `authz_mixin.py` | Authorization mixin |
| `relay/` | Message relay between platforms |

## Platform registration flow

1. `gateway/config.py` defines `Platform` enum with all known platforms
2. `gateway/run.py` reads config, binds platform adapters
3. Built-in adapters live in `gateway/platforms/`
4. Plugin adapters scanned from `plugins/platforms/` at startup
5. `PlatformRegistry` provides late-binding registration for tool use

## Related

- [[hermes-gateway-api]] -- Gateway API reference
- [[hermes-agent]] -- Core Hermes Agent runtime
- [[hermes-agent-architecture]] -- System architecture
- [[hermes-mcp-serve]] -- MCP messaging bridge for conversations

## Links

- Base adapter: `sources/hermes-agent/gateway/platforms/base.py`
- Gateway bootstrap: `sources/hermes-agent/gateway/run.py`
- Platform config: `sources/hermes-agent/gateway/config.py`
