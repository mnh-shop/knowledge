---
name: reels-af-codegraph-verify
tags: [reels-af, reels, agentfield, video, ai, openrouter, python, ffmpeg, wiki]
description: "Codegraph Verification: reels-af — validating wiki claims against indexed source code symbols"
source: sources/reels-af/
---

# Codegraph Verification: reels-af

**Date:** 2026-07-30

## Claim 1: Apache-2.0 license
- **Wiki says:** REELS-AF is licensed under Apache-2.0.
- **Source evidence:**
  - `README.md` line 7 shows the Apache 2.0 badge: `[![Apache 2.0](.../badge/License-Apache%202.0-16a34a...)](LICENSE)`
  - `README.md` line 351 states: "Apache License 2.0 — see [LICENSE](./LICENSE)"
  - `pyproject.toml` line 9: `license = { text = "Apache-2.0" }`
- **Verdict:** ✅ CORRECT (wiki previously said "Not specified" — fixed)
- **Fix needed:** None (already applied)

## Claim 2: AI-native viral reel producer on AgentField, ~80s at ~$0.10 via OpenRouter
- **Wiki says:** REELS-AF is an AI-native viral reel producer built on the AgentField framework that produces a 1080×1920 vertical reel in about 80 seconds at approximately $0.10 per reel using OpenRouter.
- **Source evidence:**
  - `README.md` line 5 states: "### AI-Native Viral Reel Producer Built on [AgentField](https://github.com/Agent-Field/agentfield)"
  - `README.md` line 24 states: "Article URL or topic phrase → 1080×1920 vertical reel with word-burst karaoke, in about 80 seconds at **≈$0.10 per reel**"
  - `README.md` line 162: topic path `~$0.10`; line 161: article path `~$0.08`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Dual entry paths article_to_reel + topic_to_reel with entry reasoner names
- **Wiki says:** Provides two entry paths — `article_to_reel` (from URL) and `topic_to_reel` (from topic string) — registered under the control-plane names `reel-af.reel_article_to_reel` and `reel-af.reel_topic_to_reel`.
- **Source evidence:**
  - `src/reel_af/app.py` line 379 defines `async def article_to_reel(url: str, ...)`
  - `src/reel_af/app.py` line 457 defines `async def topic_to_reel(topic: str, ...)`
  - `src/reel_af/app.py` lines 6-11 document both entry points feeding the shared downstream
  - `src/reel_af/app.py` line 83: `reel = AgentRouter(prefix="reel", ...)` → control-plane names `reel_article_to_reel` / `reel_topic_to_reel`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (line drift 378→379 corrected)

## Claim 4: Topic-mode hunter cascade — 4 hunters → critic → 3 narrators → judge
- **Wiki says:** Topic mode runs a cascade of 4 parallel hunters (specific_figure, reversal, temporal, cross_domain) producing 12 candidates, a critic that picks the top 3, 3 parallel narrators, and a pairwise judge — 18 reasoners total.
- **Source evidence:**
  - `src/reel_af/app.py` lines 493-498: `asyncio.gather` over `reel_hunt_specific_figure`, `reel_hunt_reversal`, `reel_hunt_temporal`, `reel_hunt_cross_domain`
  - `src/reel_af/app.py` lines 504-513: critic `reel_pick_top_essences` with `n_top=3`
  - `src/reel_af/app.py` lines 515-522: `reel_write_narrations` (3 parallel narrators)
  - `src/reel_af/app.py` lines 524-532: `reel_pick_best_narration` (pairwise judge)
  - `README.md` line 185 documents the full cascade; line 145 confirms "18 reasoners per reel; depth-3 DAG (4 hunters → critic → 3 narrators → judge → 6 downstream phases)"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Shared downstream pipeline with parallel stages
- **Wiki says:** Both entry paths feed into a shared downstream pipeline with parallel stages for audio, visuals, and accents.
- **Source evidence:**
  - `src/reel_af/app.py` line 607 defines `async def _render_downstream(...)` with comment: "Used by both entry points"
  - `src/reel_af/app.py` lines 617-618 document the parallel stages: "audio → cards/beats (parallel) → visuals/accents (parallel) → videos → stitch"
  - `src/reel_af/app.py` lines 630-641: `asyncio.gather` over `reel_pack_cards` ∥ `reel_plan_beats`; lines 646-659: `reel_plan_visuals` ∥ `reel_plan_accents`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Pydantic models with extra='forbid' + loop-back narrative validation
