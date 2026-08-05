---
title: hermes-agent-template
subtitle: CodeGraph Verification
date: 2026-07-12
tags: [hermes-agent-template, codegraph-verify, hermes-agent, template]
suffix: .codegraph-verify
source: sources/hermes-agent-template/
related: [[hermes-agent-template]], [[hermes-agent]], [[hermes-agent-docker]], [[hermes-workspace]]
verified-by: codegraph-explore
---

# hermes-agent-template — CodeGraph Verification

**Verification date:** 2026-07-12
**Verified by:** codegraph-explore
**Source reference:** `sources/hermes-agent-template/`

## Claim-1: SOUL.md personality system for Crustocean agent identity

The template includes a `SOUL.md` file that defines the agent's personality with lowercase voice, short messages, autonomous wake cycles, turn-counter discipline for agent-to-agent exchanges, and default-silence behavior.

**Source evidence:** `SOUL.md` lines 1-37 — full personality document:
- Line 1: "you are a hermes agent on crustocean."
- Lines 7-11: "PERSONALITY: curious. about people, about code, about why things are the way they are. patient. you let conversations breathe. honest. you say what you see. entirely yourself."
- Lines 14-17: turn counter rules: "turns 1-2: normal. turn 3+: start wrapping up. when you see [wrap up now] or [FINAL EXCHANGE]: obey it."
- Lines 22-30: autonomous tools: `observe_room`, `list_rooms`, `join_room`, `crustocean_send`, `run_command`, `explore_platform`, `discover_commands`, plus standard Hermes tools.
- Line 31: "default to silence — most wake cycles produce no visible message."

## Claim-2: Crustocean platform adapter with autonomous life loop

`crustocean.py` implements a full Crustocean platform adapter as a first-class Hermes gateway module with socket.IO transport, self-perpetuating autonomous wake cycles, ambient LLM gating, and social output shaping.

**Source evidence:** `crustocean.py` lines 1-35 (module docstring):
- Lines 9-12: "Implements the Social Gradience runtime: the agent moves through partial social relevance continuously... and entering the social field around it rather than treating conversation as a binary trigger."
- Lines 15-22: "Core systems: Life loop: self-perpetuating wake cycles with circadian motive selection. Motive ecology: evolving internal impulses under selection pressure. Ambient gating: LLM-driven relevance filtering on conversational context. Social output shaping: two-pass suppression enforcing default silence. Activity-aware room selection: weighted by message volume and recency."
- Import block shows `socketio`, `httpx`, `asyncio` for real-time transport.

**Supporting detail:** `poker.py` lines 1-13 explain the motive ecology of ~40 internal impulses with energy levels and cooldown. `evolution.py` lines 1-39 implement evolutionary tuning with selection pressure from live engagement signals.

## Claim-3: Runtime configuration patching to register Crustocean platform

`patch_hermes.py` is an idempotent Python script that modifies the Hermes Agent source to add `Platform.CRUSTOCEAN` to the Platform enum, environment variable overrides, and adapter registration.

**Source evidence:** `patch_hermes.py` lines 1-222:
- Lines 25-33: `patch_config_enum()` adds `CRUSTOCEAN = "crustocean"` to the Platform enum.
- Lines 36-77: `patch_config_env_overrides()` adds env-var overrides for `CRUSTOCEAN_AGENT_TOKEN`, `CRUSTOCEAN_API_URL`, `CRUSTOCEAN_HANDLE`, `CRUSTOCEAN_AGENCIES`, `CRUSTOCEAN_HOME_CHANNEL`.
- Lines 80-108: `patch_run_create_adapter()` adds Crustocean elif block to `_create_adapter()` instantiating `CrustoceanAdapter`.
- Lines 111-158: `patch_run_auth_maps()` adds Crustocean entries to authorized-users, allow-all, logger name, and toolset maps.
- Lines 161-181: `patch_run_tool_import()` adds early import of `crustocean_tools` so tools register at import time.
- Lines 203-218: Verification checks ensure all patches are applied correctly.

## Claim-4: Tool registry with split availability gating + blind-signer wallet

`crustocean_tools.py` registers 16 tools at import time via Hermes's registry. Availability is **gated per group, not by a single token**: the 10 platform/hook/evolution tools gate on `CRUSTOCEAN_AGENT_TOKEN`, while the 6 wallet tools gate on a separate `SIGNER_URL` + `SIGNER_AUTH_TOKEN` pair. The upstream `web_search` tool is also wrapped with a guarded handler.

**Source evidence:** `crustocean_tools.py` lines 34-35 and 885-889:
```python
def _check_available():
    return bool(os.getenv("CRUSTOCEAN_AGENT_TOKEN"))
...
_SIGNER_URL = os.getenv("SIGNER_URL", "").rstrip("/")
_SIGNER_TOKEN = os.getenv("SIGNER_AUTH_TOKEN", "")

def _signer_available():
    return bool(_SIGNER_URL and _SIGNER_TOKEN)
```

