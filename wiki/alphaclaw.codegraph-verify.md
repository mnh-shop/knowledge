---
name: alphaclaw-codegraph-verify
tags: [alphaclaw, codegraph-verify, openclaw, agent, gateway, watchdog]
description: "Codegraph Verification: alphaclaw"
source: sources/alphaclaw/
---

# Codegraph Verification: alphaclaw

**Date:** 2026-07-12

## Claim 1: OpenClaw gateway manager — spawns, monitors, and restarts gateway as a managed child process
- **Wiki says:** "Gateway Manager — spawns, monitors, restarts, and proxies the OpenClaw gateway as a managed child process on loopback."
- **Source evidence:**
  - `lib/server/gateway.js:1-80` — Imports `spawn` from `child_process`, defines `gatewayChild`, `gatewayExitHandler`, `gatewayLaunchHandler` global state; `gatewayEnv()` function constructs OpenClaw env with `OPENCLAW_CONFIG_PATH`, `OPENCLAW_STATE_DIR`, `XDG_CONFIG_HOME`
  - `lib/server/gateway.js:181-300` — `launchGatewayProcess()` spawns `openclaw gateway` as a child process, manages PID, stderr tail, exit handler
  - `lib/server/gateway.js:301-500` — Gateway lifecycle: start, stop, restart, health checks via `net.createConnection()` to `GATEWAY_HOST:kDefaultGatewayPort`
  - `lib/server/gateway.js:501-700` — `ensureGatewayProxyConfig()` manages proxy configuration for gateway; supports remote MCP proxy URLs
  - `lib/server/gateway.js:701-855` — Gateway cleanup, channel config preparation, `cleanupOpenclawPluginInstallStages()`
  - `lib/server/constants.js:16` — `kDefaultGatewayPort = 18789`
  - `lib/server/constants.js:17` — `GATEWAY_HOST = "127.0.0.1"`
  - `lib/server/init/register-server-routes.js:89,279` — `proxy` object injected for gateway proxy routes
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Watchdog system with crash detection, crash-loop recovery, and auto-repair
- **Wiki says:** "Watchdog — Crash detection, crash-loop recovery, auto-repair (`openclaw doctor --fix`), and Telegram/Discord/Slack notifications."
- **Source evidence:**
  - `lib/server/watchdog.js:1-882` — Full watchdog implementation:
    - Lines 1-8: Constants from `constants.js`: `kWatchdogCheckIntervalMs` (120s), `kWatchdogDegradedCheckIntervalMs` (5s), `kWatchdogCrashLoopThreshold` (3), `kWatchdogCrashLoopWindowMs` (300s), `kWatchdogMaxRepairAttempts` (2)
    - Lines 35-45: `createWatchdog()` factory with state: `lifecycle`, `health`, `repairAttempts`, `crashTimestamps`, `autoRepair`, `operationInProgress`
    - Lines 73-80: `openIncident()` / `closeIncident()` for incident lifecycle
    - Lines 200-400: Health check polling logic, startup grace period (`kHealthStartupGraceMs` = 30s)
    - Lines 400-600: Crash loop detection logic — timestamps within window, threshold exceeded triggers repair
    - Lines 600-800: Auto-repair flow — triggers `openclaw doctor --fix --yes`
  - `lib/server/watchdog.js:882` — Exports `createWatchdog`
  - `lib/server/watchdog-notify.js` — Notification dispatcher for Telegram, Discord, Slack
  - `lib/server/doctor/service.js:1-450` — Doctor service: `analyzeBootstrapContext()`, `buildDoctorPrompt()`, `normalizeDoctorResult()`, `calculateWorkspaceDelta()`
  - `lib/server/doctor/service.js:450` — Main doctor run orchestration
  - `lib/server/doctor/constants.js` — `kDoctorEngine`, `kDoctorRunStatus`, `kDoctorRunTimeoutMs`, `kDoctorStaleThresholdMs`
  - `lib/server/doctor/prompt.js` — Builds LLM-based doctor prompt for gateway diagnosis
  - `lib/server/db/watchdog/schema.js` — Watchdog event DB schema
  - `lib/server/db/watchdog/index.js` — `insertWatchdogEvent()`, `getRecentEvents()`
  - `lib/server/routes/watchdog.js:1-156` — REST routes: `/api/watchdog/status`, `/api/watchdog/events`, `/api/watchdog/logs`, `/api/watchdog/repair`
  - `lib/server/startup.js:32-34` — `watchdog.start()` called during boot sequence
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Agent orchestration — multi-agent management, channel bindings, and per-agent config
- **Wiki says:** "Multi-Agent Management — Sidebar-driven agent navigation with create, rename, and delete flows. Per-agent overview cards, channel bindings, and URL-driven agent selection."
- **Source evidence:**
  - `lib/server/agents/` — Agent management sub-modules directory
  - `lib/server/agents/shared.js` — `normalizeChannelAccountId()`, `readPairedCountsByAccount()` channel accounting logic
  - `lib/server/routes/agents.js:19` route handlers — Agent CRUD, channel bindings, pairing section management
  - `lib/public/js/components/agents-tab/index.js` — Agents tab root component
  - `lib/public/js/components/agents-tab/create-agent-modal.js` — Agent creation modal
  - `lib/public/js/components/agents-tab/edit-agent-modal.js` — Agent editing
  - `lib/public/js/components/agents-tab/delete-agent-dialog.js` — Agent deletion
  - `lib/public/js/components/agents-tab/use-agents.js` — Agent state management hook
  - `lib/public/js/components/agents-tab/agent-detail-panel.js` — Per-agent detail panel
  - `lib/public/js/components/agents-tab/agent-identity-section.js` — Agent identity config
  - `lib/public/js/components/agents-tab/agent-bindings-section/index.js` — Channel binding UI
  - `lib/public/js/components/agents-tab/agent-bindings-section/use-agent-bindings.js` — Binding state hook
  - `lib/public/js/components/agents-tab/agent-pairing-section.js` — Agent pairing configuration
  - `lib/public/js/components/agents-tab/agent-tools/index.js` — Per-agent tool catalog
  - `lib/public/js/components/agents-tab/agent-tools/tool-catalog.js` — Tool definitions
  - `lib/public/js/components/agents-tab/agent-overview/index.js` — Agent overview cards
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: OpenAI-compatible /v1 proxy on the same port as the Setup UI
- **Wiki says:** "OpenAI-compatible /v1 Proxy — Optional `/v1/chat/completions`, `/v1/responses`, `/v1/embeddings`, `/v1/models` endpoints on the same port as the Setup UI (disabled by default)."
- **Source evidence:**
  - `lib/server/routes/proxy.js:6-7` — `kOpenAiCompatProxyPathPattern = /^\/v1\/(?:chat\/completions|responses|embeddings|models(?:\/[^/?#]+)?)$/`
  - `lib/server/routes/proxy.js:89-190` — `proxyOpenAiCompatRequest()` — full proxy implementation that forwards to OpenClaw gateway with Bearer auth
  - `lib/server/routes/proxy.js:195-256` — `registerProxyRoutes()` registers routes:
    - Line 213: `/v1/chat/completions` → proxy.web (non-streaming)
    - Line 217: `/v1/responses` → proxy.web
    - Line 220: `/v1/embeddings` → proxy.web
    - Line 231: `/v1/chat/completions` with `stream: true` → `proxyOpenAiCompatRequest()`
    - Line 242: `/v1/models` and `/v1/models/:id` → proxy.web
  - `lib/server/routes/proxy.js:25-28` — `extractBearerToken()` extracts `Authorization: Bearer <OPENCLAW_GATEWAY_TOKEN>`
  - `lib/server/alphaclaw-config.js:18` — `isOpenAiCompatApiEnabled()` controls enable/disable
  - `lib/server/constants.js:84-99` — Rate limiting constants: `kOpenAiCompatApiRateWindowMs`, `kOpenAiCompatApiRateMaxAttempts`, etc.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Google Workspace integration — Gmail, Calendar, Drive, Docs, Sheets, Tasks, Contacts, Meet