- **Wiki says:** All schemas use Pydantic with `extra="forbid"` for strict structured-output compatibility, and a loop-back validator enforces that the narration's closing references the hook.
- **Source evidence:**
  - `src/reel_af/models.py` line 17 states: "All schemas use ``extra="forbid"`` so OpenAI / Bedrock strict structured-output modes accept them"
  - `src/reel_af/models.py` line 39 (`Essence`), line 97 (`ScriptDraft`), line 193 (`WordTiming`), line 212 (`Card`), line 237 (`Beat`), line 275 (`BeatVisual`), line 314 (`AccentOverlay`), line 356 (`EssenceCandidate`), line 411 (`RankedCandidate`), line 424 (`CriticOutput`), line 457 (`ConversationalScript`), line 522 (`PairwiseVerdict`) all set `model_config = ConfigDict(extra="forbid")`
  - `src/reel_af/models.py` lines 147-149 define `_loop_back_check`: `@field_validator("narration")` (147), `@classmethod` (148), `def _loop_back_check` (149), implementing "Require the longest non-stopword from the hook (≥4 chars) to appear in the final 12 words" (lines 150-155, 174-182)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (line drift 147→149 corrected)

## Claim 7: Sample-accurate word timings with ffmpeg + output spec
- **Wiki says:** Audio is produced with sample-accurate word timings using ffmpeg for measurement and assembly; output is a 20-25s H.264+AAC `reel.mp4` with a `result.json` sidecar.
- **Source evidence:**
  - `src/reel_af/app.py` line 222 documents: "Sentence-by-sentence TTS + sample-accurate word timings"
  - `src/reel_af/app.py` lines 224-228 describe: "sped-up via ffmpeg `atempo` (preserves pitch), measured with ffprobe, then native-wave concatenated"
  - `README.md` line 66: "**`reel.mp4`** — 1080×1920 vertical, 20-25s, H.264 + AAC, ready to upload"
  - `README.md` line 71: "**`result.json`** — hook variant, beats, voice, hunter rankings, judge verdict, per-phase timings"
  - `src/reel_af/app.py` lines 592-598: `topic_to_reel` returns `chosen_essence`, `winner_composite`, `winner_why`, `all_candidates`, `all_narrations`, `timings_s`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: CLI invocation, af one-call DX, and environment variables
- **Wiki says:** The CLI binary is `reel-af` invoked as `uv run reel-af topic "..."` / `uv run reel-af article "URL"`; the `af` CLI one-call uses `af call reel-af.reel_article_to_reel`; env vars are `OPENROUTER_API_KEY`, `REEL_AF_USE_VEO`, `REEL_AF_MODEL`, `REEL_AF_TTS_MODEL`, `REEL_AF_IMAGE_MODEL`, `REEL_AF_VIDEO_MODEL`, `REEL_AF_API_BASE`, `REEL_AF_API_KEY` (no `REELS_OUTPUT_DIR` exists).
- **Source evidence:**
  - `pyproject.toml` lines 33-35: `[project.scripts]` defines `reel-af = "reel_af.cli:main"` and `reel-af-server = "reel_af.app:main"`
  - `README.md` lines 210-215: `reel-af article "https://arxiv.org/abs/2509.25541"` / `reel-af topic "the placebo effect"`
  - `README.md` lines 36-39: `af call reel-af.reel_article_to_reel --in '{...}'` / `af call reel-af.reel_topic_to_reel --in '{...}'` (requires af ≥ 0.1.87)
  - `README.md` lines 249-260: env var table lists `OPENROUTER_API_KEY`, `REEL_AF_USE_VEO`, `REEL_AF_MODEL`, `REEL_AF_TTS_MODEL`, `REEL_AF_IMAGE_MODEL`, `REEL_AF_VIDEO_MODEL`, `AGENT_NODE_ID`, `AGENTFIELD_SERVER`, `AGENTFIELD_LLM_CALL_TIMEOUT`
  - `README.md` lines 277-281: `REEL_AF_API_BASE` and `REEL_AF_API_KEY` for bring-your-own-endpoint
  - `src/reel_af/app.py` lines 68-77 read `REEL_AF_MODEL`, `REEL_AF_API_KEY`, `REEL_AF_API_BASE`, `OPENROUTER_API_KEY`; no `REELS_OUTPUT_DIR` anywhere in the codebase
- **Verdict:** ✅ CORRECT (wiki previously claimed a non-existent `reels-af --topic` binary/flag and `REELS_OUTPUT_DIR` — fixed)
- **Fix needed:** None (already applied)

## Summary

All 8 key claims from the reels-af wiki have been verified against the source code:
- ✅ Apache-2.0: README badge + pyproject.toml license field confirm
- ✅ AgentField producer, ~80s at ~$0.10: README claims confirmed
- ✅ Dual entry paths: article_to_reel (app.py:379) and topic_to_reel (app.py:457) confirmed
- ✅ Topic hunter cascade: 4 hunters → critic → 3 narrators → judge confirmed in app.py
- ✅ Shared downstream: _render_downstream with parallel stages confirmed
- ✅ Pydantic extra='forbid' + loop-back validation: models.py confirmed
- ✅ Sample-accurate word timings + output spec: app.py + README confirmed
- ✅ CLI/env vars: reel-af binary, af one-call, and full env-var list confirmed; no REELS_OUTPUT_DIR

## Related

- [[reels-af]] -- Main wiki entry

## Cross-project

- [[agentfield.codegraph-verify]] -- Similar codegraph verification for AgentField
- [[pr-af.codegraph-verify]] -- Similar codegraph verification for PR-AF
