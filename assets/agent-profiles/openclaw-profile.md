---
name: openclaw-profile
tags: [openclaw, profile, typescript, agent-gateway, messaging, personal-assistant, live-canvas, ai-llm, automation, orchestration, acp, agent-profile, bootc, cli, container, dashboard, docker, mcp, plugin-sdk, quadlet, storage, systemd]
description: OpenClaw is a personal AI assistant (MIT) — TypeScript, Node.js, 30+ channels, ACP + MCP + Gateway, Live Canvas
metadata:
  type: reference
source: sources/openclaw/
---

# OpenClaw — Key Reference

**License:** MIT

**What it is:** A personal AI assistant you run on your own devices. Full agent platform with gateway, multi-channel messaging, plugin SDK, skills, Live Canvas (A2UI), ACP, and MCP.

**Quick install:**
```bash
npm install -g openclaw@latest
openclaw onboard --install-daemon
```

**Runtime:** Node 24 (recommended), Node 22.19+

**Channels:** 30+ — WhatsApp, Telegram, Discord, Slack, Signal, iMessage, IRC, Matrix, Teams, and many more.

**Key differentiators vs Hermes:**
- Larger channel ecosystem (30+ vs ~20)
- Live Canvas (A2UI) built-in — agent-driven visual workspaces
- Single-instance personal assistant (vs Hermes Workspace as separate project)
- Plugin SDK with extension marketplace (ClawHub)
- ACP + MCP both implemented in core

**Deployment:** `npm install -g` (dev/personal), Docker multi-stage (183MB), Fedora bootc via [[tank-os]]

**Interfaces:** REST API (gateway port 18789), ACP, MCP, CLI, plugin SDK

**State:** SQLite only — shared state DB + per-agent DB. No Redis/Postgres required.

**Related repos:** [[tank-os]] (bootc deploy), [[mission-control]] (dashboard)

## Related

- [[openclaw-architecture]] -- System architecture overview
- [[openclaw-api]] -- REST and WebSocket API reference
- [[openclaw-deployment]] -- Full deployment guide
- [[openclaw-acp-implementation]] -- ACP protocol implementation
- [[openclaw-mcp-implementation]] -- MCP server implementation
- [[openclaw-acp-agent]] -- ACP agent asset registration
- [[openclaw-mcp-server]] -- MCP server asset configuration
- [[openclaw-quadlet]] -- Quadlet deployment patterns
- [[openclaw]] -- Main wiki entry
