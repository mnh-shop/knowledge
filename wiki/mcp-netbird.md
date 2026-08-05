---
name: mcp-netbird
tags: [mcp, netbird, vpn, wireguard, golang, infrastructure, network, api, wiki, mcp-netbird]
description: "MCP server for managing NetBird VPN infrastructure — 50+ tools for CRUD on all NetBird resources via the Model Context Protocol"
source: sources/mcp-netbird/
verification_date: 2026-07-30
verified_by: codegraph-verify
---

# MCP NetBird

| Field | Value |
|---|---|
| **Origin** | [XNet-NGO/mcp-netbird](https://github.com/XNet-NGO/mcp-netbird) |
| **Maintainer** | XNet Inc. (lead developer Joshua S. Doucette), derived from the [MCP Server for Grafana](https://github.com/grafana/mcp-grafana) by Grafana Labs |
| **License** | Apache-2.0 |
| **Stack** | Go 1.24, mark3labs/mcp-go v0.18.0 |
| **Deployment** | Docker (recommended), standalone binary, Docker MCP Gateway |
| **Source** | `sources/mcp-netbird/` |

## What is it?

An MCP (Model Context Protocol) server that exposes the NetBird Management API through 50+ MCP tools, enabling AI coding agents to manage VPN infrastructure — peers, groups, routes, DNS settings, policies, and users — directly from natural language conversations.

Built with the mark3labs/mcp-go SDK (a popular third-party Go MCP SDK), it wraps every NetBird Management API endpoint as a typed MCP tool with JSON Schema input validation, making NetBird administration accessible to any MCP-compatible AI agent (Claude Code, Codex CLI, Cursor, etc.).

## Key Features

- **50+ MCP Tools:** Full CRUD coverage for all NetBird resources: peers, groups, routes, DNS nameservers, access policies, service users, PATs, setup keys, and more.
- **13 Tool Categories:** Tools are registered across 13 category functions in `newServer()`: Peer, Group, Policy, Network, Network Resource, Network Router, Posture Check, Port Allocation, Nameserver, Route, Setup Key, User, and Account tools.
- **Policy Helper Tools:** Dedicated helpers for policy workflows — `list_policies_by_group` (find all policies referencing a group), `replace_group_in_policies` (bulk replace groups across policies), and `get_policy_template` (example policy structures with documentation).
- **NetBird Management API Coverage:** Every major endpoint of the NetBird Management API is available as a tool with proper input schemas.
- **mark3labs/mcp-go SDK:** Built with mark3labs/mcp-go v0.18.0 for standards-compliant tool exposure.
- **Multiple Deployments:** Run as a standalone binary, Docker container, or via Docker MCP Gateway for sidecar integration.
- **AI-Native Infrastructure Management:** Enables natural-language VPN management — "create a new setup key for the dev group" or "list all peers in the staging network."

## Tech Stack

| Component | Technology |
|---|---|
| **Language** | Go 1.24 |
| **MCP SDK** | mark3labs/mcp-go v0.18.0 (third-party) |
| **Target API** | NetBird Management API (REST) |
| **Container** | Docker — plain two-stage Dockerfile (`golang:1.24-bullseye` builder → `debian:bullseye-slim`, non-root user); **not** multi-arch |

## Configuration

Configuration is resolved with the priority **CLI flags > HTTP headers (SSE mode) > environment variables**.

| Source | Keys |
|---|---|
| **Environment** | `NETBIRD_API_TOKEN`, `NETBIRD_API_HOST` |
| **CLI flags** | `--api-token`, `--api-host`, `--transport` (`stdio`/`sse`), `--sse-address` (default `localhost:8001`) |
| **HTTP headers** | Token/host supplied per-request via SSE headers |

## Deployment

### Docker (Recommended)

The image is published on Docker Hub as `xnetadmin/mcp-netbird:latest`:

```bash
docker run -e NETBIRD_API_TOKEN=your_token_here \
  -e NETBIRD_API_HOST=api.netbird.io \
  xnetadmin/mcp-netbird:latest
```

### Standalone Binary

```bash
./mcp-netbird \
  --api-token your-api-token \
  --api-host api.netbird.io
```

Pre-built binaries for Linux, macOS (x86_64/arm64), and Windows are available from the [releases page](https://github.com/XNet-NGO/mcp-netbird/releases).

### Docker MCP Gateway

The server can be configured as a tool provider via Docker MCP Gateway for integration with MCP hosts.

## Related

- [[netbird]] — The NetBird VPN platform this MCP server manages
- [[goclaw]] — Enterprise agent gateway that consumes MCP tools like this server
- [[hermes-agent]] — MCP client capable of consuming mcp-netbird tools
- [[mission-control]] — MCP audit and management server
