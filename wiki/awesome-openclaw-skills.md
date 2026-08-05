---
name: awesome-openclaw-skills
tags: [cli, developer-tools, documentation, git, openclaw, skills-platform, reference, awesome-openclaw-skills]
description: "Curated list of 5300+ community-built OpenClaw skills organized by 30 categories"
source: sources/awesome-openclaw-skills/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Awesome OpenClaw Skills

**Source:** `sources/awesome-openclaw-skills/`

A curated "awesome list" of community-built OpenClaw skills from the ClawHub registry. Filters 7,215 entries (spam, duplicates, low-quality, crypto, and malicious) down to 5,300+ curated skills organized by 30 categories. Licensed under CC0-1.0. Skills extend the OpenClaw locally-running AI assistant with external service integrations, workflow automation, and specialized task capabilities.

| Field | Value |
|---|---|
| **Origin** | [VoltAgent/awesome-clawdbot-skills](https://github.com/VoltAgent/awesome-clawdbot-skills) |
| **License** | CC0-1.0 |
| **Skills curated** | 5,300+ (7,215 entries filtered out) |
| **Categories** | 30 |
| **Source** | `sources/awesome-openclaw-skills/` |

## Overview

OpenClaw is a locally-running AI assistant that operates directly on your machine. Skills extend its capabilities, allowing it to interact with external services, automate workflows, and perform specialized tasks. This curated collection helps users discover and install the right skills for their needs from the ClawHub public registry (clawhub.ai), which hosts thousands of community-built skills. The list serves as both a discovery tool and a source of inspiration for OpenClaw use cases, with a community maintenance process via [ClawSkills.sh](https://clawskills.sh/).

## Key Features

- **30 Categories** covering AI/LLMs, Apple services, browser automation, CLI utilities, coding agents & IDEs (1,184 skills — the largest category), communication, data/analytics, DevOps & cloud (392 skills), gaming, git & GitHub (167 skills), health/fitness, image & video generation (170 skills), iOS/macOS development, marketing/sales, media/streaming, Moltbook (29 skills), notes/PKM, PDF/documents, personal development, productivity/tasks, search & research (345 skills), security/passwords, self-hosted/automation, shopping/e-commerce, smart home/IoT, speech/transcription, transportation, web & frontend development (920 skills), calendar/scheduling, and Clawdbot tools. *Count drift note: README ToC counts occasionally differ from the per-category file headers (e.g. Coding Agents & IDEs ToC 1,184 vs file 1,202; DevOps & Cloud 393 vs 392; Git & GitHub 167 vs 159; Search & Research 345 vs 354; Image & Video 170 vs 172; CLI Utilities 180 vs 179) — a source-side inconsistency.*
- **Quality Filters**: 4,065 spam entries excluded (bulk/bot accounts), 1,040 duplicates removed, 851 low-quality/non-English descriptions filtered, 886 crypto/blockchain entries excluded, 373 malicious skills removed based on published security audits (researcher-published, excluding VirusTotal) — 7,215 total entries not taken from OpenClaw's official skill registry
- **Ecosystem Tools Section**: References to Composio (managed OAuth across 1,000+ apps), MyClaw (cloud-hosted OpenClaw with one-click setup), SerpApi (real-time Google Search/YouTube/Amazon data), trentclaw (security/config auditing), and 25+ LLM provider support
- **Security Notice**: Skills are curated, not audited — may be updated after inclusion; VirusTotal partnership via ClawHub; recommended tools include Snyk Skill Security Scanner and Agent Trust Hub
- **Installation Instructions**: Four methods — `openclaw skills install <slug>`, `npx clawhub install <slug>`, manual copy to `~/.openclaw/skills/` or `<project>/skills/`, or paste GitHub link in chat

## Architecture

A flat "awesome list" repository with a markdown-based directory structure. Each category is a separate `.md` file listing skills with ClawHub links and one-line descriptions. The `README.md` serves as the top-level index with filter statistics, ecosystem information, and skill sample listings in expandable sections.

### Key Source Layout

| Path | Purpose |
|---|---|
| `README.md` | Main index (large file), skill count stats, ecosystem tools, installation guide, 30 category sections |
| `categories/` | 30 category `.md` files, each listing skills in that domain with links |
| `categories/ai-and-llms.md` | AI/LLM category |
| `categories/coding-agents-and-ides.md` | Coding agents (1,184 skills) |
| `categories/devops-and-cloud.md` | DevOps & Cloud category (392 skills) |
| `categories/web-and-frontend-development.md` | Web/Frontend (920 skills) |
| `categories/browser-and-automation.md` | Browser automation (323 skills) |
| `categories/search-and-research.md` | Search & research (345 skills) |
| `categories/git-and-github.md` | Git & GitHub (167 skills) |
| `categories/cli-utilities.md` | CLI Utilities (180 skills) |
| `categories/clawdbot-tools.md` | OpenClaw platform tools (37 skills) |
| `categories/apple-apps-and-services.md` | Apple ecosystem (44 skills) |
| `categories/image-and-video-generation.md` | Image/video generation (170 skills) |
| `CONTRIBUTING.md` | Contribution guidelines (skills must be published on ClawHub, no external repo links) |
| `.claude/settings.local.json` | Claude-specific permission config |
| `.github/workflows/pr-check.yml` | PR validation workflow |

## Usage

### Installation

```bash
# OpenClaw CLI (recommended)
openclaw skills install <skill-slug>

# ClawHub CLI (for registry-managed folders outside OpenClaw)
npx clawhub install <skill-slug>

# Manual installation
cp -r <skill-folder> ~/.openclaw/skills/

# Or paste GitHub link directly in chat
```

### For contributors

This list only includes skills already published on [ClawHub](https://clawhub.ai). Include the ClawHub link (e.g. `https://clawhub.ai/steipete/slack`) in PR descriptions. See CONTRIBUTING.md for details. PR validation runs via GitHub Actions workflow.

### Self-hosting tip

Pin your OpenClaw Docker image to a specific tag and snapshot your skills volume before upgrades — makes rollbacks painless when a skill update misbehaves.

## Related

- [[openclaw]] — The AI assistant platform these skills extend and enhance
- [[skills]] — General agent skills platform and registry standard
- [[awesome-openclaw-usecases]] — Complementary awesome list of OpenClaw use case patterns and workflows
- [[openclaw-plugin-claude-code]] — Plugin integrating OpenClaw with Claude Code for cross-platform agent orchestration
- [[hermes-agent]] — Competing agent platform with its own plugin ecosystem
- [[openclaw-container]] — Container deployment for OpenClaw with Quadlet and Docker packaging
