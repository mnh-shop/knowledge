---
name: hermes-telegram-whatsapp-messaging
type: integration
tags: [hermes-agent, telegram, whatsapp, integration, messaging, notification, multi-platform, channel-bridge]
description: "Integration: Hermes Agent multi-platform messaging via Telegram + WhatsApp channels with notification routing, human handoff, and channel bridging"
---

# Integration: Hermes Agent — Telegram + WhatsApp Messaging

**Source**: `sources/hermes-agent/`, `sources/hermes-bus/`

## Overview

Hermes Agent's multi-platform messaging gateway routes conversations across Telegram and WhatsApp through a unified adapter pattern (`BasePlatformAdapter`). Wires both channels into a single Hermes instance for notification routing, human handoff, channel bridging (cross-post), and scheduled dispatch via the plugin system and Hermes Bus IPC.

## Architecture

```
Telegram Bot API / WhatsApp Baileys → Hermes Gateway (TelegramAdapter, WhatsAppAdapter, PlatformRegistry) → Hermes Core (LLM, MCP Server, Bus) → Plugins (evey-telegram-ux, evey-bridge)
```

## Configuration

```bash
# Telegram (create bot via @BotFather)
hermes config set telegram.enabled true
hermes config set telegram.token "123456:ABC-DEF..."
hermes config set telegram.allowed_user_ids [123456789]

# WhatsApp (self-hosted Baileys — no Business API needed)
hermes config set whatsapp.enabled true
hermes config set whatsapp.session_path /data/whatsapp-session

# Or WhatsApp Business API
hermes config set whatsapp.api_token "EAAx..."

# Channel bridge for cross-platform relay
hermes plugin install evey-bridge
hermes config set plugins.bridge.routes = [
  { from: "telegram:!admin-group", to: ["whatsapp:!ops-channel"] },
  { from: "whatsapp:!support", to: ["telegram:!admin-group"] }
]
```

## Deployment (Systemd)

```ini
[Unit]
Description=Hermes Agent (Telegram + WhatsApp)
[Service]
ExecStart=/usr/local/bin/hermes gateway --platforms telegram,whatsapp
Restart=on-failure
```

### Verification

```bash
hermes gateway status
hermes send --platform telegram --chat "@me" --message "Hello"
hermes send --platform whatsapp --chat "5511999999999" --message "Hello"
```

### Human Handoff Flow

1. User messages WhatsApp → LLM agent analysis
2. Agent escalates → bridges to Telegram admin group
3. Admin replies in Telegram → relayed back to WhatsApp user
4. `hermes handoff --to human` pauses LLM inference on thread

## Related

- [[hermes-agent]] — Self-improving personal AI agent core
- [[hermes-bus]] — IPC message transport for plugin events
- [[telegram]] — Telegram Bot API integration
- [[whatsapp]] — WhatsApp messaging integration
