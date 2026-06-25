---
name: agents
tags: [knowledge, structure, guidelines]
---

# AGENTS.md

This is a GitHub-only knowledge system for coding agents.

## Principles

- **Never overengineer.** Favor the simplest solution that works. Add complexity only when it's proven necessary, not because it's anticipated.
- **Always interview and grill-me before building.** Before prototyping or implementing anything, run the `/interview` and `/grill-me` skills to validate the approach, understand constraints, and surface hidden requirements. No code before clarity.

## Focus

The focus is:

- architecture
- APIs
- MCP
- ACP
- deployment
- integrations between systems
- agentic loops

Do not create extra top-level folders.
Do not create folders unless the user asks or confirms when you ask.
Do not sort repositories by domain.
Do not duplicate repositories.

## Compatibility-first analysis

The long-term goal is reproducible deployment stacks combining Hermes, OpenClaw,
Agentfield, and n8n. Every repo should be checked for how it fits:

- **What does it provide?** (agent platform, CLI, skill, control plane, workflow engine, infra)
- **Interfaces:** MCP, REST API, CLI, webhooks, event bus, plugin system?
- **Compatibility:** Does it integrate with Hermes? OpenClaw? Agentfield? n8n?
- **Deployment:** What does it need to run? (config, database, ports, other services)

Seed `domains/integration-patterns/` with these cross-references — they're the
blueprint for deployment stacks.

## Structure

```text
sources/       full cloned GitHub repositories
raw/           Repomix XML generated from repositories
graphs/        CodeGraph output generated from repositories
wiki/          generated documentation per repository
assets/        reusable concrete things extracted from repos
domains/       cross-repo concept knowledge
integrations/  concrete system-to-system integration knowledge
```
