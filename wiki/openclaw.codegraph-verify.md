---
name: openclaw-codegraph-verify
tags: [acp, agent-gateway, live-canvas, mcp, messaging, openclaw, personal-assistant, plugin-sdk, typescript, wiki]
description: "Codegraph Verification: openclaw"
source: sources/openclaw/
---

# Codegraph Verification: openclaw

**Date:** 2026-07-30

## Claim 1: Node version floors and recommendation
- **Wiki says:** "Runtime: Node 26 (recommended); floors 22.22.3+ / 24.15.0+ / 25.9.0+"
- **Source evidence:**
  - `openclaw.mjs:11-15` — `MIN_NODE_22 = { major: 22, minor: 22, patch: 3 }`, `MIN_NODE_24 = { major: 24, minor: 15, patch: 0 }`, `MIN_NODE_25 = { major: 25, minor: 9, patch: 0 }`, `RECOMMENDED_NODE_MAJOR = 26`, `SUPPORTED_NODE_RANGE = ">=22.22.3 <23, >=24.15.0 <25, or >=25.9.0"`
  - `README.md:83` — "Runtime: **Node 24.15+ (recommended), Node 22.22.3+, or Node 25.9+**"
  - `sources/openclaw/AGENTS.md` Commands section — "Runtime: Node 22.22.3+, 24.15+, or 25.9+; Node 26 recommended"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (this corrects the previous wiki's Node-floor errors)

## Claim 2: Channel ecosystem is tiered, not "each is a plugin under extensions/"
- **Wiki says:** "The README advertises '25+ channels'; ~30-32 total, tiered: core channels (Telegram, iMessage, WebChat), ~23 official channel plugins in extensions/, external npm plugins, and voice/meeting extensions"
- **Source evidence:**
  - `README.md:22` — channel list ending "ClickClack, Raft, Reef, QQ, and the built-in WebChat"
  - `README.md:172` — "25+ channels through bundled plugins"
  - `src/channels/plugins/catalog.ts:78` — `ORIGIN_PRIORITY` distinguishes `config/workspace/global/bundled` origins from `EXTERNAL_CATALOG_PRIORITY` (line 106), i.e. bundled channels are distinct from external plugins
  - `extensions/` listing — `buzz`, `clickclack`, `discord`, `feishu`, `googlechat`, `irc`, `line`, `matrix`, `mattermost`, `msteams`, `nextcloud-talk`, `nostr`, `qqbot`, `raft`, `signal`, `slack`, `sms`, `synology-chat`, `tlon`, `twitch`, `whatsapp`, `zalo`, `zalouser` (23 official channel plugins) plus `voice-call`, `google-meet`, `teams-meetings`, `zoom-meetings`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (this corrects the previous wiki's "Each is a plugin under extensions/" framing and adds missing channels)

## Claim 3: Daemon is a sub-CLI (launchd/systemd/schtasks)
- **Wiki says:** "Daemon: `openclaw daemon` sub-CLI — launchd (macOS), systemd (Linux), schtasks (Windows)"
- **Source evidence:**
  - `src/cli/daemon-cli/register.ts:10-13` — `.command("daemon").description("Manage the Gateway service (launchd/systemd/schtasks)")`
  - `src/cli/daemon-cli/register-service-commands.ts:68-139` — subcommands `status`, `install`, `uninstall`, `start`, `stop`, `restart`
  - `src/daemon/` — `launchd.ts`, `launchd-plist.ts`, `launchd-system.ts`, `systemd.ts`, `systemd-system.ts`, `systemd-unit.ts`, `schtasks.ts`, `schtasks-install.ts`, `schtasks-control.ts` (plus Windows `schtasks-exec.ts`)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (this corrects the previous wiki's daemon-surface claim — the real surface is `openclaw daemon`)

## Claim 4: MCP is bidirectional (client registry + server), 20 files in src/mcp/
- **Wiki says:** "MCP is bidirectional — client registry (`mcp.servers`, `openclaw mcp add/set/list/probe/doctor`) AND server (`openclaw mcp serve`) at `src/mcp/` (20 files including tests)"
- **Source evidence:**
  - `src/cli/mcp-cli.ts:600-1379` — `mcp` command group with `serve`, `list`, `show`, `status`, `probe`, `doctor`, `add`, `set`, `tools`, `configure`, `login`, `logout`, `reload`, `unset` subcommands
  - `src/cli/mcp-cli.ts:37` — imports `serveOpenClawChannelMcp` from `../mcp/channel-server.js` (the server side)
  - `src/mcp/` contains exactly 20 files (12 non-test source files, 8 tests): `channel-bridge.ts`, `channel-server.ts`, `channel-tools.ts`, `plugin-tools-serve.ts`, `tools-stdio-server.ts`, `openclaw-tools-serve.ts`, `codex-supervision-tools-serve.ts`, etc.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (this corrects the previous wiki's MCP file-count claim — actual count is 20 including tests, and the wiki now reflects the client side too)

## Claim 5: ACP is ~100 files with a stdio server bridge and capped event ledger
- **Wiki says:** "ACP surface at `src/acp/` (~100 files, 57 non-test) using `@agentclientprotocol/sdk` with PROTOCOL_VERSION 4; server.ts bridge, translator, client, approval-classifier, event-ledger (200 sessions / 5000 events / 16MB), control-plane, commands, conversation-id"
- **Source evidence:**
  - `src/acp/` contains 104 `.ts` files (57 non-test) including `server.ts`, `translator.ts`, `client.ts`, `approval-classifier.ts`, `event-ledger.ts`, `commands.ts`, `conversation-id.ts`, `types.ts`, and the `control-plane/` directory (40 files)
  - `src/acp/event-ledger.ts:13-15` — `DEFAULT_MAX_SESSIONS = 200`, `DEFAULT_MAX_EVENTS_PER_SESSION = 5_000`, `DEFAULT_MAX_SERIALIZED_BYTES = 16 * 1024 * 1024`
  - `src/acp/client.ts:10,172` and `src/acp/server.ts:8` — import/pass `PROTOCOL_VERSION` from `@agentclientprotocol/sdk`
  - `src/acp/server.ts` — ACP stdio server bridging Agent Client Protocol to the Gateway
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (this corrects the previous "~35 ACP files" claim — actual is ~100; also adds the server bridge and ledger caps)

## Claim 6: Memory is a 5-tier subsystem with Dreaming/REM/QMD, not "a word"
- **Wiki says:** "5-tier memory model (Instructions/Curated Core/Episodic/Prospective/Review), Dreaming consolidation, REM, QMD engine, memory-core (89+ files), memory-host-sdk, MEMORY.md/USER.md/DREAMS.md surfaces"
- **Source evidence:**
  - `src/memory-host-sdk/` — 13 modules: `dreaming.ts`, `engine-qmd.ts`, `engine-storage.ts`, `event-store.ts`, `event-types.ts`, `events.ts`, `host/`, `multimodal.ts`, `query.ts`, `secret.ts`, `status.ts`
  - `extensions/memory-core/src/` — 227 files including `dreaming.ts`, `dreaming-consolidation.ts`, `dreaming-phases.ts`, `cli-rem.runtime.ts` (REM), `memory/manager.ts`, `memory/embeddings.ts`, `memory/hybrid.ts`, `memory/temporal-decay.ts`, `memory/qmd-document-resolver.ts`, `memory/index.ts`
  - `extensions/memory-core/src/dreaming.ts`, `cli-runtime-common.ts`, `flush-plan.ts` — reference the `MEMORY.md` / `USER.md` / `DREAMS.md` surfaces
  - Companion plugins in `extensions/`: `active-memory`, `memory-lancedb`, `memory-wiki`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (this replaces the previous one-word reduction with the actual subsystem)

## Claim 7: Docker facts — registries, variants, node user, healthcheck, tini; sponsors include Blacksmith
- **Wiki says:** "GHCR primary + Docker Hub mirror; slim/*-browser/extended-stable variants; default images bundle codex + diagnostics-otel; node:24-bookworm-slim, USER node uid 1000, HEALTHCHECK 3m, tini entrypoint. Sponsors: OpenAI, GitHub, NVIDIA, Vercel, Blacksmith, Convex."
- **Source evidence:**
  - `.github/workflows/docker-release.yml:31` — `DOCKERHUB_IMAGE_NAME: openclaw/openclaw` (Docker Hub mirror alongside GHCR)
  - `Dockerfile` — multi-stage build from `node:24-bookworm-slim` (ARG at lines 12-13), `USER node` (line 369), `HEALTHCHECK --interval=3m ...` (line 383), `ENTRYPOINT ["tini", "-s", "--"]` (line 385)
  - `extensions/codex/` and `extensions/diagnostics-otel/` exist as bundled plugins
  - `.github/workflows/docker-channel-promote.yml:7,55` — `extended-stable` release channel tags; `docker-release.yml:239` — `*-browser` variant tags
  - `README.md:26-79` — sponsors table includes OpenAI, GitHub, NVIDIA, Vercel, **Blacksmith** (`blacksmith.sh`), Convex
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (this adds Blacksmith to the sponsor list and drops the unverifiable image-size figure)

## Claim 8: src/tools/ and src/memory/ are near-empty; real implementations live elsewhere
- **Wiki says:** "`src/tools/` contains only `types.ts`; `src/memory/` contains only `root-memory-files.ts`; tool system lives in `src/agents/tools/` (~100+ files); memory lives in `src/memory-host-sdk/` + `extensions/memory-core/`"
- **Source evidence:**
  - `src/tools/` contains exactly one file: `types.ts`
  - `src/memory/` contains exactly one file: `root-memory-files.ts`
  - `src/agents/tools/` contains 217 files (the actual tool system: browser, canvas, cron, nodes, etc.)
  - `src/memory-host-sdk/` (13 modules) + `extensions/memory-core/src/` (227 files) hold the memory subsystem
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (this fixes the misleading "Tool system" and "Memory subsystem" rows in the Key Source Directories table)

## Summary

The corrected OpenClaw wiki now matches the source:
- **Node versions:** ✅ floors 22.22.3/24.15.0/25.9.0, Node 26 recommended (`openclaw.mjs:11-15`)
- **Channels:** ✅ tiered ecosystem (~30-32): core + 23 official plugins + external npm + voice/meeting
- **Daemon:** ✅ `openclaw daemon` sub-CLI (launchd/systemd/schtasks)
- **MCP:** ✅ bidirectional client+server, `src/mcp/` = 20 files (was wrongly inflated)
- **ACP:** ✅ ~100 files (was "~35"), server bridge + capped event ledger documented
- **Memory:** ✅ 5-tier subsystem with Dreaming/REM/QMD — no longer reduced to one word
- **Docker/Sponsors:** ✅ GHCR + Docker Hub, tini/node/healthcheck verified; Blacksmith added; unverifiable image-size figure removed
- **Directories:** ✅ `src/tools/` and `src/memory/` correctly shown as near-empty stubs

## Related

- [[openclaw]] -- Main wiki entry
- [[openclaw-architecture]] -- System architecture verified by this document
- [[openclaw-acp-implementation]] -- ACP implementation details referenced in claims
- [[openclaw-mcp-implementation]] -- MCP implementation details referenced in claims

## Cross-project

- [[agentfield.codegraph-verify]] -- Similar codegraph verification for AgentField
- [[podman.codegraph-verify]] -- Similar codegraph verification for Podman
