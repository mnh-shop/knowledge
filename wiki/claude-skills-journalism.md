---
name: claude-skills-journalism
tags: [journalism, skills, claude, research, academia, media, ap-style, fact-checking, osint, video, pdf, nodejs, mit]
description: "61 agent skills across 12 plugins for journalists, researchers, and academics — core journalism, research toolkit, video analysis, PDF design, dev and security toolkits"
source: sources/claude-skills-journalism/
verification_date: 2026-07-30
verified_by: codegraph-verify
---

# claude-skills-journalism

**Source:** `sources/claude-skills-journalism/`

A comprehensive collection of 61 Agent Skills for journalists, researchers, academics, media professionals, and communications practitioners. Skills are organized into 12 Claude Code Marketplace plugins covering core journalism (14 skills), a research toolkit (6 skills), a dev toolkit (11 skills), video analysis, PDF design, security, and more. The same repository serves both Claude Code and Codex via the Agent Skills specification, and publishes a docs site at skills.amditis.tech with an interactive skill browser.

| Field | Value |
|---|---|
| **Origin** | [jamditis/claude-skills-journalism](https://github.com/jamditis/claude-skills-journalism) |
| **License** | MIT |
| **Format** | Markdown SKILL.md files + Node.js scripts |
| **Plugins** | 12 (autocontext, dev-toolkit, journalism-core, okf-wiki, pdf-design, pdf-playground, project-templates-toolkit, research-toolkit, security-toolkit, superjawn, video-toolkit, visual-explainer) |
| **Skills** | 61 (60 SKILL.md packages + pdf-playground's `playground.md` entry skill) |
| **Hooks** | 17 automated workflow checks |
| **Install** | `/plugin marketplace add jamditis/claude-skills-journalism` |
| **Docs Site** | skills.amditis.tech (interactive skill browser) |
| **Source** | `sources/claude-skills-journalism/` |
| **Codegraph** | `graphs/claude-skills-journalism/` |

## What is it?

This repository provides modular instruction sets (skills) that extend Claude's capabilities for journalism, research, and academic workflows. Skills are distributed as 12 Marketplace plugins with automated hooks for AP Style enforcement, source verification, fact-checking, accessibility, and pre-publication checks. It also includes a PDF design system, a video analysis toolkit, research augmentation tools, a security toolkit, and an OKF knowledge-base scaffolder — all following the Agent Skills specification. Skill freshness is enforced by a git-history-based "updated stamp" system that ages visibly on the docs site.

## Key Features

- **14 Core Journalism Skills** (journalism-core) — AP-Style writing, AI-slop detox, source verification (SIFT, deepfakes/C2PA), FOIA + NJ OPRA requests, fact-checking, interview prep + transcription, story pitches, editorial workflow, crisis communications, newsletter publishing (Gmail/Yahoo/Outlook bulk-sender compliance), photo metadata, data journalism, social media intelligence
- **Research Toolkit** (6 skills) — Academic writing, paywall access (Unpaywall/CORE/Semantic Scholar), web archiving (Wayback/Archive.today), page-change monitoring, AI-enriched digital archives, and a curated free-API catalog with sunset currency notes (IEX Cloud, CrowdTangle, ProPublica Congress, X, Reddit)
- **Video Analysis Toolkit** (4 skills) — Download from Twitter/X, TikTok, YouTube, Instagram, Facebook via yt-dlp (browser-automation fallback); transcription with provenance sidecars (CPU whisper.cpp path as transcript of record); frame extraction + vision analysis; interactive dashboard aggregation
- **Dev Toolkit** (11 skills) — Accessibility (WCAG 2.2), Electron, mobile debugging, one-way-door irreversible-decision discipline, Python data pipelines, test-first bug fixing, vibe-coding workflow, ethical web scraping, no-build frontend, web-UI best practices, CLAUDE.md maintenance
- **Security Toolkit** (4 skills + `/security-toolkit:hotpatch`) — OWASP Top 10 pre-deployment audit, secure auth patterns (passkeys, OAuth, JWT), API hardening, npm/bun supply-chain hardening with install-time cooldown and sandboxed pre-install scan (Mini Shai-Hulud-class worm defense)
- **PDF Playground** — Interactive branded proposals, reports, one-pagers, newsletters, slides, and event materials with live design-editing control panel and guided proposal wizard (7 slash commands)
- **PDF Design** — Branded report/proposal design system with brand variables, budget tables, and reusable content blocks
- **OKF Wiki** — Scaffold an Open Knowledge Format (OKF) knowledge base: one-concept-per-file markdown with YAML frontmatter, validator, session-start orientation hooks, and optional GitHub-wiki bootstrap
- **Project Templates Toolkit** (3 skills) — CLAUDE.md project-memory writer, LESSONS.md retrospective writer, and a template-selector decision tree across 6 project types
- **Superjawn** (14 skills) — Research-augmented fork of obra/superpowers: brainstorming, systematic-debugging, writing-plans, TDD, code review, subagent-driven development, git worktrees, and more; v1.0.0 ships standalone with no soft dependency on upstream
- **Visual Explainer** — HTML diagrams, data tables, architecture views, slide decks, and KPI dashboards adapted for journalism/newsroom design
- **Autocontext Plugin** — Cross-session knowledge persistence with skill evolution; `/autocontext:evolve` folds accumulated lessons back into skill files
- **17 Automated Hooks** — Non-blocking warnings plus three intentional blockers (one-way-door-check, enforce-test-first, no-ai-attribution) covering writing quality, verification, editorial workflow, preservation, and development
- **Untrusted Content Contract** — Shared `specs/untrusted-content-contract.md` + `<!-- untrusted-content-contract:v1 -->` sections in fact-check and related skills: retrieved web material is treated as untrusted data, never as instructions (prompt-injection defense)
- **Updated-Stamp System** — Last-updated dates derived from git history (`scripts/updated-stamp.mjs`, `git log -1 --format=%cI`), re-run by CI, with 7 honesty rules covered by tests

## Tech Stack

| Component | Technology |
|---|---|
| **Skill Format** | Markdown SKILL.md with YAML frontmatter (Agent Skills spec) |
| **Scripts** | Node.js (ESM), Python, Bash |
| **Plugins** | Claude Code plugin marketplace (`.claude-plugin/marketplace.json`) |
| **PDF Generation** | HTML/CSS → PDF (custom design system) |
| **Video Processing** | yt-dlp, FFmpeg, whisper.cpp / WhisperX |
| **Hooks** | PreToolUse / PostToolUse / UserPromptSubmit / SessionStart / Stop |
| **Docs Site** | skills.amditis.tech (static site with skill browser, tape-styled age stamps) |
| **Tests** | Node test suites in `scripts/` (`.test.mjs`), pytest for okf-wiki |

## Deployment

### Marketplace Install (recommended)

```
/plugin marketplace add jamditis/claude-skills-journalism
/plugin install journalism-core@claude-skills-journalism
```

### Codex Install

```bash
npx skills@latest add https://github.com/jamditis/claude-skills-journalism/tree/master/journalism-core \
  --skill '*' --agent codex --copy -g -y
```

### Single Skill Install

```bash
git clone https://github.com/jamditis/claude-skills-journalism.git
cp -r journalism-core/skills/source-verification ~/.claude/skills/
# Or symlink for auto-updates:
ln -sfn "$PWD/research-toolkit/skills/free-apis-catalog" ~/.claude/skills/free-apis-catalog
```

### Docs & Guides

- **Skill browser:** https://skills.amditis.tech — interactive browser, per-skill cards with age-yellowing tape stamps
- **Persistent sessions:** `persistent-sessions/tmux.conf` + guide at skills.amditis.tech/persistent-sessions/ — keep Claude Code sessions alive through disconnects
- **Guides:** autonomy (autonomous vs hands-on dev work), multi-agent workflows (fan-out / pipeline / adversarial-verify patterns)

## Repository Layout

- `hooks/` — 17 workflow hooks (3 intentionally blocking)
- `specs/untrusted-content-contract.md` — shared prompt-injection defense contract
- `scripts/` — updated-stamp.mjs, agent-skills validation, install/security/contract canary test suites (`.test.mjs` files), accessibility verification
- `persistent-sessions/` — tmux-based session persistence config
- `docs/` — skills.amditis.tech static site
- `plans/` — codex-compatibility-matrix and design docs
- `okf-wiki/spec/SPEC.md`, `okf-wiki/tests/` — OKF spec and validator pytest suite

## Related

- [[SecOpsAgentKit]] — Security operations skills for AI coding agents
- [[Claude-OSINT]] — OSINT methodology and arsenal skills
- [[Claude-Red]] — Offensive security skills for Claude
- [[ctf-skills]] — Agent Skills for CTF challenges
