---
name: swe-cli-skills
tags: [cli, skills, developer-tools, coding-agent, markdown, terminal, workflow, wiki, swe-cli-skills]
description: "Open-source skill giving AI coding agents senior-engineer-level CLI expertise across 23 CLIs in 9 categories — token-efficient, loads only needed guide"
source: sources/swe-cli-skills/
verification_date: 2026-07-30
verified_by: codegraph-verify
---

# SWE CLI Skills

| Field | Value |
|---|---|
| **Origin** | [SylphAI-Inc/swe-cli-skills](https://github.com/SylphAI-Inc/swe-cli-skills) |
| **Maker** | SylphAI (makers of AdaL) |
| **License** | MIT (Copyright (c) 2026 SylphAI, Inc.) |
| **Format** | Markdown SKILL.md files (Agent Skills spec) |
| **Deployment** | `npx skills` CLI, AdaL plugin marketplace, manual git clone per agent |
| **Source** | `sources/swe-cli-skills/` |

## What is it?

"Man pages for machines." An open-source skill collection that gives AI coding agents senior-engineer-level CLI expertise across **23 CLIs** organized into **9 categories** — cloud, IaC, containers, git/VCS, dev-tools, package managers, databases, platforms, and networking. Each skill is a focused guide file that teaches an agent not just flag syntax, but operational workflows, safety guardrails, gotchas, error recovery, and composition patterns — e.g. "here's how to deploy safely" instead of "here's every flag."

The skill system is token-efficient by design: the agent reads only the root `SKILL.md` index, then loads the single guide for the CLI it currently needs (~200-400 lines) rather than bundling all documentation upfront. This keeps context windows free for actual coding work.

## Key Features

- **23 CLIs Covered:** AWS CLI, gcloud, Azure CLI, Terraform, Docker, kubectl, Helm, git, gh, jq, make, sed, npm, pip & uv, psql, redis-cli, Stripe CLI, Sentry CLI, Vercel CLI, Firebase CLI, flyctl, curl, SSH/SCP.
- **9 Categories:** cloud, iac, containers, git-vcs, dev-tools, package-managers, databases, platforms, networking — each with its own `INDEX.md`.
- **Token-Efficient Sub-Index Architecture:** Each CLI is a standalone guide — agents load only the guide they need (~200-400 lines), reducing token waste.
- **Senior-Engineer-Level Tips:** Goes beyond man-page basics — encodes real production gotchas, error recovery, and expert workflows.
- **Consistent 7-Section Guide Structure:** Setup & Auth, Core Workflows, Flag Gotchas, Error Patterns, Anti-Patterns, Composability, Agent Constraints.
- **17 Critical Gotchas Quick Reference:** The root `SKILL.md` front-loads the highest-impact mistakes (S3 filter ordering, `terraform import` without plan, `git rebase -i` TTY hangs, `KEYS *` in production, etc.).
- **npx CLI:** Install and manage via `npx skills add SylphAI-Inc/swe-cli-skills` — no permanent install required.
- **AdaL Plugin Marketplace:** Native plugin install for AdaL (the makers' own agent platform).
- **Broad Agent Compatibility:** AdaL, Claude Code, Codex, Gemini CLI, Copilot, Cursor, Windsurf, Aider, OpenCode — any agent that reads the SKILL.md standard.

## CLI Categories

| # | Category | Directory | CLIs |
|---|---|---|---|
| 1 | Cloud | `skills/cloud/` | AWS CLI, gcloud, Azure CLI |
| 2 | Infrastructure as Code | `skills/iac/` | Terraform |
| 3 | Containers & Orchestration | `skills/containers/` | Docker, kubectl, Helm |
| 4 | Git & Version Control | `skills/git-vcs/` | git, gh |
| 5 | Dev Tools | `skills/dev-tools/` | jq, make, sed |
| 6 | Package Managers | `skills/package-managers/` | npm, pip & uv |
| 7 | Databases | `skills/databases/` | psql, redis-cli |
| 8 | Platforms & Services | `skills/platforms/` | Stripe CLI, Sentry CLI, Vercel CLI, Firebase CLI, flyctl |
| 9 | Networking | `skills/networking/` | curl, SSH/SCP |

> Note: `curl` and `ssh` live in `skills/networking/` (the README's "What's Included" table lists them under Dev Tools, but the actual directory tree and the repo on disk place them in `networking/`).

## Skills Structure

A single skill following the [Agent Skills spec](https://github.com/anthropics/skills): one root `SKILL.md` entry point → 9 category directories (each with an `INDEX.md`) → 23 expert CLI guides.

```text
swe-cli-skills/
├── SKILL.md                  ← Agent reads this first (index + quick reference)
├── SKILL_TEMPLATE.md         ← Template for contributing new CLI guides
└── skills/
    ├── cloud/       (aws, gcloud, azure)
    ├── iac/         (terraform)
    ├── containers/  (docker, kubectl, helm)
    ├── git-vcs/     (git, gh)
    ├── dev-tools/   (jq, make, sed)
    ├── package-managers/ (npm, pip-uv)
    ├── databases/   (psql, redis)
    ├── platforms/   (stripe, sentry, vercel, firebase, fly)
    └── networking/  (curl, ssh)
```

**Guide frontmatter:** Most guides carry YAML frontmatter with `name`, `description`, `version` (targeted CLI version, e.g. `"1.7+"` for jq), and `category` (e.g. `dev-tools`). A few guides (e.g. `stripe.md`) have no frontmatter at all.

**7-section guide anatomy** (each guide, per SKILL.md:117-125 and SKILL_TEMPLATE.md):

1. **Setup & Auth** — Installation and credential configuration
2. **Core Workflows** — The 20% of commands covering 80% of usage
3. **Flag Gotchas** — Ordering traps, version quirks, surprising defaults
4. **Error Patterns** — Real error messages → real fixes
5. **Anti-Patterns** — "Never do X because Y" with safe alternatives
6. **Composability** — How to pipe this CLI with others (aws → jq → xargs)
7. **Agent Constraints** — Non-interactive alternatives, TTY workarounds

**Critical gotchas:** The root `SKILL.md` opens with a "Quick Reference: Critical Gotchas" section listing 17 highest-impact mistakes (SKILL.md:87-107) — including AWS S3 `--exclude`/`--include` ordering, `terraform import` without a follow-up `plan`, `git rebase -i` hanging without a TTY, `KEYS *` blocking Redis in production, and `firebase deploy` without `--only` deploying everything.

## Tech Stack

| Component | Technology |
|---|---|
| **Format** | Markdown (SKILL.md, Agent Skills spec) |
| **Frontmatter** | YAML (name, description, version, category) |
| **Package Manager** | npx (skills CLI), AdaL plugin marketplace |
| **CLI Coverage** | 23 CLIs across 9 categories |
| **Guides** | 23 guide files, ~184-377 lines each |

## Deployment

### npx skills CLI (recommended)

```bash
npx skills add SylphAI-Inc/swe-cli-skills
```

### AdaL Plugin Marketplace

```bash
# Add the marketplace (one-time)
/plugin marketplace add SylphAI-Inc/swe-cli-skills

# Install the skill
/plugin install swe-cli-skills@swe-cli-skills
```

### Manual Install (per agent)

```bash
# AdaL (project-level, recommended)
git clone https://github.com/SylphAI-Inc/swe-cli-skills.git .adal/skills/swe-cli-skills

# Claude Code
git clone https://github.com/SylphAI-Inc/swe-cli-skills.git .claude/skills/swe-cli-skills

# Codex / OpenAI Agents
git clone https://github.com/SylphAI-Inc/swe-cli-skills.git .codex/skills/swe-cli-skills

# Gemini CLI / Copilot / Cursor / Windsurf — clone into the agent's skills dir
```

## Usage

The skill is loaded on demand rather than imported wholesale:

1. Your agent sees `swe-cli-skills` in its skill index (name + description).
2. When a CLI task comes up, it reads `SKILL.md` (lightweight — just the index + gotchas).
3. It loads the specific CLI guide it needs (e.g. `skills/iac/terraform.md`).
4. It executes with expert-level knowledge (correct flag ordering, non-interactive variants, safe alternatives).

Compatible with any agent supporting the SKILL.md standard: **AdaL, Claude Code, OpenAI Codex, Gemini CLI, GitHub Copilot, Cursor, Windsurf, Aider, OpenCode.**

## Roadmap

- [x] **v0.1** — Core 10 CLIs (aws, terraform, docker, kubectl, helm, git, gh, jq, curl, ssh)
- [x] **v0.2** — 16 CLIs with category sub-indexes (gcloud, azure, npm, pip/uv, psql, redis-cli)
- [x] **v0.3** — 23 CLIs with platforms & expanded dev-tools (stripe, sentry, vercel, firebase, fly, sed, make)
- [ ] **v0.4** — rsync, mysql, mongo, yarn/pnpm, cargo, go, poetry, openssl
- [ ] **v1.0** — 30+ CLIs, community contributions, CI validation
- [ ] **Future** — Version-specific skill variants, auto-update from changelogs

## Related

- [[superpowers]] — Full dev methodology skill pack (complementary approach)
- [[skills]] — General skills collection with similar SKILL.md format
- [[agent-rules-books]] — Rule-based agent guidance
- [[hermes-agent]] — MCP hub that loads SKILL.md skills
- [[abvx-agent-skills]] — Another agent skill pack
