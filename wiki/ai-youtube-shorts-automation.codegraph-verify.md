---
name: ai-youtube-shorts-automation-codegraph-verify
tags: [youtube, shorts, automation, ollama, ffmpeg, python, video, wiki]
description: "Codegraph Verification: ai-youtube-shorts-automation — validating wiki claims against indexed source code symbols"
source: sources/ai-youtube-shorts-automation/
---

# Codegraph Verification: ai-youtube-shorts-automation

**Date:** 2026-07-30

## Claim 1: 100% free YouTube Shorts automation
- **Wiki says:** The system provides 100% free, fully autonomous YouTube Shorts creation and upload using free tools only: Ollama, edge-tts, FFmpeg, Pexels (+ Pixabay backup), YouTube Data API.
- **Source evidence:**
  - `README.md:3-4` header: "A **100% FREE**, fully autonomous YouTube Shorts creation and upload system. Runs locally on Windows with VS Code. No paid APIs needed."
  - `README.md:66-73` Free Tools table: Ollama + LLaMA 3 (Free), edge-tts (Free), FFmpeg (Free), Pexels API (Free, 200 req/hr), YouTube Data API (Free, 10K units/day)
  - `main.py:7` docstring: "100% FREE tools only"
- **Verdict:** ✅ CORRECT

## Claim 2: Full pipeline (trend discovery → Ollama script → edge-tts → Pexels → FFmpeg → YouTube upload)
- **Wiki says:** The pipeline runs: find trends → generate ideas via Ollama → write script → optimize hook → SEO metadata → AI voiceover (edge-tts) → stock footage (Pexels) → build video (FFmpeg) → upload to YouTube → track analytics.
- **Source evidence:**
  - `README.md:28-60` architecture diagram shows the 11-step pipeline: Trend Discovery → AI Idea Generator (Ollama) → Script Generator (Ollama) → Hook Optimizer (Ollama) → SEO Generator (Ollama) → Voice Generator (edge-tts) → Stock Footage (Pexels) → Video Builder (FFmpeg) → YouTube Upload → Analytics
  - `main.py:21-31` imports all pipeline modules: `trend_scraper` (get_all_trends), `ai_engine` (generate_viral_idea, generate_script, optimize_hook, generate_seo), `voice_generator`, `footage_fetcher`, `video_builder`, `youtube_upload`, `analytics_engine`
  - `modules/` contains all pipeline components plus `pixabay_fetcher.py`, `music_manager.py`, `script_quality.py`, `multi_channel.py`
- **Verdict:** ✅ CORRECT

## Claim 3: Ollama powers all AI generation
- **Wiki says:** Every AI text generation step (idea generation, script writing, hook optimization, SEO generation) is powered by local Ollama; trend discovery uses free non-AI sources (Reddit public JSON, HN API, Google Trends RSS).
- **Source evidence:**
  - `modules/ai_engine.py` handles all text generation (confirmed by main.py imports: generate_viral_idea, generate_script, optimize_hook, generate_seo)
  - `modules/trend_scraper.py:3-6` docstring: "Scrapes trending topics from multiple FREE sources: Reddit (no API key needed for public JSON), Hacker News (free API), Google Trends RSS (free)"
  - `README.md:35-44` architecture diagram shows Ollama powering Idea/Generator, Script, Hook Optimizer, SEO
- **Verdict:** ✅ CORRECT

## Claim 4: FFmpeg with Ken Burns (zoompan) + subtitles in 9:16
- **Wiki says:** FFmpeg builds vertical 9:16 videos with a Ken Burns zoom effect, clips, voice, subtitles, and thumbnail extraction.
- **Source evidence:**
  - `modules/video_builder.py:60` comment: "Adds slow zoom (Ken Burns effect) and fade transitions."
  - `modules/video_builder.py:65,68` build `zoompan` filters (`z='min(1.15,1+0.0003*on)'...` and reverse) at `VIDEO_WIDTH`×`VIDEO_HEIGHT`
  - `README.md:19` "Builds a vertical 9:16 video with FFmpeg (clips + voice + subtitles)"; `main.py:25` imports `build_final_video, extract_thumbnail, cleanup_temp_files`
- **Verdict:** ✅ CORRECT

