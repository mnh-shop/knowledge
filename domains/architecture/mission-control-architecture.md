---
name: mission-control-architecture
tags: [mission-control, architecture, typescript, nextjs, react, dashboard, orchestration, monitoring, ai-llm, automation, bootc, cli, container, docker, event-bus, git, mcp, messaging, optimization, plugin-sdk, quadlet, security, storage, systemd, virtualization, webhook]
description: Mission Control Architecture
---

# Mission Control Architecture
**Source:** `sources/mission-control/`

## Overview

Mission Control is a self-contained Next.js 16 application that serves as a **unified dashboard and orchestration hub** for AI agent management. It bundles everything into a single binary: a SQLite-backed backend, a WebSocket gateway client, a real-time SSE event stream, an MCP server, a CLI, and a 32-panel SPA dashboard. There are no external service dependencies (no Postgres, no Redis, no S3).

---

## Routing Structure

The app uses a **catch-all route** `[[...panel]]/page.tsx` that acts as the SPA root. The single `Home()` component renders a full-height flex layout (`h-screen`) containing:

- **NavRail** -- Left sidebar with icon-based navigation
- **HeaderBar** -- Top bar with search, user menu, notifications
- **Main content area** -- Routes to panel components via `ContentRouter()`

The catch-all segment `[[...panel]]` maps URL path segments (e.g., `/tasks`, `/agents`, `/chat`) to Zustand `activeTab` state, which drives which panel component renders. The redirect `/sessions` to `/chat` is handled at the route level.

## Boot Sequence

On mount, the `Home()` component runs a carefully sequenced boot process:

1. **Auth check** -- Fetches `/api/auth/me`; 401 redirects to `/login?next=...`
2. **Capabilities** -- `/api/status?action=capabilities` determines dashboard mode (local vs full gateway), sets interface mode (essential vs full), checks gateway availability
3. **Gateway connection** -- Tries to connect WebSocket to a registered gateway; falls back to env vars or constructs URL from env-derived host/port/protocol
4. **Data preload** -- Parallel fetches for agents, sessions, projects, memory graph, skills; all results feed into Zustand store
5. **Onboarding check** -- `/api/onboarding` shows onboarding wizard for first-time admins
6. **Update checks** -- `/api/releases/check` and `/api/openclaw/version`

## Panel Rendering

The `ContentRouter` function matches `activeTab` to React components imported from `@/components/panels/`. Currently 32 panels including Overview, Agents, Tasks, Chat, Sessions, Logs, Memory, Cron, Skills, Workflows, Pipelines, Gateways, Exec Approvals, Settings, Security Audit, Eval Leaderboard, Terminal, Standups, Notifications, Docs, Debug, and more.

## Error Handling

The root component wraps all panel content in `ErrorBoundary` (class component with `getDerivedStateFromError`), showing a retry UI with the error message. Each panel can pass a custom fallback.

---

## Database Schema

### Schema Foundation

The database uses **better-sqlite3** with **WAL mode** (`journal_mode=WAL`), `synchronous=NORMAL`, `cache_size=1000`, `foreign_keys=ON`, and `busy_timeout=5000`. Migrations are tracked via a `schema_migrations` table (id + applied_at). The initial schema is loaded from `src/lib/schema.sql` (migration `001_init`), then 49 incremental migrations add tables, columns, and indexes.

### Core Tables (from schema.sql)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `tasks` | Central Kanban entity | id, title, status, priority, assigned_to, tags, outcome, retry_count, dispatch_attempts, project_id, github_* |
| `agents` | AI agent registry | id, name (unique), role, status, soul_content, working_memory, config, workspace_id |
| `comments` | Nested task discussions | id, task_id, author, content, parent_id, mentions |
| `activities` | Immutable activity stream | id, type, entity_type, entity_id, actor, description, data |
| `notifications` | User notifications | id, recipient, type, title, message, source_type, source_id |
| `quality_reviews` | Aegis gate records | task_id, reviewer, status, notes |

### Migration-Added Tables (49 migrations beyond init)

