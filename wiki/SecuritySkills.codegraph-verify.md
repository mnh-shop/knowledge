---
title: "SecuritySkills"
subtitle: "CodeGraph Verification Companion"
suffix: ".codegraph-verify"
date: 2026-07-12
verified_by: "codegraph-explore"
source: "sources/SecuritySkills/"
tags: [securityskills, codegraph-verify, security, skills]
related:
  - "[[SecuritySkills]]"
  - "[[Anthropic-Cybersecurity-Skills]]"
  - "[[kali-pentest]]"
  - "[[defending-code-reference-harness]]"
---

# SecuritySkills — CodeGraph Verification

**Verification date:** 2026-07-12  
**Verified by:** codegraph-explore (source tree analysis)  
**Source reference:** `sources/SecuritySkills/`  
**Companion to:** [[SecuritySkills]]

---

## Claim-1: Repository contains 45 framework-grounded security skills across 10 security domains

The repository ships **45 structured security skills** organized across **10 security domains**. Each skill is a directory at `skills/<domain>/<skill-name>/` with `SKILL.md` as the entrypoint. Verified by filesystem read:

| Domain | Skills | Examples |
|--------|--------|---------|
| appsec | 5 | threat-modeling, secure-code-review, owasp-top-10-web, api-security, dependency-scanning |
| ai-security | 6 | llm-top-10, agentic-top-10, prompt-injection, model-supply-chain, ai-data-privacy, agent-security |
| identity | 5 | iam-review, access-review, rbac-design, zero-trust-assessment, privileged-access |
| cloud | 5 | aws-review, azure-review, gcp-review, iac-security, container-security |
| vuln-management | 4 | cve-triage, patch-prioritization, sbom-analysis, scanner-tuning |
| compliance | 5 | soc2-gap, iso27001-gap, pci-dss-review, hipaa-review, nist-csf-assessment |
| incident-response | 4 | ir-playbook, forensics-checklist, containment, post-incident-review |
| secops | 4 | detection-engineering, siem-rules, alert-triage, log-analysis |
| network | 3 | firewall-review, segmentation, dns-security |
| devsecops | 4 | pipeline-security, secrets-management, sast-config, dast-config |

Total: **45 skills** confirmed by filesystem listing (`ls skills/*/`).

**Source evidence:** `sources/SecuritySkills/README.md` lines 183–277 (full skills table), `skills/` directory (10 domain subdirectories, 45 skill directories).

---

## Claim-2: Every skill cites real framework control IDs (OWASP, NIST, MITRE ATT&CK, CIS) — no hallucinated references

Each skill's YAML frontmatter includes a `frameworks:` field with verifiable control IDs from real published frameworks:

| Skill | Frameworks Cited |
|-------|-----------------|
| Threat Modeling | STRIDE, PASTA, MITRE ATT&CK |
| Secure Code Review | OWASP ASVS 4.0.3, CWE Top 25 |
| OWASP Top 10 (Web) | OWASP Top 10 2021 |
| API Security | OWASP API Security Top 10 2023 |
| LLM Top 10 Review | OWASP LLM Top 10 2025 |
| Agentic AI Top 10 | OWASP Agentic AI, MITRE ATLAS |
| Zero Trust Assessment | NIST SP 800-207, CISA ZTMM v2 |
| AWS Security Review | CIS AWS Benchmark v3.0 |
| CVE Triage | CVSS 4.0, SSVC 2.1, CISA KEV, EPSS |
| SOC 2 Gap Analysis | AICPA TSC |
| PCI DSS Review | PCI DSS v4.0 |
| Firewall Rule Audit | CIS Controls v8, NIST SP 800-41 |

The README states: "Every skill cites real control IDs from OWASP, NIST, MITRE ATT&CK, or CIS. No invented controls. No hallucinated references."

**Source evidence:** `sources/SecuritySkills/README.md` lines 183–277 (frameworks column in skills tables), line 296 ("Framework-grounded" differentiator).

---

## Claim-3: Skills validated via multi-layered review by five specialized AI security agents

The repository documents a **five-agent review process** for every skill:

