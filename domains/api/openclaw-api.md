---
name: openclaw-api
tags: [openclaw, api, typescript, agent-gateway, messaging, personal-assistant, live-canvas, rest-api, acp, ai-llm, automation, container, mcp, plugin-sdk, quadlet, security, systemd]
description: OpenClaw API Reference
---

# OpenClaw API Reference
**Source:** `sources/openclaw/`

OpenClaw runs a single HTTP/WebSocket gateway server on port 18789 by default (configurable via `--port`, `gateway.port`, or `OPENCLAW_GATEWAY_PORT`). It multiplexes HTTP, WebSocket, and HTTPS on the same port. The primary control plane is a WebSocket-based RPC protocol (version 4), supplemented by auxiliary HTTP endpoints for health, OpenAI compatibility, and automation.

## Table of Contents

- [Overview](#overview)
- [Health Endpoints](#health-endpoints)
- [Agent/Session API (WebSocket RPC)](#agentsession-api-websocket-rpc)
- [OpenAI-Compatible HTTP Endpoints](#openai-compatible-http-endpoints)
- [HTTP Auxiliary Endpoints](#http-auxiliary-endpoints)
- [Channel Management API](#channel-management-api)
- [Message API](#message-api)
- [ACP API](#acp-api)
- [MCP Integration Points](#mcp-integration-points)
- [Auth and Security](#auth-and-security)
- [WebSocket Streaming](#websocket-streaming)
- [Examples](#examples)
- [Key Source Files](#key-source-files)

---

## Overview

### Port and Transport

| Feature | Detail |
|---------|--------|
| Default port | `18789` |
| Primary protocol | WebSocket JSON-RPC (version 4) |
| HTTP endpoints | Health, OpenAI-compatible, tools, sessions |
| TLS | Yes, via `createHttpsServer` |
| API specification | TypeScript types + TypeBox schemas (no OpenAPI spec) |
| Bind modes | loopback, lan, tailnet, auto, custom |

The HTTP server is created in `src/gateway/server-http.ts` via `createGatewayHttpServer()`. WebSocket transport runs on the same server via WebSocket upgrade events.

---

## Health Endpoints

Health endpoints are defined in `GATEWAY_PROBE_STATUS_BY_PATH` at `server-http.ts`.

### Liveness

| Method | Path | Status | Response |
|--------|------|--------|----------|
| `GET` | `/health` | 200 | `{"ok":true,"status":"live"}` |
| `GET` | `/healthz` | 200 | `{"ok":true,"status":"live"}` |
| `HEAD` | `/health` | 200 | (no body) |
| `HEAD` | `/healthz` | 200 | (no body) |
| Other methods | any | 405 | Method not allowed |

### Readiness

| Method | Path | Status | Response |
|--------|------|--------|----------|
| `GET` | `/ready` | 200/503 | `{"ready":true\|false}` |
| `GET` | `/readyz` | 200/503 | `{"ready":true\|false}` |

Readiness details (which channel is failing, uptime) are only revealed to loopback callers or authenticated requests. Remote unauthenticated probes get a bare `{"ready":true|false}`.

**Headers** set on all probe responses: `Content-Type: application/json; charset=utf-8`, `Cache-Control: no-store`.

**Readiness is checked via** `createReadinessChecker()` (`src/gateway/server/readiness.ts`) evaluating:
- Channel health (per-account snapshots, stale-event thresholds, connect grace windows)
- Startup sidecar state
- Gateway draining state

#### curl Examples

```bash
# Liveness probe
curl http://localhost:18789/healthz    # {"ok":true,"status":"live"}

# Readiness probe
curl http://localhost:18789/readyz     # {"ready":true}

# HEAD request
curl -I http://localhost:18789/healthz
```

---

## Agent/Session API (WebSocket RPC)

The primary agent/session API is a **WebSocket-based RPC protocol**, not REST.

### Connection Flow

1. **Connect**: Establish WebSocket to `ws://gateway-host:18789`
2. **Handshake**: Send `ConnectParams` JSON frame with auth credentials
3. **Hello**: Receive `HelloOk` with negotiated protocol version, server info, available methods
4. **Communicate**: Send/receive JSON request/response/event frames

### Wire Frame Format

**Request:**
```json
{"type":"req","id":"r1","method":"sessions.list","params":{}}
```

**Successful response:**
```json
{"type":"res","id":"r1","ok":true,"payload":{...}}
```

**Error response:**
```json
{"type":"res","id":"r1","ok":false,"error":{"code":-32601,"message":"Method not found"}}
```

**Server push event:**
```json
{"type":"event","event":"chat","payload":{...},"seq":142}
```

### Protocol Version

- Current: `PROTOCOL_VERSION = 4`
- Minimum client: `4`

### Frame Limits

| Limit | Value |
|-------|-------|
| Pre-connect frames | 64 KB |
| Post-handshake max payload | 25 MB (configurable) |
| Max buffered bytes | Configurable via `hello-ok.policy.maxBufferedBytes` |

### Core RPC Methods

Each method requires specific operator scopes from the six-scope model: `operator.read`, `operator.write`, `operator.admin`, `operator.approvals`, `operator.pairing`, `operator.talk.secrets`.

#### Sessions

| Method | Scope | Description |
|--------|-------|-------------|
| `sessions.create` | write | Create a new session |
| `sessions.send` | write | Send message into existing session |
| `sessions.list` | read | List all sessions |
| `sessions.subscribe` | read | Subscribe to session events |
| `sessions.describe` | read | Get session details |
| `sessions.compact` | write | Compact a session |
| `sessions.abort` | write | Abort active session work |
| `sessions.patch` | write | Patch session properties |
| `sessions.reset` | write | Reset session state |
| `sessions.delete` | admin | Delete a session |
| `sessions.steer` | write | Interrupt-and-steer active session |

#### Agents

| Method | Scope | Description |
|--------|-------|-------------|
| `agents.list` | read | List all agents |
| `agents.create` | admin | Create a new agent |
| `agents.update` | admin | Update an agent |
| `agents.delete` | admin | Delete an agent |

#### Chat

| Method | Scope | Description |
|--------|-------|-------------|
| `chat.history` | read | Get chat history |
| `chat.send` | write | Send message to start/continue chat |
| `chat.abort` | write | Abort active chat |

#### Config

| Method | Scope | Description |
|--------|-------|-------------|
| `config.get` | admin/read | Get config value |
| `config.set` | admin | Set config value |
| `config.apply` | admin | Apply config changes |
| `config.patch` | admin | Patch config |
| `config.schema` | admin | Get config schema |

#### Tools

| Method | Scope | Description |
|--------|-------|-------------|
| `tools.catalog` | read | List available tools |
| `tools.effective` | read | Get effective (visibility-resolved) tool set |
| `tools.invoke` | write | Invoke a tool |

#### Channels

| Method | Scope | Description |
|--------|-------|-------------|
| `channels.status` | read | Get channel plugin status summaries |
| `channels.start` | admin | Start individual channels |
| `channels.stop` | admin | Stop individual channels |
| `channels.logout` | admin | Log out a specific channel/account |
| `web.login.start` | admin | Initiate QR/web login flow |
| `web.login.wait` | admin | Wait for login completion |

#### Other Method Categories

- `health`, `diagnostics.stability` -- system status
- `doctor.memory.*` (read/write) -- memory diagnostics
- `logs.tail` (read) -- log streaming
- `cron.*` (read/admin) -- cron job management
- `node.pair.*`, `node.list/describe` -- node operations
- `device.*` -- device pairing and token management
- `skills.*` (read/admin) -- skill management
- `tasks.*` (read/write) -- task tracking
- `wizard.*` (admin) -- setup wizard steps
- `talk.session.*`, `talk.client.*`, `talk.speak` (write) -- voice/video sessions
- `commands.list` (read) -- available commands
- `models.list`, `models.authStatus`, `models.authLogout` (read/admin)
- `exec.approvals.*`, `exec.approval.*`, `plugin.approval.*` (approvals)
- `gateway.identity.get`, `gateway.restart.*` (read/admin)

Full method reference: `docs/reference/rpc.md` and `docs/gateway/protocol.md` in the source tree.

### Server Push Events

Events are scope-gated. The server pushes:

| Event Pattern | Scope | Description |
|---------------|-------|-------------|
| `chat` | read | UI updates, delta text |
| `agent` | read | Streaming agent output |
| `session.message` | read | Session-scoped message events |
| `session.operation` | read | Session operations |
| `session.tool` | read | Tool execution events |
| `sessions.changed` | read | Session list changed |
| `presence` | read | User/agent presence |
| `tick` | read | Periodic keepalive (15s interval) |
| `health` | read | Health state changes |
| `heartbeat` | read | Connection heartbeat |
| `cron` | read | Cron job events |
| `shutdown` | read | Server shutting down |
| `node.pair.requested/resolved` | read | Node pairing |
| `node.invoke.request` | read | Node invocation |
| `device.pair.requested/resolved` | read | Device pairing |
| `voicewake.changed` | read | Voice wake word |
| `exec.approval.requested/resolved` | read | Execution approvals |
| `plugin.approval.requested/resolved` | admin/write | Plugin approvals |
| `update.available` | read | Software update available |

---

## OpenAI-Compatible HTTP Endpoints

The gateway exposes OpenAI-compatible endpoints for tool/IDE integration. These are **disabled by default** and require explicit configuration.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/models` | List available models |
| `GET` | `/v1/models/{id}` | Get model details |
| `POST` | `/v1/chat/completions` | Chat completions (streaming supported) |
| `POST` | `/v1/embeddings` | Get embeddings |
| `POST` | `/v1/responses` | OpenResponses API |

### Configuration

```json5
{
  gateway: {
    http: {
      endpoints: {
        chatCompletions: { enabled: true },
        responses: { enabled: true }
      }
    }
  }
}
```

### Authentication

Use the gateway bearer token as the API key:

```
Authorization: Bearer <gateway-token>
```

### SSE Streaming

When `stream: true` is sent, the response uses `Content-Type: text/event-stream` with `data: [DONE]` termination.

#### curl Example

```bash
curl http://localhost:18789/v1/chat/completions \
  -H "Authorization: Bearer $OPENCLAW_GATEWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": false
  }'
```

#### Python (OpenAI SDK) Example

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:18789/v1",
    api_key="your-gateway-token",
)

response = client.chat.completions.create(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": "Hello"}],
)
print(response.choices[0].message.content)
```

---

## HTTP Auxiliary Endpoints

### Tool Invocation

```http
POST /tools/invoke
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "web_search",
  "arguments": {"query": "latest AI news"}
}
```

- Max payload: 2 MB
- Always enabled (no config toggle required)
- Uses same auth model as WebSocket control plane

#### curl Example

```bash
curl -X POST http://localhost:18789/tools/invoke \
  -H "Authorization: Bearer $OPENCLAW_GATEWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "cron", "arguments": {"action": "list"}}'
```

### Session Kill

```http
POST /sessions/{sessionKey}/kill
Authorization: Bearer <token>
```

Terminates a session by its gateway session key.

### Session History

```http
GET /sessions/{sessionKey}/history
Authorization: Bearer <token>
```

Returns session history as JSON or SSE (when `Accept: text/event-stream` is sent).

---

## Channel Management API

Channel management is done via WebSocket RPC methods:

| Method | Scope | Description |
|--------|-------|-------------|
| `channels.status` | read | Returns built-in + bundled channel/plugin status summaries |
| `channels.start` | admin | Start individual channels |
| `channels.stop` | admin | Stop individual channels |
| `channels.logout` | admin | Log out a specific channel/account |
| `web.login.start` | admin | Initiate QR/web login flow |
| `web.login.wait` | admin | Wait for login completion |

### Channel Configuration

Channel configuration is managed through `config.set`/`config.patch` RPC methods and the `openclaw.json` config file. No dedicated HTTP REST endpoints for channel CRUD.

---

## Message API

### WebSocket RPC Methods

| Method | Scope | Description |
|--------|-------|-------------|
| `sessions.create` | write | Create a new session entry |
| `sessions.send` | write | Send a message into an existing session |
| `chat.send` | write | Send message to start or continue a chat |
| `chat.abort` | write | Abort active work for a session |
| `send` | write | Direct outbound-delivery RPC for channel/account/thread-targeted sends |
| `agent` | write | Start an agent run (optionally with `deliver=true`) |
| `agent.wait` | write | Wait for a run to finish and return the terminal snapshot |
| `sessions.steer` | write | Interrupt-and-steer variant for an active session |
| `message.action` | write | Handle message actions (buttons, interactive elements) |

---

## ACP API

The ACP (Agent Client Protocol) implementation lives in `src/acp/`. It uses the `@agentclientprotocol/sdk` npm package.

### Architecture

- **ACP server** (`src/acp/server.ts`): Runs as a stdio bridge. Spawns a `GatewayClient` connecting to the OpenClaw gateway over WebSocket, then translates ACP stdio JSON-RPC frames to gateway RPC calls.
- **ACP client** (`src/acp/client.ts`): Interactive stdio client that spawns the OpenClaw CLI with "acp" subcommand args and creates a `ClientSideConnection` using the ACP SDK.
- **ACP translator** (`src/acp/translator.ts`): Maps between ACP session lifecycle events and OpenClaw gateway events.
- **Control plane** (`src/acp/control-plane/`): Session management, policies, permission relay.
- **Event ledger** (`src/acp/event-ledger.ts`): SQLite-backed audit trail.

### Usage

```bash
# Start the ACP server
openclaw acp --url ws://localhost:18789

# Or pipe to an ACP-compatible client
openclaw acp | some-acp-client
```

### ACP Protocol RPCs

| RPC | Direction | Description |
|-----|-----------|-------------|
| `initialize` | Client -> Server | Version negotiation, capability handshake |
| `session/new` | Client -> Server | Create a new agent session |
| `session/load` | Client -> Server | Load existing session by ID |
| `session/resume` | Client -> Server | Resume a previously-saved session |
| `session/list` | Client -> Server | List active sessions |
| `session/close` | Client -> Server | Close a session |
| `session/prompt` | Client -> Server | Send a prompt to an agent session |
| `cancel` | Client -> Server | Cancel current in-flight prompt |
| `session/set_mode` | Client -> Server | Change session mode |
| `session/set_config_option` | Client -> Server | Set session config options |
| `sessionUpdate` | Server -> Client | Stream updates (agent messages, tool calls, etc.) |
| `requestPermission` | Server -> Client | Request user permission for a tool call |

For full details, see [[domains/acp/openclaw-acp-implementation.md]].

---

## MCP Integration Points

OpenClaw provides three MCP servers (see [[domains/mcp/openclaw-mcp-implementation.md]]):

| Server | Purpose | Transport |
|--------|---------|-----------|
| Channel Bridge | Bridges messaging channels | stdio |
| Plugin Tools | Exposes plugin-registered tools | stdio |
| OpenClaw Tools | Exposes built-in tools (cron) | stdio |

All three use `@modelcontextprotocol/sdk` v1.x with stdio transport only.

---

## Auth and Security

### Auth Modes

| Mode | Config Value | Mechanism |
|------|-------------|-----------|
| Token | `token` | `Authorization: Bearer <token>` header. Constant-time comparison via `safeEqualSecret` |
| Password | `password` | Shared secret on connect params |
| Trusted Proxy | `trusted-proxy` | Reverse proxy forwards identity headers |
| None | `none` | Skip auth entirely (private ingress only) |
| Tailscale | `allowTailscale` | Non-loopback connections via Tailscale WhoIs API |

### Auth Token

```bash
# Auto-generated if not set
# Or explicitly:
export OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)
```

### Auth Rate Limiting

Per-IP failure tracking with configurable thresholds and retry-after durations (see `src/gateway/auth-rate-limit.ts`).

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

### HTTP Auth

Auth for HTTP requests occurs via `src/gateway/http-auth-utils.ts`:

- `getBearerToken(request)` -- extract token from Authorization header
- `authorizeGatewayHttpRequestOrReply(request, reply)` -- validate and authorize
- `checkGatewayHttpRequestAuth(request)` -- check auth without sending response

---

## WebSocket Streaming

### Protocol Version 4

All communication after handshake is JSON text frames.

### Frame Types

```
Request:  {"type":"req", "id":"...", "method":"...", "params":{...}}
Response: {"type":"res", "id":"...", "ok":true, "payload":{...}}
Event:    {"type":"event", "event":"...", "payload":{...}, "seq":?, "stateVersion":?}
```

### SSE Streaming

Available for HTTP users via:
- OpenAI-compatible endpoints: `stream: true` on `POST /v1/chat/completions` or `POST /v1/responses`
- Session history endpoint: `Accept: text/event-stream`

### Tick Interval

Clients receive tick events based on `hello-ok.policy.tickIntervalMs` (default 15 seconds, server-advertised).

### WebSocket Implementation

- `src/gateway/server-ws-runtime.ts` -- WebSocket handler runtime with tick/push/RPC channels
- `src/gateway/server/ws-connection.ts` -- Connection lifecycle
- `src/gateway/server/ws-connection/message-handler.js` -- Dynamic RPC dispatch

---

## Examples

### TypeScript WebSocket Client

```typescript
const ws = new WebSocket("ws://localhost:18789");
const pending = new Map<string, { resolve, reject }>();
let seq = 0;

ws.on("open", () => {
  ws.send(JSON.stringify({
    type: "req", id: "connect", method: "connect",
    params: {
      protocolVersion: [4],
      auth: { token: process.env.OPENCLAW_GATEWAY_TOKEN },
    },
  }));
});

ws.on("message", (data) => {
  const frame = JSON.parse(data.toString());
  if (frame.type === "res") {
    const entry = pending.get(frame.id);
    if (entry) { entry.resolve(frame); pending.delete(frame.id); }
  } else if (frame.type === "event") {
    console.log("Server event:", frame.event, frame.payload);
  }
});

function call(method: string, params: object): Promise<any> {
  return new Promise((resolve, reject) => {
    const id = `req_${seq++}`;
    pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ type: "req", id, method, params }));
  });
}

const sessions = await call("sessions.list", {});
```

### Python WebSocket Client

```python
import json, asyncio, websockets

async def openclaw_rpc():
    async with websockets.connect("ws://localhost:18789") as ws:
        await ws.send(json.dumps({
            "type": "req", "id": "connect", "method": "connect",
            "params": {
                "protocolVersion": [4, 4],
                "auth": {"token": "your-gateway-token"},
                "client": {"displayName": "MyApp"},
            },
        }))
        hello = json.loads(await ws.recv())
        print("Connected:", hello["payload"]["serverInfo"])

        await ws.send(json.dumps({
            "type": "req", "id": "s1", "method": "sessions.list",
            "params": {},
        }))
        response = json.loads(await ws.recv())
        print("Sessions:", response)

asyncio.run(openclaw_rpc())
```

### Python Health Check

```python
import requests
r = requests.get("http://localhost:18789/healthz")
print(r.json())   # {"ok": true, "status": "live"}
r = requests.get("http://localhost:18789/readyz")
print(r.json())   # {"ready": true}
```

### OpenAI SDK Client Integration

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:18789/v1",
    api_key=open("/path/to/gateway-token.txt").read().strip(),
)

# Non-streaming
response = client.chat.completions.create(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": "Tell me a joke"}],
)
print(response.choices[0].message.content)

# Streaming
stream = client.chat.completions.create(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

---

## Key Source Files

| File | Purpose |
|------|---------|
| `src/gateway/server-http.ts` | HTTP server creation and stage routing |
| `src/gateway/auth.ts` | Auth modes and auth resolution |
| `src/gateway/auth-rate-limit.ts` | Per-IP rate limiting |
| `src/gateway/http-auth-utils.ts` | HTTP request auth utilities |
| `src/gateway/method-scopes.ts` | Operator scope authorization |
| `src/gateway/operator-scopes.ts` | Scope definitions |
| `src/gateway/server/ws-connection.ts` | WebSocket connection handler |
| `src/gateway/server/ws-connection/message-handler.js` | RPC method dispatch |
| `src/gateway/server-ws-runtime.ts` | WebSocket handler runtime |
| `src/gateway/server/health-state.ts` | Health snapshot building |
| `src/gateway/server/readiness.ts` | Readiness checking |
| `src/gateway/methods/core-descriptors.ts` | 150+ RPC method definitions |
| `packages/gateway-protocol/src/version.ts` | Protocol version constants |
| `packages/gateway-protocol/src/schema/frames.ts` | Wire frame TypeBox schemas |
| `packages/gateway-protocol/src/schema/protocol-schemas.ts` | Schema registry |
| `src/acp/server.ts` | ACP stdio server |
| `src/mcp/channel-server.ts` | MCP channel bridge server |
| `src/mcp/plugin-tools-serve.ts` | MCP plugin tools server |
| `src/mcp/openclaw-tools-serve.ts` | MCP built-in tools server |

## Related

- [[openclaw-acp-agent]] -- ACP agent asset registration
- [[openclaw-mcp-server]] -- MCP server asset configuration
- [[openclaw-quadlet]] -- Quadlet deployment patterns
- [[openclaw-profile]] -- Quick reference profile
- [[openclaw]] -- Main wiki entry

---

## Related

- [[domains/architecture/openclaw-architecture.md]] -- Gateway architecture
- [[domains/mcp/openclaw-mcp-implementation.md]] -- MCP integration implementation
- [[domains/acp/openclaw-acp-implementation.md]] -- ACP implementation
- [[domains/deployment/openclaw-deployment.md]] -- Deployment configuration
