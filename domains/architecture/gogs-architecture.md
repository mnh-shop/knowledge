---
name: gogs-architecture
description: Gogs Architecture — Self-Hosted Git Service
tags: [gogs, git, architecture]
---

# Gogs Architecture — Self-Hosted Git Service

| Field | Value |
|---|---|
| **Origin** | [gogs/gogs](https://github.com/gogs/gogs) |
| **Source** | `sources/gogs/` |
| **Stack** | Go 1.26, Flamego 1.12, PostgreSQL/MySQL/SQLite, SSH, Moonrepo monorepo |
| **Runtime** | Linux, macOS, Windows, ARM — standalone binary |

## Overview

Gogs is a self-hosted Git service implemented as a single Go binary. It integrates web, SSH, and Git protocol handling, file-based repository storage, and database-backed metadata. The codebase organizes core business logic under `internal/` with a clean separation between web routes, authentication, Git operations, and database access.

## Component Architecture

```
┌─────────────────────────────────────────────────────┐
│                  HTTP Server (Flamego)                │
│  ┌───────────────────┐  ┌────────────────────────┐  │
│  │ HTML Routes        │  │ API Routes (exp.)      │  │
│  │ (webapp templates) │  │ (webapi handlers)      │  │
│  └─────────┬─────────┘  └───────────┬────────────┘  │
│            │                        │                │
│            ▼                        ▼                │
│  ┌──────────────────────────────────────────────┐   │
│  │            Internal Route Handlers           │   │
│  │  (internal/route/)                           │   │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐       │   │
│  │  │ repo │ │user  │ │org   │ │admin │       │   │
│  │  └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘       │   │
│  └─────┼────────┼────────┼────────┼────────────┘   │
└────────┼────────┼────────┼────────┼────────────────┘
         │        │        │        │
┌────────┼────────┼────────┼────────┼────────────────┐
│        ▼        ▼        ▼        ▼                │
│  ┌──────────────────────────────────────────────┐   │
│  │              Application Layer               │   │
│  │  internal/app/                               │   │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────────┐   │   │
│  │  │repo  │ │user  │ │issue │ │pull_req  │   │   │
│  │  │mgmt  │ │mgmt  │ │mgmt  │ │mgmt      │   │   │
│  │  └──────┘ └──────┘ └──────┘ └──────────┘   │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │         Git Operations (internal/gitx/)       │   │
│  │  push/pull/clone/fetch through SSH or HTTP   │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │         Data Layer                           │   │
│  │  internal/database/ (DB + migrations)        │   │
│  │  internal/conf/ (configuration)              │   │
│  │  internal/ssh/ (SSH server for Git)          │   │
│  │  internal/lfsx/ (Git LFS)                    │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## SSH Server

Gogs runs a built-in SSH server (separate from web) that handles Git protocol operations (clone, push, pull). Key components:

| Component | Purpose |
|---|---|
| `internal/ssh/` | SSH server implementation, key management |
| `cmd/gogs/serv.go` | SSH command handler — validates access, executes Git operations |

## Web Interface

Two rendering engines coexist during migration:

| Engine | Location | Status |
|---|---|---|
| Semantic UI templates | `templates/` + `public/` | Legacy, being migrated away |
| React + TanStack Router | `web/` | In-progress migration target |

See `web/DESIGN.md` for the React frontend design system.

## Configuration (`internal/conf/`)

Gogs is configured via INI-style config files. Key sections:

| Section | Purpose |
|---|---|
| `[server]` | HTTP/SSH listen addresses, domain, protocol |
| `[database]` | DB type (PostgreSQL/MySQL/SQLite), host, credentials |
| `[repository]` | Repo root path, force push, LFS settings |
| `[auth]` | Auth backends (LDAP, SMTP, GitHub, reverse proxy) |
| `[mailer]` | SMTP notification settings |
| `[webhook]` | Webhook delivery settings |
| `[cron]` | Scheduled task intervals |
| `[picture]` | Avatar mode (local, Gravatar, libravatar, disabled) |
| `[session]` | Session storage (file, Redis, DB) |
| `[log]` | Log levels and outputs |

## Authentication Backends

| Backend | Support |
|---|---|
| Local (Gogs) | Full |
| SMTP/IMAP | Full |
| LDAP | Full |
| Reverse proxy | Full |
| GitHub.com | OAuth |
| GitHub Enterprise | OAuth |
| 2FA | Yes |

## Database

Gogs uses GORM (via the `db` package) for database operations. Schema migrations are managed through `internal/database/migrations/`. Supports:

- PostgreSQL
- MySQL / MariaDB
- SQLite3

## Build System

Gogs uses a Moonrepo monorepo setup (`moon.yml`) for builds:

```bash
moon run gogs:build    # Build Go binary
moon run web:dev       # Dev server for React frontend
moon run gogs:lint     # Lint Go code
moon run web:lint      # Lint frontend code
```

## Related

- [[gogs]] — Wiki entry
- [[gogs-deployment]] — Deployment options and configuration
- [[gogs-api]] — REST API reference