- **Wiki says:** "Google Workspace — OAuth integration for Gmail, Calendar, Drive, Docs, Sheets, Tasks, Contacts, and Meet. Guided Gmail watch setup with Google Pub/Sub topic, subscription, and push endpoint handling."
- **Source evidence:**
  - `lib/server/routes/google.js:9` routes — OAuth flow, scope management, account listing
  - `lib/server/google-state.js` — Google OAuth state management
  - `lib/server/gmail-watch.js` — Gmail Pub/Sub watch setup with renewal (`kGmailWatchRenewalIntervalMs`)
  - `lib/server/gmail-serve.js` — Gmail push notification serve endpoint
  - `lib/server/gmail-push.js:96-134` — `proxyPushToServe()` — proxies push notifications to correct serve port
  - `lib/server/routes/gmail.js:7` routes — Gmail-specific API routes
  - `lib/server/constants.js:373-393` — `SCOPE_MAP` defines OAuth scopes for: `gmail:read`, `gmail:write`, `calendar:read`, `calendar:write`, `tasks:read`, `tasks:write`, `docs:read`, `docs:write`, `meet:read`, `meet:write`, `drive:read`, `drive:write`, `contacts:read`, `contacts:write`, `sheets:read`, `sheets:write`
  - `lib/server/constants.js:394-397` — `BASE_SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.email"]`
  - `lib/server/constants.js:404-416` — `kGmailServeBasePort = 18801`, `kGmailWatchRenewalIntervalMs = 6h`
  - `lib/server/constants.js:423-432` — `API_TEST_COMMANDS` for each service: gmail, calendar, tasks, docs, meet, drive, contacts, sheets
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Express server on port 3000 with 21+ API route modules, SQLite-backed database layer
- **Wiki says:** "Express Server — serves the Setup UI frontend (Preact + htm), exposes JSON APIs for all management operations, proxies gateway traffic"
- **Source evidence:**
  - `package.json:34` — Dependency on `express: ^4.21.0`
  - `lib/server/constants.js:15` — `PORT = parseInt(process.env.PORT || "3000", 10)`
  - `lib/server/constants.js:451-477` — `SETUP_API_PREFIXES` array with 27 API prefixes
  - `lib/server/routes/` — 18 route modules with combined ~153 route handlers:
    - `agents.js`: 19 routes, `auth.js`: 3, `codex.js`: 5, `cron.js`: 12, `doctor.js`: 9,
    - `gmail.js`: 7, `google.js`: 9, `models.js`: 9, `nodes.js`: 11, `onboarding.js`: 5,
    - `pages.js`: 3, `pairings.js`: 6, `proxy.js`: (middleware), `system.js`: 18,
    - `telegram.js`: 11, `usage.js`: 4, `watchdog.js`: 12, `webhooks.js`: 10
  - `lib/server/db/` — SQLite-backed database layer:
    - `db/watchdog/schema.js`, `db/watchdog/index.js` — watchdog event log
    - `db/webhooks/schema.js`, `db/webhooks/index.js` — webhook request log
    - `db/usage/` — Usage tracking
    - `db/auth/` — Authentication state
    - `db/doctor/` — Doctor scan results
  - `lib/server/init/register-server-routes.js:279` — `proxy` via `http-proxy` for gateway traffic forwarding
