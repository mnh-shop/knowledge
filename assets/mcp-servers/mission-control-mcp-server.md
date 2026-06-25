---
name: mission-control-mcp-server
tags: [mission-control, mcp-server, typescript, nextjs, react, dashboard, orchestration, monitoring]
description: Mission Control MCP Server
---

# Mission Control MCP Server
**Source:** `sources/mission-control/`

## Asset Card

| Field | Value |
|-------|-------|
| **Name** | Mission Control MCP Server |
| **Source** | `scripts/mc-mcp-server.cjs` |
| **Protocol** | JSON-RPC 2.0 over stdio (MCP spec 2024-11-05) |
| **Capabilities** | `{ tools: {} }` |
| **Dependencies** | Zero (Node.js built-ins only) |
| **Auth Methods** | API key (`MC_API_KEY`) or session cookie (`MC_COOKIE`) |
| **Default URL** | `http://127.0.0.1:3000` |

## Adding to Claude Code

```bash
claude mcp add mission-control -- node /path/to/mission-control/scripts/mc-mcp-server.cjs
```

Profile support: reads from `~/.mission-control/profiles/default.json` (stores URL, API key, and session cookie). Override per-session via environment variables `MC_URL`, `MC_API_KEY`, `MC_COOKIE`.

## Tool Categories (35 Tools)

| Category | Tools |
|----------|-------|
| **Agents** (6) | list, get, heartbeat, wake, diagnostics, attribution |
| **Agent Memory** (3) | read, write, clear |
| **Knowledge Base** (7) | search (FTS5/BM25), read file, write file, health, rebuild index, gaps, consolidate |
| **Agent Soul** (3) | read, write (inline/template), list templates |
| **Tasks** (8) | list, get, create, update, poll queue, broadcast, list comments, add comment |
| **Sessions** (4) | list, control (monitor/pause/terminate), continue, transcript |
| **Connections** (2) | list, register |
| **Tokens/Costs** (3) | token stats, agent costs, costs by agent |
| **Skills** (1) | list, read |
| **Cron** (1) | list |
| **Status** (3) | health, dashboard, status |
| **Runs** (7) | list, get, create, update, provenance, attach eval, eval leaderboard |

## Notes

- Written in CommonJS (`mc-mcp-server.cjs` extension enforces CJS in ESM project)
- 30-second fetch timeout
- Stdio line-based transport uses readline -- each line parsed as JSON-RPC 2.0
- Results JSON-stringified to stdout; errors surface as MCP error content or JSON-RPC errors
- API contract parity with the CLI -- both call the same `/api/*` REST layer

## Related

- [[mission-control]] -- Project overview
- [[mission-control-api]] -- REST API that the MCP server wraps
- [[mission-control-architecture]] -- Where the MCP server fits in the architecture
- [[mission-control-profile]] -- Quick reference for running the MCP server
