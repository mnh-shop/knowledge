---
name: agentfield-api
tags: [agentfield, api, automation, cli, control-plane, golang, harness, identity, mcp, orchestration, plugin-sdk, quadlet, rest-api, security, systemd, webhook]
description: "AgentField API reference: REST and gRPC endpoints for agent orchestration, execution, memory, identity, and MCP"
source: sources/agentfield/
---

# AgentField API Reference
**Source:** `sources/agentfield/` (v0.1.118-rc.3, Apache-2.0)

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
11. [Connector API](#11-connector-api)
12. [Config Storage & Serverless](#12-config-storage--serverless)
13. [HTTP Context Propagation Headers](#13-http-context-propagation-headers)
14. [HTTP Status Codes and Error Responses](#14-http-status-codes-and-error-responses)
15. [Pagination and Filtering](#15-pagination-and-filtering)
16. [SDK-Generated API Surface](#16-sdk-generated-api-surface)
17. [MCP Integration](#17-mcp-integration)
18. [gRPC Admin API](#18-grpc-admin-api)
19. [Harness Runtimes](#19-harness-runtimes)
20. [The /agentfield CLI Command](#20-the-agentfield-cli-command)
21. [Integration Patterns](#21-integration-patterns)

---

## 1. REST API Overview

AgentField exposes a REST API organized across **13 `routes_*.go` files** in `control-plane/internal/server/`. Routes are composed in `server.go:setupRoutes()` and registered under the `agentAPI` Gin group at `/api/v1/`.

### Route Groups (10 + 3 auxiliary)

| Group | Count | Files | Coverage |
|-------|-------|-------|----------|
| Core | 53 | `routes_core.go` | nodes register/list/heartbeat/status-lease/start/stop, discovery, execute sync/async, executions status/events/batch/cancel/pause/resume/restart, approvals, notes, cancel-tree, session-targets, session-instances |
| Memory | 14 | `routes_memory.go` | KV CRUD, vector store, events (SSE/WS/history) |
| Triggers | 18 | `routes_triggers.go` | GitHub/Slack/Stripe/GenericBearer/GenericHMAC providers, SSE stream, replay |
| Agentic | 12 | `routes_agentic.go` | discover/query/run/agent/status/batch + KB (5 routes under `/agentic/kb`) |
| DID | 9 | `routes_did.go` | DID document, policies, revocations, registered-dids, issuer keys |
| Observability | 7 | `routes_observability.go` | observability-webhook settings + DLQ |
| Admin | 6 | `routes_admin.go` | /debug/pprof endpoints (admin-gated) |
| ARD | 5 | `routes_ard.go` | /.well-known/ai-catalog.json, artifacts, search, agents, explore |
| Knowledge | 3 | `routes_knowledge.go` | upsert/search/delete source |
| Connector | conditional | `routes_connector.go` | capability-gated (`features.connector.capabilities`: weight, tags, config_management) |
| MCP | 3 | `routes_mcp.go` | POST /mcp + GET/OPTIONS preflight |
| UI v1 | 88 | `routes_ui.go` | browser-facing APIs at `/api/ui/v1` |
| UI v2 | 3 | `routes_ui.go` | `/api/ui/v2`: workflow-runs list (`:284`), detail (`:285`), golden (`:286`) |

### Route Source Files

| Route Group | File |
|-------------|------|
| Public & core execution | `routes_core.go` |
| Node lifecycle / discovery / sessions | `routes_core.go` |
| Memory | `routes_memory.go` |
| Knowledge (RAG) | `routes_knowledge.go` |
| DID/VC | `routes_did.go` |
| Admin (pprof, tag approval, policies) | `routes_admin.go` |
| Connector (fleet management) | `routes_connector.go` |
| Agentic (machine-friendly) + KB | `routes_agentic.go` |
| Triggers/webhooks | `routes_triggers.go` |
| UI API | `routes_ui.go` |
| Observability settings | `routes_observability.go` |
| ARD (Agent Resource Discovery) | `routes_ard.go` |
| MCP (embedded) | `routes_mcp.go` |

### Public (unauthenticated) Surface

- `GET /metrics` — Prometheus (`routes_core.go:21`)
- `GET /health` — health check (`routes_core.go:22`)
- `GET /.well-known/did.json` and `GET /agents/:agentID/did.json` — did:web resolution (`routes_did.go:28-29`)
- `GET /.well-known/ai-catalog.json` — public ARD catalog (`routes_ard.go:25`)
- `GET /api/v1/agentic/kb/*` — knowledge base on the root router (`routes_agentic.go:40-49`)
- `/api/ui/v1`, `/api/ui/v2`, `/ui/` SPA
- `/debug/pprof` — behind admin auth (`routes_admin.go:57-62`)
- `POST /mcp` — embedded MCP server

### Authentication Model (5 Layers)

1. **API Key** — header `X-API-Key` (preferred) or `Authorization: Bearer <key>` / `api_key` query param (`middleware/auth.go:104-108`). Required for all API calls unless `api.auth.insecure_disable_auth`. Env: `AGENTFIELD_API_KEY` / `AGENTFIELD_API_AUTH_API_KEY`.

2. **DID Signatures** (cross-agent calls) — `X-Caller-DID`, `X-DID-Signature` (Ed25519 over `{timestamp}:{SHA256(body)}`), `X-DID-Timestamp` (300s window) (`middleware/did_auth.go:172-175`).

3. **Admin Token** — header `X-Admin-Token` (`middleware/auth.go:173-178`), gated via `middleware.AdminTokenAuth()`, used for tag approval, policy management, and `/debug/pprof`. Env: `AGENTFIELD_AUTHORIZATION_ADMIN_TOKEN` (config default `admin-secret`).

4. **Internal calls** — the control plane authenticates agent-bound internal requests (cancel dispatcher, etc.) with `Authorization: Bearer <internal_token>` (`control-plane/internal/handlers/cancel_dispatcher.go:70-73`) — **not** a separate internal-token header. Agents with `RequireOriginAuth` validate it in their `originAuthMiddleware()`. Env: `AGENTFIELD_AUTHORIZATION_INTERNAL_TOKEN`.

5. **Connector Token** — header `X-Connector-Token` (`middleware/connector_auth.go:23-27`), gated via `middleware.ConnectorTokenAuth()`, authenticates external connector integrations. Config: `features.connector.token`.

### Permission Middleware (Tag-Based IAM)

When DID authorization is enabled (`features.did.authorization.enabled: true`), `middleware.PermissionCheckMiddleware()` applies to execute endpoints, legacy reasoner/skill endpoints, and session-target start. Memory uses a separate `middleware.MemoryPermissionMiddleware()` with scope ownership. First-match-wins policies; `default_deny: true` returns 403.

### DID Auth Error Responses (did_auth.go:188-298)

| HTTP | Error Code | Condition |
|------|-----------|-----------|
| 400 | `invalid_did_format` | `X-Caller-DID` is not a valid DID |
| 401 | `did_auth_required` | `X-Caller-DID` present but `X-DID-Signature`/`X-DID-Timestamp` missing |
| 400 | `invalid_timestamp` | Timestamp is not a valid Unix timestamp |
| 401 | `timestamp_expired` | Timestamp outside the 300s window |
| 400 | `body_read_error` | Request body could not be read |
| 413 | `body_too_large` | Request body exceeds size limit |
| 400 | `invalid_signature_encoding` | Signature is not valid base64 |
| 401 | `replay_detected` | Signature nonce/timestamp replayed |
| 400 | `verification_error` | Signature verification failed |
| 401 | `invalid_signature` | Ed25519 signature mismatch |

---

## 2. Execution Endpoints

### Synchronous Execution

```
POST /api/v1/execute/:target
```
- `target` format: `agent_id.reasoner_name`
- Body: `{"input": {...}}`
- Blocks until execution completes (agent call timeout configurable)

### Async Execution

```
POST /api/v1/execute/async/:target
```
- Returns immediately with `execution_id`
- Long-running agents supply `webhook: {url: "https://..."}` for callback

### Execution Status & Lifecycle

```
GET  /api/v1/executions/:execution_id
POST /api/v1/executions/:execution_id/status      (agent → control plane)
POST /api/v1/executions/:execution_id/cancel
POST /api/v1/executions/:execution_id/pause
POST /api/v1/executions/:execution_id/resume
POST /api/v1/executions/:execution_id/restart
POST /api/v1/executions/:execution_id/logs        (structured NDJSON logs)
GET  /api/v1/executions/:execution_id/events      (SSE stream, routes_core.go:121)
GET  /api/v1/executions/active
POST /api/v1/executions/batch-status              (routes_core.go:122)
```

Status values: `queued`, `running`, `completed`, `failed`, `paused`, `cancelled`.

### SSE Endpoints (complete list — there is NO `/api/v1/events`)

| Endpoint | Method | File |
|----------|--------|------|
| `/api/v1/executions/:execution_id/events` | GET (SSE) | `routes_core.go:121` |
| `/api/v1/workflow/executions/events` | POST (SSE fan-out) | `routes_core.go:159` |
| `/api/v1/memory/events/sse` | GET (SSE) | `routes_memory.go:51` |
| `/api/v1/memory/events/ws` | GET (WebSocket) | `routes_memory.go:50` |
| `/api/v1/memory/events/history` | GET | `routes_memory.go:52` |
| `/api/v1/triggers/:trigger_id/events/stream` | GET (SSE) | `routes_triggers.go:42` |

### Workflow Tree Operations

```
POST /api/v1/workflows/:workflowId/cancel-tree
```
Cancels an entire workflow tree (multi-hop DAG) (`routes_core.go:131`).

### Execution Engine Notes

Async completions flow through an **in-process completion queue** (`handlers/execute.go:174` `completionQueue chan completionJob`, default size 2048, `AGENTFIELD_EXEC_COMPLETION_QUEUE`). Execution is gated by a concurrency limiter + LLM-health circuit breaker (`handlers/execution_guards.go`). State persists in PostgreSQL — there is no distributed execution queue and no scheduler backend yet (see `nodes_rest.go:194` "scheduler backend is under construction").

---

## 3. Approval Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/executions/:execution_id/request-approval` | Request human approval (`routes_core.go:135`) |
| GET | `/api/v1/executions/:execution_id/approval-status` | Poll approval status (`routes_core.go:136`) |
| POST | `/api/v1/executions/:execution_id/approval-response` | Resolve approval (`routes_core.go:140`) |
| POST | `/api/v1/agents/:node_id/executions/:execution_id/request-approval` | Agent-scoped approval request (`:143`) |
| GET | `/api/v1/agents/:node_id/executions/:execution_id/approval-status` | Agent-scoped status (`:144`) |
| POST | `/api/v1/agents/:node_id/executions/:execution_id/awaiter-status` | Multi-hop pause propagation (`:151`) |
| POST | `/api/v1/webhooks/approval-response` | External approval resolution webhook (HMAC-secret signed, `:154`) |

The approval flow enables human-in-the-loop patterns:
1. Agent calls `app.pause("Explain reasoning before proceeding")`
2. Control plane marks execution as `paused`
3. Human reviews via `/request-approval` or `/approval-status`
4. Resolution posted to `/approval-response`
5. Control plane resumes the execution

---

## 4. Node Lifecycle Endpoints

### Registration

```
POST /api/v1/nodes/register        (routes_core.go:39)
POST /api/v1/nodes                 (alias, :40)
POST /api/v1/nodes/register-serverless  (FaaS/serverless agents, :41)
```
Registration body: agent metadata, callback URL, capabilities, tags, DID keys.

### Heartbeat, Status & Presence Lease

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/nodes` | List all registered agents |
| GET | `/api/v1/nodes/:node_id` | Get agent details |
| POST | `/api/v1/nodes/:node_id/heartbeat` | Agent heartbeat (renews presence lease) |
| PATCH | `/api/v1/nodes/:node_id/status` | **Status lease** (`NodeStatusLeaseHandler`, routes_core.go:57; `DefaultLeaseTTL = 5min`, nodes_rest.go:17-18) |
| POST | `/api/v1/nodes/status/bulk` | Bulk status update (`:50`) |
| POST | `/api/v1/nodes/status/refresh` | Refresh all statuses (`:51`) |
| GET | `/api/v1/nodes/:node_id/status` | Get node status (`:48`) |
| POST | `/api/v1/nodes/:node_id/status/refresh` | Refresh single status (`:49`) |
| POST | `/api/v1/nodes/:node_id/actions/ack` | Ack a claimed action (`:58`) |
| POST | `/api/v1/actions/claim` | Claim pending lifecycle actions (poll mode; returns empty queue — scheduler under construction, `:60`) |
| POST | `/api/v1/nodes/:node_id/start` | Start node (`:54`) |
| POST | `/api/v1/nodes/:node_id/stop` | Stop node (`:55`) |
| POST | `/api/v1/nodes/:node_id/shutdown` | Shutdown node (`:59`) |
| POST | `/api/v1/nodes/:node_id/lifecycle/status` | Update lifecycle status (`:56`) |
| DELETE | `/api/v1/nodes/:node_id/monitoring` | Unregister from monitoring (`:45`) |

---

## 5. Discovery Endpoints

```
GET /api/v1/discovery/capabilities
```
- Query parameters: `tag`, `name`, `health`
- Returns `AgentCapability` and `ReasonerCapability` objects
- Used by SDK's `app.discover()`

```
GET /api/v1/reasoners        (routes_core.go:36)
GET /api/v1/agents           (via Agentic/UI surfaces)
```

---

## 6. Memory Endpoints

Memory is organized in 4 scopes: `global`, `session`, `actor`, `workflow`. All under `/api/v1/memory` (`routes_memory.go`).

### KV Store

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/memory/set` | Set key |
| POST | `/memory/get` | Get key |
| POST | `/memory/delete` | Delete key |
| GET | `/memory/list` | List keys |

### Vector Store (pgvector)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/memory/vector` / `/memory/vector/set` | Set vector |
| GET | `/memory/vector/:key` | Get vector |
| POST | `/memory/vector/search` | Cosine similarity search |
| DELETE | `/memory/vector/:key` / `/memory/vector/delete` | Delete vector |
| DELETE | `/memory/vector/namespace` | Delete namespace vectors |

### Events

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/memory/events/sse` | SSE memory event stream |
| GET | `/memory/events/ws` | WebSocket memory event stream |
| GET | `/memory/events/history` | Event history |

Notes: `POST /api/v1/executions/note` + `GET /api/v1/executions/:execution_id/notes` add/read execution audit notes (`routes_core.go:157-158`). Reactive subscriptions via `@app.on_change()` in the Python SDK.

---

## 7. Identity (DID/VC) Endpoints

The DID system produces a three-tier key hierarchy: Platform DID (control plane) → Node DID (per agent) → Function DID (per reasoner/skill). Signing keys are Ed25519 (BIP32-derived), keystore AES-256-GCM encrypted, rotated every 90 days by default.

### DID Resolution (public, did:web)

```
GET /.well-known/did.json
GET /agents/:agentID/did.json
```

### DID & Policy Surface (`routes_did.go`)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/did/agentfield-server` | Server's own DID |
| GET | `/api/v1/did/issuer-public-key` | Control plane issuer public key (JWK) |
| GET | `/api/v1/admin/public-key` | Legacy alias |
| GET | `/api/v1/policies` | All access policies (SDKs cache for offline verification) |
| GET | `/api/v1/revocations` | All revoked DIDs |
| GET | `/api/v1/registered-dids` | All active registered DIDs |
| GET | `/api/v1/agents/:node_id/tag-vc` | Agent's verified tag VC |

Agents refresh these on a 5-minute cycle (`localVerifier.NeedsRefresh()` in the Go SDK). Registration/VC-chain/rotation endpoints (e.g. DID register, VC chain per workflow/execution) are served by the DID service handlers (`control-plane/internal/handlers/did_handlers.go`) and consume/generate VCs via the SDK `vc_generator.py`.

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
GET /metrics        -- Prometheus (routes_core.go:21)
GET /health         -- health check (routes_core.go:22)
GET /debug/pprof/   -- pprof profiles (admin-gated, routes_admin.go:57-62)
```

### Observability Webhook Settings (`routes_observability.go`)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/observability-webhook` | Get webhook config |
| POST | `/api/v1/observability-webhook` | Set webhook config |
| DELETE | `/api/v1/observability-webhook` | Delete webhook config |
| GET | `/api/v1/observability-webhook/status` | Forwarder status |
| POST | `/api/v1/observability-webhook/redrive` | Redrive failed events |
| GET | `/api/v1/observability-webhook/dlq` | Dead-letter queue contents |
| DELETE | `/api/v1/observability-webhook/dlq` | Clear DLQ |

The observability forwarder batches events (`BatchSize: 10`, `QueueSize: 1000` — `server.go:414`) and signs webhook deliveries with HMAC.

---

## 9. Agentic API

Machine-friendly endpoints for external tools, agents, and CI/CD (`routes_agentic.go`):

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/agentic/status` | System status |
| GET | `/api/v1/agentic/discover` | Endpoint catalog search |
| GET | `/api/v1/agentic/reasoners` | List reasoners |
| POST | `/api/v1/agentic/query` | Unified resource query |
| GET | `/api/v1/agentic/run/:run_id` | Run overview |
| GET | `/api/v1/agentic/agent/:agent_id/summary` | Agent summary |
| POST | `/api/v1/agentic/batch` | Batch API operations |

### Knowledge Base (public, on root router)

```
GET /api/v1/agentic/kb/topics
GET /api/v1/agentic/kb/articles
GET /api/v1/agentic/kb/articles/:article_id
GET /api/v1/agentic/kb/articles/:article_id/:sub_id
GET /api/v1/agentic/kb/guide
```

---

## 10. Trigger/Webhook Endpoints

Trigger providers: **GitHub, Slack, Stripe, GenericBearer, GenericHMAC** (+ Linear/Sentry/Snowflake via integrations), cron schedules. 18 route registrations in `routes_triggers.go`.

### Public Ingest (no auth)

```
POST /api/v1/sources/:trigger_id      (IngestSourceHandler, :19)
GET  /api/v1/sources/:name            (GetSource, :37)
GET  /api/v1/sources                  (ListSources, :45)
```

### Trigger CRUD & Ops

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/triggers` | List triggers |
| POST | `/api/v1/triggers` | Create trigger |
| GET | `/api/v1/triggers/:trigger_id` | Get trigger |
| PUT | `/api/v1/triggers/:trigger_id` | Update trigger |
| DELETE | `/api/v1/triggers/:trigger_id` | Delete trigger |
| GET | `/api/v1/triggers/:trigger_id/events` | List events |
| GET | `/api/v1/triggers/:trigger_id/events/:event_id` | Get event |
| POST | `/api/v1/triggers/:trigger_id/events/:event_id/replay` | Replay event |
| POST | `/api/v1/triggers/:trigger_id/pause` | Pause trigger |
| POST | `/api/v1/triggers/:trigger_id/resume` | Resume trigger |
| POST | `/api/v1/triggers/:trigger_id/test` | Test trigger |
| POST | `/api/v1/triggers/:trigger_id/convert-to-ui` | Convert to UI trigger |
| GET | `/api/v1/triggers/:trigger_id/secret-status` | Secret status |
| GET | `/api/v1/triggers/:trigger_id/events/stream` | SSE event stream |
| GET | `/api/v1/triggers/metrics` | Trigger metrics |

### Execution Webhooks

Webhook dispatcher signs deliveries with **HMAC-SHA256** (`control-plane/internal/handlers/webhook_dispatcher.go`; observability forwarder too, `services/observability_forwarder.go:722`). Timeout: 10s per attempt, max 3 attempts.

---

## 11. Connector API

Conditionally registered when connector capability is enabled (`features.connector.capabilities` — `weight`, `tags`, `config_management`), behind `ConnectorTokenAuth` (`routes_connector.go:22-40`; `config_management` additionally gated by `ConnectorCapabilityCheck`). Handlers in `control-plane/internal/handlers/connector/handlers.go`.

### Traffic Weight

```
PUT /api/v1/connector/reasoners/:id/versions/:version/weight
```
Body: `{"weight": int}` (0–10000). Handler `SetReasonerTrafficWeight` (`handlers.go:72`, `447-488`). **Note:** rollout percentages cited in the README are marketing; there is no traffic-shaping controller — the weight field is stored per (id, version) but no scheduler consumes it yet.

---

## 12. Config Storage & Serverless

### Config Storage API (`handlers/config_storage.go`, registered in routes_core.go:31-35)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/configs` | List stored config keys |
| GET | `/api/v1/configs/:key` | Get config value |
| PUT | `/api/v1/configs/:key` | Set config value |
| DELETE | `/api/v1/configs/:key` | Delete config value |
| POST | `/api/v1/configs/reload` | Reload runtime config |

### Serverless Registration

`POST /api/v1/nodes/register-serverless` (routes_core.go:41) — register an agent without a persistent HTTP listener (FaaS/Lambda style; see `sdk/python/agentfield/agent_serverless.py`). CLI: `af register-serverless --url <url>`.

---

## 13. HTTP Context Propagation Headers

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

---

## 14. HTTP Status Codes and Error Responses

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
| 400 | Bad Request | Invalid JSON, missing fields, `invalid_did_format`, `invalid_timestamp` |
| 401 | Unauthorized | Missing/invalid API key, `did_auth_required`, `invalid_signature`, `replay_detected` |
| 403 | Forbidden | Policy denied, tag forbidden, bad admin/connector token |
| 404 | Not Found | Agent, execution, policy, trigger not found; `/mcp` when disabled |
| 409 | Conflict | Duplicate registration or trigger name |
| 413 | Payload Too Large | `body_too_large` (DID auth) |
| 422 | Unprocessable | Input validation error per `_HandlerInputError` |
| 429 | Too Many Requests | `concurrency_limit` (execution guard) |
| 499 | Cancelled | Execution cancelled by control plane |
| 500 | Internal Error | Storage failure, unexpected error |
| 503 | Service Unavailable | `llm_unavailable`, pending approval, status manager not ready |

---

## 15. Pagination and Filtering

**Offset-limit pagination:**
```
GET /api/v1/nodes?offset=0&limit=20
```

```json
{
  "results": [...],
  "total": 100,
  "offset": 0,
  "limit": 20
}
```

**Query parameter filtering:**
- `tags=<glob>` — tag glob patterns (e.g. `tags=nlp*`)
- `health=<status>` — `ready`, `degraded`, `offline`, `starting`, `active`
- `team_id`, `group_id`, `name`, `mode`, `status`

**Bulk operations:**
```http
POST /api/v1/executions/batch-status
Content-Type: application/json

{"execution_ids": ["id1", "id2", "id3"]}
```

---

## 16. SDK-Generated API Surface

The Python SDK's `Agent` class (subclass of `FastAPI`) auto-generates REST endpoints from decorators:

| Decorator | Generated Endpoint | Method | Purpose |
|-----------|-------------------|--------|---------|
| `@app.reasoner()` | `/reasoners/{id}` | POST | AI reasoning with LLM, type-hint-derived schema |
| `@app.skill()` | `/skill/{id}` | POST | Deterministic logic |
| `@app.session()` | `/session/{id}` | POST | Multi-turn conversation session |

Each reasoner endpoint: parses JSON → validates against type hints (no Pydantic model, ~1.5-2 KB saved per handler) → wraps in workflow tracking → sync or async (`X-Execution-ID` triggers async path). All are also reachable via the unified control-plane endpoint `POST /api/v1/execute/{agent_id}.{reasoner_id}`.

The Go SDK uses `http.ServeMux` internally:
```
GET  /health                  -- Agent health check
GET  /discover                -- Capability discovery
POST /execute                 -- Execute any reasoner
POST /execute/{name}          -- Execute named reasoner
GET  /reasoners/{id}          -- Get reasoner metadata
POST /reasoners/{id}          -- Execute specific reasoner
POST /_internal/executions/{id}/cancel  -- Cancel execution (control-plane only)
POST /agentfield/v1/logs      -- NDJSON process logs
```

---

## 17. MCP Integration

**Status: ACTIVE.** The embedded MCP server is present and enabled by default.

History: MCP was removed in PR #359 ("Refactor: remove all MCP code from codebase") and **re-added in PR #817**. Current implementation (`routes_mcp.go:40-69`, `handlers/mcp.go`):

- **Endpoint:** `POST /mcp` — streamable-HTTP JSON-RPC 2.0, on the same port/trust domain as the REST API. GET → 405, OPTIONS → 204 preflight (`routes_mcp.go:61-68`)
- **Default on:** `features.mcp.enabled` (default true, `config.go:254-275`); disable with `AGENTFIELD_MCP_ENABLED=false` or `mcp.enabled: false` → `/mcp` returns 404
- **5 tools** (`docs/mcp-integration.md`):

| Tool | Input | Output |
|------|-------|--------|
| `discover_agents` | `health?` (`"active"`/`"all"`) | Agents with `id`, `health_status`, `last_heartbeat`, and their `reasoners` |
| `get_reasoner_schema` | `node`, `reasoner` | Reasoner input/output JSON Schema, description, tags |
| `execute_reasoner` | `target` (`"node.reasoner"`), `input` | Starts async execution → `{ run_id, status: "accepted" }` |
| `get_run` | `run_id` | Run `status`, `result`/`error`, per-execution summaries |
| `wait_run` | `run_id`, `timeout_seconds?` (default 60, max 120) | Server-side poll to terminal state, `timed_out` flag |

- **Auth:** MCP requests pass the same permission middleware as REST execution (`mcpAuthorizer()`, `routes_mcp.go:69-79`) — targets come from the JSON-RPC argument, not the URL
- The ARD catalog additionally registers `application/mcp-server+json` artifacts for external MCP servers

---

## 18. gRPC Admin API

- **Port:** 8180 = HTTP port + 100 (`server.go:469`), listener in `startAdminGRPCServer()` (`server.go:712-738`)
- **Service:** `AdminReasonerService` (proto: `control-plane/proto/admin/reasoner_admin.proto`), e.g. `ListReasoners`
- **Auth:** API key via `middleware.APIKeyUnaryInterceptor` when `api.auth.api_key` is set (`grpc_auth.go`)

---

## 19. Harness Runtimes

The Harness feature (`app.harness(prompt, provider=...)`) treats LLM CLI tools as autonomous computational units.

```
SUPPORTED_PROVIDERS = {"claude-code", "codex", "gemini", "opencode"}
```

| Provider | Mechanism | Options |
|----------|-----------|---------|
| **Claude Code** | `claude_agent_sdk` Python package (`sdk.query()`) | model, cwd, max_turns, allowed_tools, system_prompt, max_budget_usd, permission_mode, env, resume_session_id |
| **Codex** | `codex exec --json` subprocess | Same interface |
| **Gemini CLI** | `gemini -p` subprocess | Same interface |
| **OpenCode** | `opencode run --format json` subprocess | Same interface, concurrency cap: 10 |

Retry pipeline: transient-error backoff (±25% jitter, 3 retries) → schema validation retry (2) → `_ai_schema_repair()` (90s LLM call) → full re-run. Implementations: `sdk/python/agentfield/harness/` and `sdk/go/harness/`.

---

## 20. The /agentfield CLI Command

The `/agentfield` command is a **skill-based instruction packet** for coding agents, not a built-in slash command.

1. Bundled in the binary (`control-plane/internal/skillkit/`, embedded via `//go:embed`)
2. Installed via `af skill install` / `af skill install --target <claude-code|codex|gemini|opencode|aider|windsurf|cursor>`
3. Skills shipped: `agentfield`, `agentfield-personal`, `agentfield-use`

| Command | Purpose |
|---------|---------|
| `af skill install` | Interactive picker of targets |
| `af skill list` | Show installed skills and their targets |
| `af skill update` | Re-install at the binary's embedded version |
| `af skill uninstall` | Remove from targets |
| `af skill print` | Print SKILL.md to stdout |
| `af skill catalog` | List skills in the binary |

---

## 21. Integration Patterns

### Hermes Integration

**Option A: MCP Bridge (Hermes → AgentField)** — Hermes agents call AgentField's embedded `/mcp` (5 tools: `discover_agents`, `execute_reasoner`, `get_run`, `wait_run`) directly as MCP tools, or a wrapper FastMCP server can expose the REST surface.

**Option B: Harness Dispatch (AgentField → Hermes)** — a `hermes` harness provider mirroring the `opencode` provider.

**Option C: AgentField as Hermes Agent Backend** — Hermes routes cross-agent calls through AgentField's control plane, gaining execution traces, DAG visualization, DID identity, and verifiable audit trails.

**Option D: Webhook-based async bridge** — Hermes POSTs to async execute with a webhook URL; AgentField POSTs results back.

### n8n Integration

1. **n8n Webhook → Execution:** HTTP Request node calls `POST http://agentfield:8080/api/v1/execute/my-agent.my-reasoner` (sync) or async + webhook callback.
2. **AgentField → n8n:** approval results via `/api/v1/webhooks/approval-response`; execution webhooks (HMAC-SHA256) POST completions; ARD external invocation routes to n8n endpoints.
3. **Trigger source → n8n:** n8n POSTs to `/api/v1/sources/:trigger_id` ingest endpoints.

Architecture contract: AgentField is the **agent execution layer**; n8n is the **workflow automation layer**.

### OpenClaw Integration

- **Option A:** OpenClaw as gateway — rate limiting, circuit breaking, API-key→DID mapping, proxying to `POST /api/v1/execute/:target`.
- **Option B:** AgentField agents as OpenClaw backends — discovery via `/api/v1/discovery/capabilities`, metrics via `/metrics`.
- **Option C:** Shared DID identity — OpenClaw verifies AgentField-issued VCs at the edge; unified trust chain.
- **Option D:** Cross-mesh calling — OpenClaw-managed agents call AgentField agents via `app.call()`.

## Related

- [[agentfield]] -- wiki page for the platform
- [[agentfield-architecture]] -- system architecture
- [[agentfield-deployment]] -- deployment guide
- [[agentfield-quadlet]] -- Quadlet deployment
- [[agentfield-mcp-server]] -- MCP bridge server
- [[hermes-profiles]] -- AgentField platform profile
