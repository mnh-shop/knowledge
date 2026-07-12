---
name: communitytools
tags: [communitytools, security, ai-llm, automation, multi-agent, cli]
description: Transilience AI Community Security Tools — 27 Claude Code skills for AI-powered penetration testing, bug bounty hunting, and security reconnaissance (MIT)
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

Transilience AI Community Security Tools is a consolidated Claude Code security testing suite containing **27 skills** and **3 tool integrations** that cover the full penetration testing lifecycle. Built for AI-powered security testing including penetration testing, bug bounty hunting, AI threat testing, and security reconnaissance.

The suite achieved **100% (104/104)** on a published CTF benchmark suite using structured markdown skill files without any model fine-tuning. Skills are invoked with `/skill-name` slash commands inside Claude Code sessions.

## Key Features

- **27 Security Skills** covering OWASP Top 10, OWASP LLM Top 10, SANS Top 25 CWE, and MITRE ATT&CK
- **Multi-Agent Architecture** — coordinator, executor, and validator roles spawned dynamically via `Agent(prompt=...)`
- **Playwright Integration** — Browser automation for client-side vulnerability testing and evidence capture
- **Payload-Enriched References** — 160+ reference files with inline PayloadsAllTheThings techniques
- **Professional Reporting** — CVSS 3.1, CWE, MITRE ATT&CK, and Transilience-branded PDF reports
- **CTF Benchmark Performance** — 100% on XBOW CTF benchmark using skills-only approach
- **Cross-Model Transfer** — Skills work across Claude Sonnet 4.6 (96.2%) and Haiku 4.5 (62.5%)

## Skills by Category

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

## Architecture

The suite uses a **skills-only architecture** with canonical definitions at the repo root:

- **Skills** (`skills/` at root) — User-triggered workflows invoked with `/skill-name`. Each skill contains `SKILL.md` and `reference/` directory.
- **Coordination** (`skills/coordination/`) — Defines 3 agent roles (coordinator, executor, validator) with context injection.
- **Tools** (`tools/`) — Python utility scripts for environment reading and integrations.
- **Project Environments** (`projects/`) — Isolated working directories with symlinked skills.

The coordination flow follows a 6-phase process: surface expansion, attack-class coverage, evidence capture, validator spawning (blind review), attack-path stitching, and report generation.

## Related

- [[hermes-agent]] — Agent gateway that can use these security skills
- [[agentfield]] — Control plane for orchestrating security testing agents
- [[openclaw]] — Alternative agent framework with compatible MCP surface