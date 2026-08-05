---
name: openclaw-channels
tags: [agent-gateway, channels, cli, imessage, messaging, openclaw, plugin-sdk, security, telegram, typescript, whatsapp]
description: OpenClaw Channels
source: sources/openclaw/
---

# OpenClaw Channels
**Source:** `sources/openclaw/`

OpenClaw's channel system is a transport-agnostic message adapter layer that connects the agent gateway to external chat platforms. Channels are organized into three distribution tiers — core, bundled official plugins, and external plugins — and are implemented as plugins loaded through the plugin system, with a shared channel runtime in `src/channels/`.

## Channel Tiers

The canonical tier model is documented in `docs/channels/index.md`. Text is supported everywhere; media and reactions vary by channel.

| Tier | Channels | Distribution |
|------|----------|--------------|
| **CORE** | Telegram, iMessage, WebChat | Shipped with the core install; no plugin install required |
| **Official plugin** | ~23 channels, one per package `@openclaw/<id>` | Bundled in `extensions/`, installed via `openclaw plugins install @openclaw/<id>` or on demand during `openclaw onboard` / `openclaw channels add`; Gateway restart required after install |
| **External plugin** | WeChat, Yuanbao, Zalo ClawBot, WeCom | Maintained outside the OpenClaw repo; installed from npm/ClawHub |

Channels can run simultaneously; the Gateway routes per chat. The fastest setup is Telegram (simple bot token, no plugin install). WhatsApp requires QR pairing and stores more state on disk.

## Bundled Official Plugins

The official channel catalog lives in `scripts/lib/official-external-channel-catalog.json` (27 channel entries: 23 official + 4 external). Each entry carries the npm spec, expected integrity hash, channel id, aliases, and docs path used by the installer and onboarding wizard.

Official bundled channel plugins present in `extensions/`:

- **Buzz** — team rooms with threaded replies (`extensions/buzz`)
- **ClickClack** — desktop-centric chat (`extensions/clickclack`)
- **Discord** — Bot API + Gateway; servers, channels, DMs (`extensions/discord`)
- **Feishu** — Feishu/Lark bot via WebSocket (`extensions/feishu`)
- **Google Chat** — API app via HTTP webhook (`extensions/googlechat`)
- **IRC** — classic IRC; channels + DMs with pairing/allowlist controls (`extensions/irc`)
- **LINE** — LINE Messaging API bot (`extensions/line`)
- **Matrix** — Matrix protocol (`extensions/matrix`)
- **Mattermost** — Bot API + WebSocket (`extensions/mattermost`)
- **Microsoft Teams** — Bot Framework (`extensions/msteams`)
- **Nextcloud Talk** — self-hosted chat (`extensions/nextcloud-talk`)
- **Nostr** — decentralized DMs via NIP-04 (`extensions/nostr`)
- **QQ Bot** — private chat, group chat, rich media (`extensions/qqbot`)
- **Raft** — CLI wake bridge for human/agent collaboration (`extensions/raft`)
- **Reef** — guarded, end-to-end-encrypted claw-to-claw messaging between different people's agents (bundled plugin; `extensions/reef`, `docs/channels/reef.md`)
- **Signal** — signal-cli based (`extensions/signal`)
- **Slack** — Bolt SDK workspace apps (`extensions/slack`)
- **SMS** — Twilio-backed SMS through the Gateway webhook (`extensions/sms`)
- **Synology Chat** — Synology NAS chat via outgoing+incoming webhooks (`extensions/synology-chat`)
- **Tlon** — Urbit-based messenger (`extensions/tlon`)
- **Twitch** — Twitch chat via IRC connection (`extensions/twitch`)
- **WhatsApp** — Baileys-based, requires QR pairing (`extensions/whatsapp`)
- **Zalo / Zalo Personal** — Zalo Bot API and personal-account QR login (`extensions/zalo`, `extensions/zalouser`)

Each has a per-channel doc under `docs/channels/` (e.g. `whatsapp.md`, `slack.md`, `matrix.md`, `imessage.md`).

## External Plugins

External channel plugins are maintained outside the OpenClaw repo and installed from npm. The four entries in `scripts/lib/official-external-channel-catalog.json` with `"source": "external"`:

| Channel | Package | Notes |
|---------|---------|-------|
| WeChat | `@tencent-weixin/openclaw-weixin` | Tencent iLink bot via QR login; private chats only (`docs/channels/wechat.md`) |
| Yuanbao | `openclaw-plugin-yuanbao` | Tencent Yuanbao bot (`docs/channels/yuanbao.md`) |
| Zalo ClawBot | `@zalo-platforms/openclaw-zaloclawbot` | Personal Zalo assistant via QR login; owner-bound (`docs/channels/zaloclawbot.md`) |
| WeCom | `@wecom/wecom-openclaw-plugin` | Enterprise WeChat / WeCom channel |

These install on demand; the Gateway loads the external ClawHub/npm plugin only when the channel is actually active (WhatsApp is install-on-demand too — onboarding can show the setup flow before the package is installed).

## Voice and Meeting Extensions

Non-messaging channel-family extensions bundled in `extensions/`:

- **voice-call** — telephony via Plivo, Telnyx, or Twilio (`extensions/voice-call`, `docs/plugins/voice-call.md`)
- **google-meet** — Google Meet sessions (`extensions/google-meet`)
- **teams-meetings** — Microsoft Teams meetings (`extensions/teams-meetings`)
- **zoom-meetings** — Zoom meetings (`extensions/zoom-meetings`)

These are covered together in `docs/plugins/meeting-plugins.md`.

## Channel Runtime Architecture

The shared channel runtime lives in `src/channels/` and is consumed by the plugin SDK's channel helpers (`src/plugin-sdk/channel-*.ts`). Key modules:

