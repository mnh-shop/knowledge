---
name: redhound-arsenal-codegraph-verify
tags: [redhound, arsenal, security, pentesting, skills, offensive-security, wiki]
description: "Codegraph Verification: redhound-arsenal — validating corrected wiki claims against source README and skill files"
source: sources/redhound-arsenal/
---

# Codegraph Verification: redhound-arsenal

**Date:** 2026-07-30

## Claim 1: 76 skills as folders at the repository root — no `skills/` subdirectory
- **Wiki says:** 76 skill folders at the repo root; there is no `skills/` subdirectory; deployment loops over root folders.
- **Source evidence:**
  - `ls -d */` on the repo root returns exactly 76 directories, each containing `SKILL.md`
  - `README.md` line 30: "| Total Skills | 76 |"
  - `README.md` line 121: "`ls -d */ | wc -l`   # Should output 76"
  - `README.md` line 124: "All 76 skills are immediately available at the root level."
  - No `skills/` directory exists anywhere in the repo
- **Verdict:** ✅ CORRECT (wiki previously deployed via `cp -r skills/* ~/.hermes/skills/` — corrected)
- **Fix needed:** None (already applied)

## Claim 2: 18 category sections in the Tool Index (README stats table says 17)
- **Wiki says:** The Tool Index contains 18 category sections; the README's own stats table says 17 (its own undercount).
- **Source evidence:**
  - `README.md` line 31 (stats table): "| Categories | 17 |"
  - `README.md` sections 132-292 contain exactly 18 `###` category headings in the Tool Index: Information Gathering, Reconnaissance, Web Application, Vulnerability Analysis, Password Attacks, Active Directory, Exploitation, Post-Exploitation, Reverse Engineering, Sniffing & Spoofing, Wireless Attacks, Forensics, Social Engineering, C2 Frameworks, Pivoting & Tunneling, Cloud Security, Evasion, Reporting
