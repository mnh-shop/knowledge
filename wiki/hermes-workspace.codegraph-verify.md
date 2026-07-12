---
name: hermes-workspace-codegraph-verify
tags: [hermes-workspace, codegraph-verify, hermes-agent, mcp, swarm, electron, docker, typescript]
description: "Codegraph Verification: Hermes Workspace — validating wiki claims against indexed source code symbols"
source: sources/hermes-workspace/
---

# Codegraph Verification: Hermes Workspace

**Date:** 2026-07-12

## Claim 1: Web/desktop command center for Hermes Agent
- **Wiki says:** Hermes Workspace is a full web/desktop workspace that serves as Hermes Agent's command center — chat, files, terminal, memory, skills, MCP, swarm mode, kanban, jobs, etc. Stack: React 19 + TanStack Start + Vite 7 + Tailwind 4 + TypeScript.
- **Source evidence:**
  - `package.json` declares `"name": "hermes-workspace"`, `"type": "module"`, React 19 dependencies (`react`, `react-dom`), `@tanstack/react-router`, `@tanstack/react-start`, `vite`, `tailwindcss`
  - `electron/main.cjs` is the Electron desktop entry point with `BrowserWindow`, `app`, `ipcMain` — spawns gateway + dashboard services
  - `electron-builder.config.cjs` configures `electron-builder` for macOS (DMG, arm64+x64), Windows (portable+NSIS), with GitHub publisher
  - `electron/preload.cjs` and `electron/prod-server.cjs` support the Electron shell
  - UI screens in `src/screens/`: `chat/`, `files/`, `terminal/`, `memory/`, `skills/`, `mcp/`, `swarm/`, `swarm2/`, `dashboard/`, `tasks/` (kanban), `gateway/`, `profiles/`, `settings/`, `playground/`, `agora/`, `crew/`, `jobs/`
  - `src/server/terminal-sessions.ts` implements PTY-based terminal via Python helper
  - `src/server/memory-browser.ts` and `src/server/external-memory-browser.ts` provide memory CRUD
  - `skills/` directory at repo root contains workspace-dispatch skills
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Swarm orchestration with persistent workers
- **Wiki says:** Swarm is multi-agent orchestration with persistent workers. YAML config at `swarm.yaml` defines 10 workers (orchestrator, km-agent, builder, reviewer, QA, researcher, ops-watch, maintainer, strategist, inbox-triage). 24 `swarm-*.ts` server modules, 10 agent profiles in `agents/`, swarm UI at `src/screens/swarm/` and `src/screens/swarm2/`.
- **Source evidence:**
  - `swarm.yaml` exists (10,165 bytes, `version: 1`) with 10 worker definitions — each has `id`, `name`, `role`, `specialty`, `model`, `tools`, `skills`, `capabilities`, `greenlightRequiredFor`
  - `src/server/` contains 24 `swarm-*.ts` modules: `swarm-lifecycle.ts`, `swarm-mode.ts`, `swarm-missions.ts`, `swarm-checkpoints.ts`, `swarm-memory.ts`, `swarm-kanban-store.ts`, `swarm-environment.ts`, `swarm-foundation.ts`, `swarm-chat-reader.ts`, `swarm-notifications.ts`, `swarm-model-resolver.ts`, `swarm-profile-config.ts`, etc.
  - `agents/` directory contains 10 README.md profiles: `orchestrator`, `km-agent`, `builder`, `maintainer`, `ops-watch`, `qa`, `researcher`, `reviewer`, `strategist`, `inbox-triage`
  - `src/screens/swarm/` and `src/screens/swarm2/` contain swarm UI components
  - `docs/swarm/` contains architecture docs: `ARCHITECTURE.md`, `QUICKSTART.md`, `ROLES.md`, `SKILLS.md`
  - `docs/swarm2-*-spec.md` files exist for swarm v2 specs
  - `AGENTS.md` documents the "semantic swarm workers" contract with tool/skill/MCP assignment per worker
  - 20 API routes for swarm: `src/routes/api/swarm-*.ts` (chat, dispatch, health, lifecycle, missions, memory, runtime, kanban, decompositions, etc.)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: MCP Hub — unified MCP server catalog and installer
