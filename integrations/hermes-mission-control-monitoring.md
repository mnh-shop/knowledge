---
name: hermes-mission-control-monitoring
type: integration
tags: [hermes-agent, mission-control, integration, monitoring, dashboard, health-check, alert, prometheus]
description: "Integration: Mission Control dashboard monitoring Hermes Agent deployments"
---

# Integration: Hermes Agent ↔ Mission Control Monitoring

**Sources**: `sources/hermes-agent/`, `sources/mission-control/`

## Overview

Mission Control acts as the **observability and orchestration dashboard** for one or more Hermes Agent instances. It monitors execution traces, health status, skill usage, and routes alerts -- all without being tied to Hermes's internal storage. The integration uses Mission Control's REST API and MCP server to pull state from Hermes, combined with Prometheus metrics scraping for health monitoring.

## Architecture

```
 Hermes Agent Instance          Mission Control Dashboard
┌─────────────────────┐        ┌──────────────────────────┐
│ hermes_cli/         │        │ Panels:                  │
│  - agent loop       │───────▶│  - Agents (status)       │
│  - mcp_tool.py      │ REST   │  - Tasks (executions)    │
│  - skill_manager    │  API   │  - Logs (streaming)      │
│  - memory           │        │  - Alerts (health)       │
│  - cron scheduler   │        │  - Skills (catalog)      │
└─────────────────────┘        │  - Events (live)         │
                               └──────────────────────────┘
                                        │
                                        ▼
                               ┌──────────────────┐
                               │  Prometheus       │
                               │  (scrape /metrics)│
                               └──────────────────┘
```

Mission Control's gateway-agnostic design means it connects to Hermes via a **framework adapter** -- a thin Hermes plugin that exposes execution state through Mission Control's REST API format.

## Concrete Setup

### 1. Hermes Agent Prometheus Export

Enable Hermes's built-in metric emission (configured in `~/.hermes/config.yaml`):

```yaml
observability:
  prometheus:
    enabled: true
    port: 9091
  log_level: info
```

This exposes `/metrics` at `http://localhost:9091` with counters for:
- `hermes_executions_total{status="success|error"}`
- `hermes_skills_invoked_total{skill="<name>"}`
- `hermes_agents_active`

### 2. Mission Control Hermes Adapter

```bash
# Register Hermes as a gateway in Mission Control
pnpm mc gateways add \
  --name "hermes-prod" \
  --type "hermes" \
  --endpoint "http://localhost:9090" \
  --health-endpoint "http://localhost:9090/health" \
  --metrics-endpoint "http://localhost:9091/metrics"
```

Mission Control polls the Hermes REST API (default port 9090) for agent status and task queue state, and scrapes the Prometheus endpoint for time-series metrics.

### 3. Alert Routing

Configure alerts in Mission Control's Alerts panel:

```json
{
  "rules": [
    {
      "name": "hermes-down",
      "condition": "hermes_agents_active == 0",
      "severity": "critical",
      "actions": ["webhook:https://hooks.slack.com/...", "log"]
    },
    {
      "name": "high-error-rate",
      "condition": "rate(hermes_executions_total{status='error'}[5m]) > 10",
      "severity": "warning",
      "actions": ["webhook:https://hooks.slack.com/..."]
    }
  ]
}
```

## Quadlet Deployment (optional sidecar)

```ini
# ~/.config/containers/systemd/hermes-mc-bridge.container
[Unit]
Description=Hermes-to-Mission-Control bridge adapter
After=hermes.service mission-control.service
BindsTo=hermes.service

[Container]
Image=ghcr.io/builderz-labs/hermes-adapter:latest
ContainerName=hermes-mc-bridge
PullPolicy=newer
PublishPort=127.0.0.1:9390:9390
Environment=HERMES_ENDPOINT=http://127.0.0.1:9090
Environment=MC_ENDPOINT=http://127.0.0.1:3003

[Service]
Restart=always

[Install]
WantedBy=default.target
```

## Related

- [[hermes-agent]] -- Self-improving AI agent with multi-platform messaging
- [[mission-control]] -- Gateway-agnostic orchestration dashboard (32 panels)
- [[hermes-workspace]] -- Hermes's own web/desktop command center (alternative UI)
- [[prometheus]] -- Time-series metrics backend optionally scraped by MC
