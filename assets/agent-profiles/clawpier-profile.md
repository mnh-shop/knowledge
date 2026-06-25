---
name: clawpier-profile
tags: [clawpier, profile, rust, tauri, desktop, agent-manager, gui, desktop-app, developer-tools, agent-profile, ai-llm, cli, docker, monitoring, plugin-sdk, security]
description: "Agent Profile: ClawPier"
---
# Agent Profile: ClawPier

**Type:** Desktop Agent Manager (not an agent itself — manages agents)
**Source:** `sources/clawpier/`

## Overview

ClawPier is a Tauri v2 desktop application that manages OpenClaw and Hermes AI agent
instances inside Docker containers. It provides a GUI for creating, configuring, monitoring,
and interacting with sandboxed agents.

## Managed Agent Runtimes

| Runtime | Default Image | Config Mount | CLI Pattern |
|---|---|---|---|
| OpenClaw | `ghcr.io/openclaw/openclaw:latest` | `/home/node/.openclaw` | `openclaw agent --local --agent main --session-id {id}` |
| Hermes | `nousresearch/hermes-agent:latest` | `/opt/data` | `hermes chat -Q -q "{msg}"` |

## Key Features

- Sandbox-by-default (containers start with `--network none`)
- GUI for resource limits, network mode, port mappings, env vars
- Built-in chat interface to agents
- Live metrics (CPU, memory, network I/O)
- PTY terminal into containers
- Workspace file browser
- ClawHub skill registry browser (50+ skills)
- Health checks with auto-restart
- Config import/export (JSON/YAML)
- Desktop notifications on bot status transitions

## API Surface

58 Tauri IPC commands covering: bot CRUD, chat, terminal, monitoring, file browsing,
workspace management, config import/export, ClawHub skills, port management.

## Security Model

- **Container-level isolation** — each agent in its own Docker container
- **No network default** — network access opt-in per bot
- **Resource cgroups** — CPU/memory limits per container
- **Docker socket** — required (standard Tauri permission prompt)

## Integration Points

| System | How |
|---|---|
| [[openclaw]] | Primary managed agent runtime |
| [[hermes-agent]] | Secondary managed agent runtime |
| [[hermes-agent-docker]] | Alternative Hermes Docker packaging (no GUI) |
| ClawHub | Community skill registry for OpenClaw |

## Related

- [[clawpier]] — Wiki entry
- [[clawpier-architecture]] — Architecture documentation
- [[clawpier-deployment]] — Deployment guide
