---
name: hermes-mcp-serve
tags: [hermes, mcp-server, typescript, agent-gateway, messaging, multi-platform]
description: MCP server configuration for Hermes Agent mcp_serve.py: a messaging bridge server using FastMCP over stdio transport
---

# MCP Server: `mcp_serve.py` — Hermes Messaging Bridge

**File:** `sources/hermes-agent/mcp_serve.py`
**Framework:** `mcp.server.fastmcp.FastMCP`
**Transport:** stdio
**Entry:** `hermes mcp serve`

## What it is

This is NOT an "expose Hermes's tools as MCP" server. It is a **messaging
bridge** that lets MCP clients (Claude Code, Cursor, Codex, etc.) read and
write to Hermes conversations across all connected platforms (Telegram,
Discord, Slack, WhatsApp, Signal, Matrix, etc.).

It intentionally matches **OpenClaw's 9-tool MCP channel bridge surface**
for drop-in compatibility.

## 10 MCP Tools

| Tool | Purpose |
|---|---|
| `conversations_list` | List active conversations with session keys, platform, timestamps |
| `conversation_get` | Get detail about one conversation by session key |
| `messages_read` | Read recent message history (role, content, timestamp) |
| `attachments_fetch` | List non-text attachments (images, media) for a message |
| `events_poll` | Poll for new events since a cursor (message, approval events) |
| `events_wait` | Long-poll / wait for next event (blocking, 30s timeout default) |
| `messages_send` | Send a message to `platform:chat_id` target |
| `channels_list` | List available channels for sending (Hermes extra) |
| `permissions_list_open` | List pending approval requests |
| `permissions_respond` | Approve/deny: `allow-once`, `allow-always`, `deny` |

## Architecture

```
          MCP Client (Claude Code, Cursor, etc.)
                    │ stdio
                    ▼
            mcp_serve.py (FastMCP)
                    │
        ┌───────────┴───────────┐
        │                       │
   sessions.json          state.db (SQLite)
   (index + routing)    (message transcripts)
        │                       │
        └───────────┬───────────┘
                    │
            EventBridge (background poller)
         ┌──────────┴──────────┐
         │                     │
    SQLite file mtime      Event queue
    check (200ms poll)     (in-memory, 1000 cap)
```

The **EventBridge** background thread polls `state.db` (via `SessionDB`) for
new messages by tracking:
1. **`sessions.json` mtime** — session index changes
2. **`state.db` mtime** — message content changes
3. **Per-session timestamps** — last polled message timestamp

When both files are unchanged, the 200ms poll returns immediately (mtime
check is ~1μs). Event types: `message`, `approval_requested`,
`approval_resolved`.

## Key details

- **`_load_sessions_index()`** — reads `~/.hermes/sessions/sessions.json`,
  strips `_README` and metadata keys
- **`_load_channel_directory()`** — reads
  `~/.hermes/channel_directory.json` for send targets
- **`send_message_tool`** — delegated to
  `tools.send_message_tool.send_message_tool` for the actual delivery
- **No approval IPC** — `permissions_respond` only resolves in-memory
  approvals tracked by the bridge session; it cannot persist decisions to
  the gateway (no IPC path)

## Client config

```json
{
  "mcpServers": {
    "hermes": {
      "command": "hermes",
      "args": ["mcp", "serve"]
    }
  }
}
```

## CLI

```bash
hermes mcp serve              # default
hermes mcp serve --verbose    # debug logging to stderr
```

## Related

- [[hermes-mcp-implementation]] -- MCP implementation patterns
- [[hermes-agent]] -- Core Hermes Agent runtime
- [[hermes-agent-architecture]] -- System architecture
- [[hermes-gateway-platforms]] -- Gateway platform adapters

## Links

- Source: `sources/hermes-agent/mcp_serve.py`
- MCP client implementation: `sources/hermes-agent/tools/mcp_tool.py` (MCPServerTask)
- MCP OAuth manager: `tools/mcp_oauth_manager.py`
- OpenClaw equivalent: `sources/openclaw/` (matching 9-tool surface)
