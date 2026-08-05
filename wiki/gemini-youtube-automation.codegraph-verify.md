---
name: gemini-youtube-automation-codegraph-verify
tags: [gemini, youtube, automation, ai, python, github-actions, wiki]
description: "Codegraph Verification: gemini-youtube-automation — validating wiki claims against indexed source code symbols"
source: sources/gemini-youtube-automation/
---

# Codegraph Verification: gemini-youtube-automation

**Date:** 2026-07-30

## Claim 1: Gemini 2.5 Flash for curriculum/lesson generation
- **Wiki says:** Uses Gemini 2.5 Flash to generate full course curricula and per-lesson slide scripts.
- **Source evidence:**
  - `src/generator.py` contains `client.models.generate_content(model='gemini-2.5-flash', ...)` at line 133 for curriculum generation
  - `src/generator.py` uses the same model for lesson content generation at line 160
  - `README.md` line 106 lists "Google Gemini 2.5 Flash" as the AI script generation component
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: gTTS for narration
- **Wiki says:** Uses gTTS (Google Text-to-Speech) for per-slide audio narration.
- **Source evidence:**
  - `src/generator.py` imports `from gtts import gTTS` at line 11
  - `src/generator.py` line 82 creates `tts = gTTS(text=text, lang='en', slow=False)` for narration
  - `src/generator.py` line 73 defines `text_to_speech()` function using gTTS
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: TTS rate-limiting with exponential backoff
- **Wiki says:** TTS requests are rate-limited with exponential backoff to avoid Google throttling.
- **Source evidence:**
  - `src/generator.py` line 64 defines `_throttle_tts()` which enforces a minimum 2-second gap between requests (`TTS_MIN_GAP_SECONDS = 2` at line 30)
  - `src/generator.py` line 104 implements exponential backoff: `delay = TTS_BACKOFF_SECONDS * (2 ** (attempt - 1)) + random.uniform(0, 2)`
  - `src/generator.py` line 28 sets `TTS_MAX_ATTEMPTS = 5` with `TTS_BACKOFF_SECONDS = 5`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Pexels API with orientation-based search
- **Wiki says:** Fetches background imagery from Pexels API with orientation-based search (landscape/portrait).
- **Source evidence:**
  - `src/generator.py` line 38 defines `get_pexels_image(query, video_type)` which calls the Pexels API
  - `src/generator.py` line 45 sets orientation based on video type: `orientation = 'landscape' if video_type == 'long' else 'portrait'`
  - `src/generator.py` line 48 makes the API request: `requests.get("https://api.pexels.com/v1/search", ...)`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: YouTube Data API v3 with resumable uploads
- **Wiki says:** Uploads videos via YouTube Data API v3 with resumable upload support.
- **Source evidence:**
  - `src/uploader.py` line 58 defines `upload_to_youtube()` using the YouTube API v3 client
  - `src/uploader.py` line 77 creates a resumable media upload: `MediaFileUpload(str(video_path), chunksize=-1, resumable=True)`
  - `src/uploader.py` line 54 builds the API client: `build('youtube', 'v3', credentials=credentials)`
  - `src/uploader.py` line 87 implements chunked upload with progress: `status, response = request.next_chunk()`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: GitHub Actions daily at 7:00 AM UTC
- **Wiki says:** The pipeline runs daily at 7:00 AM UTC via GitHub Actions scheduler.
- **Source evidence:**
  - `README.md` line 34 states: "Every day at **7:00 AM UTC**, this bot runs entirely on GitHub Actions"
  - `README.md` line 111 lists "GitHub Actions" as the automation component
  - `README.md` line 8 references the Actions workflow badge from `.github/workflows/main.yml`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Dual-format output 1920×1080 + 1080×1920
- **Wiki says:** Produces both long-form (1920×1080) landscape video and vertical YouTube Short (1080×1920).
- **Source evidence:**
  - `src/generator.py` line 254 sets dimensions: `width, height = (1920, 1080) if video_type == 'long' else (1080, 1920)`
  - `README.md` line 39-40 describes both formats: "Renders a professional slide-based video (1920×1080)" and "Renders a vertical YouTube Short (1080×1920)"
  - `main.py` line 93 creates long video and line 123 creates short video confirming dual output paths
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: Origin repo and GitHub Actions secrets
- **Wiki says:** Origin is `ChaitanyaEswarRajeshJakki/gemini-youtube-automation`; deployment uses secrets `GOOGLE_API_KEY`, `PEXELS_API_KEY`, `CLIENT_SECRET_B64`, `CREDENTIALS_B64`.
- **Source evidence:**
  - `README.md` lines 8-15: every badge links `ChaitanyaEswarRajeshJakki/gemini-youtube-automation` (workflow badge, stars, last-commit, license)
  - `README.md` lines 137-140 list the four secrets: `GOOGLE_API_KEY` (Gemini), `PEXELS_API_KEY` (Pexels), `CLIENT_SECRET_B64` / `CREDENTIALS_B64` (YouTube OAuth base64)
  - `.github/workflows/main.yml` lines 50-51 restore OAuth files from `CLIENT_SECRET_B64` / `CREDENTIALS_B64`; lines 57-58 pass `GOOGLE_API_KEY` and `PEXELS_API_KEY` into the production run
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 8 key claims from the gemini-youtube-automation wiki have been verified against the source code:
- ✅ Gemini 2.5 Flash: Confirmed for curriculum and lesson content generation
- ✅ gTTS narration: Confirmed for per-slide text-to-speech
- ✅ TTS rate-limiting: Exponential backoff with configurable retry confirmed
- ✅ Pexels API: Orientation-based image search confirmed
- ✅ YouTube Data API v3: Resumable uploads with chunked progress confirmed
- ✅ GitHub Actions scheduler: Daily 7:00 AM UTC confirmed
- ✅ Dual-format output: Both 1920×1080 and 1080×1920 confirmed
- ✅ Origin + deployment secrets: ChaitanyaEswarRajeshJakki repo with GOOGLE_API_KEY / PEXELS_API_KEY / CLIENT_SECRET_B64 / CREDENTIALS_B64 confirmed

## Related

- [[gemini-youtube-automation]] -- Main wiki entry

## Cross-project

- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for Hermes Agent
- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
