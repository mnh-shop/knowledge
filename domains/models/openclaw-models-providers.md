---
name: openclaw-models-providers
tags: [agent-gateway, api, cli, llm, models, oauth, ollama, openclaw, plugin-sdk, providers, typescript]
description: OpenClaw Models and Providers
source: sources/openclaw/
---

# OpenClaw Models and Providers
**Source:** `sources/openclaw/`

OpenClaw supports a large catalog of LLM model providers plus local model services. Each provider is a plugin with an auth flow, model catalog, streaming, and replay policy. The provider directory is `docs/providers/index.md` (68 provider pages); model selection, OAuth, and failover are documented under `docs/concepts/model-providers.md`, `docs/concepts/oauth.md`, and `docs/concepts/model-failover.md`.

## Provider Catalog

The starter set from `docs/providers/models.md` plus the full `docs/providers/index.md` directory covers ~40+ providers, including:

- **Anthropic** — API key + Claude CLI / subscription auth reuse (`docs/providers/anthropic.md`)
- **OpenAI** — API key + ChatGPT OAuth + Codex (`docs/providers/openai.md`)
- **Google** — Gemini (`docs/providers/google.md`)
- **xAI** (`docs/providers/xai.md`)
- **OpenRouter** (`docs/providers/openrouter.md`)
- **GitHub Copilot** — OAuth subscription auth (`docs/providers/github-copilot.md`)
- **MiniMax**, **Mistral**, **Moonshot/Kimi**, **Qwen**, **DeepSeek**, **StepFun**, **Z.AI (GLM)**, **Cohere**, **Groq**, **Cerebras**, **NVIDIA**, **Hugging Face**, **Fireworks**, **DeepInfra**, **Together**, **Novita**, **Featherless**, **Gradium**, **GMI Cloud**, **Vercel AI Gateway**, **Cloudflare AI Gateway**, **Alibaba Model Studio**, **Qianfan**, **Volcengine**, **BytePlus**, **Amazon Bedrock**, **Baseten**, **Chutes**, **fal**, **Runway**, **Synthetic**, **OpenCode (Zen + Go)**, **Kilocode**, **Arcee**, **LongCat**, **ClawRouter** (managed multi-provider routing), **ElevenLabs**
- **Any OpenAI/Anthropic-compatible endpoint** — via `litellm`, `vercel-ai-gateway`, `cloudflare-ai-gateway`, `clawrouter`, and the compatible-endpoint provider pattern

Additional variants: `anthropic-vertex` (implicit Vertex support), `copilot-proxy` (local VS Code Copilot Proxy bridge), `google-gemini-cli` (unofficial Gemini CLI OAuth).

### Local Model Services

Local/self-hosted services are first-class providers: **Ollama** (`extensions/ollama`), **LM Studio** (`extensions/lmstudio`), **vLLM** (`extensions/vllm`), **llama.cpp** (`extensions/llama-cpp`), **sglang** (`extensions/sglang`), plus **inferrs** and **ds4** (local DeepSeek V4) provider pages.

## Authentication

- **API keys** — set via `openclaw onboard` or `openclaw models auth login`; secrets stored in the auth profile system (`~/.openclaw/agents/<agentId>/agent/auth-profiles.json` or `auth-profiles.json`).
- **OAuth / subscription auth** (`docs/concepts/oauth.md`) — PKCE token exchange supported for providers that offer it: **OpenAI Codex (ChatGPT OAuth)** and **Anthropic Claude CLI reuse**. GitHub Copilot OAuth is handled by the copilot provider plugin (`github-copilot.ts` in `src/llm/`, `provider-openai-chatgpt-oauth.ts`).
- Both OpenAI API-key and ChatGPT/Codex OAuth live under the canonical provider id `openai`; legacy `openai-codex:*` profile ids are repaired by `openclaw doctor --fix`.

## Model Failover and Auth-Profile Rotation

`docs/concepts/model-failover.md` describes two-stage failure handling:

1. **Auth profile rotation** within the current provider — the runtime rotates through configured auth profiles with cooldowns.
2. **Model fallback** — falls back to the next model in `agents.defaults.model.fallbacks`.

Configured defaults, cron job primaries, and auto-selected fallback models can use configured fallbacks; explicit user session selections are strict (no fallback). Session model overrides interact with fallback retries; provider/model resolution and routing code lives in `src/llm/model-registry.ts`, `src/llm/model-runtime-binding.ts`, `src/llm/providers/`, and `src/plugins/provider-model-*.ts`.

