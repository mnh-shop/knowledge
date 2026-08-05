---
name: 1claw-hermes-codegraph-verify
tags: [codegraph-verify, 1claw-hermes, hermes-agent, mcp]
description: "Codegraph Verification: 1claw-hermes"
source: sources/1claw-hermes/
date: 2026-07-12
---

# Codegraph Verification: 1claw-hermes

**Date:** 2026-07-12

## Claim 1: Hermes MCP shroud integration via config patching
- **Wiki says:** The package provides Hermes MCP integration via `patchHermesConfig()`, registering 1Claw under `mcp_servers.oneclaw` with stdio (default) or HTTP transport. Shroud TEE proxy routes LLM calls through a sidecar process.

- **Source evidence:** `README.md` lines 92-97 define `patchHermesConfig()` which "registers 1Claw under `mcp_servers.oneclaw`" with tools `mcp_oneclaw_*`. Lines 122-124 describe the Shroud sidecar pattern: "run the 1Claw Shroud sidecar on your machine, point Hermes at `localhost`, and let the sidecar inject headers and forward to `https://shroud.1claw.xyz`." Source file `src/mcp/hermes-config.ts` implements `patchHermesConfig()` with both stdio and HTTP transport options. Source file `src/shroud/index.ts` (line 11) exports `createShroudClient()` which returns an OpenAI-compatible client pointed at the Shroud TEE proxy. Source file `src/shroud/sidecar.ts` provides the `startSidecarAndWait()` function for programmatic sidecar lifecycle management. Source file `src/mcp/index.ts` (lines 12-23) implements `buildMcpEntry()` constructing JWT Bearer + vault ID header authorization.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Setup automation via bootstrap CLI and `pnpm setup`
- **Wiki says:** The package provides a comprehensive bootstrap and setup automation flow: enrollment, API key injection, Hermes config patching, sidecar installation and startup.

- **Source evidence:** `package.json` lines 15-19 define CLI aliases as npm scripts: `bootstrap`, `bootstrap:enroll`, `bootstrap:complete`, `setup`. `README.md` lines 12-20 document the two-phase bootstrap flow: `pnpm bootstrap enroll` sends email + agent name, then `pnpm bootstrap complete` reads `ONECLAW_AGENT_API_KEY` from `.env`. Lines 129-141 document `pnpm setup --provider google` which in one command reads the API key, patches Hermes YAML config for MCP, patches the model provider to point at the sidecar, downloads and starts the sidecar binary, and waits for `/healthz`. Source file `src/bootstrap.ts` implements `needsBootstrap()`, `bootstrapEnroll()`, and `completeBootstrapFromEnv()`. Source file `src/setup.ts` implements the unified CLI. Source file `src/bootstrap-cli.ts` implements the TTY/non-TTY CLI handler. Source file `src/dotenv-path.ts` implements dotenv resolution with ONECLAW_ENV_FILE, cwd walk, and package fallback.

- **Dotenv resolution order (README:181-186):** (1) CLI flag `--env-path`/`--env-file`; (2) `ONECLAW_ENV_FILE` env var; (3) walk cwd upward for `.env`; (4) fallback `packages/1claw-hermes/.env`. README.md line 73 documents `ONECLAW_ENV_FILE` ("Absolute path to `.env` when it is not next to this package"). README.md line 188 notes the Go `shroud-sidecar` binary does not read `.env` files itself — `pnpm shroud` loads the file and passes env vars to the child, and may auto-append `ONECLAW_AGENT_ID` to older files.

- **Verdict:** ✅ CORRECT
- **Fix needed:** Wiki now documents the resolution order and `ONECLAW_ENV_FILE`

## Claim 3: Subagent identity lifecycle with scoped access
- **Wiki says:** The package supports ephemeral subagent identity provisioning with scoped policy-based access to vault secrets.

- **Source evidence:** `README.md` lines 310-353 document `provisionSubagent()`, `deprovisionSubagent()`, and `SubagentRegistry`. The API accepts a name and `ephemeralReadPolicy()` returning a scoped identity. Source file `src/subagents/index.ts` implements the identity lifecycle with `SubagentRegistry` tracking all live identities and cleanup on `SIGTERM`. Source file `src/subagents/policy.ts` implements `PolicyBuilder` with fluent methods: `allowPath()`, `readOnly()`, `expireAfter()`, `allowChains()`, `capValue()`, and `build()`. Source file `src/client.ts` provides a singleton `@1claw/sdk` wrapper with auto token refresh for subagent-scoped calls. Test file `test/subagents.test.ts` validates provisioning, policy application, and cleanup flows.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: On-chain transaction signing through Intents API with guardrails
- **Wiki says:** The package provides Intents API integration for on-chain transaction signing with client-side guardrail validation.

- **Source evidence:** `README.md` lines 355-368 document `submitIntent()`, `validateIntent()`, and guardrail types. The flow accepts `{ to, value, chain }` intent objects, validates against `agentPolicy`, and submits via the 1Claw Intents API. Source file `src/intents/index.ts` implements `submitIntent()` returning `explorerUrl`. Source file `src/intents/guardrails.ts` implements `validateIntent()` with machine-readable error codes: `CHAIN_NOT_ALLOWED`, `VALUE_EXCEEDS_CAP`, `ADDRESS_NOT_ALLOWED`. Errors are typed as `GuardrailViolationError` in `src/errors.ts`. Test file `test/intents.test.ts` validates guardrail enforcement.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Audit log query helpers with cursor-based streaming
- **Wiki says:** The package provides audit log query helpers with cursor-based streaming for event history.