**Users and Auth:** `users`, `user_sessions`, `api_keys`, `agent_api_keys`

**Messaging:** `messages` (conversation_id-based)

**Workflows and Pipelines:** `workflow_templates`, `workflow_pipelines`, `pipeline_runs`

**Webhooks:** `webhooks` (with circuit breaker), `webhook_deliveries` (retry tracking)

**Settings:** `settings` (key/value store with category)

**Alert Rules:** `alert_rules` (entity_type, condition, action, cooldown)

**Multi-Tenancy:** `tenants`, `provision_jobs`, `provision_events`

**Workspaces:** `workspaces`

**Projects:** `projects`

**GitHub Sync:** `github_syncs`

**Skills:** `skills`

**Eval System:** `eval_runs`, `eval_golden_sets`, `eval_traces`

**Security:** `security_events`, `agent_trust_scores`, `mcp_call_log` (Ed25519 receipt signing)

**Token and Cost Tracking:** `token_usage`

**Spawn and Run Tracking:** `spawn_history`, `runs`

**Claude Sessions:** `claude_sessions`

**Adapters:** `adapter_configs`

**Direct Connections:** `direct_connections`

**FTS:** `memory_fts` (FTS5 virtual table for memory search)

### Workspace Isolation

Migrations 021-023 progressively added `workspace_id` to every data table. Migration 029 links workspaces to tenants. Every query in the system filters by `workspace_id` and `tenant_id`.

---

## State Management (Zustand 5)

Mission Control uses a **single Zustand store** (`useMissionControl`) created with `subscribeWithSelector` middleware. The store contains approximately 100+ properties organized into logical domains.

### Dashboard Mode and Boot

- `dashboardMode`: `'full'` (gateway connected) or `'local'` (standalone)
- `gatewayAvailable`, `localSessionsAvailable`, `capabilitiesChecked`, `bootComplete`
- `subscription`, `defaultOrgName`, `interfaceMode` (`'essential'` | `'full'`)

### Connection State

- `connection`: `{ isConnected, url, lastConnected, reconnectAttempts, latency, sseConnected }`
- `lastMessage`: Last WebSocket frame received

### Data Domains

Each domain has its own state array and CRUD operations:

- **Tasks** -- `tasks[]`, `selectedTask`, CRUD via `setTasks/addTask/updateTask/deleteTask`
- **Agents** -- `agents[]`, `selectedAgent`, CRUD via `setAgents/addAgent/updateAgent/deleteAgent`
- **Sessions** -- `sessions[]`, `selectedSession`, `updateSession`
- **Activities** -- `activities[]`, `setActivities`, `addActivity`
- **Notifications** -- `notifications[]`, `unreadNotificationCount`, mark read operations
- **Comments** -- `taskComments` (map of taskId to comments)

### Chat System

- `chatMessages[]`, `conversations[]`, `activeConversation`
- Pending message tracking: `replacePendingMessage`, `updatePendingMessage`, `removePendingMessage`
- `chatPanelOpen`, `isSendingMessage`

### Agent Communication

- **Terminal split panes** -- `splitPanes[]` (max 4 panes), `addSplitPane`, `removeSplitPane`, `clearSplitPanes`
- **Session attention** -- `sessionAttention` map for `'waiting'` | `'error'` indicators
- **Exec Approvals** -- `execApprovals[]` for tool execution authorization
- **Agent Chat** -- bidirectional messaging between agents

### Infrastructure

- **Logs** -- `logs[]` (last 1000), `logFilters` (level, source, session, search)
- **Token Usage** -- `tokenUsage[]`, `getUsageByModel()`, `getTotalCost()`
- **Cron Jobs** -- `cronJobs[]`, `updateCronJob`
- **Memory** -- memory files tree, content, FTS links, health
- **Skills** -- `skillsList`, `skillGroups`, `skillsTotal`
- **Memory Graph** -- `memoryGraphAgents[]` for RAG graph visualization
- **Spawn Requests** -- `spawnRequests[]` for agent spawning

