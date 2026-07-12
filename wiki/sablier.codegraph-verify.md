---
name: sablier-codegraph-verify
tags: [codegraph-verify, sablier, podman, proxy, go]
description: "Codegraph Verification: sablier"
source: sources/sablier/
---

# Codegraph Verification: sablier

**Date:** 2026-07-12

## Claim 1: Scale-to-zero proxy that starts workloads on demand and stops them after inactivity
- **Wiki says:** Sablier is a free and open-source project that starts workloads on demand and stops them after a period of inactivity. It integrates with reverse proxy plugins to intercept incoming requests, wake up sleeping workloads, and display a waiting page.

- **Source evidence:** `README.md` lines 7-9 state: "Free and open-source software that starts workloads on demand and stops them after a period of inactivity. It integrates with reverse proxy plugins (Traefik, Caddy, Nginx, Envoy, etc.) to intercept incoming requests, wake up sleeping workloads, and display a waiting page until they're ready." The architecture is confirmed by the `internal/api/` directory with `start_blocking.go`, `start_dynamic.go` which implement two startup strategies. The `Provider` interface (`pkg/sablier/`) and provider implementations in `pkg/provider/` (docker, dockerswarm, kubernetes, podman, proxmoxlxc) handle the actual container lifecycle.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Provides reverse proxy plugins for Traefik, Caddy, Nginx, Envoy, Apache APISIX, and Istio
- **Wiki says:** Sablier provides plugin integrations for Traefik middleware, Caddy module, Nginx WASM module, Envoy Proxy-WASM plugin, Apache APISIX Proxy-WASM plugin, and Istio EnvoyFilter.

- **Source evidence:** `README.md` "Usage with Reverse Proxies" section (lines 572-664) documents each integration: Apache APISIX via Proxy-WASM plugin (lines 578-589), Caddy via native module (lines 593-604), Envoy via Proxy-WASM plugin (lines 608-619), Istio via Proxy-WASM plugin (lines 623-634), Nginx via WASM module (lines 638-649), and Traefik via middleware plugin (lines 653-664). Each has a dedicated plugin repository reference. The `sablier-proxywasm-plugin` GitHub repo provides the common WASM backend for APISIX, Envoy, Istio, and Nginx.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Podman provider wraps the Docker provider via Podman's Docker-compatible API
- **Wiki says:** Sablier's Podman provider connects to the Podman socket using the Docker-compatible REST API, reusing the entire Docker provider implementation.

- **Source evidence:** `pkg/provider/podman/podman.go` lines 1-4 state: "Package podman provides a Sablier provider for Podman by wrapping the Docker provider. Podman exposes a Docker-compatible API, so we simply connect a Docker client to the Podman socket." The `Provider` struct (lines 21-23) embeds `*docker.Provider`, delegating all operations. The `New()` function (lines 27-36) takes a `*client.Client` (Docker API client) and constructs a Docker provider under the hood: `inner, err := docker.New(ctx, cli, logger, "stop")`. The interface guard at line 17 confirms `Provider` satisfies `sablier.Provider`.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Supports multiple container orchestration providers (Docker, Docker Swarm, Podman, Kubernetes, Proxmox LXC)
- **Wiki says:** Sablier supports Docker, Docker Swarm, Podman, Kubernetes, and Proxmox LXC as container providers, each implementing the same `Provider` interface.

- **Source evidence:** `pkg/provider/` directory contains implementations for: `docker/`, `dockerswarm/`, `kubernetes/`, `podman/`, `proxmoxlxc/`. The `providertest/` directory provides a shared test suite. The `Provider` interface is defined in `pkg/sablier/` (referenced by the interface guard in podman.go line 17). `README.md` lines 386-459 document each provider with features: Docker (socket connection, start/stop), Docker Swarm (scale to 0, stack support), Podman (socket connection, rootless), Kubernetes (Deployment/StatefulSet scale), Proxmox LXC (API token auth, LXC lifecycle).

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Scale mode throttles idle workloads instead of stopping them
- **Wiki says:** Sablier's scale mode keeps containers running when idle but throttles CPU, memory, and block I/O to minimal levels, restoring full resources when a session arrives — eliminating cold-start latency.

- **Source evidence:** `README.md` lines 461-493 document scale mode: "instead of stopping a container, Sablier throttles its CPU, memory, and (on Docker) block I/O to a minimal idle allocation, then restores full resources the moment a new session arrives." The idle/active label system is defined: `sablier.idle.replicas`, `sablier.idle.cpu`, `sablier.idle.memory`, `sablier.active.replicas`, `sablier.active.cpu`, `sablier.active.memory`. Block I/O throttling (`sablier.idle.blkio-weight`, `sablier.idle.blkio-device-*`) is supported on Docker only (lines 491-494).

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Prometheus metrics and OpenTelemetry tracing support
- **Wiki says:** Sablier exposes Prometheus-compatible metrics at `/metrics` and supports distributed tracing via OpenTelemetry with OTLP export to Jaeger/Grafana Tempo.

- **Source evidence:** `README.md` "Observability" section (lines 526-554) documents both. The `pkg/metrics/` directory implements the Prometheus metrics endpoint. The `pkg/tracing/` directory implements OpenTelemetry tracing. Configuration (`sablier.sample.yaml` lines 311-334) shows `tracing` config with `exporterType` (otlphttp/stdout), `endpoint`, `serviceName`, and `samplingRate`. The `server.metrics.enabled` flag controls metrics exposure. Trace context propagates via W3C TraceContext format (line 544: "if your reverse proxy injects a `traceparent` header, Sablier will join the existing trace").

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Blocking and dynamic startup strategies
- **Wiki says:** Sablier provides two startup strategies: blocking (waits synchronously for the workload to be ready, returns 200) and dynamic (displays a customizable waiting page until ready).

- **Source evidence:** `internal/api/start_blocking.go` implements the blocking strategy: returns `HTTP 200` with `X-Sablier-Session-Status: ready` header when the container is healthy. `internal/api/start_dynamic.go` implements the dynamic strategy: serves a waiting HTML page while the container starts. Configuration (`sablier.sample.yaml` lines 300-311) shows both: `strategy.dynamic` has `custom-themes-path`, `show-details-by-default`, `default-theme`, `default-refresh-frequency`; `strategy.blocking` has `default-timeout`. Available themes are defined in `internal/api/theme_list.go`.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[sablier]] -- Main wiki entry
- [[podman]] -- Podman container engine
- [[crun-vm]] -- OCI runtime shim for VM containers
- [[mission-control]] -- MCP audit server

## Cross-project

- [[podman.codegraph-verify]] -- Podman verification
- [[buildah.codegraph-verify]] -- Buildah verification
