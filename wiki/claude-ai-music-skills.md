---
name: claude-ai-music-skills
tags: [claude-ai-music-skills, agent, skill, music, ai-llm, automation, cli, python, mcp]
description: "Claude AI Music Skills: Suno-based album production pipeline for Claude Code with 53 skills and multi-model tier orchestration"
source: sources/claude-ai-music-skills/
verification_date: 2026-07-12
verified_by: codegraph-verify
updated: 2026-07-30
---

# Claude AI Music Skills

## Project Overview

**Claude AI Music Skills** (bitwize-music) is a Claude Code plugin from the **bitwize-music-studio** org that turns a conversation into a full album production pipeline: concept → research → lyrics → Suno generation → mastering → release. It ships **53 skills**, a **388-genre reference library**, and an **MCP server** (bitwize-music-mcp, stdio) that provides structured access to project state. Current plugin version: **0.101.0** (2026-07-21).

## What it is

Claude AI Music Skills is an AI music generation workflow for [Suno](https://suno.com). Skills contain domain expertise; `CLAUDE.md` contains workflow rules and structure that apply every session. Instead of a general "music creation suite," this is a focused production system: it manages albums end-to-end — from idea and concept planning through research, lyric writing with Suno-specific pronunciation handling, track generation, mixing/mastering, promo assets, and release.

## Architecture

### Core Components

| Component | Purpose | Key Features |
|-----------|---------|-------------|
| **53 Skills** | Domain-expertise markdown skills | Auto-discovered by Claude Code; invoked as `/bitwize-music:<name>` |
| **Multi-Model Orchestration** | Model-tier routing | Opus 4.8 (creative) / Sonnet 4.6 (reasoning) / Haiku 4.5 (mechanical) |
| **MCP Server** | Structured project-state access | `servers/bitwize-music-server/`, stdio, 80+ tools |
| **Genre Library** | Musical style reference | 388 genre files in `genres/` |
| **State Cache + Migrations** | Persistent project state | `migrations/` (7 entries) tracks plugin upgrades |
| **Quality Gates** | Workflow enforcement | `hooks/` (6 entries), source verification gate |

The technology stack is **Python + Markdown + shell** — no TypeScript, no Web Audio API, no AudioWorklet, no IndexedDB/SQLite, and no HTTP/WebSocket server. The MCP server speaks stdio only. The Makefile drives linting/testing (ruff + bandit + mypy + pytest); Python 3.11+ is required for the MCP server and audio tools (README.md:51).

### Multi-Model Tier Orchestration (headline feature)

Skills declare which Claude model they need, and the tier is enforced by the plugin (README.md:66-75):

| Tier | Model | Skills | Rationale |
|------|-------|--------|-----------|
| Creative | Opus 4.8 | 7 | Lyrics, Suno prompts, album concepts, legal/verification research — output quality defines the music |
| Reasoning | Sonnet 4.6 | 30 | Research coordination, pronunciation analysis, most workflows |
| Mechanical | Haiku 4.5 | 16 | Imports, validation, clipboard, help — speed over creativity |

Skills use tier aliases (`opus`/`sonnet`/`haiku`) that auto-track the frontier model (CLAUDE.md:109). Per-skill rationale lives in `reference/model-strategy.md`.

### MCP Server

`servers/bitwize-music-server/` implements the MCP server (Python, `run.py`/`server.py` + `handlers/`, launched via `mcp-launch`). `.mcp.json` registers `bitwize-music-mcp` as a **stdio** server:

```json
{
  "mcpServers": {
    "bitwize-music-mcp": {
      "type": "stdio",
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/bitwize-music-server/mcp-launch"
    }
  }
}
```

The MCP server is the **preferred way to query project state** (CLAUDE.md:52-62): `list_albums`, `find_album`, `get_track`, `list_skills`, `get_skill`, `get_ideas`, `get_pending_verifications`, `get_config`, `get_session`, `update_session`, `search`, `rebuild_state`. The cache schema is documented in `reference/state-schema.md`. The server exposes 80+ tools (README.md:77 "MCP Server (80+ Tools)").

## Album Production Pipeline

The core workflow (CLAUDE.md:143):

```
Concept → Research → Write (+Suno Prompt) → [Refine] → QC/Verify → Generate → [Polish] → Master → Promo Videos (optional) → Promo Copy (optional) → Release
```

Each phase maps to dedicated skills:

- **Concept** — `album-conceptualizer` (Phase 1-7 planning), `album-ideas`, `promote-idea`
- **Research** — `researcher` plus 10 specializations (`researchers-biographical`, `researchers-financial`, `researchers-gov`, `researchers-historical`, `researchers-journalism`, `researchers-legal`, `researchers-primary-source`, `researchers-security`, `researchers-tech`, `researchers-verifier`); `document-hunter`
- **Lyrics** — `lyric-writer` (prosody rules, rhyme schemes, Suno pronunciation quirks), `lyric-refiner`, `lyric-reviewer`, `pronunciation-specialist`, `explicit-checker`, `plagiarism-checker`, `voice-checker`
- **Suno generation** — `suno-engineer` (style boxes, Suno prompt engineering)
- **Polish/Master** — `mix-engineer`, `mastering-engineer` (loudness targets per platform, genre-specific EQ curves), `sheet-music-publisher`
- **Release** — `promo-writer`, `promo-director`, `promo-reviewer`, `release-director`

Track statuses flow `Not Started → Sources Pending → Sources Verified → In Progress → Generated → Final`; album statuses flow `Concept → Research Complete → Sources Verified → In Progress → Complete → Released` (CLAUDE.md:185-209). An album advances only when ALL its tracks reach the corresponding level.

## Source Verification Gate

Human-in-the-loop research verification blocks generation (CLAUDE.md:175-180):

1. Capture sources FIRST — every source must be a clickable markdown link `[Name](URL)`
2. Save RESEARCH.md and SOURCES.md to the album directory
3. After adding sources → status `❌ Pending` → human verifies via `/bitwize-music:verify-sources` → `✅ Verified (DATE)`
4. Generation is blocked if verification is incomplete — `/bitwize-music:pre-generation-check` enforces this

"Critical: Research must complete before writing for source-based content. Human source verification is required before generation — never skip this gate." (CLAUDE.md:145)

## Genre Library

`genres/` contains **388 genre reference files** (including `INDEX.md`), covering styles from `2-step-garage`, `a-cappella`, `abstract-hip-hop`, `acid-jazz`, `afro-house`, `afrobeats` through `zouk` and hundreds more. These files provide genre-specific guidance for Suno prompts, mastering targets, and stylistic defaults used during album conceptualization.

## Toolchain & Quality Gates

- **Python 3.11+** for the MCP server and audio tools (README.md:51)
- **Makefile**: `make lint` runs ruff (scoped to tools/, servers/, hooks/) + bandit + mypy; `make check` = lint + test (pytest with coverage, `--cov-fail-under=75`); `make test` runs the pytest suite with `-n auto`
- **Hooks** (`hooks/`, 6 entries): `hooks.json` (PostToolUse), `check_version_sync.py`, `validate_track.py`, `pre-commit`, `install.sh`, `README.md`
- **Migrations** (`migrations/`, 7 entries): `0.40.0.md` → `0.91.0.md` + README; checked via the `get_pending_migrations` MCP tool; `acknowledge_migrations` advances `last_migrated_version`
- **Cross-platform matrix**: `reference/cross-platform/tool-compatibility-matrix.md` + `wsl-setup-guide.md`; macOS, Linux, WSL2, and native Windows fully supported (CI runs on windows-latest, README.md:51)
- **Session start health check**: `/bitwize-music:session-start` runs the health-check sequence (venv stale check, skills stale check, MCP state check, pending migrations) before work begins

## Key Skills

- **`lyric-writer`** — prosody rules, rhyme-scheme analysis, Suno pronunciation quirks
- **`mastering-engineer`** — loudness targets per platform, genre-specific EQ curves
- **`researcher`** — coordinates parallel sub-agents across 10 domain specializations
- **`suno-engineer`** — Suno prompt/style-box expertise (usually auto-invoked by lyric-writer)
- **`album-conceptualizer`** — Phase 1-7 album planning
- **`mix-engineer`** — audio polishing and Suno artifact fixes
- **`verify-sources`** / **`pre-generation-check`** — human verification gate enforcement
- **`genre-creator`** — adds new genre reference files
- **`sheet-music-publisher`** — MuseScore PDF export (CI-verified on windows-latest)

## Configuration

- **Config is always at** `~/.bitwize-music/config.yaml` (CLAUDE.md:26)
- Setup via `/bitwize-music:setup` (detects environment, installs dependencies) and `/bitwize-music:configure` (artist name, workspace paths)
- Workspace layout: `{audio_root}/artists/[artist]/albums/[genre]/[album]/` for mastered audio

## Version History

- **[0.101.0] — 2026-07-21** (CHANGELOG.md:9) — current release
- Migration files track the upgrade path from **0.40.0** through **0.91.0**

## License & Origin

- **Origin:** [bitwize-music-studio/claude-ai-music-skills](https://github.com/bitwize-music-studio/claude-ai-music-skills) (plugin.json repository field + README marketplace badges)
- **License:** CC0-1.0 (plugin.json)

---

*This wiki entry is generated from the source repository and follows the Claude AI Music Skills project's documentation standards.*

---

**Last Updated:** 2026-07-30
**Verification:** Source code verified against `sources/claude-ai-music-skills/`
**Version:** 0.101.0
