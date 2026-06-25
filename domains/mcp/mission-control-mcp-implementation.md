---
name: mission-control-mcp
description: "Mission Control MCP hub server — 49 tools across system, developer workflow, and service management"
tags: [ai-llm, cli, dashboard, documentation, mcp, monitoring, plugin-sdk, security]
---

# Mission Control MCP Implementation

Mission Control provides a **Model Context Protocol (MCP) server** that wraps its REST API as MCP tools. It ships as a standalone script (`scripts/mc-mcp-server.cjs`) using JSON-RPC 2.0 over stdin/stdout with zero external dependencies.

## Quick Reference

```bash
# Register with Claude Code
claude mcp add mission-control -- node /path/to/mission-control/scripts/mc-mcp-server.cjs

# Environment
MC_URL=http://127.0.0.1:3000
MC_API_KEY=<key>
# Alternative: MC_COOKIE=<session-cookie>
```

## Implementation Overview

| Aspect | Detail |
|---|---|
| Transport | stdio (stdin/stdout, blocking mode) |
| Protocol | JSON-RPC 2.0, MCP `2024-11-05` |
| Auth | `x-api-key` header or `Cookie` header, proxied from env |
| Config load order | `~/.mission-control/profiles/default.json`, then env vars |
| Request timeout | 30 seconds per HTTP call |
| Server identity | `name: "mission-control"`, `version: "2.0.1"` |
| Capabilities | `tools: {}` (no resources or prompts exposed yet) |
| Test coverage | Playwright E2E tests in `tests/mcp-server.spec.ts` |

## MCP Protocol Methods Supported

- `initialize` -- returns protocol version, server info, empty capabilities
- `tools/list` -- returns all 49 tool definitions with names, descriptions, and input schemas
- `tools/call` -- dispatches to named tool handler, returns JSON string result
- `ping` -- returns empty response for liveness check
- `notifications/initialized` -- acknowledged (no response)

## Tool Categories

All 49 tools are organized into 13 logical groups. Every tool name is prefixed with `mc_`.

### Agents (6 tools)

Tools for registering, inspecting, and managing AI agents.

| Tool | Description | Endpoint |
|---|---|---|
| `mc_list_agents` | List all registered agents | `GET /api/agents` |
| `mc_get_agent` | Get details of a specific agent by ID | `GET /api/agents/{id}` |
| `mc_heartbeat` | Send a heartbeat indicating the agent is alive | `POST /api/agents/{id}/heartbeat` |
| `mc_wake_agent` | Wake a sleeping agent | `POST /api/agents/{id}/wake` |
| `mc_agent_diagnostics` | Get diagnostics (health, config, recent activity) | `GET /api/agents/{id}/diagnostics` |
| `mc_agent_attribution` | Get cost attribution, audit trail, and mutation history | `GET /api/agents/{id}/attribution?hours=&section=` |

Inputs: `id` (string|number, required for all except list). Attribution also accepts `hours` (number, default 24) and `section` (comma-separated: identity,audit,mutations,cost).

### Agent Memory (3 tools)

Read, write, and clear an agent's working memory.

| Tool | Description | Endpoint |
|---|---|---|
| `mc_read_memory` | Read an agent's working memory | `GET /api/agents/{id}/memory` |
| `mc_write_memory` | Write or append to an agent's working memory | `PUT /api/agents/{id}/memory` |
| `mc_clear_memory` | Clear an agent's working memory | `DELETE /api/agents/{id}/memory` |

`mc_write_memory` requires `id` and `working_memory` (string). Optional `append` (boolean, default false).

### Knowledge Base (7 tools)

File-system-backed memory with full-text search, health diagnostics, graph analysis, and gap detection.

| Tool | Description | Endpoint |
|---|---|---|
| `mc_search_knowledge` | Full-text search across knowledge base (FTS5, BM25, operators: AND, OR, NOT, NEAR, "phrase", prefix\*) | `GET /api/memory/search?q=&limit=` |
| `mc_read_knowledge_file` | Read a file from the knowledge base (returns content, wiki-links, schema validation) | `GET /api/memory?action=content&path=` |
| `mc_write_knowledge_file` | Create or update a knowledge base file | `POST /api/memory` |
| `mc_knowledge_health` | Health diagnostics: schema, connectivity, link integrity, freshness, naming, organization | `GET /api/memory/health` |
| `mc_rebuild_search_index` | Rebuild FTS index from all knowledge base files | `POST /api/memory/search` (action: rebuild) |
| `mc_knowledge_gaps` | Detect knowledge gaps (broken wiki-links, orphans, stale content, missing topics) | `POST /api/memory/process` (action: gap-detect) |
| `mc_knowledge_consolidate` | Analyze knowledge graph structure (hub nodes, bridges, clusters, weak edges) | `POST /api/memory/process` (action: consolidate) |

