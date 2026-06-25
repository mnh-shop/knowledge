---
name: sablier-architecture
tags:
  - sablier
  - scale-to-zero
  - architecture
description: Sablier Architecture
---

# Sablier Architecture

**Language**: Go  
**Source**: https://github.com/sablierapp/sablier  
**Entrypoint**: `/Users/admin1/Documents/knowledge/sources/sablier/cmd/sablier/cmd.go`  
**Root command**: `pkg/sabliercmd/root.go` with `start` subcommand at `pkg/sabliercmd/start.go`

---

## Overview

Sablier is a scale-to-zero daemon for containerized workloads. It sits next to a reverse proxy (Traefik, Caddy, Nginx, Envoy, Istio, Apache APISIX) and manages the lifecycle of containers based on demand. When no requests arrive for a configurable session duration, Sablier stops (or throttles) the container. When a new request arrives, the proxy plugin intercepts it, wakes Sablier, which starts the container and returns when healthy.

The core model is **session-based idle detection**: the reverse proxy plugin is responsible for renewing sessions. Sablier does not monitor inbound traffic itself.

---

## Key Source Files

| File | Purpose |
|------|---------|
| `cmd/sablier/cmd.go` | Entry point, calls `sabliercmd.NewRootCommand()` |
| `pkg/sabliercmd/root.go` | Root CLI command definition |
| `pkg/sabliercmd/start.go` | Startup flow: tracing, provider, store, server |
| `pkg/sablier/sablier.go` | Core engine: Provider, Store, groups, pendingStarts |
| `pkg/sablier/instance_request.go` | Session orchestration, request deduplication |
| `pkg/sablier/provider.go` | Provider interface definition |
| `pkg/config/configuration.go` | Config struct (Viper-based) |
| `pkg/provider/docker/` | Docker provider implementation |
| `pkg/provider/dockerswarm/` | Docker Swarm provider implementation |
| `pkg/provider/kubernetes/` | Kubernetes provider implementation |
| `pkg/provider/proxmoxlxc/` | Proxmox LXC provider implementation |
| `pkg/provider/podman/` | Podman provider (thin Docker wrapper) |
| `pkg/store/tinykv/tinykv.go` | In-memory KV store with TTL-based expiration |
| `pkg/store/valkey/` | Valkey/Redis store implementation |
| `internal/server/` | Gin-based HTTP server |
| `internal/api/start_blocking.go` | Blocking strategy endpoint |
| `internal/api/start_dynamic.go` | Dynamic strategy endpoint (waiting page) |
| `pkg/theme/` | Waiting page themes (hacker-terminal, matrix, ghost, shuffle) |
| `pkg/metrics/` | Prometheus metrics |
| `pkg/tracing/` | OpenTelemetry tracing |
| `pkg/webhook/` | Webhook notifications |

---

## Architecture Components

### 1. Boot Flow (`pkg/sabliercmd/start.go`)
The `Start()` function is the main orchestrator called by the Cobra `start` subcommand:

1. Create OS signal context (SIGINT, SIGTERM)
2. Initialize structured logger from config
3. Set up OpenTelemetry tracing via `tracing.Setup()` (OTLP HTTP exporter or stdout)
4. Initialize the provider (Docker, Podman, Kubernetes, etc.) via `setupProvider()`
5. Create metrics recorder (Prometheus or Noop)
6. Initialize session store (in-memory or Valkey) with optional file persistence
7. Create `Sablier` core instance with provider, store, and metrics
8. Register OnExpire callback which calls `provider.InstanceStop()` for expired sessions
9. Register GroupLockCollector for Prometheus metrics
10. Load initial groups from provider via `provider.InstanceGroups()`
11. Start background goroutines: `GroupWatch`, instance events listener, auto-stop watchers, running-hours watcher, webhook dispatcher
12. Set up theme system (built-in + custom themes)
13. Create `api.ServeStrategy` and start the Gin HTTP server via `server.Start()`
14. Block until context cancellation, then gracefully shut down

### 2. Config Layer (`pkg/config/`)
Viper-based configuration loaded from YAML, env vars, or CLI flags. The `Config` struct holds: `Server`, `Storage`, `Provider`, `Sessions`, `Logging`, `Strategy`, `Webhooks`, `Tracing`. Configuration is evaluated with precedence: config file < environment variables < CLI flags. Load order for config files: `/etc/sablier/`, `$XDG_CONFIG_HOME/`, `$HOME/.config/`, current directory.

