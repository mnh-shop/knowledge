---
name: hermes-workspace-features
tags: [agent-gateway, architecture, cli, dashboard, desktop, hermes-agent, mcp, messaging, multi-platform, orchestration, plugin-sdk, typescript]
description: "Hermes Workspace feature inventory: 19-screen UI surface, Conductor mission dispatch, jobs, echo-studio, vt-capital, playground, agents"
source: sources/hermes-workspace/
---

# Hermes Workspace — Feature Inventory

**Source:** `sources/hermes-workspace/`
**Codegraph:** `graphs/hermes-workspace/`
**Version:** 2.3.0 (MIT)

> Note: the repo's own `FEATURES-INVENTORY.md` is stale (declares v2.0.0).
> This page tracks the current 2.3.0 surface. Verifiable against
> `src/screens/`, `src/routes/`, and `src/server/`.

## UI surface — 19 screens

All screens live under `src/screens/` (each with a corresponding route
module in `src/routes/` where applicable):

| Screen | Module | What it does | Backend |
|---|---|---|---|
| Chat | `src/screens/chat/` | Hermes chat sessions with SSE streaming | `src/server/chat-backends.ts`, `chat-event-bus.ts` |
| Dashboard | `src/screens/dashboard/` | Metrics overview | `src/server/dashboard-aggregator.ts` |
| Files | `src/screens/files/` | Monaco file explorer + xterm terminal | `src/server/terminal-sessions.ts`, `pty-helper.py` |
| Memory | `src/screens/memory/` | Memory browser + external memory | `memory-browser.ts`, `external-memory-browser.ts` |
| Skills | `src/screens/skills/` | Skills catalog (`skills-screen.tsx`, `workspace-skills-screen.tsx`) | `src/routes/api/skills/` |
| MCP | `src/screens/mcp/` | MCP Hub: catalog, search, install | `src/server/mcp-hub/` |
| Swarm | `src/screens/swarm/` | Swarm v1 control plane | `src/server/swarm-*.ts` |
| Swarm2 | `src/screens/swarm2/` | Swarm v2 control plane | `src/server/swarm-*.ts` |
| Tasks | `src/screens/tasks/` | Kanban TaskBoard | `src/server/kanban-backend.ts` |
| Gateway | `src/screens/gateway/` | Gateway pairing/status | `src/server/gateway.ts`, `gateway-capabilities.ts` |
| Profiles | `src/screens/profiles/` | Hermes profile management | `src/server/hermes-config-store.ts` |
| Settings | `src/screens/settings/` | Connection settings, live re-pairing | `~/.hermes/workspace-overrides.json` |
| Playground | `src/screens/playground/` | Agent playground | `playground-admin.ts`, `playground-npc.ts` |
| Agora | `src/screens/agora/` | Agora community view | |
| Crew | `src/screens/crew/` | Crew orchestration | `crew-status.ts` |
| Jobs | `src/screens/jobs/` | Scheduled jobs + tasks | `claude-jobs.ts`, `claude-tasks.ts`, `jobs-api.ts` |
| Echo Studio | `src/screens/echo-studio/` | Echo Studio | |
| VT Capital | `src/screens/vt-capital/` | VT Capital | `vt-capital.ts` |
| Agents | `src/screens/agents/` | Agent View / Operations | `workspace-agents.ts`, `src/routes/operations.tsx` |

That is 19 screen modules in `src/screens/` (agents, agora, chat, crew,
dashboard, echo-studio, files, gateway, jobs, mcp, memory, playground,
profiles, settings, skills, swarm, swarm2, tasks, vt-capital).

## Conductor — mission dispatch

The Conductor is the mission/command surface (README.md:17,51,58,748):

- **Primary path:** uses the upstream hermes-agent **dashboard mission API**
  when available (zero-fork).
- **Fallback path:** when that endpoint is absent, dispatches through
  **Workspace-native Swarm** (`mode: native-swarm`) — no fork required
  ([#262](https://github.com/outsourc-e/hermes-workspace/issues/262)).
- **Routes:** `src/routes/api/conductor-spawn.ts` (status via
  `/api/conductor-spawn?missionId=...`), `conductor-stop.ts`.
- **Capability gates:** features requiring upstream endpoints show a clean
  placeholder instead of failing mid-action.
- **Screens:** `src/routes/conductor.tsx` + `src/screens/jobs/`.

## Jobs & tasks

- `src/routes/api/claude-jobs.ts`, `claude-jobs.$jobId.ts` — job lifecycle.
- `src/routes/api/claude-tasks.ts`, `claude-tasks.$taskId.ts`,
  `claude-tasks-assignees.ts`, `hermes-tasks.ts`, `hermes-tasks.$taskId.ts`.
- Client helpers: `src/lib/jobs-api.ts`, `src/lib/tasks-api.ts`,
  `src/server/kanban-backend.ts` (21,668 bytes).

## Echo Studio, VT Capital, Playground

- **Echo Studio** (`src/screens/echo-studio/`, `src/routes/echo-studio.tsx`) —
  audio/echo production surface.
- **VT Capital** (`src/screens/vt-capital/`, `src/routes/api/vt-capital.ts`) —
  trading/capital surface.
- **Playground** (`src/screens/playground/`, `src/routes/playground.tsx`) —
  agent experimentation; routes `playground-admin.ts`, `playground-npc.ts`;
  plus a **separate Cloudflare Worker** in `playground-ws-worker/`
  (`wrangler.toml`, `src/`) for WebSocket playground traffic.

## Agent View / Operations

- `src/screens/agents/` + `src/routes/operations.tsx` — the "Agent View /
  Operations" surface (README.md:17).
- `src/lib/workspace-agents.ts` — agent client helper.
- `src/routes/api/agent-bus.ts` — agent message bus route.

## MCP Hub

- `src/server/mcp-hub/`: `index.ts` unified search via `Promise.allSettled`
  over `sources/{local-file,mcp-get,generic-json}.ts`, dedup by
  `${source}:${name}`; `types.ts` trust levels; `cache.ts` (30 min mem +
  24 h disk); `trust.ts`; `lib/ssrf-guard.ts`.
- Routes: `src/routes/api/mcp/` (9 non-test modules).

## PWA, desktop, deployment

- **PWA** installable on desktop (Chrome/Edge install icon), iOS (Add to
  Home Screen), Android (Chrome "Add to Home screen") — README.md:577-633.
- **Tailscale** remote access: `tailscale ip -4` →
  `http://<ip>:3000` — README.md:577-633.
- **Native desktop:** Electron shell (`electron/main.cjs`, ports 8642/9119,
  `APP_PORT` 3847) + desktop updater (`docs/desktop-update-system.md`).
- **Cloudflare:** `wrangler.jsonc` + `playground-ws-worker/`.
- **macOS:** `macos/com.hermes.workspace.plist.template` launchd service.
- **Scripts:** 14 helper scripts in `scripts/`.
- **E2E:** Playwright specs in `e2e/` (chat-flicker-duplicate,
  chat-thinking-state, conductor-mobile-rendering).

## Related

- [[hermes-workspace]] -- Wiki entry
- [[hermes-workspace-architecture]] -- System architecture
- [[hermes-workspace-swarm-architecture]] -- Swarm architecture
- [[hermes-workspace-security]] -- Security model
- [[hermes-workspace-api]] -- REST API reference
- [[hermes-workspace-mcp-hub]] -- MCP hub implementation
- [[hermes-workspace-deployment]] -- Deployment guide
- [[hermes-agent]] -- Upstream backend
