---
title: hermes-startup-architect
subtitle: CodeGraph Verification
date: 2026-07-12
tags: [hermes-startup-architect, codegraph-verify, hermes-agent, startup]
suffix: .codegraph-verify
source: sources/hermes-startup-architect/
related: [[hermes-startup-architect]], [[hermes-agent]], [[af-deep-research]], [[research-methodology]]
verified-by: codegraph-explore
---

# hermes-startup-architect — CodeGraph Verification

**Verification date:** 2026-07-12
**Verified by:** codegraph-explore
**Source reference:** `sources/hermes-startup-architect/`

## Claim-1: Self-contained Hermes SKILL.md with trigger phrases and structured workflow

The repository contains a single Hermes skill at `skills/business/startup-architect/SKILL.md` with YAML frontmatter defining trigger phrases (startup idea:, analyze this startup:, create a startup kit for, here is my startup concept) and a 4-step structured workflow.

**Source evidence:** `skills/business/startup-architect/SKILL.md` lines 1-10:
```yaml
---
name: startup-architect
description: A comprehensive workflow for researching a startup idea and generating a full startup kit...
version: 1.0.0
triggers:
  - "startup idea:"
  - "analyze this startup:"
  - "create a startup kit for"
  - "here is my startup concept"
---
```

**Supporting detail:** Lines 16-18 define the four workflow steps: "STEP 1: MARKET RESEARCH (Mandatory)", "STEP 2: PROJECT INITIALIZATION", "STEP 3: ASSET GENERATION", "STEP 4: COMPLETION."

## Claim-2: Research-first approach with mandatory 3+ web searches

The skill requires at least 3 distinct web searches before generating any output, targeting market size (TAM/SAM/SOM), competitor analysis (pricing/positioning), and market gaps/why-now factors. Generic or placeholder data is explicitly prohibited.

**Source evidence:** `SKILL.md` lines 18-23:
```
### STEP 1: MARKET RESEARCH (Mandatory)
Perform at least 3 distinct web searches to gather real data.
- **Search 1:** Market size (TAM/SAM/SOM), growth rates, and industry trends.
- **Search 2:** Top competitors, their pricing, and market positioning.
- **Search 3:** Market gaps, customer pain points, and "Why Now" factors.
- **Goal:** Extract real numbers, specific company names, and current year trends.
```

**Supporting detail:** Lines 96-98 (Critical Rules): "**RESEARCH FIRST:** Never use generic data. If research fails, try different search terms." Lines 97-98: "**NO PLACEHOLDERS:** All text must be plausible, specific, and professionally written."

## Claim-3: 8-file startup kit generation with sequential confirmation gates

The skill generates 8 files one-by-one with explicit `✅` confirmation between each file: `market_analysis.md`, `competitor_map.md`, `product_spec.md`, `business_model.md`, `pitch_deck.md`, `product_roadmap.md`, `investor_pitch.md`, and `landing_page.html`.

**Source evidence:** `SKILL.md` lines 46-89 define all 8 files with detailed specifications:
- Lines 48-51: `market_analysis.md` — "Detailed TAM/SAM/SOM with real researched numbers. 3-5 major market trends and key opportunities."
- Lines 53-56: `competitor_map.md` — "Profile 5 real competitors: Name, URL, Pricing, Strengths, Weaknesses."
- Lines 58-63: `product_spec.md` — "Problem/Solution statement. 5 core MVP features. Tech stack recommendation."
- Lines 65-67: `business_model.md` — "Revenue streams and pricing tiers (Free/Pro/Enterprise). Unit economics and growth loops. Top 3 KPIs."
- Lines 69-70: `pitch_deck.md` — "5 slides (Problem, Solution, Market, Business Model, Ask)."
- Lines 72-75: `product_roadmap.md` — "Month 1-3: MVP, Month 4-6: Feedback Loop, Month 7-12: Scaling."
- Lines 77-80: `investor_pitch.md` — "One-paragraph elevator pitch. Why Now, Why Us. Projected milestones."
- Lines 82-89: `landing_page.html` — "Tailwind CDN, Inter font, Unsplash images, Animate.css, Indigo-to-Purple gradients, 7 components."

**Supporting detail:** Line 46: "Generate the following 8 files one-by-one. **Confirm each file with ✅ before moving to the next.** " Line 97: "**SEQUENTIAL SAVING:** Save one file at a time and acknowledge it."

## Claim-4: Optional X/Twitter social signal pass via Hermes Tweet plugin

The skill supports an optional social signal pass using the Hermes Tweet plugin for scraping tweets, reading replies, and researching follower audiences — with explicit prohibitions on posting or DMing without human confirmation.

