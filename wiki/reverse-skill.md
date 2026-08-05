---
name: reverse-skill
description: Reverse Engineering / Authorized Penetration Testing / Security Research Skill Router Pack for AI agents
tags:
  - reverse-skill
  - security
  - ai-agents
  - automation
  - harness
  - agent
source: sources/reverse-skill/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# reverse-skill

AI-powered routing skill pack for reverse engineering, penetration testing, and security research. Provides an on-demand toolchain bootstrapping system with self-evolving knowledge base.

## Description

reverse-skill is a comprehensive skill router pack designed for AI agents (Claude Code, Codex CLI, Cursor, Cline, Windsurf) to handle reverse engineering, authorized penetration testing, and security research tasks. It solves the problem of AI agents not knowing which methodology or toolchain to use when facing APK analysis, binary reverse engineering, frontend JS encryption, packet capture, or CTF challenges.

The system follows a clear workflow: user task → RULES.md → Skill Router → target skill → tools/MCP/scripts → report + experience logs.

## Key Features

- **Skill Router Architecture**: Central routing matrix dispatches tasks by target type, user intent, and toolchain availability
- **Cross-Platform Support**: Windows, Kali Linux, Ubuntu/Debian, macOS with platform-specific deployment paths
- **Toolchain Integration**: MCP-enabled workflows for IDA Pro (72 tools), jshookmcp, burp-mcp, nmap, frida, jadx, radare2, and 20+ pentest tools
- **CTF Competition Stack**: 40+ sub-skills covering Web/Pwn/Reverse/Mobile/Crypto/Cloud/Active Directory/Forensics
- **Auto-Evolving Experience**: Field-journal system writes back task experience for future reference and reuse

## Architecture Notes

The system operates on two layers:

1. **Bootstrap layer** (`README_AI.md`): OS detection, tool index refresh, platform routing
2. **Execution layer** (`skills/SKILL.md` + `skills/routing.md`): Route first, execute second paradigm

Key architectural files:
- `RULES.md` - Global routing rules and mandatory behavior chain (steps 0-14; verified steps 8-14 at lines 164-172)
- `skills/MASTER-ROUTING.md` + `skills/routing.md` / `routing_zh.md` - Primary + full routing matrices
- `skills/tool-index.md.template` - Template for the auto-generated local tool availability registry
- `skills/ops/` - Operational layer: `scope-contract`, `role-map`, `evidence-finding-path`, `IDENTITY` (+ sandbox-profile, timeline-workitem, skill-supply-chain)
- `CTF-Sandbox-Orchestrator/` - Dedicated CTF orchestration subsystem (43 entries)
- `reports/`, `docs/`, `kali/` - Output reports, documentation, and Kali-specific tooling

The "precedent-first" design requires reading authorization context (`field-journal/precedent-auth.md`) before any security operations.

## Skills / Tools

Skills organized by scenario (all under `skills/` — ~40 sub-skills total):

- `apk-reverse/` — Android APK unpacking, jadx decompilation, smali modification, Frida hook
- `ida-reverse/` — IDA Pro MCP HTTP server with decompilation and cross-reference tools (72 MCP tools)
- `js-reverse/` — Frontend signature analysis, encrypted parameter reverse, browser automation
- `radare2/` — CLI binary reconnaissance, disassembly, patching
- `pentest-tools/` — Nmap, Nuclei, SQLMap, FFUF, Hashcat MCP workflows
- `pwn-chain/` — Stack/heap/kernel exploit development from reverse engineering
- `patch-diff-exploit/` — N-day analysis from vendor patches to PoC weaponization
- `firmware-pentest/` — OWASP FSTM nine-stage firmware penetration chain
- `edr-bypass-re/` — Red-team EDR hook table/ETW/AMSI bypass techniques
- `browser-automation/` — Playwright browser operations + desktop automation
- `attack-chain/` — Multi-stage attack path planning and execution orchestration

Additional sub-skills (not previously listed in wiki):
- `ghidra-reverse/`, `malware-analysis/`, `mobile-reverse/`, `dotnet-reverse/`, `go-rust-reverse/`, `macos-reverse/`, `protocol-reverse/`, `radio-sdr/`, `wifi-wireless/`, `ot-ics/`, `thick-client/`, `cloud-k8s/`, `database-security/`, `email-security/`, `llm-security/`, `supply-chain-security/`, `identity-federation/`, `api-security/`, `code-audit/`, `digital-forensics/`, `threat-hunting/`, `windows-ad/`, `hardware-security/`, `binary-diff/`, `browser-extension-reverse/`, `reverse-engineering/`

**Ops layer (`skills/ops/`):** `scope-contract` (scope/auth contracts), `role-map` (role assignment), `evidence-finding-path` (Evidence → Finding → Path chains), `IDENTITY` (agent identity), plus `sandbox-profile`, `timeline-workitem`, `skill-supply-chain`.

**Supporting trees:** `reports/` (task reports), `docs/` (ARCHITECTURE, OVERVIEW, PLATFORMS, PACKAGE-SECURITY-AUDIT...), `kali/` (Kali-specific tooling incl. `scripts/refresh-tool-index.sh` and `README-kali.md`).

## Deployment / Use

**Installation:**
```bash
git clone https://github.com/zhaoxuya520/reverse-skill.git
```

**Tool index refresh:**
```bash
# Linux/macOS
bash skills/scripts/refresh-tool-index.sh

# Windows
powershell -File skills/scripts/refresh-tool-index.ps1

# Kali Linux
bash kali/scripts/refresh-tool-index.sh
```

**Bootstrap missing tools:**
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill-root>\skills\scripts\bootstrap-reverse.ps1" -Capability @('jadx','frida','nmap')
```
> Note: the bootstrap scripts live in `skills/scripts/` (`bootstrap-reverse.ps1` / `bootstrap-reverse.sh`), not at repo root — root `scripts/` holds only `refresh-tool-index.ps1`.

## Related

- [[hermes-agent]] — AI agent runtime that can integrate this skill pack
- [[SecuritySkills]] — Related security skill collections
- [[agent-rules-books]] — Security rules and methodology documentation