# n8n — Instance AI Architecture

**Source:** `sources/n8n/packages/@n8n/instance-ai/`
**Key docs:** `docs/architecture.md`, `docs/tools.md`, `docs/streaming-protocol.md`, `docs/memory.md`, `docs/sandboxing.md`, `docs/filesystem-access.md`, `docs/configuration.md`

## What it is

Instance AI is an **autonomous agent embedded in every n8n instance**. It provides a natural language interface to workflows, executions, credentials, and nodes — with the goal that most users never need to interact with workflows directly. **Framework-agnostic core** with no hard dependency on n8n internals (uses service interfaces).

The system follows the **deep agent architecture** — an orchestrator with explicit planning, dynamic sub-agent delegation, observational memory, and structured prompts. The LLM controls the execution loop; the architecture provides the primitives. **LLM-agnostic** — works with any capable model.

## System Architecture

```
Frontend (Vue 3 Chat) ──POST──→ Backend Express ──→ InstanceAiService
     ↑                                                        │
     │ SSE                                      ┌─────────────┤
     │                                          ▼             ▼
     │                                    Agent Factory    LocalGateway
     │                                          │             │
     │                                          ▼          (filesystem
     │                                    Orchestrator    SSE daemon)
     │                                     │         │
     │                                     ▼         ▼
     │                                Plan Tool  Delegate Tool
     │                                  │            │
     │                                  ▼            ▼
     │                             Planned Tasks  Sub-Agent A
     │                               │             │
     │                               ▼             ▼
     │                           Background    Sub-Agent B
     │                           Tasks
     │
     └── Event Bus (SSE) ───── All agents publish here ──→ Thread Storage
```

### Package Distribution

| Package | Role |
|---------|------|
| `@n8n/instance-ai` | Agent core — framework-agnostic, defines service interfaces |
| `packages/cli/src/modules/instance-ai/` | Backend integration — controllers, adapters, services, TypeORM entities |
| `packages/@n8n/api-types` | Shared types — event schemas, agent types, DTOs, reducer |
| `packages/frontend/.../instanceAi/` | Frontend — chat UI, SSE client, agent tree, store |

## Deep Agent Architecture

The system implements four pillars:

### 1. Explicit Planning

- **Orchestrator** loads `planning` skill to externalize execution strategy
- Uses `create-tasks` tool to persist a dependency-aware task graph
- Tasks have kinds: `build-workflow`, `delegate`, `checkpoint`
- Plan shown to user for approval before execution
- Standalone data-table work uses `data-table-manager` skill directly (no plan)
- Clear single-workflow builds go directly to the builder

### 2. Dynamic Sub-Agent Composition

- The `delegate` tool spawns focused sub-agents on the fly
- Orchestrator specifies: **role** (free-form), **instructions**, **tools** (subset)
- No fixed taxonomy of sub-agent types — fully dynamic
- Sub-agents are **stateless** (context via briefing only)
- Sub-agents cannot spawn their own sub-agents (cascading prevention)
- Low `maxSteps` default (10)
- Sub-agents publish directly to event bus

### 3. Observational Memory

- **Tier 1**: Storage backend (PostgreSQL or LibSQL/SQLite, auto-selected)
- **Tier 2**: Recent messages — sliding window (default 20, configurable)
- **Tier 3**: Observational memory — two background agents for compression:
  - **Observer**: When messages exceed ~30K tokens, compresses into dense observations
  - **Reflector**: When observations exceed ~40K tokens, condenses into higher-level patterns
- 5–40x compression for tool-heavy workloads
- Sub-agents are stateless — context is passed via briefing only
- Memory is thread-scoped. Cross-user isolation enforced.

### 4. Structured System Prompt

- Orchestrator's system prompt covers delegation, planning, loop behavior, and tool usage
- Sub-agents get focused, task-specific prompts written by the orchestrator
- Dynamic context-aware prompt based on instance configuration

## Tools (50+)

### Orchestration Tools (exclusive to orchestrator)

| Tool | Purpose |
|------|---------|
| `create-tasks` | Persist dependency-aware plan, user approval, then schedule execution |
| `delegate` | Spawn a dynamic sub-agent with tool subset |
| `update-tasks` | Update visible task checklist |
| `cancel-background-task` | Cancel a running background task |
| `correct-background-task` | Send course correction to a running task |
| `verify-built-workflow` | Run a built workflow with pin data (simulates destructive/user-action nodes) |
| `report-verification-verdict` | Feed results into the workflow loop state machine |
| `apply-workflow-credentials` | Atomically apply real credentials to mocked nodes |

### Workflow Tools (10–14)

