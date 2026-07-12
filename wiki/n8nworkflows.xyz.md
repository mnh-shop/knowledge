---
name: n8nworkflows.xyz
tags: [n8nworkflows.xyz, n8n, workflow-automation, templates, community]
description: "Community workflow template catalog for n8n automation"
source: sources/n8nworkflows.xyz/
---

# n8nworkflows.xyz

| Field | Value |
|---|---|
| **Origin** | [n8n-workflows/n8nworkflows.xyz](https://github.com/n8n-workflows/n8nworkflows.xyz) |
| **Source** | `sources/n8nworkflows.xyz/` |
| **Repomix** | `raw/n8nworkflows.xyz/n8nworkflows.xyz.xml` |
| **Codegraph** | `graphs/n8nworkflows.xyz/` |

## Overview

n8nworkflows.xyz is a community-driven catalog of workflow templates for n8n, the open-source workflow automation platform. It provides a searchable collection of pre-built automation workflows covering integrations with common SaaS platforms, data processing pipelines, notification systems, and AI/LLM integration patterns. The catalog serves as both a reference library and a starting point for building custom automations.

## Key Features

- **Template Library** — Curated collection of reusable n8n workflow templates across multiple categories
- **Integration Coverage** — Templates spanning CRM, email, messaging, cloud storage, AI/LLM, and development tools
- **Search & Discovery** — Tag-based and category-based browsing for finding relevant workflows
- **Exportable JSON** — All templates available as standard n8n workflow JSON for direct import
- **Community Contributions** — Open submission process for users to share their workflow patterns
- **Usage Documentation** — Each template includes setup instructions, required credentials, and configuration notes

## Architecture

The catalog is published as a static website built from workflow template definitions stored as structured JSON files. Each template includes metadata (tags, category, required integrations) alongside the n8n workflow definition. The site provides filtering, search, and one-click copy functionality for importing workflows directly into n8n instances.

## Related

- [[n8n]] — Open-source workflow automation platform that consumes these templates
- [[n8n-workflows]] — Official n8n workflow template collection
- [[awesome-n8n-templates]] — Community-curated list of n8n workflow resources
- [[n8n-skills]] — Agent skills for building and deploying n8n workflows
