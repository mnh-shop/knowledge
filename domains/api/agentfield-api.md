---
name: agentfield-api
tags: [agentfield, api, rest, reference]
---

# AgentField API Reference
**Source:** `sources/agentfield/`

**Status:** Active research target  
**Control plane port:** 8080 (configurable via `AGENTFIELD_PORT`)  
**gRPC admin port:** 8180 (HTTP port + 100)  
**Framework:** Gin (Go)  
**Base path:** `/api/v1/`

---

## Table of Contents

1. [REST API Overview](#1-rest-api-overview)
2. [Execution Endpoints](#2-execution-endpoints)
3. [Approval Endpoints](#3-approval-endpoints)
4. [Node Lifecycle Endpoints](#4-node-lifecycle-endpoints)
5. [Discovery Endpoints](#5-discovery-endpoints)
6. [Memory Endpoints](#6-memory-endpoints)
7. [Identity (DID/VC) Endpoints](#7-identity-didvc-endpoints)
8. [Observability Endpoints](#8-observability-endpoints)
9. [Agentic API](#9-agentic-api)
10. [Trigger/Webhook Endpoints](#10-triggerwebhook-endpoints)
11. [HTTP Context Propagation Headers](#11-http-context-propagation-headers)
12. [MCP Integration](#12-mcp-integration)
13. [Harness Runtimes](#13-harness-runtimes)
14. [The /agentfield CLI Command](#14-the-agentfield-cli-command)
15. [Integration Patterns](#15-integration-patterns)

---

## 1. REST API Overview

AgentField exposes a REST API organized across specialized `routes_*.go` files in `control-plane/internal/server/`. Routes are composed in `server.go:setupRoutes()` and registered under the `agentAPI` Gin group at `/api/v1/`.

### Route Registration Order

```go
func (s *AgentFieldServer) setupRoutes() {
    s.registerPublicRoutes()      // /metrics, /health (no auth)
    s.registerDIDWellKnownRoutes() // /.well-known/did.json, /agents/:agentID/did.json
    s.registerARDPublicRoutes()    // /.well-known/ai-catalog.json
    s.registerUIStatic()           // /ui/ SPA serving
    s.registerUIAPI()              // /api/ui/v1, /api/ui/v2 (browser APIs)
    // Then under /api/v1 with authentication:
    s.registerCoreRoutes(agentAPI)       // execution, nodes, discovery, lifecycle
    s.registerMemoryRoutes(agentAPI)     // KV + vector memory
    s.registerKnowledgeRoutes(agentAPI)  // RAG knowledge store
    s.registerDIDRoutes(agentAPI)        // DID/VC, policies, revocations
    s.registerObservabilityRoutes(agentAPI) // observability webhook settings
    s.registerAdminRoutes(agentAPI)      // tag approval, policy management
    s.registerConnectorRoutes(agentAPI)  // connector API (capability-gated)
    s.registerAgenticRoutes(agentAPI)    // /agentic/* discovery, query, batch
    s.registerTriggerRoutes(agentAPI)    // trigger CRUD + public ingest
    s.registerARDRoutes(agentAPI)        // ARD registry search/explore
    s.registerKBRoutes()                 // /api/v1/agentic/kb (public, no auth)
    s.register404()                      // Smart 404 + SPA fallback
}
```

### Route Source Files

| Route Group | File |
|-------------|------|
| Public & core execution | `routes_core.go` |
| Node lifecycle | `routes_core.go` |
| Discovery | `routes_core.go` |
| Memory | `routes_memory.go` |
| Knowledge (RAG) | `routes_knowledge.go` |
| DID/VC | `routes_did.go` |
| Admin (tags, policies) | `routes_admin.go` |
| Connector (fleet management) | `routes_connector.go` |
| Agentic (machine-friendly) | `routes_agentic.go` |
| Triggers/webhooks | `routes_triggers.go` |
| Sessions | `routes_core.go` |
| UI API | `routes_ui.go` |
| Observability settings | `routes_observability.go` |
| ARD (Agent Resource Discovery) | `routes_ard.go` |
| Knowledge Base | `routes_agentic.go` |

### Authentication Model (Layered)

AgentField uses five authentication layers applied in order:

1. **API Key** (header `Authorization: Bearer <key>` or query param `api_key`): Required for all API calls unless `api.auth.insecure_disable_auth` is set. Config: `AGENTFIELD_API_AUTH_API_KEY`.

2. **DID Signatures** (cross-agent calls): Every cross-agent call carries DID auth headers:
   - `X-Caller-DID` -- The caller's W3C DID
   - `X-DID-Signature` -- Ed25519 signature over `{timestamp}:{SHA256(body)}`
   - `X-DID-Timestamp` -- Signing timestamp (300s window via `timestamp_window_seconds`)
   - `X-DID-Nonce` -- Optional replay protection nonce (deduped in memory cache within window)

3. **Admin Token** (`AGENTFIELD_AUTHORIZATION_ADMIN_TOKEN`): Required for tag approval and policy management endpoints when authorization is enabled. Gated via `middleware.AdminTokenAuth()`.

4. **Internal Token** (`AGENTFIELD_AUTHORIZATION_INTERNAL_TOKEN`): Sent as `Authorization: Bearer <token>` when the control plane forwards execution requests to agents. Agents with `RequireOriginAuth` enabled validate this in their `originAuthMiddleware()`, preventing direct HTTP access to agent ports.

5. **Connector Token** (`features.connector.token`): Authenticates external connector integrations. Gated via `middleware.ConnectorTokenAuth()`.

### Permission Middleware (Tag-Based IAM)

When DID authorization is enabled (`features.did.authorization.enabled: true`), the permission middleware `middleware.PermissionCheckMiddleware()` is applied to:
- Execute endpoints: `POST /api/v1/execute/:target` and `POST /api/v1/execute/async/:target`
- Legacy reasoner endpoints: `POST /api/v1/reasoners/:reasoner_id`
- Legacy skill endpoints: `POST /api/v1/skills/:skill_id`
- Session target endpoints: `POST /api/v1/session-targets/:target/start`

Memory endpoint authorization uses a separate `middleware.MemoryPermissionMiddleware()` with scope ownership enforcement.

The middleware evaluates first-match-wins access policies with function-level allow/deny lists and parameter constraints. Default deny mode (`default_deny: true`) returns 403 for unmatched requests.

### DID Auth Error Responses

| HTTP | Error Code | Condition |
|------|-----------|-----------|
| 401 | `did_auth_required` | No `X-Caller-DID` header provided |
| 401 | `signature_required` | `X-Caller-DID` present but no `X-DID-Signature` |
| 401 | `signature_invalid` | Ed25519 signature verification failed |
| 403 | `did_revoked` | Caller's DID is on the revocation list |
| 403 | `did_not_registered` | DID not found in the control plane's registration set |
| 403 | `policy_denied` | No matching policy or denied by tag policy |

---

## 2. Execution Endpoints

### Synchronous Execution

```
POST /api/v1/execute/:target
```
- `target` format: `agent_id.reasoner_name`
- Body: `{"input": {...}}`
- Returns the reasoner's output as JSON
- Blocks until execution completes
- Timeout: 180s (configurable)

### Async Execution

```
POST /api/v1/execute/async/:target
```
- Same target format as sync
- Returns immediately with `execution_id`
- Response: `{"execution_id": "uuid", "status": "queued"}`
- Long-running agents supply `webhook: {url: "https://..."}` for callback

### Execution Status

```
GET /api/v1/executions/:execution_id
```
- Returns status and result (if completed)
- Status values: `queued`, `running`, `completed`, `failed`, `paused`, `cancelled`

```
POST /api/v1/executions/batch-status
```
- Body: `{"execution_ids": ["id1", "id2", ...]}`

### Execution Lifecycle

| Endpoint | Action |
|----------|--------|
| `POST /api/v1/executions/:execution_id/status` | Status callback (agent to control plane) |
| `POST /api/v1/executions/:execution_id/cancel` | Cancel a running execution |
| `POST /api/v1/executions/:execution_id/pause` | Pause for human approval |
| `POST /api/v1/executions/:execution_id/resume` | Resume after human approval |
| `POST /api/v1/executions/:execution_id/restart` | Restart an execution |
| `POST /api/v1/executions/:execution_id/events` | SSE stream of execution events |
| `POST /api/v1/executions/:execution_id/logs` | Structured execution logs |

### Workflow Tree Operations

```
POST /api/v1/workflows/:workflowId/cancel-tree
```
- Cancels an entire workflow tree (multi-hop DAG)

---

## 3. Approval Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/executions/:execution_id/request-approval` | Request human approval |
| `GET /api/v1/executions/:execution_id/approval-status` | Poll approval status |
| `POST /api/v1/agents/:node_id/executions/:execution_id/request-approval` | Agent-scoped approval request |
| `POST /api/v1/agents/:node_id/executions/:execution_id/awaiter-status` | Multi-hop pause propagation |
| `POST /api/v1/webhooks/approval-response` | Approval resolution webhook (agent or external service callback) |

The approval flow enables human-in-the-loop patterns:
1. Agent calls `app.pause("Explain reasoning before proceeding")`
2. Control plane marks execution as `paused`
3. External system or human reviews via `/request-approval` or `/approval-status`
4. Resolution posted to `/approval-response` webhook
5. Control plane resumes the execution

---

## 4. Node Lifecycle Endpoints

### Registration

```
POST /api/v1/nodes/register
```
- Body: agent metadata, callback URL, capabilities, tags, DID keys
- Returns: node_id, identity package

```
POST /api/v1/nodes/register-serverless
```
- Registration without persistent HTTP listener (for FaaS/serverless agents)

### Heartbeat and Status

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/nodes` | List all registered agents |
| `GET /api/v1/nodes/:node_id` | Get agent details |
| `POST /api/v1/nodes/:node_id/heartbeat` | Agent heartbeat |
| `POST /api/v1/nodes/:node_id/start\|stop\|shutdown` | Lifecycle management |
| `POST /api/v1/nodes/:node_id/lifecycle/status` | Update lifecycle status |
| `POST /api/v1/nodes/:node_id/status` | Update status lease |
| `POST /api/v1/nodes/status/bulk` | Bulk status update |
| `POST /api/v1/actions/claim` | Claim pending lifecycle actions |

---

## 5. Discovery Endpoints

```
GET /api/v1/discovery/capabilities
```
- Query parameters: `tag` (filter by tag), `name` (filter by name), `health` (filter by health status)
- Returns list of `AgentCapability` and `ReasonerCapability` objects
- Used by SDK's `app.discover()` method

```
GET /api/v1/reasoners
```
- List all registered reasoners across all agents

---

## 6. Memory Endpoints

Memory is organized in 4 scopes: `global`, `session`, `actor`, `workflow`.

```
POST /api/v1/executions/note
```
- Add an execution audit note

KV store operations and vector search (cosine distance) are available per scope.

Memory event subscriptions enable reactive patterns via `@app.on_change()` in the Python SDK.

---

## 7. Identity (DID/VC) Endpoints

The DID system produces a three-tier key hierarchy: Platform DID (control plane itself) -> Node DID (per registered agent) -> Function DID (per reasoner/skill). DID methods supported: `did:web` (primary, with did:web resolution URL endpoints) and `did:key` (fallback, self-contained but non-revocable).

### DID Registration

```
POST /api/v1/did/register
```
- Body: `{"agent_id": "my-agent", "public_key_jwk": { ... }}`
- Returns: `DIDIdentityPackage` with per-component keys
- Keys generated with Ed25519 + BIP32 derivation (AES-256-GCM encrypted keystore)
- Auto-registers DID document at Web resolution URLs
- Optionally generates Verifiable Credentials for agent tags

### DID Resolution

```
GET /.well-known/did.json
```
- Standard `did:web` resolution endpoint (spec: `did:web:{domain} -> GET /.well-known/did.json`)
- Serves DID documents with public keys in JWK format

```
GET /agents/:agentID/did.json
```
- Per-agent `did:web` resolution (spec: `did:web:{domain}:agents:{agentID} -> GET /agents/{agentID}/did.json`)

```
GET /api/v1/did/resolve/:did
```
- Resolve any DID known to the control plane
- Returns full DID document with verification methods

### Complete DID Endpoint Surface

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/did/register` | Register agent DID identity package |
| GET | `/api/v1/did/resolve/:did` | Resolve DID document |
| POST | `/api/v1/did/key-agreement/rotate` | Rotate X25519 key agreement key |
| POST | `/api/v1/did/verify` | Verify a Verifiable Credential |
| POST | `/api/v1/did/verify-audit` | Verify an audit bundle (VC chain) |
| GET | `/api/v1/did/workflow/:workflow_id/vc-chain` | Get VC chain for a workflow |
| POST | `/api/v1/did/workflow/:workflow_id/vc` | Create VC for a workflow |
| GET | `/api/v1/did/status` | DID system status |
| GET | `/api/v1/did/export/vcs` | Export all stored VCs |
| GET | `/api/v1/did/document/:did` | Get DID document |
| GET | `/api/v1/did/agentfield-server` | Get AgentField server's own DID |
| GET | `/api/v1/did/issuer-public-key` | Get control plane issuer public key (JWK) |
| POST | `/api/v1/execution/vc` | Create VC for an execution |

### Policy Distribution Endpoints (For Local Verification)

These are consumed by agent SDKs for offline DID verification:

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/policies` | List all access policies (agents cache these) |
| GET | `/api/v1/revocations` | List all revoked DIDs |
| GET | `/api/v1/registered-dids` | List all active registered DIDs |
| GET | `/api/v1/admin/public-key` | Legacy alias for issuer public key |
| GET | `/api/v1/agents/:node_id/tag-vc` | Get agent's verified tag VC |

Agents refresh these on a 5-minute cycle using `localVerifier.NeedsRefresh()` in the Go SDK.

### W3C DID Document Structure

```json
{
  "@context": [
    "https://www.w3.org/ns/did/v1",
    "https://w3id.org/security/suites/ed25519-2020/v1"
  ],
  "id": "did:key:z6Mk...",
  "verificationMethod": [{
    "id": "did:key:z6Mk...#key-1",
    "type": "Ed25519VerificationKey2020",
    "controller": "did:key:z6Mk...",
    "publicKeyJwk": { ... }
  }],
  "authentication": ["did:key:z6Mk...#key-1"],
  "assertionMethod": ["did:key:z6Mk...#key-1"]
}
```

---

## 8. Observability Endpoints

```
GET /metrics
```
- Prometheus metrics via `github.com/prometheus/client_golang`

```
GET /health
```
- Combined storage + cache health check
- Returns 200 when control plane is operational

```
GET /api/v1/workflows/:id/dag
```
- Workflow DAG visualization data
- Used by the web UI for execution trace visualization

---

## 9. Agentic API

Machine-friendly endpoints for external tools and automated clients:

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/agentic/status` | System status |
| `GET /api/v1/agentic/discover` | Endpoint catalog search |
| `POST /api/v1/agentic/query` | Unified resource query |
| `GET /api/v1/agentic/run/:run_id` | Run overview |
| `GET /api/v1/agentic/agent/:agent_id/summary` | Agent summary |
| `/api/v1/agentic/kb/` | Knowledge base search and management |
| `POST /api/v1/agentic/batch` | Batch API operations |

The Agentic API is designed for machine consumers (other agents, automation tools, CI/CD pipelines) that need a simplified, self-describing interface to AgentField.

---

## 10. Trigger/Webhook Endpoints

- Trigger registration and dispatch (source-based: GitHub, Slack, Linear, Sentry, Snowflake, Stripe, cron, generic HMAC/bearer)
- SSE streaming for live trigger events
- Execution webhooks with HMAC-SHA256 signing
- `webhook_timeout`: 10s per attempt, `webhook_max_attempts`: 3 retries

---

## 11. HTTP Context Propagation Headers

These headers are passed through the cross-agent mesh for traceability:

| Header | Purpose |
|--------|---------|
| `X-Run-ID` | Workflow run tracking |
| `X-Workflow-ID` | Workflow DAG identification |
| `X-Execution-ID` | Specific execution trace ID |
| `X-Parent-Execution-ID` | Parent-child call tree linkage |
| `X-Session-ID` | Multi-turn session tracking |
| `X-Actor-ID` | Actor identity |
| `X-Caller-DID` | DID of the calling agent |
| `X-Target-DID` | DID of the target agent |
| `X-Routed-Version` | Version traffic routing |
| `X-AgentField-Replay-*` | Execution replay headers |

---

## 11.5 HTTP Status Codes and Error Responses

All errors follow a consistent JSON envelope:

```json
{
  "error": "error_code",
  "message": "Human-readable description"
}
```

| Code | Meaning | Common Scenarios |
|------|---------|-----------------|
| 200 | Success | GET, POST (sync execution), status queries |
| 201 | Created | POST register, POST create policy, POST create trigger |
| 202 | Accepted | Async execution queued, heartbeat accepted |
| 400 | Bad Request | Invalid JSON, missing required fields, validation error |
| 401 | Unauthorized | Missing or invalid API key, DID signature failure |
| 403 | Forbidden | DID revoked, policy denied, tag forbidden, access control violation |
| 404 | Not Found | Agent, execution, policy, or trigger not found |
| 409 | Conflict | Duplicate registration or trigger name |
| 410 | Gone | Tag VC revoked |
| 422 | Unprocessable | Input validation error (invalid type, missing field per `_HandlerInputError`) |
| 499 | Cancelled | Execution cancelled by control plane |
| 500 | Internal Error | Storage failure, unexpected error in service |
| 503 | Service Unavailable | Health monitor not available, pending approval, status manager not ready |

## 11.6 Pagination and Filtering

List endpoints support these patterns:

**Offset-limit pagination:**
```
GET /api/v1/nodes?offset=0&limit=20
```

Response envelope:
```json
{
  "results": [...],
  "total": 100,
  "offset": 0,
  "limit": 20
}
```

**Query parameter filtering:**
- `tags=<glob>` -- Filter by tag glob patterns (e.g., `tags=nlp*`, `tags=production,ml`)
- `health=<status>` -- Filter by health status (`ready`, `degraded`, `offline`, `starting`, `active`)
- `team_id=<id>` -- Filter by team ID
- `group_id=<id>` -- Filter by agent group
- `name=<name>` -- Filter by name
- `mode=<mode>` -- Filter by app mode (`user`, `admin`, `developer`)
- `status=<status>` -- Filter by lifecycle status

**Bulk operations:**
```http
POST /api/v1/executions/batch-status
Content-Type: application/json

{"execution_ids": ["id1", "id2", "id3"]}
```

## 11.7 HTTP Context Propagation Headers

These headers are passed through the cross-agent mesh for traceability:

| Header | Purpose |
|--------|---------|
| `X-Run-ID` | Workflow run tracking |
| `X-Workflow-ID` | Workflow DAG identification |
| `X-Execution-ID` | Specific execution trace ID |
| `X-Parent-Execution-ID` | Parent-child call tree linkage |
| `X-Session-ID` | Multi-turn session tracking |
| `X-Actor-ID` | Actor identity |
| `X-Caller-DID` | DID of the calling agent |
| `X-Target-DID` | DID of the target agent |
| `X-Routed-Version` | Version traffic routing |
| `X-Caller-Agent-ID` | Agent node ID for memory access control |
| `X-Agent-Roles` | Agent roles for access control evaluation |
| `X-Team-ID` | Team ID for team-restricted memory access |
| `X-AgentField-Replay-*` | Execution replay headers |

## 11.8 SDK-Generated API Surface

The Python SDK's `Agent` class (subclass of `FastAPI`) auto-generates REST endpoints from decorators:

| Decorator | Generated Endpoint | Method | Purpose |
|-----------|-------------------|--------|---------|
| `@app.reasoner()` | `/reasoners/{id}` | POST | AI reasoning with LLM, auto-extracts type hints |
| `@app.skill()` | `/skill/{id}` | POST | Deterministic logic |
| `@app.session()` | `/session/{id}` | POST | Multi-turn conversation session |

The SDK creates FastAPI routes at decoration time; each reasoner endpoint:
1. Parses JSON body
2. Validates input against function parameter type hints (no Pydantic model -- saves ~1.5-2 KB per handler)
3. Wraps execution in workflow tracking (`tracked_func` with weakref-based GC)
4. Supports sync (blocking) and async (`X-Execution-ID` triggers async path) modes

The registered reasoner/skill is also callable via the control plane's unified execute endpoint:
```
POST /api/v1/execute/{agent_id}.{reasoner_id}
```

The Go SDK uses `http.ServeMux` internally with its own route set:
```
GET  /health                  -- Agent health check
GET  /discover                 -- Capability discovery
POST /execute                 -- Execute any reasoner
POST /execute/{name}          -- Execute named reasoner
GET  /reasoners/{id}          -- Get reasoner metadata
POST /reasoners/{id}          -- Execute specific reasoner
POST /_internal/executions/{id}/cancel  -- Cancel execution (control-plane only)
POST /agentfield/v1/logs      -- Send NDJSON process logs to control plane
```

The Go SDK also supports a router API (`sdk/go/agent/router.go`) with `IncludeRouter()` for nesting sub-routers and `RegisterReasoner`/`RegisterSkill` for registering handlers at specific paths, enabling complex agent architectures.

## 12. MCP Integration

**Current status:** AgentField had a full MCP (Model Context Protocol) implementation that was **completely removed** in a refactor (CHANGELOG entry: "Refactor: remove all MCP code from codebase (#359)").

### What was removed:
- `control-plane/internal/mcp/` -- manager, discovery, protocol client
- `control-plane/internal/cli/mcp.go` -- CLI commands (including `af add --mcp --url <server>`)
- `control-plane/internal/handlers/ui/mcp.go` -- HTTP handlers for `/mcp/health`, `/mcp/status`
- `control-plane/internal/core/domain/mcp_health.go` -- domain models
- All MCP routes from `server.go`
- MCP methods from the `AgentClient` interface
- MCP types from TypeScript SDK

### Only remaining artifact:
In the ARD (Agent Resource Discovery) system, `application/mcp-server+json` persists as an `ArtifactType` for catalog entries. MCP servers can still be registered and discovered as external resources through the ARD catalog, but AgentField no longer has a first-party MCP client or protocol adapter.

### Reconnecting MCP today:

**Option A: Implement an MCP client as a new provider in the ARD external invocation system**
- The plumbing exists: `ExternalEntry` has a `URL` field and the `callExternalARD` handler in `execute.go` already forwards HTTP requests to external bindings

**Option B: Write an MCP adapter agent**
- Run a Python MCP client and expose its tools via `@app.reasoner()` or `@app.skill()`
- The SDK's `tools="discover"` feature makes them available to LLM calls

---

## 13. Harness Runtimes

The Harness feature (`app.harness(prompt, provider=...)`) treats LLM CLI tools as autonomous computational units.

### Provider Factory

```
SUPPORTED_PROVIDERS = {"claude-code", "codex", "gemini", "opencode"}
```

Implementation locations:
- **Python SDK:** `sdk/python/agentfield/harness/` (providers, runner, schema, result)
- **Go SDK:** `sdk/go/harness/` (mirror structure)

### Provider Details

| Provider | Mechanism | Options |
|----------|-----------|---------|
| **Claude Code** (`claude-code`) | `claude_agent_sdk` Python package (`sdk.query()`) | model, cwd, max_turns, allowed_tools, system_prompt, max_budget_usd, permission_mode, env, resume_session_id |
| **Codex** (`codex`) | `codex exec --json` subprocess | Same interface |
| **Gemini CLI** (`gemini`) | `gemini -p` subprocess | Same interface |
| **OpenCode** (`opencode`) | `opencode run --format json` subprocess | Same interface, concurrency cap: 10 simultaneous |

### Common Retry Pipeline (`HarnessRunner`)

1. Transient error detection with exponential backoff (±25% jitter, 3 retries)
2. Schema validation retry loop (2 retries for output JSON compliance)
3. Cost capping (`max_budget_usd`)
4. Turn limiting (`max_turns`)
5. Tool access control
6. System prompt injection

### Output Recovery (3 layers)

1. **`_ai_schema_repair()`** -- Lightweight LLM call (90s timeout) that reformats malformed JSON
2. **Schema retry** -- Retry with diagnostic followup if repair fails
3. **Full re-run** -- Complete re-execution if both repair and retry fail

### Adding a New Provider

1. Create `harness/providers/mytool.py` implementing `async def execute(prompt, options) -> RawResult`
2. Add to `SUPPORTED_PROVIDERS` in `_factory.py`
3. Add import + branch in `build_provider()`

---

## 14. The /agentfield CLI Command

The `/agentfield` command is a **skill-based instruction packet** for coding agents, not a built-in slash command.

### How to use:

```
/agentfield Build a claims processor with risk scoring, pattern detection,
and human approval for low-confidence decisions.
```

### How it works:

1. The skill is bundled with the `af` binary as embedded markdown in `control-plane/internal/skillkit/`
2. Installed via: `af skill install` (interactive) or `af skill install --target claude-code`
3. The installer writes SKILL.md (and reference files) to the coding agent's instruction directory
4. Supported targets: Claude Code, Codex, Gemini CLI, OpenCode, Aider, Windsurf, Cursor
5. When the user types `/agentfield` in Claude Code, the active SKILL.md teaches Claude how to:
   - Design composable multi-reasoner architectures
   - Build deep dynamic call graphs
   - Fetch live SDK docs from agentfield.ai
   - Run async-first smoke tests
   - Scaffold complete agent projects

### Skill management:

| Command | Purpose |
|---------|---------|
| `af skill install` | Interactive picker of targets |
| `af skill list` | Show installed skills and their targets |
| `af skill update` | Re-install at the binary's embedded version |
| `af skill uninstall` | Remove from targets |
| `af skill print` | Print SKILL.md to stdout |
| `af skill catalog` | List skills in the binary |

---

## 15. Integration Patterns

### Hermes Integration

**Option A: MCP Bridge (Hermes to AgentField)**
- Write a Hermes MCP server that wraps the AgentField REST API (~100 lines of Python using FastMCP)
- Expose AgentField's execution endpoints as MCP tools (e.g., `agentfield_execute(agent, reasoner, input)` -> tool)
- Expose discovery as MCP resources
- Let Hermes agents call any AgentField reasoner as an MCP tool

**Option B: Harness Dispatch (AgentField to Hermes)**
- New `hermes` harness provider that runs Hermes CLI as a subprocess
- Same pattern as the existing `opencode` provider

**Option C: AgentField as Hermes Agent Backend**
- AgentField agents register as services in Hermes's workspace network
- Hermes routes cross-agent calls through AgentField's control plane
- Gains execution traces, DAG visualization, DID identity, cryptographically verifiable audit trails

**Option D: Webhook-based async bridge**
- Hermes POSTs to AgentField's async execute endpoint with a webhook URL
- AgentField executes and POSTs the result back
- No tight coupling, works across networks

### n8n Integration

**Pattern 1: n8n Webhook Node -> AgentField Execution (works today)**
1. n8n workflow triggers (webhook, cron, form)
2. n8n HTTP Request node calls `POST http://agentfield:8080/api/v1/execute/my-agent.my-reasoner`
3. AgentField executes and returns synchronously
4. For long-running agents, use async execute with webhook callback

**Pattern 2: AgentField -> n8n Webhook**
- Approval results POST to n8n webhooks via `/api/v1/webhooks/approval-response`
- Execution webhooks POST results to n8n endpoints when async executions complete
- ARD external invocation system (`/api/v1/execute/external.*`) routes to n8n endpoints

**Pattern 3: AgentField Trigger Source -> n8n**
- n8n workflow POSTs to AgentField trigger endpoints to kick off agent executions
- Trigger dispatcher runs the agent and routes results back as webhooks

Architecture contract: AgentField is the **agent execution layer** (reasoning, memory, orchestration, identity). n8n is the **workflow automation layer** (business process integration, 400+ connectors, UI workflow builder).

### OpenClaw Integration

**Option A: OpenClaw as AgentField's Gateway Layer**
- Rate limiting and circuit breaking for agent execution calls
- API key authentication and tenant isolation (maps external API keys to DID identity)
- Request routing to the correct control plane instance
- Proxies to `POST /api/v1/execute/:target`

**Option B: AgentField Agents as OpenClaw Backends**
- Agents register as backend services behind OpenClaw
- OpenClaw discovers agents via AgentField's discovery API
- Canary/A/B support via AgentField's version routing
- Metrics collected from AgentField's `/metrics` endpoint

**Option C: Shared DID Identity Layer**
- AgentField generates W3C VCs for every execution
- OpenClaw verifies AgentField-issued VCs at the gateway edge
- OpenClaw issues gateway-level credentials that AgentField's policy service validates
- Unified trust chain: OpenClaw authenticates -> issues gateway VC -> AgentField validates -> grants access

**Option D: Cross-Mesh Agent Calling**
- OpenClaw-managed agents call AgentField agents via OpenClaw's routing layer
- AgentField's `app.call()` routes through OpenClaw for non-AgentField targets
- Transparent cross-mesh calls, unified agent mesh

## Related

- [[agentfield]] -- wiki page for the platform
- [[agentfield-architecture]] -- system architecture
- [[agentfield-deployment]] -- deployment guide
- [[agentfield-quadlet]] -- Quadlet deployment
- [[agentfield-mcp-server]] -- MCP bridge server
- [[agentfield-profile]] -- AgentField platform profile
