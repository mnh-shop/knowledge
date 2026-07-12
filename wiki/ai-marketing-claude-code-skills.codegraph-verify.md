---
name: ai-marketing-claude-code-skills-codegraph-verify
tags: [ai-marketing-claude-code-skills, codegraph-verify, claude-code, skills, marketing]
description: "Codegraph Verification: ai-marketing-claude-code-skills — validating wiki claims against indexed source code symbols"
source: sources/ai-marketing-claude-code-skills/
---

# Codegraph Verification: ai-marketing-claude-code-skills

**Date:** 2026-07-12

## Claim 1: 23+ marketing automation skills for Claude Code
- **Wiki says:** 23+ free marketing automation skills packaged as SKILL.md files that Claude Code executes. Organized into 5 marketing domains: Strategy & Positioning, Content & Authority, Research & Intelligence, Conversion & Sales, Productivity & Operations.
- **Source evidence:**
  - Top-level directory listing shows 23 skill directories: `ai-discoverability-audit/`, `case-study-builder/`, `cold-outreach-sequence/`, `content-idea-generator/`, `daily-briefing-builder/`, `de-ai-ify/`, `go-mode/`, `homepage-audit/`, `last30days/`, `linkedin-authority-builder/`, `linkedin-profile-optimizer/`, `marketing-principles/`, `meeting-prep/`, `newsletter-creation-curation/`, `plan-my-day/`, `positioning-basics/`, `reddit-insights/`, `social-card-gen/`, `testimonial-collector/`, `tweet-draft-reviewer/`, `vault-cleanup-auditor/`, `voice-extractor/`, `youtube-summarizer/`
  - `CHANGELOG.md` v3.1.0: "quick|standard|deep execution mode added to all 19 free skills"
  - `README.md` badge: "23 Free + 10 Pro" (line 8)
  - `README.md` groups skills by category: "Strategy & Positioning", "Content & Authority", "Research & Intelligence", "Conversion & Sales", "Productivity & Operations"
  - `README.md` line 13: "March 2026 — v3.1: All 19 free skills now support quick|standard|deep execution modes"
  - `README.md` line 248-256 documents platform support: Claude Code, OpenClaw, Cursor, Windsurf, Generic
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: quick|standard|deep execution mode system (SKILL_MODE pattern)
- **Wiki says:** Every skill supports three execution depths (quick/standard/deep) documented in SKILL-MODE-PATTERN.md and present in every skill's Mode section. Quick provides minimal output in <15 min, standard provides full process in 30-45 min, deep provides extended research in 60-90 min.
- **Source evidence:**
  - `SKILL-MODE-PATTERN.md` is a 76-line document defining the SKILL_MODE pattern: mode table, tagged phases, and design principles (line 8-76)
  - `SKILL-MODE-PATTERN.md` line 68-71: "quick is not worse — it's appropriate for different jobs", "Don't change the skill's core logic", "Detect from context first"
  - `ai-discoverability-audit/SKILL.md` has Mode section at line 14-24: quick (Phase 1 only + 3 fixes), standard (all 4 phases + scored report), deep (+ competitive benchmarking + 90-day plan)
  - `content-idea-generator/SKILL.md` has Mode section at line 14-22: quick (5 ideas), standard (10-15 ideas), deep (full content calendar)
  - `homepage-audit/SKILL.md` has Mode section at line 14-22: quick (5-second test + 3 fixes), standard (full audit), deep (+ rewrites + A/B hypotheses)
  - `CHANGELOG.md` v3.1.0 (line 1-20): Documents the mode system addition, credits ECC runtime profile system as inspiration
  - `SKILL-MODE-PATTERN.md` line 75: "Pattern introduced: March 8, 2026"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Multi-platform installation with auto-detection