## Provider Plugin Contract

Providers are a plugin kind with a dedicated SDK and runtime surface:

- **SDK** — `src/plugin-sdk/provider-entry.ts`, `provider-auth.ts`, `provider-oauth-runtime.ts`, `provider-setup.ts`, `provider-stream.ts`, `provider-tools.ts`, `provider-catalog-runtime.ts`, `provider-model-types.ts`
- **Core runtime** — `src/plugins/providers*.ts`: `provider-runtime.ts`, `provider-discovery.ts`, `provider-validation.ts`, `provider-catalog.ts`, `provider-wizard.ts`, `provider-oauth-flow.ts`, `provider-api-key-auth.ts`, `provider-auth-choice.ts`, `provider-model-routes.ts`, `provider-model-compat.ts`, `provider-thinking.ts`, `provider-replay-helpers.ts`
- **Wizard/setup** — `provider-wizard.ts`, `provider-setup.ts`, `provider-self-hosted-setup.ts`, `provider-install-catalog.ts`
- Provider extensions in `extensions/` (each with `openclaw.plugin.json`): `anthropic`, `openai`, `google`, `xai`, `openrouter`, `ollama`, `lmstudio`, `vllm`, `llama-cpp`, `sglang`, `litellm`, `microsoft`, `amazon-bedrock`, `amazon-bedrock-mantle`, `deepseek`, `qwen`, `moonshot`, `minimax`, `mistral`, `groq`, `cerebras`, `together`, `openrouter`, `cohere`, `huggingface`, `novita`, `featherless`, `gradium`, `fireworks`, `deepinfra`, `baseten`, `chutes`, `fal`, `runway`, `pixverse`, `volcengine`, `qianfan`, `alibaba`, `tencent`, `xiaomi`, `zai`, `stepfun`, `kilocode`, `gmi`, `synthetic`, `copilot`, `copilot-proxy`, `clawrouter`, `vercel-ai-gateway`, `cloudflare-ai-gateway`, `openai`-family media providers, and more.

## LLM Core (`src/llm/`)

- `stream.ts` — streaming completion host (`stream.sync-host.ts`, `stream.complete-host.ts`)
- `model-registry.ts` — model registry and routing
- `model-runtime-binding.ts` — session-to-model binding
- `oauth.ts`, `github-copilot-oauth-types.ts`, `openai-compatible-auth.ts` — auth helpers
- `ai-transport-host.ts`, `providers/`, `utils/` — transport adapters and utilities

## CLI

| Command | Purpose | Source |
|---------|---------|--------|
| `openclaw models` | list/status/auth login/logout for model providers | `src/cli/models-cli.ts` |
| `openclaw promos` | provider promotional model listings | `src/cli/promos-cli.ts` |
| `openclaw infer` | one-shot inference against a model | `src/cli/capability-cli.ts` |
| `openclaw capability` | capability detection/selection | `src/cli/capability-cli.ts` |
| `openclaw onboard` | provider auth onboarding wizard | `src/cli/run-main.ts` |

Gateway RPC surfaces: `models.list`, `models.authStatus`, `models.authLogout`, and OpenAI-compatible HTTP endpoints (`/v1/models`, `/v1/chat/completions`, `/v1/responses`, `/v1/embeddings`).

## Key Source Files

| File | Purpose |
|------|---------|
| `docs/providers/index.md` | Full provider directory (68 pages) |
| `docs/concepts/model-providers.md` | Model selection and provider concepts |
| `docs/concepts/oauth.md` | OAuth token exchange, storage, multi-account |
| `docs/concepts/model-failover.md` | Auth-profile rotation + model fallback |
| `src/llm/model-registry.ts` | Model registry |
| `src/llm/stream.ts` | Streaming completions |
| `src/plugins/provider-runtime.ts` | Provider plugin runtime |
| `src/plugins/provider-oauth-flow.ts` | OAuth flow for providers |
| `src/cli/models-cli.ts` | models CLI |
| `extensions/{anthropic,openai,google,ollama,lmstudio,vllm,...}/` | Provider plugin implementations |

## Related

- [[domains/architecture/openclaw-architecture.md]] — Overall system architecture
- [[domains/plugins/openclaw-plugins.md]] — Provider plugin contract and lifecycle
- [[wiki/openclaw.md]] — Wiki entry
