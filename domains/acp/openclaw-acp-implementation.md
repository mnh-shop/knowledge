---
name: openclaw-acp-implementation
tags: [acp, agent-gateway, ai-llm, cli, git, live-canvas, mcp, messaging, openclaw, personal-assistant, plugin-sdk, quadlet, security, systemd, typescript]
description: OpenClaw ACP Implementation
---

# OpenClaw ACP Implementation
**Source:** `sources/openclaw/`

OpenClaw implements the Agent Client Protocol (ACP) as a stdio-based bridge that connects ACP-compatible clients to the OpenClaw Gateway. This document details the architecture, protocol surface, security model, and implementation of the ACP server.

---

## Architecture Overview

The ACP implementation uses the `@agentclientprotocol/sdk` npm package and consists of three main components:

| Component | Source | Purpose |
|-----------|--------|---------|
| **ACP Server** | `src/acp/server.ts` | Stdio-to-Gateway bridge. Spawns a `GatewayClient` connecting to the OpenClaw Gateway over WebSocket, translates ACP stdio JSON-RPC frames to Gateway RPC calls. |
| **ACP Client** | `src/acp/client.ts` | Interactive stdio client. Spawns the OpenClaw CLI with "acp" subcommand args and creates a `ClientSideConnection` using the ACP SDK. |
| **ACP Translator** | `src/acp/translator.ts` | Maps between ACP session lifecycle events and OpenClaw Gateway events. |

### Data Flow

```
ACP Client <-> stdio <-> ACPServer <-> GatewayClient <-> WebSocket <-> OpenClaw Gateway

ACP Client (via SDK ClientSideConnection)
  <-> stdio <-> openclaw acp CLI <-> ACPServer (via AgentSideConnection)
```

---

## ACP Server Implementation (`src/acp/server.ts`)

The ACP server is the core of OpenClaw's ACP surface. It runs as a stdio process that bridges between the ACP protocol and the Gateway's internal WebSocket RPC protocol.

### SDK Integration

Uses `AgentSideConnection` from `@agentclientprotocol/sdk` to implement the ACP server side. Communication happens over stdio with NDJSON (JSON-RPC-style message framing).

### CLI Flags

The ACP server is launched via `openclaw acp` with these flags:

| Flag | Description |
|------|-------------|
| `--url` | Gateway WebSocket URL (default: auto-resolved from credentials) |
| `--token` | Gateway auth bearer token |
| `--token-file` | Read gateway token from file |
| `--password` | Gateway auth password |
| `--password-file` | Read gateway password from file |
| `--session` | Session ID to load on connect |
| `--session-label` | Label for new sessions |
| `--require-existing` | Fail if specified session does not exist |
| `--reset-session` | Reset session state on connect |
| `--no-prefix-cwd` | Disable CWD prefixing in session context |
| `--provenance` | Provenance mode: `off`, `meta`, or `meta+receipt` |
| `--verbose` | Verbose logging |

### Session Lifecycle

1. Server starts, reads flags and config
2. Connects to Gateway via WebSocket (`GatewayClient`)
3. Advertises ACP capabilities on `initialize`
4. Routes incoming ACP RPCs to Gateway methods
5. Forwards Gateway events back as ACP session updates
6. On shutdown, closes Gateway connection cleanly

### Protocol Version Normalization

The ACP server normalizes the ACP `initialize` protocol version for MCP client compatibility. This allows ACP clients that expect specific version formats to interoperate with OpenClaw's Gateway protocol versioning.

---

## ACP Client Implementation (`src/acp/client.ts`)

The ACP client provides an interactive REPL that:

1. Spawns the ACP server as a child process
2. Creates an ACP client session using `ClientSideConnection` from the ACP SDK
3. Presents a prompt for user input
4. Streams responses and tool calls to stdout/stderr
5. Auto-approves safe tools (`readonly_scoped`, `readonly_search`)
6. Prompts for approval of `exec`/`control-plane`/`mutating` tools

### Usage

```bash
openclaw acp
```

Launches the interactive REPL connecting to the local gateway.

---

