---
name: openclaw-acp-agent
tags: [openclaw, acp-agent, typescript, agent-gateway, messaging, personal-assistant, live-canvas, acp, ai-llm, automation, cli, container, git, mcp, plugin-sdk, quadlet, security, storage, systemd]
description: OpenClaw ACP Agent
---

# OpenClaw ACP Agent
**Source:** `sources/openclaw/`

Asset file for registering OpenClaw as an ACP (Agent Communication Protocol) agent with Claude Code, Cursor, Windsurf, and other ACP-compatible clients.

## Agent Identity

| Property | Value |
|----------|-------|
| Protocol | Agent Client Protocol (ACP) |
| Framework | `@agentclientprotocol/sdk` |
| Transport | stdio with NDJSON (JSON-RPC-style message framing) |
| Entry point | `openclaw acp` or `src/acp/server.ts` |
| SDK version | Latest from `@agentclientprotocol/sdk` |
| Protocol version | Negotiated at initialize (server reports `PROTOCOL_VERSION`) |

---

## Registration for Claude Code

### Method 1: `claude acp add` Command

```bash
claude acp add openclaw -- openclaw acp
```

### Method 2: `~/.claude/settings.json`

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

### Method 3: Custom Server Path

```json
{
  "acpServers": {
    "openclaw": {
      "command": "node",
      "args": ["--import", "tsx", "/path/to/openclaw/src/acp/server.ts"]
    }
  }
}
```

### Method 4: With Gateway URL

```json
{
  "acpServers": {
    "openclaw": {
      "command": "openclaw",
      "args": ["acp", "--url", "ws://localhost:18789"]
    }
  }
}
```

### Method 5: With Token File

```json
{
  "acpServers": {
    "openclaw": {
      "command": "openclaw",
      "args": ["acp", "--token-file", "/path/to/gateway-token"]
    }
  }
}
```

### Method 6: Cursor IDE

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

### Method 7: Windsurf IDE

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

### Available Commands (26 base commands)

The ACP server advertises the following commands via `sessionUpdate.available_commands_update`:

**Core:** `help`, `commands`, `status`

**Information:** `context` (list/detail/json), `whoami`, `id`

**Management:** `subagents`, `config` (owner-only), `debug` (owner-only)

**Session Control:** `stop`, `restart`, `reset`, `new`

**Mode Switches:** `think` (off/minimal/low/medium/high/xhigh), `verbose` (on/full/off), `trace`, `reasoning`, `elevated`, `model`

**Behavior:** `activation` (mention/always), `send` (on/off/inherit), `usage` (off/tokens/full), `queue`, `bash`, `compact`

Plus plugin-registered `dock:` commands discovered at runtime.

---

## Interaction Patterns

### Pattern 1: Direct ACP Client (REPL)

```bash
openclaw acp
```

Launches an interactive REPL that:
1. Spawns the ACP server as a child process
2. Creates an ACP client session using `ClientSideConnection` from the SDK
3. Presents a prompt for user input
4. Streams responses and tool calls to stdout/stderr
5. Auto-approves safe tools (`readonly_scoped`, `readonly_search`)
6. Prompts for approval of exec/control-plane/mutating tools

### Pattern 2: Claude Code Integration

Register as an ACP agent in `~/.claude/settings.json` (see above). Claude Code then treats OpenClaw as an available agent for task delegation.

### Pattern 3: IDE Integration (Cursor, Windsurf)

Any ACP-compatible IDE can connect to OpenClaw's ACP server using methods 6 or 7 above.

### Pattern 4: Programmatic Server Embedding

```typescript
import { serveAcpGateway } from "openclaw/src/acp/server.js";

serveAcpGateway({
  gatewayUrl: "ws://localhost:18789",
  gatewayToken: process.env.OPENCLAW_GATEWAY_TOKEN,
});
```

### Pattern 5: Session Replay

Use the SQLite event ledger for session replay:

```typescript
const ledger = createSqliteAcpEventLedger({ db: openclawDb });
const replay = await ledger.readReplayBySessionKey("agent:main:acp:session-1");
```

---

## Security

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
1. `_meta.toolName`
2. `rawInput.tool` / `rawInput.toolName` / `rawInput.name`
3. Title prefix (text before `": "`)

If any source disagrees or has an invalid name, the tool is classified as `unknown` (fails closed).

### Environment Sanitization

When the ACP server spawns the Gateway bridge, provider auth env vars are stripped:
- `OPENAI_API_KEY`, `GITHUB_TOKEN`, `HF_TOKEN`
- Active-skill env keys
- `OPENCLAW_SHELL=acp-client` is set as a marker

---

## Event Ledger

All session interactions are recorded in the SQLite-backed event ledger:

| Table | Purpose |
|-------|---------|
| `acp_replay_sessions` | Session metadata |
| `acp_replay_events` | Individual events with sequence numbers |

### Retention

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

### Lifecycle Methods

| Method | Description |
|--------|-------------|
| `startSession()` | Creates a new ledger session entry |
| `recordUserPrompt()` | Records the initial user prompt as an event |
| `recordUpdate()` | Records a session update |
| `markIncomplete()` | Marks a session as incomplete |
| `readReplay()` | Reads back all events for replay |

---

## Known Limitations

1. **No outbound ACP client** -- OpenClaw cannot act as a client to other ACP servers (like Hermes). It is a server-only implementation.
2. **Plugin tool approval over ACP bridge** -- Plugin tools report approval requirements as errors rather than opening approval flows.
3. **Single-process design** -- The ACP server is a single Node.js process; large-scale concurrent session handling is limited by process resources.
4. **Multi-backend failover** requires runtime backends contributed by plugins.

---

## ACP Server CLI Flags

The ACP server (`openclaw acp`) supports these flags for advanced configuration:

| Flag | Description |
|------|-------------|
| `--url` | Gateway WebSocket URL |
| `--token` | Gateway auth token |
| `--token-file` | Read token from file |
| `--password` | Gateway auth password |
| `--password-file` | Read password from file |
| `--session` | Session ID to load on connect |
| `--require-existing` | Fail if session doesn't exist |
| `--reset-session` | Reset session on connect |
| `--no-prefix-cwd` | Disable CWD prefixing |
| `--provenance` | Provenance mode: off/meta/meta+receipt |
| `--verbose` | Verbose logging |

## Related

- [[openclaw-profile]] -- Quick reference profile
- [[openclaw-mcp-server]] -- MCP server asset configuration (companion protocol)
- [[openclaw-quadlet]] -- Quadlet deployment patterns
- [[openclaw-deployment]] -- Full deployment guide
- [[openclaw]] -- Main wiki entry

---

## Related

- [[domains/acp/openclaw-acp-implementation.md]] -- Comprehensive ACP implementation document
- [[domains/mcp/openclaw-mcp-implementation.md]] -- MCP integration (related companion protocol)
- [[domains/architecture/openclaw-architecture.md]] -- Gateway and agent system
- [[domains/api/openclaw-api.md]] -- API reference
- [[domains/acp/hermes-acp-implementation.md]] -- Hermes ACP implementation (interop reference)
