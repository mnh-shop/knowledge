---
name: n8n-deployment
tags: [n8n, deployment, typescript, vue, workflow-automation, low-code, integration, fair-code, automation, webhook, ai-llm, cli, docker, event-bus, mcp, orchestration, security, storage, virtualization]
description: n8n — Deployment
---

# n8n — Deployment

**Source:** `sources/n8n/docker/`, `sources/n8n/packages/cli/src/scaling/`, `sources/n8n/packages/cli/src/task-runners/`

## Overview

n8n supports multiple deployment models — from single-process to distributed multi-main with dedicated workers. All deployment is self-hosted (n8n.cloud is managed by n8n).

## Docker Images

Images under `docker/images/`:

| Image | Base | Purpose |
|-------|------|---------|
| `n8n` | `node:24.16.0-alpine3.22` | Main n8n server — multi-arch (amd64 + arm64). Node 24.16.0. |
| `n8n-base` | Alpine | Base layer for n8n variants |
| `engine` | — | Workflow execution engine |
| `runners` | Distroless or Alpine | Task runners (Node.js + Python) |

### Docker Image Build

The main Dockerfile uses a multi-stage build:
1. **Builder stage**: Node 24.16.0 Alpine with full toolchain (python3, make, g++)
   - Rebuilds sqlite3 native module
   - Rebuilds `isolated-vm` from source (musl compatibility)
   - Multi-arch digest-pinned for reproducible builds
2. **Runtime stage**: Same Node base, copies compiled artifacts

### Task Runner Images (`docker/images/runners/`)

| File | Purpose |
|------|---------|
| `Dockerfile` | Standard runner image |
| `Dockerfile.distroless` | Minimal-distro runner (smaller, fewer CVEs) |
| `n8n-task-runners.json` | Runner configuration schema |

## Deployment Models

### 1. Single Process (Default)

```
n8n start
```

- All-in-one: server + execution engine + webhooks
- SQLite or PostgreSQL
- Simplest deployment, best for dev/small teams

### 2. Queue Mode (Redis + Workers)

```
n8n start        # Main server (queue mode)
n8n worker       # Worker process(es)
```

- **Main**: Handles HTTP, webhooks, API, orchestration
- **Workers**: Execute workflows, polled from Redis queue
- **Redis**: Bull queue manager, pub/sub event bus
- **PostgreSQL**: Shared database

### 3. Multi-Main (High Availability)

```
n8n start --multi-main-setup
```

- Multiple main instances share workload
- Leader election via Redis
- Webhook routing across instances
- State synchronization via Redis pub/sub
- **Available in queue mode only**

### 4. Docker Compose

Typical production stack:
- `n8n` container (main + optional worker)
- `postgres` (database)
- `redis` (queue + event bus + scaling)
- Optional: `traefik`/`nginx` (reverse proxy), `mailpit` (email testing), `proxy` (external service proxy)

## Scaling Architecture (`packages/cli/src/scaling/`)

Multi-main scaling coordination:

| Aspect | Mechanism |
|--------|-----------|
| Leader election | Redis-backed |
| Workflow distribution | Redis queue |
| State sync | Redis pub/sub |
| Webhook routing | Multi-instance aware |
| Execution offload | Workers consume from Redis |

### Task Runners

For Node.js (TypeScript) and Python:

| Runner | Tech | Execution Model |
|--------|------|----------------|
| `@n8n/task-runner` | Node.js | Receives tasks, executes in isolated contexts |
| `@n8n/task-runner-python` | Python | Pyodide (wasm) or native Python |

CLI module (`packages/cli/src/task-runners/`) manages runner lifecycle, connection pooling, and authentication.

## Database

| Database | Use Case | Driver |
|----------|----------|--------|
| SQLite | Dev/small deployments | `sqlite3` (native module) |
| PostgreSQL | Production | `pg` (via TypeORM) |

TypeORM with entity files in `packages/cli/src/databases/` and repositories via `@n8n/db`.

## Configuration

Environment variables for all settings. Key ones:

| Variable | Purpose |
|----------|---------|
| `N8N_DB_TYPE` | `sqlite` (default) or `postgresdb` |
| `N8N_DB_POSTGRESDB_*` | PostgreSQL connection params |
| `N8N_ENCRYPTION_KEY` | Credential encryption key |
| `N8N_METRICS` | Prometheus metrics |
| `N8N_DISABLED_MODULES` | Disable feature modules |
| `N8N_INSTANCE_AI_MODEL` | Enable Instance AI agent |
| `N8N_EXPERIMENT_OVERRIDES` | Feature flags |

## Cloud / Managed

[n8n.cloud](https://app.n8n.cloud/) is the managed SaaS offering. Not in this repo — it's a separate hosted platform. The repo covers self-hosted deployment only.

## Related

- n8n Architecture: [[n8n-architecture]]
- n8n Instance AI: [[n8n-instance-ai]] -- Autonomous agent architecture and tools
- n8n API: [[n8n-api]]
- n8n MCP: [[n8n-mcp]] -- MCP integration surfaces
- n8n Agent Profile: [[n8n-agent-profile]] -- Engineering standards and development patterns
- Wiki entry: [[n8n]]