## Protocol Surface

### Session Lifecycle RPCs

| RPC | Direction | Description |
|-----|-----------|-------------|
| `initialize` | Client -> Server | Version negotiation, capability handshake |
| `session/new` | Client -> Server | Create a new agent session |
| `session/load` | Client -> Server | Load an existing session by ID |
| `session/resume` | Client -> Server | Resume a previously-saved session |
| `session/list` | Client -> Server | List active sessions |
| `session/close` | Client -> Server | Close a session |
| `session/prompt` | Client -> Server | Send a prompt to an agent session |
| `cancel` | Client -> Server | Cancel the current in-flight prompt |
| `session/set_mode` | Client -> Server | Change session mode |
| `session/set_config_option` | Client -> Server | Set session configuration options |
| `authenticate` | Client -> Server | Authenticate the connection |

### Streaming Notifications (Server -> Client)

| Notification | Description |
|--------------|-------------|
| `sessionUpdate` | Stream updates: agent messages, tool calls, thought chunks, config changes, available commands |

### Permission Flow

| Message | Direction | Description |
|---------|-----------|-------------|
| `requestPermission` | Server -> Client | Request user permission for a tool call |
| Permission response | Client -> Server | Options: `allow_once`, `reject_once`, `allow_always`, `reject_always` |

### Capabilities Advertised

| Capability | Value |
|------------|-------|
| `loadSession` | `true` |
| `imageSupport` | `true` |
| `sessionListing` | `true` |
| `resume` | `true` |

---

## Session Management

### Session Modes

| Mode | Description |
|------|-------------|
| `interactive` | Normal interactive mode with tool approvals |
| `background` | Runs autonomously without user interaction prompts |
| `batch` | Batch processing mode, no streaming |

### Available Commands

The ACP server advertises 26 base commands via `sessionUpdate.available_commands_update`:

**Core:** `help`, `commands`, `status`

**Information:** `context` (list/detail/json), `whoami`, `id`

**Management:** `subagents`, `config` (owner-only), `debug` (owner-only)

**Session Control:** `stop`, `restart`, `reset`, `new`

**Mode Switches:** `think` (off/minimal/low/medium/high/xhigh), `verbose` (on/full/off), `trace`, `reasoning`, `elevated`, `model`

**Behavior:** `activation` (mention/always), `send` (on/off/inherit), `usage` (off/tokens/full), `queue`, `bash`, `compact`

Plus plugin-registered `dock:` commands discovered at runtime.

---

## Event Ledger

All ACP session interactions are recorded in a SQLite-backed event ledger (`src/acp/event-ledger.ts`).

### Data Model

```typescript
interface LedgerStore {
  sessions: LedgerSession[];
}

interface LedgerSession {
  sessionId: string;     // ACP session ID
  sessionKey: string;    // Gateway session key
  cwd: string;           // Working directory at session start
  complete: boolean;     // Whether session has ended
  createdAt: string;     // ISO timestamp
  updatedAt: string;     // ISO timestamp
  nextSeq: number;       // Next event sequence number
  events: LedgerEvent[];
}

interface LedgerEvent {
  seq: number;           // Monotonic sequence within session
  at: string;            // ISO timestamp
  sessionId: string;
  sessionKey: string;
  runId: string;
  update: unknown;       // The ACP sessionUpdate payload
}
```

### Retention Limits

| Limit | Default |
|-------|---------|
| Max sessions | 200 |
| Max events per session | 5000 |
| Max total storage | 16 MB |

### Replay API

| Method | Description |
|--------|-------------|
| `readReplay(sessionId, sessionKey)` | Full replay by ID + key |
| `readReplayBySessionId(sessionId)` | Replay by session ID only |
| `readReplayBySessionKey(sessionKey)` | Most recent complete session by Gateway key |

### Ledger Lifecycle

- `startSession()` -- Creates a new ledger session entry
- `recordUserPrompt()` -- Records the initial user prompt as an event
- `recordUpdate()` -- Records a session update (agent response, tool call, etc.)
- `markIncomplete()` -- Marks a session as incomplete (interrupted)
- `readReplay()` -- Reads back all events for replay

