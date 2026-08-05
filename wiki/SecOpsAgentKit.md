---
name: SecOpsAgentKit
tags: [security, appsec, devsecops, secsdlc, compliance, incident-response, claude, skills, ai-agents, python, bash]
description: "Security operations skills for AI coding agents — AppSec, DevSecOps, Secure SDLC, Compliance, Incident Response, and Offensive Security"
source: sources/SecOpsAgentKit/
verification_date: 2026-07-30
verified_by: codegraph-verify
---

# SecOpsAgentKit

**Source:** `sources/SecOpsAgentKit/`

SecOpsAgentKit provides specialized Claude Code skills for security operations, covering AppSec (SAST/DAST, secure code review), DevSecOps (CI/CD security, container scanning), Secure SDLC (threat modeling, security requirements), Compliance (policy-as-code, auditing), Incident Response (forensics, detection rules), and Offensive Security (recon, exploitation, credential attacks). A collaborative approach to shift-left security using AI coding agents.

| Field | Value |
|---|---|
| **Origin** | [AgentSecOps/SecOpsAgentKit](https://github.com/AgentSecOps/SecOpsAgentKit) |
| **License** | Dual (CC-BY-SA 4.0 / MPL 2.0) |
| **Format** | Markdown SKILL.md files + Python/Bash scripts |
| **Categories** | 7 (appsec, devsecops, secsdlc, threatmodel, compliance, incident-response, offsec) |
| **Skills** | 31 (appsec 8, devsecops 6, offsec 9, secsdlc 3, incident-response 3, compliance 1, threatmodel 1) |
| **Install** | `/plugin marketplace add` or copy to `~/.claude/skills/` |
| **Source** | `sources/SecOpsAgentKit/` |
| **Codegraph** | `graphs/SecOpsAgentKit/` |

## What is it?

SecOpsAgentKit is a structured collection of Claude Code skills that embed security operations expertise directly into AI coding agent workflows. Each skill follows a standardized four-part structure: SKILL.md with YAML frontmatter, executable scripts, reference documentation, and configuration templates. Skills are organized by security discipline and trigger automatically when Claude encounters relevant security tasks — enabling shift-left security without manual context switching.

## Key Features

- **Application Security** — Skills for SAST (Bandit, Semgrep), DAST (ZAP, Nuclei, ffuf), API security (mitmproxy, Spectral), and SCA (Black Duck)
- **DevSecOps** — Container scanning (Grype, Trivy, Hadolint), IaC security (Checkov), secret detection (Gitleaks), vulnerability management (DefectDojo)
- **Secure SDLC** — Automated code review (reviewdog), multi-language SAST (Horusec), SBOM generation (Syft)
- **Compliance** — Policy-as-code with Open Policy Agent (OPA)
- **Threat Modeling** — Python-based threat modeling with pytm for STRIDE analysis
- **Incident Response** — Sigma detection rules, osquery forensics, Velociraptor endpoint visibility
- **Offensive Security** — Recon (nmap), packet analysis (tshark), credential attacks (hashcat), exploitation (metasploit, sqlmap, nikto), and OT assessment
- **Standardized Skill Format** — Every skill has validated YAML frontmatter and progressive disclosure; the <500-line SKILL.md rule (CLAUDE.md:15,115,191) is documented but violated by a few skills — the largest offenders are api-spectral (708), iac-checkov (671), analysis-tshark (638), and recon-nmap (635)
- **Marketplace Integration** — Install via `/plugin marketplace add` or manual copy

## Tech Stack

| Component | Technology |
|---|---|
| **Skill Format** | Markdown SKILL.md with YAML frontmatter (Agent Skills spec) |
| **Scripts** | Python 3, Bash |
| **Security Tools** | Semgrep, ZAP, Nuclei, Trivy, Checkov, Gitleaks, osquery, Velociraptor, OPA, pytm, Sigma (all present as skill dirs) |
| **Validation** | Custom Python validator (`validate_skill.py`) with YAML frontmatter checks |
| **Install** | Claude Code plugin marketplace or manual `~/.claude/skills/` copy |

## Deployment

### Marketplace Install (recommended)

```
/plugin marketplace add https://github.com/AgentSecOps/SecOpsAgentKit.git
```

### Manual Install

```bash
git clone https://github.com/AgentSecOps/SecOpsAgentKit.git ~/.claude/skills/secops-agent-kit
```

Or copy individual skills:

```bash
cp -r SecOpsAgentKit/skills/appsec/sast-semgrep ~/.claude/skills/
```

## Related

- [[Claude-Red]] — 58 offensive security skills for Claude Skills system
- [[Claude-OSINT]] — OSINT methodology and arsenal skills for Claude
- [[ctf-skills]] — Agent Skills for CTF challenges
- [[Hexstrike-redteam-full]] — AI-powered MCP cybersecurity automation platform
