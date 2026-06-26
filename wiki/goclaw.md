---
name: goclaw
tags: [ai-llm, cli, container, gateway, golang, mcp, acp, orchestration, plugin-sdk, quadlet, security, systemd, webhook, wiki]
description: "GoClaw — Go-based AI agent gateway with MCP, ACP, and REST API"
source: sources/goclaw/
---

# GoClaw — Go-based AI Agent Gateway

| Field | Value |
|---|---|
| **Origin** | [nextlevelbuilder/goclaw](https://github.com/nextlevelbuilder/goclaw) |
| **License** | Unknown |
| **Stack** | Go (net/http.ServeMux), Quadlet systemd units |
| **Container** | `ghcr.io/nextlevelbuilder/goclaw:latest` |
| **Port** | 18789 |
| **Source** | `sources/goclaw/` |

## What it is

GoClaw is a **Go-based AI agent gateway** — a lightweight alternative to [[openclaw]] and [[hermes-agent]] built in Go. It provides agent lifecycle management, tool execution, MCP client/server surfaces, and ACP-based external agent orchestration via JSON-RPC over stdin/stdout.

## Features

- **REST API** — Comprehensive `net/http.ServeMux`-based API with handler registration in `internal/http/`
- **MCP Client/Server** — Connect to external MCP servers (client) or expose GoClaw's own tools as an MCP server (bridge)
- **ACP (Agent Communication Protocol)** — Orchestrate external AI agents (Gemini, Claude CLI) as subprocesses via JSON-RPC
- **Health Checks** — Configurable `/healthz` endpoint with health check support
- **Auto-Updates** — Quadlet `AutoUpdate=registry` for automatic container updates
- **Agent CRUD** — Agent creation, workspace management, prompts, export/import
- **Skills System** — Skills CRUD, evolution, versioning, upload/download
- **Run Traces** — Timeline-based run traces and session data
- **Quadlet Deployment** — Systemd Quadlet unit for rootless Podman deployment

## Architecture

GoClaw's internal architecture follows a modular handler pattern:

```
cmd/
├── gateway_http_handlers.go   — HTTP handler wiring
├── gateway_http_wiring.go     — Dependency injection
internal/
├── http/                      — HTTP handler implementations
├── mcp/                       — MCP client + bridge server
├── mcp/bridge_server.go       — MCP tools bridge
├── providers/acp/             — ACP agent orchestration
├── providers/acp_provider.go  — ACP provider bridge
└── tools/                     — Tool registry
```

## Domain Documentation

- [Architecture](domains/architecture/goclaw-architecture.md) — Go module structure, HTTP handler wiring, dependency injection
- [API](domains/api/goclaw-api.md) — REST API reference: agents, skills, traces, webhooks
- [MCP Implementation](domains/mcp/goclaw-mcp-implementation.md) — MCP client (connect to external servers) + MCP server (expose GoClaw tools)
- [ACP Implementation](domains/acp/goclaw-acp-implementation.md) — JSON-RPC external agent orchestration as subprocesses
- [Deployment](domains/deployment/goclaw-deployment.md) — Quadlet rootless Podman, auto-updates, health checks

## Related

- [[openclaw]] — TypeScript-based agent gateway (similar category, different implementation language)
- [[hermes-agent]] — Python-based agent gateway (similar category)
- [[alphaclaw]] — Setup UI and gateway manager for OpenClaw
- [[tank-os]] — Fedora bootc deployment for OpenClaw
- [[clawpier]] — Desktop GUI for managing OpenClaw/Hermes Docker containers
