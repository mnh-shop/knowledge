---
name: hermes-profiles
description: "Hermes Agent SOUL profile scaffolds — 7 profiles from workspace prototyping (local-admin, coder, planner, qa-tester, control, FCC, KB-ingest, OMO)."
tags: [ideas, hermes, profile, agent-profile, index]
source: workspace/deployment-setup-automation/hermes-profiles/
---

> **⚠️ Workspace prototype SOUL files — not production-grade.**
> These are design explorations from workspace prototyping. Production Hermes
> profile configuration should be derived from `sources/hermes-agent/`.

## Profiles

| Profile | Role |
|---|---|
| [[hermes-profile-local-admin\|local-admin]] | Gateway orchestrator, Telegram intake, kanban dispatch |
| [[hermes-profile-coder\|coder]] | Implementation via Pi coding-agent bridge |
| [[hermes-profile-planner\|planner]] | Research, decomposition, linked qa-tester |
| [[hermes-profile-qa-tester\|qa-tester]] | Browser-only E2E verification |
| [[hermes-profile-control\|hermes-control]] | Lightweight stack orchestrator |
| [[hermes-profile-fcc-architect\|free-claude-code-architect]] | Architecture review lane |
| [[hermes-profile-kb-ingest\|kb-graph-ingest]] | Repository ingest + knowledge graph |
| [[hermes-profile-opencode-omo\|opencode-omo]] | Bounded coding worker |

## Shared config

The original workspace also defines a shared `model-routing.yaml` and per-profile `config.yaml`
files. The key model routing principles:
- OpenRouter free-only routing
- Two fallback providers (OpenRouter free tier → Nous Research free tier)
- Per-profile skills whitelist via `skills.include`
- Per-profile tool restrictions via `disabled_toolsets`

## Context

These profiles are referenced in [[hermes-local-admin-setup]] and are part of the broader
[[setup-factory/README|Setup Factory]] prototype.

## Sources

- `workspace/deployment-setup-automation/hermes-profiles/profiles/` — local-admin, coder, planner, qa-tester (with full config.yaml)
- `workspace/deployment-setup-automation/h-coderstack-docker/profiles/` — free-claude-code-architect, hermes-control, kb-graph-ingest, opencode-omo (SOUL only)
