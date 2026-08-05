---
name: ai-youtube-shorts-automation
tags: [youtube, shorts, automation, ai, video, content-creation, python, ollama, ffmpeg, edge-tts]
description: "Free, fully autonomous YouTube Shorts creation and upload system — trend discovery, AI script generation, voiceover, video assembly, and auto-upload, with Windows-local setup"
source: sources/ai-youtube-shorts-automation/
verification_date: 2026-07-30
verified_by: codegraph-verify
---

# ai-youtube-shorts-automation

**Source:** `sources/ai-youtube-shorts-automation/`

A 100% free, fully autonomous YouTube Shorts creation and upload system. No paid APIs needed — every component uses free tiers: Ollama for AI text generation, edge-tts for voiceover, FFmpeg for video assembly, Pexels (with a Pixabay backup) for stock footage, and the YouTube Data API for uploads. The project is set up for local Windows development with VS Code and ships Windows-only `.bat` setup scripts.

| Field | Value |
|---|---|
| **Origin** | [Yashvi-Vekariya/ai-youtube-shorts-automation](https://github.com/Yashvi-Vekariya/ai-youtube-shorts-automation) |
| **License** | Not specified |
| **Stack** | Python, Ollama, edge-tts, FFmpeg, Pexels + Pixabay APIs, YouTube Data API v3 |
| **AI Model** | LLaMA 3 (via Ollama) |
| **Platform** | Windows-focused local setup (VS Code + `.bat` scripts) |
| **Python** | `pip install -r requirements.txt` |
| **Artifacts** | `config/`, `assets/music/`, `output/`, `logs/` |
| **Source** | `sources/ai-youtube-shorts-automation/` |
| **Codegraph** | `graphs/ai-youtube-shorts-automation/` |

## What is it?

This system runs on a scheduled loop: it discovers trending topics from Reddit, Hacker News, and Google Trends RSS, generates a viral video idea using local Ollama AI, writes a 30-second script with hook and twist, optimizes the hook, creates an AI voiceover via edge-tts, downloads stock footage from Pexels (with Pixabay as an automatic backup source), mixes in optional background music, assembles a vertical 9:16 video with subtitles using FFmpeg, uploads to YouTube automatically, and tracks analytics with AI-generated optimization feedback.

## Key Features

- **Trend Discovery** — `modules/trend_scraper.py` scrapes Reddit (free public JSON, no API key), Hacker News (free API), and Google Trends RSS; falls back to keywords when Reddit rate-limits
- **AI Script Generation** — Ollama-powered idea generator, script generator, hook optimizer, and SEO generator with curiosity gaps and loop endings
- **SEO Metadata** — Auto-generated title, description, tags, and hashtags optimized for discovery
- **AI Voiceover** — edge-tts (free Microsoft neural voices) with configurable voice (e.g. `en-US-ChristopherNeural`, `hi-IN-MadhurNeural`)
- **Stock Footage** — Pexels API (200 requests/hour) with **Pixabay backup fetcher** (`modules/pixabay_fetcher.py`, 100 requests/min, no watermark) used when Pexels has no results or rate-limits
- **Background Music** — `modules/music_manager.py` auto-downloads free royalty-free music from Pixabay and manages local `.mp3` files in `assets/music/`; mixed at 8% volume (configurable `BACKGROUND_MUSIC_VOLUME`), voiceover-only fallback
- **Script Quality Checker** — `modules/script_quality.py` validates and scores scripts before video creation (word/sentence counts, hook strength) and improves weak scripts
- **Video Assembly** — FFmpeg vertical 9:16 builder with Ken Burns zoom effect (`zoompan`), clips, voice, subtitles, and thumbnail extraction
- **Auto-Upload** — YouTube Data API v3 upload with OAuth 2.0 + thumbnail set
- **Analytics Tracking** — Performance monitoring with AI optimization feedback loop (`refresh_all_stats`, `generate_ai_feedback`)
- **Multi-Channel Mode** — Up to 5 channels via `modules/multi_channel.py` (5 channels × 4 shorts/day = 20 videos/day)
- **Scheduler** — CRON-style execution every few hours via `scheduler.py`; Windows Task Scheduler auto-start via `setup_task_scheduler.bat`
- **5 Pre-Configured Niches** — AI & Technology, Money & Business, Psychology Facts, Space & Science, History Facts

## Tech Stack

| Component | Technology |
|---|---|
| **Runtime** | Python 3.10+ |
| **AI Text Generation** | Ollama + LLaMA 3 |
| **Voiceover** | edge-tts (free Microsoft neural voices) |
| **Video Processing** | FFmpeg (`zoompan` Ken Burns, subtitles, thumbnail) |
| **Stock Footage** | Pexels API (primary) + Pixabay API (backup) |
| **Background Music** | Pixabay music API + local `assets/music/*.mp3` |
| **Upload** | YouTube Data API v3 (10K units/day free), OAuth 2.0 |
| **Scheduling** | `scheduler.py` + `setup_task_scheduler.bat` (Windows Task Scheduler) |
| **Setup** | `setup_windows.bat` (Windows), VS Code workflow |

## Deployment

### Local Setup (Windows + VS Code — the documented path)

```bash
git clone https://github.com/Yashvi-Vekariya/ai-youtube-shorts-automation.git
cd ai-youtube-shorts-automation
pip install -r requirements.txt
# Configure Pexels API key in config/settings.py
# Add Pixabay key (optional, backup footage) in config/settings.py
# Put YouTube OAuth client_secret.json in config/
setup_windows.bat
```

### Prerequisites

- Python 3.10+ (check "Add Python to PATH")
- FFmpeg installed and in PATH (or `choco install ffmpeg`)
- Ollama installed with LLaMA 3 pulled (`ollama pull llama3`, then `ollama serve`)
- Pexels API key (free); optional Pixabay API key (free, 100 req/min) for backup footage
- YouTube Data API v3 OAuth credentials — enable the API, create an OAuth client ID (Desktop app), save as `config/client_secret.json`; first upload opens a browser for Google login

### Auto-Run on Windows

```bash
setup_task_scheduler.bat
```

Creates a Windows scheduled task that runs the pipeline every 6 hours automatically, even after restart.

## Usage

```bash
python main.py --mode test            # quick test, no upload
python main.py --mode single --dry-run # create 1 video, no upload
python main.py --mode single           # create + upload 1 video
python main.py --mode batch --count 4 --dry-run   # batch of 4
python main.py --mode analytics        # run analytics + AI feedback
python scheduler.py                    # start automatic scheduler
python scheduler.py --interval 4       # custom interval (hours)
python scheduler.py --multi-channel --once   # run all channels once
python dashboard.py                    # status dashboard
```

Pick a niche: `python main.py --mode single --niche 0` (AI & Tech) … `--niche 4` (History Facts).

### Project Layout (Artifacts)

```
config/            settings.py (all config + .env loader), client_secret.json,
                   client_secret_ch1-5.json, channels.json, youtube_token.json
assets/music/      drop .mp3 files here for background music (auto-downloads also supported)
output/            generated videos (+ temp voice files cleaned between runs)
logs/              automation logs + analytics data
utils/             logger
```

## Related

- [[MoneyPrinterV2]] — Multi-workflow money automation (includes YouTube Shorts)
- [[freellmapi]] — Free LLM API aggregator (augment AI generation)
- [[9router]] — AI routing gateway (route to additional AI providers)