### Tenant and Multi-Tenancy

- `tenants[]`, `activeTenant`, `fetchTenants`, `fetchOsUsers`
- `projects[]`, `activeProject`, `fetchProjects`
- Persisted to localStorage (`mc-active-tenant`, `mc-active-project`)

### UI State

- `activeTab` -- current panel (synced with URL via `usePathname()`)
- `sidebarExpanded`, `collapsedGroups[]` -- sidebar state persisted to localStorage
- `liveFeedOpen`, `headerDensity` (`'focus'` | `'compact'`)
- `dashboardLayout` -- persisted widget layout

### Update Notifications

- `updateAvailable` -- Mission Control version updates
- `openclawUpdate` -- OpenClaw gateway updates
- `doctorDismissedAt` -- OpenClaw Doctor banner 24-hour dismiss

### Persistence Pattern

Most UI state is persisted to **localStorage** with fallback defaults:

- Sidebar: `mc-sidebar-expanded`, `mc-sidebar-groups`
- Header: `mc-header-density`
- Layout: `mc-dashboard-layout`
- Dismissals: `mc-update-dismissed-version`, `mc-openclaw-update-dismissed`, `mc-doctor-dismissed-at`
- Tenant/Project context: `mc-active-tenant`, `mc-active-project`
- Live feed: `mc-livefeed-open`

### Usage Pattern

Components access the store via individual selectors for re-render optimization:

```typescript
const tasks = useMissionControl(s => s.tasks)
const updateTask = useMissionControl(s => s.updateTask)
```

---

## Real-Time System

### Two-Channel Architecture

Mission Control uses **two parallel real-time channels**:

**Channel 1: Server-Sent Events (SSE) for Local DB Mutations**

- Endpoint: `GET /api/events` -- `ReadableStream` with `text/event-stream`
- 30-second heartbeat keepalive
- Auth-gated: requires `viewer` role minimum
- Workspace-aware: filters events by `workspace_id`
- Forwards events from the `ServerEventBus` (singleton `EventEmitter` surviving HMR via `globalThis`)
- Server hook: `useServerEvents()` -- creates `EventSource`, dispatches to Zustand, reconnect with exponential backoff (2^attempts * 1000ms base, max 30s, 20 retries)

Event types broadcasted: `task.created`, `task.updated`, `task.deleted`, `task.status_changed`, `chat.message`, `notification.created`, `activity.created`, `agent.created/updated/deleted/status_changed/synced`, `audit.security`, `security.event`, `connection.created/disconnected`, `github.synced`, `run.created/updated/completed/eval_attached`, `task.escalated`, `session.updated`

**Channel 2: WebSocket for Gateway Communication**

- Client hook: `useWebSocket()` -- uses singleton refs (not React state) to survive re-renders
- Connection flow: connect to gateway WebSocket URL, receive `connect.challenge` with nonce, sign device identity payload using WebCrypto Ed25519, send handshake with signature/role/scopes
- Device identity: persistent Ed25519 keypair in localStorage (`mc-device-id` + `mc-device-key`)
- Heartbeat protocol: 30-second ping interval via `req`/`pong` frames, tracks `missedPongsRef`, after 3 missed pongs forces reconnect
- Gateway protocol frames: `connect.challenge`, `res` (response), `event` (real-time data)
- Event types: `tick`, `log`, `chat.message`, `notification`, `agent.status`, `tool.stream`, `exec.approval`, `context.compaction`, `model.fallback`, `spawn_result`, `cron_status`, `token_usage`
- Reconnection strategy: exponential backoff with 50% jitter, max 10 attempts, non-retryable errors stop immediately, path fallback tries `/ws`, `/gateway/ws`, etc.
- Gateway optional mode: `NEXT_PUBLIC_GATEWAY_OPTIONAL=true` skips reconnect entirely

### Smart Polling Fallback

When SSE or WebSocket is not available, panels fall back to REST polling via standard `apiFetch` calls.

### Server Event Bus

`src/lib/event-bus.ts` -- Singleton `EventEmitter` with typed events:

