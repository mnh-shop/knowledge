---
title: "Podman REST API Implementation"
tags: [REST-API, cli, container, containers, docker, golang, gorilla-mux, mcp, monitoring, podman, quadlet, systemd]
description: "Analysis of Podman's REST API v2 server implementation (not MCP protocol)"
source: sources/podman/
date: 2026-06-24
---

# Podman REST API Server

**Podman does NOT implement the Model Context Protocol (MCP).** It implements a comprehensive **REST API v2** server that is Docker-compatible, serving endpoints for container, image, pod, volume, network, and system management. This document analyzes the API server found in the Podman codebase.

## Architecture Overview

- **Language:** Go
- **HTTP Router:** gorilla/mux
- **Transport:** Unix domain socket (`/run/podman/podman.sock`) or TCP
- **API Versions:** two parallel API surfaces -- Docker-compatible ("compat") and native Podman ("libpod")
- **Protocol:** REST/HTTP with JSON request/response bodies
- **gRPC support:** stubs exist in `pkg/api/grpcpb/` but the main server is HTTP-based
- **Swagger spec:** generated from Go source via `swagger generate spec`

## Core Types

### APIServer (pkg/api/server/server.go)

```go
type APIServer struct {
    http.Server
    grpc               *grpc.Server
    net.Listener
    *libpod.Runtime
    *schema.Decoder
    context.CancelFunc
    context.Context
    CorsHeaders        string
    PProfAddr          string
    idleTracker        *idle.Tracker
    tlsCertFile        string
    tlsKeyFile         string
    tlsClientCAFile    string
}
```

Key methods:
- **NewServerWithSettings** -- creates and configures a new API server
- **Serve** -- starts the HTTP server
- **Shutdown** -- graceful shutdown with halt flag
- **setupSystemd** -- integrates with systemd socket activation
- **setupPprof** -- optional pprof endpoint
- **APIHandler / StreamBufferedAPIHandler** -- middleware wrappers for request handling

### ServiceOptions (entities)

```go
type ServiceOptions struct {
    CorsHeaders     string
    PProfAddr       string
    Timeout         time.Duration
    URI             string
    TLSCertFile     string
    TLSKeyFile      string
    TLSClientCAFile string
}
```

### Defaults

- **DefaultCorsHeaders**: `""` (empty string)
- **DefaultServiceDuration**: `300 * time.Second`
- **UnlimitedServiceDuration**: `0 * time.Second`
- **Default Root API Path**: `/run/podman/podman.sock` (Linux), `/var/run/podman/podman.sock` (FreeBSD)
- **Default API Address**: `unix://` + DefaultRootAPIPath

## Handler Registration

The APIServer registers handlers via gorilla/mux routers. Each domain has a `register*Handlers` method. 25 registration functions total.

### Full list of registered handler groups:

| Module | File | Handler Prefix |
|--------|------|----------------|
| Archive | `register_archive.go` | libpod |
| Artifacts | `register_artifacts.go` | libpod |
| Auth | `register_auth.go` | compat |
| Containers | `register_containers.go` | compat + libpod |
| Distribution | `register_distribution.go` | compat |
| Events | `register_events.go` | compat |
| Exec | `register_exec.go` | compat |
| Generate | `register_generate.go` | libpod |
| HealthCheck | `register_healthcheck.go` | libpod |
| Images | `register_images.go` | compat + libpod |
| Info | `register_info.go` | compat |
| Kube | `register_kube.go` | libpod |
| Manifest | `register_manifest.go` | libpod |
| Monitor | `register_monitor.go` | libpod |
| Networks | `register_networks.go` | compat + libpod |
| Ping | `register_ping.go` | compat |
| Plugins | `register_plugins.go` | compat |
| Pods | `register_pods.go` | libpod |
| Quadlets | `register_quadlets.go` | libpod |
| Secrets | `register_secrets.go` | compat + libpod |
| Swagger | `register_swagger.go` | -- |
| Swarm | `register_swarm.go` | compat (no-op) |
| System | `register_system.go` | compat + libpod |
| Version | `register_version.go` | compat |
| Volumes | `register_volumes.go` | compat + libpod |

## API Endpoint Categories

### Docker-Compatibility Endpoints ("compat")

These endpoints mirror the Docker Engine API v1.24+ for drop-in compatibility:

- `GET /v{version}/_ping`
- `POST /v{version}/auth`
- `GET /v{version}/events`
- Container lifecycle: create, start, stop, restart, kill, pause, unpause, wait, remove, prune
- Container inspection: list, get, logs, stats, top, changes, export
- Exec: create, start, inspect, resize
- Image operations: create, build, push, tag, search, history, remove, prune, save, load, inspect
- Network: list, inspect, create, remove, connect, disconnect, prune
- Volume: list, inspect, create, remove, prune
- System: info, version, df, events
- Secrets: list, inspect, create, remove, update

### Native Podman Endpoints ("libpod")

Podman-specific endpoints not in the Docker API:

- **Pods**: create, list, inspect, start, stop, restart, kill, pause, unpause, prune, rm, stats, top, exists
- **Generate**: spec (generate OCI spec), systemd (generate systemd unit files), kube (generate Kubernetes YAML)
- **HealthCheck**: run, report
- **Kube**: play (apply Kubernetes YAML), down (teardown)
- **Artifacts**: add, extract, inspect, list, pull, push, remove
- **Quadlets**: list, file, remove
- **Manifests**: create, inspect, add, annotate, remove, push
- **Monitor**: container monitor endpoint

## Middleware Chain