## Claim 5: YouTube Data API v3 with OAuth 2.0 + pickle token persistence
- **Wiki says:** YouTube uploads use the YouTube Data API v3 with OAuth 2.0 authentication and pickle token persistence (`config/youtube_token.json`).
- **Source evidence:**
  - `modules/youtube_upload.py:10` comment: "Create OAuth 2.0 credentials (Desktop application)"
  - `modules/youtube_upload.py:17,49,76` import pickle, load saved token via `pickle.load`, persist via `pickle.dump`
  - `README.md:130-142` documents enabling YouTube Data API v3 and creating an OAuth client ID (Desktop app) saved as `config/client_secret.json`; `README.md:351` references `config/youtube_token.json`
- **Verdict:** ✅ CORRECT

## Claim 6: Windows-focused local setup (VS Code + .bat scripts)
- **Wiki says:** The project is set up for local Windows development — the README's setup guide targets Windows + VS Code and the repo ships only `.bat` setup scripts; it is not a cross-platform deployment story.
- **Source evidence:**
  - `README.md:4` "Runs locally on Windows with VS Code"; `README.md:77` "## Setup Guide (Windows + VS Code)"
  - `setup_windows.bat` and `setup_task_scheduler.bat` are the only setup scripts in the repo (verified via filesystem; `README.md:228-229` documents both)
  - `README.md:202-206` "### Auto-Run on Windows (Task Scheduler): `setup_task_scheduler.bat`" — creates a scheduled task that runs every 6 hours
- **Verdict:** ✅ CORRECT

## Claim 7: Extended modules — Pixabay backup footage, background music, script quality, multi-channel
- **Wiki says:** Beyond the core pipeline, the repo ships a Pixabay backup footage fetcher, a background music manager, a script quality checker, and a multi-channel manager.
- **Source evidence:**
  - `modules/pixabay_fetcher.py:3-5` docstring: "Backup Footage Fetcher - Pixabay API. Used when Pexels has no results or rate-limits you. Free: 100 requests/min, no watermark."
  - `modules/music_manager.py:3-5` docstring: "Background Music Manager. Auto-downloads free royalty-free background music from Pixabay. Also manages local music files in assets/music/ folder."; `README.md:310-319` documents auto-mixing at 8% volume (`BACKGROUND_MUSIC_VOLUME`)
  - `modules/script_quality.py:3-5` docstring: "Script Quality Checker. Validates and scores scripts before video creation."; `main.py:27` imports `validate_script, improve_script`
  - `modules/multi_channel.py` exists; `README.md:278-298` documents 5-channel operation
- **Verdict:** ✅ CORRECT

## Claim 8: Artifact layout — config/, assets/music/, output/, logs/
- **Wiki says:** The project lays out `config/` (settings, OAuth credentials, channels), `assets/music/` (background music), `output/` (generated videos), and `logs/` (automation logs + analytics data).
- **Source evidence:**
  - `README.md:234-260` project structure tree: `config/` (settings.py, client_secret.json), `assets/ └── music/` ("Put .mp3 files here for background music"), `output/` ("Generated videos"), `logs/` ("Automation logs + analytics data"), `utils/` (logger)
  - `main.py:19` imports `OUTPUT_DIR` from `config.settings`; `modules/music_manager.py:13` uses `ASSETS_DIR / "music"` from settings
- **Verdict:** ✅ CORRECT

## Summary

All 8 key claims from the ai-youtube-shorts-automation wiki have been verified against the source code:
- ✅ 100% free: Confirmed in README.md and main.py with free-only tools
- ✅ Full pipeline: All 11 pipeline steps confirmed in architecture diagram and module imports
- ✅ Ollama-powered AI + free trend sources: All text generation via Ollama; Reddit/HN/Google Trends confirmed
- ✅ FFmpeg 9:16 with Ken Burns zoompan + subtitles: zoompan filters confirmed in video_builder.py
- ✅ YouTube Data API v3 + OAuth 2.0 + pickle tokens: Authentication and token persistence confirmed
- ✅ Windows-focused setup: VS Code guide + .bat scripts only; no cross-platform claim
- ✅ Extended modules: pixabay_fetcher, music_manager, script_quality, multi_channel confirmed
- ✅ Artifact layout: config/, assets/music/, output/, logs/ documented in README structure

## Related

- [[ai-youtube-shorts-automation]] -- Main wiki entry

## Cross-project

- [[MoneyPrinterV2.codegraph-verify]] -- Similar automation project