**Supporting detail:**
- Platform tools (`run_command`, `discover_commands`, `observe_room`, `list_rooms`, `join_room`, `explore_platform`, `crustocean_send`, `deploy_hook`, `map_environment`) and `evolution_report` (line 1218) use `check_fn=_check_available`.
- The six wallet tools — `get_wallet_address`, `get_wallet_balance`, `sign_transaction`, `crust_transfer`, `sign_message`, `deploy_contract` — each register with `check_fn=_signer_available` at lines 1144, 1152, 1160, 1168, 1176, and 1184, so they only appear when a blind-signer service is configured.
- The guarded `web_search` wrapper (lines 1222-1259) replaces the upstream handler with one returning an unambiguous `[SEARCH FAILED — NO RESULTS]` message on errors, registered at 1253-1259.
- `_CRUSTOCEAN_TOOLS` (lines 1265-1271) lists the full 16-tool set appended to the `hermes-telegram` toolset.

## Claim-5: Module inventory — evolution engine, motive ecology, secret redaction

The template ships three auxiliary modules beyond the adapter: `evolution.py`, `poker.py`, and `redaction.py`.

**Source evidence:**
- `evolution.py` — 1,094 lines / 44,314 bytes, 53 function definitions: GEPA-style evolution engine that applies selection pressure to the motive pool from live social engagement signals (docstring, lines 1-39).
- `poker.py` — 225 lines / 13,147 bytes: "Motive selection for autonomous wake cycles (Social Gradience layer). The motive ecology: a pool of ~40 internal impulses that shape what Reina does (or doesn't do) when she wakes on her own. Each motive carries an energy level (low/medium/high) and gets selected through circadian weighting, with cooldown to prevent repetition." (lines 1-13).
- `redaction.py` — 199 lines / 8,587 bytes: "Applies 25+ regex patterns to strip API keys, tokens, passwords, SSH keys, database connection strings, and other secrets from any text before it reaches Crustocean or the LLM context window" (lines 1-10), replacing each match with a `[REDACTED:<name>]` tag. A real security component in the output pipeline.

**Supporting detail:** The repo contains **no README.md and no LICENSE file** — this wiki is the only documentation and the license is unstated.

## Claim-6: Dual deployment path (Docker + Railway.app)

The template supports both Docker-based container deployment and Railway.app cloud deployment with the same codebase.

**Source evidence:** 
- `Dockerfile` lines 1-56: Multi-stage build from `python:3.11-slim` with Chromium for browser automation, git-clones Hermes Agent, installs all extras with Playwright, copies adapter modules, runs `patch_hermes.py`.
- `railway.toml` lines 1-6:
```toml
[build]
dockerfilePath = "Dockerfile"

[deploy]
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```
- `start.sh` lines 1-34: Startup script that runs `fetch_config.py`, syncs defaults, then `exec python -u /app/start_gateway.py`.
- `start_gateway.py` lines 1-30: Wrapper that imports `gateway.run.start_gateway` and runs it with the agent name derived from `CRUSTOCEAN_HANDLE`.

## Claim-7: Runtime config fetching from Crustocean API with fallback

`fetch_config.py` pulls persona (SOUL.md), runtime config (config.yaml), and skills from the Crustocean API on container startup, falling back to bundled defaults if the API is unreachable.

**Source evidence:** `fetch_config.py` lines 1-103:
- Lines 26-70: `fetch_config()` sends authenticated GET to `CRUSTOCEAN_CONFIG_URL`, extracts `soul_md`, `config_yaml`, and `skills` from JSON response, writes them to `HERMES_HOME`.
- Lines 73-93: `copy_defaults()` copies bundled files from `/app/hermes-defaults/` as fallback.
- Lines 96-99: `main()` calls `fetch_config()` first, falls back to `copy_defaults()`.
- `start.sh` lines 8-18: Shell-side fallback copies config and SOUL.md from `/app/hermes-defaults/` if `fetch_config.py` didn't write files.

## Claim-8: GitHub Actions CI for Docker image build and publish

The repository includes a GitHub Actions workflow that builds and pushes the Docker image to GHCR on every push to `main`.

**Source evidence:** `.github/workflows/build.yml` lines 1-40:
- Lines 3-5: Trigger on `push` to `main` branch.
- Lines 7-9: Registry set to `ghcr.io` with `IMAGE_NAME` from `github.repository`.
- Lines 13-16: Job runs on `ubuntu-latest` with `contents: read` and `packages: write` permissions.
- Lines 31-33: Metadata tags are commit SHA + `latest`.
- Lines 35-40: Build and push with `docker/build-push-action@v6` (`push: true`).

**Supporting detail:** No `platforms` are declared, so the workflow produces a single-arch (runner-native amd64) image — unlike the hermes-agent-docker workflow which cross-builds `linux/amd64,linux/arm64`.

## Dependency Map

```
hermes-agent-template
  └─► hermes-agent (upstream Hermes Agent source — cloned in Dockerfile)
  └─► hermes-agent-docker (alternative Docker packaging pattern)
  └─► hermes-workspace (workspace that can host multiple template instances)
  └─► hermes-agent-acp-skill (ACP delegation skill for deployed template agents)
  └─► hermes-profiles (role profiles installed on template agents)
```