- **Wiki says:** MCP Hub at `src/server/mcp-hub/` provides unified search over multiple MCP sources (local-file, mcp-get, generic-json, user-defined). UI at `src/screens/mcp/`. Sources include local-file, mcp-get, generic-json, and user-defined.
- **Source evidence:**
  - `src/server/mcp-hub/index.ts` (270 lines) implements `unifiedSearch()` aggregating results from `fetchLocalFile()`, `fetchMcpGet()`, `fetchGenericJson()` via `Promise.allSettled`, with dedup by `${source}:${name}`
  - `src/server/mcp-hub/types.ts` defines `HubMcpEntry` with `id`, `name`, `description`, `source` (mcp-get|local|user), `trust` (official|community|unverified), `template` (MCP client config), `installed` flag
  - `src/server/mcp-hub/sources/local-file.ts` wraps `mcp-presets-store` to return preset entries
  - `src/server/mcp-hub/sources/mcp-get.ts` fetches from the mcp-get registry
  - `src/server/mcp-hub/sources/generic-json.ts` loads user-defined sources at runtime
  - `src/server/mcp-hub/cache.ts` implements two-tier cache (in-memory 30 min + disk 24h)
  - `src/server/mcp-hub/trust.ts` validates/normalizes templates (CODEX-6 hardening — shell metachar rejection, transport validation)
  - `src/server/mcp-hub/lib/ssrf-guard.ts` provides SSRF protection
  - `src/server/mcp-hub/lib/ssrf-guard.test.ts` tests the SSRF guard
  - API routes under `src/routes/api/mcp/` expose MCP catalog and config operations
  - UI at `src/screens/mcp/mcp-screen.tsx` with sub-components, hooks, and lib
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Docker deployment with multi-service compose
- **Wiki says:** Docker deployment via `Dockerfile` and `docker-compose.yml`. One-line install via `install.sh`. Also supports Nix flake (`flake.nix`). Images published to `ghcr.io/outsourc-e/hermes-workspace`.
- **Source evidence:**
  - `Dockerfile` exists (multi-stage: `node:22-slim` build → runtime, includes `python3` for PTY helper)
  - `docker-compose.yml` defines services for `hermes-agent` and `hermes-workspace` with persistent volumes (`hermes-agent-data`, `hermes-workspace-files`), health checks, and network config
  - `docker-compose.dev.yml` provides development overrides
  - `install.sh` exists at repo root
  - `flake.nix` exists for Nix-based deployment
  - Dockerfile comments reference `ghcr.io/outsourc-e/hermes-workspace:latest`
  - `docker/` directory contains additional Docker resources
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: SSE streaming chat backends with multiple providers
- **Wiki says:** Chat uses SSE streaming with backend abstraction supporting Enhanced Claude and Portable backends. `chat-event-bus.ts` handles event broadcasting. API routes serve session management, history, and streaming.
- **Source evidence:**
  - `src/server/chat-backends.ts` exports `streamClaudeChat()` and `UnifiedChatOptions` — resolves chat backend via `chat-mode.ts`
  - `src/server/chat-event-bus.ts` implements SSE event bus with subscriber pattern (`ChatSSESubscriber`, `broadcast()`) — survives Vite HMR via `globalThis`
  - `src/server/chat-mode.ts` contains backend resolution logic
  - `src/server/claude-api.ts` (18,671 bytes) implements the Claude API client
  - `src/server/openai-compat-api.ts` provides OpenAI-compatible backend support
  - API routes: `src/routes/api/send-stream.ts`, `src/routes/api/send.ts`, `src/routes/api/sessions/`, `src/routes/api/chat-events.ts`, `src/routes/api/session-history.ts`
  - Test files: `src/server/claude-agent.test.ts`, `src/server/claude-tasks-backend.test.ts`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: REST API surface with 30+ endpoint modules