### 3. Provider Layer (`pkg/sablier/provider.go`)
An interface at `pkg/sablier/provider.go`:

```go
type Provider interface {
    InstanceStart(ctx, instance) error
    InstanceStop(ctx, instance) error
    InstanceInspect(ctx, instance) (InstanceInfo, error)
    InstanceGroups(ctx) (map[string][]string, error)
    InstanceList(ctx, options) ([]InstanceConfiguration, error)
    InstanceEvents(ctx, opts) InstanceEventStream
}
```

The `InstanceEventStream` type returns two channels: `Events (<-chan InstanceEvent)` for lifecycle notifications and `Err (<-chan error)` for terminal errors. Sablier subscribes to `InstanceEventStopped` events to clean up session state when instances stop externally.

### 4. Core Engine (`pkg/sablier/sablier.go`)
The `Sablier` struct holds:
- **Provider** -- the backend (Docker, Swarm, K8s, Podman, Proxmox)
- **Store** -- session state (in-memory via tinykv or Valkey/Redis)
- **groups** registry -- concurrent-safe `groupRegistry` mapping group names to instance names
- **pendingStarts** -- deduplication map (`map[string]*pendingStart`) with mutex for concurrent start requests
- Configurable timings:
  - `BlockingRefreshFrequency`: 5s (how often polling checks instance readiness)
  - `InstanceStartTimeout`: 5m (max time for async start goroutine)
  - `ExternallyStartedScanInterval`: 30s (reconciliation scan for externally started instances)
  - `RunningHoursRefreshFrequency`: 30s (running-hours window reconciliation)
- Metrics recorder (Prometheus or Noop)
- OpenTelemetry tracer
- Options: `rejectUnlabeledRequests`, `verifyEnabledOnExpiration`

### 5. HTTP Server (`internal/server/`)
- Gin-based HTTP server on configurable port (default 10000)
- Base path configurable via `server.base-path` (default "/")
- Middleware chain: OpenTelemetry tracing (`otelgin.Middleware`) -> Structured logging -> Gin Recovery
- Routes:
  - `GET /health` -- health check (returns 200 OK, or 503 during graceful shutdown)
  - `GET /metrics` -- Prometheus metrics (only registered when `server.metrics.enabled=true`)
  - `GET /api/strategies/blocking` -- wake and wait for ready (blocking strategy)
  - `GET /api/strategies/dynamic` -- wake with custom waiting page (dynamic strategy)
  - `GET /api/themes` -- list available themes
  - `GET /api/events` -- SSE events stream for session state changes
- Graceful shutdown on SIGINT/SIGTERM with 15-second timeout

### 6. API Layer (`internal/api/`)

The API provides two strategies:

**Blocking Strategy** (`start_blocking.go`):
- Endpoint: `GET /api/strategies/blocking`
- Parameters: `names` (comma-separated), `group`, `session_duration`, `timeout`
- Flow: Calls `RequestReadySession` (or `RequestReadySessionGroup`) which polls until all instances report `IsReady() == true` or the timeout expires
- Returns: JSON with session state including `X-Sablier-Status` header
- Use case: API-to-API communication where clients can wait synchronously

**Dynamic Strategy** (`start_dynamic.go`):
- Endpoint: `GET /api/strategies/dynamic`
- Parameters: `names`, `group`, `show_details`, `display_name`, `theme`, `session_duration`, `refresh_frequency`
- Flow: Calls `RequestSession` (non-blocking), renders an HTML waiting page with auto-refresh that polls until ready, then redirects
- Use case: End-user browser access with visual waiting experience
- Six built-in themes and support for custom HTML themes

### 7. Store (`pkg/store/`)
Interface: `Get/Put/Delete/OnExpire`. Three key implementations:
- **In-memory** (`pkg/store/inmemory/`) -- wraps `tinykv`, a concurrent map with a min-heap for TTL-based expiration. A background `expireLoop()` goroutine polls the heap, adaptively adjusting poll interval. On expiry, calls the registered `onExpire` callback.
- **Valkey/Redis** (`pkg/store/valkey/`) -- distributed store for multi-replica Sablier deployments. Uses Valkey keyspace notifications for cross-instance expiration.
- **File-backed** -- optional persistence via `storage.file` path. Sessions are serialized as JSON on shutdown and reloaded on startup. Survives Sablier restarts.

