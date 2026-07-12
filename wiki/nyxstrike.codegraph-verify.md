---
name: nyxstrike-codegraph-verify
tags: [nyxstrike, codegraph-verify, security, orchestration, mcp, python, pentest]
description: "Codegraph Verification: nyxstrike — validating wiki claims against indexed source code symbols"
source: sources/nyxstrike/
---

# Codegraph Verification: nyxstrike

**Date:** 2026-07-12

## Claim 1: 185+ security tools across categories with effectiveness scoring
- **Wiki says:** "185+ Security Tools organized across 12 categories including network reconnaissance, web exploitation, wireless security, OSINT, password attacks, and cloud/API security. Each tool is registered with effectiveness scoring (0.0–1.0) for AI decision-making."
- **Source evidence:**
  - `tool_registry.py` contains **173 tool definitions** with `"desc"` keys (not 185+)
  - Each tool has an `"effectiveness"` float (0.0–1.0), e.g., `nmap: 0.90`, `gobuster: 0.90`, `nuclei: 0.85`, `ffuf: 0.93`
  - Tools span **21 distinct categories**, not 12: `active_directory`, `ai_assist`, `api`, `binary`, `brute_force`, `cloud`, `data_processing`, `database`, `essential`, `exploitation`, `fingerprint`, `forensics`, `intelligence`, `lateral_movement`, `network_recon`, `osint`, `vulnerability_intelligence`, `web_recon`, `web_scan`, `web_vuln`, `wifi_pentest`
  - `tool_registry.py:34-50` — `_validate_registry()` validates every tool definition at import time, rejecting entries with missing required keys or out-of-range effectiveness
  - 52 `mcp_tools/` directories and 56 `server_api/` endpoints implement the tool surface across Flask REST routes
- **Verdict:** ⚠️ PARTIALLY ACCURATE
- **Fix needed:** Actual tool count is 173 (not 185+). Actual category count is 21 (not 12). The wiki overestimates tool count but underestimates category breadth.

