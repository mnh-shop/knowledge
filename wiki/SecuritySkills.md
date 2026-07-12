---
name: SecuritySkills
description: "Framework-grounded security skills for AI coding agents — threat modeling, code review, vulnerability management, compliance, and AI security (MIT)"
tags: [SecuritySkills, security, skill, agent]
source: sources/SecuritySkills/
---

# SecuritySkills

| Field | Value |
|---|---|
| **Origin** | [UnitOneAI/SecuritySkills](https://github.com/UnitOneAI/SecuritySkills) |
| **License** | MIT |
| **Source** | `sources/SecuritySkills/` |
| **Skills** | 45 across 10 security domains |

## What is it?

SecuritySkills provides structured, framework-grounded security expertise for AI coding agents. It addresses the problem where AI agents hallucinate control numbers, miss vulnerability categories, and produce inconsistent security output by grounding every finding in real published frameworks — OWASP, NIST, MITRE ATT&CK, and CIS Controls.

Skills are organized directories with `SKILL.md` entrypoints following the [Agent Skills](https://agentskills.io) open standard, compatible with Claude Code, Gemini CLI, Cursor, Codex CLI, OpenClaw, and Kiro.

## Key Features

- **Framework-grounded output** — Every finding cites verifiable control IDs from OWASP, NIST, MITRE ATT&CK, or CIS
- **45 skills across 10 domains** — Application Security, AI Security, Identity & Access, Cloud Security, Vulnerability Management, Compliance, Incident Response, SecOps, Network Security, DevSecOps
- **Role bundles** — Pre-configured sequences for vCISO, SOC Analyst, Security Engineer, AppSec Engineer, Cloud Security Engineer
- **Injection-hardened** — All skills reviewed against OWASP LLM01:2025, CI scans for prompt injection patterns on every PR
- **Normalized JSON output** — Findings conform to `schemas/finding.schema.json` with CWE mapping, evidence, and remediation
- **Multi-agent compatible** — Works with Claude Code, Gemini CLI, Cursor, Codex CLI, OpenClaw, and Kiro

## Skills

### Application Security
- Threat Modeling (STRIDE) — System designs and architectures
- Secure Code Review — OWASP ASVS 4.0.3, CWE Top 25 based analysis
- OWASP Top 10 (Web), API Security Review, Dependency Scanning

### AI Security (Uniquely Covered)
- LLM Top 10 Review — OWASP LLM Top 10 2025 framework coverage
- Agentic AI Top 10, Prompt Injection Testing, Model Supply Chain, AI Data Privacy, Agent Security Architecture

### Identity & Access
- IAM Security Review (NIST SP 800-63B, CIS Controls v8)
- Zero Trust Assessment (NIST SP 800-207), Privileged Access Management

### Cloud Security
- AWS/Azure/GCP Security Review (CIS Benchmarks)
- IaC Security (SLSA v1.0), Container Security (CIS Docker, CIS K8s)

### Vulnerability Management
- CVE Triage (CVSS 4.0, SSVC 2.1, CISA KEV, EPSS)
- Patch Prioritization, SBOM Analysis, Scanner Tuning

### Compliance
- SOC 2 Gap Analysis, ISO 27001 Gap Analysis, PCI DSS Review, HIPAA Review, NIST CSF Assessment

## Role Bundles

Pre-configured skill sequences for common security engagements:

| Role | Engagement Types |
|------|------------------|
| Security Engineer | Code Review, Pipeline Hardening, Vulnerability Response, Infrastructure Review |
| AppSec Engineer | Threat Modeling, Secure Code Review, API Security, Dependency Scanning |
| Cloud Security Engineer | AWS/Azure/GCP Review, IaC Security, Container Security, Zero Trust |
| vCISO | Program-level risk assessment, compliance, board reporting |
| SOC Analyst | Alert Triage, Detection Engineering, Incident Response, Log Analysis |

## Deployment / Use

**Claude Code (native format)**
```bash
# Global install — all skills available via auto-discovery and /slash-commands
cp -r skills/*/* ~/.claude/skills/

# Or project-local
mkdir -p .claude/skills && cp -r skills/*/* .claude/skills/

# Use naturally:
# "Review this code for security issues" → Auto-loads secure-code-review
# /threat-modeling → Direct invocation
# /cve-triage CVE-2024-1234 → With arguments
```

**Other agents**
- Gemini CLI: `cp -r skills/ ~/.gemini/skills/`
- Cursor: `cp -r skills/ .cursor/rules/`
- Generic: Point agent at skill's `SKILL.md` file

## Architecture Notes

- Skills use YAML frontmatter with `frameworks`, `difficulty`, `time_estimate`, `allowed-tools`, `injection-hardened` fields
- Role bundles orchestrate skills in logical sequences (e.g., pipeline-security → secrets-management → container-security)
- Progressive disclosure pattern: `SKILL.md` entrypoints stay lean (~500 lines); detailed reference files load on demand
- Validation scripts in `scripts/` verify schema compliance, framework provenance, and injection hardening

## Related

- [[Anthropic-Cybersecurity-Skills]] — Related cybersecurity skill collection with MITRE ATT&CK coverage
- [[hermes-agent]] — Hermes skills integration pattern
- [[agentfield]] — Security skills can be dispatched via AgentField harness
- [[skills]] — Agent skills platform
- [[Android-Pentesting-Checklist]] — Penetration testing methodology reference