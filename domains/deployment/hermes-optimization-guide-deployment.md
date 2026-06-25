---
name: hermes-optimization-guide-deployment
description: "Deployment patterns and infrastructure templates from the Hermes Optimization Guide: systemd units, Docker Compose observability stack, Caddy reverse proxy, VPS bootstrap script, cron schedules, and reference architectures"
tags: [cli, dashboard, deployment, desktop-app, developer-tools, docker, mcp, messaging, monitoring, multi-platform, optimization, plugin-sdk, security, storage, systemd, webhook]
---

# Hermes Optimization Guide -- Deployment Domain

**Source:** `sources/hermes-optimization-guide/`

Analysis of the production-grade deployment infrastructure shipped alongside the Hermes Optimization Guide. This covers everything needed to run a self-hosted Hermes Agent in production, from a $5/mo VPS to a local NVIDIA DGX Spark with full observability.

## Deployment Topology

```
Internet                    VPS / Workstation / DGX Spark
                           ┌─────────────────────────────────────┐
                           │  Caddy (auto-TLS reverse proxy)     │
                           │    ├── hermes.yourdomain.com ──→ 127.0.0.1:8765 (dashboard)
                           │    ├── hooks.yourdomain.com  ──→ 127.0.0.1:8766 (webhooks)
                           │    └── langfuse.yourdomain.com ──→ 127.0.0.1:3000
                           │                                     │
User ── Telegram/Discord ──┤  hermes.service (systemd, 4G limit) │
       / Web / Desktop     │  hermes-dashboard.service (1G limit)│
                           │                                     │
                           │  Langfuse v3 (Docker Compose)       │
                           │    PostgreSQL + ClickHouse + MinIO  │
                           │    + Redis                          │
                           │                                     │
                           │  fail2ban + UFW                     │
                           │  unattended-upgrades                │
                           │                                     │
                           │  ~/.hermes/                          │
                           │    ├── config.yaml                  │
                           │    ├── .env (600 perms)             │
                           │    ├── SOUL.md                      │
                           │    ├── skills/ (symlinked from guide)│
                           │    ├── memories/                    │
                           │    ├── cron.yaml                    │
                           │    └── logs/                        │
                           └─────────────────────────────────────┘
```

## Infrastructure Templates

### systemd Units

Two hardened systemd service files in `templates/systemd/`:

**hermes.service**
- Runs as non-root `hermes` user
- Type=simple with `Restart=on-failure` (RestartSec=5, StartLimitBurst=5 in 300s)
- `ProtectSystem=strict`, `ProtectHome=read-only`, `ReadWritePaths=/home/hermes/.hermes /tmp`
- `NoNewPrivileges=true`, empty `CapabilityBoundingSet=`
- Kernel protection: `ProtectKernelTunables`, `ProtectKernelModules`, `ProtectKernelLogs`, `ProtectControlGroups`, `ProtectHostname`, `ProtectClock`
- `ProtectProc=invisible`, `ProcSubset=pid`
- `RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6 AF_NETLINK`
- `SystemCallFilter=@system-service` (excludes `@privileged @resources @mount @cpu-emulation @debug @reboot @swap`)
- Memory limit: 4G, File descriptors: 65536, Tasks: 4096

**hermes-dashboard.service**
- Binds to `hermes.service` via `BindsTo=`
- Serves on `127.0.0.1:8765` only
- Same hardening set but with `RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6` (no netlink)
- Memory limit: 1G, Tasks: 512

### Caddy Reverse Proxy

`templates/caddy/Caddyfile` provides a production Caddy configuration with:
- Auto Let's Encrypt TLS
- zstd + gzip encoding
- Basic auth for dashboard
- HSTS (6-month `includeSubDomains preload`)
- Security headers (X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy)
- 1MB request body limit for webhook endpoint (no basic auth, signature-validated in Hermes)
- Per-subdomain logging to `/var/log/caddy/`

### Docker Compose -- Self-Hosted Langfuse v3

