---
name: n8n-mcp
tags: [n8n, mcp, apps, browser]
description: n8n — MCP Integration
---

# n8n — MCP Integration

**Sources:**
- `sources/n8n/packages/@n8n/mcp-apps/` — n8n app MCP server
- `sources/n8n/packages/@n8n/mcp-browser/` — Browser automation MCP server
- `sources/n8n/packages/@n8n/mcp-browser-extension/` — Browser extension companion
- `sources/n8n/packages/@n8n/instance-ai/src/mcp/` — Instance AI MCP client manager
- `sources/n8n/packages/cli/src/modules/mcp/` — Native MCP server running inside n8n CLI

## Overview

n8n has **four MCP surfaces**:

1. **MCP Apps** (`@n8n/mcp-apps`) — Expose n8n app features as an MCP server (apps, components, workflows)
2. **MCP Browser** (`@n8n/mcp-browser`) — Browser automation via CDP relay, Playwright MCP SDK
3. **Instance AI MCP Client** (`@n8n/instance-ai mcp/`) — Connect external MCP servers to the AI agent
4. **Native MCP Server** (`packages/cli/modules/mcp/`) — Expose n8n tools as an MCP server for external MCP clients

## 1. MCP Apps (`@n8n/mcp-apps`)

Exposes n8n app-related functionality as an MCP server.

**Source:** `packages/@n8n/mcp-apps/src/server/`

| Module | Purpose |
|--------|---------|
| `index.ts` | Exports `registerMcpAppTool`, `registerWorkflowPreviewApp`, `injectTelemetryConfig` |
| `register-mcp-app-tool.ts` | Registers individual MCP app tools |
| `apps/workflow-preview.ts` | Workflow preview rendering as MCP app |
| `sdk-version.ts` | MCP SDK version tracking |
| `telemetry-config.ts` | Telemetry injection for MCP commands |
| `resource-loader.ts` | Resource loading for MCP resources |

**Telemetry**: n8n-specific MCP app telemetry via `injectTelemetryConfig()`. Uses RudderStack for analytics with global config singleton.

## 2. MCP Browser (`@n8n/mcp-browser`)

Browser automation MCP server — uses Playwright MCP SDK with CDP relay.

**Source:** `packages/@n8n/mcp-browser/src/`

| Module | Purpose |
|--------|---------|
| `server.ts` | Main MCP server — McpServer (stdio + StreamableHTTP), tool registration, bearer auth |
| `cdp-relay.ts` | WebSocket bridge between MCP server and Chrome extension (near-stateless) |
| `cdp-relay-protocol.ts` | CDP ↔ extension command/event definitions |
| `browser-discovery.ts` | Auto-detect + install Chrome extension |
| `connection.ts` | Browser connection management |
| `server-config.ts` | Server configuration parsing |
| `tools/` | Browser automation tools (~12 tools) |

### Browser Tools

| Tool | Purpose |
|------|---------|
| `browser_navigate` | Navigate to URL |
| `browser_snapshot` | Get page snapshot |
| `browser_click` | Click element |
| `browser_type` | Type text into element |
| `browser_select_option` | Select dropdown option |
| `browser_set_credential` | Fill credential field |
| `browser_screenshot` | Take screenshot |
| `browser_inspect_element` | Inspect element properties |
| `browser_press_key` | Keyboard shortcut |
| `browser_wait` | Wait for condition |
| `browser_tab_management` | Tab management |
| `browser_session` | Session management |

**Architecture**: Server → CDP Relay (WebSocket) → Chrome Extension → Browser. The relay is near-stateless: the extension owns all tab state.

**Security**: Bearer token auth, loopback host validation, sensitivity-aware HTML sanitization via `sensitivity/` and `redaction/` modules.

## 3. Instance AI MCP Client (`@n8n/instance-ai mcp/`)

The AI agent connects to external MCP servers via `McpClientManager`.

**Source:** `packages/@n8n/instance-ai/src/mcp/mcp-client-manager.ts`

**Architecture:**
- `McpClientManager` owns all external MCP connections
- Supports SSE/stdio transport
- Schema sanitization for Anthropic API compatibility:
  - ZodNull → optional fields
  - Discriminated unions → flattened objects
  - Array types → recursive element fix
- Name-checking against reserved domain tool names (prevents shadowing)
- Cached by config hash
- `mcpManager.disconnect()` on service shutdown closes all connections

**Config**: External MCP servers configured via `N8N_INSTANCE_AI_MCP_SERVERS` env var (JSON array of `{name, url/command, transport, toolFilter}`).

**Isolation**: MCP tools are orchestrator-only — not available to sub-agents (security containment).

## 4. Native MCP Server (`packages/cli/modules/mcp/`)

n8n-native MCP server that exposes n8n tools and resources through the Model Context Protocol, running inside the n8n CLI process.

**Source:** `packages/cli/src/modules/mcp/`

| Module | Purpose |
|--------|---------|
| `mcp.module.ts` | Module registration, lifecycle |
| `mcp.service.ts` | Core MCP server logic — exposes n8n tools externally |
| `mcp.controller.ts` | HTTP endpoints for MCP configuration |
| `mcp.config.ts` | MCP server configuration |
| `mcp.types.ts` | TypeScript type definitions |
| `mcp.errors.ts` | MCP error classes |
| `mcp.utils.ts` | MCP utility functions |
| `mcp-api-key.service.ts` | API key authentication for MCP |
| `mcp-server-middleware.service.ts` | Server middleware |
| `mcp.settings.controller.ts` | Settings management |
| `mcp.settings.service.ts` | Settings business logic |
| `mcp-protected-resource.ts` | Protected resource definitions |
| `mcp.typeguards.ts` | TypeScript type guards |
| `tools/` | Tool implementations (what n8n exposes via MCP) |

### Exposed Tools

| Tool | Purpose |
|------|---------|
| `search-workflows.tool.ts` | Search workflows |
| `get-workflow-details.tool.ts` | Get workflow details |
| `publish-workflow.tool.ts` | Publish workflow |
| `unpublish-workflow.tool.ts` | Unpublish workflow |
| `execute-workflow.tool.ts` | Execute workflow |
| `test-workflow.tool.ts` | Test workflow |
| `get-execution.tool.ts` | Get execution details |
| `search-executions.tool.ts` | Search executions |
| `list-credentials.tool.ts` | List credentials |
| `search-projects.tool.ts` | Search projects |
| `search-folders.tool.ts` | Search folders |
| `list-tags.tool.ts` | List tags |
| `data-table/` | Data table operations |
| `workflow-builder/` | Workflow builder tools |
| `schemas.ts` | Tool input/output schemas |

**Workflow builder tools** provide AI-assisted workflow construction using n8n's own tools, enabling external AIs to build workflows via MCP.

## Related

- n8n Architecture: [[n8n-architecture]]
- n8n Instance AI: [[n8n-instance-ai]]
- n8n API: [[n8n-api]]
- n8n Deployment: [[n8n-deployment]] -- Deployment models, Docker images, and scaling
- n8n Agent Profile: [[n8n-agent-profile]] -- Engineering standards and development patterns
- Hermes MCP (for comparison): [[hermes-mcp-implementation]]
- Wiki entry: [[n8n]]
