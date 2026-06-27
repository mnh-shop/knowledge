---
name: hermes-local-admin-setup
description: "Synthesized Hermes local-admin multi-profile setup tutorial — Telegram gateway, kanban, coder/planner/qa-tester profiles. Workspace prototype."
tags: [ideas, deployment, hermes, setup, profile, kanban, telegram]
source: workspace/deployment-setup-automation/setup-artifact.rtf
---

> **⚠️ Idea / Prototype — not production-grade.**
> This is a synthesized summary of the `setup-artifact.rtf` (296KB, 2,147 lines)
> from the workspace. The full source document contains exact files, values,
> patch content, and compose definitions for a complete Hermes local-admin setup.
>
> The vault's `sources/hermes-agent/` and `domains/deployment/` remain the
> authoritative reference for Hermes deployment.

## Overview

A fully autonomous, multi-profile Hermes agent system on a single Apple Silicon Mac with four profiles operating in parallel:

| Profile | Role |
|---|---|
| **local-admin** | Gateway + orchestrator. Accepts user requests via Telegram, decomposes into kanban tasks, assigns to specialists. Never writes code or runs browsers. |
| **coder** | Code implementation via Pi coding-agent bridge (`pi clone` → Z.AI GLM-5.1 cloud model). All file writes go through the Pi bridge at port 9876. |
| **planner** | Researches, decomposes, files sub-tasks. Creates roadmap for multi-step features. Always creates a linked qa-tester task after any coder task. |
| **qa-tester** | Browser-only E2E verification against production port (3001) exclusively. Files coder bug task for every failure before calling kanban_complete. |

## Supporting Services

All in the same Docker network:

| Service | Description |
|---|---|
| Hermes gateway | Primary container running all 4 profiles as s6-supervised gateway processes |
| Pi coding agent | HTTP API at port 9876 (`@mariozechner/pi-coding-agent`) |
| Bitwarden | Self-hosted password vault at port 8310 (HTTPS) |
| SearXNG | Self-hosted meta-search at port 8888 |
| Hindsight PostgreSQL | pgvector/pg16 — vector store backend |
| Hindsight service | REST API wrapping pgvector at port 8889 |

## Key Architectural Decisions

- **Shared kanban DB** — single SQLite `/opt/data/kanban.db` shared by all profiles
- **local-admin dispatcher hook** — sole task promoter; built-in gateway dispatcher disabled (`max_spawn: 0`)
- **8 patch files** — overlay specific Python modules via `:ro` bind mounts; base image never rebuilt
- **LM Studio on host** — port 1234, accessed via `host.docker.internal:1234`
- **lm_studio_recovery.py** — auto reload on crash
- **Skills repository profile** — all profiles symlink into a shared repo; `skills.include` whitelist per profile
- **OpenRouter-first routing** — free-only with fallback policy

## Model Routing

| Provider | Model | Role |
|---|---|---|
| Z.AI | GLM-5.1 | Primary cloud coding model |
| OpenCode Go | Kimi-k2.6 / deepseek-v4-flash | Auxiliary coding, delegation, compression |
| Nous Research | Nemotron-3-ultra:free | Free tier, third fallback |
| LM Studio (local) | Qwen3.6-35B-A3B-GGUF | Last resort / long tool-call chains |

## Verification Checklist (from Section 18)

- All containers up and healthy
- Hermes logs show no startup errors
- Volume mounts landed (secrets, kanban, patches, hindsight)
- Patches active (check from inside container)
- kanban.db exists with correct schema
- Dispatcher hook firing (check gateway logs)
- Bitwarden HTTPS accessible
- Hindsight and PG healthy
- qa-tester sees only its 6 whitelisted skills (not all 54)

## Related

- [[hermes-profiles|Hermes Profiles (SOUL files)]] — the Local-admin, Coder, Planner, QA-Tester SOUL.md files and config.yaml
- [[security-boundary-pattern|Security Boundary Pattern]] — the "agents never on host OS" deployment rule
- [[setup-factory/README|Setup Factory]] — the manifest-driven stack generator descended from this prototype
- [[setup-factory/v1-stack-architecture|V1 Stack Architecture]] — next-generation architecture building on these patterns
