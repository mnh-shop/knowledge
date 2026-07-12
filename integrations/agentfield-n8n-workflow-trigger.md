---
name: agentfield-n8n-workflow-trigger
type: integration
tags: [agentfield, n8n, integration, workflow-automation, webhook, mcp, bridge]
description: "AgentField triggering n8n workflows via webhook, n8n reporting results back to AgentField via API, MCP bridge pattern"
---

# Integration: AgentField ↔ n8n Workflow Trigger

**Sources**: `sources/agentfield/`, `sources/n8n/`

## Overview

AgentField triggers n8n workflows via webhook and n8n reports results back through AgentField's REST API. This is a bidirectional MCP bridge pattern: AgentField reasoners invoke n8n workflows as callable tools, and n8n workflows push results or request agent intervention through AgentField's event bus. Both run as Podman containers on a shared network.

## Architecture

```
AgentField (:8080)                        n8n (:5678)
     │                                         │
     ├─ skill("n8n_trigger") ──► POST /webhook │
     │  MCP client call           execute      │
     │                              workflow   │
     │  ◄── HTTP callback ── n8n response     │
     │       POST /api/events                  │
```

**AgentField → n8n**: Reasoners call `n8n_trigger` as a skill — sends POST to n8n webhook URL. Workflow executes and returns the result synchronously or via callback.

**n8n → AgentField**: Workflows use AgentField's `POST /api/events` to push results. AgentField's event bus routes them back to the originating reasoner.

## Configuration

**AgentField MCP skill** registering n8n webhook:
```python
@app.skill("n8n_trigger")
def trigger_workflow(workflow_id: str, payload: dict) -> dict:
    return agentfield_mcp_client.call("webhook_send", {
        "url": f"http://n8n:5678/webhook/{workflow_id}",
        "method": "POST", "body": payload,
    })
```

**n8n Webhook node** with POST method, path `webhook/<id>`, Response Mode set to Last Node. Add an HTTP Request node pointing to `POST http://agentfield:8080/api/events` for callback push.

**Deployment**:
```bash
podman network create af-n8n --subnet 10.92.0.0/24
podman run -d --name n8n --network af-n8n -p 5678:5678 docker.n8n.io/n8nio/n8n:latest
podman run -d --name agentfield --network af-n8n -p 8080:8080 ghcr.io/agent-field/agentfield:latest
```

## Related

- [[agentfield]] — AI control plane: reasoners, skills, DID identity, durable execution
- [[n8n]] — Workflow automation platform with webhook triggers
- [[af-deep-research]] — AgentField deep research skill (example n8n workflow consumer)
- [[n8n-mcp]] — Standalone MCP server for n8n node documentation and workflow CRUD
- [[domains/mcp/agentfield-mcp-implementation.md]] — AgentField's MCP surface details
- [[integrations/openclaw-n8n-gateway.md]] — Equivalent OpenClaw + n8n pattern
