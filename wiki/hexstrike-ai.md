---
name: hexstrike-ai
tags: [hexstrike-ai, python, mcp, security, ai-llm, ai-agents, multi-agent, orchestration, tool-calling]
description: "AI-powered MCP cybersecurity automation platform with 150+ security tools and 12+ autonomous agents for penetration testing and red team operations"
source: sources/hexstrike-ai/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# HexStrike AI

| Field | Value |
|---|---|
| **Origin** | [0x4m4/hexstrike-ai](https://github.com/0x4m4/hexstrike-ai) |
| **License** | MIT |
| **Stack** | Python 3.8+ |
| **Source** | `sources/hexstrike-ai/` |

## What it is

HexStrike AI is an **AI-powered cybersecurity automation platform** that provides MCP (Model Context Protocol) integration for penetration testing, bug bounty hunting, and red team operations. Built on the FastMCP framework, it enables AI agents to autonomously execute security assessments through intelligent tool selection, parameter optimization, and attack chain discovery.

## Key features

- **150+ Security Tools** — Network reconnaissance, web app testing, binary analysis, cloud security, CTF, and forensics tools
- **12+ Autonomous AI Agents** — Bug bounty workflow manager, CTF solver, CVE intelligence, exploit generator, vulnerability correlator
- **Intelligent Decision Engine** — Tool selection AI, parameter optimization, and attack chain discovery
- **Browser Agent** — Headless Chrome automation with Selenium for web application security testing
- **Modern Visual Engine** — Real-time dashboards, progress tracking, and vulnerability cards
- **Smart Caching System** — LRU eviction for optimal performance with repeated operations
- **FastMCP Integration** — Native MCP protocol support for Claude, VS Code Copilot, Cursor, and other AI clients

## Architecture

Multi-agent architecture with intelligent decision engine:

```
AI Agent → HexStrike MCP Server → [Tools, Agents, Decision Engine, Visual Engine]
```

The platform consists of:
- **Intelligent Decision Engine** — Analyzes targets and selects optimal testing strategies
- **Autonomous Agents** — Specialized agents for different security domains
- **Security Tool Layer** — 150+ integrated tools across 6 categories
- **Modern Visual Engine** — Real-time dashboards and reporting

## Skills & Tools

**Security Tool Categories:**
- Network & Recon (nmap, masscan, rustscan, amass, subfinder, nuclei, theharvester)
- Web App Security (gobuster, feroxbuster, ffuf, nikto, sqlmap, wpscan, dalfox)
- Binary Analysis (gdb, radare2, binwalk, ghidra, checksec, pwntools, angr)
- Cloud Security (prowler, trivy, kube-hunter, docker-bench-security)
- CTF & Forensics (volatility3, foremost, steghide, exiftool)
- OSINT (sherlock, recon-ng, spiderfoot, shodan-cli)

**Core MCP Tools:**
- `nmap_scan()` — Advanced Nmap scanning with optimization
- `gobuster_scan()` — Directory and file enumeration
- `feroxbuster_scan()` — Recursive content discovery
- `nuclei_scan()` — Vulnerability scanning with templates
- `sqlmap_scan()` — SQL injection testing
- `prowler_assess()` — AWS/Azure/GCP security assessment
- `ghidra_analyze()` — Software reverse engineering

## Deployment

**Quick Setup:**
```bash
git clone https://github.com/0x4m4/hexstrike-ai.git
cd hexstrike-ai
python3 -m venv hexstrike-env
source hexstrike-env/bin/activate
pip3 install -r requirements.txt
```

**Start MCP Server:**
```bash
python3 hexstrike_server.py --port 8888
```

**AI Client Configuration:**
Add to Claude Desktop config (`~/.config/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "hexstrike-ai": {
      "command": "python3",
      "args": [
        "/path/to/hexstrike-ai/hexstrike_mcp.py",
        "--server",
        "http://localhost:8888"
      ],
      "description": "HexStrike AI v6.0 - Advanced Cybersecurity Automation Platform",
      "timeout": 300
    }
  }
}
```

## Related

- [[Hexstrike-redteam]] — Related red team variant with BOAZ payload evasion
- [[mcp]] — Model Context Protocol for tool integration
- [[security]] — Security-focused agent ecosystem
- [[hermes-agent]] — Agent runtime with compatible MCP surface
- [[openclaw]] — Personal AI assistant with MCP security tool integration
- [[agentfield]] — Control plane that could orchestrate HexStrike agents via MCP