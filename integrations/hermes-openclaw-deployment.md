---
name: hermes-openclaw-deployment
type: integration
tags: [hermes-agent, openclaw, deployment, integration, mcp, podman, quadlet]
description: "Side-by-side deployment of Hermes Agent and OpenClaw under rootless Podman with MCP bridge on a shared Quadlet network"
---

# Integration: Hermes Agent + OpenClaw — Side-by-Side Deployment

## Overview

Hermes Agent and OpenClaw are competing agent gateways with intentionally compatible MCP bridges. This integration deploys both as rootless Podman Quadlet services sharing a pod network, enabling cross-agent MCP communication. Hermes runs on port 8642 (gateway API) and 9119 (dashboard); OpenClaw runs on port 18789 (gateway) and 18790 (API). Both attach to the same Quadlet pod for localhost DNS resolution.

## Architecture

```
[Pod: agent-stack]
 ├── hermes-agent.container     Ports: 8642, 9119
 │    Image: nousresearch/hermes-agent:latest
 │    MCP bridge: 10 messaging tools (list/send conversations)
 │    ACP server: editor integration
 │
 ├── openclaw-gateway.container   Ports: 18789, 18790
 │    Image: ghcr.io/openclaw/openclaw:latest
 │    MCP bridge: 3 server surfaces (channel, plugin, built-in tools)
 │    ACP server: approval classifier + event ledger
 │
 └── Shared state via host bind mounts
      ~/.hermes/  ~/.openclaw/
```

**MCP bridge surface compatibility**: Hermes exposes 10 MCP tools for conversation management; OpenClaw exposes 9 matching tools plus 3 MCP server modes (channel bridge, plugin tools, built-in tools). Either agent can consume the other's MCP surface by pointing `mcp_servers` config at `http://<peer-container>:<mcp-port>` over the shared pod network.

## Configuration

### Quadlet Pod

Create `~/.config/containers/systemd/agent-stack.pod`:

```ini
[Pod]
PodName=agent-stack
PublishPort=127.0.0.1:8642:8642
PublishPort=127.0.0.1:9119:9119
PublishPort=127.0.0.1:18789:18789
PublishPort=127.0.0.1:18790:18790

[Service]
Restart=always

[Install]
WantedBy=default.target
```

### Hermes Agent Container

Create `~/.config/containers/systemd/hermes-agent.container`:

```ini
[Unit]
Description=Hermes Agent
After=network-online.target
Wants=network-online.target

[Container]
Image=docker.io/nousresearch/hermes-agent:latest
ContainerName=hermes
Pod=agent-stack.pod
Exec=gateway run
Environment=HERMES_DASHBOARD=1
Environment=HERMES_DASHBOARD_HOST=0.0.0.0
Environment=HERMES_DASHBOARD_PORT=9119
Environment=API_SERVER_HOST=0.0.0.0
Environment=API_SERVER_ENABLED=true
Environment=API_SERVER_PORT=8642
EnvironmentFile=%h/.config/hermes/agent.env
Volume=%h/.hermes:/opt/data:Z
HealthCmd=curl -fsS http://localhost:8642/health || exit 1
HealthInterval=10s
HealthRetries=5

[Service]
Type=forking
Restart=on-failure

[Install]
WantedBy=default.target
```

### OpenClaw Container

Create `~/.config/containers/systemd/openclaw-gateway.container`:

```ini
[Unit]
Description=OpenClaw Gateway
After=network-online.target
Wants=network-online.target

[Container]
Image=ghcr.io/openclaw/openclaw:latest
ContainerName=openclaw
Pod=agent-stack.pod
Exec=node openclaw.mjs gateway --port 18789 --bind lan
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

### Cross-Agent MCP Configuration

Configure Hermes to consume OpenClaw's MCP tools, and vice versa:

**Hermes `config.yaml`** (`mcp_servers` section):
```yaml
mcp_servers:
  openclaw:
    url: "http://openclaw:18789/mcp"
```

**OpenClaw** does not auto-discover MCP servers — use its MCP client plugin or deploy `openclaw-plugin-claude-code` as a bridge consuming Hermes MCP.

## Deployment Steps

```bash
# 1. Create config directories
mkdir -p ~/.config/containers/systemd ~/.hermes ~/.openclaw

# 2. Create Hermes environment file
cat > ~/.config/hermes/agent.env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-...
EOF
chmod 600 ~/.config/hermes/agent.env

# 3. Write Quadlet files (from above)

# 4. Pull images
podman pull docker.io/nousresearch/hermes-agent:latest
podman pull ghcr.io/openclaw/openclaw:latest

# 5. Reload and start pod
systemctl --user daemon-reload
systemctl --user start agent-stack.pod

# 6. Verify both services
systemctl --user status hermes-agent.service
systemctl --user status openclaw-gateway.service
curl -s http://127.0.0.1:8642/health
curl -s http://127.0.0.1:18789/healthz
```

## Related

- [[hermes-agent]] — Core agent runtime
- [[openclaw]] — Competing agent gateway
- [[podman]] — Rootless container runtime
- [[mission-control]] — Dashboard that can connect to both gateways
- [[assets/deployment/hermes-agent-quadlet.md]] — Hermes Quadlet reference
- [[assets/deployment/openclaw-quadlet.md]] — OpenClaw Quadlet reference
- [[hermes-workspace]] — Hermes UI control plane
