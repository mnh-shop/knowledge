---
name: hermes-startup-architect
tags: [hermes, wiki, typescript, agent-gateway, messaging, multi-platform]
description: Wiki entry for Hermes Startup Architect: Hermes Agent skill for turning startup ideas into research-backed kits (MIT)
---

# Hermes Startup Architect

| Field | Value |
|---|---|
| **Origin** | [outsourc-e/hermes-startup-architect](https://github.com/outsourc-e/hermes-startup-architect) |
| **License** | MIT |
| **Source** | `sources/hermes-startup-architect/` |
| **Raw** | `raw/hermes-startup-architect/hermes-startup-architect.xml` (64KB) |
| **Size** | Small — one skill file + one example kit |
| **Author** | Dilek x Hermes Agent |

## What it is

A structured workflow skill for Hermes Agent that turns a startup idea into
a research-backed 0-to-1 startup kit (8 files: market analysis, competitive
map, product spec, business model, pitch deck, roadmap, investor pitch,
landing page).

## Where to find things

| What | Where |
|---|---|
| Skill definition | `skills/business/startup-architect/SKILL.md` |
| Trigger phrases | "startup idea:", "analyze this startup:", "create a startup kit for" |
| Workflow steps | See [[hermes-startup-architect-skill]] (`assets/agent-skills/`) |
| Example output | `examples/forge-kit/` (8 complete files) |
| Setup guide | `SETUP.md` |
| Optional dependency | hermes-tweet plugin for X/Twitter market signals |

## Relationship to Hermes

- **Depends on** [[hermes-agent]] for execution (web_search, terminal, write_file tools)
- Not a standalone app — a skill that runs **inside** Hermes Agent
- Optional: [hermes-tweet](https://github.com/Xquik-dev/hermes-tweet) plugin for social signal pass

## For fork consideration

This is a small, self-contained skill. Forking considerations:
- **License:** MIT
- **Size:** Very small (~64KB raw) — easy to maintain
- **Value:** If you do startup work, this is a useful template
- **Customization:** Easy to fork and modify the 8-file template or add
  new asset types
- **Dependency:** Requires Hermes Agent to run; skill format is
  Hermes-specific (SKILL.md with frontmatter + workflow steps)

## Related

- [[hermes-startup-architect-skill]] -- Skill asset (SKILL.md definition)
- [[hermes-agent]] -- Hermes Agent runtime that executes this skill

## Cross-project

- [[hermes-workspace]] -- Can install this startup skill inside the workspace
- [[n8n]] -- Could automate startup research workflows
- [[agentfield]] -- Could orchestrate startup analysis as agent tasks
- [[af-deep-research]] -- Deep research engine could enhance startup research
