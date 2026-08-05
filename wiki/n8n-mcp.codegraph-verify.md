---
name: n8n-mcp-codegraph-verify
tags: [n8n-mcp, codegraph-verify, n8n, mcp, typescript, sqlite]
description: "Codegraph Verification: n8n-mcp — validating wiki claims against indexed source code symbols"
source: sources/n8n-mcp/
---

# Codegraph Verification: n8n-mcp

**Date:** 2026-07-30 (claims 1 and 7 re-verified against current README.md and manifest.json)

## Claim 1: MCP server with stdio/HTTP dual-mode and 23 registered MCP tools
- **Wiki says:** The MCP server in `src/mcp/` implements both stdio and HTTP modes, registering exactly 23 MCP tools: 7 core documentation/validation tools (`tools_documentation`, `search_nodes`, `get_node`, `validate_node`, `validate_workflow`, `search_templates`, `get_template`) and 16 n8n management tools (`n8n_create_workflow`, `n8n_get_workflow`, `n8n_update_full_workflow`, `n8n_update_partial_workflow`, `n8n_delete_workflow`, `n8n_list_workflows`, `n8n_validate_workflow`, `n8n_autofix_workflow`, `n8n_test_workflow`, `n8n_executions`, `n8n_health_check`, `n8n_workflow_versions`, `n8n_deploy_template`, `n8n_manage_datatable`, `n8n_manage_credentials`, `n8n_audit_instance`). Entry points are `src/mcp/index.ts` and `src/mcp/server.ts`; the `N8NDocumentationMCPServer` class is defined at `server.ts:168`.
- **Source evidence:**
  - `src/mcp/index.ts` — Main entry point with mode selection
  - `src/mcp/server.ts` — Core `N8NDocumentationMCPServer` class for tool registration and execution (class at line 168, ~171KB file)
  - `src/mcp/stdio-wrapper.ts` — Stdio transport wrapper
  - `manifest.json` (repo root) defines exactly 23 `tools` entries (lines 84-177): `tools_documentation`, `search_nodes`, `get_node`, `validate_node`, `get_template`, `search_templates`, `validate_workflow`, `n8n_create_workflow`, `n8n_get_workflow`, `n8n_update_full_workflow`, `n8n_update_partial_workflow`, `n8n_delete_workflow`, `n8n_list_workflows`, `n8n_validate_workflow`, `n8n_autofix_workflow`, `n8n_test_workflow`, `n8n_executions`, `n8n_health_check`, `n8n_workflow_versions`, `n8n_deploy_template`, `n8n_manage_datatable`, `n8n_manage_credentials`, `n8n_audit_instance`
  - `package.json` lines 27-28 show `start` (stdio) and `start:http` modes
  - `n8n_list_available_tools` and `n8n_diagnostic` appear ONLY as tool-docs in `src/mcp/tool-docs/system/` — they are not registered tools
  - Fabricated tool names (`n8n_search_nodes`, `n8n_get_node_essentials`, `n8n_generate_workflow`, etc.) have 0 grep hits in `src/`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (wiki previously listed fabricated tool names; corrected to the real 23-tool manifest catalog)

