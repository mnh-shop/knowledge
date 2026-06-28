---
name: nyxstrike
description: "AI-powered offensive security orchestration engine — connects LLM agents to security tools for reconnaissance to exploitation"
tags: [mcp, security, pentest, python, agent]
source: sources/nyxstrike/
---

# NyxStrike

**NyxStrike** (`github.com/CommonHuman-Lab/nyxstrike`) is an AI-powered offensive security orchestration engine that connects LLM agents to real security tools and executes full attack chains — from reconnaissance to exploitation.

## Description

Previously known as Hexstrike AI Community Edition, NyxStrike provides an MCP-compatible interface to 100+ security tools including nmap, sqlmap, metasploit, and specialized recon/exploit utilities. The system orchestrates attack chains through natural language prompts while maintaining security tooling isolation.

## Key Features

- **MCP Interface** — JSON-RPC tool exposure for LLM agents
- **Tool suite** — 100+ security tools (nmap, sqlmap, metasploit, etc.)
- **Attack chain orchestration** — recon → exploit workflows
- **Python 3.13+** — Modern async tooling

## Quick Start

```bash
git clone https://github.com/CommonHuman-Lab/nyxstrike
cd nyxstrike
pip install -r requirements.txt
python nyxstrike_server.py
```

## Source

- `sources/nyxstrike/` — Full cloned repository
- MCP servers documented in `sources/nyxstrike/mcp_servers/`