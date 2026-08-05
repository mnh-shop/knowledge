---
name: 9router
tags: [ai, router, gateway, token-saver, proxy, llm, nextjs, sqlite, docker, openai-compatible, mit]
description: "Free AI router and token saver — connects AI coding tools to 40+ providers and 100+ models with RTK compression, 3-tier fallback, quota tracking, and bundled agent skills"
source: sources/9router/
verification_date: 2026-07-30
verified_by: codegraph-verify
---

# 9Router

**Source:** `sources/9router/`

9Router is a local AI routing gateway and token-saving proxy that exposes a single OpenAI-compatible endpoint (`/v1/*`) and routes traffic across 40+ upstream providers. It features RTK (Response Token Killing) compression to save 20-40% tokens per request, automatic 3-tier fallback (subscription → cheap → free), and multi-account round-robin for zero-downtime coding. Two artifacts ship from one repo: the dashboard + gateway (`9router-app`, Next.js) and a separately versioned CLI launcher published to npm as `9router`.

| Field | Value |
|---|---|
| **Origin** | [decolua/9router](https://github.com/decolua/9router) |
| **License** | MIT |
| **Stack** | Node.js, Next.js, SQLite, open-sse engine |
| **Dashboard** | `http://localhost:20128/dashboard` |
| **API** | `http://localhost:20128/v1` (OpenAI-compatible) |
| **npm** | `npm install -g 9router` |
| **Docker** | `decolua/9router` (Docker Hub + GHCR, linux/amd64 + linux/arm64) |
| **Agent Skills** | 9 bundled (9router + chat, embeddings, image, stt, tts, video, web-fetch, web-search) |
| **i18n** | 7 README translations incl. `i18n/README.zh-CN.md` |
| **Source** | `sources/9router/` |
| **Codegraph** | `graphs/9router/` |

## What is it?

9Router is a smart local proxy that sits between your AI coding tool (Claude Code, Cursor, Copilot, Codex, Cline, OpenClaw, OpenCode, etc.) and 40+ AI providers. It translates formats (OpenAI ↔ Claude ↔ Gemini ↔ Cursor ↔ Kiro ↔ Vertex), tracks per-provider quota, auto-refreshes tokens, and compresses tool result content with RTK to cut token consumption by 20-40%. When a subscription provider hits its rate limit, 9Router falls through to cheap providers (GLM, MiniMax), then free ones (Kiro, OpenCode Free, Vertex credits) — keeping you coding continuously.

**Port note:** the repo is internally inconsistent on its port. The root `package.json` scripts hardcode `--port 20127` (`dev`, `dev:webpack`, `start`, `dev:bun`), while README.md, DOCKER.md, and the CLI docs all describe the service at **20128**. This wiki documents the dashboard/API at **20128 per the README**; if you run from source, the production start command overrides the port explicitly (`PORT=20128 HOSTNAME=0.0.0.0 npm run start`).

## Key Features

- **RTK Token Saver** — Pre-translate hooks that compress `tool_result` content in-place (git diff, grep, ls, tree filters; 1KB auto-detect) to save 20-40% tokens per request; fail-open and default ON
- **3-Tier Fallback** — Subscription (Claude Code, Codex, GitHub Copilot, Cursor) → Cheap (GLM $0.6/1M, MiniMax $0.2/1M, Kimi $9/mo flat) → Free (Kiro, OpenCode Free, Vertex), zero downtime
- **Multi-Account Round-Robin** — Distribute requests across multiple accounts per provider, auto-fallback when one hits quota
- **Format Translation** — OpenAI-intermediate-format pivot with direct routes for fragile pairs (thinking blocks, tool IDs, non-base64 images)
- **Quota Tracking & Auto-Refresh** — Monitor per-provider usage with reset countdowns and auto-refresh OAuth tokens
- **40+ Providers, 100+ Models** — Connect to virtually any AI provider through a single endpoint
- **Universal Compatibility** — Works with Claude Code, Codex, Cursor, Cline, Gemini CLI, OpenClaw, OpenCode, and any OpenAI-compatible client
- **Next.js Dashboard** — Browser-based UI for provider management, quota monitoring, combos, and configuration
- **Bundled Agent Skills** — `skills/` ships 9 skills for agents: `9router` (gateway skill) plus 8 sub-skills — `chat`, `embeddings`, `image`, `stt`, `tts`, `video`, `web-fetch`, `web-search`
- **Extras** — Headroom token saver integration, Caveman Mode, Ponytail ("lazy senior dev" prompt), cloud sync, usage analytics, request logging

### Free-Tier Provider Specifics

| Provider | What you get | Caveats |
|---|---|---|
| **Kiro AI** (`kr/`) | Claude 4.5 + GLM-5 + MiniMax free; ~50 credits/month (500 trial credits for new accounts in first 30 days) | Paid tiers above the cap: Pro $20/mo, Pro+ $40/mo, Pro Max $100/mo, Power $200/mo |
| **OpenCode Free** (`oc/`) | No-auth passthrough proxy; models auto-fetched from `opencode.ai/zen/v1/models` | Free model list fluctuates (some free only for limited promos) — subject to change |
| **Vertex AI** (`vertex/`) | Gemini 3 Pro + DeepSeek + GLM-5 via $300 credits for new GCP accounts (90 days) | Since Mar 2026 the Gemini API endpoint no longer consumes credits — call the **Vertex AI Studio** endpoint |

Discontinued free tiers (README no longer recommends): iFlow (moved to paid, 2026), Qwen Code (shut down 2026-04-15), Gemini CLI (shut down 2026-06-18, replaced by closed-source Antigravity).

## Tech Stack

| Layer | Technology |
|---|---|
| **Runtime** | Node.js (ESM), Bun |
| **Framework** | Next.js (webpack/bun build) |
| **Routing Engine** | `open-sse/` — provider-agnostic routing, translation, and execution engine |
| **Database** | SQLite via `bun:sqlite` → `better-sqlite3` → `node:sqlite` → `sql.js` adapter chain |
| **CLI** | Separate npm package (`9router`) with tray support |
| **Auth** | OAuth, API keys, JWT session cookies |
| **Translators** | OpenAI-intermediate-format pivot with direct routes for fragile pairs |
| **Agent Skills** | Markdown SKILL.md (Agent Skills spec), 9 bundled |

## Deployment

### Quick Install (npm)

```bash
npm install -g 9router
9router
# Dashboard opens at http://localhost:20128
```

### Docker

```bash
docker run -d \
  --name 9router \
  -p 20128:20128 \
  -v "$HOME/.9router:/app/data" \
  -e DATA_DIR=/app/data \
  decolua/9router:latest
# → http://localhost:20128
```

Data persists at `$HOME/.9router/db/data.sqlite` (host) ↔ `/app/data/db/data.sqlite` (container). Multi-platform images on Docker Hub and GHCR.

### Production Build (from source)

```bash
cp .env.example .env
npm install
npm run build
PORT=20128 HOSTNAME=0.0.0.0 NEXT_PUBLIC_BASE_URL=http://localhost:20128 npm run start
```

### Other Entry Points

- `start.sh` — convenience launcher script at repo root
- `captain-definition` — CapRover one-click deploy support
- `docker-compose.yml` — compose file for the app
- i18n: `i18n/README.zh-CN.md` (plus vi, ja-JP, ru, th, fa_IR, id-ID) and a root `README.zh-CN.md`

### Key Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `PORT` / `HOSTNAME` | `20128` / `0.0.0.0` | Service bind |
| `JWT_SECRET` | auto-generated | Dashboard auth cookie signing |
| `INITIAL_PASSWORD` | `123456` | First-login password (must override) |
| `DATA_DIR` | `~/.9router` | SQLite location (`$DATA_DIR/db/data.sqlite`) |
| `API_KEY_SECRET`, `MACHINE_ID_SALT` | endpoint-proxy defaults | HMAC for API keys / machine IDs |
| `REQUIRE_API_KEY` | `false` | Enforce Bearer key on `/v1/*` (recommended for internet-exposed deploys) |
| `SEARXNG_URL` | `http://localhost:8888/search` | Built-in SearXNG web-search provider |

## Usage

Point any OpenAI-compatible client at the local endpoint:

```
Endpoint: http://localhost:20128/v1
API Key:  [copy from dashboard]
Model:    kr/claude-sonnet-4.5        # free via Kiro
          glm/glm-5.1                 # cheap backup
          premium-coding              # or a named combo
```

Claude Code (`~/.claude/config.json`): set `anthropic_api_base: "http://localhost:20128/v1"`. OpenClaw: define a `9router` provider with `baseUrl: http://127.0.0.1:20128/v1` (use `127.0.0.1`, not `localhost`, to avoid IPv6 issues).

## Related

- [[freellmapi]] — Self-hosted LLM API aggregator with 29 free providers
- [[hermes-agent]] — Multi-platform AI agent with MCP bridge
- [[goclaw]] — Go-based MCP gateway with compatible routing patterns
