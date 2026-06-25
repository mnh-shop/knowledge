---
name: podman-api
description: "Podman REST API reference — Docker-compatible and native libpod endpoints"
source: sources/podman/
tags: [api, container, docker, gorilla-mux, podman, rest-api, systemd]
---

# Podman — API Reference

Podman's comprehensive REST API is documented in the [[podman-mcp-implementation]] domain doc (filed under `domains/mcp/` as "Podman does not implement MCP" — it documents the REST API server instead).

## Key API Facts

| Feature | Detail |
|---------|--------|
| **Transport** | Unix socket (`/run/podman/podman.sock`) or TCP |
| **HTTP Router** | gorilla/mux |
| **Surfaces** | Docker-compatible ("compat") + native Podman ("libpod") |
| **Handler groups** | 25 registration functions |
| **Spec** | OpenAPI via `swagger generate spec` |
| **Client library** | `pkg/bindings/` Go client library |

## Endpoint Categories

| Registry | Prefix | Description |
|----------|--------|-------------|
| `register_containers.go` | compat + libpod | Container CRUD, lifecycle, exec, logs |
| `register_images.go` | compat + libpod | Image operations |
| `register_pods.go` | libpod | Pod management |
| `register_networks.go` | compat + libpod | Network management |
| `register_volumes.go` | compat + libpod | Volume management |
| `register_quadlets.go` | libpod | Quadlet management |
| `register_secrets.go` | compat + libpod | Secret management |
| `register_system.go` | compat + libpod | System info, version, events |
| `register_kube.go` | libpod | Kubernetes YAML play/down |
| `register_healthcheck.go` | libpod | Container health checks |
| +15 more | — | Archive, artifacts, auth, distribution, exec, etc. |

## Full Reference

See [[podman-mcp-implementation]] for the complete API reference including:
- Transport options (Unix socket, TCP, systemd socket activation, TLS)
- Middleware chain (request ID, logging, panic recovery)
- Idle connection tracking
- Client bindings
- Systemd integration (service + socket units)
- 25 handler groups with endpoint details

## Related

- [[podman-mcp-implementation]] — Full REST API documentation
- [[podman-architecture]] — Container engine internals
- [[podman-deployment]] — Deployment guide
