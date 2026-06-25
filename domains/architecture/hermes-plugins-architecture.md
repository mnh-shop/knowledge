---
name: hermes-plugins-architecture
description: "Plugin system architecture for 34 evey-* plugins extending hermes-agent"
source: sources/hermes-plugins/
tags: [ai-llm, architecture, dashboard, developer-tools, docker, event-bus, git, messaging, multi-platform, orchestration, plugin-sdk, security, skills-platform, storage]
---

# Hermes Plugins -- Architecture

**Source:** `sources/hermes-plugins/`

## Plugin System Model

Each `evey-*` plugin is a self-contained Python package that the hermes-agent framework discovers and loads at startup. The formal contract between plugin and agent consists of two files per plugin:

### 1. `plugin.yaml` -- Manifest

```yaml
name: evey-autonomy
version: 1.0.0
description: Autonomous decision engine -- priority queue, planning, and reflection
provides_tools:
  - autonomous_decide
  - autonomous_plan
  - autonomous_reflect
```

Fields: `name`, `version`, `description`, `provides_tools`. The agent reads all `plugin.yaml` files in the plugins directory to build its tool registry. Some plugins omit `provides_tools` (e.g., evey-commands, which registers slash commands instead).

### 2. `__init__.py` -- Implementation

Required export: `def register(ctx)`. The agent calls this at startup, passing a `ctx` object that exposes a registration API. Inside `register()`, the plugin calls `ctx.set_router(...)` or similar to register its tool schemas with the agent's dispatch system.

```python
# Pattern used across all plugins:
def register(ctx):
    ctx.set_router({
        "tool_name": { "schema": SCHEMA, "handler": handler_func },
    })
```

### Shared Utility Layer

`evey_utils.py` lives alongside the plugin directories and provides:

- `call_llm(model, prompt, ...)` -- quick LLM call, returns content string
- `call_model(model, prompt, ...)` -- full model call with retries (exponential backoff), reasoning recovery for reasoning-model responses, returns parsed JSON with content + usage
- `http_get(url)`, `http_get_json(url)`, `http_post_json(url, data_dict)` -- HTTP helpers with error handling, returns None on failure

All plugins that call LLMs import from `evey_utils.py` using Python's `importlib` with `spec_from_file_location()` to load it from the parent directory at runtime.

## Data Flow

### Autonomous Decision Cycle

```
User/System trigger
    |
    v
evey-autonomy.decide_handler()
    |-- Collect signals from: bridge, goals, memories, cron, time context
    |-- Score each action: urgency * importance * recency (max 1000)
    |-- Deduplicate near-identical signals
    |-- Route: ROUTING dict maps task_type to model/prompt
    |-- Return: { action, description, reasoning, routed_to }
    |
    v
evey-delegate-model.handler()  (or council or cached_delegate)
    |-- Task-type detection -> smart model selection
    |-- Sensitive content check -> force local models
    |-- Fallback chain (4 models, 3 retries per model)
    |-- Optional: parallel delegation (up to 6)
    |
    v
evey-validate.validate_output()
    |-- Regex hallucination patterns (fast pass)
    |-- LLM scoring (0-10) via qwen35-4b
    |-- Returns: TRUST / CAUTION / REJECT
    |
    v
evey-reflect.reflect_on_output()
    |-- Critique via qwen35-4b against accuracy/completeness/actionability
    |-- Up to 3 iterations of critique + fix
    |
    v
evey-autonomy.reflect_handler()
    |-- Heuristic quality scoring
    |-- Update decision log
    |-- Suggest next action
```

### Memory Pipeline

```
Langfuse traces (24h window)
    |
    v
evey-memory-consolidate
    |-- _langfuse_query(): fetch traces from API
    |-- _extract_facts(): LLM extracts 3-5 facts per session
    |-- _score_fact(): LLM rates importance 1-10, keep >= 5
    |-- _update_memory(): append to MEMORY.md with date header
    |-- _embed_to_qdrant(): embed via snowflake-arctic-embed2 -> Qdrant
    |
    v
evey-rag (reads from Qdrant)
    |-- Semantic search with type filters
    |-- Stats: total vectors, type distribution, sources
```

### External Service Integration Pattern

Plugins follow a consistent pattern for external API integration:

1. Read config from environment variables (e.g., `os.environ.get("MQTT_HOST", "hermes-mqtt")`)
2. Build request with `urllib.request` (stdlib, no external deps beyond what the agent provides)
3. Use `evey_utils.http_get`/`evey_utils.http_post_json` for error handling
4. Register tool schemas as Python dicts with `"schema"` and `"handler"` keys

## Configuration Model

### Environment Variables (shared across plugins)

