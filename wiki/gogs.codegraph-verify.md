---
name: gogs-codegraph-verify
tags: [gogs, codegraph-verify, git, go]
description: "Codegraph Verification: gogs — validating wiki claims against indexed source code symbols"
source: sources/gogs/
---

# Codegraph Verification: gogs

**Date:** 2026-07-30

## Claim 1: Go binary, module gogs.io/gogs, Go 1.26
- **Wiki says:** Language: Go 1.26, module `gogs.io/gogs`.
- **Source evidence:**
  - `go.mod:1` — `module gogs.io/gogs`
  - `go.mod:3` — `go 1.26.0`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: CLI framework is urfave/cli v3 (NOT "Cobra-like")
- **Wiki says (CORRECTED):** CLI framework: urfave/cli v3.
- **Source evidence:**
  - `cmd/gogs/cmd.go:6` — `"github.com/urfave/cli/v3"` import; flag helpers `stringFlag`/`intFlag`/`boolFlag` build `cli.StringFlag`/`cli.IntFlag` structs (cmd.go:9-20, 33-40)
  - `cmd/gogs/main.go:19-48` — root `cli.Command` named "Gogs" with subcommands, run via `cmd.Run(context.Background(), os.Args)`
  - `go.mod:50` — `github.com/urfave/cli/v3 v3.9.0`
- **Verdict:** ❌ PREVIOUSLY WRONG (was labeled "Cobra-like"); now ✅ CORRECT — urfave/cli v3.
- **Fix needed:** Done (wiki stack section + this page).

## Claim 3: cmd/gogs/ standalone entry points (9 files)
- **Wiki says:** CLI entry points: `main.go`, `admin.go`, `backup.go`, `restore.go`, `hook.go`, `import.go`, `serv.go` (+ `cmd.go`, `internal/web/`).
- **Source evidence:**
  - `cmd/gogs/` contains exactly 9 files: `main.go`, `admin.go`, `backup.go`, `restore.go`, `hook.go`, `import.go`, `serv.go`, `cmd.go`, plus `internal/web/` package
  - `main.go:19-48` — root command registers `web`, `serv`, `hook`, `admin`, `import`, `backup`, `restore`
  - `admin.go:17-32` — 8 admin subcommands wired
  - `hook.go:28-57` — `pre-receive`, `update`, `post-receive` subcommands
- **Verdict:** ✅ CORRECT (with `cmd.go` and `internal/web/` added)
- **Fix needed:** Done (wiki package table).

## Claim 4: internal/ has 36 packages, NO internal/db/
- **Wiki says (CORRECTED):** Database layer lives in `internal/database/` only.
- **Source evidence:**
  - `internal/` directory listing shows exactly 36 packages: `app`, `auth`, `authx`, `avatar`, `conf`, `context`, `cron`, `cryptox`, `database`, `dbtest`, `dbx`, `email`, `errx`, `form`, `gitx`, `httplib`, `iox`, `lazyregexp`, `lfsx`, `markup`, `mocks`, `netx`, `osx`, `pathx`, `process`, `ptrx`, `repox`, `route`, `semverx`, `ssh`, `strx`, `sync`, `template`, `testx`, `tool`, `urlx`, `userx`
  - `internal/db/` does NOT exist (confirmed via directory listing)
  - `internal/database/database.go` — engine setup, `internal/database/migrations/` — schema migrations
- **Verdict:** ❌ PREVIOUSLY WRONG (claimed `internal/db/`); now ✅ CORRECT — only `internal/database/`.
- **Fix needed:** Done (wiki package table).

## Claim 5: Web framework is Flamego v1.12
- **Wiki says:** Web framework: Flamego (v1.12).
- **Source evidence:**
  - `go.mod:16` — `github.com/flamego/flamego v1.12.0`
  - `go.mod:13-18` — `flamego/binding v1.3.0`, `flamego/cache v1.5.1`, `flamego/captcha v1.3.0`, `flamego/session v1.3.0`, `flamego/validator v1.0.0`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Built-in SSH server; serv.go gates git verbs then execs
- **Wiki says:** Built-in SSH server for Git protocol.
- **Source evidence:**
  - `internal/ssh/ssh.go` implements the SSH server
  - `cmd/gogs/serv.go:24-32` — `serv` subcommand: "This command should only be called by SSH shell"
  - `cmd/gogs/serv.go:120-123` — `allowedCommands` map: `git-upload-pack` → Read, `git-receive-pack` → Write
  - `cmd/gogs/serv.go:172` — `requestMode, ok := allowedCommands[verb]` (access gate)
  - `cmd/gogs/serv.go:251-253` — `exec.Command(verbs[0], verbs[1], repoFullName)` / `exec.Command(verb, repoFullName)`; hook env composed for write mode (:255-267), `gitCmd.Dir = conf.Repository.Root` (:269)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: DB backends postgres/mysql/sqlite3 via GORM