- **Verdict:** ✅ CORRECT (wiki previously listed a fabricated 10-row taxonomy including a nonexistent "Scanning & Enumeration" — rebuilt from the README's actual sections)
- **Fix needed:** None (already applied)

## Claim 3: Frontmatter fields are name, description, license, metadata.{author, version, repo, language} — no tools/category/tags
- **Wiki says:** SKILL.md frontmatter carries `name`, `description`, `license`, `metadata.author`, `metadata.version`, `metadata.repo`, `metadata.language`; no `tools`, `category`, or `tags` fields.
- **Source evidence:**
  - `README.md` lines 494-504: "Frontmatter Fields" table listing exactly these 7 fields
  - `nmap/SKILL.md` lines 1-16: frontmatter with `name: nmap`, `description: >`, `license: NPSL / GPLv2`, `metadata: {author: redhoundinfosec, version: '1.0', repo, language: C/Lua}`
  - Verification across all 76 `*/SKILL.md` files: 76/76 have `name:`, `description:`, and `metadata:`; 0 files have `^tools:` or `^category:` frontmatter fields; no frontmatter `tags:` field (only a body-level YAML example inside `chainsaw/SKILL.md`)
- **Verdict:** ✅ CORRECT (wiki previously claimed "(name, description, tools, category, tags)" — corrected)
- **Fix needed:** None (already applied)

## Claim 4: MIT license
- **Wiki says:** Skill content is MIT-licensed; per-tool licenses live in each skill's `license` frontmatter field.
- **Source evidence:**
  - `README.md` line 566: "The skill content in this repository is licensed under the [MIT License](./LICENSE)."
  - `LICENSE` line 1: "MIT License"; line 3: "Copyright (c) 2026 redhoundinfosec"
- **Verdict:** ✅ CORRECT (wiki previously said "Not specified" — corrected)
- **Fix needed:** None (already applied)

## Claim 5: Deployment is a root-folder shell loop, not `cp -r skills/*`
- **Wiki says:** Bulk install uses `for dir in */; do [ -f "$dir/SKILL.md" ] && cp "$dir/SKILL.md" ~/.claude/skills/"${dir%/}.md"; done`.
- **Source evidence:**
  - `README.md` lines 76-78: "for dir in */; do `[ -f "$dir/SKILL.md" ] && cp "$dir/SKILL.md" ~/.claude/skills/"${dir%/}.md"`; done"
  - `README.md` lines 93-95: same loop for Cursor (`~/.cursor/skills/`)
- **Verdict:** ✅ CORRECT (wiki previously used a nonexistent `skills/*` path — corrected)
- **Fix needed:** None (already applied)

## Claim 6: Documented agent targets are Perplexity Computer, Claude Code, Cursor, Codex CLI, manual injection, HTTP serving — no Hermes/OpenCode instructions
- **Wiki says:** Agent-Ready for Perplexity Computer, Claude Code, Cursor, Codex CLI, manual system-prompt injection, and HTTP serving; no Hermes/OpenCode instructions exist in the source.
- **Source evidence:**
  - `README.md` lines 56-63: "### Perplexity Computer" install steps
  - `README.md` lines 65-79: "### Claude Code" (`~/.claude/skills/`)
  - `README.md` lines 81-96: "### Cursor" (`~/.cursor/skills/`)
  - `README.md` lines 98-114: "### Codex CLI and Other Agents" + "### Manual Installation" (system-prompt injection)
  - `README.md` lines 506-519: "### Hosting and Serving Skills" (`python3 -m http.server 8000`, `curl http://localhost:8000/nmap/SKILL.md`)
  - Zero occurrences of "Hermes" or "OpenCode" in README.md
- **Verdict:** ✅ CORRECT (wiki previously claimed "Hermes, Claude Code, OpenCode" — softened to the documented targets)
- **Fix needed:** None (already applied)

## Claim 7: HTTP serving port is 8000, and NetExec is the CrackMapExec successor
- **Wiki says:** HTTP serving uses `python3 -m http.server 8000`; CrackMapExec is not in the repo — its successor NetExec is.
- **Source evidence:**
  - `README.md` line 513: "python3 -m http.server 8000"
  - Tool Index `README.md` line 194 lists `netexec` (NetExec); `ls -d */` confirms `netexec/` and no `crackmapexec/` directory
  - `netexec/SKILL.md` line 4: "the successor to CrackMapExec maintained at" (upstream); line 27: "The user asks about CrackMapExec — NetExec (nxc) is its direct successor"
- **Verdict:** ✅ CORRECT (wiki previously said port 8080 and listed CrackMapExec as a covered tool — corrected)
- **Fix needed:** None (already applied)

## Claim 8: Operator-grade depth, Red Hound provenance, auto-activation, ranking methodology, and stacking
- **Wiki says:** 300-500 lines per skill (seven sections); Red Hound InfoSec with 20+ years Fortune 500 experience; auto-activation via description matching; 4-factor ranking methodology; multi-skill stacking; agentskills.io format.
- **Source evidence:**
  - `README.md` line 33: "| Depth | Operator-grade (300-500 lines per skill) |"; line 363: "Skills are 300-500 lines of content each."
  - `README.md` line 11: "Built by [Red Hound InfoSec](https://redhound.us) — 20+ years of Fortune 500 offensive security experience"
  - `README.md` line 302: "Skills use keyword and semantic matching on the `description` field... the agent automatically loads and applies that skill's knowledge"
  - `README.md` lines 393-400: 4-factor score formula (`real_world_usage × 3.0` + `uniqueness × 2.5` + `normalized_stars × 1.5` + `kali_top10_bonus × 2.0`)
  - `README.md` line 345: "Skills can be **stacked**."; line 492: multi-skill activation guidance
  - `README.md` line 54: "The file follows the [agentskills.io](https://agentskills.io) format"
  - Line counts: nmap 408, metasploit-framework 453, burpsuite 453, ligolo-ng 330
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 8 claims from the corrected redhound-arsenal wiki verified against source:
- ✅ 76 skill folders at repo root, no `skills/` subdir
- ✅ 18 Tool Index category sections (README stats table says 17)
- ✅ Frontmatter: name, description, license, metadata.{author, version, repo, language} — no tools/category/tags
- ✅ MIT license (Copyright (c) 2026 redhoundinfosec)
- ✅ Deployment via root-folder shell loop
- ✅ Documented targets: Perplexity, Claude Code, Cursor, Codex CLI, manual, HTTP — no Hermes/OpenCode
- ✅ HTTP port 8000; NetExec (successor) present, CrackMapExec absent
- ✅ Operator-grade depth, Red Hound provenance, auto-activation, ranking, stacking, agentskills.io

## Related

- [[redhound-arsenal]] -- Main wiki entry

## Cross-project

- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
- [[swe-cli-skills.codegraph-verify]] -- Similar codegraph verification for SWE CLI skills
