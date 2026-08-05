---
name: sablier
tags: [container, docker, podman, quadlet, reverse-proxy, sablier, scale-to-zero, systemd, webhook, wiki, golang]
description: "Scale-to-zero reverse proxy for containerized services"
source: sources/sablier/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Sablier

Scale-to-zero daemon for containerized workloads. Manages container lifecycle based on demand via reverse proxy plugin integration.

---

## Queue

| Key | Value |
|-----|-------|
| Origin | [sablierapp/sablier](https://github.com/sablierapp/sablier) |
| License | Apache 2.0 |
| Stack | Go 1.26.3, Gin HTTP framework, Cobra/Viper CLI |
| Source | `sources/sablier/` |
| Wanted | Scale-to-zero for agent services (Hermes, OpenClaw, n8n) on constrained VPS |

## Overview

- **Purpose**: Stop idle containers, start them on demand via reverse proxy interception
- **Language**: Go
- **Image**: `sablierapp/sablier` (Docker Hub) / `ghcr.io/sablierapp/sablier` (GHCR)
- **Image size**: ~20MB (scratch-based, multi-stage build)
- **Port**: 10000
- **License**: Apache 2.0

## Core Concept

Session-based idle detection. A reverse proxy plugin (Traefik, Caddy, Nginx, Envoy, Istio, APISIX) intercepts requests, calls Sablier's blocking API, Sablier starts the container and returns when healthy, then the proxy forwards the request. The session timer resets on each request; after inactivity exceeding `session_duration`, Sablier stops the container.

## Providers

| Provider | Socket/Endpoint | Stop Method | Scale Mode |
|----------|----------------|-------------|------------|
| Docker | `/var/run/docker.sock` | Stop/Pause | Yes |
| Podman | `/run/podman/podman.sock` | Stop/Pause | Yes |
| Docker Swarm | Docker socket | Replicas=0 | Yes |
| Kubernetes | In-cluster config | Replicas=0 | Yes |
| Proxmox LXC | Proxmox VE API | Stop | No |

## Key Labels

- `sablier.enable` -- Enable Sablier management
- `sablier.group` -- Group name for the container
- `sablier.running-hours` -- Scheduled uptime window (e.g. "Mon-Fri 09:00-17:00")
- `sablier.ready-after` -- Grace period after readiness (e.g. "30s")
- `sablier.idle.replicas` / `sablier.idle.cpu` / `sablier.idle.memory` -- Scale mode idle resources
- `sablier.active.replicas` / `sablier.active.cpu` / `sablier.active.memory` -- Scale mode active resources

## Scale Mode

Alternative to stop/start. Throttles CPU/memory at idle instead of stopping. Zero cold-start latency. Enable with `sablier.idle.replicas=1`. Block I/O throttling (`sablier.idle.blkio-weight` / `sablier.idle.blkio-device-*`) is **Docker-only** (README:504-507).

## Advanced Features

- **Anti-affinity** (`pkg/sablier/anti_affinity.go`): a workload backs off automatically (stopped or throttled to idle in scale mode) while another declared group is active — avoids GPU/RAM contention. Labels: `sablier.anti-affinity=<group>` (comma-separated groups allowed).
- **Autostop / Autowarm** (`autostop.go`, `autowarm.go`): scheduled stop and pre-warm of workloads.
- **Running-hours windows** (`running_hours.go`, `running_hours_watch.go`): `sablier.running-hours` restricts operation to scheduled uptime windows (e.g. "Mon-Fri 09:00-17:00"), with a watcher that reacts to window boundaries.
- **Instance dependencies** (`instance_dependency.go`): declare dependencies between instances so dependent workloads start/stop in order.
- **Group registry & watch** (`group_registry.go`, `group_watch.go`): group membership tracking and reactive updates when group labels change.

## Webhooks

Fire-and-forget HTTP POST on start/stop events. Payload: `{"event": "started"|"stopped", "instance": {"name": "..."}, "timestamp": "..."}` — normalized, provider-agnostic (dispatcher.go:29-42). 10s timeout, no retry; delivery is best-effort and must not block the event loop (dispatcher.go:137-139).

## Key Files (Source Repo)

| Path | Purpose |
|------|---------|
| `pkg/sablier/provider.go` | Provider interface |
| `pkg/sablier/instance_request.go` | Session orchestration, dedup |
| `pkg/provider/docker/` | Docker provider |
| `pkg/provider/podman/podman.go` | Podman provider (36-line Docker wrapper) |
| `pkg/store/inmemory/` | In-memory session store with TTL expiration |
| `pkg/store/valkey/` | Valkey-backed session store (Redis-compatible, `valkey-go` dep) |
| `pkg/config/storage.go` | State persistence config — file path via `SABLIER_STORAGE_FILE` (empty = stateless) |
| `internal/api/start_blocking.go` | Blocking strategy endpoint |
| `internal/api/start_dynamic.go` | Dynamic strategy (waiting page) |
| `pkg/theme/` | Waiting page themes |
| `pkg/metrics/` | Prometheus metrics |
| `pkg/tracing/` | OpenTelemetry tracing |
| `pkg/webhook/` | Webhook dispatcher |

## Related

- [Architecture](domains/architecture/sablier-architecture.md) — Scale-to-zero flow, request dedup, session expiry, proxy plugin model
- [Deployment](domains/deployment/sablier-deployment.md) — Traefik/Caddy/Nginx/Envoy configs, agent service examples
- [Quadlet Config](assets/deployment/sablier-quadlet.md) — Standalone, Traefik-integrated, agent service examples
- [[sablier-architecture]] -- Architecture deep-dive, boot flow, provider layer
- [[sablier-deployment]] -- Deployment guide for Docker, Podman, Kubernetes
- [[sablier-quadlet]] -- Quadlet `.container` files for rootless Podman

## Cross-project

- [[podman]] -- Podman provider support for scale-to-zero
- [[hermes-agent]] -- Scale-to-zero for Hermes agent services
- [[openclaw]] -- Scale-to-zero for OpenClaw agent services
- [[n8n]] -- Scale-to-zero for n8n workflow services
- [[agentfield]] -- Scale-to-zero for AgentField control plane
- [[mission-control]] -- Scale-to-zero for Mission Control dashboard
- [[nix-podman-stacks]] -- Sablier integration in Nix-managed stacks
