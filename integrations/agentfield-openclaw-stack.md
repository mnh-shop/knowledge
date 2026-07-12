---
name: agentfield-openclaw-stack
type: integration
tags: [agentfield, openclaw, integration, mcp, orchestration, bridge, container, quadlet]
description: "Integration: AgentField orchestrating OpenClaw agent gateways over MCP"
---

# Integration: AgentField ↔ OpenClaw Stack

**Sources**: `sources/agentfield/`, `sources/openclaw/`

## Overview

AgentField (the AI control plane) orchestrates one or more OpenClaw agent gateways through a shared MCP bridge. OpenClaw handles multi-channel user messaging (WhatsApp, Telegram, Discord, 30+ channels) while AgentField provides durable execution, DID-based identity, policy enforcement, and cross-agent routing. The MCP bridge connects the two control planes so AgentField can dispatch tasks to OpenClaw agents and OpenClaw can invoke AgentField reasoners.

This integration is not native to either project -- it is a **custom bridge layer** using the MCP surfaces both systems expose.

## Architecture

```
User Message → OpenClaw Gateway (channels/*)
                    │
                    ▼
            OpenClaw MCP Server (src/mcp/)
                    │ MCP protocol (stdio/SSE)
                    ▼
         AgentField MCP Client (control plane)
                    │
                    ▼
          AgentField Reasoner/Skill
                    │
                    ▼
         Response → OpenClaw → User
```

The bridge runs as a sidecar or embedded agent in AgentField: an `@app.reasoner("openclaw-bridge")` that wraps the OpenClaw MCP server as an AgentField tool surface. OpenClaw's MCP server (9 tools: conversation list/send, channel query) maps to AgentField skills.

### Cross-cutting concerns

- **Identity**: OpenClaw sessions are mapped to AgentField DID subjects. Each OpenClaw user channel becomes an AgentField-traceable execution context.
- **Execution durability**: AgentField's PostgreSQL-backed queue absorbs OpenClaw tasks when the control plane is busy -- no dropped messages.
- **Policy**: AgentField ACCESS/DENY rules gate which OpenClaw commands can invoke which reasoners.

## Quadlet Deployment

### AgentField Control Plane

```ini
# ~/.config/containers/systemd/agentfield.container
[Unit]
Description=AgentField control plane
After=network-online.target
Wants=network-online.target

[Container]
Image=ghcr.io/agent-field/agentfield:latest
ContainerName=agentfield
PullPolicy=newer
RunInit=true
Volume=agentfield-data:/data:Z
PublishPort=127.0.0.1:8080:8080
Environment=AF_DB_DSN="postgres://af:pass@localhost:5432/agentfield"
Environment=AF_LOG_LEVEL=info

[Service]
Restart=always

[Install]
WantedBy=default.target
```

### OpenClaw Gateway

```ini
# ~/.config/containers/systemd/openclaw.container
[Unit]
Description=OpenClaw agent gateway
After=network-online.target agentfield.service
BindsTo=agentfield.service

[Container]
Image=ghcr.io/openclaw/openclaw:latest
ContainerName=openclaw
PullPolicy=newer
RunInit=true
Volume=%h/.openclaw:/home/node/.openclaw:Z
PublishPort=127.0.0.1:18789:18789
Environment=OPENCLAW_MCP_BRIDGE=http://127.0.0.1:8080

[Service]
Restart=always

[Install]
WantedBy=default.target
```

## MCP Bridge Configuration

The bridge agent in AgentField registers as a skill:

```python
@app.skill("openclaw_send_message")
def send_message(channel: str, user: str, message: str):
    """Send a message through OpenClaw's MCP channel bridge."""
    return openclaw_mcp_client.call("send_message", {
        "channel": channel,
        "recipient": user,
        "text": message,
    })
```

Configuration mapping is stored in AgentField's memory store (`app.memory.set("openclaw/channel_map", ...)`) and reloaded on agent restart.

## Related

- [[agentfield]] -- AI control plane: reasoners, skills, DID identity, durable execution
- [[openclaw]] -- Personal AI assistant with 30+ messaging channels
- [[goclaw]] -- Go-based lightweight alternative; same MCP surface pattern
- [[mission-control]] -- Gateway-agnostic dashboard; can monitor both sides of the bridge