Key inputs for write: `path` (string, e.g. "memory/decisions/auth-strategy.md"), `content` (string, markdown), `create` (boolean, fails if path exists). Search accepts `q` (required, FTS5 syntax) and `limit` (default 20, max 100).

### Agent Soul (3 tools)

Manage an agent's SOUL -- the personality/capability definition injected into dispatch prompts.

| Tool | Description | Endpoint |
|---|---|---|
| `mc_read_soul` | Read an agent's SOUL content (identity and behavioral directives) | `GET /api/agents/{id}/soul` |
| `mc_write_soul` | Write SOUL content or apply a named template | `PUT /api/agents/{id}/soul` |
| `mc_list_soul_templates` | List available SOUL templates or retrieve a specific one | `PATCH /api/agents/{id}/soul?template=` |

`mc_write_soul` accepts `soul_content` (string, markdown) or `template_name` (string). `mc_list_soul_templates` accepts optional `template` name to retrieve.

### Tasks (6 tools)

Full task lifecycle: create, read, update, list, queue, and broadcast.

| Tool | Description | Endpoint |
|---|---|---|
| `mc_list_tasks` | List tasks with optional filters (status, assignee, priority, search, limit) | `GET /api/tasks` |
| `mc_get_task` | Get a specific task by ID | `GET /api/tasks/{id}` |
| `mc_create_task` | Create a new task | `POST /api/tasks` |
| `mc_update_task` | Update an existing task (status, priority, assignee, title, description) | `PUT /api/tasks/{id}` |
| `mc_poll_task_queue` | Poll the task queue for an agent -- returns next available task(s) | `GET /api/tasks/queue?agent=&max_capacity=` |
| `mc_broadcast_task` | Broadcast a message to all subscribers of a task | `POST /api/tasks/{id}/broadcast` |

Status values for filtering: `backlog`, `inbox`, `assigned`, `awaiting_owner`, `in_progress`, `review`, `quality_review`, `done`, `failed`. Priorities: `low`, `medium`, `high`, `critical`. Default list limit 50, max 200.

### Task Comments (2 tools)

Threaded comments on tasks with @mention support.

| Tool | Description | Endpoint |
|---|---|---|
| `mc_list_comments` | List comments on a task | `GET /api/tasks/{id}/comments` |
| `mc_add_comment` | Add a comment to a task (supports @mentions and threaded replies) | `POST /api/tasks/{id}/comments` |

`mc_add_comment` requires `id` and `content`. Optional `parent_id` for threaded replies.

### Sessions (4 tools)

Manage active Claude Code, Codex CLI, and Hermes sessions.

| Tool | Description | Endpoint |
|---|---|---|
| `mc_list_sessions` | List all active sessions | `GET /api/sessions` |
| `mc_control_session` | Control a session (monitor, pause, terminate) | `POST /api/sessions/{id}/control` |
| `mc_continue_session` | Send a follow-up prompt to an existing session | `POST /api/sessions/continue` |
| `mc_session_transcript` | Get the transcript of a session (messages, tool calls, reasoning) | `GET /api/sessions/transcript` |

Session kinds: `claude-code`, `codex-cli`, `hermes`. `mc_control_session` actions: `monitor`, `pause`, `terminate`. Transcript limit default 40, max 200.

### Connections (2 tools)

Tool registration for agents connecting directly (no gateway required).

| Tool | Description | Endpoint |
|---|---|---|
| `mc_list_connections` | List active agent connections (tool registrations) | `GET /api/connect` |
| `mc_register_connection` | Register a tool connection for an agent | `POST /api/connect` |

Registration requires `tool_name` and `agent_name`.

### Tokens & Costs (3 tools)

Token usage and cost analytics.

| Tool | Description | Endpoint |
|---|---|---|
| `mc_token_stats` | Aggregate token usage (total tokens, cost, requests, per-model breakdown) | `GET /api/tokens?action=stats&timeframe=` |
| `mc_agent_costs` | Per-agent cost breakdown with timeline and model details | `GET /api/tokens?action=agent-costs&timeframe=` |
| `mc_costs_by_agent` | Per-agent cost summary over N days | `GET /api/tokens/by-agent?days=` |

Timeframes: `hour`, `day`, `week`, `month`, `all`. `mc_costs_by_agent` days default 30, max 365.

### Skills (2 tools)

Browse and read agent skills from local directories and external registries.

| Tool | Description | Endpoint |
|---|---|---|
| `mc_list_skills` | List all skills available in the system | `GET /api/skills` |
| `mc_read_skill` | Read the content of a specific skill | `GET /api/skills?mode=content&source=&name=` |

