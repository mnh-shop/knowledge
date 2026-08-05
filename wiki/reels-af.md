---
name: reels-af
tags: [agentfield, ai-video, automation, cli, content-creation, ffmpeg, openrouter, python, social-media, wiki, reels-af]
description: "AI-native viral reel producer on AgentField — turns URL or topic into 1080x1920 vertical reel with karaoke subtitles in ~80 seconds"
source: sources/reels-af/
verification_date: 2026-07-30
verified_by: codegraph-verify
---

# Reels-AF — AI Viral Reel Producer

| Field | Value |
|---|---|
| **Origin** | [awesomelabs/reels-af](https://github.com/awesomelabs/reels-af) |
| **License** | Apache-2.0 |
| **Stack** | Python 3.10+, AgentField, OpenRouter, ffmpeg |
| **Deployment** | Docker Compose or CLI via `uv sync` |
| **Source** | `sources/reels-af/` |

## What is it?

An AI-native vertical reel producer built on [[agentfield]] that transforms a URL or topic into a complete 1080×1920 vertical video with karaoke-style subtitles in approximately 80 seconds. It handles the entire content pipeline — research, script writing, voiceover generation, video assembly, and subtitle synchronization.

Designed for rapid social media content creation, reels-af produces platform-ready reels optimized for TikTok, Instagram Reels, and YouTube Shorts.

The system runs **18 specialized reasoners** through the AgentField control plane to extract the essence of a source, write a Hook → Mechanism → Payoff script, hunt a viral angle (in topic mode), synthesize sample-accurate audio, plan beats and cards in parallel, generate per-beat first frames + motion, and stitch everything in a single ffmpeg pass. Every reasoner is a visible, individually re-runnable node in the control-plane DAG.

Two entry points, one downstream pipeline. Drop in a URL when you have a source; drop in a topic when you just have a thread to pull on.

## How It Works — Two Paths, Six Phases

Both paths converge on the same downstream after phase 02:

1. **Intake** — `article_to_reel` runs one harness call to extract the surprising claim + mechanism + evidence + content_mode. `topic_to_reel` fans out the **4-hunter cascade** (see below).
2. **Script** — one `.ai()` call produces a ScriptDraft (Hook → Mechanism → Payoff + inline TTS tags). A schema validator enforces the final clause to echo a hook keyword, creating the loop.
3. **Audio** — sentences synthesize in parallel, are ffprobe-measured, sped via `atempo=1.35`, then native-wave concatenated. Sentence boundaries are sample-accurate; words inside are distributed by syllable count. No ASR in the loop.
4. **Plan** — two parallel deterministic helpers (cards for subtitle layout, beats for visual planning) and two parallel LLM fan-outs (per-beat image prompts, per-beat optional accents). Cards and beats render onto the same reel but don't gate each other — no shot-too-long failures.
5. **Render** — one first-frame image per beat (Gemini Flash Image), then either local ken-burns animation (default) or a Veo i2v call per beat (`REEL_AF_USE_VEO=true`). Per-beat fallback: image fail → placeholder; Veo fail → ken-burns.
6. **Stitch** — one ffmpeg invocation: concat filter (sample-accurate) + libass burn (word-burst + accents) + AAC mux of the full TTS WAV. One encode, no priming drift.

The architectural choice that earns the engagement: **video is decoupled from word timing**. Cards drive subtitles, beats drive visuals, audio is master.

### Topic Mode: The Hunter Cascade

`topic_to_reel` runs an 8-node cascade before the shared downstream:

```
4 parallel hunters (12 candidates)
    │  hunt_specific_figure · hunt_reversal · hunt_temporal · hunt_cross_domain
    ▼
critic (pick_top_essences) → scores novelty / specificity / hookability / narratability → top 3
    ▼
3 parallel narrators (write_narrations) → delayed-reveal scripts
    ▼
pairwise judge (pick_best_narration) → winner → shared downstream
```

- **4 hunters × 3 candidates = 12 candidate essences** — each hunter is angle-constrained: `specific_figure` (named person), `reversal` (common interpretation backwards), `temporal` (a specific year/event), `cross_domain` (unexpected field bridge).
- **Critic** ranks all 12 on novelty / specificity / hookability / narratability, picking the top 3 while preferring angle diversity when scores are close.
- **3 narrators** write delayed-reveal scripts (tease → common_belief → reveal → payoff) in parallel.
- **Pairwise judge** picks the most viral script, returning a composite score and rationale.

The topic path runs 18 reasoners total (vs 10 for the article path), which is why it's slightly slower (~85-110s) and slightly pricier (~$0.10) than the article path (~70-90s, ~$0.08).

### The 18 Reasoners

| Group | Reasoners |
|---|---|
| **Entry** | `reel_article_to_reel`, `reel_topic_to_reel` |
| **Article-only** | `extract_essence`, `compose_script` |
| **Topic-only** | `hunt_specific_figure`, `hunt_reversal`, `hunt_temporal`, `hunt_cross_domain`, `pick_top_essences`, `write_narrations`, `pick_best_narration` |
| **Shared downstream** | `synthesize_audio`, `pack_cards`, `plan_beats`, `plan_visuals`, `plan_accents`, `generate_videos`, `stitch_reel` |

## Key Features

- **80-Second Production:** Complete reel from topic/URL to rendered video in roughly 80 seconds (topic path 85-110s).
- **URL or Topic Input:** Drop a URL for research-based content or a plain topic for creative scripts.
- **Hunter Cascade (topic mode):** 4 angle-constrained hunters → critic → 3 narrators → pairwise judge.
- **Karaoke Subtitles:** Word-level synchronized subtitle rendering (one word at a time, 170px, bottom-center, libass) for engaging viewing experience.
- **Optional Editorial Accents:** UPPERCASE callouts for numbers, names, jargon glosses (6 patterns: number / named_entity / jargon_translation / hook_title_card / reaction / list_marker).
- **1080×1920 Vertical Format:** Optimized for TikTok, Instagram Reels, and YouTube Shorts.
- **AI Research + Scripting:** Uses OpenRouter (multi-model access) for content research and script generation — one env var swaps the whole model stack.
- **Veo 3.1 Lite i2v Upgrade:** Optional full-motion video via `REEL_AF_USE_VEO=true` (~$1.20/reel); ken-burns is the free default.
- **AgentField Orchestration:** Runs as an AgentField harness, with the 18-reasoner DAG rendered live in the control-plane UI.
- **ffmpeg Video Assembly:** Single-pass concat + libass burn + AAC mux; sample-accurate, no per-shot priming drift.
- **Two-Tier Per-Beat Fallback:** image fail → placeholder + ken-burns; Veo fail → real first-frame + ken-burns. A single beat failure never crashes the reel.
- **Zero Manual Editing:** Fully automated pipeline from idea to rendered video.

## Output

**Every reel:**

- **`reel.mp4`** — 1080×1920 vertical, **20-25s, H.264 + AAC**, ready to upload
- **Word-burst karaoke** — one word at a time, 170px bottom-center, sample-accurate
- **Per-beat first frames** — Gemini Flash Image stills, content-mode-aware style
- **Motion** — ken-burns by default (free); Veo 3.1 Lite i2v when `REEL_AF_USE_VEO=true`
- **Optional editorial accents** — UPPERCASE callouts for numbers, names, jargon glosses

**`result.json` sidecar** (next to `reel.mp4` under `./output/<run-id>/`):

- `video_path`, `duration_s`, `beat_count`, `card_count`, `accent_count`
- `hook` / `hook_variant`, `content_mode`, `domain`, `voice_id`
- **Topic runs additionally:** `tease`, `reveal`, `payoff`, `open_style`, `chosen_essence` (with `core_claim`, `angle`, `novelty_pitch`), `winner_composite`, `winner_why`, `all_candidates`, `all_narrations`
- **`timings_s`** — per-phase wall times: `hunt`, `critic`, `narrate`, `judge`, `tts`, `plan`, `visual_accent`, `media`, `stitch`, `total`

## Cost and Timing

Default config — ken-burns motion from generated first frames, OpenRouter list prices verified 2026-05:

| Path | Reasoners | Wall time | Cost / reel |
|---|---|---|---|
| `article_to_reel` (URL → reel) | 10 | ~70-90s | **~$0.08** |
| `topic_to_reel` (topic → reel) | 18 | ~85-110s | **~$0.10** |

Cost split per reel: Gemini 2.5 Flash Image first frames ~$0.02, Gemini 3.1 Flash TTS ~$0.015, DeepSeek V4 Pro reasoning ~$0.02, ken-burns motion free.

**Upgrade to full Veo i2v motion** by setting `REEL_AF_USE_VEO=true`. Veo 3.1 Lite at $0.05/sec adds ~$1.10/reel (5 beats × ~6s of generated video), bringing the total to **~$1.20/reel**.

Track actual numbers via the OpenRouter activity dashboard and the `timings_s` block in `result.json`.

## Tech Stack

| Component | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **Agent Framework** | AgentField SDK |
| **AI Models** | OpenRouter (multi-provider): DeepSeek V4 Pro reasoning, Gemini 3.1 Flash TTS, Gemini 2.5 Flash Image, Veo 3.1 Lite |
| **Video Processing** | ffmpeg (`zoompan` / `concat` / `atempo`), libass + pysubs2 |
| **Article Extraction** | readability-lxml |
| **Deployment** | Docker Compose, uv sync |

## Deployment

### Docker Compose

```bash
git clone https://github.com/awesomelabs/reels-af.git
cd reels-af
cp .env.example .env       # paste OPENROUTER_API_KEY
docker compose up --build
```

Open **http://localhost:8080/ui/** to watch the 18-reasoner DAG execute live. Outputs land under `./output/<run-id>/reel.mp4` with a `result.json` sidecar.

### CLI (uv sync)

```bash
uv sync
cp .env.example .env

uv run reel-af article "https://arxiv.org/abs/2509.25541"
uv run reel-af topic   "the placebo effect"
```

The CLI (`reel-af` from `[project.scripts]`, backed by `reel_af.cli:main`) submits to the AgentField control plane at `http://localhost:8080` by default. Use `--server` if your control plane is exposed elsewhere. A second binary, `reel-af-server`, runs the reasoner server itself.

### AgentField One-Call DX (`af` CLI, requires af ≥ 0.1.87)

```bash
# URL → reel
af call reel-af.reel_article_to_reel --in '{"url": "https://arxiv.org/abs/2509.25541"}'

# Topic → reel (runs the 4-hunter → critic → 3-narrator → judge cascade)
af call reel-af.reel_topic_to_reel --in '{"topic": "the placebo effect"}'
```

Prefer raw HTTP? Hit the API directly with curl:

```bash
curl -X POST http://localhost:8080/api/v1/execute/async/reel-af.reel_topic_to_reel \
  -H "Content-Type: application/json" \
  -d '{"input": {"topic": "the placebo effect"}}'
```

## Configuration

Most behaviour is driven by environment variables; see `.env.example` for the full list.

| Env var | Default | What it controls |
|---|---|---|
| `OPENROUTER_API_KEY` | — | Required. Get one at openrouter.ai and load $5+ in credits (~50 reels at default config). |
| `REEL_AF_USE_VEO` | `false` | Set to `true` for Veo 3.1 Lite i2v motion (~$1.10 extra per reel). Default ken-burns mode animates the generated stills locally. |
| `REEL_AF_MODEL` | `openrouter/deepseek/deepseek-v4-pro` | Reasoning model for every `.ai()` call. Any OpenRouter model works. |
| `REEL_AF_TTS_MODEL` | `google/gemini-3.1-flash-tts-preview` | TTS model. Gemini Flash is the only one supporting inline audio tags. |
| `REEL_AF_IMAGE_MODEL` | `openrouter/google/gemini-2.5-flash-image` | First-frame image generator. Swap for Flux, Imagen, etc. |
| `REEL_AF_VIDEO_MODEL` | `openrouter/google/veo-3.1-lite` | Veo model used when `REEL_AF_USE_VEO=true`. |
| `REEL_AF_API_BASE` | OpenRouter (`https://openrouter.ai/api/v1`) | Base URL for reasoning `.ai()` calls (advanced: local vLLM / Ollama / custom gateway). Empty = OpenRouter. |
| `REEL_AF_API_KEY` | falls back to `OPENROUTER_API_KEY` | Key sent to the reasoning endpoint. |
| `AGENT_NODE_ID` | `reel-af` | Node id registered with the AgentField control plane. |
| `AGENTFIELD_SERVER` | `http://localhost:8080` | Control-plane URL (Docker compose wires this automatically). |
| `AGENTFIELD_LLM_CALL_TIMEOUT` | `120` | Per-call timeout in seconds. |

**Bring your own model (advanced):** point reasoning at any OpenAI-compatible endpoint without touching code:

```bash
REEL_AF_MODEL=openai/your-model-id          # how your endpoint names the model
REEL_AF_API_BASE=http://localhost:8000/v1   # your OpenAI-compatible base URL
REEL_AF_API_KEY=sk-local-or-anything        # your endpoint's key
```

Use the `openai/` prefix for OpenAI-compatible servers so the request is shaped correctly. Media (TTS/image/video) still routes through OpenRouter, so keep `OPENROUTER_API_KEY` set.

Voice, pacing, and tone are picked in code (`render/tts.py:_VOICE_BY_TONE` and the `_AUDIO_SPEED_FACTOR` constant).

## Related

- [[agentfield]] — The AgentField platform reels-af runs on
- [[pr-af]] — Code review system on AgentField (same harness pattern)
- [[af-deep-research]] — Deep research agent on AgentField
- [[SWE-AF]] — SWE-bench agent on AgentField
- [[hermes-agent]] — MCP hub that can orchestrate reels-af as a tool
- [[hyperframes]] — HTML-to-video rendering framework (complementary video tech)
