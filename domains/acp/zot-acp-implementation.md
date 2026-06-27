---
name: zot-acp-implementation
description: "Zot swarm multi-agent orchestration — subprocess agent dispatch, JSONL event protocol, supervision, and lifecycle management"
tags: [acp, zot, multi-agent]
source: sources/zot/
---

# Zot ACP Implementation

Zot does **not** implement the formal Agent Communication Protocol (ACP). However, the **swarm subsystem** (`packages/agent/swarm/`) provides multi-agent orchestration capabilities that serve an equivalent role: spawning subprocess agents, managing their lifecycle, and consuming their event streams.

## Swarm Architecture

```
Supervisor (zot process)
│
├── Swarm Manager
│   ├── Agent "researcher" (subprocess zot --json ...)
│   │   ├── Inbox: Unix socket for command input
│   │   ├── Stdout: JSONL event stream
│   │   └── Status: running / done / failed / killed
│   ├── Agent "coder" (subprocess zot --json ...)
│   │   ├── Inbox: Unix socket
│   │   ├── Stdout: JSONL event stream
│   │   └── Status: running / done / failed / killed
│   └── Agent "..." (subprocess)
└── Dashboard (reports activity + transcript)
```

### Event Protocol

Each swarm agent emits structured JSONL events on stdout:

```json
{"type":"agent_ready","inbox":"/tmp/zot-swarm-001","session":"...","cwd":"..."}
{"type":"turn_start","step":0}
{"type":"user_message","content":[{"type":"text","text":"..."}]}
{"type":"assistant_message","content":[{"type":"text","text":"..."}]}
{"type":"turn_end","stop":"end"}
{"type":"agent_stopped","reason":"shutdown"}
```

### Lifecycle States

| State | Description |
|-------|-------------|
| `StatusPending` | Agent created, not yet started |
| `StatusRunning` | Agent active, processing turns |
| `StatusDone` | Agent completed successfully |
| `StatusFailed` | Agent exited with error |
| `StatusKilled` | Agent cancelled by supervisor |

### Capabilities

- **Subprocess isolation**: Each agent runs as an independent process with its own working directory and session file
- **Unix-socket inbox**: Supervisor sends input to agents via a Unix socket for low-latency command delivery
- **Activity reporting**: Agents report real-time activity updates back to the dashboard
- **Cancellation**: Supervisor can cancel any agent mid-turn
- **Graceful shutdown**: `shutdown` command initiates clean termination

### Comparison with Formal ACP

| Feature | ACP Standard | Zot Swarm |
|---------|-------------|-----------|
| Agent-to-agent messages | JSON-RPC methods | Subprocess stdout + Unix socket inbox |
| Agent discovery | Registry lookup | Filesystem-based swarm config |
| Task delegation | Structured delegation frames | `Run(ctx, sink)` via `Runner` interface |
| State management | Formal state machine | Status enum (running/done/failed/killed) |
| Identity/auth | DID-based or shared keys | OS process boundary |
| Streaming | SSE events | JSONL stdout stream |
| Inter-agent routing | Message routing | Direct supervisor mediation |

### Integration with Other Vault Services

- **agentfield**: Agentfield's sandbox management could spawn zot swarm agents inside micro-VMs for isolated code execution
- **goclaw**: GoClaw's tool bridge could wire zot's RPC mode as a worker tool, with swarm managing multiple parallel zot instances
- **hermes-agent**: Hermes's multi-platform agent loop could delegate coding subtasks to a zot swarm

## Related Documentation

- [[zot-architecture]] — Full architecture doc
- [[zot-mcp-implementation]] — Extension protocol as MCP-adjacent surface
- [[zot-api]] — Telegram bot and RPC API
- [[zot-deployment]] — Deployment patterns
- [[agentfield-architecture]] — Agentfield sandbox architecture
- Source: `sources/zot/packages/agent/swarm/`
