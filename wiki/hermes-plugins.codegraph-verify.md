---
name: hermes-plugins-codegraph-verify
tags: [hermes-plugins, codegraph-verify, hermes-agent, plugin, python, autonomy, evey]
description: "Codegraph Verification: Hermes Plugins (evey-*) — validating wiki claims against indexed source code symbols"
source: sources/hermes-plugins/
---

# Codegraph Verification: Hermes Plugins

**Date:** 2026-07-12 (claims re-validated against source)

## Claim 1: 34 evey-* plugins; README is stale ("23 custom plugins")
- **Wiki says:** 34 custom plugins for hermes-agent, prefixed `evey-*`. Repository at `42-evey/hermes-plugins` (MIT licensed). The README still claims 23 plugins.
- **Source evidence:**
  - 34 `evey-*` directories confirmed at repo root (listing of `sources/hermes-plugins/`): evey-autonomy, evey-bridge, evey-cache, evey-commands, evey-cost-guard, evey-council, evey-delegate-model, evey-delegation-score, evey-digest, evey-email-guard, evey-github, evey-goals, evey-habits, evey-identity, evey-learner, evey-memory-adaptive, evey-memory-consolidate, evey-moltbook, evey-mqtt, evey-news, evey-proactive, evey-rag, evey-reflect, evey-research, evey-sandbox, evey-scheduler, evey-session-guard, evey-status, evey-telegram-ux, evey-telemetry, evey-validate, evey-verification, evey-wallet, evey-watchdog
  - `README.md:6` — "23 custom plugins for hermes-agent..." (11 plugins missing from README tables: commands, github, habits, moltbook, news, proactive, rag, scheduler, verification, wallet, watchdog)
  - `LICENSE` confirms MIT License ("Copyright (c) 2026 Evey")
- **Verdict:** ✅ CORRECT (count confirmed; README staleness flagged as upstream gap)

## Claim 2: 33 of 34 plugins have `plugin.yaml`; evey-commands uses `register_command()` instead
- **Wiki says:** Each plugin has a `plugin.yaml` manifest and `__init__.py` exposing `register(ctx)`, except evey-commands which uses the upstream `register_command()` API.
- **Source evidence:**
  - `evey-commands/` contains only `__init__.py` — no `plugin.yaml` (directory listing)
  - `evey-commands/__init__.py:3-4` — "Uses the new upstream register_command() API (hermes-agent #2359) to add slash commands that appear in /help, tab-complete, Telegram, and gateway"
  - `evey-commands/__init__.py:117-120` — `def register(ctx)` calls `ctx.register_command(...)` (with fallback "Older hermes versions without register_command — silently skip")
  - Representative manifests: `evey-autonomy/plugin.yaml` (`provides_tools: [autonomous_decide, autonomous_plan, autonomous_reflect]`), `evey-cost-guard/plugin.yaml` (`version: 2.0.0`), `evey-council/plugin.yaml`
  - `evey_utils.py` at repo root provides shared utilities: `call_llm()`, `call_model()`, `http_get()`, `http_get_json()`, `http_post_json()` with retry logic
- **Verdict:** ✅ CORRECT (33/34 with plugin.yaml; evey-commands is the documented exception)

## Claim 3: evey-autonomy version is 1.1.0 (corrected from 1.0.0)
- **Wiki says:** evey-autonomy (v1.1.0) — core autonomy engine with `autonomous_decide`, `autonomous_plan`, `autonomous_reflect`.
- **Source evidence:**
  - `evey-autonomy/plugin.yaml:2` — `version: 1.1.0` (was previously mis-cited as 1.0.0)
  - `evey-autonomy/plugin.yaml:4-6` — `provides_tools: [autonomous_decide, autonomous_plan, autonomous_reflect]`
  - `evey-autonomy/__init__.py` implements `TIME_PROFILES` (5 time blocks), `_get_hour()` time-of-day routing (Europe/Berlin), planning templates, and stdlib-only heuristic reflection