### 8. Group Registry (`pkg/sablier/group_registry.go`)
A concurrent-safe `groupRegistry` that maps group names to instance name slices. Provides:
- `Snapshot()` -- deep copy for metrics collection
- `Sync(instance, newGroups)` -- atomic add/remove to match desired group membership
- `Remove(instance)` -- drop instance from all groups (called on `InstanceEventStopped`)
- `GroupsOf(instance)` -- inverse lookup
- Groups change logging via `cmp.Diff` for auditability

### 9. Request Deduplication System (`pkg/sablier/instance_request.go`)

The `pendingStarts` map ensures only one goroutine starts an instance at a time:

1. **Check phase**: Lock -> check if entry exists -> if completed, clean up -> if running, return cached info -> unlock
2. **Inspect phase**: No lock -- allows slow remote calls without blocking
3. **Registration phase**: Lock again -> re-check for race -> create `pendingStart{ done, err, info, spanCtx }` -> unlock
4. **Start phase**: Go routine with background context carrying the OTel span context from the triggering request. Timeout via `InstanceStartTimeout` (5m default). Metrics recorded: `RecordReadyWaitBegin`, `RecordActiveInstance`, `RecordInstanceStartEnd`, `RecordInstanceStartFailure`.
5. **Cleanup**: On success, `pendingStarts` entry removed. On failure, `ps.err` set for retry.

OTel trace propagation: The `pendingStart.spanCtx` is captured from the triggering HTTP request so the async start goroutine appears as a child span, uncoupled from the request's cancellation deadline.

### 10. Session Expiry Engine (`pkg/sablier/instance_expired.go`)

The `OnInstanceExpired` callback is registered with the store during boot:

```go
func onInstanceExpired(ctx, provider, recorder, verifyEnabled) func(string) {
    return func(key) {
        go func(key) {
            if verifyEnabled {
                info := provider.InstanceInspect(key)
                if info.Enabled != "true" { return } // skip stop
            }
            err := provider.InstanceStop(key)
            recorder.RecordInstanceStop(key, "expired")
            recorder.RecordInactiveInstance(key)
        }(key)
    }
}
```