## Claim 2: MCP-compatible interface with JSON-RPC tool exposure
- **Wiki says:** "MCP-Compatible Interface — JSON-RPC tool exposure via FastMCP. Connect any MCP-compatible AI client — OpenCode, Cursor, Claude Desktop, VS Code Copilot, Roo Code."
- **Source evidence:**
  - `nyxstrike_mcp.py` — MCP client entry point (43 lines) with `main()` that connects to the FastMCP server
  - `mcp_core/mcp_entry.py` — Core MCP registration logic
  - `mcp_tools/gateway.py` — Gateway tool registration with 2 `mcp.tool()` calls
  - `mcp_core/plugin_mcp_loader.py` — Plugin-based MCP tool loading
  - `mcp_core/api_client.py` — API client for MCP-server communication
  - `mcp_core/cli_colors.py` — Terminal output styling for MCP interface
  - `mcp_core/server_setup.py` — Server bootstrap for MCP integration
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: AI Orchestration Engine with LLM integration
- **Wiki says:** "AI Orchestration Engine — The intelligent decision engine uses catalog-driven tool scoring to chain tools automatically. Includes personality profiles, CVE intelligence management, and tool scoring algorithms."
- **Source evidence:**
  - `server_core/intelligence/intelligent_decision_engine.py` — Central decision engine with AttackChain/AttackStep integration
  - `server_core/intelligence/decision_engine_constants.py` — `initialize_tool_effectiveness()`, `initialize_technology_signatures()`, `initialize_attack_patterns()`
  - `server_core/intelligence/tool_scoring.py` — Scoring algorithms for tool selection
  - `server_core/intelligence/tool_catalog.py` — Catalog-driven tool lookup
  - `server_core/intelligence/chat_personalities.py` — `class PersonalityPreset`, `get_preset()`, `resolve_prompt()` — personality profiles for AI agent behavior
  - `server_core/intelligence/cve_intelligence_manager.py` — `class CVEIntelligenceManager:` with `fetch_latest_cves()`, `analyze_cve_exploitability()`, `search_existing_exploits()`
  - `server_core/llm_agent.py` — LLM agent with `analyze_session()`, `follow_up_session()`, finding parsing and risk assessment
  - `server_core/llm_client.py` — Multi-backend LLM client with `OllamaBackend`, `OpenAIBackend`, `AnthropicBackend` classes
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Attack chain workflows with session management
- **Wiki says:** "Attack Chain Workflows — Full recon → enumeration → exploitation → reporting workflows. The server core includes workflow definitions, session management, process management, and a failure recovery system."
- **Source evidence:**
  - `server_core/session_flow.py` — Session flow management for attack chains
  - `server_core/session_store.py` — Session persistence and retrieval
  - `server_core/process_manager.py` — Process lifecycle management
  - `server_core/enhanced_process_manager.py` — Extended process control
  - `server_core/failure_recovery_system.py` — Failure recovery with retry and fallback logic
  - `server_core/error_handling.py` — Error classification and handling
  - `server_core/recovery_executor.py` — Recovery strategy execution
  - `server_core/vulnerability_correlator.py` — `find_attack_chains()` discovers multi-vulnerability attack chains with depth control
  - `server_core/workflows/bugbounty/` and `server_core/workflows/ctf/` — Predefined workflow templates
  - `server_core/operation_types.py` — Operation type definitions for workflow steps
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Real-time dashboard and tool profiles for context window optimization
- **Wiki says:** "Real-Time Dashboard — Web-based session dashboard at http://localhost:8888 with live command output, session logs, and performance monitoring." and "Tool Profiles — Profile-based tool loading to fit model context windows — only 5–8 tools per category for smaller models, with expandable profiles for larger contexts."
- **Source evidence:**
  - `ui/` — Full Vite/React dashboard: `index.html`, `vite.config.ts`, `package.json`, `src/` directory with React source, `eslint.config.js`
  - `README.md:49` — "Open http://localhost:8888 to access the dashboard"
  - `README.md:103` — "Real-time session dashboard with live command output and logs"
  - `mcp_core/tool_profiles.py` — Profile system with `TOOL_PROFILES` dict: `"compact"` (essential tools only), `"active_directory"`, `"api_audit"`, `"osint"`, plus dependency resolution via `resolve_profile_dependencies()`
  - The tool profile system explicitly limits tool loading per category: "Only 5-8 tools are loaded per task category to fit small model context windows"
  - `config.py` — Central configuration with environment variable overrides
  - `Dockerfile` + `docker-compose.yml` — Containerized deployment options
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Modular plugin system and Docker deployment
- **Wiki says:** "Modular Plugin System — Plugin architecture via plugins/plugins.yaml supporting extensible tool loading through plugin_loader.py and plugin_mcp_loader.py." and "Docker Deployment — docker-compose.yml for containerized deployment with AI model support."
- **Source evidence:**
  - `plugins/plugins.yaml` — Plugin manifest with three types: `tools` (Flask API + FastMCP), with future types documented (workflows, agents, reports)
  - `plugins/README.md` — Plugin documentation and authoring guide
  - `plugins/tools/` — Plugin tool implementations
  - `server_core/plugin_loader.py` — Plugin loading and initialization
  - `mcp_core/plugin_mcp_loader.py` — Plugin MCP tool registration
  - `Dockerfile` — Multi-stage Docker build with pip installation
  - `docker-compose.yml` — Compose configuration with `NYXSTRIKE_API_TOKEN` env var, port mapping, and build context
  - `docker-entrypoint.sh` — Container entry point with Flask server startup
  - `.dockerignore` — Docker build context optimization
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

| Claim | Verdict |
|-------|---------|
| 185+ security tools with effectiveness scoring (actual: 173 tools, 21 categories) | ⚠️ PARTIALLY ACCURATE |
| MCP-compatible interface with JSON-RPC | ✅ CORRECT |
| AI Orchestration Engine with LLM integration | ✅ CORRECT |
| Attack chain workflows with session management | ✅ CORRECT |
| Real-time dashboard and tool profiles | ✅ CORRECT |
| Modular plugin system and Docker deployment | ✅ CORRECT |

The nyxstrike codebase is a well-structured Python offensive security orchestration engine with real multi-backend LLM support (Ollama, OpenAI, Anthropic), comprehensive attack workflow management, and a modular plugin architecture. The tool count (173) falls slightly short of the claimed 185+, and categories (21) significantly exceed the claimed 12, suggesting the wiki underrepresents the breadth of tool coverage while slightly overstating the total count.

## Related

- [[nyxstrike]] — Main wiki entry
- [[hexstrike-ai.codegraph-verify]] — Upstream project verification
- [[Hexstrike-redteam.codegraph-verify]] — Red team variant verification
- [[sec-af]] — Security agent framework
- [[kali-pentest]] — Kali Linux tool integration reference

## Cross-project

- [[openclaw.codegraph-verify]] — Similar codegraph verification for OpenClaw
- [[podman.codegraph-verify]] — Similar codegraph verification for Podman
