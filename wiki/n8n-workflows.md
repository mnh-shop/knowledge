---
name: n8n-workflows
liveurl: https://zie619.github.io/n8n-workflows/
description: "Curated collection of 2,061 n8n automation workflows with workflow patterns and metadata from the community repository"
source: sources/n8n-workflows/
verification_date: 2026-07-12
verified_by: codegraph-verify
tags: [ai-agents, automation, docker, git, integration-patterns, messaging, n8n, n8n-workflows, python, storage, webhook, workflows]
---

# n8n Workflows

A curated repository containing **2,061** n8n automation workflows available from the community source. This catalog serves as a production-ready workflow library and reference corpus for understanding integration patterns across services.

## Overview

[n8n](https://n8n.io/) is a fair-code, extensible workflow automation tool that connects services through a visual node-based interface. Each workflow is stored as a JSON file containing node definitions, connections, and configurations.

## Current Status

**Updated:** November 2025

**Key figures**:
- **2,061** workflow JSON definitions (updated from claimed 4,343)
- **319** distinct non-utility n8n-nodes-base.* service integrations (334 raw types incl. utility nodes)
- **188** service-named category directories under `workflows/`
- **30,774** total nodes across all workflows (avg 14.93 per workflow)
- **85** distinct trigger node types (top: manualTrigger 927, scheduleTrigger 330, executeWorkflowTrigger 180, formTrigger 123)
- **Analysis period:** July 2025 - November 2025

## Source Structure Analysis

The repository contains a different structure than documented:

```
n8n-workflows/
├── workflows/
│   └── [service]/              # 188 service-named category dirs, 2,061 workflow JSON files
├── src/                         # Workflow analysis scripts
│   ├── ai_assistant.py
│   ├── analytics_engine.py
│   ├── community_features.py
│   ├── integration_hub.py
│   ├── performance_monitor.py
│   └── user_management.py
├── scripts/                     # Utility scripts
│   ├── generate_search_index.py
│   ├── update_readme_stats.py
│   └── update_github_pages.py
├── api_server.py                # FastAPI application
├── workflow_db.py               # Database manager
├── run.py                      # Server launcher
└── docs/                       # Documentation
```

## Workflow Categories

The `workflows/` directory contains **188 service-named category directories** — one per n8n integration service, not curated topic folders. Directories take the n8n node class name (e.g. `Activecampaign`, `Awsrekognition`, `Baserow`, `Clickup`, `Emailreadimap`, `Emailsend`), alongside a small number of utility/flow dirs (e.g. `Aggregate`, `Code`, `Compression`, `Cron`, `Crypto`). Selected examples:

| Category dir | Typical content |
|--------------|-----------------|
| `Activecampaign` | ActiveCampaign marketing automation workflows |
| `Awsrekognition` | AWS Rekognition image analysis workflows |
| `Baserow` | Baserow database workflows |
| `Clickup` | ClickUp project management workflows |
| `Emailreadimap` | Email (IMAP) trigger workflows |
| `Emailsend` | Email (SMTP) send workflows |
| `Gmail` | Gmail trigger/action workflows |
| `Httprequest` | Generic HTTP request workflows |
| `Openai` | OpenAI LLM workflows |
| `Slack` | Slack messaging workflows |

Note: the "By The Numbers" table in the upstream `README.md` (lines 46-49) claims 4,343 workflows / 365 integrations / 29,445 nodes / 15 categories — these are stale upstream claims; the filesystem holds 2,061 workflow JSONs across 188 dirs with 30,774 computed nodes.

## Technical Specifications

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/api/search` | GET | Search workflows |
| `/api/stats` | GET | Repository statistics |
| `/api/workflow/{id}` | GET | Get workflow JSON |
| `/api/categories` | GET | List all categories |
| `/api/export` | GET | Export workflows |

### Features

- **Smart Search** — Full-text search across workflow names, descriptions, and nodes
- **15+ Categories** — Browse by specific use case or integration type
- **Mobile Ready** — Responsive design for any device
- **Direct Downloads** — Instant download of workflow JSONs
- **Advanced Filtering** — Filter by triggers, complexity, and services

## Workflow Analysis

### Collection Characteristics

- **Average complexity:** 14.93 nodes per workflow (30,774 nodes / 2,061 workflows; the upstream claim of 14.9 was accurate, an earlier wiki revision inverted it)
- **Most common trigger types:** manualTrigger (927), scheduleTrigger (330), executeWorkflowTrigger (180), formTrigger (123)
- **Popular integration patterns:**
  - Data pipelines (Trigger → Transform → Store/Send)
  - Integration sync (Cron → API → Compare → Update)
  - Email notification workflows

### Search Capabilities

The interface provides:

- **Full-text search** across all workflow metadata
- **Category filtering** for 15+ use cases
- **Trigger type filtering** (85 types available)
- **Service filtering** (319 integrations)
- **Complexity filtering** (Low/Medium/High)

## Usage

### Online Interface

Visit the live interface at **[zie619.github.io/n8n-workflows](https://zie619.github.io/n8n-workflows)** for:

- Instant workflow browsing
- Smart search functionality
- Category-based exploration
- Direct workflow downloads

### Local Installation

```bash
# Clone repository
git clone https://github.com/Zie619/n8n-workflows.git
cd n8n-workflows

# Install dependencies
pip install -r requirements.txt

# Start server
python run.py

# Access at http://localhost:8000
```

## Repository Usage

### For Analysis Tasks

When analyzing workflows in this repository:

1. Parse JSON files to understand workflow structure
2. Examine node chains to determine business functionality
3. Identify external services and API integrations
4. Consider execution flows and scheduling patterns

### Common Patterns Found

- **Data Pipeline**: Trigger → Fetch Data → Transform → Store/Send
- **Integration Sync**: Schedule → API Call → Compare → Update Systems
- **Notification**: Trigger → Process → Conditional Logic → Actions
- **Monitoring**: Cron → Check Status → Alert if Issues

## Status: Growing Repository

**Note:** This repository contains **2,061 workflows** and continues to grow. The collection represents curated best practices and common automation patterns for n8n users.

## Repository Metadata

- **Source:** `sources/n8n-workflows/`
- **Live Interface:** [zie619.github.io/n8n-workflows](https://zie619.github.io/n8n-workflows)
- **Search API:** FastAPI with SQLite FTS5
- **Total Nodes:** 30,774 across all workflows (avg 14.93)
- **Last Updated:** November 2025
- **License:** MIT

## Related

- [[n8n]] — Main n8n platform documentation
- [[n8n-workflows]] — Alternative link
- [[n8n-mcp]] — n8n MCP integration documentation