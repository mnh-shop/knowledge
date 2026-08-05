---
name: MoneyPrinterV2
tags: [automation, money, youtube, twitter, affiliate-marketing, outreach, python, ollama, selenium, agpl]
description: "Automates online money-making workflows — Twitter bots, YouTube Shorts, affiliate marketing, and cold outreach using local AI"
source: sources/MoneyPrinterV2/
verification_date: 2026-07-30
verified_by: codegraph-verify
---

# MoneyPrinter V2

**Source:** `sources/MoneyPrinterV2/`

MoneyPrinter V2 (MPV2) is an application that automates the process of making money online. It is a complete rewrite of the original MoneyPrinter project with a focus on a wider range of features and a more modular architecture — Twitter bots, YouTube Shorts automation, affiliate marketing, and local business cold outreach, all driven by local AI.

| Field | Value |
|---|---|
| **Origin** | [FujiwaraChoki/MoneyPrinterV2](https://github.com/FujiwaraChoki/MoneyPrinterV2) |
| **License** | AGPL-3.0 |
| **Stack** | Python 3.12, Go, Ollama, moviepy, Selenium, Google APIs |
| **Python** | `python3 -m venv venv && pip install -r requirements.txt` |
| **Source** | `sources/MoneyPrinterV2/` |
| **Codegraph** | `graphs/MoneyPrinterV2/` |

## What is it?

MoneyPrinter V2 is a modular automation framework that runs locally using free AI tools. It combines four major income-generating workflows: a Twitter/X bot with scheduled posting, a YouTube Shorts automator that creates and publishes videos, an Amazon affiliate marketing system, and a local business finder with cold outreach. All AI generation runs through local Ollama models, keeping costs at zero.

## Key Features

- **Twitter Bot** — Automated content generation and posting with CRON scheduling; engages with trends and manages posting cadence
- **YouTube Shorts Automator** — End-to-end Shorts creation: trend discovery, script writing, TTS voiceover, video assembly, and auto-upload with CRON scheduling (local Whisper STT for subtitles by default; AssemblyAI optional as `third_party_assemblyai`)
- **PostBridge** — Crossposts content (e.g., YouTube Shorts) to other platforms via `src/classes/PostBridge.py` and `src/post_bridge_integration.py` (`maybe_crosspost_youtube_short`)
- **Affiliate Marketing** — Amazon product integration with Twitter promotion pipeline
- **Local Business Finder & Cold Outreach** — Scrapes local businesses via a Go-based scraper (google-maps-scraper), generates personalized outreach emails and messages via local AI
- **Local AI-Powered** — All content generation via Ollama (no paid API calls)
- **Modular Architecture** — Provider-specific components in `src/classes/` (YouTube.py, Twitter.py, Tts.py, AFM.py, Outreach.py, PostBridge.py)

## Tech Stack

| Layer | Technology |
|---|---|
| **Runtime** | Python 3.12 |
| **AI Generation** | Ollama (local LLMs) |
| **Video Processing** | moviepy, FFmpeg |
| **Browser Automation** | Selenium (Firefox + GeckoDriver) |
| **Subtitles/STT** | Local Whisper (default) + optional AssemblyAI (`third_party_assemblyai`) |
| **Outreach Scraper** | Go (google-maps-scraper binary, built via `build_scraper`) |
| **Scheduling** | Python CRON (scheduler) |
| **TTS** | Local TTS engine |

## Documentation

- [TwitterBot](docs/TwitterBot.md)
- [YouTube](docs/YouTube.md)
- [AffiliateMarketing](docs/AffiliateMarketing.md)
- [PostBridge](docs/PostBridge.md)
- [Configuration](docs/Configuration.md)
- [Roadmap](docs/Roadmap.md)

## Deployment

### Local Setup

```bash
git clone https://github.com/FujiwaraChoki/MoneyPrinterV2.git
cd MoneyPrinterV2
cp config.example.json config.json
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 src/main.py
```

### Preflight Validation

```bash
python3 scripts/preflight_local.py
```

> **Note:** The Outreach workflow requires the Go Programming Language installed to build the google-maps-scraper binary (`Outreach.py` `is_go_installed` / `build_scraper`).

## Related

- [[ai-youtube-shorts-automation]] — Free autonomous YouTube Shorts creation and upload system
- [[freellmapi]] — Self-hosted LLM API aggregator (can supplement local AI)
- [[9router]] — AI routing gateway (can route to free/cheap providers)
