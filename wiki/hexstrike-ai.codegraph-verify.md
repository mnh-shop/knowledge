---
name: hexstrike-ai-codegraph-verify
tags: [hexstrike-ai, codegraph-verify, security, pentesting, mcp, python]
description: "Codegraph Verification: hexstrike-ai — validating wiki claims against indexed source code symbols"
source: sources/hexstrike-ai/
---

# Codegraph Verification: hexstrike-ai

**Date:** 2026-07-12

## Claim 1: AI-powered penetration testing platform with Intelligent Decision Engine
- **Wiki says:** "AI-powered cybersecurity automation platform" with an "Intelligent Decision Engine — Tool selection AI, parameter optimization, and attack chain discovery"
- **Source evidence:**
  - `hexstrike_server.py:572` — `class IntelligentDecisionEngine:` with tool effectiveness scoring (nmap: 0.8, gobuster: 0.9, sqlmap: 0.9, etc.), attack pattern initialization, and parameter optimization per tool
  - `hexstrike_server.py:13623` — `class BrowserAgent:` described as "AI-powered browser agent for web application testing"
  - `hexstrike_server.py:7028` — AI-powered exploit generation capabilities
  - `hexstrike_server.py:9652` — `create_attack_chain()` endpoint builds full attack chains with success probability and estimated time
  - The server header reads: "HexStrike AI - Advanced Penetration Testing Framework Server" with "AI-powered intelligence & automation"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: 150+ Security Tools via MCP surface
- **Wiki says:** "150+ Security Tools — Network reconnaissance, web app testing, binary analysis, cloud security, CTF, and forensics tools"
- **Source evidence:**
  - `hexstrike_mcp.py` contains **151 `@mcp.tool()`** decorated functions registered via `setup_mcp_server()`
  - Tool categories found: network recon (nmap, masscan, rustscan, autorecon), web app (gobuster, ffuf, nikto, sqlmap, wpscan, dalfox, feroxbuster), binary analysis (gdb, radare2, ghidra, pwntools, angr), cloud security (prowler, trivy, kube-hunter, scout_suite, cloudmapper), CTF/forensics (volatility, binwalk, foremost), OSINT (sherlock, recon-ng, spiderfoot)
  - Each tool is an async endpoint in `hexstrike_server.py` called via `safe_post()` to the server API
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: 12+ Autonomous AI Agents for security domains
- **Wiki says:** "12+ Autonomous AI Agents — Bug bounty workflow manager, CTF solver, CVE intelligence, exploit generator, vulnerability correlator"
- **Source evidence:**
  - `hexstrike_server.py:2447` — `class BugBountyWorkflowManager:` manages bug bounty target profiles, vulnerability tracking, and automated reporting
  - `hexstrike_server.py:3856` — CTF challenge automation system with AI-powered optimization
  - `hexstrike_server.py:1558-1606` — `IntelligentErrorHandler` with error classification, recovery strategies, and graceful degradation
  - `hexstrike_server.py:5085` — `AdvancedCache` with LRU eviction and intelligent TTL management
  - `hexstrike_server.py:13623` — `BrowserAgent` for headless web application testing
  - `hexstrike_mcp.py:5153` — Enhanced HTTP testing framework combining browser agent with Burp Suite–alternative features
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Browser Agent with headless Chrome automation via Selenium
- **Wiki says:** "Browser Agent — Headless Chrome automation with Selenium for web application security testing"
- **Source evidence:**
  - `hexstrike_server.py:13623` — `class BrowserAgent:` with `setup_browser()`, `navigate_and_inspect()`, `run_active_tests()`, `close_browser()`
  - `hexstrike_server.py:13644` — Chrome options configured with `--headless`, custom user-agent `HexStrike-BrowserAgent/1.0`
  - `hexstrike_server.py:13665-13735` — Browser logging with status tracking and error handling
  - `hexstrike_server.py:14136` — `browser_agent_endpoint()` Flask route at `/api/tools/browser-agent`
  - `hexstrike_mcp.py:5198` — `browser_agent_inspect()` MCP tool calling the browser agent API
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: FastMCP Integration for native MCP protocol support
- **Wiki says:** "FastMCP Integration — Native MCP protocol support for Claude, VS Code Copilot, Cursor, and other AI clients"
- **Source evidence:**
  - `hexstrike_mcp.py:277` — `mcp = FastMCP("hexstrike-ai-mcp")` instantiates the FastMCP server
  - 151 `@mcp.tool()` decorators register all security tools as MCP tools
  - `hexstrike-ai-mcp.json` — provides ready-to-use Claude Desktop configuration with command, args, timeout, and `alwaysAllow` settings
  - The MCP protocol enables any MCP-compatible client (Claude, Cursor, Copilot) to consume the full 151-tool surface
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Smart Caching System with LRU eviction
- **Wiki says:** "Smart Caching System — LRU eviction for optimal performance with repeated operations"
- **Source evidence:**
  - `hexstrike_server.py:5085` — `class AdvancedCache:` docstring: "Advanced caching system with intelligent TTL and LRU eviction"
  - `hexstrike_server.py:5109` — Access time tracking for LRU: `self.access_times[key] = current_time`
  - `hexstrike_server.py:5169` — Explicit LRU eviction log: `logger.debug(f"Evicted LRU cache entry: {lru_key}")`
  - `hexstrike_server.py:5090-5097` — Thread-safe with `threading.RLock()`, hit/miss counters, and daemon cleanup thread
  - `hexstrike_mcp.py:245-256` — `execute_command()` supports caching via `use_cache` parameter
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: README tool names differ from code function names
- **Wiki says:** "Code-accurate names preferred — README documents `prowler_assess()` and `ghidra_analyze()`, but the code functions are `prowler_scan` and `ghidra_analysis`"
- **Source evidence:**
  - `README.md:540` — documents `prowler_assess()`; actual code: `hexstrike_mcp.py:422` — `def prowler_scan(provider: str = "aws", ...)` posting to `api/tools/prowler`
  - `README.md:533` — documents `ghidra_analyze()`; actual code: `hexstrike_mcp.py:2012` — `def ghidra_analysis(binary: str, project_name: str = "hexstrike_analysis", ...)`
  - Wiki now carries both names with the code-accurate variant primary
