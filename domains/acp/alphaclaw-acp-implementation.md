---
name: alphaclaw-acp
description: "AlphaClaw ACP (Agent Communication Protocol) analysis — no ACP found, related multi-agent features"
source: sources/alphaclaw/
tags: [acp, documentation, mcp]
---
# AlphaClaw ACP (Agent Communication Protocol) Implementation

**Source repo:** `@chrysb/alphaclaw` (v0.9.18)

## Finding

AlphaClaw does **not** implement the Agent Communication Protocol (ACP). A search of the entire codebase for `acp`, `AgentCommunication`, `agent-comm`, and related terms returned zero results.

## What AlphaClaw Has Instead

AlphaClaw manages agents indirectly by writing configuration consumed by the OpenClaw gateway process. The closest features are:

1. **Multi-Agent Management** -- Sidebar-driven agent navigation with create, rename, and delete flows. Per-agent overview cards, channel bindings, and URL-driven agent selection. (Setup UI layer only; no agent-to-agent protocol.)

2. **Agent Tools Configuration** -- Per-agent tool allow/deny overrides configured via the Setup UI and stored in OpenClaw's profiles.

3. **Channel Bindings** -- Per-agent channel bindings for Telegram, Discord, and Slack, all configured through the Setup UI.

4. **MCP Server Registration** -- Writing `mcp.servers.<name>` blocks into `openclaw.json` so the agent can call external MCP servers (see the MCP implementation document). This is the closest to an agent communication capability, but it is unidirectional (agent to MCP server) and uses a standard MCP client within OpenClaw, not ACP.

## No ACP Protocol Elements Found

- No `AgentCommunication` client or server classes
- No ACP message types or schemas
- No agent-to-agent communication channels
- No ACP handshake or capability negotiation
- No inter-agent routing or discovery
- No agent-communication middleware or handlers

## Partial ACP Reference in Codebase

The constant `acpRuntime: 'acp_runtime'` exists at `lib/server/doctor/constants.js:19`. However, no ACP protocol implementation, handler, or integration was found anywhere else in the codebase -- this constant is not referenced by any other module and appears to be a forward-looking placeholder or naming convention rather than an active ACP feature.

## Related

- [[acp]]
- [[alphaclaw]]
- [[openclaw]]
