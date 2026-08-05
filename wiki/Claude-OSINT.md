---
name: Claude-OSINT
tags: [osint, claude, skills, recon, red-team, bug-bounty, security, dorks, secret-scanning, mit]
description: "Paired Claude skills for OSINT methodology and offensive OSINT arsenal — 90+ recon modules, 48 secret-regex patterns, 80+ dorks, 27 attack-path templates"
source: sources/Claude-OSINT/
verification_date: 2026-07-30
verified_by: codegraph-verify
---

# Claude-OSINT

**Source:** `sources/Claude-OSINT/`

Claude-OSINT is a paired set of drop-in `SKILL.md` files that turn Claude into a god-mode external recon operator for authorized red-team and bug-bounty engagements. Two skills — `osint-methodology` (strategic thinking, 455 lines) and `offensive-osint` (tactical arsenal, 4,213 lines) — combine to deliver 90+ capabilities across 12 reconnaissance domains.

| Field | Value |
|---|---|
| **Origin** | [elementalsouls/Claude-OSINT](https://github.com/elementalsouls/Claude-OSINT) |
| **License** | MIT |
| **Format** | Markdown SKILL.md files |
| **Skills** | 2 (osint-methodology + offensive-osint) |
| **Recon Modules** | 90+ |
| **Scripts** | Python helpers (stdlib-only) |
| **Source** | `sources/Claude-OSINT/` |
| **Codegraph** | `graphs/Claude-OSINT/` |

## What is it?

Claude-OSINT provides a structured tradecraft library (4,600+ lines) that primes Claude with expert-level OSINT methodology. The methodology skill teaches strategic asset-graph discipline, severity rubrics, time budgeting, and identity-fabric mapping. The offensive-OSINT skill delivers a tactical arsenal of probe paths, regexes, payloads, scoring rules, curl one-liners, and tool URLs — turning Claude into a senior recon analyst that knows techniques, tooling, edge cases, and escalation paths while staying in scope.
## Key Features

- **90+ Recon Capabilities** — Across 12 domains: asset discovery, identity/SSO mapping, credential validation, subdomain enumeration, cloud reconnaissance, and more
- **48 Secret-Regex Patterns** — Pre-built patterns for finding leaked credentials across code, configs, and paste sites
- **80+ Google Dorks** — Targeted search operator chains for deep information discovery
- **27 Attack-Path Templates** — Structured escalation paths from initial recon to high-impact findings
- **5-Stage External Recon Pipeline** — Time-budget profiles for 1h, 4h, 1d, and 1w engagements
- **Skill Trigger-Activated** — Claude auto-loads the relevant skill based on conversational triggers (127 in offensive-osint + 52 in methodology)
- **32-Prompt Self-Evaluation Suite** — 31/32 PASS (96.9%) on comprehensive methodology testing. *Caveat: per `docs/coverage.md:72`, the 96.9% is "Claude grading itself on tests Claude designed... not an objective measure"*
- **4 End-to-End Engagement Walk-Throughs** — Realistic scenarios demonstrating the full workflow

## Tech Stack

| Component | Technology |
|---|---|
| **Skill Format** | Markdown SKILL.md (Claude Skills System) |
| **Scripts** | Python 3 (stdlib-only), no external dependencies |
| **Helpers** | `secret_scan.py` — stdlib-only secret scanner; `h1_reference.py` — HackerOne disclosed-reports reference agent |
| **Recon Sources** | crt.sh, Wayback CDX, WHOIS/RDAP, Shodan, Censys, GitHub, and 20+ public data sources |

## Deployment

Drop both skill directories into `~/.claude/skills/`:

```bash
git clone https://github.com/elementalsouls/Claude-OSINT ~/.claude/skills/claude-osint
# Or copy individual skills:
cp -r claude-osint/skills/osint-methodology ~/.claude/skills/
cp -r claude-osint/skills/offensive-osint ~/.claude/skills/
```

Claude auto-triggers on relevant phrases (e.g. "recon", "subdomain", "OSINT").

## Related

- [[Claude-Red]] — 58 offensive security skills for Claude Skills system
- [[SecOpsAgentKit]] — Security operations skills for AI coding agents
- [[ctf-skills]] — Agent Skills for CTF challenges across 11 categories
