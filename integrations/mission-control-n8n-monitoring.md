---
name: mission-control-n8n-monitoring
type: integration
tags: [mission-control, n8n, integration, monitoring, dashboard, health-check, alert, prometheus]
description: "Mission Control dashboard monitoring n8n workflow executions, health checks, webhook alert routing"
---

# Integration: Mission Control ↔ n8n Monitoring

**Sources**: `sources/mission-control/`, `sources/n8n/`

## Overview

Mission Control serves as the observability dashboard for n8n workflow deployments. It natively supports n8n as a gateway type, polling execution status, health endpoints, and metrics via n8n's REST API. Alerts route through Mission Control's rules engine to Slack, email, or webhook targets.

## Architecture

```
n8n (:5678)                     Mission Control (:3003)
┌──────────────┐                ┌────────────────────────┐
│ REST API     │──────────────▶│ n8n Gateway Panel       │
│ /healthz     │  poll 30s     │ - Executions (live)     │
│ /workflows   │               │ - Failure rate          │
│ /executions  │               │ - Duration histograms   │
└──────────────┘               │ - Active webhooks       │
                               │ - Health checks         │
                               └───────────┬────────────┘
                                           ▼
                                  Alert Rules → Slack/Email
```

Mission Control's `n8n` gateway adapter polls n8n's REST API at configurable intervals. Execution failures, webhook errors, and instance health degradations surface on dedicated panels.

## Configuration

Register n8n in Mission Control:
```bash
pnpm mc gateways add \
  --name "n8n-prod" --type "n8n" \
  --endpoint "http://localhost:5678" \
  --health-endpoint "http://localhost:5678/healthz" \
  --poll-interval 30s --api-key "<n8n-api-key>"
```

Alert rules example:
```json
{
  "rules": [
    { "name": "n8n-down", "condition": "n8n_prod_health == 0",
      "severity": "critical", "actions": ["slack:#ops"] },
    { "name": "high-failure-rate", "condition": "n8n_prod_error_rate > 0.1",
      "severity": "warning", "actions": ["webhook:https://hooks.slack.com/..."],
      "threshold_window": "5m" }
  ]
}
```

Optional Prometheus scrape (enable via `N8N_METRICS=true`):
```bash
pnpm mc gateways update n8n-prod --metrics-endpoint "http://localhost:5678/metrics"
```

## Related

- [[mission-control]] — Gateway-agnostic orchestration dashboard (32 panels)
- [[n8n]] — Workflow automation platform
- [[hermes-agent]] — Co-monitored alongside n8n in the same MC dashboard
- [[prometheus]] — Metrics backend for time-series enrichment
- [[integrations/hermes-mission-control-monitoring.md]] — Same MC gateway pattern for Hermes