- **Registry** — `registry.ts`, `registry-lookup.ts`, `registry-normalize.ts`, plus `channel-catalog-registry.ts` and `bundled-channel-catalog-read.ts` under `src/plugins/`
- **Config** — `channel-config.ts`, `config-presence.ts`, per-channel config schemas
- **Session** — `session.ts`, `session-envelope.ts`, `session-meta.ts`, `session.types.ts`, `conversation-binding-*.ts`
- **Targets** — `targets.ts`, `chat-target-prefixes.ts`, `native-command-session-targets.ts`
- **Thread bindings** — `thread-binding-id.ts`, `thread-bindings-messages.ts`, `thread-bindings-policy.ts`, `thread-addressing.ts`, `threading-tool-context-internal.ts`
- **Allowlists** — `allowlists/`, `allow-from.ts`, `allowlist-match.ts`, `group-access.ts`, `command-gating.ts`
- **Pairing** — `plugins/pairing.ts`, `plugins/pairing-adapters.ts`, `plugins/pairing-message.ts`, plus per-channel pairing adapters; DM pairing flows documented in `docs/channels/pairing.md`
- **Direct DM** — `direct-dm.ts`, `direct-dm-access.ts`, `direct-dm-guard-policy.ts`
- **DM access** — `plugins/dm-access.ts`, `plugins/exposure.ts`
- **Status reactions** — `status-reactions.ts`, `ack-reactions.ts`, `status/` (per-channel status)
- **Typing** — `typing.ts`, `typing-lifecycle.ts`, `typing-start-guard.ts`
- **Streaming** — `streaming.ts`, `draft-stream-*.ts`, `draft-preview-finalizer.ts`, `draft-streaming-chunking.ts`, `progress-draft-*.ts`
- **Inbound debounce** — `inbound-debounce-policy.ts`, `inbound-event/`
- **Run state machine** — `run-state-machine.ts`, `session-envelope.ts`
- **Bundled channel runtime** — `src/channels/plugins/` also contains `setup-wizard.ts`, `setup-wizard-binary.ts`, `setup-registry.ts`, `exec-approval-local.ts`, `bootstrap-registry.ts`, `configured-binding-*.ts`, `account-action-gate.ts`

Gateway-level channel lifecycle is managed by `ChannelManager` in `src/gateway/server-channels.ts` (`startChannels()`, `startChannel(id, accountId)`, `stopChannel()`, `getRuntimeSnapshot()`). Channel connectivity through restricted networks uses SSH tunnel proxies established during the startup proxy-bootstrap phase.

## Installation and Pairing

- Official channels: `openclaw plugins install @openclaw/<id>`, or add during `openclaw onboard` / `openclaw channels add`.
- After install, a Gateway restart is required for the channel to load.
- **DM pairing** is enforced for safety: pairing/approval flows gate who can message the agent; see `docs/channels/pairing.md`, `src/channels/plugins/pairing*.ts` and the SDK helpers `src/plugin-sdk/channel-pairing.ts`.
- Multi-user and group policies are separate surfaces: `docs/channels/groups.md`, `docs/channels/access-groups.md`, `docs/channels/broadcast-groups.md`, `docs/channels/group-messages.md`, `docs/channels/channel-routing.md`.
- Bot loop protection (`docs/channels/bot-loop-protection.md`) prevents bot pairs from replying to each other indefinitely; ambient room events (`docs/channels/ambient-room-events.md`) turn unmentioned room chatter into quiet context.

## Channel-Specific Quirks

- **WhatsApp** — requires QR pairing via Baileys and stores significant state on disk (`docs/channels/whatsapp.md`).
- **iMessage** — native macOS integration via the `imsg` bridge on a signed-in Mac, or an SSH wrapper when the Gateway runs elsewhere; supports private API actions for replies, tapbacks, effects, attachments, and group management (`docs/channels/imessage.md`; BlueBubbles variant in `imessage-from-bluebubbles.md`).
- **Matrix** — crypto and push-rule configuration; see `matrix.md`, `matrix-migration.md`, `matrix-presentation.md`, `matrix-push-rules.md`.
- **Telegram** — grammY-based Bot API; markdown image syntax in replies is converted to media replies on the final outbound path when possible; supports groups.
- **Slack** — multi-person DMs route as group chats, so group policy and mention behavior apply to MPIMs.
- **SMS** — Twilio-backed through the Gateway webhook.

## Key Source Files

| File | Purpose |
|------|---------|
| `docs/channels/index.md` | Canonical channel tier model and full supported-channel list |
| `scripts/lib/official-external-channel-catalog.json` | Official + external channel install catalog (27 entries) |
| `src/channels/registry.ts` | Channel registry |
| `src/channels/session.ts`, `session-envelope.ts` | Per-channel session management |
| `src/channels/targets.ts` | Channel target resolution |
| `src/channels/streaming.ts` | Streaming config normalization (preview modes, chunking) |
| `src/channels/run-state-machine.ts` | Channel run state machine |
| `src/channels/plugins/pairing.ts` | DM pairing flows |
| `src/channels/plugins/setup-wizard.ts` | Channel setup wizard |
| `src/channels/plugins/exec-approval-local.ts` | Local exec approval handling |
| `src/gateway/server-channels.ts` | ChannelManager lifecycle |
| `src/plugin-sdk/channel-*.ts` | Plugin SDK channel contracts (entry, pairing, setup, streaming, targets, message, lifecycle) |
| `extensions/{whatsapp,slack,discord,telegram,...}/` | Bundled channel plugin implementations |

## Related

- [[domains/architecture/openclaw-architecture.md]] — Gateway and channel architecture
- [[domains/plugins/openclaw-plugins.md]] — Plugin system that hosts channel adapters
- [[wiki/openclaw.md]] — Wiki entry
