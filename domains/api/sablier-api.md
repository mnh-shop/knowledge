---
name: sablier-api
description: "Sablier REST API reference — Gin-based dynamic container scaling endpoints"
source: sources/sablier/
tags: [api, container, gin, rest-api, sablier, scaling]
---

# Sablier — API Reference

Sablier exposes a Gin-based REST API for dynamic container scaling, session management, and health monitoring.

## Server

| Feature | Detail |
|---------|--------|
| **Framework** | Gin (Go) |
| **Default port** | Configurable via `config.Server` |
| **Base path** | Configurable (`serverConf.BasePath`) |
| **Metrics** | Prometheus `/metrics` endpoint (when PromRecorder active) |

## Endpoints

### Health

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `{basePath}/health` | Server health check |

### Metrics

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `{basePath}/metrics` | Prometheus metrics (only when Prom recorder active) |

### Session Strategies

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `{basePath}/api/strategies/dynamic` | Dynamic scaling strategy — start container on demand |
| `GET` | `{basePath}/api/strategies/blocking` | Blocking strategy — wait for container readiness |

### Instance Events

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `{basePath}/api/events` | Instance events (SSE stream) |

### Theme

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `{basePath}/api/themes` | List available themes |
| `GET` | `{basePath}/api/dynamic/themes` | Legacy themes path |

## Core Types

### `Sablier` Interface

| Method | Description |
|--------|-------------|
| `RequestSession(ctx, names, duration)` | Request session for named instances |
| `RequestSessionGroup(ctx, group, duration)` | Request session for a named group |
| `RequestReadySession(ctx, names, duration, timeout)` | Request ready session with timeout |
| `RequestReadySessionGroup(ctx, group, duration, timeout)` | Request ready group session with timeout |
| `InstanceEvents(ctx, opts)` | Stream instance events |

### `ServeStrategy`

```go
type ServeStrategy struct {
    Theme         *theme.Themes
    Sablier       Sablier
    Metrics       metrics.Recorder
    StrategyConfig config.Strategy
    SessionsConfig config.Sessions
}
```

### Response Headers

Every Sablier response includes the session state via `AddSablierHeader()`.

## Architecture

```
Client → Sablier Server (Gin)
  → API handlers (health, strategies, events, themes)
    → Sablier interface (session management)
      → Provider (Docker)
        → Container lifecycle
```

Supported providers:
- **Docker** (primary) — container start/stop lifecycle
- Testcontainers — testing framework integration

## Related

- [[sablier-architecture]] — System architecture
- [[sablier-deployment]] — Deployment guide
- [[sablier-mcp-implementation]] — MCP assessment (no MCP found)