| Variable | Default | Used By |
|----------|---------|---------|
| `HERMES_HOME` | `~/.hermes` | File-path resolution for all plugins |
| `OPENAI_BASE_URL` | (empty) | LiteLLM endpoint for model calls |
| `OPENAI_API_KEY` | (empty) | LiteLLM auth |
| `LANGFUSE_HOST` | (empty) | evey-cost-guard, evey-digest, evey-memory-consolidate |
| `LANGFUSE_PUBLIC_KEY` | (empty) | Langfuse auth |
| `LANGFUSE_SECRET_KEY` | (empty) | Langfuse auth |
| `SEARXNG_URL` | `http://hermes-searxng:8080` | evey-news, evey-research |
| `NTFY_URL` | `http://hermes-ntfy:80` | evey-watchdog, evey-digest |
| `MQTT_HOST` | `hermes-mqtt` | evey-mqtt |
| `MQTT_PORT` | `1883` | evey-mqtt |
| `DASHBOARD_URL` | `http://hermes-dashboard:8088` | evey-commands, evey-status |

### File-Based State (under `~/.hermes/`)

| Path | Format | Owned By |
|------|--------|----------|
| `goals.md` | Markdown | evey-goals |
| `SOUL.md` | Markdown | evey-identity |
| `memories/MEMORY.md` | Markdown | evey-memory-consolidate |
| `memories/.memory_scores.json` | JSON | evey-memory-adaptive |
| `claude-bridge/inbox/` | YAML files | evey-bridge |
| `claude-bridge/outbox/` | JSONL | evey-bridge |
| `claude-bridge/channel.jsonl` | JSONL | evey-bridge |
| `cron/jobs.json` | JSON | evey-scheduler (via hermes-agent) |
| `workspace/orchestrator/autonomy-log.jsonl` | JSONL | evey-autonomy |
| `workspace/orchestrator/delegation-cache.json` | JSON | evey-cache |
| `workspace/orchestrator/learnings.jsonl` | JSONL | evey-learner |
| `workspace/manager/habits.json` | JSON | evey-habits |
| `workspace/manager/schedule.json` | JSON | evey-scheduler |
| `workspace/manager/proactive-state.json` | JSON | evey-proactive |
| `workspace/watchdog-state.json` | JSON | evey-watchdog |
| `workspace/checkpoints/` | JSON | evey-session-guard |
| `workspace/delegation-scores.jsonl` | JSONL | evey-delegation-score |
| `workspace/moltbook-state.json` | JSON | evey-moltbook |
| `telemetry/events.jsonl` | JSONL | evey-telemetry |
| `cost-budget.json` | JSON | evey-cost-guard |

## Service Dependencies (Docker network)

The plugin stack expects these containers on the Docker network:

| Service | Used By | Purpose |
|---------|---------|---------|
| `hermes-litellm` | All LLM-calling plugins | Unified LLM API proxy |
| `hermes-ollama` | evey-rag, evey-memory-consolidate | Local embedding model |
| `hermes-qdrant` | evey-rag, evey-memory-consolidate | Vector database |
| `hermes-searxng` | evey-news, evey-research | Web/metasearch engine |
| `hermes-crawl4ai` | evey-research | Web page scraping |
| `hermes-mqtt` | evey-mqtt | Real-time event bus |
| `hermes-ntfy` | evey-watchdog, evey-digest | Push notifications |
| `hermes-dashboard` | evey-commands, evey-status | Hermes web dashboard API |
| Langfuse (external) | evey-cost-guard, evey-digest, evey-memory-consolidate | LLM observability + cost tracking |

## Security Architecture

### Guard Layers (layered defense)

1. **evey-email-guard** -- Input security for email channel
   - Layer 1: 20+ regex patterns (framework-injection tokens, <system>, [INST], etc.)
   - Layer 2: Local LLM classifier (qwen35-4b) for semantic attacks
   - Sanitization: removes known injection tokens from body

2. **evey-delegate-model** -- Data exfiltration prevention
   - Sensitive content detection: regex patterns for keys, credentials, PII
   - On match: force routing to local-only models (e.g., qwen35-4b), never sends to external API

3. **evey-sandbox** -- Execution isolation
   - Read-only access to configured folders via Docker mount
   - Extension whitelist (code, text, data files)
   - PII scrubbing on read
   - 500KB max file size

4. **evey-validate** -- Output reliability
   - Regex hallucination patterns (contradictions, unsubstantiated claims, etc.)
   - LLM scoring (0-10) with TRUST/CAUTION/REJECT tiers

## Deployment

Plugins ship as a git clone that the user copies into `~/.hermes/plugins/`:

```bash
git clone https://github.com/42-evey/hermes-plugins.git
cp -r hermes-plugins/evey-* ~/.hermes/plugins/
cp hermes-plugins/evey_utils.py ~/.hermes/plugins/
# Restart hermes-agent
```

No additional Python dependencies beyond what hermes-agent provides. All HTTP calls use `urllib.request` from stdlib. The third-party `paho-mqtt` library is optional and gracefully degraded.

## Related

[[hermes-plugins]], [[hermes-agent]], [[openclaw]], [[hermes-suite-architecture]], [[hermes-agent-architecture]]
