---
name: cybersecurity-skills
description: "900+ cybersecurity skills organized into 4 use-case catalogs — AI & AppSec, Cloud & Infrastructure, Offensive Security, Governance & Compliance"
tags: [cybersecurity, skills, catalog, index]
metadata:
  type: catalog
---

# Cybersecurity Skills

Skills for penetration testing, vulnerability assessment, exploitation, forensics, AI security, compliance, and security auditing — organized by practitioner surface.

**Total skills:** 900+ across 6 primary sources

---

## Use Case Catalogs

| Catalog | Skills | Focus |
|---------|--------|-------|
| [AI & Application Security](ai-appsec.md) | 30+ | AI security, exploitation testing, DevSecOps, secure code review |
| [Cloud & Infrastructure Security](cloud-infrastructure-security.md) | 25+ | AWS/GCP/Azure audits, network security, IAM, containers |
| [Offensive Security & Vulnerability](offensive-security.md) | 20+ | Pentesting, reverse engineering, vulnerability scanning, CVE/SBOM |
| [Governance, Compliance & Incident Response](governance-compliance-ir.md) | 25+ | SOC2/HIPAA/ISO27001/NIST/PCI-DSS, IR/forensics, SIEM, threat modeling |

---

## Skill Sources

| Repo | Count | Harness Support |
|------|-------|-----------------|
| `sources/Anthropic-Cybersecurity-Skills/` | 817 skills | hermes-agent, openclaw, goclaw, ECC, agentfield |
| `sources/SecuritySkills/` | 45 skills | All skills-compatible harnesses |
| `sources/CyberStrikeAI/skills/` | 20 skills | CyberStrikeAI, adaptable to others |
| `sources/reverse-skill/skills/` | 15 skills | All skills-compatible |
| `sources/awesome-openclaw-skills/skills/` | ~20 security skills | openclaw, hermes-agent |
| `sources/ECC/skills/` | 5 security skills | ECC, hermes-agent |

---

## Harness Compatibility

- **Hermes Agent** — Full support via skills format with frontmatter
- **OpenClaw** — Skills work via extensions or MCP bridge
- **GoClaw** — Native skill support
- **AgentField** — Hook-integrated skills via ECC
- **ECC** — Native skills with aggressive hook triggers
- **CyberStrikeAI** — Native Eino agent skills format

---

## Related

- [[skills-catalog]] — Main skills catalog
- [[sec-af]] — Security auditor agent (built on AgentField)
- [[openclaw-skills]] — OpenClaw extensions
- [[SecuritySkills]] — Framework-grounded security skills source
- [[awesome-openclaw-skills]] — Community security skill marketplace
- [[reverse-skill]] — Reverse engineering skill collection