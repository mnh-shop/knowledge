---
name: hermes-workspace
tags: [agent, hermes-agent, agent-gateway, dashboard, desktop, docker, mcp, messaging, multi-platform, orchestration, quadlet, systemd, wiki, typescript, nix, hermes-workspace]
description: "Wiki entry for Hermes Workspace: web/desktop command center for Hermes Agent with swarm orchestration and MCP hub (MIT)"
source: sources/hermes-workspace/
verification_date: 2026-07-12
verified_by: codegraph-verify
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
(README.md:15,17)

## Where to find things

### Architecture & Design

| What | Where |
|---|---|
| Full architecture | [[hermes-workspace-architecture]] (`domains/architecture/`) |
| Swarm architecture | [[hermes-workspace-swarm-architecture]] (`domains/architecture/`) |
| Feature inventory | [[hermes-workspace-features]] (`domains/architecture/`) |
| Security model | [[hermes-workspace-security]] (`domains/security/`) |
| Features inventory (stale) | `sources/hermes-workspace/FEATURES-INVENTORY.md` — v2.0.0, lags current 2.3.0; prefer the wiki/domains pages above |
| AGENTS.md (swarm contract) | `sources/hermes-workspace/AGENTS.md` |
| Design docs | `sources/hermes-workspace/docs/design/`, `docs/requirements/` |

### Screens (19 total)

The UI is organized into 19 screen modules under `src/screens/`:

| Screen | Purpose | Notes |
|---|---|---|
| `chat/` | Chat sessions | Routes `src/routes/chat/`, components `src/components/agent-chat/` |
| `dashboard/` | Metrics overview | Backed by `src/server/dashboard-aggregator.ts` |
| `files/` | File explorer (Monaco) | |
| `memory/` | Memory browser | `src/server/memory-browser.ts` |
| `skills/` | Skills catalog | `skills-screen.tsx` + `workspace-skills-screen.tsx` |
| `mcp/` | MCP Hub UI | `mcp-screen.tsx` + sub-components |
| `swarm/` | Swarm v1 control | |
| `swarm2/` | Swarm v2 control | |
| `tasks/` | Kanban TaskBoard | `src/server/kanban-backend.ts` |
| `gateway/` | Gateway status/pairing | |
| `profiles/` | Hermes profile manager | |
| `settings/` | Workspace settings | |
| `playground/` | Agent playground | |
| `agora/` | Agora community view | |
| `crew/` | Crew orchestration | `src/routes/api/crew-status.ts` |
| `jobs/` | Scheduled jobs | `claude-jobs.ts`, `claude-tasks.ts` |
| `echo-studio/` | Echo Studio | |
| `vt-capital/` | VT Capital | `src/routes/api/vt-capital.ts` |
| `agents/` | Agent View / Operations | |

Routes for most screens: `src/routes/<screen>.tsx` (e.g. `operations.tsx`,
`conductor.tsx`, `hermes-world.tsx`, `echo-studio.tsx`, `jobs.tsx`,
`playground.tsx`, `agora.tsx`, `swarm.tsx`, `swarm2.tsx`, `skills.tsx`).

### Swarm Orchestration

The Swarm is the most distinctive feature — multi-agent orchestration with
persistent workers.

| What | Where |
|---|---|
| Swarm architecture | [[hermes-workspace-swarm-architecture]] (`domains/architecture/`) |
| Swarm YAML (10 workers) | `sources/hermes-workspace/swarm.yaml` |
| Worker profiles | `sources/hermes-workspace/agents/` (10 README.md files) |
| Swarm server modules | `sources/hermes-workspace/src/server/swarm-*.ts` (24 files: 14 modules + 10 tests) |
| Swarm UI | `sources/hermes-workspace/src/screens/swarm/` |
| Swarm v2 UI | `sources/hermes-workspace/src/screens/swarm2/` |
| Swarm docs | `sources/hermes-workspace/docs/swarm/` (ARCHITECTURE.md, QUICKSTART.md, ROLES.md, SKILLS.md, AUTORESEARCH.md) |
| Swarm v2 specs | `sources/hermes-workspace/docs/swarm2-*-spec.md` |

The 14 non-test `swarm-*.ts` modules: `swarm-lifecycle`, `swarm-mode`,
`swarm-missions`, `swarm-checkpoints`, `swarm-memory`, `swarm-kanban-store`,
`swarm-environment`, `swarm-foundation`, `swarm-chat-reader`,
`swarm-notifications`, `swarm-model-resolver`, `swarm-profile-config`,
`swarm-roster`, `swarm-runtime-reset`. (10 `swarm-*.test.ts` companions.)

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
| Skills browser | `src/screens/skills/skills-screen.tsx` + `workspace-skills-screen.tsx` (there is no `src/components/skill-browser/`) |
| Skills server | `sources/hermes-workspace/skills/` (workspace-dispatch) |

### Dashboard & Kanban

| What | Where |
|---|---|
| Dashboard | `src/screens/dashboard/`, `src/server/dashboard-aggregator.ts` |
| Kanban TaskBoard | `src/screens/tasks/`, `src/server/kanban-backend.ts` |
| Swarm Kanban | `src/server/swarm-kanban-store.ts` |

### Conductor

Mission dispatch with a graceful zero-fork fallback (README.md:17,748):

- Uses the **dashboard mission API** when the upstream hermes-agent dashboard
  exposes it.
- Falls back to **Workspace-native Swarm dispatch** (`mode: native-swarm`)
  when that endpoint is absent — no fork required.
- Routes: `src/routes/api/conductor-spawn.ts`, `src/routes/api/conductor-stop.ts`.
- Status queryable via `/api/conductor-spawn?missionId=...`.
- Capability gates: features needing upstream endpoints show a clean
  placeholder instead of failing mid-action.

