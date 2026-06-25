---
name: n8n-acp-implementation
description: "n8n — no ACP implementation found"
source: sources/n8n/
tags: [acp, integration, n8n, workflow-automation]
---

# n8n — ACP Implementation

**Conclusion: n8n does not implement the Agent Client Protocol (ACP).**

n8n is a workflow automation platform with a Node.js backend and TypeScript/Vue frontend. It does not implement agent-to-agent communication via ACP. Its AI features (Instance AI) use the internal REST API and MCP for external tool connectivity.

## Related ACP-Adjacent Features

- **Instance AI MCP client** — connects external MCP servers (`@n8n/instance-ai mcp/`) but this is MCP, not ACP
- **Public REST API** — programmatic access via `/api/v1` OpenAPI endpoints (see [[n8n-api]])
- **Webhook system** — external triggers via HTTP webhooks

For ACP, consider using a dedicated ACP server (e.g., Hermes, OpenClaw) that can bridge between ACP clients and n8n workflows.

## Related

- [[n8n-mcp]] — MCP integration (the relevant protocol for n8n's AI features)
- [[n8n-api]] — REST API reference
- [[n8n-architecture]] — System architecture