---

## Control Plane

The control plane (`src/acp/control-plane/`) manages session lifecycle across the ACP bridge:

- **Session management**: Create, load, resume, close sessions
- **Policy enforcement**: Approval policies, tool classification
- **Permission relay**: Forwards permission requests from the Gateway to the ACP client

### Approval Classifier

The ACP approval classifier (`src/acp/approval-classifier.ts`) determines whether agent actions need human approval:

- Uses tool metadata, ownership, and action type to classify
- Supports `always`, `threshold`, and `contextual` approval rules
- Wired into the ACP permission flow

---

## Security Model

### Tool Approval Classification

When a tool call requires permission, the server classifies it:

| Class | Auto-Approved | Examples |
|-------|---------------|----------|
| `readonly_scoped` | Yes | `read` targeting paths inside CWD |
| `readonly_search` | Yes | `search`, `web_search`, `memory_search` |
| `mutating` | No | Write/modify operations |
| `exec_capable` | No | Shell, exec, bash, process tools |
| `control_plane` | No | Cron, gateway, session management |
| `other` | No | Known tool, not safe |
| `unknown` | No (fails closed) | Unresolvable tool name (spoofing detected) |

### Spoofing Detection

The server cross-references three identity sources for every tool call:

1. `_meta.toolName` -- Canonical tool name from metadata
2. `rawInput.tool` / `rawInput.toolName` / `rawInput.name` -- Raw input variations
3. Title prefix (text before `": "`) -- Display name prefix

If any source disagrees or has an invalid name, the tool is classified as `unknown` (fails closed).

### Environment Sanitization

When the ACP server spawns the Gateway bridge, provider auth env vars are stripped:

- `OPENAI_API_KEY`, `GITHUB_TOKEN`, `HF_TOKEN`
- Active-skill env keys
- `OPENCLAW_SHELL=acp-client` is set as a marker

### Gateway Authentication

The ACP server authenticates to the Gateway using one of:

- Bearer token (from flag, file, or environment)
- Password (from flag or file)
- Auto-resolved from `~/.openclaw/credentials/`

---

## Interaction Patterns

### Pattern 1: Direct ACP Client (REPL)

```bash
openclaw acp
```

Launches an interactive REPL that connects to the local gateway. Provides a prompt for user input with streaming responses and tool call handling.

### Pattern 2: Claude Code Integration

Register as an ACP agent in `~/.claude/settings.json`:

```json
{
  "acpServers": {
    "openclaw": {
      "command": "openclaw",
      "args": ["acp"]
    }
  }
}
```

### Pattern 3: IDE Integration (Cursor, Windsurf)

```json
{
  "agentServers": {
    "openclaw": {
      "command": "openclaw",
      "args": ["acp"]
    }
  }
}
```

### Pattern 4: Programmatic Server Embedding

```typescript
import { serveAcpGateway } from "openclaw/src/acp/server.js";

serveAcpGateway({
  gatewayUrl: "ws://localhost:18789",
  gatewayToken: process.env.OPENCLAW_GATEWAY_TOKEN,
});
```

### Pattern 5: Session Replay

```typescript
const ledger = createSqliteAcpEventLedger({ db: openclawDb });
const replay = await ledger.readReplayBySessionKey("agent:main:acp:session-1");
```

---

## Known Limitations

1. **No outbound ACP client** -- OpenClaw cannot act as a client to other ACP servers (like Hermes). It is a server-only implementation.
2. **Plugin tool approval over ACP bridge** -- Plugin tools report approval requirements as errors rather than opening approval flows.
3. **Single-process design** -- The ACP server is a single Node.js process; large-scale concurrent session handling is limited by process resources.
4. **Multi-backend failover** requires runtime backends contributed by plugins.
5. **Session replay is append-only** -- Events cannot be deleted or modified after recording.

---

## Key Source Files

