---
name: hermes-acp-implementation
description: "Deep dive into Hermes ACP implementation: server mode for ACP clients and client mode for connecting to external ACP agents"
source: sources/hermes-agent/
tags: [acp, agent-gateway, cli, hermes-agent, mcp, messaging, multi-platform, typescript]
---

# Hermes ACP Implementation

Hermes implements ACP (Agent Communication Protocol) in two directions:

1. **ACP Server** (`acp_adapter/server.py`) — other ACP clients talk to
   Hermes through the ACP protocol (drives the agent from editors).
2. **ACP Client** (`agent/copilot_acp_client.py`) — Hermes talks to GitHub
   Copilot through ACP (interoperates with the Copilot ecosystem).

---

## 1. ACP Server — `HermesACPAgent`

See [[hermes-acp-agent]] for the full asset reference. Key architectural points:

`HermesACPAgent` (`acp_adapter/server.py:565`) subclasses `acp.Agent`; the
`SessionManager` (`acp_adapter/session.py:175`) handles ACP session CRUD and
maps them to AIAgent sessions. The server also wires up edit approval
(`edit_approval.py`), permissions (`permissions.py`), and provenance
(`provenance.py`).

### Protocol mapping

The `acp` Python package provides the protocol transport. `HermesACPAgent`
extends `acp.Agent` and implements the ACP lifecycle:

```
ACP Client (Zed, Claude Code, etc.)
    │ ACP (stdio)
    ▼
HermesACPAgent
    │
    ├── SessionManager (session.py) — CRUD for ACP sessions
    │   └── maps to AIAgent sessions (state.py / hermes_state)
    │
    └── ThreadPoolExecutor(max_workers=4) — runs AIAgent synchronously
        └── each call isolated via contextvars.copy_context()
```

### ACP ↔ Hermes session mapping

ACP sessions have a stable `session_id` that is the client-facing handle.
Internally, the Hermes `AIAgent.session_id` may rotate when context
compression splits the database head. When this happens, `HermesACPAgent`
emits a `session_info_update` with `_meta.hermes.sessionProvenance`
carrying both the old and new internal session ids so the client can
maintain lineage.

### Capabilities advertised to ACP clients

Advertised in the `InitializeResponse` (`acp_adapter/server.py:1064-1070`):

| Capability | Value |
|---|---|
| `load_session` | True |
| `prompt_capabilities.image` | True |
| `session_capabilities.fork` | True |
| `session_capabilities.list` | True (paginated, 50/page) |
| `session_capabilities.resume` | True |
| `auth_methods` | Provider-specific or terminal setup |

Agent identity: `Implementation(name="hermes-agent", version=HERMES_VERSION)`.

### Tool surface

Tools available to ACP sessions are controlled by the `enabled_toolsets`
config. The default ACP toolset is `"hermes-acp"`. When an ACP client
provides MCP server configs, those are registered and the tool surface is
refreshed dynamically — including memory provider tools.

### Approval flow

ACP approvals flow through `conn.request_permission()`:
- **Terminal tool approvals** → `terminal_tool._get_approval_callback()` →
  `approval_cb` → `conn.request_permission()`
- **File edit approvals** → `EditApprovalRequester` →
  `conn.request_permission()`, controlled by edit_approval_policy (ask,
  workspace_session, session)
- `HERMES_INTERACTIVE=1` is set so approval.py takes the
  CLI-interactive path instead of auto-approve

---

## 2. ACP Client — `agent/copilot_acp_client.py`

Hermes can act as an ACP *client*, communicating with GitHub Copilot via
the ACP protocol. This lets Hermes interoperate with the Copilot ecosystem.

The module docstring describes it as an **"OpenAI-compatible shim that
forwards Hermes requests to `copilot --acp`"**: each request starts a
short-lived ACP session, sends the formatted conversation as a single prompt,
collects text chunks, and converts the result back into the minimal shape
Hermes expects from an OpenAI client.

---

## 3. CLI — `hermes acp` *is* the server

There is **no `serve` subcommand**: `hermes acp` runs the ACP server directly
(`hermes_cli/subcommands/acp.py`, handler `cmd_acp` at `hermes_cli/main.py:10895`).
Flags:

| Flag | Purpose |
|---|---|
| `--version` | Print Hermes ACP version and exit |
| `--check` | Sanity-check the ACP environment |
| `--setup` | Interactive provider/model setup for ACP terminal auth |
| `--setup-browser` | Browser-assisted setup |
| `--yes` | Accept all prompts (used by `--setup-browser` to skip confirmations) |

---

## Interaction between ACP and MCP

ACP clients can supply MCP server configurations when creating a session:

```
ACP Client
  │ session/new(mcp_servers=[...])
  ▼
HermesACPAgent._register_session_mcp_servers()
  │
  ├── tools.mcp_tool.register_mcp_servers(config_map)
  ├── model_tools.get_tool_definitions(enabled_toolsets)
  └── memory_manager.inject_memory_provider_tools(agent)
```

This means MCP servers can be provisioned *through* ACP — an editor like
Zed can start Hermes with its own MCP servers already registered.

---

## Related

- [[hermes-acp-agent]] -- ACP agent asset
- [[hermes-agent]] -- Core agent runtime
- [[hermes-agent-architecture]] -- System architecture
- [[hermes-mcp-implementation]] -- MCP implementation (related protocol)

## Links

- ACP server: `sources/hermes-agent/acp_adapter/server.py`
- ACP session manager: `sources/hermes-agent/acp_adapter/session.py`
- ACP events: `sources/hermes-agent/acp_adapter/events.py`
- ACP tools: `sources/hermes-agent/acp_adapter/tools.py`
- ACP auth: `sources/hermes-agent/acp_adapter/auth.py`
- ACP permissions: `sources/hermes-agent/acp_adapter/permissions.py`
- ACP provenance: `sources/hermes-agent/acp_adapter/provenance.py`
- ACP edit approval: `sources/hermes-agent/acp_adapter/edit_approval.py`
- ACP entry point: `sources/hermes-agent/acp_adapter/entry.py`
- ACP client (Copilot): `sources/hermes-agent/agent/copilot_acp_client.py`
- ACP CLI: `sources/hermes-agent/hermes_cli/subcommands/acp.py` → `cmd_acp` (`hermes_cli/main.py`)
- Note: `acp_registry/agent.json` was removed (commit `d84e11af4`) and no longer exists.
