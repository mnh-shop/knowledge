---
name: hermes-bus-codegraph-verify
tags: [hermes-bus, codegraph-verify, hermes-agent, messaging, python, ipc, unix-socket]
description: "Codegraph Verification: Hermes Bus — validating wiki claims against indexed source code symbols"
source: sources/hermes-bus/
---

# Codegraph Verification: Hermes Bus

**Date:** 2026-07-12

## Claim 1: Zero-dependency Python daemon (Python ≥3.10)
- **Wiki says:** Hermes Bus is a zero-dependency Python daemon for Unix Domain Socket IPC. Requires Python 3.10+ with no external packages.
- **Source evidence:**
  - `pyproject.toml:8-9` — `requires-python = ">=3.10"` and `dependencies = []` (empty — zero external packages)
  - `pyproject.toml:36` — Build system: `setuptools` + `wheel` only (standard library)
  - Entire package consists of 4 Python files (`__init__.py`, `server.py`, `client.py`, `busd.py`) plus `hooks.yaml` — no imports from outside stdlib
  - `pyproject.toml:28-30` — Entry points registered as console scripts: `hermes-bus-server`, `hermes-busd`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Unix Domain Socket IPC with 4-byte big-endian length prefix protocol
- **Wiki says:** Uses AF_UNIX sockets with a 4-byte big-endian length prefix followed by UTF-8 JSON body. Maximum payload 10 MB.
- **Source evidence:**
  - `server.py:136` — `sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)` (Unix socket creation)
  - `client.py:40-68` — `_recv_msg()` reads 4-byte header: `header = b""; while len(header) < 4: chunk = sock.recv(4 - len(header))` then `struct.unpack(">I", header)[0]` for length
  - `client.py:71-77` — `_send_msg()` encodes: `header = struct.pack(">I", len(data))` then `sock.sendall(header + data)`
  - `server.py:353-383` — `_recv_msg()` uses same 4-byte framing: `struct.unpack(">I", header)[0]`
  - Both files define `MAX_PAYLOAD_BYTES = 10 * 1024 * 1024` (10 MB) — `server.py:37`, `client.py:32`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Named endpoint registration with anonymous senders
- **Wiki says:** Long-lived connections register with a name and appear in the endpoint map. Short-lived (anonymous) connections send one message and disconnect without polluting the map.
- **Source evidence:**
  - `server.py:115-116` — `self.sessions: dict[str, dict[str, Any]] = {}` and `self.endpoint_map: dict[str, str] = {}` for tracking `{endpoint_name -> session_id}`
  - `server.py:197-224` — Registration handler creates `session_id` (uuid), stores in `self.sessions[session_id]` with endpoint name, socket, and `last_ping`
  - `server.py:110` — Comment: "Short-lived: send message directly, no registration, no endpoint_map entry."
  - `client.py:82-129` — `send_message()` static function: connects, sends one message, disconnects without registering
  - `busd.py:69-99` — `_is_socket_alive()` uses `list_endpoints` (not `register`) specifically to avoid polluting the endpoint map
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Heartbeat keep-alive (60s client, 90s server timeout)
- **Wiki says:** Client heartbeat at 60s interval, server timeout at 90s, stale connections are pruned.
- **Source evidence:**
  - `server.py:38-40` — `HEARTBEAT_INTERVAL = 60`, `HEARTBEAT_TIMEOUT = 90`, `HEARTBEAT_CHECK_EVERY = 15`
  - `server.py:331-349` — `_heartbeat_check_loop()`: iterates sessions every 15s, checks `time.time() - sess["last_ping"] > HEARTBEAT_TIMEOUT`, closes stale sockets, removes from both `sessions` and `endpoint_map`
  - `server.py:214` — `last_ping` key set at registration; `server.py:232` refreshed on `ping`; `server.py:239` refreshed on every `message`
  - `client.py:33` — `HEARTBEAT_INTERVAL = 60`; `client.py:420-431` — `_heartbeat_loop()` sleeps `HEARTBEAT_INTERVAL` (60s, line 423) then sends `{"type": "ping"}`
  - NOTE: state key is `last_ping` (not `last_heartbeat`) — `server.py:214,232,239`; earlier wiki evidence pointed at the wrong key name