- `broadcast(type, data)` -- Emits structured events to all SSE clients
- Preserved across HMR via `globalThis.__eventBus`

---

## Agent Orchestration

### Agent Registration and Lifecycle

Agents are registered via the `agents` DB table. Each agent has:

- `name` (unique), `role` (coder|researcher|reviewer|tester|devops|assistant|agent)
- `status` (offline|idle|busy|error)
- `soul_content` (SOUL.md instructions), `working_memory`
- `config` (JSON with openclawId, dispatchModel, capabilities, capacity)

Registration paths:
- `POST /api/agents/register` or MCP tool `agents_register`
- Agent-sync system (`src/lib/agent-sync.ts`) syncs from gateway workspace directories
- Gateway adapters broadcast `agent.created` events through the event bus

### Task Dispatch Pipeline

The dispatch system runs as a scheduled tick with four stages in `src/lib/task-dispatch.ts`:

**Stage 1: Auto-Routing (`autoRouteInboxTasks`)**

Tasks in `inbox` status with no `assigned_to` get auto-assigned via **role affinity scoring**:

- Each task title + description is scored against agent keywords per role
- Idle agents get a +5 bonus
- Agent capabilities from config give +15 per matching keyword
- Capacity check: agents with 3+ in_progress tasks are skipped unless all agents at capacity
- Best-scoring available agent gets the assignment

**Stage 2: Aegis Review (`runAegisReviews`)**

Tasks in `review` status are fed to an LLM reviewer:

- Builds review prompt from task description + agent resolution
- Sends to configured LLM (gateway or direct API)
- Parses verdict: `VERDICT: APPROVED` or `VERDICT: REJECTED`
- Approved moves to `done`; rejected (max 3 retries) moves back to `assigned` with rejection notes
- On 3rd rejection, moves to `failed` with escalation event

**Stage 3: Dispatch (`dispatchAssignedTasks`)**

Tasks in `assigned` status are dispatched to their assigned agent:

- Atomic claim: `UPDATE tasks SET status='in_progress' WHERE status='assigned' AND id=?` prevents double-dispatch
- Dispatch path selection:
  1. Direct API (no gateway) -- calls Claude/OpenAI/local provider based on `dispatchModel` prefix
  2. Targeted session -- sends to existing gateway session via `chat.send`
  3. New gateway session -- invokes agent via OpenClaw gateway RPC with idempotency key
- Deferred completion via `agent.wait` with `async_state: 'pending'` later reconciled
- On failure: increments `dispatch_attempts`, retries up to 5 times before moving to `failed`

**Stage 4: Stale Task Recovery (`requeueStaleTasks`)**

Tasks stuck `in_progress` for 10+ minutes with offline agents are requeued back to `assigned` or moved to `failed` after 5 retries.

### Model Routing (`classifyDirectModel`)

Intelligent model selection based on task content:

- **Complex signals** (debug, diagnose, security audit, refactor) to Opus (claude-opus-4-6)
- **Routine signals** (status check, health check, simple, minor) to Haiku
- **Default** to Sonnet (claude-sonnet-4-6)
- Per-agent `dispatchModel` config override takes priority

### Provider Routing (`pickProvider`)

Based on `dispatchModel` prefix:

- `openai/`, `gpt-*`, `o1-*`, `o3-*` to OpenAI REST API
- `local/`, `ollama/`, `lmstudio/`, `litellm/` to LOCAL_LLM_ENDPOINT
- `claude-*` or bare to host-mounted Claude Code CLI (preferred) or Anthropic API

### Capacity Control

- Max 3 concurrent in-progress tasks per agent
- Auto-routing skips agents at capacity
- Agent status (offline/idle/busy) gates dispatch
- Direct API mode skips the offline-agent check

### Kill Signals

Agents can be stopped via `POST /api/agents/{id}/wake` (restart), `POST /api/sessions/{id}/control`, and gateway disconnect RPC. Session control includes pause/resume/stop commands.

---

## Multi-Gateway Architecture

