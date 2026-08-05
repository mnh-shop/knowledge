---
name: swe-cli-skills-codegraph-verify
tags: [swe, cli, skills, devops, cloud, containers, databases, platforms, wiki]
description: "Codegraph Verification: swe-cli-skills — validating wiki claims against indexed source code symbols"
source: sources/swe-cli-skills/
---

# Codegraph Verification: swe-cli-skills

**Date:** 2026-07-30

> This page verifies the REWRITTEN wiki. The previous wiki contained fabricated content (wrong origin `swe-cli/skills`, invented categories like "System Admin"/"Text Processing", and fake CLIs like yq, awk, systemd, tar, rsync, find, grep). All claims below were re-verified against the source repo and the fabricated statements were corrected.

## Claim 1: Origin is SylphAI-Inc/swe-cli-skills, maker is SylphAI
- **Wiki says:** The repo originates from [SylphAI-Inc/swe-cli-skills](https://github.com/SylphAI-Inc/swe-cli-skills), built by SylphAI (makers of AdaL).
- **Source evidence:**
  - Git remote: `origin https://github.com/SylphAI-Inc/swe-cli-skills`
  - `README.md` line 18: `npx skills add SylphAI-Inc/swe-cli-skills`
  - `README.md` line 357: "Built by [SylphAI](https://sylph.ai/) — the team behind [AdaL](https://docs.sylph.ai/)"
- **Verdict:** ✅ CORRECT
- **Correction:** Previous wiki claimed origin `swe-cli/skills` — WRONG, fixed.

## Claim 2: MIT license, Copyright (c) 2026 SylphAI, Inc.
- **Wiki says:** Licensed MIT with "Copyright (c) 2026 SylphAI, Inc."
- **Source evidence:**
  - `LICENSE` line 1: "MIT License"
  - `LICENSE` line 3: "Copyright (c) 2026 SylphAI, Inc."
  - `README.md` line 350: "MIT — use these skills in any project, commercial or open-source."
- **Verdict:** ✅ CORRECT
- **Correction:** Previous wiki said "Not specified" — WRONG, fixed.

## Claim 3: 23 CLIs across 9 categories, real inventory
- **Wiki says:** Covers 23 CLIs organized into 9 real categories: cloud, iac, containers, git-vcs, dev-tools, package-managers, databases, platforms, networking.
- **Source evidence:**
  - `README.md` line 7: "It covers **23 CLIs** across 9 categories"
  - Actual `skills/` directory listing: cloud/ (aws, azure, gcloud = 3), iac/ (terraform = 1), containers/ (docker, kubectl, helm = 3), git-vcs/ (git, gh = 2), dev-tools/ (jq, make, sed = 3), package-managers/ (npm, pip-uv = 2), databases/ (psql, redis = 2), platforms/ (stripe, sentry, vercel, firebase, fly = 5), networking/ (curl, ssh = 2) — totals 23
  - Each category directory contains an `INDEX.md` listing its guides (e.g. `skills/networking/INDEX.md` lines 5-8: curl, SSH/SCP)
- **Verdict:** ✅ CORRECT
- **Correction:** Previous wiki fabricated categories ("Version Control / Data Processing / System Admin / File Operations / Text Processing / Shell Scripting") and CLIs (yq, awk, systemd, journalctl, tar, rsync, scp, find, grep, sort, uniq, wc, xargs) — all WRONG, replaced with the real inventory.

## Claim 4: Guide anatomy — YAML frontmatter + 7-section structure
- **Wiki says:** Guides carry YAML frontmatter (name, description, version, category) and follow a consistent 7-section structure; some guides (e.g. stripe) have no frontmatter.
- **Source evidence:**
  - `skills/dev-tools/jq.md` lines 1-5: `name: jq`, `description: ...`, `version: "1.7+"`, `category: dev-tools`
  - `skills/platforms/stripe.md` line 1 starts directly with `# Stripe CLI` — no frontmatter
  - `SKILL.md` lines 117-125: the 7 sections (Setup & Auth, Core Workflows, Flag Gotchas, Error Patterns, Anti-Patterns, Composability, Agent Constraints)
  - `README.md` lines 194-201: same 7-section structure documented
  - `SKILL_TEMPLATE.md` defines the template with frontmatter fields and section-by-section guidance
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Category sub-index architecture for token efficiency
- **Wiki says:** Uses a category sub-index architecture — the agent reads root SKILL.md, then loads only the specific CLI guide (~200-400 lines) instead of the entire library.
- **Source evidence:**
  - `SKILL.md` line 111: "This skill uses a **category sub-index architecture**"
  - `SKILL.md` lines 112-113: read root SKILL.md to find the category, then read only the specific CLI guide
  - `SKILL.md` line 115: "load one guide (~200-400 lines) instead of the entire library"
  - `README.md` line 259: "the agent only loads one guide (~200-400 lines) instead of the entire library"
  - Guide sizes confirmed in range: 184 lines (sed) to 377 lines (aws)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Installable via npx skills CLI and AdaL plugin marketplace
- **Wiki says:** Install with `npx skills add SylphAI-Inc/swe-cli-skills`, or via the AdaL plugin marketplace, or by manual git clone per agent.
- **Source evidence:**
  - `README.md` line 15: "### npx ([skills CLI](https://skills.sh/docs/cli))"
  - `README.md` line 18: `npx skills add SylphAI-Inc/swe-cli-skills`
  - `README.md` lines 27-30: `/plugin marketplace add SylphAI-Inc/swe-cli-skills` then `/plugin install swe-cli-skills@swe-cli-skills`
  - `README.md` lines 33-86: manual clone instructions per agent (AdaL, Claude Code, Codex, Gemini CLI, Copilot, Cursor/Windsurf)
- **Verdict:** ✅ CORRECT
- **Correction:** Previous wiki showed a fabricated `npx skills install swe-cli-skills/git` form — WRONG, replaced with the real `npx skills add SylphAI-Inc/swe-cli-skills` command.

## Claim 7: 17 critical gotchas in the root SKILL.md
- **Wiki says:** The root SKILL.md opens with a "Quick Reference: Critical Gotchas" listing 17 highest-impact mistakes.
- **Source evidence:**
  - `SKILL.md` line 87: "## Quick Reference: Critical Gotchas"
  - `SKILL.md` lines 91-107: exactly 17 bullet gotchas (AWS S3, Terraform, Docker, kubectl, Helm, Git, SSH, psql, Redis, gcloud, npm, sed, make, Stripe, Sentry, Vercel, Firebase)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: Roadmap (v0.1 → v1.0) and agent compatibility
- **Wiki says:** Roadmap runs v0.1 (10 CLIs) → v0.2 (16) → v0.3 (23) → v1.0 (30+ CLIs); compatible with AdaL, Claude Code, Codex, Gemini CLI, Copilot, Cursor, Windsurf, Aider, OpenCode.
- **Source evidence:**
  - `README.md` lines 323-328: roadmap checklist — v0.1 core 10 CLIs, v0.2 16 CLIs, v0.3 23 CLIs, v0.4 planned (rsync, mysql, mongo, yarn/pnpm, cargo, go, poetry, openssl), v1.0 "30+ CLIs, community contributions, CI validation"
  - `README.md` lines 293-306: compatible agents list — AdaL, Claude Code, OpenAI Codex, Gemini CLI, GitHub Copilot, Cursor, Windsurf, Aider, OpenCode
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 8 key claims from the rewritten swe-cli-skills wiki have been verified against the source repo:
- ✅ Origin SylphAI-Inc/swe-cli-skills (previously WRONG as swe-cli/skills — corrected)
- ✅ MIT license (previously WRONG as "Not specified" — corrected)
- ✅ 23 CLIs across 9 real categories (fabricated categories/CLIs removed — corrected)
- ✅ Guide anatomy: frontmatter + 7-section structure (stripe lacks frontmatter)
- ✅ Category sub-index token-efficient architecture
- ✅ Real npx + AdaL plugin install commands (fabricated install form removed — corrected)
- ✅ 17 critical gotchas in SKILL.md
- ✅ Roadmap v0.1→v1.0 and 9-agent compatibility list

## Related

- [[swe-cli-skills]] -- Main wiki entry

## Cross-project

- [[superpowers.codegraph-verify]] -- Similar codegraph verification for Superpowers
- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
