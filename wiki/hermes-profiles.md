---
name: hermes-profiles
description: "Curated Hermes Agent profiles for specialist swarms with role identity, skill dependencies, and Hermes-native patterns"
source: sources/hermes-profiles/
verification_date: 2026-07-12
verified_by: codegraph-verify
tags: [hermes-profiles, hermes-agent, agent-profile, catalog, swarm, orchestration]
---

# Hermes Profiles

## Overview

Hermes Profiles is a curated collection of 39+ specialist agent profiles for the [[hermes-agent]] runtime. Each profile packages a complete role identity (`SOUL.md`), skill dependencies, and runtime configuration for a specific architecture, engineering, or business capability that can be deployed as a Hermes agent. The repository is organized into a shared skill pool (`skills/`) and a set of profile directories (`profiles/`) that symlink back to the pool, ensuring skill files exist in one canonical copy. Profiles follow **Hermes-native patterns**: artifact-pyramid output format for progressive disclosure, skill-based methodology loading via `skill_view`, Hermes kanban for multi-agent orchestration, and the Hermes profile system for role isolation. While the profiles themselves are Hermes-specific, the skills in `skills/` follow the [Agent Skills Open Standard](https://www.agensi.io/learn/agent-skills-open-standard) adopted by Claude Code, Codex CLI, Cursor, Gemini CLI, OpenClaw, GitHub Copilot, and 20+ other coding agents, making them portable across agent harnesses.

## Key Features

- **39+ specialist profiles** spanning engineering (backend, frontend, data, ML, SRE, security, platform), design (UX, brand), research (researcher, wonderer), management (product-manager, kanban-strategist, orchestrator, implementation-planner), quality (qa-engineer, reviewer, verifier), content (writer, editor, copy-editor, curator, technical-writer), and C-suite roles (CEO, CTO, CFO, COO, CPO, CMO, chief-of-staff, CLO, CHRO). Each profile includes a `SOUL.md` (first-principles identity document), `profile.yaml` (metadata with required and recommended skill listings), `README.md` (human usage guide), and `AGENTS.md` (agent-facing trigger patterns and handoff protocol).

- **Shared skill pool with symlink-based reuse** — the root `skills/` directory contains 40+ skill categories (architecture ADRs, artifact-pyramids, backend-engineering, research-methodology, mermaid-diagrams, financial-modeling, go-to-market, security-audit-methodology, etc.) as the single canonical copy. Each profile's `skills/` directory contains only relative symlinks back to the shared pool. Git tracks symlinks by reference (mode 120000), so clones reproduce correctly on macOS and Linux without duplicating content. This means one copy of each skill serves every profile, and adding a new skill to the pool immediately makes it available to all profiles.

- **Progressive disclosure skill design** — skills follow a layered loading model: `SKILL.md` is a thin index file with trigger conditions and loading instructions, while detailed methodology lives in `references/` subdirectories loaded on demand via `skill_view(name, file_path=path)`. Skills are designed to work on a vanilla Hermes install with no dependencies on council, cashew, or agent-specific infrastructure.

- **Validation automation** — the repository includes `scripts/validate_profiles.py`, a comprehensive validation tool that checks for: duplicate YAML keys in `profile.yaml`, missing required files (`SOUL.md`, `profile.yaml`, `README.md`, `AGENTS.md`), declared skills that do not exist in the shared skill pool or are not reachable through profile symlinks, invalid shared-skill frontmatter (missing `name` or `description`), and broken or absolute symlinks. This ensures profiles are always in a working state.

- **CI/CD-ready contribution workflow** — profiles are contributed via GitHub PRs (`feat/your-profile` branch) with a clear checklist: SOUL.md with first principles and output contract, profile.yaml with valid YAML and required skills, README.md with installation and quick-start, AGENTS.md with trigger patterns, resolved relative symlinks, and no duplicate skill files. The `validate_profiles.py` script can be run as a CI gate.

## Repository Structure

```
hermes-profiles/
├── skills/                          ← Shared skill pool (actual files, 40+ categories)
│   ├── architecture/                ← ADR, arc42, C4 diagramming
│   ├── artifact-pyramids/           ← Progressive disclosure output format
│   ├── backend-engineering/         ← API, service logic, database skills
│   ├── research-methodology/        ← Deep investigation, evidence synthesis
│   ├── financial-modeling/          ← Unit economics, pricing, projections
│   ├── security-audit-methodology/  ← Threat modeling, vulnerability assessment
│   └── ... (35+ more categories)
├── profiles/                        ← 39 agent profiles (symlinks to skills)
│   ├── backend-engineer/
│   ├── researcher/
│   ├── technical-architect/
│   ├── product-manager/
│   └── ... (including 9 C-suite profiles)
├── scripts/
│   └── validate_profiles.py         ← Validation automation
├── CONTRIBUTING.md
├── AGENTS.md
└── README.md
```

## Usage

```bash
# Clone the repo
git clone https://github.com/magnus919/hermes-profiles.git ~/hermes-profiles

# Symlink a profile into ~/.hermes/profiles/
ln -s ~/hermes-profiles/profiles/researcher ~/.hermes/profiles/

# Switch to profile (skills are bundled via symlinks)
hermes --profile researcher
```

Each profile's `profile.yaml` declares required and recommended skills. When Hermes loads a profile, it resolves the symlinks in the profile's `skills/` directory back to the shared pool and makes those skills available at runtime. To add a new skill to a profile, create the skill directory in `skills/` first, then add a relative symlink from the profile's `skills/` directory.

## Related

- [[hermes-agent]] — Core Hermes agent runtime that consumes these profiles for role-based operation
- [[skills]] — Cross-project skill taxonomy and the Agent Skills Open Standard
- [[hermes-suite]] — All-in-one Hermes deployment stack that can use these profiles
- [[agentfield]] — Control plane that can orchestrate Hermes agents with specific profiles
- [[mission-control]] — MCP audit server that can monitor profile-switching behavior
- [[hermzner]] — Hetzner automations that pair with platform-engineer and SRE profiles
- [[pi]] — TypeScript agent harness compatible with Hermes profile skills
- [[abvx-agent-skills]] — Alternative skill collection with compatible SKILL.md format