`templates/compose/langfuse-stack.yml` deploys the full Langfuse observability stack:
- **langfuse-web** and **langfuse-worker** (langfuse/langfuse:3)
- **PostgreSQL 16** (primary + Direct URL for migrations)
- **ClickHouse 24** (analytics storage for traces)
- **MinIO** (S3-compatible object storage for event uploads)
- **Redis 7** (queuing and caching)
- All services use health checks, restart policy `unless-stopped`, and bind to `127.0.0.1` only

### Cron Schedule

`templates/cron/production-crons.yaml` defines 8 production cron jobs:

| Schedule | Task |
|----------|------|
| Daily 3am | `nightly-backup` (encrypted, to S3/SSH/local) |
| Weekly Monday 9am | `audit-mcp` (MCP server trust audit) |
| Weekly Monday 10am | `audit-approval-bypass` |
| Weekly Monday 11am | `cost-report` (7-day window) |
| Weekly Monday 12pm | `weekly-dep-audit` |
| Monthly 1st at 4am | `rotate-secrets` (webhook HMACs) |
| Daily 2am | `audit-injection-attempts` |
| Every 15min | `disk-watchdog` (no_agent mode, pure shell) |

### VPS Bootstrap Script

`scripts/vps-bootstrap.sh` is a one-command production bootstrap targeting Debian 12 / Ubuntu 24.04:
1. Installs dependencies (curl, jq, git, python3-venv, age, rclone, ufw, fail2ban, unattended-upgrades)
2. Installs Node.js 20 and Caddy
3. Creates non-root `hermes` user
4. Clones the optimization guide to `/opt/hermes-optimization-guide`
5. Installs Hermes and symlinks all 13 skills
6. Seeds a cost-optimized `config.yaml` and `.env` template (with placeholder keys)
7. Installs hardened systemd units
8. Configures UFW (22, 80, 443 only, default deny)
9. Enables fail2ban and unattended-upgrades
10. Non-destructive and re-runnable

## Config Templates

Five opinionated `config.yaml` templates in `templates/config/`:

- **minimum.yaml** -- bare minimum for local use
- **telegram-bot.yaml** -- optimized for Telegram-only operation
- **production.yaml** -- full production setup
- **cost-optimized.yaml** -- cheapest viable setup (Gemini Flash default, Cerebras for classification, Sonnet only for high-stakes coding; typical $0.05-0.30/active hour)
- **security-hardened.yaml** -- maximum security posture

## Reference Architectures

Four complete blueprints with parts lists, cost estimates, and scaling ceilings:

| Blueprint | Cost/mo | Target User |
|-----------|---------|-------------|
| **Homelab** | ~$0 + keys | Fully private, on own hardware |
| **Solo Developer** | $25-70 | VPS + phone bot, daily driver |
| **Small Agency** | $225-825 | 2-6 devs, multiple clients |
| **Road Warrior** | $5 + on-demand | Phone drives cloud box, anywhere |

Key design patterns across all architectures:
- All use the same templates, differing only in scale and which ones apply
- Each includes honest scaling ceilings (e.g., CX22 ram at "5-10 concurrent tool calls + LightRAG")
- Explicit graduation paths between tiers

## Security Hardening

The deployment includes multiple defense layers (documented in Part 19 and enforced in templates):

1. **OS-level**: non-root user, UFW, fail2ban, unattended-upgrades
2. **systemd hardening**: strict Protect*, NoNewPrivileges, CapabilityBoundingSet, SystemCallFilter, RestrictAddressFamilies
3. **Secrets management**: `.env` at 600 permissions, never committed
4. **Web security**: Caddy with HSTS, security headers, basic auth, body-size limits
5. **Approval layer**: denylist, allowlist, quarantine profiles, secrets redaction, MCP trust levels
6. **Network**: reverse-proxy-only exposure, internal services on loopback only

## Key Relationships

- The systemd units reference `hermes` user home, guide skills, and Part 12 documentation
- The Caddyfile references dashboard port (8765), webhook port (8766), and Langfuse port (3000)
- The Docker Compose stack is referenced by Part 20 (Observability)
- The VPS bootstrap script ties everything together: systemd, Caddy, skills, config template
- All reference architectures use the same templates, differing only in which ones apply
