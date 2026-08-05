---
name: freellmapi
tags: [llm, api, aggregator, openai-compatible, free, providers, proxy, router, typescript, nodejs, react, sqlite, docker, mit]
description: "Self-hosted LLM API aggregator combining 29 free providers (358 model endpoints) behind a single OpenAI-compatible API — ~4B tokens/month free"
source: sources/freellmapi/
verification_date: 2026-07-30
verified_by: codegraph-verify
---

# FreeLLMAPI

**Source:** `sources/freellmapi/`

FreeLLMAPI aggregates free tiers from 29 LLM providers (358 model endpoints) behind a single OpenAI-compatible `/v1` API. Keys are stored encrypted (AES-256-GCM in SQLite), a smart router picks the best available model for each request, falls over to the next provider when one is rate-limited, and tracks per-key usage to stay under every free-tier cap. Roughly ~4 billion tokens per month of free inference capacity.

| Field | Value |
|---|---|
| **Origin** | [tashfeenahmed/freellmapi](https://github.com/tashfeenahmed/freellmapi) |
| **License** | MIT |
| **Stack** | TypeScript/Node.js monorepo, React dashboard, SQLite |
| **Model Endpoints** | 358 from 29 providers |
| **Monthly Tokens** | ~4B free |
| **npm** | `npm install && npm run build`, then `node server/dist/index.js` (no root `start` script) |
| **Docker** | `ghcr.io/freellmapi/freellmapi` — serves on **port 3001** |
| **Source** | `sources/freellmapi/` |
| **Codegraph** | `graphs/freellmapi/` |

## What is it?

Every major AI lab offers free tiers — a few million tokens a month, a few thousand requests a day. On their own each is a toy; stacked together they add up to ~4 billion tokens per month of working inference. FreeLLMAPI collapses 29 different provider SDKs, rate limits, and failure modes into one OpenAI-compatible endpoint. Point any OpenAI client library at your local server, and it routes transparently across whichever providers you've added keys for. The router updates its own model catalog from a signed feed — new models, quota changes, and compatibility fixes land without a `git pull`.

**One unified token out:** provider keys never leave your machine as plaintext. They are AES-256-GCM encrypted in SQLite and decrypted in-memory per request; your apps only ever see a single `freellmapi-…` bearer token that the router maps to whichever upstream provider keys are needed. Every response carries an `X-Routed-Via: <platform>/<model>` header so you can see which provider actually served it.

## Key Features

- **29 Providers, 358 Endpoints** — Google, Groq, Cerebras, Mistral, OpenRouter, Cloudflare, Cohere, Z.ai (Zhipu), NVIDIA, HuggingFace, ModelScope, OpenCode Zen, and 17+ more
- **One OpenAI-Compatible API** — Drop-in replacement for any OpenAI client library or coding agent
- **Smart Routing, Six Strategies** — `priority` / `balanced` / `smartest` / `fastest` / `reliable` / `custom` (see below)
- **Automatic Fallover** — retries the next model in the chain on 429/5xx, with cooldowns and key rotation
- **Encrypted Key Storage** — provider API keys AES-256-GCM encrypted in SQLite, unified `freellmapi-…` bearer token out
- **Per-Key Usage Tracking** — RPM/RPD/TPM/TPD counters per (platform, model, key) that learn providers' reported ceilings
- **Live Model Catalog** — router syncs a signed catalog from freellmapi.co twice a day; no git pull needed
- **Custom Provider Support** — point at any OpenAI-compatible endpoint (llama.cpp, vLLM, Ollama, LM Studio)
- **Chat, Embeddings, Image & Audio** — full multimodal support through aggregation (`/v1/chat/completions`, `/v1/responses`, `/v1/completions`, `/v1/images/generations`, `/v1/audio/speech`, `/v1/embeddings`, `/v1/models`)
- **Anthropic Messages + Native Gemini + Ollama surfaces** — `/v1/messages` for Claude Code, native `/v1beta` for Gemini CLI, opt-in Ollama emulation for local-model clients
- **Agent Config Generators** — `npx freellmapi setup-claude` / `setup-codex` and ten more, plus zero-persistence `launch` / `launch-codex` launchers
- **Fusion (multi-model synthesis)** — the virtual `fusion` model fans a prompt to a panel of models and a judge synthesizes one answer
- **React Dashboard** — browser-based management UI for keys, reordering the fallback chain, playground, and p50/p95/TTFT analytics (24h–90d windows)
- **Desktop App** — native Electron menu-bar app with the entire router + dashboard in the tray

## Routing: Six Strategies

The router ranks models on live per-model speed / capability / reliability scores and picks the best available (highest-priority) model with a healthy key that's under all its rate limits. On a 429/5xx it cools that key down and retries the next model in your chain.

| Strategy | Behavior |
|---|---|
| `priority` | Legacy manual chain — the order you set in the Fallback Chain page, plus a 429 penalty |
| `balanced` | **Default** — analytics-driven bandit routing, convex combination of reliability + capability + speed scores |
| `smartest` | Heavily weights the intelligence/capability axis |
| `fastest` | Heavily weights the speed/latency axis |
| `reliable` | Heavily weights the reliability axis (Beta-posterior Thompson sampling) |
| `custom` | User-tuned weight vector persisted in settings |

Strategies are selectable per request via `auto`, `auto:fast`, `auto:smart`, or a profile (`auto:<profile>`), and the same model on several providers collapses into one entry with strict in-group failover. Sticky sessions keep a conversation on one model for 30 minutes; an optional compact handoff note keeps the thread coherent when a mid-chat switch does happen.

## API Surfaces

Beyond the OpenAI-compatible `/v1`, the router speaks several native wire formats over the same fallback chain:

- **Anthropic Messages API** — `/v1/messages` speaks Anthropic's wire format, so Claude Code and official Anthropic SDKs run against your free pool
- **Gemini native `/v1beta`** — `GET /v1beta/models`, `POST /v1beta/models/{model}:generateContent`, `:streamGenerateContent`, `:countTokens` — Gemini CLI speaks its native wire
- **Ollama emulation** — opt-in NDJSON `chat`/`generate`, `tags`, metadata, and embeddings for Zed, JetBrains AI, and other local-model clients
- **MCP server** — agents can introspect usable models, provider health, and routing strategy over `/mcp`; an OpenAPI viewer lives at `/v1/docs`

## Client Config Generators

Most coding agents configure themselves with one command — `npx freellmapi setup-claude --url http://localhost:3001 --api-key <unified-key>` (or `setup-codex`, `setup-aider`, `setup-cline`, and more). Every generator supports `--dry-run`, creates a timestamped backup before touching an existing file, and never clobbers what's already there. Claude Code and Codex also get zero-persistence launchers (`freellmapi launch`, `freellmapi launch-codex`) that inject credentials into the child process only, keeping them out of config files.

## Tech Stack

| Layer | Technology |
|---|---|
| **Runtime** | TypeScript/Node.js 20+ (monorepo) |
| **Workspaces** | `shared`, `server`, `client`, `cli` |
| **Dashboard** | React 19 |
| **Database** | SQLite (better-sqlite3 / drizzle-orm), AES-256-GCM encrypted keys |
| **API Format** | OpenAI-compatible (`/v1`) + Anthropic Messages + Gemini `/v1beta` + Ollama emulation |
| **Desktop** | Electron menu-bar app |
| **CI** | GitHub Actions |
| **Container** | Docker (ghcr.io), multi-arch linux/amd64 + arm64 |

## Deployment

### Docker (recommended)

```bash
docker pull ghcr.io/freellmapi/freellmapi:latest
docker run -d -p 3001:3001 ghcr.io/freellmapi/freellmapi:latest
```

The image serves the API **and** the built React dashboard on port **3001** (ENV PORT=3001 / EXPOSE 3001). Requires an `ENCRYPTION_KEY` for at-rest key storage.

### npm (manual)

```bash
git clone https://github.com/tashfeenahmed/freellmapi.git
cd freellmapi
npm install
npm run build
node server/dist/index.js      # server + dashboard both served on :3001
```

There is **no root `start` script** — the production entry is `node server/dist/index.js` (or `npm run start -w server`, the `server` workspace's own `start` script).

### Docker Compose with ENCRYPTION_KEY + HOST_BIND

```bash
git clone https://github.com/tashfeenahmed/freellmapi.git
cd freellmapi

# Generate an encryption key for at-rest key storage
ENCRYPTION_KEY="$(openssl rand -hex 32)"
printf "ENCRYPTION_KEY=%s\nPORT=3001\n" "$ENCRYPTION_KEY" > .env

docker compose up -d
```

`ENCRYPTION_KEY` is required for startup — provider keys are encrypted at rest with it, so keep the same `.env` and volume when upgrading. In non-production dev it auto-generates a dev key to `.encryption-key` (0600) next to the DB, but don't rely on that fallback with real keys.

**Reaching it from another machine?** By default the container is published only on `127.0.0.1`. To expose it on your LAN (e.g. a Raspberry Pi) start it with:

```bash
HOST_BIND=0.0.0.0 docker compose up -d
```

Only do this on a trusted network: the proxy is single-user and guarded only by the unified API key.

### Development

```bash
npm install
ENCRYPTION_KEY="$(node -e 'console.log(require("crypto").randomBytes(32).toString("hex"))')"
printf "ENCRYPTION_KEY=%s\nPORT=3001\n" "$ENCRYPTION_KEY" > .env
npm run dev    # server on :3001 + Vite dashboard on :5173 with HMR
```

### Desktop App

```bash
npm run desktop:dist    # Build native desktop application
```

The desktop menu-bar app runs the entire router + dashboard from the tray with no account setup — the only credential is the unified API key from the tray popover.

## Configuration

| Env var | Purpose |
|---|---|
| `ENCRYPTION_KEY` | **Required.** Hex key (e.g. `openssl rand -hex 32`) for AES-256-GCM at-rest encryption of provider keys and backups |
| `PORT` | Server port (default `3001`) |
| `HOST_BIND` | Container publish address (`127.0.0.1` default; `0.0.0.0` to expose on the LAN) |
| `FREELLMAPI_DIR` | One-liner install directory (default `~/freellmapi`) |
| `FREEAPI_CONFIG_PATH` / `FREEAPI_CONFIG_JSON` | Declarative startup config (keys, custom providers, models, routing strategy) applied on every boot |
| `FREEAPI_DB_PATH` | SQLite DB location (default `server/data/freeapi.db`) |
| `FREEAPI_DB_BACKUP_PATH` / `FREEAPI_DB_BACKUP_URL` | Encrypted backup target; restored automatically when the DB is missing |
| `REQUEST_ANALYTICS_RETENTION_DAYS` / `REQUEST_ANALYTICS_MAX_ROWS` | Analytics retention (default 90 days / 100k rows) |

## Related

- [[9router]] — AI routing gateway with RTK compression and multi-provider fallback
- [[hermes-agent]] — Multi-platform AI agent that can use FreeLLMAPI as a provider
- [[goclaw]] — Go-based MCP gateway (can integrate FreeLLMAPI as upstream)
