---
title: "Anthropic-Cybersecurity-Skills"
subtitle: "CodeGraph Verification Companion"
suffix: ".codegraph-verify"
date: 2026-07-12
verified_by: "codegraph-explore"
source: "sources/Anthropic-Cybersecurity-Skills/"
tags: [anthropic-cybersecurity-skills, codegraph-verify, security, claude-code]
related:
  - "[[Anthropic-Cybersecurity-Skills]]"
  - "[[SecuritySkills]]"
  - "[[Android-Pentesting-Checklist]]"
  - "[[kali-pentest]]"
---

# Anthropic-Cybersecurity-Skills — CodeGraph Verification

**Verification date:** 2026-07-12  
**Verified by:** codegraph-explore (source tree analysis)  
**Source reference:** `sources/Anthropic-Cybersecurity-Skills/`  
**Companion to:** [[Anthropic-Cybersecurity-Skills]]

---

## Claim-1: Repository contains 817 production-grade cybersecurity skills across 29 domains

The repository ships **817 structured cybersecurity skills** organized across **29 security domains**. Verified by reading from `sources/Anthropic-Cybersecurity-Skills/`:

- README badge: `[![Skills](https://img.shields.io/badge/skills-817-brightgreen)]` (line 13)
- Body text: "817 production-grade cybersecurity skills · 29 security domains" (line 27)
- Domain table lists 29 rows (Cloud Security through Hardware & Firmware Security), lines 150–180
- Actual filesystem: `ls skills/ | wc -l` returns **817** — one directory per skill, confirmed against disk

**Source evidence:** `sources/Anthropic-Cybersecurity-Skills/README.md` lines 13, 27, 150–180; filesystem listing of `skills/` directory.

---

## Claim-2: Skills map to six frameworks — but coverage is partial, not universal

The README's aspirational claim (line 43: "Every skill is mapped to six industry frameworks") does not hold against the actual filesystem. Measured across all **817** `skills/*/SKILL.md` files by counting which frontmatter framework key each file declares:

| Framework key | Skills declaring it | Coverage |
|---------------|--------------------:|---------:|
| `mitre_attack` | 817 | 100.0% |
| `nist_csf` | 816 | 99.9% |
| `d3fend_techniques` | 139 | ~17% |
| `mitre_f3` | 94 | ~12% |
| `nist_ai_rmf` | 85 | ~10% |
| `atlas_techniques` | 81 | ~10% |

Only ATT&CK and (nominally) NIST CSF approach full coverage; ATLAS, D3FEND, AI RMF, and F3 appear in a small minority of skills. Framework versions/scopes per the README table: ATT&CK v19.1 (15 tactics, 286 techniques), NIST CSF 2.0 (6 functions, 22 categories), ATLAS v5.4 (16 tactics, 84 techniques), D3FEND v1.3 (7 categories, 267 techniques), AI RMF 1.0 (4 functions, 72 subcategories), F3 v1.1 (8 tactics, 123 techniques, 94 fraud-relevant skills).

**Source evidence:** `sources/Anthropic-Cybersecurity-Skills/README.md` lines 43–56 (six-framework table, aspirational claim); filesystem `grep -rl "^<key>:" skills/*/SKILL.md` counts; `docs/mitre-f3-mapping.md` (F3 schema documentation).

---

## Claim-3: Skills use progressive disclosure architecture (frontmatter + Markdown body + references + scripts)

Each skill follows the agentskills.io standard with a consistent directory structure:

```
skills/performing-memory-forensics-with-volatility3/
├── SKILL.md              ← Skill definition (YAML frontmatter + Markdown body)
├── references/
│   ├── standards.md      ← MITRE ATT&CK, ATLAS, D3FEND, NIST mappings
│   └── workflows.md      ← Deep technical procedure reference
├── scripts/
│   └── process.py        ← Working helper scripts
└── assets/
    └── template.md       ← Filled-in checklists and report templates
```

Agent discovery is designed for ~30 tokens per skill (frontmatter only) and 500–2000 tokens for full load. This enables agents to search all 817 skills in a single pass without blowing context windows.

**Source evidence:** `sources/Anthropic-Cybersecurity-Skills/README.md` lines 182–262 (skill anatomy, YAML frontmatter example, Markdown body sections, token-cost estimates).

---

## Claim-4: MITRE ATT&CK v19.1 coverage table — README totals stale, no shipped validation

