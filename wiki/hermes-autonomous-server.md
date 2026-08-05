---
name: hermes-autonomous-server
description: "Autonomous Hermes server agent with self-healing and adaptive runtime capabilities"
source: sources/hermes-autonomous-server/
verification_date: 2026-07-12
verified_by: codegraph-verify
tags: [agent, hermes-agent, deployment, monitoring, security, hermes-autonomous-server]
---

# 🚀 Hermes Agent – Autonomous Linux Server Setup

A clean, reboot-safe, headless deployment guide for Hermes Agent on dedicated Linux servers using native Hermes scheduler and systemd gateway service.

## Summary

Hermes Autonomous Server is a production-ready deployment approach that allows you to run Hermes Agent fully autonomously on your own infrastructure. This setup eliminates shell loops, TTY hacks, and third-party hosting requirements in favor of clean systemd integration and native cron scheduling.

> **Note:** The repository is a single README (335 lines) — a pure prose deployment guide with the systemd unit defined inline. It ships no scripts, service files, or tests.

**Key Features:**
- ✅ Reboot-safe operation
- ✅ Fully headless deployment
- ✅ Native systemd service integration
- ✅ Native cron scheduler
- ✅ Self-hosted infrastructure

## Architecture Overview

```
Systemd (system service)
        ↓
Hermes Gateway
        ↓
Hermes Cron Scheduler
        ↓
Claude Model (Nous Portal)
        ↓
Local Output Files
```

## Core Components

### Requirements
- **Nous Portal subscription** with API credits
- **Ubuntu/Debian** system with systemd
- **Dedicated server or VPS**
- **Non-root user recommended** (e.g., `hermes`)

### What This Guide Covers
- Installing Hermes Agent
- Authentication with Nous Portal  
- Creating autonomous cron jobs
- Setting up Hermes Gateway as system service
- Ensuring headless operation
- Reboot survival guarantees

## Key Differentiators

❌ **This is NOT:**
- An official Hermes project
- Affiliated with Nous Research
- A hosted service
- Shell-based infinite loops
- Fragile TTY emulation hacks

✅ **This IS:**
- A deployment guide for self-hosted Hermes
- Clean production-ready architecture
- Minimal operational complexity
- Full infrastructure control

## Operation Model

Once configured, Hermes runs fully autonomous:

1. **Setup Phase**: Install agent, authenticate, create cron jobs
2. **Runtime**: Systemd service manages Hermes Gateway
3. **Execution**: Native cron scheduler fires Hermes tasks automatically
4. **Persistence**: Auto-starts on reboot, survives system crashes

## Cost Considerations

Typical configuration:
- **Interval**: 10-minute cron jobs
- **Response size**: ~180 words per execution
- **Monthly runs**: ~4,320 executions
- **Estimated cost**: $8–12/month (model-dependent)

## Monitoring & Maintenance

### Gateway Logs
```bash
journalctl -u hermes-gateway -f
```

### Cron Job Status
```bash
hermes cron status
hermes cron list
```

### Emergency Commands
```bash
# Service control
sudo systemctl stop/start/restart hermes-gateway
sudo systemctl enable hermes-gateway

# Authentication
hermes login
hermes status

# Cron management — create jobs conversationally inside hermes chat
hermes chat
```

> **Note:** Cron jobs are **not** created via any CLI subcommand — the `hermes cron` interface exposes no job-creation command. Jobs are created conversationally inside the interactive `hermes chat` shell — e.g. "Create a cronjob that runs every 10 minutes. The task should: Write a short reflective paragraph about technology trends. Limit response to 180 words." — and Hermes returns a job ID. The scheduler is managed read-only via `hermes cron status` and `hermes cron list` (see Monitoring & Maintenance).

## Security Guidelines

- **Network**: Do not expose publicly without proper firewall rules
- **Privileges**: Never run as root
- **Monitoring**: Regularly track API usage and billing
- **Updates**: Keep server OS and packages current
- **Trust**: Assume this runs on trusted infrastructure only

## Uninstall Procedure

```bash
sudo systemctl stop hermes-gateway
sudo systemctl disable hermes-gateway
hermes uninstall
```

## Why This Approach?

The README's rationale ("Why This Approach?") makes the case for native Hermes scheduling over brittle alternatives:

✅ **Advantages:**
- Native Hermes scheduler integration
- No shell-based infinite loops
- No TTY emulation hacks
- Clean systemd integration
- Minimal operational complexity
- Fully self-hosted control

✅ **Reboot & Crash Safety:**
- Automatic reboot recovery — service is enabled at boot (`WantedBy=multi-user.target`)
- Persistent background operation — no open SSH session required
- Fully headless operation
- Crash-restart protection — the systemd unit sets `Restart=always` with `RestartSec=10`, so the gateway auto-restarts if it crashes

This autonomous server setup represents the most robust and production-ready approach for running Hermes AI agents continuously on dedicated infrastructure.

## Related

- [[hermes-agent]] — Core Hermes agent platform
- [[domains/deployment/INDEX|deployment]] — Deployment patterns