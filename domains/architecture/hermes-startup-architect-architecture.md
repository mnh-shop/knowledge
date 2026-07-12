---
name: hermes-startup-architect-architecture
tags: [hermes-startup-architect, architecture, hermes-agent, skill]
description: "Research-first startup pipeline as a Hermes Agent skill — 4-step workflow, 8-file forge-kit generation, mandatory market research gates"
source: sources/hermes-startup-architect/
verification_date: 2026-07-12
verified_by: source SKILL.md + README + wiki
---

# Hermes Startup Architect — Architecture

**Source:** `sources/hermes-startup-architect/skills/business/startup-architect/SKILL.md`

## Overview

Hermes Startup Architect is a structured workflow **skill** for the [[hermes-agent]] platform that transforms a raw startup idea into a comprehensive, research-backed 0-to-1 startup kit. It is not a standalone application — it runs inside the Hermes Agent runtime and depends on Hermes's built-in `web_search`, `terminal`, and `write_file` tools. The skill is self-contained in a single `SKILL.md` file and produces 8 deliverable files per invocation.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Hermes Agent Runtime                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Hermes Tools                                 │   │
│  │  ┌───────────┐  ┌───────────┐  ┌─────────────────────┐  │   │
│  │  │ web_search │  │ terminal  │  │     write_file      │  │   │
│  │  └─────┬─────┘  └─────┬─────┘  └──────────┬──────────┘  │   │
│  └────────┼──────────────┼───────────────────┼──────────────┘   │
│           │              │                   │                   │
│  ┌────────┴──────────────┴───────────────────┴──────────────┐   │
│  │           Startup Architect Skill (SKILL.md)              │   │
│  │                                                           │   │
│  │  ┌───────────────────────────────────────────────────┐   │   │
│  │  │  Activation Triggers                               │   │   │
│  │  │  "startup idea:", "analyze this startup:",        │   │   │
│  │  │  "create a startup kit for", "here is my concept" │   │   │
│  │  └──────────────────────┬────────────────────────────┘   │   │
│  │                         │                                 │   │
│  │  ┌──────────────────────v────────────────────────────┐   │   │
│  │  │  STEP 1: MARKET RESEARCH (Mandatory)               │   │   │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────────┐     │   │   │
│  │  │  │ Search 1 │ │ Search 2 │ │  Search 3    │     │   │   │
│  │  │  │ TAM/SAM/ │ │Competitor│ │Market Gaps   │     │   │   │
│  │  │  │ SOM      │ │Pricing   │ │& "Why Now"   │     │   │   │
│  │  │  └──────────┘ └──────────┘ └──────────────┘     │   │   │
│  │  │  ┌──────────────────────────────────────────┐   │   │   │
│  │  │  │ Optional: X/Twitter Social Signal Pass   │   │   │   │
│  │  │  │ (tweet_explore, tweet_read, tweet_action)│   │   │   │
│  │  │  └──────────────────────────────────────────┘   │   │   │
│  │  └──────────────────────┬────────────────────────────┘   │   │
│  │                         │                                 │   │
│  │  ┌──────────────────────v────────────────────────────┐   │   │
│  │  │  STEP 2: PROJECT INITIALIZATION                    │   │   │
│  │  │  mkdir -p ~/Desktop/startup_kit                    │   │   │
│  │  └──────────────────────┬────────────────────────────┘   │   │
│  │                         │                                 │   │
│  │  ┌──────────────────────v────────────────────────────┐   │   │
│  │  │  STEP 3: ASSET GENERATION (8 files, sequential)    │   │   │
│  │  │                                                     │   │   │
│  │  │  1. market_analysis.md     (TAM/SAM/SOM + trends)  │   │   │
│  │  │  2. competitor_map.md      (5 real competitors)     │   │   │
│  │  │  3. product_spec.md        (MVP features + stack)  │   │   │
│  │  │  4. business_model.md      (revenue + pricing)     │   │   │
│  │  │  5. pitch_deck.md          (5 slides)              │   │   │
│  │  │  6. product_roadmap.md     (12-month plan)         │   │   │
│  │  │  7. investor_pitch.md      (narrative pitch)       │   │   │
│  │  │  8. landing_page.html      (Tailwind CSS)          │   │   │
│  │  │                                                     │   │   │
│  │  │  Each file: ✅ confirmed before next                │   │   │
│  │  └──────────────────────┬────────────────────────────┘   │   │
│  │                         │                                 │   │
│  │  ┌──────────────────────v────────────────────────────┐   │   │
│  │  │  STEP 4: COMPLETION                                │   │   │
│  │  │  List all 8 files with one-sentence summaries      │   │   │
│  │  └────────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow Pipeline