### Framework Adapter Interface

All adapters share the `FrameworkAdapter` interface defined in `src/lib/adapters/adapter.ts`:

```typescript
interface FrameworkAdapter {
  readonly framework: string
  register(agent: AgentRegistration): Promise<void>
  heartbeat(payload: HeartbeatPayload): Promise<void>
  reportTask(report: TaskReport): Promise<void>
  getAssignments(agentId: string): Promise<Assignment[]>
  disconnect(agentId: string): Promise<void>
}
```

### Six Adapter Implementations

| Adapter | File | Framework |
|---------|------|-----------|
| OpenClaw | `openclaw.ts` | Primary adapter for OpenClaw gateway ecosystem |
| Generic | `generic.ts` | Fallback for any framework-agnostic agent |
| CrewAI | `crewai.ts` | CrewAI multi-agent teams |
| LangGraph | `langgraph.ts` | LangGraph agents |
| AutoGen | `autogen.ts` | Microsoft AutoGen agents |
| Claude SDK | `claude-sdk.ts` | Claude API SDK-based agents |

### Adapter Registry

The `getAdapter(framework)` function in `src/lib/adapters/index.ts` provides factory lookup.

### All Adapters Follow the Same Pattern

1. `register()` broadcasts `agent.created` event with framework tag, agent ID, name, metadata
2. `heartbeat()` broadcasts `agent.status_changed` with status and metrics
3. `reportTask()` broadcasts `task.updated` with progress, status, output
4. `getAssignments()` queries DB for pending tasks assigned to the agent
5. `disconnect()` broadcasts `agent.status_changed` with status='offline'

### Adapter Config Storage

Migration 032 creates `adapter_configs` table storing per-workspace framework configurations with a unique constraint on `(workspace_id, framework)`.

### Gateway Connection Management

Gateways are registered in the `gateways` table, managed by API routes under `/api/gateways/`. The system supports:

- **Gateway discovery** -- `/api/gateways/discover` finds available gateways
- **Gateway health** -- `/api/gateways/health` with health log history
- **Gateway connect** -- `/api/gateways/connect` establishes WebSocket connections with tokens
- **Gateway control** -- `/api/gateways/control` for management commands
- **Primary gateway** -- One gateway can be marked `is_primary`, auto-selected for WebSocket connections

### Direct API Dispatch (Gateway-Free)

When no gateway is available, the system falls back to direct API dispatch:

- **Anthropic** -- `ANTHROPIC_API_KEY` or host-mounted Claude Code CLI
- **OpenAI** -- `OPENAI_API_KEY`
- **Local** -- `LOCAL_LLM_ENDPOINT` (defaults to `http://host.docker.internal:1234/v1`)

The `NEXT_PUBLIC_GATEWAY_OPTIONAL=true` env var disables WebSocket reconnect loops in standalone mode.

---

## Security and Auth System

### Authentication Methods

1. **Session Cookie Auth (Default)** -- Login via `POST /api/auth/login`, scrypt password hashing, SHA-256 hashed session tokens with 7-day expiry
2. **API Key Auth** -- `x-api-key` header or `Authorization: Bearer <key>`, constant-time comparison via `safeCompare()`
3. **Agent-Scoped API Keys** -- Per-agent keys stored in `agent_api_keys` table with scopes, expiration, revocation
4. **Google Sign-In** -- OAuth flow via `POST /api/auth/google` with Google ID token
5. **Proxy Auth (Trusted Header)** -- For deployment behind Envoy/Authentik with OIDC
6. **Setup Wizard** -- `/setup` page with admin creation form for first-run

### Password Security

- scrypt hashing via `hashPassword()` / `verifyPassword()`
- Progressive rehashing on login
- Timing-safe rejection: non-existent usernames still run `verifyPassword()` against a `DUMMY_HASH`
- Minimum 12-character password enforced

### RBAC (Role-Based Access Control)

