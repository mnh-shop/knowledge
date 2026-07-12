---
name: hermes-autonomous-server-architecture
tags: [hermes-autonomous-server, architecture, hermes-agent]
description: "Reboot-safe headless deployment architecture for Hermes Agent — systemd gateway service, native cron scheduler, layered service model"
source: sources/hermes-autonomous-server/
verification_date: 2026-07-12
verified_by: source README + wiki
---

# Hermes Autonomous Server — Architecture

**Source:** `sources/hermes-autonomous-server/`

## Overview

Hermes Autonomous Server is a production-ready deployment pattern for running Hermes Agent on dedicated Linux infrastructure. It layers systemd service management over the native Hermes scheduler to create a reboot-safe, fully headless runtime. The architecture eliminates shell-based infinite loops, TTY hacks, and third-party hosting in favor of clean OS-level service integration. This is an independent deployment guide (not official Hermes project, not affiliated with Nous Research).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Linux Server (Ubuntu/Debian)               │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              systemd (PID 1)                          │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │       hermes-gateway.service                    │  │   │
│  │  │  ┌──────────────────┐  ┌───────────────────┐   │  │   │
│  │  │  │  Restart=always   │  │  WantedBy=multi-  │   │  │   │
│  │  │  │  RestartSec=10   │  │  user.target      │   │  │   │
│  │  │  └──────────────────┘  └───────────────────┘   │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│                         │                                    │
│                         v                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Hermes Gateway Process                   │   │
│  │  ┌──────────┐     ┌──────────────┐                    │   │
│  │  │ Authenti-│     │  Scheduler   │                    │   │
│  │  │ cation   │────>│  Manager     │                    │   │
│  │  │ (Nous    │     │  (native     │                    │   │
│  │  │  Portal) │     │   cron)      │                    │   │
│  │  └──────────┘     └──────┬───────┘                    │   │
│  └──────────────────────────┼────────────────────────────┘   │
│                             │                                 │
│                             v                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Claude Model (Nous Portal)               │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │   │
│  │  │ Receive  │  │ Process  │  │ Generate ~180-   │   │   │
│  │  │ Task     │──>│ (gateway)│──>│ word response   │   │   │
│  │  └──────────┘  └──────────┘  └────────┬─────────┘   │   │
│  └────────────────────────────────────────┼──────────────┘   │
│                                           v                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Local Output Files                       │   │
│  │  (journald logs, cron execution output, task files)   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Layered Architecture

The architecture follows a strict dependency chain with four layers:

1. **OS Layer** (systemd): Provides process lifecycle management, auto-restart on crash, reboot persistence. The `hermes-gateway.service` systemd unit runs under a dedicated non-root user with `Restart=always` and 10-second restart delay.

2. **Gateway Layer** (Hermes Gateway): The persistent process that manages authentication state, keeps the Nous Portal session alive, and serves as the runtime for scheduled tasks. Runs via `hermes gateway` command.

3. **Scheduler Layer** (Hermes Cron Scheduler): Native cron-based scheduling built into Hermes Agent. Cron jobs are created through the Hermes chat interface and persisted in Hermes's internal state. The gateway must be running for cron jobs to execute.

4. **Execution Layer** (Claude Model via Nous Portal): Each cron firing sends a task to the Claude model through Nous Portal's API. Responses are limited (configurable, ~180 words typical) and cost approximately $0.002 per execution.

### Key Design Decisions

- **Native Hermes scheduler** over shell-based loops: Hermes's built-in cron scheduler is more reliable and manageable than `while true; do ...; sleep 600; done` patterns.
- **System-level systemd service** over user-level: VPS environments often lack `systemctl --user` support. System-level services are universally available and survive user session termination.
- **Dedicated non-root user** over root: Reduces security surface. The service runs as user `hermes` with sudo privileges only for initial setup.
- **journald logging** over file logs: Standardized, persistent, queryable via `journalctl -u hermes-gateway -f`.

## Key Components

### systemd Service Unit (`/etc/systemd/system/hermes-gateway.service`)

```ini
[Unit]
Description=Hermes Gateway Service
After=network.target

[Service]
User=hermes
WorkingDirectory=/home/hermes
ExecStart=/home/hermes/.local/bin/hermes gateway
Restart=always
RestartSec=10
Environment=PATH=/home/hermes/.local/bin:/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=multi-user.target
```

### Cron Job Management

Jobs are created interactively via `hermes chat` using natural language ("Create a cronjob that runs every 10 minutes...") and managed via `hermes cron list`, `hermes cron status`. Each execution consumes Nous Portal API credits.

### Monitoring Tools

- `journalctl -u hermes-gateway -f` — real-time gateway logs
- `hermes cron status` — scheduler health
- `hermes cron list` — active job listing
- `sudo systemctl status hermes-gateway` — service health

## Related

- [[hermes-autonomous-server]] — Wiki page with deployment and setup guide
- [[hermes-agent]] — Core Hermes agent platform that this architecture deploys
- [[hermes-suite]] — All-in-one container image stack (alternative deployment)
- [[hermes-workspace]] — Command center with swarm (alternative deployment)
- [[hermes-caduceus]] — Inter-agent communication (complementary to autonomous operation)
