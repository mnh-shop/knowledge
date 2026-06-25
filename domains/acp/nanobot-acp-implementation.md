---
name: nanobot-acp
description: "Nanobot agent communication and subagent system — worker agents, task decomposition"
source: sources/nanobot/
tags: [acp, agent-profile, ai-llm, documentation, event-bus, plugin-sdk]
---
# Nanobot Agent Communication & Subagent System

Source repository: `nanobot` (https://github.com/HKUDS/nanobot)
Primary file: `nanobot/agent/subagent.py`
Supporting files: `nanobot/agent/tools/spawn.py`, `nanobot/agent/tools/self.py`, `nanobot/bus/events.py`, `nanobot/bus/queue.py`

## Overview

Nanobot does **not** implement an ACP (Agent Communication Protocol) at this time. Instead, it has a built-in **subagent system** for agent-to-agent task delegation, and a **MessageBus** for in-process event passing. Agent-to-agent communication across separate nanobot instances is handled through the "Agent Social Network" concept, which uses skill installation rather than a formal protocol.

## Subagent System (`nanobot/agent/subagent.py`)

The subagent system allows the main agent to spawn child agents (subagents) to handle tasks concurrently, with results delivered back to the parent session.

### `SubagentStatus`
Dataclass tracking subagent state:
- `task_id`, `label`, `task_description` -- identity and purpose.
- `started_at` -- when the subagent was spawned.
- `phase` -- lifecycle phase: `"initializing"`, `"running"`, `"completed"`, `"failed"`.
- `iteration`, `tool_events`, `usage` -- execution metrics.
- `stop_reason`, `error` -- terminal state details.

### `SubagentManager`
Manages all subagent lifecycle:
- **`run_subagent(task, label, origin_channel, origin_chat_id, session_key, ...)`** -- spawns a new subagent task:
  1. Generates a unique `task_id` (8-char uuid prefix).
  2. Creates a `SubagentStatus` entry.
  3. Creates an `asyncio.Task` that runs the subagent loop.
  4. Tracks the task in `_running_tasks` and `_session_tasks`.
  5. Starts at `AgentDefaults().max_concurrent_subagents` (default: 3).

- **Subagent execution flow**:
  1. Builds a fresh `ToolRegistry` for the subagent (can limit tools via `ToolsConfig`).
  2. Constructs a system prompt via `_build_subagent_prompt()` -- includes time context, skills summary, workspace info.
  3. Creates initial messages: system prompt + user task.
  4. Calls `runner.run(AgentRunSpec(...))` with its own provider, model, and timeout.
  5. Result is rendered via template `subagent_announce.md` and delivered back as an `InboundMessage`.

- **`cancel_by_session(session_key)`** -- cancels all subagents for a given session.
- **`get_running_count()`**, **`get_running_count_by_session(session_key)`** -- status queries.
- **Limits**: `max_concurrent_subagents` (from `AgentDefaults`), `max_iterations` per subagent (configured via `ToolsConfig` or falls back to agent defaults).

### SpawnTool (`nanobot/agent/tools/spawn.py`)
The tool that agents call to create subagents:
- `SpawnTool.execute(label, task)` -- creates a subagent via `SubagentManager`.
- Input: `label` (display name for the subagent), `task` (instructions/goal for the subagent).
- Output: result announcement delivered to the parent session's chat.
- Subagent runs with access to a configurable subset of tools (filesystem, shell, web, etc.), controlled by `ToolsConfig`.

## Message Bus (`nanobot/bus/queue.py`)

The `MessageBus` provides async pub/sub for in-process communication:
- **`publish_inbound(msg: InboundMessage)`** -- push a message for the agent to process.
- **`consume_inbound()`** -- await the next inbound message.
- **`publish_outbound(msg: OutboundMessage)`** -- push a response for the channel.
- **`consume_outbound()`** -- await the next outbound message.

### Message Types (`nanobot/bus/events.py`)

**`InboundMessage`**:
- Fields: `channel`, `sender_id`, `chat_id`, `content`, `timestamp`, `media`, `metadata`, `session_key_override`.
- `metadata` can carry: `_runtime_control` for MCP reload triggers, `_progress`, and other system events.

**`OutboundMessage`**:
- Fields: `channel`, `chat_id`, `sender_id`, `content`, `media`, `reply_to`, `buttons`, `metadata`.
- `metadata` can carry `OUTBOUND_META_AGENT_UI` blobs for rich WebUI rendering.

## Runtime Event Bus (`nanobot/bus/runtime_events.py`)

A separate event system for internal runtime events:
- **`RuntimeEventBus`** -- publish/subscribe for typed runtime events.
- **Events**:
  - `SessionTurnStarted` -- when a session turn begins.
  - `TurnRunStatusChanged` -- status transitions for a turn run.
  - `TurnCompleted` -- turn completion with latency.
  - `GoalStateChanged` -- when session goal state changes.
  - `RuntimeModelChanged` -- when the active model changes.
- Supports both sync (`publish_nowait`) and async (`publish`) publication.

## Agent-to-Agent Communication (External)

### Agent Social Network (`docs/agent-social-network.md`)
Nanobot can join external agent platforms:
- **Moltbook** (`https://moltbook.com/`) -- send "Read https://moltbook.com/skill.md and follow the instructions to join Moltbook".
- **ClawdChat** (`https://clawdchat.ai/`) -- send "Read https://clawdchat.ai/skill.md and follow the instructions to join ClawdChat".
- These platforms use skill-based integration: the agent reads a skill markdown file and follows instructions to join the network.
- No formal ACP wire protocol is implemented for cross-instance communication.

## Agent Hook System (`nanobot/agent/hook.py`)

The `_SubagentHook` extends `AgentHook` to monitor subagent execution:
- `before_execute_tools(context)` -- logs tool call arguments to subagent status.
- `after_iteration(context)` -- updates iteration count and usage metrics.

## Key Files Reference

| File | Purpose |
|------|---------|
| `nanobot/agent/subagent.py` | SubagentManager, SubagentStatus, subagent lifecycle |
| `nanobot/agent/tools/spawn.py` | SpawnTool for subagent creation |
| `nanobot/agent/tools/self.py` | Self-tool for runtime introspection |
| `nanobot/agent/hook.py` | AgentHook base and subagent hook |
| `nanobot/bus/queue.py` | MessageBus pub/sub for in-process messaging |
| `nanobot/bus/events.py` | InboundMessage, OutboundMessage definitions |
| `nanobot/bus/runtime_events.py` | RuntimeEventBus for typed runtime events |
| `nanobot/agent/runner.py` | AgentRunner used by subagents for model interaction |
| `nanobot/agent/loop.py` | AgentLoop for main session orchestration |
| `nanobot/templates/agent/subagent_announce.md` | Template for subagent result announcements |
| `nanobot/templates/agent/subagent_system.md` | System prompt template for subagents |
| `nanobot/utils/subagent_channel_display.py` | Subagent message scrubbing for channel output |
| `docs/agent-social-network.md` | Documentation for joining external agent platforms |
| `tests/agent/tools/test_subagent_tools.py` | Subagent tool tests |
| `tests/agent/test_subagent_lifecycle.py` | Subagent lifecycle tests |
| `tests/agent/test_subagent.py` | General subagent tests |
