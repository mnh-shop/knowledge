---
name: n8nworkflows.xyz
tags: [n8nworkflows.xyz, n8n, workflow-automation, templates, community]
description: "Community workflow template catalog for n8n automation"
source: sources/n8nworkflows.xyz/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# n8nworkflows.xyz

| Field | Value |
|---|---|
| **Origin** | [nusquama/n8nworkflows.xyz](https://github.com/nusquama/n8nworkflows.xyz) |
| **Source** | `sources/n8nworkflows.xyz/` |
| **Repomix** | `raw/n8nworkflows.xyz/n8nworkflows.xyz.xml` |
| **Codegraph** | `graphs/n8nworkflows.xyz/` |

## Overview

n8nworkflows.xyz is a community-driven catalog of 9,823 n8n workflow templates, preserved as a versionable archive from the official [n8n.io/workflows](https://n8n.io/workflows) website. Maintained by [nusquama](https://github.com/nusquama/n8nworkflows.xyz), this repository allows users to preserve, version, and reuse workflow templates in a minimal, offline-ready format. The corresponding website at [n8nworkflows.xyz](https://n8nworkflows.xyz) provides a searchable interface for browsing and discovering workflows.

Each workflow is isolated in its own folder with a standardized file set: a Markdown description (`readme-{id}.md`), the raw workflow JSON for direct n8n import (`{snake_case}.json`), structured metadata including author tags and creation date (`metada-{id}.json`), and a workflow screenshot in WebP format (`{id}--{kebab-case}.webp`). The folder names embed the workflow id (e.g. `RAG Chatbot for Company Documents using Google Drive and Gemini-2753`). The vast majority of folders hold 4 files; 265 of the 9,823 folders deviate (mostly 3 files, i.e. missing the screenshot; some malformed/duplicate 1-file dirs). This structured format facilitates navigation, versioning, and individual import whether online or offline.

The catalog covers an extraordinary breadth of automation use cases — from AI agent chatbots and email auto-responders to SEO content pipelines, CRM integrations, social media publishing, financial analysis, developer tooling, and MCP server implementations. The repository is independently maintained and not officially affiliated with n8n.

## Key Features

- **9,823 Workflow Templates** — The largest community archive of n8n workflows, spanning AI/LLM integrations, CRM automation, email marketing, social media management, data processing, e-commerce, HR, finance, DevOps, and security.
- **Standardized Archive Format** — Every workflow stored as 4 files per folder: `readme-{id}.md` (description), `{snake_case}.json` (importable definition), `metada-{id}.json` (author, tags, creation date, public n8n.io link), and a workflow screenshot in WebP format (`{id}--{kebab-case}.webp`). 265 of 9,823 folders deviate from the 4-file norm (mostly missing the screenshot).
- **Offline-Ready** — All workflow JSON files are self-contained and importable directly into any n8n instance without requiring network access to the official n8n workflow registry.
- **Version Control** — Git-based versioning preserves the complete history of archived workflows, enabling diffing, rollback, and tracking of template evolution over time.
- **Extensive AI/LLM Coverage** — Thousands of workflows featuring OpenAI (GPT-4o, GPT-4.1, o3), Anthropic Claude, Google Gemini, Mistral AI, Groq, DeepSeek, Ollama local LLMs, and Perplexity integration patterns including RAG, agentic loops, multi-model routing, and tool-use architectures.
- **MCP Server Templates** — Dedicated section of MCP server workflow templates covering eBay APIs, New York Times, Google services, Clearbit, Sentry, PagerDuty, and many more SaaS tools.
- **Community Sourced** — Workflows are archived from community submissions to n8n.io/workflows, preserving the creativity and problem-solving patterns of the global n8n user community.
- **Compact Structure** — Minimal file-per-workflow format that avoids unnecessary boilerplate while being human-readable and machine-parseable.

## Architecture

The repository is structured as a flat archive:

```
n8nworkflows.xyz/
└── workflows/
    ├── workflow-name-id-1/          # e.g. RAG Chatbot ... Gemini-2753
    │   ├── readme-2753.md           # Workflow description in Markdown
    │   ├── rag_chatbot_....json     # Raw n8n workflow JSON (direct import)
    │   ├── metada-2753.json         # Author, tags, creation date, public link
    │   └── 2753--rag-chatbot-....webp  # Screenshot/hero image
    ├── workflow-name-id-2/
    │   └── ...
    └── ...
```

Each `{snake_case}.json` is a standard n8n workflow export containing the full node graph, connections, credentials references, and settings. Import into any n8n instance via the "Import from File" or "Import from URL" features in the n8n editor.

The `metada-{id}.json` captures structured information about each workflow including the original author (anonymized as `user_*`), categorization tags, creation date, and a public link back to the original listing on n8n.io. The WebP screenshot provides a visual reference of the workflow graph.

## Usage

### Browsing Workflows

Browse the [n8nworkflows.xyz website](https://n8nworkflows.xyz) for a searchable interface, or explore the `workflows/` directory directly in the GitHub repository. Workflow categories include:

- **AI Agents & Chatbots** — Telegram/WhatsApp/Slack/Instagram AI bots with memory, tool-use, and multi-agent orchestration
- **Email Automation** — Gmail/Outlook auto-responders, inbox triage with AI classification, invoice processing
- **CRM & Sales** — HubSpot/Salesforce/Pipedrive/GoHighLevel lead management, enrichment, scoring, and outreach sequences
- **Content & Social Media** — Automated blog generation, social media publishing, video creation, and content repurposing
- **Data Processing** — ETL pipelines, EDI parsing, document extraction, and database synchronization
- **Development & DevOps** — GitHub/GitLab automation, CI/CD workflows, incident response, and monitoring alerts
- **E-Commerce** — Shopify/WooCommerce order processing, abandoned cart recovery, product management
- **MCP Servers** — Tool MCP server templates for eBay, SaaS platforms, news APIs, and more

### Importing a Workflow

```bash
# Navigate to the workflow folder (name includes the workflow id, e.g. -2753)
cd workflows/your-workflow-name-id/
# Import the {snake_case}.json file (the standard n8n workflow export) via:
# n8n editor → Import from File → select {snake_case}.json
```

Or use the n8n API (substituting the folder's `{snake_case}.json`):

```bash
curl -X POST https://your-n8n-instance/api/v1/workflows \
  -H "Content-Type: application/json" \
  -H "X-N8N-API-KEY: your-api-key" \
  -d @your_snake_case_file.json
```

### Notable Workflow Categories

The archive contains significant coverage of:

- AI Research Agents with multi-source search (Perplexity, Tavily, Brave) and RAG pipelines
- MCP Tool Servers for 100+ SaaS APIs (Google Drive, Stripe, Salesforce, Trello, GitLab, etc.)
- Automated content factories (RSS → Blog → Social Media → Multi-platform publishing)
- AI Customer Support systems with human handoff
- SEO audit pipelines with keyword research and content optimization
- Financial analysis and cryptocurrency market monitoring
- Social media content repurposing (YouTube → TikTok → Instagram → Reels)

## Related

- [[n8n]] — Open-source workflow automation platform that consumes these templates
- [[n8n-workflows]] — Official n8n workflow template collection from n8n.io
- [[awesome-n8n-templates]] — Community-curated list of n8n workflow resources
- [[n8n-skills]] — Agent skills for building and deploying n8n workflows
- [[n8n-mcp]] — MCP node indexer supporting MCP server workflows in n8n
