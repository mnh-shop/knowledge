---
name: ai-marketing-claude-code-skills-codegraph-verify
tags: [ai-marketing-claude-code-skills, codegraph-verify, claude-code, skills, marketing]
description: "Codegraph Verification: ai-marketing-claude-code-skills — validating wiki claims against indexed source"
source: sources/ai-marketing-claude-code-skills/
---

# Codegraph Verification: ai-marketing-claude-code-skills

**Date:** 2026-07-30

## Claim 1: 23 free skills across 5 marketing domains, at the repo root
- **Wiki says:** 23 free skills organized into 5 marketing domains (Strategy & Positioning, Content & Authority, Research & Intelligence, Conversion & Sales, Productivity & Operations); skill directories live at the repository root, not under a `skills/` subdirectory.
- **Source evidence:** Top-level listing shows exactly 23 skill directories: `ai-discoverability-audit/`, `case-study-builder/`, `cold-outreach-sequence/`, `content-idea-generator/`, `daily-briefing-builder/`, `de-ai-ify/`, `go-mode/`, `homepage-audit/`, `last30days/`, `linkedin-authority-builder/`, `linkedin-profile-optimizer/`, `marketing-principles/`, `meeting-prep/`, `newsletter-creation-curation/`, `plan-my-day/`, `positioning-basics/`, `reddit-insights/`, `social-card-gen/`, `testimonial-collector/`, `tweet-draft-reviewer/`, `vault-cleanup-auditor/`, `voice-extractor/`, `youtube-summarizer/`. No `skills/` directory exists; no dot-prefixed category dirs (only `.git`/`.gitignore`). README.md domain section headers at lines 46, 75, 122, 160, 198. README.md:8 badge: "Skills-23%20Free%20%2B%2010%20Pro".
- **Verdict:** ✅ CORRECT
- **Fix needed:** Wiki layout corrected — "skills/.marketing/", "skills/.social/" style paths removed (no such subdirectories exist).

## Claim 2: Pure Markdown + 3 bash scripts — no TypeScript/Python/SQLite backend
- **Wiki says:** The repo is pure Markdown plus 3 bash scripts; no TypeScript, Python, SQLite, or OpenAI/Google API code.
- **Source evidence:** `ls */SKILL.md | wc -l` = 23 and `ls */SKILL-OC.md | wc -l` = 23 (dual-file format). `scripts/` contains exactly `install.sh`, `convert.sh`, `list-skills.sh` — no other code files. Repo-wide grep for `\.ts`, `\.py`, `SQLite`, `OpenAI API`, `Workflow Engine` → 0 files. The single "TypeScript" string appears in `youtube-summarizer/examples/sample-output.md:51` as example output text (a sample of a summarized article) — not part of the stack.
- **Verdict:** ✅ CORRECT
- **Fix needed:** Fabricated tech stack (TypeScript primary, Python backend, SQLite, OpenAI/Google APIs) and the "Workflow Engine / Auth System / Error Recovery retry logic" components removed from wiki.

