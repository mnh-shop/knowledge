---
name: ai-marketing-claude-code-skills
tags: [ai-marketing-claude-code-skills, agent, skill, marketing, ai-llm, automation, cli, bash]
description: "AI marketing agent skills for Claude Code: 23 free skills across 5 marketing domains with quick/standard/deep execution modes"
source: sources/ai-marketing-claude-code-skills/
verification_date: 2026-07-12
verified_by: codegraph-verify
updated: 2026-07-30
---

# AI Marketing Claude Code Skills

**AI Marketing Claude Code Skills** is a suite of 23 free marketing skills for Claude Code that turns the agent into an executable marketing playbook. Skills live at the **repository root** (one directory per skill), each shipping dual files — `SKILL.md` (Claude Code, verbose) and `SKILL-OC.md` (OpenClaw, condensed). All skills follow the **SKILL_MODE pattern** (quick|standard|deep) and a structured INTAKE→ANALYZE→OUTPUT format. The repo is pure **Markdown + 3 bash scripts** — no application code, no database.

## What it is

The README's framing is "Marketing frameworks that Claude Code actually executes. Not guides. Not courses. *Skills* — packaged expertise your AI coding agent loads and follows." Skills cover 5 marketing domains and range from positioning and cold outreach to LinkedIn authority building, homepage auditing, and daily operations.

## Architecture

### Core Components

| Component | Purpose | Key Features |
|-----------|---------|-------------|
| **23 Free Skills** | Specialized marketing instructions | One directory per skill at repo root, each with SKILL.md + SKILL-OC.md |
| **SKILL_MODE Pattern** | Three-tier execution (quick/standard/deep) | Documented in SKILL-MODE-PATTERN.md (76 lines); mode table in every skill |
| **Structured Skill Format** | Consistent execution | YAML frontmatter, Mode section, Context Loading Gates, INTAKE→ANALYZE→OUTPUT phases, Output Format |
| **Multi-Platform Install** | Cross-harness distribution | `scripts/install.sh` auto-detects Claude Code, OpenClaw, Cursor, Windsurf; 5-platform table in README |
| **Premium Tier** | Paid skills via Gumroad | 7 individual products + bundle, $9-49 |

There is **no TypeScript, no Python backend, no SQLite, and no OpenAI/Google API integration code** — the skills are instructions that run inside the agent harness, backed only by the three shell scripts in `scripts/` (`install.sh`, `convert.sh`, `list-skills.sh`).

### Skill Layout — at the repo root

There is no `skills/` subdirectory and no dot-prefixed category directories. Skills are top-level directories:

```
ai-marketing-claude-code-skills/
  README.md
  CHANGELOG.md
  SKILL-MODE-PATTERN.md
  scripts/                       # 3 bash scripts: install.sh, convert.sh, list-skills.sh
  ai-discoverability-audit/      # 23 skill directories, each with:
    SKILL.md                     #   SKILL.md (Claude Code edition)
    SKILL-OC.md                  #   SKILL-OC.md (OpenClaw edition)
  case-study-builder/
  ... (21 more skills)
```

Install via `cp -r ai-marketing-claude-code-skills/* ~/.claude/skills/` — the copy brings in every skill directory directly.

### The 23 Free Skills (5 domains)

