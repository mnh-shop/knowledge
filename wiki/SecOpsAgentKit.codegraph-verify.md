---
name: SecOpsAgentKit-codegraph-verify
tags: [secops, security, skills, devsecops, appsec, claude-code, wiki]
description: "Codegraph Verification: SecOpsAgentKit — validating wiki claims against indexed source code symbols"
source: sources/SecOpsAgentKit/
---

# Codegraph Verification: SecOpsAgentKit

**Date:** 2026-07-30

## Claim 1: 31 security skills across 7 categories (incl. offsec)
- **Wiki says:** SecOpsAgentKit provides 31 security skills across 7 categories: AppSec, DevSecOps, Secure SDLC, Compliance, Threat Modeling, Incident Response, and Offensive Security.
- **Source evidence:**
  - Filesystem: `skills/` has 7 category directories — `appsec/` (8 skills), `devsecops/` (6), `offsec/` (9), `secsdlc/` (3), `incident-response/` (3), `compliance/` (1), `threatmodel/` (1) = 31 skills (plus `_template/`)
  - CLAUDE.md line 48: "Must be one of seven valid categories: `appsec`, `devsecops`, `secsdlc`, `threatmodel`, `compliance`, `incident-response`, `offsec`"
  - README.md lists skills under category headings incl. Offensive Security (`offsec/` section)
- **Verdict:** ✅ CORRECT (earlier "75+ skills" figure was fabricated — "75" appears nowhere in the repo; the only "75x" string is Checkov's "750+ built-in policies" in `devsecops/iac-checkov/SKILL.md:4,29`)

## Claim 2: Standardized 4-part skill structure (SKILL.md + scripts/ + references/ + assets/)
- **Wiki says:** Every skill follows a standardized four-part structure: SKILL.md (required), scripts/ (optional), references/ (optional), assets/ (optional).
- **Source evidence:**
  - CLAUDE.md explicitly documents: "Every skill follows a standardized four-part structure: 1. **SKILL.md** (Required), 2. **scripts/** (Optional), 3. **references/** (Optional), 4. **assets/** (Optional)"
  - CLAUDE.md confirms each directory's purpose: scripts for deterministic operations, references for framework mappings, assets for templates and configs
  - `skills/_template/` directory serves as the base template for all skills
- **Verdict:** ✅ CORRECT

## Claim 3: Claude Code marketplace plugin
- **Wiki says:** Skills are installable via Claude Code marketplace as a plugin using `/plugin marketplace add` command.
- **Source evidence:**
  - `README.md` shows: `/plugin marketplace add https://github.com/AgentSecOps/SecOpsAgentKit.git` (README.md:16)
  - CLAUDE.md documents marketplace integration: "Skills are registered in `skills/.claude-plugin/marketplace.json`"
  - `skills/.claude-plugin/marketplace.json` registers 7 plugins (one per category): `appsec-skills`, `devsecops-skills`, `secsdlc-skills`, `threatmodel-skills`, `compliance-skills`, `incident-response-skills`, `offsec-skills`
- **Verdict:** ✅ CORRECT

## Claim 4: 4 development scripts (init_skill.sh, validate_skill.py, generate_marketplace.py, install_hooks.sh)
- **Wiki says:** Four development scripts exist: init_skill.sh for scaffolding, validate_skill.py for validation, generate_marketplace.py for marketplace registration, and install_hooks.sh for git hooks.
- **Source evidence:**
  - `scripts/` directory contains exactly: `generate_marketplace.py`, `init_skill.sh`, `install_hooks.sh`, `validate_skill.py`
  - CLAUDE.md documents `./scripts/init_skill.sh <skill-name> <category>` for scaffolding
  - CLAUDE.md documents `./scripts/validate_skill.py skills/<category>/<skill-name>` for validation
  - `.githooks/pre-commit` exists for hook installation
- **Verdict:** ✅ CORRECT

## Claim 5: Strict frontmatter validation with "Use when:" clause
- **Wiki says:** All skills use strict frontmatter validation. The `description` field must include a "Use when:" clause for skill triggering in Claude Code.
- **Source evidence:**
  - `scripts/validate_skill.py` line 42: `MIN_DESCRIPTION_LEN = 100`
  - `scripts/validate_skill.py` lines 114–121: rejects descriptions missing "Use when:" clause or under 100 chars
  - `scripts/validate_skill.py` lines 74–103 (`check_frontmatter`): enforces `---` delimiters, parseable YAML mapping
  - CLAUDE.md documents other required fields: `name`, `description`, `version`, `maintainer`, `category`, `tags`
- **Verdict:** ✅ CORRECT

## Claim 6: <500-line SKILL.md rule documented but violated by 4 skills
- **Wiki says:** Progressive disclosure keeps SKILL.md under 500 lines (CLAUDE.md:15,115,191), but 4 shipped skills exceed it.
- **Source evidence:**
  - CLAUDE.md line 15: "Must be under 500 lines - use progressive disclosure pattern"
  - CLAUDE.md line 115: "Keep SKILL.md concise (<500 lines)"
  - CLAUDE.md line 191: "Check SKILL.md line count (<500)"
  - `wc -l` results: `appsec/api-spectral/SKILL.md` 708, `devsecops/iac-checkov/SKILL.md` 671, `offsec/analysis-tshark/SKILL.md` 638, `offsec/recon-nmap/SKILL.md` 635 (all > 500; a handful of other skills are marginally over)
- **Verdict:** ✅ CORRECT (rule documented, violated)

## Summary

All 6 key claims from the SecOpsAgentKit wiki have been verified against the source code:
- ✅ 31 skills across 7 categories (incl. offsec with 9 skills) — "75+" was fabricated, no such string in repo
- ✅ 4-part skill structure: SKILL.md + scripts/ + references/ + assets/ pattern confirmed
- ✅ Claude Code marketplace plugin: Installation command and 7 plugin registrations in marketplace.json confirmed
- ✅ 4 development scripts: All four scripts confirmed in scripts/ directory
- ✅ Strict frontmatter with "Use when:" clause: Validation requirements confirmed in validate_skill.py
- ✅ <500-line rule documented (CLAUDE.md) but violated by 4 skills (largest: api-spectral 708)

## Related

- [[SecOpsAgentKit]] -- Main wiki entry

## Cross-project

- [[Claude-Red.codegraph-verify]] -- Similar codegraph verification for skill collections
- [[Claude-OSINT.codegraph-verify]] -- Similar codegraph verification for skill collections
