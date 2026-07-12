---
name: clawpier-api
description: "ClawPier API — Tauri IPC commands, Docker management API, agent connection endpoints"
source: sources/clawpier/
tags: [clawpier, api, desktop, mcp]
---

# ClawPier — API Reference

ClawPier is a desktop GUI for managing Docker containers and OpenClaw agents, built with Tauri. Its API surface spans three layers: Tauri IPC (frontend↔backend), Docker engine proxy calls, and agent connection/status endpoints exposed via the Rust backend.

## Key API Facts

| Feature | Detail |
|---------|--------|
| **Framework** | Tauri v2 (Rust backend + web frontend) |
| **IPC transport** | Tauri `invoke()` — JSON serialized commands over webview bridge |
| **Docker surface** | Thin client over Docker REST API via `bollard` Rust crate |
| **Agent surface** | HTTP/WS connections to OpenClaw agent instances + MCP endpoints |
| **Frontend** | SolidJS + Tailwind (rendered in system webview) |
| **State pattern** | Reactive signals (SolidJS stores) synced via Tauri events |

## Tauri IPC Commands

All frontend-to-backend communication uses `tauri::command` functions exported from the Rust backend:

### Container Management

| Command | Parameters | Description |
|---------|-----------|-------------|
| `list_containers` | `filter: Option<String>` | List Docker containers (all/running) |
| `start_container` | `id: String` | Start a stopped container |
| `stop_container` | `id: String` | Stop a running container |
| `restart_container` | `id: String` | Restart a container |
| `remove_container` | `id: String, force: bool` | Remove a container |
| `container_logs` | `id: String, tail: u32` | Stream container logs |
| `container_stats` | `id: String` | Live resource stats (CPU, memory, net) |
| `exec_in_container` | `id: String, cmd: Vec<String>` | Execute command inside container |

### Image Management

| Command | Parameters | Description |
|---------|-----------|-------------|
| `list_images` | `filter: Option<String>` | List downloaded images |
| `pull_image` | `name: String, tag: String` | Pull image from registry |
| `remove_image` | `id: String, force: bool` | Remove an image |
| `prune_images` | — | Remove unused images |
| `image_history` | `id: String` | Show image layer history |

### Agent Connection

| Command | Parameters | Description |
|---------|-----------|-------------|
| `connect_agent` | `url: String, token: Option<String>` | Connect to an OpenClaw agent |
| `disconnect_agent` | `agent_id: String` | Disconnect from agent |
| `list_agents` | — | List configured agent connections |
| `agent_status` | `agent_id: String` | Get agent health/status |
| `send_agent_command` | `agent_id: String, command: String` | Send command to connected agent |

### System Commands

| Command | Parameters | Description |
|---------|-----------|-------------|
| `get_system_info` | — | Host OS, Docker version, resource usage |
| `get_settings` | — | Read application configuration |
| `update_settings` | `settings: AppSettings` | Save application configuration |
| `export_logs` | — | Export application and Docker logs |

## Docker Management API (via bollard)

ClawPier uses the [`bollard`](https://crates.io/crates/bollard) Rust crate to communicate with the Docker daemon. The Rust backend wraps bollard calls behind IPC commands, providing:

- **Container lifecycle**: list, create, start, stop, restart, remove
- **Image operations**: pull, list, remove, prune, inspect
- **Streaming**: logs (stdout/stderr), stats (CPU/memory/network), events
- **Networks and volumes**: list, inspect (basic management via IPC)

The backend connects to Docker via the default socket path (`/var/run/docker.sock`) or the `DOCKER_HOST` environment variable.

## Agent Connection Protocol

ClawPier connects to agents (OpenClaw or MCP-compatible) over:

| Protocol | Port/Path | Usage |
|----------|-----------|-------|
| **HTTP** | Configurable URL | REST status and command dispatch |
| **WebSocket** | `ws://<agent-url>/ws` | Real-time logs, stats, events |
| **MCP** | `http://<agent-url>/mcp` | Model Context Protocol endpoints |

Connection state is maintained in the Rust backend and surfaced to the frontend via Tauri events (`agent-connected`, `agent-disconnected`, `agent-error`).

## Authentication

- **Docker**: Inherits host socket permissions (Unix socket group membership)
- **Agent connections**: Token-based authentication configurable per agent
- **MCP endpoints**: No auth by default; configurable bearer token
- **Settings storage**: Local filesystem (`~/.config/clawpier/settings.json`) — no passwords stored, tokens only

## Usage

```typescript
// Frontend IPC call to list containers
const containers = await invoke("list_containers", { filter: "running" });

// Connect to an agent
await invoke("connect_agent", { url: "http://localhost:8080", token: "abc123" });
```

## Related

- [[clawpier]] — Source repository and wiki
- [[openclaw]] — Agent platform that ClawPier manages
- [[hermes-agent]] — Compatible MCP agent for connection
- [[mcp]] — Model Context Protocol integration