README.md groups 19 skills by domain (section headers at lines 46, 75, 122, 160, 198); the remaining 4 directories exist but are not in the grouped listing (they're CHANGELOG-verified instead):

| Domain | Skills (per README grouping) |
|--------|------------------------------|
| **Strategy & Positioning** | positioning-basics, ai-discoverability-audit, marketing-principles |
| **Content & Authority** | linkedin-authority-builder, content-idea-generator, voice-extractor, de-ai-ify, social-card-gen |
| **Research & Intelligence** | last30days, reddit-insights, youtube-summarizer, linkedin-profile-optimizer |
| **Conversion & Sales** | homepage-audit, cold-outreach-sequence, case-study-builder, testimonial-collector |
| **Productivity & Operations** | plan-my-day, newsletter-creation-curation, go-mode |
| *(not in grouped listing)* | daily-briefing-builder, meeting-prep, tweet-draft-reviewer, vault-cleanup-auditor (all 4 confirmed via CHANGELOG v3.0.0 "Front Matter Verified") |

## The SKILL_MODE Pattern

Every skill supports three execution depths (SKILL-MODE-PATTERN.md:8-20):

| Mode | Output depth | Time expectation |
|------|-------------|-----------------|
| `quick` | Minimum viable output — single pass, no deep research, no scoring | < 15 min |
| `standard` | Full process — all phases, scoring where relevant, priority output | 30–45 min |
| `deep` | Extended research + iteration + frameworks for ongoing use | 60–90 min |

Each skill carries a Mode table immediately after the intro, before Phase 1 (e.g. homepage-audit/SKILL.md:14-22: `quick` = 5-second test + top 3 fixes, `standard` = full section-by-section audit, `deep` = full audit + rewrites + A/B test hypotheses). Design principles (SKILL-MODE-PATTERN.md:68-71): quick is not worse, don't change core logic, detect from context first, deep should earn its time. **Pattern introduced: March 8, 2026** (SKILL-MODE-PATTERN.md:75), inspired by everything-claude-code (ECC) runtime profile system.

## Structured Skill Format

- **YAML frontmatter** with `name`/`description` on every skill (so the trigger system sees them)
- **Context Loading Gates** — mandatory inputs loaded before execution
- **Phased execution** — INTAKE→ANALYZE→OUTPUT (CHANGELOG v3.0.0; meeting-prep/SKILL.md)
- **Output Format section** describing what each mode delivers
- Conversion-optimized output: scoring, rewrite recommendations, A/B test hypotheses (homepage-audit)

## Installation

- `git clone https://github.com/BrianRWagner/ai-marketing-claude-code-skills.git`
- `./scripts/install.sh` — auto-detects Claude Code, OpenClaw, Cursor, and Windsurf (README.md:229-237); flags `--all`, `--platform=claude|openclaw|cursor|windsurf|generic`, `--include-pro`, `--dry-run` (scripts/install.sh:10-15)
- `./scripts/convert.sh` — converts SKILL.md → `.mdc` (Cursor) / `.md` (Windsurf) rule format
- `./scripts/list-skills.sh` — lists available skills
- Manual: `mkdir -p ~/.claude/skills && cp -r ai-marketing-claude-code-skills/* ~/.claude/skills/`

### Platform Support (README.md:245-256)

| Platform | Install Location | File Used |
|----------|-----------------|-----------|
| Claude Code | `~/.claude/skills/` | `SKILL.md` |
| OpenClaw | `~/.openclaw/skills/` | `SKILL-OC.md` |
| Cursor | `.cursor/rules/` | `SKILL.md` → `.mdc` |
| Windsurf | `.windsurf/rules/` | `SKILL.md` → `.md` |
| Generic | `./ai-marketing-skills/` | `SKILL.md` |

Dual-file system: each skill ships `SKILL.md` (Claude Code, verbose, all phases) and `SKILL-OC.md` (OpenClaw, condensed, ~200 lines, token-efficient) — 23 + 23 files (README.md:257).

## Premium Skills (Gumroad)

The README badge claims "23 Free + 10 Pro" (README.md:8), but the actual Gumroad catalog (README.md:287-301) lists **7 individual paid products** plus the bundle:

| Skill | Price |
|-------|-------|
| AI Marketing Bundle (all 7) | $49 |
| AI Discoverability Audit v2 | $19 |
| Founder Intelligence | $15 |
| Morning Brief System | $14 |
| Competitor Intel Brief | $12 |
| Brand Voice Extractor | $9 |
| AI Employee Onboarding | $9 |
| Brand Positioning Audit | $9 |

→ [Browse all on Gumroad](https://brianrwagner.gumroad.com). Pro editions are "full Claude Code editions with structured reasoning phases, self-critique loops, and output precision." The "10 Pro" badge count is not supported by the product table — 7 individual products are listed.

## Version History (CHANGELOG.md)

- **v3.1.0 — March 8, 2026** — `quick|standard|deep` execution mode added to all free skills; `SKILL-MODE-PATTERN.md` shipped; mode table in every skill; no breaking changes (standard = v3.0.0 behavior)
- **v3.0.0 — February 28, 2026** — 3-layer architecture refactor; new Meeting Prep skill (INTAKE→ANALYZE→OUTPUT, vault search + prior brief lookup); front matter verified across skills; "All skills follow INTAKE→ANALYZE→OUTPUT structure. No autonomy triggers."

---

*This wiki entry is generated from the source repository and follows the AI Marketing Claude Code Skills repository's documentation standards.*

---

**Last Updated:** 2026-07-30
**Verification:** Source code verified against `sources/ai-marketing-claude-code-skills/`