| Tool | Purpose |
|------|---------|
| `list-workflows` | List accessible workflows |
| `get-workflow` | Full workflow definition |
| `get-workflow-as-code` | TypeScript SDK code for existing workflow |
| `build-workflow` | Compile, validate, save workspace source file |
| `delete-workflow` | Archive (soft delete) |
| `unarchive-workflow` | Restore archived |
| `setup-workflow` | Open UI for per-node credential/parameter setup (HITL) |
| `publish-workflow` | Publish to production |
| `unpublish-workflow` | Stop production execution |
| `list-workflow-versions` | Version history (conditional — license) |
| `get-workflow-version` | Full version details (conditional — license) |
| `restore-workflow-version` | Restore to previous version (conditional — license, HITL) |
| `update-workflow-version` | Update version metadata (conditional — `feat:namedVersions`) |

### Execution Tools (6)

| Tool | Purpose |
|------|---------|
| `list-executions` | List recent executions |
| `run-workflow` | Execute and wait (with timeout) |
| `get-execution` | Get status without blocking |
| `debug-execution` | Analyze failed execution with structured diagnostics |
| `get-node-output` | Get output data from a specific node |
| `stop-execution` | Cancel a running execution |

### Credential Tools (6)

| Tool | Purpose |
|------|---------|
| `list-credentials` | List credentials (no secrets) |
| `get-credential` | Get metadata (no secrets) |
| `delete-credential` | Permanently delete (HITL) |
| `search-credential-types` | Search available credential types |
| `setup-credentials` | Open credential picker UI (secrets never exposed to LLM) |
| `test-credential` | Test credential validity |

### Node Discovery Tools (6)

| Tool | Purpose |
|------|---------|
| `list-nodes` | List available node types |
| `get-node-description` | Detailed node description with properties |
| `get-node-type-definition` | Full JSON schema |
| `search-nodes` | Relevance-ranked search with `@builderHint` annotations |
| `get-suggested-nodes` | Curated suggestions for common use cases |
| `explore-node-resources` | Explore dynamic resources (listSearch/loadOptions) |

### Data Table Tools (11)

Full CRUD suite: `list-data-tables`, `create-data-table`, `delete-data-table`, `get-data-table-schema`, `add-data-table-column`, `delete-data-table-column`, `rename-data-table-column`, `query-data-table-rows`, `insert-data-table-rows`, `update-data-table-rows`, `delete-data-table-rows`.

### Workspace Tools (up to 8, conditional)

| Tool | Purpose |
|------|---------|
| `list-projects` | List projects |
| `tag-workflow` | Apply tags |
| `list-tags` | List available tags |
| `cleanup-test-executions` | Remove test execution data |
| `list-folders` | List folders (conditional) |
| `create-folder` | Create folder (conditional) |
| `delete-folder` | Delete folder (conditional) |
| `move-workflow-to-folder` | Move workflow to folder (conditional) |

### Web Research Tools (2)

| Tool | Purpose |
|------|---------|
| `web-search` | Web search (Brave > SearXNG > disabled) — LRU cache 100 entries, 15 min TTL |
| `fetch-url` | Fetch web page as markdown (Readability + Turndown + GFM, SSRF protected) |

### Filesystem Tools (dynamic, conditional)

Dynamically created from connected Computer Use gateway MCP server.
See `docs/filesystem-access.md`.

### Other

| Tool | Purpose |
|------|---------|
| `ask-user` | Suspend and request user input (single/multi-select or text) |

### Tool Distribution Matrix

| Category | Orchestrator | Sub-Agents | Background Agents |
|----------|:---:|:---:|:---:|
| Orchestration tools | ✅ | ❌ | ❌ |
| Workflow tools | ✅ | ✅ | ✅ (builder) |
| Execution tools | ✅ | ✅ | ❌ |
| Credential tools | ✅ | ✅ | ✅ (setup only) |
| Node discovery | ✅ | ✅ | ✅ (builder) |
| Data table tools | ✅ | ✅ | ❌ |
| Workspace tools | ✅ | ✅ | ❌ |
| Filesystem tools | ✅ | ✅ | ❌ |
| Web research | ✅ | ✅ | ❌ |
| MCP tools | ✅ | ❌ | ❌ |
| Computer Use browser | ✅ | ❌ | ❌ |

### Tool Search (Deferred Tools)

Tools are stratified into two tiers:
- **Core tools** (always-loaded): `create-tasks`, `delegate`, `ask-user`, `web-search`, `fetch-url`
- **Deferred tools** (behind ToolSearchProcessor): All other domain tools — discovered on-demand via `search_tools`, activated via `load_tool`

Follows Anthropic's guidance on tool search for large tool sets.

## Event System & Streaming

### Transport

- **POST `/instance-ai/chat/:threadId`** → returns `{ runId }`. One active run per thread (409 if busy).
- **SSE `/instance-ai/events/:threadId`** → subscribes to all agent events. Reconnect via `Last-Event-ID` header or `?lastEventId` query.
- `X-Accel-Buffering: no` for nginx compat.

