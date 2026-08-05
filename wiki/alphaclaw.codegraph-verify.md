---
name: alphaclaw-codegraph-verify
tags: [alphaclaw, codegraph-verify, openclaw, agent, gateway, watchdog]
description: "Codegraph Verification: alphaclaw"
source: sources/alphaclaw/
---

# Codegraph Verification: alphaclaw

**Date:** 2026-07-30

## Claim 1: Node runtime floor — `engines` gate requires 22.22.3+ / 24.15.0+ / 25.9.0
- **Wiki says:** "Stack — Node.js 22.22.3+ (22.x), 24.15.0+ (24.x), or 25.9.0+ (25.x) per `engines` gate"
- **Source evidence:**
  - `package.json:53-54` — `"engines": { "node": ">=22.22.3 <23 || >=24.15.0 <25 || >=25.9.0" }`
  - `README.md:222` — "Requirements: Node.js ≥ 22.22.3 on Node 22, ≥ 24.15.0 on Node 24, or ≥ 25.9.0"
  - `bin/alphaclaw.js:141-148` — `start` command calls `assertSupportedNodeVersion()` before boot; exits 1 on unsupported runtime
- **Verdict:** ✅ CORRECT — corrects the previously wrong Node floor claim
- **Fix needed:** None

## Claim 2: Route surface — 19 route modules, ~154 route handlers, 25 setup API prefixes
- **Wiki says:** "route modules (19 modules, ~154 handlers)" and "SETUP_API_PREFIXES … enumerates 25 protected prefixes"
- **Source evidence:**
  - `lib/server/routes/` contains 18 `.js` modules plus the `browse/` directory (19 modules total)
  - Handler counts per module (matched `app.<verb>(...)` registrations): `agents.js` 19, `system.js` 18, `watchdog.js` 12, `cron.js` 12, `telegram.js` 11, `nodes.js` 11, `webhooks.js` 10, `models.js` 9, `google.js` 9, `doctor.js` 9, `gmail.js` 7, `pairings.js` 6, `onboarding.js` 6, `codex.js` 5, `usage.js` 4, `pages.js` 3, `auth.js` 3 (login/status/logout; the 3 `app.use` at `auth.js:152-154` are auth middleware), `proxy.js` 0 (middleware only) = **154 handlers**; `browse/index.js` adds 13 more
  - `lib/server/constants.js:469-490` — `SETUP_API_PREFIXES` array with 25 prefixes (status, pairings, google, codex, models, browse, chat, gateway, restart-status, onboard, env, auth, openclaw, devices, sync-cron, telegram, webhooks, gmail, watchdog, usage, cron, agents, channels, operations, nodes)
- **Verdict:** ✅ CORRECT — corrects the previously wrong route-count claim
- **Fix needed:** None

## Claim 3: Gateway Manager — spawns/monitors/restarts the OpenClaw gateway child process
- **Wiki says:** "Gateway Manager — spawns OpenClaw as a managed child process bound to `127.0.0.1:18789` (`spawn("openclaw", ["gateway", "run"])`)"
- **Source evidence:**
  - `lib/server/gateway.js:2` — `const { spawn, execSync } = require("child_process")`
  - `lib/server/gateway.js:352` — `const child = spawn("openclaw", ["gateway", "run"], ...)`
  - `lib/server/gateway.js:255,269` — `execSync("openclaw gateway <cmd>")` / `execSync("openclaw gateway restart")` for lifecycle ops
  - `lib/server/constants.js:16` — `kDefaultGatewayPort = 18789`; `lib/server/constants.js:17` — `GATEWAY_HOST = "127.0.0.1"`
  - `lib/server/gateway.js:501-700` — `ensureGatewayProxyConfig()` manages proxy config including remote MCP proxy URLs
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: OpenAI-compatible /v1 proxy with gateway-token auth and security boundary
- **Wiki says:** "Optional `/v1/chat/completions`, `/v1/responses`, `/v1/embeddings`, `/v1/models` endpoints on the same port as the Setup UI (disabled by default)"
- **Source evidence:**
  - `lib/server/routes/proxy.js:6` — `kOpenAiCompatProxyPathPattern = /^\/v1\/(?:chat\/completions|responses|embeddings|models(?:\/[^/?#]+)?)$/`
  - `lib/server/routes/proxy.js:193` — `registerProxyRoutes()` registers the four endpoint groups; `proxy.js:227-228` — when disabled/missing, `/v1` returns 404
  - `lib/server/alphaclaw-config.js:63` — `isOpenAiCompatApiEnabled()` gates enablement (persisted in `alphaclaw.json`)
  - `README.md:187-195` — Bearer `<OPENCLAW_GATEWAY_TOKEN>` required, failed attempts rate-limited, setup-UI cookie stripped, hop-by-hop headers dropped, 50 MB body limit; security boundary: a valid token is full operator access
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Codex OAuth — built-in PKCE flow for OpenAI Codex CLI model access
- **Wiki says:** "Codex OAuth: Built-in PKCE flow for OpenAI Codex CLI model access — `/auth/codex/start` → OpenAI authorize → token exchange → server-side profile, managed via `/api/codex/*` endpoints"
- **Source evidence:**
  - `README.md:46` — "Codex OAuth: Built-in PKCE flow for OpenAI Codex CLI model access"
  - `lib/server/constants.js:31-38` — `CODEX_PROFILE_ID = "openai:codex-cli"`, `CODEX_OAUTH_CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"`, authorize/token URLs at `auth.openai.com`, redirect `http://localhost:1455/auth/callback`, scope `openid profile email offline_access`, `kCodexOauthStateTtlMs = 10 * 60 * 1000`
  - `lib/server/routes/codex.js:47-72` — `/auth/codex/start` builds the authorize URL with `code_challenge_method=S256` and `codex_cli_simplified_flow=true`
  - `lib/server/routes/codex.js:74-140` — `/auth/codex/callback` exchanges code+verifier at `CODEX_OAUTH_TOKEN_URL`, upserts profile via `authProfiles.upsertCodexProfile()`
  - `lib/server/routes/codex.js:36,142,201` — `/api/codex/status`, `/api/codex/exchange`, `/api/codex/disconnect` management endpoints
