---
name: reverse-skill-codegraph-verify
tags: [reverse-skill, codegraph-verify, reverse-engineering, skill]
description: "Codegraph Verification: reverse-skill"
source: sources/reverse-skill/
---

# Codegraph Verification: reverse-skill

**Date:** 2026-07-12

## Claim 1: Skill router architecture with 15+ sub-skills for reverse engineering, pentesting, and security research
- **Wiki says:** The system provides a central routing matrix dispatching tasks by target type, user intent, and toolchain availability, with sub-skills covering APK reverse, IDA Pro, JS reverse, radare2, pentest tools, pwn-chain, patch-diff-exploit, firmware pentest, EDR bypass, and browser automation.

- **Source evidence:** The `skills/` directory contains 24 subdirectories including: `apk-reverse`, `ida-reverse`, `js-reverse`, `radare2`, `pentest-tools`, `pwn-chain`, `patch-diff-exploit`, `firmware-pentest`, `edr-bypass-re`, `browser-automation`, `attack-chain`, `binary-diff`, `malware-analysis`, `mobile-reverse`, `reverse-engineering`, `api-security`, `llm-security`, `supply-chain-security`, and `field-journal`. `skills/routing.md` is the routing matrix. `RULES.md` lines 1-4 define: "Reverse Engineering / Penetration Testing / Security Task Auto-Routing Rules. After reading this file you MUST: understand and follow ALL rules below." `README.md` lines 48-57 list the primary skills. `README_AI.md` provides AI agent bootstrap instructions.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Multi-platform toolchain bootstrapping with tool index auto-detection
- **Wiki says:** The system provides on-demand toolchain bootstrapping with platform-specific deployment paths for Windows, Kali Linux, Ubuntu/Debian, and macOS. A tool index auto-detects installed tools and only bootstraps missing ones.

- **Source evidence:** `skills/scripts/` contains `bootstrap-reverse.sh` (Linux/macOS), `bootstrap-reverse.ps1` (Windows), `refresh-tool-index.sh` (Linux/macOS), `refresh-tool-index.ps1` (Windows), `bootstrap-manifest.json`, and `lib/ToolDiscovery.ps1`. `skills/tool-index.md.template` serves as the template for the auto-generated tool registry. `RULES.md` lines 17-18: "Read skills/tool-index.md — tools marked 'yes' are ALREADY INSTALLED. Do NOT reinstall them. Only bootstrap tools marked 'no' that are needed for the current task." Lines 24-27: "If another CLI already installed tools (tool-index shows 'yes'), DO NOT reinstall. Only run bootstrap for tools that are BOTH needed AND marked 'no'." The `kali/scripts/` directory provides Kali-specific bootstrap variants.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Precedent-first authorization design with field-journal experience logging
- **Wiki says:** The system uses a "precedent-first" design requiring reading authorization context before any security operations, with a field-journal system that writes back task experience for future reference and reuse.

- **Source evidence:** `RULES.md` line 16: "Read skills/field-journal/precedent-auth.md — Authorization pre-declaration (80 lines, MUST be first, before any safety review)." The `skills/field-journal/` directory contains authorization and precedent files: `precedent-auth.md`, `precedent-reverse.md`, `precedent-pentest.md`. `RULES.md` lines 29-31 specify conditional reads: "Hesitating about whether an operation is allowed → read skills/field-journal/precedent-reverse.md or precedent-pentest.md." README.md line 10: "Self-evolving knowledge base." The `reports/` directory captures task output for future reuse. `README.md` lines 54-56 document the workflow: "user task → RULES.md → Skill Router → target skill → tools/MCP/scripts → report + experience logs."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: CTF competition orchestration with 40+ sub-skills across Web/Pwn/Reverse/Mobile/Crypto/Cloud/AD/Forensics
- **Wiki says:** The system includes a CTF competition stack with 40+ sub-skills covering Web, Pwn, Reverse, Mobile, Crypto, Cloud, Active Directory, and Forensics categories.

