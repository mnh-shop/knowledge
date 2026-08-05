---
name: communitytools
tags: [communitytools, security, ai-llm, automation, multi-agent, cli]
description: Transilience AI Community Security Tools — 40 Claude Code skills for AI-powered penetration testing, bug bounty hunting, and security reconnaissance (MIT)
source: sources/communitytools/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Community Security Tools

| Field | Value |
|---|---|
| **Origin** | [transilienceai/communitytools](https://github.com/transilienceai/communitytools) |
| **License** | MIT |
| **Source** | `sources/communitytools/` |

## What is it?

Transilience AI Community Security Tools is a consolidated Claude Code security testing suite containing **40 skills** and **20+ Python tool integrations** that cover the full penetration testing lifecycle. Built for AI-powered security testing including penetration testing, bug bounty hunting, AI threat testing, and security reconnaissance.

The suite achieved **100% (104/104)** on a published CTF benchmark suite using structured markdown skill files without any model fine-tuning. Skills are invoked with `/skill-name` slash commands inside Claude Code sessions.

## Key Features

- **40 Security Skills** covering OWASP Top 10, OWASP LLM Top 10, SANS Top 25 CWE, and MITRE ATT&CK
- **Multi-Agent Architecture** — executor, skeptic, and validator roles spawned dynamically via `Agent(prompt=...)`, orchestrated by the coordinator with a P0–P5 pipeline
- **Playwright Integration** — Browser automation for client-side vulnerability testing and evidence capture
- **Payload-Enriched References** — 160+ reference files with inline PayloadsAllTheThings techniques
- **Professional Reporting** — CVSS 3.1, CWE, MITRE ATT&CK, and Transilience-branded PDF reports (ReportLab)
- **CTF Benchmark Performance** — 100% on XBOW CTF benchmark using skills-only approach
- **Cross-Model Transfer** — Skills work across Claude Sonnet 4.6 (96.2%) and Haiku 4.5 (62.5%)
- **MCP Server** — `mcp/transilience-vuln` exposes CVE enrichment tools (`enrich_cve`, `bulk_enrich_cves`, `get_cached_cve`, `cache_stats`)
- **Claude Code Plugin** — `.claude-plugin/` with `marketplace.json` + `plugin.json` for marketplace installation

## Skills by Category

`skills/` contains 40 skill directories plus `INDEX.md`.

### Vulnerability Testing (10)
- `/injection` — SQL, NoSQL, OS Command, SSTI, XXE, LDAP/XPath injection
- `/client-side` — XSS, CSRF, Clickjacking, CORS, Prototype Pollution
- `/server-side` — SSRF, HTTP Smuggling, Path Traversal, File Upload, Deserialization
- `/authentication` — Auth Bypass, JWT, OAuth, Password Attacks, 2FA Bypass
- `/api-security` — GraphQL, REST API, WebSockets, Web LLM
- `/web-app-logic` — Business Logic, Race Conditions, IDOR, Cache Poisoning
- `/cloud-containers` — AWS, Azure, GCP, Docker, Kubernetes
- `/system` — Active Directory, Privilege Escalation, Exploit Development
- `/infrastructure` — Port Scanning, DNS, MITM, SMB/NetBIOS
- `/social-engineering` — Phishing, Pretexting, Vishing, Physical Security

### Reconnaissance (3)
- `/reconnaissance` — Subdomain discovery, port scanning, endpoint enumeration
- `/osint` — Repository enumeration, secret scanning, employee footprint
- `/techstack-identification` — Passive tech stack inference across 17 intelligence domains

### Specialized (5)
- `/ai-threat-testing` — OWASP LLM Top 10 — prompt injection, model extraction, data poisoning
- `/blockchain-security` — Smart contract security, EVM storage, DeFi exploits
- `/cve-poc-generator` — CVE research, NVD lookup, safe Python PoC generation
- `/dfir` — Digital forensics, incident response, PCAP analysis
- `/source-code-scanning` — SAST — OWASP Top 10, CWE Top 25, dependency CVEs

### Platform Integrations (2)
- `/hackthebox` — Playwright-based HackTheBox challenge automation
- `/hackerone` — Bug bounty workflow with scope CSV parsing

### Coordination & Engagement (5)
- `/coordination` — Pentest orchestrator; P0–P5 pipeline (see Architecture), spawns executor/skeptic/validator agents per target
- `/attack-path-stitcher` — Standalone skill for attack-path stitching (separate from coordination, not a phase)
- `/pentest-engagement` — Full engagement lifecycle management
- `/regression-sweep` — Regression testing of repeated attack classes
- `/risk-prioritiser` — Risk prioritization of findings and attack chains

### Defense & Mobile (3)
- `/cloud-defense` — Cloud security posture review and defense analysis
- `/firewall-review` — Firewall rule review and misconfiguration detection
- `/mobile-security` — Mobile app security testing (Android/iOS)

### Intelligence & Risk (5)
- `/cve-risk-score` — CVE risk scoring and prioritization
- `/cryptography` — Crypto implementation review and attacks
- `/patt-fetcher` — PayloadsAllTheThings technique fetcher
- `/ti-ingest` — Threat intelligence ingestion
- `/transilience-report-style` — Transilience-branded PDF report generation

### Workflow & Meta (7)
- `/essential-tools` — Core toolkit bootstrap
- `/github-workflow` — GitHub-centric testing workflow
- `/pci-secure-software` — PCI secure software lifecycle guidance
- `/reverse-engineering` — Binary/source reverse engineering
- `/script-generator` — Test script generation
- `/skill-prune` — Skill cleanup/refactoring
- `/skill-update` — Skill maintenance and versioning

## Architecture

The suite uses a **skills-only architecture** with canonical definitions at the repo root:

- **Skills** (`skills/`, 40 dirs + `INDEX.md`) — User-triggered workflows invoked with `/skill-name`. Each skill contains `SKILL.md` and `reference/` directory.
- **Coordination** (`skills/coordination/`) — Coordinator subagent orchestrates P0–P5 pipeline with context-controlled spawning.
- **Tools** (`tools/`) — 20+ Python utility scripts (activity-logger, block-coordinator-ask, chain-merger, coverage_catalog, coverage_gate, enumerate_cells, env-reader, kev-lookup, network_coverage_map, nvd-lookup, passive_web_probe, protect_deliverable, register_source_ip, report_data_build, risk-prioritise, session-start, slack-send, stats-updater, ti-ingest, validate_catalog, validation_cache, plus `pci-sss/`) with 14 test files and shell helpers (`provision_vantage.sh`).
- **MCP** (`mcp/transilience-vuln/`) — Python MCP server exposing `enrich_cve`, `bulk_enrich_cves`, `get_cached_cve`, `cache_stats` tools (NVD CVE enrichment with cache).
- **Plugin** (`.claude-plugin/`) — `marketplace.json` + `plugin.json` for Claude Code plugin marketplace install.
- **Scripts** (`scripts/`) — `kali-claude-setup.sh` (Kali Docker setup flow), `debug-mcp.sh`, `proxy.sh`, `skill_linter.py`.
- **Benchmarks** (`benchmarks/`) — Harnesses: `xbow`, `bountybench`, `cybench`, `dvba_android` with `run_benchmarks.py` / `analyze_results.py`.
- **Project Environments** (`projects/`) — Isolated working directories with symlinked skills; 7 project types: attack-path-prioritisation, attacks-validation, compliance, ctf, offsec, pentest, webinars (+ `rfp-3.2`/`rfp-3.3` referenced in `skills/INDEX.md`).

### Coordination Pipeline (P0–P5)

The coordination flow is a **P0–P5 pipeline** (not a fixed 6-phase process), defined in `skills/coordination/SKILL.md:19-33`:

```
P0: Ingest scope
P1: Recon + read source code → write attack-chain.md → run preflight-checklist
P2: Think — read chain + experiments.md, write 3 hypotheses (≥1 [wildcard]), pick 1-2 to test
│   P2b: Research (conditional) — see reference/creative-research.md
P3: Execute — spawn 1-2 executors with CHAIN_CONTEXT [+ RESEARCH_BRIEF]
P4: Integrate — materialize each candidate; validate it now (interleaved, strict per-finding,
│   fresh blind agents) → CONFIRMED | REJECTED | CURE→re-validate | DROPPED; update chain, revise theory
└─ loop (max 30 experiments; mandatory skeptic at experiments 5, 15, 25)
P4b: Reset — re-read all recon + source + chain (when no progress 1 batch or goal_attempts ≥ 3)
P5: Engagement-thoroughness validation + Report (validated/ → Transilience PDF)
```

Key properties: the coordinator runs as a spawned subagent (one per target) and must not delegate its own thinking; "attack-path stitching" is a **separate skill** (`attack-path-stitcher/`), not a phase of the pipeline; coverage flips only on `VALID` findings.

## Related

- [[hermes-agent]] — Agent gateway that can use these security skills
- [[agentfield]] — Control plane for orchestrating security testing agents
- [[openclaw]] — Alternative agent framework with compatible MCP surface
