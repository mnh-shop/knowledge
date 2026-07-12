---
name: Mnemosyne-architecture
tags: [mnemosyne, architecture, memory, ai-agents, sqlite, mcp, python, vector-search]
description: Mnemosyne Architecture — L1-L3 tiered memory storage with hybrid vector+FTS5 recall, MCP server interface, and Hermes plugin integration
source: sources/Mnemosyne/
---

# Mnemosyne Architecture
**Source:** `sources/Mnemosyne/`

Mnemosyne is a universal memory layer for AI agents. SQLite-backed, zero-dependency, and fully private, it provides sub-millisecond recall with tiered storage, hybrid vector+FTS5 search, and MCP/stdio interfaces for any agent framework.

## Architecture

### Tiered Storage Layers (L1-L3)

All layers share a single thread-local SQLite connection:

| Layer | Module | Purpose |
|-------|--------|---------|
| **L1: Working Memory** | `mnemosyne/core/beam.py` | Immediate short-term storage with importance scoring, scope (session/global), optional TTL |
| **L2: Episodic Memory** | `mnemosyne/core/beam.py` (consolidation) | Sleep-time compressed summaries of past sessions |
| **L3: Canonical Facts** | `mnemosyne/core/canonical.py` | Owner-scoped single-source-of-truth, versioned upsert with supersede semantics |

A sleep-time consolidation process summarizes working memory rows into episodic memory and optionally extracts structured facts. Veracity Consolidation (`mnemosyne/core/veracity_consolidation.py`) aggregates veracity signals across working memory into episodic summaries.

### Hybrid Vector+FTS5 Recall

Polyphonic Recall (`mnemosyne/core/polyphonic_recall.py`) combines keyword (SQLite FTS5), vector (`fastembed` + `sqlite-vec`), structured (AnnotationStore queries), and unified tiered recall. MMR re-ranker provides diversity-aware results; Query Intent classifier routes to optimal strategy.

### Core Abstractions

| Class | Role |
|-------|------|
| `BeamMemory` | Core engine — connection owner, entity/fact extraction, E6 auto-migration |
| `Mnemosyne` | High-level facade — streaming, compression, pattern detection, delta sync |
| `CanonicalStore` | Versioned single-source-of-truth facts |
| `AnnotationStore` | E6 typed annotations (replaces legacy TripleStore) |

### Interfaces

- **MCP Server** (`mnemosyne/mcp_server.py`) — stdio + SSE transports, 30+ memory tools
- **Hermes Plugin** (`hermes_memory_provider/`) — plugin.yaml, CLI, persona management, sync adapter, LLM extraction backend

### Memory Lifecycle

```
User input → Working Memory (L1, importance-scored, optional TTL)
                ↓ (sleep-time consolidation)
         Episodic Memory (L2, compressed summaries)
                ↓ (persistent beliefs)
         Canonical Facts (L3, versioned, never-delete audit model)
```

The never-delete audit model supersedes (valid_until stamp) rather than deleting — all history is preserved and auditable.

### Entity Extraction, Sync, and Streaming

Always-on regex entity extraction (`mnemosyne/core/entities.py`) costs zero LLM tokens. Optional LLM extraction via `extract=True`. Streaming (`MemoryEvent`/`EventType`) feeds subscribers; Delta Sync computes changesets between peers; Encrypted Sync uses `cryptography` for cross-device sync.

### Platform Interfaces

| Platform | Interface |
|----------|-----------|
| Cursor, Claude Code, Codex CLI, Windsurf | MCP (stdio) |
| Hermes Agent | MCP + native plugin |
| OpenWebUI | `@tool` bridge |
| OpenClaw | Native provider |
| Any Python | `import mnemosyne` |

## Key Components

| Module | Role |
|--------|------|
| `mnemosyne/core/beam.py` | BEAM memory engine — central episodic store |
| `mnemosyne/core/canonical.py` | Versioned canonical fact store |
| `mnemosyne/core/annotations.py` | E6 typed annotation store |
| `mnemosyne/core/polyphonic_recall.py` | Multi-strategy hybrid recall |
| `mnemosyne/core/embeddings.py` | Optional vector embeddings + sqlite-vec |
| `mnemosyne/mcp_server.py` | MCP server (stdio + SSE) |
| `hermes_memory_provider/` | Hermes Agent plugin integration |
| `mnemosyne/core/importers/` | 9 import adapters (Mem0, Zep, Letta, etc.) |

## Related

- [[Mnemosyne]] — Wiki entry
- [[hermes-agent]] — Consumes Mnemosyne as memory backend
- [[infinite-brain-os]] — Alternative memory architecture
- [[materia]] — GitOps deployment framework
- [[domains/architecture/hermes-agent-architecture.md]]
