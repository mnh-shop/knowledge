---
name: agentfield-deployment
tags: [agentfield, cli, container, control-plane, deployment, docker, git, golang, harness, identity, monitoring, orchestration, plugin-sdk, podman, quadlet, security, storage, systemd, webhook]
description: "AgentField deployment guide: local dev, Docker Compose (pgvector), Helm/Kubernetes, production operations, and the desktop app"
source: sources/agentfield/
---

# AgentField Deployment Guide
**Source:** `sources/agentfield/`

**Status:** Active research target  

---

## Table of Contents

1. [System Requirements](#1-system-requirements)
2. [Local Development](#2-local-development)
3. [Docker Compose (PostgreSQL)](#3-docker-compose-postgresql)
4. [Configuration Reference](#4-configuration-reference)
5. [Secrets and Credentials](#5-secrets-and-credentials)
6. [Quadlet Deployment (Rootless Podman)](#6-quadlet-deployment-rootless-podman)
7. [Ecosystem Agent Deployment](#7-ecosystem-agent-deployment)
8. [Helm/Kubernetes](#8-helmkubernetes)
9. [Desktop App and Menu-Bar Companion](#9-desktop-app-and-menu-bar-companion)
10. [Release Builds](#10-release-builds)

---

## 1. System Requirements

### Development

| Component | Version | Notes |
|-----------|---------|-------|
| Go | 1.23+ (1.25 in Dockerfile) | CGO required for SQLite + sqlite_fts5 |
| Python | 3.10+ (<3.14) | Python SDK supports 3.10-3.13 |
| Node.js | 20+ | For web UI build + TypeScript SDK |
| PostgreSQL | 15+ | Required for cloud/production mode; pgvector extension needed |
| Docker | 20+ | For Docker Compose deployments |
| Air | optional | Auto-reload for Go server development (watches .go files; not required — `af dev --watch` covers agent packages) |

### Production Minimum (Local/SQLite Mode)

- Linux x86_64 or arm64 (macOS for development only)
- Disk space: 100 MB for binary + variable for SQLite database
- No external databases required

### Production Recommended (PostgreSQL Mode)

- PostgreSQL 15+ with pgvector extension
- 1 GB+ RAM for control plane (goroutine-based, scales with worker count)
- Persistent volume for `/data` (keys, telemetry ID, config overrides)

### Docker Image Sizes

| Image | Base | Approximate Size |
|-------|------|------------------|
| Control plane | `gcr.io/distroless/base-debian12` | ~50 MB (Go binary ~20 MB + static assets) |
| Python agent | `python:3.11-slim` | ~120 MB |
| Go agent | `gcr.io/distroless/static-debian12:nonroot` | ~15 MB |
| PostgreSQL | `pgvector/pgvector:pg16` | ~400 MB |

---

## 2. Local Development

### Single-Binary Server Mode (No Dependencies)

Bare `af` defaults to server mode (`root.go:37` — the root command's `Run` is the server function); `af server` is the explicit alias.

```bash
cd control-plane
go run ./cmd/af        # bare `af` = server mode
# or
go run ./cmd/af server
```

This starts the control plane with:
- SQLite (with FTS5 via `sqlite_fts5` build tag) for relational data
- BoltDB for KV storage
- Data under `~/.agentfield/data/`
- No PostgreSQL, no Redis, no external database required

### Agent Package Dev Mode (`af dev`)

`af dev [path]` runs an **AgentField agent package** in development mode — NOT the control plane. It looks for `agentfield.yaml` in the current directory (or the specified path), starts the agent without requiring installation, and auto-restarts on file changes (`commands/dev.go:37`).

```bash
af dev                    # Run package in current directory
af dev ./my-agent         # Run package in specified directory
af dev --port 8005        # Use a specific port
af dev --watch            # Watch for changes and auto-restart
```

Flags: `--port/-p`, `--watch/-w` (auto-restart on file changes), `--verbose/-v`. Watch/auto-restart is provided exclusively by `--watch`/`-w` — the CLI ships no alternative reload flag.

### Go Server Dev Loop (Optional Air)

For iterating on the Go server binary itself, Air can watch `.go`, `.yaml`, `.yml` files using `.air.toml` in `control-plane/`:

```bash
# Uses .air.toml in control-plane/
air
```

Rebuild command (as configured in `.air.toml`):
```
go build -tags 'sqlite_fts5' -o ./tmp/agentfield-server ./cmd/agentfield-server
```

### Dev with PostgreSQL (Optional, for Parity Testing)

```bash
# Start pgvector in Docker:
docker compose -f control-plane/docker-compose.dev.yml up

# Source the dev env and run:
source control-plane/.env.dev
go run ./cmd/agentfield-server
```

`.env.dev` sets `AGENTFIELD_STORAGE_MODE=postgresql` with auto-migration enabled.

### UI Development

```bash
cd control-plane/web/client
npm install && npm run dev   # Vite on :5173

# In parallel:
cd control-plane && go run ./cmd/agentfield-server
```

The Vite dev server proxies API calls to the Go backend. Production embeds the built UI via Go's `embed` package.

---

## 3. Docker Compose (PostgreSQL)

### File Location

`sources/agentfield/deployments/docker/docker-compose.yml`

### Services

| Service | Image | Purpose |
|---------|-------|---------|
| `postgres` | `pgvector/pgvector:pg16` | Relational DB with pgvector extension |
| `control-plane` | custom build from `Dockerfile.control-plane` | REST/gRPC API + UI + execution engine |
| `demo-go-agent` | custom build from `Dockerfile.demo-go-agent` | Go agent with demo skills (deterministic) |
| `demo-python-agent` | custom build from `Dockerfile.demo-python-agent` | Python agent with demo skills (profile: python-demo) |

### Startup

```bash
cd deployments/docker
docker compose --profile python-demo up --build
```

Available at `http://localhost:8080/ui/`.

### Control Plane Dockerfile (Multi-Stage Build)

1. **Stage 1: UI** (`node:20-alpine`) -- `npm ci`, `npx vite build`
2. **Stage 2: Go** (`golang:1.25-bookworm`) -- `go build -tags "embedded sqlite_fts5" -o /app/bin/agentfield-server ./cmd/agentfield-server`. Cross-compile via `BUILDPLATFORM`/`TARGETOS`/`TARGETARCH`. Requires `build-essential`, `pkg-config` plus optional `gcc-aarch64-linux-gnu`/`libc6-dev-arm64-cross` for arm64. Pre-creates `/tmp/agentfield-data` owned by UID 65532 (nonroot in distroless).
3. **Stage 3: Runtime** (`gcr.io/distroless/base-debian12`) -- copies binary + config dir + data directory. Runs as `nonroot:nonroot`. Entrypoint: `/usr/local/bin/agentfield-server`.

### Agent Dockerfiles

- **Go agent:** `golang:1.25-alpine` builder, `gcr.io/distroless/static-debian12:nonroot` runtime. `CGO_ENABLED=0`.
- **Python agent:** `python:3.11-slim` base. Installs Python SDK from local source (`pip install /tmp/python-sdk`), copies demo agent source. Exposes port 8001.

### Network and Callback

- Agents and control plane communicate over the Docker Compose network by service name.
- The control plane reaches agents at their registered `AGENT_CALLBACK_URL` (Python) or `AGENT_PUBLIC_URL` (Go).
- For agents outside Docker: use `host.docker.internal`.

### Persistence

- `pgdata` volume: PostgreSQL data at `/var/lib/postgresql/data`
- `agentfield-data` volume: Control plane data at `/data` (keys, telemetry ID, etc.)

### Functional Test Compose Files

Additional compose files under `tests/functional/docker/`:
- `docker-compose.local.yml` -- control plane (SQLite) + test-runner with pytest
- `docker-compose.postgres.yml` -- control plane (PostgreSQL) + pgvector:pg16 + test-runner
- `docker-compose.log-demo.yml` -- full observability demo with Python, Go, and TypeScript agents emitting NDJSON process logs

---

## 4. Configuration Reference

Configuration uses Viper with this precedence (highest wins):
1. Environment variables
2. Config YAML file
3. Built-in defaults

### Config File

Default location: `control-plane/config/agentfield.yaml` (dev) or overridden via `AGENTFIELD_CONFIG_FILE`.

### Config Sections

| Section | Purpose |
|---------|---------|
| `agentfield.*` | Server settings (port, execution queue params, cleanup policy, webhooks, approval) |
| `storage.*` | Storage mode (`local`/`postgres`/`cloud`), connection strings, vector store (cosine distance) |
| `ui.*` | Enable/disable, mode (`embedded`/`development`), dev port |
| `api.*` | CORS config, auth (insecure for dev, API key for prod) |
| `features.did.*` | Decentralized Identity (Ed25519 keys, BIP32 derivation, VC requirements, keystore with AES-256-GCM) |
| `features.tracing.*` | OpenTelemetry export (OTLP HTTP/gRPC) |
| `features.connector.*` | Agent connector with token-based auth |
| `telemetry.*` | Anonymous usage telemetry to agentfield.ai |

### Environment Variables

**Core:**
| Variable | Default | Description |
|----------|---------|-------------|
| `AGENTFIELD_PORT` | 8080 | HTTP listen port |
| `AGENTFIELD_MODE` | local | `local` or `cloud` |
| `AGENTFIELD_CONFIG_FILE` | - | Path to YAML config |

**Storage:**
| Variable | Default | Description |
|----------|---------|-------------|
| `AGENTFIELD_STORAGE_MODE` | local | `local`, `postgresql`, or `cloud` |
| `AGENTFIELD_STORAGE_LOCAL_DATABASE_PATH` | - | SQLite path for local mode |
| `AGENTFIELD_STORAGE_LOCAL_KV_STORE_PATH` | - | BoltDB path for local mode |
| `AGENTFIELD_STORAGE_POSTGRES_URL` | - | PostgreSQL DSN when mode=postgresql |
| `AGENTFIELD_DATABASE_URL` | - | Alternative alias for PostgreSQL DSN |
| `AGENTFIELD_STORAGE_POSTGRES_MAX_CONNECTIONS` | 25 | PostgreSQL connection pool |
| `AGENTFIELD_STORAGE_POSTGRES_ENABLE_AUTO_MIGRATION` | false | Auto-run Goose migrations on startup |

**Environment Variable Inventory:** `control-plane/.env.example` documents **43 `AGENTFIELD_*` variables** covering UI, CORS/API, cloud mode, storage (local/postgres/cloud), execution, and telemetry. `AGENTFIELD_CONFIG_FILE` points the server at an explicit YAML config; without it the server looks for `agentfield.yaml` in `.` or `./config`.

**Telemetry:**
| Variable | Default | Description |
|----------|---------|-------------|
| `AGENTFIELD_TELEMETRY_ENABLED` | true | Toggle anonymous usage telemetry |
| `AGENTFIELD_TELEMETRY_ENDPOINT` | `https://agentfield.ai/api/oss/telemetry` | OTLP/HTTP telemetry endpoint |
| `AGENTFIELD_TELEMETRY_INSTALL_ID` | - | Install identifier for dedup |

Set `AGENTFIELD_TELEMETRY_ENABLED=false` to disable telemetry entirely (the Docker Compose file forwards both variables, defaulting enabled to true).

**Execution Queue (YAML config):**
| Parameter | Default | Description |
|-----------|---------|-------------|
| `worker_count` | 16 | Concurrent goroutine workers |
| `agent_call_timeout` | 1800s | Timeout for agent HTTP calls |
| `request_timeout` | 180s | Overall request timeout |
| `queue_soft_limit` | 10000 | Max queued executions before backpressure |
| `lease_duration` | 180s | Lease time for work items |
| `poll_interval` | 100ms | How often workers poll for new work |
| `webhook_timeout` | 10s | Per-attempt webhook delivery timeout |
| `webhook_max_attempts` | 3 | Delivery retries |

**Execution Cleanup (YAML config):**
| Parameter | Default | Description |
|-----------|---------|-------------|
| `retention_period` | 72h | Executions older than this are deleted |
| `cleanup_interval` | 5m | How often cleanup runs |
| `batch_size` | 200 | Deletes per batch |
| `preserve_recent_duration` | 1h | Don't touch executions newer than this |
| `stale_execution_timeout` | 10m | Stale executions get marked failed |

**Helm Defaults:**
The Helm chart sets `AGENTFIELD_CONFIG_FILE=/dev/null` -- the control plane uses built-in defaults + environment variables only, no bundled YAML. Fully declarative via Helm values.

---

## 5. Secrets and Credentials

### API Authentication

| Mode | Configuration | Header |
|------|--------------|--------|
| Insecure (dev) | `api.auth.insecure_disable_auth: true` | None |
| API Key (production) | `AGENTFIELD_API_KEY` | `X-API-Key` |

### Auth Tokens

| Token | Env Variable | Purpose |
|-------|-------------|---------|
| Admin Token | `AGENTFIELD_AUTHORIZATION_ADMIN_TOKEN` | Protects admin endpoints (tag approval, policy management). Default in dev: `admin-secret` |
| Internal Token | `AGENTFIELD_AUTHORIZATION_INTERNAL_TOKEN` | Sent to agents during request forwarding. Agents with `RequireOriginAuth=true` validate this to ensure only the control plane can invoke them |
| Approval Webhook Secret | `AGENTFIELD_APPROVAL_WEBHOOK_SECRET` | HMAC key for approval webhook callback verification |
| Connector Token | `features.connector.token` in YAML | Authenticates agent connectors |

### Encrypted Secret Store (`af secrets`)

Node secrets (e.g. `GH_TOKEN`, LLM provider keys) declared as `type: secret` in an agent's `user_environment` section of `agentfield-package.yaml` are stored in an **encrypted store under `~/.agentfield`** (`secrets.go:19`):

```bash
af secrets set KEY [VALUE]   # store a secret (prompt hidden if VALUE omitted)
af secrets ls                # list stored secrets (values masked; alias: list)
af secrets rm KEY            # remove a secret (aliases: remove, delete)
```

- Encryption at rest: **AES-256-GCM**; decrypted only on demand
- Secrets are injected into agents via the `user_environment` mechanism when a node is run/installed — `user_environment.required` entries prompt on first run and are remembered encrypted; `type: secret` hides input and stores it encrypted (see `docs/installing-agent-nodes.md`)
- Scope: `global` (default, shared across nodes) or `node` (this node only)

### DID/VC Cryptographic Keys

- Algorithm: Ed25519
- Derivation: BIP32
- Keystore: Local filesystem at `<data_dir>/keys/` (default: `~/.agentfield/data/keys`)
- Encryption: AES-256-GCM (at rest)
- Auto-backup: Every 24h (configurable)
- Key rotation: Every 90 days (configurable)

Auto-generated on first run. No manual key provisioning needed, but the keystore directory must be persisted for production.

> **Backup = copy the keystore directory.** The `af vc` command surface exposes **only `verify`** (plus the `verify` alias) — no export/import subcommands exist in `vc.go`. Backing up DID keys means copying `<data_dir>/keys/` (see [DID Key Management](#did-key-management)).

### LLM Provider Credentials

Passed directly to agents, not stored in the control plane. Agents need their own:
- `OPENROUTER_API_KEY` (functional tests use this)
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`
- `OPENROUTER_MODEL` (functional tests default to `google/gemini-2.5-flash-lite`)

### Air-Gapped / Offline Deployments

The Connector feature is a **token-authenticated REST surface** (`/api/v1/connector/*`, registered only when `features.connector.enabled` and `features.connector.token` are set — `routes_connector.go:22-28`) plus a config-management sub-route gated by a `config_management` capability. It is well suited to air-gapped control: external integrations authenticate with the connector token (no public internet or outbound WebSocket channel required), and agent↔control-plane communication is ordinary HTTP callbacks over the local network. The runtime has no hypervisor or virtual-machine dependency — agent nodes are plain processes/containers reached over HTTP.

### Helm Secrets

The chart creates a Secret for PostgreSQL credentials (`postgres-secret.yaml`) and optionally for API auth (`api-auth-secret.yaml`). Both support `existingSecret` for BYO secret management.

### No Secrets Required for Initial Run

AgentField in local mode with PostgreSQL disabled starts instantly with no credentials. All auth is optional and enabled explicitly for production hardening.

---

## 6. Quadlet Deployment (Rootless Podman)

See `assets/deployment/agentfield-quadlet.md` for a dedicated Quadlet deployment guide.

Key points for AgentField with Quadlet:
- The single Go binary (no dependencies) maps cleanly to a single `.container` Quadlet unit
- No Redis/external queue eliminates sidecar dependencies
- Distroless base image is Quadlet-friendly; use `curl` health checks from the host namespace
- PostgreSQL mode needs two Quadlet units (postgres + control-plane) with an `After=` dependency

---

## 7. Ecosystem Agent Deployment

SWE-AF, sec-af, af-deep-research, af-reactive-atlas-mongodb are ecosystem agent nodes that register with the AgentField control plane. Each runs as a separate unit that:

1. Starts after the control plane is healthy
2. Connects via `AGENTFIELD_URL=http://agentfield:8080`
3. Registers its agent ID and skills/reasoners
4. Listens on a callback port the control plane uses for execution requests

### General Pattern

Each ecosystem agent needs:
- Its own unit with a unique port (8002-8005 typically)
- Its own LLM API keys (injected via environment)
- No direct coupling to each other -- only to the control plane
- Container name DNS resolution on the Podman default bridge

### SDK Agent Images

The repo ships base Dockerfiles for building any agent:
- `Dockerfile.python-agent`: `python:3.11-slim` with Python SDK pre-installed. Override CMD.
- `Dockerfile.go-agent`: `golang:1.25-alpine` with Go SDK pre-downloaded. Override CMD.
- `Dockerfile.tmpl`: Generated by `af init <name>` -- single-stage Python 3.11-slim build with SDK pip-installed from source.

Pre-built images:
- `ghcr.io/agent-field/agentfield:latest` -- control plane
- `ghcr.io/agent-field/init-example:latest` -- demo init example agent

---

## 8. Helm/Kubernetes

The Helm chart is at `deployments/helm/agentfield/`:
- `values.yaml` (109 lines) + `values.schema.json` (JSON Schema validation, 91 lines)
- Configurable replicas for horizontal scaling
- Persistent volumes for PostgreSQL (5Gi default, with pgvector/pgvector:pg16 image)
- Ingress configuration with TLS support
- Multi-agent deployment support (demo Go agent + demo Python agent)
- Sets `AGENTFIELD_CONFIG_FILE=/dev/null` to use built-in defaults + helm values only (fully declarative)
- **Admin gRPC:** the control plane runs an `AdminReasonerService` on the gRPC port (`server.go:712-738`), which is **HTTP port + 100** (8180 by default; `values.yaml` `controlPlane.service.grpcPort: 0` = auto-compute). The gRPC server is protected by the API key via a unary interceptor when `api.auth.apiKey` is configured.

### Helm Values Breakdown

**Control Plane (`controlPlane`):**
| Parameter | Default | Description |
|-----------|---------|-------------|
| `replicaCount` | 1 | Horizontal replicas (stateless) |
| `image.repository` | `agentfield/control-plane` | Container image |
| `image.tag` | `latest` | Image tag |
| `service.type` | `ClusterIP` | Kubernetes service type |
| `service.port` | 8080 | HTTP port |
| `service.grpcPort` | 0 | Admin gRPC port (auto: port+100) |
| `ingress.enabled` | false | Ingress controller |
| `storage.mode` | `local` | `local` (SQLite/Bolt) or `postgres` |
| `storage.postgresUrl` | `""` | PostgreSQL DSN (auto-wired if empty and `postgres.enabled=true`) |
| `persistence.enabled` | true | PVC for control plane data |
| `persistence.size` | 1Gi | Data volume size |
| `env.AGENTFIELD_CONFIG_FILE` | `/dev/null` | No bundled YAML; use env vars only |

**PostgreSQL (`postgres`):**
| Parameter | Default | Description |
|-----------|---------|-------------|
| `enabled` | false | Deploy pgvector container |
| `image.repository` | `pgvector/pgvector` | PostgreSQL with pgvector |
| `image.tag` | `pg16` | PG16 variant |
| `auth.username` | `agentfield` | DB user |
| `auth.password` | `agentfield` | DB password |
| `auth.database` | `agentfield` | DB name |
| `auth.existingSecret` | `""` | BYO secret for credentials |
| `persistence.size` | 5Gi | PostgreSQL volume size |

**Demo Agents:**
| Parameter | Default | Description |
|-----------|---------|-------------|
| `demoAgent.enabled` | false | Deploy Go demo agent |
| `demoAgent.image.repository` | `agentfield-demo-go-agent` | Build locally from `Dockerfile.demo-go-agent` |
| `demoAgent.nodeId` | `demo-go-agent` | Agent node ID |
| `demoPythonAgent.enabled` | false | Deploy Python demo agent (installs SDK from PyPI at startup) |
| `demoPythonAgent.pipPackage` | `agentfield` | PyPI package to install |

### Template Files

| Template | Purpose |
|----------|---------|
| `control-plane-deployment.yaml` | Main deployment with replica count, env, probes |
| `control-plane-service.yaml` | ClusterIP service for the control plane |
| `control-plane-ingress.yaml` | Optional ingress with host/TLS config |
| `control-plane-pvc.yaml` | Persistent volume claim for data directory |
| `postgres-statefulset.yaml` | PostgreSQL statefulset with pgvector |
| `postgres-service.yaml` | PostgreSQL service |
| `postgres-secret.yaml` | PostgreSQL credentials secret |
| `api-auth-secret.yaml` | API key and auth secrets |
| `demo-agent-deployment.yaml` | Go demo agent deployment |
| `demo-agent-service.yaml` | Go demo agent service |
| `demo-python-agent-deployment.yaml` | Python demo agent deployment |
| `demo-python-agent-service.yaml` | Python demo agent service |
| `demo-python-agent-configmap.yaml` | Python agent config |
| `_helpers.tpl` | Common template helpers |
| `NOTES.txt` | Post-install notes |

### Helm Installation

```bash
helm repo add agentfield https://agent-field.github.io/helm-charts
helm install agentfield agentfield/agentfield \
  --set postgres.enabled=true \
  --set controlPlane.storage.mode=postgres
```

### Agent Registration Flow in Helm

1. PostgreSQL starts first (statefulset with health check via `pg_isready`)
2. Control plane starts and auto-runs Goose migrations when `AGENTFIELD_STORAGE_POSTGRES_ENABLE_AUTO_MIGRATION=true`
3. Demo agents start and register with the control plane
4. The control plane tracks agent health via heartbeats and periodic health checks
5. Agents are accessible at `POST /api/v1/execute/{agent_id}.{reasoner_id}`

---

## 8.5 Production Operations

### Scaling

The control plane is **stateless** (all state in PostgreSQL). Horizontal scaling is additive:
```bash
kubectl scale deployment agentfield-control-plane --replicas=3
```

Or via Helm:
```yaml
controlPlane:
  replicaCount: 3
```

No shared state coordination needed. Each replica independently:
- Accepts agent registrations (DB-backed)
- Queues and executes work (goroutine worker pool)
- Serves the embedded web UI
- Runs a gRPC admin server on port +100

### DID Key Management

Keys are auto-generated on first run. For production:

- **Backup**: The keystore directory (`<data_dir>/keys/`, default `~/.agentfield/data/keys`) must be backed up. Losing keys invalidates all existing DIDs and VCs. **The `af vc` surface only exposes `verify`** — no export/import subcommand exists. Backing up keys means copying the keystore directory (below).
- **Rotation**: Auto-rotation every 90 days (configurable via `features.did.key_rotation_days`). Rotated keys remain valid for verification but are no longer used for signing new credentials. A companion `x25519gen` utility (`cmd/x25519gen`) derives the X25519 key-agreement keypair for the DID service (HKDF-SHA256 with salt `agentfield-did-keyagreement-v1`, info `<path>/enc/<epoch>`), used for interop cross-checks with the SDK crypto layer.
- **Restore**: Copy the keystore directory to the new deployment. Keys are AES-256-GCM encrypted at rest (requires `encryption_passphrase` if configured).

```bash
# Backup
tar czf agentfield-keys-backup-$(date +%Y%m%d).tar.gz ~/.agentfield/data/keys/

# Restore
tar xzf agentfield-keys-backup-*.tar.gz -C ~/.agentfield/
```

### Agent Update Strategy

Agent versions are tracked via `agent_instance_id` (per-process UUID). When an agent redeploys:
1. New process gets a new `agent_instance_id`
2. Control plane detects the change on first heartbeat
3. In-flight executions from the previous `agent_instance_id` are failed with `agent_redeployed`
4. New executions route to the new instance

Canary deployments use traffic weight routing:
```http
PUT /api/v1/connector/reasoners/:id/versions/:version/weight
Body: {"weight": 50}  // 50% of traffic
```

### Backup and Restore

**PostgreSQL mode:**
```bash
pg_dump -h localhost -U agentfield agentfield > agentfield-backup.sql
psql -h localhost -U agentfield agentfield < agentfield-backup.sql
```

**Local mode (SQLite):**
```bash
# Backup while control plane is stopped
cp ~/.agentfield/data/agentfield_local.db agentfield-backup.db
cp -r ~/.agentfield/data/keys agentfield-keys-backup/
```

### Monitoring

Built-in observability surface:

| Endpoint | Purpose | Format |
|----------|---------|--------|
| `GET /metrics` | Prometheus metrics | Prometheus text format (via `prometheus/client_golang`) |
| `GET /health` | Storage + cache health | JSON with per-check status |
| `GET /api/ui/v1/queue/status` | Execution queue depth | JSON |
| `GET /api/ui/v1/llm/health` | LLM backend health (circuit breaker) | JSON |
| `GET /api/ui/v1/dashboard/*` | Dashboard summary | JSON |

OpenTelemetry tracing: configurable via `features.tracing.*` with OTLP HTTP/gRPC export.

### Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Control plane won't start (PostgreSQL mode) | Database not running or wrong URL | Check `AGENTFIELD_DATABASE_URL` and PostgreSQL status |
| `migration failed` on startup | Schema version mismatch | Set `AGENTFIELD_STORAGE_POSTGRES_ENABLE_AUTO_MIGRATION=true` or run `goose up` manually |
| Agent shows `offline` in UI | Heartbeat not received | Check agent can reach `AGENTFIELD_URL`. Check agent's `AGENT_CALLBACK_URL` is reachable from control plane |
| `401 unauthorized` on API calls | Missing or wrong API key | Check `AGENTFIELD_API_KEY` matches what clients send |
| `403 policy_denied` | Tag policy blocking execution | Check `access_policies` in config, or check agent tags |
| `did_not_registered` | Agent's DID not registered | Check agent registration succeeded. If running in local mode, restart both CP and agent |
| Async execution stuck in `queued` | Worker pool full or agent unreachable | Check `GET /api/ui/v1/queue/status`. Increase `worker_count` |
| Web UI blank | Vite dev server not running (dev) or dist not built (prod) | In dev: `npm run dev`. In prod: rebuild with `embedded` tag |
| `connection pool exhausted` | Too many concurrent DB connections | Increase `AGENTFIELD_STORAGE_POSTGRES_MAX_CONNECTIONS` |
| `agent_redeployed` errors | Agent restarted mid-execution | Expected during rolling updates. Retry failed executions |

## 9. Desktop App and Menu-Bar Companion

### AgentField Desktop (Electron)

The `desktop/` directory ships an **Electron desktop dashboard** for the control plane and locally installed agent nodes. Built with electron-vite (TypeScript, React renderer); `electron-builder` packages it with the `af` and `af-tray` binaries bundled as `extraResources` (`vendor/` → `bin/`, filtered to `af`, `af.exe`, `af-tray`). Registers the `agentfield://` deep-link protocol.

- **Screens:** Home/Dashboard, Agents (marketplace-style library of installed + addable nodes), Activity (dense, filterable run history), Install (maps to the Agents view with add-mode), Settings
- **`af`-as-contract:** the desktop shells out to the CLI for all node operations — `af install <source>` (installer), `af run/stop <name>` (agents), plus `af skill`/`af list`/`af version` — the CLI is the single source of truth for the package registry
- **Autostart:** the app can start the local control plane and registered agents on launch (autostart plan); cold-launch goes to Home when agents exist, Agents add-mode when the library is empty
- **IPC:** sandboxed preload exposes `agentfield:*` IPC channels (snapshot, install, agent-action, start-control-plane, secrets, settings, cli-status, app-update) to the renderer; all `~/.agentfield` and control-plane HTTP reads live in one data-access module pointed at the active control-plane base URL (default `http://localhost:8080`)

Install the app, then point it at a local `af server` (or let autostart start one) — it manages the same `~/.agentfield` installation the CLI uses.

### af-tray (macOS Menu Bar)

`cmd/af-tray` is a **separate Go binary** for the macOS menu bar — it deliberately carries the systray/GUI dependency so the server binary never does (`af-tray/main.go`).

- Subcommands: `af-tray run` (default), `af-tray install` (provisions `~/Applications/AgentField.app` + launchd LaunchAgent autostart), `af-tray uninstall`, `af-tray version`
- Fleet status from the control plane, a **24h usage chart** (text-free image renderer, `chart_render.go`), and **Claude quota** rows (reads the user's Claude Code OAuth token from the macOS keychain, `claude_quota_darwin.go`)
- `launchd_darwin.go` registers a LaunchAgent for autostart; the desktop's `tray-companion.ts` manages provisioning (installs/reloads when the launchd agent is missing). Non-macOS builds get no-op stubs (`tray_other.go`); headless runs exit cleanly.

### Deployment Relationship

```
AgentField Desktop (Electron) ──HTTP──▶ local af server (control plane) ──▶ PostgreSQL (pgvector)
        │                                        │
        └──spawns af install/run/stop───────┐    └──spawns agent nodes (af run)
                                             ▼
                              ~/.agentfield (registry, secrets, keys)
```

## 10. Release Builds

`.goreleaser.yml` at repo root builds four platform binaries via `./cmd/af`:
- linux/amd64 (CGO_ENABLED=1, using system gcc)
- linux/arm64 (cross-compiled with aarch64-linux-gnu-gcc)
- darwin/amd64
- darwin/arm64

All builds use tags `embedded sqlite_fts5` and link flags `-s -w`. The `af` CLI is the single binary -- it can run as a server (`af server`, `af dev`) or as a CLI tool.

### Installer Script

`scripts/install.sh` at root:
1. Downloads correct binary from GitHub Releases
2. Verifies SHA256 checksum
3. Installs to `~/.agentfield/bin/`
4. Optionally configures PATH
5. Optionally installs the agentfield skill into detected coding agents (Claude Code, Codex, Gemini, Aider, etc.)
6. Latest version auto-detected from GitHub API

### Go Dependencies (control-plane)

| Library | Purpose |
|---------|---------|
| `gin-gonic/gin` | HTTP framework |
| `spf13/viper` + `spf13/cobra` | Config + CLI |
| `jackc/pgx/v5` | PostgreSQL driver |
| `mattn/go-sqlite3` | CGO-based SQLite driver |
| `modernc.org/sqlite` | Pure-Go SQLite driver (for builds without CGO) |
| `gorm.io/gorm` | ORM layer |
| `boltdb/bolt` | KV store |
| `go.opentelemetry.io/otel` | OpenTelemetry tracing |
| `prometheus/client_golang` | Metrics |
| `rs/zerolog` | Structured logging |
| `golang.org/x/crypto` | Ed25519 keys for DID |
| `google.golang.org/grpc` | gRPC API |
| `pressly/goose/v3` | Database migrations |

### Python SDK Dependencies

| Library | Purpose |
|---------|---------|
| `fastapi` + `uvicorn` | Agent HTTP server |
| `litellm` | Multi-provider LLM calls |
| `cryptography` + `joserfc` | JOSE/JWT for VC chains |
| `pydantic>=2.0` | Schema validation |
| `websockets` | Streaming execution |
| `aiohttp` | Async HTTP |

## Related

- [[agentfield]] -- wiki page for the platform
- [[agentfield-architecture]] -- system architecture
- [[agentfield-api]] -- REST API reference
- [[agentfield-cli]] -- `af` CLI command reference
- [[agentfield-desktop]] -- Electron desktop app + af-tray architecture
- [[agentfield-quadlet]] -- Quadlet deployment
- [[agentfield-mcp-server]] -- MCP bridge server
- [[hermes-profiles]] -- AgentField platform profile
- [[SWE-AF]] -- autonomous engineering factory
- [[sec-af]] -- security auditor agent
- [[af-deep-research]] -- deep research engine
- [[af-reactive-atlas-mongodb]] -- reactive MongoDB intelligence