- **Verdict:** ✅ CORRECT (state key name corrected to `last_ping`)
- **Fix needed:** Wiki/verify evidence updated to `last_ping`; heartbeat interval is 60s (code), NOT the 55s the repo README claims (README:204 carries a source-doc bug)

## Claim 5: Broadcast support (empty `to` field routes to all endpoints)
- **Wiki says:** Messages with `"to": ""` or `"to": "*"` are delivered to all registered endpoints.
- **Source evidence:**
  - `server.py:296-306` — `_route_message()`: reads `to_ep = msg.get("to", "")`, then `if not to_ep:` enters the broadcast branch and iterates all sessions (`for sess in list(self.sessions.values()): self._send_raw(sess["socket"], content)`)
  - `server.py:307` — `elif to_ep in self.endpoint_map:` — any truthy `to` value (including `"*"`) falls into endpoint lookup
  - `server.py:315-324` — If the target is not in `endpoint_map` and a reply socket exists: sends `{"type": "error", "code": "endpoint_not_found", ...}` — a literal `"*"` therefore returns `endpoint_not_found`, it does NOT broadcast
  - `server.py:4` — Module docstring: "session_id <-> endpoint bi-directional mapping for point-to-point routing and broadcast."
- **Verdict:** ❌ INCORRECT — only an **empty** `to` (`""`) triggers broadcast. The wiki's `"*"` broadcast claim is wrong; `"*"` is truthy → endpoint lookup → `endpoint_not_found` error reply
- **Fix needed:** Wiki changed to broadcast-via-empty-`to`-only; `"*"` documented as an error case

## Claim 6: Post-route hook scripts
- **Wiki says:** After each message is routed, configured hook scripts run asynchronously (subprocess). Resolution order: `HERMES_BUS_HOOKS` env var, then `hooks.yaml` config file, then default (none).
- **Source evidence:**
  - `server.py:49-89` — `_get_home()`, `_resolve_hook_scripts()` implements full resolution order: env var (comma-separated or JSON array), then `$HERMES_HOME/hermes-bus/hooks.yaml` config file
  - `server.py:278-293` — `_trigger_hooks()`: iterates `self.hook_scripts`, spawns `subprocess.Popen([sys.executable, hook_path], stdin=...)`, writes JSON to stdin
  - `hermes_bus/hooks.yaml` exists (empty config file — default disabled)
  - Server docstring (lines 11-21) documents hook configuration in detail
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Session isolation via `HERMES_BUS_ROOT` vs `HERMES_HOME`
- **Wiki says:** `HERMES_BUS_ROOT` controls bus socket location; `HERMES_HOME` controls config home. Multiple profiles share one daemon. Profile endpoint naming convention: `<profile>-gateway`.
- **Source evidence:**
  - `server.py:32-34` — `_get_bus_socket_path()`: `root = os.environ.get("HERMES_BUS_ROOT", os.path.expanduser("~/.hermes"))`
  - `server.py:45-46` — `_get_home()`: `return os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))`
  - `busd.py:28-31` — Same pattern: `HERMES_HOME`, `ROOT_HERMES_HOME` (from `HERMES_BUS_ROOT`), `RUN_DIR` all derive from separate env vars
  - `client.py:27-29` — Socket path uses `HERMES_BUS_ROOT`, separate from profile config
  - Both env vars default to `~/.hermes` when unset, but can be independently configured
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (profile endpoint naming convention `<profile>-gateway` is a downstream convention — README.md:71 — not enforced in bus source)

