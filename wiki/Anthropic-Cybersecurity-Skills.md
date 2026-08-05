---
name: anthropic-cybersecurity-skills
description: "Structured cybersecurity skill library for AI agents with 817 skills across 29 domains, mapped to MITRE ATT&CK, NIST CSF 2.0, ATLAS, D3FEND, AI RMF, and MITRE F3 frameworks"
tags: [anthropic, Anthropic-Cybersecurity-Skills, security, skill, skills-platform, claude-code]
source: sources/Anthropic-Cybersecurity-Skills/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Anthropic Cybersecurity Skills

An open-source cybersecurity skills library designed for AI agents, providing structured playbooks and procedures for security analysis workflows. Contains 817 production-grade skills spanning 29 security domains, each following the agentskills.io standard with YAML frontmatter for discovery and step-by-step execution guides.

## Overview

This is the largest open-source cybersecurity skills library for AI agents — an AI-native knowledge base built from the ground up for the agentskills.io standard. Every skill encodes real practitioner workflows (not generated summaries) covering digital forensics, threat hunting, malware analysis, cloud security, incident response, and more. The library bridges the 4.8-million-unfilled-role cybersecurity workforce gap (ISC2 2024) by giving AI agents the structured decision-making workflow a senior security analyst follows: when to use each technique, what prerequisites to check, how to execute step-by-step, and how to verify results. Existing security tool repos give you wordlists, payloads, or exploit code — this project gives an AI agent the practitioner playbook.

**Community project** by Mahipal Jangra ([@mukul975](https://github.com/mukul975)), not affiliated with Anthropic PBC. Licensed under Apache 2.0.

## Key Features

- **817 structured cybersecurity skills** covering digital forensics, threat hunting, malware analysis, cloud security (66 skills), threat hunting (58), threat intelligence (52), network security (43), web application security (42), digital forensics (41), malware analysis (39), IAM (37), SOC operations (35), security operations (28), red teaming (33), container security (33), OT/ICS security (28), API security (28), incident response (26), vulnerability management (25), penetration testing (21), DevSecOps (18), zero trust architecture (17), endpoint security (17), cryptography (16), phishing defense (15), AI security (14), mobile security (13), ransomware defense (13), compliance & governance (9), supply chain security (8), deception technology (6), and hardware/firmware security (4) — 29 domains total
- **Six-framework mappings with partial real-world coverage** — the README's aspirational claim that "every skill is mapped to six industry frameworks" (README.md:43) does not hold when measured across all 817 SKILL.md files: `mitre_attack` 817/817 (100%), `nist_csf` 816/817 (99.9%), `d3fend_techniques` 139/817 (~17%), `mitre_f3` 94/817 (~12%), `nist_ai_rmf` 85/817 (~10%), `atlas_techniques` 81/817 (~10%). Only ATT&CK reaches full coverage; the other five are partial. Framework versions: MITRE ATT&CK v19.1 (286 techniques across all 15 Enterprise tactics), NIST CSF 2.0 (6 functions, 22 categories), MITRE ATLAS v5.4 (16 tactics, 84 AI/ML techniques), MITRE D3FEND v1.3 (267 defensive techniques), NIST AI RMF 1.0 (72 subcategories), and MITRE Fight Fraud Framework F3 v1.1 (8 tactics, 123 techniques)
- **Progressive disclosure** for AI agents: ~30 tokens to scan frontmatter, 500-2000 tokens to load full workflow — agents search all 817 skills in a single pass without blowing context windows
- **MITRE F3 fight fraud framework support** — 94 fraud-relevant skills covering Positioning (FA0001: synthetic-identity seeding, account warming, SIM-swap) and Monetization (FA0002: money-mule layering, APP fraud, crypto off-ramping)
- **Compatible with 26+ platforms**: Claude Code, GitHub Copilot, Cursor, Windsurf, Cline, Aider, Continue, Roo Code, Amazon Q Developer, Tabnine, Sourcegraph Cody, JetBrains AI, OpenAI Codex CLI, Gemini CLI, Devin, Replit Agent, SWE-agent, OpenHands, LangChain, CrewAI, AutoGen, Semantic Kernel, Haystack, Vercel AI SDK, and any MCP-compatible agent
- **Validation tooling**: `tools/validate-skill.py` validates skill *structure* only — required frontmatter fields present, kebab-case `name` ≤64 chars, `description` ≥50 chars, subdomain in the registry, and ≥2 tags (validate-skill.py:182-257). It does **not** check framework-mapping completeness or MITRE ID validity: no `mitreattack` import exists anywhere in the shipped tooling, so the README's claim of ATT&CK ID validation (README.md:79) is not backed by any in-repo tool

## Usage

Skills follow a consistent directory structure with YAML frontmatter defining metadata (name, description, domain, subdomain, tags, framework technique IDs) followed by Markdown body sections:

```yaml
---
name: performing-memory-forensics-with-volatility3
description: Analyze memory dumps to extract running processes and malware artifacts
domain: cybersecurity
subdomain: digital-forensics
tags: [forensics, memory-analysis, volatility3, dfir]
mitre_attack: [T1003, T1055]
nist_csf: [DE.CM-01, RS.AN-03]
version: "1.2"
---
```

Each skill includes `When to Use` (trigger conditions), `Prerequisites` (tools, access levels), `Workflow` (step-by-step commands with decision points), and `Verification` (confirmation methods). Skills live in directories under `skills/` with optional `references/`, `scripts/`, and `assets/` subdirectories.

```bash
# Install via npx (recommended)
npx skills add mukul975/Anthropic-Cybersecurity-Skills

# Or clone the repository
git clone https://github.com/mukul975/Anthropic-Cybersecurity-Skills.git
```

The ATT&CK Navigator layer file is included in v1.0.0 release assets for visual coverage mapping. Note: `mappings/attack-navigator-layer.json` declares `"attack": "14"` in its versions block — it was built against ATT&CK **v14**, not v19.1, and should be treated as a legacy view. The project has been featured in awesome-agent-skills, awesome-ai-security, awesome-codex-cli, and SkillsLLM directory.

## Related

- [[skills]] — Agent skills platform and registry
- [[SecuritySkills]] — Security-focused agent skill ecosystem
- [[Android-Pentesting-Checklist]] — Android-specific pentesting companion for mobile security assessment
- [[CyberStrikeAI]] — AI-powered cybersecurity platform with red-teaming capabilities
- [[abvx-agent-skills]] — Auditable skillpack for coding agents
- [[defending-code-reference-harness]] — Reference implementation for autonomous vulnerability discovery using agents
