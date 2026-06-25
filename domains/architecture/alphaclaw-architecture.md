---
name: alphaclaw-architecture
tags: [ai-llm, architecture, bootc, cli, container, dashboard, desktop-app, docker, express, mcp, messaging, monitoring, nodejs, openclaw, orchestration, plugin-sdk, storage, virtualization, watchdog, webhook, webhooks]
description: "Architecture deep-dive of the AlphaClaw ops and setup layer for OpenClaw"
---

# AlphaClaw Architecture

**Source:** `sources/alphaclaw/`

## Runtime Model

AlphaClaw runs as a single Node.js process that acts as a management plane for an OpenClaw gateway child process:

```
┌─────────────────────────────────────────────────────────────────────┐
│                     AlphaClaw (Express)                             │
│  ┌────────────┐  ┌───────────┐  ┌────────┐  ┌───────────────────┐  │
│  │ Auth Layer │  │ API Routes│  │Proxy   │  │ Static / UI       │  │
│  │ (password) │  │ (19 mods) │  │http-proxy │ (lib/public/dist/) │  │
│  └────────────┘  └───────────┘  └───┬────┘  └───────────────────┘  │
│                                      │                              │
│  ┌──────────────────┐  ┌────────────▼────────────┐                │
│  │  Gateway Manager │  │  Watchdog               │                │
│  │  spawn + monitor │  │  health + crash + repair│                │
│  └───────┬──────────┘  └───────────┬─────────────┘                │
│          │                         │                               │
│          │ child process spawn     │ periodic health checks        │
│          ▼                         ▼                               │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                 OpenClaw Gateway (child)                     │   │
│  │                 127.0.0.1:18789                              │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  ALPHACLAW_ROOT_DIR (/data)                                  │   │
│  │  ├── .openclaw/          OpenClaw config + state              │   │
│  │  ├── .env                Environment variables                │   │
│  │  ├── alphaclaw.json      AlphaClaw config                     │   │
│  │  ├── logs/               AlphaClaw log files                  │   │
│  │  ├── hooks/transforms/   Webhook transform modules            │   │
│  │  └── workspace/          The agent's workspace (git repo)      │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Process Lifecycle

### Startup Sequence

1. `bin/alphaclaw.js` is the CLI entrypoint. `alphaclaw start` calls `lib/server.js`.
2. `server.js` initializes the logging subsystem (`initLogWriter`), SQLite databases (watchdog events, webhooks, usage tracking, Gmail state), and loads configuration.
3. The Express server binds to port 3000 (configurable via `PORT` env var).
4. The gateway manager (`gateway.js`) resolves the OpenClaw binary path, prepares the environment via `withOpenclawStartupEnv`, and spawns OpenClaw as a child process on `127.0.0.1:18789`.
5. The watchdog (`watchdog.js`) begins health checks after a 30-second startup grace period (`kHealthStartupGraceMs`).
6. Post-startup, the onboarding wizard checks whether the user has completed setup. If not, the setup UI redirects to the onboarding flow.

### Gateway Lifecycle (`lib/server/gateway.js`)

The gateway manager handles:

- **Spawn:** Resolves the OpenClaw entry point (`require.resolve("openclaw")`), constructs CLI args, injects environment variables (channel tokens, workspace repo, credential paths), and spawns via `child_process.spawn`.
- **Monitoring:** Listens for `exit` events on the child process. Stderr output is captured in a ring buffer (`gatewayStderrTail`, max 50 lines) for diagnostics.
- **Restart:** On unexpected exit, restarts the gateway with exponential backoff. On expected exits (user-triggered via API), waits silently.
- **Environment injection:** `withOpenclawStartupEnv` injects `OPENCLAW_GATEWAY_TOKEN`, managed MCP server entries, and credential file paths. Channel credentials (Telegram, Discord, Slack) are read from the agents' `openclaw.json` config and injected as environment variables.
- **Plugin runtime deps preflight:** Before spawning, the manager runs a preflight check (`kPluginRuntimeDepsPreflightTimeoutMs`: 120s) to verify all required system dependencies are present.
- **Duplicate launch detection:** On exit code 1 with stderr mentioning "already in use" or "already listening", the manager treats this as non-fatal and assumes another gateway instance is running.

### Watchdog Subsystem (`lib/server/watchdog.js`)

The watchdog is a finite state machine with these lifecycle states: `stopped`, `starting`, `healthy`, `degraded`, `crash_loop`, `repairing`.

Key constants:

| Constant | Default | Purpose |
|---|---|---|
| `kWatchdogCheckIntervalMs` | 30,000 ms | Normal health check interval |
| `kWatchdogDegradedCheckIntervalMs` | 10,000 ms | Interval when health is degraded |
| `kWatchdogCrashLoopWindowMs` | 300,000 ms | Time window for crash counting |
| `kWatchdogCrashLoopThreshold` | 3 | Crashes within window to trigger crash loop |
| `kWatchdogMaxRepairAttempts` | 2 | Auto-repair retry limit |
| `kWatchdogStartupFailureThreshold` | 3 | Consecutive startup health failures |

**State transitions:**

1. **Starting:** After gateway launch, a bootstrap health check runs after 5 seconds. If it succeeds, transitions to `healthy`. If it fails, increments `startupConsecutiveHealthFailures`. After `kWatchdogStartupFailureThreshold` failures, transitions to `crash_loop`.
2. **Healthy:** Periodic health checks via `openclaw health` HTTP call to the gateway. Success stays in `healthy`. Failure transitions to `degraded`.
3. **Degraded:** Higher-frequency checks (10s interval). On recovery, transitions back to `healthy`. On persistent failure, transitions to `crash_loop`.
4. **Crash Loop:** The gateway child process exit triggers `gatewayExitHandler` in the watchdog. `crashTimestamps` are tracked within a rolling window. If count exceeds `kWatchdogCrashLoopThreshold` within `kWatchdogCrashLoopWindowMs`, crash loop is declared.
5. **Repairing:** If `WATCHDOG_AUTO_REPAIR` is enabled, the watchdog runs `openclaw doctor --fix --yes` to attempt self-repair. After repair, the gateway is relaunched and health is rechecked. If repair fails after `kWatchdogMaxRepairAttempts`, the watchdog stops and awaits manual intervention.

**Notifications:** On crashes, repairs, and recovery, the watchdog sends alerts via Telegram, Discord, or Slack based on configured channel tokens. The notification format follows a structured pattern (emoji prefix, status line, context, optional view-logs link).

**Incident tracking:** The watchdog maintains `activeIncidentKey` and `sentIncidentNotifications` for deduplication. Incidents are logged to a SQLite-backed event log.

## Startup and Expected Restart Handling

The gateway has a concept of "expected restarts" (`kExpectedRestartWindowMs`: 15s). When an API route triggers a gateway restart (e.g., after env var changes), it sets `expectedRestartInProgress = true` with a deadline. During this window, watchdog exit handling is suppressed. After the deadline, if the gateway hasn't restarted, the watchdog takes over.

## Authentication Flow

AlphaClaw uses a single `SETUP_PASSWORD` for all access, not OpenClaw's pairing code flow.

Login state machine (`login-throttle.js`):

- **Per-IP throttling:** Exponential backoff with `kLoginBaseLockMs`, `kLoginMaxLockMs`, tracked per normalized IP within `kLoginWindowMs` (default 30s window, 5 attempts).
- **Global throttling:** A separate global counter with its own lockout. If total failed attempts across all IPs exceeds `kLoginGlobalMaxAttempts` within `kLoginGlobalWindowMs`, the entire login endpoint is locked.
- **State store:** Default in-memory (`Map`), designed with a `createMemoryLoginThrottleStore` that returns a store interface. The store interface (`get`, `set`, `delete`, `entries`, `runExclusive`) is abstracted so a Redis-backed store could be swapped in.
- **Session management:** Session cookies are set on successful login and validated by middleware on all `/api/*` routes. The `/api/auth` route handles login, logout, and session validation.

## Proxy Layer

Express middleware proxying via `http-proxy` (`lib/server/routes/proxy.js`):

- Routes matching OpenClaw gateway paths (e.g., `/chat`, `/dashboard`, `/api/events/*`) are forwarded to `http://127.0.0.1:18789`.
- Cookie stripping: The setup UI session cookie is removed from requests before forwarding.
- Hop-by-hop headers (`Transfer-Encoding`, `Connection`, etc.) are not passed through.
- WebSocket upgrade is supported via `ws` library for the gateway's real-time event stream.
- The proxy is single-hop -- it only forwards between the Express server and the local gateway child process.

## Webhook Subsystem (`lib/server/webhooks.js` + `lib/server/webhook-middleware.js`)

The webhook system is a full request pipeline:

1. **Registration:** Named webhook endpoints are stored in `openclaw.json` under `hooks.mappings[]`. Each mapping has a name, path, optional transform module, and delivery destination(s).
2. **Ingestion:** Inbound requests hit the Express webhook middleware (`webhook-middleware.js`), which:
   - Authenticates via query-string token (for providers without `Authorization` header support)
   - Sanitizes and redacts sensitive headers and payload fields
   - Deduplicates Gmail push notifications (24-hour TTL)
   - Logs the request to the SQLite webhooks database
3. **Transform pipeline:** If the mapping has a transform module, the raw body is passed through the transform (an ES module loaded from `hooks/transforms/<name>/<name>-transform.mjs`). The module exports a function that can mutate the payload before delivery.
4. **Delivery:** Transformed payloads are forwarded to the configured destination URL via HTTP/HTTPS. Delivery status (success/failure, HTTP status, response body excerpt) is logged.
5. **OAuth callbacks:** Special webhook routes handle OAuth callback flows (e.g., Google Workspace auth). The middleware creates OAuth callback records with tokens, then marks them used after the callback completes.

Managed webhooks: The `gmail` webhook is auto-configured by the Gmail Watch setup flow and is managed internally (config entries are in `kManagedWebhookConfigs`).

## OpenAI-compatible /v1 Proxy

When enabled in the Setup UI (stored in `alphaclaw.json`), the server mounts additional routes:

- `/v1/chat/completions` (POST) -- routes to OpenClaw chat endpoint
- `/v1/responses` (POST) -- routes to OpenClaw responses endpoint
- `/v1/embeddings` (POST) -- routes to OpenClaw embeddings endpoint
- `/v1/models`, `/v1/models/<id>` (GET) -- lists agent targets

Authentication: `Authorization: Bearer <OPENCLAW_GATEWAY_TOKEN>`. Failed bearer token attempts are rate-limited. The setup UI cookie is stripped. JSON bodies up to 50 MB are accepted. When the feature is disabled, all `/v1` paths return 404.

Security note: The gateway token grants full operator-level access -- OpenClaw treats `/v1/chat/completions` as a complete agent-control surface. This proxy is designed for trusted server-to-server callers only.

## Remote MCP Integration

When `REMOTE_MCP_URL` + `REMOTE_MCP_API_TOKEN` are set, AlphaClaw writes a managed `mcp.servers.<REMOTE_MCP_NAME>` block (default key `remote`) to `openclaw.json` on every gateway start. This allows the OpenClaw agent to call back into the remote MCP server. If `REMOTE_MCP_PROXY_URL` is set, the connection routes through a same-host scanning proxy (e.g., Pipelock MCP reverse proxy).

The token is persisted as a `${REMOTE_MCP_API_TOKEN}` reference in `openclaw.json`, never as plaintext. The actual value is injected into the runtime environment.

## Setup UI Frontend (`lib/public/js/`)

The frontend is a single-page application built with Preact + htm + Wouter. It is compiled to a single bundle (plus optional chunks) by esbuild via `scripts/build-ui.mjs`.

### Component Architecture

```
lib/public/js/
├── app.js             -- SPA shell with routing, tabs, agent sidebar
├── components/         -- Reusable UI components
│   ├── action-button.js
│   ├── badge.js
│   ├── confirm-dialog.js
│   ├── icons.js          -- Shared SVG icons
│   ├── loading-spinner.js
│   ├── modal-shell.js
│   ├── page-header.js
│   ├── secret-input.js
│   ├── toggle-switch.js
│   └── tooltip.js
├── hooks/               -- Custom hooks for data fetching
│   ├── use-cached-fetch.js
│   └── use-polling.js
├── lib/                 -- Shared utilities
│   ├── api-cache.js     -- In-memory cache layer
│   ├── format.js        -- Date/time/number formatters
│   ├── session-keys.js  -- Session key parsing
│   └── storage-keys.js  -- localStorage key constants
└── [feature-folders]/   -- Per-tab feature components
    ├── browse/
    ├── cron/
    ├── envars/
    ├── google/
    ├── nodes/
    ├── providers/
    ├── usage/
    ├── watchdog/
    └── webhooks/
```

### Data Flow

1. Components mount and call `useCachedFetch` or `usePolling` hooks.
2. Hooks call the Express API via `cachedFetch` (wraps `fetch` with an in-memory cache tier).
3. Tab switching preserves state via cache -- components unmount on navigation and remount from cache on return.
4. Mutations (POST/PUT/DELETE) invalidate the relevant cache keys via `invalidateCache()`.

### Caching Strategy (`api-cache.js`)

- Single in-memory `Map<url, {data, timestamp}>`.
- TTL defaults: polling data (shorter), static data (longer).
- `usePolling` has a `pauseWhenHidden` flag (default `true`) to avoid background traffic.
- After mutations, the calling code calls `invalidateCache(url)` to force re-fetch on next mount.

### Theme System (`lib/public/css/theme.css` + `tailwind.config.cjs`)

CSS variables define the color palette (surface, field, border, accent, status colors, etc.) and are exposed through Tailwind's `tailwind.config.cjs` as semantic utility classes:

- `text-body`, `text-fg-muted`, `text-fg-dim` -- text hierarchy
- `bg-surface`, `bg-field`, `bg-modal` -- background layers
- `bg-status-error-bg`, `border-status-warning-border` -- status colors
- `ac-btn-cyan`, `ac-btn-secondary`, `ac-btn-green`, `ac-btn-danger`, `ac-btn-ghost` -- button styles
- `ac-surface-inset` -- nested surface backgrounds
- `ac-tip-link` -- help/tip link styling

All UI color tokens are defined as CSS variables and consumed through Tailwind, making theme changes centralized rather than distributed across components.

## Google Workspace Integration

The Google integration (`lib/server/google-state.js`, `lib/server/gmail-watch.js`, `lib/server/gmail-serve.js`, `lib/server/gmail-push.js`) follows this flow:

1. **OAuth:** Uses Google OAuth 2.0 with PKCE. The user configures client ID and secret in the Setup UI. The OAuth flow opens a Google consent screen, and the callback is handled by a managed webhook endpoint.
2. **Multi-service scopes:** The integration requests scopes for Gmail, Calendar, Drive, Docs, Sheets, Tasks, Contacts, and Meet.
3. **Gmail Watch:** The setup wizard guides the user through creating a Google Cloud Pub/Sub topic + subscription. The subscription pushes to AlphaClaw's webhook endpoint. AlphaClaw validates incoming push notifications, fetches new emails via Gmail API, and injects them as tool results.
4. **State management:** Google credentials and tokens are stored in the AlphaClaw config (`alphaclaw.json`), not in plaintext env vars. Token refresh is handled automatically.

## Usage Tracking (`lib/plugin/usage-tracker/`)

AlphaClaw ships an OpenClaw plugin (`lib/plugin/usage-tracker/`) that hooks into the OpenClaw gateway to capture per-session and per-agent token usage and cost data. The data is stored in a SQLite database (`usage.sqlite`) and exposed through the Setup UI's Usage tab with breakdowns by session, agent, and time period, plus cost projections and trend charts (Chart.js).

## Prompt Hardening (`lib/setup/core-prompts/`)

AlphaClaw ships runtime prompt templates injected into the OpenClaw agent's system prompt:

- **AGENTS.md:** Set of agent behavioral guide rails -- commit discipline, safe practices, change summaries. This is the deployed agent's prompt, NOT project-level instructions (which go in the repo-root AGENTS.md).
- **TOOLS.md:** Tool usage guidance.

These are loaded and injected by the AlphaClaw server into the agent's system prompt on every message, preventing drift.

## Channel Orchestration

### Telegram

- Bot token configured via Setup UI or `TELEGRAM_BOT_TOKEN` env var.
- Multi-topic support: Telegram topics can be mapped to specific agents via the CLI (`alphaclaw telegram topic add ...`).
- The topic registry (`topic-registry.js`) tracks thread-to-agent mappings.
- The workspace helper (`telegram-workspace.js`) generates the Telegram configuration block for `openclaw.json`.

### Discord

- Bot token configured via `DISCORD_BOT_TOKEN` env var.
- Per-agent channel bindings are persisted in the agent's config.
- A lightweight API helper (`discord-api.js`) handles bot registration and channel list retrieval.

### Slack

- Socket Mode bot with `SLACK_BOT_TOKEN`.
- API helper (`slack-api.js`, ~9.5KB) handles channel discovery and pairing.
- App-level token for Socket Mode connections.

## Cron Job Management (`lib/server/cron-service.js`)

The cron subsystem manages a cron tab file on disk and exposes CRUD operations through the API:

- Jobs are stored as standard cron entries in `/etc/cron.d/alphaclaw` (or a fallback path).
- Each job runs a command (typically an OpenClaw tool invocation) at the scheduled interval.
- The service tracks run history, exit codes, stdout/stderr, and usage breakdowns per run.
- The UI includes an interactive rolling calendar view and trend analytics.

## Deployment Topology

AlphaClaw deploys as a single container (or VM process) running the Express server. It manages OpenClaw as a child process in the same container. Key deployment paths:

- **Railway:** One-click deploy template, must upgrade to Hobby plan for 8GB RAM.
- **Render:** One-click deploy template with Web Service configuration.
- **Docker:** Multi-stage build from `node:22-slim` with `tini` as init system.
- **npm global:** `npm install -g @chrysb/alphaclaw && alphaclaw start` for direct server runs.

Data directory (`ALPHACLAW_ROOT_DIR`, default `/data`) contains all persistent state: OpenClaw config, SQLite databases, env file, logs, webhook transform modules, and the Git-backed workspace.

## Release Flow

1. Beta iterations: `npm version prerelease --preid=beta`, publish with `--tag beta`.
2. After each beta, pin the exact version in deployment templates (Railway, Render, Apex).
3. Promote to stable: `npm version <version>`, `npm publish`, pin all templates to `latest`.
4. Tests: `npm test` runs 440+ Vitest tests across server routes, watchdog, webhooks, and core utilities.

## Related

- [[alphaclaw]] -- Main wiki entry
- [[openclaw]] -- The AI assistant platform AlphaClaw manages
- [[openclaw-deployment]] -- OpenClaw's own deployment patterns
- [[clawpier]] -- Desktop GUI for OpenClaw Docker containers
- [[tank-os]] -- Fedora bootc appliance for OpenClaw deployment