1. **referenceIDHandler** -- assigns a unique reference ID per request
2. **loggingHandler** -- request/response logging
3. **panicHandler** -- recovers panics and returns 500
4. **APIHandler / StreamBufferedAPIHandler** -- wraps with CORS headers, error handling

## Middleware Implementation

### handler_api.go
- `BufferedResponseWriter` -- wraps `http.ResponseWriter` with `bufio.Writer` for write buffering
- `APIHandler` -- standard handler wrapper
- `StreamBufferedAPIHandler` -- handler wrapper for streaming endpoints (attach, logs, exec)
- `VersionedPath` -- adds `/v{version}` prefix to route paths

### handler_logging.go
- `loggingHandler` -- mux middleware that logs each request URI, method, remote address, and response size/code

### handler_panic.go
- `panicHandler` -- mux middleware that catches panics and returns HTTP 500

### handler_rid.go
- `referenceIDHandler` -- mux middleware that injects a unique request ID into the request context

## Idle Connection Tracking (pkg/api/server/idle/tracker.go)

The `Tracker` struct manages idle connections for automatic shutdown:

```go
type Tracker struct {
    Duration time.Duration
    hijacked int
    managed  map[net.Conn]struct{}
}
```

Methods:
- `NewTracker(idle time.Duration)` -- create tracker
- `ConnState(conn, state)` -- hook into HTTP Server ConnState
- `ActiveConnections()` -- current active count
- `TotalConnections()` -- total lifetime count
- `Done()` -- channel that fires when idle timeout elapses
- `Close()` -- close tracker

## Transport Options

1. **Unix domain socket** -- default (`unix:///run/podman/podman.sock`)
2. **TCP** -- via `tcp:host:port` URI
3. **systemd socket activation** -- uses `LISTEN_FD` (fd 3) when activated by systemd
4. **TLS** -- configurable via `TLSCertFile`, `TLSKeyFile`, `TLSClientCAFile`

## Client Bindings (pkg/bindings/)

Go client library that wraps the REST API:
- `pkg/bindings/artifacts/` -- artifact operations
- `pkg/bindings/images/` -- image operations
- `pkg/bindings/containers/` -- container operations
- Other bindings for pods, volumes, networks, secrets, etc.
- Generated option types with builder pattern (`WithForce`, `WithIgnore`, etc.)

## Command-Line Server (`podman system service`)

The server is launched via `podman system service`:
- `cmd/podman/system/service.go` -- cobra command definition
- `cmd/podman/system/service_abi.go` -- Linux/FreeBSD implementation
- `cmd/podman/system/service_abi_linux.go` -- Linux-specific (cgroup, service reaper)
- `cmd/podman/system/service_abi_common.go` -- FreeBSD-specific
- `podman-remote` -- client binary that connects to the API server

## Integration with systemd

Systemd unit files in `contrib/systemd/system/`:
- `podman.service` -- the API service unit
- `podman.socket` -- socket activation unit
- `podman-auto-update.service` / `.timer` -- auto-update container images
- `podman-clean-transient.service` -- cleanup transient containers
- `podman-kube@.service` -- run pods from Kubernetes YAML
- `podman-restart.service` -- handle container restarts
- `podman-docker.conf` -- Docker API compatibility socket (`/var/run/docker.sock` → Podman socket)

## Quadlet (systemd-native containers)

Quadlet allows running containers as systemd services using `.container`, `.pod`, `.volume`, and `.network` unit files:
- `pkg/systemd/quadlet/` -- Quadlet parser and converter
- `cmd/podman/quadlet/` -- CLI for managing Quadlet files (list, print, rm), including `quadlet.go` (main entry) and `install.go` (unit install/uninstall)
- Converts container descriptions to systemd service files dynamically

## Swagger API Documentation

- Makefile target: `make swagger.yaml`
- Generates OpenAPI spec from Go source annotations
- Tags group endpoints by domain:
  - artifacts, containers, exec, images, manifests, networks, pods, volumes, secrets, system
  - Same set with " (compat)" suffix for Docker-compatible endpoints

## Key File Paths

- `/Users/admin1/Documents/knowledge/raw/podman/podman.xml` -- full repomix source
- `pkg/api/server/server.go` -- APIServer struct and main server loop
- `pkg/api/server/register_*.go` -- handler registration (25 files)
- `pkg/api/server/handler_api.go` -- API wrapper middleware
- `pkg/api/server/handler_logging.go` -- logging middleware
- `pkg/api/server/handler_panic.go` -- panic recovery middleware
- `pkg/api/server/handler_rid.go` -- request ID middleware
- `pkg/api/server/idle/tracker.go` -- idle connection tracking
- `pkg/api/handlers/compat/` -- Docker-compatible handlers
- `pkg/api/handlers/libpod/` -- native Podman handlers
- `pkg/api/grpcpb/` -- gRPC stubs (proto + generated Go)
- `pkg/api/types/types.go` -- API context key types
- `pkg/bindings/` -- Go client bindings
- `pkg/domain/entities/` -- shared domain entity types (ServiceOptions, etc.)
- `contrib/systemd/system/` -- systemd unit files
- `cmd/podman/system/service.go` -- `podman system service` command

## MCP Assessment

**Conclusion: Podman does not implement the Model Context Protocol (MCP).** The 15 occurrences of "mcp" in the codebase are false positives:
- `.mcp.json` files inside vendored `go-openapi` test tool dependencies
- `SYS_MEMCPY` / `SYS_WMEMCPY` syscall constants in vendored `golang.org/x/sys/unix`
- A substring match in a byte encoding table

For MCP-based container management, one would need a separate MCP server that wraps Podman's REST API (e.g., using the `pkg/bindings/` Go client library or calling the REST API directly).
