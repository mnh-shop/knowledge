---
name: hermes-profiles
description: "Curated Hermes Agent profiles for specialist swarms with role identity, skill dependencies, and Hermes-native patterns"
source: sources/hermes-profiles/
tags: [hermes-profiles, agent-profile, agent, automation, orchestration, reference, skills]
---

# Hermes Profiles

Curated Hermes Agent profiles for specialist swarms. Each profile packages a role identity (SOUL.md), skill dependencies, and configuration for a specific architecture/engineering capability that can be deployed as a Hermes agent.

These profiles are **opinionated** — they use Hermes-native patterns:
- Artifact-pyramid output format (progressive disclosure, path-as-handoff)
- Skill-based methodology loading (`skill_view` → load references)
- Hermes kanban for multi-agent orchestration
- Hermes profile system for role isolation

## Key Features

- 39+ specialist profiles (engineers, researchers, designers, C-suite roles)
- Shared skill pool with symlink-based reuse across profiles
- Each profile includes SOUL.md (first principles), profile.yaml (metadata), README.md, and AGENTS.md
- Skills follow the Agent Skills open standard (compatible with Claude Code, OpenClaw, Cursor, etc.)
- Relative symlinks ensure clean git tracking and reproducibility

## Repository Structure

```
hermes-profiles/
├── skills/              ← Shared skill pool (actual files)
│   ├── architecture/    ← ADR, C4, arc42 skills
│   ├── artifact-pyramids/
│   ├── backend-engineering/
│   ├── data-engineering/
│   └── ... (40+ skill categories)
└── profiles/            ← Agent profiles (symlinks to skills)
    ├── backend-engineer/
    ├── researcher/
    ├── technical-architect/
    └── ... (39 profiles including C-suite: ceo, cto, cfo, etc.)
```

## Using a Profile

```bash
# Clone the repo
git clone https://github.com/magnus919/hermes-profiles.git ~/hermes-profiles

# Symlink the profile into ~/.hermes/profiles/
ln -s ~/hermes-profiles/profiles/researcher ~/.hermes/profiles/

# Switch to profile (skills are bundled)
hermes --profile researcher
```

## Related

- [[hermes-agent]] — Core Hermes agent runtime that uses these profiles
- [[hermes-suite]] — All-in-one Hermes deployment that can use these profiles
- [[skills]] — Cross-project skill taxonomy and standards
- [[agentfield]] — Control plane that can orchestrate Hermes agents