---
name: openclaw-n8n-gateway
type: integration
tags: [openclaw, n8n, integration, mcp, agent-gateway, podman, quadlet]
description: "OpenClaw as an agent gateway routing agent requests to n8n workflows via MCP tools, with n8n's MCP client node consuming OpenClaw's channel bridge"
---

# Integration: OpenClaw + n8n — Agent Gateway to Workflow Engine

## Overview

OpenClaw acts as the agent gateway and n8n executes workflows on demand. OpenClaw agents invoke n8n workflows through MCP tools (exposing workflow triggers as agent-callable functions), and n8n workflows consume OpenClaw's MCP channel bridge to send messages to 30+ messaging platforms. Both run as rootless Podman Quadlets on a shared network.

## Architecture

```
OpenClaw Gateway (port 18789)          n8n (port 5678)
     │                                       │
     ├─ MCP tools ──HTTP──►  n8n webhook    │
     │  invoke_workflow     POST /webhook/   │
     │  check_execution     GET /execution/  │
     │                                       │
     │  ◄──MCP bridge── n8n MCP Node        │
     │                   OpenClaw channel    │
     │                   bridge tools        │
     │                   (send_message, etc.)│
     │                                       │
     └── Shared Quadlet network ─────────────┘
```

**OpenClaw → n8n direction**: OpenClaw's MCP surface exposes n8n workflow tools to agents. When an agent requests an action, OpenClaw dispatches it to n8n via HTTP webhook or the n8n REST API (port 5678). Execution results return as MCP tool responses.

**n8n → OpenClaw direction**: n8n's built-in MCP client node connects to OpenClaw's channel bridge MCP server (`src/mcp/channel-bridge.ts`), enabling workflows to send messages to any of OpenClaw's 30+ messaging channels (Telegram, Discord, WhatsApp, etc.) as part of workflow automation.

## Configuration

### Shared Quadlet Network

Create `~/.config/containers/systemd/gateway-net.network`:

```ini
[Network]
Description=Shared network for OpenClaw and n8n
Subnet=10.91.0.0/24
```

### OpenClaw Gateway Container

`~/.config/containers/systemd/openclaw.container`:

```ini
[Unit]
Description=OpenClaw Agent Gateway
After=network-online.target

[Container]
Image=ghcr.io/openclaw/openclaw:latest
ContainerName=openclaw
Network=gateway-net.network
PublishPort=127.0.0.1:18789:18789
Volume=%h/.openclaw:/home/node/.openclaw:Z
Environment=NODE_ENV=production
User=1000
Group=1000
HealthCmd=node -e "fetch('http://127.0.0.1:18789/healthz').then(r => process.exit(r.ok?0:1))"
HealthInterval=180s

[Service]
Restart=always

[Install]
WantedBy=default.target
```

### n8n Container

`~/.config/containers/systemd/n8n.container`:

```ini
[Unit]
Description=n8n Workflow Automation
After=network-online.target

[Container]
Image=docker.n8n.io/n8nio/n8n:2.28.1
ContainerName=n8n
Network=gateway-net.network
PublishPort=127.0.0.1:5678:5678
Volume=%h/.n8n:/home/node/.n8n:Z
Environment=DB_TYPE=sqlite
Environment=N8N_EDITOR_BASE_URL=http://localhost:5678

[Service]
Restart=always

[Install]
WantedBy=default.target
```

### OpenClaw MCP Configuration for n8n

OpenClaw agents need n8n webhooks registered as available tools. Define a custom tool in `~/.openclaw/openclaw.json`:

```json
{
  "plugins": {
    "mcp": {
      "servers": {
        "n8n-gateway": {
          "transport": "http",
          "url": "http://n8n:5678",
          "tools": ["list_workflows", "execute_workflow"]
        }
      }
    }
  }
}
```

Alternatively, deploy [[goclaw]] as a lightweight MCP bridge that routes agent tool calls to n8n HTTP endpoints with minimal overhead:

```bash
# GoClaw routes: agent → MCP bridge → n8n webhook
goclaw gateway --mcp-server-url http://n8n:5678 --port 18790
```

### n8n MCP Node to OpenClaw Channel Bridge

Inside the n8n editor, add an **MCP Client Tool** node with:

| Parameter | Value |
|-----------|-------|
| Server URL | `http://openclaw:18789/mcp` |
| Server Type | SSE |
| Connection Type | channel-bridge |

The connected tools include `send_message`, `list_channels`, `list_conversations` — enabling n8n workflows to dispatch results to Telegram, Discord, Slack, SMS, or any of OpenClaw's 30+ channels.

## Deployment Steps

```bash
# 1. Create config directories
mkdir -p ~/.config/containers/systemd ~/.openclaw ~/.n8n

# 2. Write OpenClaw config
cat > ~/.openclaw/openclaw.json << 'EOF'
{
  "gateway": {
    "port": 18789,
    "bind": "lan"
  },
  "plugins": {
    "mcp": {
      "servers": {}
    }
  }
}
EOF

# 3. Write Quadlet files (from above)

# 4. Pull images
podman pull ghcr.io/openclaw/openclaw:latest
podman pull docker.n8n.io/n8nio/n8n:2.28.1

# 5. Start stack
systemctl --user daemon-reload
systemctl --user start openclaw.service n8n.service

# 6. Verify
curl -s http://127.0.0.1:18789/healthz
curl -s http://127.0.0.1:5678/healthz

# 7. Configure n8n webhooks in the n8n editor UI,
#    then register them in openclaw.json's mcp_servers.
```

## Related

- [[openclaw]] — Agent gateway with 30+ messaging channels
- [[n8n]] — Workflow automation platform
- [[goclaw]] — Lightweight Go MCP bridge alternative for n8n routing
- [[n8n-mcp]] — MCP server for n8n node documentation and workflow CRUD
- [[assets/deployment/openclaw-quadlet.md]] — OpenClaw Quadlet reference
- [[domains/mcp/openclaw-mcp-implementation.md]] — OpenClaw's 3 MCP server surfaces
- [[integrations/hermes-n8n-workflow-engine.md]] — Equivalent Hermes + n8n pattern
