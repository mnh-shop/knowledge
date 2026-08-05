---
name: gogs-architecture
description: Gogs — Architecture and component design: cmd layer, route tree, database stores, SSH serv flow, frontend, config sections, internal packages
source: sources/gogs/
verification_date: 2026-07-30
verified_by: codegraph-verify
tags: [gogs, architecture, git, go, flamego, ssh, lfs, database]
---

# Gogs — Architecture

Companion doc to [[gogs]]. Describes how the binary is layered: `cmd/gogs/` entry points delegate to `internal/` packages, the route tree serves the HTTP/API surface, the database layer stores domain state, and the SSH server bridges Git protocol to the filesystem.

## Layer overview

```
User → SSH / HTTP / HTTPS
        │
        ▼
┌─────────────────────────────────┐
│        cmd/gogs/ (main)         │  urfave/cli v3 commands
│  web | serv | hook | admin      │
│  import | backup | restore      │
│        │                        │
│        ▼                        │
│     internal/ (36 packages)     │  conf → database → route → domain
└──────────────┬──────────────────┘
               │
               ▼
   Database (postgres/mysql/sqlite3)  +  Git repos on disk + LFS objects
```

## cmd layer ↔ internal layer mapping

| Command (`cmd/gogs/`) | Registered | Delegates to | Purpose |
|---|---|---|---|
| `main.go` | root `cli.Command` "Gogs" (main.go:19-48) | registers all subcommands | Binary entry point; version `0.15.0+dev` (main.go:13-17) |
| `cmd.go` | flag helpers | shared with all commands | `stringFlag`/`intFlag`/`boolFlag` + `configFromLineage` (cmd.go:9-31) |
| `web` | main.go:29 | `cmd/gogs/internal/web/` (`web.go`, `webapi.go`, `webapp_dev.go`, `webapp_prod.go`, `cache.go`, `recovery.go`) | HTTP server: web UI, API, HTTP Git endpoints |
| `serv` | main.go:32 | `internal/ssh/` + `internal/database` | SSH Git protocol handler (serv.go) |
| `hook` | main.go:34 | `internal/database`, `internal/email`, `internal/httplib` | Git hook delegation: `pre-receive`/`update`/`post-receive` (hook.go:28-57) |
| `admin` | main.go:35 | `internal/database` | 8 admin maintenance operations (admin.go:17-32) |
| `import` | main.go:36 | `internal/conf`, `internal/osx` | Import portable data + locale files (import.go:20-39) |
| `backup` / `restore` | main.go:37-38 | `internal/database`, `unknwon/cae/zip` | Portable zip backup/restore of files + database |

Every subcommand receives `--config, -c` for a custom `app.ini` path; the flag is resolved through the command lineage via `configFromLineage` (cmd.go:24-31).

## Route tree

`internal/route/` registers Flamego handlers grouped by area:

| Area | Package | Surface |
|---|---|---|
| `admin` | `internal/route/admin/` | Admin dashboard (users, orgs, repos, auth sources, notices, monitor) |
| `api` | `internal/route/api/v1/` (33 files) | REST API v1: users, orgs, repos, branches, commits, contents, issues, labels, milestones, hooks, keys, tags, markdown |
| `dev` | `internal/route/dev/` | Development/debug routes |
| `lfs` | `internal/route/lfs/` | Git LFS: `basic.go`, `batch.go`, `store.go`, `route.go` |
| `org` | `internal/route/org/` | Organization pages, teams, members |
| `repo` | `internal/route/repo/` | Repo pages: `wiki.go`, `editor.go`, `release.go`, `branch.go`, `webhook.go`, `setting.go` (incl. deploy keys :655), `repo.go`, `issue.go`, `pull.go`, `commit.go` |
| `user` | `internal/route/user/` | User profile, settings, auth (login/signup), notifications |
| `home` | `internal/route/` root | Landing, explore, sign-in/sign-up |

Key handler evidence: webhooks Slack/Discord/Dingtalk at `internal/route/repo/webhook.go:202/235/267`; protected branches in `repo_branch.go`; deploy keys at `route/repo/setting.go:655`.

## Database stores

`internal/database/` is the only database package (there is NO `internal/db/`). Engine selection by driver name at `database.go:87-92` (`postgres`, `mysql`, `sqlite3`) using GORM (`go.mod:58-60`) with pure-Go `glebarez` SQLite drivers (`go.mod:19-20`). Key stores:

| Store file | Responsibility |
|---|---|
| `database.go` | Engine setup, driver selection, connection |
| `models.go` | Core model structs |
| `migrations/` | Schema migrations |
| `users.go`, `two_factor.go` | Users, 2FA (OTP, `go.mod:40` pquerna/otp) |
| `repo.go`, `repositories.go`, `repo_branch.go`, `repo_editor.go`, `repo_tag.go` | Repos, branches (protected branches), editor ops, tags |
| `mirror.go` | Repository mirroring from other hosts |
| `pull.go` | Pull requests; `MergeStyleRebase` at :189, applied at :255/:278 |
| `issue.go`, `issue_label.go`, `issue_mail.go` | Issues, labels, mail notifications |
| `milestone.go`, `release.go`, `attachment.go` | Milestones, releases, attachments |
| `wiki.go` | Wiki pages |
| `webhook.go`, `webhook_slack.go`, `webhook_discord.go`, `webhook_dingtalk.go` | Webhook delivery + channel adapters |
| `actions.go` | Actions (CI/CD) records |
| `access_tokens.go`, `login_sources.go`, `public_keys.go`, `ssh_key.go` | Tokens, auth sources, SSH keys, deploy keys |
| `backup.go` | Backup archive import/export helpers |
| `org.go`, `organizations.go`, `org_team.go` | Organizations and teams |
| `permissions.go` | Access control |

## SSH serv flow

The `serv` command (invoked by the SSH server via `~/.ssh/authorized_keys` command directive) gates and executes Git:

1. `internal/ssh/ssh.go` accepts the SSH connection and runs `gogs serv ...`.
2. `cmd/gogs/serv.go` parses the original SSH command (`parseSSHCmd`, :94-100) and checks the verb against `allowedCommands` (:120-123): `git-upload-pack` → Read, `git-receive-pack` → Write.
3. Unauthorized verbs are rejected (`fail`, :37-49); deploy keys are validated (:102-118); access mode resolved at :172.
4. The git binary is exec'd directly: `exec.Command(verbs[0], verbs[1], repoFullName)` / `exec.Command(verb, repoFullName)` (:251-253) with `cwd = conf.Repository.Root` (:269).
5. For write access, `database.ComposeHookEnvs` (:255-267) injects auth/repo env vars so Git hooks can run `gogs hook` with identity context.

## web/ frontend structure

React SPA (progressive migration from server-rendered Semantic UI templates):

| Path | Role |
|---|---|
| `web/package.json` | `@tanstack/react-query` (:27), `@tanstack/react-router` (:28) |
| `web/src/router.tsx`, `web/src/routes/` | Route definitions: `repo.tsx`, `user.tsx` (TanStack Router file routes) |
| `web/src/pages/` | Page components: `Landing.tsx`, `NotFound.tsx`, `ServerError.tsx`, `repo/`, `user/` |
| `web/src/App.tsx`, `main.tsx` | App shell + entry |
| `web/src/lib/`, `components/`, `locales/` | Data fetching, shared components, i18n |

## Configuration sections (`internal/conf/conf.go`)

Key `app.ini` sections mapped via `gopkg.in/ini.v1`:

| Section | Responsibility |
|---|---|
| `[server]` | HTTP listen address/port, SSH domain/port, protocol |
| `[database]` | Driver (`postgres`/`mysql`/`sqlite3`), host, name, credentials |
| `[lfs]` | LFS enable, `ObjectsPath`/`ObjectsTempPath` (conf.go:386-393) |
| `[auth]` | Auth backends; `TrustedProxyIPs` parsed into `TrustedProxyCIDRs` (conf.go:247-263) |
| `[repository]` | Repo root (`conf.Repository.Root`), mirror/upload settings |
| `[log]`, `[security]`, `[mailer]`, `[webhook]`, etc. | Logging, secrets/session, email, webhook delivery |

## internal/ 36-package summary

| Group | Packages |
|---|---|
| Domain/feature | `app`, `auth`, `authx`, `avatar`, `cron`, `database`, `email`, `form`, `gitx`, `lfsx`, `markup`, `repox`, `ssh`, `template`, `userx` |
| HTTP/routing | `context`, `httplib`, `route` |
| Config/util | `conf`, `cryptox`, `errx`, `iox`, `lazyregexp`, `netx`, `osx`, `pathx`, `process`, `ptrx`, `semverx`, `strx`, `sync`, `tool`, `urlx` |
| Test support | `dbtest`, `dbx`, `mocks`, `testx` |

## Related

- [[gogs]] — Main wiki entry
- [[gogs-cli]] — CLI command reference
- [[gogs.codegraph-verify]] — Evidence-backed claim verification
- [[gogs-api]] — REST API reference
- [[gogs-deployment]] — Deployment options and configuration
