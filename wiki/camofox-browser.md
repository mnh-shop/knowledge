---
name: camofox-browser
title: Camofox Browser
description: "Anti-detection browser automation tool for MCP-based web scraping and testing"
tags: [cli, docker, mcp, browser-automation, javascript]
source: sources/camofox-browser/
license: MIT
org: Jo Inc
version: 1.11.2
---

# camofox-browser

Anti-detection browser automation server for AI agents, powered by Camoufox (a Firefox fork with C++-level fingerprint spoofing). Wraps a Camoufox browser engine in a REST API designed for programmatic agent use: accessibility snapshots instead of HTML, stable element refs for interaction, session isolation, and search macros for common sites.

Built by [AskJo.ai](https://askjo.ai) (`@askjo/camofox-browser`).

## Key Concepts

**Camoufox** -- A Firefox fork that patches browser fingerprint vectors at the C++ implementation level (hardwareConcurrency, WebGL renderers, AudioContext, screen geometry, WebRTC). No JavaScript shims or wrappers that could be detected.

**Element Refs** -- Instead of fragile CSS selectors, the API assigns stable identifiers (`e1`, `e2`, `e3`) to interactive elements in an accessibility snapshot. Agents interact using these refs, which survive page changes better than selectors.

**Session Isolation** -- Each `userId` gets an isolated Playwright browser context with its own cookies, storage, and proxy settings. Sessions expire after a configurable timeout.

**Search Macros** -- Built-in shortcuts for navigating common sites: `@google_search`, `@youtube_search`, `@amazon_search`, `@reddit_search`, `@wikipedia_search`, `@twitter_search`, `@yelp_search`, `@spotify_search`, `@netflix_search`, `@linkedin_search`, `@instagram_search`, `@tiktok_search`, `@twitch_search`.

## Architecture

```
camofox-browser
  ├── server.js          -- Express app: all REST routes, session management, browser lifecycle
  ├── lib/               -- Core modules (config, auth, launcher, plugins, snapshot, etc.)
  ├── plugins/           -- Extensible plugin system (Youtube, Persistence, VNC)
  ├── scripts/           -- CLI tools (plugin management, postinstall, OpenAPI generation)
  ├── docs/              -- OpenAPI/stripey docs UI
  └── workers/           -- Cloudflare Workers (crash reporter)
```

### server.js

Single-file Express server (~6000 lines). Handles all REST API routes, manages browser sessions, coordinates the Camoufox browser lifecycle, and loads plugins. Key internal state:

- `sessions` (Map) -- `userId -> { context, tabGroups, lastAccess }` -- each user gets an isolated browser context
- `CONFIG` -- merged from env vars, defaults, and `camofox.config.json`
- `healthState` -- tracks browser health, crash recovery, and memory pressure
- `pluginEvents` (EventEmitter) -- plugin event bus for lifecycle hooks
- `pluginEvents.emitAsync()` -- awaitable event emission for mutating hooks

### lib/ modules

| Module | Path | Purpose |
|--------|------|---------|
| Config | `lib/config.js` | Load config from env vars + `camofox.config.json` |
| Auth | `lib/auth.js` | Bearer token auth (`CAMOFOX_API_KEY`, `CAMOFOX_ACCESS_KEY`, `CAMOFOX_ADMIN_KEY`) |
| Launcher | `lib/launcher.js` | Spawn/manage the Camoufox child process |
| Plugins | `lib/plugins.js` | Plugin loader, event bus, config reader |
| Snapshot | `lib/snapshot.js` | Accessibility snapshot windowing/truncation (80K char limit, paginated) |
| Macros | `lib/macros.js` | Search macro expansion (e.g. `@google_search` -> URL) |
| Proxy | `lib/proxy.js` | Proxy pool with rotation and locale/timezone auto-detection |
| Cookies | `lib/cookies.js` | Netscape cookie file parser, cookie injection |
| Downloads | `lib/downloads.js` | Browser download capture and API retrieval |
| Tracing | `lib/tracing.js` | Playwright trace capture (per-session opt-in, list/fetch/delete) |
| Extract | `lib/extract.js` | JSON Schema-based structured extraction (`x-ref`) |
| Metrics | `lib/metrics.js` | Prometheus metrics (`prom-client`): request duration, page load, etc. |
| Fly | `lib/fly.js` | Horizontal scaling helpers (Fly.io multi-machine `fly-replay`) |
| Images | `lib/images.js` | DOM image extraction (list `<img>` elements) |
| Resources | `lib/resources.js` | Resource block/interception for page optimization |
| Persistence | `lib/persistence.js` | Session state persistence (CRDT-based, optional Redis) |
| Inflight | `lib/inflight.js` | Track in-flight requests for graceful shutdown |
| Reporter | `lib/reporter.js` | Telemetry/crash reporter (anonymized GitHub Issues) |
| Sentry | `lib/sentry.js` | Optional Sentry error reporting |
| OpenAPI | `lib/openapi.js` | Auto-generate OpenAPI spec from JSDoc, serve docs UI |
| Tmp-cleanup | `lib/tmp-cleanup.js` | Temp directory size monitoring and cleanup |
| Request-utils | `lib/request-utils.js` | Request ID generation, validation utilities |
| Camoufox-executable | `lib/camoufox-executable.js` | Camoufox binary path resolution |

### Plugins System

Plugins live in `plugins/<name>/index.js` and export a `register(app, ctx, pluginConfig)` function. The plugin context (`ctx`) provides access to sessions, config, logging, auth middleware, core functions, and the EventEmitter for lifecycle hooks.

**Plugin lifecycle events** (29 events across 7 categories):
- Browser lifecycle: `browser:launching` (mutable), `browser:launched`, `browser:restart`, `browser:closed`, `browser:error`
- Session lifecycle: `session:creating` (mutable), `session:created`, `session:destroying`, `session:destroyed`, `session:expired`
- Tab lifecycle: `tab:created`, `tab:navigated`, `tab:destroyed`, `tab:recycled`, `tab:error`
- Content: `tab:snapshot`, `tab:screenshot`, `tab:evaluate`, `tab:evaluated`
- Input: `tab:click`, `tab:type`, `tab:scroll`, `tab:press`
- Downloads: `tab:download:start`, `tab:download:complete`
- Cookies/Auth: `session:cookies:import`, `session:storage:export`
- Server: `server:starting`, `server:started`, `server:shutdown`

Some hooks are mutable -- plugins receive the options object by reference and can modify it before core processing.

**Built-in plugins:**

| Plugin | Path | Purpose |
|--------|------|---------|
| youtube | `plugins/youtube/` | YouTube transcript extraction via yt-dlp |
| persistence | `plugins/persistence/` | CRDT-based session state persistence (optional Redis) |
| vnc | `plugins/vnc/` | VNC virtual display via Xvfb + x11vnc + noVNC for interactive login |

**Plugin management scripts:**
- `node scripts/plugin.js install <name>` -- install from npm, git URL, or local dir
- `node scripts/plugin.js remove <name>` -- remove a plugin
- `node scripts/plugin.js list` -- list installed plugins with status

## REST API

Server listens on port 9377 by default. Routes are organized into these groups:

| Group | Routes | Description |
|-------|--------|-------------|
| **System** | `GET /health`, `GET /metrics`, `GET /stop` | Health, Prometheus metrics, graceful shutdown |
| **Tabs** | `POST /tabs`, `GET /tabs`, `GET /tabs/:tabId`, `DELETE /tabs/:tabId`, `DELETE /tabs/group/:listItemId` | Create, list, inspect, close tabs and tab groups |
| **Navigation** | `POST /tabs/:tabId/navigate`, `POST /tabs/:tabId/back`, `POST /tabs/:tabId/forward`, `POST /tabs/:tabId/refresh` | URL navigation and browser history |
| **Interaction** | `POST /tabs/:tabId/click`, `POST /tabs/:tabId/type`, `POST /tabs/:tabId/scroll`, `POST /tabs/:tabId/press`, `POST /tabs/:tabId/evaluate` | Element interaction |
| **Content** | `GET /tabs/:tabId/snapshot`, `GET /tabs/:tabId/screenshot`, `GET /tabs/:tabId/links`, `GET /tabs/:tabId/images`, `POST /tabs/:tabId/extract`, `GET /tabs/:tabId/downloads`, `GET /tabs/:tabId/downloads/:filename` | Page content, screenshots, structured extraction |
| **Sessions** | `POST /sessions/:userId/cookies`, `POST /sessions/:userId/cookies/import`, `DELETE /sessions/:userId`, `GET /sessions/:userId/traces`, `DELETE /sessions/:userId/traces/:traceName` | Cookie management, session teardown, trace capture |
| **Browser** | `POST /browser/start`, `POST /browser/stop`, `POST /browser/restart` | Global browser lifecycle control |
| **Docs** | `GET /openapi.json`, `GET /docs`, `GET /fox.png` | OpenAPI spec and UI |

### Core workflow

```
1. POST /tabs        -> {"tabId": "abc"}
2. POST /tabs/:tabId/navigate  -> navigates to URL
3. GET /tabs/:tabId/snapshot   -> accessibility tree with refs
4. POST /tabs/:tabId/click     -> interact via ref (e.g. {"ref": "e1"})
5. Repeat 3-4 as needed
```

## OpenClaw Plugin (MCP Integration)

The project ships as an OpenClaw/Clawdbot MCP-compatible plugin via `plugin.ts` (TypeScript source) and `plugin.js` (compiled output). When installed via `openclaw plugins install @askjo/camofox-browser`, it registers 11 tools:

- `camofox_create_tab` -- Open a new browser tab
- `camofox_snapshot` -- Accessibility snapshot + screenshot
- `camofox_click` -- Click element by ref or selector
- `camofox_type` -- Type text into element
- `camofox_navigate` -- Navigate to URL or search macro
- `camofox_scroll` -- Scroll page
- `camofox_screenshot` -- Capture screenshot
- `camofox_close_tab` -- Close a tab
- `camofox_evaluate` -- Execute JavaScript in page context
- `camofox_list_tabs` -- List open tabs for a user
- `camofox_import_cookies` -- Import Netscape cookie file (requires `CAMOFOX_API_KEY`)

The plugin auto-starts the server process (default `localhost:9377`) and proxies tool calls to the REST API.

## Configuration

Env vars and `camofox.config.json` (in project root):

```json
{
  "id": "camofox-browser",
  "plugins": {
    "youtube": { "enabled": true },
    "persistence": { "enabled": true },
    "vnc": { "enabled": false, "resolution": "1920x1080" }
  }
}
```

Key env vars: `CAMOFOX_PORT`, `CAMOFOX_API_KEY`, `CAMOFOX_ACCESS_KEY`, `CAMOFOX_ADMIN_KEY`, `MAX_SESSIONS`, `MAX_TABS_PER_SESSION`, `SESSION_TIMEOUT_MS`, `PROMETHEUS_ENABLED`, `CAMOUFOX_EXECUTABLE`, `CAMOFOX_CRASH_REPORT_ENABLED`, `PROXY_LIST`, `DISABLE_AUTO_DOWNLOAD`.

See `AGENTS.md` for full reference.

## Deployment

- **npm**: `npx @askjo/camofox-browser`
- **Docker**: `make up` (auto-detects arch, pre-fetches binaries for fast rebuilds)
- **Fly.io**: via `fly.toml` (horizontal scaling with `fly-replay`)
- **Railway**: via `railway.toml`

Docker image (`node:22-slim`) includes Camoufox binary, yt-dlp, Mesa for WebGL, Xvfb for virtual display, and fonts. Build uses multi-stage caching.

## Testing

Unit and integration tests use Jest with `--experimental-vm-modules`. Live tests require `RUN_LIVE_TESTS=1`.

Test files in `tests/unit/` cover: session cleanup, downloads, proxy, navigation timeout, tab lifecycle, crash relay, memory pressure, auth, access key, cookies, config, reporter, snapshot, type/keyboard mode, Fly replay, viewport, security, tracing, and more.

## Related

- **Camoufox** — the underlying Firefox fork with C++ anti-detection (covered above under Key Concepts)
- [[OpenClaw]] -- the MCP agent runtime that hosts this plugin
- [[Clawdbot]] -- the broader agent ecosystem
- [Playwright](https://playwright.dev) -- the browser automation layer
- [AskJo.ai](https://askjo.ai) -- the company behind camofox-browser (AskJo.ai)
