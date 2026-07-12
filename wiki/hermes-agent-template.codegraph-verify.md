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

## Claim-4: Comprehensive tool registry with 16+ Crustocean-specific tools

`crustocean_tools.py` registers tools at import time via Hermes's registry, including slash commands, room traversal, wallet operations, and hook deployment. All tools gate availability on `CRUSTOCEAN_AGENT_TOKEN`.

**Source evidence:** `crustocean_tools.py` lines 1-1289:
- Lines 34-35: `_check_available()` gates all tools on `bool(os.getenv("CRUSTOCEAN_AGENT_TOKEN"))`.
- Lines 3-10: Docstring lists "run_command, discover_commands, observe_room, traverse the platform, and join new rooms."
- Line 7: "Tools register at import time via registry.register()."
- Line 40+: Contains schemas for multiple tools: `RUN_COMMAND_SCHEMA`, `DISCOVER_COMMANDS_SCHEMA`, `OBSERVE_ROOM_SCHEMA`, `LIST_ROOMS_SCHEMA`, `JOIN_ROOM_SCHEMA`, `CRUSTOCEAN_SEND_SCHEMA`, plus wallet tools (`get_wallet_address`, `get_wallet_balance`, `sign_transaction`, `crust_transfer`, `sign_message`, `deploy_contract`), `deploy_hook`, `map_environment`, and `evolution_report`.

## Claim-5: Dual deployment path (Docker + Railway.app)

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

## Claim-6: Runtime config fetching from Crustocean API with fallback

`fetch_config.py` pulls persona (SOUL.md), runtime config (config.yaml), and skills from the Crustocean API on container startup, falling back to bundled defaults if the API is unreachable.

**Source evidence:** `fetch_config.py` lines 1-103:
- Lines 26-70: `fetch_config()` sends authenticated GET to `CRUSTOCEAN_CONFIG_URL`, extracts `soul_md`, `config_yaml`, and `skills` from JSON response, writes them to `HERMES_HOME`.
- Lines 73-93: `copy_defaults()` copies bundled files from `/app/hermes-defaults/` as fallback.
- Lines 96-99: `main()` calls `fetch_config()` first, falls back to `copy_defaults()`.
- `start.sh` lines 8-18: Shell-side fallback copies config and SOUL.md from `/app/hermes-defaults/` if `fetch_config.py` didn't write files.

## Claim-7: GitHub Actions CI for Docker image build and publish

The repository includes a GitHub Actions workflow that builds and pushes the Docker image to GHCR on every push to `main`.

**Source evidence:** `.github/workflows/build.yml` lines 1-40:
- Lines 3-5: Trigger on `push` to `main` branch.
- Lines 7-9: Registry set to `ghcr.io` with `IMAGE_NAME` from `github.repository`.
- Lines 13-16: Job runs on `ubuntu-latest` with `contents: read` and `packages: write` permissions.
- Lines 19-39: Steps: checkout → docker login → metadata (SHA + latest tags) → build and push with `docker/build-push-action@v6`.

## Dependency Map

```
hermes-agent-template
  └─► hermes-agent (upstream Hermes Agent source — cloned in Dockerfile)
  └─► hermes-agent-docker (alternative Docker packaging pattern)
  └─► hermes-workspace (workspace that can host multiple template instances)
  └─► hermes-agent-acp-skill (ACP delegation skill for deployed template agents)
  └─► hermes-profiles (role profiles installed on template agents)
```
