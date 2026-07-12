---
name: clawpier-desktop-integration
type: integration
tags: [clawpier, hermes-agent, openclaw, integration, desktop, mcp, container-management, tauri]
description: "ClawPier desktop manager connecting to Hermes Agent and OpenClaw: Docker container lifecycle management, agent health monitoring, Tauri desktop IPC"
---

# Integration: ClawPier Desktop ↔ Hermes + OpenClaw

**Sources**: `sources/clawpier/`, `sources/hermes-agent/`, `sources/openclaw/`

## Overview

ClawPier is a Tauri-based desktop GUI for managing Hermes Agent and OpenClaw deployments. It provides container lifecycle management (start, stop, logs), agent health monitoring, and workspace integration through a native desktop interface. Communication happens via REST APIs and MCP surfaces, making ClawPier an MCP-aware desktop control plane.

## Architecture

```
ClawPier Desktop (Tauri) ──┬── Hermes REST API (:8642)
                           │      /health, /executions
                           ├── OpenClaw REST API (:18789)
                           │      /healthz, /gateway
                           └── Podman Socket
                                  start/stop/logs
```

ClawPier's Rust backend communicates with Hermes and OpenClaw via HTTP REST. The Podman socket provides direct container control. Tauri IPC bridges the Rust backend to the Svelte/React frontend.

## Configuration

**Connection settings** (`~/.config/clawpier/config.json`):
```json
{
  "connections": {
    "hermes": { "endpoint": "http://127.0.0.1:8642", "health": "/health" },
    "openclaw": { "endpoint": "http://127.0.0.1:18789", "health": "/healthz" },
    "podman": { "socket": "/run/user/1000/podman/podman.sock" }
  },
  "poll_interval": 5000
}
```

**Hermes** needs `HERMES_DASHBOARD=1 API_SERVER_ENABLED=true API_SERVER_PORT=8642`.
**OpenClaw** needs `gateway.port: 18789` with health endpoint `/healthz`.

**Dashboard features**: Agent health cards (green/red via polling), container start/stop (Podman socket via Rust), log streaming (Tauri events → frontend WebSocket view), and deep-links to hermes-workspace web UI for advanced views.

## Related

- [[clawpier]] — Tauri desktop GUI for agent management
- [[hermes-agent]] — Core agent runtime (primary ClawPier target)
- [[openclaw]] — Agent gateway (secondary ClawPier target)
- [[hermes-workspace]] — Web-based agent UI; ClawPier links to it for advanced views
- [[integrations/hermes-openclaw-deployment.md]] — Container deployment pattern for Hermes + OpenClaw
- [[domains/mcp/hermes-mcp-implementation.md]] — Hermes MCP surface consumed by ClawPier
