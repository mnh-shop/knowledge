---
name: mnemosyne
description: "Mnemosyne memory server with MCP integration for AI agent persistent storage"
source: sources/Mnemosyne/
tags: [ai-llm, cli, mcp, plugin-sdk, storage]
  - sqlite
  - mcp
  - hermes
---

# Mnemosyne

**Universal Memory Layer for AI Agents.** SQLite-backed, zero-dependency, fully private, sub-millisecond. Designed to work with any agent framework — Claude Code, Cursor, Codex, OpenWebUI, OpenClaw, Hermes, or custom agents.

- **Repository**: [AxDSan/mnemosyne](https://github.com/AxDSan/mnemosyne)
- **PyPI**: `mnemosyne-memory`
- **License**: MIT
- **Author**: Abdias J (AxDSan)
- **Language**: Python 3.10+
- **Status**: Production/Stable (Development Status 5)
- **Benchmarked**: Top scores on LongMemEval (ICLR 2025) and BEAM (ICLR 2026)

---

## Architecture Overview

Mnemosyne is a layered SQLite-backed memory system organized into several core stores and subsystems, all sharing a single thread-local connection per session.

### Core Storage Layers (sharing one SQLite connection)

| Layer | Module | Purpose |
|-------|--------|---------|
| **BEAM Memory** | `mnemosyne/core/beam.py` | Central episodic memory interface. Working memory, consolidation, fact extraction, deduplication, and event streaming. Core class: `BeamMemory`. |
| **CanonicalStore** | `mnemosyne/core/canonical.py` | Owner-scoped single-source-of-truth facts — identity cards, persistent beliefs. Versioned upsert with supersede semantics (never overwrites, always appends a new version). |
| **AnnotationStore** | `mnemosyne/core/annotations.py` | E6 schema split — typed annotations (mentions, facts, occurred_on, has_source) replacing the legacy TripleStore for structured metadata. |
| **TripleStore** | `mnemosyne/core/triples.py` | Legacy RDF-style triple store (subject-predicate-object). Deprecated in favor of AnnotationStore; still present for external scripts and backward compatibility. |
| **Memory Banks** | `mnemosyne/core/banks.py` | Multi-bank isolation — each bank is a separate SQLite database, enabling complete data partitioning by agent or domain. |
| **Episodic Graph** | `mnemosyne/core/episodic_graph.py` | Phase 3: graph-based representation of episodic memory for cross-session inference. |
| **Veracity Consolidator** | `mnemosyne/core/veracity_consolidation.py` | Phase 4: sleep-time consolidation that aggregates veracity signals across working memory into episodic summaries. |

### Core Abstractions: `Mnemosyne` (legacy) vs `BeamMemory`

- **`Mnemosyne`** (`mnemosyne/core/memory.py`): High-level facade wrapping BeamMemory with streaming, compression, pattern detection, delta sync, and plugin support. The class `Mnemosyne` instantiates a `BeamMemory` internally.
- **`BeamMemory`** (`mnemosyne/core/beam.py`): The core engine — owns the connection, manages working memory, entity/fact extraction, deduplication, and the E6 auto-migration.

### Extraction & Entity Systems

- **Entity Extraction** (`mnemosyne/core/entities.py`): Regex-based extraction of entity mentions from stored content. Always-on, zero LLM cost.
- **LLM-based Extraction** (`mnemosyne/extraction/client.py`): Optional LLM-powered structured fact extraction triggered by `extract=True` on `remember()`.
- **Content Sanitizer** (`mnemosyne/core/content_sanitizer.py`): Strips binary payloads from memory content and stores them as blobs.

### Embeddings & Vector Search

- **Embeddings** (`mnemosyne/core/embeddings.py`): Optional vector embeddings via `fastembed` and `sqlite-vec`. Enables semantic recall.
- **Binary Vectors** (`mnemosyne/core/binary_vectors.py`): Compact binary vector representation for efficient similarity search.
- **MMR Re-ranker** (`mnemosyne/core/mmr.py`): Maximum Marginal Relevance for diversity-aware recall results.
- **Query Cache** (`mnemosyne/core/query_cache.py`): Caches vector query results.

### Recall & Retrieval

- **Polyphonic Recall** (`mnemosyne/core/polyphonic_recall.py`): Multi-strategy recall that combines keyword, vector, and structured queries.
- **Unified Recall** (in `beam.py`): Tiered recall across working memory, consolidated episodes, canonical facts, and annotations.
- **Weibull-based MMR** (`mnemosyne/core/weibull.py`): Weibull distribution for intent-aware diversity scoring.
- **Query Intent** (`mnemosyne/core/query_intent.py`): Classifies recall queries by intent for routing to the optimal retrieval strategy.
- **Recall Diagnostics** (`mnemosyne/core/recall_diagnostics.py`): Analysis tools for measuring recall quality and precision.

### Memory Lifecycle

1. **Working Memory** (`working_memory` table): Immediate, short-term storage with importance scoring, scope (session/global), and optional TTL (valid_until).
2. **Consolidation**: Sleep-time process that summarizes working memory rows into episodic memory and optionally extracts structured facts.
3. **Episodic Memory** (`episodic_memory` table): Consolidated, compressed summaries of past sessions and experiences.
4. **Canonical Facts**: Persistent, versioned single-source-of-truth facts (e.g., user preferences, identity cards).

### Streaming & Patterns

- **Streaming** (`mnemosyne/core/streaming.py`): Event-based streaming of memory operations via `MemoryEvent` / `EventType`. `MemoryStream` for subscribers, `DeltaSync` for cross-device sync.
- **Pattern Detection** (`mnemosyne/core/patterns.py`): `PatternDetector` and `MemoryCompressor` — identifies recurring themes and compresses redundant content across memories.
- **Typed Memory** (`mnemosyne/core/typed_memory.py`): NLP-based memory type classification (procedural, declarative, episodic, etc.).

### Integrations & Protocol

- **MCP Server** (`mnemosyne/mcp_server.py`, `mnemosyne/mcp_tools.py`): Model Context Protocol server supporting both stdio and SSE transports. Exposes 30+ memory tools (remember, recall, forget, search, etc.).
- **CLI** (`mnemosyne/cli.py`): Direct command-line interface for memory operations, MCP server launch, install, uninstall.
- **OpenWebUI Tool** (`mnemosyne/integrations/openwebui_tool.py`): Single-file bridge for OpenWebUI custom tools.
- **OpenClaw Provider** (`mnemosyne/integrations/openclaw.py`): Native OpenClaw memory provider.
- **Memory Browser** (`mnemosyne/integrations/memory_browser.py`): Web UI for browsing stored memories.
- **Auto-save** (`mnemosyne/integrations/auto_save_openwebui.py`): Auto-save integration with OpenWebUI.

### Import Adapters (9 external memory systems)

`mnemosyne/core/importers/` contains adapters for importing from:
- **Mem0** (`mem0.py`), **Zep** (`zep.py`), **Honcho** (`honcho.py`), **Letta** (`letta.py`), **Hindsight** (`hindsight.py`), **Cognee** (`cognee.py`), **Holographic Memory** (`holographic.py`), **Agentic Memory** (`agentic.py`), **Supermemory** (`supermemory.py`)

### Sync

- **Sync** (`mnemosyne/core/sync.py`): Encrypted memory synchronization across devices using `cryptography`.
- **Sync Server** (`mnemosyne/core/sync_server.py`): Server component for peer-to-peer memory sync.
- **Delta Sync** (in `streaming.py`): Computes and applies delta changesets between peers.

### Schema Migrations

- **E6 TripleStore Split** (`mnemosyne/migrations/e6_triplestore_split.py`): Automatic migration from legacy TripleStore to AnnotationStore. Backs up the database before migration.

### Diagnostics & Recovery

- **Diagnose** (`mnemosyne/diagnose.py`): System diagnostics for optional dependencies, schema version, and database health.
- **DR Recovery** (`mnemosyne/dr/recovery.py`): Disaster recovery utilities.

---

## Key Design Patterns

- **Thread-local connection sharing**: All stores (CanonicalStore, AnnotationStore, EpisodicGraph, VeracityConsolidator) share BeamMemory's single SQLite connection, avoiding per-call file-descriptor costs.
- **BEGIN IMMEDIATE for atomicity**: Writes use `BEGIN IMMEDIATE` transactions so read-current + supersede + insert sequences are atomic against concurrent writers.
- **Never-delete audit model**: Versions are superseded (valid_until stamp) rather than deleted — all history is preserved and auditable.
- **Lazy initialization**: Streaming, patterns, compression, and plugins are lazy-initialized on first access, avoiding overhead when not used.
- **E6 auto-migration**: On first init with a pre-E6 database, legacy TripleStore rows are auto-migrated to AnnotationStore with backup.

---

## Development

### Directory Structure

```
mnemosyne/
  __init__.py              # Package version
  cli.py                   # CLI entry point (mnemosyne command)
  diagnose.py              # System diagnostics
  install.py               # Install/uninstall scripts
  mcp_server.py            # MCP protocol server
  mcp_tools.py             # MCP tool definitions
  core/
    __init__.py
    aaak.py                # AAAK architecture utilities
    annotations.py          # AnnotationStore (E6)
    banks.py                # Memory bank management
    beam.py                # BEAM memory engine (main core)
    binary_vectors.py      # Binary vector operations
    canonical.py            # CanonicalStore
    chat_normalize.py       # Chat text normalization
    content_sanitizer.py    # Binary content extraction to blobs
    cost_log.py             # Cost logging
    embeddings.py           # Vector embeddings
    entities.py             # Entity extraction
    episodic_graph.py       # Episodic graph (Phase 3)
    extraction.py           # Fact extraction
    importers/              # Import adapters (9 memory systems)
    llm_backends.py         # LLM backend abstraction
    llm_conflict_detector.py # Conflict detection between facts
    local_llm.py            # Local LLM integration
    memory.py               # Mnemosyne facade class
    mmr.py                  # MMR re-ranker
    orchestrator.py         # Memory orchestrator
    patterns.py             # Pattern detection & compression
    persona.py              # Persona management
    plugins.py              # Plugin system
    polyphonic_recall.py    # Multi-strategy recall
    query_cache.py          # Vector query cache
    query_intent.py         # Query intent classification
    recall_diagnostics.py   # Recall quality measurement
    shmr.py                 # SHMR (Structured Hierarchical Memory Representation)
    streaming.py            # Streaming events & delta sync
    sync.py                 # Encrypted memory sync
    sync_server.py          # Sync server
    synonyms.py             # Synonym expansion for recall
    temporal_parser.py      # Temporal expression parsing
    token_counter.py        # Token counting
    triples.py              # Legacy TripleStore
    typed_memory.py         # Memory type classification
    veracity_consolidation.py # Sleep-time veracity consolidation
    weibull.py              # Weibull distribution for recall
  dr/
    recovery.py             # Disaster recovery
  extraction/
    client.py               # LLM extraction client
    diagnostics.py           # Extraction diagnostics
    prompts.py               # Extraction prompts
  integrations/
    auto_save_openwebui.py
    memory_browser.py
    openclaw.py
    openwebui_tool.py
  migrations/
    e6_triplestore_split.py
tests/                       # 60+ test files
tools/                       # Benchmark and diagnostic scripts
```

### Tests

Over 60 test files covering:
- BEAM benchmark tests (comprehensive, SOTA, pure recall gate)
- Identity memory, provider tools across 15 tools
- E6 migration, vector rewiring, cross-tier dedup
- MCP server, CLI errors and operations
- Streaming, pattern detection, extraction parity
- Sync, recovery paths, temporal parsing
- Persona injection, persona schema, persona adapter

---

## Benchmarks

| Benchmark | Score | Details |
|-----------|-------|---------|
| **LongMemEval Recall@All@5** | **98.9%** | Apr 2026, bge-small-en-v1.5, 100 instances |
| **BEAM (ICLR 2026) 100K QA** | **65.2%** | End-to-end question answering |
| **BEAM Recall@10 (10M scale)** | **20%** | 35ms latency, 7.2MB storage |
| **Abstention accuracy** | **100%** | Never hallucinates on unknowns |
| **Episodic compression** | **9.4x** | Storage savings via consolidation |

---

## Platform Compatibility

| Platform | Interface |
|----------|-----------|
| **Cursor** | MCP (`.cursor/mcp.json`) |
| **Claude Code** | MCP (`claude.json`) |
| **OpenAI Codex CLI** | MCP (`.codex/mcp.json`) |
| **Windsurf** | MCP (`.windsurf/mcp_config.json`) |
| **OpenWebUI** | `@tool` bridge file |
| **OpenClaw** | Native provider plugin |
| **Hermes Agent** | MCP + Plugin (ships enabled) |
| **Any MCP client** | stdio or SSE transport |
| **Any Python agent** | `import mnemosyne` |

---

## Key Dependencies

- **Zero hard dependencies** — core works with stdlib only.
- **Optional**: `fastembed`, `sqlite-vec` for vector search.
- **Optional**: `mcp`, `anyio` for MCP server.
- **Optional**: `cryptography` for encrypted sync.
- **Optional**: `ctransformers`, `llama-cpp-python`, `huggingface-hub` for local LLM extraction.
