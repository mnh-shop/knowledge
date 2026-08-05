---
name: gemini-youtube-automation
tags: [ai-llm, automation, cli, container, gemini, github-actions, python, youtube, wiki, gemini-youtube-automation]
description: "Fully autonomous AI bot that writes, produces, and uploads YouTube lessons daily using Gemini 2.5 Flash — zero human input required"
source: sources/gemini-youtube-automation/
verification_date: 2026-07-30
verified_by: codegraph-verify
---

# Gemini YouTube Automation

| Field | Value |
|---|---|
| **Origin** | [ChaitanyaEswarRajeshJakki/gemini-youtube-automation](https://github.com/ChaitanyaEswarRajeshJakki/gemini-youtube-automation) |
| **License** | MIT |
| **Stack** | Python 3.11, Google Gemini 2.5 Flash, gTTS, MoviePy, FFmpeg, YouTube Data API v3 |
| **Deployment** | GitHub Actions (free CI runners) |
| **Source** | `sources/gemini-youtube-automation/` |

## What is it?

A fully autonomous AI bot that writes video scripts, generates spoken audio, assembles video with visuals and subtitles, and uploads finished YouTube lessons — all on a daily schedule with zero human input. It runs entirely on free GitHub Actions CI runners and costs only the Gemini API usage for script/content generation.

The bot handles the complete content pipeline: topic selection → script writing → TTS narration → video assembly → thumbnail creation → YouTube upload → content-plan commit.

## Key Features

- **Fully Autonomous Pipeline:** No human intervention required from topic to upload. Runs on a cron schedule via GitHub Actions.
- **Gemini 2.5 Flash Powered:** Uses Google's Gemini 2.5 Flash model for script writing, curriculum generation, and educational material creation.
- **TTS Narration:** Generates natural-sounding voiceovers using gTTS (Google Text-to-Speech).
- **TTS Rate-Limiting & Backoff:** TTS requests are throttled (minimum 2-second gap) with exponential backoff plus jitter (up to 5 attempts) to survive Google's throttling of shared CI IPs.
- **Video Assembly:** Composes final video with MoviePy and FFmpeg — combines audio, visuals, captions, transitions, and background music.
- **Custom Thumbnails:** Auto-generates a thumbnail for each format (Pillow) and uploads it with the video.
- **YouTube API Integration:** Authenticated upload via YouTube Data API v3 with resumable uploads and thumbnail support.
- **Self-Updating Repo:** After each successful run, the workflow commits the updated `content_plan.json` (lesson marked `complete` with its YouTube ID) and demo GIF back to the repo.
- **Daily Content Loop:** Designed for daily lesson production — one topic per day, fully automated.

## Tech Stack

| Component | Technology |
|---|---|
| **Language** | Python 3.11 |
| **AI/LLM** | Google Gemini 2.5 Flash |
| **Text-to-Speech** | gTTS (Google Text-to-Speech) |
| **Video Editing** | MoviePy, FFmpeg |
| **Upload API** | YouTube Data API v3 |
| **CI/Orchestration** | GitHub Actions (cron-triggered workflows) |
| **Dependencies** | `pip` (requirements.txt) |

## Deployment

### GitHub Actions (Default)

The primary deployment target is GitHub Actions free runners:

1. Fork or clone the repository
2. Configure repository secrets (Settings → Secrets and variables → Actions):
   - `GOOGLE_API_KEY` — Gemini API key from Google AI Studio
   - `PEXELS_API_KEY` — Pexels API key for stock imagery
   - `CLIENT_SECRET_B64` — YouTube OAuth `client_secrets.json` encoded in base64
   - `CREDENTIALS_B64` — YouTube OAuth `credentials.json` encoded in base64
3. The workflow runs daily at **7:00 AM UTC** (`0 7 * * *`) defined in `.github/workflows/main.yml`
4. Each run: reads the content plan → generates script → produces audio → fetches Pexels imagery → assembles long + short videos → uploads both with thumbnails → commits the updated content plan back to the repo

### Local Development

```bash
git clone https://github.com/ChaitanyaEswarRajeshJakki/gemini-youtube-automation.git
cd gemini-youtube-automation
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# Set GOOGLE_API_KEY and PEXELS_API_KEY, and place client_secrets.json / credentials.json (YouTube OAuth)
python main.py
```

## Related

- [[goclaw]] — Enterprise agent gateway that could orchestrate similar automation pipelines
- [[n8n]] — Workflow engine alternative for scheduled content pipelines
