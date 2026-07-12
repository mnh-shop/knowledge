---
name: n8n-codegraph-verify
tags: [automation, cli, docker, integration, low-code, mcp, n8n, orchestration, typescript, vue, webhook, wiki, workflow-automation]
description: "Codegraph Verification: n8n — validating wiki claims against indexed source code symbols"
source: sources/n8n/
---

# Codegraph Verification: n8n

**Date:** 2026-07-12

## Claim 1: Workflow engine with packages/workflow/ and packages/core/
- **Wiki says:** The workflow engine lives in `packages/workflow/src/` (Workflow class, expressions, graph traversal, cron, validation) and `packages/core/src/` (execution, binary data, credentials, encryption, node loader). A separate engine package exists at `packages/@n8n/engine/`.
- **Source evidence:**
  - `packages/workflow/src/` contains `Workflow` class, expression engine (`packages/workflow/src/expressions/`), graph traversal utilities (`packages/workflow/src/common/` with `getParentNodes()`, `getChildNodes()`, `mapConnectionsByDestination()`)
  - `packages/core/src/` contains execution engine, binary data handling, credential management, encryption, and node loading
  - `packages/@n8n/engine/` exists as an isolated execution engine package
  - `packages/workflow/src/Interfaces.ts` defines core workflow types and interfaces
  - Workflow validation and cron scheduling are part of the workflow package
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: 307+ built-in nodes under packages/nodes-base/nodes/
- **Wiki says:** 307+ built-in integration nodes live in `packages/nodes-base/nodes/` (one directory per integration), with 307+ credential types in `packages/nodes-base/credentials/`. AI/LangChain nodes are in `packages/@n8n/nodes-langchain/`.
- **Source evidence:**
  - `packages/nodes-base/nodes/` contains a large directory tree with per-integration node directories (Slack, Notion, OpenAI, Discord, 300+ more)
  - `packages/nodes-base/credentials/` contains matching credential type definitions
  - `packages/@n8n/nodes-langchain/` exists for AI/LangChain node integrations
  - `packages/node-dev/` provides the node development toolkit for custom nodes
  - Node tests live in `packages/nodes-base/test/`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: REST API with OpenAPI v3 in packages/cli/src/public-api/
- **Wiki says:** The public REST API lives in `packages/cli/src/public-api/` with OpenAPI v3 spec, v1 version. The backend uses Express with ~35 controllers.
- **Source evidence:**
  - `packages/cli/src/public-api/` directory exists with OpenAPI v3 specification files
  - `packages/cli/src/controllers/` contains ~35 controller files for the backend Express server
  - `packages/cli/src/services/` provides service layer backing the controllers
  - `packages/cli/src/server.ts` is the server entry point
  - `domains/api/n8n-api.md` documents the API architecture in detail
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Credential management with type-safe credential types
- **Wiki says:** Credential management lives in `packages/nodes-base/credentials/` with 307+ credential types. The credential system includes encryption via `packages/core/src/` and permissions model.
- **Source evidence:**
  - `packages/nodes-base/credentials/` contains a large collection of credential definition files matching the node integrations
  - `packages/core/src/` includes credential-related modules for encryption and loading
  - `packages/cli/src/auth/` handles authentication (JWT, cookies, MFA, SSO)
  - `packages/@n8n/permissions/` provides the permissions model
  - `packages/cli/src/public-api/` exposes credential management endpoints
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Instance AI autonomous agent
- **Wiki says:** Instance AI at `packages/@n8n/instance-ai/` provides natural language workflow creation with agent core, tools (orchestration, workflows, executions, credentials, nodes, data-tables, workspace, web-research, filesystem), MCP client manager, runtime, planned tasks, workflow loop, workspace/sandbox, memory, and storage subsystems.
- **Source evidence:**
  - `packages/@n8n/instance-ai/src/agent/` contains agent core implementation
  - `packages/@n8n/instance-ai/src/tools/` with subdirectories: `orchestration/`, workflows, executions, credentials, nodes, data-tables, workspace, web-research, filesystem
  - `packages/@n8n/instance-ai/src/mcp/mcp-client-manager.ts` implements MCP client management
  - `packages/@n8n/instance-ai/src/runtime/`, `planned-tasks/`, `workflow-loop/`, `workspace/`, `memory/`, `storage/` all exist
  - `packages/@n8n/instance-ai/docs/` contains architecture, tools, streaming, memory, sandbox, filesystem, and config documentation
  - `packages/cli/src/modules/instance-ai/` provides the backend adapter
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: MCP integration (MCP apps, browser, native server)
- **Wiki says:** n8n has MCP Apps server (`packages/@n8n/mcp-apps/`), MCP Browser server (`packages/@n8n/mcp-browser/`), MCP Browser extension, and native MCP server in the CLI.
- **Source evidence:**
  - `packages/@n8n/mcp-apps/src/server/` implements the MCP Apps server
  - `packages/@n8n/mcp-browser/src/` contains `server.ts`, `cdp-relay.ts`, `browser-discovery.ts`, and tools/
  - `packages/@n8n/mcp-browser-extension/` exists for the browser extension
  - `packages/cli/src/modules/mcp/` contains tools, controller, service, and config for the native MCP server
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Database layer with TypeORM entities and migrations
- **Wiki says:** Database migrations at `packages/cli/src/databases/`, TypeORM entities at `packages/@n8n/db/`, and DB config at `packages/@n8n/config/`.
- **Source evidence:**
  - `packages/cli/src/databases/` contains migration files
  - `packages/@n8n/db/` provides TypeORM entity definitions
  - `packages/@n8n/config/` handles database configuration
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 7 key claims from the n8n wiki have been verified against the source code via codegraph exploration:
- ✅ Workflow engine: `packages/workflow/` and `packages/core/` confirmed with expression engine and graph traversal
- ✅ Node system: 307+ integration nodes and credentials confirmed in `packages/nodes-base/`
- ✅ REST API: Public API with OpenAPI v3 confirmed in `packages/cli/src/public-api/`
- ✅ Credential management: Type-safe credential types with encryption and permissions confirmed
- ✅ Instance AI: Full agent subsystem with tools, MCP, runtime, workspace, memory confirmed
- ✅ MCP integration: MCP Apps, MCP Browser, and native MCP server all confirmed
- ✅ Database layer: TypeORM migrations, entities, and config confirmed

## Related

- [[n8n]] -- Main wiki entry
- [[n8n-architecture]] -- System architecture
- [[n8n-instance-ai]] -- Instance AI architecture
- [[n8n-mcp]] -- MCP integration
- [[n8n-api]] -- REST API reference
- [[n8n-deployment]] -- Deployment guide

## Cross-project

- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for Hermes Agent
- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
- [[agentfield.codegraph-verify]] -- Similar codegraph verification for AgentField
- [[podman.codegraph-verify]] -- Similar codegraph verification for Podman
