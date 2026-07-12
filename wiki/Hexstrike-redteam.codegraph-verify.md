---
name: hexstrike-redteam-codegraph-verify
tags: [hexstrike-redteam, codegraph-verify, security, redteam, mcp, python, boaz]
description: "Codegraph Verification: Hexstrike-redteam — validating wiki claims against indexed source code symbols"
source: sources/Hexstrike-redteam/
---

# Codegraph Verification: Hexstrike-redteam

**Date:** 2026-07-12

## Claim 1: AI-powered penetration testing with FastMCP and 127 security tools
- **Wiki says:** "AI-powered MCP cybersecurity automation platform" with "127 Security Tools (53 auto-installed)"
- **Source evidence:**
  - `hexstrike_mcp.py` contains **137 `@mcp.tool()`** decorated functions across 5,048 lines — exceeds the claimed 127.
  - The README states "127 security tools (53 auto-installed)" and line 11 describes "Advanced AI-powered penetration testing MCP framework with 127 security tools"
  - `hexstrike_mcp.py` header: "HexStrike AI MCP Client — Enhanced AI Agent Communication Interface" with "Bug Bounty | CTF | Red Team | Security Research"
  - The platform is **Python-based** (FastMCP), not Go-based as sometimes described externally
  - `hexstrike_mcp.py:267` — `setup_mcp_server()` uses FastMCP to register all tools
- **Verdict:** ⚠️ PARTIALLY ACCURATE
- **Fix needed:** The actual MCP tool count is 137 (not 127), and the platform is Python+FastMCP, not Go-based

## Claim 2: 12+ Autonomous AI Agents for adversarial red team automation
- **Wiki says:** "12+ Autonomous AI Agents — Bug bounty workflow, CTF solver, CVE intelligence, exploit generator, vulnerability correlator"
- **Source evidence:**
  - `hexstrike_server.py:575` — `class IntelligentDecisionEngine:` with tool effectiveness scoring, attack pattern initialization, and per-tool parameter optimization (nmap, gobuster, nuclei, sqlmap, ffuf, hydra, ghidra, pwntools, etc.)
  - `hexstrike_server.py:2098` — AI-powered exploit development and enhancement functions
  - `hexstrike_server.py:9652` — `create_attack_chain()` endpoint with success probability and estimated time calculations
  - `hexstrike_mcp.py:285-575` — Five dedicated BOAZ MCP tools: `boaz_generate_payload`, `boaz_list_loaders`, `boaz_list_encoders`, `boaz_analyze_binary`, `boaz_validate_options`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: BOAZ payload evasion with 77+ process injection loaders
- **Wiki says:** "BOAZ Payload Evasion — 77+ process injection loaders, 12 encoding schemes (AES, ChaCha20, UUID, XOR)"
- **Source evidence:**
  - `BOAZ_beta/loaders/` contains **68 loader files** (not 77+): includes `loader1.c`, `loader1.dll.c`, shellcode injection, process hollowing, thread injection variants
  - `BOAZ_beta/encoders/` contains **13 encoders** (one more than claimed): `bin2aes.py`, `bin2base45.py`, `bin2base58.py`, `bin2base64.py`, `bin2chacha.py`, `bin2des.py`, `bin2ipv4.py`, `bin2mac.py`, `bin2rc4.py`, `bin2uuid.py`, `bin2xor.py`, `bin_to_c_array.py`, `sgn` (Shikata Ga Nai)
  - `BOAZ_beta/README.md` confirms AES, ChaCha20, UUID, XOR among the encoding schemes
  - `boaz/boaz_manager.py` (17KB) provides the orchestration layer for BOAZ operations
  - The README explicitly claims "77+ loaders, 12 encoders" in the badge header
- **Verdict:** ⚠️ PARTIALLY ACCURATE
- **Fix needed:** Loader count is 68 (not 77+). Encoder count is 13 (not 12). The wiki's 12 encoding schemes is close but slightly undercounts; 77+ loaders is an overestimate.

