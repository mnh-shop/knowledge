---
name: hexstrike-redteam-codegraph-verify
tags: [hexstrike-redteam, codegraph-verify, security, redteam, mcp, python, boaz]
description: "Codegraph Verification: Hexstrike-redteam — validating wiki claims against indexed source code symbols"
source: sources/Hexstrike-redteam/
---

# Codegraph Verification: Hexstrike-redteam

**Date:** 2026-07-30

## Claim 1: 137 registered MCP tools (README's 127/150+/155+ claims inconsistent)
- **Wiki says:** "AI-powered MCP cybersecurity automation platform" with "137 registered MCP tools" — README's own counts (127/150+/155+) are internally inconsistent.
- **Source evidence:**
  - `hexstrike_mcp.py` contains **137 `@mcp.tool()`** decorated functions across 5,048 lines (`grep -c "@mcp.tool()"` = 137) — authoritative disk count
  - `README.md:11` — "127 security tools (53 auto-installed)" (undercount)
  - `README.md:130` — "150+ tools" (overcount)
  - `hexstrike-ai-mcp.json:10` — "155+ tools including 77+ loaders, 12 encoders" (overcount)
  - `hexstrike_mcp.py:267` — `setup_mcp_server()` uses FastMCP to register all tools
- **Verdict:** ⚠️ PARTIALLY ACCURATE (now corrected — wiki reports 137 with README inconsistencies documented)

## Claim 2: 12+ Autonomous AI Agents for adversarial red team automation
- **Wiki says:** "12+ Autonomous AI Agents — Bug bounty workflow, CTF solver, CVE intelligence, exploit generator, vulnerability correlator"
- **Source evidence:**
  - `README.md:746-761` — "12+ Specialized AI Agents" listing IntelligentDecisionEngine, BugBountyWorkflowManager, CTFWorkflowManager, CVEIntelligenceManager, AIExploitGenerator, VulnerabilityCorrelator, TechnologyDetector, RateLimitDetector, FailureRecoverySystem, PerformanceMonitor, ParameterOptimizer, GracefulDegradation
  - `hexstrike_server.py:575` — `class IntelligentDecisionEngine:` with tool effectiveness scoring, attack pattern initialization, and per-tool parameter optimization (nmap, gobuster, nuclei, sqlmap, ffuf, hydra, ghidra, pwntools, etc.)
  - `hexstrike_server.py:9643` — `@app.route("/api/intelligence/create-attack-chain")` endpoint with success probability and estimated time calculations
- **Verdict:** ✅ CORRECT

## Claim 3: BOAZ payload evasion — 68 loaders + 13 encoders (README's 77+/12 overstate)
- **Wiki says:** "BOAZ Payload Evasion — 68 process injection loaders, 13 encoding schemes (AES, ChaCha20, UUID, XOR)"
- **Source evidence:**
  - `BOAZ_beta/loaders/` contains **68 files** (67 `*.c`/`*.py` loader sources + `nt.h`): includes `loader1.c`, `loader1.dll.c`, shellcode injection, process hollowing, thread injection variants
  - `BOAZ_beta/encoders/` contains **13 encoders**: `bin2aes.py`, `bin2base45.py`, `bin2base58.py`, `bin2base64.py`, `bin2chacha.py`, `bin2des.py`, `bin2ipv4.py`, `bin2mac.py`, `bin2rc4.py`, `bin2uuid.py`, `bin2xor.py`, `bin_to_c_array.py`, `sgn` (Shikata Ga Nai)
  - `BOAZ_beta/README.md` confirms AES, ChaCha20, UUID, XOR among the encoding schemes
  - The README's "77+ loaders, 12 encoders" badge overstates both counts (68/13 on disk)
- **Verdict:** ⚠️ PARTIALLY ACCURATE (now corrected — wiki reports 68 loaders / 13 encoders)

## Claim 4: EDR/AV bypass with API unhooking, ETW patching, LLVM obfuscation
- **Wiki says:** "EDR/AV Bypass — API unhooking, ETW patching, LLVM obfuscation (Akira/Pluto), anti-emulation"
- **Source evidence:**
  - `BOAZ_beta/evader/` — evasion techniques incl. `etw_pass.c`, `api_untangle.c`, `sleep_encrypt.c`
  - `BOAZ_beta/obfuscate/` — Obfuscation modules
  - `BOAZ_beta/signature/` — Signature manipulation tools
  - `BOAZ_beta/indirect_syscall/` — Indirect syscall implementations (`indirect_syscall.asm`)
  - `BOAZ_beta/direct_syscall.asm` — Direct syscall assembly
  - `BOAZ_beta/edr_syscall_1.asm`, `edr_syscall_2.asm` — EDR-aware syscall implementations
  - `BOAZ_beta/patch_enum_syscalls.c` — Syscall enumeration patching
  - `BOAZ_beta/requirements.sh` installs LLVM with Akira/Pluto obfuscators
- **Verdict:** ✅ CORRECT

