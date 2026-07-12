---
name: orchestration-skills
description: "54+ workflow orchestration skills for planning, coordination, and multi-agent systems"
tags: [orchestration, skills, mcp]
metadata:
  type: catalog
---

# Orchestration Skills

Skills for workflow planning, multi-agent coordination, and execution orchestration.

**Total skills:** 54+ across 14 repos

---

## Skill Sources

| Repo | Skills | Harness |
|------|--------|---------|
| `sources/hermes-agent/skills/` | 4 skills | hermes-agent |
| `sources/hermes-profiles/skills/` | 8 skills | hermes-agent |
| `sources/abvx-agent-skills/skills/execution-*/` | 8 skills | All |
| `sources/n8n-skills/skills/` | 14 skills | All (via MCP/hooks) |
| `sources/oh-my-hermes/plugins/omh/skills/` | 5 skills | hermes-agent |
| `sources/ECC/skills/` | 4 skills | ECC, hermes-agent |
| `sources/open-design/skills/` | 2 skills | open-design, hermes-agent |

---

## Skill Catalog

| Skill | Source | Harness | Description |
|-------|--------|---------|-------------|
| orchestration-methodology | hermes-profiles | hermes-agent | Multi-agent workflow coordination |
| orchestration | hermes-profiles | hermes-agent | Decompose/sequence/synthesize pattern |
| phase-spec-execution | abvx | All | Explicit phases with acceptance criteria |
| dynamic-workflow-packets | abvx | All | Risk-gated workflow packets |
| loopops-protocol | abvx | All | Loop-design artifact ladder |
| workflow-policy-layering | abvx | All | Safety/authority rule separation |
| kanban-guru | hermes-profiles | hermes-agent | Kanban flow optimization |
| kanban-strategist | hermes-profiles | hermes-agent | Board configuration design |
| brief-first-execution | abvx | All | Create brief before work |
| project-context-bootstrap | abvx | All | Bootstrap project context |
| agents-best-practices | abvx | All | Best practices for agent orchestration patterns |
| autonomous-loops | ECC | ECC, hermes-agent | Autonomous feedback loops in agent workflows |
| continuous-agent-loop | ECC | ECC | Continuous agent loop for persistent operations |
| team-agent-orchestration | ECC | ECC | Multi-agent team coordination |
| stitch-loop | open-design | open-design | Workflow stitching and merging |
| stitch-skill | open-design | open-design | Skill-to-skill integration patterns |

---

## Agent Orchestration Skills

| Skill | Source | Harness | Description |
|-------|--------|---------|-------------|
| claude-code | hermes-agent | hermes-agent | Claude Code CLI integration and orchestration |
| codex | hermes-agent | hermes-agent | Codex CLI integration and orchestration |
| hermes-agent | hermes-agent | hermes-agent | Self-referential Hermes Agent configuration |
| opencode | hermes-agent | hermes-agent | OpenCode CLI integration and orchestration |

---

## n8n-MCP Workflow Skills

| Skill | Description |
|-------|-------------|
| using-n8n-mcp-skills | Entry point, routes to specialists |
| n8n-workflow-patterns | Architectural patterns (webhook, batch, scheduled) |
| n8n-node-configuration | Operation-aware node setup |
| n8n-subworkflows | Reusable sub-workflow design |
| n8n-validation-expert | Error interpretation and fixing |

---

## Related

- [[skills-catalog]] — Main catalog
- [[hermes-workspace]] — Swarm orchestration
- [[n8n-skills]] — Workflow automation
- [[agentfield]] — Harness orchestration