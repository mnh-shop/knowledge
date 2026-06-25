---
name: knowledge
tags: [shared, index, deployment, architecture, landscape]
---

# Knowledge

A curated knowledge base for AI agent ecosystems: architecture, deployment,
APIs, protocols (MCP, ACP), and cross-system integrations.

**Focus:** Hermes, OpenClaw, AgentField, Podman, n8n, and the surrounding
ecosystem — 23 repositories across 6 functional layers.

## Use as an Obsidian vault

Open this folder in Obsidian to browse with:
- **Wikilinks** (`[[page]]`) for cross-references
- **Tags** for graph color groups by project
- **8 color groups** mapping major projects

## Structure

| Directory | Contents |
|---|---|
| `wiki/` | One entry per repository — what it is, where to find things |
| `domains/` | Cross-repo concept knowledge (architecture, deployment, APIs, MCP, ACP) |
| `assets/` | Reusable resources (agent profiles, quadlet configs, MCP server refs) |
| `integrations/` | Concrete system-to-system integration docs |
| `memory/` | Persistent session memory |
| `tests/` | Validation scripts for wikilinks and markdown quality |

## For agent instructions

See [`AGENTS.md`](./AGENTS.md) — principles, structure rules, and
compatibility-first analysis guidelines for AI coding agents working
with this repo.

## For the system index

See [`MEMORY.md`](./MEMORY.md) — the full landscape of 23 repositories
across 6 layers, with the compatibility matrix.

## Validation

```bash
bash tests/validate-wikilinks.sh   # all [[links]] resolve
bash tests/validate-markdown.sh    # fences, size, frontmatter
```
