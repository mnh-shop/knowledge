---
name: stack-reference-mission-control
description: "Deployment reference: Mission Control dashboard monitoring agents"
tags: [ai-llm, architecture, container, dashboard, hermes, ideas, integration, mcp, messaging, mission-control, monitoring, openclaw, quadlet, stack-reference, systemd, webhook]
---

# Mission Control Stack Reference

## System Architecture

```
                          ┌──────────────────────────────────┐
                          │         Mission Control          │
                          │      (Dashboard + Monitor)       │
                          │       (port 3000 / 8080)         │
                          └────┬─────────────┬───────────────┘
                               │             │
                    ┌──────────▼──┐    ┌─────▼────────────┐
                    │  MCP Client │    │  Webhook Listener │
                    │  (pull      │    │  (push alerts)   │
                    │   status)   │    └────────┬─────────┘
                    └──────┬─────┘             │
                           │                   │
                    ┌──────▼───────────────────▼────┐
                    │         OpenClaw Gateway       │
                    │         (port 18789)           │
                    │         MCP Server             │
                    └────────────────────────────────┘

                          ┌──────────────────────────────────┐
                          │           Hermes                 │
                          │      (Notification Relay)        │
                          │       (port 9090)                │
                          └──────────────────────────────────┘
                                     │
                                     ▼
                          ┌──────────────────────────────────┐
                          │   Telegram / Slack / Email       │
                          └──────────────────────────────────┘
```

## MCP Integration for Agent Status

Mission Control connects to the OpenClaw MCP server to pull real-time status of all registered agents:

| MCP Tool               | Purpose                                      |
|------------------------|----------------------------------------------|
| `agent_list`           | List all agents and their current state       |
| `agent_status <id>`    | Get detailed status for a specific agent      |
| `agent_metrics <id>`   | Get runtime metrics (latency, errors, uptime) |
| `agent_logs <id>`      | Stream recent log entries                     |

Mission Control polls these endpoints on a configurable interval (default 30s) and updates the dashboard UI with agent health indicators (green/yellow/red).

## Webhook-Based Alerting

Agents can push alerts to Mission Control via webhooks for immediate display:

1. An OpenClaw agent detects an anomaly or threshold breach.
2. The agent sends an HTTP POST to Mission Control's webhook endpoint:
   ```
   POST /api/v1/alerts
   Content-Type: application/json

   {
     "agent": "telegram-bot",
     "severity": "warning",
     "title": "High latency detected",
     "message": "Response time exceeded 5s threshold",
     "timestamp": "2026-06-24T12:00:00Z"
   }
   ```
3. Mission Control displays the alert in the dashboard and optionally forwards it to Hermes for notification relay.

## Quadlet Dependencies

```
# mission-control.container
[Unit]
Description=Mission Control Dashboard
After=network-online.target openclaw.service
Wants=openclaw.service

[Container]
Image=ghcr.io/mission-control/mission-control:latest
PublishPort=3000:3000
EnvironmentFile=%E/mission-control.env
Volume=/opt/mission-control/data:/data:Z

[Service]
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

```
# hermes.container (if used alongside Mission Control)
[Unit]
Description=Hermes Notification Relay
After=network-online.target mission-control.service
Wants=mission-control.service

[Container]
Image=ghcr.io/hermes/hermes:latest
PublishPort=9090:9090
EnvironmentFile=%E/hermes.env
Volume=/opt/hermes/data:/data:Z

[Service]
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

**Dependency chain:** `mission-control` `After=openclaw.service` -- Mission Control reads agent status from OpenClaw on startup, so OpenClaw must be available first.

## Environment Variables

### Mission Control (`/etc/containers/mission-control.env`)

```
MC_PORT=3000
MC_DASHBOARD_TITLE=Agent Dashboard
MC_POLL_INTERVAL=30
MC_WEBHOOK_SECRET=<webhook-secret>
OPENCLAW_MCP_URL=http://openclaw:18789/mcp
OPENCLAW_MCP_API_KEY=<mcp-api-key>
HERMES_WEBHOOK_URL=http://hermes:9090/webhook
LOG_LEVEL=info
```

### Hermes (`/etc/containers/hermes.env`)

```
HERMES_PORT=9090
TELEGRAM_BOT_TOKEN=<telegram-token>
SLACK_WEBHOOK_URL=<slack-webhook-url>
SMTP_HOST=<smtp-host>
SMTP_PORT=587
SMTP_USER=<smtp-user>
SMTP_PASS=<smtp-pass>
NOTIFICATION_DEFAULT_CHANNEL=telegram
LOG_LEVEL=info
```

## Related Wikilinks

- [[openclaw-agent-gateway]]
- [[hermes-notification-relay]]
- [[mission-control-dashboard]]
- [[quadlet-deployment-guide]]
- [[mcp-server-setup]]
- [[telegram-bot-setup]]
- [[podman-pod-stack]]
- [[stack-reference-openclaw-n8n]]
