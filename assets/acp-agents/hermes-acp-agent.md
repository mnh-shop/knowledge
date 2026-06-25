---
name: hermes-acp-agent
tags: [acp, agent, hermes, protocol]
description: ACP agent configuration for Hermes Agent wrapping its AIAgent behind the Agent Communication Protocol
---

# ACP Agent: `HermesACPAgent`

**File:** `sources/hermes-agent/acp_adapter/server.py`
**Class:** `HermesACPAgent(acp.Agent)` (extends `acp.Agent`)
**Protocol:** ACP (Agent Communication Protocol)
**Entry:** `hermes acp serve` / `python -m acp_adapter`

## What it is

Wraps Hermes's internal `AIAgent` (the conversation loop) behind the ACP
protocol so that ACP-compatible editors (Zed, Claude Code in ACP mode,
Codex, OpenCode, Pi) can drive Hermes as an agent — create sessions, send
prompts, see streaming tool calls, switch models, and manage approvals.

## Registry (for ACP discovery)

`sources/hermes-agent/acp_registry/agent.json`:

```json
{
  "id": "hermes-agent",
  "name": "Hermes Agent",
  "version": "0.17.0",
  "repository": "https://github.com/NousResearch/hermes-agent",
  "distribution": {
    "uvx": {
      "package": "hermes-agent[acp]==0.17.0",
      "args": ["hermes-acp"]
    }
  }
}
```

## Session Lifecycle

| Method | ACP Endpoint | What it does |
|---|---|---|
| `initialize` | session/initialize | Advertises capabilities: load, fork, list, resume, prompt images |
| `authenticate` | session/authenticate | Validates provider credentials or triggers terminal setup |
| `new_session` | session/new | Creates a fresh Hermes session, optionally registers MCP servers |
| `load_session` | session/load | Loads existing session + streams full history via replay |
| `resume_session` | session/resume | Loads or creates fallback session + history replay |
| `fork_session` | session/fork | Forks an existing session into a new one |
| `list_sessions` | session/list | Paginated list (50/page) of persisted sessions |
| `cancel` | session/cancel | Interrupts running agent via cancel_event + agent.interrupt() |
| `set_config_option` | session/config | Sets config like edit_approval_policy |
| `prompt` | session/prompt | Sends prompt → runs agent → streams events → returns response |

## Key design decisions

### Thread safety

Runs the synchronous `AIAgent` on a `ThreadPoolExecutor(max_workers=4)`.
Each call is wrapped in `contextvars.copy_context()` so concurrent ACP
sessions don't stomp on each other's ContextVar writes (notably
`HERMES_SESSION_KEY` for the interactive sudo password cache scope).

### History replay (load/resume)

`load_session` and `resume_session` **must** replay the full conversation
history via `session/update` notifications **before** the response is sent.
This is by ACP spec and matches Codex, Claude Code, OpenCode, and Pi.
The Zed client registers its session-update routing entry *before* awaiting
loadSession specifically so in-call history updates can find the thread.

Replays: user messages, assistant text, reasoning/thought blocks, tool call
starts, tool call completions, and plan updates from `todo` tool results.

### Concurrent prompt handling

If a second prompt arrives for the same session while it's running:
- `/steer` → injects guidance into the running turn
- `/queue` → explicitly queued for after turn ends
- Other text → auto-queued, runs after current turn finishes via recursive
  `self.prompt()` call at `~L1644`

### MCP server registration from ACP clients

ACP clients can pass MCP server configs at session creation time
(`mcp_servers` parameter). These are registered via
`tools.mcp_tool.register_mcp_servers()`, then the agent's tool surface is
refreshed via `model_tools.get_tool_definitions()` + memory provider injection.
This is how an editor can supply its own MCP servers to the Hermes session.

### Slash commands

Slash commands are intercepted locally and never reach the LLM:

| Command | What it does |
|---|---|
| `/help` | List available commands |
| `/model` | Show/switch model (resolves `provider:model` syntax) |
| `/tools` | List available tools with descriptions |
| `/context` | Show conversation message counts by role |
| `/reset` | Clear conversation history |
| `/compact` | Compress conversation context |
| `/steer` | Inject guidance into the running turn |
| `/queue` | Queue a prompt to run after current turn |
| `/version` | Show Hermes version |

### Session modes (edit approval policy)

Maps to ACP `SessionMode` to control file edit approval:

| Mode | Policy | Behavior |
|---|---|---|
| `default` | `ask` | Ask before edits |
| `accept_edits` | `workspace_session` | Auto-allow workspace + /tmp, sensitive paths still ask |
| `don't_ask` | `session` | Auto-allow for session, except sensitive paths |

### Usage / context tracking

Sends `UsageUpdate` via ACP session updates to drive Zed's circular context
indicator. `size` = model context window; `used` = estimated current
request pressure from system prompt + history + tool schemas.

## ACP ↔ Hermes mapping

```
ACP concept          → Hermes equivalent
─────────────────────────────────────────
Session (ACP id)     → Stable handle (may rotate internal DB head)
Hermes agent session → AIAgent.session_id (rotated on compression)
Prompts              → list[TextContentBlock | ImageContentBlock | ...]
Agent response       → Streaming updates + PromptResponse
Tool calls           → build_tool_start / build_tool_complete chunks
Edit approval        → EditApprovalRequester wrapping conn.request_permission
MCP servers          → tools.mcp_tool.register_mcp_servers
```

## Related

- [[hermes-agent]] -- Core agent runtime wrapped by this ACP adapter
- [[hermes-acp-implementation]] -- Deep dive into ACP server and client modes
- [[hermes-agent-architecture]] -- System architecture of Hermes Agent

## Links

- Source: `sources/hermes-agent/acp_adapter/` (server.py, session.py, events.py,
  tools.py, auth.py, permissions.py, provenance.py, edit_approval.py)
- Registry: `sources/hermes-agent/acp_registry/agent.json`
- ACP client for Copilot: `sources/hermes-agent/agent/copilot_acp_client.py`
