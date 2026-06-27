---
name: hermes-startup-architect-skill
tags: [agent-gateway, hermes-agent, messaging, multi-platform, plugin-sdk, skill, skills-platform, typescript]
description: Hermes Agent skill that transforms a raw startup idea into a comprehensive research-backed startup kit with 8 files
---

# Skill: Startup Architect

**Source:** `sources/hermes-startup-architect/skills/business/startup-architect/SKILL.md`
**Version:** 1.0.0
**Type:** Hermes Agent skill (SKILL.md format)

## Purpose

Transforms a raw startup idea into a comprehensive, research-backed startup
kit. This is a skill that runs inside Hermes Agent — it's a structured
workflow, not a CLI tool or library.

## How it works

When a user says a trigger phrase ("startup idea:", "analyze this startup:",
"create a startup kit for", "here is my startup concept"), Hermes loads this
skill and executes a 4-step workflow using its built-in tools
(`web_search`, `terminal`, `write_file`):

### Step 1: Market Research (mandatory)
3+ web searches for real market data:
- TAM/SAM/SOM, growth rates, industry trends
- Top competitors, pricing, market positioning
- Market gaps, customer pain points, "Why Now" factors

Optional: X/Twitter social signals via [hermes-tweet plugin](https://github.com/Xquik-dev/hermes-tweet)

### Step 2: Project Init
Creates `~/Desktop/startup_kit/` directory.

### Step 3: Asset Generation (8 files)
Generated one at a time, each confirmed with ✅:

| # | File | Content |
|---|---|---|
| 1 | `market_analysis.md` | TAM/SAM/SOM with real numbers, 3-5 trends |
| 2 | `competitor_map.md` | 5 real competitors, gap analysis |
| 3 | `product_spec.md` | Problem/solution, 5 MVP features, tech stack |
| 4 | `business_model.md` | Revenue streams, pricing, unit economics, KPIs |
| 5 | `pitch_deck.md` | 5 slides (Problem/Solution/Market/Model/Ask) |
| 6 | `product_roadmap.md` | 12-month timeline (MVP → Growth → Scaling) |
| 7 | `investor_pitch.md` | Elevator pitch, "Why Now", milestones |
| 8 | `landing_page.html` | Tailwind CSS + Inter font + Unsplash images |

### Step 4: Completion
Lists all 8 files with one-sentence summaries.

## Critical rules

- Research first — never generic data
- One file at a time — no batch saves
- No placeholder text — every word is specific and professional
- Landing page must be investor-ready (visually polished, responsive)
- X/Twitter: read-only only unless human explicitly confirms

## Example output

`sources/hermes-startup-architect/examples/forge-kit/` — a complete FORGE
launch kit with all 8 files.

## Installation

```bash
mkdir -p ~/.hermes/skills/business/startup-architect
cp skills/business/startup-architect/SKILL.md ~/.hermes/skills/business/startup-architect/SKILL.md
```

Then trigger with: "I want to build [idea]. Use the startup-architect skill."

## Related

- [[hermes-startup-architect]] -- Wiki entry for Startup Architect
- [[hermes-agent]] -- Hermes Agent runtime that executes this skill

## Links

- Wiki: [[hermes-startup-architect]]
- Source: `sources/hermes-startup-architect/`