## Claim 3: quick|standard|deep execution mode system (SKILL_MODE pattern)
- **Wiki says:** Every skill supports three execution depths (quick/standard/deep) documented in SKILL-MODE-PATTERN.md and present in each skill's Mode section.
- **Source evidence:** `SKILL-MODE-PATTERN.md` is 76 lines; mode table at lines 8-20 (`quick` <15 min, `standard` 30-45 min, `deep` 60-90 min); design principles at lines 68-71; line 75: "*Pattern introduced: March 8, 2026*". `homepage-audit/SKILL.md:14-22` Mode section: quick (5-second test + top 3 fixes), standard (full section-by-section audit), deep (+ rewrites + A/B test hypotheses). `CHANGELOG.md:4`: "`quick|standard|deep` execution mode added to all 19 free skills. Inspired by ECC's runtime profile system." (v3.1.0 names 19 skills; repo currently holds 23 directories).
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Multi-platform installation with dual-file SKILL.md/SKILL-OC.md format
- **Wiki says:** `scripts/install.sh` auto-detects Claude Code, OpenClaw, Cursor, and Windsurf; each skill ships SKILL.md (Claude Code) and SKILL-OC.md (OpenClaw).
- **Source evidence:** `scripts/install.sh` exists with flags `--all`, `--platform=claude|openclaw|cursor|windsurf|generic`, `--include-pro`, `--dry-run` (scripts/install.sh:10-15). `scripts/convert.sh` and `scripts/list-skills.sh` present. README.md:245-256 platform table: Claude Code → `~/.claude/skills/` (SKILL.md), OpenClaw → `~/.openclaw/skills/` (SKILL-OC.md), Cursor → `.cursor/rules/`, Windsurf → `.windsurf/rules/`, Generic → `./ai-marketing-skills/`. README.md:257: "**Dual-file system:** Each skill ships two versions — `SKILL.md` (Claude Code, verbose, all phases) and `SKILL-OC.md` (OpenClaw, condensed, ~200 lines, token-efficient)." README.md:229-237 auto-detection sentence.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Structured skill format — frontmatter, gates, INTAKE→ANALYZE→OUTPUT
- **Wiki says:** Each skill follows: YAML frontmatter (name/description), Mode section, Context Loading Gates, phased execution (INTAKE→ANALYZE→OUTPUT), Output Format section; conversion-optimized with scoring, rewrite recommendations, A/B test hypotheses.
- **Source evidence:** `CHANGELOG.md` v3.0.0: "All skills follow INTAKE→ANALYZE→OUTPUT structure. No autonomy triggers."; "Meeting Prep skill — INTAKE→ANALYZE→OUTPUT format. Vault search + prior brief lookup + question generation."; "`daily-briefing-builder` — INTAKE→ANALYZE→OUTPUT format, confirmed good". `homepage-audit/SKILL.md` has Context Loading Gates (lines 26-39), Phases 1-4, scoring and rewrite recommendations. `meeting-prep/SKILL.md` confirms the INTAKE→ANALYZE→OUTPUT format. Every skill includes YAML frontmatter with `name` and `description`.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Premium tier — 7 individual Gumroad products, not 8/10 Pro
- **Wiki says:** The Gumroad table lists 7 individual paid products (bundle $49 aggregating all 7, audit v2 $19, individuals $9-15). The "10 Pro" badge count is not supported by the product table.
- **Source evidence:** README.md:287-301 "Premium Skills (Gumroad)" section table rows: AI Marketing Bundle (all 7) $49, AI Discoverability Audit v2 $19, Founder Intelligence $15, Morning Brief System $14, Competitor Intel Brief $12, Brand Voice Extractor $9, AI Employee Onboarding $9, Brand Positioning Audit $9 — i.e. 7 individual products + bundle row (8 table rows, 7 distinct products). README.md:293 links to https://brianrwagner.gumroad.com. README.md:8 badge says "23 Free + 10 Pro", but no 10-product catalog exists — the badge overstates the Pro tier. `scripts/install.sh` `--include-pro` flag exists (line 243 area).
- **Verdict:** ⚠️ PARTIAL — "23 Free" confirmed; "10 Pro" badge is contradicted by the Gumroad table (7 individual products)
- **Fix needed:** Wiki corrected from "8 paid skills"/"10 Pro" → 7 individual Gumroad products (bundle + 7), with the badge discrepancy noted.

## Claim 7: Version history — v3.1.0 and v3.0.0 changelog entries
- **Wiki says:** CHANGELOG v3.1.0 (March 8, 2026) added modes; v3.0.0 (February 28, 2026) added the 3-layer architecture + Meeting Prep skill.
- **Source evidence:** `CHANGELOG.md:1` "## [3.1.0] — March 8, 2026"; line 4 mode addition. `CHANGELOG.md` v3.0.0 "— February 28, 2026": "3-layer architecture refactor + new Meeting Prep skill"; "Skills audit (Feb 28) found 3 CC free skills missing YAML front matter"; "All skills follow INTAKE→ANALYZE→OUTPUT structure." Matches SKILL-MODE-PATTERN.md:75 date.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All key claims verified against source; the following fabrications were removed from the wiki:
- ❌ TypeScript primary / Python backend / SQLite / OpenAI-Google APIs stack (0 code files; 3 bash scripts only)
- ❌ `skills/.marketing/`, `skills/.social/` layout (skills live at repo root)
- ❌ Workflow Engine / Auth System / Error Recovery retry logic (no such components)
- ❌ "8 paid skills" / "10 Pro" Gumroad claims (7 individual products + bundle)

## Related

- [[ai-marketing-claude-code-skills]] — Main wiki entry
- [[claude-seo]] — Related claude-code marketing skill
- [[claude-ai-music-skills]] — Companion creative skill pack

## Cross-project

- [[n8n-mcp.codegraph-verify]] — Similar codegraph verification for n8n MCP
- [[abvx-agent-skills.codegraph-verify]] — Similar codegraph verification for ABVX Agent Skills
- [[drawio-skill.codegraph-verify]] — Similar codegraph verification for drawio-skill
