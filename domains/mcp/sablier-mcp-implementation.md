---
name: sablier-mcp-implementation
description: "Sablier — no MCP implementation (REST API with Gin, no model context protocol)"
source: sources/sablier/
tags: [container, mcp, sablier, scaling]
---

# Sablier — MCP Implementation

**Conclusion: Sablier does not implement the Model Context Protocol (MCP).**

Sablier is a dynamic container scaling tool written in Go with a Gin-based REST API. It has no MCP server or client.

## What Sablier Provides Instead

- **Gin REST API** — health checks, session management, instance events (see [[sablier-api]])
- **Docker provider backend** — manages container lifecycle
- **Strategy system** — dynamic and blocking session strategies

For MCP-based integration, use an MCP wrapper server that consumes Sablier's REST API.

## Related

- [[sablier-api]] — REST API reference
- [[sablier-architecture]] — System architecture
- [[sablier-deployment]] — Deployment guide
