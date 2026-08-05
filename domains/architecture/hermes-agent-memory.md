---
name: hermes-agent-memory
tags: [architecture, hermes-agent, memory, sqlite, fts5]
description: "Hermes Agent memory: MemoryManager, memory tool, SessionDB/FTS5 with CJK extension, 8 memory provider plugins (honcho, mem0, supermemory, byterover, hindsight, holographic, openviking, retaindb), hermes memory CLI"
source: sources/hermes-agent/
---

# Hermes Agent Memory

**Codegraph:** `graphs/hermes-agent`
**Source:** `sources/hermes-agent/agent/memory_manager.py` · `sources/hermes-agent/tools/memory_tool.py` · `sources/hermes-agent/hermes_state.py`

Hermes memory is layered: a **built-in** bounded file store (`MEMORY.md` /
`USER.md` in the Hermes home) injected into the system prompt every turn, a
**session database** (SQLite, FTS5 searchable) holding full conversation
history, and **external memory provider plugins** for cross-session semantic
memory. Only one external provider is active at a time.

## Built-in memory — `agent/memory_manager.py`

| Symbol | Line | Role |
|---|---|---|
| `MemoryManager` | 364 | Cross-session memory persistence and recall; owns provider registration and prefetch |
| `add_provider` / `providers` / `get_provider` | 404/473/477 | Register and look up external `MemoryProvider`s |
| `build_system_prompt` | 486 | Assembles the memory section of the cached system prompt prefix |
| `prefetch_all` / `queue_prefetch_all` | 525/597 | Synchronous / fire-and-forget prefetch of relevant memories per turn |
| `inject_memory_provider_tools` | 110 | Adds provider tool schemas to the active toolset |
| `StreamingContextScrubber` | 182 | Sanitizes streamed output (block-boundary aware tag scrubbing) |
| `build_memory_context_block` | 347 | Renders the raw memory context block |

Writes are durability-classed: futures are tracked by durability class so
shutdown can flush pending writes (memory_manager.py:391). The default
memory dir and per-store char limits are enforced by the memory tool.

## Memory tool — `tools/memory_tool.py`

Single `memory` tool schema (memory_tool.py:1153) with batch semantics:

- **Targets:** `user` (who the user is: name, role, preferences, style) or
  `memory` (agent notes: environment, conventions, tool quirks, lessons).
- **Actions:** `add`, `replace`, `remove` — all mutations in ONE call via an
  `operations` array applied atomically; the char limit is checked only on
  the final result so a single batch can free room and add new entries.
- **Limits:** `memory_char_limit` 2200 (~800 tokens), `user_char_limit` 1375
  (~500 tokens) from config.
- **Full-store handling:** an overflowing `add` is rejected with current
  entries shown; guidance instructs reissuing as one batch.
- File-backed with drift detection (`_drift_error`, `_reload_target`,
  `_file_lock`) to survive concurrent writers; `get_memory_dir()` resolves
  the store path under the Hermes home.

## Session database — SessionDB / FTS5

`SessionDB` (hermes_state.py:1720, composed of `SessionSearchMixin`,
`SessionSchemaMixin`, `SessionPortabilityMixin`) is the SQLite-backed store
for sessions and messages (`hermes_state`). Key search features:

- **FTS5 full-text index** over messages with the **CJK-bigram extension**:
  `native/fts5_cjk/fts5_cjk.c` is compiled and loaded via
  `load_fts5_cjk_extension` (hermes_state.py:1110, 1274). The CJK bigram
  tokenizer replaces the trigram index (which needs ≥3 chars per term and
  breaks on 1-2 char CJK queries); the `FTS_CJK_STALE_KEY` marker triggers
  index rebuild when the extension becomes available.
- **Search tool:** `tools/session_search_tool.py` — three modes: FTS5
  discovery (query → dedupe by session lineage → top-N sessions with
  highlighted snippets + ±5 anchored message windows), anchor mode (window
  around a message, no FTS5), and recent-session metadata. No LLM calls —
  purely FTS5-backed (session_search_tool.py:967). Exposed to the agent in
  the `session_search` toolset (toolsets.py:62, 225).
- FTS5 failures are detected and reported via
  `SessionDB._is_fts5_unavailable_error` instead of crashing.

