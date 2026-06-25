---
name: mcp
description: "Model Context Protocol — the universal protocol for LLM tool integration"
tags: [mcp, protocol, ai-llm, integration]
---

# Model Context Protocol (MCP)

**MCP** (Model Context Protocol) is an open protocol developed by Anthropic that standardizes how LLM applications connect to external tools, data sources, and services. It provides a universal interface layer — analogous to USB for AI — allowing any MCP-compatible client (Claude Code, Cursor, VS Code, etc.) to use any MCP server's tools.

## In This Vault

This vault documents MCP implementations across multiple repositories. See the `domains/mcp/` directory for the full catalog of MCP implementation analysis docs, including:

- [[mission-control]] — 49-tool MCP hub server
- [[hermes-agent]] — Hermes agent MCP client/server
- [[n8n-mcp]] — 1,845+ nodes indexed as MCP tools
- `goclaw` — BridgeTool-based MCP implementation (see `domains/mcp/goclaw-mcp-implementation.md`)
- [[podman]] — Container management MCP tools
- [[nanobot]], [[agentfield]], [[llmtrim]], [[openclaw]] and more
