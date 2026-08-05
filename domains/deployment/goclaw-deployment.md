---
name: goclaw-deployment
tags: [goclaw, deployment, docker, postgresql]
description: "GoClaw Deployment — Docker Compose, PostgreSQL, security hardening"
source: sources/goclaw/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# GoClaw — Deployment

**Source:** `sources/goclaw/` · [docs.goclaw.sh/deployment](https://docs.goclaw.sh/deployment/docker-compose.md)

## Overview

GoClaw compiles to a single static binary (~25 MB) and supports four deployment paths: **Quick binary install** (curl one-liner), **Bare metal** (Go 1.26+, manual PostgreSQL), **Docker Compose** (recommended), and **VPS production** (Docker on a $5+ VPS).

## Docker Compose (Recommended)

GoClaw ships one base compose file plus modular overlays. `prepare-compose.sh` only assembles the contents of `compose.d/*.yml` (which in the repo contains just the core gateway file); overlays live as **top-level** `docker-compose.*.yml` files, with numbered reference copies under `compose.options/` for the standard stack.

```
compose.d/
  00-goclaw.yml        Core gateway service (image ghcr.io/nextlevelbuilder/goclaw)

# Top-level overlays (reference copies in compose.options/ as NN-<name>.yml):
docker-compose.postgres.yml     PostgreSQL 18 + pgvector (pgvector/pgvector:pg18)
docker-compose.selfservice.yml  Web dashboard UI (nginx + React, port 3000)
docker-compose.upgrade.yml      One-shot DB migration/upgrade runner (goclaw upgrade)
docker-compose.browser.yml      Headless Chrome sidecar (CDP port 9222)
docker-compose.otel.yml         Jaeger OpenTelemetry tracing (port 16686)
docker-compose.redis.yml        Redis 7 cache backend
docker-compose.sandbox.yml      Docker-in-Docker sandbox for agent code execution
docker-compose.tailscale.yml    Tailscale tsnet for secure remote access
docker-compose.claude-cli.yml   Claude Code CLI sidecar
docker-compose.cloudflared.yml  Cloudflare Tunnel (cloudflare/cloudflared)
docker-compose.forkdev.yml      Fork/dev image (goclaw:forkdev)
```

```bash
./prepare-env.sh                          # Generate secrets
./prepare-compose.sh                      # Build COMPOSE_FILE from compose.d/*.yml only
docker compose -f docker-compose.yml -f docker-compose.postgres.yml up -d --build
```

To run the full standard stack, copy the reference overlays you need into `compose.d/` (e.g. `cp compose.options/11-postgres.yml compose.d/`) or pass them explicitly with `-f docker-compose.postgres.yml -f docker-compose.selfservice.yml ...`. This starts the gateway at `http://localhost:18790` with PostgreSQL + pgvector automatically configured.

## Database

| Requirement | Detail |
|-------------|--------|
| **Production** | PostgreSQL 15+ with pgvector (required for vector search, multi-tenancy) |
| **Desktop** | SQLite (single-user, reduced features — no vector operations) |
| **Migrations** | Auto-applied on startup via `golang-migrate` — **96 migration pairs** (192 files: `000001_init_schema` … `000096_subagent_tasks_root_agent_scope`), `RequiredSchemaVersion = 96` (`internal/upgrade/version.go:5`) |
| **Encryption** | Provider API keys and secrets stored AES-256-GCM encrypted **when** `GOCLAW_ENCRYPTION_KEY` is set |

Set via environment: `GOCLAW_POSTGRES_DSN=postgres://user:pass@host:5432/goclaw?sslmode=require`

## Core Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `GOCLAW_GATEWAY_TOKEN` | Yes* | Bearer token for API/WebSocket auth. Required unless `GOCLAW_ALLOW_INSECURE_NO_AUTH=1` (explicit opt-in for local dev); empty-token auth otherwise limited to loopback hosts (`internal/config/config_load.go:18,38`) |
| `GOCLAW_ENCRYPTION_KEY` | No (warn-only) | AES-256-GCM key for credential encryption. **If missing, GoClaw only warns** (`cmd/bitrix_portal.go:94-96`) and credentials are stored **UNENCRYPTED** (`crypto.Encrypt` returns plaintext when key is empty — `internal/crypto/aes.go:20-23`) |
| `GOCLAW_POSTGRES_DSN` | Production | PostgreSQL connection string |
| `GOCLAW_*_API_KEY` | No | LLM provider keys (Anthropic, OpenAI, OpenRouter, etc.) |
| `GOCLAW_AUTO_UPGRADE` | Recommended | Auto-run DB migrations on startup |

## Security Hardening (5 Defense Layers)

| Layer | Protections |
|-------|-------------|
| **1. Transport** | CORS origin validation, 512 KB WS message limit, 1 MB HTTP body limit, timing-safe auth, rate limiting |
| **2. Input** | 6 prompt injection patterns detected (configurable action: off/log/warn/block), ILIKE SQL escape |
| **3. Tools** | 15 shell deny groups (destructive ops, reverse shell, crypto mining, etc.), SSRF protection (3-step: block hostnames → private IPs → DNS pinning), path traversal prevention, exec approval |
| **4. Output** | Credential scrubbing (**14 regex patterns** in `internal/tools/scrub.go`), web/MCP content tagging as untrusted |
| **5. Isolation** | Per-user workspace directories, Docker sandbox (read-only root, no network, all caps dropped), privilege separation in container |

## Production Checklist

- [ ] PostgreSQL 15+ with pgvector, automated daily backups
- [ ] TLS termination via Caddy or Nginx (reverse proxy)
- [ ] `GOCLAW_GATEWAY_TOKEN` set to a strong random value (mandatory for external exposure)
- [ ] `GOCLAW_ENCRYPTION_KEY` set — otherwise credentials are stored unencrypted (warn-only)
- [ ] `gateway.allowed_origins` set to dashboard domain
- [ ] `gateway.injection_action: "block"` for public-facing deployments
- [ ] Docker sandbox enabled (`sandbox.mode: "all"`) for untrusted workloads
- [ ] Scoped API keys created for integrations instead of sharing gateway token
- [ ] Monitoring: structured JSON logs via slog, periodic `/health` checks

## Upgrading

```bash
# Docker: pull latest, run the upgrade overlay, restart
docker compose pull
docker compose -f docker-compose.yml -f docker-compose.postgres.yml -f docker-compose.upgrade.yml run --rm upgrade --dry-run   # Preview
docker compose -f docker-compose.yml -f docker-compose.postgres.yml -f docker-compose.upgrade.yml run --rm upgrade              # Apply
docker compose up -d --build                 # Restart
```

Migrations are idempotent. Since the binary requires `RequiredSchemaVersion = 96`, any binary newer than the database schema runs pending migrations on startup; `goclaw upgrade --status` reports current/pending state and `goclaw upgrade --dry-run` previews without applying. Set `GOCLAW_AUTO_UPGRADE=true` for automatic schema updates on startup (CI/CD friendly).

## Related

- [[goclaw]] — GoClaw wiki entry
- [[podman]] — Container runtime
- [[postgresql]] — Database backend
- [[goclaw-architecture]] — GoClaw architecture overview
- [[goclaw-operations]] — Backup/restore, upgrade lifecycle, runtime ops