`mc_read_skill` requires `source` (e.g. workspace, system) and `name`.

### Cron (1 tool)

| Tool | Description | Endpoint |
|---|---|---|
| `mc_list_cron` | List all cron jobs | `GET /api/cron` |

### Status (3 tools)

System health and overview.

| Tool | Description | Endpoint |
|---|---|---|
| `mc_health` | Check Mission Control health status (no auth required) | `GET /api/status?action=health` |
| `mc_dashboard` | Dashboard summary (agents, tasks, sessions, costs) | `GET /api/status?action=dashboard` |
| `mc_status` | System status overview (uptime, memory, disk, sessions, processes) | `GET /api/status?action=overview` |

### Runs (7 tools)

Agent-run protocol lifecycle: report, track, evaluate, and compare agent runs.

| Tool | Description | Endpoint |
|---|---|---|
| `mc_list_runs` | List agent runs with optional filtering (agent_id, status, since, limit) | `GET /api/v1/runs` |
| `mc_get_run` | Get a single run (steps, cost, provenance, eval) | `GET /api/v1/runs/{run_id}` |
| `mc_create_run` | Report a new agent run | `POST /api/v1/runs` |
| `mc_update_run` | Update a run (status, outcome, cost, error) | `PATCH /api/v1/runs/{run_id}` |
| `mc_run_provenance` | Get run provenance (hash chain, model version, config hash) | `GET /api/v1/runs/{run_id}/provenance` |
| `mc_attach_eval` | Attach an evaluation result (pass/fail, score) to a run | `PUT /api/v1/runs/{run_id}/eval` |
| `mc_eval_leaderboard` | Eval leaderboard -- agents ranked by avg score, pass rate, and cost | `GET /api/v1/evals/leaderboard` |

Run statuses: `pending`, `running`, `completed`, `failed`, `cancelled`, `timeout`. Triggers for create: `manual`, `cron`, `webhook`, `agent`, `pipeline`, `queue`. Outcomes for update: `success`, `failed`, `partial`, `abandoned`. Eval requires `run_id`, `pass` (boolean), `score` (0-100), optional `task_type` and `detail`.

## Architecture

```
Claude Code / Agent Client
        |
        | JSON-RPC 2.0 over stdin/stdout
        v
  mc-mcp-server.cjs       <-- MCP Server (stdio transport)
        |                    - Zero deps, built-in Node.js only
        | HTTP (fetch)       - 30s timeout per request
        v                    - Auth via x-api-key or Cookie
  Mission Control REST API  <-- Next.js App Router
        |                    - 101+ API routes
        | SQLite
        v
  mission-control.db
```

### MCP Audit System

Beyond the MCP server itself, Mission Control includes a comprehensive **MCP audit subsystem** (`src/lib/mcp-audit.ts`) that logs every tool call with:

- Agent name, tool name, MCP server
- Success/failure status and duration
- Error details
- Ed25519 signed receipts for tamper-evident audit trails
- Per-agent statistics with tool-level breakdowns

Audit data is used for:
- Security dashboards with real-time posture scoring (0-100)
- Injection attempt tracking
- Component evals (p50/p95/p99 tool latency)
- Per-agent trust scores

Key API routes:
- `POST /api/mcp-audit` -- log an MCP call
- `GET /api/mcp-audit/stats` -- get MCP call statistics
- `GET /api/mcp-audit/verify` -- verify cryptographic integrity of audit records

### Security Features

- **Injection Guard** (`src/lib/injection-guard.ts`): scan for prompt injection, command injection, data exfiltration, and obfuscated content. Used by MCP audit and skill scanner.
- **Receipt Signing**: each MCP audit record can be Ed25519-signed at write time for tamper evidence.
- **Hook Profiles**: configurable security strictness (`minimal`/`standard`/`strict`), each enabling different combinations of secret scanning, MCP auditing, and rate limiting.

### Comparison: MCP vs CLI vs REST API

| Interface | Recommended For | Notes |
|---|---|---|
| **MCP Server** | Autonomous Claude Code agents | 49 tools, best for agent-to-agent control |
| **CLI** (`mc-cli.cjs`) | Shell scripts, CI/CD, human operators | JSON mode, profile persistence, SSE events |
| **REST API** | Custom integrations, programmatic access | 101 routes, OpenAPI spec at `/openapi.json` |

All three interfaces authenticate identically (API key or session cookie) and talk to the same backend -- they are three views of the same control plane.

## Test Coverage

Playwright-based E2E tests in `tests/mcp-server.spec.ts` verify:
- Initialization handshake
- Tool discovery via `tools/list`
- Tool invocation via `tools/call`
- Error handling for unknown tools
- Integration with live Mission Control API
