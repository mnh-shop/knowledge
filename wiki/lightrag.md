---
name: lightrag
tags: [rag, graph, retrieval, llm, python, postgres, neo4j, mongodb, reference]
description: "Wiki entry for LightRAG — HKUDS graph-based RAG framework (reference repo, not part of agent knowledge system)"
source: sources/lightrag/
verification_date: 2026-08-12
verified_by: codegraph-verify
---

# LightRAG

|| Field | Value |
||---|---|
|| **Origin** | [HKUDS/LightRAG](https://github.com/HKUDS/LightRAG) |
|| **License** | MIT |
|| **Version** | `lightrag/_version.py` (dynamic, from git) |
|| **Source** | `sources/lightrag/` |
|| **Python pkg** | `lightrag-hku` (PyPI) |
|| **CBM index** | `Users-admin-repos-knowledge-sources-lightrag` (27,664 nodes, 145,022 edges) |

## What is it?

LightRAG is a Retrieval-Augmented Generation framework that uses a dual-level knowledge graph (entity+relation extraction) for enhanced information retrieval. It extracts entities and relationships from documents, builds a graph, and supports multiple retrieval modes (`local`, `global`, `hybrid`, `mix`, `naive`).

This is a **reference repository** — it is the upstream LightRAG project itself, not a tool or platform used by this knowledge system. It is kept in `sources/` for reference only.

## Architecture

LightRAG uses 4 pluggable storage types:

- **KV_STORAGE** — LLM response cache, text chunks, document info
- **VECTOR_STORAGE** — entity/relation/chunk embeddings
- **GRAPH_STORAGE** — entity-relation graph (JSON, NetworkX, Neo4j, PostgreSQL, MongoDB, Redis, Milvus, Qdrant, Faiss, Memgraph, OpenSearch, NanoVectorDB)
- **DOC_STATUS_STORAGE** — document processing status

Key modules:
- `lightrag/lightrag.py` — main `LightRAG` orchestrator class
- `lightrag/operate.py` — core extraction and query operations
- `lightrag/base.py` — abstract storage backends
- `lightrag/kg/` — storage implementations
- `lightrag/llm/` — LLM/embedding provider bindings (OpenAI, Ollama, Azure, Gemini, Bedrock, Anthropic)
- `lightrag/pipeline.py` — document ingestion pipeline
- `lightrag/chunker/` — chunking strategies

### Deployment

- `docker-compose.yml` — full stack (lightrag server + Postgres + Neo4j)
- `Dockerfile` — container build
- `lightrag-server` — CLI entry point (PyPI `uv tool install lightrag-hku[api]`)
- Port 9621 default

## Why it's in sources/

This repo is kept as a reference for the RAG/framework landscape. It is **not** indexed for agent knowledge lookup. The `actualize-repos.py` SKIP list excludes it from repomix (`SKIP = {'n8nworkflows.xyz', 'lightrag'}`). Its CBM index exists from a prior manual indexing but is not part of the regular sync pipeline.

## Value for coding agents

LightRAG is relevant as a reference architecture for graph-based RAG — useful when evaluating RAG approaches, but not a deployment target or integration point for this knowledge system.