## Claim 8: Auto-reconnect with exponential backoff
- **Wiki says:** Clients retry connection with exponential backoff: 1s initial, 30s max.
- **Source evidence:**
  - `client.py:34-35` — `RECONNECT_DELAY_INITIAL = 1.0`, `RECONNECT_DELAY_MAX = 30.0`
  - `client.py:356-386` — `_start_reconnect_thread()`: spawns a daemon thread with `_reconnect_loop` that sleeps with exponential backoff (`self._reconnect_delay * 1.5`) capped at `RECONNECT_DELAY_MAX`
  - `client.py:249-251` — On initial connection failure, immediately starts reconnect thread
  - Thread safety: `_server_start_lock = threading.Lock()` (client.py:135) prevents duplicate connect attempts
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 9: Envelope — server adds only `id` + `ts`; `from` is client-set
- **Wiki says (was):** "The bus adds `from` (if unset) and `ts` during routing."
- **Source evidence:**
  - `server.py:241-242` — Server routing adds ONLY `id` (`msg.setdefault("id", str(uuid.uuid4()))`) and `ts` (`msg.setdefault("ts", time.time())`) — `setdefault` preserves any client-provided values
  - `server.py:214,232,239` — `from` is never assigned anywhere in server routing code
  - `client.py:109` — `send_message()` sets `"from": from_ep` (default `"anonymous"`)
  - `client.py:298` — `BusClient.send()` sets `"from": self.endpoint`
  - `client.py:110-111, 299-300` — Clients also set `id` and `ts` themselves (server `setdefault` then no-ops)
- **Verdict:** ❌ INCORRECT (original wiki claim) — corrected: server adds `id` (uuid) + `ts` only, via `setdefault`; `from` is set by clients and stays unset otherwise. The repo README (README:191,221) carries the same bug
- **Fix needed:** Wiki updated to id/ts `setdefault` semantics; `from` documented as client-set

## Claim 10: Disconnect diagnostics keywords
- **Wiki says (was):** "error keywords (traceback, error, failed, assert, killed, OOM, syntaxerror, importerror)"
- **Source evidence:**
  - `busd.py:180-193` — Actual keyword→description pairs scanned over the last 50 log lines (`busd.py:175`): `traceback`, `connectionreset`, `brokenpipe`, `timeout`, `oserror`, `memory`, `permission`, `file not found`, `bind`, `address already`, `sigkill`, `sigterm`, `killed`
  - `busd.py:128-204` — `_diagnose_disconnect()` mechanism: `pgrep -f hermes_bus.server` process count (135-147), socket mtime staleness (>300s, 150-156), PID/socket consistency (158-169), keyword scan + log tail (171-204)
- **Verdict:** ❌ INCORRECT (original keyword list) — corrected to the actual 13 keywords above; mechanism (pgrep, mtime staleness, last 50 lines) was already correct
- **Fix needed:** Wiki keyword list replaced

## Claim 11: Client auto-starts the daemon on connect failure
- **Wiki says (was):** (gap — not documented)
- **Source evidence:**
  - `client.py:138-178` — `_start_bus_server()`: probes the socket (connect test, 0.5s timeout), unlinks stale socket files, spawns `subprocess.Popen(["hermes-busd", "start"], ...)`, waits up to 2s (20 × 0.1s) for the socket to appear
  - `client.py:96-104` — `send_message()` calls `_start_bus_server()` on `FileNotFoundError`/`ConnectionRefusedError`/`OSError`, then retries once
  - `client.py:244-251` — `BusClient.connect()` calls `_start_bus_server()` after a failed `_connect_and_register()`, then retries; falls back to the reconnect thread on a second failure
  - `client.py:436-438` — `ensure_bus_running()` public helper wrapping `_start_bus_server()`
- **Verdict:** ✅ NEW CLAIM — auto-start confirmed; previously undocumented
- **Fix needed:** Wiki expanded with auto-start behavior + `ensure_bus_running()`