- **Verdict:** ✅ CORRECT — new coverage (previously absent from wiki)
- **Fix needed:** None

## Claim 6: Remote MCP injection — managed `mcp.servers.<name>` entry in `openclaw.json`
- **Wiki says:** "When `REMOTE_MCP_URL` + `REMOTE_MCP_API_TOKEN` are set, AlphaClaw writes a managed `mcp.servers.<REMOTE_MCP_NAME>` entry into `openclaw.json` on every gateway start"
- **Source evidence:**
  - `README.md:171` — `REMOTE_MCP_URL`: "When set together with `REMOTE_MCP_API_TOKEN`, AlphaClaw writes a managed `mcp.servers.<name>` entry to `openclaw.json` on every gateway start"
  - `README.md:172` — `REMOTE_MCP_API_TOKEN` persisted as the `${REMOTE_MCP_API_TOKEN}` env reference, never plaintext
  - `README.md:173` — `REMOTE_MCP_NAME` defaults to `remote`
  - `README.md:174` — `REMOTE_MCP_PROXY_URL` routes OpenClaw through a same-host scanning proxy (e.g. `pipelock mcp proxy --listen <url> --upstream <url>`)
  - `lib/server/gateway.js:501-700` — `ensureGatewayProxyConfig()` applies the remote MCP proxy URL during gateway startup
- **Verdict:** ✅ CORRECT — new coverage (previously absent from wiki)
- **Fix needed:** None

## Claim 7: Git auth shim + askpass — credential-free GitHub pushes for the workspace repo
- **Wiki says:** "Git Auth Shim: Installs a managed git shim + askpass helper so the workspace repo can push to GitHub using `GITHUB_TOKEN` without storing credentials"
- **Source evidence:**
  - `README.md:168` — `ALPHACLAW_GIT_SHIM_PATH`: install the managed git auth shim at this path and prepend its directory to runtime `PATH` (default `/usr/local/bin/git`)
  - `README.md:169` — `ALPHACLAW_GIT_ASKPASS_PATH`: install the git askpass helper (default `$TMPDIR/alphaclaw-git-askpass.sh`)
  - `bin/alphaclaw.js:957-991` — copies `lib/scripts/git-askpass` and `lib/scripts/git`, substitutes `@@REAL_GIT@@` / `@@OPENCLAW_REPO_ROOT@@` / `@@ASKPASS_PATH@@`, prepends shim dir to `PATH`
  - `bin/alphaclaw.js:325-357` — `git-sync` writes a per-PID askpass script answering `x-access-token` / `${GITHUB_TOKEN:-}` and runs git with `GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=...`
- **Verdict:** ✅ CORRECT — new coverage (previously absent from wiki)
- **Fix needed:** None

## Claim 8: Deployment surface — Render/Railway templates, Docker, macOS desktop app
- **Wiki says:** "Deploy via Render/Railway one-click templates, Docker, or the macOS desktop app"
- **Source evidence:**
  - `README.md:21-22` — Deploy-to-Render and Deploy-on-Railway buttons; `README.md:26` — Render sponsorship with `RENDER-ALPHACLAW` $50 credit code
  - `README.md:63-65` — official template repo `render-examples/openclaw-render-template`; `README.md:69-73` — Railway `openclaw-fast-start` template with Hobby-plan (8 GB RAM) upgrade guidance
  - `README.md:23` — macOS desktop app DMG at `https://updates.alphaclaw.md/desktop/prod/alphaclaw-mac-latest.dmg`
  - `README.md:84-95` — official `node:22-slim` Dockerfile with git/curl/procps/cron/tini and `ALPHACLAW_ROOT_DIR=/data`
- **Verdict:** ✅ CORRECT — new coverage (previously absent from wiki)
- **Fix needed:** None

## Summary

The AlphaClaw wiki was corrected and expanded:
- **Node floor:** ✅ Fixed — `engines` gate is 22.22.3+ / 24.15.0+ / 25.9.0, not the previously stated older floor
- **Route count:** ✅ Fixed — 19 route modules / ~154 handlers / 25 setup prefixes, not the previously stated lower count
- **Gateway manager:** ✅ Correct (spawn/execSync lifecycle, 127.0.0.1:18789)
- **/v1 proxy:** ✅ Correct (4 endpoint groups, Bearer token, 404 when disabled, security boundary)
- **Codex OAuth:** ✅ Added (PKCE flow, 5 handlers, constants)
- **Remote MCP injection:** ✅ Added (4 env vars, managed `mcp.servers` entry)
- **Git auth shim + askpass:** ✅ Added (managed shim/askpass install, cron git-sync auth)
- **Deployment surface:** ✅ Added (Render/Railway templates, Docker, macOS desktop app)

## Related

- [[alphaclaw]] -- Main wiki entry
- [[openclaw]] -- The AI assistant platform AlphaClaw manages
- [[goclaw]] -- Go MCP gateway
- [[openclaw-container]] -- Container deployment for OpenClaw

## Cross-project

- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
- [[clawpier.codegraph-verify]] -- Similar codegraph verification for ClawPier