Key design decisions:
- Runs in a goroutine (non-blocking to store's expire loop)
- Optional verification re-checks `sablier.enable=true` before stopping (prevents races with label changes)
- Webhook notifications are dispatched separately via the webhook dispatcher watching instance events

### 11. Auto-Stop System (`pkg/sablier/autostop.go`)

Two mechanisms:

**`StopAllUnregisteredInstances`** (startup):
- Lists all running managed instances from provider
- Cross-references with session store
- Stops any that Sablier is not tracking (cleanup after crash/restart)

**`WatchAndStopExternallyStarted`** (continuous):
- Subscribes to `InstanceEventStarted` events from provider
- Verifies if start was initiated by Sablier via `isStartedByUs()` (checks `pendingStarts` and store)
- Stops externally started instances to maintain scale-to-zero
- Periodic reconciliation scan (default 30s) as safety net

---

## Providers

### Docker (`pkg/provider/docker/`)
- Connects via the Docker socket using moby client
- Uses `ContainerStart`/`ContainerStop` (or `ContainerPause`/`ContainerUnpause` based on `--provider.docker.strategy`)
- Inspect checks Container State status and health status for readiness
- Supports scale mode via `ContainerUpdate` (CPU/memory cgroup updates)
- Events streamed via Docker's events API

### Podman (`pkg/provider/podman/`)
Thin wrapper around the Docker provider (37 lines). Podman exposes a Docker-compatible REST API on its socket (`/run/podman/podman.sock`). Sablier creates a Docker client configured with the Podman URI and delegates everything to the Docker provider.

### Docker Swarm (`pkg/provider/dockerswarm/`)
- Scales services via `ServiceScale` (replica count)
- Start/stop by setting replicas to 0/1+
- Supports scale mode via service update with resource constraints

### Kubernetes (`pkg/provider/kubernetes/`)
- Connects via in-cluster config
- Manages Deployments, StatefulSets, and CNPG (CloudNativePG) clusters
- Scales via replicas to 0/1+
- Instance names use `namespace_delimiter_type_delimiter_name` format

### Proxmox LXC (`pkg/provider/proxmoxlxc/`)
- Connects via Proxmox VE API with token authentication
- Starts/stops LXC containers
- Discovers containers by `sablier` tags (`sablier-group-<name>`)
- Does NOT support scale mode (uses tags, not labels)

---

## Reverse Proxy Integration

Sablier provides plugins for six reverse proxies via separate repositories. Each plugin adapts Sablier's HTTP API to the proxy's specific plugin system. The proxy plugins are client-side consumers of Sablier's API -- they do not modify Sablier itself.

### Plugin Architecture

| Reverse Proxy | Repository | Integration Type | Runtime vs Compiled | Provider Support |
|---------------|-----------|-----------------|---------------------|------------------|
| Traefik | [sablier-traefik-plugin](https://github.com/sablierapp/sablier-traefik-plugin) | Yaegi Go plugin | Runtime (no rebuild) | Docker, Swarm, K8s |
| Caddy | [sablier-caddy-plugin](https://github.com/sablierapp/sablier-caddy-plugin) | Caddy Go module | Compiled (`xcaddy`) | Docker, Swarm |
| Envoy | [sablier-proxywasm-plugin](https://github.com/sablierapp/sablier-proxywasm-plugin) | Proxy WASM filter | Runtime (WASM loading) | Docker |
| Nginx | [sablier-proxywasm-plugin](https://github.com/sablierapp/sablier-proxywasm-plugin) | Proxy WASM filter | Runtime (WASM loading) | Docker |
| Apache APISIX | (sablier repo docs) | Apache APISIX plugin | Runtime | Docker, Swarm, K8s |
| Istio | (sablier repo docs) | EnvoyFilter CRD | Runtime (Istio injects WASM) | K8s (partial) |

### Integration Flow

1. User configures a route/service managed by Sablier, mapping it to a Sablier group name
2. Request arrives at the proxy for that service
3. Proxy plugin intercepts the request, calls `GET /api/strategies/blocking?group=GROUP&session_duration=DURATION&timeout=TIMEOUT`
4. Sablier starts the container(s), returns 200 with `X-Sablier-Session-Status: ready` when healthy
5. Proxy forwards original request to the now-running backend
6. Session timer starts; after `session_duration` of inactivity, Sablier's expiry callback stops the container

### Runtime vs Compiled Plugins

- **Runtime plugins** (Traefik with Yaegi, Nginx/Envoy with Proxy WASM): The proxy can load the plugin dynamically without recompilation. Configuration changes take effect at proxy reload.
- **Compiled plugins** (Caddy): Requires rebuilding the proxy binary with `xcaddy build --with github.com/sablierapp/caddy-sablier`. The binary must be rebuilt when updating the plugin version.

### Proxy Compatibility

| Reverse Proxy | Docker | Docker Swarm | Kubernetes |
|---------------|--------|-------------|------------|
| Apache APISIX | Yes | Yes | Yes |
| Caddy | Yes | Yes | No |
| Envoy | Yes | Compatible | Compatible |
| Istio | No | No | Partial |
| Nginx | Yes | Compatible | Compatible |
| Traefik | Yes | Yes | Yes |

### Lifecycle from the Proxy's Perspective

The proxy plugin handles two distinct phases:

**Dynamic strategy** (`/api/strategies/dynamic`):
1. Proxy intercepts request, calls Sablier's dynamic endpoint
2. Sablier returns an HTML waiting page immediately (non-blocking)
3. The browser auto-refreshes the page, which polls Sablier's readiness
4. When ready, the page redirects to the actual service URL
5. Proxy sees the redirected request and forwards to the now-running backend

**Blocking strategy** (`/api/strategies/blocking`):
1. Proxy intercepts request, calls Sablier's blocking endpoint
2. Sablier holds the HTTP connection open, polling the provider
3. When the instance is ready, Sablier returns a 200 with status headers
4. Proxy forwards the original request to the running backend
5. Used for API-to-API communication where clients wait synchronously

---

## Complete Scale-to-Zero Lifecycle

### Phase 1: Request Interception

```
User/Browser/API Client
    |
    v
Reverse Proxy (Traefik/Caddy/Nginx)
    |
    | Plugin intercepts: backend container is stopped/unknown
    | Calls: GET /api/strategies/blocking?group=myapp&session_duration=5m&timeout=1m
    v
Sablier HTTP API
```

### Phase 2: Session Request (`RequestReadySession`)

Hanler chain: `StartBlocking()` -> `Sablier.RequestReadySession()` -> `requestReadySession()` -> `requestSession()` -> `instanceRequest()` for each instance

**Step 1: Parallel start dispatch** (`requestSession` function in `pkg/sablier/session_request.go:20`):
- Creates a goroutine per instance name
- Each goroutine calls `instanceRequest()` independently
- Results collected via mutex into a shared `SessionState.Instances` map
- Returns immediately with whatever state each instance is in

**Step 2: Instance request** (`instanceRequest` function in `pkg/sablier/instance_request.go:188`):
1. Check session store: `sessions.Get(ctx, name)`
2. If `store.ErrKeyNotFound` (instance not running):
   a. Call `requestStart(ctx, name, rejectUnlabeled)` which:
      - Checks `pendingStarts` for existing start goroutine
      - Inspects instance via `provider.InstanceInspect()` (outside lock)
      - Checks `sablier.enable=true` if rejectUnlabeled is set
      - Sets status to `InstanceStatusStarting`
      - Registers `pendingStart` entry (with OTel span context)
      - Dispatches async goroutine: `provider.InstanceStart()`
      - Returns pending `InstanceInfo` immediately
   b. Check `state.RunningHours` for window extension
   c. Put session in store: `sessions.Put(ctx, state, effectiveDuration)`
   d. Return state (starting/ready)
3. If found in store but not `InstanceStatusReady`:
   a. Check `consumePendingError(name)` for completed async start
   b. If start still pending, return cached state
   c. If done, inspect via `provider.InstanceInspect()`
   d. If first transition to ready, stamp `ReadyAt` time for `sablier.ready-after` enforcement
4. If found and ready: cache hit, return immediately (session refresh)

**Step 3: Wait for readiness** (`requestReadySession` in `pkg/sablier/session_request.go:78`):
If `session.IsReady()` returns false after initial dispatch:
- Enter polling loop with select on 4 channels:
  1. `ctx.Done()` -- request cancelled by client
  2. `readiness` -- all instances report IsReady() == true
  3. `errch` -- any instance returned an error
  4. `time.After(timeout)` -- default 1 minute timeout
- Ticker at `BlockingRefreshFrequency` (default 5s) re-calls `requestSession()`
- `requestSession()` re-checks store/provider status for each instance
- Returns when all instances report ready, or on timeout/error

### Phase 3: Request Forwarding

```
Sablier returns 200 OK with:
  X-Sablier-Status: ready
  {"session": {"instances": [{...}], "status": "ready"}}

Proxy sees ready status, forwards original request to running backend
```

### Phase 4: Instance Start (Async Goroutine)

```
requestStart() creates:
  pendingStart{
    done:    chan struct{}  -- closed when goroutine completes
    err:     error          -- set on failure
    info:    InstanceInfo   -- cached at creation time
    spanCtx: SpanContext    -- OTel trace parent
  }

Goroutine:
  1. Create background context with OTel span from triggering request
  2. Apply timeout: InstanceStartTimeout (default 5m)
  3. Call provider.InstanceStart():
     - Docker: inspect -> check scale config
       - Scale mode active: applyResources (restore CPU/memory)
       - Pause strategy: ContainerUnpause
       - Default: ContainerStart
  4. On success:
     - Record metrics: RecordInstanceStartEnd, ReadyWaitDuration
     - Clean up pendingStarts entry
  5. On failure:
     - Set ps.err for retry
     - Record metrics: RecordInstanceStartFailure
```

### Phase 5: Idle Timeout & Container Stop

```
Session TTL (default 5m) set via sessions.Put(state, duration)
    |
    | tinykv expireLoop polls min-heap
    v
Entry expires -> OnInstanceExpired callback
    |
    | Optional: re-inspect container, verify sablier.enable=true
    v
provider.InstanceStop():
  - Docker: inspect -> check scale config
    - Scale mode (idle.replicas >= 1):
      - applyResources: throttle CPU/memory to idle profile
    - Pause strategy:
      - ContainerPause
    - Default:
      - ContainerStop + WaitConditionNotRunning
  - Record metrics: RecordInstanceStop, RecordInactiveInstance
  - Fire webhook event (async, non-blocking)
```

### Phase 6: Session Refresh

Each new request to the proxy for the same service calls the blocking/dynamic endpoint again. Sablier finds the instance in the store (still running), calls `sessions.Put(info, duration)` to refresh the TTL. The instance continues running. If no requests arrive within the TTL window, Phase 5 triggers.

### Request Deduplication (`pkg/sablier/instance_request.go`)

The `pendingStarts` map prevents multiple concurrent requests from starting the same container:

1. **First request**: Lock -> no pending entry -> unlock -> inspect -> lock -> register entry -> unlock -> dispatch goroutine
2. **Concurrent request (while starting)**: Lock -> pending entry exists, `ps.done` not closed -> return cached `ps.info` -> unlock
3. **Concurrent request (after completion)**: Lock -> pending entry exists, `ps.done` closed -> clean up -> unlock -> proceed normally
4. **Failure case**: Completed with error -> `ps.err` set -> retry generates clean state

OTel trace context carried in `pendingStart.spanCtx` so the async goroutine is parented to the triggering HTTP request's trace, even though it runs in a background context free from the request's cancellation deadline.

---

## Idle Detection

Sablier's idle detection is **session-based** rather than traffic-based.

### How It Works
1. Reverse proxy plugin makes a `blocking` request with `session_duration` (e.g. "5m")
2. Sablier starts the container and stores a `(name, InstanceInfo, TTL=duration)` entry
3. Background goroutine (`expireLoop()`) runs a min-heap of timeout entries, fires `OnExpire` callback when TTL expires
4. Expire callback calls `provider.InstanceStop()` for each expired entry

### Configuration
- `sessions.default-duration`: 5 minutes (default session TTL)
- `sessions.expiration-interval`: 20 seconds (heap polling interval, adaptively adjusted)

### Key Insight
The reverse proxy is responsible for renewing sessions. The proxy makes blocking requests that map to a session timeout -- if the proxy doesn't renew, the container stops. Sablier does NOT monitor inbound traffic itself.

### Running-Hours Label (`sablier.running-hours`)
- Extends session duration to keep instance running during busy windows
- At window start, Sablier proactively starts the instance via `WatchRunningHours`
- During the window, request-triggered sessions extend to window end

---

## Scale Mode

An alternative to stop/start. Instead of stopping the container on session expiry, Sablier throttles its CPU and memory to a minimal idle allocation, then restores full resources when a new session arrives. The container never stops, so there is zero cold-start latency.

### How It Works
- `InstanceStart`: if `sc.Idle.Replicas >= 1`, check if active CPU/memory is set, call `applyResources()` to restore full resources with `docker update`
- `InstanceStop`: if `sc.Idle.Replicas >= 1` and `sc.Idle.CPU`/`sc.Idle.Memory` set, call `applyResources()` to throttle with `docker update`

### Scale Mode Labels
| Label | Default | Description |
|-------|---------|-------------|
| `sablier.idle.replicas` | 0 (stop) | >= 1 = keep running |
| `sablier.idle.cpu` | - | CPU limit when idle (e.g. "0.1") |
| `sablier.idle.memory` | - | Memory limit when idle (e.g. "64m") |
| `sablier.active.replicas` | 1 | Replica count when active |
| `sablier.active.cpu` | - | CPU limit when active (e.g. "2.0") |
| `sablier.active.memory` | - | Memory limit when active (e.g. "512m") |

### Supported Providers
Docker, Podman, Docker Swarm, Kubernetes. NOT Proxmox LXC.

---

## Webhooks

Asynchronous, fire-and-forget HTTP POST notifications when managed instances start or stop. Implementation at `pkg/webhook/dispatcher.go`.

### Configuration
```yaml
webhooks:
  endpoints:
    - url: https://uptime.example.com/api/push/xxx
      headers:
        Authorization: "Bearer <token>"
      events:
        - started
        - stopped
```

### Payload
```json
{
  "event": "started",
  "instance": { "name": "my-nginx" },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Delivery Semantics
- 10-second timeout per request
- No built-in retry (errors logged and dropped)
- Non-blocking: errors do not affect Sablier's operation
- Provider-agnostic payload structure
- OTel-instrumented HTTP client
- User-Agent: `sablier/<version>`

---

## Observability

### Prometheus Metrics (at `pkg/metrics/`)
Enabled via `server.metrics.enabled: true`. Served at `GET /metrics`.

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `sablier_group_locked` | gauge | group | 1 if any instance in group has active session |
| `sablier_group_active_instances` | gauge | group | Number of instances with active session in group |
| `sablier_instance_start_duration_seconds` | histogram | instance | Duration of start calls (success only) |
| `sablier_instance_ready_duration_seconds` | histogram | instance | E2E time from first not-ready to ready |
| `sablier_session_requests_total` | counter | strategy, target | Total session requests received |
| `sablier_instance_start_failures_total` | counter | instance | Total start failures |
| `sablier_instance_stops_total` | counter | instance, reason | Total stops by reason |

### OpenTelemetry Tracing (at `pkg/tracing/`)
- OTLP HTTP exporter (Jaeger, Grafana Tempo, etc.)
- W3C TraceContext propagation (joins existing traces from reverse proxy)
- Every HTTP request traced via `otelgin.Middleware`
- Every provider call instrumented via wrapped transports
- Config: `tracing.enabled`, `tracing.exporterType` (otlphttp/stdout), `tracing.endpoint`, `tracing.samplingRate`

---

## Waiting Page Themes

Sablier provides customizable waiting pages (the "dynamic" strategy) for direct browser access.

### Built-in Themes (`pkg/theme/`)
- `hacker-terminal` (default) -- green-on-black hacker aesthetic
- `matrix` -- Matrix rain-inspired animation
- `ghost` -- minimal ghost animation
- `shuffle` -- animated shuffle effect

### Custom Themes
Loaded from a directory specified by `strategy.dynamic.custom-themes-path`. Any `.html` file found recursively is registered as a named theme.

### Dynamic Strategy Flow
1. Proxy intercepts request, calls `GET /api/strategies/dynamic?group=myapp&theme=hacker-terminal`
2. Sablier starts container(s) via `RequestSession` (non-blocking)
3. Returns an HTML page that auto-refreshes (default every 5s)
4. HTML page polls Sablier for readiness status
5. When all instances are ready, page redirects browser to actual service URL

### Configuration
- `strategy.dynamic.default-theme`: "hacker-terminal"
- `strategy.dynamic.show-details-by-default`: true
- `strategy.dynamic.default-refresh-frequency`: 5s

---

## Agent Stack Synergy (Rootless Podman on CX23)

In a rootless Podman environment on a 2GB CX23 VPS, Sablier provides significant resource savings:

### Good Candidates for Scale-to-Zero
- **Agent gateways (OpenClaw ACP)** -- HTTP-facing services with sporadic traffic. Wake on demand. Idle-to-ready latency: 3-10 seconds (image cached).
- **n8n** -- Workflow engines on schedule/webhook. Sleep between executions. Session duration: 30m-1h.
- **Admin UIs (Hermes workspace, Mission Control)** -- Accessed by humans. Sleep between sessions.

### Poor Candidates
- **Infrastructure daemons** (crun-vm, Podman system services) -- must always run
- **Message queue consumers** -- need constant uptime for pull-based consumption
- **Watchdog/monitoring services** -- defeat the purpose

### Expected Resource Savings
- 3-4 agent services (OpenClaw ACP, n8n, Hermes, Mission Control) each consume ~100-300MB RAM while running
- Combined idle: ~1GB. Stopped: near-zero
- Potential savings: 60-80% RAM reduction during off-hours
- Cold-start penalty: 3-10 seconds per service (Podman, cached images)
- Scale mode alternative: `sablier.idle.replicas=1`, `sablier.idle.cpu=0.1`, `sablier.idle.memory=64m` -- zero cold-start at ~64MB per service

## Related

- [[sablier-deployment]] -- Deployment guide with practical configuration examples
- [[sablier-quadlet]] -- Quadlet configuration for rootless Podman deployment
- [[sablier]] -- Main wiki page for Sablier
