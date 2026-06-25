---
name: agentfield-mcp-server
tags: [agentfield, mcp, bridge, server]
description: MCP server reference for wrapping AgentField REST API as an MCP bridge server for Claude Code
---

# AgentField MCP Server
**Source:** `sources/agentfield/`

**Type:** MCP server asset (AgentField REST API wrapper)  
**Status:** Reference implementation guide  
**Rationale:** AgentField's native MCP integration was removed from the codebase. This document describes how to add AgentField MCP capabilities to Claude Code via a bridge server.

---

## Context

AgentField had a full MCP implementation that was removed in PR #359. The only remaining MCP artifact is the `application/mcp-server+json` type in the ARD (Agent Resource Discovery) catalog. To reconnect MCP to AgentField, the recommended approach is a **bridge MCP server** that wraps the AgentField REST API.

---

## Architecture

```
Claude Code
    |
    | MCP protocol
    v
AgentField MCP Server (this bridge)
    |
    | HTTP REST
    v
AgentField Control Plane (:8080)
    |
    | POST /api/v1/execute/:target
    v
Agent Nodes (Python/Go/TS)
```

The MCP server translates MCP tool calls into AgentField REST API calls. It runs as a local process that Claude Code spawns via its MCP configuration.

---

## Implementation (Python, ~150 lines)

### Requirements

- Python 3.10+
- `httpx` or `aiohttp` for async HTTP to AgentField
- `mcp` (FastMCP) for MCP server

### Basic Implementation

```python
"""
AgentField MCP Bridge Server

Exposes AgentField reasoners/skills as MCP tools for Claude Code.
"""
import os
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("agentfield")

AGENTFIELD_URL = os.environ.get("AGENTFIELD_URL", "http://localhost:8080")
AGENTFIELD_API_KEY = os.environ.get("AGENTFIELD_API_KEY", "")
HEADERS = {"X-API-Key": AGENTFIELD_API_KEY} if AGENTFIELD_API_KEY else {}


@mcp.tool()
async def agentfield_execute(
    target: str,
    input_data: dict,
    mode: str = "sync"
) -> dict:
    """Execute an AgentField reasoner or skill.

    Args:
        target: Format 'agent_id.reasoner_name' (e.g. 'my-agent.analyze')
        input_data: JSON input to pass to the reasoner
        mode: 'sync' for blocking execution, 'async' for fire-and-forget
    """
    async with httpx.AsyncClient() as client:
        if mode == "async":
            resp = await client.post(
                f"{AGENTFIELD_URL}/api/v1/execute/async/{target}",
                json={"input": input_data},
                headers=HEADERS,
                timeout=30
            )
        else:
            resp = await client.post(
                f"{AGENTFIELD_URL}/api/v1/execute/{target}",
                json={"input": input_data},
                headers=HEADERS,
                timeout=180
            )
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
async def agentfield_execution_status(execution_id: str) -> dict:
    """Get the status of an AgentField execution.

    Args:
        execution_id: The UUID returned by async execution
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{AGENTFIELD_URL}/api/v1/executions/{execution_id}",
            headers=HEADERS,
        )
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
async def agentfield_discover(tag: str = "", name: str = "") -> list:
    """Discover available agents and their capabilities.

    Args:
        tag: Optional tag filter
        name: Optional name filter
    """
    params = {}
    if tag:
        params["tag"] = tag
    if name:
        params["name"] = name
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{AGENTFIELD_URL}/api/v1/discovery/capabilities",
            params=params,
            headers=HEADERS,
        )
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
async def agentfield_memory(
    scope: str,
    key: str = "",
    query: str = "",
    agent_id: str = ""
) -> dict:
    """Read from AgentField's cross-agent memory.

    Args:
        scope: Memory scope - 'global', 'session', 'actor', or 'workflow'
        key: Specific key to read (optional)
        query: Vector search query string (optional, alternative to key)
        agent_id: Agent ID for actor-scoped queries (optional)
    """
    async with httpx.AsyncClient() as client:
        params = {"scope": scope}
        if key:
            params["key"] = key
        if query:
            params["query"] = query
        if agent_id:
            params["agent_id"] = agent_id
        resp = await client.get(
            f"{AGENTFIELD_URL}/api/v1/memory",
            params=params,
            headers=HEADERS,
        )
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
async def agentfield_list_agents() -> list:
    """List all registered agents on the AgentField control plane."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{AGENTFIELD_URL}/api/v1/nodes",
            headers=HEADERS,
        )
        resp.raise_for_status()
        return resp.json()


@mcp.resource("agentfield://agents")
async def get_agents_resource() -> str:
    """MCP resource listing all agents and their capabilities as text."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{AGENTFIELD_URL}/api/v1/discovery/capabilities",
            headers=HEADERS,
        )
        resp.raise_for_status()
        agents = resp.json()
        lines = []
        for agent in agents:
            lines.append(f"Agent: {agent.get('name', 'unknown')}")
            lines.append(f"  ID: {agent.get('node_id', 'unknown')}")
            lines.append(f"  Health: {agent.get('health', 'unknown')}")
            for reasoner in agent.get("reasoners", []):
                lines.append(f"  Reasoner: {reasoner.get('id')} -> {reasoner.get('description', '')}")
        return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
```

