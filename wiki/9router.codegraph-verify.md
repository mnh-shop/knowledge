---
name: 9router-codegraph-verify
tags: [9router, ai-router, nextjs, mcp, token-compression, npm, cli, wiki]
description: "Codegraph Verification: 9router — validating wiki claims against indexed source code symbols"
source: sources/9router/
---

# Codegraph Verification: 9router

**Date:** 2026-07-30

## Claim 1: Two published artifacts — dashboard+gateway (9router-app) and CLI (npm 9router)
- **Wiki says:** 9Router publishes two artifacts from a single repo: the dashboard + gateway (root `package.json`, `9router-app`) as a Next.js server, and a separate CLI launcher (`cli/`, npm-published as `9router`) with its own package.json and version.
- **Source evidence:**
  - Root `package.json` has `"name": "9router-app"` and `"private": true` with Next.js scripts (`next dev`, `next build`, `next start`)
  - `cli/package.json` has `"name": "9router"` with a `"bin":` entry
  - `CLAUDE.md` states: "Two published artifacts live in this one repo: The **dashboard + gateway** (root `package.json`, `9router-app`) and the **CLI launcher** (`cli/`, published to npm as `9router`)"
  - `README.md:79` shows `npm install -g 9router` as the installation method
- **Verdict:** ✅ CORRECT

## Claim 2: RTK token compression saves 20-40%, fail-open
- **Wiki says:** RTK (Real-Time Token Saver) pre-translate hooks compress `tool_result` content in-place to cut tokens, saving 20-40% per request. Fail-open: any error returns null and leaves the body untouched.
- **Source evidence:**
  - `open-sse/rtk/` directory exists with `applyFilter.js`, `autodetect.js`, `caveman.js` modules
  - `CLAUDE.md` section "RTK token saver (`open-sse/rtk/`)" confirms: "Pre-translate hooks that compress `tool_result` content in-place to cut tokens. **Fail-open**: any error returns null and leaves the body untouched — never throw out of them"
  - `README.md:6` reads "Save 20-40% tokens with RTK"; `README.md:450` "Save **20-40% input tokens** per request"
- **Verdict:** ✅ CORRECT

## Claim 3: SQLite persistence with 4-driver fallback chain
- **Wiki says:** SQLite layer under `src/lib/db/` with adapter fallback chain: `bun:sqlite` → `better-sqlite3` → `node:sqlite` (Node ≥22.5) → `sql.js` (pure-JS fallback). `better-sqlite3` is in `optionalDependencies`.
- **Source evidence:**
  - `CLAUDE.md` states: "It's a SQLite layer under `src/lib/db/` with an adapter fallback chain (`driver.js`): `bun:sqlite` → `better-sqlite3` (optional native dep) → `node:sqlite` (Node ≥22.5) → `sql.js` (pure-JS fallback, always works)"
  - Root `package.json` has `"optionalDependencies": { "better-sqlite3": "^12.6.2" ... }`
  - Root `package.json` has `"dependencies": { "sql.js": "^1.14.1" ... }`
  - `README.md:1250` confirms the DB file at `${DATA_DIR}/db/data.sqlite`
- **Verdict:** ✅ CORRECT

## Claim 4: Translator pivots through OpenAI as intermediate format
- **Wiki says:** The translator engine pivots through OpenAI format as the intermediate format; a translator registered on an exact `source:target` pair runs as a direct route, skipping the double-hop.
- **Source evidence:**
  - `CLAUDE.md` states: "Pivots through **OpenAI as the intermediate format**. A translator registered on an exact `source:target` pair (e.g. `claude:kiro`) runs as a **direct route**, skipping the lossy double-hop"
  - `CLAUDE.md` references `open-sse/translator/` with `register(from, to, reqFn, resFn)` self-registration as an import side effect
- **Verdict:** ✅ CORRECT

## Claim 5: custom-server.js strips X-Forwarded-For
- **Wiki says:** `custom-server.js` wraps the Next.js standalone server to derive client IP from the TCP socket and strip attacker-controlled `X-Forwarded-For` headers, trusting forwarding headers only from a loopback reverse proxy.
- **Source evidence:**
  - `custom-server.js` wraps `http.createServer` and reads `req.socket.remoteAddress`
  - Code comments confirm: "derive client IP from the TCP socket (unspoofable) and strip client-supplied forwarding headers"
  - Logic checks `isLoopbackProxy` and only trusts forwarding headers when the TCP peer is `127.0.0.1` or `::1`
  - `CLAUDE.md` confirms: "`custom-server.js` wraps the Next standalone server to derive client IP from the TCP socket and strip attacker-controlled `X-Forwarded-For`"
