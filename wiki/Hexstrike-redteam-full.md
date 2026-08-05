---
name: Hexstrike-redteam-full
tags: [security, pentesting, mcp, ai-agents, red-team, boaz, payload-evasion, ctf, bug-bounty, python, flask, mit]
description: "AI-powered MCP cybersecurity automation platform v6.0 — 137 registered MCP tools, 12+ AI agents, BOAZ payload evasion framework, and multi-agent autonomous pentesting"
source: sources/Hexstrike-redteam-full/
verification_date: 2026-07-30
verified_by: codegraph-verify
---

# HexStrike RedTeam Full

**Source:** `sources/Hexstrike-redteam-full/`

> **⚠️ Duplicate entry:** This repo is **byte-identical** to `Hexstrike-redteam` (same commit `89779b7`, zero diff on tracked files). It is a duplicated vault entry; all claims below are verified against the shared source.

HexStrike AI RED-TEAM is an AI-powered MCP cybersecurity automation platform with multi-agent architecture. It integrates 137 registered MCP tools (README claims "127", "150+", and "155+" — internally inconsistent), 12+ autonomous AI agents, and the BOAZ red team payload evasion framework (68 loaders, 13 encoders) into a unified MCP server that Claude, GPT, Copilot, and other MCP-compatible agents can drive.

| Field | Value |
|---|---|
| **Origin** | [Yenn503/Hexstrike-redteam](https://github.com/Yenn503/Hexstrike-redteam) |
| **License** | ⚠️ Conflicted: README badge says MIT but no root `LICENSE` file; only `BOAZ_beta/LICENSE` (GPL-3.0) |
| **Stack** | Python (Flask, FastMCP), MCP protocol |
| **Port** | 8888 |
| **Registered MCP Tools** | 137 (README claims 127/150+/155+) |
| **AI Agents** | 12+ |
| **Source** | `sources/Hexstrike-redteam-full/` |
| **Codegraph** | `graphs/Hexstrike-redteam-full/` |

## What is it?

HexStrike is a complete MCP-based penetration testing framework that turns any MCP-compatible AI agent (Claude, GPT, Copilot) into an autonomous security operator. v6.0 introduces a multi-agent architecture with dedicated agents for bug bounty, CTF solving, CVE intelligence, and exploit generation. The BOAZ payload engine provides enterprise-grade evasion with 68 process injection loaders, 13 encoding schemes, and EDR/AV bypass techniques.

## Key Features

- **137 Registered MCP Tools** — 53 auto-installed across network (10), web app (19), password & auth (5), binary (13), forensics (16), OSINT (13), cloud (10), and Metasploit (per `README.md:215-276`)
- **12+ Autonomous AI Agents** — BugBounty Agent, CTF Solver Agent, CVE Intelligence Agent, Exploit Generator Agent, and more
- **BOAZ Payload Evasion** — 68 process injection loaders (syscall, stealth, threadless, VEH/VCH), 13 encoding schemes (AES, ChaCha20, UUID, XOR, RC4), EDR/AV bypass (API unhooking, ETW patching, LLVM obfuscation)
- **MCP Protocol Integration** — FastMCP-based server, compatible with Claude, GPT, Cline, OpenClaw, and any MCP client
- **Intelligent Decision Engine** — Target analysis, tool selection, parameter optimization, and attack chain discovery
- **Real-Time Dashboards** — Visual vulnerability cards, progress visualization, risk analysis
- **Smart Caching & Resource Optimization** — Error recovery and adaptive execution

## Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | Python 3.8+, Flask, FastMCP |
| **Protocol** | MCP (Model Context Protocol) |
| **AI Agents** | 12+ role-specific autonomous agents |
| **Payload Engine** | BOAZ (68 loaders, 13 encoders, EDR bypass) |
| **Auto-Install** | Bash/Python installers for 53 of 137 tools |

## Deployment

### Quick Install

```bash
git clone https://github.com/Yenn503/Hexstrike-redteam
cd Hexstrike-redteam
python3 -m venv hexstrike_env
source hexstrike_env/bin/activate
python3 -m pip install -r requirements.txt
python3 hexstrike_server.py
# MCP server runs on port 8888
```

### Alternative (using install scripts)

The `install/` directory contains the actual installers (no `install_hexstrike.sh` exists):
- `install/install_all.sh` — full install (deps + security tools + venv + MCP config)
- `install/install_system_deps.sh` — system dependencies
- `install/install_security_tools.sh` — auto-installs the 53 tools
- `install/setup_hexstrike_venv.sh` — Python venv setup
- `install/configure_mcp.sh` — MCP configuration for Claude Desktop/CLI

```bash
bash install/install_all.sh
```

The server exposes MCP endpoints that any MCP-compatible agent can connect to.

## Related

- [[Claude-Red]] — 58 offensive security skills for Claude Skills system
- [[Claude-OSINT]] — OSINT methodology and arsenal skills for Claude
- [[SecOpsAgentKit]] — Security operations skills for AI coding agents
- [[ctf-skills]] — Agent Skills for CTF challenges
