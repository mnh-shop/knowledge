---
name: hermes-profiles-architecture
tags: [hermes-profiles, architecture, hermes-agent, agent-profile, swarm, skills]
description: "39 role profiles for Hermes Agent — 4-file structure, symlink-based shared skill pool, progressive disclosure skills, CI/CD validation automation"
source: sources/hermes-profiles/
verification_date: 2026-07-12
verified_by: fixer
---

# Hermes Profiles — Architecture

**Source:** `sources/hermes-profiles/`

## Overview

Hermes Profiles is a curated collection of **39 specialist agent profiles** for the Hermes Agent runtime. Each profile packages a complete role identity, skill dependencies, and runtime configuration into four files. The repository is organized as a **shared skill pool** (`skills/`) with 40+ skill categories, where each profile's `skills/` directory contains only relative symlinks back to the shared pool — ensuring one canonical copy of every skill serves all profiles. Profiles follow Hermes-native patterns: artifact-pyramid output format, skill-based methodology loading via `skill_view`, Hermes kanban for multi-agent orchestration, and Hermes profile system for role isolation.

## Architecture

The architecture follows a **two-tier symlink-based design**: a canonical skill pool at the repository root, and 39 profile directories whose `skills/` subdirectories contain relative symlinks to that pool. Validation automation (`validate_profiles.py`) enforces structural integrity across the entire graph.

```
hermes-profiles/
├── skills/                            ← Shared skill pool (canonical files)
│   ├── architecture/                  ← ADR, arc42, C4 diagramming
│   ├── artifact-pyramids/             ← Progressive disclosure output format
│   ├── backend-engineering/           ← API, service logic, database skills
│   ├── research-methodology/          ← Deep investigation, evidence synthesis
│   ├── financial-modeling/            ← Unit economics, pricing, projections
│   ├── security-audit-methodology/    ← Threat modeling, vulnerability assessment
│   ├── mermaid-diagrams/              ← Diagram generation skill
│   ├── product-methodology/           ← Product strategy and roadmap skills
│   └── ... (35+ more categories)
│
├── profiles/                          ← 39 agent profiles (symlinks to skills)
│   ├── backend-engineer/
│   │   ├── SOUL.md                    ← First-principles identity document
│   │   ├── profile.yaml               ← Metadata + required/recommended skills
│   │   ├── README.md                  ← Human usage guide
│   │   ├── AGENTS.md                  ← Agent trigger patterns and handoff
│   │   └── skills/                    ← Relative symlinks only (mode 120000)
│   │       ├── architecture -> ../../../skills/architecture
│   │       └── backend-engineering -> ../../../skills/backend-engineering
│   ├── researcher/
│   ├── technical-architect/
│   ├── product-manager/
│   ├── site-reliability-engineer/
│   ├── data-scientist/
│   ├── debugger/
│   ├── ... (39 total, including 9 C-suite profiles)
│
├── scripts/
│   └── validate_profiles.py           ← Validation automation (211 lines)
├── CONTRIBUTING.md
└── README.md
```

### Profile File Structure

Every profile follows a strict 4-file contract:

| File | Purpose |
|------|---------|
| **`SOUL.md`** | First-principles identity document — methodology, output contract, core values |
| **`profile.yaml`** | Machine-readable metadata — `name`, `description`, `required_skills`, `recommended_skills`, `tags` |
| **`README.md`** | Human-facing — installation, quick start, skill reference table |
| **`AGENTS.md`** | Agent-facing — trigger patterns, loading order, handoff protocol |

### Symlink Architecture

All symlinks are **relative** and deep-linked from the profile's `skills/` directory: `profiles/<name>/skills/<skill-name>` → `../../../skills/<skill-name>`. Git tracks symlinks by reference (mode 120000), so clones reproduce correctly on macOS and Linux without duplicating content. Adding a new skill to the shared pool immediately makes it available to all profiles.

### Progressive Disclosure Skill Design

Skills follow a layered loading model: `SKILL.md` is a thin index file with trigger conditions and loading instructions, while detailed methodology lives in `references/` subdirectories loaded on demand via `skill_view(name, file_path=path)`. Skills are designed to work on a vanilla Hermes install with no dependencies on council, cashew, or agent-specific infrastructure.

### Validation Automation (`validate_profiles.py`)

The 211-line validator checks: duplicate YAML keys in `profile.yaml`, missing required files (any of the 4-file contract), declared skills that do not exist in the shared pool or are not reachable through symlinks, invalid shared-skill frontmatter (missing `name` or `description`), and broken or absolute symlinks. Runs as a CI gate on PRs.

## Key Components

| Component | Location | Role |
|-----------|----------|------|
| **Shared skill pool** | `skills/` | 40+ canonical skill categories with SKILL.md + references/ |
| **Profile collection** | `profiles/` | 39 agent profiles with 4-file contract |
| **Validation script** | `scripts/validate_profiles.py` | YAML integrity, file existence, symlink resolution |
| **Role categories** | `profiles/<role>/` | Engineering, design, research, management, quality, content, C-suite |

### Profile Role Taxonomy

- **Engineering** (12): backend, frontend, data-engineer, data-scientist, data-architect, SRE, security, platform, debugger, implementation-planner, technical-architect, ML-engineer
- **Design** (2): brand-designer, UX-designer
- **Research** (2): researcher, wonderer
- **Management** (4): product-manager, kanban-strategist, orchestrator, implementation-planner
- **Quality** (3): QA-engineer, reviewer, verifier
- **Content** (6): writer, editor, copy-editor, curator, technical-writer
- **C-Suite** (9): CEO, CTO, CFO, COO, CPO, CMO, chief-of-staff, CLO, CHRO

## Related

- [[hermes-profiles]] — Wiki entry with full profile listing
- [[hermes-agent]] — Core Hermes Agent runtime that consumes these profiles
- [[hermes-profiles]] — 20 agent reference profiles in knowledge assets
- [[hermzner]] — Hetzner automations that pair with platform-engineer and SRE profiles
- [[skills]] — Cross-project skill taxonomy and Agent Skills Open Standard
- [[pi]] — TypeScript agent harness compatible with the skill format
