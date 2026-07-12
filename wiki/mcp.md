---
name: mcp
description: "Model Context Protocol — the universal protocol for LLM tool integration and cross-system interoperability"
source: domains/mcp/
tags: [integration, mcp, protocol, reference, anthropic]
---

# Model Context Protocol (MCP)

**MCP** (Model Context Protocol) is an open protocol developed by Anthropic that standardizes how LLM applications connect to external tools, data sources, and services. It provides a universal interface layer — analogous to USB for AI — allowing any MCP-compatible client (Claude Code, Cursor, VS Code, etc.) to use any MCP server's tools.

## What MCP Provides

MCP solves the fragmentation problem in AI tool integration. Before MCP, each LLM application required custom adapters for every tool or service. Now, any MCP server can expose its capabilities as long as it implements the JSON-RPC 2.0-based protocol over stdio or HTTP transport.

The protocol defines three core capability types:

- **Tools** — executable functions with input schemas (the most common)
- **Resources** — read-only data sources with URI templates
- **Prompts** — reusable prompt templates with argument injection

## Key Features

**Transport Flexibility**: MCP supports stdio (most common for local tools), HTTP, and Server-Sent Events (SSE) for remote deployments. Most servers in this vault use stdio transport with zero external dependencies.

**Standardized Discovery**: Clients can enumerate available tools via `tools/list` and understand their requirements through JSON Schema input validation, enabling dynamic tool binding without hardcoding.

**Zero-Config Integration**: Once registered (`claude mcp add <name> -- <command>`), MCP tools appear automatically in the client's tool registry — no code changes required.

**Framework Agnostic**: Any programming language can implement MCP servers. This vault catalogs implementations in Node.js, Go, Python, and TypeScript.

## Implementation Patterns in This Vault

The vault contains extensive MCP implementation analysis across multiple repositories. Key patterns observed:

| Pattern | Description | Examples |
|---------|-------------|----------|
| **stdio MCP servers** | Direct tool exposure via stdin/stdout | [[mission-control]], [[hermes-agent]], [[free-claude-code]] |
| **BridgeTool architecture** | Protocol adaptation layer | [[goclaw]], [[openclaw]] |
| **Proxy/Cache servers** | Tool compression and caching | [[llmtrim]], [[nanobot]] |
| **Hub servers** | Centralized multi-server management | [[hermes-workspace]], [[mission-control]] |

## Available MCP Servers in This Vault

- [[mission-control]] — 49 tools across agent, task, memory, and session management
- [[hermes-agent]] — Agent orchestration with MCP client/server duality
- [[goclaw]] — Go-based agent gateway with OAuth-authenticated MCP
- [[openclaw]] — Rust-based agent system with 3 stdio MCP servers
- [[n8n]] — Workflow automation with MCP surfaces for integration
- [[nanobot]] — Agent framework with tool registration and capability exposure
- [[podman]] — Container management (REST API, not MCP protocol)

## MCP Audit & Security

Mission Control implements a comprehensive MCP audit subsystem that logs every tool call with:

- Agent identity tracking and tool-level breakdowns
- Timing metrics with p50/p95/p99 latency distributions
- Ed25519-signed receipts for tamper-evident audit trails
- Injection detection for prompt injection, command injection, and data exfiltration
- Per-agent trust scores derived from MCP call patterns

Hook profiles (`minimal`/`standard`/`strict`) control security strictness and enable secret scanning, MCP auditing, and rate limiting. See [[mission-control]] for details.

## Getting Started with MCP

To add an MCP server to Claude Code:

```bash
# Add Mission Control MCP server
claude mcp add mission-control -- node /path/to/mission-control/scripts/mc-mcp-server.cjs

# Or add hermes-agent MCP
claude mcp add hermes -- node /path/to/hermes/scripts/hermes-mcp.cjs
```

Then restart Claude Code — tools will appear in the available tool list automatically.

## MCP Transport Details

**stdio**: Most common for local tool servers. Uses blocking stdin/stdout communication with JSON-RPC messages. Requires no network setup. Examples: Mission Control, Hermes, free-claude-code.

**HTTP**: For remote servers, accepts POST requests with JSON-RPC body. Requires base URL configuration and typically API key authentication.

**SSE (Server-Sent Events)**: Enables push-based notifications for long-running operations. Used by servers that need to stream progress updates.

## Protocol Methods

MCP servers must implement:

- `initialize` — handshake returning protocol version and capabilities
- `tools/list` — enumerate available tools with input schemas
- `tools/call` — execute a named tool with provided arguments
- `ping` — liveness check (optional but recommended)

Optional: `resources/*` and `prompts/*` for read-only data and template access.

## Related

- [[hermes-agent]] — MCP client/server for agent orchestration
- [[mission-control]] — MCP hub with 49 tools and audit capability
- [[goclaw]] — Go MCP implementation with OAuth support
- [[domains/mcp|index]] — Full catalog of MCP implementation analysis