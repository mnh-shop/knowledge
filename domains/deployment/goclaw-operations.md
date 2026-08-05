---
name: goclaw-operations
tags: [goclaw, operations, cli, backup, upgrade]
description: "GoClaw Operations — backup/restore, upgrade lifecycle, packages, build tags, log streams"
source: sources/goclaw/
verification_date: 2026-07-30
verified_by: codegraph-verify
---

# GoClaw — Operations

**Source:** `sources/goclaw/` · CLI surface in `cmd/`, backup engine in `internal/backup/`, schema tracking in `internal/upgrade/`

## Overview

GoClaw ships a full operator CLI (21 commands) for day-2 management: `onboard`, `version`, `pairing`, `agent`, `doctor`, `config`, `providers`, `channels`, `bitrix-portal`, `cron`, `skills`, `sessions`, `traces`, `migrate`, `upgrade`, `backup`, `restore`, `tenant-backup`, `tenant-restore`, `auth`, `setup` (registered in `cmd/root.go`). This page covers the operational lifecycle: backups, upgrades, runtime package management, build variants, log conventions, and the heartbeat system.

## Backup / Restore

Backup engine lives in `internal/backup/` (`backup.go`, `restore.go`, `tenant_backup.go`, `tenant_restore.go`, `db_dump.go`, `db_restore.go`, `fs_archive.go`, `manifest.go`, `preflight.go`, `s3_client.go`, `s3_config.go`). A backup is a `.tar.gz` archive combining a **database dump** + **filesystem archive** (workspace/data dirs), with a manifest for verification.

### Full backup / restore

```bash
goclaw backup --output ./backup-$(date +%F).tar.gz        # DB + files
goclaw backup --exclude-db                                 # filesystem only
goclaw backup --exclude-files                              # database only
goclaw backup --upload-s3                                  # ...then upload to S3

goclaw restore ./backup-2026-07-30.tar.gz                  # requires --force
goclaw restore --from-s3 backups/backup-2026-07-30.tar.gz  # pull from S3 first
goclaw restore --list-s3                                   # list available backups
goclaw restore --dry-run <archive>                         # inspect + plan without applying
```

Restore is destructive and demands `--force`; `--skip-db` / `--skip-files` restore partial archives. S3 (or S3-compatible) storage is configured through the encrypted `config_secrets` store under keys `backup.s3.access_key_id`, `backup.s3.secret_access_key`, `backup.s3.bucket`, `backup.s3.region`, `backup.s3.endpoint`, `backup.s3.prefix` (`internal/backup/s3_config.go`).

### Tenant-scoped backup / restore

Multi-tenant deployments can back up a single tenant's rows + files:

```bash
goclaw tenant-backup --tenant acme -o acme.tar.gz          # slug or UUID (--tenant-id)
goclaw tenant-backup --tenant acme --upload-s3
goclaw tenant-restore acme.tar.gz --mode upsert            # upsert | replace | new
goclaw tenant-restore acme.tar.gz --mode replace --force   # replace requires --force
goclaw tenant-restore acme.tar.gz --mode new --new-tenant-slug acme2
```

`preflight.go` runs validation checks (disk space, pg_dump availability, SQLite vs PG detection) before any backup proceeds.

## Upgrade Lifecycle

### Schema versioning

- Schema is tracked by `RequiredSchemaVersion = 96` (`internal/upgrade/version.go:5`) — the migration version the binary requires. Any newer binary runs pending `migrations/` pairs (96 total, `000001`…`000096`) against the database.
- `goclaw migrate` provides direct control: `up`, `down`, `version`, `force <version>`, `goto <version>`, `drop` (`cmd/migrate.go`).
- `internal/upgrade/hooks.go` runs **data hooks** after migrations (e.g. `hook_web_search_migrate.go`, `hook_workspace_normalize.go`) for non-SQL data transformations.

### Upgrade commands

```bash
goclaw upgrade --status        # show current upgrade status (schema + pending hooks)
goclaw upgrade --dry-run       # preview what would change without applying
goclaw upgrade                 # apply pending migrations + data hooks
```

### Upgrade overlay (Docker)

`docker-compose.upgrade.yml` (reference copy `compose.options/13-upgrade.yml`) runs `goclaw upgrade` as a **one-shot container** against the postgres service — `run --rm upgrade --dry-run` to preview, `run --rm upgrade` to apply, `--status` to check. It shares the `goclaw-data` volume and reads `GOCLAW_ENCRYPTION_KEY` / `GOCLAW_POSTGRES_DSN` from the environment.

### Binary self-update & dashboard update

