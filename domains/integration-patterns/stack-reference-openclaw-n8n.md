---
name: stack-reference-openclaw-n8n
description: "Deployment reference: combining OpenClaw agent gateway with n8n workflow engine"
tags: [architecture, container, integration, mcp, messaging, n8n, openclaw, podman, quadlet, storage, systemd, webhook]
---

# OpenClaw + n8n Stack Reference

## System Architecture

```
                          ┌──────────────────────────────┐
                          │        External World         │
                          │  (Telegram, Slack, HTTP, CLI) │
                          └──────────┬───────────────────┘
                                     │
                                     ▼
                ┌──────────────────────────────────────────┐
                │         OpenClaw Agent Gateway           │
                │           (port 18789)                    │
                │                                          │
                │   ┌──────────┐    ┌───────────────────┐  │
                │   │  Agent   │    │   MCP Server       │  │
                │   │  Router  │◄──►│   (tool provider)  │  │
                │   └────┬─────┘    └────────┬──────────┘  │
                └────────┼──────────────────┼──────────────┘
                         │                  │
                ┌────────▼──────┐  ┌────────▼──────────┐
                │   Webhook     │  │  MCP Tool Calls    │
                │   Outbound    │  │  (n8n → OpenClaw)  │
                └───────┬───────┘  └────────┬───────────┘
                        │                  │
                        ▼                  │
                ┌──────────────────┐       │
                │   n8n Workflow   │◄──────┘
                │   Engine         │
                │   (port 5678)    │
                └──────────────────┘
```

## Port Mappings

| Component          | Protocol | Port  | Service Name        |
|--------------------|----------|-------|---------------------|
| OpenClaw gateway   | HTTP     | 18789 | `openclaw`          |
| n8n web UI / API   | HTTP     | 5678  | `n8n`               |

## Communication Patterns

### OpenClaw webhooks -> n8n

OpenClaw agents can trigger n8n workflows by issuing HTTP POST requests to n8n webhook endpoints. This is the primary path for agent-initiated automation:

1. An OpenClaw agent (e.g., Telegram handler) receives a message.
2. The agent decides a workflow step is needed and calls n8n's webhook URL.
3. n8n executes the workflow and optionally returns a result payload.
4. OpenClaw incorporates the result into its response.

### n8n -> OpenClaw MCP tools

n8n workflows can call back into OpenClaw via its MCP server API to invoke agent tools for AI-heavy processing:

1. An n8n workflow node makes an HTTP request to the OpenClaw MCP endpoint.
2. OpenClaw routes the request to the appropriate agent/tool.
3. The agent processes and returns structured data.
4. n8n continues the workflow with the enriched data.

## Quadlet Service Dependencies

```
# openclaw.container (podman quadlet)
[Unit]
Description=OpenClaw Agent Gateway
After=network-online.target
Wants=network-online.target

[Container]
Image=ghcr.io/openclaw/openclaw:latest
PublishPort=18789:18789
EnvironmentFile=%E/openclaw.env
Volume=/opt/openclaw/data:/data:Z

[Service]
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

```
# n8n.container (podman quadlet)
[Unit]
Description=n8n Workflow Engine
After=network-online.target openclaw.service
Wants=openclaw.service

[Container]
Image=docker.io/n8nio/n8n:latest
PublishPort=5678:5678
EnvironmentFile=%E/n8n.env
Volume=/opt/n8n/data:/home/node/.n8n:Z

[Service]
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

**Dependency chain:** `n8n` `After=openclaw.service` -- n8n starts after OpenClaw so MCP tool targets are available on boot.

## Environment Variables

### OpenClaw (`/etc/containers/openclaw.env`)

```
OPENCLAW_PORT=18789
OPENCLAW_AGENT_DIR=/opt/openclaw/agents
OPENCLAW_LOG_LEVEL=info
OPENCLAW_WEBHOOK_BASE_URL=http://n8n:5678
MCP_ENABLED=true
MCP_PORT=18789
```

### n8n (`/etc/containers/n8n.env`)

```
N8N_PORT=5678
N8N_PROTOCOL=http
N8N_HOST=localhost
N8N_EDITOR_BASE_URL=http://localhost:5678
WEBHOOK_URL=http://localhost:5678
EXECUTIONS_DATA_PRUNE=true
EXECUTIONS_DATA_MAX_AGE=168
OPENCLAW_MCP_URL=http://openclaw:18789/mcp
OPENCLAW_WEBHOOK_SECRET=<webhook-secret>
```

## Integration Scenarios

### Scenario 1: Telegram message -> OpenClaw -> n8n -> OpenClaw

1. User sends a Telegram message to the bot.
2. OpenClaw Telegram agent receives the message and decides it needs structured data enrichment.
3. OpenClaw sends an HTTP POST to n8n webhook endpoint with the message context.
4. n8n workflow enriches the data (calls external APIs, databases, etc.).
5. n8n returns the enriched result as the webhook response.
6. OpenClaw agent incorporates the enrichment and replies to the user on Telegram.

### Scenario 2: n8n scheduled report -> OpenClaw AI analysis -> Telegram/Slack

1. n8n cron trigger fires a scheduled workflow (e.g., daily sales summary).
2. n8n collects raw data from databases / APIs.
3. n8n calls the OpenClaw MCP endpoint with the raw data, requesting AI analysis.
4. OpenClaw agent processes the data and returns a natural-language summary.
5. n8n takes the summary and sends it to Telegram and/or Slack channels.
6. n8n optionally archives the raw data and the summary in a database.

### Scenario 3: Multi-step data pipeline

1. n8n ingests data on a schedule or webhook trigger (e.g., from a CRM sync).
2. n8n cleans and normalizes the data, then calls OpenClaw MCP for classification or insight extraction.
3. OpenClaw agent returns structured classifications.
4. n8n archives the enriched records to a data store (Postgres, S3, etc.).
5. n8n triggers a follow-up notification if classifications indicate action needed.

## Related Wikilinks

- [[openclaw-agent-gateway]]
- [[n8n-workflow-engine]]
- [[quadlet-deployment-guide]]
- [[mcp-server-setup]]
- [[telegram-bot-setup]]
- [[podman-pod-stack]]
