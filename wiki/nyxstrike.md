---
name: nyxstrike
description: "AI-powered offensive security orchestration engine — connects LLM agents to security tools for reconnaissance to exploitation"
tags: [mcp, security, pentest, python, agent]
source: sources/nyxstrike/
---

# NyxStrike

**NyxStrike** (`github.com/CommonHuman-Lab/nyxstrike`) is an AI-powered offensive security orchestration engine that connects LLM agents to real security tools and executes full attack chains — from reconnaissance to exploitation. Previously known as Hexstrike AI Community Edition, it provides an MCP-compatible interface to 185+ security tools across 12 categories.

## Overview

NyxStrike bridges the gap between AI reasoning and real-world offensive security tooling. Rather than requiring a human operator to manually run individual tools like nmap, sqlmap, or metasploit, NyxStrike lets an LLM agent orchestrate entire attack workflows through natural language prompts. The system maintains security tooling isolation while providing a real-time session dashboard for operator oversight.

The project is built on Python 3.13+ and uses FastMCP for MCP server integration. It ships with a modular tool registry (`tool_registry.py`) that categorizes tools and validates their schemas at import time, with per-category effectiveness scoring. The server (`nyxstrike_server.py`) exposes API endpoints, while the MCP client (`nyxstrike_mcp.py`) provides the AI agent communication layer with colored logging, profile-based tool loading, and intelligent decision engine integration.

## Key Features

- **185+ Security Tools** — Tools organized across 12 categories including network reconnaissance, web exploitation, wireless security, OSINT, password attacks, and cloud/API security. Each tool is registered in a compact schema with effectiveness scoring (0.0–1.0) for AI decision-making.
- **MCP-Compatible Interface** — JSON-RPC tool exposure via FastMCP. Connect any MCP-compatible AI client — OpenCode, Cursor, Claude Desktop, VS Code Copilot, Roo Code — using the universal MCP command.
- **AI Orchestration Engine** — The intelligent decision engine (`server_core/intelligence/`) uses catalog-driven tool scoring to chain tools automatically. Includes personality profiles (`chat_personalities.py`), CVE intelligence management, and tool scoring algorithms.
- **Attack Chain Workflows** — Full recon → enumeration → exploitation → reporting workflows. The server core includes workflow definitions, session management, process management, and a failure recovery system.
- **Real-Time Dashboard** — Web-based session dashboard at `http://localhost:8888` with live command output, session logs, and performance monitoring.
- **Modular Plugin System** — Plugin architecture via `plugins/plugins.yaml` supporting extensible tool loading through `plugin_loader.py` and `plugin_mcp_loader.py`.
- **Tool Profiles** — Profile-based tool loading (`mcp_core/tool_profiles.py`) to fit model context windows — only 5–8 tools per category for smaller models, with expandable profiles for larger contexts.
- **Docker Deployment** — `docker-compose.yml` for containerized deployment with AI model support (full ~8.4GB or small ~2.5GB via `nyxstrike.sh` flags).
- **Security Controls** — API token authentication (`NYXSTRIKE_API_TOKEN`), configurable command timeouts, isolated environments recommendation, and per-tool parameter validation.

## Architecture

NyxStrike follows a layered architecture:

```
AI Client (MCP) ←→ nyxstrike_mcp.py ←→ nyxstrike_server.py (REST API)
                                               │
                                    ┌──────────┴──────────┐
                                    │   server_core/       │
                                    │  ─ intelligence/     │
                                    │  ─ command_executor/ │
                                    │  ─ session_flow/     │
                                    │  ─ process_manager/  │
                                    │  ─ failure_recovery/ │
                                    └─────────────────────┘
                                               │
                                    ┌──────────┴──────────┐
                                    │   mcp_tools/ (52+)   │
                                    │   server_api/ (56+)  │
                                    │   tool_registry.py   │
                                    └─────────────────────┘
```

The `server_core/` directory handles core server logic including the intelligent decision engine (catalog-driven tool selection and scoring), command execution with parameter validation, process pooling, session management, and failure recovery. The `mcp_tools/` directory contains over 52 tool category directories (net_scan, osint, exploit_framework, vuln_scan, wifi_pentest, etc.) each exposing tools via `mcp.tool()` decorators through gateway registration.

## Usage

### Quick Start

```bash
git clone https://github.com/CommonHuman-Lab/nyxstrike
cd nyxstrike
./nyxstrike.sh -a               # Setup + start server
# Or with Docker:
docker compose up --build -d
```

### MCP Integration

Connect any MCP-compatible AI client:

```bash
/path/to/nyxstrike/nyxstrike-env/bin/python3 \
  /path/to/nyxstrike/nyxstrike_mcp.py \
  --server http://127.0.0.1:8888 \
  --profile full
```

For OpenCode, add to `opencode.json`:

```json
{
  "mcp": {
    "nyxstrike": {
      "type": "local",
      "command": [
        "/path/to/nyxstrike/nyxstrike-env/bin/python3",
        "/path/to/nyxstrike/nyxstrike_mcp.py",
        "--server", "http://127.0.0.1:8888",
        "--profile", "full"
      ],
      "enabled": true
    }
  }
}
```

### Security Considerations

- Run only in isolated environments or dedicated security testing VMs
- AI agents may execute real commands — maintain operator oversight
- Monitor activity via the real-time dashboard
- Use `NYXSTRIKE_API_TOKEN` for any non-local deployment
- Legal use requires written authorization for penetration testing; intended for bug bounty programs, CTF competitions, and authorized red team exercises

## Related

- [[hexstrike-ai]] — Upstream project that inspired NyxStrike's architecture
- [[Hexstrike-redteam]] — Red team variant with specialized exploitation workflows
- [[sec-af]] — Security agent framework with complementary orchestration capabilities
- [[kali-pentest]] — Kali Linux penetration testing reference (NyxStrike integrates Kali tooling)
- [[hermes-agent]] — MCP hub that can consume NyxStrike's MCP server tools
- [[Mnemosyne]] — Memory system that pairs with session storage for long-running operations
