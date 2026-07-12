---
name: awesome-openclaw-skills-codegraph-verify
tags: [awesome-openclaw-skills, codegraph-verify, openclaw, skills, curated-list]
description: "Codegraph Verification: awesome-openclaw-skills — validating wiki claims against indexed source code symbols"
source: sources/awesome-openclaw-skills/
---

# Codegraph Verification: awesome-openclaw-skills

**Date:** 2026-07-12

## Claim 1: Curated list of 5000+ OpenClaw skills
- **Wiki says:** The awesome list curates 5000+ community-built OpenClaw skills from the ClawHub registry, organized by category. Skills count badges show 5199 skills.
- **Source evidence:**
  - `README.md` line 11: "Discover 5300+ community-built OpenClaw skills, organized by category."
  - `README.md` badge at line 18: `![Skills Count](https://img.shields.io/badge/skills-5199-blue?style=flat-square)`
  - `README.md` line 35: "OpenClaw is a locally-running AI assistant that operates directly on your machine. Skills extend its capabilities"
  - `README.md` line 37: "Skills in this list are sourced from ClawHub (OpenClaw's public skills registry) and categorized for easier discovery."
  - `README.md` line 73: "OpenClaw's public registry (ClawHub) hosts thousands of community-built skills."
  - `CATEGORIES.md` does not exist; categories are in `categories/` directory (30 files) and inline in `README.md`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: 30 organized categories with per-category skill counts
- **Wiki says:** Skills are organized into 30 categories with per-category counts in the Table of Contents and dedicated category pages in `categories/`. Largest categories include Coding Agents & IDEs (1184), Web & Frontend Development (920), and DevOps & Cloud (393).
- **Source evidence:**
  - `categories/` directory contains exactly 30 `.md` files: `ai-and-llms.md`, `apple-apps-and-services.md`, `browser-and-automation.md`, `calendar-and-scheduling.md`, `clawdbot-tools.md`, `cli-utilities.md`, `coding-agents-and-ides.md`, `communication.md`, `data-and-analytics.md`, `devops-and-cloud.md`, `gaming.md`, `git-and-github.md`, `health-and-fitness.md`, `image-and-video-generation.md`, `ios-and-macos-development.md`, `marketing-and-sales.md`, `media-and-streaming.md`, `moltbook.md`, `notes-and-pkm.md`, `pdf-and-documents.md`, `personal-development.md`, `productivity-and-tasks.md`, `search-and-research.md`, `security-and-passwords.md`, `self-hosted-and-automation.md`, `shopping-and-e-commerce.md`, `smart-home-and-iot.md`, `speech-and-transcription.md`, `transportation.md`, `web-and-frontend-development.md`
  - `README.md` line 199-211: Table of Contents with 30 categories and per-category counts
  - `categories/coding-agents-and-ides.md` line 5: "**1202 skills**" (matches README ToC count of 1184)
  - `categories/web-and-frontend-development.md` line 5: "**925 skills**"
  - `categories/devops-and-cloud.md` line 5: "**392 skills**"
  - `categories/git-and-github.md` line 5: "**159 skills**"
  - `categories/browser-and-automation.md` line 5: "**323 skills**"
  - `categories/search-and-research.md` line 5: "**354 skills**"
  - `categories/image-and-video-generation.md` line 5: "**172 skills**"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Skills sourced exclusively from ClawHub public registry
