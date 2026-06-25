---
name: hermes-autonomous-server
description: "Autonomous Hermes server agent with self-healing and adaptive runtime capabilities"
source: sources/hermes-autonomous-server/
tags: [ai-llm, monitoring, security]
  - hermes
  - autonomous-server
  - deployment
  - linux-server
  - systemd
  - cron
  - nous-portal
---

# 🚀 Hermes Agent – Autonomous Linux Server Setup

A clean, reboot-safe, headless deployment guide for Hermes Agent on dedicated Linux servers using native Hermes scheduler and systemd gateway service.

## Summary

Hermes Autonomous Server is a production-ready deployment approach that allows you to run Hermes Agent fully autonomously on your own infrastructure. This setup eliminates shell loops, TTY hacks, and third-party hosting requirements in favor of clean systemd integration and native cron scheduling.

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
harmes status

# Cron management
hermes chat
harmes cron create [schedule]
```

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
harmes uninstall
```

## Why This Approach?

✅ **Advantages:**
- Native Hermes scheduler integration
- No shell-based infinite loops
- No TTY emulation hacks
- Clean systemd integration
- Minimal operational complexity
- Full self-hosted control

✅ **Production Benefits:**
- Automatic reboot recovery
- Persistent background operation
- System-level service management
- Native cron scheduling
- Headless operation
- Memory leak protection

This autonomous server setup represents the most robust and production-ready approach for running Hermes AI agents continuously on dedicated infrastructure.