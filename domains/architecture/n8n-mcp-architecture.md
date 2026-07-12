---
name: n8n-mcp-architecture
tags: [n8n-mcp, architecture, n8n, mcp]
description: "MCP server bridging AI assistants to n8n's 1,845+ node ecosystem — dual-mode transport, SQLite FTS5 indexing, multi-stage node processing pipeline"
source: sources/n8n-mcp/
verification_date: 2026-07-12
verified_by: codegraph + wiki
---

# n8n-MCP — Architecture

**Source:** `sources/n8n-mcp/`

## Overview

n8n-MCP is a standalone **Model Context Protocol (MCP) server** that provides AI assistants (Claude, Copilot, Cursor) with comprehensive access to n8n's workflow automation node ecosystem. It is the canonical way for LLMs to interact with n8n — not an n8n plugin, but an external bridge that reads `@n8n/nodes-base` and `@n8n/nodes-source` packages to build a searchable SQLite database of every node's parameters, operations, and documentation. Optionally connects to an n8n instance via HTTP API for bidirectional workflow CRUD.

## Architecture

```
                    MCP Client                          n8n Instance
                 (Claude, Cursor,              (optional, workflow CRUD)
                  VS Code, etc.)                        |
                         |                              |
                         v                              v
                 +---------------+              +------------------+
                 |  MCP Server    | <---------> |  n8n HTTP API    |
                 |  (stdio/http)  |              |  (workflow CRUD) |
                 +---------------+              +------------------+
                         |
           +-------------+-------------+
           |             |             |
           v             v             v
     +---------+   +---------+   +-----------+
     | SQLite  |   | n8n npm  |   | Template  |
     | Node DB |   | Packages |   | Repository|
     +---------+   +---------+   +-----------+
```

### Dual-Mode Transport

The server operates in two transport modes selected at startup:

- **stdio mode** (`npm start`): Direct process integration with Claude Desktop, Claude Code, VS Code. The MCP server communicates via stdin/stdout, with console output isolated via `ConsoleManager` to prevent protocol corruption.
- **HTTP mode** (`npm run start:http`): Remote SSE-based transport via Express. Exposes a full HTTP API for multi-tenant deployments, including a single-session HTTP variant for session-persistent use.

### Node Processing Pipeline

The pipeline ingests n8n packages into the searchable database through these stages:

1. **Loader** (`src/loaders/node-loader.ts`): Loads node definitions from installed `@n8n/nodes-base` and `@n8n/nodes-source` npm packages. Handles version resolution and package discovery.

2. **Parser** (`src/parsers/node-parser.ts`): Extracts node metadata, parameter schemas, operation definitions, and type information. Supports versioned node structures and typeVersion-aware parsing.

3. **Property Extractor** (`src/parsers/property-extractor.ts`): Performs deep property analysis — extracts all parameter types, constraints, display conditions, and nested type structures (filter, resourceMapper, etc.). Achieves 99% node property coverage.

4. **Docs Mapper** (`src/mappers/docs-mapper.ts`): Maps external documentation URLs and content to each node type and operation, achieving 87% documentation coverage from official n8n docs.

5. **Database Indexing** (`src/database/`): Stores parsed metadata in SQLite with FTS5 full-text search via a universal adapter supporting both `better-sqlite3` and `sql.js` backends. The `NodeRepository` class provides the data access layer.

### Service Layer

MCP tool handlers delegate to a layered service architecture:

| Service | File | Purpose |
|---------|------|---------|
| Property Filter | `services/property-filter.ts` | Reduces node properties to AI-friendly essentials |
| Config Validator | `services/config-validator.ts` | Multi-profile validation (minimal, runtime, ai-friendly, strict) |
| Enhanced Config Validator | `services/enhanced-config-validator.ts` | Operation-aware validation with 22 type structures |
| Expression Validator | `services/expression-validator.ts` | Validates n8n template expression syntax |
| Workflow Validator | `services/workflow-validator.ts` | Complete workflow structure validation with diff engine |
| Type Structure Service | `services/type-structure-service.ts` | Validates complex nested types (filter, resourceMapper, etc.) |
| Template Service | `templates/template-service.ts` | Template business logic over 2,352+ cached templates |

## Key Components

### MCP Server (`src/mcp/server.ts` — 4,852 lines)

Core `N8NDocumentationMCPServer` class implementing the MCP protocol. Handles tool registration, execution, resource handling, protocol version negotiation, and session management. Registers 25+ tools across discovery, configuration, validation, and management categories.

### Tool Documentation System (`src/mcp/tool-docs/`)

Every MCP tool carries structured `ToolDocumentation` with two detail levels:
- **essentials**: Short description, key parameters, example, performance notes, tips
- **full**: Complete documentation with parameters, types, return values, use cases, best practices, pitfalls

### n8n Native Node (`src/n8n/MCPNode.node.ts`)

A bidirectional capability — n8n-MCP is both an MCP server (AI → n8n) and provides an MCP client node for n8n workflows (n8n → external MCP servers). Supports operations: callTool, listTools, readResource, listResources, getPrompt, listPrompts.

### SQLite Database (`data/nodes.db`)

Stores: 1,845 node types (816 core + 1,029 community), 63.6% operation coverage, 2,352 workflow templates with 99.96% AI metadata coverage. MCPB-packable as `.mcpb` bundles.

## Related

- [[n8n-mcp]] — Wiki page with full tool reference and deployment modes
- [[n8n]] — Overall n8n platform documentation
- [[mcp]] — Model Context Protocol reference
- [[n8n-workflows]] — Workflow template catalog
- [[hermes-agent]] — Comparable agent platform with MCP plugin architecture
- [[mission-control]] — MCP audit server for monitoring MCP interactions
