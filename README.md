---
name: knowledge
description: "Vault root: cross-linked knowledge base for AI agent infrastructure — OpenClaw, Hermes Agent, n8n, AgentField, and deployment patterns"
tags: [acp, ai-llm, architecture, deployment, documentation, index, landscape, mcp, plugin-sdk, quadlet, shared, systemd]
---

# Knowledge

A curated knowledge base for AI agent ecosystems: architecture, deployment,
APIs, protocols (MCP, ACP), and cross-system integrations.

**Focus:** Hermes, OpenClaw, AgentField, Podman, n8n, and the surrounding
ecosystem — 115 source repositories (cloned and indexed) across 6 functional layers.

## Use as an Obsidian vault

Open this folder in Obsidian to browse with:
- **Wikilinks** (`[[page]]`) for cross-references
- **Tags** for graph color groups by project, capability, and domain
- **15+ color groups** mapping projects and capabilities

## Structure

| Directory | Contents |
|---|---|
| `wiki/` | One entry per repository — what it is, where to find things |
| `domains/` | Cross-repo concept knowledge (architecture, deployment, APIs, MCP, ACP) |
| `assets/` | Reusable resources — see below |
| `integrations/` | Concrete system-to-system integration docs |
| `memory/` | Persistent session memory |
| `tests/` | Validation scripts for wikilinks and markdown quality |

### assets/ subdirectories

| Subdirectory | Contents |
|---|---|
| `agent-references/` | 20 agent reference profiles for specialist swarms |
| `hermes-profiles/` | 40 Hermes Agent role profiles (backend-engineer through writer) |
| `deployment/` | Quadlet configs, Terraform/Ansible templates |
| `skills/` | 67 cataloged agent skills across engineering, design, methodology |
| `n8n-workflows/` | Workflow pattern catalog from 2,061 n8n workflow JSONs |
| `mcp-servers/` | MCP server references |
| `acp-agents/` | ACP agent references |
| `api-clients/` | API client references |

## For agent instructions

See [`AGENTS.md`](./AGENTS.md) — principles, structure rules, and
compatibility-first analysis guidelines for AI coding agents working
with this repo.

## For the system index

See [`MEMORY.md`](./MEMORY.md) — the full landscape of indexed repositories
across 6 layers, with the compatibility matrix.

## Validation

```bash
bash tests/validate-wikilinks.sh   # all [[links]] resolve
bash tests/validate-markdown.sh    # fences, size, frontmatter
```
