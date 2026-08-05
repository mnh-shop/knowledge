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

### `run.py` — Gateway bootstrap (`GatewayRunner`)

`GatewayRunner` (defined at `gateway/run.py:5399`; the file is 25,765 LOC —
the largest module in the repo) is the long-lived process core. It:
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

Dynamic registry (`gateway/platform_registry.py:162`) that maps platform names
to their adapter classes. Supports late-binding registration for tool use
(e.g., `send_message_tool` needs to find a platform by name).

### `stream_dispatch.py` — `GatewayEventDispatcher`

`GatewayEventDispatcher` (`gateway/stream_dispatch.py:40`) routes streaming
events from the agent core to the correct platform's output channel. Handles
message chunks, tool progress, interruptions.

### `delivery.py` — Message delivery

Routes completed messages to their target platform. Handles:
- Rate limiting per platform
- Platform-specific formatting
- Cross-platform delivery (relay)
- Post-delivery callbacks

### `relay/` — Cross-platform relay + connector contract

Allows messages received on one platform to be forwarded to another:
e.g., "Monica sent a Telegram message that Hermes relays to a Slack thread."
Uses the adapter pattern (`RelayAdapter`).

**Experimental connector contract.** `gateway/relay/` also implements the
*Relay ↔ Connector Contract v1* (`docs/relay-connector-contract.md`, marked
EXPERIMENTAL). The gateway runs a generic `RelayAdapter` that dials **out** to
an external connector (`NousResearch/gateway-gateway`, Node/TypeScript) and
exchanges normalized `MessageEvent`s over a per-turn bidirectional WebSocket.
At handshake the connector returns a `CapabilityDescriptor`
(`gateway/relay/descriptor.py`) describing the fronted platform — the gateway
never learns which concrete platform it is talking to. `contract_version`
(now `1`) is carried in the descriptor and evolution is additive-only. The
production transport is `WebSocketRelayTransport`
(`gateway/relay/ws_transport.py`).

### `hooks.py` / `builtin_hooks/` — Message pipeline hooks

- `gateway/hooks.py` — `HookRegistry` (`:52`) with
  `_register_builtin_hooks()` (`:72`) registers built-in hook handlers that
  run per incoming message.
- `gateway/builtin_hooks/` — bundled built-in hook definitions.
- Hooks are configured in `config.yaml` under a `hooks:` key, and
  `hooks_auto_accept: true` (default `False`, `hermes_cli/config_defaults.py`)
  auto-accepts hook prompts for CI/headless runs (equivalent to
  `HERMES_ACCEPT_HOOKS=1`).

## Platform adapter inventory

The gateway connects through **30 adapter classes** split across two locations:

| Source | Count | Adapters |
|---|---|---|
| `plugins/platforms/` (bundled plugins) | 21 | buzz, dingtalk, discord, email, feishu, google_chat, homeassistant, irc, line, matrix, mattermost, ntfy, photon, raft, simplex, slack, sms, teams, telegram, wecom, whatsapp |
| `gateway/platforms/` (core) | 9 | api_server, signal, weixin, yuanbao, qqbot, bluebubbles, whatsapp_cloud, msgraph_webhook, webhook |

The base class for all of them is `BasePlatformAdapter`
(`gateway/platforms/base.py:2626`); `WebhookAdapter`
(`gateway/platforms/webhook.py:177`) is one of the core nine.

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

(The canonical class is `gateway/platforms/base.py:2626`.)

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
hermes gateway [run|start|stop|restart|status|install|uninstall|setup|enroll|list]
hermes gateway enroll            # Enroll a platform
hermes slack                     # Configure Slack
hermes whatsapp                  # Configure WhatsApp Cloud
hermes webhook                   # Manage webhooks
hermes approvals                 # Mine approval history into allowlist proposals
hermes pairing [list|approve]    # DM pairing codes for user authorization
hermes dashboard                 # Web UI dashboard (port 9119)
```

`hermes gateway` has a full service lifecycle (`run`, `start`, `stop`,
`restart`, `status`, `install`, `uninstall`), plus `setup` (interactive
platform configuration), `enroll`, `list` (profile gateway status), and
`migrate-legacy` (`hermes_cli/subcommands/gateway.py`). Pairing
(`hermes_cli/subcommands/pairing.py`) manages DM pairing codes used for user
authorization on direct-message platforms; approvals
(`hermes_cli/subcommands/approvals.py`) mines past approval decisions from the
session DB into `command_allowlist` proposals.

## Related

- [[hermes-gateway-platforms]] -- Platform adapter reference
- [[hermes-agent]] -- Core agent runtime
- [[hermes-agent-architecture]] -- System architecture
- [[hermes-agent-deployment]] -- Deployment guide

## Links

- Gateway bootstrap (`GatewayRunner`): `sources/hermes-agent/gateway/run.py`
- Base adapter: `sources/hermes-agent/gateway/platforms/base.py`
- Platform config: `sources/hermes-agent/gateway/config.py`
- Platform registry: `sources/hermes-agent/gateway/platform_registry.py`
- Stream dispatch: `sources/hermes-agent/gateway/stream_dispatch.py`
- Delivery: `sources/hermes-agent/gateway/delivery.py`
- Relay connector contract: `sources/hermes-agent/docs/relay-connector-contract.md`
- WebSocket relay transport: `sources/hermes-agent/gateway/relay/ws_transport.py`
- Hooks: `sources/hermes-agent/gateway/hooks.py` + `gateway/builtin_hooks/`
- Plugin platforms: `sources/hermes-agent/plugins/platforms/`
- Core platforms: `sources/hermes-agent/gateway/platforms/` (incl. `webhook.py`)
- Gateway CLI: `sources/hermes-agent/hermes_cli/subcommands/gateway.py`
- Approvals CLI: `sources/hermes-agent/hermes_cli/subcommands/approvals.py`
- Pairing CLI: `sources/hermes-agent/hermes_cli/subcommands/pairing.py`
