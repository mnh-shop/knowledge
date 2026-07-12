---
title: camofox-browser.codegraph-verify
description: "Source-level verification of camofox-browser — Headless browser MCP for AI agents"
date: 2026-07-12
tags: [camofox-browser, codegraph-verify, browser, mcp, anti-detection]
verified_by: codegraph-explore
source: sources/camofox-browser/
---

# camofox-browser — CodeGraph Verification

**Claim-1: camofox-browser provides a headless browser automation server with C++-level anti-detection for AI agents, built on Camoufox (a Firefox fork).**

- **Evidence:** `README.md` line 4 states "**Anti-detection browser server for AI agents, powered by Camoufox**". Line 12 notes it "Standing on the mighty shoulders of [Camoufox](https://camoufox.com) - a Firefox fork with fingerprint spoofing at the C++ level." Lines 36-37 detail that "Camoufox patches Firefox at the **C++ implementation level** - `navigator.hardwareConcurrency`, WebGL renderers, AudioContext, screen geometry, WebRTC - all spoofed before JavaScript ever sees them. No shims, no wrappers, no tells."
- **Source path:** `sources/camofox-browser/README.md`

**Claim-2: camofox-browser ships an OpenClaw plugin exposing 11 agent tools (create_tab, snapshot, click, type, navigate, scroll, screenshot, close_tab, evaluate, list_tabs, import_cookies).**

- **Evidence:** `package.json` lines 58-116 define the `"openclaw"` extension block with 11 tools listed under `"tools"`: `camofox_create_tab`, `camofox_snapshot`, `camofox_click`, `camofox_type`, `camofox_navigate`, `camofox_scroll`, `camofox_screenshot`, `camofox_close_tab`, `camofox_evaluate`, `camofox_list_tabs`, `camofox_import_cookies`. The `README.md` line 77 shows the plugin install command: `openclaw plugins install @askjo/camofox-browser`. The `openclaw.plugin.json` file (284 lines) provides full plugin metadata including env vars, config schema, permissions, security model, and telemetry declarations.
- **Source path:** `sources/camofox-browser/package.json`, `sources/camofox-browser/openclaw.plugin.json`

**Claim-3: camofox-browser uses element refs (e1, e2, e3) and accessibility snapshots that are ~90% smaller than raw HTML for token-efficient agent interaction.**

- **Evidence:** `README.md` lines 42-43 list features: "**Element Refs** - stable `e1`, `e2`, `e3` identifiers for reliable interaction" and "**Token-Efficient** - accessibility snapshots are ~90% smaller than raw HTML." The API examples at lines 513-534 show the workflow: create tab → get snapshot with refs → click/type by ref. The `AGENTS.md` "Core Workflow" section reinforces this pattern. The snapshot endpoint returns accessibility tree with refs like `[link e1] More information...`.
- **Source path:** `sources/camofox-browser/README.md`

**Claim-4: camofox-browser implements session isolation, cookie import with Netscape-format files, proxy + GeoIP support, and VNC interactive login.**

- **Evidence:** `README.md` lists all these under Features (lines 46-58): "**Session Isolation** - separate cookies/storage per user", "**Cookie Import** - inject Netscape-format cookie files for authenticated browsing", "**Proxy + GeoIP** - route traffic through residential proxies with automatic locale/timezone", and "**VNC Interactive Login** - log into sites visually via noVNC, export storage state for agent reuse." Lines 186-251 document the cookie import flow including the auth gate (`CAMOFOX_API_KEY`), the architecture diagram showing the file-to-browser pipeline, and the sandbox directory (`~/.camofox/cookies/`) with path traversal protection. Proxy configuration is documented at lines 337-379 with support for both simple and backconnect (rotating sticky session) strategies.
- **Source path:** `sources/camofox-browser/README.md`

**Claim-5: camofox-browser separates security concerns across the codebase — no `process.env` in route handlers, no `child_process` in plugin route handlers — enabling auditability for credential handling.**

- **Evidence:** `README.md` "Security Model" section at lines 669-703 documents the code isolation: "All `process.env` reads are centralized in `lib/config.js`. All `child_process` usage is in `lib/launcher.js` and `plugins/youtube/youtube.js`. The main `server.js` has route handlers but zero `process.env` reads and zero `child_process` imports. No single file combines environment/credential access with network sends." The `AGENTS.md` "Code Separation Conventions" section reinforces: "Configuration: `process.env` reads live in `lib/config.js`, which exports a plain config object. No other file reads environment variables directly." The `server.js` imports confirm this — `loadConfig` from `lib/config.js` on line 9, with no `process.env` access in the main handler file.
- **Source path:** `sources/camofox-browser/README.md`, `sources/camofox-browser/AGENTS.md`, `sources/camofox-browser/server.js`

**Claim-6: camofox-browser includes a plugin system with 29 lifecycle events, mutating hooks for browser/session creation, and support for custom metrics via prom-client.**

- **Evidence:** `AGENTS.md` "Plugin System" section documents the full plugin API: `register(app, ctx)` receives 27+ context properties including `ctx.sessions`, `ctx.events`, `ctx.auth`, `ctx.ensureBrowser`, `ctx.getSession`, `ctx.withUserLimit`. The events table lists 29 events across Browser Lifecycle (5), Session Lifecycle (4), Tab Lifecycle (6), Content (4), Input (4), Downloads (2), Cookies/Auth (2), and Server (2). Mutating hooks (`browser:launching`, `session:creating`) use `events.emitAsync()` so listeners can modify launch options in-place before proceeding. Custom metrics are created via `ctx.createMetric()` which returns no-op stubs when Prometheus is disabled. The YouTube plugin (`plugins/youtube/`) serves as a reference implementation.
- **Source path:** `sources/camofox-browser/AGENTS.md`

**Related:** [[camofox-browser]], [[mcp]], [[hermes-agent]], [[openclaw]]
