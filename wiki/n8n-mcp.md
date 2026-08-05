---
name: n8n-mcp
description: "n8n-MCP server — 2,285 nodes indexed, MCP tools for AI-assisted n8n workflow authoring"
source: sources/n8n-mcp/
verification_date: 2026-07-12
verified_by: codegraph-verify
tags: [cli, docker, fair-code, integration, mcp, n8n, orchestration, storage, typescript, workflow-automation, n8n-mcp]
---

# n8n-MCP

## Overview

n8n-MCP is a **Model Context Protocol (MCP) server** that provides AI assistants (Claude, Copilot, Cursor, etc.) with comprehensive access to n8n workflow automation node documentation, properties, and operations. It bridges n8n's 2,285-node ecosystem (828 core + 1,457 community, 1,295 verified) and AI models, enabling AI-assisted workflow authoring without memorizing every node's parameter schema. Built for n8n 2.31.x compatibility — the README badge targets n8n 2.31.6, with all n8n packages pinned to 2.31.3.

Created by **Romuald Czlonkowski** ([www.aiadvisors.pl/en](https://www.aiadvisors.pl/en)), this is the reference implementation for AI-assisted n8n workflow building — it is the canonical way for LLMs to interact with n8n.

### Relationship to the n8n Ecosystem

- n8n is an open-source workflow automation platform with 828+ core nodes and 1,457+ community nodes spanning AI/LLM, HTTP, database, file, messaging, and SaaS integrations.
- n8n-MCP **is not** an n8n plugin or package — it is a standalone MCP server that reads n8n's `n8n-nodes-base`, `n8n-workflow`, `n8n-core`, and `@n8n/n8n-nodes-langchain` packages to build a searchable SQLite database of every node's parameters, operations, and documentation.
- It connects to an n8n instance via HTTP API (optional) to **read, create, update, and validate real workflows** — making it a bidirectional bridge: AI learns n8n, then AI controls n8n.
- n8n-MCP also ships an **n8n community-node wrapper** (`src/n8n/`) — an n8n node (`MCPNode`) that connects to external MCP servers from within a workflow, serving the opposite direction (n8n -> external MCP server).

## Architecture

```
                  MCP Client                        n8n Instance
               (Claude, Cursor,            (optional, for management tools)
                VS Code, etc.)                      |
                       |                            |
                       v                            v
               +--------------+             +------------------+
               |  MCP Server  | <---------> |  n8n HTTP API    |
               |  (stdio/http)|             |  (workflow CRUD) |
               +--------------+             +------------------+
                       |
         +-------------+-------------+
         |           |               |
         v           v               v
   +---------+ +---------+   +-----------+
   | SQLite  | |n8n npm  |   |Template   |
   | Node DB | |Packages |   |Repository |
   +---------+ +---------+   +-----------+
```

### Source Layout

| Directory | Purpose |
|---|---|
| `src/mcp/` | MCP server, tool definitions, handlers, tool documentation |
| `src/mcp/server.ts` | Core `N8NDocumentationMCPServer` class (~171KB, class defined at server.ts:168) — tool registration, execution, resource handling |
| `src/mcp/tools.ts` | Tool definitions for all MCP-exposed operations |
| `src/mcp/tools-n8n-manager.ts` | n8n workflow CRUD management tools |
| `src/mcp/handlers-n8n-manager.ts` | Handlers for n8n API operations (create, read, update, delete workflows) |
| `src/mcp/tool-docs/` | Structured documentation for every MCP tool (discovery, config, validation, guides, workflow management) |
| `src/mcp/tools-documentation.ts` | Documentation generation system for tools |
| `src/database/` | SQLite data access layer (node-repository, database-adapter with FTS5 support) |
| `src/services/` | Validation, type-structure, expression, workflow, property-filter, templates, similarity, telemetry services |
| `src/parsers/` | Node parsing and property extraction from n8n packages |
| `src/loaders/` | NPM package loader for n8n nodes |
| `src/mappers/` | Documentation mapping |
| `src/templates/` | n8n workflow template fetcher, repository, service |
| `src/n8n/` | n8n community-node wrapper (MCPNode, MCPApi credentials) — allows n8n workflows to connect to external MCP servers |
| `src/config/` | n8n API configuration |
| `src/types/` | TypeScript type definitions (tool, resource, prompt, instance-context, session-state) |
| `src/telemetry/` | Telemetry and anonymous usage tracking |
| `src/utils/` | Utilities: MCP client, bridge, caching, logging, HTTP helpers |
| `src/triggers/` | Trigger detection |
| `src/community/` | Community node management |
| `scripts/` | Build, validation, migration, test, and deployment scripts (80+ scripts) |
| `tests/` | Unit, integration, and E2E tests |
| `data/` | SQLite node databases, workflow patterns |
| `ui-apps/` | Dashboard/UI applications for the managed hosting |
| `docs/` | Deployment guides, IDE setup guides, self-hosting documentation |

## MCP Tools

The server registers **23 MCP tools** (defined in `manifest.json:84-177`, repo root): **7 core documentation/validation tools** that work offline against the bundled SQLite node database, and **16 n8n management tools** that require a live n8n instance via `N8N_API_URL` / `N8N_API_KEY`.

### Core Tools (7, offline)

| Tool | Purpose |
|---|---|
| `tools_documentation` | Get documentation for any MCP tool (START HERE) |
| `search_nodes` | Full-text search across all 2,285 nodes; `source: 'community'\|'verified'` filter, `includeExamples` for real configs |
| `get_node` | Unified node info: `detail: 'minimal'\|'standard'\|'full'`; modes `docs`, `search_properties`, `versions`, `compare`, `breaking`, `migrations` |
| `validate_node` | Node config validation: `mode: 'minimal'` (quick) or `'full'` (profiles: minimal, runtime, ai-friendly, strict) |
| `validate_workflow` | Complete workflow validation: structure, connections, expressions, AI tools |
| `search_templates` | Template search: `searchMode: 'keyword'\|'by_nodes'\|'by_task'\|'by_metadata'` |
| `get_template` | Get complete workflow JSON by template ID (modes: nodes_only, structure, full) |

### n8n Management Tools (16, require n8n API)

**Workflow management**
- `n8n_create_workflow` — Create new workflows with nodes and connections
- `n8n_get_workflow` — Get workflow by ID (modes: full, details, structure, minimal)
- `n8n_update_full_workflow` — Replace an entire workflow
- `n8n_update_partial_workflow` — Incremental diff-based updates (preferred; `addConnection`/`removeConnection` use four-parameter syntax)
- `n8n_delete_workflow` — Permanently delete workflows
- `n8n_list_workflows` — List workflows (minimal metadata)
- `n8n_validate_workflow` — Validate a deployed workflow by ID
- `n8n_autofix_workflow` — Auto-fix common workflow validation errors
- `n8n_workflow_versions` — Version history, rollback, cleanup
- `n8n_deploy_template` — Deploy an n8n.io template directly to your instance with auto-fix

**Execution**
- `n8n_test_workflow` — Test/trigger workflow execution (webhook, form, chat)
- `n8n_executions` — Unified execution management (get details, list, delete)

**Data & credentials**
- `n8n_manage_datatable` — Manage n8n data tables and rows (list, get, create, update, delete)
- `n8n_manage_credentials` — Manage n8n credentials (list, get, create, update, delete, getSchema)

**Security & system**
- `n8n_audit_instance` — Security audit combining n8n's audit API with deep workflow scanning
- `n8n_health_check` — Check n8n API connectivity and features

> **Note:** `n8n_list_available_tools` and `n8n_diagnostic` are **NOT** registered MCP tools — they exist only as tool-docs in `src/mcp/tool-docs/system/`.

Read-only deployment is supported: `DISABLED_TOOLS` removes write/destructive tools, `DISABLED_TOOL_OPERATIONS` blocks destructive operations on tools that bundle reads and writes (e.g. `n8n_workflow_versions:delete,rollback,prune`, `n8n_executions:delete`).

## Tools Documentation System

`src/mcp/tool-docs/` provides structured `ToolDocumentation` objects for every MCP tool, organized into:

| Category | Files |
|---|---|
| `configuration/` | `get-node.ts` |
| `discovery/` | `search-nodes.ts` |
| `guides/` | `ai-agents-guide.ts` |
| `system/` | `n8n-health-check.ts`, `n8n-diagnostic.ts`, `n8n-audit-instance.ts`, `n8n-list-available-tools.ts`, `tools-documentation.ts` |
| `templates/` | `get-template.ts`, `search-templates.ts` |
| `validation/` | `validate-node.ts`, `validate-workflow.ts` |
| `workflow_management/` | `n8n-*.ts` — CRUD, executions, versions, test, autofix, deploy-template, manage-datatable, manage-credentials |

Each `ToolDocumentation` has:
- **essentials**: Short description, key parameters, example, performance notes, tips
- **full**: Full description, parameters with types, return values, examples, use cases, best practices, pitfalls, related tools

## Data Layer

- **SQLite database** (`data/nodes.db`, ~95MB) stores parsed node metadata with FTS5 full-text search
- **Repository pattern**: All database operations through `NodeRepository`
- **Universal adapter**: Supports both `better-sqlite3` and `sql.js` backends
- **Workflow template cache**: 2,352+ templates fetched from n8n.io API with 99.96% AI metadata coverage
- **MCPB packable**: Can be packed as an MCP bundle (`.mcpb`)

## Key Features

- **2,285 n8n nodes** indexed: 828 core + 1,457 community (1,295 verified)
- **99% node property coverage** with detailed parameter schemas
- **66.5% operation coverage** across available node actions
- **86% documentation coverage** from official n8n docs (including AI nodes)
- **267 AI-capable tool variants** detected and documented
- **156 ranked configurations** extracted from popular templates
- **2,352 workflow templates** with metadata
- **n8n 2.31.x compatibility** — README badge 2.31.6; n8n packages pinned to 2.31.3
- **Multi-profile validation**: minimal, runtime, ai-friendly, strict profiles
- **Type structure validation**: Complex nested types (filter, resourceMapper, etc.)
- **n8n expression syntax validation**
- **Complete workflow structure validation** with diff engine

## n8n Community-Node Wrapper (src/n8n/)

The `src/n8n/` directory is the **n8n community-node wrapper** shipped with this repo — not the n8n product's built-in node. It lets n8n workflows connect to **external** MCP servers:

- **MCPNode** (`MCPNode.node.ts`) — An n8n community node that connects to external MCP servers, supporting operations: callTool, listTools, readResource, listResources, getPrompt, listPrompts
- **MCPApi** (`MCPApi.credentials.ts`) — Credential type for MCP server auth (Server URL, Auth Token, Connection Type)

This makes n8n-MCP a bidirectional bridge: the MCP server gives AI tools for n8n (AI → n8n), while the wrapper node lets n8n workflows call external MCP servers (n8n → MCP).

## Deployment

### Managed Hosting

**[dashboard.n8n-mcp.com](https://dashboard.n8n-mcp.com)** — the fastest way to try n8n-MCP with no installation:
- Free tier: 100 tool calls/day
- Always up-to-date n8n nodes and templates
- No infrastructure to manage — sign up, get an API key, connect your MCP client

### Self-Hosting

Supports multiple deployment modes (see `docs/SELF_HOSTING.md` and `docs/N8N_DEPLOYMENT.md`):
- **npx** — `npx -y n8n-mcp` (stdio)
- **Docker** — `ghcr.io/czlonkowski/n8n-mcp`
- **Railway** — One-click cloud deploy
- **Local / HTTP** — stdio and HTTP (SSE) transports, plus single-session HTTP for multi-tenant; n8n instance via `N8N_API_URL` / `N8N_API_KEY`, optional Cloudflare Access auth (`N8N_CF_CLIENT_ID` / `N8N_CF_CLIENT_SECRET`), and read-only deployment via `DISABLED_TOOLS` / `DISABLED_TOOL_OPERATIONS`

## Development

```bash
npm run build          # Compile TypeScript
npm run rebuild        # Rebuild node database from n8n packages
npm run validate       # Validate all node data
npm start              # Start stdio MCP server
npm run start:http     # Start HTTP MCP server
npm test               # Run test suite (5418+ passing tests)
npm run dev            # Build + rebuild + validate pipeline
```

## Key Dependencies

- `@modelcontextprotocol/sdk` — MCP protocol implementation
- `n8n-workflow` — n8n core type definitions
- `n8n-nodes-base` — n8n core node packages (runtime)
- `n8n-core`, `@n8n/n8n-nodes-langchain` — supporting n8n packages (all n8n packages pinned to 2.31.3)
- `better-sqlite3` (optional) / `sql.js` — SQLite database backends
- `express` — HTTP server framework

## Related Docs in This Vault

- [[n8n]] — Overall n8n platform documentation
- [[n8n-nodes]] — n8n node reference
- [[../sources/n8n-mcp/CLAUDE.md]] — Project CLAUDE.md with development instructions

> **Source**: `sources/n8n-mcp/`
