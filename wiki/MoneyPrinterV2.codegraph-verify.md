---
name: MoneyPrinterV2-codegraph-verify
tags: [moneyprinter, automation, python, youtube, twitter, ollama, affiliate, wiki]
description: "Codegraph Verification: MoneyPrinterV2 — validating wiki claims against indexed source code symbols"
source: sources/MoneyPrinterV2/
---

# Codegraph Verification: MoneyPrinterV2

**Date:** 2026-07-30

## Claim 1: Python automation for Twitter/YouTube/affiliate/outreach
- **Wiki says:** MoneyPrinterV2 automates Twitter bots, YouTube Shorts, affiliate marketing (Amazon + Twitter), and cold outreach to local businesses.
- **Source evidence:**
  - `README.md` lists features: "Twitter Bot (with CRON Jobs)", "YouTube Shorts Automator (with CRON Jobs)", "Affiliate Marketing (Amazon + Twitter)", "Find local businesses & cold outreach"
  - `src/classes/` contains dedicated provider classes: `Twitter.py`, `YouTube.py`, `AFM.py` (Affiliate Marketing), `Outreach.py`
  - `src/main.py` imports all four classes: `Twitter`, `YouTube`, `AffiliateMarketing`, `Outreach`
- **Verdict:** ✅ CORRECT

## Claim 2: Requires Python 3.12 + local Ollama
- **Wiki says:** The application requires Python 3.12 and uses a local Ollama instance for all AI generation.
- **Source evidence:**
  - `README.md` states: "MPV2 needs Python 3.12 to function effectively"
  - `src/llm_provider.py` imports `ollama` and uses `ollama.Client(host=get_ollama_base_url())` for all text generation
  - `src/llm_provider.py` provides `list_models()`, `select_model()`, `get_active_model()`, and `generate_text()` functions all backed by Ollama
  - `src/config.py` has `get_ollama_base_url()` function reading from `config.json`
- **Verdict:** ✅ CORRECT

## Claim 3: YouTube class uses Selenium Firefox + MoviePy, optional AssemblyAI
- **Wiki says:** The YouTube automation uses Selenium with Firefox (via GeckoDriver) and MoviePy for video editing. Speech-to-text is local Whisper by default, with AssemblyAI as an optional `third_party_assemblyai` subtitle provider — not the primary audio-processing path.
- **Source evidence:**
  - `src/classes/YouTube.py` imports `selenium.webdriver`, `selenium.webdriver.firefox.options`, `selenium.webdriver.firefox.service`
  - `src/classes/YouTube.py` imports `from webdriver_manager.firefox import GeckoDriverManager`
  - `src/classes/YouTube.py` imports `from moviepy.editor import *` and `from moviepy.video.fx.all import crop`
  - `src/classes/YouTube.py` line 7 imports `import assemblyai as aai`
  - `src/classes/YouTube.py` lines 459-479: provider dispatch — `local_whisper` → `generate_subtitles_local_whisper`, `third_party_assemblyai` → `generate_subtitles_assemblyai`; unknown providers fall back to `local_whisper` (the default)
- **Verdict:** ✅ CORRECT (with nuance)
- **Fix needed:** Previously overstated AssemblyAI as the audio-processing path; it is the optional third-party subtitle provider while local STT is default

## Claim 4: JSON config with email/Firefox/Ollama settings
- **Wiki says:** Configuration is via `config.json` with settings for email credentials, Firefox profile path, Ollama base URL, and headless mode.
- **Source evidence:**
  - `src/config.py` reads from `config.json`: `get_email_credentials()` loads `json.load(file)["email"]`
  - `src/config.py` has `get_firefox_profile_path()` reading `json.load(file)["firefox_profile"]`
  - `src/config.py` has `get_ollama_base_url()` reading `json.load(file).get("ollama_base_url", "http://127.0.0.1:11434")`
  - `src/config.py` has `get_headless()` reading `json.load(file)["headless"]`
  - `README.md` instructs: `cp config.example.json config.json` and "fill out values in config.json"