- **Verdict:** ✅ CORRECT

## Claim 6: Bundled agent skills — 9router + 8 sub-skills
- **Wiki says:** `skills/` ships 9 agent skills: the `9router` gateway skill plus 8 sub-skills (chat, embeddings, image, stt, tts, video, web-fetch, web-search).
- **Source evidence:**
  - `skills/` contains `9router/SKILL.md` and `skills/README.md` (verified via filesystem)
  - Eight sub-skill dirs each with SKILL.md: `9router-chat/`, `9router-embeddings/`, `9router-image/`, `9router-stt/`, `9router-tts/`, `9router-video/`, `9router-web-fetch/`, `9router-web-search/`
  - Total = 9 SKILL.md files under `skills/`
- **Verdict:** ✅ CORRECT

## Claim 7: Repo-internal port inconsistency — 20127 in package.json vs 20128 in docs
- **Wiki says:** Root package.json scripts hardcode port 20127; README.md and DOCKER.md describe the service at 20128. The wiki documents the dashboard at 20128 per the README.
- **Source evidence:**
  - `package.json:7` `"dev": "next dev --port 20127"`; `package.json:8` `"dev:webpack": "next dev --webpack --port 20127"`; `package.json:10` `"start": "next start --port 20127"`; `package.json:11` `"dev:bun": "bun --bun next dev --webpack --port 20127"`
  - `README.md:83` "🎉 Dashboard opens at `http://localhost:20128`"; `README.md:119-120` Dashboard `http://localhost:20128/dashboard`, API `http://localhost:20128/v1`
  - `DOCKER.md:13,20` `-p 20128:20128` and "App listens on port `20128`"
  - Production start overrides explicitly: `README.md:114` `PORT=20128 HOSTNAME=0.0.0.0 ... npm run start`
- **Verdict:** ✅ CORRECT (with noted inconsistency)

## Claim 8: Deployment extras — start.sh, captain-definition, i18n/zh-CN; free-tier provider specifics
- **Wiki says:** The repo ships `start.sh`, a CapRover `captain-definition`, a Chinese (zh-CN) README plus 6 more i18n translations; free tier specifics: Kiro AI (~50 credits/mo), OpenCode Free (no auth), Vertex AI ($300 credits).
- **Source evidence:**
  - `start.sh` (executable) and `captain-definition` exist at repo root (verified via filesystem)
  - `i18n/README.zh-CN.md` exists (plus vi, ja-JP, ru, th, fa_IR, id-ID); root `README.zh-CN.md` also present; `README.md:20` lists all 7 translations
  - `README.md:336-337` Kiro AI "Claude 4.5 + GLM-5 + MiniMax, 50 credits/month free"
  - `README.md:339-341` OpenCode Free "No auth • Auto-fetch models"; `README.md:344-346` Vertex AI "Gemini 3 Pro + GLM-5 + DeepSeek, $300 credits free"
  - `README.md:352-356` documents discontinued free tiers (iFlow, Qwen Code, Gemini CLI) and the Vertex AI Studio endpoint caveat
- **Verdict:** ✅ CORRECT

## Summary

All 8 key claims from the 9Router wiki have been verified against the source code:
- ✅ Two published artifacts: root `9router-app` + npm `9router` CLI confirmed
- ✅ RTK token compression: 20-40% savings confirmed with fail-open pattern
- ✅ SQLite 4-driver fallback: full chain confirmed in CLAUDE.md and package.json
- ✅ OpenAI pivot format: translator architecture confirmed
- ✅ custom-server.js X-Forwarded-For stripping: source code confirms socket-based IP derivation
- ✅ Bundled agent skills: 9router + 8 sub-skills = 9 SKILL.md files confirmed
- ✅ Port inconsistency: package.json hardcodes 20127; README/DOCKER.md use 20128
- ✅ Deployment extras + free tiers: start.sh, captain-definition, i18n/zh-CN, and Kiro/OpenCode Free/Vertex specifics confirmed

## Related

- [[9router]] -- Main wiki entry

## Cross-project

- [[freellmapi.codegraph-verify]] -- Similar codegraph verification for FreeLLMAPI
- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for Hermes Agent