- **Verdict:** ✅ CORRECT (version corrected to 1.1.0 per plugin.yaml)

## Claim 4: evey-sandbox is a secure file reader with PII scrubbing — NOT code execution
- **Wiki says:** evey-sandbox is "Evey Secure Reader" — reads files from V-approved folders with PII scrubbing. No Docker, no code execution. Tools: `secure_read`, `secure_search`, `sandbox_list`.
- **Source evidence:**
  - `evey-sandbox/__init__.py:1-3` — docstring: "Evey Secure Reader — read files from V-approved folders with PII scrubbing. Fast tool. No Docker, no code execution. Just read + clean + return."
  - `evey-sandbox/__init__.py:18-25` — `PII_PATTERNS` inline regex list (email, phone, ID number, card, API key, IP)
  - `evey-sandbox/__init__.py:27` — `MAX_FILE_SIZE = 500_000`; lines 29-33 — extension allowlist; lines 96-103 — `_scrub_pii()`; lines 87-93 — `_is_allowed()` folder whitelist check
  - `evey-sandbox/__init__.py:306-309` — `register(ctx)` registers tools named `secure_read`, `secure_search`, `sandbox_list` (NOT `sandbox_read`/`sandbox_search`)
  - `evey-sandbox/plugin.yaml:2-3` — description "Run code in sandboxed Docker containers with read-only folder access" is STALE/misleading; the code is authoritative
- **Verdict:** ✅ CORRECT (rewritten as secure reader; stale plugin.yaml description flagged)

## Claim 5: External-service topology via Docker service names + LiteLLM env
- **Wiki says:** plugins reference fixed Docker services (hermes-qdrant:6333, hermes-ntfy:80, hermes-searxng:8080, hermes-crawl4ai:11235, hermes-dashboard:8088, hermes-ollama:11434) and route LLM calls through LiteLLM via `OPENAI_BASE_URL`.
- **Source evidence:**
  - `evey-memory-consolidate/__init__.py:18` — `QDRANT_URL = "http://hermes-qdrant:6333"`; `evey-rag/__init__.py:11` — same
  - `evey-digest/__init__.py:15` and `evey-watchdog/__init__.py:22` — `NTFY_URL = ... "http://hermes-ntfy:80"`
  - `evey-news/__init__.py:18` — `SEARXNG_URL = ... "http://hermes-searxng:8080"`
  - `evey-research/__init__.py:16` — `CRAWL4AI_URL = "http://hermes-crawl4ai:11235"`
  - `evey-status/__init__.py:16` and `evey-commands/__init__.py:19` — `DASHBOARD_URL = ... "http://hermes-dashboard:8088"`
  - `evey-memory-consolidate/__init__.py:19` — `OLLAMA_URL = "http://hermes-ollama:11434"`
  - `evey_utils.py:19-20` — `LITELLM_URL = os.environ.get("OPENAI_BASE_URL", "")`, `LITELLM_KEY = os.environ.get("OPENAI_API_KEY", "")`
- **Verdict:** ✅ CORRECT (topology table added to wiki)

## Claim 6: Shared utility layer (`evey_utils.py`) with retry + reasoning recovery
- **Wiki says:** all plugins share `evey_utils.py` for LLM calls (`call_llm`, `call_model`) with exponential-backoff retry and reasoning recovery, plus HTTP helpers.
- **Source evidence:**
  - `evey_utils.py:23-26` — `call_llm()` delegates to `call_model()`
  - `evey_utils.py:29-90` — `call_model()` retry loop `for attempt in range(1, retries + 2)` with `time.sleep(2 ** (attempt - 1))` exponential backoff (lines 71, 84)
  - `evey_utils.py:59-67` — reasoning recovery: extracts `reasoning_content`/`reasoning`/`provider_specific_fields.reasoning_content` when content is empty
  - `evey_utils.py:93-100` — `http_get()` with error handling
- **Verdict:** ✅ CORRECT