| Role | Level | Access |
|------|-------|--------|
| admin | 2 | Full access to all endpoints, settings, user management, super admin features |
| operator | 1 | Can manage tasks, agents, execute operations, create quality reviews |
| viewer | 0 | Read-only access to dashboards and status |

Usage: `requireRole(request, 'operator')` returns `{ user }` on success or `{ error, status: 401|403 }` on failure.

### Security Audit Trail

- **Audit log** -- `audit_log` table for all admin operations
- **Security events** -- `security_events` table (event_type, severity, source)
- **MCP call audit** -- `mcp_call_log` table with Ed25519 receipt signing for cryptographic offline verification
- **Trust scoring** -- `agent_trust_scores` table tracking trust_score, auth_failures, injection_attempts, etc.

### Hook Profiles (Security Configuration)

Three profiles in `src/lib/hook-profiles.ts`:

| Feature | minimal | standard | strict |
|---------|---------|----------|--------|
| Secret scanning | OFF | ON | ON |
| MCP audit | OFF | ON | ON |
| Block on secrets | OFF | OFF | ON |
| Rate limit multiplier | 2.0x | 1.0x | 0.5x |

### Security Scanner

Comprehensive on-demand security scan across 5 categories:

- **Credentials**: Admin password strength, API key config, .env file permissions
- **Network**: Host allowlist, HSTS, secure cookies, gateway binding
- **OpenClaw**: Gateway auth, bind address, tool permissions, sandboxing, exec restrictions
- **Runtime**: Injection guard, rate limiting, DB integrity, backup age, MCP receipt signing
- **OS** (platform-aware): Firewall, SSH, disk encryption, ASLR, MAC framework, fail2ban, system integrity protection

Each check has a `fixSafety` level: safe / requires-restart / requires-review / manual-only. Results produce an overall rating: hardened / secure / needs-attention / at-risk.

### Secret Scanner

25+ regex patterns for detecting leaked credentials: AWS keys, GitHub tokens, Stripe keys, JWTs, private keys, database connection strings, Slack/Discord webhooks, OpenAI/Anthropic API keys, GCP service accounts, Azure storage, SSH keys. Also provides `redactSecrets()` for safe logging.

---

## Aegis Review System

Aegis is an LLM-powered automatic quality reviewer for agent task completions. It acts as a **gate between "review" and "done" statuses**.

### Two-Path Integration

**Path 1: Scheduler-Driven** -- The scheduler calls `runAegisReviews()` on each tick:

1. Query tasks in `review` status (up to 3 per tick)
2. Lock by moving to `quality_review` status
3. Build review prompt with task details and agent resolution (up to 6000 chars)
4. Dispatch to LLM via gateway RPC or direct API
5. Parse verdict via regex: `VERDICT: APPROVED` or `VERDICT: REJECTED` with `NOTES:`
6. Approved to `done`; rejected (up to 3 retries) back to `assigned` with rejection comments; on 3rd rejection, to `failed` with escalation event

**Path 2: Manual (API-Driven)** -- `POST /api/quality-review` -- Human operator submits a review with taskId, reviewer name, status, and notes. Requires `operator` role minimum, rate-limited by `mutationLimiter`.

---

## Eval Framework

### Four-Layer Eval Engine

**Layer 1: Output Evals** -- Task completion and correctness. Score = completed/total. Pass threshold >= 70%.

**Layer 2: Trace Evals** -- Convergence analysis from MCP call logs. `convergenceScore()` computes total_calls / unique_tools ratio. Ratio > 3.0 indicates looping. Pass = not looping.

**Layer 3: Component Evals** -- Tool reliability from MCP call logs. Pass threshold >= 80%.

**Layer 4: Drift Detection** -- Rolling baseline comparison across three metrics (avg_tokens_per_session, tool_success_rate, task_completion_rate). Threshold > 10% drift = flagged.

### Storage

- `eval_runs` table: agent_name, eval_layer, score, passed, detail, golden_dataset_id
- `eval_golden_sets` table: named curated test suites with JSON entries
- `eval_traces` table: agent_name, task_id, trace (JSON step log), convergence_score, total_steps, optimal_steps

