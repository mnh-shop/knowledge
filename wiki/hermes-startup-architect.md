---
name: hermes-startup-architect
tags: [hermes-startup-architect, hermes-agent, skill, startup, research, business, entrepreneurship]
description: "Hermes Agent skill for transforming startup ideas into research-backed 0-to-1 kits with 8 deliverable files"
source: sources/hermes-startup-architect/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Hermes Startup Architect

## Overview

A structured workflow skill for [[hermes-agent]] that transforms a raw startup idea into a comprehensive, research-backed 0-to-1 startup kit. Authored by Dilek, the skill activates on trigger phrases such as "startup idea:", "analyze this startup:", "create a startup kit for", and "here is my startup concept". Each invocation produces 8 files: market analysis, competitor map, product spec, business model, pitch deck, product roadmap, investor pitch, and a high-fidelity Tailwind CSS landing page. The skill is designed as a self-contained Hermes SKILL.md that lives under `skills/business/startup-architect/` and uses Hermes's built-in `web_search`, `terminal`, and `write_file` tools to gather real market data and produce professional-grade deliverables. It is not a standalone application — it runs inside the Hermes Agent runtime and depends on Hermes for execution.

## Key Features

- **Research-first approach with mandatory market data** — the workflow requires at least 3 distinct web searches before generating any output: market size (TAM/SAM/SOM with real numbers), competitor analysis (pricing and positioning of real companies), and market gaps/customer pain points/why-now factors. The skill explicitly prohibits generic or placeholder data — every analysis must be based on real market research with current-year trends, specific company names, and verifiable numbers.

- **8-file startup kit generation** — each invocation produces a complete startup package: `market_analysis.md` (TAM/SAM/SOM trends and opportunities), `competitor_map.md` (5 real competitors with URLs, pricing, strengths/weaknesses), `product_spec.md` (problem/solution, 5 MVP features, tech stack), `business_model.md` (revenue streams, pricing tiers, unit economics, 3 KPIs), `pitch_deck.md` (5 slides: Problem, Solution, Market, Business Model, Ask), `product_roadmap.md` (12-month roadmap in 3 phases), `investor_pitch.md` (narrative elevator pitch with why-now and milestones), and `landing_page.html` (investor-ready Tailwind CSS page with Unsplash imagery, Animate.css, and Indigo-to-Purple-to-Pink gradients). **Naming drift:** the spec names the landing page `landing_page.html` (SKILL.md:82), but the example kit in `examples/forge-kit/` actually ships it as `index.html`.

- **Optional X/Twitter social signal pass** — if the Hermes Tweet plugin is installed (`hermes plugins install Xquik-dev/hermes-tweet --enable`) and `XQUIK_API_KEY` is configured, the skill can perform an optional social signal pass before writing the kit. It uses `tweet_explore` to scrape tweets for pain points and competitor mentions, `tweet_read` to monitor founders and customers, and `tweet_action` for read-side follower research. This adds real-time social proof to the market analysis. The skill explicitly prohibits posting tweets or DMs without human confirmation.

- **Sequential asset generation with confirmation gates** — the 8 files are generated one-by-one with explicit `✅` confirmation between each file. Each file is saved via `write_file` or `terminal` with no placeholder text allowed. The workflow enforces that all text must be plausible, specific, and professionally written — no lorem ipsum, no "TBD", no boilerplate.

- **Flexible setup for self-hosting** — the skill is installed by copying the `startup-architect` folder into the Hermes skills directory (`~/.hermes/skills/business/startup-architect/SKILL.md`). No additional dependencies beyond Hermes Agent itself. An example output kit is available under `examples/forge-kit/` showing the full 8-file output from a live session. **Upstream gap:** the repo contains NO LICENSE file (no MIT or other license is declared anywhere), so the license status is unspecified despite some external descriptions labeling it MIT-licensed. `SETUP.md` is a byte-identical duplicate of `README.md`.

## Workflow Steps

The skill defines a strict 4-step research-to-output pipeline:

1. **Market Research (Mandatory)** — perform 3+ web searches for TAM/SAM/SOM, competitor pricing, and market gaps. Optionally run the X/Twitter social signal pass.
2. **Project Initialization** — create the output directory (`~/Desktop/startup_kit/`).
3. **Asset Generation** — generate and save all 8 files sequentially with per-file confirmation.
4. **Completion Declaration** — list all 8 files with a one-sentence summary of each.

## Installation

```bash
# Prerequisite: Hermes Agent installed and configured

# Copy the skill into place
mkdir -p ~/.hermes/skills/business/startup-architect
cp skills/business/startup-architect/SKILL.md ~/.hermes/skills/business/startup-architect/SKILL.md

# Activate via Hermes prompt:
# "I want to build [Your Startup Idea]. Use the startup-architect skill to research and build my kit."

# Optional: install Hermes Tweet for X/Twitter signals
hermes plugins install Xquik-dev/hermes-tweet --enable
```

## Related

- [[hermes-agent]] — Hermes Agent runtime that executes this skill
- [[af-deep-research]] — Deep research engine that could enhance the startup research phase
- [[hermes-startup-architect-skill]] — Skill asset definition in `assets/skills/`
- [[hermes-workspace]] — Hermes workspace that can install and run this startup skill
- [[n8n]] — Workflow automation that could automate startup research data collection
- [[agentfield]] — Orchestration layer that could run parallel startup analyses
- [[hermzner]] — Hetzner infrastructure automation (pair with business_model for cost analysis)
- [[open-design]] — Design system approach that could enhance landing page templates
