---
name: anthropic-cybersecurity-skills
description: "Structured cybersecurity skill library for AI agents with 817 skills across 29 domains, mapped to MITRE ATT&CK, NIST CSF 2.0, ATLAS, D3FEND, AI RMF, and MITRE F3 frameworks"
tags: [anthropic, Anthropic-Cybersecurity-Skills, security, skill, skills-platform, claude-code]
source: sources/Anthropic-Cybersecurity-Skills/
---

# Anthropic Cybersecurity Skills

An open-source cybersecurity skills library designed for AI agents, providing structured playbooks and procedures for security analysis workflows. Contains 817 production-grade skills spanning 29 security domains, each following the agentskills.io standard with YAML frontmatter for discovery and step-by-step execution guides.

## Key Features

- **817 structured cybersecurity skills** covering digital forensics, threat hunting, malware analysis, cloud security, and more
- **Six framework mappings** per skill: MITRE ATT&CK v19.1, NIST CSF 2.0, MITRE ATLAS v5.4, MITRE D3FEND v1.3, NIST AI RMF, and MITRE Fight Fraud Framework (F3)
- **Progressive disclosure** for AI agents: ~30 tokens to scan frontmatter, 500-2000 tokens to load full workflow
- **29 security domains**: cloud security, threat hunting, digital forensics, malware analysis, SIEM operations, vulnerability management, incident response, red teaming, and others
- **6 framework mappings**: Every skill maps across MITRE ATT&CK, NIST CSF, ATLAS, D3FEND, AI RMF, and F3 frameworks for compliance and defense coverage
- Works with Claude Code, GitHub Copilot, Cursor, OpenAI Codex CLI, Gemini CLI, and any agentskills.io-compatible platform

## Architecture

Skills follow a consistent structure with YAML frontmatter defining metadata (name, description, domain, subdomain, tags, framework technique IDs) followed by Markdown body sections for execution guidance. Each skill includes:

- `When to Use` — trigger conditions for agent activation
- `Prerequisites` — required tools, access levels, and environment setup
- `Workflow` — step-by-step execution guide with commands and decision points
- `Verification` — methods to confirm successful execution

Skills are organized in directories under `skills/` with optional `references/`, `scripts/`, and `assets/` subdirectories for technical depth.

## Skills & Tools

The repo includes a validation script (`tools/validate-skill.py`) for testing skill structure and framework mapping completeness. Skills cover a wide range of security tasks from memory forensics with Volatility3 to cloud security assessments across AWS, Azure, and GCP.

## Deployment / Use

```bash
# Install via npx (recommended)
npx skills add mukul975/Anthropic-Cybersecurity-Skills

# Or clone the repository
git clone https://github.com/mukul975/Anthropic-Cybersecurity-Skills.git
```

Compatible with 26+ AI platforms including Claude Code, Cursor, Windsurf, GitHub Copilot, and any agentskills.io-compatible agent runtime.

## Related

- [[skills]] — Agent skills platform and registry
- [[abvx-agent-skills]] — Auditable skillpack for coding agents
- [[SecuritySkills]] — Security-focused agent skill ecosystem