| File | Purpose |
|------|---------|
| `src/acp/server.ts` | ACP stdio-to-Gateway bridge server |
| `src/acp/client.ts` | Interactive ACP client REPL |
| `src/acp/translator.ts` | Mappings between ACP events and Gateway events |
| `src/acp/event-ledger.ts` | SQLite-backed event audit trail |
| `src/acp/approval-classifier.ts` | Tool classification for permission decisions |
| `src/acp/control-plane/` | Session management and policy enforcement |
| `src/acp/commands.ts` | ACP command definitions |
| `src/acp/conversation-id.ts` | Stable conversation identity across sessions |
| `src/acp/control-plane/control-plane-connection.ts` | Gateway ACP control plane connection |
| `src/agents/acp-spawn.ts` | ACP subagent spawning from Gateway agents |

## Related

- [[openclaw-profile]] -- Quick reference profile
- [[openclaw-mcp-server]] -- MCP server asset configuration (companion protocol)
- [[openclaw-quadlet]] -- Quadlet deployment patterns
- [[openclaw-deployment]] -- Full deployment guide
- [[openclaw]] -- Main wiki entry

---

## Related

- [[domains/architecture/openclaw-architecture.md]] -- Gateway architecture and agent system
- [[domains/mcp/openclaw-mcp-implementation.md]] -- MCP integration (companion protocol)
- [[assets/acp-agents/openclaw-acp-agent.md]] -- ACP agent asset registration
- [[domains/api/openclaw-api.md]] -- API reference
- [[domains/acp/hermes-acp-implementation.md]] -- Hermes ACP implementation (interop reference)
# OpenClaw ACP Implementation