The skill defines a strict **4-step research-to-output pipeline** with mandatory gates:

1. **Market Research** — Enforces 3+ distinct web searches before any output generation. If Hermes Tweet plugin is installed, an optional social signal pass augments the research with real-time Twitter/X data (pain points, competitor mentions, launch reactions).

2. **Project Initialization** — Creates the output directory (`~/Desktop/startup_kit/`) on the local filesystem.

3. **Sequential Asset Generation** — Generates 8 files one-by-one with per-file confirmation gates (`✅`). Each file is saved via `write_file` or `terminal`, with strict rules against placeholder text (no lorem ipsum, no "TBD", no boilerplate).

4. **Completion Declaration** — Lists all 8 files with a one-sentence summary per file.

### Forge-Kit Pattern

The term "forge-kit" describes the complete 8-file output package. Each file has a specific purpose:

| File | Format | Purpose |
|------|--------|---------|
| `market_analysis.md` | Markdown | TAM/SAM/SOM with real numbers, market trends |
| `competitor_map.md` | Markdown | 5 real competitors with URLs, pricing, SWOT |
| `product_spec.md` | Markdown | Problem/solution, 5 MVP features, tech stack |
| `business_model.md` | Markdown | Revenue streams, pricing tiers, unit economics |
| `pitch_deck.md` | Markdown | 5-slide pitch (Problem, Solution, Market, Model, Ask) |
| `product_roadmap.md` | Markdown | 12-month roadmap in 3 phases |
| `investor_pitch.md` | Markdown | Narrative elevator pitch with why-now |
| `landing_page.html` | HTML/CSS | Tailwind CSS page (Inter, Animate.css, Unsplash imagery) |

## Key Components

### Skill Definition (`SKILL.md`)

A self-contained Hermes Agent skill file with frontmatter metadata (name, version, triggers), a 4-step workflow, and critical rules. Trigger phrases activate the skill when Hermes processes user input. The file lives at `skills/business/startup-architect/SKILL.md` in the Hermes skills directory.

### Hermes Tools Used

- `web_search` — Performs real-time web searches for market data, competitor analysis, and trend research
- `terminal` — Executes shell commands for directory creation and file operations
- `write_file` — Writes each generated asset to disk

### X/Twitter Integration (Optional)

When Hermes Tweet plugin is installed, the skill can:
- `tweet_explore` — Scrape Twitter/X for pain points and competitor signals
- `tweet_read` — Monitor founders, customers, competitors
- `tweet_action` — Read-side export followers for ICP audience mapping

Posting tweets or DMs requires explicit human confirmation — the skill prohibits automated posting.

## Related

- [[hermes-startup-architect]] — Wiki page with full feature reference
- [[hermes-agent]] — Runtime platform that executes this skill
- [[af-deep-research]] — Deep research engine for enhancing the research phase
- [[research-methodology]] — Cross-cutting research patterns
- [[hermes-workspace]] — Workspace platform for running Hermes skills
- [[open-design]] — Design system approach for landing page templates
- [[n8n]] — Workflow automation for automating research data collection