### Deployment

| What | Where |
|---|---|
| Docker | `sources/hermes-workspace/Dockerfile`, `docker-compose.yml` |
| One-line install | `curl -fsSL https://...install.sh | bash` |
| Install script | `sources/hermes-workspace/install.sh` |
| Nix | `sources/hermes-workspace/flake.nix` |
| Electron | `sources/hermes-workspace/electron/` (main.cjs, electron-builder) |
| Quadlet | [[hermes-workspace-quadlet]] — asset only (`assets/deployment/hermes-workspace-quadlet.md`); no wiki/domains page exists for it |
| Cloudflare | `sources/hermes-workspace/wrangler.jsonc` + `playground-ws-worker/` (separate Cloudflare Worker) |
| macOS launchd | `sources/hermes-workspace/macos/com.hermes.workspace.plist.template` |
| Helper scripts | `sources/hermes-workspace/scripts/` (14: start-stable.sh, stop-stable.sh, install-dashboard-service.sh, swarm-lifecycle-sweep.sh, generate-pwa-icons.js, etc.) |
| E2E tests | `sources/hermes-workspace/e2e/` (Playwright: chat-flicker-duplicate, chat-thinking-state, conductor-mobile-rendering) |

### PWA & Mobile Access

- **PWA** — installable app (README.md:577-633): desktop via Chrome/Edge
  install icon, iOS via "Add to Home Screen", Android via "Add to Home
  screen"; offline support + keyboard shortcuts.
- **Tailscale** — remote access without port forwarding: `tailscale ip -4`
  then `http://<tailscale-ip>:3000`; traffic stays end-to-end encrypted.
- **Desktop updater** — separate update system for the Workspace vs the
  bundled Agent (`docs/desktop-update-system.md`).
- **Live re-pairing** — connection URLs can be changed from
  `Settings → Connection` without restart; persisted to
  `~/.hermes/workspace-overrides.json` and applied immediately (gateway
  capabilities are reprobed on save) (README.md:169).

### Security

| Control | Where |
|---|---|
| Auth middleware on every API route | `src/server/auth-middleware.ts` (session tokens, password, cookie flags) |
| Rate limiting | `src/server/rate-limit.ts` (in-memory sliding window) |
| Path-traversal guard | `src/routes/api/files.ts` (real-path boundary check via `path.resolve` + `..` prefix reject) |
| SSRF guard | `src/server/mcp-hub/lib/ssrf-guard.ts` (DNS resolve + private/loopback/link-local reject) |
| Fail-closed remote bind | refuses non-loopback bind without `HERMES_PASSWORD` (README.md:682) |
| Cookie flags | `HttpOnly` + `SameSite=Strict` + `Secure` (production), overridable via `COOKIE_SECURE` (README.md:683,689-690) |

Full model: [[hermes-workspace-security]] (`domains/security/`).

### API Routes

All routes under `src/routes/api/` — **132 non-test route modules** in 14
domain groups plus top-level files:

| Group | Purpose |
|---|---|
| `sessions/` | Hermes session management |
| `memory/` | Memory CRUD |
| `skills/` | Skills catalog |
| `mcp/` | MCP catalog + config |
| `profiles/` | Hermes profiles |
| `dashboard/` | Dashboard metrics |
| `claude-proxy/` | Claude API proxy |
| `knowledge/` | Knowledge browser |
| `external-memory/` | External memory providers |
| `model/` | Model/provider info |
| `runs/` | Run tracking |
| `swarm-memory/` | Swarm-specific memory |
| `hermesworld/` | HermesWorld game API |
| `update/` | Desktop update |

Plus top-level route modules (`agent-bus.ts`, `auth.ts`, `auth-check.ts`,
`chat-events.ts`, `claude-config.ts`, `claude-jobs.ts`, `claude-tasks.ts`,
`conductor-spawn.ts`, `conductor-stop.ts`, `crew-status.ts`, `files.ts`,
`gateway-status.ts`, `gateway-reprobe.ts`, `mcp.ts`, `memory.ts`,
`models.ts`, `oauth.device-code.ts`, `oauth.poll-token.ts`, `plugins.ts`,
`send-stream.ts`, `send.ts`, `session-history.ts`, `session-status.ts`,
`skills.ts`, `swarm-*.ts`, `terminal-*.ts`, `transcribe.ts`, `vt-capital.ts`,
`workspace.ts`, etc.).

### HermesWorld Game Docs

There's a substantial game design project inside `docs/hermesworld/` — an
"AI-first MMO" concept with guild economics, agent companions, agora systems,
and visual specs. **40 markdown files** (23 top-level + `guides/` 7,
`lore/` 6, `walkthroughs/` 4): MASTER-PLAN.md, VISION-BEST-AI-MMO.md,
SWARM-GAME-ARCHITECTURE.md, GUILDS-AGENTS-COMPANION-ECONOMY.md, plus lore
(CLASSES-LORE, FACTIONS-LORE, SIGILS-LORE, TIMELINE, WORLD-LORE, ZONES-LORE)
and quest walkthroughs. This appears to be a side project/aspirational
design, not shipped code.

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
- [[hermes-workspace-features]] -- Feature inventory (19 screens, Conductor, jobs)
- [[hermes-workspace-security]] -- Security model
- [[hermes-workspace-api]] -- REST API reference
- [[hermes-workspace-deployment]] -- Deployment guide
- [[hermes-workspace-mcp-hub]] -- MCP hub implementation
- [[hermes-workspace-quadlet]] -- Quadlet deployment (asset only, no wiki page)
- [[hermes-profiles]] -- Agent profile

## Related

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