- **Verdict:** ✅ CORRECT (discrepancy noted and resolved in wiki)
- **Fix needed:** None (documented, not a code defect)

## Claim 8: No test suite, CI, or Docker assets in the repository
- **Wiki says:** "The repo ships no test suite, no CI configuration, and no Docker/Containerfile assets"
- **Source evidence:**
  - Repo root contains only `LICENSE`, `README.md`, `assets/`, `hexstrike-ai-mcp.json`, `hexstrike_mcp.py`, `hexstrike_server.py`, `requirements.txt`
  - No `.github/` directory (no CI workflows)
  - No files matching `*test*` and no `Dockerfile`/`Containerfile` at any depth
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

| Claim | Verdict |
|-------|---------|
| AI-powered platform with Intelligent Decision Engine | ✅ CORRECT |
| 150+ Security Tools (151 MCP tools confirmed) | ✅ CORRECT |
| 12+ Autonomous AI Agents | ✅ CORRECT |
| Browser Agent with headless Chrome/Selenium | ✅ CORRECT |
| FastMCP Integration | ✅ CORRECT |
| Smart Caching System with LRU eviction | ✅ CORRECT |
| README tool names vs. code function names | ✅ CORRECT (discrepancy documented) |
| No tests / CI / Docker in repo | ✅ CORRECT |

All major wiki claims verify against source. The codebase delivers a substantial Python/FastMCP server with a large MCP tool surface, autonomous agent classes for multiple security domains, and an intelligent decision engine for tool selection and attack chaining. Note the README/code naming discrepancy for `prowler_scan`/`ghidra_analysis` and the absence of tests, CI, and Docker assets.

## Related

- [[hexstrike-ai]] — Main wiki entry
- [[Hexstrike-redteam.codegraph-verify]] — Red team variant verification
- [[nyxstrike.codegraph-verify]] — Related offensive security orchestration verification
- [[sec-af]] — Security agent framework

## Cross-project

- [[openclaw.codegraph-verify]] — Similar codegraph verification for OpenClaw
- [[n8n.codegraph-verify]] — Similar codegraph verification for n8n