---

## Claude Code Configuration

Add to your Claude Code MCP configuration (`~/.claude/settings.json` or project `.claude/settings.local.json`):

```json
{
  "mcpServers": {
    "agentfield": {
      "command": "python",
      "args": ["/path/to/agentfield_mcp_server.py"],
      "env": {
        "AGENTFIELD_URL": "http://localhost:8080",
        "AGENTFIELD_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Multi-Server Configuration (with other MCP servers)

```json
{
  "mcpServers": {
    "agentfield": {
      "command": "python",
      "args": ["/path/to/agentfield_mcp_server.py"],
      "env": {
        "AGENTFIELD_URL": "http://localhost:8080"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"]
    }
  }
}
```

---

## Alternative: MCP Adapter Agent

Instead of a standalone MCP bridge, you can write an **AgentField agent** that acts as an MCP adapter:

```python
import agentfield
from mcp.client import MCPClient  # hypothetical

app = agentfield.Agent("mcp-adapter")

# Connect to an MCP server
client = MCPClient("http://some-mcp-server:8080")
tools = client.list_tools()

# Auto-expose each MCP tool as an AgentField skill
for tool in tools:
    @app.skill(name=tool.name)
    async def handler(input: dict):
        return await client.call_tool(tool.name, input)
```

This pattern lets AgentField's `tools="discover"` in `app.ai()` make MCP tools available to LLM calls routed through the control plane.

---

## ARD-Based MCP Discovery

AgentField's ARD (Agent Resource Discovery) system preserves `application/mcp-server+json` as an `ArtifactType` in the catalog. This means MCP servers can be registered and discovered as external ARD resources even though AgentField no longer has a first-party MCP client:

```json
{
  "artifact_type": "application/mcp-server+json",
  "name": "my-mcp-server",
  "url": "http://mcp-server:8080",
  "description": "Custom MCP tools for data processing"
}
```

The ARD external invocation system can forward requests to these registered MCP endpoints via the `ExploreRegistry` and `SearchRegistry` APIs.

## Advanced MCP Integration Patterns

### Running the Bridge as a Systemd Service

For production use, run the MCP bridge as a managed service:

```ini
[Unit]
Description=AgentField MCP Bridge
After=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/agentfield-mcp/agentfield_mcp_server.py
Restart=on-failure
RestartSec=5
Environment=AGENTFIELD_URL=http://localhost:8080
Environment=AGENTFIELD_API_KEY=your-api-key

[Install]
WantedBy=default.target
```

### Hermes Integration via MCP

Add the AgentField MCP bridge to Hermes's MCP configuration:

```json
{
  "mcpServers": {
    "agentfield": {
      "command": "python",
      "args": ["/opt/agentfield-mcp/agentfield_mcp_server.py"],
      "env": {
        "AGENTFIELD_URL": "http://agentfield:8080"
      }
    }
  }
}
```

This lets Hermes agents call any AgentField reasoner as an MCP tool. The MCP bridge translates Hermes tool requests into AgentField REST API calls with full tracing through the control plane.

### OpenClaw Integration via MCP

For OpenClaw users, the MCP bridge can run alongside OpenClaw's gateway:

```json
{
  "mcpServers": {
    "agentfield": {
      "command": "python",
      "args": ["/opt/agentfield-mcp/agentfield_mcp_server.py"],
      "env": {
        "AGENTFIELD_URL": "http://agentfield.openclaw.svc:8080"
      }
    }
  }
}
```

OpenClaw's rate limiting, circuit breaking, and API key authentication become an additional layer on top of AgentField's DID identity system.

### Securing the MCP Bridge

- Use environment variables for credentials (never hardcode)
- Run the bridge on localhost only in development (`--host 127.0.0.1`)
- Use TLS in production
- The bridge should use AgentField API key auth; the MCP protocol itself handles transport

## Cross-Reference

- [AgentField Architecture](../../domains/architecture/agentfield-architecture.md)
- [AgentField API](../../domains/api/agentfield-api.md) -- REST endpoints, execution flow, integration patterns
- [AgentField Deployment](../../domains/deployment/agentfield-deployment.md) -- local, Docker Compose, Quadlet
- [AgentField Quadlet](../deployment/agentfield-quadlet.md) -- Quadlet-specific deployment

## Related

- [[agentfield]] -- wiki page for the platform
- [[agentfield-architecture]] -- system architecture
- [[agentfield-api]] -- REST API reference
- [[agentfield-deployment]] -- deployment guide
- [[agentfield-quadlet]] -- Quadlet deployment
- [[agentfield-profile]] -- AgentField platform profile
