---
name: free-claude-code-acp
description: "ACP agent communication protocol implementation in free-claude-code"
source: sources/free-claude-code/
tags: [acp, cli, documentation, messaging]
---
# free-claude-code ACP Implementation

## Overview

The "free-claude-code" project does NOT implement the formal ACP (Agent Communication Protocol) specification. However, it does implement a practical agent orchestration layer that enables multi-agent conversation patterns through:

1. **Subagent/Task Tool Forwarding** -- the proxy passes through Claude Code's built-in `Agent` (subagent) tool, including its subagent_type and capabilities catalog.
2. **Managed Claude Code Session Pool** -- `ManagedClaudeSessionManager` maintains multiple parallel subprocess sessions for concurrent conversation processing.
3. **Messaging Platform Bridging** -- Discord and Telegram platforms serve as communication channels between users and Claude Code agents.
4. **Tree-Based Conversation State** -- `MessageTree` and `TreeQueueManager` manage multi-turn, branching conversation histories with parallel node execution.

## Subagent Tool Infrastructure

Claude Code's subagent/task tool is the primary mechanism for agent-to-agent communication. The proxy forwards this tool catalog to clients. Key integration points:

**Configuration: `config/settings.py`**
```
debug_subagent_stack: bool = Field(default=False)
```

**Event Parsing: `messaging/event_parser.py`**

The event parser processes Claude Code stream-json events including subagent metadata:
- `subagent_type` extracted from tool_use inputs
- Subagent tool calls and results tracked in transcript segments
- Session IDs linked to subagent context

**Transcript: `messaging/transcript.py`**

The file defines multiple segment types including `TextSegment` (line 58) and `SubagentSegment` (line 93):

```python
class SubagentSegment(Segment):
    """Represents a subagent invocation in conversation history."""
    description: str = ""
    tool_calls: list[ToolCallSegment] = []
    tools_used: dict[str, int] = {}
    current_tool: ToolCallSegment | None = None
```

The transcript buffer tracks:
- Subagent stack depth (`_subagent_stack` list of tool_use_ids)
- Open tools by index (`_open_tools_by_index` mapping)
- Subagent nesting via `_subagent_current()` and `_subagent_push()` / `_subagent_pop()`

**Smoke Tests: `smoke/lib/claude_cli_matrix.py`**
```python
_SUBAGENT_SYSTEM_PROMPT = (
    "You are a deterministic smoke-test coordinator. Use Agent when asked to "
    "use a subagent."
)
```

The smoke matrix validates:
- Agent tool present in tool catalog (`agent_catalog_present`)
- Agent tool was invoked (`agent_tool_count > 0`)
- Agent tool produced results (`agent_result_count > 0`)

## Managed Session Pool

**File: `cli/managed/manager.py`**

`ManagedClaudeSessionManager` manages a pool of Claude Code subprocess sessions:

```python
class ManagedClaudeSessionManager:
    _sessions: dict[str, ManagedClaudeSession]       # active sessions
    _pending_sessions: dict[str, ManagedClaudeSession] # pending sessions
    _temp_to_real: dict[str, str]                    # temp ID -> real session ID
    _real_to_temp: dict[str, str]                    # real session ID -> temp ID
```

Key features:
- **`get_or_create_session(session_id)`** -- returns existing session or creates new one
- **`register_real_session_id(temp_id, real_session_id)`** -- maps temp ID to real CLI-assigned session ID
- **`remove_session(session_id)`** -- stops and removes a session
- **`stop_all()`** -- stops all sessions (used during shutdown)
- **`get_stats()`** -- returns active/pending/busy counts

**File: `cli/managed/session.py`**

`ManagedClaudeSession` wraps a single Claude Code subprocess:
```
claude -p "<prompt>" --output-format stream-json --dangerously-skip-permissions --verbose
```

- Persistent per-conversation subprocess
- Each session has its own `current_session_id`
- Lock-based task isolation (`_cli_lock`)
- Stderr capture (capped at 256 KiB)

## Messaging Platform Communication

**File: `messaging/platforms/`**

The messaging layer bridges external chat platforms to Claude Code agents:

- **Discord** (`discord.py`, `discord_io.py`, `discord_inbound.py`): Discord bot integration with markdown rendering
- **Telegram** (`telegram.py`, `telegram_io.py`, `telegram_inbound.py`): Telegram bot integration

**File: `messaging/workflow.py`**

`MessagingWorkflow` coordinates the message lifecycle:
```python
class MessagingWorkflow:
    async def handle_message(self, incoming: IncomingMessage) -> None
    async def stop_all_tasks(self) -> int
    async def stop_task(self, node_id: str) -> int
```

The workflow:
1. Receives messages from Discord/Telegram
2. Routes them to Claude Code CLI subprocesses via `ManagedClaudeSessionManager`
3. Streams results back to the platform
4. Manages parallel conversation trees

## Conversation Tree Management

**File: `messaging/trees/`**

Agent conversations are modeled as `MessageTree` structures with `TreeQueueManager`:

- **`data.py`**: `MessageTree`, `MessageNode`, and `_SnapshotQueue` data structures
- **`manager.py`**: `TreeQueueManager` -- manages multiple trees with callbacks for queue updates and node processing
- **`processor.py`**: Node processing logic
- **`repository.py`**: Tree persistence and retrieval

## Application Runtime

**File: `api/runtime.py`**

`AppRuntime` wires together all agent components during startup:

```python
class AppRuntime:
    messaging_runtime: MessagingRuntime | None = None
    messaging_workflow: MessagingWorkflow | None = None
    cli_manager: ManagedClaudeSessionManager | None = None
```

The startup sequence:
1. Initialize `ProviderRegistry`
2. Start model list refresh
3. Configure messaging platform (Discord/Telegram/None)
4. Initialize `ManagedClaudeSessionManager` pointing back to the proxy
5. Initialize `SessionStore` for session persistence
6. Initialize `MessagingWorkflow` and start listening
7. Restore any saved conversation trees

## Stop All Tasks Endpoint

The `POST /stop` API endpoint at `api/routes.py` provides an agent-wide emergency stop:
```python
@router.post("/stop")
async def stop_cli(request: Request, _auth=Depends(require_api_key)):
    workflow = getattr(request.app.state, "messaging_workflow", None)
    count = await workflow.stop_all_tasks()
    return {"status": "stopped", "cancelled_count": count}
```

## Key Files

| File | Role |
|---|---|
| `cli/managed/manager.py` | Session pool for parallel Claude Code agents |
| `cli/managed/session.py` | Wraps one Claude Code subprocess per conversation |
| `cli/managed/claude.py` | Subprocess command, env build, and stdout parsing |
| `messaging/workflow.py` | Message-to-agent orchestration workflow |
| `messaging/transcript.py` | Subagent stack tracking in transcripts |
| `messaging/event_parser.py` | CLI event parsing including subagent events |
| `messaging/trees/` | Tree-based conversation state management |
| `messaging/platforms/` | Discord/Telegram platform bridges |
| `api/runtime.py` | Application lifecycle composition |

## Summary

free-claude-code does not implement the ACP specification. Its agent communication model is:

- **Claude Code's agent subagent tool** as the agent-to-agent primitive
- **Managed subprocess pool** for concurrent agent conversations
- **Discord/Telegram platform bridges** as agent communication channels
- **Tree-based conversation management** for branching multi-turn interactions
- **Centralized stop mechanism** for agent-wide control

## Related

- [[acp]]
- [[free-claude-code]]