---

## Skills Hub

### Skill Sources

Five primary roots + per-agent workspace directories:

| Source | Path |
|--------|------|
| user-agents | `~/.agents/skills/` |
| user-codex | `~/.codex/skills/` |
| project-agents | `$CWD/.agents/skills/` |
| project-codex | `$CWD/.codex/skills/` |
| openclaw | `$OPENCLAW_HOME/skills/` |
| workspace | `$OPENCLAW_WORKSPACE_DIR/skills/` |

### Bidirectional Sync

- Disk scan: Recursively scans skill roots for directories containing `SKILL.md`
- Content hashing: SHA-256 of SKILL.md content for change detection
- Upsert logic: New skills inserted, changed skills updated (disk wins), removed skills auto-deleted (non-registry only)
- Registry skills (with `registry_slug`) are never auto-deleted from DB

### Registry Integration

- ClawdHub and skills.sh registries browsable via `/api/skills/registry`
- Skills installable from registries with security scanning
- Registry skills tracked via `registry_slug` and `registry_version`

### Security Scanning

Each skill gets a `security_status` ('unchecked' | 'safe' | 'suspicious' | 'blocked') tracked in the DB. The secret scanner + hook profiles gate which skills can be installed in strict mode.

---

## Key Source Files

| File | Purpose |
|------|---------|
| `src/app/[[...panel]]/page.tsx` | SPA shell, boot sequence, panel routing |
| `src/app/layout.tsx` | Root layout with globals.css |
| `src/app/login/page.tsx` | Login page |
| `src/app/setup/page.tsx` | First-time setup wizard |
| `src/store/index.ts` | Single Zustand store (approx. 100 properties) |
| `src/lib/db.ts` | Database singleton (better-sqlite3, WAL mode) |
| `src/lib/schema.sql` | Base schema (10 tables) |
| `src/lib/migrations.ts` | 50 incremental migrations (35+ tables total) |
| `src/lib/auth.ts` | Complete auth system (cookie/API key/proxy/Google/agent-scoped keys, RBAC) |
| `src/lib/password.ts` | scrypt hashing and verification |
| `src/lib/task-dispatch.ts` | Full orchestration pipeline |
| `src/lib/websocket.ts` | WebSocket client with Ed25519 device identity, heartbeat, reconnection |
| `src/lib/use-server-events.ts` | Client-side SSE hook dispatching to Zustand |
| `src/lib/event-bus.ts` | Server-side singleton EventEmitter |
| `src/app/api/events/route.ts` | SSE streaming endpoint for real-time DB mutations |
| `src/lib/adapters/adapter.ts` | FrameworkAdapter interface |
| `src/lib/adapters/index.ts` | Framework adapter factory (6 adapters) |
| `src/lib/agent-evals.ts` | Four-layer eval engine |
| `src/lib/security-scan.ts` | Comprehensive OS + app security scanner |
| `src/lib/secret-scanner.ts` | Credential leak detection (25+ regex patterns) |
| `src/lib/hook-profiles.ts` | Three security profiles (minimal/standard/strict) |
| `src/lib/skill-sync.ts` | Bidirectional disk-to-DB skill synchronization |
| `src/lib/scheduler.ts` | Built-in cron scheduler for periodic tasks |
| `src/lib/webhooks.ts` | Webhook delivery engine with retries and circuit breaker |
| `src/lib/device-identity.ts` | WebCrypto Ed25519 key management |
| `src/lib/csp.ts` | Content Security Policy |
| `src/lib/injection-guard.ts` | Prompt and command injection detection |
| `src/lib/rate-limit.ts` | Rate limiting |

## Related

- [[mission-control]] -- Project overview and feature summary
- [[mission-control-api]] -- REST, MCP, and CLI interfaces
- [[mission-control-deployment]] -- Deployment configuration and methods
- [[mission-control-mcp-server]] -- MCP server implementation
- [[mission-control-quadlet]] -- Container deployment with Quadlet
- [[mission-control-profile]] -- Quick reference profile