OpenClaw implements the Agent Communication Protocol (ACP) as a bidirectional bridge between ACP-compatible clients (IDEs, Claude Code, Cursor) and the OpenClaw Gateway. The implementation lives at `src/acp/` and spans approximately 71 files across the ACP runtime, session management, commands, and plugin integration.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Approval Classifier](#approval-classifier)
- [Event Ledger](#event-ledger)
- [Control Plane](#control-plane)
- [Client Protocol](#client-protocol)
- [Command Definitions](#command-definitions)
- [Hermes ACP Compatibility](#hermes-acp-compatibility)
- [Integration Patterns](#integration-patterns)

---

## Architecture Overview

### Directory Structure

```
src/acp/
  server.ts                          -- ACP stdio server (NDJSON over stdin/stdout)
  client.ts                          -- Interactive stdio ACP client (terminal REPL)
  translator.ts                      -- Core AcpGatewayAgent implementing ACP Agent interface
  approval-classifier.ts             -- Tool call risk classification and auto-approval
  event-ledger.ts                    -- Persistent SQLite-backed audit trail
  policy.ts                          -- Config-driven gates (enable/disable, dispatch, allowed agents)
  permission-relay.ts                -- Bridges Gateway exec.approval events to ACP permission protocol
  commands.ts                        -- Available command list for ACP clients
  client-helpers.ts                  -- Client-side permission resolution helpers
  control-plane/
    manager.ts / manager.core.ts     -- AcpSessionManager singleton (orchestrates sessions)
    manager.types.ts                 -- Shared ACP session management types
    active-turns.ts                  -- Global signal registry for in-flight turns
    manager.initialize-session.ts    -- Session creation on runtime backends
    manager.turn-runner.ts           -- Full turn execution lifecycle with failover
    manager.turn-stream.ts           -- Coordinated event + result stream consumption
    manager.turn-timeout.ts          -- Timeout handling with grace period
    manager.backend-failover.ts      -- Multi-backend failover logic
    manager.runtime-controls.ts      -- Apply persisted runtime options to sessions
    manager.runtime-options-commands.ts -- Handlers for setSessionMode, etc.
    manager.runtime-handle-cache.ts  -- LRU-like cache with idle TTL eviction
    manager.runtime-resume-state.ts  -- Handle resume/recovery after backend failures
    manager.background-task.ts       -- Mirror child ACP turns as background tasks
    manager.cancel-session.ts        -- Session cancellation logic
    manager.close-session.ts         -- Session close with cleanup
    manager.identity-reconcile.ts    -- Identity synchronization between session and runtime
    session-actor-queue.ts           -- Per-session async serialization (KeyedAsyncQueue)
    runtime-options.ts               -- Normalization/validation for runtime options
    spawn.ts                         -- Cleanup helpers for partially-created sessions
```

### Transport

- **ACP protocol**: stdio with NDJSON (JSON-RPC-style message framing)
- **Gateway internal**: WebSocket-based JSON-RPC
- The ACP server bridges between ACP stdio and Gateway WebSocket

### Protocol API Surface

ACP RPCs (from the `@agentclientprotocol/sdk` contract):

| RPC | Description |
|-----|-------------|
| `initialize` | Protocol version negotiation, capability handshake |
| `session/new` | Create a new agent session |
| `session/load` | Load an existing session by ID |
| `session/resume` | Resume a previously-saved session |
| `session/list` | List active sessions |
| `session/close` | Close a session |
| `session/prompt` | Send a prompt to an agent session |
| `cancel` | Cancel the current in-flight prompt |
| `session/set_mode` | Change session mode (interactive/background/batch) |
| `session/set_config_option` | Set session configuration options |
| `authenticate` | Authenticate the connection |

---

## Approval Classifier

**File:** `src/acp/approval-classifier.ts`

Classifies ACP tool permission requests into one of 10 risk classes and determines auto-approval behavior.

### Function

`classifyAcpToolApproval(toolCall, cwd) -> AcpApprovalClass`

Takes:
- `toolCall.title` -- human-readable title
- `toolCall._meta` -- metadata including tool name
- `toolCall.rawInput` -- raw input including tool/name fields
- `cwd` -- current working directory for path scoping

### Risk Classes (`AcpApprovalClass`)

| Class | Auto-Approved? | Description |
|-------|---------------|-------------|
| `readonly_scoped` | Yes | `read` tool targeting a path inside CWD |
| `readonly_search` | Yes | search tools (`search`, `web_search`, `memory_search`) from core tool catalog |
| `mutating` | No | Any tool identified as mutating via `isMutatingToolCall()` |
| `exec_capable` | No | exec/spawn/shell/bash/process/code_execution/nodes -- never auto-approved |
| `control_plane` | No | cron/gateway/sessions_spawn/sessions_send/session_status |
| `interactive` | N/A | Reserved (not matched in current classification) |
| `other` | No | Readable known tool but not safe, not exec, not control-plane |
| `unknown` | No | Tool name could not be resolved (fails closed) |

### Spoofing Detection

The `resolveToolNameForPermission` function fuses three identity sources:

1. `toolCall._meta.toolName`
2. `toolCall.rawInput.tool` / `toolCall.rawInput.toolName` / `toolCall.rawInput.name`
3. Title prefix (text before `": "`)

Returns `undefined` (unknown) if:
- Any identity source has an invalid name (>128 chars, non-alphanumeric/dot/underscore/hyphen)
- Sources disagree (meta says A, title says B, rawInput says C)

This prevents a tool from claiming to be `search` in metadata while actually running `exec`.

### Path Scoping

`isReadToolCallScopedToCwd` resolves the target path from rawInput or the title tail (after `": "`) and checks whether it resolves inside the CWD using `isPathInside`. Supports `file://` URIs, `~` expansion, absolute and relative paths.

---

## Event Ledger

**File:** `src/acp/event-ledger.ts`

A tamper-resistant audit trail for ACP session interactions. Records every event for replay and compliance.

### Backends

| Backend | Factory | Use Case |
|---------|---------|----------|
| In-memory | `createInMemoryAcpEventLedger()` | Tests and ephemeral runtimes |
| SQLite | `createSqliteAcpEventLedger()` | Production (shared `state/openclaw.sqlite` database) |

### Tables

- `acp_replay_sessions` -- session metadata
- `acp_replay_events` -- individual events with sequence numbers

### Key Operations

| Operation | Description |
|-----------|-------------|
| `startSession(sessionId, sessionKey, cwd, complete, reset)` | Begin tracking a session |
| `recordUserPrompt(sessionId, sessionKey, runId, prompt[])` | Record user prompts as `user_message_chunk` events |
| `recordUpdate(sessionId, sessionKey, runId, update)` | Record SessionUpdate (agent messages, tool calls, config changes) |
| `markIncomplete(sessionId, sessionKey)` | Mark session as incomplete (partial event recording) |
| `readReplay(sessionId, sessionKey)` | Read full replay by session ID + key |
| `readReplayBySessionId(sessionId)` | Read replay by session ID only |
| `readReplayBySessionKey(sessionKey)` | Read most recent complete session for a Gateway session key |

### Retention Policy

| Limit | Default | Behavior |
|-------|---------|----------|
| `maxSessions` | 200 | Oldest sessions evicted when exceeded |
| `maxEventsPerSession` | 5000 | Oldest events trimmed per session |
| `maxSerializedBytes` | 16 MB | Total storage limit, evicts oldest events/sessions |

### Legacy Migration

`migrateFileAcpEventLedgerToSqlite` imports from legacy JSON file (`state/acp/event-ledger.json`) into SQLite, then archives the source. Runs at ACP server startup.

### Key Design Detail

Sessions are identified by both `sessionId` (ACP client-facing UUID) and `sessionKey` (Gateway-internal routing key). The ledger properly handles the pattern where a provisional session key (e.g. `acp:gateway-session-1`) becomes a canonical Gateway key (e.g. `agent:main:acp:gateway-session-1`) by matching on the latter's session key.

---

## Control Plane

**Directory:** `src/acp/control-plane/`

The `AcpSessionManager` is a process-wide singleton orchestrating ACP sessions, runtime handles, and turn execution. It sits between the ACP protocol translator and configurable runtime backends contributed by OpenClaw plugins.

### AcpSessionManager API

| Method | Description |
|--------|-------------|
| `resolveSession(sessionId)` | Resolve a session resolution (none/stale/ready) |
| `initializeSession(input)` | Create session on a runtime backend |
| `getSessionStatus(sessionId)` | Get current session status |
| `setSessionRuntimeMode(id, mode)` | Change session mode |
| `setSessionConfigOption(id, option)` | Set a config option on the session |
| `updateSessionRuntimeOptions(id, opts)` | Update runtime options |
| `resetSessionRuntimeOptions(id)` | Reset to default options |
| `runTurn(input)` | Execute a full turn |
| `cancelSession(id)` | Cancel active turn + runtime cancel |
| `closeSession(input)` | Full close with optional state discard |
| `reconcilePendingSessionIdentities()` | Reconcile identities after drift |
| `getObservabilitySnapshot()` | Get metrics and state snapshot |

### Session Resolution (`AcpSessionResolution`)

A discriminated union:

- `{ type: "none" }` -- no session found
- `{ type: "stale", meta }` -- session exists but runtime handle is stale
- `{ type: "ready", session }` -- session is active and ready

### Turn Execution Flow (`manager.turn-runner.ts`)

1. Build ordered, deduped backend list (primary + resolved primary + configurable fallbacks)
2. Iterate through backend candidates with up to 2 retry attempts each
3. Ensure runtime handle: `runtime.ensureSession()`
4. Apply runtime controls (model, thinking, timeout, etc.)
5. Consume turn stream via `consumeAcpTurnStream`
6. Handle timeout detection with `awaitTurnWithTimeout`
7. Background task mirroring for spawned child sessions
8. Post-turn cleanup (runtime handle reconciliation, oneshot-mode close)

### Backend Failover

`manager.backend-failover.ts`:

- Builds ordered, deduped backend list from configured primary, resolved primary metadata, and `acp.fallbacks` config
- `isFailoverWorthyBackendError` checks for transient errors: unavailable, rate-limited, quota exhausted, overloaded -- with no output seen

### Runtime Handle Cache

`manager.runtime-handle-cache.ts`:

- Process-local LRU-like cache for live `AcpRuntimeHandle` instances
- Supports idle TTL eviction (configurable via `acp.idleTtlMs`)
- Health checks via `getStatus`
- Handle-to-meta matching for stale detection

### Per-Session Serialization

`session-actor-queue.ts`:

- `KeyedAsyncQueue` ensures ACP operations for the same session execute sequentially
- Tracks pending count per session for observability

### Background Task Mirroring

`manager.background-task.ts`:

- Mirrors child ACP spawn turns into detached "background tasks" visible to the requester session
- Captures progress text (bounded to 240 characters)
- Detects terminal outcomes ("Permission denied" = blocked, writable session required, etc.)

---

## Client Protocol

**File:** `src/acp/client.ts`

An interactive stdio ACP client for connecting a terminal to an OpenClaw ACP server.

### How It Works

1. Resolves the server command (prefers dist-built entry point, falls back to `openclaw` on PATH)
2. Sanitizes environment: strips provider auth env vars (`OPENAI_API_KEY`, `GITHUB_TOKEN`, `HF_TOKEN`) and active-skill env keys so credentials don't leak
3. Spawns the ACP server as a child process with stdio pipes
4. Creates an NDJSON stream (Writeable -> child stdin, Readable <- child stdout)
5. Builds a `ClientSideConnection` with two callbacks:
   - `sessionUpdate`: prints text chunks to stdout, tool status to stderr, available commands
   - `requestPermission`: delegates to `resolvePermissionRequest` which auto-approves safe tools or prompts the user via stdin readline (30-second timeout, y/N)
6. Initializes the connection with `PROTOCOL_VERSION` and client capabilities (fs read/write, terminal)
7. Creates a new ACP session
8. Enters a readline REPL: user types prompts, sent via `client.prompt()`, responses streamed

### Client Capabilities Advertised

- `fs.readTextFile`
- `fs.writeTextFile`
- `terminal` support

### Permission Resolution (`client-helpers.ts`)

1. Calls `classifyAcpToolApproval` from `approval-classifier.ts`
2. Auto-approves: `readonly_scoped` reads, `readonly_search` tools
3. Prompts for: exec, control-plane, mutating, other, unknown
4. Sanitizes tool titles before display (strips ANSI escape codes and control characters)
5. Falls back to non-interactive denial when no TTY is available

### Environment Sanitization

- Provider auth env vars are stripped only when spawning the default OpenClaw bridge (not for custom ACP servers)
- Active-skill env keys are always stripped
- `OPENCLAW_SHELL=acp-client` is set as a marker

---

## Command Definitions

**File:** `src/acp/commands.ts`

Builds the `available_commands` list exposed to ACP clients via `sessionUpdate.available_commands_update`.

### Base Commands (26 commands)

**Core:**
- `help` -- Show available commands
- `commands` -- List available commands
- `status` -- Show session status

**Information:**
- `context` (list|detail|json) -- View session context
- `whoami` / `id` -- Show agent identity

**Management:**
- `subagents` -- Manage subagents
- `config` (owner-only) -- View configuration
- `debug` (owner-only) -- Debug tools

**Session Control:**
- `stop` -- Stop current execution
- `restart` -- Restart session
- `reset` / `new` -- Reset session state

**Mode Switches:**
- `think` (off/minimal/low/medium/high/xhigh) -- Reasoning effort
- `verbose` (on/full/off) -- Verbosity level
- `trace` -- Enable tracing
- `reasoning` -- Enable reasoning mode
- `elevated` -- Elevate permissions
- `model` -- Switch model

**Behavior:**
- `activation` (mention|always) -- Activation trigger
- `send` (on/off/inherit) -- Send mode
- `usage` (off/tokens/full) -- Usage display
- `queue` -- Queue management
- `bash` -- Bash mode
- `compact` -- Compact session

### Plugin Commands

`listDockAvailableCommands()` discovers plugin-registered `dock:` commands from the chat commands registry and maps their text aliases + descriptions into the ACP command list.

### Integration Point

Used by `getAvailableCommands()` which `AcpTranslatorSessionUpdates.sendAvailableCommands` calls after session creation and after mode/config changes. These represent the user-facing `/` slash commands available in OpenClaw channels, translated to ACP's `AvailableCommand` format.

---

## Hermes ACP Compatibility

Both OpenClaw and Hermes implement the same standard **Agent Client Protocol** from `@agentclientprotocol/sdk`, so the wire protocol is compatible. However, practical interop faces structural barriers.

### What They Share (Wire Protocol Compatibility)

- Same transport: stdio with NDJSON
- Same session lifecycle RPCs: initialize, newSession, loadSession, resumeSession, listSessions, closeSession, prompt, cancel
- Same streaming protocol: server pushes `sessionUpdate` notifications (agent_message_chunk, tool_call, tool_call_update, user_message_chunk, etc.)
- Same permission flow: `requestPermission` with allow_once/reject_once/allow_always/reject_always option kinds
- Same config controls: setSessionMode, setSessionConfigOption
- Both advertise `loadSession=true`, image support, session listing, and resume capabilities

### What Differs

| Dimension | OpenClaw | Hermes |
|-----------|----------|--------|
| Backend integration | Bridges to Gateway (WebSocket multi-agent routing) | Bridges to AIAgent (Python, ThreadPoolExecutor 4 workers) |
| Replay/ledger | SQLite event ledger with session rehydration | Lineage tracking via `session_info_update._meta.hermes.sessionProvenance` |
| Backend failover | Multi-backend failover with configurable fallbacks | Single-backend |
| Proxy/services | No outbound ACP client to third-party agents | Copilot ACP client for GitHub Copilot |
| Session management | Full control plane with per-session async queues, idle TTL eviction, rate limiting, observability | Simpler in-process SessionManager backed by AIAgent state |

### Can They Talk to Each Other?

At the protocol level, yes -- both implement the same ACP specification using the same SDK. But in practice:

1. Both are *server* implementations (ACP Agents). They wait for incoming connections. Neither is a generic ACP client to an arbitrary peer.
2. OpenClaw's `client.ts` is an interactive terminal-based client that spawns *its own* `openclaw acp` server as a child process -- it is not a general-purpose ACP client for connecting to arbitrary ACP servers like Hermes.
3. Hermes has an ACP client (`agent/copilot_acp_client.py`) but it is specifically designed to talk to GitHub Copilot's ACP, not a generic peer.

### True Interop Would Require One Of:

1. Implement an ACP client in one system that connects to the other's ACP server via stdio or a forwarder process
2. Pipe the two together: have the agent output channeled through an ACP adapter on one end of a stdio pair, and an ACP gateway agent on the other
3. Build a common routing layer that both register with

**Verdict**: Protocol-compatible but architecturally not designed for direct interop. The most viable path would be implementing an ACP client wrapper in one system that spawns the other's ACP server as a subprocess.

---

## Integration Patterns

### Pattern 1: External ACP Client (Claude Code, Cursor)

```json
// ~/.claude/settings.json
{
  "acpServers": {
    "openclaw": {
      "command": "openclaw",
      "args": ["acp"]
    }
  }
}
```

### Pattern 2: Terminal ACP Client

```bash
openclaw acp --url ws://localhost:18789
```

Launches the interactive REPL client connected to a local Gateway.

### Pattern 3: Custom ACP Bridge

The ACP server (`src/acp/server.ts`) provides `serveAcpGateway()` which can be embedded into custom Node.js processes to bridge MCP protocol to OpenClaw agents.

### Pattern 4: Programmatic Session Control

```typescript
import { serveAcpGateway } from "./src/acp/server.js";

// Start ACP server with custom options
serveAcpGateway({
  gatewayUrl: "ws://localhost:18789",
  gatewayToken: process.env.OPENCLAW_GATEWAY_TOKEN,
  // Session management options
});
```

---

## Related

- [[domains/architecture/openclaw-architecture.md]] -- Gateway and agent system architecture
- [[domains/mcp/openclaw-mcp-implementation.md]] -- MCP integration (related companion protocol)
- [[assets/acp-agents/openclaw-acp-agent.md]] -- ACP agent asset file
- [[domains/acp/hermes-acp-implementation.md]] -- Hermes ACP implementation (interop reference)

---

