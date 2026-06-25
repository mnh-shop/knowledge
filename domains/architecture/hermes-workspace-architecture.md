---
name: hermes-workspace-architecture
tags: [hermes, architecture, typescript, agent-gateway, messaging, multi-platform]
description: Hermes Workspace architecture: web/desktop command center for Hermes Agent with swarm orchestration and MCP hub
---

# Hermes Workspace Architecture

**Codegraph:** `graphs/hermes-workspace/`
**Source:** `sources/hermes-workspace/`

## What it is

A full-featured web/desktop workspace that serves as the command center for
Hermes Agent. It is **not** a chat wrapper — it's an orchestration surface
for managing Hermes sessions, swarm workers, memory, skills, MCP servers,
files, terminals, and scheduled jobs.

**Zero-fork philosophy** (from README): "Clone, don't fork. Runs on vanilla
hermes-agent installed via Nous's own installer."

## Stack

| Layer | Technology |
|---|---|
| Framework | React 19 + TanStack Start/Router + Vite 7 |
| Styling | Tailwind CSS 4 |
| State | Zustand |
| Terminal | xterm.js + Python pty-helper (server-side) |
| Editor | Monaco Editor (file explorer) |
| Language | TypeScript |
| Package | pnpm workspaces |
| Desktop | Electron (electron/main.cjs) |
| Nix | flake.nix + flake.lock |
| CI/CD | None visible — manual/build scripts |

## Architecture

```
Client (Browser / Electron)
    │
    ├── React SPA (TanStack Router)
    │   ├── /chat          — Chat sessions
    │   ├── /dashboard     — Aggregated metrics
    │   ├── /files         — File browser + Monaco
    │   ├── /terminal      — PTY terminal
    │   ├── /memory        — Memory browser
    │   ├── /skills        — Skills browser
    │   ├── /mcp           — MCP catalog + config
    │   ├── /swarm         — Swarm control plane
    │   ├── /swarm2        — Swarm v2 (next-gen)
    │   ├── /tasks         — Kanban TaskBoard
    │   ├── /jobs          — Cron job manager
    │   ├── /gateway       — Gateway status
    │   ├── /settings      — All config
    │   ├── /agents        — Agent profiles
    │   ├── /agora         — Agora (game AI?)
    │   ├── /crew          — Crew mode
    │   ├── /profiles      — Hermes profiles
    │   ├── /playground    — API playground
    │   ├── /echo-studio   — Echo Studio
    │   └── /vt-capital    — VT Capital
    │
    └── Components: agent-chat, agent-swarm, agent-view,
                    file-explorer, terminal, memory-viewer,
                    inspector, usage-meter, mobile-prompt, etc.
```

**Server side** (TanStack Start server functions + API routes):

```
src/server/
├── auth-middleware.ts         — Route authentication (CSP, path traversal)
├── chat-backends.ts           — Chat backend abstraction (Enhanced Claude / Portable)
├── chat-event-bus.ts          — Real-time chat events
├── claude-api.ts              — Claude API client
├── claude-dashboard-api.ts    — Hermes dashboard API proxy
├── claude-tasks-backend.ts    — Claude Tasks / Conductor integration
├── conductor-mission-*.ts     — Mission dispatch + decomposition
├── gateway.ts                 — Hermes Gateway client
├── mcp-hub/                   — MCP catalog + marketplace + sources
├── swarm-*.ts                 — Swarm orchestration subsystem (10+ files)
├── memory-browser.ts          — Memory browsing API
├── knowledge-browser.ts       — Knowledge browsing API
├── skills-browser.ts          — Skills browsing API (not found — check name)
├── profiles-browser.ts        — Hermes profiles
├── terminal-sessions.ts       — PTY terminal sessions
├── kanban-backend.ts          — Kanban board backend
├── update-system.ts           — Desktop update system
└── workspace-state-dir.ts     — Workspace state directory management
```

## Key concepts

### Dual chat backend

The chat screen supports two backends:
1. **Enhanced Claude** — full session API via Hermes Agent gateway (persistent
   history, tool calls, streaming)
2. **Portable** — OpenAI-compatible `/v1/chat/completions` (Ollama, LM Studio,
   vLLM, etc.)

### Routes

API routes are under `src/routes/api/`:
- `/api/sessions` — Hermes session management
- `/api/memory` — Memory CRUD
- `/api/skills` — Skills catalog
- `/api/mcp` — MCP catalog + config
- `/api/profiles` — Hermes profiles
- `/api/dashboard` — Dashboard metrics
- `/api/claude-proxy` — Proxy to Claude API
- `/api/knowledge` — Knowledge browser
- `/api/external-memory` — External memory providers
- `/api/model` — Model/provider info
- `/api/runs` — Run tracking
- `/api/swarm-memory` — Swarm-specific memory
- `/api/hermesworld` — HermesWorld game API
- `/api/update` — Desktop update

## Relationship to hermes-agent

- **Depends on** [[hermes-agent]] for the backend agent runtime
- Communicates with Hermes via Gateway API (`:8642`) and Dashboard API (`:9119`)
- "Clone, don't fork" — zero-fork policy means it targets vanilla hermes-agent

## For fork consideration

This is a substantial codebase (~4MB raw). Forking considerations:
- **License:** MIT
- **Active:** v2.3.0 with active development, swarm mode, extensive docs
- **Dependency chain:** Deeply tied to Hermes Agent; forking means either
  keeping hermes-agent compatibility or diverging significantly
- **Complexity:** Large surface area (20+ screens, 50+ server modules, swarm
  subsystem, MCP hub)
- **Unique value:** Swarm orchestration, MCP hub, all-in-one Hermes control
  plane — features that don't exist in hermes-agent itself

## Related

- [[hermes-workspace]] -- Wiki entry
- [[hermes-workspace-profile]] -- Agent profile
- [[hermes-workspace-api]] -- REST API reference
- [[hermes-workspace-swarm-architecture]] -- Swarm architecture
- [[hermes-workspace-deployment]] -- Deployment guide
- [[hermes-workspace-mcp-hub]] -- MCP hub implementation
- [[hermes-workspace-quadlet]] -- Quadlet deployment

## Links

- Wiki: [[hermes-workspace]]
- Source: `sources/hermes-workspace/`
- Repomix: `raw/hermes-workspace/hermes-workspace.xml` (4MB)
- Features inventory: `sources/hermes-workspace/FEATURES-INVENTORY.md`
- Agent contract (swarm): `sources/hermes-workspace/AGENTS.md`