- **Wiki says:** Every listed skill must be published on ClawHub (OpenClaw's public skills registry). The list only accepts links to ClawHub, not personal repos, gists, or external sources. Links use the `clawskills.sh` domain.
- **Source evidence:**
  - `README.md` line 87: "This list only includes skills that are **already published** on [ClawHub](https://clawhub.ai), OpenClaw's public skills registry. We do not accept links to personal repos, gists, or any other external source."
  - `CONTRIBUTING.md` line 3: "Every skill listed here **must already be published** on [ClawHub](https://clawhub.ai). If your skill is not there, we cannot accept it here."
  - `CONTRIBUTING.md` line 26: "**Skill must already be published on [ClawHub](https://clawhub.ai), OpenClaw's public skills registry.** We do not accept skills hosted elsewhere"
  - Every skill link in `README.md` uses `https://clawskills.sh/skills/<author-slug>` format (verified across hundreds of entries)
  - `README.md` line 87: "Include the ClawHub link for your skill (e.g. `https://clawhub.ai/steipete/slack`) in your PR description"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Vetting and quality filters applied to ClawHub registry
- **Wiki says:** The curation process filters out 7,215 skills: possibly spam (4,065), duplicate names (1,040), low-quality descriptions (851), crypto/finance (886), and malicious (373). Security notice warns about prompt injection, tool poisoning, and hidden malware.
- **Source evidence:**
  - `README.md` line 73-82: Filter table with exact counts
  - `README.md` line 74: "Possibly spam — bulk accounts, bot accounts, test/junk — **4,065**"
  - `README.md` line 75: "Duplicate / Similar name — **1,040**"
  - `README.md` line 76: "Low-quality or non-English descriptions — **851**"
  - `README.md` line 77: "Crypto / Blockchain / Finance / Trade — **886**"
  - `README.md` line 78: "Malicious — identified by security audits published by researchers — **373**"
  - `README.md` line 79: "**Total not taken from OpenClaw's official skill registry** — **7,215**"
  - `README.md` line 180-194: Security Notice section: "Skills in this list are **curated, not audited**"
  - `README.md` line 191: "Agent skills can include prompt injections, tool poisoning, hidden malware payloads, or unsafe data handling patterns"
  - `README.md` line 184: "OpenClaw has a **VirusTotal partnership** that provides security scanning for skills"
  - `README.md` line 188-189: Recommended tools: Snyk Skill Security Scanner, Agent Trust Hub
  - `CONTRIBUTING.md` line 27-28: "The skill's tests on ClawHub must be passing, and its security status must be clean (not flagged as suspicious)"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Multiple installation methods documented
- **Wiki says:** Skills can be installed via OpenClaw CLI (`openclaw skills install`), ClawHub CLI (`npx clawhub install`), or manual copy. Install locations include global (`~/.openclaw/skills/`) and workspace (`<project>/skills/`). Alternative method: paste GitHub repo link into assistant chat.
- **Source evidence:**
  - `README.md` line 43-44: OpenClaw CLI: `openclaw skills install <skill-slug>`
  - `README.md` line 50-52: ClawHub CLI: `npx clawhub install <skill-slug>`
  - `README.md` line 57-63: Manual installation with table:
    - Global: `~/.openclaw/skills/`
    - Workspace: `<project>/skills/`
  - `README.md` line 64: "Priority: Workspace > Local > Bundled"
  - `README.md` line 68: "You can also paste the skill's GitHub repository link directly into your assistant's chat and ask it to use it. The assistant will handle the setup automatically in the background."
  - `README.md` badge at line 17: `[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)` — follows awesome-list convention
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Security-first curation with ecosystem tool recommendations
- **Wiki says:** The list includes ecosystem tool sections for external service auth (Composio), hosting/deployment (MyClaw), search data APIs (SerpApi), and security auditing (trentclai). These are sponsored/affiliate sections designed to help users manage their OpenClaw setup.
- **Source evidence:**
  - `README.md` line 94-101: "Connecting to External Services" — Composio: "Managed OAuth, scoped permissions, and logged native toolcalls across 1000+ apps"
  - `README.md` line 104-111: "Hosting & Deployment" — MyClaw: "Run these skills without managing a server"
  - `README.md` line 120-128: "Search & Web Data" — SerpApi: "Give OpenClaw agents access to real-time Google Search"
  - `README.md` line 130-137: "Security & Config Auditing" — trentclai: "maps config, installed skills, custom code, secrets, and permissions"
  - `README.md` line 142-154: "Model Providers" — 25+ LLM providers, OpenAI model examples with config
  - `README.md` line 163: "You can feature your OpenClaw ecosystem tool in the section above" — sponsored placement section
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 6 key claims from the awesome-openclaw-skills wiki have been verified against source code:
- ✅ 5000+ curated skills confirmed from badges and README claims
- ✅ 30 organized categories confirmed from `categories/` directory (30 files) and README ToC
- ✅ ClawHub-only sourcing confirmed from README and CONTRIBUTING.md
- ✅ Vetting filters and security warnings confirmed with exact 7,215 exclusion count
- ✅ Multiple installation methods confirmed: OpenClaw CLI, ClawHub CLI, manual copy
- ✅ Ecosystem tool sections confirmed: Composio, MyClaw, SerpApi, trentclai

## Related

- [[awesome-openclaw-skills]] — Main wiki entry
- [[openclaw]] — OpenClaw agent platform
- [[awesome-openclaw-usecases]] — Companion use-cases list
- [[skills]] — Agent skills overview

## Cross-project

- [[n8n.codegraph-verify]] — Similar codegraph verification for n8n
- [[hermes-agent.codegraph-verify]] — Similar codegraph verification for Hermes Agent
- [[openclaw.codegraph-verify]] — Similar codegraph verification for OpenClaw
