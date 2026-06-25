---
name: gogs
description: Gogs — Self-Hosted Git Service
tags: [gogs, wiki, golang, git, self-hosted, version-control, ssh, developer-tools, security, container, ai-llm, automation, bootc, cli, docker, messaging, nix, plugin-sdk, quadlet, storage, systemd, webhook]
---

# Gogs — Self-Hosted Git Service

| Field | Value |
|---|---|
| **Origin** | [gogs/gogs](https://github.com/gogs/gogs) |
| **License** | MIT |
| **Stack** | Go, PostgreSQL/MySQL/SQLite, SSH, Go 1.26 |
| **Source** | `sources/gogs/` |
| **Wanted** | Lightweight self-hosted Git service for agent code repositories and CI/CD integration |

## What it is

Gogs (pronounced /gɑgz/) is a self-hosted Git service written in Go — standalone binary, cross-platform, minimal resource requirements. It provides GitHub-like features (repositories, issues, pull requests, wikis, webhooks) with a focus on being painless to set up and run on modest hardware.

It is actively compatible with our knowledge system — the repo includes `AGENTS.md`, `CLAUDE.md`, and `skills-lock.json` for agent-assisted development.

## Features

- **Repository management** — public/private repos, organization repos, collaboration
- **Code hosting** — SSH, HTTP, HTTPS protocol access; Git LFS support
- **Issue tracking** — issues, labels, milestones, assignment
- **Pull requests** — with code review, protected branches, merge strategies
- **Wiki** — built-in project wiki
- **Webhooks** — repository and organization webhooks (Slack, Discord, Dingtalk, custom)
- **Git hooks** — repository-level Git hooks and deploy keys
- **Web editor** — quick file editing and wiki editing via browser
- **Repository migration/mirroring** — import repos from other hosts with wiki
- **Rendering** — Jupyter Notebook and PDF rendering
- **Authentication** — SMTP, LDAP, reverse proxy, GitHub.com, GitHub Enterprise, 2FA
- **Localization** — 31+ languages
- **API** — experimental API with [documentation](https://gogs.io/api-reference)
- **Database** — PostgreSQL, MySQL, MariaDB, SQLite3, or compatible

## Architecture

```
User → SSH / HTTP / HTTPS
        │
        ▼
┌─────────────────────────────────┐
│        Gogs Binary              │
│  ┌─────────┐  ┌───────────┐    │
│  │ Web     │  │ SSH       │    │
│  │ Routes  │  │ Server    │    │
│  └────┬────┘  └─────┬─────┘    │
│       │              │          │
│       ▼              ▼          │
│  ┌─────────────────────────┐   │
│  │     Internal Services   │   │
│  │  ┌──────┐ ┌──────┐     │   │
│  │  │ Repo │ │ Auth │     │   │
│  │  ├──────┤ ├──────┤     │   │
│  │  │ Issue│ │ User │     │   │
│  │  ├──────┤ ├──────┤     │   │
│  │  │ Web  │ │ LFS  │     │   │
│  │  └──────┘ └──────┘     │   │
│  └─────────────────────────┘   │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│         Database                │
│  (PostgreSQL / MySQL / SQLite)  │
│         +                       │
│    Git repos on disk            │
└─────────────────────────────────┘
```

### Package Structure

| Package | Purpose |
|---|---|
| `cmd/gogs/` | CLI entry points: `main.go`, `admin.go`, `backup.go`, `restore.go`, `hook.go`, `import.go`, `serv.go` |
| `internal/app/` | Core application logic |
| `internal/route/` | Web route handlers |
| `internal/conf/` | Configuration management |
| `internal/db/` / `internal/database/` | Database layer with migrations |
| `internal/auth/` | Authentication backends (LDAP, SMTP, OAuth, etc.) |
| `internal/ssh/` | SSH server for Git operations |
| `internal/repox/` | Repository management |
| `internal/gitx/` | Git operations |
| `internal/lfsx/` | Git LFS implementation |
| `internal/markup/` | Rendering engine (Markdown, Jupyter, PDF) |
| `internal/email/` | Notification emails |
| `internal/cron/` | Scheduled tasks |
| `internal/template/` | HTML templates |
| `internal/avatar/` | Avatar generation |
| `web/` | React frontend (TanStack Router, migration in progress) |

### Stack

- **Language:** Go 1.26
- **Web framework:** [Flamego](https://github.com/flamego/flamego) (v1.12)
- **Database:** PostgreSQL, MySQL/MariaDB, SQLite3 via GORM-compatible drivers
- **Frontend:** React + TanStack Router (progressive migration from Semantic UI templates)
- **SSH:** Built-in SSH server for Git protocol
- **Build system:** Moonrepo monorepo (`moon.yml`)

## Resource Requirements

- **Minimum:** Raspberry Pi or $5 VPS — 64MB RAM enough for personal use
- **Team baseline:** 2 CPU cores, 512MB RAM
- **Browser support:** Minimum 1024×768 resolution

## Deployment

Gogs can run as a standalone binary, behind a reverse proxy, or in Docker:

```bash
# Quick start with binary
./gogs web

# Docker
docker run --name=gogs -p 10022:22 -p 10880:3000 gogs/gogs
```

## API

Gogs has an experimental REST API documented at https://gogs.io/api-reference.

## Integration with Core Systems

- **Hermes / OpenClaw** — Can serve as a private Git backend for agent code repositories, deployment scripts, and configuration
- **n8n** — Webhooks enable n8n workflows triggered by Git events (push, PR, issues)
- **Agentfield / SWE-AF** — Git operations (clone, push, PR) as part of agent workflows
- **Hermzner / tank-os** — Can host deployment configs, Quadlet files, bootc image specs

## Related

- [[hermzner]] — Hetzner VPS deployment, could host Gogs for agent code repos
- [[tank-os]] — Bootc appliance, Gogs could host its build configs
- [[n8n]] — Webhook integration for Git event → workflow pipelines
- [[SWE-AF]] — Autonomous engineering runtime, uses Git for code management
- [[gogs-architecture]] — Architecture and component design
- [[gogs-api]] — REST API reference
- [[gogs-deployment]] — Deployment options and configuration

## Cross-project

- [[hermes-agent]] — Git backend for Hermes agent code repositories
- [[openclaw]] — Git backend for OpenClaw agent code repositories
- [[agentfield]] — Git operations in agent workflow automation
- [[mission-control]] — Pipeline integration with Git events
- [[podman]] — Container runtime for Gogs deployment
- [[sec-af]] — Security auditing of Git repositories
- [[nix-podman-stacks]] — Nix-based deployment of Gogs
