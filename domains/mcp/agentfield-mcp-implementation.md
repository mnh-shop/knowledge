---
name: agentfield-mcp-implementation
tags: [agentfield, ai-llm, cli, mcp, model-context-protocol, monitoring, plugin-sdk, removed-feature]
description: "AgentField MCP (Model Context Protocol) implementation: historical support, removal, and remaining artifacts"
---

# AgentField MCP Integration

**Source:** `sources/agentfield/` (historical: control-plane/internal/mcp/, SDK mcp modules, web client MCP components)

**Status:** MCP support was fully implemented then **removed** in a codebase refactor. Only minimal artifacts remain.

---

## 1. Current State

MCP (Model Context Protocol) was **completely removed** from the AgentField codebase in a systematic cleanup (CHANGELOG: "Refactor: remove all MCP code from codebase (#359)"). The removal encompassed backend, CLI, SDK, and UI layers.

### What Was Removed

| Component | Location | Details |
|-----------|----------|---------|
| MCP Manager | `control-plane/internal/mcp/` | Manager, discovery, protocol client |
| CLI Commands | `control-plane/internal/cli/mcp.go` | `af add --mcp --url <server>` |
| HTTP Handlers | `control-plane/internal/handlers/ui/mcp.go` | `/mcp/health`, `/mcp/status`, etc. |
| Domain Models | `control-plane/internal/core/domain/mcp_health.go` | `MCPServerStatus`, `MCPServerHealth` |
| Server Routes | `server.go` | All MCP route registrations |
| AgentClient Interface | `internal/packages/agent_client.go` | MCP methods removed |
| Health Monitor | Heartbeat status processing | MCP health tracking fields |
| Node Events | Event types | MCP event types |
| Python SDK | `sdk/python/agentfield/` modules | `mcp_manager`, `mcp_client`, `mcp_stdio_bridge`, `agent_mcp`, `dynamic_skills` |
| TypeScript SDK | `sdk/typescript/src/mcp/` | Full MCP client, types, registry |
| Web Client | `web/client/src/mcp/` | Services, components (MCPServerList, MCPServerCard, MCPHealthIndicator, MCPServerControls, MCPToolExplorer, MCPToolTester), hooks, utilities |
| Tests | All SDK MCP test files | `test_mcp_manager.py`, `test_mcp_stdio_bridge.py`, `mcp_client_expanded.test.ts` |

---

## 2. Historical Architecture (Before Removal)

### Control Plane MCP Endpoints

The MCP system exposed these REST endpoints through the UI API:

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/ui/v1/mcp/status` | Overall MCP status across all nodes |
| GET | `/api/ui/v1/nodes/:nodeID/mcp/health` | Node MCP health (user mode) |
| GET | `/api/ui/v1/nodes/:nodeID/mcp/health?mode=developer` | Node MCP health (developer mode, shows servers) |
| POST | `/api/ui/v1/nodes/:nodeID/mcp/servers/:alias/restart` | Restart an MCP server on a node |
| GET | `/api/ui/v1/nodes/:nodeID/mcp/servers/:alias/tools` | List tools from an MCP server |

### CLI Command

```
af add --mcp --url <mcp-server-url>
```

This registered an MCP server endpoint with the AgentField control plane, making its tools discoverable to agents.

### SDK Integration

**Python SDK:**
- `mcp_client` -- MCP protocol client
- `mcp_manager` -- MCP server lifecycle management
- `mcp_stdio_bridge` -- stdio transport for local MCP processes
- `agent_mcp` -- MCP integration in the Agent class
- `dynamic_skills` -- MCP tools surfaced as dynamic AgentField skills
- 143 tests across the MCP modules

**TypeScript SDK:**
- `src/mcp/` -- Full MCP client implementation
- `types/mcp.ts` -- MCP type definitions
- `mcp_client.test.ts` -- 27 tests for health checks, tool listing, tool execution
- `mcp_registry.test.ts` -- 20 tests for client registry, tool registrar, namespace handling

**Web Client UI:**
- Components: `MCPServerList`, `MCPServerCard`, `MCPHealthIndicator`, `MCPServerControls`, `MCPToolExplorer`, `MCPToolTester`
- Tabs: MCP Servers, Tools, Performance tabs on the NodeDetailPage
- Hooks: `useMCPHealthSSE(nodeId)` for SSE-based MCP health monitoring

### Go Backend

- `control-plane/internal/mcp/` directory with manager, discovery, protocol client
- `mcp_health.go` domain models for MCP health state
- MCP-related fields in `AgentStatus`, `heartbeat processing`, `HealthMonitor`, `StatusManager`

---

## 3. Remaining Artifacts

### ARD (Agent Resource Discovery) -- `application/mcp-server+json`

The ARD system retains `application/mcp-server+json` as an `ArtifactType` for catalog entries. MCP servers can still be registered and discovered as **external resources** through the ARD catalog, but AgentField no longer has a first-party MCP client or protocol adapter.

ARD external invocation (`callExternalARD` in `execute.go`) can forward HTTP requests to external bindings, providing a path for limited MCP interaction via the ARD layer without native MCP support.

### MCP Test Scripts (Remnants)

Two test scripts survive in `control-plane/scripts/`:
- `quick-mcp-test.sh` -- Quick smoke tests for MCP endpoints
- `test-mcp-endpoints.sh` -- Comprehensive MCP endpoint test suite (7 tests covering status, health, tools, restart, error cases, SSE events)

These scripts reference endpoints that no longer exist in the current codebase.

### MCP in Docs References

- The TS SDK README mentions "MCP tooling" in its capabilities list
- The Hermes integration section documents "Option A: MCP Bridge (Hermes to AgentField)" as a viable integration pattern
- The feature table still shows "MCP server integration" as a dev experience feature (`af add --mcp --url <server>`)

---

## 4. Reconnecting MCP Today

### Option A: Implement an MCP client as a new provider in the ARD external invocation system

The plumbing exists: `ExternalEntry` has a `URL` field and the `callExternalARD` handler in `execute.go` already forwards HTTP requests to external bindings. An MCP protocol adapter could be written as an ARD provider type.

### Option B: Write an MCP adapter agent

Run a Python MCP client and expose its tools via `@app.reasoner()` or `@app.skill()`. The SDK's `tools="discover"` feature makes them available to LLM calls as tool schemas.

### Option C: Hermes MCP Bridge (for Hermes integrations only)

Write a Hermes MCP server that wraps the AgentField REST API (~100 lines of Python using FastMCP). Expose AgentField's execution endpoints as MCP tools and discovery as MCP resources. This lets Hermes agents call any AgentField reasoner as an MCP tool, but it is a Hermes-side adapter, not AgentField-side MCP support.

## 5. Related

- [[agentfield-api]] -- REST API reference (section 12 documents MCP removal)
- [[agentfield-acp-implementation]] -- Agent communication protocol