## Claim 4: EDR/AV bypass with API unhooking, ETW patching, LLVM obfuscation
- **Wiki says:** "EDR/AV Bypass — API unhooking, ETW patching, LLVM obfuscation (Akira/Pluto), anti-emulation"
- **Source evidence:**
  - `BOAZ_beta/evader/` — 27-item directory with evasion techniques
  - `BOAZ_beta/obfuscate/` — Obfuscation modules
  - `BOAZ_beta/signature/` — Signature manipulation tools
  - `BOAZ_beta/indirect_syscall/` — Indirect syscall implementations (`indirect_syscall.asm`)
  - `BOAZ_beta/direct_syscall.asm` — Direct syscall assembly
  - `BOAZ_beta/edr_syscall_1.asm`, `edr_syscall_2.asm` — EDR-aware syscall implementations
  - `BOAZ_beta/patch_enum_syscalls.c` — Syscall enumeration patching
  - `BOAZ_beta/requirements.sh` installs LLVM with Akira/Pluto obfuscators
  - `BOAZ_beta/Stardust/` — Additional evasion component
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: 12+ encoding/encryption schemes for payload obfuscation
- **Wiki says:** "12 encoding schemes (AES, ChaCha20, UUID, XOR)"
- **Source evidence:**
  - `BOAZ_beta/encoders/` directory contains **13 encoder scripts**:
    - `bin2aes.py` — AES encryption
    - `bin2base45.py`, `bin2base58.py`, `bin2base64.py` — Base encoding variants
    - `bin2chacha.py` — ChaCha20 stream cipher
    - `bin2des.py` — DES encryption
    - `bin2ipv4.py` — IPv4伪装 encoding
    - `bin2mac.py` — MAC address format encoding
    - `bin2rc4.py` — RC4 stream cipher
    - `bin2uuid.py` — UUID format encoding
    - `bin2xor.py` — XOR obfuscation
    - `bin_to_c_array.py` — C array byte format
    - `sgn/` — Shikata Ga Nai (polymorphic instruction decoder)
  - `boaz/encoder_reference.py` — Reference documentation for encoders
- **Verdict:** ⚠️ PARTIALLY ACCURATE
- **Fix needed:** The count should be 13 encoders (not 12); the wiki omits `bin_to_c_array.py` and/or `sgn` in its count

## Claim 6: Attack chain automation with Intelligent Decision Engine
- **Wiki says:** "Intelligent Decision Engine — Tool selection AI, parameter optimization, attack chain discovery"
- **Source evidence:**
  - `hexstrike_server.py:575` — `IntelligentDecisionEngine` class with `_initialize_tool_effectiveness()` (scores 30+ tools), `_initialize_attack_patterns()`, `_initialize_technology_signatures()`
  - `hexstrike_server.py:814` — `analyze_target()` resolves domains, detects technologies, calculates attack surface
  - `hexstrike_server.py:974` — `select_optimal_tools()` picks tools based on target profile and objective
  - `hexstrike_server.py:1006` — `optimize_parameters()` per-tool parameter optimization (nmap, gobuster, nuclei, sqlmap, ffuf, hydra, rustscan, masscan, ghidra, pwntools, angr, prowler, scout_suite)
  - `hexstrike_server.py:9644` — `create_attack_chain()` Flask endpoint builds full multi-step attack chains
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

| Claim | Verdict |
|-------|---------|
| AI-powered FastMCP platform with 127 tools (actual: 137 tools) | ⚠️ PARTIALLY ACCURATE |
| 12+ Autonomous AI Agents | ✅ CORRECT |
| BOAZ 77+ loaders (actual: 68 loaders) | ⚠️ PARTIALLY ACCURATE |
| EDR/AV bypass techniques | ✅ CORRECT |
| 12 encoding schemes (actual: 13 encoders) | ⚠️ PARTIALLY ACCURATE |
| Attack chain automation with Intelligent Decision Engine | ✅ CORRECT |

The codebase is a Python+FastMCP server that extends the upstream hexstrike-ai with the BOAZ red-team payload evasion subsystem. Loader counts in the README (77+) exceed the actual filesystem count (68). Encoder count (13) exceeds the claimed 12. The platform is Python-based, not Go-based.

## Related

- [[Hexstrike-redteam]] — Main wiki entry
- [[hexstrike-ai.codegraph-verify]] — Upstream hexstrike-ai verification
- [[nyxstrike.codegraph-verify]] — Related offensive security orchestration verification
- [[kali-pentest]] — Kali Linux integration reference
- [[sec-af]] — Security agent framework

## Cross-project

- [[openclaw.codegraph-verify]] — Similar codegraph verification for OpenClaw
- [[n8n.codegraph-verify]] — Similar codegraph verification for n8n