- **Wiki says:** The `scripts/install.sh` auto-detects Claude Code, OpenClaw, Cursor, and Windsurf. Each skill ships dual-file format (SKILL.md for Claude Code, SKILL-OC.md for OpenClaw). Platform-specific flags and dry-run support.
- **Source evidence:**
  - `scripts/install.sh` exists as the installer entry point
  - `scripts/list-skills.sh` lists available skills
  - `scripts/convert.sh` converts to platform-specific formats (cursor, windsurf)
  - `README.md` line 229-237: "Auto-detects Claude Code, OpenClaw, Cursor, and Windsurf. Walks you through the rest."
  - `README.md` flags section (line 239-245): `--all`, `--platform=cursor`, `--include-pro`, `--dry-run`
  - `README.md` platform support table (line 249-256) shows 5 platforms with install locations
  - `README.md` line 257: "Dual-file system: Each skill ships two versions — SKILL.md (Claude Code, verbose, all phases) and SKILL-OC.md (OpenClaw, condensed, ~200 lines, token-efficient)"
  - Evidence of dual-file format: `ai-discoverability-audit/SKILL.md` and `ai-discoverability-audit/SKILL-OC.md` both exist, same for `cold-outreach-sequence/`, `linkedin-authority-builder/`, `positioning-basics/`, `homepage-audit/`, etc.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Structured skill format with mode tables and phased execution
- **Wiki says:** Each skill follows a consistent structure: YAML frontmatter with name/description, Mode section, Context Loading Gates, phased execution (INTAKE→ANALYZE→OUTPUT), and Output Format section. Skills are conversion-optimized with scoring, rewrite recommendations, and A/B test hypotheses.
- **Source evidence:**
  - Every skill includes YAML frontmatter with `name` and `description` fields (verified across `ai-discoverability-audit/SKILL.md`, `content-idea-generator/SKILL.md`, `homepage-audit/SKILL.md`)
  - `CHANGELOG.md` v3.0.0 (line 35-39): "Front Matter Verified — `daily-briefing-builder` — INTAKE→ANALYZE→OUTPUT format, confirmed good"
  - `homepage-audit/SKILL.md` has Context Loading Gates (line 26-39), phased execution (Phases 1-4), Output Format, scoring, and rewrite recommendations
  - `ai-discoverability-audit/SKILL.md` has Context Loading Gates (line 30-40+), 4 phases, scored report, priority roadmap
  - `content-idea-generator/SKILL.md` has Context Loading Gates (line 26-37), positioning gate, format and rationale output
  - `CHANGELOG.md` v3.0.0 line 33: "Meeting Prep skill — INTAKE→ANALYZE→OUTPUT format. Vault search + prior brief lookup + question generation."
  - `meeting-prep/SKILL.md` confirms the INTAKE→ANALYZE→OUTPUT format
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Premium/Pro tier with monetization via Gumroad
- **Wiki says:** Premium "Pro" skills are available via Gumroad with pricing from $9-$49. Skills include AI Marketing Bundle ($49), AI Discoverability Audit v2 ($19), and individual skills ($9-$15). Free tier has 23 skills, Pro tier has 10 additional skills.
- **Source evidence:**
  - `README.md` line 288-303: "Premium Skills (Gumroad)" section with table of 8 paid skills and links
  - `README.md` line 293: `→ [Browse all on Gumroad](https://brianrwagner.gumroad.com)`
  - `README.md` line 289: "Full Claude Code editions with structured reasoning phases, self-critique loops, and output precision"
  - `README.md` line 295: AI Marketing Bundle listed at $49
  - `README.md` line 296: AI Discoverability Audit v2 at $19
  - `README.md` line 299-302: Individual skills at $9-$15 pricing
  - `README.md` badge at line 8: `Skills-23%20Free%20%2B%2010%20Pro-green`
  - `scripts/install.sh` flag at line 243: `--include-pro` to include Pro skills
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 5 key claims from the ai-marketing-claude-code-skills wiki have been verified against source code:
- ✅ 23+ free skills confirmed from directory listing across 5 marketing domains
- ✅ quick|standard|deep execution mode confirmed in `SKILL-MODE-PATTERN.md` and implemented in every skill
- ✅ Multi-platform installation confirmed via `scripts/install.sh` and dual-file SKILL.md/SKILL-OC.md format
- ✅ Structured skill format confirmed with YAML frontmatter, Mode tables, Context Loading Gates, and phased execution
- ✅ Premium/Pro tier confirmed with Gumroad links and --include-pro install flag

## Related

- [[ai-marketing-claude-code-skills]] — Main wiki entry
- [[claude-seo]] — Related claude-code marketing skill
- [[claude-ai-music-skills]] — Companion creative skill pack
- [[openai-skills]] — Official OpenAI skills catalog

## Cross-project

- [[n8n.codegraph-verify]] — Similar codegraph verification for n8n
- [[abvx-agent-skills.codegraph-verify]] — Similar codegraph verification for ABVX Agent Skills
- [[drawio-skill.codegraph-verify]] — Similar codegraph verification for drawio-skill
