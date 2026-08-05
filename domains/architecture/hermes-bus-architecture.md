---
name: hermes-bus-architecture
tags: [hermes-bus, architecture, hermes-agent, messaging, python, ipc, unix-socket]
description: Hermes Bus Architecture — Zero-dependency Python daemon for point-to-point Unix Domain Socket JSON routing with broadcast
source: sources/hermes-bus/
---

# Hermes Bus Architecture
**Source:** `sources/hermes-bus/`

Hermes Bus is the transport layer in the Hermes messaging ecosystem. It is a zero-dependency Python daemon that routes JSON messages between named endpoints over Unix Domain Sockets. The bus is transport-only — it moves messages without knowledge of audio, display, LLM contexts, or chat platforms. Routing is **point-to-point** (by named endpoint) plus an **empty-`to` broadcast** — it is **not** a pub/sub system (no topics, no subscriptions).

## Architecture

### Three-Layer Ecosystem

```
Layer 1: CLI            hermes-notify           injects messages into bus
Layer 2: Transport      hermes-bus              routes JSON over Unix sockets
Layer 3: Plugin         hermes-bus-plugin       terminal/LLM/command receivers
Layer 4: Gateway        downstream adapters     WeChat, Feishu, DingTalk replies
```

### Server-Client Model

Two Python modules implement the core:

| Module | Class | Role |
|--------|-------|------|
| `hermes_bus/server.py` | `BusServer` | Socket listener, session management, message routing, hook triggers, heartbeat pruning |
| `hermes_bus/client.py` | `BusClient` | Endpoint registration, auto-reconnect, auto-start daemon, heartbeat, thread-safe message queue |

`busd.py` provides daemon lifecycle: start/stop/status/restart with process management and diagnostics.

### Wire Protocol

All messages use a **4-byte big-endian length prefix** followed by a **UTF-8 JSON body** (max 10 MB payload):

```
+------------------+------------------------------------+
|  4 bytes (BE)    |  JSON body (up to 10 MB)           |
|  payload length  |  UTF-8 encoded                     |
+------------------+------------------------------------+
```

Framing is identical on both sides (`_recv_msg`/`_send_msg` in `server.py` and `client.py`); over-long payloads (>10 MB) are dropped.

### Message Types

| `type` | Direction | Description |
|--------|-----------|-------------|
| `register` | client -> server | Register as a named endpoint (carries `endpoint`) |
| `registered` | server -> client | Acknowledgement with `endpoint` + `session_id` |
| `ping` | client -> server | Heartbeat (every 60s on long-lived connections) |
| `pong` | server -> client | Heartbeat response (filtered from app layer) |
| `list_endpoints` | client -> server | Query connected endpoints |
| `endpoints_list` | server -> client | Response with `{endpoint: session_id}` map |
| `message` | bidirectional | Application message routed by `to` |
| `error` | server -> client | Failure reply, e.g. `code: "endpoint_not_found"` |

### Message Envelope

```json
{
  "type": "message", "id": "3f2c1b9e-8d44-4a1f-9c6e-0a2b3c4d5e6f",
  "to": "target-endpoint", "from": "sender-endpoint",
  "ts": 1716307200.123,
  "body": {"text": "Content", "type": "task_done", "channel": "feishu:oc_abc123"}
}
```

Envelope semantics (from source, not README):

- **Server-side routing** (`server.py:241-242`) adds exactly two fields via `setdefault`: `id` (a `uuid.uuid4()` string) and `ts` (float seconds). Existing client-provided values are preserved, never overwritten.
- **`from` is never set by the server.** Clients populate it: `BusClient.send()` uses the registered endpoint name (`client.py:298`); `send_message()` defaults to `"anonymous"` (`client.py:109`). An unset `from` stays unset.
- `body` passes through unmodified.

### Routing and State

