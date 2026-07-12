---
name: hermes-n8n-workflow-engine
type: integration
tags: [hermes-agent, n8n, integration, workflow-automation, webhook, mcp]
description: "Bidirectional integration between Hermes Agent and n8n: Hermes triggers n8n workflows via webhooks, n8n notifies Hermes via its MCP client node"
---

# Integration: Hermes Agent + n8n Workflow Engine

## Overview

Hermes Agent triggers n8n workflows via webhooks and n8n notifies Hermes via MCP. This is a bidirectional pattern: Hermes agents call n8n workflows as tools (outbound), and n8n workflows send results or request agent intervention via Hermes's MCP messaging bridge (inbound). Both run as rootless Podman containers on a shared Quadlet network.

## Architecture

```
Hermes Agent (port 8642)              n8n (port 5678)
     │                                      │
     ├─ MCP client ──HTTP──►  n8n webhook  │
     │  (via mcp_servers)   POST /webhook/  │
     │                        trigger workflow
     │                                      │
     │  ◄──MCP message──  n8n MCP node     │
     │  (via hermes mcp serve)  call tool   │
     │                        send message  │
     │                                      │
     └── Shared Quadlet network ────────────┘
```

**Direction A (Hermes → n8n)**: Hermes sends HTTP POST to n8n webhook endpoints with workflow payload. n8n executes the workflow and optionally calls back via webhook response.

**Direction B (n8n → Hermes)**: n8n's `MCPNode` (native in n8n v2.28+) connects to Hermes's MCP messaging bridge (`hermes mcp serve`) as an MCP client. It calls `send_message` to post results to Hermes channels, or `list_conversations` to read agent context.

## Configuration

### Shared Quadlet Network

Create `~/.config/containers/systemd/hermes-n8n.network`:

```ini
[Network]
Description=Shared network for Hermes and n8n
Subnet=10.90.0.0/24
```

### Hermes Agent with n8n MCP Client Config

`~/.config/containers/systemd/hermes-agent.container`:

```ini
[Unit]
Description=Hermes Agent with n8n integration
After=network-online.target

[Container]
Image=docker.io/nousresearch/hermes-agent:latest
ContainerName=hermes
Network=hermes-n8n.network
Exec=gateway run
Environment=HERMES_DASHBOARD=1
Environment=API_SERVER_ENABLED=true
Environment=API_SERVER_PORT=8642
EnvironmentFile=%h/.config/hermes/agent.env
Volume=%h/.hermes:/opt/data:Z
PublishPort=127.0.0.1:8642:8642
PublishPort=127.0.0.1:9119:9119

[Service]
Type=forking
Restart=on-failure

[Install]
WantedBy=default.target
```

Add to Hermes `config.yaml`:

```yaml
mcp_servers:
  n8n-webhook:
    url: "http://n8n:5678/"

# Register n8n's workflow execution as a tool
tools:
  n8n-run-workflow:
    type: webhook
    url: "http://n8n:5678/webhook/{{workflow_id}}"
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
Network=hermes-n8n.network
PublishPort=127.0.0.1:5678:5678
Volume=%h/.n8n:/home/node/.n8n:Z
Environment=DB_TYPE=sqlite
Environment=N8N_EDITOR_BASE_URL=http://localhost:5678
Environment=GENERIC_TIMEZONE=UTC

[Service]
Restart=always

[Install]
WantedBy=default.target
```

### n8n MCP Node Configuration

Inside the n8n editor, configure the **MCP Client Tool** node to connect to Hermes:

| Parameter | Value |
|-----------|-------|
| Server URL | `http://hermes:8642/mcp` |
| Server Type | HTTP / SSE |
| Auth Token | (optional — Hermes gateway token) |

The MCP node exposes Hermes's messaging tools (`send_message`, `list_conversations`, `get_conversation_history`) as workflow-accessible tools, enabling n8n workflows to post results back to user channels or query agent context.

## Deployment Steps

```bash
# 1. Create config directories
mkdir -p ~/.config/containers/systemd ~/.hermes ~/.n8n ~/.config/hermes

# 2. Write Hermes environment file
cat > ~/.config/hermes/agent.env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-...
EOF
chmod 600 ~/.config/hermes/agent.env

# 3. Write Quadlet and network files (from above)

# 4. Pull images
podman pull docker.io/nousresearch/hermes-agent:latest
podman pull docker.n8n.io/n8nio/n8n:2.28.1

# 5. Start stack
systemctl --user daemon-reload
systemctl --user start n8n.service
systemctl --user start hermes-agent.service

# 6. Configure n8n webhooks:
#    - Create a Webhook node in n8n editor (port 5678)
#    - Copy the webhook URL (POST /webhook/<id>)
#    - Register it in Hermes mcp_servers config
#    - Restart hermes-agent: systemctl --user restart hermes-agent.service

# 7. Verify
curl -s http://127.0.0.1:8642/health
curl -s http://127.0.0.1:5678/healthz
```

## Related

- [[hermes-agent]] — Core agent runtime (MCP client + server)
- [[n8n]] — Workflow automation platform
- [[hermes-workspace]] — Hermes UI with swarm orchestration
- [[n8n-mcp]] — Standalone MCP server for n8n node documentation
- [[assets/deployment/hermes-agent-quadlet.md]] — Hermes Quadlet reference
- [[domains/mcp/hermes-mcp-implementation.md]] — Hermes MCP bridge details
- [[integrations/nix-podman-stacks-n8n.md]] — Nix-based n8n deployment
