---
name: n8n-supabase-ai-pipeline
type: integration
tags: [n8n, supabase, integration, ai, database, vector, embeddings, rag]
description: "Integration: n8n AI agent workflows with Supabase storage + PostgreSQL vector embeddings for RAG pipelines and tool calls"
---

# Integration: n8n + Supabase AI Pipeline

**Source**: `sources/n8n/`, `sources/n8n-mcp/`

## Overview

Wires n8n's AI agent capabilities to Supabase as a unified backend for structured data (PostgreSQL), vector storage (pgvector), and file storage. n8n workflows ingest documents, generate embeddings via an LLM provider, store vectors in Supabase for semantic search, and expose the pipeline through webhooks or n8n-MCP.

## Architecture

```
User / AI Client → n8n (HTTP/Webhook, AI Agent, Embeddings, Supabase nodes) → Supabase (PostgreSQL + pgvector + Storage)
```

## Configuration

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE documents (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), content TEXT NOT NULL, metadata JSONB DEFAULT '{}', embedding VECTOR(1536), created_at TIMESTAMPTZ DEFAULT now());
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

Generate a `service_role` key from the Supabase dashboard. In n8n, configure **Supabase credentials** (Project URL + service_role key) and **LLM credentials** (OpenAI API key or local Ollama).

## Deployment (Podman Quadlet)

```yaml
# n8n.container
[Container]
Image=docker.n8n.io/n8nio/n8n:latest
Environment=DB_TYPE=postgresdb DB_POSTGRESDB_HOST=supabase-db DB_POSTGRESDB_PASSWORD=changeme
Volume=n8n_data:/home/node/.n8n:U
Pod=n8n-supabase.pod
PublishPort=5678:5678

# supabase-db.container
[Container]
Image=pgvector/pgvector:pg17
Environment=POSTGRES_PASSWORD=changeme
Volume=pgvector_data:/var/lib/postgresql/data:U
Pod=n8n-supabase.pod
```

For managed Supabase (recommended), use the cloud connection string directly in n8n credentials.

### RAG Pipeline Workflow

1. **Trigger** → Webhook receives document
2. **Chunk** → Split text into 512-token segments
3. **Embed** → OpenAI embeddings per chunk
4. **Store** → Insert into Supabase `documents` table
5. **Query** → Embed query, pgvector similarity search, return as LLM context

## Related

- [[n8n]] — Workflow automation platform
- [[n8n-mcp]] — MCP server for AI-assisted n8n workflow building
- [[supabase]] — Firebase alternative with PostgreSQL + vector storage
- [[postgresql]] — Relational database backend