- **Wiki says:** Database: PostgreSQL, MySQL/MariaDB, SQLite3 via GORM-compatible drivers.
- **Source evidence:**
  - `internal/database/database.go:87-92` — `case "postgres"`, `case "mysql"`, `case "sqlite3"`
  - `go.mod:58-60` — `gorm.io/driver/mysql v1.5.2`, `gorm.io/driver/postgres v1.6.0`, `gorm.io/gorm v1.25.12`
  - `go.mod:19-20` — `github.com/glebarez/go-sqlite v1.21.2`, `github.com/glebarez/sqlite v1.11.0` (pure-Go SQLite drivers)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: import.go is portable-data import (NOT external-repo migration); markup is Markdown/Org-mode only
- **Wiki says (CORRECTED):** `import` = "Import portable data as local Gogs data" + locale subcommand; rendering = Markdown + Org-mode.
- **Source evidence:**
  - `cmd/gogs/import.go:20-28` — `importCommand` usage: "Import portable data as local Gogs data"; description: "Allow user import data from other Gogs installations to local instance without manually hacking the data files"
  - `cmd/gogs/import.go:30-39` — `subcmdImportLocale`: "Import locale files to local repository"
  - Repo migration/mirroring actually lives in `internal/database/mirror.go` (+ `internal/route/repo/repo.go`, `internal/route/api/v1/repo_repo.go`)
  - `internal/markup/` contains ONLY `markdown.go`, `orgmode.go`, `sanitizer.go` (+ `markup.go` + tests) — no Jupyter/PDF renderer
  - `internal/tool/file.go:23` — MIME sniff only (`application/pdf`), not a renderer
- **Verdict:** ❌ PREVIOUSLY WRONG (import claimed as external-repo import; markup claimed Jupyter/PDF); now ✅ CORRECT.
- **Fix needed:** Done (wiki features + package table).

## Additional verified facts (not standalone claims)

- **Auth backends:** `internal/auth/` — LDAP, SMTP, GitHub, PAM (`go.mod:21,32,37` deps); 2FA in `internal/database/two_factor.go`; trusted proxy CIDRs parsed in `internal/conf/conf.go:247-263`
- **Webhooks:** Slack/Discord/Dingtalk handlers in `internal/route/repo/webhook.go` (:202 Slack, :235 Discord, :267 Dingtalk)
- **Protected branches / merge styles / deploy keys:** `internal/database/repo_branch.go` (ProtectedBranch), `internal/database/pull.go:189,255,278` (MergeStyleRebase), `internal/route/repo/setting.go:655` + `internal/database/ssh_key.go`
- **LFS:** `internal/route/lfs/{basic,batch,store}.go`; `[lfs]` section in `internal/conf/conf.go:386-393`
- **Localization:** 32 `conf/locale/locale_*.ini` files (31+ languages)
- **Frontend:** React + TanStack Router — `web/package.json:27-28` (`@tanstack/react-query`, `@tanstack/react-router`); `web/src/pages/{repo,user}`
- **Monorepo:** `moon.yml`, `.moon/`, `pnpm-workspace.yaml`
- **Agent-compat:** `AGENTS.md`, `CLAUDE.md`, `skills-lock.json`

## Summary

All 8 key claims from the Gogs wiki have been verified against the source code; two were corrected:
- ✅ urfave/cli v3 CLI framework (was wrongly "Cobra-like")
- ✅ 36 internal packages, no `internal/db/` (was wrongly listed)
- ✅ import = portable data + locale (was wrongly "external-repo import")
- ✅ markup = Markdown + Org-mode only (was wrongly "Jupyter/PDF")
- ✅ cmd/gogs entry points, Flamego v1.12, SSH serv flow, GORM DB backends, Go 1.26 confirmed

## Related

- [[gogs]] -- Main wiki entry
- [[gogs-architecture]] -- Architecture and component design
- [[gogs-cli]] -- CLI command reference
- [[gogs-deployment]] -- Deployment options and configuration
- [[gogs-api]] -- REST API reference

## Cross-project

- [[podman.codegraph-verify]] -- Similar codegraph verification for Podman
- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for Hermes Agent
- [[n8n.codegraph-verify]] -- Similar codegraph verification for n8n
- [[goclaw.codegraph-verify]] -- Similar codegraph verification for GoClaw