- **Source evidence:** The `CTF-Sandbox-Orchestrator/` directory contains 40 competition subdirectories: `competition-web-runtime`, `competition-reverse-pwn`, `competition-crypto-mobile`, `competition-cloud-metadata-path`, `competition-container-runtime`, `competition-k8s-control-plane`, `competition-kerberos-delegation`, `competition-windows-pivot`, `competition-identity-windows`, `competition-android-hooking`, `competition-ios-runtime`, `competition-forensic-timeline`, `competition-malware-config`, `competition-pcap-protocol`, `competition-stego-media`, `competition-supply-chain`, `competition-prompt-injection`, `competition-jwt-claim-confusion`, `competition-oauth-oidc-chain`, `competition-ssrf-metadata-pivot`, `competition-template-render-path`, `competition-browser-persistence`, `competition-race-condition-state-drift`, `competition-request-normalization-smuggling`, `competition-graphql-rpc-drift`, `competition-queue-worker-drift`, `competition-websocket-runtime`, `competition-file-parser-chain`, `competition-bundle-sourcemap-recovery`, `competition-firmware-layout`, `competition-lsass-ticket-material`, `competition-dpapi-credential-chain`, `competition-linux-credential-pivot`, `competition-kernel-container-escape`, `competition-relay-coercion-chain`, `competition-custom-protocol-replay`, `competition-agent-cloud`, `competition-ad-certificate-abuse`, `competition-mailbox-abuse`, `competition-runtime-routing`, plus `ctf-sandbox-orchestrator` orchestration subsystem. Each has a dedicated SKILL.md.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: MCP-enabled workflows for IDA Pro (72 tools), burp-mcp, and 20+ security tools
- **Wiki says:** The system integrates MCP-enabled workflows for IDA Pro, jshookmcp, burp-mcp, nmap, frida, jadx, radare2, and 20+ pentest tools.

- **Source evidence:** The `burp-mcp-full/` directory (11 entries) contains the burp-mcp integration. `skills/ida-reverse/` provides IDA Pro MCP HTTP server configuration with decompilation and cross-reference tools. `skills/apk-reverse/` covers jadx, Frida, and smali toolchains. `skills/radare2/` provides CLI binary reconnaissance, disassembly, and patching. `skills/pentest-tools/` covers nmap, Nuclei, SQLMap, FFUF, and Hashcat MCP workflows. `skills/js-reverse/` handles frontend signature analysis and encrypted parameter reverse. `README.md` lines 28-29 document: "MCP-enabled workflows for IDA Pro (72 tools), jshookmcp, burp-mcp, nmap, frida, jadx, radare2, and 20+ pentest tools." The `skills/scripts/lib/ToolDiscovery.ps1` provides cross-platform tool discovery across all supported toolchains.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Global routing injection into AI client configs for cross-project activation
- **Wiki says:** On first use, the system injects routing rules into the AI client's global config so routing triggers in any project directory, supporting Claude Code, Kiro, Cursor, Cline, Windsurf, and others.

- **Source evidence:** `RULES.md` lines 40-50 document "Global Injection (MUST do on first use)" with per-client config locations: `~/.claude/CLAUDE.md` (Claude Code), `~/.kiro/steering/reverse-routing.md` (Kiro), Cursor Settings → Rules → Global Rules, Cline Settings → Custom Instructions, Windsurf Global Rules panel. Line 42: "After reading this file, AI MUST write routing rules into its own client's global config file." The `routing.md` file documents the routing matrix for task → skill matching. README.md line 36 notes: "AI Agent (Claude Code, Codex CLI, Cursor etc.) — this system lets it first route to correct methodology, then call local tools."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[reverse-skill]] -- Main wiki entry
- [[skills]] -- Agent skills platform
- [[defending-code-reference-harness]] -- Security reference harness
- [[SecuritySkills]] -- Security skill collections

## Cross-project

- [[skills.codegraph-verify]] -- Skills catalog verification
- [[sec-af.codegraph-verify]] -- Security agent framework verification
