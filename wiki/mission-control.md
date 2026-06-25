---
name: mission-control
tags: [mission-control, dashboard, orchestration, wiki]
description: Mission Control — AI Agent Orchestration Dashboard
---

# Mission Control — AI Agent Orchestration Dashboard

| Field | Value |
|---|---|
| **Origin** | [builderz-labs/mission-control](https://github.com/builderz-labs/mission-control) |
| **License** | MIT |
| **Stack** | Next.js 16, React 19, TypeScript 5, SQLite (better-sqlite3), Tailwind CSS 3, Zustand 5 |
| **Source** | `sources/mission-control/` |
| **Wanted** | Self-hosted dashboard for managing AI agent fleets, dispatching tasks, tracking costs, orchestration |

## What it is

Mission Control is an **open-source dashboard for AI agent orchestration** — manage agent fleets, dispatch tasks, track costs, and coordinate multi-agent workflows. Zero external dependencies (SQLite only), single `pnpm start` to run.

**Key positioning:** It is gateway-agnostic. It connects to OpenClaw, CrewAI, LangGraph, AutoGen, and Claude SDK via framework adapters. It is NOT tied to any single agent platform — it sits above the agent layer as a management/observability plane.

## Features

32 panels including: Tasks, Agents, Skills, Logs, Tokens, Memory, Security, Cron, Alerts, Webhooks, Pipelines. Real-time via WebSocket + SSE push updates with smart polling. Role-based access (viewer, operator, admin). Built-in Aegis review system. Skills Hub for browsing ClawdHub and skills.sh registries. Claude Code bridge for read-only team integration.

### Agent Eval & Security

- Four-layer evaluation framework
- Trust scoring
- Secret detection
- MCP call auditing
- Hook profiles (minimal / standard / strict)

## Architecture

```
Frame (Next.js 16 SPA shell)
├── Panels (32 panels, lazy-loaded)
│   ├── Agent Management (agent list, cap control, kill, command)
│   ├── Task Management (queue, dispatch, templates, rich markdown)
│   ├── Memory (agent memory, soul config, comments, tokens)
│   ├── Skills (browse, install, security-scan)
│   ├── Security (eval, scoring, secrets, MCP audit)
│   ├── Monitoring (logs, events, cron, alerts)
│   └── Admin (users, settings, gateways, webhooks, pipelines)
├── State (Zustand 5 stores)
├── Database (SQLite via better-sqlite3, WAL mode)
└── Real-time (WebSocket + SSE push)
```

## Interfaces

### MCP Server (recommended for Claude Code agents)

```bash
claude mcp add mission-control -- node /path/to/mission-control/scripts/mc-mcp-server.cjs
```

35 tools: agents, tasks, sessions, memory, soul, comments, tokens, skills, cron, status

### CLI

```bash
pnpm mc agents list --json
pnpm mc tasks queue --agent Aegis --max-capacity 2 --json
pnpm mc events watch --types agent,task
```

### REST API

101 endpoints documented in `openapi.json`. Interactive docs at `/docs` when running.

## Deployment

### One-Command Install
```bash
bash install.sh --local     # or: bash install.sh --docker
```

### Docker
```bash
docker compose up
docker pull ghcr.io/builderz-labs/mission-control:latest
```

### Manual
```bash
pnpm install && pnpm dev    # http://localhost:3000/setup
pnpm start                  # production
node .next/standalone/server.js  # standalone mode
```

### Docker compose production hardening
```bash
docker compose -f docker-compose.yml -f docker-compose.hardened.yml up -d
```

### Requirements
- Node.js >= 22
- pnpm
- SQLite only — no Redis, no PostgreSQL, no Docker required (optional)
- MISSION_CONTROL_DATA_DIR env var for custom data location (defaults to `.data/`)

## Compatibility with Core Systems

| System | Can it work with Mission Control? | How |
|---|---|---|
| [[hermes-agent]] | ✅ | Hermes gateway can be registered via multi-gateway framework adapters |
| [[openclaw]] | ✅ | OpenClaw gateway supported out of the box via framework adapter |
| [[agentfield]] | ✅ Generic REST is sufficient | Not a named adapter, but AgentField exposes `/api/v1/nodes`, `/api/v1/executions`, `/api/v1/workflows` endpoints consumable via generic REST. Mission Control panels can connect. MCP bridge at `assets/mcp-servers/agentfield-mcp-server.md` adds MCP tool access |
| [[n8n]] | ✅ | Webhook panel can trigger/receive n8n workflows; n8n REST API compatible |

Mission Control is **most useful when paired with at least one agent gateway** — it provides the dashboard/management plane that Hermes, OpenClaw, and others lack natively.

## Domain docs & assets

- [Architecture: mission-control](domains/architecture/mission-control-architecture.md)
- [API: mission-control](domains/api/mission-control-api.md) — 101 REST endpoints, 35 MCP tools
- [Deployment: mission-control](domains/deployment/mission-control-deployment.md)
- [Quadlet: mission-control](assets/deployment/mission-control-quadlet.md)
- [MCP Server: mission-control](assets/mcp-servers/mission-control-mcp-server.md)
- [Agent Profile: mission-control](assets/agent-profiles/mission-control-profile.md)

## Related

- [[openclaw]] — Supported gateway (out of box)
- [[hermes-agent]] — Supported gateway (via framework adapter)
- [[agentfield]] — Generic REST integration for management plane
- [[stack-landscape]] — Where this fits in the overall deployment stack
- [[mission-control-architecture]] — Detailed system architecture
- [[mission-control-api]] — REST API, MCP tools, and CLI reference
- [[mission-control-deployment]] — Deployment methods and configuration
- [[mission-control-mcp-server]] — MCP server setup and tools
- [[mission-control-quadlet]] — Quadlet container deployment
- [[mission-control-profile]] — Quick reference profile

## Cross-project

- [[n8n]] -- Workflow engine with webhook panel integration
- [[podman]] -- Container runtime for Mission Control deployment
- [[clawpier]] -- Alternative desktop GUI for agent management
- [[gogs]] -- Self-hosted Git service for pipeline integration
- [[nix-podman-stacks]] -- Declarative container deployment
- [[sablier]] -- Scale-to-zero for Mission Control services
