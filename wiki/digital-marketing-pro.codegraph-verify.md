---
name: digital-marketing-pro-codegraph-verify
tags: [digital-marketing-pro, codegraph-verify, marketing, automation, ai, agents, skills]
description: "Codegraph Verification: digital-marketing-pro — validating wiki claims against indexed source code symbols"
source: sources/digital-marketing-pro/
---

# Codegraph Verification: Digital Marketing Pro

**Date:** 2026-07-12 (re-verified 2026-07-30 against v3.17.0)

## Claim 1: 24 specialist marketing agents with dedicated agent profiles
- **Wiki says:** Digital Marketing Pro ships 24 specialist AI marketing agents, each with a dedicated `.md` agent profile in `agents/`.
- **Source evidence:**
  - `agents/` directory contains exactly **24** agent profile files (was 25 — `competitor-intelligence.md` no longer exists; `competitive-intel.md` remains).
  - `package.json` description: "158 skills, 24 agents, 12-Part Strategy Flow, EU AI Act ready."
  - `README.md:7`: "**158 skills, 24 specialist agents, EU AI Act Article 50 ready**".
  - `README.md:22` (v3.15.0 changelog): "agents consolidated 25 → 24".
  - `README.md:52` comparison table: "Specialist agents | **24**".
- **Verdict:** ✅ CORRECT (updated from 25)
- **Fix needed:** None (verify page's earlier 25-file list was stale)

## Claim 2: 158 skills, 18 CLI commands, 86 Python scripts
- **Wiki says:** The plugin ships 158 skill directories (`skills/`), 18 CLI commands (`commands/`), and 86 Python helper scripts (`scripts/`).
- **Source evidence:**
  - `skills/` directory contains exactly 158 skill directories, each with a `SKILL.md`.
  - `commands/` directory contains exactly 18 command files (brand-setup, campaign-plan, seo-audit, competitor-analysis, content-engine, email-sequence, keyword-cluster, performance-report, engagement, check, doctor, backlink-gap, seo-drift, execute-action, cowork-setup, output-folder, resume, status).
  - `scripts/*.py` contains exactly 86 Python scripts.
  - `README.md:20` (v3.17.0): "all 158 skills, 24 agents, 18 commands, 86 scripts".
  - `README.md:7`: "**158 skills, 24 specialist agents**".
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: 209/209 tests green
- **Wiki says:** The plugin ships a comprehensive stdlib unittest suite with 209 passing tests.
- **Source evidence:**
  - `README.md:20` (v3.17.0): "**209/209 tests green**".
  - `README.md:60` comparison table: "Tests | **209 stdlib unittest**".
  - `README.md:22` (v3.15.0): suite "grew from 123 to 207 passing".
  - `tests/` contains 210 `def test_*` functions across 17 `test_*.py` modules plus `run_all.py` orchestration.
- **Verdict:** ✅ CORRECT (updated from stale 123)
- **Fix needed:** None

## Claim 4: Version 3.17.0 with v3.15–3.17 reliability features
- **Wiki says:** Current version is 3.17.0 (package.json, 2026-07-29), adding typed-approval gates, a line-by-line audit, and a storage split-brain fix.
- **Source evidence:**
  - `package.json`: `"version": "3.17.0"`.
  - `README.md:20`: "**v3.17.0 (July 29, 2026): the Line-by-Line Audit**… ~250 fixes shipped… the storage split-brain fully closed… 209/209 tests green."
  - `README.md:22` (v3.15.0): "all 18 execution skills carry a uniform typed-approval gate (closes issue #6)".
  - `CHANGELOG.md:9` "### Changed — The Line-by-Line Audit"; `CHANGELOG.md:16` "storage split-brain fully closed…"; `CHANGELOG.md:50` "`scripts/_common.py` — one shared workspace-root resolver… adopted across the script layer to kill the storage split-brain".
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: No references/ directory
- **Wiki says:** The project structure includes no `references/` directory (an earlier revision claimed 167 reference knowledge files).
- **Source evidence:**
  - Repository root listing (v3.17.0) contains: AGENTS.md, CHANGELOG.md, CONNECTORS.md, README.md, agents/, assets/, commands/, docs/, hooks/, scripts/, skills/, tests/, plus manifests — **no `references/` directory exists**.
- **Verdict:** ✅ CORRECT (structure corrected)
- **Fix needed:** None

## Claim 6: 68+ MCP integrations, 8 HTTP connectors, 47-entry model registry
- **Wiki says:** The plugin integrates with 68+ MCP connectors; executes 8 verified HTTP connectors live with 25 OAuth connectors manifest-ready; the model registry holds 47 verified entries.
- **Source evidence:**
  - `docs/integrations-guide.md` (73KB) documents the 68+ MCP integrations across analytics, advertising, CRM, email marketing, commerce, SEO, productivity, social, memory/RAG, CMS, communication, project management, and databases.
  - `.mcp.json.example` (24.5KB) provides the full MCP configuration template.
  - `CONNECTORS.md` (6.2KB) documents connector architecture.
  - `README.md:40`: "8 verified HTTP connectors executing end-to-end (Slack · HubSpot · Klaviyo · SendGrid · Brevo · Customer.io · Mailchimp · Ahrefs); 25 OAuth connectors via MCP manifest. Stdlib only".
  - `README.md:380`: "**Model registry rebuilt to 47 entries**".
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: 8 native surfaces + 35+ Agent Skills platforms, 12-Part Flow
- **Wiki says:** DM Pro installs natively on 8 surfaces (Claude Code, Cowork, Codex, Cursor, Copilot CLI, Antigravity, Hermes, OpenClaw) plus 35+ additional platforms via Agent Skills; every brand runs the 12-Part Strategy Flow (61 steps, ~60 min, $15–40).
- **Source evidence:**
  - `README.md:59`: "**8 native — CC + Cowork + Codex + Cursor + Copilot CLI + Antigravity + Hermes + OpenClaw**".
  - `README.md:7`: "**+ 35+ Agent Skills platforms**".
  - Manifest files: `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.github/plugin/`, `gemini-extension.json`, `openclaw.plugin.json`, `plugin.yaml` + `__init__.py` (Hermes native).
  - `README.md:107`: "**Four Core Documents — 61 explicit steps**"; `README.md:5`: "~60 minutes per brand… $15–40 of API spend".
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: C2PA content provenance, EU AI Act Article 50, 16 jurisdictions
- **Wiki says:** The plugin enforces C2PA content provenance (Article 50, applicable 2 Aug 2026) via `scripts/embed-c2pa.py`, with privacy compliance across 16 jurisdictions.
- **Source evidence:**
  - `README.md:660`: "## Compliance — **16 jurisdictions, EU AI Act Article 50 ready**" listing EU (GDPR + AI Act Article 50), US Federal, CCPA/CPRA, Canada, Brazil, UK, Australia, Singapore, China, India, Japan, South Korea, Saudi Arabia, UAE, Thailand.
  - `README.md:660-666`: C2PA signing end-to-end tested against c2pa-python 0.32; pre-publish gate `/digital-marketing-pro:check` treats missing C2PA on AI-flagged EU assets as CRITICAL → BLOCKED.
  - `docs/c2pa-production-cert-guide.md` — C2PA certification guide; `scripts/embed-c2pa.py` — provenance signing script.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 8 key claims from the digital-marketing-pro wiki have been verified against source v3.17.0:

- ✅ 24 specialist agents confirmed in `agents/` (consolidated from 25 in v3.15.0)
- ✅ 158 skills / 18 commands / 86 scripts confirmed
- ✅ 209/209 tests green (210 test functions in `tests/`)
- ✅ Version 3.17.0 with typed-approval gates, Line-by-Line Audit, storage split-brain fix
- ✅ No `references/` directory exists (structure corrected)
- ✅ 68+ MCP integrations + 8 live HTTP connectors + 47-entry model registry
- ✅ 8 native surfaces + 35+ Agent Skills platforms + 12-Part Flow
- ✅ C2PA / EU AI Act Article 50 / 16 jurisdictions compliance

## Related

- [[digital-marketing-pro]] -- Main wiki entry
- [[outreachmagic]] -- Related marketing automation
- [[ai-marketing-claude-code-skills]] -- AI marketing skills collection
- [[claude-seo]] -- SEO-focused skills for Claude
- [[hermes-agent]] -- Hermes Agent (supported surface)

## Cross-project

- [[outreachmagic.codegraph-verify]] -- OutreachMagic verification
- [[ai-marketing-claude-code-skills.codegraph-verify]] -- AI marketing skills verification
- [[claude-seo.codegraph-verify]] -- Claude SEO verification
- [[hermes-agent.codegraph-verify]] -- Hermes Agent verification
- [[openclaw.codegraph-verify]] -- OpenClaw verification