- **Binary:** `scripts/zuey/goclaw-upgrade-release.sh` downloads a GitHub Release tarball, verifies checksums, extracts to `/opt/goclaw/releases/<tag>`, and switches via `goclaw-deploy` (health-check + rollback). A gateway HTTP endpoint (`POST /v1/system/gateway/upgrade`, `GET /v1/system/gateway/upgrade/status`) is available in builds with the upgrade endpoint, protected by `X-GoClaw-Upgrade-Token` (`docs/deployment-guide.md`).
- **Dashboard:** the web dashboard is served embedded at the API port by default; the optional `docker-compose.selfservice.yml` overlay runs the standalone `ghcr.io/nextlevelbuilder/goclaw-web:latest` image under nginx on port 3000.

## Packages — Runtime Package Management

GoClaw installs CLI tools / skill dependencies at **runtime** into `{dataDir}/.runtime/` (`apk-packages`, `pip/`, `npm-global/`, `bin/`) via a `pkg-helper` binary. Configured under the `packages` config block (`internal/config/config.go:63`, `PackagesConfig`), with three installers documented in `docs/`:

| Installer | Source | Syntax |
|-----------|--------|--------|
| GitHub releases | `docs/packages-github.md` | `github:owner/repo[@tag]` — auto-selects `linux` asset for arch, verifies SHA256 + ELF magic, extracts safely, installs to `{runtimeDir}/bin/` |
| apk (Alpine) | `docs/packages-apk.md` | System packages via `apk` |
| pip / npm | `docs/packages-pip-npm.md` | Python / Node packages into per-runtime dirs |

## Build Variants

The Go binary is feature-gated by build tags (Dockerfile passes them via `-tags`):

| Tag | Effect | Source |
|-----|--------|--------|
| `otel` | Enable OpenTelemetry tracing export | `cmd/gateway_otel.go` (noop: `cmd/gateway_otel_noop.go`) |
| `redis` | Enable Redis cache backend | `cmd/gateway_redis.go` (noop: `cmd/gateway_redis_noop.go`) |
| `tsnet` | Enable Tailscale tsnet (tailnet-in-container) | `cmd/gateway_tsnet.go` (noop: `cmd/gateway_tsnet_noop.go`) |
| `sandbox` | Docker sandbox support (runtime feature) | `internal/sandbox/`, `Dockerfile.sandbox` image, `docker-compose.sandbox.yml` (ENABLE_SANDBOX build arg) |
| `embedui` | Embed web dashboard into binary | `Dockerfile` ENABLE_EMBEDUI |
| `sqliteonly` / `tui` | Desktop Lite edition / TUI build | `ui/desktop/`, Makefile |

Docker images (GHCR `ghcr.io/nextlevelbuilder/goclaw`, Docker Hub `digitop/goclaw`) ship variants: `latest` (backend + web UI + Python), `base` (API-only), `full` (all runtimes + skills), `web` (standalone nginx), `beta`.

## Log Streams

All logs are structured via `log/slog`. Security-relevant events use the `security.*` naming convention (`slog.Warn("security.<event>")`), so operators can filter/alert on a single namespace:

```text
security.sandbox_unavailable            internal/tools/shell.go
security.rate_limited                   internal/http + channels
security.cross_tenant_send_blocked      internal/tools/message.go
security.ssh_host_key_changed           internal/workstation/backends/ssh_dial.go
security.vault_symlink_escape           internal/vault
security.mutable_symlink_parent         internal/tools/filesystem.go
security.credentialed_binary_denied     internal/tools/shell.go
security.workstation_cmd_denied         internal/workstation/security/allowlist.go
security.pairing_check_failed           internal
```

Related operational stream names: `crypto.unencrypted_value_read` (`internal/crypto/aes.go`) warns when a stored value lacks the `aes-gcm:` prefix; `mcp.server.connect_failed` marks MCP connectivity problems.

## Heartbeat System

Documented in `docs/22-heartbeat-system.md`. A background **Ticker polls every 30 s** (`internal/heartbeat/ticker.go`, `pollInterval = 30 * time.Second`) for due agent heartbeats, runs each agent's `HEARTBEAT.md` checklist through the agent loop, and delivers results to messaging channels — **suppressing delivery** when the run contains `HEARTBEAT_OK`. Configs live in `agent_heartbeats`, execution logs in `heartbeat_run_logs`; cache invalidation propagates via the `cache:heartbeat` bus event. This is an application-level agent check-in, unrelated to WebSocket keep-alive.

## Related

- [[goclaw]] — GoClaw wiki entry
- [[goclaw-deployment]] — Compose stack, env vars, security hardening
- [[goclaw-mcp-implementation]] — MCP client + server surfaces
- [[goclaw-architecture]] — GoClaw architecture overview