## Memory provider plugins (8)

`plugins/memory/` — each is a full plugin with its own tool schemas, client,
config schema, and plugin.yaml:

| Provider | Notes |
|---|---|
| **honcho** | Honcho AI-native memory — cross-session user modeling with dialectic Q&A, semantic search, persistent conclusions. Registers `on_session_end` hook (plugin.yaml). Config resolved from `$HERMES_HOME/honcho.json` then legacy `~/.honcho/config.json`. Tools: `honcho_profile`, `honcho_search`, `honcho_reasoning`, `honcho_context`. CLI: `hermes honcho setup | status | sessions | map | peer` (honcho/cli.py). OAuth via honcho/oauth.py + oauth_flow.py. |
| **mem0** | mem0 provider |
| **supermemory** | SuperMemory provider |
| **byterover** | ByteRover provider |
| **hindsight** | Hindsight provider |
| **holographic** | Holographic provider (uses SessionDB-backed store/retrieval: holographic/store.py, retrieval.py) |
| **openviking** | OpenViking provider (OOB message relay) |
| **retaindb** | RetainDB provider |

Shared plumbing lives in `plugins/memory/config_schema.py` (field kinds:
`KIND_BOOL`, `KIND_JSON`, `KIND_NUMBER`, `KIND_SECRET`, `KIND_SELECT`,
`KIND_TEXT`; `STORAGE_HONCHO_HOST_BLOCK`) and `plugins/memory/query_rewrite.py`.

## Configuration

`memory:` config section (config_defaults.py:1531):

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  write_approval: false      # gate on memory writes; /memory pending|approve|reject when on
  memory_char_limit: 2200
  user_char_limit: 1375
  provider: ""               # activate: openviking, mem0, hindsight, holographic, retaindb, byterover (honcho also registerable)
```

- **`write_approval`** applies to BOTH foreground turns and the background
  self-improvement review fork (the source of unprompted "wrong assumption"
  saves). When enabled, foreground writes prompt inline; background writes
  are staged and reviewed via `/memory pending`, `/memory approve <id>`,
  `/memory reject <id>`.
- Only ONE external provider at a time.

## CLI + slash commands

- **`hermes memory`** — `hermes_cli/subcommands/memory.py` (`build_memory_parser`):
  `setup` (configure external provider), `status` (show provider config),
  `off` (disable external provider, built-in only), `reset` (erase built-in
  memory, `--store all|memory|user`).
- **`hermes memory-graph` / `hermes learning`** — aliases for the learning
  journey (commands.py:145-146).
- **Slash commands:** `/memory` (review pending writes / toggle the approval
  gate, commands.py:250), `/journey` (learning timeline; aliases `learning`,
  `memory-graph`).

## Learning graph

`agent/learning_graph.py` builds the "learning made visible" graph for the
desktop panel (`build_learning_graph`, learning_graph.py:254): memory chunks
are first-class graph nodes connected to learned skills (skills that are NOT
base-installed and show real learning signal). `agent/learning_mutations.py`
handles the write path. Skill-usage signal comes from `tools/skill_usage.py`.

## Related

- [[hermes-agent-architecture]] -- Overall architecture; `agent/memory_manager.py` as part of the agent core
- [[hermes-agent-plugins]] -- The 8 memory providers are plugins under `plugins/memory/`
- [[hermes-agent-cli]] -- `hermes memory`, `hermes honcho`, `/memory`, `/journey`
- [[hermes-agent-skills]] -- Learning graph connects memory chunks to learned skills

## Links

- Manager: `sources/hermes-agent/agent/memory_manager.py`
- Tool: `sources/hermes-agent/tools/memory_tool.py`
- Session DB: `sources/hermes-agent/hermes_state.py` (SessionDB, FTS5, CJK)
- Native extension: `sources/hermes-agent/native/fts5_cjk/fts5_cjk.c`
- Search tool: `sources/hermes-agent/tools/session_search_tool.py`
- Providers: `sources/hermes-agent/plugins/memory/`
- CLI: `sources/hermes-agent/hermes_cli/subcommands/memory.py`
- Config: `sources/hermes-agent/hermes_cli/config_defaults.py`
- Learning graph: `sources/hermes-agent/agent/learning_graph.py`, `learning_mutations.py`
