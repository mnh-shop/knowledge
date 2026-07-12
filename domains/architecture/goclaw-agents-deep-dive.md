---
name: goclaw-agents-deep-dive
description: "GoClaw agent architecture — how agents work, pipeline internals, context files, agent types, and lifecycle"
tags: [goclaw, architecture, agent, agent-gateway]
source: sources/goclaw/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# GoClaw Agents Deep Dive
**Source:** `sources/goclaw/`

GoClaw agents are the core abstraction of the platform — each agent has an identity, model configuration, tool sets, permission scopes, and a file-based personality defined through Markdown context files. Every agent interaction runs through the same 8-stage pluggable pipeline, with stages defined in `internal/pipeline/` and the agent loop in `internal/agent/`.

This document covers how agents work internally, how they are defined, and their lifecycle. See [[goclaw-architecture]] for the broader system architecture.

## How Agents Work

### The 8-Stage Pipeline (v3)

Every agent run — whether from a chat message, a cron job, a subagent spawn, or a WebSocket RPC call — executes through an 8-stage pluggable pipeline (`internal/pipeline/pipeline.go`). The pipeline is fully stateless: all mutable state lives in `RunState`, passed by pointer through each stage.

```
Setup (runs once, before the iteration loop):
  ContextStage — inject agent/user/workspace context, resolve per-user files,
                 compute token overhead for tools, set EffectiveContextWindow

Iteration loop (up to DefaultMaxIterations=30 × per turn):
  PruneStage    → 2-phase: soft trim (≥30% window) then hard clear (≥50% window)
                  triggers memory flush before compaction
  ThinkStage    → build system prompt from 15+ sections, filter tools by policy,
                  call LLM, emit streaming deltas
  ToolStage     → execute tool calls (parallel goroutines for read-only tools,
                  sequential for mutating tools); preflight checks authorization
  ObserveStage  → drain InjectCh for injected messages, process tool results,
                  append to message buffer, accumulate assistant media
  CheckpointStage → track iteration count, check loop exit conditions
                  (max iterations hit? BreakLoop signal? tool error?)

Finalize (runs once, survives cancellation):
  FinalizeStage → 7-step output sanitization (config leak detection for
                  predefined agents, credential scrubbing), flush messages,
                  update session metadata, process media attachments
```

The pipeline is assembled in `NewPipeline()`:

```go
stages := []Stage{
    NewContextStage(d),
    NewPruneStage(d, memFlush),
    NewThinkStage(d),
    NewToolStage(d),
    NewObserveStage(d),
    NewCheckpointStage(d),
    NewFinalizeStage(d),
}
```

Key behavior: `BreakLoop` from `ThinkStage` (no tool calls needed) causes remaining stages in the iteration to complete (including `ObserveStage`), then exits the loop to `FinalizeStage`. This ensures responses are always observed and finalized.

#### ContextStage

Runs once per turn in the setup phase. Responsibilities:

- Call `BuildFilteredTools()` to enumerate available tools and store them in `state.Think.Tools`
- Compute tool token overhead via `ModelRegistry.ToolOverhead()` — tool definitions consume context budget
- Resolve `EffectiveContextWindow` from agent config or model registry
- Inject agent identity, user context, and workspace paths into `RunState`

Source: `internal/pipeline/context_stage.go` (tested in `context_stage_overhead_test.go`, `context_stage_integration_test.go`)

#### PruneStage

Runs every iteration before `ThinkStage`. Two-phase context pruning:

1. **Soft trim**: Remove eligible old tool-result messages when history exceeds 30% of `EffectiveContextWindow` (`SoftTrimRatio`). Eligible means tool calls older than `keepLastAssistants` (default 3).
2. **Hard clear**: When history exceeds 50% (`HardClearRatio`), clear all eligible tool-result messages, not just the oldest.

Triggers memory flush before compaction (invokes `MemoryFlushStage` inline, not registered as a separate pipeline stage). `CheckPendingAssistant` preserves in-flight `tool_calls` messages from the previous `ThinkStage` — critical regression guard for mid-loop compaction tool-pairing bugs (`compaction_pending_preservation_test.go`).

Source: `internal/pipeline/prune_stage.go`

#### ThinkStage

The core LLM invocation stage per iteration:

1. Build the system prompt from `BuildSystemPrompt()` (15+ sections — see [System Prompt Assembly](#system-prompt-assembly))
2. Filter available tools via `FilterTools()` (policy engine, credential gating, bootstrap mode restrictions)
3. Call the LLM provider (streaming to WebSocket clients via event push)
4. Parse the response — either `tool_calls` (continue to `ToolStage`) or text content (set `BreakLoop` flag)
5. Handle emergency compaction: if the response exceeds context window, trigger compaction and retry
6. Handle empty/invalid args: `write_file` with empty args is treated as truncated (retry), `datetime` empty args is a legitimate heartbeat pattern (no retry)

Source: `internal/pipeline/think_stage.go`, `internal/agent/systemprompt.go`

#### ToolStage

Executes tool calls produced by `ThinkStage`. Concurrency model:

- **Parallel execution** (`executeParallel`): All read-only tools run concurrently via goroutines. Uses erringroup for cancellation.
- **Sequential execution** (per-tool sequential): Mutating tools (write_file, exec, etc.) run one at a time.
- If any tool call is blocked by policy, `checkExitConditions` is still called — ensures the agent gets a chance to respond.
- Preflight phase: checks each tool call against `PolicyEngine` (allow/deny lists, credential gating, shell deny groups). Blocked calls return a `blocked_by_policy` message instead of executing.
- Batch budget check: if batch exceeds `MaxToolCalls` (default 25), excess calls are skipped.

Source: `internal/pipeline/tool_stage.go`

#### ObserveStage

Runs after `ToolStage`. Drains `InjectCh` (injected messages from hooks or subagent relay), processes tool results, accumulates assistant images into `state.Observe.AssistantImages` for `FinalizeStage` to upload. Handles silent tool completion — when all tool results are in but the LLM hasn't produced visible text, it still sets `Continue` so the loop can produce a meta-response.

Source: `internal/pipeline/observe_stage.go`

#### CheckpointStage

Tracks iteration state and decides whether to continue or break:

- Checks `state.Think.LLMResponse`: if `BreakLoop` is set (text-only response, no tool calls needed), signals exit
- Counts iterations against `MaxToolIterations` (default 30, configurable)
- Checks for error conditions that should abort the loop

Source: `internal/pipeline/checkpoint_stage.go`

#### FinalizeStage

Runs once unconditionally after the iteration loop exits (survives cancellation). Seven-step output sanitization:

1. Config leak detection (predefined agents only — `StripConfigLeak` in `internal/agent/sanitize.go`)
2. Credential scrubbing (strip API keys, tokens from output)
3. Message flush to database
4. Session metadata update (token count, compaction count, model used)
5. Process accumulated media (upload images from `ObserveStage.AssistantImages`)
6. Emit final streaming event to WebSocket clients
7. Trigger post-run hooks (`PostToolUse`, `Stop`)

Source: `internal/pipeline/finalize_stage.go`

### Agent Types

GoClaw supports two agent types, defined in `internal/store/agent_store.go`:

| Type | Constant | Behavior |
|------|----------|----------|
| **Open** | `AgentTypeOpen = "open"` | Each user gets their own complete copy of all context files (AGENTS.md, SOUL.md, IDENTITY.md, CAPABILITIES.md, TOOLS.md). Users can fully customize the agent's personality through conversation. Seeded on first chat. Best for **personal assistants**. |
| **Predefined** | `AgentTypePredefined = "predefined"` | Fixed shared personality (SOUL.md, IDENTITY.md, AGENTS.md) defined at the agent level — no user can change these through chat. Per-user only gets USER.md + BOOTSTRAP.md. Agent-level files apply to every user of that agent. Best for **team bots, customer support, fixed-role agents**. |

The agent type affects:
- **Context file scoping**: Open agents have per-user context files; predefined agents share agent-level files except USER.md.
- **Bootstrap behavior**: Open agents get slim bootstrap mode (only `write_file` available); predefined agents get full capabilities with soft onboarding copy.
- **Self-evolution**: Only predefined agents can update SOUL.md via chat (when `self_evolve` is enabled).
- **Config leak detection**: Predefined agents have `StripConfigLeak` applied in `FinalizeStage` to prevent them from revealing their internal configuration.
- **Tool filtering during bootstrap**: Open agents restrict API tools to `write_file` only during first-run; predefined agents do not.

### Agent Statuses

Defined in `internal/store/agent_store.go`:

| Status | Constant | Meaning |
|--------|----------|---------|
| `active` | `AgentStatusActive` | Agent is live and accepting messages |
| `inactive` | `AgentStatusInactive` | Agent is disabled, won't respond to messages |
| `summoning` | `AgentStatusSummoning` | Agent is being created/spawned (transient) |
| `summon_failed` | `AgentStatusSummonFailed` | Agent creation/spawn failed |

Status transitions from `summoning` to `summon_failed` on error (handled in both `store/pg/agents.go` and `store/sqlitestore/agents.go`).

## How Agents Are Defined

### Context Files (7 editable + 1 virtual + 3 runtime-generated)

Context files form the agent's personality, knowledge, and operating instructions. They are stored as rows in `agent_context_files` (agent-level) and `user_context_files` (per-user) tables, defined in `internal/bootstrap/files.go`.

**Editable context files:**

| File | Purpose | Scope (Open) | Scope (Predefined) |
|------|---------|-------------|-------------------|
| `AGENTS.md` | Operating instructions, memory rules, behavior policies | Per-user | Agent-level |
| `SOUL.md` | Personality, tone, voice, boundaries, core values | Per-user | Agent-level |
| `CAPABILITIES.md` | Domain knowledge, expertise areas, skill descriptions | Per-user | Agent-level |
| `IDENTITY.md` | Name, emoji, creature type, vibe, greeting style | Per-user | Agent-level |
| `TOOLS.md` | Local tool notes, usage guidance, workspace-specific tools | Per-user | Agent-level |
| `USER.md` | About the human user — interests, preferences, context | Per-user | Per-user |
| `USER_PREDEFINED.md` | User-handling rules for predefined agents (communication style, baseline language) | N/A | Agent-level |
| `BOOTSTRAP.md` | First-run ritual questionnaire (deleted/cleared on completion) | Per-user | Per-user |
| `MEMORY.md` | Long-term curated memory (can also be `memory.md` or `MEMORY.json`) | Per-user | Per-user |

**Runtime-generated virtual files** (built by the agent resolver, not stored on disk):

| File | Purpose | Generated By |
|------|---------|-------------|
| `DELEGATION.md` | Task context for spawned subagents — what to do, constraints, return format | `internal/agent/resolver.go` (via `agent_links`) |
| `TEAM.md` | Team orchestration instructions — member roster, task board rules, coordination | `internal/agent/resolver_helpers.go` `buildTeamMD()` |
| `AVAILABILITY.md` | Member status for teams — who's online, busy, or available for delegation | `internal/agent/resolver.go` |

These virtual files are injected into the system prompt when the agent is part of a team or has delegation links. They are also protected from filesystem read/write — the `filesystem.go` tool intercepts them with a message like "TEAM.md is already loaded in your system prompt."

**Additional system files:**
- `AGENTS_CORE.md` — Core instructions used in minimal mode (heartbeat sessions)
- `AGENTS_TASK.md` — Task-specific instructions used in task mode
- `HEARTBEAT.md` — Periodic monitoring configuration (heartbeat sessions)

All file name constants in `internal/bootstrap/files.go`:

```go
AgentsFile         = "AGENTS.md"
SoulFile           = "SOUL.md"
ToolsFile          = "TOOLS.md"
IdentityFile       = "IDENTITY.md"
UserFile           = "USER.md"
UserPredefinedFile = "USER_PREDEFINED.md"
BootstrapFile      = "BOOTSTRAP.md"
CapabilitiesFile   = "CAPABILITIES.md"
AgentsCoreFile     = "AGENTS_CORE.md"
AgentsTaskFile     = "AGENTS_TASK.md"
DelegationFile     = "DELEGATION.md"
TeamFile           = "TEAM.md"
AvailabilityFile   = "AVAILABILITY.md"
HeartbeatFile      = "HEARTBEAT.md"
MemoryFile         = "MEMORY.md"
MemoryAltFile      = "memory.md"
MemoryJSONFile     = "MEMORY.json"
```

### File Loading Order

The standard file loading order is defined by `standardFiles` in `internal/bootstrap/files.go`:

1. `AGENTS.md` → 2. `SOUL.md` → 3. `TOOLS.md` → 4. `IDENTITY.md` → 5. `USER.md` → 6. `BOOTSTRAP.md` → 7. `CAPABILITIES.md` → 8. `MEMORY.md` (or `memory.md`, then `MEMORY.json`)

For system prompt injection, the order is more nuanced (handled in `internal/agent/systemprompt_sections.go`). SOUL.md and IDENTITY.md are injected **twice** — once in the primacy zone (early, after identity) and again in the recency zone (late, before tooling) — to prevent persona drift during long conversations.

**Prompt mode filtering:**
Based on the session type, context files are filtered by `ModeAllowlist()`:

| Mode | Files Included | Used For |
|------|---------------|----------|
| `full` | All files (nil filter = pass-through) | Main agent sessions |
| `task` | AGENTS_TASK.md, TOOLS.md, CAPABILITIES.md, SOUL.md, IDENTITY.md | Enterprise automation |
| `minimal` | AGENTS_CORE.md, CAPABILITIES.md | Subagent/cron/heartbeat |
| `none` | TOOLS.md only | Identity-only sessions |

Mode resolution is 3-layer: runtime override > auto-detect (heartbeat→minimal, subagent/cron→task) > config > default (full).

### System Prompt Assembly

The system prompt is built by `BuildSystemPrompt()` in `internal/agent/systemprompt.go`. It constructs 15+ sections in order, with mode-based gating for task/minimal/none modes:

1. **Identity** — Channel-aware context (channel name, chat type, reply target)
2. **First-run bootstrap** — BOOTSTRAP.md instructions (only when present)
3. **Persona** — SOUL.md + IDENTITY.md content (primacy zone)
4. **Identity anchoring** — SOUL.md echo (predefined agents, full mode only)
5. **Self-evolution** — SOUL.md update instructions (predefined agents with self_evolve)
6. **Provider-specific instructions** — From `PromptContributor` interface
7. **Memory instructions** — How to use memory_search/memory_get
8. **Knowledge Graph** — KG search instructions (when available)
9. **Vault** — Knowledge Vault search instructions (when available)
10. **Skills** — Skill usage and management instructions
11. **MCP** — MCP tool search instructions
12. **Project Context** — All context files (AGENTS.md, USER.md, BOOTSTRAP.md, CAPABILITIES.md, TOOLS.md, MEMORY.md)
13. **Sandbox** — Docker sandbox configuration (when enabled)
14. **Tooling** — Available tools with one-line descriptions (`coreToolSummaries` map)
15. **Credentialed CLI** — Secure CLI context from `tools.GenerateCredentialContext()`
16. **Delegation targets** — Linked agents available via `delegate` tool
17. **Team context** — TEAM.md, member roster, task board rules
18. **Persona reminder** — SOUL.md + IDENTITY.md (recency zone, prevents drift)
19. **Cache boundary marker** — `<!-- GOCLAW_CACHE_BOUNDARY -->` for Anthropic prompt caching
20. **Provider contribution** — Dynamic sections from provider
21. **Extended thinking** — `<antThinking>` support for Anthropic
22. **Extra prompt** — Subagent context, injected messages
23. **Channel closing** — Channel-specific closing instructions

The prompt cache boundary marker (`CacheBoundaryMarker`) separates stable (agent config, persona) from dynamic (per-turn) content. The Anthropic provider splits the system message into two blocks at this boundary — the stable block gets `cache_control`, the dynamic block doesn't.

**Truncation**: Context files have per-file limits (`BootstrapMaxChars` default 20K) and a total budget (`BootstrapTotalMaxChars` default 24K). When truncation is needed, 70% is kept from the file start and 20% from the end.

### Agent Configuration

Agents are configured through either the config file (`config.json`, `internal/config/config.go`) or the database.

**Config file structure:**

```json5
{
  "agents": {
    "defaults": {
      "provider": "openrouter",
      "model": "anthropic/claude-sonnet-4-5",
      "max_tool_iterations": 30,
      "temperature": 0.7,
      "agent_type": "open",          // "open" (default) or "predefined"
      "context_window": 200000,
      "max_tool_calls": 25,
      "workspace": "./workspace",
      "restrict_to_workspace": true,
      "subagents": {
        "maxConcurrent": 8,
        "maxSpawnDepth": 1,
        "maxChildrenPerAgent": 5
      },
      "memory": { /* memory config */ },
      "compaction": { /* compaction config */ },
      "contextPruning": { /* pruning config */ }
    },
    "list": {
      "code-helper": {
        "displayName": "Code Helper",
        "model": "claude-opus-4-6",
        "temperature": 0.3,
        "agent_type": "open",
        "tools": {
          "deny": ["web_search", "browser"]
        },
        "identity": {
          "name": "Code Helper",
          "emoji": "💻"
        }
      },
      "support-bot": {
        "displayName": "Customer Support",
        "model": "gpt-4o",
        "agent_type": "predefined",
        "temperature": 0.5,
        "workspace": "./workspace/support"
      }
    }
  }
}
```

The `AgentDefaults` struct (`internal/config/config.go`) provides defaults inherited by all agents. `AgentSpec` provides per-agent overrides — zero values mean "inherit from defaults."

**Agent-level overridable fields** (stored in the database `agents` table):
- `provider`, `model`, `temperature`, `max_tokens`
- `max_tool_iterations`, `context_window`, `max_tool_calls`
- `agent_type` (open/predefined), `workspace`, `restrict_to_workspace`
- `tools_config`, `sandbox_config`, `subagents_config`, `memory_config`
- `compaction_config`, `context_pruning`, `other_config` (extensibility bag)
- `self_evolve` (boolean, column-migrated from `other_config`)

### Agent Access Control

When a user tries to access an agent, the `CanAccess()` method in `store/pg/agents.go` (and `store/sqlitestore/agents_access.go`) evaluates a 4-step chain:

1. **Agent exists?** → If not found (deleted or missing), return `false, "", error`
2. **Is default agent?** (`is_default = true`) → Allow access:
   - Owner gets role `"owner"`
   - Any other user gets role `"user"`
3. **Is owner?** (`owner_id == userID`) → Allow with role `"owner"` (admin role)
4. **Has share record?** (`agent_shares` table) → Allow with stored `role` (`"operator"` or `"viewer"`)
5. **Deny** → Return `false, "", nil` (no error, just no access)

This is called from the gateway method handlers before any operation, preventing cross-user access to agents they don't own or haven't been shared with. Shares are managed via `agent_shares` table with `role` column (operator/viewer).

### Agent Routing

The `bindings` configuration maps channels to specific agents:

```json5
{
  "bindings": [
    {
      "agentId": "support-bot",
      "match": {
        "channel": "telegram",
        "accountId": "bot12345",
        "peer": { "kind": "group", "id": "-1001234567890" }
      }
    },
    {
      "agentId": "code-helper",
      "match": { "channel": "discord", "guildId": "987654321" }
    }
  ]
}
```

Unbound conversations (no matching binding) go to the default agent (the agent marked `is_default = true` or the first agent in the config list). The `AgentBinding` struct supports matching by channel, account ID, guild ID, and specific peer (DM or group chat).

For Telegram specifically, per-group agent bindings are supported — different groups can be routed to different agents.

## Agent Lifecycle

```
Create → Configure → Summon → Chat → Edit/Iterate
```

### Creation

Agents can be created through:
- **Dashboard** (Web UI) — Create Agent form with name, provider, model, agent type
- **Config file** — Defined in `agents.list` and imported to database on startup
- **CLI** — `./goclaw agent create` commands
- **WebSocket RPC** — `agents.create` method

Creation flow:
1. Generate `agent_key` (human-readable slug) and `agent_uuid`
2. Set owner (creating user), tenant context
3. Seed default context files (AGENTS.md, SOUL.md, IDENTITY.md, CAPABILITIES.md, USER.md)
4. Set status to `active`

### Configuration

After creation, context files are seeded by `SeedUserFiles()` in `internal/bootstrap/seed_store.go`:

- **Open agents**: Seed full set — AGENTS.md, SOUL.md, TOOLS.md, IDENTITY.md, USER.md, BOOTSTRAP.md, CAPABILITIES.md, MEMORY.md. BOOTSTRAP.md is only seeded for brand-new workspaces.
- **Predefined agents**: Seed USER.md + BOOTSTRAP.md per-user (user-focused onboarding template). Agent-level files already exist. If wizard has written USER.md at agent level, prefer that content as seed.

Channel-provided contact info (name, username from Telegram/Discord) can pre-fill USER.md directly, skipping the interactive bootstrap.

### Summoning (First Message)

1. User sends first message to the agent
2. Agent must be in `active` status (set from `summoning`→`active` on creation)
3. If BOOTSTRAP.md exists and agent_type is "open": bootstrap mode engaged — only `write_file` tool available, slim system prompt
4. If BOOTSTRAP.md exists but agent_type is "predefined": soft onboarding — full capabilities, get-to-know tone
5. After bootstrap completion: BOOTSTRAP.md is deleted/cleared, full capabilities unlocked

### Chat (Ongoing)

Each conversation is a session. Sessions follow a state machine (`internal/agent/loop.go`):

1. Session resolved or created per user-agent pair
2. History loaded from database (compacted if needed)
3. Pipeline executed with session context
4. Tool calls executed, results observed
5. Messages flushed to database on finalize
6. Session metadata updated (token counts, model used, compaction count)

### Editing and Iteration

Agents can be refined over time:
- **Context files** can be edited via dashboard, CLI, or WebSocket (`agents.updateContextFile`)
- **Model/provider** can be changed without losing conversation history
- **Tools** can be allowed/denied per-agent via tool policy config
- **Identity** (name, emoji) can be updated — triggers IDENTITY.md field update via `UpdateIdentityField()` in `internal/bootstrap/identity_update.go`
- **Config hot-reload**: Changes to `config.json` are detected by `fsnotify` (300ms debounce) and applied without restart

### Self-Evolution

Predefined agents with `self_evolve = true` can update their own SOUL.md (style, tone, boundaries) through conversation. The self-evolution system (`internal/agent/loop.go`) uses a 3-stage guardrailed pipeline:

1. **Metrics collection** — Track tool usage patterns, retrieval patterns, interaction frequency
2. **Suggestion analysis** — LLM analyzes conversation history for SOUL.md adaptation opportunities
3. **Auto-adaptation** — Guardrail-protected apply of SOUL.md updates with rollback capability

Self-evolution is explicitly gated to predefined agents only (`agentType == store.AgentTypePredefined`). Open agents would have per-user SOUL.md updates, which is a different mechanism (direct user editing).

The agent's loop tracks `selfEvolve` flag and injects SOUL.md update instructions in the system prompt for predefined agents:

```go
// internal/agent/loop_context.go
if l.selfEvolve {
    ctx = store.WithSelfEvolve(ctx, true)
}
```

## Source Files

| File | Purpose |
|------|---------|
| `internal/pipeline/pipeline.go` | 8-stage pipeline orchestrator |
| `internal/pipeline/stage.go` | Stage interface (stateless, RunState-based) |
| `internal/pipeline/context_stage.go` | Context injection, tool overhead, context window |
| `internal/pipeline/prune_stage.go` | 2-phase context pruning, memory flush trigger |
| `internal/pipeline/think_stage.go` | System prompt build, LLM call, streaming |
| `internal/pipeline/tool_stage.go` | Tool execution (parallel/sequential), authorization |
| `internal/pipeline/observe_stage.go` | Tool result processing, image accumulation |
| `internal/pipeline/checkpoint_stage.go` | Iteration tracking, exit condition check |
| `internal/pipeline/finalize_stage.go` | Output sanitization, message flush, metadata update |
| `internal/agent/loop.go` | Agent execution loop, pipeline invocation |
| `internal/agent/systemprompt.go` | System prompt builder (15+ sections) |
| `internal/agent/systemprompt_sections.go` | Individual section builders |
| `internal/agent/resolver.go` | Agent resolver — context file loading, virtual files |
| `internal/agent/resolver_helpers.go` | TEAM.md builder, helper functions |
| `internal/agent/loop_context.go` | Loop context propagation |
| `internal/agent/loop_history.go` | Session history loading, bootstrap mode detection |
| `internal/agent/loop_tool_filter.go` | Tool filtering by policy and bootstrap mode |
| `internal/agent/loop_pipeline_callbacks.go` | Pipeline callbacks from loop |
| `internal/agent/sanitize.go` | Output sanitization, config leak detection |
| `internal/agent/preview_prompt.go` | Prompt preview for dashboard |
| `internal/bootstrap/files.go` | Context file constants, loading, mode filtering |
| `internal/bootstrap/seed_store.go` | Per-user context file seeding |
| `internal/bootstrap/backfill_capabilities.go` | CAPABILITIES.md backfill migration |
| `internal/bootstrap/identity_update.go` | IDENTITY.md field update helper |
| `internal/store/agent_store.go` | Agent data model, store interface |
| `internal/store/pg/agents.go` | PostgreSQL agent store (CanAccess, CRUD) |
| `internal/store/sqlitestore/agents.go` | SQLite agent store |
| `internal/store/sqlitestore/agents_access.go` | SQLite CanAccess, shares |
| `internal/config/config.go` | Config struct, AgentDefaults, AgentSpec |
| `internal/config/defaults.go` | Default agent constant values |

## Related

- [[goclaw]] — GoClaw wiki
- [[goclaw-architecture]] — Core architecture overview
- [[goclaw.codegraph-verify]] — Codegraph verification
- [[goclaw-api]] — REST/WS API reference
- [[openclaw-architecture]] — OpenClaw architecture
- [[hermes-agent]] — Hermes Agent (competing platform)
- [[mcp]] — Model Context Protocol
