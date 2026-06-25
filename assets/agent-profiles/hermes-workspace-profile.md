---
name: hermes-workspace-profile
tags: [hermes, profile, typescript, agent-gateway, messaging, multi-platform]
description: "Agent profile for Hermes Workspace: quick reference profile for the web/desktop command center for Hermes Agent"
---

# Hermes Workspace — Quick Reference Profile
**Source:** `sources/hermes-workspace/`

## Identity

Hermes-workspace is the web UI and API server for the Hermes agent ecosystem. It provides a browser-based interface for chatting with the Hermes agent, managing sessions, configuring providers, orchestrating swarm workers, browsing the MCP hub, managing files, and running terminals. It serves as the control plane bridging the user browser, the Hermes agent gateway, worker processes, and the file system.

## Stack

- **Framework**: TanStack Start (React + SSR)
- **Runtime**: Node.js 22+
- **Build**: Vite, pnpm
- **Auth**: Cookie-based sessions, 30-day TTL, timing-safe comparison
- **Streaming**: Server-Sent Events (SSE)

## Ports

| Port | Service | Protocol |
|------|---------|----------|
| 3000 | Workspace Web UI + API | HTTP |
| 8642 | Hermes Agent Gateway | HTTP |
| 9119 | Hermes Agent Dashboard | HTTP |
| 18789 | Hermes Agent Gateway | WebSocket |

## Communication Protocols

1. **Gateway WebSocket** (`ws://127.0.0.1:18789`) — JSON-RPC with Ed25519 device identity, circuit breaker pattern.
2. **Gateway HTTP API** (`http://127.0.0.1:8642`) — Capability probing, health checks, model listing.
3. **Dashboard HTTP API** (`http://127.0.0.1:9119`) — Sessions, skills, config, jobs, MCP, conductor, kanban.
4. **OpenAI-Compatible API** — `/v1/chat/completions` for portable backends.
5. **Direct Subprocess** — tmux sessions or child_process for swarm workers.

## Key Features

- **Chat UI**: Streaming SSE-based chat with session management
- **Swarm Orchestration**: 10-worker multi-agent system with tmux-based lifecycle
- **MCP Hub**: Unified catalog search across Smithery registry + local config
- **Terminal**: PTY-based web terminal via Python helper
- **File Browser**: File system access and artifact management
- **Config Management**: Read/write config.yaml, .env, auth profiles
- **Provider Management**: Multi-provider support (Anthropic, OpenAI, local)
- **Conductor**: Task management with Kanban board and mission lifecycle
- **Jobs/Cron**: Job scheduling and cron management
- **Update System**: Self-update for workspace and agent
- **Electron**: Desktop builds for macOS and Windows

## Auth Architecture

- Cookie: `claude-auth=<token>` — HttpOnly, Secure, SameSite=Strict, Path=/, Max-Age=2592000
- Store: `~/.hermes/workspace-sessions.json`
- Middleware: `isAuthenticated()` on all API routes except `/api/auth`, `/api/ping`
- CSRF: `requireJsonContentType()` on mutating POST requests
- Password required for non-loopback host access
- No password = local-only (loopback) mode

## Key Files

- `src/routes/api/` — All API route handlers
- `src/server/gateway.ts` — WebSocket gateway client
- `src/server/gateway-capabilities.ts` — HTTP gateway capability probing
- `src/server/mcp-hub/` — MCP catalog search aggregator
- `src/server/swarm-dispatch.ts` — Swarm worker dispatch
- `src/server/swarm-lifecycle.ts` — Worker lifecycle management
- `src/server/openai-compat-api.ts` — OpenAI-compatible API endpoints
- `~/.hermes/config.yaml` — Hermes agent configuration
- `~/.hermes/.env` — API keys and environment settings
- `~/.hermes/workspace-sessions.json` — Session token store
- `~/.hermes/workspace-overrides.json` — Runtime connection overrides

## Dependencies

- **hermes-agent** (required): Gateway + dashboard backend
- **hermes CLI** (required): For swarm worker spawning and oneshot execution
- **tmux** (required for swarm on Linux/macOS)
- **Python 3** (required for PTY terminal)
- **pnpm** (for building)

## Related

- [[hermes-workspace]] -- Wiki entry for Hermes Workspace
- [[hermes-workspace-api]] -- Full REST API endpoint inventory
- [[hermes-workspace-deployment]] -- Deployment guide
- [[hermes-workspace-quadlet]] -- Rootless Podman Quadlet config
- [[hermes-workspace-architecture]] -- System architecture
- [[hermes-workspace-mcp-hub]] -- MCP hub implementation
- [[hermes-workspace-swarm-architecture]] -- Swarm architecture

## Related

- `../domains/api/hermes-workspace-api.md` — Full REST API endpoint inventory
- `../domains/deployment/hermes-workspace-deployment.md` — Deployment guide
- `../deployment/hermes-workspace-quadlet.md` — Rootless Podman Quadlet config
