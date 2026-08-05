---
name: Hexstrike-redteam-full-codegraph-verify
tags: [hexstrike, redteam, mcp, security, boaz, penetration-testing, wiki]
description: "Codegraph Verification: Hexstrike-redteam-full — validating wiki claims against indexed source code symbols"
source: sources/Hexstrike-redteam-full/
---

# Codegraph Verification: Hexstrike-redteam-full

**Date:** 2026-07-30

## Claim 1: Byte-identical duplicate of Hexstrike-redteam (commit 89779b7)
- **Wiki says:** This repo is byte-identical to `Hexstrike-redteam` (same commit `89779b7`) — a duplicated vault entry; claims verified against the shared source.
- **Source evidence:**
  - `git -C sources/Hexstrike-redteam rev-parse HEAD` = `89779b7948444b88ae11600799880d6feb8e0094`
  - `git -C sources/Hexstrike-redteam-full rev-parse HEAD` = `89779b7948444b88ae11600799880d6feb8e0094` (identical commit)
  - `diff -rq` on tracked files reports **zero differences** (only `.git/` metadata and `.DS_Store` differ)
- **Verdict:** ✅ CORRECT (duplicate entry; byte-identical to Hexstrike-redteam)

## Claim 2: 137 registered MCP tools (README 127/150+/155+ inconsistent)
- **Wiki says:** 137 registered MCP tools; README's own counts (127/150+/155+) are internally inconsistent.
- **Source evidence:**
  - `hexstrike_mcp.py` contains **137 `@mcp.tool()`** decorators (`grep -c "@mcp.tool()"` = 137) — authoritative disk count
  - `README.md:11` — "127 security tools (53 auto-installed)" (undercount)
  - `README.md:130` — "150+ tools" (overcount)
  - `hexstrike-ai-mcp.json:10` — "155+ tools including 77+ loaders, 12 encoders" (overcount)
  - `BOAZ_beta/loaders/` holds **68 files** (67 `*.c`/`*.py` + `nt.h`); `BOAZ_beta/encoders/` holds **13 encoders** (incl. `bin_to_c_array.py` and `sgn`)
- **Verdict:** ⚠️ PARTIALLY ACCURATE (corrected to 137 tools / 68 loaders / 13 encoders)

## Claim 3: File-ops restricted to BOAZ_beta/ (hexstrike_mcp.py:332-334)
- **Wiki says:** BOAZ MCP file operations are restricted to the `BOAZ_beta/` directory as a security requirement.
- **Source evidence:**
  - `hexstrike_mcp.py:332-334` — "FILE PATH REQUIREMENTS: Input file MUST be inside BOAZ_beta directory (security requirement)"; relative paths enforced (`input_file="payload.exe"` not absolute paths); output written to `BOAZ_beta/output/`
  - `hexstrike_mcp.py:285` — `boaz_generate_payload`; `:481` — `boaz_list_loaders`; `:512` — `boaz_list_encoders`; `:539` — `boaz_analyze_binary`; `:575` — `boaz_validate_options`
- **Verdict:** ✅ CORRECT (replaces the previous strawman "path traversal validation" claim — the wiki never claimed that)

## Claim 4: Two-script architecture (Flask + FastMCP)
- **Wiki says:** The server uses a two-script architecture: `hexstrike_server.py` (Flask-based server) and `hexstrike_mcp.py` (FastMCP-based MCP client for AI agent communication).
- **Source evidence:**
  - `hexstrike_server.py:42` — `from flask import Flask, request, jsonify`; `hexstrike_server.py:97` — `app = Flask(__name__)`
  - `hexstrike_mcp.py:29` — `from mcp.server.fastmcp import FastMCP`; documented as "MCP Client for AI agent communication with HexStrike server" using "FastMCP integration for tool orchestration"
  - `hexstrike_server.py:101` — `API_PORT = int(os.environ.get('HEXSTRIKE_PORT', 8888))` (port 8888)
- **Verdict:** ✅ CORRECT

## Claim 5: EDR/AV evasion + anti-analysis
- **Wiki says:** BOAZ includes EDR/AV evasion via API unhooking, ETW patching, and LLVM obfuscation (Akira/Pluto), plus anti-emulation checks and sleep obfuscation.
- **Source evidence:**
  - `README.md:27-31` — feature list: "EDR/AV Evasion - API unhooking, ETW patching, LLVM obfuscation (Akira/Pluto)" and "Anti-Analysis - Anti-emulation checks, sleep obfuscation, entropy reduction"
  - `BOAZ_beta/evader/` — `etw_pass.c`, `api_untangle.c`, `sleep_encrypt.c`
  - `BOAZ_beta/obfuscate/`, `BOAZ_beta/signature/`, `BOAZ_beta/indirect_syscall/`, `BOAZ_beta/direct_syscall.asm`, `BOAZ_beta/edr_syscall_1.asm`, `edr_syscall_2.asm`, `BOAZ_beta/patch_enum_syscalls.c`
  - `BOAZ_beta/requirements.sh` installs LLVM with Akira/Pluto obfuscators
