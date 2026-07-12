---
name: n8n-workflows-architecture
tags: [n8n-workflows, architecture, n8n, workflows, catalog, fastapi]
description: "Workflow catalog architecture — FastAPI search backend, SQLite FTS5 indexing, workflow pattern taxonomy, and 2,061 curated n8n workflows"
source: sources/n8n-workflows/
verification_date: 2026-07-12
verified_by: fixer
---

# n8n Workflows — Architecture

**Source:** `sources/n8n-workflows/`

## Overview

n8n-workflows is a curated catalog of **2,061 n8n workflow JSON definitions** organized into 20 category directories, wrapped by a FastAPI search server with SQLite FTS5 full-text indexing. The repository serves dual roles: a production-ready workflow library for n8n users, and a reference corpus for studying integration patterns across 282 unique service integrations. Workflows are stored as flat JSON files, each containing node definitions, connections, configuration, and metadata.

## Architecture

The system follows a three-layer architecture: a flat filesystem catalog of workflow JSON files, an SQLite database layer with FTS5 search, and a FastAPI REST server that exposes browse, search, and export endpoints.

```
┌──────────────────────────────────────────────────────┐
│                  FastAPI REST Server                  │
│  /api/search · /api/stats · /api/workflow/{id}        │
│  /api/categories · /api/export · Static Web UI         │
│  GZip middleware · CORS · Rate limiting                │
└────────────────────────┬─────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────┐
│              Workflow Database (SQLite)                │
│  workflows table · FTS5 virtual table · PRAGMA WAL    │
│  Triggers · Complexity · Integrations · Tags           │
└────────────────────────┬─────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────┐
│              Workflow Filesystem Catalog               │
│  workflows/[category]/*.json — 2,061 files             │
│  85 categories · 8,923 nodes · 48 trigger types        │
└──────────────────────────────────────────────────────┘
```

### Filesystem Catalog Layer

Workflow JSON files are stored flat under `workflows/`, organized by integration category (e.g., `Airtable/`, `Slack/`, `OpenAI/`). Each file contains the full n8n workflow serialization: `name`, `nodes` (array of node objects with type, position, parameters), `connections` (node graph edges), `settings`, `staticData`, `tags`, and timestamps. The file hash (`SHA-256`) deduplicates across imports.

### Database Layer (`workflow_db.py`)

The `WorkflowDatabase` class manages a local SQLite database with WAL journal mode, memory temp store, and tuned cache size (10,000 pages). The schema includes a `workflows` table for structured metadata (name, trigger type, complexity, node count, integrations as JSON array) and a `workflows_fts` FTS5 virtual table over `filename`, `name`, and `description` columns for sub-100ms full-text search. Index build uses batch inserts with explicit transaction boundaries.

### API Layer (`api_server.py`)

FastAPI 2.0 application with six endpoints: `/api/search` (FTS5 query with category/trigger/complexity filters), `/api/stats` (aggregate repository metrics), `/api/workflow/{id}` (individual workflow JSON or metadata), `/api/categories` (distinct category listing), `/api/export` (bulk download), and a static web UI root. Middleware stack includes `GZipMiddleware` (1000-byte threshold), CORS with restricted origin whitelist, and in-memory rate limiting (60 req/min per client).

## Key Components

| Component | File | Role |
|-----------|------|------|
| **FastAPI server** | `api_server.py` (835 lines) | REST API with 6 endpoints, CORS, rate limiting, static file serving |
| **Workflow DB** | `workflow_db.py` (835 lines) | SQLite with FTS5 — schema management, indexing, query builder |
| **Analytics engine** | `src/analytics_engine.py` | Workflow complexity analysis, pattern detection |
| **Integration hub** | `src/integration_hub.py` | Service integration metadata extraction from nodes |
| **Performance monitor** | `src/performance_monitor.py` | Query latency tracking, cache hit ratios |
| **Search index generator** | `scripts/generate_search_index.py` | Batch index all workflow JSONs into FTS5 |
| **Stats updater** | `scripts/update_readme_stats.py` | Regenerate repository-level statistics |
| **Workflow categories** | `workflows/[category]/` | 20+ top-level categories, 85 subdirectories, 2,061 JSON files |

### Workflow Pattern Taxonomy

Common integration patterns observed across the catalog:

- **Data Pipeline**: Trigger → Fetch → Transform → Store/Send (most common)
- **Integration Sync**: Cron → API Call → Compare → Update Systems
- **Notification Flow**: Webhook → Process → Conditional → Actions
- **Monitoring Loop**: Schedule → Check Status → Alert on Threshold

## Related

- [[n8n-workflows]] — Wiki entry for the workflow catalog
- [[n8n]] — Core n8n workflow engine architecture
- [[n8n-mcp]] — MCP server bridge to n8n
- [[awesome-n8n-templates]] — Alternative template collection
- [[n8n-architecture]] — n8n platform internals deep-dive
