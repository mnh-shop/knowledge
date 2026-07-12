---
name: appstore
tags: [appstore, mcp, developer-tools, marketplace, agent-tools]
description: "MCP server marketplace and discovery platform for AI agent tools"
source: sources/appstore/
---

# AppStore

| Field | Value |
|---|---|
| **Origin** | [nicholasgriffintn/mcp-marketplace](https://github.com/nicholasgriffintn/mcp-marketplace) |
| **Source** | `sources/appstore/` |
| **Repomix** | `raw/appstore/appstore.xml` |
| **Codegraph** | `graphs/appstore/` |

## Overview

AppStore is an MCP server marketplace and discovery platform that catalogs available MCP servers for AI agents. It provides a browsable registry where agents and their operators can find, evaluate, and connect to MCP-compatible tools and services, reducing the friction of discovering new capabilities.

## Key Features

- **MCP Server Registry** — Catalog of available MCP servers with descriptions, capabilities, and configuration details
- **Search & Discovery** — Search and filter interface for finding MCP servers by category, protocol, or capability
- **Agent Integration** — Simplified workflow for connecting discovered MCP servers to agent runtimes
- **Metadata Curation** — Structured metadata for each MCP server (tools, resources, authentication requirements)
- **Community Contributions** — Mechanism for publishing and updating MCP server listings

## Architecture

The platform aggregates MCP server metadata from community submissions and automated discovery, presenting it through a web interface and optionally through an API that agent runtimes can query programmatically.

## Related

- [[hermes-agent]] — MCP client that can consume servers from the marketplace
- [[openclaw]] — MCP server surface that could be listed in the marketplace
- [[mcp]] — Model Context Protocol standard
- [[n8n-mcp]] — MCP servers for n8n workflow automation
