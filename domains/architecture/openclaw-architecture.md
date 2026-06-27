---
name: openclaw-architecture
tags: [acp, agent-gateway, architecture, cli, docker, live-canvas, mcp, messaging, monitoring, openclaw, orchestration, personal-assistant, plugin-sdk, quadlet, security, storage, systemd, typescript]
description: OpenClaw Architecture
source: sources/openclaw/
---

# OpenClaw Architecture
**Source:** `sources/openclaw/`

OpenClaw is a self-hosted, open-source gateway and agent runtime for building autonomous AI agent deployment stacks. Written in TypeScript (Node.js, no Express/Fastify), it provides a custom HTTP+WebSocket server, plugin system, 30+ channel adapters, and dual-protocol ACP/MCP surfaces.

## Table of Contents

- [Gateway Architecture](#gateway-architecture)
- [Startup Sequence and Lifecycle](#startup-sequence-and-lifecycle)
- [WebSocket Runtime](#websocket-runtime)
- [Agent System](#agent-system)
- [Channel Architecture](#channel-architecture)
- [Plugin System](#plugin-system)
- [State and Storage](#state-and-storage)
- [Tool System](#tool-system)
- [Gateway Protocol](#gateway-protocol)
- [UI and Live Canvas (A2UI)](#ui-and-live-canvas-a2ui)
- [Security Architecture](#security-architecture)
- [CLI Architecture](#cli-architecture)
- [Talk System (Voice/Video)](#talk-system-voicevideo)
- [Node and Device Pairing](#node-and-device-pairing)
- [Key Source Components](#key-source-components)

---

## Gateway Architecture

The Gateway is a Node.js HTTP+WebSocket server built from scratch (no Express, no Fastify). Entry at `src/entry.ts` via `isMainModule()`, delegating to `src/cli/run-main.ts` `runCli()` which bootstraps proxies, runs Crestodian onboarding for fresh installs, builds a Commander program, registers plugin commands, and launches `startGatewayServer()`.

### Server Implementation

The actual server lives in `src/gateway/server.impl.ts` (~1300 lines). It assembles runtime state:

- Method registries (RPC method catalog)
- Plugin channel registries
- Config snapshots
- Auth rate limiter
- Task runner
- Event loop health monitor
- Startup readiness sidecar

It then builds an HTTP server via `src/gateway/server-http.ts` `createGatewayHttpServer()` and attaches WebSocket upgrade handling via `attachGatewayUpgradeHandler()`.

### Lazy Module Architecture

The server uses a lazy-loading pattern (`src/gateway/server.ts`) to defer heavy module imports:

- `server.ts` re-exports only types and the `truncateCloseReason` helper
- `startGatewayServer()` dynamically imports `server.impl.js` at call time via `loadServerImpl()`
- Startup tracing via `OPENCLAW_GATEWAY_STARTUP_TRACE` environment variable
- Control UI SPA handler is dynamically imported to avoid bundling the SPA at startup
- WebSocket message handler (`ws-connection/message-handler.js`) is dynamically imported after WebSocket upgrade

### HTTP Routing: Stages Pattern

HTTP routing uses an ordered list of `GatewayHttpRequestStage` objects that run sequentially. The first stage that returns `true` claims the request. Stages are defined in `server-http.ts`:

1. `gateway-probes` -- health endpoints (`/healthz`, `/readyz`, `/health`, `/ready`)
2. `hooks` -- lifecycle hooks
3. `models` -- model listing (`/v1/models`)
4. `embeddings` -- embedding endpoints (`/v1/embeddings`)
5. `tools-invoke` -- tool invocation (`/tools/invoke`)
6. `sessions-kill` -- session termination (`/sessions/{key}/kill`)
7. `sessions-history` -- session history retrieval (`/sessions/{key}/history`)
8. `openresponses` -- OpenAI Responses API compatibility (`/v1/responses`)
9. `openai` -- OpenAI Chat Completions API compatibility (`/v1/chat/completions`)
10. `plugin-node-capability-auth`
11. `plugin-http` -- plugin-registered HTTP routes
12. `control-ui` -- SPA fallback
13. `chat-managed-image-media`

This allows plugin routes, control UI SPA fallback, and OpenAI-compatible endpoints to coexist on the same port without conflicts.

### WebSocket Upgrades

WebSocket upgrades go through:

1. **Pre-auth connection budget enforcement** (anti-DoS) via `AuthRateLimiter`
2. **Plugin upgrade handler dispatch** -- registered plugin WS handlers get first chance
3. **`ws` library** handles the raw connection
4. **Post-handshake auth** via `auth-resolve.ts` (token, password, trusted-proxy, Tailscale WhoIs)
5. **Connection handler** at `src/gateway/server/ws-connection.ts` attaches a message handler from `src/gateway/server/ws-connection/message-handler.js` (dynamically imported for startup laziness), which routes incoming RPC frames to `GatewayMethodRegistry`-resolved method handlers
6. **Streaming handler** at `src/gateway/server/ws-streaming.ts` attaches streaming callbacks

### Auth Modes

Auth is resolved in `auth-resolve.ts`:

| Mode | Config Value | Mechanism |
|------|-------------|-----------|
| None | `none` | Skip auth entirely (private ingress only) |
| Token | `token` | Bearer token with constant-time comparison via `safeEqualSecret` |
| Password | `password` | Shared secret on connect params |
| Trusted Proxy | `trusted-proxy` | Reverse proxy forwards identity headers |
| Tailscale | `allowTailscale` | Non-loopback connections via Tailscale WhoIs API |

Rate limiting uses `AuthRateLimiter` per IP with configurable thresholds and retry-after durations (`src/gateway/auth-rate-limit.ts`).

### Health and Lifecycle

- **Liveness probes** at `/health` and `/healthz` return `{"ok":true,"status":"live"}`
- **Readiness probes** at `/ready` and `/readyz` return subsystem status (channel health, startup sidecar, drain state)
- Detailed readiness revealed only to loopback or authenticated callers
- **Graceful shutdown** tracks active sessions and drains the command queue
- **TLS support** via `createHttpsServer`
- **Tailscale serve mode** for secure remote exposure
- **HSTS headers** on all HTTP responses
- **Control UI SPA** at a configurable base path
- **Config reload hooks** without restart

### Bind Modes

Via `OPENCLAW_GATEWAY_BIND`:

| Mode | Behavior |
|------|----------|
| `loopback` | 127.0.0.1 only (default for non-Docker) |
| `lan` | 0.0.0.0 (default for Docker) |
| `tailnet` | Tailscale interface only |
| `auto` | Detect from environment |
| `custom` | Use `customBindHost` |

### Server Capabilities

The Gateway supports a `GatewayServerCapability` type system that drives what the server advertises at connect time:

- Channel support capability
- Config file capability
- Cron capability
- Device pairing capability
- Node pairing capability
- Message sending capability
- Plugin approval capability
- Secret management capability
- Tool execution capability
- Stream mode capability

OPC (Operator Capabilities) model: each capability can expose methods, events, and their scopes to connecting clients.

### Event Loop Health Monitor

`src/gateway/server/event-loop-health-monitor.ts`: Monitors Node event loop lag. Delays are reported as subsystem status and can drive readiness probe failures if the event loop is blocked beyond a threshold.

---

## Startup Sequence and Lifecycle

The gateway startup (`src/daemon/gateway-entrypoint.ts`) follows 8 phases tracked by `startupTrace.measure()`:

1. **Proxy bootstrap** -- SSH tunnel proxies for channel connectivity
2. **Config loading** -- Load `openclaw.json5` with `$include` resolution, env var substitution, validation
3. **Database initialization** -- Open shared state SQLite DB (`openclaw-state-db`), run migrations
4. **Plugin system initialization** -- Load plugin manifests, activate bundled plugins, register runtime hooks
5. **Channel startup** -- Start configured channel adapters (Telegram, Discord, etc.)
6. **Method registration** -- Register all gateway RPC methods (150+) in the method registry
7. **HTTP+WebSocket server start** -- Bind port, start accepting connections
8. **Startup sidecar completion** -- Mark readiness probes as successful

Each phase is timed. Summary sent to log on completion. Failures in phases 1-6 cause startup to abort; phase 7+ failures are handled as degraded mode.

### Readiness Sidecar

A startup sidecar object tracks completion of each phase. The readiness probe checks:

- Are all startup phases complete?
- Are channels healthy? (per-account snapshots, stale-event thresholds, connect grace windows)
- Is the gateway not draining?

### Gateway Restart Modes

| Command | Behavior |
|---------|----------|
| `--safe` | Preflights active work, defers restart until completion |
| `--safe --skip-deferral` | Same preflight but bypasses deferral (escape hatch) |
| `--force` | Immediate restart, no active-work drain |
| `SIGUSR1` | In-process restart (when `commands.restart` enabled) |
| `SIGINT`/`SIGTERM` | Graceful stop |

### Service Management

| Platform | Mechanism |
|----------|-----------|
| Linux | systemd user service at `~/.config/systemd/user/openclaw-gateway.service` |
| macOS | LaunchAgent at `~/Library/LaunchAgents/ai.openclaw.gateway.<profile>.plist` |
| Windows | Scheduled Task via `schtasks` |

---

## WebSocket Runtime

The WebSocket handler runtime (`src/gateway/server-ws-runtime.ts`) implements a non-blocking select-like event loop with three prioritized channels:

1. **Tick channel** -- Periodic keepalive ticks (default 15s interval, configurable)
2. **Push channel** -- Server-pushed events (chat updates, agent messages, tool calls, etc.)
3. **RPC channel** -- Incoming JSON-RPC request/response frames

### Handler Registration

- Handlers are registered via `GatewayMethodRegistry` (`src/gateway/methods/core-descriptors.ts`)
- Each method has a: name, schema (TypeBox), handler function, scope requirements
- Methods are registered at startup from core methods and plugin-registered methods

### Wire Format

JSON-over-WebSocket with three frame types discriminated by a `type` field:

```json
{"type":"req","id":"r1","method":"sessions.list","params":{}}
{"type":"res","id":"r1","ok":true,"payload":{...}}
{"type":"event","event":"chat","payload":{...},"seq":142}
```

### Frame Limits

- Pre-connect frames: 64 KB max
- Post-handshake max payload: 25 MB (configurable via `hello-ok.policy.maxPayload`)
- Max buffered bytes: Configurable via `hello-ok.policy.maxBufferedBytes`

### Protocol Version

- Current: 4 (`PROTOCOL_VERSION = 4`)
- Minimum client version: 4

### Connect Flow

1. Client connects WebSocket to `ws://gateway-host:18789`
2. Client sends `ConnectParams` JSON frame with protocol version range, client metadata, auth credentials
3. Server responds with `HelloOk` containing negotiated protocol version, server info, available methods/events, state snapshot, auth info
4. Normal RPC communication begins

### Push Events

Events are scope-gated. Major event types include: `chat` (delta text, UI updates), `agent` (streaming agent output), `session.*` (message, operation, tool), `presence`, `tick`, `health`, `heartbeat`, `cron`, `shutdown`, `node.*`, `device.*`, `exec.approval.*`, `plugin.approval.*`, `update.available`.

---

## Agent System

OpenClaw is fundamentally agent-based. Each agent has an identity (name, avatar, description), model configuration, tool sets, permission scopes, and file attachments.

### Agent Lifecycle

Agents are created/updated/deleted via CLI or gateway RPC methods. The session lifecycle is defined in `src/gateway/session-lifecycle-state.ts`:

- **State machine** with phases (`start`, `end`, `error`) and terminal statuses (`done`, `timeout`, `killed`, `failed`)
- **Session persistence** to shared state database with compaction support for long-running conversations
- **Restart recovery** detects stale sessions and resumes them
- **Steering queue**: interrupt-and-steer variant for active sessions (`sessions.steer`)

### Subagent Spawning (ACP)

Subagent spawning uses ACP (`src/agents/acp-spawn.ts`):

- Spawn depth limits (default 4)
- Max children per agent (default 10)
- Requester origin resolution for child agents
- Thread binding policy
- Workspace isolation
- Parent-stream relay (`acp-spawn-parent-stream.ts`) for stdout/stderr relay to subagent sessions

### Workspaces

Workspaces are per-agent directories containing configuration, files, and `BOOT.md` files. `src/gateway/boot.ts` processes BOOT.md on gateway startup by running them as agent commands with internal-runtime-context delimiters.

### Embedded Runners

Agent execution uses embedded runners (`src/agents/embedded-agent-runner/`) with hooks:

- `before-agent-start`
- `before-tool-call`
- `before-agent-reply`
- `after-tool-call`
- Compaction
- Finalization

Agent settings, steering queues, and sandbox runtime status are managed in `src/agents/`.

### Identity

Identity management via `src/agents/identity-avatar.ts` resolves assistant identity from config and serves avatar images through the control UI HTTP handler.

---

## Channel Architecture

The channel system provides transport-agnostic message adapters for external platforms. 30+ supported channels including: WhatsApp, Telegram, Slack, Discord, Google Chat, Signal, iMessage, IRC, Microsoft Teams, Matrix, Feishu, LINE, Mattermost, Nextcloud Talk, Nostr, Synology Chat, Tlon, Twitch, Zalo, WeChat, QQ, and WebChat.

Channel plugins live in `extensions/` as bundled plugins, discovered and loaded through the plugin system.

### Core Abstractions

Core channel abstractions in `src/channels/`:

- **Session management** -- Per-channel session IDs, thread binding
- **Message routing** -- `resolve-route.ts` with `RoutePeer` (kind + id), `ChatType` (direct/group/channel)
- **Thread binding** -- Reply-to-thread, conversation resolution
- **Streaming config** -- `streaming.ts` normalizes legacy flat keys and current nested config: preview modes (`off`, `partial`, `block`, `progress`), text chunking (`length`, `newline`), block coalescing
- **DM policy** -- Who can DM the agent
- **Mention gating** -- Whether the agent responds to @mentions only
- **Typing lifecycle** -- Typing indicators when agent is generating
- **Reaction handling** -- Emoji reactions on messages
- **Status monitoring** -- Per-channel health checks
- **Outbound delivery** -- Queue-based outbound message delivery

### Channel Manager

`src/gateway/server-channels.ts` defines the `ChannelManager` type:

- `startChannels()` -- Start all configured channels
- `startChannel(id, accountId)` -- Start a specific channel + account
- `stopChannel(id, accountId, opts)` -- Stop a specific channel
- `getRuntimeSnapshot()` -- Get channel runtime health/status

Channel lifecycle hooks: `onChannelStarted`, `onChannelStopped`, health check callbacks.

### Plugin SDK for Channels

The Plugin SDK (`src/plugin-sdk/core.ts`) provides:

- `defineChannelPluginEntry()` -- Define a channel plugin entry point
- `createChatChannelPlugin()` -- Create a chat channel plugin
- `createChannelPluginBase()` -- Base constructor for channel plugins

It composes security (DM policy), pairing (approval notification), threading (reply-to modes), and outbound delivery behavior.

### Proxy Bootstrap

Channel connectivity through restricted networks uses SSH tunnel proxies configured at startup. The proxy bootstrap phase establishes tunnels before channel plugins start.

---

## Plugin System

The plugin system is one of the most complex subsystems. It supports:

1. **Bundled plugins** -- Shipped in `extensions/` (85+ plugins: Anthropic, OpenAI, Google, AWS Bedrock, Slack, Discord, Telegram, canvas, browser, etc.)
2. **Third-party/community plugins** -- Installed via ClawHub marketplace, npm, or git.

### Plugin SDK Contract

The plugin SDK (`src/plugin-sdk/`) is the public contract between plugins and core, using narrow subpaths and acyclic exports. Plugin authors should only ever import from `openclaw/plugin-sdk/*`.

The SDK provides ~70+ registration methods including:

- `definePluginEntry()` -- Core entry point definition
- `defineToolPlugin()` -- Tool plugin with TypeBox schemas
- `defineChannelPluginEntry()` -- Channel plugin entry
- `registerTool()`, `registerHook()`, `registerCommand()`, `registerHTTPRoute()`, `registerChannel()`, etc.

### Plugin Entry System

`src/plugin-sdk/plugin-entry.ts`: `DefinePluginEntryOptions` with `id`, `name`, `description`, `configSchema`, and a `register` callback that receives `OpenClawPluginApi`. Uses jiti (JavaScript Import Transform Interop) for module loading.

### Lifecycle

Plugin lifecycle (`src/plugins/loader.ts`):

1. **Discovery** -- From bundled dirs (`extensions/`), npm packages, git repos, local paths
2. **Manifest validation** -- `manifest.json5` with `id`, `version`, `capabilities`, `hooks`, `tools`, `entrypoints`
3. **Compatibility check** -- `min-host-version` enforcement
4. **Activation** -- Through `src/plugins/activation-planner.ts` which resolves dependency order
5. **Runtime tracking** -- Via `src/plugins/runtime.ts` tracking: active plugins, HTTP routes, session extensions, gateway methods, channel registrations

### Plugin Types

From `src/plugins/types.ts`:

- **Providers** -- LLM model providers (Anthropic, OpenAI, Google, etc.) with auth, model catalogs, streaming, replay policies
- **Channels** -- External platform adapters (Slack, Discord, etc.)
- **Skills** -- Agent capabilities (browser, file-transfer, web-search, etc.)
- **Hooks** -- Lifecycle hooks (before-agent-start, before-tool-call, etc.)
- **Capability providers** -- Feature providers (memory, document extraction, web fetching, etc.)
- **Embedding providers** -- Vector embedding providers

### Manifest System

The manifest system (`src/plugins/manifest.ts`, `src/plugins/manifest-types.ts`) validates and serves plugin manifests. The ClawHub marketplace (`src/plugins/clawhub.ts`, `src/plugins/marketplace.ts`) handles install/uninstall/update flows.

### Hook System

`src/plugins/hooks.ts` wires plugin hooks into agent execution phases:

- Before/after agent start
- Before/after tool call
- Before agent finalize
- Before install
- Compaction
- Message routing
- Decision making
- Correlation tracking

### Canonical Record Architecture

Plugins use a Canonical Install Record (CIR) system for tracking installed versions across migrations. The `src/plugins/canonical-record.ts` stores install provenance (source, version, install date) and is used for update detection and migration.

### Tool Plugin Pattern

`src/plugin-sdk/tool-plugin.ts`: `defineToolPlugin()` creates plugins that expose tools. Uses TypeBox schemas for input/output validation. Factory pattern with:

- `defineToolPlugin({ toolName, description, inputSchema, outputSchema, execute })`
- Automatic schema generation from TypeBox definitions
- Error handling and retry support

---

## State and Storage

State is stored in a dual SQLite database design, both using Kysely query builder with generated TypeScript types.

### Shared State Database

`src/state/openclaw-state-db.ts` (940 lines): `openclaw-state-db` -- global runtime state with tables for:

- Cron jobs (scheduling, execution tracking)
- Delivery queue entries (outbound channel message queue)
- Node pairing (paired nodes, capabilities)
- Sandbox registry (sandbox runtime status)
- Subagent runs (ACP subagent tracking)
- Task runs (async task tracking)
- Agent database registrations (links to per-agent DBs)
- Conversation bindings (session-to-channel mapping)
- ACP event ledger sessions and events
- Schema migrations (versioned, idempotent)

Uses 30-second busy timeout, synchronous WAL mode, private 0o600/0o700 file permissions.

### Per-Agent Database

`src/state/openclaw-agent-db.ts` (298 lines): `openclaw-agent-db` -- agent-scoped state with ownership assertion to prevent cross-agent access. Registers itself in the shared state's `agent_databases` table.

### Config Storage

JSON5 config file (`openclaw.json5`) with `$include` directives for modular composition. Loaded by `src/config/io.ts` (2984 lines):

1. Load `.env` files (process env, `./.env`, `~/.openclaw/.env`)
2. Resolve config path from env or default
3. Read file (JSON or JSON5), parse
4. Resolve `$include` chains (modular composition across files)
5. Apply `config.env` block to `process.env`
6. Resolve `${VAR}` env references
7. Strip shipped plugin install records (migrated to plugin index)
8. Validate against Zod schemas
9. Load shell env fallback if configured
10. Materialize runtime config

Config write safety: atomic file replace via temp file + rename, SHA256 hash-based conflict detection, backup rotation before writes, audit logging, `${VAR}` reference preservation, clobber protection.

### Secrets

`src/secrets/` stores sensitive values (API keys, tokens) with three reference types:

| Type | Syntax | Description |
|------|--------|-------------|
| Environment | `$env:VAR_NAME` | Read from environment variable |
| File | `$file:/path/to/secret` | Read from file |
| Exec | `$exec:command` | Execute command to resolve |

Resolved at runtime through the secrets runtime state (`src/secrets/runtime-state.ts`).

### OAuth and Auth Profiles

- Auth profiles stored per-agent in SQLite (newer installs) or `auth-profiles.json`
- Auth profile encryption keys stored in `~/.config/openclaw/` (separate Docker mountpoint for security)
- OAuth credentials in `~/.openclaw/credentials/oauth.json`

---

## Tool System

The tool system uses a descriptor-driven planning architecture. Core types in `src/tools/types.ts`.

### Tool Descriptors

- `ToolDescriptor` -- Name, description, input/output schemas (JSON Schema), owner reference, optional executor binding, availability expression, annotations
- `ToolOwnerRef` -- Classifies ownership: `core`, `plugin` (by pluginId), `channel` (by channelId + optional pluginId), `MCP server` (by serverId)
- `ToolExecutorRef` -- Resolved executor after planning: core executor, plugin tool, channel action, or MCP server tool
- `ToolAvailabilityExpression` -- Boolean tree of signals: `always`, `auth` (providerId), `config` (path + check type), `env` (var name), `plugin-enabled`, `context` (key + optional equals value), combined with `allOf`/`anyOf`
- `ToolPlan` -- Split into visible and hidden entries, with diagnostics explaining each hidden descriptor's unavailability

### Tool Planner

The planner (`src/tools/planner.ts`): `buildToolPlan()` sorts descriptors by `sortKey`, evaluates availability against runtime context, returns visible+hidden plan. Throws `ToolPlanContractError` on duplicate names or missing executors.

### Availability Evaluation

`src/tools/availability.ts` (186 lines): Evaluates each signal against a `ToolAvailabilityContext` containing auth provider IDs, config (JSON), env vars, enabled plugin IDs, and custom context values. `allOf` = all pass, `anyOf` = at least one passes.

### Gateway RPC Methods

The gateway protocol includes tool RPC methods:

- `tools.catalog` -- List available tools
- `tools.effective` -- See the effective (visibility-resolved) tool set
- `tools.invoke` -- Invoke tools

Built-in tools include browser, canvas, cron, nodes, sessions, and system tools.

---

## Gateway Protocol

The gateway protocol is a custom WebSocket RPC protocol defined in the `packages/gateway-protocol/` package. Current version is 4.

### Schema Validation

All frames and method params are validated against TypeBox-generated JSON schemas (`packages/gateway-protocol/src/schema/frames.ts`). Validators are lazily compiled (first call compiles, cached thereafter). The `ProtocolSchemas` registry at `packages/gateway-protocol/src/schema/protocol-schemas.ts` maps every schema name to its TypeBox definition.

### Method Surface

150+ RPC methods across categories:

| Category | Key Methods |
|----------|-------------|
| Sessions | create, send, list, describe, compact, abort, patch, reset, delete, steer, subscribe |
| Agents | create, update, delete, files, list |
| Chat | history, send, abort |
| Config | get, set, apply, patch, schema |
| Channels | status, start, stop, logout |
| Cron | list, add, remove, update, run |
| Devices | pair, approve, token |
| Nodes | pair, invoke, describe |
| Tools | catalog, effective, invoke |
| Skills | install, search, proposals, upload |
| Tasks | list, get, cancel |
| Health | health, diagnostics.stability |
| Model | list, authStatus, authLogout |
| Exec Approvals | approvals.*, approval.* |
| Talk | session.*, client.*, speak |
| Web push | push notifications |
| Wizard | start, next, status |

### Operator Scopes

Six scopes defined in `src/gateway/operator-scopes.ts`:

| Scope | Description |
|-------|-------------|
| `operator.admin` | Full administrative access |
| `operator.read` | Read-only access |
| `operator.write` | Write access |
| `operator.approvals` | Approval resolution |
| `operator.pairing` | Device/node pairing |
| `operator.talk.secrets` | Voice/video session secrets |

### HTTP Compatibility

Gateway also exposes OpenAI-compatible HTTP endpoints (`/v1/chat/completions`, `/v1/responses`, `/v1/models`, `/v1/embeddings`) and a custom `/tools/invoke` endpoint, authenticated through the same gateway auth system.

---

## UI and Live Canvas (A2UI)

The gateway includes a built-in web control UI served as an SPA at a configurable base path (default `/`). Implemented in `src/gateway/control-ui.ts` (dynamically imported to avoid startup cost).

### A2UI Protocol (v0.8)

The Live Canvas system (A2UI -- Agent-to-UI protocol) is implemented in the `canvas` extension. It uses a JSONL-based protocol where agents can create, update, and manage visual workspaces:

| RPC | Description |
|-----|-------------|
| `beginRendering` | Create a new surface (canvas workspace), returns surfaceId |
| `surfaceUpdate` | Update component properties on an existing surface |
| `dataModelUpdate` | Update the shared data model across components |
| `deleteSurface` | Remove a surface and all its components |

### Surface/Component Architecture

- **Surface**: A named canvas workspace with a unique ID. Can have multiple components rendered on it.
- **Component**: A visual element on a surface (text, chart, image, form, etc.). Has type, props, data bindings.
- **Data Model**: A shared state object that components can bind to for reactive updates.

### Controls

- Serves an HTML shell, static assets, agent identity info, and avatar images
- The control UI communicates with the gateway via the WebSocket RPC protocol for real-time updates
- Live canvas surfaces appear as interactive workspaces within the control UI

---

## Security Architecture

### Auth Rate Limiting

Per-IP failure tracking with:

- Configurable max failures per window
- Configurable retry-after duration
- Separate budgets for pre-connect (low) and post-connect (standard)

### Connection Budget

Pre-connection WebSocket upgrade requests are rate-limited to prevent DoS. The budget is distinct from the RPC auth rate limit.

### HTTP Security

- HSTS headers on all responses
- `no-new-privileges: true` security_opt in Docker
- Dropped capabilities: `NET_RAW`, `NET_ADMIN`
- Bearer token validation via constant-time comparison

### Operator Scopes

RPC methods require specific operator scopes. Scope model: `operator.read`, `operator.write`, `operator.admin`, `operator.approvals`, `operator.pairing`, `operator.talk.secrets`.

### TLS Support

- HTTPS via `createHttpsServer`
- Certificate configuration in `openclaw.json5`
- Tailscale integration for secure remote access without TLS configuration

---

## CLI Architecture

The CLI is built on the Commander library. Entry point is `src/entry.ts`, which handles compile cache, Windows argv normalization, container detection, and fast-paths for `--help` and `--version`.

### CLI Orchestration

Delegates to `src/cli/run-main.ts` `runCli()` (1097 lines) which orchestrates:

1. Container target detection
2. Environment normalization
3. Proxy bootstrap
4. Help fast-paths
5. Crestodian onboarding wizard
6. Commander program construction
7. Plugin command registration
8. Argument parsing and execution

Plugin commands are registered at startup from plugin manifests and registry snapshots. The `startupTrace.measure()` pattern profiles each phase.

### Key CLI Subcommands

- `openclaw gateway` -- start/stop/restart/manage the gateway daemon
- `openclaw agent` -- one-shot agent execution
- `openclaw message` -- send messages through channels
- `openclaw channels` -- manage channel plugins
- `openclaw plugins` -- manage plugin installation
- `openclaw config` -- read/write configuration
- `openclaw health` -- health probes
- `openclaw doctor` -- diagnostics and repair
- `openclaw backup` -- backup management
- `openclaw update` -- self-update
- `openclaw onboard` -- initial setup wizard
- `openclaw secrets` -- secret management
- `openclaw acp` -- start ACP protocol server
- `openclaw nodes` -- node operations
- `openclaw dev` -- developer utilities

---

## Talk System (Voice/Video)

The "Talk" system provides real-time voice/video sessions through its own protocol flow:

- **`TalkClient`** -- Client abstraction for connecting to talk sessions
- **`TalkSession`** -- Session management with audio streaming
- **TURN management** -- TURN server configuration for NAT traversal
- Gateway RPC methods: `talk.session.*`, `talk.client.*`, `talk.speak`

---

## Node and Device Pairing

### Node Pairing

OpenClaw supports a node network where remote nodes can be paired for distributed execution:

- Pairing protocol (`node.pair.*`) with request/approval flow
- Node capability advertisement
- Remote tool invocation (`node.invoke`)
- SSH tunnel proxy support for nodes behind NAT

### Device Pairing

Device management for companion devices (mobile, desktop):

- Pairing protocol (`device.pair.*`) with QR code or token
- Key-based device proof verification
- Push notification support

---

## Key Source Components

| File | Purpose |
|------|---------|
| `src/entry.ts` | Node.js entry point with fast-paths |
| `src/cli/run-main.ts` | CLI orchestration (Commander) |
| `src/gateway/server.impl.ts` | Gateway server implementation |
| `src/gateway/server.ts` | Lazy-loading server entry point |
| `src/gateway/server-http.ts` | HTTP server with stage-based routing |
| `src/gateway/server/ws-connection.ts` | WebSocket connection handler |
| `src/gateway/server/ws-connection/message-handler.js` | RPC method dispatch (dynamic import) |
| `src/gateway/server-ws-runtime.ts` | WebSocket runtime with tick/push/RPC channels |
| `src/gateway/server/ws-streaming.ts` | Streaming response handler |
| `src/gateway/session-lifecycle-state.ts` | Session lifecycle state machine |
| `src/gateway/auth-resolve.ts` | Connection authorization (token, password, proxy) |
| `src/gateway/auth-rate-limit.ts` | Per-IP auth rate limiting |
| `src/gateway/boot.ts` | BOOT.md workspace initialization |
| `src/gateway/control-ui.ts` | Built-in web control UI SPA |
| `src/gateway/server/readiness.ts` | Readiness probe checking |
| `src/gateway/server/health-state.ts` | Health snapshot building |
| `src/gateway/methods/core-descriptors.ts` | 150+ RPC method definitions |
| `src/gateway/method-scopes.ts` | Operator scope authorization |
| `src/gateway/operator-scopes.ts` | Scope definitions |
| `src/gateway/http-auth-utils.ts` | HTTP request auth utilities |
| `src/gateway/server-channels.ts` | Channel manager lifecycle |
| `src/gateway/server/event-loop-health-monitor.ts` | Event loop health monitoring |
| `src/daemon/gateway-entrypoint.ts` | Gateway startup sequence |
| `src/plugins/loader.ts` | Plugin discovery and loading |
| `src/plugins/runtime.ts` | Active plugin runtime registry |
| `src/plugins/hooks.ts` | Plugin lifecycle hook system |
| `src/plugins/activation-planner.ts` | Plugin activation planning |
| `src/plugins/manifest.ts` | Plugin manifest validation |
| `src/plugins/types.ts` | Plugin type definitions |
| `src/plugins/canonical-record.ts` | Canonical Install Record system |
| `src/plugin-sdk/core.ts` | Channel plugin SDK construction helpers |
| `src/plugin-sdk/plugin-entry.ts` | Plugin entry point definition |
| `src/plugin-sdk/tool-plugin.ts` | Tool plugin pattern with TypeBox |
| `src/channels/streaming.ts` | Streaming config normalization |
| `src/channels/resolve-route.ts` | Channel message routing |
| `src/state/openclaw-state-db.ts` | Shared SQLite state DB |
| `src/state/openclaw-agent-db.ts` | Per-agent SQLite DB |
| `src/config/io.ts` | Config file load/write with atomic safety |
| `src/tools/types.ts` | Tool descriptor and planning types |
| `src/tools/planner.ts` | Tool availability planner |
| `src/tools/availability.ts` | Availability signal evaluation |
| `src/agents/acp-spawn.ts` | ACP subagent spawning |
| `src/acp/server.ts` | ACP stdio/gateway bridge server |
| `src/acp/event-ledger.ts` | SQLite-backed ACP event audit trail |
| `src/mcp/channel-server.ts` | MCP server for channel bridge |
| `src/mcp/plugin-tools-serve.ts` | MCP server for plugin tools |
| `src/mcp/openclaw-tools-serve.ts` | MCP server for built-in tools |
| `src/secrets/runtime-state.ts` | Runtime secret resolution |
| `packages/gateway-protocol/src/index.ts` | Gateway RPC protocol types |
| `packages/gateway-protocol/src/schema/frames.ts` | Wire frame schemas |
| `packages/gateway-protocol/src/schema/protocol-schemas.ts` | Schema registry |
| `packages/gateway-protocol/src/version.ts` | Protocol version constants |
| `extensions/` | 85+ bundled plugins (providers, channels, skills) |

## Related

- [[openclaw.codegraph-verify]] -- Codegraph verification document

---

## Related

- [[domains/mcp/openclaw-mcp-implementation.md]] -- MCP integration implementation
- [[domains/acp/openclaw-acp-implementation.md]] -- ACP agent protocol implementation
- [[domains/api/openclaw-api.md]] -- REST and WebSocket API reference
- [[domains/deployment/openclaw-deployment.md]] -- Deployment and operations
- [[assets/mcp-servers/openclaw-mcp-server.md]] -- MCP server asset registration
- [[assets/acp-agents/openclaw-acp-agent.md]] -- ACP agent asset registration
- [[assets/deployment/openclaw-quadlet.md]] -- Quadlet deployment patterns
- [[assets/profiles/openclaw-profile.md]] -- Quick reference profile
- [[wiki/openclaw.md]] -- Wiki entry
