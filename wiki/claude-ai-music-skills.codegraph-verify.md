---
name: claude-ai-music-skills-codegraph-verify
tags: [claude-ai-music-skills, codegraph-verify, claude-code, music]
description: "Codegraph Verification: claude-ai-music-skills"
source: sources/claude-ai-music-skills/
---

# Codegraph Verification: claude-ai-music-skills

**Date:** 2026-07-30

## Claim 1: 53 skills, not "90+", and plugin version 0.101.0
- **Wiki says:** The plugin ships 53 skills at version 0.101.0.
- **Source evidence:** `ls skills/ | wc -l` = 53. README.md:59: "### Skill System (53 Skills)"; README.md:136 lists "All 53 skills". `.claude-plugin/plugin.json` declares `"version": "0.101.0"` and `"skills": "./skills/"`. CHANGELOG.md:9: "## [0.101.0] - 2026-07-21".
- **Verdict:** ✅ CORRECT
- **Fix needed:** Wiki corrected from "90+ skills" / version 2.0.0 / AgriciDaniel origin → 53 skills / 0.101.0 / bitwize-music-studio.

## Claim 2: Origin is bitwize-music-studio, not AgriciDaniel; Python + Markdown + shell stack
- **Wiki says:** The repository is `bitwize-music-studio/claude-ai-music-skills`, built on Python + Markdown + shell — no TypeScript/Web Audio/AudioWorklet/IndexedDB/SQLite.
- **Source evidence:** `.claude-plugin/plugin.json` `repository` and `homepage` fields point to `https://github.com/bitwize-music-studio/claude-ai-music-skills`; README install snippet (line 47 area) uses `/plugin marketplace add bitwize-music-studio/claude-ai-music-skills`. Grep across all `.md`/`.py`/`.json`/`.toml`/Makefile for `TypeScript`, `\.ts`, `Web Audio`, `AudioWorklet`, `IndexedDB`, `SQLite`, `/api/melodies`, `ws://localhost:8080`, `daniel@musicclaude`, `AgriciDaniel` → 0 files. The only "quantum" hits are genre-reference content (e.g. `genres/gqom/README.md:9` "quantum sound" subgenre, song/album titles) — not a roadmap feature. `pyproject.toml`, `requirements.txt`, `Makefile` confirm Python toolchain; skills are markdown.
- **Verdict:** ✅ CORRECT
- **Fix needed:** Fabricated tech stack (TypeScript primary, Web Audio API, AudioWorklet, IndexedDB, SQLite), REST/WebSocket API sections, and daniel@musicclaude.com contact removed from wiki.

## Claim 3: Multi-model tier orchestration (Opus 4.8 / Sonnet 4.6 / Haiku 4.5)
- **Wiki says:** Skills declare their required Claude model across three tiers — Creative (Opus 4.8, 7 skills), Reasoning (Sonnet 4.6, 30 skills), Mechanical (Haiku 4.5, 16 skills).
- **Source evidence:** README.md:67 "### Multi-Model Orchestration"; README.md:73-75 table rows: "| Creative | Opus 4.8 | 7 | ... |", "| Reasoning | Sonnet 4.6 | 30 | ... |", "| Mechanical | Haiku 4.5 | 16 | ... |". CLAUDE.md:109 (step 5 note): "skills use tier aliases (`opus`/`sonnet`/`haiku`) that auto-track the frontier model". Per-skill rationale in `reference/model-strategy.md`.
- **Verdict:** ✅ CORRECT
- **Fix needed:** This headline feature was absent from the wiki — added.

## Claim 4: MCP server for state via stdio; preferred data access
- **Wiki says:** `servers/bitwize-music-server/` implements a stdio MCP server (bitwize-music-mcp) exposing structured state tools; it is the preferred way to query project state. No HTTP server exists.
- **Source evidence:** `servers/bitwize-music-server/` contains `run.py`, `server.py`, `handlers/`, `mcp-launch`. `.mcp.json` registers `"bitwize-music-mcp"` with `"type": "stdio"`. CLAUDE.md:52-62: "The `bitwize-music-mcp` server is the **preferred way to query project state**" with tool list `list_albums`, `find_album`, `get_track`, `list_skills`, `get_skill`, `get_ideas`, `get_pending_verifications`, `get_config`, `get_session`, `update_session`, `search`, `rebuild_state`. `reference/state-schema.md` documents the cache schema. README.md:77 "### MCP Server (80+ Tools)".
- **Verdict:** ✅ CORRECT
- **Fix needed:** Fabricated REST (`GET /api/melodies`) and WebSocket (`ws://localhost:8080/music`) API sections removed — repo has only stdio MCP.

