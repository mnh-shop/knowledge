---
title: hermes-autonomous-server
subtitle: CodeGraph Verification
date: 2026-07-12
tags: [hermes-autonomous-server, codegraph-verify, hermes-agent, server]
suffix: .codegraph-verify
source: sources/hermes-autonomous-server/
related: [[hermes-autonomous-server]], [[hermes-agent]], [[hermes-workspace]], [[hermes-suite]]
verified-by: codegraph-explore
---

# hermes-autonomous-server — CodeGraph Verification

**Verification date:** 2026-07-12
**Verified by:** codegraph-explore
**Source reference:** `sources/hermes-autonomous-server/`

## Claim-1: Reboot-safe headless deployment guide for Hermes Agent

This repository provides a clean, production-ready architecture for running Hermes Agent autonomously on a dedicated Linux server without shell loops or TTY hacks.

**Source evidence:** README lines 1-24:
> "**Hermes Agent – Autonomous Linux Server Setup**\n\nA clean, reboot-safe, headless deployment guide for Hermes Agent.\n\nNo shell loops.\nNo fragile TTY hacks.\nNo third-party hosting required.\n\nClean, production-ready architecture."

**Supporting detail:** Badges confirm Linux-tested, systemd service, headless, and cron scheduler support (lines 9-13).

## Claim-2: Uses native Hermes scheduler with systemd gateway service

The guide configures Hermes Gateway as a system-level systemd service with cron scheduling — no infinite shell loops.

**Source evidence:** README lines 173-188 (systemd service definition):
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
...
[Install]
WantedBy=multi-user.target
```

**Supporting detail:** Lines 303-308 state: "Uses native Hermes scheduler / Avoids shell-based infinite loops / Avoids TTY emulation hacks / Clean systemd integration / Minimal operational complexity / Fully self-hosted."

## Claim-3: Architecture layers systemd → Gateway → Cron → Model → Output

The deployment follows a clear layered architecture with systemd at the top and local output files at the bottom.

**Source evidence:** README lines 224-236:
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

**Supporting detail:** The guide explains that cron jobs require the gateway to be running, API credits are consumed per execution, and monitoring is done via `journalctl` and `hermes cron` commands (lines 258-278).

## Claim-4: Nous Portal subscription required for model access

The guide clearly states that an active Nous Portal subscription is required for cron jobs and gateway tasks to function.

**Source evidence:** README lines 52-66:
> "You need an active **Nous Portal subscription**:\n👉 https://portal.nousresearch.com/billing\n\nWithout an active subscription or API credits:\n- Cron jobs will not execute\n- Gateway will run but no tasks will fire"

**Supporting detail:** The promotional code `HERMESAGENT` is mentioned for basic subscription activation (lines 65-66).

## Claim-5: Complete lifecycle management — install, monitor, uninstall

The guide covers the full lifecycle from dedicated user creation through installation, authentication, cron creation, service enablement, verification, monitoring, and clean uninstall.

**Source evidence:** README lines 82-107 (install steps):
```bash
sudo adduser hermes
sudo usermod -aG sudo hermes
su - hermes
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

**Supporting detail:** Uninstall steps at lines 293-297:
```bash
sudo systemctl stop hermes-gateway
sudo systemctl disable hermes-gateway
hermes uninstall
```

## Claim-6: Cost estimation and monitoring provided

The guide includes concrete cost estimates and monitoring commands for the autonomous setup.

**Source evidence:** README lines 239-248:
> "Example configuration:\n- 10-minute interval\n- ~180-word responses\n- ~4,320 runs/month\n- Typically ~$8-12/month depending on model and output size."

**Supporting detail:** Monitoring commands at lines 258-276: `journalctl -u hermes-gateway -f`, `hermes cron list`, `hermes cron status`.

## Claim-7: Security considerations documented

The guide includes explicit security guidance for production deployments.

**Source evidence:** README lines 322-329:
> "- Do not expose your server publicly without firewall rules.\n- Avoid running Hermes as root.\n- Monitor API usage regularly.\n- Keep your server updated.\n\nThis guide assumes a trusted VPS or dedicated environment."

**Supporting detail:** The guide is explicitly marked as an independent deployment guide not affiliated with Nous Research (lines 334-335).

## Dependency Map

```
hermes-autonomous-server
  └─► hermes-agent (upstream — provides installer, gateway, cron scheduler)
  └─► hermes-workspace (companion MCP hub server, shares config patterns)
  └─► hermes-suite (alternative all-in-one container approach)
```
