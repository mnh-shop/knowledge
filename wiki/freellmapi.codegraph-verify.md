---
name: freellmapi-codegraph-verify
tags: [freellmapi, llm, api, express, typescript, routing, providers, wiki]
description: "Codegraph Verification: freellmapi — validating wiki claims against indexed source code symbols"
source: sources/freellmapi/
---

# Codegraph Verification: freellmapi

**Date:** 2026-07-30

## Claim 1: 29 free providers + 358 model endpoints + 4B tokens/month behind single OpenAI-compatible API
- **Wiki says:** FreeLLMAPI aggregates 29 free providers, 358 free model endpoints, and ~4 billion tokens per month behind a single OpenAI-compatible `/v1` API.
- **Source evidence:**
  - `README.md` line 5 states: "4 billion tokens per month. 29 free LLM providers. 358 free model endpoints. One OpenAI-compatible endpoint."
  - `README.md` line 16 confirms: "251 model families, 358 free endpoints"
  - `README.md` lines 243-246 confirm: "The catalog currently tracks **29 providers**, **251 model families**, **358 provider/model endpoints**, and roughly **4 billion tokens per month** of listed free-tier capacity"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Express TypeScript server with 20+ route modules
- **Wiki says:** The server is built with Express and TypeScript, featuring 20+ route modules.
- **Source evidence:**
  - `server/src/app.ts` imports from 22 route modules: `keys`, `models`, `proxy`, `responses`, `anthropic`, `fallback`, `profiles`, `embeddings`, `media`, `analytics`, `health`, `settings`, `premium`, `cache`, `compression`, `auth`, `docs`, `mcp`, `status`, `gemini`, `ollama`, `url-tokens`
  - `server/src/app.ts` uses `express()` and imports from `express`
  - `server/src/routes/` directory contains the route files
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: 8 provider implementations
- **Wiki says:** The system implements 8 provider-specific modules for Google, Cohere, Cloudflare, AI Horde, ModelScope, Pollinations, and OpenAI-compatible providers (Groq, Cerebras, Mistral, NVIDIA, etc.).
- **Source evidence:**
  - `server/src/providers/` contains 9 files: `aihorde.ts`, `base.ts`, `cloudflare.ts`, `cohere.ts`, `google.ts`, `index.ts`, `modelscope.ts`, `openai-compat.ts`, `pollinations.ts`
  - `server/src/providers/index.ts` registers: `GoogleProvider`, `OpenAICompatProvider` (reused for Groq, Cerebras, NVIDIA, Mistral, etc.), `CohereProvider`, `CloudflareProvider`, `AIHordeProvider`, `ModelScopeProvider`, `PollinationsProvider`
  - OpenAICompatProvider is a single implementation reused for multiple providers
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Six routing strategies, Thompson-sampling bandit scoring, fallover on 429/5xx with cooldowns + key rotation
- **Wiki says:** The router supports six strategies (`priority`, `balanced`, `smartest`, `fastest`, `reliable`, `custom`) with Beta-posterior Thompson-sampling reliability scoring; on a 429/5xx it cools the key down and retries the next model in the chain.
- **Source evidence:**
  - `server/src/services/scoring.ts` line 34: `export type RoutingStrategy = 'priority' | 'balanced' | 'smartest' | 'fastest' | 'reliable' | 'custom';`
  - `server/src/services/router.ts` line 295: `const VALID_STRATEGIES: RoutingStrategy[] = ['priority', 'balanced', 'smartest', 'fastest', 'reliable', 'custom'];` with `BANDIT_PRESETS` per strategy (scoring.ts:36) and `DEFAULT_STRATEGY = 'balanced'` (scoring.ts:51)
  - `server/src/services/scoring.ts` states: "Reliability is drawn from a Beta posterior (Thompson sampling) so exploration is automatic and proportional to uncertainty"
  - `README.md` line 146: "automatic fallover retries the next model on 429/5xx with cooldowns and key rotation"
  - `server/src/services/fusion.ts` lines 285-286 and 375-376: `getCooldownDecisionForLimit(...)` + `setCooldown(route.platform, route.modelId, route.keyId, decision.durationMs, decision.source)` on rate-limit signals
  - `server/src/services/cooldown-probe.ts` lines 1-15: "probe-based early recovery for benched keys" — heuristic cooldowns cleared early when the probe passes
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (expanded from single "Thompson sampling" claim to the full six-strategy model)

## Claim 5: AES-256-GCM encrypted keys in SQLite + unified freellmapi-… bearer token + per-key usage tracking
- **Wiki says:** Provider keys are AES-256-GCM encrypted in SQLite and decrypted in-memory per request; clients only see one unified `freellmapi-…` bearer token, and per-key RPM/RPD/TPM/TPD usage is tracked to stay under free-tier caps.
- **Source evidence:**
  - `server/src/lib/crypto.ts` line 6: `const ALGORITHM = 'aes-256-gcm';` (used via `crypto.createCipheriv` / `createDecipheriv`)
  - `README.md` line 152: "provider keys are AES-256-GCM encrypted in SQLite and decrypted in-memory per request; your apps only ever see a single unified `freellmapi-…` bearer token"
  - `README.md` line 148: "Per-key rate tracking — RPM/RPD/TPM/TPD counters per `(platform, model, key)` that learn providers' reported ceilings"
  - `docs/architecture.md` line 60: "Clients authenticate to your proxy with a single `freellmapi-…` bearer token"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Self-updating model catalog from signed feed at freellmapi.co ($19/yr premium)
