---
name: ctf-skills-codegraph-verify
tags: [ctf, skills, security, capture-the-flag, claude-code, wiki]
description: "Codegraph Verification: ctf-skills — validating wiki claims against indexed source code symbols"
source: sources/ctf-skills/
---

# Codegraph Verification: ctf-skills

**Date:** 2026-07-30

## Claim 1: 11 skill directories = 9 challenge categories + ctf-writeup + solve-challenge orchestrator
- **Wiki says:** The repo ships 11 skill directories: 9 challenge categories (ctf-web, ctf-pwn, ctf-crypto, ctf-reverse, ctf-forensics, ctf-osint, ctf-ai-ml, ctf-malware, ctf-misc) plus `ctf-writeup` and `solve-challenge`.
- **Source evidence:**
  - Repo root contains exactly 11 skill dirs: `ctf-web/`, `ctf-pwn/`, `ctf-crypto/`, `ctf-reverse/`, `ctf-forensics/`, `ctf-osint/`, `ctf-ai-ml/`, `ctf-malware/`, `ctf-misc/`, `ctf-writeup/`, `solve-challenge/` (verified via filesystem listing)
  - `README.md:73-83` skill table lists all 9 categories plus solve-challenge ("Orchestrator skill — analyzes challenge and delegates to category skills") and ctf-writeup ("Generates standardized submission-style writeups")
- **Verdict:** ✅ CORRECT

## Claim 2: README per-category file counts exclude each directory's SKILL.md
- **Wiki says:** The README inventory lists ctf-web at 20 files, ctf-crypto at 16, ctf-pwn/ctf-reverse at 18, ctf-forensics at 14, ctf-misc at 12, and ctf-ai-ml/ctf-osint/ctf-malware at 3 — and these counts exclude the SKILL.md in each directory.
- **Source evidence:**
  - `README.md:74` ctf-web = 20 files; `README.md:76` ctf-crypto = 16 files
  - On-disk counts are README count + 1 SKILL.md each: ctf-web has 21 files, ctf-crypto 17, ctf-pwn 19, ctf-reverse 19, ctf-forensics 15, ctf-misc 13, ctf-ai-ml 4, ctf-osint 4, ctf-malware 4 (verified via filesystem listing)
  - `README.md:83-84` solve-challenge and ctf-writeup show 0 files because they contain only their SKILL.md
- **Verdict:** ✅ CORRECT

## Claim 3: Only two documented install paths — npx and Friday Studio
- **Wiki says:** The repository documents skill installation via `npx skills add ljagiello/ctf-skills` or Friday Studio import; no manual copy-to-user-skills-folder flow is documented.
- **Source evidence:**
  - `README.md:8` shows: `npx skills add ljagiello/ctf-skills`
  - `README.md:17-23` documents the Friday Studio path: "Import individual skills by reference (e.g. `ljagiello/ctf-skills/ctf-web`), or upload this repo as a folder"
  - No manual skills-folder copy path appears anywhere in the repository (grep over tracked files returns nothing)
- **Verdict:** ✅ CORRECT

## Claim 4: install_ctf_tools.sh with per-package-manager modes and --dry-run/--force/--verify
- **Wiki says:** `scripts/install_ctf_tools.sh` supports modes `all`, `python`, `apt`, `brew`, `gems`, `go`, `manual`, with `--dry-run` (preview), `--force` (reinstall), and `--verify` modes; logs go to `~/.ctf-tools/`.
- **Source evidence:**
  - `scripts/install_ctf_tools.sh:8-10` header documents modes: "python, apt, brew, gems, go, manual, all, --verify"
  - `scripts/install_ctf_tools.sh:12-13` options: `--dry-run` "Show what would be installed without installing", `--force` "Reinstall packages even if already present"
  - `scripts/install_ctf_tools.sh:33` `LOG_DIR="${HOME}/.ctf-tools"`; `scripts/install_ctf_tools.sh:41-48` argument parsing loop
  - `README.md:34-61` documents all modes and flags
- **Verdict:** ✅ CORRECT

## Claim 5: Supporting quality tooling — scripts, tests, pyproject, pre-commit
- **Wiki says:** The repo ships `scripts/generate_catalog.py`, `scripts/skill_security_auditor.py`, a pytest suite in `tests/`, `pyproject.toml`, and pre-commit/CI config.
- **Source evidence:**
  - `scripts/` contains `generate_catalog.py`, `install_ctf_tools.sh`, `skill_security_auditor.py` (verified via filesystem listing)
  - `tests/` contains `test_cross_references.py`, `test_skill_discoverability.py`, `test_skill_frontmatter.py`, `test_skill_security_auditor.py`
  - Repo root contains `pyproject.toml`, `.pre-commit-config.yaml`, `.markdownlint-cli2.yaml`, `.lychee.toml`, and `.github/` (CI)
- **Verdict:** ✅ CORRECT

## Claim 6: Each skill has a Prerequisites section for install-as-you-go
- **Wiki says:** Each skill's SKILL.md has a Prerequisites section listing only the tools needed for that category; the README recommends installing tools on demand during a challenge.
- **Source evidence:**
  - `README.md:67` states: "Each skill's `SKILL.md` has a **Prerequisites** section listing only the tools needed for that category. Install as you go when the agent encounters a missing tool."
  - `README.md:30-31` "Pre-install (recommended before competitions)" vs `README.md:65-67` "On-demand (during challenges)" strategy split
- **Verdict:** ✅ CORRECT

## Summary

All 6 key claims from the ctf-skills wiki have been verified against the source code:
- ✅ 11 skill directories: 9 challenge categories + writeup + orchestrator confirmed
- ✅ README counts exclude SKILL.md: on-disk counts are exactly +1 each
- ✅ Only two install paths: npx and Friday Studio; no manual skills-folder copy claim in repo
- ✅ install_ctf_tools.sh modes and flags: header and argument parsing confirmed
- ✅ Quality tooling: catalog + security auditor scripts, pytest suite, pyproject, pre-commit confirmed
- ✅ Prerequisites per skill: README.md confirms per-skill Prerequisites and on-demand install

## Related

- [[ctf-skills]] -- Main wiki entry

## Cross-project

- [[claude-skills-journalism.codegraph-verify]] -- Similar codegraph verification for skill collections
- [[SecOpsAgentKit.codegraph-verify]] -- Similar codegraph verification for skill collections
