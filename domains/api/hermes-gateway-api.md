---
name: hermes-gateway-api
description: "Hermes Gateway API reference: multi-platform messaging layer connecting to 20+ platforms through adapter pattern"
source: sources/hermes-agent/
tags: [agent-gateway, api, cli, hermes-agent, messaging, multi-platform, plugin-sdk, rest-api, typescript, webhook]
---

# Hermes Gateway API — Multi-Platform Messaging Layer

## What it is

The Hermes Gateway is a long-lived process that connects Hermes to ~20+
messaging platforms. It receives messages from any platform, routes them
to the agent core, and delivers responses back — potentially to a
*different* platform than the request came from (via the relay system).

## Architecture

```
Platform A (Telegram) ───┐
Platform B (Discord)  ───┤
Platform C (Slack)    ───┼──→ gateway/run.py ──→ Agent Core
Platform D (WhatsApp) ───┤
... (~20 platforms)   ───┘
                              │
                              ▼
                         Delivery back to
                         original or relay
                         target platform
```

## Core infrastructure (`gateway/`)

### `run.py` — Gateway bootstrap

The gateway runner:
1. Loads config from config.yaml via `gateway/config.py`
2. Scans `plugins/platforms/` for plugin-based platform adapters
3. Instantiates and connects each configured platform adapter
4. Binds event handlers for message ingress
5. Runs the main loop (poll each adapter, process messages, deliver responses)
6. Handles lifecycle: start, stop, restart (with `--replace`), crash handling

### `config.py` — Platform configuration

- `Platform` enum — all known platforms (used for registration)
- `PlatformConfig` — per-platform config (API keys, policies, extra settings)
- `_scan_bundled_plugin_platforms()` — discovers plugin-based adapters
- Config can be overridden via env vars (`{PLATFORM}_*`)

### `platform_registry.py` — `PlatformRegistry`

Dynamic registry that maps platform names to their adapter classes.
Supports late-binding registration for tool use (e.g., `send_message_tool`
needs to find a platform by name).

### `stream_dispatch.py` — `GatewayEventDispatcher`

Routes streaming events from the agent core to the correct platform's
output channel. Handles message chunks, tool progress, interruptions.

### `delivery.py` — Message delivery

Routes completed messages to their target platform. Handles:
- Rate limiting per platform
- Platform-specific formatting
- Cross-platform delivery (relay)
- Post-delivery callbacks

### `relay/` — Cross-platform relay

Allows messages received on one platform to be forwarded to another:
e.g., "Monica sent a Telegram message that Hermes relays to a Slack thread."
Uses the adapter pattern (`RelayAdapter`).

## Platform adapters

See the [[hermes-gateway-platforms]] asset for the full adapter reference.

### `BasePlatformAdapter` design (from source)

```python
class BasePlatformAdapter(ABC):
    """All platform adapters inherit from this.

    Subclasses implement platform-specific logic for:
    - Connecting and authenticating
    - Receiving messages
    - Sending messages/responses
    - Handling media
    """
```

Key behavioral flags:

| Flag | Purpose |
|---|---|
| `supports_code_blocks` | True → render fenced code blocks (Telegram, Discord) |
| `supports_async_delivery` | False → stateless (API server can't push notifications after turn) |
| `splits_long_messages` | True → adapter chunks in send(), safe from gateway truncation |
| `typed_command_prefix` | "/" for most, "!" for Slack threads and Matrix clients |
| `enforces_own_access_policy` | True → adapter gates access (WeCom, Weixin, QQBot, WhatsApp) |

### Session state management

Each adapter maintains:
- `_active_sessions` — per-session cancel events
- `_session_tasks` — per-session asyncio Tasks (for interrupting/killing)
- `_post_delivery_callbacks` — one-shot callbacks after message delivery
- `_background_tasks` — background processing tasks (cancelled on shutdown)
- `_busy_text_mode` — "interrupt" (default) or "queue" for busy state
- Voice mode tracking (auto-TTS on voice input)

## Webhook adapter (`gateway/platforms/webhook.py`)

The `WebhookAdapter` is a special adapter:
- Supports dynamic route registration (incoming webhooks)
- Validates signatures (HMAC, Svix)
- Renders prompts from webhook payloads
- Supports `HERMES_API_KEY` authentication
- Can deliver responses back to the webhook origin

## CLI integration

```bash
hermes gateway                   # Start the gateway
hermes gateway enroll            # Enroll a platform
hermes slack                     # Configure Slack
hermes whatsapp                  # Configure WhatsApp Cloud
hermes webhook                   # Manage webhooks
```

## Related

- [[hermes-gateway-platforms]] -- Platform adapter reference
- [[hermes-agent]] -- Core agent runtime
- [[hermes-agent-architecture]] -- System architecture
- [[hermes-agent-deployment]] -- Deployment guide

## Links

- Gateway bootstrap: `sources/hermes-agent/gateway/run.py`
- Base adapter: `sources/hermes-agent/gateway/platforms/base.py`
- Platform config: `sources/hermes-agent/gateway/config.py`
- Platform registry: `sources/hermes-agent/gateway/platform_registry.py`
- Stream dispatch: `sources/hermes-agent/gateway/stream_dispatch.py`
- Delivery: `sources/hermes-agent/gateway/delivery.py`
- Built-in hooks: `sources/hermes-agent/gateway/builtin_hooks/`