## Claim 12: `error` reply type for unknown endpoints
- **Wiki says (was):** (gap — message types table listed only register/registered/ping/pong/list_endpoints/endpoints_list/message)
- **Source evidence:**
  - `server.py:315-324` — `_route_message()`: when `to_ep` is not in `endpoint_map` and a `reply_socket` exists (anonymous sender), replies `{"type": "error", "code": "endpoint_not_found", "detail": f"Endpoint '{to_ep}' is not connected", "id": msg.get("id")}`
  - `client.py:117-122` — `send_message()` reads the reply with a 1.0s timeout and returns `False` when `reply.get("type") == "error"`
  - Registered senders route without a `reply_socket` (server.py:244) — their unmatched messages are dropped silently
- **Verdict:** ✅ NEW CLAIM — `error` reply type confirmed; previously undocumented
- **Fix needed:** Wiki message types table now includes `error`

## Claim 13: Socket hardening + log rotation
- **Wiki says (was):** (gap — not documented)
- **Source evidence:**
  - `server.py:139` — `os.chmod(self.socket_path, 0o600)` — socket restricted to the owning user
  - `server.py:143` — `signal.signal(signal.SIGPIPE, signal.SIG_IGN)` — a client disconnect won't kill the server via SIGPIPE
  - `busd.py:30-33` — `LOG_PATH = RUN_DIR / "busd.log"` where `RUN_DIR = $HERMES_BUS_ROOT/run`
  - `busd.py:37-38` — `MAX_LOG_BYTES = 500_000`; `busd.py:53-55` — `_log()` rotates in-place when the log exceeds 500 KB (keeps trailing half)
- **Verdict:** ✅ NEW CLAIM — socket chmod `0o600` + SIGPIPE ignore + 500 KB log rotation at `run/busd.log` confirmed
- **Fix needed:** Wiki expanded with hardening + log rotation details

## Summary

All claims from the Hermes Bus wiki have been re-verified against the source code (v0.7.0):
- ✅ Zero-dependency daemon: `dependencies = []`, Python 3.10+ confirmed
- ✅ Unix Domain Socket + 4-byte BE length prefix protocol confirmed
- ✅ Named endpoint registration + anonymous senders confirmed
- ✅ Heartbeat 60s/90s with stale session pruning confirmed (state key `last_ping`; 60s per code, not the README's 55s)
- ❌ Broadcast: only empty `to` (`""`) broadcasts; `"*"` returns `endpoint_not_found` — wiki `"*"` claim corrected
- ✅ Post-route hook scripts with 3-tier resolution confirmed
- ✅ Session isolation via `HERMES_BUS_ROOT`/`HERMES_HOME` confirmed
- ✅ Auto-reconnect with exponential backoff (1s initial, 30s max, ×1.5) confirmed
- ❌ Envelope: server adds `id`+`ts` via `setdefault` only; `from` is client-set — wiki claim corrected
- ❌ Diagnostics keyword list corrected to the actual 13 keywords in `busd.py`
- ✅ NEW: Client auto-starts daemon (`_start_bus_server`, `ensure_bus_running`)
- ✅ NEW: `error` reply type (`endpoint_not_found`)
- ✅ NEW: Socket chmod `0o600` + SIGPIPE ignore + 500 KB log rotation

## Related

- [[hermes-bus]] -- Main wiki entry
- [[hermes-agent.codegraph-verify]] -- Codegraph verification for upstream Hermes Agent
- [[hermes-agent]] -- Main Hermes Agent wiki
- [[hermes-workspace]] -- Downstream consumer of bus messages

## Cross-project

- [[hermes-workspace.codegraph-verify]] -- Codegraph verification for Hermes Workspace
- [[hermes-plugins.codegraph-verify]] -- Codegraph verification for Hermes Plugins
- [[openclaw.codegraph-verify]] -- Comparable openclaw message bus verification