| Reviewer Role | Focus Area |
|---------------|-----------|
| CISO Reviewer | Strategic risk, compliance alignment, program-level gaps |
| Security Architect | Framework accuracy, control ID verification, design patterns |
| Security Engineer | Implementation correctness, tooling gaps, operational feasibility |
| AI Security Researcher | LLM/agentic threat modeling, prompt injection hardening, ATLAS coverage |
| SOC Analyst | Detection engineering, alert triage accuracy, IR workflows |

Each skill is also **prompt-injection hardened** — reviewed against OWASP LLM01:2025, with CI scanning for injection patterns on every PR. The `injection-hardened: true` field appears in every skill's frontmatter.

**Source evidence:** `sources/SecuritySkills/README.md` lines 303–315 (review process documentation), line 300 (prompt-injection hardening claim).

---

## Claim-4: Includes normalized JSON output schema, SARIF mapping, and tracker handoff for enterprise integration

Skills emit findings as **normalized JSON** validated against a formal schema:

- `schemas/finding.schema.json` — Normalized finding envelope with run/skill metadata, evidence, framework/CWE references, remediation fields
- `schemas/skill.schema.json` — Machine-readable skill frontmatter validation schema
- `schemas/tracker-handoff.schema.json` — Tracker-ready work item mapping
- `docs/normalized-json-output.md` — Normalized output specification
- `docs/sarif-output.md` — SARIF 2.1.0 mapping guidance
- `docs/tracker-handoff.md` — Issue tracker handoff format

All skills validate against their schemas via Ruby scripts:
- `scripts/validate_skill_schema.rb` — Validates all skill frontmatter
- `scripts/validate_framework_registry.rb` — Validates framework provenance, versions, owners
- `scripts/generate_quality_scorecard.rb` — Generates deterministic quality scorecards

**Source evidence:** `sources/SecuritySkills/` — `schemas/` directory (3 schema files), `docs/` directory (output specification docs), `scripts/` directory (validation scripts).

---

## Claim-5: Multi-agent compatible across 6+ AI platforms with same SKILL.md file

Skills work across **6+ AI platforms** without modification:

- **Claude Code** — native format with auto-discovery and `/slash-commands`
- **Gemini CLI** — references skills via `@` commands
- **Cursor** — adds as Cursor rules (`.cursor/rules/`)
- **Codex CLI** — loads via `--context` flag
- **OpenClaw** — compatible agent platform
- **Kiro** — loads via `kiro spec --skill`

The `SKILL.md` format follows the [Agent Skills](https://agentskills.io) open standard. Claude Code discovers skills automatically; other tools can load them by path.

**Source evidence:** `sources/SecuritySkills/README.md` lines 29–66 (Quick Start for each platform), badge row showing 6 platform compatibilities (lines 7–12).

---

## Claim-6: Includes role bundles that orchestrate skills for common security roles

Pre-configured **skill sequences** (role bundles) orchestrate skills in the right order for five common security roles:

| Role | Skill Sequence |
|------|---------------|
| **vCISO** | nist-csf-assessment → soc2-gap → iam-review → cve-triage → threat-modeling |
| **SOC Analyst** | alert-triage → detection-engineering → ir-playbook → log-analysis → cve-triage |
| **Security Engineer** | secure-code-review → dependency-scanning → cve-triage → secrets-management → pipeline-security → container-security → iam-review |
| **AppSec Engineer** | threat-modeling → secure-code-review → api-security → dependency-scanning → prompt-injection → owasp-top-10-web |
| **Cloud Security Engineer** | aws-review → azure-review → gcp-review → iac-security → container-security → zero-trust-assessment → privileged-access |

These bundles represent a unique approach: not just standalone skills, but **orchestrated sequences** reflecting real job functions.

**Source evidence:** `sources/SecuritySkills/README.md` lines 280–291 (Role Bundles section).

---

## Related Pages

- [[SecuritySkills]] — Main wiki entry for this repository
- [[Anthropic-Cybersecurity-Skills]] — 817 cybersecurity skills (broader coverage)
- [[kali-pentest]] — Kali Linux penetration testing automation
- [[defending-code-reference-harness]] — Security defense reference harness
