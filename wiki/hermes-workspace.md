---
name: hermes-workspace
tags: [hermes, workspace, swarm, wiki]
description: Wiki entry for Hermes Workspace: web/desktop command center for Hermes Agent with swarm orchestration and MCP hub (MIT)
---

# Hermes Workspace

| Field | Value |
|---|---|
| **Origin** | [outsourc-e/hermes-workspace](https://github.com/outsourc-e/hermes-workspace) |
| **License** | MIT |
| **Version** | 2.3.0 |
| **Source** | `sources/hermes-workspace/` |
| **Repomix** | `raw/hermes-workspace/hermes-workspace.xml` (4MB) |
| **Codegraph** | `graphs/hermes-workspace/` |
| **Profile** | `sources/hermes-workspace/AGENTS.md` |
| **Stack** | React 19 + TanStack Start + Vite 7 + Tailwind 4 + TypeScript |

## What it is

A full web/desktop workspace that serves as Hermes Agent's command center.
Not a chat wrapper — it's an orchestration surface with chat, files,
terminal, memory, skills, MCP, swarm mode, kanban, jobs, and more.

**Zero-fork** — targets vanilla `hermes-agent`. Clone, don't fork.

## Where to find things

### Architecture & Design

| What | Where |
|---|---|
| Full architecture | [[hermes-workspace-architecture]] (`domains/architecture/`) |
| Swarm architecture | [[hermes-workspace-swarm-architecture]] (`domains/architecture/`) |
| Features inventory | `sources/hermes-workspace/FEATURES-INVENTORY.md` (comprehensive) |
| AGENTS.md (swarm contract) | `sources/hermes-workspace/AGENTS.md` |

### Swarm Orchestration

The Swarm is the most distinctive feature — multi-agent orchestration with
persistent workers.

| What | Where |
|---|---|
| Swarm architecture | [[hermes-workspace-swarm-architecture]] (`domains/architecture/`) |
| Swarm YAML (10 workers) | `sources/hermes-workspace/swarm.yaml` |
| Worker profiles | `sources/hermes-workspace/agents/` (10 README.md files) |
| Swarm server modules | `sources/hermes-workspace/src/server/swarm-*.ts` (15 files) |
| Swarm UI | `sources/hermes-workspace/src/screens/swarm/` |
| Swarm v2 UI | `sources/hermes-workspace/src/screens/swarm2/` |
| Swarm docs | `sources/hermes-workspace/docs/swarm/` (ARCHITECTURE.md, QUICKSTART.md, ROLES.md, SKILLS.md) |
| Swarm v2 specs | `sources/hermes-workspace/docs/swarm2-*-spec.md` |

### MCP Hub

| What | Where |
|---|---|
| MCP Hub architecture | [[hermes-workspace-mcp-hub]] (`domains/mcp/`) |
| Server source | `sources/hermes-workspace/src/server/mcp-hub/` (unified search over sources) |
| UI | `sources/hermes-workspace/src/screens/mcp/` |
| Sources: local-file, mcp-get, generic-json, user-defined | |

### Chat

| What | Where |
|---|---|
| Chat screens | `src/screens/chat/`, `src/routes/chat/` |
| Chat components | `src/components/agent-chat/` |
| Backend abstraction | `src/server/chat-backends.ts` (Enhanced Claude / Portable) |
| SSE streaming | `src/server/chat-event-bus.ts` |

### Files & Terminal

| What | Where |
|---|---|
| File browser | `src/components/file-explorer/` (Monaco Editor) |
| Terminal | `src/components/terminal/` (xterm.js) |
| Server-side terminal | `src/server/terminal-sessions.ts` |
| PTY helper | `src/server/pty-helper.py` |

### Memory & Skills

| What | Where |
|---|---|
| Memory browser | `src/screens/memory/`, `src/server/memory-browser.ts` |
| External memory | `src/server/external-memory-browser.ts` |
| Skills browser | `src/screens/skills/`, `src/components/skill-browser/` |
| Skills server | `sources/hermes-workspace/skills/` (workspace-dispatch) |

### Dashboard & Kanban

| What | Where |
|---|---|
| Dashboard | `src/screens/dashboard/`, `src/server/dashboard-aggregator.ts` |
| Kanban TaskBoard | `src/screens/tasks/`, `src/server/kanban-backend.ts` |
| Swarm Kanban | `src/server/swarm-kanban-store.ts` |

### Deployment

| What | Where |
|---|---|
| Docker | `sources/hermes-workspace/Dockerfile`, `docker-compose.yml` |
| One-line install | `curl -fsSL https://...install.sh | bash` |
| Install script | `sources/hermes-workspace/install.sh` |
| Nix | `sources/hermes-workspace/flake.nix` |
| Electron | `sources/hermes-workspace/electron/` (main.cjs, electron-builder) |

### API Routes

All routes under `src/routes/api/`:

| Route | Purpose |
|---|---|
| `/api/sessions` | Hermes session management |
| `/api/memory` | Memory CRUD |
| `/api/skills` | Skills catalog |
| `/api/mcp` | MCP catalog + config |
| `/api/profiles` | Hermes profiles |
| `/api/dashboard` | Dashboard metrics |
| `/api/claude-proxy` | Claude API proxy |
| `/api/knowledge` | Knowledge browser |
| `/api/external-memory` | External memory providers |
| `/api/model` | Model/provider info |
| `/api/runs` | Run tracking |
| `/api/swarm-memory` | Swarm-specific memory |
| `/api/hermesworld` | HermesWorld game API |
| `/api/update` | Desktop update |

### HermesWorld Game Docs

There's a substantial game design project inside `docs/hermesworld/` — an
"AI-first MMO" concept with guild economics, agent companions, agora systems,
and visual specs. See `docs/hermesworld/` for the full set (20+ markdown
files). This appears to be a side project/aspirational design, not shipped
code.

## For fork consideration

| Factor | Assessment |
|---|---|
| **License** | MIT |
| **Activity** | Active (v2.3.0, extensive docs, CI) |
| **Size** | Large (~4MB raw, 38MB codegraph) |
| **Dependencies** | Deeply tied to hermes-agent (gateway + dashboard APIs) |
| **Fork cost** | High — forking means either maintaining hermes-agent compat or diverging |
| **Unique value** | Swarm, MCP Hub, unified control plane — not available in hermes-agent itself |
| **Zero-fork** | Designed to be cloned, not forked — upstream is always hermes-agent |

## Related

- [[hermes-workspace-architecture]] -- System architecture
- [[hermes-workspace-swarm-architecture]] -- Swarm architecture
- [[hermes-workspace-api]] -- REST API reference
- [[hermes-workspace-deployment]] -- Deployment guide
- [[hermes-workspace-mcp-hub]] -- MCP hub implementation
- [[hermes-workspace-quadlet]] -- Quadlet deployment
- [[hermes-workspace-profile]] -- Agent profile

## Related repos

| Repo | Relationship |
|---|---|
| [[hermes-agent]] | Backend — Hermes Workspace is the UI control plane for Hermes Agent |
| [[hermes-startup-architect]] | Hermes skill — can be installed inside the workspace |

## Cross-project

- [[openclaw]] -- Comparable workspace/UI concept
- [[mission-control]] -- Alternative orchestration dashboard
- [[n8n]] -- Workflow engine complementary to workspace automation
- [[podman]] -- Container runtime for workspace deployment
- [[agentfield]] -- Alternative control plane for agent orchestration
