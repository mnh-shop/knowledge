---
name: hermes-plugins
description: "34 evey-* plugins extending hermes-agent with autonomous decision-making, observability, cost control, memory, safety guards, and external integrations"
source: sources/hermes-plugins/
tags: [cli, hermes-agent, dashboard, developer-tools, docker, event-bus, git, messaging, monitoring, multi-platform, orchestration, plugin, skills-platform, storage, python, hermes-plugins]
---

# Hermes Plugins (evey-*)

**Source:** `sources/hermes-plugins/`

34 custom plugins for the [hermes-agent](https://github.com/NousResearch/hermes-agent) framework, prefixed `evey-*`. Built for Evey, an autonomous AI agent that runs 24/7 on free/open-weight models via LiteLLM (OpenRouter + Ollama + Nous Portal). The plugin ecosystem covers autonomy, observability, cost control, safety, memory, learning, communication, and external service integration.

Repository: `42-evey/hermes-plugins` (MIT licensed).

## Key Features

- **Autonomous decision engine** -- priority queue with time-of-day routing, structured planning templates, and self-reflection scoring
- **Multi-model orchestration** -- smart task-type routing, 4-model fallback chain, parallel delegation (up to 6 concurrent), and a 3-model debate ("Council") with a judge
- **Cost governance** -- daily and per-task budgets enforced via Langfuse analytics, per-model cost breakdowns, budget recommendations
- **Self-monitoring stack** -- structured JSON telemetry for every tool call/delegation/error, auto-rotating logs, silent-period watchdog with ntfy alerts
- **Memory system** -- importance-scored and decayed memories, nightly consolidation into MEMORY.md + Qdrant vector store, experiential learning from past interactions
- **Safety guards** -- dual-layer prompt injection screening (regex + local LLM) for incoming email, output hallucination validation, session checkpoints, sandboxed execution
- **External integrations** -- MQTT event bus, bidirectional Claude Code bridge, Telegram UX, Moltbook social network, crypto wallet monitoring, GitHub repo status, web research
- **Shared utility layer** -- `evey_utils.py` with retry logic (exponential backoff), HTTP helpers used across all plugins

## Architecture

Each plugin is a self-contained directory (`evey-*`) with:

- `plugin.yaml` -- manifest (name, version, description, `provides_tools` list)
- `__init__.py` -- implementation exposing a `register(ctx)` function that registers tool schemas with the hermes-agent framework

Plugins share `evey_utils.py` for LLM calls (`call_llm`, `call_model` with retry + reasoning recovery) and HTTP helpers. Many also depend on external services (Qdrant, Langfuse, MQTT broker, SearXNG, ntfy, LiteLLM) referenced via environment variables or hardcoded Docker service names.

Plugins are installed by copying each `evey-*` directory and `evey_utils.py` into `~/.hermes/plugins/`. After restarting hermes-agent, the agent discovers them at startup via `register(ctx)`.

### Plugin Categories

| Category | Plugins |
|----------|---------|
| **Autonomy & Decisions** | evey-autonomy, evey-council, evey-delegate-model, evey-delegation-score, evey-commands |
| **Observability** | evey-telemetry, evey-status, evey-mqtt, evey-cost-guard, evey-digest |
| **Quality & Safety** | evey-reflect, evey-validate, evey-email-guard, evey-sandbox, evey-session-guard, evey-verification |
| **Learning & Memory** | evey-learner, evey-memory-adaptive, evey-memory-consolidate, evey-cache, evey-identity |
| **Communication** | evey-bridge, evey-goals, evey-telegram-ux, evey-research, evey-proactive, evey-habits |
| **External Services** | evey-github, evey-moltbook, evey-news, evey-wallet, evey-watchdog |
| **Scheduling** | evey-scheduler |
| **RAG** | evey-rag |

### Plugin Catalog

**evey-autonomy** (v1.0.0) -- Core autonomy engine. Provides `autonomous_decide` (priority-queue based on urgency x importance x recency with time-of-day profiling), `autonomous_plan` (task-type-specific planning templates up to 12 steps), and `autonomous_reflect` (heuristic quality scoring of completed tasks).

**evey-bridge** (v1.0.0) -- Bidirectional bridge to Claude Code via a file-based inbox/outbox (YAML task files + JSONL channel). Tools: `claude_bridge_task`, `claude_bridge_message`, `claude_bridge_check`. Auto-compresses old channel lines and archives after 7 days.

**evey-cache** (v1.0.0) -- Smart delegation caching with 24h TTL and LRU eviction. Caches `(model, goal)` pairs to avoid redundant LLM calls. Single tool: `cached_delegate`.

**evey-commands** -- Slash commands registered with hermes-agent's upstream API. Includes `stack` (Docker service health), `sites` (resource URLs), `research` (spec doc stats), and `bridge` (inbox/channel status).

**evey-cost-guard** (v2.0.0) -- Budget enforcement via Langfuse. Default $1.00 daily / $0.25 per-task budgets. Three tools: `cost_check` (spend-to-date), `cost_set_budget` (config update), `cost_analytics` (per-model breakdown with recommendations).

**evey-council** (v1.0.0) -- Multi-model debate system. Query 3 free models in parallel, then a judge model synthesizes the best answer. Tools: `council_decide`. Uses model list from env and a dedicated judge.

**evey-delegate-model** (v1.0.0) -- Smart model routing. Auto-detects task type (code/research/analysis/creative/summary), routes to the best model, falls through a 4-model chain. Sensitive content filter forces local-only models. Also provides parallel delegation (up to 6 concurrent). Tools: `delegate_with_model`, `delegate_parallel`.

**evey-delegation-score** (v1.0.0) -- Tracks delegation quality over time. Logs scores (0-10) per model + task type, provides stats with best/worst performers and overall recommendations. Tools: `delegation_log`, `delegation_stats`.

**evey-digest** (v1.0.0) -- Morning digest aggregator. Queries Langfuse costs (24h), cron health, bridge backlog, goals progress, and ntfy alerts. Single tool: `daily_digest`.

**evey-email-guard** (v1.0.0) -- Dual-layer prompt injection screening. First: 20+ regex patterns (fast, catches known attacks). Second: local LLM classifier (qwen35-4b, catches subtle attacks). Sanitizes known prompt-injection tokens. Tool: `email_screen`.

**evey-github** (v1.0.0) -- Monitors 42-evey GitHub organization repos (stars, issues, forks, push dates) and upstream PR status on NousResearch/hermes-agent. Tools: `github_status`, `github_prs`.

**evey-goals** (v1.0.0) -- Autonomous goal management on a markdown goals.md file with sections (Active, Completed, Backlog). Supports read, add, complete, and delete operations. Tool: `evey_goals`.

**evey-habits** (v1.0.0) -- Behavioral learning plugin. Tracks interaction patterns: hourly activity, topic frequency, mood trends, peak hours, busiest days, success rates. Generates recommendations (e.g., "you're most productive at 14:00"). Tools: `habits_log`, `habits_insights`.

**evey-identity** (v1.0.0) -- Self-updating personality system. Extracts behavioral rules from reflections and appends them to SOUL.md, keeping only the most recent 10. Uses qwen35-4b for rule extraction. Tool: `update_identity`.

**evey-learner** (v1.0.0) -- Experiential learning system. Stores learnings as JSONL (up to 500), scores by recency + relevance + quality, and retrieves top matches for new tasks. Tools: `learn_from_interaction`, `apply_learnings`.

**evey-memory-adaptive** (v1.0.0) -- Memory scoring and decay engine. Scores memories by importance, decays scores over time (14-day half-life), and can rank/flag low-value memories for pruning. Tools: `memory_score`, `memory_decay`.

**evey-memory-consolidate** (v1.0.0) -- Nightly memory consolidation pipeline. Fetches Langfuse traces, extracts 3-5 key facts per session with LLM, scores each fact (1-10), appends high-value facts to MEMORY.md, and indexes into Qdrant vector store with snowflake-arctic-embed2 embeddings. Tool: `consolidate_daily_memory`.

**evey-moltbook** (v1.0.0) -- Moltbook social network integration. Browse home feed, reply to comments, and create posts on the AI social network at moltbook.com. Tools: `moltbook_heartbeat`, `moltbook_reply`, `moltbook_post`.

**evey-mqtt** (v2.0.0) -- Auto-connecting MQTT event stream. Connects on plugin load, subscribes to bridge/events/health/mother topics, buffers messages in memory. Tools: `mqtt_subscribe`, `mqtt_publish_event`, `mqtt_status`.

**evey-news** (v1.0.0) -- AI news monitor. Searches for trending AI developments (LLM releases, agent frameworks, open-source AI) via SearXNG. Tool: `news_scan`.

**evey-proactive** (v1.0.0) -- Proactive messaging with interruption budget. Surfaces insights and nudges to the user during work hours with configurable cooldown. Tools: `proactive_nudge`, `proactive_budget`.

**evey-rag** (v1.0.0) -- Semantic search over Evey's Qdrant knowledge base. Supports type-filtered queries (plugin, skill, config, research, memory, goals, etc.) and collection stats. Uses snowflake-arctic-embed2 via Ollama for embedding. Tools: `knowledge_search`, `knowledge_stats`.

**evey-reflect** (v1.0.0) -- Self-correction loop. Critiques draft outputs using qwen35-4b against configurable criteria, returns PASS/FAIL with improvement suggestions. Up to 3 iterations. Tool: `reflect_on_output`.

**evey-research** (v1.0) -- Web research pipeline. Searches via SearXNG, scrapes pages via crawl4ai, saves findings as markdown files to the knowledge library. Tools: `web_search`, `extract_page`, `save_finding`.

**evey-sandbox** (v1.0) -- Sandboxed code execution with read-only folder access via Docker. Supports PII scrubbing, extension filtering, and YAML-based config. Tools: `sandbox_read`, `sandbox_search`, `sandbox_list`.

**evey-scheduler** (v1.0.0) -- Schedule management with JSON-file backend. Supports natural language parsing ("tomorrow at 3pm", "next monday"). Tools: `schedule_add`, `schedule_list`, `schedule_remove`.

**evey-session-guard** (v1.0) -- Session checkpoint system. Saves/restores critical context before compression or long tasks. Stores checkpoints as JSON with labels. Tools: `session_checkpoint`, `session_restore`.

**evey-status** (v1.0.0) -- Unified status check. ONE call replaces 5-8 separate checks: bridge, MQTT, costs, cron, goals, time context. Fetches from the Hermes dashboard API. Tool: `status_check`.

**evey-telegram-ux** (v1.0) -- Rich Telegram formatting. Generates HTML status cards with style icons, code block preservation, and formatted delegation results. Tools: `telegram_card`, `telegram_quick_status`.

**evey-telemetry** (v1.0.0) -- Structured JSON logging for the agent stack. Emits events for tool calls, delegations, errors, and cron jobs. Auto-rotates at 10MB. Tool: `telemetry_query`.

**evey-validate** (v1.0.0) -- Delegation output validation. Uses regex hallucination patterns + LLM scoring (0-10) to detect unreliable model outputs. Returns TRUST/CAUTION/REJECT recommendations. Tool: `validate_output`.

**evey-verification** (v1.0.0) -- External target verification. Checks URLs (HEAD), GitHub repos existence, endpoint availability, and DNS resolution before the agent acts on them. Tools: `verify_url`, `verify_repo`, `verify_endpoint`, `verify_dns`.

**evey-wallet** (v1.0.0) -- Crypto wallet monitoring. Checks balances on BTC, ETH, SOL, XRP, and DOGE via multiple fallback APIs per chain with deposit detection. Tool: `wallet_balance`.

**evey-watchdog** (v1.0.0) -- Self-monitoring watchdog. Tracks last activity heartbeat, sends ntfy alerts if Evey goes silent for >120 minutes during work hours. Tools: `watchdog_heartbeat`, `watchdog_status`.

## Interfaces

- **Plugin API** -- Each plugin exposes a `register(ctx)` function and tool schemas consumed by hermes-agent's internal tool dispatch
- **Plugin manifest** -- `plugin.yaml` with `provides_tools` list for agent discovery
- **CLI** -- Via hermes-agent's slash command system (evey-commands registers `/stack`, `/sites`, `/research`, `/bridge`)
- **File-based IPC** -- evey-bridge uses YAML task files + JSONL channel for Claude Code communication
- **REST APIs** -- Multiple plugins call external REST APIs (GitHub, Langfuse, SearXNG, crawl4ai, MQTT REST, Moltbook, blockchain explorers, ntfy)
- **Message bus** -- evey-mqtt provides real-time pub/sub via MQTT
- **Vector search** -- evey-rag and evey-memory-consolidate use Qdrant's REST API for vector storage and search
- **Shared utility** -- `evey_utils.py` provides `call_llm`, `call_model`, `http_get`, `http_get_json`, `http_post_json` for all plugins

## Related

[[hermes-agent]], [[openclaw]], [[hermes-suite]], [[hermes-startup-architect]], [[hermes-workspace]], [[nix-podman-stacks]]
