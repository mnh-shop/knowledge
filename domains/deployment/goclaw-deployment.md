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

GoClaw uses modular compose overlays assembled by `prepare-compose.sh`:

```
compose.d/
  00-goclaw.yml        Core gateway service
  11-postgres.yml      PostgreSQL 18 + pgvector
  12-selfservice.yml   Web dashboard UI (nginx + React, port 3000)
  13-upgrade.yml       One-shot DB migration runner
  14-browser.yml       Headless Chrome sidecar (CDP port 9222)
  15-otel.yml          Jaeger OpenTelemetry tracing (port 16686)
  16-redis.yml         Redis 7 cache backend
  17-sandbox.yml       Docker-in-Docker sandbox for agent code execution
  18-tailscale.yml     Tailscale tsnet for secure remote access
```

```bash
./prepare-env.sh                          # Generate secrets
./prepare-compose.sh                      # Build COMPOSE_FILE
docker compose up -d --build              # Start stack
```

This starts the gateway at `http://localhost:18790` with PostgreSQL + pgvector automatically configured.

## Database

| Requirement | Detail |
|-------------|--------|
| **Production** | PostgreSQL 15+ with pgvector (required for vector search, multi-tenancy) |
| **Desktop** | SQLite (single-user, reduced features — no vector operations) |
| **Migrations** | Auto-applied on startup via `golang-migrate` (86 migration files, current schema: 80) |
| **Encryption** | Provider API keys and secrets stored AES-256-GCM encrypted |

Set via environment: `GOCLAW_POSTGRES_DSN=postgres://user:pass@host:5432/goclaw?sslmode=require`

## Core Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `GOCLAW_GATEWAY_TOKEN` | Yes | Bearer token for API/WebSocket auth |
| `GOCLAW_ENCRYPTION_KEY` | Yes | AES-256-GCM key for credential encryption |
| `GOCLAW_POSTGRES_DSN` | Production | PostgreSQL connection string |
| `GOCLAW_*_API_KEY` | No | LLM provider keys (Anthropic, OpenAI, OpenRouter, etc.) |
| `GOCLAW_AUTO_UPGRADE` | Recommended | Auto-run DB migrations on startup |

## Security Hardening (5 Defense Layers)

| Layer | Protections |
|-------|-------------|
| **1. Transport** | CORS origin validation, 512 KB WS message limit, 1 MB HTTP body limit, timing-safe auth, rate limiting |
| **2. Input** | 6 prompt injection patterns detected (configurable action: off/log/warn/block), ILIKE SQL escape |
| **3. Tools** | 15 shell deny groups (destructive ops, reverse shell, crypto mining, etc.), SSRF protection (3-step: block hostnames → private IPs → DNS pinning), path traversal prevention, exec approval |
| **4. Output** | Credential scrubbing (13 regex patterns), web/MCP content tagging as untrusted |
| **5. Isolation** | Per-user workspace directories, Docker sandbox (read-only root, no network, all caps dropped), privilege separation in container |

## Production Checklist

- [ ] PostgreSQL 15+ with pgvector, automated daily backups
- [ ] TLS termination via Caddy or Nginx (reverse proxy)
- [ ] `GOCLAW_GATEWAY_TOKEN` and `GOCLAW_ENCRYPTION_KEY` set to strong random values
- [ ] `gateway.allowed_origins` set to dashboard domain
- [ ] `gateway.injection_action: "block"` for public-facing deployments
- [ ] Docker sandbox enabled (`sandbox.mode: "all"`) for untrusted workloads
- [ ] Scoped API keys created for integrations instead of sharing gateway token
- [ ] Monitoring: structured JSON logs via slog, periodic `/health` checks

## Upgrading

```bash
# Docker: pull latest, run upgrade overlay, restart
docker compose pull
docker compose run --rm upgrade --dry-run   # Preview
docker compose run --rm upgrade              # Apply
docker compose up -d --build                 # Restart
```

Migrations are idempotent. Set `GOCLAW_AUTO_UPGRADE=true` for automatic schema updates on startup (CI/CD friendly).

## Related

- [[goclaw]] — GoClaw wiki entry
- [[podman]] — Container runtime
- [[postgresql]] — Database backend
- [[goclaw-architecture]] — GoClaw architecture overview