- **Verdict:** ✅ CORRECT

## Claim 5: CRON scheduler with multi-account support
- **Wiki says:** Twitter and YouTube bots can run via CRON scheduler, with support for managing multiple accounts.
- **Source evidence:**
  - `README.md` confirms: "Twitter Bot (with CRON Jobs => `scheduler`)" and "YouTube Shorts Automator (with CRON Jobs => `scheduler`)"
  - `src/main.py` imports `schedule` module
  - `src/main.py` main menu provides options to manage accounts and set up CRON jobs
- **Verdict:** ✅ CORRECT

## Claim 6: src/classes/ for provider implementations
- **Wiki says:** Provider-specific components live in `src/classes/` (YouTube, Twitter, TTS, AFM, Outreach).
- **Source evidence:**
  - `src/classes/` directory contains: `AFM.py`, `Outreach.py`, `PostBridge.py`, `Tts.py`, `Twitter.py`, `YouTube.py`
  - AGENTS.md confirms: "`src/classes/` holds provider-specific components (for example `YouTube.py`, `Twitter.py`, `Tts.py`, `AFM.py`, `Outreach.py`)"
  - `src/main.py` imports classes from `classes.YouTube`, `classes.Twitter`, `classes.Tts`, `classes.AFM`, `classes.Outreach`
- **Verdict:** ✅ CORRECT

## Claim 7: PostBridge crossposting (YouTube → other platforms)
- **Wiki says:** MPV2 includes a PostBridge crossposting component that pushes content (e.g., YouTube Shorts) from one platform to others, wired into the main flow via `post_bridge_integration.py`.
- **Source evidence:**
  - `src/classes/PostBridge.py` — dedicated crossposting provider class in `src/classes/`
  - `src/post_bridge_integration.py` — integration module exposing `maybe_crosspost_youtube_short`
  - `src/main.py` imports `from post_bridge_integration import maybe_crosspost_youtube_short`
  - `docs/PostBridge.md` — documentation subpage for the PostBridge workflow
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (added — previously missing from wiki)

## Claim 8: Go dependency for the Outreach scraper
- **Wiki says:** The Outreach workflow depends on the Go Programming Language to build the local-business scraper (google-maps-scraper) binary; Go is part of the MPV2 stack.
- **Source evidence:**
  - `README.md` line 37: "please first install the [Go Programming Language](https://golang.org/)" for reaching out to scraped businesses
  - `src/classes/Outreach.py` line 49: `is_go_installed()` — checks `go version` is available
  - `src/classes/Outreach.py` line 85: `build_scraper()` — builds the `google-maps-scraper` binary (`.exe` on Windows)
  - `src/classes/Outreach.py` `_find_scraper_dir()` — locates the `google-maps-scraper-*` directory by its `go.mod`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (added — Go was missing from the wiki's stack)

## Summary

All 8 key claims from the MoneyPrinterV2 wiki have been verified against the source code:
- ✅ Twitter/YouTube/affiliate/outreach: All four automation features confirmed in README and src/classes/
- ✅ Python 3.12 + Ollama: Version requirement and Ollama usage confirmed
- ✅ YouTube Selenium Firefox + MoviePy: Confirmed; AssemblyAI clarified as optional `third_party_assemblyai` subtitle provider (local Whisper is default)
- ✅ JSON config: email, Firefox, Ollama, headless settings confirmed in config.py
- ✅ CRON scheduler: Scheduler support confirmed in README and main.py
- ✅ src/classes/ for providers: All six provider classes confirmed (incl. PostBridge.py)
- ✅ PostBridge crossposting: `PostBridge.py` + `post_bridge_integration.py` confirmed
- ✅ Go dependency: `is_go_installed`/`build_scraper` in Outreach.py and README Go requirement confirmed

## Related

- [[MoneyPrinterV2]] -- Main wiki entry

## Cross-project

- [[ai-youtube-shorts-automation.codegraph-verify]] -- Similar automation project
