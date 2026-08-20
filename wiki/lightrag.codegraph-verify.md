---
name: lightrag-codegraph-verify
tags: [lightrag, rag, codegraph-verify, reference]
description: "Codegraph Verification: lightrag — validating wiki claims against indexed source code symbols"
source: sources/lightrag/
---

# Codegraph Verification: lightrag

**Date:** 2026-08-12

**Version checked:** `6f50fddd` (main, Merge pull request #3629)

## Claim 1: Dual-level knowledge graph with entity+relation extraction

- **Wiki says:** LightRAG extracts entities and relationships from documents, builds a knowledge graph, and supports multiple retrieval modes.
- **Source evidence:**
  - `lightrag/operate.py` — `extract_entities()`, `extract_relations()` functions for KG construction
  - `lightrag/lightrag.py` — `LightRAG` class with `aquery()` supporting `local`, `global`, `hybrid`, `mix`, `naive` modes
  - `lightrag/base.py` — `BaseGraphStorage` abstract class defining graph operations
- **Verdict:** ✅ CORRECT

## Claim 2: 4 pluggable storage types

- **Wiki says:** KV_STORAGE, VECTOR_STORAGE, GRAPH_STORAGE, DOC_STATUS_STORAGE with pluggable backends.
- **Source evidence:**
  - `lightrag/base.py` — four abstract base classes: `BaseKVStorage`, `BaseVectorStorage`, `BaseGraphStorage`, `BaseDocStatusStorage`
  - `lightrag/kg/__init__.py` — `STORAGE_IMPLEMENTATIONS` registry with JSON, NetworkX, Neo4j, PostgreSQL, MongoDB, Redis, Milvus, Qdrant, Faiss, Memgraph, OpenSearch, NanoVectorDB
  - `lightrag/kg/factory.py` — `get_storage_class()` resolves backend from config
- **Verdict:** ✅ CORRECT

## Claim 3: Python 3.10+, MIT license, pip installable

- **Wiki says:** Python 3.10+, MIT license, available as `lightrag-hku` on PyPI.
- **Source evidence:**
  - `pyproject.toml` — `requires-python = ">=3.10"`, `license = {text = "MIT"}`
  - `pyproject.toml` — `name = "lightrag-hku"`
  - `README.md` — PyPI install instructions: `uv tool install "lightrag-hku[api]"`
- **Verdict:** ✅ CORRECT

## Claim 4: Pluggable LLM backends

- **Wiki says:** Supports OpenAI, Ollama, Azure, Gemini, Bedrock, Anthropic and others.
- **Source evidence:**
  - `lightrag/llm/` — provider modules: `openai.py`, `ollama.py`, `azure.py`, `gemini.py`, `bedrock.py`, `anthropic.py`
  - `lightrag/llm/__init__.py` — provider registration and routing
  - All LLM modules are async with caching support
- **Verdict:** ✅ CORRECT

## Claim 5: Docker deployment available

- **Wiki says:** Docker Compose and Dockerfile for deployment, port 9621 default.
- **Source evidence:**
  - `docker-compose.yml` — services: lightrag (port 9621), Postgres, Neo4j
  - `Dockerfile` — container build definition
  - `config.ini.example` — configuration template for Neo4j, MongoDB, Redis, Qdrant, Postgres backends
- **Verdict:** ✅ CORRECT

## Claim 6: Exclusion from knowledge system pipeline

- **Wiki says:** Excluded from repomix by SKIP list in actualize-repos.py; kept as reference only.
- **Source evidence:**
  - `scripts/actualize-repos.py` line 85: `SKIP = {'n8nworkflows.xyz', 'lightrag'}`
  - No `raw/lightrag/` directory (confirmed on disk)
- **Verdict:** ✅ CORRECT — this repo is intentionally excluded from the automated knowledge pipeline

## Claim 7: CBM index exists but is outside regular pipeline

- **Wiki says:** CBM index exists from prior manual indexing but is not part of the regular sync pipeline.
- **Source evidence:**
  - CBM project `Users-admin-repos-knowledge-sources-lightrag` exists with 27,664 nodes, 145,022 edges
  - `scripts/actualize-repos.py` SKIP list excludes it from repomix
  - `.cbm_queue_normal.txt` does not include lightrag
- **Verdict:** ⚠️ PARTIAL — index exists, exclusion is correct, but wiki page was missing until now
