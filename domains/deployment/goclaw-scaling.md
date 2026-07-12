---
name: goclaw-scaling
description: "GoClaw scaling guide — from single-user desktop to multi-tenant production deployment"
tags: [goclaw, deployment, scaling, production, postgresql]
source: sources/goclaw/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# GoClaw — Scaling Guide

**Source:** `sources/goclaw/` · [docs.goclaw.sh](https://docs.goclaw.sh/)

GoClaw's architecture scales cleanly from a single-user desktop binary to a multi-tenant SaaS gateway. This guide maps each tier, the configuration changes required, and the operational practices to adopt at each stage.

## Scaling Tiers

### Tier 1: Single-User Desktop (SQLite)

- SQLite backend, single static binary (~25 MB)
- No pgvector — vault semantic search falls back to lexical BM25
- No Docker, no PostgreSQL required
- Max 5 agents, 1 team (desktop edition limit)
- Build: `go build -o goclaw .`
- Run: `./goclaw onboard && source .env.local && ./goclaw`
- Dashboard at `http://localhost:18790`
- **Best for:** development, personal use, prototyping

**Build tags (optional):** `go build -tags embedui -o goclaw .` embeds the web UI in the binary.

### Tier 2: Single-User Docker

- Docker Compose with PostgreSQL 18 + pgvector
- Full feature set: knowledge vault with semantic search, multi-agent teams, all 22 providers
- 2 GB RAM minimum (~1.2 GB at idle)
- Dashboard served at `http://localhost:18790`
- **Best for:** feature-complete personal setup, local testing of production features

```bash
docker compose -f docker-compose.yml -f docker-compose.postgres.yml up -d --build
```

### Tier 3: Multi-User Team (Docker/VPS)

- PostgreSQL 15+ with pgvector, connection pooling
- Multi-tenant isolation activated: per-user context, sessions, memory, traces
- Dashboard + gateway separation via `docker-compose.selfservice.yml` (nginx + React SPA at port 3000)
- Rate limiting and quota enforcement configured
- Reverse proxy with TLS (Caddy/Nginx)
- **Best for:** small teams, departmental deployments, single-tenant production

### Tier 4: Production (VPS/Bare Metal)

- Everything in Tier 3 plus:
  - Redis caching layer (`docker-compose.redis.yml`, `-tags redis`)
  - OpenTelemetry tracing via Jaeger (`docker-compose.otel.yml`, `-tags otel`)
  - Docker sandbox for agent code execution (`docker-compose.sandbox.yml`)
  - Tailscale secure networking (`docker-compose.tailscale.yml`, `-tags tsnet`)
  - Daily automated PostgreSQL backups
  - Scoped API keys with RBAC (no shared gateway token)
  - Monitoring and alerting on structured JSON logs
- **Best for:** multi-tenant SaaS, enterprise deployments, public-facing gateways

## Concurrency Tuning

GoClaw uses lane-based scheduling to limit concurrent agent runs by type. Each lane has a configurable cap via environment variable:

| Lane | Default | Env Var | Purpose |
|------|---------|---------|---------|
| main | 30 | `GOCLAW_LANE_MAIN` | Channel messages + WebSocket chat |
| subagent | 50 | `GOCLAW_LANE_SUBAGENT` | Spawned subagent tasks |
| delegate | 100 | `GOCLAW_LANE_DELEGATE` | Agent-to-agent delegation (teams) |
| cron | 30 | `GOCLAW_LANE_CRON` | Scheduled cron jobs |

Tune based on server resources: lower values reduce memory pressure, higher values improve throughput. On a 2 vCPU / 4 GB VPS, halving defaults is a safe starting point.

**Subagent limits** (in `config.json`):
| Field | Default | Description |
|-------|---------|-------------|
| `subagents.maxConcurrent` | 20 | Max parallel subagents across all sessions |
| `subagents.maxSpawnDepth` | 1 | Max nesting depth (1–5) |
| `subagents.maxChildrenPerAgent` | 5 | Max children per parent agent (1–20) |

## Docker Compose Overlays

GoClaw v3 uses `compose.d/` for always-active overlays and `compose.options/` for reference copies. Run `./prepare-compose.sh` to assemble the `COMPOSE_FILE` variable.

| Overlay | Filename | Purpose |
|---------|----------|---------|
| Core gateway | `00-goclaw.yml` | GoClaw gateway + embedded UI |
| PostgreSQL | `11-postgres.yml` | PostgreSQL 18 with pgvector |
| Self-service UI | `12-selfservice.yml` | Nginx + separate React SPA (port 3000) |
| DB upgrade | `13-upgrade.yml` | One-shot migration runner |
| Browser | `14-browser.yml` | Headless Chrome sidecar (CDP port 9222) |
| OTel/Jaeger | `15-otel.yml` | OpenTelemetry trace visualization |
| Redis | `16-redis.yml` | Redis 7 cache backend (requires `-tags redis`) |
| Sandbox | `17-sandbox.yml` | Docker-in-Docker for agent code execution |
| Tailscale | `18-tailscale.yml` | tsnet secure networking (requires `-tags tsnet`) |

**Build args** for Docker images:

| Build Arg | Enables |
|-----------|---------|
| `ENABLE_OTEL` | OpenTelemetry span exporter |
| `ENABLE_TSNET` | Tailscale networking |
| `ENABLE_REDIS` | Redis cache backend |
| `ENABLE_SANDBOX` | Docker CLI in container |
| `ENABLE_PYTHON` | Python 3 runtime for skills |
| `ENABLE_NODE` | Node.js runtime for skills |
| `ENABLE_CLAUDE_CLI` | Claude Code CLI (npm) |

Start with what you need:
```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.postgres.yml \
  -f docker-compose.redis.yml \
  up -d --build
```

## Production Checklist

### Database
- [ ] PostgreSQL 15+ with pgvector extensions (`pgcrypto`, `vector`)
- [ ] Connection pool: 25 max open / 10 max idle (tune via DSN: `pool_max_conns=25`)
- [ ] Automated daily backups with quarterly restore tests
- [ ] Schema up to date: `./goclaw upgrade --status` or `docker compose run --rm upgrade --status`

### Secrets
- [ ] `GOCLAW_ENCRYPTION_KEY` = random 32-byte hex — **back this up** (loss = all encrypted API keys unreadable)
- [ ] `GOCLAW_GATEWAY_TOKEN` = strong random value
- [ ] All provider API keys via env vars, never in `config.json` or git history
- [ ] Credentials checked for exposure: logs should show `***` masking, not raw values

### Network
- [ ] TLS termination via Caddy/Nginx/Cloudflare (GoClaw does not terminate TLS internally)
- [ ] `gateway.allowed_origins` set to actual client origins (empty = allow all WebSocket origins)
- [ ] Port 18790 not exposed directly to the internet without TLS

### Rate Limiting
- [ ] `gateway.rate_limit_rpm`: 20 (default, tune as needed; 0 = disabled)
- [ ] `tools.rate_limit_per_hour`: 150 (default)
- [ ] Webhook rate limiting built-in (30 req/60s per source)

### Security
- [ ] `gateway.injection_action`: `"warn"` or `"block"` — never `"off"` in production
- [ ] `agents.defaults.restrict_to_workspace`: `true`
- [ ] Sandbox mode configured (`"non-main"` for subagents, `"all"` for everything)
- [ ] `sandbox.network_enabled`: `false` unless agents explicitly need it
- [ ] `sandbox.read_only_root`: `true`
- [ ] `gateway.owner_ids` contains only trusted admin IDs

### Monitoring
- [ ] Structured JSON logging via `slog` — collected from stdout/stderr
- [ ] Alert on `slog.Warn("security.*")` entries (blocked attacks, anomalies)
- [ ] Alert on `tracing: span buffer full` (collector falling behind)
- [ ] Uptime monitoring via `/health` endpoint
- [ ] Interactive API docs at `/docs` (Swagger UI) and `/v1/openapi.json`
- [ ] OpenTelemetry export configured for trace-level visibility (Jaeger)

## Multi-Tenancy

GoClaw v3 provides per-user isolation across all 22+ store interfaces. Every SQL query enforces `WHERE tenant_id = $N` — fail-closed, no cross-tenant leakage.

### Tenant Resolution

| Credential | Tenant Resolution |
|------------|-------------------|
| Gateway token + owner user ID | All tenants (cross-tenant admin) |
| Gateway token + non-owner user ID | User's tenant membership |
| API key (tenant-bound) | Auto from key's `tenant_id` |
| Browser pairing | Paired tenant |
| No credentials | Master tenant (dev/single-user) |

**Recommended for SaaS:** Use tenant-bound API keys. The tenant resolves automatically — no extra header needed.

### What Gets Isolated

| Data | Isolation |
|------|-----------|
| Context files | Per-user per-agent |
| Sessions | Per-user per-agent per-channel |
| Memory | Per-user per-agent |
| Traces | Per-user filterable |
| LLM providers | Per-tenant (separate API keys) |
| MCP servers | Per-tenant + per-user credential overrides |
| Skills | Per-tenant enable/disable |
| Built-in tools | Per-tenant enable/disable |
| 40+ tables | `tenant_id` NOT NULL constraint |

### API Key Scopes

| Scope | Role | Permissions |
|-------|------|-------------|
| `operator.admin` | admin | Full access — agents, config, API keys, tenants |
| `operator.read` | viewer | Read-only — list agents, sessions, configs |
| `operator.write` | operator | Read + write — chat, create sessions, manage agents |
| `operator.approvals` | operator | Approve/reject execution requests |
| `operator.provision` | operator | Create tenants and manage users |
| `operator.pairing` | operator | Manage device pairing |

### Per-Edition Limits

Editions control resource usage per tenant:

| Field | Description |
|-------|-------------|
| `MaxSubagentConcurrent` | Max parallel subagents per tenant |
| `MaxSubagentDepth` | Max delegation nesting depth |

## Upgrading

### Bare Metal
```bash
cd goclaw && git pull && go build -o goclaw . && ./goclaw upgrade
```

### Docker
```bash
cd /opt/goclaw && git pull && docker compose up -d --build
```
Migrations auto-apply on startup. Set `GOCLAW_AUTO_UPGRADE=true` for automatic migrations, or use the upgrade overlay explicitly:
```bash
docker compose -f docker-compose.yml -f docker-compose.postgres.yml \
  -f docker-compose.upgrade.yml run --rm upgrade
```

### Pre-upgrade checks
- `./goclaw upgrade --status` — check schema version
- `./goclaw upgrade --dry-run` — preview changes
- Verify backup exists before upgrading production

## Related

- [[goclaw]] — GoClaw wiki (architecture, features, providers, channels)
- [[goclaw-deployment]] — Docker Compose, database, security hardening
- [[podman]] — Container runtime
- [[postgresql]] — Database
- [[mission-control]] — Monitoring dashboard
- [[goclaw-architecture]] — Core architecture