- **`endpoint_map`** — `{name → session_id}` for O(1) route resolution
- **`sessions`** — `{session_id → {endpoint, socket, last_ping}}` connection tracking; `last_ping` refreshed on registration (`server.py:214`), on ping (`server.py:232`), and on every message (`server.py:239`)
- **Broadcast semantics** — only an **empty** `to` (`""`) broadcasts to all registered sessions (`server.py:300-306` `if not to_ep:`). A literal `"*"` is truthy → falls into endpoint lookup (`server.py:307`) → returns `endpoint_not_found` (`server.py:315-324`), it does NOT broadcast
- **`error` reply** — anonymous senders whose target is unconnected receive `{"type": "error", "code": "endpoint_not_found", "detail": ..., "id": ...}`; registered senders route with no reply socket, so unmatched messages are dropped silently
- **Kick-old re-registration** — registering an endpoint name already in `endpoint_map` closes the old session's socket, evicts it from `sessions`/`endpoint_map`, and replaces the mapping (`server.py:199-216`)
- Anonymous connections never appear in either map; broadcast via `"to": ""`
- Long-lived clients: `BusClient("name")` → register → poll (registered in map)
- Short-lived: `send_message()` → connect → send → close (anonymous); returns `False` on `error` reply or connect failure

### Auto-start, Auto-reconnect and Hooks

- **Auto-start daemon** — on connect failure, both `send_message()` (`client.py:96-104`) and `BusClient.connect()` (`client.py:244-251`) call `_start_bus_server()` (`client.py:138-178`), which probes the socket (connect test, 0.5s timeout), unlinks stale socket files, spawns `hermes-busd start`, and waits up to 2s for the socket. Public helper: `ensure_bus_running()` (`client.py:436-438`)
- **Auto-reconnect** — clients retry with exponential backoff (1s initial, 30s max, ×1.5 growth); on success the delay resets to 1s (`client.py:356-386`)
- **Heartbeat** — client pings every 60s (`client.py:33,423`); server prunes sessions idle > 90s, checked every 15s (`server.py:38-40,331-349`)
- **Hooks** — run asynchronously after each route; resolved from `HERMES_BUS_HOOKS` env var or `$HERMES_HOME/hermes-bus/hooks.yaml`

### Socket Hardening

- **chmod `0o600`** — the socket file is restricted to the owning user at bind time (`server.py:139`)
- **SIGPIPE ignored** — a client disconnect cannot kill the server via SIGPIPE (`server.py:143`)

### Daemon Lifecycle

| Phase | Behavior |
|-------|----------|
| start | Clean stale socket, spawn `BusServer`, wait ≤3s; log at `run/busd.log` with 500 KB in-place rotation |
| stop | SIGTERM → ~4.5s (15 × 0.3s) grace → SIGKILL, clean PID + socket |
| status | PID check, socket check, responsiveness test, endpoint query, diagnostics, log tail |
| restart | stop then start |

Configuration: `HERMES_BUS_ROOT` (~/.hermes, socket + run dir), `HERMES_HOME` (~/.hermes, config home), `HERMES_BUS_HOOKS` (comma-separated or JSON array of hook paths).

Diagnostics on failure: `pgrep -f hermes_bus.server` process count, socket mtime staleness (>300s), PID/socket consistency, last 50 log lines scanned for error keywords (traceback, connectionreset, brokenpipe, timeout, oserror, memory, permission, file not found, bind, address already, sigkill, sigterm, killed), plus log tail.

## Key Components

| File | Purpose |
|------|---------|
| `hermes_bus/server.py` | BusServer — listener, routing, hooks, pruning |
| `hermes_bus/client.py` | BusClient — registration, reconnect, auto-start, message queue |
| `hermes_bus/busd.py` | Daemon manager — start/stop/status/restart |

## Related

- [[hermes-bus]] — Wiki entry
- [[hermes-agent]] — Core Hermes agent
- [[hermes-workspace]] — Hermes workspace manager
- [[hermes-plugins]] — Hermes plugin system
