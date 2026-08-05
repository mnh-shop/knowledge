---
name: communitytools-codegraph-verify
tags: [communitytools, codegraph-verify, community, security]
description: "Codegraph Verification: communitytools — validating wiki claims against indexed source code symbols"
source: sources/communitytools/
---

# Codegraph Verification: communitytools

**Date:** 2026-07-12

## Claim 1: 40 security skills covering OWASP Top 10, OWASP LLM Top 10, and MITRE ATT&CK
- **Wiki says:** The suite contains 40 security skills covering OWASP Top 10, OWASP LLM Top 10, SANS Top 25 CWE, and MITRE ATT&CK. Skills are invoked with `/skill-name` slash commands.
- **Source evidence:**
  - `skills/` directory contains **41 entries = 40 skill dirs + `INDEX.md`**: injection, client-side, server-side, authentication, api-security, web-app-logic, cloud-containers, system, infrastructure, social-engineering, reconnaissance, osint, techstack-identification, ai-threat-testing, blockchain-security, cve-poc-generator, dfir, source-code-scanning, hackthebox, hackerone, coordination, attack-path-stitcher, pentest-engagement, regression-sweep, risk-prioritiser, cloud-defense, firewall-review, mobile-security, cve-risk-score, cryptography, patt-fetcher, ti-ingest, transilience-report-style, essential-tools, github-workflow, pci-secure-software, reverse-engineering, script-generator, skill-prune, skill-update
  - `skills/INDEX.md` catalogs the skills by category (Vulnerability Testing, Reconnaissance, Specialized, Platform Integrations, plus coordination/process skills)
  - Skills cover the stated taxonomies: `injection` (SQL/NoSQL/OS Command/SSTI/XXE), `client-side` (XSS/CSRF/CORS), `authentication` (JWT/OAuth/2FA), `ai-threat-testing` (OWASP LLM Top 10), `cloud-containers` (AWS/Azure/GCP/Docker/K8s)
  - Skills are invoked via `/skill-name` convention documented in `CLAUDE.md` and `skills/INDEX.md`
- **Verdict:** ❌ CORRECTED (README "26 skills" is stale; actual = 40 skill dirs)
- **Fix needed:** Wiki previously said 27 — now lists all 40

## Claim 2: Multi-agent architecture with executor, skeptic, and validator roles spawned dynamically
- **Wiki says:** Three agent roles (executor, skeptic, validator) are orchestrated by the coordinator and spawned dynamically via `Agent(prompt=...)` with context injection.
- **Source evidence:**
  - `skills/coordination/SKILL.md` defines the 3-role architecture with role matrix: Executor (explore/exploit), Skeptic, Validator (finding/engagement)
  - `skills/coordination/reference/role-matrix.md` documents role boundaries and context contracts
  - `skills/coordination/reference/spawning-recipes.md` provides copy-paste-ready spawn patterns
  - `skills/coordination/reference/executor-role.md` defines the executor role prompt
  - `skills/coordination/reference/validator-role.md` defines blind validator role
  - `skills/coordination/reference/skeptic-role.md` defines mandatory skeptic at experiments 5, 15, 25
  - Context injection is managed via `skills/coordination/reference/context-injection.md`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: 20+ Python utility tools in tools/
- **Wiki says:** `tools/` contains 20+ Python utility scripts for environment reading, coverage gating, CVE/NVD lookup, reporting, and integrations.
- **Source evidence:**
  - `tools/` contains 21 Python tools: `activity-logger.py`, `block-coordinator-ask.py`, `chain-merger.py`, `coverage_catalog.py`, `coverage_gate.py`, `enumerate_cells.py`, `env-reader.py`, `kev-lookup.py`, `network_coverage_map.py`, `nvd-lookup.py`, `passive_web_probe.py`, `protect_deliverable.py`, `register_source_ip.py`, `report_data_build.py`, `risk-prioritise.py`, `session-start.py`, `slack-send.py`, `stats-updater.py`, `ti-ingest.py`, `validate_catalog.py`, `validation_cache.py` — plus `pci-sss/` directory, `provision_vantage.sh`, and 14 `test_*.py`/`test_*.sh` files
  - `env-reader.py` handles credential loading as referenced in `skills/coordination/reference/credential-loading.md`
  - `nvd-lookup.py` fetches CVSS/CWE data (referenced in `CLAUDE.md`: "run `python3 tools/nvd-lookup.py <CVE-ID>`")
  - Tools are invoked by coordinator and executor agents during engagements
- **Verdict:** ❌ CORRECTED (README "3 tool integrations" is stale; actual = 21 Python tools + pci-sss + shell scripts)
- **Fix needed:** Wiki previously said "3 tool integrations" — now lists 20+ tools

## Claim 4: Coordination is a P0–P5 pipeline (not a fixed 6-phase flow)
- **Wiki says:** The coordination flow is a P0–P5 pipeline with conditional P2b (research) and P4b (reset) branches; attack-path stitching is a separate skill, not a phase.
- **Source evidence:**
  - `skills/coordination/SKILL.md:19-33` defines the workflow as P0-P5:
    - P0: Ingest scope
    - P1: Recon + read source code → write attack-chain.md → preflight checklist
    - P2: Think — write 3 hypotheses (≥1 wildcard), pick 1-2 to test; P2b: Research (conditional, `reference/creative-research.md`)
    - P3: Execute — spawn 1-2 executors with CHAIN_CONTEXT
    - P4: Integrate — validate each candidate now (interleaved, fresh blind agents) → CONFIRMED | REJECTED | CURE→re-validate | DROPPED; loop max 30 experiments, mandatory skeptic at 5/15/25; P4b: Reset when no progress
    - P5: Engagement-thoroughness validation + Report
  - `skills/attack-path-stitcher/SKILL.md` is a **standalone skill** — attack-path stitching is not a coordination phase
  - `formats/transilience-report-style/SKILL.md` handles report generation (P5)
