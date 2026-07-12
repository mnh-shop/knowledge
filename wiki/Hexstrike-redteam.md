---
name: hexstrike-redteam
tags: [Hexstrike-redteam, python, mcp, security, ai-llm, ai-agents, multi-agent, orchestration, tool-calling]
description: "AI-powered cybersecurity automation MCP platform with BOAZ red team payload evasion (127 tools, 12+ agents, 77+ loaders)"
source: sources/Hexstrike-redteam/
---

# Hexstrike RedTeam

**AI-powered MCP cybersecurity automation platform** with BOAZ red team integration. Features 127 security tools (53 auto-installed), 12+ autonomous AI agents, and advanced payload evasion capabilities including 77+ process injection loaders and 12 encoding schemes.

## What is it?

Hexstrike-redteam is an MCP (Model Context Protocol) server that provides AI agents with comprehensive penetration testing capabilities. Built on FastMCP framework, it enables autonomous security assessment through AI-driven tool selection, parameter optimization, and attack chain discovery.

Key features:
- **127 Security Tools** — Network scanning, web app testing, binary analysis, cloud security, CTF, and forensics tools
- **12+ Autonomous AI Agents** — Bug bounty workflow, CTF solver, CVE intelligence, exploit generator, vulnerability correlator
- **BOAZ Payload Evasion** — 77+ process injection loaders, 12 encoding schemes (AES, ChaCha20, UUID, XOR)
- **EDR/AV Bypass** — API unhooking, ETW patching, LLVM obfuscation (Akira/Pluto), anti-emulation
- **Browser Automation** — Headless Chrome with Selenium for web application security testing
- **FastMCP Integration** — Native MCP protocol support for Claude, VS Code Copilot, Cursor, and other AI clients

## Architecture

Multi-agent architecture with intelligent decision engine:

```
AI Agent → HexStrike MCP Server → [Tools, Agents, BOAZ Engine, Visual Engine]
```

The platform separates concerns through:
- **Intelligent Decision Engine** — Tool selection AI, parameter optimization, attack chain discovery
- **Autonomous Agents** — Specialized agents for different security domains (bug bounty, CTF, CVE intel)
- **BOAZ Payload Engine** — Processes injection via syscall, stealth, memory guard, threadless, VEH/VCH techniques
- **Security Tool Layer** — 127 integrated tools across 6 categories (network, web, cloud, binary, CTF, OSINT)

## Skills & Tools

**BOAZ MCP Tools** (file operations restricted to `BOAZ_beta/` directory):
- `boaz_generate_payload` — Generate evasive payloads with loader/encoding selection
- `boaz_list_loaders` — List 77+ injection loaders filtered by category
- `boaz_list_encoders` — List 12 encoding/encryption schemes
- `boaz_analyze_binary` — Calculate Shannon entropy for evasion assessment
- `boaz_validate_options` — Validate loader/encoder compatibility

**Security Tool Categories:**
- Network & Recon (nmap, masscan, rustscan, amass, subfinder, nuclei)
- Web App Security (gobuster, feroxbuster, ffuf, nikto, sqlmap, wpscan, dalfox)
- Binary Analysis (gdb, radare2, binwalk, ghidra, checksec, pwntools, angr)
- Cloud Security (prowler, trivy, kube-hunter, docker-bench-security)
- CTF & Forensics (volatility3, foremost, steghide, exiftool)
- OSINT (sherlock, recon-ng, spiderfoot, shodan-cli)

## Deployment

**Quick Setup:**
```bash
git clone https://github.com/Yenn503/Hexstrike-redteam.git hexstrike-ai
cd hexstrike-ai
python3 -m venv hexstrike-env
source hexstrike-env/bin/activate
pip3 install -r requirements.txt
cd BOAZ_beta && bash requirements.sh  # Install MinGW, NASM, LLVM obfuscators
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
      "args": ["hexstrike_mcp.py", "--server", "http://localhost:8888"]
    }
  }
}
```

## Related

- [[mcp]] — Model Context Protocol for tool integration
- [[security]] — Security-focused agent ecosystem
- [[CyberStrikeAI]] — Similar Go-based security testing platform
- [[hermes-agent]] — Agent runtime with MCP support
- [[goclaw]] — Go-based agent gateway with compatible MCP surface