- **Source evidence:** `README.md` lines 370-378 document `recentEvents(20)` and `streamEvents(new Date("2026-01-01"))`. Source file `src/audit/index.ts` implements both synchronous batch and async streaming interfaces for audit log retrieval. The events return fields including `action`, `path`, and `outcome`. The architecture diagram in `README.md` lines 396-422 lists "Audit log query helpers with cursor-based streaming" under `src/audit/index.ts`.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: CMO talent subsystem — 23 post formats, wedge-artifact campaign, Shroud drafts
- **Wiki says:** The package contains a "CMO talent" subsystem for automated social media content generation and posting to X/Twitter and Telegram, with 23 post formats and a 4-week campaign whose Week 1 is "Build the wedge artifact".

- **Source evidence:**
  - `src/talents/cmo/draft-generator.ts` lines 11-36: `CmoPostFormat` union — 13 gitlawb-style (`newsdrop`, `stats`, `qt`, `qt-bigissue`, `milestone`, `release`, `dogfood`, `poll`, `shoutout`, `rally`, `thread`, `journal-cta`, `ugc-repost`) + 9 1clawai/Bankr-ecosystem (`holder-milestone`, `onchain-stats`, `listing-news`, `reference-demo`, `editorial-coverage`, `ecosystem-partner`, `essay`, `stack-diagram`, `bankr-amplified`) + `auto` = **23 formats**. `qt-bigissue` (line 16) is the "3-paragraph claim → why → product-anchor QT" previously missing from the wiki's list.
  - `draft-generator.ts` lines 147-154: candidate count clamp `if (n < 1 || n > 12)`; default model `claude-sonnet-4-20250514`, `temperature: 0.85`; system prompt built from `persona.md` + `style-notes.md` + `products.md` + `campaign.md` (lines 71-113)
  - `src/talents/cmo/campaign.md` line 88: "### Week 1 (Days 1-7): Build the wedge artifact" — theme "ship the reference agent" (line 90); Weeks 2-4 at lines 106, 124, 139
  - `src/talents/cmo/x-poster.ts`, `snap-poster.ts`, `cli.ts`, `index.ts`, `persona.md` (brand voice), `style-notes.md` (13 gitlawb patterns), `products.md` (product catalog) — full talent tree
  - `package.json` dependency `"twitter-api-v2": "^1.29.0"` confirms X/Twitter integration; build script copies the Markdown briefings to `dist/talents/cmo/`
  - Test files `test/cmo.test.ts`, `test/snap-poster.test.ts`, `test/x-poster.test.ts` validate the subsystem
- **Verdict:** ✅ CORRECT (format count corrected 26 → 23, `qt-bigissue` added, Week 1 theme corrected)
- **Fix needed:** Wiki updated

## Claim 7: Sidecar operations — two-process model, process managers, and troubleshooting
- **Wiki says:** Shroud does not turn on by itself; Hermes and the sidecar are two separate processes (Hermes does not supervise the sidecar); process-manager guidance (systemd user / launchd / tmux / Docker) with `scripts/` templates; `APIConnectionError` diagnosis; `SHROUD_TOKEN` config.

- **Source evidence:**
  - README.md line 3: "**Shroud does not turn on by itself:** you either run the Shroud sidecar in front of Hermes, or call Shroud from TypeScript via `createShroudClient()`"
  - README.md lines 143-149: "Hermes and the sidecar are two different processes" — `pnpm setup` patches `model.base_url: http://127.0.0.1:8080/v1`, but "Hermes does not start or supervise the sidecar"; restart → `APIConnectionError` / connection refused until sidecar restarted
  - README.md lines 151-177: process-manager table (systemd user, launchd, tmux/screen, Docker/compose) with step-by-step Linux (systemd + `loginctl enable-linger`) and macOS (launchd LaunchAgent) setup; health check `curl -s http://127.0.0.1:8080/healthz`
  - README.md lines 238-248: troubleshooting table — `APIConnectionError` to `localhost:8080/v1` = sidecar not running/wrong port/different host; `SHROUD_PROVIDER` under `mcp_servers.oneclaw.env` only configures the MCP subprocess, not Hermes's model HTTP client; Docker note on network namespaces
  - `scripts/shroud-sidecar.service.example` lines 14-31: systemd user unit — `ExecStart=/usr/bin/node dist/shroud/sidecar.js`, `Restart=always`, `RestartSec=5`, `Environment=ONECLAW_DEFAULT_PROVIDER=google`, optional `ONECLAW_ENV_FILE`
  - `scripts/shroud-sidecar.launchd.plist.example` lines 15-43: LaunchAgent `com.1claw.shroud-sidecar` with `RunAtLoad` + `KeepAlive`, `WorkingDirectory`, absolute `node` path, `ONECLAW_ENV_FILE`, stdout/stderr log paths
  - README.md line 79: `SHROUD_TOKEN` — "Bearer for Shroud (`createShroudClient`); not used by the sidecar binary"
- **Verdict:** ✅ CORRECT (new claim — operational content previously absent from wiki)
- **Fix needed:** None

## Related

- [[1claw-hermes]] -- Main wiki entry
- [[1claw-hermes.operations]] -- Companion: sidecar process management, two-process model, dotenv resolution, CMO format catalog
- [[hermes-agent]] -- Hermes Agent upstream
- [[mcp]] -- Model Context Protocol
- [[hermes-workspace]] -- Hermes Workspace

## Cross-project

- [[hermes-agent.codegraph-verify]] -- Hermes Agent verification
- [[hermes-workspace.codegraph-verify]] -- Hermes Workspace verification