The README documents ATT&CK v19.1 coverage (lines 81–97). The tactic table is shown below with the actual sum of its own rows:

| Tactic | ID | Skills |
|--------|----|--------|
| Reconnaissance | TA0043 | 103 |
| Resource Development | TA0042 | 22 |
| Initial Access | TA0001 | 467 |
| Execution | TA0002 | 350 |
| Persistence | TA0003 | 444 |
| Privilege Escalation | TA0004 | 464 |
| Stealth | TA0005 | 442 |
| Defense Impairment | TA0112 | 92 |
| Credential Access | TA0006 | 202 |
| Discovery | TA0007 | 237 |
| Lateral Movement | TA0008 | 68 |
| Collection | TA0009 | 172 |
| Command and Control | TA0011 | 123 |
| Exfiltration | TA0010 | 82 |
| Impact | TA0040 | 50 |

Corrections against source:

- **The table sums to 3,318 skill–tactic assignments, not 3,518.**
- **README's "754/754 skills mapped" (line 77) is stale** — the repo now ships 817 skills; only the 817/817 ATT&CK count (line 43/Claim-2 measurement) is current.
- **No ATT&CK ID validation is shipped.** README:79 claims IDs were "validated against ... the official `mitreattack-python` library", but no `.py` file imports `mitreattack` — `tools/validate-skill.py` validates structure only (required fields, kebab-case name ≤64, description ≥50 chars, subdomain registry, ≥2 tags; lines 182–257).
- **The ATT&CK Navigator layer file targets v14, not v19.1**: `mappings/attack-navigator-layer.json` declares `"versions": { "attack": "14", ... }`.

v19.1's restructured Defense Evasion (split into Stealth and Defense Impairment) is reflected in the table.

**Source evidence:** `sources/Anthropic-Cybersecurity-Skills/README.md` lines 77–98 (ATT&CK coverage table, stale 754/754 and v19.1 validation claims), `tools/validate-skill.py` lines 182–257 (structure-only validation), `mappings/attack-navigator-layer.json` (versions block, `"attack": "14"`), `mappings/mitre-attack/` directory.

---

## Claim-5: Includes MITRE Fight Fraud Framework (F3) v1.1 with 94 fraud-relevant skills

The repository added 94 fraud-relevant skills mapped to the MITRE Fight Fraud Framework (F3) v1.1, released April 9, 2026 by MITRE's CTID. F3 covers two fraud-specific tactics not found in ATT&CK:

- **Positioning** (`FA0001`) — synthetic-identity seeding, account warming, SIM-swap pre-positioning
- **Monetization** (`FA0002`) — money-mule layering, APP fraud, crypto off-ramping

Fraud-specific techniques use `F1XXX` IDs (e.g., `F1005.003` Add Beneficiary). All 123 F3 v1.1 technique IDs were verified against the upstream STIX bundle. Mapping documentation lives in `docs/mitre-f3-mapping.md`.

**Source evidence:** `sources/Anthropic-Cybersecurity-Skills/README.md` lines 65–75 (F3 section), `docs/mitre-f3-mapping.md` (schema documentation).

---

## Claim-6: Compatible with 26+ AI platforms via agentskills.io standard

The repository documents compatibility with **26+ platforms** across four categories:

- **AI code assistants:** Claude Code, GitHub Copilot, Cursor, Windsurf, Cline, Aider, Continue, Roo Code, Amazon Q Developer, Tabnine, Sourcegraph Cody, JetBrains AI
- **CLI agents:** OpenAI Codex CLI, Gemini CLI
- **Autonomous agents:** Devin, Replit Agent, SWE-agent, OpenHands
- **Agent frameworks:** LangChain, CrewAI, AutoGen, Semantic Kernel, Haystack, Vercel AI SDK, any MCP-compatible agent

All platforms supporting the agentskills.io standard can load these skills with zero configuration. Quick start via `npx skills add mukul975/Anthropic-Cybersecurity-Skills` or git clone.

**Source evidence:** `sources/Anthropic-Cybersecurity-Skills/README.md` lines 328–342 (compatible platforms), lines 99–110 (quick start).

---

## Related Pages

- [[Anthropic-Cybersecurity-Skills]] — Main wiki entry for this repository
- [[SecuritySkills]] — 45 framework-grounded security skills (complementary approach)
- [[Android-Pentesting-Checklist]] — Android-specific pentesting checklist
- [[kali-pentest]] — Kali Linux penetration testing automation
