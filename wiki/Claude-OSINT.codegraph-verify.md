---
name: Claude-OSINT-codegraph-verify
tags: [claude-osint, osint, skills, security, recon, red-team, wiki]
description: "Codegraph Verification: Claude-OSINT — validating wiki claims against indexed source code symbols"
source: sources/Claude-OSINT/
---

# Codegraph Verification: Claude-OSINT

**Date:** 2026-07-30

## Claim 1: 2 paired skills — osint-methodology (455 lines) + offensive-osint (4,213 lines)
- **Wiki says:** Claude-OSINT contains 2 paired skills: osint-methodology (455 lines) and offensive-osint (4,213 lines), totaling ~4,600 lines of structured tradecraft.
- **Source evidence:**
  - `skills/osint-methodology/SKILL.md` is 455 lines (`wc -l`)
  - `skills/offensive-osint/SKILL.md` is 4,213 lines (`wc -l`)
  - Combined total: 4,668 lines (~4,600)
  - `README.md` explicitly states: "~4,600 lines of structured tradecraft" and documents the two skills
  - Note: an earlier wiki revision cited 4,168 lines for offensive-osint; the on-disk count is 4,213 (verified with `wc -l`)
- **Verdict:** ✅ CORRECT (line count corrected from 4,168 → 4,213)

## Claim 2: 48 secret-regex patterns + 80+ Google Dorks
- **Wiki says:** The offensive-osint skill contains 48 secret-regex patterns and 80+ Google Dorks for external recon.
- **Source evidence:**
  - `skills/offensive-osint/SKILL.md:1685` — "## 17. Secret-Pattern Catalog — 48 patterns (29 base + 19 modern)"
  - `README.md` states "80+ dork corpus across 9 categories" (tagline/arsenal section)
- **Verdict:** ✅ CORRECT

## Claim 3: 9 read-only credential validators
- **Wiki says:** The arsenal includes 9 read-only credential validators, ensuring no modification to target systems during recon.
- **Source evidence:**
  - `README.md:117` — "9 read-only credential validators (Postman / AWS / GitHub / Slack / Anthropic / OpenAI / npm / Atlassian / DataDog)"
  - `skills/offensive-osint/SKILL.md` description block enumerates the same 9 validators
- **Verdict:** ✅ CORRECT

## Claim 4: 27 attack-path templates + 90+ capabilities across 12 domains
- **Wiki says:** The skill provides 27 attack-path templates and 90+ capabilities across 12 domains.
- **Source evidence:**
  - `README.md:176` — "Attack-path hint patterns (27 templates)"
  - `README.md:57` — "90+ capabilities across 12 domains"
  - `README.md` shows capability tables organized across 12 domain sections (Reconnaissance, Identity & SSO, Web Application Attack Surface, Cloud & Container, etc.)
- **Verdict:** ✅ CORRECT

## Claim 5: 5-stage pipeline with 1h/4h/1d/1w budgets + 4 end-to-end walkthroughs
- **Wiki says:** The methodology skill defines a 5-stage external recon pipeline with time-budget profiles for 1h, 4h, 1d, and 1w engagements, plus 4 end-to-end walkthroughs.
- **Source evidence:**
  - `README.md:63` — "5-stage external recon pipeline + time-budget profiles (1h / 4h / 1d / 1w)"
  - `examples/` contains 4 walkthroughs: `01-quick-recon.md`, `02-bug-bounty-workflow.md`, `03-identity-fabric-mapping.md`, `04-secret-hunting.md`
- **Verdict:** ✅ CORRECT

## Claim 6: Trigger counts — 127 in offensive-osint, 52 in methodology
- **Wiki says:** Skill trigger-activation with 127 triggers in offensive-osint and 52 in methodology.
- **Source evidence:**
  - `skills/offensive-osint/SKILL.md` frontmatter `triggers:` block contains 127 entries (counted via `awk`)
  - `skills/osint-methodology/SKILL.md` frontmatter `triggers:` block contains 52 entries (counted via `awk`)
  - Both skills auto-load via conversational triggers; `README.md:296` confirms "both skills auto-load and trigger on relevant phrases"
- **Verdict:** ✅ CORRECT (counts verified against SKILL.md frontmatter, not README prose)

## Claim 7: 32-prompt self-eval 31/32 PASS (96.9%) — with self-grading caveat
- **Wiki says:** 32-prompt self-evaluation suite grades 31/32 PASS (96.9%), with the caveat that 96.9% is Claude grading itself on tests Claude designed, not an objective measure.
- **Source evidence:**
  - `tests/smoke-test-prompts.md:19` — "Current self-grade: 31 PASS / 1 PARTIAL / 0 FAIL on original 32 prompts (96.9%)" (Tier 1 has 12 prompts; 12+10+10 structure across tiers)
  - `README.md:328` — "32-prompt self-evaluation suite (current grade: 31/32 PASS)"
  - `docs/coverage.md:72` — "The smoke-test number (96.9% PASS) is **Claude grading itself on tests Claude designed**. It's a useful signal for tracking gaps but not an objective measure of real-world coverage."
- **Verdict:** ✅ CORRECT (self-eval caveat added to wiki next to the 96.9% claim)

## Claim 8: Drop-in SKILL.md files with MIT license
- **Wiki says:** Each skill is a drop-in SKILL.md file — clone into `~/.claude/skills/` and Claude auto-triggers on relevant phrases. MIT licensed, origin elementalsouls/Claude-OSINT.
- **Source evidence:**
  - `README.md` states "Each skill is a structured `SKILL.md` file" and "Drop both into your Claude environment and it behaves like a senior recon analyst"
  - `README.md` confirms: "Each skill directory is self-contained. Drop into `~/.claude/skills/` and Claude auto-triggers on relevant phrases"
  - Both `skills/osint-methodology/SKILL.md` and `skills/offensive-osint/SKILL.md` exist as self-contained skill files
  - License: MIT (README badge / license file)
- **Verdict:** ✅ CORRECT

## Summary

All 8 key claims from the Claude-OSINT wiki have been verified against the source:
- ✅ 2 paired skills (~4,600 lines): 455 + 4,213 = 4,668 lines (line count corrected to 4,213)
- ✅ 48 secret-regex patterns (SKILL.md:1685) + 80+ dorks (README:121)
- ✅ 9 read-only credential validators (README:117)
- ✅ 27 attack-path templates + 90+ capabilities across 12 domains (README:57,176)
- ✅ 5-stage pipeline 1h/4h/1d/1w budgets + 4 examples (README:63)
- ✅ 127 offensive-osint + 52 methodology triggers (SKILL.md frontmatter)
- ✅ 32-prompt self-eval 31/32 PASS (96.9%) + self-grading caveat (smoke-test:19, README:328, coverage.md:72)
- ✅ Drop-in SKILL.md files, MIT, elementalsouls origin

## Related

- [[Claude-OSINT]] -- Main wiki entry
- [[Claude-Red.codegraph-verify]] -- Similar codegraph verification for Claude-Red

## Cross-project

- [[Claude-Red.codegraph-verify]] -- Similar codegraph verification for Claude-Red
- [[SecOpsAgentKit.codegraph-verify]] -- Similar codegraph verification for SecOpsAgentKit