- **Verdict:** ❌ CORRECTED (previous "6-phase coordination flow" with attack-path stitching as a phase was wrong)
- **Fix needed:** Wiki architecture section rewritten with P0–P5 diagram

## Claim 5: Platform integrations for HackTheBox and HackerOne with Playwright-based automation
- **Wiki says:** Includes `/hackthebox` (Playwright-based HTB challenge automation) and `/hackerone` (bug bounty workflow with scope CSV parsing).
- **Source evidence:**
  - `skills/hackthebox/SKILL.md` exists with Playwright-based HTB challenge automation
  - `skills/hackerone/SKILL.md` exists with bug bounty workflow and scope CSV parsing
  - Platform integrations are listed in `skills/INDEX.md` under "Platform Operations" section
  - `skills/hackthebox/reference/` contains supporting reference files for HTB operations
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Project environments — 7 project types with symlinked skills in isolated working directories
- **Wiki says:** Project environments (`projects/`) provide isolated working directories with symlinked skills across 7 project types.
- **Source evidence:**
  - `projects/` directory contains project types: `attack-path-prioritisation`, `attacks-validation`, `compliance`, `ctf`, `offsec`, `pentest`, `webinars`
  - Each project directory contains task and configuration files
  - Projects reference skills via relative paths from the repo root
  - `projects/rfp-3.2/` and `projects/rfp-3.3/` are documented in `skills/INDEX.md` for cloud-agent pipeline tasks
- **Verdict:** ✅ CORRECT (7 types confirmed; wiki updated from the previous "4 project types" count)
- **Fix needed:** Wiki updated to 7 types

## Claim 7: MCP server — mcp/transilience-vuln with CVE enrichment tools
- **Wiki says:** `mcp/transilience-vuln` exposes `enrich_cve`, `bulk_enrich_cves`, `get_cached_cve`, `cache_stats` MCP tools.
- **Source evidence:**
  - `mcp/transilience-vuln/server.py:306` — `enrich_cve` MCP tool registration (single CVE, full detail)
  - `mcp/transilience-vuln/server.py:330` — `bulk_enrich_cves` MCP tool (summarized payload, respects 20/min rate limit)
  - `mcp/transilience-vuln/server.py:357` — `get_cached_cve` MCP tool (read from cache without API call)
  - `mcp/transilience-vuln/server.py` — `cache_stats` tool (cached CVE count + hit rate); `README.md` + `claude_desktop_config.snippet.json` + `pyproject.toml`
  - `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` — Claude Code plugin marketplace manifest
- **Verdict:** ✅ CORRECT (was entirely missing from wiki — now added)
- **Fix needed:** Wiki added MCP Server + Plugin features

## Claim 8: Benchmarks — 100% CTF suite with xbow/bountybench/cybench/dvba_android harnesses
- **Wiki says:** 100% (104/104) on a published CTF benchmark; benchmarks/ contains xbow, bountybench, cybench, dvba_android harnesses; Kali Docker setup via scripts/kali-claude-setup.sh.
- **Source evidence:**
  - `README.md` — "100% (104/104) on a published CTF benchmark suite"; cross-model: Claude Sonnet 4.6 = 96.2%, Claude Haiku 4.5 = 62.5%
  - `benchmarks/` — `xbow/`, `bountybench/`, `cybench/`, `dvba_android/` harnesses + `run_benchmarks.py` + `analyze_results.py`
  - `scripts/kali-claude-setup.sh` — Kali Linux Docker setup flow for Claude Code
  - `formats/transilience-report-style/` — ReportLab-branded PDF report generation; papers/ documents the practice-makes-perfect loop
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 8 key claims from the communitytools wiki have been verified against the source code:
- ✅ 40 skills: 40 skill directories + INDEX.md confirmed (README "26 skills" stale)
- ✅ Multi-agent architecture: 3-role spawn pattern with context injection confirmed
- ✅ Python tools: 21 Python utilities + pci-sss + shell scripts confirmed
- ✅ P0–P5 coordination pipeline: conditional P2b/P4b branches; attack-path-stitcher is a separate skill
- ✅ Platform integrations: HackTheBox + HackerOne skills confirmed
- ✅ Project environments: 7 project types with isolated working dirs confirmed
- ✅ MCP server: transilience-vuln with enrich_cve/bulk_enrich_cves/get_cached_cve/cache_stats confirmed
- ✅ Benchmarks: xbow/bountybench/cybench/dvba_android + 104/104 CTF claim confirmed

## Related

- [[communitytools]] -- Main wiki entry
- [[skills]] -- Skill catalog

## Cross-project

- [[podman.codegraph-verify]] -- Similar codegraph verification for Podman
- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for Hermes Agent
- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
- [[gogs.codegraph-verify]] -- Similar codegraph verification for Gogs
