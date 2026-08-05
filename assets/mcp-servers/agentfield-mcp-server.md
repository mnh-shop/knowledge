---
name: agentfield-mcp-server
tags: [agentfield, cli, control-plane, golang, harness, identity, mcp, orchestration, plugin-sdk, quadlet, security, systemd]
description: Embedded MCP server reference for AgentField — POST /mcp, the 5 MCP tools, feature flag, DID auth, and client wiring for Claude Code, Hermes, and OpenClaw
---

# AgentField MCP Server
**Source:** `sources/agentfield/` (v0.1.118-rc.3)

**Type:** MCP server asset (embedded AgentField control-plane MCP server)  
**Status:** Reference  
**Rationale:** The AgentField control plane ships a built-in Model Context Protocol server at `POST /mcp`, on by default. No bridge, wrapper process, or extra service is needed — any MCP-capable harness connects straight to the control plane URL.

---

## Context

AgentField exposes an embedded MCP server directly on the control plane (`control-plane/internal/server/routes_mcp.go`, `internal/handlers/mcp.go`). Any harness that speaks MCP — Claude Code, Hermes, OpenClaw, Cursor, etc. — can discover and drive the agents already running on a control plane with **zero extra processes and zero setup**.

History: AgentField's original MCP implementation was removed in PR #359, but the embedded server was **re-added in PR #817** and ships enabled by default. The `application/mcp-server+json` type also remains in the ARD catalog (see below).

### Endpoint & Transport

| Property | Value |
|----------|-------|
| Endpoint | `POST <server>/mcp` (default `http://localhost:8080/mcp`) |
| Transport | Streamable HTTP, JSON-RPC 2.0 over a single POST |
| State | Stateless — no session negotiation; `Mcp-Session-Id` and `MCP-Protocol-Version` request headers are tolerated and ignored |
| GET `/mcp` | 405 with `Allow: POST, OPTIONS` (not a valid transport verb) |
| OPTIONS `/mcp` | Preflight/probe answered with 204 |
| Protocol versions | `2025-06-18` (default), `2025-03-26`, `2024-11-05` |
| Server info | `initialize` returns `serverInfo { name: "agentfield", version: <build version> }` |
| Batches | Unsupported — a single JSON-RPC message per POST (arrays rejected) |

---

## Tools

The `tools/list` catalog exposes five tools; `tools/call` dispatches `discover_agents`, `get_reasoner_schema`, `execute_reasoner`, `get_run`, `wait_run` (`mcpToolCatalog` in `internal/handlers/mcp.go`).

| Tool | Arguments | Returns |
|---|---|---|
| `discover_agents` | `health?`: `"active"` (default) or `"all"` | Agents with `id`, `health_status`, `last_heartbeat`, and their `reasoners` (`id`, `description`, entrypoint `tags`, `target`). `"active"` lists only healthy agents; `"all"` includes unhealthy ones. |
| `get_reasoner_schema` | `node`, `reasoner` | The reasoner's input/output JSON Schema, description, and tags, exactly as the discovery surface serves them. |
| `execute_reasoner` | `target` (`"node.reasoner"`), `input` (object) | Validates the target exists (a clear error naming `discover_agents` if not), starts an **asynchronous** execution, and returns `{ run_id, status: "accepted" }`. |
| `get_run` | `run_id` | Current run `status`, `result`/`error`, and per-execution summaries (`reasoner_id`, `node_id`, `status`). |
| `wait_run` | `run_id`, `timeout_seconds?` (default 60, max 120) | Server-side poll until the run is terminal or the timeout elapses. Same shape as `get_run` plus a `timed_out` flag. The timeout is hard-capped so a single tool call can never hang the harness. |

Tool results are returned as a single MCP text content block containing compact JSON — the shape harnesses parse most reliably. Validation and business failures (unknown target, unknown run) come back as MCP tool errors (`isError: true`) rather than transport errors, so the model sees and can react to them.

### Example flow

1. `discover_agents` → find `swe-planner` and its `build` reasoner.
2. `get_reasoner_schema` `{ node: "swe-planner", reasoner: "build" }` → learn the input shape.
3. `execute_reasoner` `{ target: "swe-planner.build", input: { goal: "Add JWT auth" } }` → `{ run_id: "run_…", status: "accepted" }`.
4. `wait_run` `{ run_id: "run_…", timeout_seconds: 120 }` → block until the run finishes (or `timed_out: true`), then read `result`.

---

## Enabling / Disabling

Enabled by default (`MCPConfig.IsEnabled()` returns true when the flag is unset). Disable via config or environment:

```yaml
# control-plane/config/agentfield.yaml
features:
  mcp:
    enabled: false      # default: true (nil => enabled)
```

