---
name: skills-catalog
description: "Cross-harness skills catalog organized by use case — 1000+ skills across cybersecurity, software engineering, research, and automation domains"
tags: [skills, catalog, index, cybersecurity, swe, mcp]
metadata:
  type: catalog
---

# Skills Catalog

Skills organized by **use case** with cross-harness compatibility. Skills are usable patterns that can run across multiple agentic harnesses (Hermes Agent, OpenClaw, GoClaw, AgentField, n8n, ECC, opencode, pydantic-ai).

**Total skills catalogued:** 1000+

---

## Use Case Categories

| Category | Repos | Skills | Harnesses |
|----------|-------|--------|-----------|
| [Cybersecurity](cybersecurity/) | 10 repos | [4 sub-catalogs](cybersecurity/) | hermes-agent, openclaw, goclaw, ECC, agentfield |
| [Software Engineering](software-engineering/) | 25+ repos | 235+ skills | hermes-agent, openclaw, ECC, goclaw, agentfield |
| [Research](research/) | 17 repos | 45+ skills | hermes-agent, openclaw, pydantic-ai, af-deep-research, ECC |
| [Workflow Orchestration](orchestration/) | 14 repos | 54+ skills | hermes-agent, n8n, agentfield, ECC, open-design |
| [Token Efficiency](token-efficiency/) | 4 repos | 11+ skills | hermes-agent, ECC, agentfield |
| [Product Management](product-management/) | 7 repos | 45+ skills | hermes-agent, ECC, open-design |
| [Content Creation](content-creation/) | 9 repos | 95+ skills | openclaw, hermes-agent, ECC, open-design |
| [Infrastructure](infrastructure/) | 8 repos | 35+ skills | ECC, hermes-agent, agentfield, goclaw |
| [n8n Workflows](n8n-workflows/) | 3 repos | 188 workflows | n8n (native), all (via MCP) |

---

## Harness Compatibility Matrix

| Harness | Native Skills Format | Can Use | Notes |
|---------|-------------------|---------|-------|
| **Hermes Agent** | SKILL.md with frontmatter | abvx, ECC (hooks), Hermes-caduceus, open-design | Progressive disclosure, symlinked skills |
| **OpenClaw** | skills/ directories | hermes-profiles (via symlink), extensions | ClawHub registry integration |
| **GoClaw** | skills/ directories | Native skills, skill-creator pattern | Document processing focus |
| **AgentField** | skill/ subdirectories | ECC (hooks), n8n-mcp | Harness orchestration support |
| **n8n** | MCP tools via n8n-mcp | All skills (via hooks/MCP) | Workflow automation platform |
| **ECC** | .claude/skills/ with hooks | All skills (aggressive hooks) | 273 native skills + hook ecosystem |
| **opencode** | skills/ directories | open-design, n8n, pydantic-ai | Native skill format |
| **pydantic-ai** | tool-calling approach | pydantic-ai skills, can wrap others | Tool-calling based |

---

## Source Repositories

Skills come from these primary sources:

- `sources/Anthropic-Cybersecurity-Skills/` — 817 security testing skills
- `sources/SecuritySkills/` — 45 framework-grounded AI security skills
- `sources/awesome-openclaw-skills/skills/` — ~20 security + audit skills
- `sources/reverse-skill/skills/` — 15 reverse engineering skills
- `sources/CyberStrikeAI/skills/` — Security testing skills
- `sources/abvx-agent-skills/` — 55+ general agent skills (Matt Pocock)
- `sources/ECC/` — 285+ ECC skills + hooks ecosystem
- `sources/hermes-agent/skills/` — 72 Hermes skills in 18 categories
- `sources/hermes-agent/skills/` — 72 Hermes Agent preinstalled skills in 18 categories
- `sources/hermes-profiles/skills/` — 40 shared methodology skills
- `sources/openclaw/extensions/` — Platform-specific extension skills
- `sources/open-design/skills/` — 160+ design/creative skills
- `sources/n8n-skills/` — 14 n8n workflow skills
- `sources/pydantic-ai-skills/` — Pydantic AI skills framework