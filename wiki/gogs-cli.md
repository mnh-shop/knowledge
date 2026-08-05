---
name: gogs-cli
description: Gogs — CLI command reference for the ./gogs binary: web, admin, backup/restore, hook, import, serv
source: sources/gogs/
verification_date: 2026-07-30
verified_by: codegraph-verify
tags: [gogs, cli, git, go, urfave-cli, admin, backup, deployment]
---

# Gogs — CLI Reference

Companion doc to [[gogs]]. Reference for the `./gogs` binary, built with [urfave/cli](https://github.com/urfave/cli) v3 (`cmd/gogs/cmd.go:6`, `go.mod:50`).

## Root command

```bash
./gogs [global options] <command> [subcommand] [options]
```

- **Name:** `Gogs` (main.go:20)
- **Version:** `0.15.0+dev` (main.go:13-17), shown via `--version`
- **Commands:** `web`, `serv`, `hook`, `admin`, `import`, `backup`, `restore` (main.go:24-43)
- **Common flag:** every subcommand accepts `-c, --config <path>` for a custom configuration file (default `custom/conf/app.ini`); resolved through the command lineage by `configFromLineage` (cmd.go:24-31)

## web — start the server

```bash
./gogs web [--port 3000] [--config path]
```

| Flag | Default | Purpose |
|---|---|---|
| `-p, --port` | `3000` | Alternative listening port |
| `-c, --config` | `<custom>/conf/app.ini` | Custom configuration file path |

Serves the web UI, REST API, and HTTP Git endpoints. Implementation lives in `cmd/gogs/internal/web/` (`web.go`, `webapi.go`, `webapp_dev.go`, `webapp_prod.go`). Production mode is enabled by setting `[server]` `RUN_USER`/`PROTOCOL` etc. in `app.ini`; dev mode serves the React app (`webapp_dev.go`), prod mode serves built assets (`webapp_prod.go`).

## admin — maintenance operations

```bash
./gogs admin <subcommand> [--config path]
```

Parent usage: "Perform admin operations on command line" (admin.go:19). All subcommands operate on the live database via `database.Handle` and share the `-c, --config` flag.

| Subcommand | CLI name | Variable | Purpose |
|---|---|---|---|
| Create user | `create-user` | `subcmdCreateUser` | Create a user in the database. Flags: `--name`, `--password`, `--email`, `--admin` (admin.go:34-45) |
| Delete inactive users | `delete-inactive-users` | `subcmdDeleteInactivateUsers` | Delete all inactive accounts (admin.go:47-57) |
| Delete repo archives | `delete-repository-archives` | `subcmdDeleteRepositoryArchives` | Delete all repository archives (admin.go:59-69) |
| Delete missing repos | `delete-missing-repositories` | `subcmdDeleteMissingRepositories` | Delete repo records that lost their Git files (admin.go:71-81) |
| Garbage collect | `collect-garbage` | `subcmdGitGcRepos` | Run `git gc` on all repositories (admin.go:83-93) |
| Rewrite authorized keys | `rewrite-authorized-keys` | `subcmdRewriteAuthorizedKeys` | Rewrite `.ssh/authorized_keys`; warning: non-Gogs keys are lost (admin.go:95-105) |
| Resync hooks | `resync-hooks` | `subcmdSyncRepositoryHooks` | Resync `pre-receive`, `update`, `post-receive` hooks on all repos (admin.go:107-117) |
| Reinit missing repos | `reinit-missing-repositories` | `subcmdReinitMissingRepositories` | Reinitialize repo records that lost their Git files (admin.go:119-129) |

Each operation runs through `adminDashboardOperation` (admin.go:169-189), which inits config + logging, sets the DB engine, and prints a success message.

## backup — dump files and database

```bash
./gogs backup [flags]
```

Usage: "Backup files and database" (backup.go:21). Produces a portable zip archive (format version 1, `metadata.ini` inside) usable for migration across database engines.

| Flag | Default | Purpose |
|---|---|---|
| `-c, --config` | — | Custom configuration file path |
| `-v, --verbose` | `false` | Show process details |
| `-t, --tempdir` | `os.TempDir()` | Temporary directory for staging |
| `--target` | `./` | Directory to save the backup archive |
| `--archive-name` | `gogs-backup-<timestamp>.zip` | Backup archive filename |
| `--database-only` | `false` | Dump only the database |
| `--exclude-mirror-repos` | `false` | Exclude mirror repositories |
| `--exclude-repos` | `false` | Exclude repositories |

## restore — restore from backup

```bash
./gogs restore [flags]
```

Usage: "Restore files and database from backup" (restore.go:21). The archive version must be <= current Gogs version; backup from other DB engines can be imported (database migration path). Missing files/tables in the archive are skipped unchanged.

| Flag | Default | Purpose |
|---|---|---|
| `-c, --config` | — | Custom configuration file path |
| `-v, --verbose` | `false` | Show process details |
| `-t, --tempdir` | `os.TempDir()` | Temporary directory for extraction |
| `--from` | — | Path to the backup archive |
| `--database-only` | `false` | Import only the database |
| `--exclude-repos` | `false` | Exclude repositories |

## hook — Git hook delegation

```bash
./gogs hook <subcommand>   # pre-receive | update | post-receive
```

Parent usage: "Delegate commands to corresponding Git hooks" (hook.go:28). All subcommands "should only be called by Git" — the server installs them as repository hooks and the `serv` flow injects identity via env vars (`database.ComposeHookEnvs`, serv.go:255-267; hook env read at hook.go:224-226).

| Subcommand | Purpose |
|---|---|
| `pre-receive` | Enforce push rules before refs are updated (hook.go:44) |
| `update` | Per-ref update checks (hook.go:50) |
| `post-receive` | Post-push side effects: webhook dispatch (Slack/Discord/Dingtalk), notifications via `internal/email` + `internal/httplib` (hook.go:56) |

## import — portable data + locale

```bash
./gogs import locale --source <dir> --target <dir> [--config path]
```

Usage: "Import portable data as local Gogs data" (import.go:20-28). This is NOT external-repository migration; it imports data exported from other Gogs installations and locale files. Repo mirroring from other hosts is a separate feature (`internal/database/mirror.go`).

| Flag | Purpose |
|---|---|
| `--source` | Source directory with new locale files |
| `--target` | Target directory with old locale files |
| `-c, --config` | Custom configuration file path |

## serv — SSH Git handler (internal)

```bash
./gogs serv <verb> <repo>   # invoked by the SSH server only
```

Usage: "This command should only be called by SSH shell" (serv.go:24-32). Not for human use: parses the SSH original command, validates `git-upload-pack` (read) / `git-receive-pack` (write) against `allowedCommands` (serv.go:120-123), checks deploy keys (serv.go:102-118), and `exec`s the git binary (serv.go:251-253). See [[gogs-architecture]] for the full flow.

## Deployment notes

```bash
# Binary (Linux/macOS): quick start
./gogs web --port 3000

# Docker (host SSH 10022, host HTTP 10880)
docker run --name=gogs -p 10022:22 -p 10880:3000 gogs/gogs

# Reverse proxy: terminate TLS at nginx/caddy, forward to 127.0.0.1:3000
```

- All commands honor `-c, --config`; run `./gogs --help` and `./gogs <cmd> --help` for exact usage.
- `backup`/`restore` archives are the supported path for moving an instance between machines or database engines.
- `admin` commands are safe to run while the server is stopped (they init the DB engine themselves).
- Build via Moonrepo: `moon run gogs:build` (see `moon.yml`).

## Related

- [[gogs]] — Main wiki entry
- [[gogs-architecture]] — Architecture and component design
- [[gogs.codegraph-verify]] — Evidence-backed claim verification
- [[gogs-deployment]] — Deployment options and configuration
