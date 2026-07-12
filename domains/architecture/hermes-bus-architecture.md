---
name: hermes-bus-architecture
tags: [hermes-bus, architecture, hermes-agent, messaging, python, ipc, unix-socket, pub-sub]
description: Hermes Bus Architecture — Zero-dependency Python daemon for Unix Domain Socket IPC and JSON pub/sub messaging
source: sources/hermes-bus/
---

# Hermes Bus Architecture
**Source:** `sources/hermes-bus/`

Hermes Bus is the transport layer in the Hermes messaging ecosystem. It is a zero-dependency Python daemon that routes JSON messages between named endpoints over Unix Domain Sockets. The bus is transport-only — it moves messages without knowledge of audio, display, LLM contexts, or chat platforms.

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
| `hermes_bus/client.py` | `BusClient` | Endpoint registration, auto-reconnect, heartbeat, thread-safe message queue |

`busd.py` provides daemon lifecycle: start/stop/status/restart with process management and diagnostics.

### Wire Protocol

All messages use a **4-byte big-endian length prefix** followed by a **UTF-8 JSON body** (max 10 MB payload):

```
+------------------+------------------------------------+
|  4 bytes (BE)    |  JSON body (up to 10 MB)           |
|  payload length  |  UTF-8 encoded                     |
+------------------+------------------------------------+
```

### Message Envelope

Five message types: `register`, `registered`, `ping`/`pong` (heartbeat 55s interval, 90s timeout), `list_endpoints`/`endpoints_list`, and `message`. The envelope:

```json
{
  "type": "message", "to": "target-endpoint", "from": "sender-endpoint",
  "ts": 1716307200.123,
  "body": {"text": "Content", "type": "task_done", "channel": "feishu:oc_abc123"}
}
```

The bus adds `from` (if unset) and `ts`. `body` passes through unmodified.

### Routing and State

- **`endpoint_map`** — `{name → session_id}` for O(1) route resolution
- **`sessions`** — `{session_id → {endpoint, socket, last_heartbeat}}` connection tracking
- Anonymous connections never appear in either map; broadcast via `"to": ""` or `"to": "*"`
- Re-registration evicts the old session gracefully
- Long-lived clients: `BusClient("name")` → register → poll (registered in map)
- Short-lived: `send_message()` → connect → send → close (anonymous)

### Auto-reconnect and Hooks

Clients retry with exponential backoff (1s initial, 30s max). Server prunes after 90s inactivity. Hook scripts run asynchronously after each route — resolved from `HERMES_BUS_HOOKS` env var or `~/.hermes/hermes-bus/hooks.yaml`.

### Daemon Lifecycle

| Phase | Behavior |
|-------|----------|
| start | Clean stale socket, spawn `BusServer`, wait ≤3s |
| stop | SIGTERM → 5s grace → SIGKILL, clean PID + socket |
| status | PID check, socket check, responsiveness test, log tail |
| restart | stop then start |

Configuration: `HERMES_BUS_ROOT` (~/.hermes, socket dir), `HERMES_HOME` (~/.hermes, config home), `HERMES_BUS_HOOKS` (comma-separated or JSON array of hook paths).

## Key Components

| File | Purpose |
|------|---------|
| `hermes_bus/server.py` | BusServer — listener, routing, hooks, pruning |
| `hermes_bus/client.py` | BusClient — registration, reconnect, message queue |
| `hermes_bus/busd.py` | Daemon manager — start/stop/status/restart |

## Related

- [[hermes-bus]] — Wiki entry
- [[hermes-agent]] — Core Hermes agent
- [[hermes-workspace]] — Hermes workspace manager
- [[hermes-plugins]] — Hermes plugin system
