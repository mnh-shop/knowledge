---
name: awesome-openclaw-skills
tags: [ai-llm, cli, developer-tools, documentation, git, openclaw, plugin-sdk, skills-platform]
description: "Curated list of 5300+ community-built OpenClaw skills organized by 30 categories"
---

# Awesome OpenClaw Skills

**Source:** `sources/awesome-openclaw-skills/`

A curated "awesome list" of community-built OpenClaw skills from the ClawHub registry. Filters 7,215 entries (spam, duplicates, low-quality, crypto, and malicious) down to 5,300+ curated skills organized by category. Licensed under CC0-1.0.

| Field | Value |
|---|---|
| **Origin** | [VoltAgent/awesome-clawdbot-skills](https://github.com/VoltAgent/awesome-clawdbot-skills) |
| **License** | CC0-1.0 |
| **Skills curated** | 5,300+ from 12,415+ total registrations |
| **Categories** | 30 |
| **Source** | `sources/awesome-openclaw-skills/` |

## Key Features

- **30 Categories** covering AI/LLMs, Apple services, browser automation, CLI utilities, coding agents, communication, data/analytics, DevOps/cloud, gaming, git/GitHub, health/fitness, image/video generation, iOS/macOS development, marketing/sales, media/streaming, notes/PKM, PDF/documents, personal development, productivity/tasks, search/research, security/passwords, self-hosted/automation, shopping/e-commerce, smart home/IoT, speech/transcription, transportation, and web development.
- **Quality Filters:** 4,065 spam entries excluded, 1,040 duplicates removed, 851 low-quality/non-English descriptions filtered, 886 crypto/blockchain entries excluded, 373 malicious skills removed based on published security audits.
- **Installation Instructions:** Multiple install methods including `openclaw skills install <slug>`, `npx clawhub install <slug>`, manual copy to `~/.openclaw/skills/`, or paste GitHub link directly.
- **Ecosystem Tools Section:** References to Composio for managed OAuth across 1,000+ apps.
- **Community Standard:** Only includes skills published on ClawHub, no external repo links.

## Architecture

A flat "awesome list" repository with a markdown-based directory structure. Each category is a separate `.md` file listing skills with ClawHub links and one-line descriptions. The `README.md` serves as the top-level index with filter statistics and ecosystem information.

### Key Source Layout

| Path | Purpose |
|---|---|
| `README.md` | Main index (132KB), skill count stats, ecosystem tools, installation guide |
| `categories/` | 30 category `.md` files, each listing skills in that domain |
| `categories/ai-and-llms.md` | AI/LLM category |
| `categories/devops-and-cloud.md` | DevOps & Cloud category (392 skills) |
| `categories/cli-utilities.md` | CLI Utilities category (179 skills) |
| `categories/clawdbot-tools.md` | OpenClaw platform tools (37 skills) |
| `categories/apple-apps-and-services.md` | Apple ecosystem (44 skills) |
| `CONTRIBUTING.md` | Contribution guidelines |
| `.claude/settings.local.json` | Claude-specific permission config |
| `.github/workflows/pr-check.yml` | PR validation workflow |

## Interfaces

- **Skills Registry:** Skills installed via `openclaw skills install <slug>` or `npx clawhub install <slug>`
- **ClawHub API:** Skills sourced from https://clawhub.ai, the official OpenClaw public skills registry
- **Web:** Category pages hosted at https://clawskills.sh/skills/

## Related

- [[openclaw]] -- The AI assistant platform these skills extend
- [[hermes-agent]] -- Competing agent platform with its own plugin ecosystem
- [[openclaw]] -- The AI assistant platform these skills extend