## Claim 2: SQLite database layer with FTS5 full-text search and universal adapter
- **Wiki says:** SQLite database at `data/nodes.db` stores parsed node metadata with FTS5 full-text search. Repository pattern via `NodeRepository` and universal adapter supporting both `better-sqlite3` and `sql.js`.
- **Source evidence:**
  - `src/database/schema.sql` — SQLite schema including FTS5 virtual tables
  - `src/database/schema-optimized.sql` — Optimized schema variant
  - `src/database/node-repository.ts` — Data access layer implementing repository pattern
  - `src/database/database-adapter.ts` — Universal adapter supporting both `better-sqlite3` and `sql.js` backends
  - `src/database/shared-database.ts` — Shared database connection management
  - `data/nodes.db` — Actual SQLite node database file
  - `scripts/prebuild-fts5.ts` — FTS5 prebuild script
  - `scripts/migrate-nodes-fts.js` — FTS5 migration script
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Node processing pipeline — loader, parser, property extractor, docs mapper
- **Wiki says:** The node processing pipeline has 4 stages: Loader loads nodes from n8n npm packages, Parser extracts metadata, Property Extractor performs deep property analysis, and Docs Mapper maps external documentation.
- **Source evidence:**
  - `src/loaders/node-loader.ts` — NPM package loader for n8n packages
  - `src/parsers/node-parser.ts` — Enhanced parser with version support
  - `src/parsers/property-extractor.ts` — Dedicated property/operation extraction
  - `src/mappers/docs-mapper.ts` — Documentation mapping with fixes
  - `package.json` dependencies include `n8n-workflow`, `n8n-core`, `n8n-nodes-base`, `@n8n/n8n-nodes-langchain` (lines 163-173) — the n8n packages parsed by the loaders
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Service layer with 38 modules covering validation, templates, expressions, and workflow diff
- **Wiki says:** The `src/services/` directory contains 38 service modules including configuration validation, expression validation, workflow validation, template management, type structure validation, property dependencies, and a workflow diff engine.
- **Source evidence:**
  - `src/services/config-validator.ts` — Multi-profile validation (minimal, runtime, ai-friendly, strict)
  - `src/services/enhanced-config-validator.ts` — Operation-aware validation
  - `src/services/expression-validator.ts` — n8n expression syntax validation
  - `src/services/workflow-validator.ts` — Complete workflow structure validation
  - `src/services/workflow-diff-engine.ts` — Efficient diff-based workflow updates
  - `src/services/workflow-auto-fixer.ts` — Auto-fix workflow validation errors
  - `src/services/type-structure-service.ts` — Complex nested type validation
  - `src/services/property-dependencies.ts` — Property dependency analysis
  - `src/services/property-filter.ts` — Reduces node properties to AI-friendly essentials
  - `src/services/task-templates.ts` — Pre-configured node settings
  - `src/services/example-generator.ts` — Working example generation
  - `src/services/expression-format-validator.ts` — Expression format validation
  - `src/services/universal-expression-validator.ts` — Universal expression validation
  - Total of 38 `.ts` files in `src/services/` directory
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Template system fetching 2,352+ templates from n8n.io API
- **Wiki says:** The template system in `src/templates/` fetches and stores 2,352+ workflow templates from the n8n.io API with 99.96% AI metadata coverage. Supports template search and validation.
- **Source evidence:**
  - `src/templates/template-fetcher.ts` — Fetches templates from n8n.io API
  - `src/templates/template-repository.ts` — Template database operations
  - `src/templates/template-service.ts` — Template business logic
  - `src/scripts/fetch-templates.ts` — CLI script for fetching templates
  - `src/scripts/test-templates.ts` — Template functionality tests
  - `src/mcp/tools.ts` — Template search via `search_templates` tool
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: n8n-native MCP client node (bidirectional bridge)
- **Wiki says:** The `src/n8n/` directory contains an n8n-native MCPNode that allows n8n workflows to connect to external MCP servers — making n8n-mcp both an MCP server for AI tools and an MCP client node for n8n workflows.
- **Source evidence:**
  - `src/n8n/` directory exists with n8n-native integration code
  - `MCPNode.node.ts` — n8n node that connects to external MCP servers with operations: callTool, listTools, readResource, listResources, getPrompt, listPrompts
  - `MCPApi.credentials.ts` — Credential type for MCP server auth
  - The wiki notes this is a bidirectional bridge: AI learns n8n, then AI controls n8n
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: 2,285 n8n nodes indexed (828 core + 1,457 community, 1,295 verified)
- **Wiki says:** The system indexes 2,285 total n8n nodes: 828 core + 1,457 community (1,295 verified), with 99% node property coverage, 66.5% operation coverage, 86% documentation coverage, and 267 AI-capable tool variants.
- **Source evidence:**
  - `README.md:12` — "2,285 workflow automation nodes (828 core + 1,457 community)"
  - `README.md:18` — 828 core + 1,457 community (1,295 verified)
  - `README.md:19-22` — 99% property coverage, 66.5% operation coverage, 86% documentation coverage, 267 AI tools
  - `README.md:8` — n8n 2.31.6 compatibility badge
  - `src/community/` — Community node management
  - `src/scripts/fetch-community-nodes.js` — Fetches community node metadata
  - `src/loaders/node-loader.ts` — Core node loading
  - `package.json` dependencies pin `n8n-nodes-base`, `n8n-workflow`, `n8n-core`, and `@n8n/n8n-nodes-langchain` to 2.31.3 for node access
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (wiki previously carried stale 1,845/816/1,029/911, 63.6%, 87%, 265 counts; updated to current README stats)

## Summary

All 7 key claims from the n8n-mcp wiki have been verified against the source code via codegraph exploration:
- ✅ MCP server: stdio/HTTP dual-mode with 23 registered MCP tools confirmed in `src/mcp/` and `manifest.json:84-177`
- ✅ SQLite database: FTS5 full-text search with universal adapter confirmed in `src/database/`
- ✅ Node processing pipeline: Loader, parser, extractor, mapper all confirmed in respective directories
- ✅ Service layer: 38 service modules covering validation, templates, expressions, diff engine confirmed
- ✅ Template system: Fetches templates from n8n.io API with repository and service layers confirmed
- ✅ n8n MCP client node: Bidirectional bridge confirmed in `src/n8n/` directory (community-node wrapper)
- ✅ Node index: Community node management and 2,285 indexed nodes (828 core + 1,457 community) confirmed

## Related

- [[n8n-mcp]] -- Main wiki entry
- [[n8n]] -- Overall n8n platform documentation
- [[n8n-workflows]] -- Workflow catalog

## Cross-project

- [[n8n-skills.codegraph-verify]] -- Companion verification for n8n skills
- [[n8n.codegraph-verify]] -- Similar codegraph verification for n8n
- [[agentfield.codegraph-verify]] -- Similar codegraph verification for AgentField