## Claim 5: Album production pipeline with source verification gate
- **Wiki says:** Core workflow is Concept → Research → Write (+Suno Prompt) → QC/Verify → Generate → Master → Release, gated by a human source-verification step that blocks generation.
- **Source evidence:** CLAUDE.md:143: "Concept → Research → Write (+Suno Prompt) → [Refine] → QC/Verify → Generate → [Polish] → Master → Promo Videos (optional) → Promo Copy (optional) → **Release**". CLAUDE.md:145: "Human source verification is required before generation — never skip this gate." CLAUDE.md:175-180 "### Source Verification Gate": capture sources as clickable markdown links, save RESEARCH.md/SOURCES.md, `❌ Pending` → human verifies via `/bitwize-music:verify-sources` → `✅ Verified (DATE)`, "Block generation if verification incomplete — `/bitwize-music:pre-generation-check` enforces this". `skills/verify-sources/SKILL.md` and `skills/pre-generation-check/` implement the gate. README.md:4-5: "a Claude Code plugin that turns a conversation into a full album production pipeline" with "quality gates and source verification at every stage".
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (line refs corrected to 143/175-180).

## Claim 6: Genre library (388 files) and cross-platform matrix
- **Wiki says:** `genres/` holds 388 genre reference files; platform support spans macOS/Linux/WSL2/Windows with a compatibility matrix in `reference/`.
- **Source evidence:** `ls genres/ | wc -l` = 388 (includes `INDEX.md`). README.md:51 documents full support for macOS, Linux, WSL2, and native Windows with CI on windows-latest, and points to `reference/cross-platform/tool-compatibility-matrix.md`. `reference/` also contains `state-schema.md`, `model-strategy.md`, `mastering`, `suno`, `release`, `workflows`, `cloud`, `promotion`, `quick-start`, `sheet-music`, `terminology.md`, `distribution.md`, `streaming-mastering-specs.md`, `overrides`, `SKILL_INDEX.md`.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Python 3.11+ toolchain; Makefile lint/check; migrations and hooks
- **Wiki says:** Python 3.11+ (not 3.10+); `make lint` runs ruff + bandit + mypy; `make check` = lint + test; `migrations/` has 7 entries; `hooks/` has 6 entries.
- **Source evidence:** README.md:51: "Python 3.11+ for the MCP server and audio tools." Makefile:48 `lint:` runs `$(RUFF) check tools/ servers/ hooks/` + scoped PLW1514 ruff + `$(BANDIT) -r tools/ servers/ -ll -q -s B108,B608` + `$(MYPY)`; Makefile:62 `check: lint test`; `test:` runs pytest with `--cov-fail-under=75`. `migrations/` lists 7 entries (`0.40.0.md`, `0.43.0.md`, `0.44.0.md`, `0.59.0.md`, `0.90.0.md`, `0.91.0.md`, `README.md`). `hooks/` lists 6 entries (`README.md`, `check_version_sync.py`, `hooks.json`, `install.sh`, `pre-commit`, `validate_track.py`). CLAUDE.md:100-107 documents `get_pending_migrations` / `acknowledge_migrations` handling.
- **Verdict:** ✅ CORRECT
- **Fix needed:** Wiki corrected from Python 3.10+ → 3.11+.

## Related

- [[claude-ai-music-skills]] -- Main wiki entry
- [[claude-seo]] -- Claude SEO skill plugin
- [[ai-marketing-claude-code-skills]] -- AI marketing skills

## Cross-project

- [[claude-seo.codegraph-verify]] -- Claude SEO verification
- [[hermes-agent.codegraph-verify]] -- Hermes agent verification
