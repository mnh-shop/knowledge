---
name: Claude-Red
tags: [claude, security, red-team, offensive-security, skills, pentesting, exploit, webapp, ad, cloud, mit]
description: "58 offensive security skills for the Claude Skills system — web app hacking, wireless, exploit dev, cloud, Active Directory, and more"
source: sources/Claude-Red/
verification_date: 2026-07-30
verified_by: codegraph-verify
---

# Claude-Red

**Source:** `sources/Claude-Red/`

Claude-Red is a curated library of 58 offensive security skills for the Claude Skills system. Each skill is a structured `SKILL.md` file that primes Claude with expert-level methodology for a specific attack surface — from SQLi to shellcode, EDR evasion to ADCS abuse. Skills load on demand based on conversational triggers, so you don't pay context for skills you aren't using.

| Field | Value |
|---|---|
| **Origin** | [SnailSploit/Claude-Red](https://github.com/SnailSploit/Claude-Red) |
| **License** | MIT |
| **Format** | Markdown SKILL.md files |
| **Skills** | 58 |
| **Categories** | 13 |
| **Install** | Clone to `~/.claude/skills/` or `git sparse-checkout` |
| **Source** | `sources/Claude-Red/` |
| **Codegraph** | `graphs/Claude-Red/` |

## What is it?

Claude-Red provides structured, expert-level offensive security knowledge in a format Claude can load on demand. Drop a skill into your Claude environment and it behaves like a specialist red team operator — it knows the techniques, the tooling, the edge cases, and the escalation paths for its domain. Skills span 13 categories including web application, Active Directory, wireless, cloud, mobile, exploit development, AI security, and IoT/embedded.

## Key Features

- **58 Skills Across 13 Categories** — Web app (SQLi, XSS, SSRF), Active Directory (ADCS, Kerberos), Cloud (AWS, Azure, GCP), Wireless, Mobile, IoT, Exploit Dev, Fuzzing, Recon, AI Security, and more
  - **Wireless: 14 skills on disk** — `Skills/wireless/` contains 14 `SKILL.md` files (incl. `offensive-lorawan-sub-ghz`); the README category table (`README.md:103`) undercounts at 13 by omitting it, though the README skill index (lines 166-179) lists all 14
  - Note: the README category table sums to 57 across its 13 rows (16+2+1+13+1+1+1+7+6+4+2+1+2) vs. the 58 badge — a source-side inconsistency; disk count is 58 `SKILL.md` files
- **Trigger-Activated Loading** — Skills auto-load based on conversational triggers, minimizing context waste
- **Structured Methodology** — Each skill includes tooling, edge cases, escalation paths, and operator-level tradecraft
- **Bash-Based Installation** — Simple `git clone` or sparse-checkout per category
- **Dual-Format Support** — Works with Claude Skills system and Claude Code (`cat SKILL.md | claude --system-file -`)

## Tech Stack

| Component | Technology |
|---|---|
| **Skill Format** | Markdown SKILL.md (Claude Skills System) |
| **Installation** | Bash, git clone/sparse-checkout |
| **Categories** | 13 attack domains |
| **Scripts** | Bash (optional, tool wrappers) |

## Deployment

### Claude Skills System (recommended)

```bash
git clone https://github.com/SnailSploit/Claude-Red ~/.claude/skills/claude-red
# Or install only one category:
git clone --filter=blob:none --sparse https://github.com/SnailSploit/Claude-Red
cd claude-red && git sparse-checkout set Skills/web Skills/active-directory
```

### Claude Code

```bash
# Load a single skill
cat Skills/web/offensive-sqli/SKILL.md | claude --system-file -
# Load a whole category
cat Skills/active-directory/**/SKILL.md | claude --system-file -
```

## Related

- [[Claude-OSINT]] — Paired Claude skills for OSINT methodology and offensive OSINT arsenal
- [[SecOpsAgentKit]] — Security operations skills for AI coding agents
- [[ctf-skills]] — Agent Skills for CTF challenges across 11 categories
- [[Hexstrike-redteam-full]] — AI-powered MCP cybersecurity automation platform