## Claim 5: BOAZ MCP tools + file-ops restricted to BOAZ_beta/
- **Wiki says:** Five BOAZ MCP tools (generate_payload, list_loaders, list_encoders, analyze_binary, validate_options), with file operations restricted to the `BOAZ_beta/` directory.
- **Source evidence:**
  - `hexstrike_mcp.py:285` — `boaz_generate_payload`
  - `hexstrike_mcp.py:481` — `boaz_list_loaders`
  - `hexstrike_mcp.py:512` — `boaz_list_encoders`
  - `hexstrike_mcp.py:539` — `boaz_analyze_binary`
  - `hexstrike_mcp.py:575` — `boaz_validate_options`
  - `hexstrike_mcp.py:332-334` — FILE PATH REQUIREMENTS: "Input file MUST be inside BOAZ_beta directory (security requirement)"; relative paths enforced
- **Verdict:** ✅ CORRECT

## Claim 6: 7 tool categories (README:503-683)
- **Wiki says:** 137 MCP-registered tools across 7 categories: Network, Web, Auth, Binary, Cloud, CTF&Forensics, OSINT.
- **Source evidence:**
  - `README.md:503` — "Network Reconnaissance & Scanning (25+ Tools)"
  - `README.md:526` — "Web Application Security Testing (40+ Tools)"
  - `README.md:578` — "Authentication & Password Security (12+ Tools)"
  - `README.md:596` — "Binary Analysis & Reverse Engineering (25+ Tools)"
  - `README.md:626` — "Cloud & Container Security (20+ Tools)"
  - `README.md:652` — "CTF & Forensics Tools (20+ Tools)"
  - `README.md:683` — "Bug Bounty & OSINT Arsenal (20+ Tools)"
- **Verdict:** ✅ CORRECT (7 categories; the wiki previously listed 6, omitting Authentication)

## Claim 7: Python FastMCP + Flask architecture, port 8888
- **Wiki says:** FastMCP (hexstrike_mcp.py) client + Flask (hexstrike_server.py) server, port 8888.
- **Source evidence:**
  - `hexstrike_mcp.py:29` — `from mcp.server.fastmcp import FastMCP`
  - `hexstrike_server.py:42` — `from flask import Flask, request, jsonify`
  - `hexstrike_server.py:97` — `app = Flask(__name__)`
  - `hexstrike_server.py:101` — `API_PORT = int(os.environ.get('HEXSTRIKE_PORT', 8888))`
  - `hexstrike_server.py:575` — `class IntelligentDecisionEngine:`
  - `hexstrike_server.py:9643` — `@app.route("/api/intelligence/create-attack-chain", methods=["POST"])`
- **Verdict:** ✅ CORRECT

## Claim 8: License conflict — MIT badge vs. no root LICENSE (BOAZ_beta/LICENSE is GPL-3.0)
- **Wiki says:** README badge claims MIT, but no LICENSE file exists at repo root; the only license on disk (BOAZ_beta/LICENSE) is GPL-3.0.
- **Source evidence:**
  - `README.md:9` — badge `[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)` — links to a `LICENSE` file that does **not** exist at repo root
  - `README.md:970` — "MIT License - see LICENSE file for details."
  - `ls LICENSE*` at repo root: **no match**
  - `BOAZ_beta/LICENSE` — "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
- **Verdict:** ⚠️ INCONSISTENT (documented as a license conflict in the wiki)

## Summary

| Claim | Verdict |
|-------|---------|
| 137 registered MCP tools (README 127/150+/155+ inconsistent) | ⚠️ PARTIALLY ACCURATE (corrected) |
| 12+ Autonomous AI Agents (README:746-761, server.py:575) | ✅ CORRECT |
| BOAZ 68 loaders + 13 encoders (README 77+/12 overstated) | ⚠️ PARTIALLY ACCURATE (corrected) |
| EDR/AV bypass techniques (evader/, obfuscate/, syscalls) | ✅ CORRECT |
| 5 BOAZ MCP tools + BOAZ_beta/ file-ops restriction | ✅ CORRECT |
| 7 tool categories incl. Auth (README:503-683) | ✅ CORRECT (was 6) |
| FastMCP + Flask, port 8888, attack-chain endpoint | ✅ CORRECT |
| License conflict (MIT badge, no root LICENSE, BOAZ GPL-3.0) | ⚠️ INCONSISTENT (documented) |

The codebase is a Python+FastMCP server that extends the upstream hexstrike-ai with the BOAZ red-team payload evasion subsystem. Disk counts are authoritative: 137 MCP tools, 68 loaders, 13 encoders — the README's 127/150+/155+ and 77+/12 figures are internally inconsistent and overstated. The platform is Python-based, not Go-based.

## Related

- [[Hexstrike-redteam]] — Main wiki entry
- [[Hexstrike-redteam-full.codegraph-verify]] — Byte-identical duplicate repo verification
- [[hexstrike-ai.codegraph-verify]] — Upstream hexstrike-ai verification
- [[nyxstrike.codegraph-verify]] — Related offensive security orchestration verification

## Cross-project

- [[openclaw.codegraph-verify]] — Similar codegraph verification for OpenClaw
- [[n8n.codegraph-verify]] — Similar codegraph verification for n8n
