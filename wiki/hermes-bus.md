---
name: hermes-bus
tags: [cli, hermes-agent, developer-tools, event-bus, messaging, monitoring, agent, python, hermes-bus]
description: "Unix Socket IPC daemon that routes JSON messages between endpoints in the Hermes ecosystem"
source: sources/hermes-bus/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Hermes Bus -- Message Transport Layer

| Field | Value |
|---|---|
| **Origin** | [mlinquan/hermes-bus](https://github.com/mlinquan/hermes-bus) |
| **License** | MIT |
| **Stack** | Python 3.10+, Unix Domain Sockets |
| **Source** | `sources/hermes-bus/` |
| **Repomix** | `raw/hermes-bus/hermes-bus.xml` |
| **Version** | 0.7.0 |
| **Wanted** | Zero-dependency message bus for inter-process JSON routing within the Hermes agent ecosystem |

## What it is

Hermes Bus is the **transport layer** in the [Hermes] messaging ecosystem. It is a zero-dependency Python daemon that routes JSON messages between named endpoints over Unix Domain Sockets. The bus is transport-only -- it knows nothing about audio, display, LLM contexts, or chat platforms. It just moves messages. Routing is **point-to-point** (by named endpoint) with an **optional broadcast** (empty `to`); it is not a pub/sub system with topics.

The ecosystem follows a three-part chain: **notify -> bus -> plugin**.

| Layer | Package | Role |
|---|---|---|
| 1 -- CLI | **hermes-notify** | CLI senders (`notify-hermes`, `notify-agent`) inject messages into the bus or tmux sessions |
| 2 -- Transport | **hermes-bus** | Route JSON messages between endpoints via Unix Socket |
| 3 -- Plugin | **hermes-bus-plugin** | Receive-side agent plugin: print to terminal, LLM context injection, command execution, channel routing |
| 4 -- Gateway | *(downstream)* | Platform adapters (WeChat, Feishu, WeCom, DingTalk) deliver replies to end users |

## Key Features

- **Zero dependencies** -- pure Python 3.10+, no external packages required
- **Unix Domain Socket IPC** -- low-latency local inter-process communication; socket chmod `0o600` and SIGPIPE ignored server-side
- **Named endpoint registration** -- long-lived connections register with a name; messages route by name; re-registering a name kicks the old session
- **Anonymous senders** -- short-lived connections send one message and disconnect without polluting the endpoint map; unknown targets get an `error` reply
- **Heartbeat keep-alive** -- 60s client heartbeat, 90s server timeout; stale connections are pruned
- **Auto-reconnect** -- clients retry connection with exponential backoff (1s initial, 30s max, ×1.5 growth)
- **Auto-start daemon** -- if the bus is not running, `BusClient`/`send_message()` boot it via `hermes-busd start`
- **Broadcast support** -- messages with an **empty** `"to"` (`""`) are delivered to all registered endpoints; a literal `"*"` is NOT a wildcard (it falls through to endpoint lookup and returns `endpoint_not_found`)
- **Post-route hook scripts** -- async subprocess hooks triggered after each message is routed
- **Session isolation** -- `HERMES_BUS_ROOT` (socket location) separates from `HERMES_HOME` (config); multiple profiles share one daemon
- **Thread-safe message queue** -- `BusClient` uses `queue.Queue` so consumers can poll on any thread
- **Bilingual docs** -- README.md + README.zh.md

## Architecture

```
client.py ---- Unix Socket ---- server.py
  (BusClient)                    (BusServer)
   - Register endpoint           - Session management
   - Heartbeat (60s)             - Message routing
   - Auto-reconnect              - Hook triggers
   - Auto-start daemon           - Kick old on re-register
   - Thread-safe message queue

busd.py -- Daemon manager: start / stop / status / restart
```

### Wire Protocol

All messages use a **4-byte big-endian length prefix** followed by a **UTF-8 JSON body**. Maximum payload is 10 MB.

```
+------------------+------------------------------------+
|  4 bytes (BE)    |  JSON body (up to 10 MB)           |
|  payload length  |  UTF-8 encoded                     |
+------------------+------------------------------------+
```

### Message Types

| `type` | Direction | Description |
|---|---|---|
| `register` | client -> server | Register as a named endpoint (carries `endpoint`) |
| `registered` | server -> client | Registration acknowledgement with `endpoint` + `session_id` |
| `ping` | client -> server | Heartbeat (every 60s on long-lived connections) |
| `pong` | server -> client | Heartbeat response (not surfaced to the app layer) |
| `list_endpoints` | client -> server | Request connected endpoint list |
| `endpoints_list` | server -> client | Response with `{endpoint: session_id}` map |
| `message` | bidirectional | Application message routed by `to` field |
| `error` | server -> client | Failure reply, e.g. `code: "endpoint_not_found"` when an anonymous sender targets an unconnected endpoint |

### Message Envelope

```json
{
  "type": "message",
  "id": "3f2c1b9e-8d44-4a1f-9c6e-0a2b3c4d5e6f",
  "to": "target-endpoint",
  "from": "sender-endpoint",
  "ts": 1716307200.123,
  "body": {
    "text": "Human-readable message content",
    "type": "task_done",
    "channel": "feishu:oc_abc123"
  }
}
```

The **server** only ever adds `id` (a `uuid.uuid4()` string) and `ts` (float seconds) -- via `setdefault`, so pre-existing values are left untouched. `from` is **never** set by the server; clients set it themselves (`BusClient.send()` uses the registered endpoint name; `send_message()` defaults to `"anonymous"`). An unset `from` stays unset. `body` is passed through unmodified.

### State Management

- **`endpoint_map`** -- `{endpoint_name -> session_id}` for O(1) route resolution
- **`sessions`** -- `{session_id -> {endpoint, socket, last_ping}}` for connection tracking; `last_ping` is refreshed on registration, on ping, and on every message
- Anonymous (short-lived) connections never appear in either map, preventing map pollution
- Re-registration with the same endpoint name evicts the old session gracefully ("kick old" -- old socket closed, map entry replaced)

## Interfaces

### CLI

Two entry points registered via `pyproject.toml`:

| Command | Entry | Description |
|---|---|---|
| `hermes-busd {start\|stop\|status\|restart}` | `hermes_bus.busd:main` | Daemon lifecycle management |
| `hermes-bus-server` | `hermes_bus.server:main` | Run bus server in foreground (debugging) |

### Python API

```python
from hermes_bus.client import BusClient, send_message, ensure_bus_running

# Long-lived: register as an endpoint and receive messages
client = BusClient("my-service")
client.connect()   # auto-starts the daemon if the socket is absent
for msg in client.poll():
    print(msg)

# Short-lived: fire-and-forget
send_message("target-service", {"text": "hello", "type": "ack"})

# Ensure daemon is up without connecting (useful at boot)
ensure_bus_running()
```

If the bus is not running, both `BusClient.connect()` and `send_message()` invoke `_start_bus_server()` (client.py), which spawns `hermes-busd start` and waits up to 2s for the socket to appear.

### Hooks

After routing, hook scripts run asynchronously (non-blocking). Resolution order:

1. `HERMES_BUS_HOOKS` env var (comma-separated path list or JSON array)
2. Config file `$HERMES_HOME/hermes-bus/hooks.yaml`
3. Default: none

Each hook receives the full message JSON on stdin.

## Configuration

| Variable | Default | Description |
|---|---|---|
| `HERMES_BUS_ROOT` | `~/.hermes` | Bus socket directory (`hermes-bus.sock`), run directory (`run/`) with `busd.pid` + `busd.log` |
| `HERMES_HOME` | `~/.hermes` | Hermes config home (profile-scoped); does NOT affect bus socket location |
| `HERMES_BUS_HOOKS` | (none) | Comma-separated or JSON array of hook script paths |

All profiles share one `hermes-busd` daemon. Profile endpoint naming: `<profile>-gateway` (e.g., `work` -> `work-gateway`).

## Daemon Lifecycle

- **start** -- cleans stale socket, spawns `BusServer` via `subprocess.Popen`, waits up to 3s for socket to appear; server chmods the socket `0o600` and ignores SIGPIPE
- **stop** -- sends SIGTERM, waits ~4.5s (15 × 0.3s) for graceful shutdown, force-kills with SIGKILL if needed, cleans up PID file and stale socket
- **status** -- checks PID file, socket existence, server responsiveness, prints diagnostics and log tail on failure
- **restart** -- stop then start
- **log rotation** -- log at `$HERMES_BUS_ROOT/run/busd.log`, rotated in-place when it exceeds 500 KB (keeps the tail half)

Diagnostics on failure (`busd.py` `_diagnose_disconnect`) include: process tree inspection via `pgrep -f hermes_bus.server`, socket file staleness by mtime age, last 50 log lines scanned for error keywords (traceback, connectionreset, brokenpipe, timeout, oserror, memory, permission, file not found, bind, address already, sigkill, sigterm, killed), and a log tail.

## Files

| Path | Purpose |
|---|---|
| `hermes_bus/server.py` | `BusServer` -- socket listener, session management, message routing, hook triggers, heartbeat pruning |
| `hermes_bus/client.py` | `BusClient` -- endpoint registration, auto-reconnect, auto-start, heartbeat, thread-safe message queue + `send_message()` static helper |
| `hermes_bus/busd.py` | Daemon manager -- `start`/`stop`/`status`/`restart` with diagnostics |
| `hermes_bus/hooks.yaml` | Hook script configuration (default empty) |
| `pyproject.toml` | Package metadata, Python 3.10+, console script entry points |
| `README.md` / `README.zh.md` | Bilingual documentation (English + Simplified Chinese) |

## Related

[[hermes-agent]], [[hermes-agent-docker]], [[hermes-suite]], [[hermes-startup-architect]], [[hermes-workspace]]
