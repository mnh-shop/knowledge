---
name: sablier-codegraph-verify
tags: [codegraph-verify, sablier, podman, proxy, go]
description: "Codegraph Verification: sablier"
source: sources/sablier/
---

# Codegraph Verification: sablier

**Date:** 2026-07-30

## Claim 1: Scale-to-zero proxy that starts workloads on demand and stops them after inactivity
- **Wiki says:** Sablier starts workloads on demand and stops them after a period of inactivity, integrating with reverse proxy plugins to intercept requests and display a waiting page.
- **Source evidence:** `README.md` lines 7-9 describe the core concept. Architecture confirmed by `internal/api/start_blocking.go` and `internal/api/start_dynamic.go` (the two startup strategies) and the `Provider` interface (`pkg/sablier/`) with implementations in `pkg/provider/` (docker, dockerswarm, kubernetes, podman, proxmoxlxc).
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Reverse proxy plugin integrations (Traefik, Caddy, Nginx, Envoy, APISIX, Istio)
- **Wiki says:** Sablier provides plugin integrations for Traefik middleware, Caddy module, Nginx WASM, Envoy Proxy-WASM, APISIX Proxy-WASM, and Istio EnvoyFilter.
- **Source evidence:** `README.md` "Usage with Reverse Proxies" section (lines 572-664) documents each integration; the `sablier-proxywasm-plugin` repo provides the common WASM backend for APISIX, Envoy, Istio, Nginx.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Podman provider wraps the Docker provider via Podman's Docker-compatible API
- **Wiki says:** The Podman provider connects to the Podman socket using the Docker-compatible REST API, reusing the entire Docker provider implementation (36-line wrapper).
- **Source evidence:** `pkg/provider/podman/podman.go` is exactly 36 lines. Lines 1-4: "Package podman provides a Sablier provider for Podman by wrapping the Docker provider. Podman exposes a Docker-compatible API..." The `Provider` struct (lines 21-23) embeds `*docker.Provider`; line 17 is the interface guard `var _ sablier.Provider = (*Provider)(nil)`; `New()` (lines 27-36) calls `docker.New(ctx, cli, logger, "stop")` at line 30.
- **Verdict:** ✅ CORRECT
- **Fix needed:** Line count fixed from 37 to 36 in the wiki.

## Claim 4: Multiple container orchestration providers (Docker, Docker Swarm, Podman, Kubernetes, Proxmox LXC)
- **Wiki says:** Sablier supports Docker, Docker Swarm, Podman, Kubernetes, and Proxmox LXC, each implementing the same `Provider` interface.
- **Source evidence:** `pkg/provider/` contains `docker/`, `dockerswarm/`, `kubernetes/`, `podman/`, `proxmoxlxc/`, plus `providertest/` shared test suite. `README.md` lines 399-472 document each provider (Docker socket, Swarm scale-to-0, Podman rootless, Kubernetes replica scaling, Proxmox API token + LXC lifecycle).
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Scale mode throttles idle workloads instead of stopping them
- **Wiki says:** Scale mode keeps containers running when idle but throttles CPU, memory, and (Docker-only) block I/O, restoring full resources on session arrival — zero cold-start latency.
- **Source evidence:** `README.md` lines 470-507: scale-mode explanation, the idle/active label table (`sablier.idle.replicas/cpu/memory`, `sablier.active.*`), and lines 504-507: `sablier.idle.blkio-weight` / `sablier.idle.blkio-device-*` marked "(Docker only)".
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Prometheus metrics and OpenTelemetry tracing
- **Wiki says:** Sablier exposes Prometheus metrics and supports OpenTelemetry tracing with OTLP export (W3C TraceContext propagation).
- **Source evidence:** `README.md` "Observability" section (lines 526-554); `pkg/metrics/` implements the metrics endpoint; `pkg/tracing/` implements OpenTelemetry. `sablier.sample.yaml` lines 311-334 show `tracing` config (`exporterType`, `endpoint`, `serviceName`, `samplingRate`) and `server.metrics.enabled`.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Blocking and dynamic startup strategies
- **Wiki says:** Two strategies: blocking (synchronous wait, HTTP 200) and dynamic (customizable waiting page).
- **Source evidence:** `internal/api/start_blocking.go` returns `HTTP 200` with `X-Sablier-Session-Status: ready`; `internal/api/start_dynamic.go` serves a waiting HTML page; themes in `internal/api/theme_list.go`; strategy config in `sablier.sample.yaml` lines 300-311 (`strategy.dynamic` custom-themes-path/show-details-by-default/default-theme, `strategy.blocking` default-timeout).
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: Go 1.26.3 toolchain; state store is inmemory/ + valkey/ (no tinykv); advanced lifecycle features
- **Wiki says:** Sablier is built with Go 1.26.3; the state store is `pkg/store/inmemory/` (in-memory TTL) plus `pkg/store/valkey/` (Redis-compatible via `valkey-go`); persistence is a file path (`SABLIER_STORAGE_FILE`). Additional features: anti-affinity, autostop/autowarm, running-hours windows, instance dependencies, group registry/watch.
- **Source evidence:**
  - `go.mod` line 3: `go 1.26.3`; line 29: `github.com/valkey-io/valkey-go v1.0.76`
  - `pkg/store/` contains only `inmemory/`, `store.go`, `storetest/`, `valkey/` — `pkg/store/tinykv/` does **not** exist
  - `pkg/config/storage.go` lines 1-16: `Storage` struct with `File` field, "Env: SABLIER_STORAGE_FILE", "CLI: --storage.file", "Default: \"\" (stateless)"
  - `pkg/sablier/anti_affinity.go`, `autostop.go`, `autowarm.go`, `running_hours.go`, `running_hours_watch.go`, `instance_dependency.go`, `group_registry.go`, `group_watch.go` — all present; README.md line 23 advertises anti-affinity
  - `go.mod` lines 7, 19, 21: `gin-gonic/gin v1.12.0`, `spf13/cobra v1.10.2`, `spf13/viper v1.21.0`
- **Verdict:** ✅ CORRECT (fixed: Go version bumped from "1.23+" to 1.26.3; tinykv row replaced with inmemory/ + valkey/ + storage config; advanced features added)
- **Fix needed:** Key Files table and Queue row updated in the wiki.

## Summary

All 8 key claims from the sablier wiki have been verified against the source:
- ✅ Scale-to-zero core + proxy plugins — README + internal/api/
- ✅ Podman = 36-line Docker wrapper — pkg/provider/podman/podman.go
- ✅ Five providers — pkg/provider/, README:399-472
- ✅ Scale mode + Docker-only blkio — README:470-507
- ✅ Prometheus + OTel — pkg/metrics/, pkg/tracing/
- ✅ Blocking/dynamic strategies — internal/api/start_*.go
- ✅ Go 1.26.3 + inmemory/valkey store (no tinykv) + SABLIER_STORAGE_FILE
- ✅ Anti-affinity, autostop/autowarm, running-hours, instance deps, group registry/watch

## Related

- [[sablier]] -- Main wiki entry
- [[podman]] -- Podman container engine
- [[crun-vm]] -- OCI runtime shim for VM containers
- [[mission-control]] -- MCP audit server

## Cross-project

- [[podman.codegraph-verify]] -- Podman verification
- [[buildah.codegraph-verify]] -- Buildah verification
