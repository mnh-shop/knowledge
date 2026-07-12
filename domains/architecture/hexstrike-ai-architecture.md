---
name: hexstrike-ai-architecture
tags: [hexstrike-ai, architecture, security, pentesting, mcp, multi-agent, orchestration]
description: Architecture of HexStrike AI — AI-powered penetration testing platform with 150+ MCP tools and multi-agent orchestration
source: sources/hexstrike-ai/
---

# HexStrike AI Architecture

## Overview

HexStrike AI is an **AI-powered cybersecurity automation platform** providing MCP (Model Context Protocol) integration for penetration testing, bug bounty hunting, and red team operations. Built on the FastMCP framework, it enables AI agents to autonomously execute security assessments through intelligent tool selection, parameter optimization, and attack chain discovery. The platform exposes 150+ security tools and 12+ autonomous agents via a unified MCP server interface.

## Architecture

```
AI Agent (Claude, Copilot, Cursor, etc.)
        │  MCP protocol (stdin/stdout or HTTP)
        ▼
┌────────────────────────────────────────┐
│        HexStrike MCP Server            │
│  ┌──────────────────────────────────┐  │
│  │  Intelligent Decision Engine     │  │
│  │  ─ Target analysis & strategy    │  │
│  │  ─ Tool selection AI             │  │
│  │  ─ Parameter optimization        │  │
│  │  ─ Attack chain discovery        │  │
│  ├──────────────────────────────────┤  │
│  │  Autonomous Agent Layer          │  │
│  │  ─ Bug bounty workflow manager   │  │
│  │  ─ CTF solver                    │  │
│  │  ─ CVE intelligence              │  │
│  │  ─ Exploit generator             │  │
│  │  ─ Vulnerability correlator      │  │
│  │  ─ Browser agent (Selenium)      │  │
│  ├──────────────────────────────────┤  │
│  │  Security Tool Layer (150+)      │  │
│  │  Network │ Web │ Binary │ Cloud   │  │
│  │  OSINT   │ CTF │ Forensics        │  │
│  ├──────────────────────────────────┤  │
│  │  Visual Engine & Caching         │  │
│  │  ─ Real-time dashboards          │  │
│  │  ─ Vulnerability cards           │  │
│  │  ─ LRU smart caching             │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘
```

### Tool Categories

- **Network & Recon** — nmap, masscan, rustscan, amass, subfinder, nuclei, theharvester
- **Web App Security** — gobuster, feroxbuster, ffuf, nikto, sqlmap, wpscan, dalfox
- **Binary Analysis** — gdb, radare2, binwalk, ghidra, checksec, pwntools, angr
- **Cloud Security** — prowler, trivy, kube-hunter, docker-bench-security
- **CTF & Forensics** — volatility3, foremost, steghide, exiftool
- **OSINT** — sherlock, recon-ng, spiderfoot, shodan-cli

### Core MCP Tools

Key tools exposed via FastMCP: `nmap_scan()` (optimized scanning), `gobuster_scan()` (directory enumeration), `feroxbuster_scan()` (recursive content discovery), `nuclei_scan()` (vulnerability scanning), `sqlmap_scan()` (SQL injection), `prowler_assess()` (cloud security), `ghidra_analyze()` (reverse engineering).

## Key Components

- **Intelligent Decision Engine** — Analyzes targets, selects optimal tools, tunes parameters, and chains attacks. The AI router determines which tool to invoke based on reconnaissance results and testing objectives.
- **12+ Autonomous Agents** — Specialized agents for bug bounty workflows, CTF solving, CVE research, exploit generation, and vulnerability correlation. Each agent has domain-specific knowledge and tool access.
- **Browser Agent** — Headless Chrome automation via Selenium for web application security testing, form interaction, and login workflows.
- **FastMCP Integration** — Native MCP protocol support connects HexStrike to Claude Desktop, VS Code Copilot, Cursor, and any MCP-compatible AI client.
- **Smart Caching System** — LRU eviction caches scan results for repeated operations, reducing redundant tool calls during iterative testing.

### Data Flow

1. AI agent sends MCP request with target specification
2. Decision engine analyzes target profile (technology stack, exposed services)
3. Optimal tools selected and parameterized for the target
4. Tools execute in sequence or parallel based on dependency graph
5. Results cached; consolidated findings returned via MCP response
6. Optional: agents chain multiple tools for attack path discovery

## Related

- [[hexstrike-ai]] — Wiki overview of the project
- [[Hexstrike-redteam]] — Related red team variant with BOAZ payload evasion
- [[nyxstrike]] — Security orchestration platform
- [[sec-af]] — AI-native security auditor (complementary tool)
- [[mcp]] — Model Context Protocol for tool integration
- [[hermes-agent]] — Agent runtime with compatible MCP surface
- [[openclaw]] — Personal AI assistant with MCP security tool integration