## Claim 7: Cost governance, council debate, delegation chain, memory pipeline
- **Wiki says:** evey-cost-guard (v2.0.0) enforces $1.00 daily / $0.25 per-task budgets via Langfuse with 3 tools; evey-council debates with COUNCIL_MODELS + JUDGE_MODEL; evey-delegate-model routes through a 4-model chain with sensitive-content local-only filter and parallel delegation ≤6; memory stack uses Qdrant + snowflake-arctic-embed2 with 14-day half-life decay and 500-entry learning store.
- **Source evidence:**
  - `evey-cost-guard/plugin.yaml` — `version: 2.0.0`, `provides_tools: [cost_check, cost_set_budget, cost_analytics]`
  - `evey-council/__init__.py:25-32` — `COUNCIL_MODELS = ["mimo-v2-pro", "llama70b-free", "qwen-coder-free"]`, `JUDGE_MODEL = "mimo-v2-pro"`
  - `evey-delegate-model/__init__.py:93` — `SENSITIVE_PATTERNS` list; `:123-126` — local-only routing on sensitive match; `:276`/`:353` — `delegate_parallel`
  - `evey-memory-consolidate/__init__.py:18-22` — `QDRANT_URL = "http://hermes-qdrant:6333"`, `EMBED_MODEL = "snowflake-arctic-embed2"`
  - `evey-memory-adaptive/__init__.py:38-41` — `_decay_score(importance, last_accessed, half_life_days=14)` exponential decay
  - `evey-learner/__init__.py:24` — `MAX_LEARNINGS = 500`
- **Verdict:** ✅ CORRECT

## Claim 8: Safety, observability, and watchdog constants
- **Wiki says:** evey-email-guard screens with qwen35-4b + 20+ INJECTION_PATTERNS; evey-watchdog alerts after 120 silent minutes during 9am-9pm work hours; evey-telemetry rotates at 10MB; evey-validate returns TRUST/CAUTION/REJECT.
- **Source evidence:**
  - `evey-email-guard/__init__.py:22` — `SCREENING_MODEL = "qwen35-4b"  # local, FREE, fast`; `:25+` — `INJECTION_PATTERNS` regex list
  - `evey-watchdog/__init__.py:23` — `SILENT_THRESHOLD_MINUTES = 120`; `:22` — `NTFY_URL = ... "http://hermes-ntfy:80"`; `:24` — `WORK_HOURS = (9, 21)`; `:4` — "hours (9am-9pm), sends an alert to ntfy"
  - `evey-telemetry/__init__.py:22` — `MAX_EVENTS_FILE_SIZE = 10 * 1024 * 1024  # 10MB before rotation`
  - `evey-validate/__init__.py:113-117` — score thresholds: `>= 7` → TRUST, `>= 4` → CAUTION, else REJECT
- **Verdict:** ✅ CORRECT

## Summary

All 8 claims from the Hermes Plugins wiki have been verified against the source:
- ✅ 34 evey-* plugins (README stale at "23")
- ✅ 33/34 with plugin.yaml; evey-commands uses `register_command()`
- ✅ evey-autonomy version corrected to 1.1.0
- ✅ evey-sandbox rewritten as secure PII-scrubbing file reader (no Docker/code execution)
- ✅ External-service topology table added (qdrant/ntfy/searxng/crawl4ai/dashboard/ollama + LiteLLM env)
- ✅ evey_utils.py retry + reasoning recovery confirmed
- ✅ Cost/council/delegation/memory constants confirmed
- ✅ Safety/observability/watchdog constants confirmed

## Related

- [[hermes-plugins]] -- Main wiki entry
- [[hermes-agent.codegraph-verify]] -- Codegraph verification for upstream Hermes Agent
- [[hermes-agent]] -- Host framework for all evey-* plugins

## Cross-project

- [[hermes-workspace.codegraph-verify]] -- Codegraph verification for Hermes Workspace
- [[hermes-bus.codegraph-verify]] -- Codegraph verification for Hermes Bus
- [[oh-my-hermes]] -- Alternative plugin/composition system for Hermes Agent
