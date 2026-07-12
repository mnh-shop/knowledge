---
name: assets-catalog
description: "Master catalog of reusable assets extracted from the source repositories — skills, profiles, deployment templates, MCP/ACP references"
tags: [index, catalog, reference]
---

# Assets Catalog

Reusable artifacts extracted, synthesized, or curated from the 115 source repositories. Each subdirectory below contains one category of assets.

## Directory Overview

| Subdirectory | Count | Description |
|---|---|---|
| [[agent-references\|assets/agent-references/]] | 20 files | Agent reference profiles for specialist swarms — role definitions, capabilities, and usage patterns. Hermes Agent profiles in separate sub-directory. |
| [[hermes-profiles\|assets/hermes-profiles/]] | 40 profiles | Curated Hermes Agent role profiles — backend-engineer, brand-designer, product-manager, researcher, and 36 more. Each with AGENTS.md guide and profile.yaml. |
| [[deployment\|assets/deployment/]] | 10 guides + 94 quadlet files | Quadlet configurations and infrastructure-as-code templates for deploying agent services via Podman Quadlet systemd units. |
| [[skills\|assets/skills/]] | 67 entries | Extracted agent skill definitions across 67 categories: engineering, design, methodology, infrastructure, cybersecurity, and more. |
| [[mcp-servers\|assets/mcp-servers/]] | 4 files | MCP server reference implementations and configuration guides for connecting AI agents to external tools. |
| [[acp-agents\|assets/acp-agents/]] | 2 files | Agent Communication Protocol agent reference implementations. |
| [[api-clients\|assets/api-clients/]] | 1 file | API client reference documentation for gateway platforms. |
| [[n8n-workflows\|assets/n8n-workflows/]] | 9,655 workflows indexed | Full sweep catalog of all n8n workflows from n8nworkflows.xyz, organized by n8n's own category taxonomy with tool usage breakdown. |

## Profile Location Reference

Profiles are split across two directories to match their source:

- **`assets/agent-references/`** — Singular agent reference profiles (one `.md` per agent framework or platform). Naming convention: `<platform>-reference.md`.
- **`assets/hermes-profiles/`** — Screened Hermes Agent role profiles (40 roles, each a directory with AGENTS.md + profile.yaml). Managed via the [hermes-profiles](sources/hermes-profiles/) tooling.

## Usage Guidelines

1. **Skills** — Each skill directory under `assets/skills/` contains an independent skill definition. Full catalog in `assets/skills/INDEX.md`.
2. **Deployment** — Quadlet `.container` and `.volume` files in `assets/deployment/quadlets/`. Standalone guides as `.md` in `assets/deployment/`.
3. **N8N Workflows** — The workflow catalog INDEX lives at `assets/n8n-workflows/n8n-workflows-INDEX.md`.
4. **Agent References** — Each reference describes a distinct agent persona. Linked to its source repo via the `sources/` path in the frontmatter.

## Related

- [SCHEMA.md](../SCHEMA.md) — Vault structure and conventions
- [AGENTS.md](../AGENTS.md) — Agent instructions and index table
- `assets/skills/INDEX.md` — Full skills catalog
- `assets/hermes-profiles/INDEX.md` — Hermes profile catalog
- `assets/agent-references/INDEX.md` — Agent reference index
