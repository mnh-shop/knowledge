---
name: CyberStrikeAI
description: "AI-native security testing platform with 100+ integrated tools, multi-agent orchestration, and built-in C2 framework"
source: sources/CyberStrikeAI/
tags: [CyberStrikeAI, golang, security, ai-llm, mcp, orchestration, multi-agent, rest-api, plugin, skills-platform]
---

# CyberStrikeAI

**AI-powered security testing platform** built in Go that integrates 100+ security tools with intelligent orchestration, role-based testing, and a built-in lightweight C2 framework for authorized engagements.

## Overview

CyberStrikeAI is an AI-native security testing platform that enables end-to-end automation from conversational commands to vulnerability discovery, attack-chain analysis, and result visualization. It provides an auditable, traceable, and collaborative testing environment through native MCP protocol support and AI agents.

## Key Features

- **100+ Security Tools** — Integrates nmap, masscan, sqlmap, nuclei, metasploit, burpsuite, subfinder, and more covering the full attack kill chain
- **Multi-Agent Orchestration** — CloudWeGo Eino-powered single-agent and multi-agent modes (deep, plan_execute, supervisor) with progressive skill loading
- **Role-Based Testing** — 12+ predefined security roles (Penetration Testing, CTF, Web App Scanning, API Security) with custom prompts and tool restrictions
- **Built-in C2 Framework** — AI-oriented command and control with TCP reverse, HTTP/HTTPS beacon, and WebSocket listeners for authorized engagements
- **Skills System** — Agent Skills-compatible structure with SKILL.md files, progressive disclosure, and optional Eino middleware (plantask, checkpoints, reduction)
- **Knowledge Base** — RAG with embedding-based vector retrieval, optional Eino Compose indexing pipeline, and configurable reranking hooks
- **Vulnerability Management** — CRUD operations, severity tracking (critical/high/medium/low/info), status workflow, and statistics
- **WebShell Management** — Manage PHP/ASP/ASPX/JSP shells with virtual terminal, file manager, and AI assistant integration
- **MCP Everywhere** — Native MCP implementation with HTTP/stdio/SSE transports and external MCP federation support

## Architecture

CyberStrikeAI follows a layered architecture:

```
CyberStrikeAI/
├── cmd/           -- Server and MCP stdio entrypoints
├── internal/      -- Core agent, MCP, C2, handlers, security executor
├── web/           -- Static SPA and templates
├── tools/         -- YAML tool recipes (100+ predefined tools)
├── roles/         -- Role configurations (YAML-based)
├── skills/        -- Agent Skills directories (SKILL.md + optional files)
├── agents/        -- Multi-agent Markdown definitions (orchestrator + sub-agents)
└── mcp-servers/   -- Standalone MCP servers (e.g., reverse shell)
```

**Key architectural components:**

- **Eino ADK Integration** — Single-agent via `/api/eino-agent/stream`, multi-agent via `/api/multi-agent/stream` with orchestration modes
- **YAML Tool Recipes** — Declarative tool definitions in `tools/*.yaml` with parameters, descriptions, and metadata
- **SQLite Persistence** — Conversations, vulnerabilities, webshell connections, and C2 data stored in SQLite
- **Event Streaming** — SSE-based real-time updates for tool execution and C2 events

## Skills & Tools

The platform uses a dual system for extensibility:

- **Agent Skills** — Directories under `skills/` with `SKILL.md` (YAML frontmatter: name, description) enabling progressive disclosure in multi-agent sessions
- **Eino Middleware** — Optional middlewares: tool_search, patch_toolcalls, plantask (TaskCreate/Get/Update/List), reduction, deep_model_retry_max_retries, checkpoint_dir
- **Tool Extensions** — YAML-based recipes in `tools/` define command, arguments, and parameter schemas for the 100+ security tools

Skills are loaded via the `skill` tool in multi-agent mode. Tool outputs exceeding size limits are compressed via Eino reduction and persisted to `tmp/reduction/`.

## Deployment

**Quick Start (one-command):**

```bash
git clone https://github.com/Ed1s0nZ/CyberStrikeAI.git
cd CyberStrikeAI
chmod +x run.sh && ./run.sh
```

The `run.sh` script validates Go/Python environments, installs dependencies, builds the project, and starts the server with HTTPS by default.

**Configuration** (config.yaml):

```yaml
openai:
  api_key: "sk-xxx"
  base_url: "https://api.deepseek.com/v1"
  model: "deepseek-chat"
mcp:
  enabled: true
  port: 8081
multi_agent:
  enabled: false
  eino_skills:
    disable: false
knowledge:
  enabled: false
```

Access the web UI at `https://127.0.0.1:8080/` after first launch.

## Related

- [[mcp]] — Model Context Protocol for tool integration
- [[hermes-agent]] — Similar agent runtime with MCP support
- [[security]] — Security-focused agent ecosystem
- [[skills-platform]] — Skill-based extensibility pattern