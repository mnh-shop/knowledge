---
name: token-efficiency-skills
description: "10+ skills for optimizing LLM token usage, budget management, and cost-aware development workflows"
tags: [token-efficiency, skills, mcp, ai-llm]
metadata:
  type: catalog
---

# Token Efficiency Skills

Skills for optimizing LLM token consumption, managing context budgets, and cost-aware pipeline design.

**Total skills:** 11+ across 4 repos

---

## Skill Sources

| Repo | Count | Harness Support |
|------|-------|-----------------|
| `sources/abvx-agent-skills/skills/` | 3 skills | All skills-harnesses |
| `sources/ECC/skills/` | 6 skills | ECC, hermes-agent |
| `sources/hermes-profiles/skills/` | 2 skills | hermes-agent |

---

## Skill Catalog

| Skill | Source | Harness | Description |
|-------|--------|---------|-------------|
| token-efficient-execution | abvx | All | Execute with minimal token overhead |
| token-frugal-mode | abvx | All | Low-token consumption mode |
| token-usage-audit | abvx | All | Audit token consumption patterns |
| cost-aware-llm-pipeline | ECC | ECC, hermes-agent | Optimize pipeline for LLM costs |
| cost-tracking | ECC | ECC, hermes-agent | Track LLM usage costs |
| context-budget | ECC | ECC | Manage context window budget |
| compaction-survival | abvx | All | Survive context window limits |
| lean-context-layout | abvx | All | Minimize context footprint |
| shell-output-compaction | abvx | All | Compact shell output for LLM |
| ecc-tools-cost-audit | ECC | ECC | Audit ECC tool costs |
| prompt-optimizer | ECC | ECC | Optimize prompts for minimal token consumption |

---

## Harness Compatibility

- **Hermes Agent** — Progressive disclosure, skill_view() loading
- **ECC** — Aggressive hook integration
- **opencode** — Native skills format
- **pydantic-ai** — Can wrap any skill for tool-calling pattern

---

## Related

- [[skills-catalog]] — Main skills catalog
- [[hermes-agent]] — Cost-aware agent platform