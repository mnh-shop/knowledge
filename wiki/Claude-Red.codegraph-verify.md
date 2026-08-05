---
name: Claude-Red-codegraph-verify
tags: [claude-red, security, skills, offensive, red-team, wiki]
description: "Codegraph Verification: Claude-Red — validating wiki claims against indexed source code symbols"
source: sources/Claude-Red/
---

# Codegraph Verification: Claude-Red

**Date:** 2026-07-30

## Claim 1: 58 offensive security skills in 13 categories
- **Wiki says:** Claude-Red contains 58 offensive security skills organized across 13 categories.
- **Source evidence:**
  - `README.md` badge shows `[![Skills](https://img.shields.io/badge/skills-58-red.svg)](#skill-index)`
  - `README.md` badge shows `[![Categories](https://img.shields.io/badge/categories-13-orange.svg)](#categories)`
  - Disk count: `find Skills -name "SKILL.md" | wc -l` = **58 SKILL.md files** — matches the badge
  - Table of Contents lists 13 category sections: Web Application, Auth & Identity, Active Directory, Wireless, Cloud, Mobile, IoT & Embedded, Infrastructure & Red Team, Exploit Development, Fuzzing & Vulnerability Research, Reconnaissance, AI Security, Utility
  - Note (source-side inconsistency): the README category table rows sum to **57** (16+2+1+13+1+1+1+7+6+4+2+1+2) vs. the 58 badge; disk count confirms 58
- **Verdict:** ✅ CORRECT (58 on disk; category-table sum of 57 is a README inconsistency)

## Claim 2: 16 web app skills (OWASP Top 10)
- **Wiki says:** The Web Application category has 16 skills focused on OWASP Top 10 and advanced web bug classes.
- **Source evidence:**
  - `README.md:100` confirms: "| [Web Application](#web-application) | 16 | OWASP Top 10 + business logic + advanced web bug classes |"
  - Disk count: `Skills/web/*/SKILL.md` = 16 files
- **Verdict:** ✅ CORRECT

## Claim 3: 14 wireless skills on disk (README table undercounts at 13)
- **Wiki says:** The Wireless category has 14 skills on disk (incl. `offensive-lorawan-sub-ghz`); the README category table lists 13, omitting it.
- **Source evidence:**
  - Disk count: `Skills/wireless/*/SKILL.md` = **14 files** — includes `offensive-lorawan-sub-ghz` alongside wifi/wpa/ble/zigbee/z-wave skills
  - `README.md:103` category table says "| [Wireless](#wireless) | 13 | ..." — undercounts
  - `README.md:166-179` skill index lists all 14 skills, including `[offensive-lorawan-sub-ghz](Skills/wireless/offensive-lorawan-sub-ghz/SKILL.md)`
- **Verdict:** ⚠️ PARTIALLY ACCURATE (README table says 13; disk has 14 — wiki now reports the disk count with the README discrepancy noted)

## Claim 4: 6 exploit dev skills
- **Wiki says:** The Exploit Development category has 6 skills for binary exploitation and shellcode development.
- **Source evidence:**
  - `README.md` category table shows Exploit Development with 6 skills
  - Disk count: `Skills/exploit-development/*/SKILL.md` = 6 files
- **Verdict:** ✅ CORRECT

## Claim 5: On-demand trigger-based loading
- **Wiki says:** Skills load on demand based on conversational triggers — mentioning "SQLi" loads the offensive-sqli skill. No context cost for unused skills.
- **Source evidence:**
  - `README.md` states: "Skills load on demand based on conversational triggers — you don't pay context for skills you aren't using"
  - `README.md` confirms: "Claude will auto-load matching skills based on conversational triggers (e.g. mentioning SQLi loads `offensive-sqli`)"
  - Each `SKILL.md` carries a frontmatter `triggers:` block (e.g. `Skills/web/offensive-sqli/SKILL.md`)
- **Verdict:** ✅ CORRECT

## Claim 6: Git clone + install.sh deployment (--target / --category / interactive)
- **Wiki says:** Deployed via `git clone` into `~/.claude/skills/` or using `install.sh` with options for target directory, categories, and interactive mode.
- **Source evidence:**
  - `README.md` shows: `git clone https://github.com/SnailSploit/claude-red ~/.claude/skills/claude-red`
  - `install.sh:6-9` documents usage: `./install.sh` (interactive), `./install.sh --target ~/.claude/skills`, `./install.sh --category web`, `./install.sh --target DIR --category web`
  - `install.sh:43-44` parses `--target` and `--category`; `install.sh:62-65` prompts interactively when no target is given
- **Verdict:** ✅ CORRECT

## Claim 7: Dual-format Claude Code usage + converter
- **Wiki says:** Works with the Claude Skills system and Claude Code (`cat SKILL.md | claude --system-file -`).
- **Source evidence:**
  - `README.md` documents Claude Code usage: `cat Skills/web/offensive-sqli/SKILL.md | claude --system-file -`
  - `convert_skills.py:3` — "Claude Skills Converter v4" (Markdown format converter)
  - `claude-skills.json` contains 59 entries including the root-level name (58 skills + root)
- **Verdict:** ✅ CORRECT

## Summary

All 7 key claims from the Claude-Red wiki have been verified against the source:
- ✅ 58 skills / 13 categories: badges + disk count (58 SKILL.md); README table sums to 57 (source-side inconsistency)
- ✅ 16 web app skills: README:100 + disk count
- ⚠️ Wireless: 14 on disk vs README table 13 (undercount, omits offensive-lorawan-sub-ghz; skill index lists all 14)
- ✅ 6 exploit dev skills: category table + disk count
- ✅ On-demand trigger-based loading: README + frontmatter triggers
- ✅ install.sh --target/--category/interactive: install.sh:6-9,43-44,62-65
- ✅ Dual-format Claude Code + convert_skills.py v4 + claude-skills.json (59 entries)

## Related

- [[Claude-Red]] -- Main wiki entry
- [[Claude-OSINT.codegraph-verify]] -- Similar codegraph verification for Claude-OSINT

## Cross-project

- [[Claude-OSINT.codegraph-verify]] -- Similar codegraph verification for Claude-OSINT
- [[SecOpsAgentKit.codegraph-verify]] -- Similar codegraph verification for SecOpsAgentKit
