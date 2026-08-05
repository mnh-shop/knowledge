---
name: docker-netbird
tags: [docker, netbird, wireguard, vpn, ztna, rootless, distroless, container, networking, security, mit]
description: "Rootless, distroless Docker image for NetBird WireGuard overlay network with ZTNA — 70MB, no shell, single container, pinned semver build, multi-arch"
source: sources/docker-netbird/
verification_date: 2026-07-30
verified_by: codegraph-verify
---

# docker-netbird

**Source:** `sources/docker-netbird/`

A rootless and distroless Docker image for [NetBird](https://github.com/netbirdio/netbird) — a WireGuard-based overlay network with Zero Trust Network Access. This image combines all NetBird components (management server, dashboard UI, signal/relay) into a single 70MB container that runs as user 1000:1000 with no shell, no root, a read-only filesystem, and automatic CVE scanning. Since post-0.70.5 it ships the embedded IdP by default and uses the unified management binary with YAML config.

| Field | Value |
|---|---|
| **Origin** | [11notes/docker-netbird](https://github.com/11notes/docker-netbird) |
| **License** | MIT |
| **Stack** | Docker (scratch-based distroless), Go, NetBird, Nginx |
| **Image Size** | 70MB (vs 331MB for netbirdio/*) |
| **User** | 1000:1000 (rootless; `-unraid` → 99:100, `-nobody` → 65534:65534) |
| **Architectures** | amd64, arm64 |
| **Build** | Pinned semver `11notes/netbird:0.76.0` (no `:latest` tag) |
| **Database** | PostgreSQL only (distroless image cannot run SQLite) |
| **Registries** | Docker Hub, GHCR, Quay |
| **Source** | `sources/docker-netbird/` |
| **Codegraph** | `graphs/docker-netbird/` |

## What is it?

This image provides a hardened, single-container deployment of NetBird's self-hosted ZTNA mesh network. Unlike the official multi-container images (331MB, running as root `0:0`), this single 70MB image runs all NetBird services (management server, dashboard UI, signal/relay) rootless and distroless — no shell, no package manager, no unnecessary attack surface. It includes automatic health checks, CVE scanning, and env-var-based configuration with YAML template substitution and inline config support. The embedded IdP means no external identity provider is required for basic setups, though Keycloak or any external IdP can be added.

## Key Features

- **Rootless & Distroless** — Runs as user 1000:1000 with no shell, minimizing attack surface
- **Single Container** — Combines management, dashboard, signal, and relay into one image; the dashboard is started with the `--dashboard` command flag
- **70MB Image Size** — Dramatically smaller than the official 331MB multi-image deployment
- **Pinned Semver Builds** — No `:latest` tag; releases are pinned to exact versions (e.g. `0.76.0`), with short semver aliases `:0` / `:0.76` and an opt-in `:rolling` tag
- **Auto-Updated via CI/CD** — Pinned, reproducible multi-arch pipeline rebuilds on upstream releases
- **Health Check** — Built-in `localhealth` endpoint at `:9000/health` (checks only 127.0.0.1)
- **Read-Only Root Filesystem** — Only volumes at `/netbird/etc` and `/netbird/var` are writable; transient data goes to tmpfs
- **CVE Scanning** — Automatic grype scanning before and after publishing, fail-on-severity configurable
- **Env-Var Config** — All configuration via environment variables with `${VAR}` / `$VAR` YAML template substitution; inline configs supported
- **Embedded IdP** — Built-in identity provider (no external IdP required for basic setups)
- **PostgreSQL Backend** — All three stores (store, activityStore, authStore) use a Postgres engine
- **Multi-Arch** — Built for amd64 and arm64 via a platform-aware `arch.dockerfile`

## Tech Stack

| Layer | Technology |
|---|---|
| **Base Image** | Scratch (distroless layers: localhealth, nginx, curl) |
| **Overlay Network** | WireGuard (via NetBird) |
| **Dashboard** | Nginx (serves NetBird dashboard UI) |
| **Application** | NetBird unified management binary (Go, static, cgo-patched) |
| **Database** | PostgreSQL (external, required — no SQLite support) |
| **IdP** | Embedded Dex IdP by default (external IdP optional) |
| **Config** | YAML (`default.yml`) with env-var substitution, inline config support |
| **Health Check** | `localhealth` → HTTP `:9000/health` |
| **Metrics** | Prometheus endpoint on port 9090 |
| **Build** | `arch.dockerfile` multi-stage with TARGETPLATFORM/TARGETOS/TARGETARCH |

## Deployment

### Docker Compose

Condensed from the shipped `compose.yml` (image pinned at `0.76.0`, three services, internal backend network):

```yaml
name: "netbird"

x-lockdown: &lockdown
  read_only: true
  security_opt:
    - "no-new-privileges=true"

x-image-netbird: &image
  image: "11notes/netbird:0.76.0"
  <<: *lockdown

services:
  server:
    depends_on:
      postgres:
        condition: "service_healthy"
        restart: true
    <<: *image
    environment:
      TZ: "Europe/Zurich"
      NETBIRD_FQDN: "${NETBIRD_FQDN}"
      POSTGRES_PASSWORD: "${POSTGRES_PASSWORD}"
    volumes:
      - "server.etc:/netbird/etc"
      - "server.var:/netbird/var"
    tmpfs:
      - "/tmp:uid=1000,gid=1000"
    networks:
      frontend:
      backend:
    ports:
      - "3478:3478/udp"
      - "8080:8080/tcp"
    restart: "always"

  dashboard:
    <<: *image
    # start dashboard instead of management server
    command: "--dashboard"
    environment:
      TZ: "Europe/Zurich"
      NETBIRD_MGMT_API_ENDPOINT: "https://${NETBIRD_FQDN}"
      NETBIRD_MGMT_GRPC_API_ENDPOINT: "https://${NETBIRD_FQDN}"
      AUTH_AUTHORITY: "https://${NETBIRD_FQDN}/oauth2"
    volumes:
      - "dashboard.var:/nginx/var"
    tmpfs:
      - "/nginx/cache:uid=1000,gid=1000"
      - "/nginx/run:uid=1000,gid=1000"
    networks:
      frontend:
      backend:
    ports:
      - "3000:3000/tcp"
    restart: "always"

  postgres:
    # https://github.com/11notes/docker-postgres
    image: "11notes/postgres:18"
    <<: *lockdown
    environment:
      TZ: "Europe/Zurich"
      POSTGRES_PASSWORD: "${POSTGRES_PASSWORD}"
      POSTGRES_BACKUP_SCHEDULE: "0 3 * * *"
    volumes:
      - "postgres.etc:/postgres/etc"
      - "postgres.var:/postgres/var"
      - "postgres.backup:/postgres/backup"
    tmpfs:
      - "/postgres/run:uid=1000,gid=1000"
      - "/postgres/log:uid=1000,gid=1000"
    networks:
      backend:
    restart: "always"

volumes:
  server.etc:
  server.var:
  dashboard.var:
  postgres.etc:
  postgres.var:
  postgres.backup:

networks:
  frontend:
  backend:
    internal: true
```

### Volumes

| Path | Purpose |
|---|---|
| `/netbird/etc` | Configuration directory |
| `/netbird/var` | Dynamic runtime data (NetBird) |
| `/nginx/var` | Dashboard (nginx) runtime data |
| `/postgres/etc`, `/postgres/var`, `/postgres/backup` | Postgres config, data, and nightly backups |

### tmpfs Mounts

All transient paths run in memory (uid=1000,gid=1000) so the root filesystem stays read-only:

| Mount | Service |
|---|---|
| `/tmp` | server |
| `/nginx/cache`, `/nginx/run` | dashboard |
| `/postgres/run`, `/postgres/log` | postgres |

### Ports

| Port | Service | Source |
|---|---|---|
| 3478/udp | Signal / relay (WebRTC/DTLS) | compose `server` service |
| 8080/tcp | NetBird management API | compose `server` service |
| 3000/tcp | Dashboard UI (nginx) | compose `dashboard` service |
| 9000 | Health check (`localhealth`) | default config `healthcheckAddress` |
| 9090 | Metrics (Prometheus) | default config `metricsPort` |

**TLS note:** the container does not bind port 443. TLS terminates at a reverse proxy (Traefik/Nginx/HAProxy recommended); the default config only references it as a string — `exposedAddress: "https://${NETBIRD_FQDN}:443"` — used for the OAuth issuer and redirect URIs.

### Network Topology

- `frontend` network: server + dashboard (receives external traffic)
- `backend` network: **internal: true** — server, dashboard, and postgres; Postgres is never exposed to the frontend

### Postgres Backups

The `11notes/postgres:18` image runs a scheduled backup via `POSTGRES_BACKUP_SCHEDULE: "0 3 * * *"` (daily at 03:00), writing to the `postgres.backup` volume.

## Usage

### Environment Variables

| Variable | Purpose |
|---|---|
| `NETBIRD_FQDN` | Public hostname; substituted into `exposedAddress`, OAuth issuer, and dashboard redirect URIs |
| `POSTGRES_PASSWORD` | Password for the Postgres DSN (`host=postgres user=postgres dbname=postgres port=5432`) |
| `TZ` | Container timezone (e.g. `Europe/Zurich`) |
| `DEBUG` | Debug mode for image and app |

### Dashboard Environment

The dashboard service (nginx + NetBird UI) is configured via:

- `NETBIRD_MGMT_API_ENDPOINT` — management API base URL (`https://${NETBIRD_FQDN}`)
- `NETBIRD_MGMT_GRPC_API_ENDPOINT` — management gRPC endpoint
- `AUTH_AUTHORITY` — OAuth2 authority (`https://${NETBIRD_FQDN}/oauth2`)

### Tag Strategy

There is no `:latest`. Pinned tags include `0.76.0`, plus `-unraid` (runs as 99:100) and `-nobody` (runs as 65534:65534) variants. Short semver tags (`:0`, `:0.76`) track the latest minor/major, and `:rolling` tracks the bleeding edge (not recommended).

### Registries

```
docker pull 11notes/netbird:0.76.0
docker pull ghcr.io/11notes/netbird:0.76.0
docker pull quay.io/11notes/netbird:0.76.0
```

## Related

- [[netbird]] — NetBird: WireGuard-based overlay network with ZTNA (upstream project)
- [[podman]] — Container runtime (alternative to Docker for running this image)
- [[bootc]] — Bootable containers (deployment model compatible with rootless images)
