---
name: n8n-workflow-catalog
description: "Catalog of 4,343 production-ready n8n workflow templates with 365+ integrations, searchable via web interface and API"
source: sources/n8n-workflows/
tags: [fair-code, integration, n8n, n8n-workflows, templates, workflow-automation, automation, api, sqlite, fastapi]
---

# n8n Workflow Catalog

A comprehensive collection of production-ready n8n workflow templates designed to accelerate automation development across 15+ categories and 365+ service integrations.

## Description

The n8n Workflow Catalog provides an extensive library of pre-built automation workflows that can be imported directly into n8n instances. Each workflow is stored as a structured JSON file containing node definitions, connections, and configurations. The collection is backed by a FastAPI server with SQLite FTS5 full-text search, enabling instant discovery of workflows through both a web interface and REST API.

The project serves as both a template repository and a reference implementation, demonstrating patterns for common automation scenarios like data pipelines, integration syncs, and monitoring systems. Users can browse workflows online at [zie619.github.io/n8n-workflows](https://zie619.github.io/n8n-workflows) without any installation required.

## Key Features

- **4,343 Production-Ready Workflows** — Curated collection covering diverse automation needs
- **365+ Unique Integrations** — Support for major services including Slack, Discord, HTTP APIs, databases, and cloud platforms
- **15+ Category Organization** — Workflows grouped by use case (Marketing, Sales, DevOps, AI/ML, etc.)
- **Full-Text Search** — SQLite FTS5 integration for sub-100ms search across names, descriptions, and nodes
- **Web Interface** — Modern responsive UI with dark/light mode support at the GitHub Pages site
- **REST API Access** — Programmatic access via `/api/search`, `/api/stats`, `/api/workflow/{id}` endpoints
- **Docker Deployment** — Multi-platform container images for amd64 and arm64 architectures
- **Security Hardened** — Path traversal protection, input validation, CORS protection, and Trivy scanning

## Repository Structure

The source repository contains three primary areas:

- `workflows/` — Directory housing all 4,343+ JSON workflow files, organized by integration category
- `src/` — Python source code for the API server and database management
- `api_server.py` — FastAPI application providing REST endpoints for workflow access

Each workflow JSON includes standard n8n fields: `name`, `nodes`, `connections`, `settings`, `staticData`, and `tags`.

## Related Resources

- [[n8n-workflows]] — Detailed statistics and category breakdown of the workflow collection
- [[awesome-n8n-templates]] — Additional curated templates for n8n automation
- [[n8n]] — General n8n platform documentation and node reference

## Quick Start

To run the catalog locally:

```bash
git clone https://github.com/Zie619/n8n-workflows.git
cd n8n-workflows
pip install -r requirements.txt
python run.py
```

Or using Docker:
```bash
docker run -p 8000:8000 zie619/n8n-workflows:latest
```

## API Reference

The FastAPI server exposes several endpoints for programmatic access:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface with search UI |
| `/api/search` | GET | Full-text search across workflows |
| `/api/stats` | GET | Repository statistics summary |
| `/api/workflow/{id}` | GET | Retrieve specific workflow JSON |
| `/api/categories` | GET | List all workflow categories |
| `/api/export` | GET | Export workflows in bulk |

Search supports filtering by trigger type (Webhook, Schedule, Manual), complexity level (Low, Medium, High), and specific service integrations.

## Technical Architecture

The system follows a clean three-tier architecture:

1. **Frontend Layer** — Static HTML/JS interface with Tailwind CSS styling, hosted via GitHub Pages
2. **API Layer** — FastAPI Python server handling search and retrieval requests
3. **Data Layer** — SQLite database with FTS5 extension enabling fast full-text indexing

The database indexes workflow metadata including names, descriptions, node types, and category tags. The `workflow_db.py` module manages database initialization and query operations, while `api_server.py` routes requests to appropriate handlers.

## Use Cases

Common patterns demonstrated in the catalog include:

- **Data Pipeline Automation** — Fetch data from APIs, transform, and store in databases
- **Integration Sync** — Keep multiple services synchronized with scheduled comparisons
- **Webhook Processing** — Handle incoming webhooks and trigger downstream actions
- **AI/ML Workflows** — Connect to LLM APIs for document processing and inference tasks
- **DevOps Monitoring** — Scheduled health checks with alerting on failures
- **Sales & Marketing** — Lead capture, email campaigns, CRM synchronization

Each workflow follows n8n conventions with clear trigger mechanisms and modular node structures for easy customization.