**Source evidence:** `SKILL.md` lines 25-37:
```
**Optional X/Twitter social signal pass:** If Hermes Tweet is installed
(`hermes plugins install Xquik-dev/hermes-tweet --enable`) and `XQUIK_API_KEY`
is configured, use it as a native Hermes Agent X/Twitter plugin...
- `tweet_explore`: scrape/search tweets and search Twitter/X for pain points,
  competitor mentions, launch reactions, and "why now" signals.
- `tweet_read`: read tweet replies, look up users, and monitor tweets from
  founders, customers, competitors, analysts, and early adopters.
- `tweet_action`: use read-side export followers research only when it helps
  map ICP clusters or competitor audiences.
```

**Supporting detail:** Lines 36-37: "Do not post tweets, post replies, send DMs, or automate X actions in this skill unless the human explicitly confirms the exact action." The `README.md` (lines 23-30) and `SETUP.md` (lines 22-30) both document the same Hermes Tweet integration pattern.

## Claim-5: Complete example output kit in `examples/forge-kit/`

The repository includes a full example output from a live session under `examples/forge-kit/` containing all 8 generated files for the fictional startup "FORGE (The AI Asset Marketplace)."

**Source evidence:** Directory listing of `examples/forge-kit/`:
- `market_analysis.md` — TAM/SAM/SOM with real 2026-estimate numbers ($1.2T TAM, $14.1B SAM, $215M SOM), market trends, key opportunities.
- `competitor_map.md` — 5 real competitor profiles.
- `product_spec.md`, `business_model.md`, `pitch_deck.md`, `product_roadmap.md`, `investor_pitch.md`, `index.html` — all 8 files present.
- **Naming drift:** the spec file is named `landing_page.html` (SKILL.md:82), but the example kit ships it as `index.html` — the wiki flags this drift.

**Supporting detail:** `examples/forge-kit/market_analysis.md` lines 1-21 show concrete data: "TAM (Total Addressable Market): $1.2 Trillion" with specific percentages, named trends, and named opportunities. This confirms the skill produces real, non-placeholder content. `README.md` line 43: "See the `/examples/` folder for the full FORGE launch kit we built during our live session."

## Claim-6: `landing_page.html` uses high-fidelity Tailwind CSS with specific design tokens

The landing page specification mandates Tailwind CDN, Inter font, Unsplash imagery, Animate.css animations, and a specific Indigo-to-Purple-to-Pink gradient theme with 7 named components.

**Source evidence:** `SKILL.md` lines 82-89:
```
8. **landing_page.html**
   - High-fidelity HTML/CSS using Tailwind CDN.
   - Fonts: Inter (Google Fonts).
   - Graphics: Unsplash-sourced product/hero images.
   - Animations: Animate.css.
   - Theme: Indigo to Purple to Pink gradients.
   - Components: Nav, Hero, Problem/Solution (3 cards), Features (3 cards),
     Pricing (2 tiers), Testimonials (3 quotes), Footer.
```

**Supporting detail:** The `examples/forge-kit/index.html` file (confirmed present via filesystem listing) is the actual rendered output matching this spec. `README.md` line 42: "`landing_page.html` (High-fidelity Tailwind CSS site)."

## Claim-7: Pitch deck slide 4 is "Business Model"

The 5-slide pitch deck names the fourth slide "Business Model" — not just "Model" as some summaries state.

**Source evidence:** `SKILL.md:69` — "5 slides (Problem, Solution, Market, Business Model, Ask)." The wiki was corrected to the full slide title.

## Claim-8: No LICENSE file — license status is an upstream gap; SETUP.md duplicates README.md

The repository contains no license file of any kind, and `SETUP.md` is byte-identical to `README.md`.

**Source evidence:**
- `find . -iname "LICENSE*"` at repo root returns zero results (only `.git/`, `README.md`, `SETUP.md`, `examples/`, `skills/` present)
- `diff README.md SETUP.md` exits 0 — both files are exactly 2205 bytes, byte-identical
- `README.md` contains no license section; earlier claims of "MIT-licensed" are NOT supported by the repo itself
- **Verdict:** ⚠️ FLAGGED as upstream gap — wiki states the license is unspecified and notes the SETUP.md duplication

## Dependency Map

```
hermes-startup-architect
  └─► hermes-agent (Hermes Agent runtime that executes this skill)
  └─► af-deep-research (deep research engine that could enhance the startup research phase)
  └─► research-methodology (research methodology skill for structured investigation)
  └─► hermes-workspace (workspace that can install and run this startup skill)
  └─► n8n (workflow automation for automated startup data collection)
  └─► agentfield (orchestration layer for parallel startup analysis)
  └─► hermzner (Hetzner infrastructure cost analysis paired with business_model)
  └─► open-design (design system approach for landing page templates)
```