```bash
AGENTFIELD_MCP_ENABLED=false   # equivalent env override
```

When disabled, `registerMCPRoutes` does not register the route and `/mcp` returns 404.

---

## Auth and DID Interplay

The MCP endpoint binds wherever the control plane binds and lives in the **same trust domain as the REST API**: it starts async executions and reads run state through the same service layer, subject to the same global API-key auth. If the control plane has an API key set (`AGENTFIELD_API_KEY`), `/mcp` requires it just like `/api/v1` — pass it as an `X-API-Key: <key>` header in the client's MCP configuration.

When DID authorization is enabled (`features.did.authorization.enabled`), MCP execution is authorized exactly like REST execution: `mcpAuthorizer` (in `routes_mcp.go`) feeds the MCP target and input through the shared target-aware permission middleware by synthesizing the REST request shape — it never trusts client-supplied identity headers. A verified caller DID becomes the authoritative run owner: it is forwarded to the target agent as the actor, and `get_run`/`wait_run` scope results to runs the caller owns (runs without a matching owner are indistinguishable from missing).

**Do not** expose the control plane's port to an untrusted network expecting `/mcp` to be more restricted than `/api/v1`; it is not. Set `AGENTFIELD_MCP_ENABLED=false` to remove the endpoint entirely.

---

## Client Wiring

### Claude Code

```bash
claude mcp add --transport http agentfield http://localhost:8080/mcp
```

If `AGENTFIELD_API_KEY` is set, add the header to the client's MCP config:

```json
{
  "mcpServers": {
    "agentfield": {
      "url": "http://localhost:8080/mcp",
      "headers": { "X-API-Key": "your-api-key" }
    }
  }
}
```

### Hermes Integration via MCP

Hermes's MCP client supports HTTP/streamable-http via `url`. Add an `mcp_servers` entry to `~/.hermes/config.yaml` pointing at the control plane's `/mcp` endpoint:

```yaml
mcp_servers:
  agentfield:
    url: "http://agentfield:8080/mcp"
    headers:
      X-API-Key: "your-api-key"     # only if AGENTFIELD_API_KEY is set
    timeout: 180
```

Hermes then discovers AgentField's five tools and registers them into its tool registry, so Hermes agents can call any reasoner on the control plane as an MCP tool — with full tracing through the control plane.

### OpenClaw Integration via MCP

OpenClaw's `openclaw mcp` CLI registers HTTP MCP servers in `mcp.servers` (client-side registry). Point it at the control plane's `/mcp` endpoint with the streamable-http transport:

```bash
openclaw mcp add agentfield --url http://agentfield.openclaw.svc:8080/mcp --transport streamable-http
```

Or register with an API-key header via `openclaw mcp set`:

```json
{
  "url": "http://agentfield.openclaw.svc:8080/mcp",
  "transport": "streamable-http",
  "headers": { "X-API-Key": "your-api-key" }
}
```

OpenClaw's rate limiting, circuit breaking, and API-key handling become an additional layer on top of AgentField's DID identity system.

---

## Beyond MCP

MCP covers the common discover → execute → poll loop. AgentField also exposes:

- **REST API** — `/api/v1` with 10 route groups (~127 endpoints): discovery, execution, memory, knowledge, ARD, DID, connectors, triggers, observability, admin.
- **gRPC** — `AdminReasonerService` on the admin port (control plane port + 100, i.e. 8180 when the control plane is on 8080; `AGENTFIELD_ADMIN_GRPC_PORT` overrides).
- **`af` CLI** — the full-power path: sessions, streaming, cancel-tree, secrets, load-aware pacing.

## ARD-Based MCP Discovery

AgentField's ARD (Agent Resource Discovery) catalog preserves `application/mcp-server+json` as an `ArtifactType`, so external MCP servers can still be registered and discovered as ARD resources alongside the embedded server (e.g. via the Discovery UI's MCP server entry type).

## Related

- [AgentField Architecture](../../domains/architecture/agentfield-architecture.md)
- [AgentField API](../../domains/api/agentfield-api.md) -- REST endpoints, execution flow, integration patterns
- [AgentField Deployment](../../domains/deployment/agentfield-deployment.md) -- local, Docker Compose, Quadlet
- [AgentField Quadlet](../deployment/agentfield-quadlet.md) -- Quadlet-specific deployment

## Related

- [[agentfield]] -- wiki page for the platform
- [[agentfield-architecture]] -- system architecture
- [[agentfield-api]] -- REST API reference
- [[agentfield-deployment]] -- deployment guide
- [[agentfield-quadlet]] -- Quadlet deployment
- [[agentfield-profile]] -- AgentField platform profile
