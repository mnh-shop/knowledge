---
name: api-domain
description: "REST and HTTP API reference docs for repositories in the vault"
tags: [api, index, catalog]
---

# API Domain Docs

REST API references and HTTP endpoint documentation for repositories in the vault. Each doc covers endpoint paths, request/response shapes, authentication, and usage patterns.

## By Repository

| Doc | Repo | Description |
|-----|------|-------------|
| [[agentfield-api\|AgentField API]] | agentfield | REST and gRPC endpoints for sandbox management and pipeline orchestration |
| [[alphaclaw-api\|AlphaClaw API]] | alphaclaw | Gateway management, agent config, MCP and channel setup |
| [[free-claude-code-api\|Free Claude Code API]] | free-claude-code | REST API endpoints and usage |
| [[goclaw-api\|GoClaw API]] | goclaw | Agent/tool management, webhook provisioning, SSE streaming |
| [[gogs-api\|Gogs API]] | gogs | Self-hosted Git service API |
| [[hermes-agent-api\|Hermes Agent API]] | hermes-agent | OpenAI-compatible Chat/Responses, Runs, Sessions, Jobs, skills/toolsets |
| [[hermes-gateway-api\|Hermes Gateway API]] | hermes-agent | Multi-platform messaging layer with 20+ platform adapters |
| [[hermes-workspace-api\|Hermes Workspace API]] | hermes-workspace | Web/desktop command center API |
| [[llmtrim-api\|LLMTrim API]] | llmtrim | stdin/pipe, MCP proxy, and SSE-based streaming callback |
| [[mission-control-api\|Mission Control API]] | mission-control | System management API |
| [[n8n-api\|n8n API]] | n8n | Workflow automation API architecture |
| [[nanobot-api\|Nanobot API]] | nanobot | OpenAI-compatible chat completions, sessions, tool execution |
| [[openclaw-api\|OpenClaw API]] | openclaw | WebSocket RPC + OpenAI-compatible HTTP endpoints + MCP/ACP surfaces |
| [[podlet-api\|Podlet API]] | podlet | CLI-only tool — no REST API |
| [[podman-api\|Podman API]] | podman | Docker-compatible REST API + native libpod endpoints |
| [[sablier-api\|Sablier API]] | sablier | Gin-based REST API for dynamic container scaling |
| [[tank-os-api\|Tank OS API]] | tank-os | No REST API (bootc container OS, CLI-only) |

## API Patterns

- Most repos use REST over HTTP, with a trend toward OpenAI-compatible endpoints
- Common auth: `x-api-key` header or Bearer JWT
- Several expose SSE streaming for real-time events
- gRPC appears in agentfield alongside REST
