---
name: n8n-mcp
description: "n8n-MCP server — 1,845+ nodes indexed, MCP tools for AI-assisted n8n workflow authoring"
source: sources/n8n-mcp/
tags: [cli, docker, fair-code, integration, mcp, n8n, orchestration, storage, typescript, workflow-automation, n8n-mcp]
---

# n8n-MCP

## Overview

n8n-MCP is a **Model Context Protocol (MCP) server** that provides AI assistants (Claude, Copilot, Cursor, etc.) with comprehensive access to n8n workflow automation node documentation, properties, and operations. It bridges n8n's 1,845+ node ecosystem and AI models, enabling AI-assisted workflow authoring without memorizing every node's parameter schema.

Created by **Romuald Czlonkowski** ([www.aiadvisors.pl/en](https://www.aiadvisors.pl/en)), this is the reference implementation for AI-assisted n8n workflow building — it is the canonical way for LLMs to interact with n8n.

### Relationship to the n8n Ecosystem

- n8n is an open-source workflow automation platform with 816+ core nodes and 1,029+ community nodes spanning AI/LLM, HTTP, database, file, messaging, and SaaS integrations.
- n8n-MCP **is not** an n8n plugin or package — it is a standalone MCP server that reads n8n's @n8n/nodes-base and @n8n/nodes-source packages to build a searchable SQLite database of every node's parameters, operations, and documentation.
- It connects to an n8n instance via HTTP API (optional) to **read, create, update, and validate real workflows** — making it a bidirectional bridge: AI learns n8n, then AI controls n8n.
- The n8n product itself has a built-in "MCP Client Tool" node (`src/n8n/MCPNode.node.ts`) that can connect to external MCP servers from within a workflow, but n8n-MCP serves the opposite direction (AI -> n8n).

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
| `src/mcp/server.ts` | Core `N8NDocumentationMCPServer` class (179KB) — tool registration, execution, resource handling |
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
| `src/n8n/` | n8n-native node (MCPNode, MCPApi credentials) — allows n8n workflows to connect to external MCP servers |
| `src/config/` | n8n API configuration |
| `src/types/` | TypeScript type definitions (tool, resource, prompt, instance-context, session-state) |
| `src/telemetry/` | Telemetry and anonymous usage tracking |
| `src/utils/` | Utilities: MCP client, bridge, caching, logging, HTTP helpers |
| `src/triggers/` | n8n trigger definitions |
| `src/community/` | Community node management |
| `scripts/` | Build, validation, migration, test, and deployment scripts (80+ scripts) |
| `tests/` | Unit, integration, and E2E tests |
| `data/` | SQLite node databases, workflow patterns |
| `ui-apps/` | Dashboard/UI applications for the managed hosting |
| `docs/` | Deployment guides, IDE setup guides, self-hosting documentation |

## MCP Tools

The server exposes tools organized into these categories:

### Discovery Tools
- **n8n_list_available_tools** — List all available n8n tools/functions
- **n8n_search_nodes** — Full-text search across 1,845 node types
- **n8n_get_node_essentials** — Get essential parameters for a node (optimized, faster)
- **n8n_get_node_info** — Get full node information
- **n8n_get_node_documentation** — Get external documentation for a node
- **n8n_search_node_properties** — Search within a node's properties
- **n8n_list_ai_tools** — List AI-capable tool variants (265+ detected)

### Configuration Tools
- **n8n_validate_node_operation** — Validate a full node configuration
- **n8n_validate_node_minimal** — Check minimal required fields
- **n8n_generate_workflow** — Generate a complete workflow from a description
- **n8n_generate_workflow_doc** — Generate documentation for existing workflows

### Workflow Validation Tools
- **n8n_validate_workflow** — Complete workflow structure validation
- **n8n_update_partial_workflow** — Update specific parts of a workflow
- **n8n_list_available_tools** — Discover available tools for workflow building
- **Workflow diff engine** — Efficient diff-based workflow updates

### Management Tools (require n8n API connection)
- **n8n_create_workflow** — Create a new workflow on the n8n instance
- **n8n_read_workflow** — Read workflow definitions
- **n8n_update_workflow** — Update existing workflows
- **n8n_delete_workflow** — Delete workflows
- **n8n_activate_workflow** / **n8n_deactivate_workflow** — Toggle workflow active state
- **n8n_list_workflows** — List all workflows
- **n8n_execute_workflow** — Trigger workflow execution
- **n8n_get_execution** — Get execution status and results
- **n8n_audit_instance** — Audit the n8n instance configuration
- **n8n_diagnostic** — Run diagnostics on the n8n instance
- **n8n_health_check** — Check n8n instance health

## MCP Resources

The server exposes resources for node documentation:
- `n8n://docs/{nodeType}` — Documentation for a specific node
- `n8n://essentials/{nodeType}` — Essential parameters for a node
- UI app resources (dashboard)
- Skill resources (Claude skills integration)

## Tools Documentation System

`src/mcp/tool-docs/` provides structured `ToolDocumentation` objects for every MCP tool, organized into:

| Category | Files |
|---|---|
| `configuration/` | `get-node.ts`, `validate-node.ts` |
| `discovery/` | `search-nodes.ts`, `list-available-tools.ts` |
| `guides/` | `ai-agents-guide.ts` |
| `system/` | `health-check.ts`, `diagnostic.ts`, `audit-instance.ts` |
| `templates/` | Template-related documentation |
| `validation/` | `validate-workflow.ts` |
| `workflow_management/` | CRUD operations, execution, update, diff |

Each `ToolDocumentation` has:
- **essentials**: Short description, key parameters, example, performance notes, tips
- **full**: Full description, parameters with types, return values, examples, use cases, best practices, pitfalls, related tools

## Data Layer

- **SQLite database** (`data/nodes.db`) stores parsed node metadata with FTS5 full-text search
- **Repository pattern**: All database operations through `NodeRepository`
- **Universal adapter**: Supports both `better-sqlite3` and `sql.js` backends
- **Workflow template cache**: 2,352+ templates fetched from n8n.io API with 99.96% AI metadata coverage
- **MCPB packable**: Can be packed as an MCP bundle (`.mcpb`)

## Key Features

- **1,845 n8n nodes** indexed: 816 core + 1,029 community (911 verified)
- **99% node property coverage** with detailed parameter schemas
- **63.6% operation coverage** across available node actions
- **87% documentation coverage** from official n8n docs
- **265 AI-capable tool variants** detected and documented
- **156 ranked configurations** extracted from popular templates
- **2,352 workflow templates** with metadata
- **Multi-profile validation**: minimal, runtime, ai-friendly, strict profiles
- **Type structure validation**: Complex nested types (filter, resourceMapper, etc.)
- **n8n expression syntax validation**
- **Complete workflow structure validation** with diff engine

## n8n Node Module

The `src/n8n/` directory contains n8n-native integration code:
- **MCPNode** (`MCPNode.node.ts`) — An n8n node type that connects to external MCP servers, supporting operations: callTool, listTools, readResource, listResources, getPrompt, listPrompts
- **MCPApi** (`MCPApi.credentials.ts`) — Credential type for MCP server auth (Server URL, Auth Token, Connection Type)

This means n8n-MCP is both an **MCP server** (AI tools for n8n) and provides an **MCP client node** for n8n workflows (n8n calling external MCP servers).

## Deployment

Supports multiple deployment modes:
- **stdio** — Direct integration with Claude Desktop, Claude Code, VS Code
- **HTTP** — Remote MCP server with SSE transport
- **Docker** — Containerized deployment via Docker Compose
- **Railway** — One-click cloud deploy
- **Single-session HTTP** — Session-persistent HTTP mode for multi-tenant

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
- `@n8n/nodes-base` — n8n core node packages (runtime)
- `better-sqlite3` / `sql.js` — SQLite database backends
- `express` — HTTP server framework
- `node-fetch` — HTTP client for n8n API
- `winston` — Logging

## Related Docs in This Vault

- [[n8n]] — Overall n8n platform documentation
- [[n8n-nodes]] — n8n node reference
- [[../sources/n8n-mcp/CLAUDE.md]] — Project CLAUDE.md with development instructions

> **Source**: `sources/n8n-mcp/`