### Event Schema

```typescript
{ type: string; runId: string; agentId: string; payload?: object }
```

### Event Types

| Type | Purpose |
|------|---------|
| `run-start` | First event — orchestrator started |
| `text-delta` | Streaming text output (progressive rendering) |
| `tool-call` | Tool invocation (which tool, what input) |
| `tool-result` | Tool completion (result summary) |
| `sub-agent-start` | Sub-agent spawned |
| `sub-agent-text-delta` | Sub-agent streaming output |
| `sub-agent-tool-call` | Sub-agent tool invocation |
| `sub-agent-tool-result` | Sub-agent tool completion |
| `sub-agent-complete` | Sub-agent finished |
| `suspension` | HITL suspension (awaiting approval) |
| `tasks-update` | Task checklist update |
| `run-finish` | Final event — completion status + summary |
| `run-error` | Run terminated with error |

### Stream Execution

```
streamAgentRun() → agent.stream() → executeResumableStream()
  ├─ chunk → mapAgentChunkToEvent() → eventBus.publish()
  ├─ suspension → wait for confirmation → agent.resumeStream() → loop
  └─ return StreamRunResult
```

Two control modes:
- **Manual**: Returns suspension to caller (used by orchestrator's main run)
- **Auto**: Waits for confirmation and resumes automatically (background sub-agents)

### Background Task Manager

- Concurrent tasks: default 5 per thread
- Correction queueing: `correct-background-task` mid-flight steering
- Three cancel surfaces: stop button, "stop that" message, or `cancelRun`
- Running task context injected into orchestrator messages

## Planned Tasks & Workflow Loop

### Task Kinds

| Kind | Executor | Use |
|------|----------|-----|
| `build-workflow` | Builder agent | Build/update workflows |
| `delegate` | Custom sub-agent | Any focused subtask |
| `checkpoint` | Orchestrator follow-up | Semantic/cross-workflow validation |

### Workflow Loop State Machine

```
build → submit → verify → (success | needs_patch | needs_rebuild | failed_terminal)
```

- Simulation: Destructive/user-action nodes are simulated (output pinned, never actually executes)
- `report-verification-verdict` feeds results into state machine
- Same failure signature twice → terminal state (prevents infinite loops)

## MCP Integration

- **`McpClientManager`** (`mcp/mcp-client-manager.ts`): Owns all external MCP connections
- Schema sanitization for Anthropic compat (ZodNull → optional, discriminated unions → flattened)
- Name-checking against reserved domain tool names (prevents shadowing)
- Cached by config hash — clean disconnect on shutdown
- Supports SSE/stdio transport
- MCP tools are orchestrator-only (not available to sub-agents)

## Sandbox

Three-layer abstraction:
1. **Agent Layer**: LLM + Agent Runtime (`@n8n/agents`)
2. **Workspace Layer**: Filesystem interface + Sandbox interface
3. **Providers**: Daytona (remote container) or n8n Sandbox Service (remote container)

The agent never talks to providers directly — only sees the Workspace.

## Security Model

| Concern | Mechanism |
|---------|-----------|
| Permission scoping | RBAC via adapter (`userHasScopes()`) |
| Credential safety | Tool outputs never include decrypted secrets; setup via UI |
| Destructive operations | HITL confirmation for delete, publish, restore |
| External URLs | Per-domain user approval via DomainAccessTracker |
| Memory isolation | Thread-scoped, cross-user enforced |
| Sub-agent containment | Cannot spawn sub-agents, no MCP tools, low maxSteps |
| MCP tools | Name-checked against reserved names, schema sanitized |
| Sandbox isolation | Container isolation, path-traversal protection, shell quoting |
| Filesystem safety | Read-only, 512KB cap, binary detection, exclusions, symlink escape protection |
| Web research | SSRF protection (private IPs, loopback, non-HTTP), post-redirect check |
| Module gating | Disabled by default unless `N8N_INSTANCE_AI_MODEL` is set |

## Key Design Decisions

1. **Clean interface boundary**: `@n8n/instance-ai` defines interfaces, not implementations. Backend adapter bridges to real n8n services.
2. **Agent created per request**: Fresh orchestrator per `sendMessage` call. MCP config and user context are request-scoped.
3. **Pub/Sub streaming**: Event bus decouples agent execution from event delivery. All events persist regardless of transport.
4. **Module system**: Can be disabled via `N8N_DISABLED_MODULES=instance-ai`. Only runs on `main` instance type (not workers).

## Related

- n8n Architecture: [[n8n-architecture]]
- n8n MCP: [[n8n-mcp]]
- n8n API: [[n8n-api]]
- Wiki entry: [[n8n]]