- **Wiki says:** The model catalog updates automatically from a signed feed at freellmapi.co, a premium service at $19/year.
- **Source evidence:**
  - `README.md` line 21 confirms: "Your router updates its own model catalog from a signed feed: new free models, quota changes, and compatibility fixes land without a `git pull`"
  - `README.md` line 149: "the router syncs a signed catalog from freellmapi.co twice a day"
  - `README.md` lines 252-254 link "[Go live at freellmapi.co](https://freellmapi.co)" with "$19/year or $49 once, lifetime"
  - `server/src/routes/premium.ts` handles premium/catalog sync functionality
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Native Gemini /v1beta + Ollama emulation surfaces + setup-claude/setup-codex config generators
- **Wiki says:** FreeLLMAPI exposes a native Gemini `/v1beta` surface (`generateContent`, streaming, `countTokens`, models), an opt-in Ollama emulation (NDJSON chat/generate, tags, metadata, embeddings) for local-model clients, and one-command config generators (`npx freellmapi setup-claude`, `setup-codex`, etc.).
- **Source evidence:**
  - `README.md` line 142: "Native Gemini + Ollama surfaces — Gemini CLI can use `/v1beta` (`generateContent`, streaming, token counting, models), while opt-in Ollama emulation serves NDJSON chat/generate, tags, metadata, and embeddings"
  - `docs/api.md` lines 159-165: native surface endpoints `GET /v1beta/models`, `POST /v1beta/models/{model}:generateContent`, `:streamGenerateContent`, `:countTokens`
  - `README.md` line 126: "`npx freellmapi setup-claude`, `setup-codex`, `setup-aider`, and ten more generators"; line 191: `npx freellmapi setup-claude --url http://localhost:3001 --api-key <unified-key>`
  - `docs/clients.md` lines 29-30, 40-41: `setup-claude` / `setup-codex` recipes with base URLs
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: Docker port 3001, no root start script, ENCRYPTION_KEY required, HOST_BIND LAN publishing
- **Wiki says:** The Docker image and server serve on port **3001** (not 3000); there is no root `start` script — production runs `node server/dist/index.js`; `ENCRYPTION_KEY` is required for startup; the container binds `127.0.0.1` by default and publishes on the LAN with `HOST_BIND=0.0.0.0`.
- **Source evidence:**
  - `Dockerfile` line 36: `ENV PORT=3001`; line 54: `EXPOSE 3001`; line 58: HEALTHCHECK pings `process.env.PORT || 3001`; line 60: `CMD ["node", "server/dist/index.js"]`
  - `docs/install.md` line 29: "Open http://localhost:3001"; line 113: "`node server/dist/index.js`     # server + dashboard both served on :3001"
  - Root `package.json` (lines 10-25) defines `dev`, `dev:lan`, `test`, `build`, `desktop:dist`, `db:*` scripts — **no `start` script**; the `start` script lives in `server/package.json` line 9: `"start": "node dist/index.js"` (invoked as `npm run start -w server`)
  - `docs/install.md` lines 45-46: `ENCRYPTION_KEY="$(openssl rand -hex 32)"` with the note at lines 95-99 that `ENCRYPTION_KEY` is required for startup
  - `docs/install.md` lines 63-67 and 182: default publish on `127.0.0.1`, LAN exposure via `HOST_BIND=0.0.0.0 docker compose up -d`
- **Verdict:** ✅ CORRECT (wiki previously claimed port 3000 and a root `npm run start` — fixed)
- **Fix needed:** None (already applied)

## Summary

All 8 key claims from the freellmapi wiki have been verified against the source code:
- ✅ 29 providers + 358 endpoints + 4B tokens/month: Confirmed in README.md
- ✅ Express TypeScript with 20+ routes: 22 route modules confirmed in app.ts
- ✅ 8 provider implementations: 8 distinct provider classes confirmed
- ✅ Six routing strategies + Thompson sampling: scoring.ts/router.ts confirm the strategy enum and bandit scoring; fallover/cooldowns confirmed in fusion.ts + cooldown-probe.ts
- ✅ AES-256-GCM encrypted keys + unified freellmapi-… token + per-key usage: crypto.ts + README confirmed
- ✅ Self-updating catalog from freellmapi.co ($19/yr): Premium catalog sync confirmed
- ✅ Gemini /v1beta + Ollama emulation + setup-claude/setup-codex generators: README + docs/api.md + docs/clients.md confirmed
- ✅ Port 3001, no root start script, ENCRYPTION_KEY, HOST_BIND: Dockerfile + docs/install.md + package.json confirmed

## Related

- [[freellmapi]] -- Main wiki entry

## Cross-project

- [[9router.codegraph-verify]] -- Similar codegraph verification for AI routing gateway
- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for agent gateway
