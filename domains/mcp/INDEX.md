---
name: mcp-domain
description: "MCP (Model Context Protocol) implementation analysis across all repos in the vault"
tags: [mcp, index, catalog]
---

# MCP Domain Docs

Analysis of MCP (Model Context Protocol) implementations across repositories. Each doc covers protocol transport, tool/resource/prompt definitions, authentication, and architectural patterns.

## By Repository

| Doc | Repo | Description |
|-----|------|-------------|
| [[agentfield-mcp-implementation\|AgentField MCP]] | agentfield | Historical MCP support, removal, and remaining artifacts |
| [[alphaclaw-mcp-implementation\|AlphaClaw MCP]] | alphaclaw | MCP configuration manager — writes mcp.servers blocks |
| [[buildah-mcp-implementation\|Buildah MCP]] | buildah | No MCP found; gRPC RPC server only |
| [[free-claude-code-mcp-implementation\|Free Claude Code MCP]] | free-claude-code | MCP server tools, resources, and config |
| [[goclaw-mcp-implementation\|GoClaw MCP]] | goclaw | BridgeTool-based MCP client/server with OAuth |
| [[hermes-mcp-implementation\|Hermes MCP]] | hermes-agent | MCP client consuming tools + MCP server exposing capabilities |
| [[hermes-workspace-mcp-hub\|Hermes Workspace MCP Hub]] | hermes-workspace | Centralized MCP server management for workspace agents |
| [[llmtrim-mcp-implementation\|LLMTrim MCP]] | llmtrim | MCP proxy with request compression and SSE streaming |
| [[mission-control-mcp-implementation\|Mission Control MCP]] | mission-control | 49-tool MCP hub server across system, dev, and service management |
| [[n8n-mcp\|n8n-MCP]] | n8n | 4 MCP surfaces: MCP apps, browser, Instance AI client, native server |
| [[nanobot-mcp-implementation\|Nanobot MCP]] | nanobot | Tool registration, resource model, and agent capability exposure |
| [[openclaw-mcp-implementation\|OpenClaw MCP]] | openclaw | 3 stdio MCP servers: channel bridge, plugin tools, built-in tools |
| [[podlet-mcp-implementation\|Podlet MCP]] | podlet | No MCP found (Rust CLI tool, no server) |
| [[podman-mcp-implementation\|Podman MCP]] | podman | Analysis of Podman's REST API (not MCP protocol) |
| [[sablier-mcp-implementation\|Sablier MCP]] | sablier | No MCP found (Gin REST API, no MCP) |
| [[tank-os-mcp-implementation\|Tank OS MCP]] | tank-os | Deploys service-gator MCP sidecar via Quadlet |

## Key Patterns

- **stdio transport** is the most common, with HTTP/SSE as an alternative
- Most servers expose `tools/*` capabilities; few implement resources or prompts
- Auth varies: `x-api-key`, Bearer JWT, Cookie, or none for local tools
- Several repos have NO MCP implementation despite being AI-focused tools