- **Wiki says:** API routes under `src/routes/api/` cover sessions, memory, skills, MCP, profiles, dashboard, claude-proxy, knowledge, external-memory, model info, runs, swarm-memory, hermesworld, and update.
- **Source evidence:**
  - `src/routes/api/` contains 60+ route modules/files organized by domain
  - Confirmed route modules: `sessions/`, `memory/`, `skills/`, `mcp/`, `profiles/`, `dashboard/`, `claude-proxy/`, `knowledge/`, `external-memory/`, `model/`, `runs/`, `swarm-memory/`, `hermesworld/`, `update/`, `files.ts`, `terminal-*.ts`, `swarm-*.ts`, `gateway-status.ts`, `plugins.ts`, etc.
  - Dashboard: `src/server/dashboard-aggregator.ts` (36,271 bytes) aggregates metrics
  - Kanban: `src/server/kanban-backend.ts` (21,668 bytes) with task management
  - Auth: `src/server/auth-middleware.ts` (9,101 bytes)
  - Data stores: `src/server/hermes-config-store.ts`, `src/server/mcp-hub-sources-store.ts`, `src/server/local-session-store.ts`
- **Verdict:** ✅ CORRECT (API surface confirmed; precise count of 60+ route files exceeds wiki's listed 15+ endpoint groups)
- **Fix needed:** None

## Claim 7: Gateway integration with WebSocket protocol
- **Wiki says:** Workspace integrates with Hermes Agent gateway; AGENTS.md documents gateway pairing. Gateway uses WebSocket-based protocol frames.
- **Source evidence:**
  - `src/server/gateway.ts` (27,539 bytes) implements WebSocket gateway with `GatewayFrame` type system (req/res/event/evt frames), cryptographic key exchange, and framing protocol
  - `src/server/gateway-capabilities.ts` (32,100 bytes) defines capability negotiation
  - `src/routes/api/gateway-status.ts` and `src/routes/api/gateway-reprobe.ts` provide gateway health endpoints
  - `AGENTS.md` documents canonical setup: "one gateway + one dashboard" with specific ports (gateway :8642, dashboard :9119, workspace :3000)
  - `electron/main.cjs` spawns gateway + dashboard as child processes
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 7 key claims from the Hermes Workspace wiki have been verified against the source code:
- ✅ Web/desktop command center: React 19 + TanStack Start + Electron confirmed
- ✅ Swarm orchestration: 10 workers, 24 server modules, 10 agent profiles confirmed
- ✅ MCP Hub: Unified search over local/mcp-get/generic-json sources confirmed
- ✅ Docker deployment: Dockerfile, docker-compose.yml, install.sh, flake.nix confirmed
- ✅ SSE streaming chat: Event bus with multiple backend abstraction confirmed
- ✅ REST API: 60+ route modules across 15+ domain groups confirmed
- ✅ Gateway integration: WebSocket protocol with cryptographic frames confirmed

## Related

- [[hermes-workspace]] -- Main wiki entry
- [[hermes-workspace-architecture]] -- System architecture
- [[hermes-workspace-mcp-hub]] -- MCP hub implementation
- [[hermes-workspace-swarm-architecture]] -- Swarm architecture
- [[hermes-workspace-deployment]] -- Deployment guide
- [[hermes-agent.codegraph-verify]] -- Codegraph verification for upstream Hermes Agent

## Cross-project

- [[hermes-bus.codegraph-verify]] -- Codegraph verification for Hermes Bus
- [[hermes-plugins.codegraph-verify]] -- Codegraph verification for Hermes Plugins
- [[openclaw.codegraph-verify]] -- Comparable workspace/orchestration verification
- [[mission-control]] -- Alternative orchestration dashboard
