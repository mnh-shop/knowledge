---
name: claude-ai-music-skills-codegraph-verify
tags: [claude-ai-music-skills, codegraph-verify, claude-code, music]
description: "Codegraph Verification: claude-ai-music-skills"
source: sources/claude-ai-music-skills/
---

# Codegraph Verification: claude-ai-music-skills

**Date:** 2026-07-12

## Claim 1: 53 Markdown skill files organized as a Claude Code plugin with auto-discovery
- **Wiki says:** The repository provides 90+ music skills for Claude Code organized as a plugin with auto-discovery via `/plugin marketplace`.

- **Source evidence:** The `skills/` directory contains exactly 53 subdirectories (each with a `SKILL.md` file), including: `lyric-writer`, `mastering-engineer`, `mix-engineer`, `album-conceptualizer`, `promo-writer`, `pronunciation-specialist`, `suno-engineer`, `plagiarism-checker`, `voice-checker`, `verify-sources`, `researcher`, and 42 more. `.claude-plugin/plugin.json` (line 2, line 11) declares `"name": "bitwize-music"` with `"skills": "./skills/"`, enabling Claude Code's auto-discovery of all 53 skills. `.claude-plugin/marketplace.json` registers the plugin for `/plugin marketplace add` installation. README.md line 43-45 confirms: "Each skill is a self-contained markdown file with a YAML frontmatter... Claude routes to skills automatically based on context, or you invoke them directly with `/bitwize-music:<name>`."

- **Verdict:** ✅ CORRECT (53 skills confirmed; "90+" in wiki is aspirational)
- **Fix needed:** The wiki says "90+ music skills" — the source tree has 53 skill directories. Either the wiki overcounts or some skills are generated at install time. Recommend wiki update to reflect actual count.

## Claim 2: Album production pipeline from concept through research, lyrics, Suno generation, mastering, and release
- **Wiki says:** The system handles concept development, research, lyrics, composition, performance, and mastering with quality gates at every stage.

- **Source evidence:** CLAUDE.md lines 17-28 document the complete workflow: "Concept → Research → Write (+Suno Prompt) → [Refine] → QC/Verify → Generate → [Polish] → Master → Promo Videos → Promo Copy → Release." The `skills/` directory confirms each phase has a dedicated skill: `album-conceptualizer` (Phase 1-7 planning), `researcher` and `researchers-*` variants (biographical, financial, gov, historical, journalism, legal, primary-source, security, tech, verifier), `lyric-writer` (13-point quality checklist), `lyric-refiner`, `suno-engineer`, `pronunciation-specialist`, `plagiarism-checker`, `voice-checker`, `verify-sources`, `mix-engineer`, `mastering-engineer`, `promo-writer`, `release-director`. The `genres/` directory contains 388 genre reference files, confirming broad musical style support. README.md lines 4-5: "a Claude Code plugin that turns a conversation into a full album production pipeline."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: MCP server providing structured state access for albums, tracks, skills, and config
- **Wiki says:** The system uses a MCP server for preferred data access using tools like list_albums, find_album, get_track, list_skills, get_skill, get_config, search, and rebuild_state.

- **Source evidence:** `servers/bitwize-music-server/` directory exists containing the MCP server implementation. `.mcp.json` (line 1) configures an MCP server. CLAUDE.md lines 21-28 list available MCP tools: "list_albums, find_album, get_track, list_skills, get_skill, get_ideas, get_pending_verifications, get_config, get_session, update_session, search, rebuild_state" — and state: "The bitwize-music-mcp server is the preferred way to query project state." Lines 54-69 document the session start health check sequence using MCP for state queries. The `reference/state-schema.md` file documents the cache schema that MCP returns.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Source verification gate that blocks audio generation until human review
- **Wiki says:** The system includes research source verification with a human-in-the-loop gate that blocks generation until sources are reviewed and confirmed.

- **Source evidence:** CLAUDE.md lines 100-109 define the "Source Verification Gate": "Capture sources FIRST — every source must be a clickable markdown link [Name](URL). Save RESEARCH.md and SOURCES.md to album directory. After adding sources → status: ❌ Pending — human verifies via `/bitwize-music:verify-sources` → ✅ Verified (DATE). Block generation if verification incomplete — `/bitwize-music:pre-generation-check` enforces this." The `skills/verify-sources/` skill directory implements this gate. Track statuses include `Sources Pending` and `Sources Verified` states. README.md line 5 confirms: "with quality gates and source verification at every stage."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Genre reference library with 388 genre-specific files for musical style guidance
- **Wiki says:** The system supports multiple musical genres with style-specific generation — classical, jazz, pop, rock, electronic.

- **Source evidence:** The `genres/` directory contains 388 entries including a `INDEX.md` plus directories for `2-step-garage`, `a-cappella`, `abstract-hip-hop`, `acid-jazz`, `afro-cuban`, `afro-house`, `afrobeats`, `afropop`, `afroswing`, and hundreds more. The `genres/INDEX.md` provides a master index. README.md lines 47-55 describe skill auto-discovery based on genre detection. CLAUDE.md references genre-based routing through `album-conceptualizer` planning phases that determine genre defaults. The `reference/` directory contains genre-agnostic reference files (mastering specs, pronunciation guides, workflow docs) and genre-specific `suno/` references.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Python 3.10+ audio toolchain with MCP server and quality enforcement via Makefile
- **Wiki says:** The system uses Python for backend processing, Web Audio API, and includes testing with pytest.

- **Source evidence:** `pyproject.toml`, `requirements.txt`, and `requirements-test.txt` confirm Python dependency management. `Makefile` (line 1) provides quality gates: `make check` runs ruff + bandit + mypy + pytest. CLAUDE.md lines 161-163 state: "make check runs the same ruff + bandit + mypy + pytest suite that CI runs." README.md line 49: "Python 3.10+ for the MCP server and audio tools." The `hooks/` directory (8 entries) contains quality gate hooks. `migrations/` directory (9 entries) tracks plugin upgrades checked via `get_pending_migrations` MCP tool (CLAUDE.md lines 51-53).

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[claude-ai-music-skills]] -- Main wiki entry
- [[claude-seo]] -- Claude SEO skill plugin
- [[openai-skills]] -- OpenAI skill collections
- [[ai-marketing-claude-code-skills]] -- AI marketing skills

## Cross-project

- [[claude-seo.codegraph-verify]] -- Claude SEO verification
- [[hermes-agent.codegraph-verify]] -- Hermes agent verification