- **Verdict:** ✅ CORRECT

## Claim 6: ~17,400 line Flask server + dashboards + smart caching
- **Wiki says:** `hexstrike_server.py` is a ~17,400-line Flask server with real-time dashboards, vulnerability cards, and smart caching/adaptive execution.
- **Source evidence:**
  - `hexstrike_server.py` is **17,406 lines** (`wc -l`)
  - `README.md:94-96` — visual vulnerability cards / risk analysis features
  - `README.md:768` — "Modern Visual Engine - Real-time dashboards and progress tracking"
  - `README.md:825` — `GET /api/processes/dashboard` live monitoring dashboard endpoint
  - `README.md:763` — smart caching and adaptive execution
- **Verdict:** ✅ CORRECT

## Claim 7: Auto-install breakdown (README:215-276) — includes Password & Auth, Forensics, Metasploit
- **Wiki says:** 53 auto-installed tools across network (10), web app (19), password & auth (5), binary (13), forensics (16), OSINT (13), cloud (10), and Metasploit.
- **Source evidence:**
  - `README.md:215` — "Network & Reconnaissance (10 tools)"
  - `README.md:223` — "Web Application Security (19 tools)"
  - `README.md:233` — "Password & Authentication (5 tools)"
  - `README.md:240` — "Binary Analysis & RE (13 tools)"
  - `README.md:249` — "Forensics (16 tools)"
  - `README.md:257` — "OSINT & Intelligence (13 tools)"
  - `README.md:265` — "Cloud Security (10 tools)"
  - `README.md:273` — "Metasploit Framework" (msfconsole, msfvenom, searchsploit)
  - Note: the earlier wiki's "CTF (10)" was wrong — that count is Forensics (16); Password & Auth and Metasploit were omitted
- **Verdict:** ⚠️ PARTIALLY ACCURATE (corrected breakdown now matches README:215-276)

## Claim 8: License conflict + install/ contents (no install_hexstrike.sh)
- **Wiki says:** License is conflicted (README badge MIT but no root LICENSE; only BOAZ_beta/LICENSE GPL-3.0), and `install/` contains install_all.sh / install_security_tools.sh / install_system_deps.sh / setup_hexstrike_venv.sh / configure_mcp.sh — there is no install_hexstrike.sh.
- **Source evidence:**
  - `README.md:9` — badge `[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)`; `README.md:970` — "MIT License - see LICENSE file for details."
  - `ls LICENSE*` at repo root: **no match**; only `BOAZ_beta/LICENSE` exists, which is "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
  - `install/` contains: `README.md`, `configure_mcp.sh`, `install_all.sh`, `install_security_tools.sh`, `install_system_deps.sh`, `setup_hexstrike_venv.sh`, `start_server.sh`, `test_server.sh` — **no `install_hexstrike.sh`**
- **Verdict:** ✅ CORRECT (license conflict documented; install script names fixed)

## Summary

All 8 key claims from the Hexstrike-redteam-full wiki have been verified against the source:
- ✅ Byte-identical duplicate of Hexstrike-redteam (same commit 89779b7, zero tracked-file diff)
- ⚠️ 137 registered MCP tools (README 127/150+/155+ inconsistent; 68 loaders / 13 encoders on disk)
- ✅ File-ops restricted to BOAZ_beta/ (hexstrike_mcp.py:332-334) — replaces previous strawman claim
- ✅ Two-script Flask (server.py:42,97) + FastMCP (mcp.py:29) architecture, port 8888
- ✅ EDR/AV evasion + anti-analysis (README:27-31, BOAZ_beta/evader/)
- ✅ 17,406-line Flask server + dashboards (README:768,825) + smart caching (README:763)
- ⚠️ Auto-install breakdown corrected: Network 10, Web 19, Password&Auth 5, Binary 13, Forensics 16, OSINT 13, Cloud 10, Metasploit (README:215-276)
- ✅ License conflict documented (MIT badge, no root LICENSE, BOAZ GPL-3.0); install scripts corrected (install_all.sh, no install_hexstrike.sh)

## Related

- [[Hexstrike-redteam-full]] -- Main wiki entry
- [[Hexstrike-redteam.codegraph-verify]] -- Verification of the byte-identical twin repo

## Cross-project

- [[Claude-Red.codegraph-verify]] -- Similar codegraph verification for security tools
- [[SecOpsAgentKit.codegraph-verify]] -- Similar codegraph verification for SecOpsAgentKit