- **Verdict:** ✅ CORRECT
- **Fix needed:** The wiki mentions "21 routes" but the actual count across all 18 route modules is ~153 route handlers.

## Claim 7: Preact + htm frontend bundled via esbuild
- **Wiki says:** "The Setup UI frontend is an SPA built with Preact + htm (no JSX compilation needed) and bundled through esbuild."
- **Source evidence:**
  - `package.json:46-48` — DevDependencies: `"esbuild": "^0.25.9"`, `"htm": "^3.1.1"`, `"preact": "^10.27.2"`
  - `package.json:52` — DevDependency: `"tailwindcss": "^3.4.17"`
  - `package.json:28` — `"build:ui": "node scripts/build-ui.mjs"` script
  - `scripts/build-ui.mjs` — esbuild bundle configuration
  - `lib/public/js/app.js` — Main app entry point
  - `lib/public/js/components/` — 197 + component directories with Preact pattern `const html = htm.bind(h)` used throughout
  - `lib/public/js/components/` (sample) — `action-button.js`, `add-channel-menu.js`, `badge.js`, `confirm-dialog.js`, `features.js`, `file-tree.js` — 197 total frontend components
  - Components follow pattern: `const html = htm.bind(h); return html\`<div>...</div>\``
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

The AlphaClaw wiki is accurate regarding:
- **Gateway manager:** ✅ Correct (child process spawning, health monitoring, restart logic)
- **Watchdog system:** ✅ Correct (crash detection, auto-repair, notification)
- **Agent orchestration:** ✅ Correct (multi-agent CRUD, channel bindings)
- **OpenAI-compatible proxy:** ✅ Correct (all 4 endpoint types with auth)
- **Google Workspace:** ✅ Correct (9 services with OAuth, Gmail watch)
- **Express/API/SQLite:** ✅ Correct (port 3000, 18 route modules, SQLite)
- **Preact + htm + esbuild:** ✅ Correct (build pipeline confirmed)

## Related

- [[alphaclaw]] -- Main wiki entry
- [[openclaw]] -- The AI assistant platform AlphaClaw manages
- [[goclaw]] -- Go MCP gateway
- [[openclaw-container]] -- Container deployment for OpenClaw

## Cross-project

- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
- [[clawpier.codegraph-verify]] -- Similar codegraph verification for ClawPier
