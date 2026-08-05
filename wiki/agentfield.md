---
name: agentfield
tags: [agentfield, cli, container, control-plane, dashboard, desktop, docker, event-bus, grpc, harness, identity, mcp, monitoring, orchestration, podman, quadlet, security, sessions, storage, systemd, triggers, webhook, wiki, agent, python, golang, typescript]
description: "Wiki entry for AgentField: AI control plane that orchestrates agent nodes (Go/Python/TS SDKs) with DID IAM, memory, sessions, triggers, an embedded MCP server, and a desktop tray"
source: sources/agentfield/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# AgentField

| Field | Value |
|---|---|
| **Origin** | [Agent-Field/agentfield](https://github.com/Agent-Field/agentfield) |
| **License** | Apache 2.0 |
| **Version** | `0.1.118-rc.3` |
| **Stack** | Go (control plane) + Python/Go/TypeScript SDKs + Electron desktop + React UI |
| **Source** | `sources/agentfield/` |
| **CLAUDE.md** | `sources/agentfield/CLAUDE.md` |
| **Reference** | `assets/agent-references/agentfield-reference.md` |
| **API** | `domains/api/agentfield-api.md` — REST surface, 5-layer auth, DID IAM, SDK-generated APIs |
| **Deployment** | `domains/deployment/agentfield-deployment.md` — Docker Compose, Helm, production ops |
| **Quadlet** | `assets/deployment/agentfield-quadlet.md` — rootless Podman Quadlet units |
| **MCP** | Embedded MCP server at `POST /mcp` (5 tools) + bridge reference in `assets/mcp-servers/agentfield-mcp-server.md` |
| **Wanted** | AgentField is an **AI backend control plane** — deploy, observe, and prove AI agents in production |

## What it is

AgentField turns agent logic into production infrastructure. You write agent code in Python, Go, or TypeScript — AgentField turns it into REST endpoints with routing, coordination, memory, async execution, and cryptographic audit trails.

**What it orchestrates:** Agent nodes. SDK-based agents register with the control plane, which then exposes their reasoners and skills as callable endpoints, coordinates cross-agent calls, tracks executions as DAGs, and signs every execution with a verifiable credential. AgentField does **not** sandbox or virtualize agent runtimes — the control plane is stateless orchestration, and agents run wherever the SDK ships them (containers, bare metal, VMs, serverless).

**Position vs alternatives:** AgentField positions itself as the control plane layer *under* agent frameworks (LangChain, CrewAI) and alongside workflow engines (n8n, Temporal). Key differentiator: IAM for agents (DID/VC identity), harness orchestration for coding agents, and cross-agent mesh with discovery.

## Key Features

### Build
- **Reasoners & Skills**: `@app.reasoner()` for AI judgment, `@app.skill()` for deterministic code (`sdk/python/agentfield/decorators.py:50,125`)
- **Structured output**: `app.ai(schema=MyModel)` → typed Pydantic/Zod output from any LLM (100+ models via LiteLLM, `types.py:587-704`)
- **Harness orchestration**: `app.harness("Fix the bug")` dispatches multi-turn tasks to Claude Code, Codex, Gemini CLI, or OpenCode — with `max_turns`, `max_budget_usd`, and `tools` control (`harness/providers/_factory.py:9`; `_runner.py:160-168`)
- **Cross-agent calls**: `app.call("other-agent.func")` routes through the control plane with full tracing (`routes_core.go:93-116`)
- **Service discovery**: `app.discover(tags=["ml*"])` finds agents across the mesh; `tools="discover"` lets LLMs auto-invoke (`agent_discovery.py`)
- **Memory**: `app.memory.set()` / `.get()` / `.similarity_search()` — KV + vector search, 4 scopes: **global / actor / session / workflow**, no external dependencies (`memory.py:471`; scope resolution in `handlers/memory.go:402-418`)

### Run
- **Sync/async execution**: REST endpoints for sync, fire-and-forget with webhooks/SSE for async
- **HITL**: `app.pause()` suspends for human approval — crash-safe, durable, audited (`routes_core.go:128-144`)
- **Traffic weight routing**: `PUT /connector/reasoners/:id/versions/:version/weight` steers a % of traffic to a reasoner version (`connector/handlers.go:72`) — A/B testing, blue-green. Note: the 5% → 50% → 100% rollout narrative in the README is marketing; the API takes an arbitrary weight
- **Observability**: Automatic workflow DAGs, Prometheus metrics, structured logging, execution timeline
- **In-process execution queue**: async executions are buffered in a Go channel (`execute.go:174` `completionQueue`, `server.go:414` `QueueSize: 1000`) — **not** a PostgreSQL-backed durable queue with leases. "Lease" in the codebase refers only to agent node presence heartbeats (`nodes_rest.go:18` `DefaultLeaseTTL = 5 * time.Minute`)

### Govern
- **Cryptographic identity**: Every agent gets a W3C DID (Ed25519 verification keys, `Ed25519VerificationKey2020` in `routes_did.go:313`) — agents authenticate like services do with mTLS
- **Verifiable Credentials**: Tamper-proof receipt per execution — offline-verifiable via `af vc verify audit.json`
- **Policy enforcement**: Tag-based ACCESS/DENY rules, enforced by infrastructure, not prompts (`access_policy_service.go`)
- **Permission request workflows**: Auto-created when access denied

## Architecture

```
Agent (Python/Go/TS SDK)
  → registers with Control Plane (Go)
  → REST API endpoints auto-exposed
  → Cross-agent calls route through CP
  → Execution traced as DAGs
  → DID-signed audit trail per execution

Control Plane (stateless Go):
  - REST API (10 route groups under /api/v1/, ~127 endpoint registrations)
  - Embedded MCP server (POST /mcp, streamable HTTP, 5 tools)
  - gRPC AdminReasonerService (:8180 = HTTP port + 100)
  - Execution engine (sync + async + SSE streaming, in-process queue)
  - Identity & policy (API Key, DID, Admin Token, Bearer internal token, Connector Token)
  - Memory service (KV + vector, 4 scopes: global/actor/session/workflow)
  - Trigger engine (GitHub/Slack/Stripe/GenericBearer/GenericHMAC providers)
  - Sessions (realtime-offer, tools, session-targets)
  - Web UI (embedded React, two API versions: /api/ui/v1 and /api/ui/v2)

Binaries:
  - af (unified CLI; bare `af` = server mode)
  - agentfield-server (standalone server, used by Docker/distroless)
  - af-tray (macOS menu-bar: fleet status, 24h usage, Claude quota, launchd autostart)
  - x25519gen (DID keypair generator)

Storage: PostgreSQL 15+ (production) or SQLite + BoltDB (local dev)
No external queue needed — state in SQLite or PostgreSQL
```

### Route Groups (from source)

10 groups registered under `/api/v1` (`server.go:873-885`), ~127 endpoint registrations across 13 route files. `routes_middleware.go` holds middleware composition (no endpoints) and `routes_ui.go` serves the browser-facing `/api/ui/v1` + `/api/ui/v2` surfaces plus embedded React static files. There is **no** `routes_swagger.go`.

| # | Route file | Endpoints | Group |
|---|-----------|-----------|-------|
| 1 | `routes_core.go` | 53 | Agent registration, execution (sync/async/stream), node management, session-targets, pause/resume/restart, approvals, health |
| 2 | `routes_triggers.go` | 18 | Trigger CRUD + public ingest at `/sources/:trigger_id`, provider dispatch, SSE, replay |
| 3 | `routes_memory.go` | 14 | KV memory CRUD, vector memory search, memory events (SSE + WebSocket + history) |
| 4 | `routes_agentic.go` | 12 | Agentic API: discover, query, run, agent, batch, status + public KB routes (`/api/v1/agentic/kb`) |
| 5 | `routes_did.go` | 9 | DID document resolution (did:web → did:key fallback), VC issuance, policy distribution, revocation, issuer public key |
| 6 | `routes_observability.go` | 7 | Observability webhook settings |
| 7 | `routes_admin.go` | 6 | Admin endpoints gated by AdminTokenAuth — tag approval, access policy management |
| 8 | `routes_ard.go` | 5 | ARD (Agent Resource Discovery) public + authenticated routes |
| 9 | `routes_knowledge.go` | 3 | Knowledge store CRUD and search |
| 10 | `routes_connector.go` | (feature-gated) | Connector API for air-gapped deployments, token-authenticated (`routes_connector.go:22-28`), traffic weight config |
| — | `routes_mcp.go` | 3 | Embedded MCP server: POST `/mcp` (JSON-RPC 2.0), GET 405, OPTIONS preflight |
| — | `routes_ui.go` | — | `/api/ui/v1` (agents, nodes, executions, workflows, reasoners, dashboard, DID, VC, `ard`, `llm/health`, `queue/status`) + `/api/ui/v2` (workflow-runs, golden runs) + embedded React static |
| — | `routes_middleware.go` | — | Middleware composition (auth layers, permission checks, CORS) |

### Authentication (5-Layer, from source)

| Layer | Header/Mechanism | Purpose |
|-------|-----------------|---------|
| API Key | `X-API-Key` | Simple key auth for agents and clients |
| DID (decentralized) | `X-Caller-DID` + `X-DID-Signature` + `X-DID-Timestamp` + `X-DID-Nonce` | Ed25519-signed requests, 300s timestamp window, antireplay nonce + signature replay cache |
| Admin Token | `X-Admin-Token` | Protects admin endpoints (access policies, tag approval) |
| Internal Token | `Authorization: Bearer <token>` | CP-to-agent internal request auth (execution dispatch, cancel callbacks — `cancel_dispatcher.go:70-73,213`). **Not** a dedicated internal-token header |
| Connector Token | `X-Connector-Token` | Air-gapped connector auth (`routes_connector.go:22-28`) |

DID auth error codes (`middleware/did_auth.go:188-298`): `invalid_did_format`, `did_auth_required`, `invalid_timestamp`, `timestamp_expired`, `body_read_error`, `body_too_large`, `invalid_signature_encoding`, `replay_detected`, `verification_error`, `invalid_signature`.

### Key packages

| Package | Role |
|---------|------|
| `control-plane/cmd/af/` | Unified CLI (root = server; `init`, `dev`, `install`, `call`, `agent`, `session`, `vc`, `secrets`, `skill`, …) |
| `control-plane/cmd/agentfield-server/` | Standalone server binary (Docker/distroless entrypoint) |
| `control-plane/cmd/af-tray/` | macOS menu-bar app (fleet status, 24h usage histogram, Claude quota, launchd autostart) |
| `control-plane/cmd/x25519gen/` | DID keypair generator |
| `control-plane/internal/server/` | HTTP server setup (Gin), 13 route files (`routes_*.go`), gRPC `AdminReasonerService` (:8180) |
| `control-plane/internal/handlers/` | REST/gRPC handlers (per-domain subdirectories, incl. `connector/`, `ui/`, `triggers/`) |
| `control-plane/internal/services/` | Business logic (execution, registry, memory, identity, skillkit, trigger dispatcher, cancel dispatcher) |
| `control-plane/internal/storage/` | Multi-backend storage (SQLite + BoltDB, PostgreSQL + pgvector, connector) |
| `control-plane/internal/events/` | Event bus + SSE streaming |
| `control-plane/internal/core/` | Domain models (agent, execution, session, workflow, memory) |
| `control-plane/internal/config/` | Configuration (Viper, structs: AgentFieldConfig, DIDConfig, MCPConfig, ConnectorConfig, etc.) |
| `control-plane/internal/encryption/` | DID/VC primitives (Ed25519, AES-256-GCM) |
| `control-plane/internal/packages/` | Agent node package system (`agentfield-package.yaml`, installer, secrets store, env resolver) |
| `control-plane/internal/ard/` | ARD catalog publishing (default artifact type `application/openapi+json`) |
| `control-plane/internal/application/` | Application service orchestration |
| `control-plane/internal/infrastructure/` | DB connection pooling, source plugins |
| `control-plane/internal/logger/` | Structured logging (zerolog) |
| `control-plane/internal/sources/` | Plugin source interface + trigger providers (github, slack, stripe, genericbearer, generichmac, cron, databricks, linear, sentry, snowflake) |
| `control-plane/internal/skillkit/` | Skill installation system (3 bundled skills) |
| `control-plane/internal/cli/` | Cobra command implementations (~35 commands) |
| `control-plane/web/client/` | React admin UI (Vite + Tailwind + Radix) |
| `desktop/` | Electron desktop app (Dashboard/Agents/Activity/Install/Settings, autostart, `af` as contract) |
| `sdk/python/agentfield/` | Python SDK (FastAPI-based, 54 top-level modules, 68 incl. harness/fixtures, ~1.3MB) |
| `sdk/go/` | Go SDK (agent builder, HTTP client, DID auth client, types) |
| `sdk/typescript/` | TypeScript SDK (DID encryption, agent builder) |

## Interfaces

| Interface | Details |
|-----------|---------|
| **REST API** | ~127 endpoint registrations in 10 route groups under `/api/v1/` — execute (sync/async/stream), nodes, memory, DID/VC, admin, agentic+KB, triggers, connectors, knowledge, observability, ARD. Full spec in `domains/api/agentfield-api.md` |
| **CLI (`af`)** | ~35 commands — see CLI surface below |
| **MCP** | **Embedded and on by default**: `POST /mcp` (streamable HTTP, JSON-RPC 2.0), same port as REST, behind the same auth/trust domain. Disable with `AGENTFIELD_MCP_ENABLED=false`. 5 tools: `discover_agents`, `get_reasoner_schema`, `execute_reasoner`, `get_run`, `wait_run` (`routes_mcp.go:40-69`; tool catalog in `handlers/mcp.go:721-800`; docs in `docs/mcp-integration.md`). Bridge-server reference retained in `assets/mcp-servers/agentfield-mcp-server.md` |
| **gRPC** | `AdminReasonerService` on port `:8180` (HTTP port + 100) — `ListReasoners`, etc. API-key interceptor (`server.go:712-738`; `middleware/grpc_auth.go`) |
| **/agentfield** | Claude Code / Codex slash command (skillkit) — prompts scaffold a full Docker Compose stack |
| **SDKs** | Python (FastAPI-based, 54 top-level modules / 68 total, ~1.3MB), Go (agent builder + HTTP client + DID auth), TypeScript |
| **SSE** | Execution events at `/api/v1/executions/:execution_id/events` (`routes_core.go:121`), workflow executions at `/api/v1/workflow/executions/events` (`:159`), memory change events at `/api/v1/memory/events/sse` (`routes_memory.go:51`). **There is no `/api/v1/events`** |
| **WebSocket** | Memory events at `/api/v1/memory/events/ws` (`routes_memory.go:50`) |
| **Webhooks** | Async execution completion with HMAC-SHA256 signed callbacks |
| **Node packages** | `agentfield-package.yaml` manifest, `af install <path-or-git-url>`, `af run`, `af call`, encrypted secrets store (`~/.agentfield/secrets/*.enc`), `user_environment` injection (`internal/packages/installer.go`, `secrets.go`, `env_resolver.go`) |
| **Sessions** | Realtime offer at `/api/v1/sessions/:session_id/realtime-offer`, session tools, `/session-targets` group (`routes_core.go:161,181`) |
| **Triggers** | GitHub, Slack, Stripe, GenericBearer, GenericHMAC (plus cron, databricks, linear, sentry, snowflake sources) — SSE delivery, replay, public ingest |

### CLI surface (`af`)

~35 commands across the lifecycle:

- **Server/control**: `server`, `dev [path]` (with `--watch`/`-w`, `--port`), `init [project-name]`
- **Nodes**: `install <package-path>`, `run <agent-node-name>`, `uninstall <package-name>`, `stop <agent-node-name>`, `ps`, `list`, `nodes`, `logs <agent-node-name>`, `config <package-name>`, `show-requirements <path-or-git-url>`, `register-serverless --url <invocation-url>`
- **Executions**: `call <node>.<reasoner>`, `exec`, `execution`, `cancel <execution_id>`, `pause <execution_id>`, `resume <execution_id>`, `restart <execution_id>`, `wait <run_id>`, `tail <run_id>`, `batch`, `approve`, `approval-status`
- **Agent JSON mode**: `agent status|discover|search|query|run`, `kb topics|search|read|guide|batch`
- **Sessions**: `session start|offer|tool|workflows`
- **Identity**: `vc verify <vc-file.json>` (plus top-level `verify` alias), `version`
- **Secrets**: `secrets set KEY [VALUE]`, `secrets ls`, `secrets rm KEY` — encrypted store under `~/.agentfield/`
- **Skills**: `skill catalog|install|list|print|uninstall|update|path`
- **Diagnostics**: `doctor`, `harness doctor`, `share [workflow-id]`

**Note:** `af dev` uses `--watch`/`-w` (its only watch flag), and there is **no** key-export CLI subcommand — `vc.go` exposes only `verify`; DID keystore backup is a plain copy of `~/.agentfield/data/keys/`.

### Desktop app (`desktop/`)

Electron app targeting GitHub-comfortable developers. Views: **Dashboard** (usage totals, cold-launch to Home when agents exist), **Agents** (marketplace-style library of installed agents + add), **Activity** (high-volume dense/filterable runs, per-row usage when the API allows), **Install**, **Settings**. macOS autostart via launchd; talks to the control plane through the `af` CLI as its contract (`desktop/src/main/cli.ts`, `autostart.ts`, `env.ts`, `agents.ts`).

## Python SDK deep dive

The Python SDK (`sdk/python/agentfield/`, 54 top-level modules / 68 files including `harness/` and `fixtures/`, ~1.3MB) is the reference SDK. It builds on FastAPI and registers agents with the control plane over HTTP.

### Core building blocks

| Piece | Module | Notes |
|-------|--------|-------|
| `Agent` class | `agent.py` | Central `app` object; per-process `agent_instance_id` (UUID, line 754) powers redeploy detection |
| `@app.reasoner()` | `decorators.py:50` | Registers an AI-judgment function; `path`, `tags`, `description` kwargs; stored in `_reasoner_registry` |
| `@app.skill()` | `decorators.py:125` | Deterministic-code handler in `_skill_registry` |
| `app.ai(schema=...)` | `agent.py:3617` / `types.py:587-704` | Typed LLM output; LiteLLM-backed (100+ models); schema validation via Pydantic; context-length auto-detection from `litellm.get_model_info()` |
| `app.harness(...)` | `harness/` | Dispatches to Claude Code / Codex / Gemini CLI / OpenCode (`harness/providers/_factory.py:9`); knobs: `max_turns`, `max_budget_usd`, `max_retries`, `tools`, `permission_mode`, `system_prompt`, backoff tuning (`_runner.py:160-168`) |
| `app.call(...)` | `agent.py` | Cross-agent call routed through CP (`POST /api/v1/execute/:target`) with tracing |
| `app.discover(...)` | `agent_discovery.py` | `_AgentDiscoveryMixin` — `/discover` metadata exchange at registration, `_apply_discovery_response` |
| `app.pause()/resume()` | `agent_pause.py` | HITL suspension; execution state tracked by CP |
| Sessions | `sessions.py`, `session_transport.py` | Realtime offers, session tool invocation, transport normalization (`NormalizeSessionTransportValue`) |
| Triggers | `triggers.py` | In-SDK trigger registration |
| VC generation | `vc_generator.py`, `agent_vc.py` | Verifiable-credential creation for executions and workflows |
| DID auth | `did_auth.py`, `did_manager.py`, `crypto.py` | Ed25519 signing of requests; key loading from JWK; payload format `timestamp[:nonce]:SHA256(body)` |
| Memory | `memory.py` | KV + vector via REST; scope-aware headers (`X-Workflow-ID`, `X-Session-ID`, `X-Actor-ID`); `similarity_search()` at line 471 |

### Memory scopes

Four scopes, widest to narrowest — narrow scopes override broader ones on read:

| Scope | Header / id | Use |
|-------|-------------|-----|
| `global` | default (`"global"`) | Shared configuration, cross-node constants |
| `actor` | `X-Actor-ID` | Per-actor state (a user, a session actor) |
| `session` | `X-Session-ID` | Per-session state |
| `workflow` | `X-Workflow-ID` | Per-workflow-run state |

Scope resolution lives in `handlers/memory.go:402-418` (`resolveScope`) and is exercised in `handlers/vector_memory_test.go:142,231,280,329`. Vector search is `similarity_search()` (with top-K and filters) — not `.search()`.

### LLM output typing

`app.ai(schema=MyPydanticModel)` produces typed output via LiteLLM:
- 100+ model families through a single interface (OpenAI, Anthropic, Gemini, local via Ollama, etc.)
- Schema-constrained output (structured responses / function-calling shaped to the Pydantic model)
- Per-call cost tracking (`cost_tracker.py`), rate limiting (`rate_limiter.py`), result caching (`result_cache.py`), OpenRouter attribution (`openrouter_attribution.py`)
- Multimodal support (`multimodal.py`, `media_providers.py`, `media_router.py`)
- `agent_ai.py` powers the `app.ai_handler()` façade (`agent.py:928`)

## Embedded MCP server

The control plane ships MCP in-process — no bridge process needed:

- **Endpoint:** `POST <server>/mcp` (default `http://localhost:8080/mcp`)
- **Transport:** streamable HTTP, JSON-RPC 2.0; stateless — `Mcp-Session-Id` / `MCP-Protocol-Version` headers tolerated and ignored
- **Auth:** sits behind the same global auth/trust domain as REST (`X-API-Key` when an API key is configured); permission middleware runs on synthetic requests so MCP calls get identical ACCESS/DENY policy enforcement (`routes_mcp.go:75-101`)
- **Enablement:** on by default; `AGENTFIELD_MCP_ENABLED=false` or `features.mcp.enabled: false` removes the route (404)
- **Tools:** `discover_agents` (with `health:"all"`), `get_reasoner_schema`, `execute_reasoner` (async, returns `run_id`), `get_run`, `wait_run` (server-side poll, capped at 120s)
- **Docs:** `docs/mcp-integration.md` (Claude Code wiring: `claude mcp add --transport http agentfield http://localhost:8080/mcp`)

The older bridge-server reference in `assets/mcp-servers/agentfield-mcp-server.md` remains for wrapping the REST API where the embedded server is disabled.

## Trigger engine

18 endpoints under `/api/v1/triggers` plus a public ingest surface (`routes_triggers.go`):

| Provider | Source dir | Auth |
|----------|-----------|------|
| GitHub | `sources/github` | HMAC-SHA256 webhook verification |
| Slack | `sources/slack` | Slack signing secret |
| Stripe | `sources/stripe` | `stripe-v1` signature (`types/trigger_event_vc.go:26`) |
| GenericBearer | `sources/genericbearer` | Static bearer token per trigger |
| GenericHMAC | `sources/generichmac` | Configurable HMAC |
| Cron | `sources/cron` | Scheduled firing |
| SaaS integrations | `sources/databricks`, `linear`, `sentry`, `snowflake` | Provider-specific |

- Public ingest at `/sources/:trigger_id` (unauthenticated — the provider secret IS the auth)
- Async dispatch via `services/trigger_dispatcher.go`; events stored durably; provider-friendly semantics (4xx = "don't retry", 2xx = acked)
- SSE event delivery + event replay
- Trigger events carry a VC (audited), hence `trigger_event_vc.go`

## Sessions & realtime

- `/api/v1/session-targets` group — declare which reasoners can be offered into a session (`routes_core.go:161`)
- `POST /api/v1/sessions/:session_id/realtime-offer` — push a realtime session offer (`routes_core.go:181`)
- Session tool invocation: `af session tool <session_id> <tool>` and `session workflows <session_id>` from the CLI
- SDK transport normalization across realtime providers (`pkg/types/session_transport.go:15-73`)
- Session state lives in the registry (per-agent), distributed through the CP

## Agentic API, KB, and serverless

- `POST /api/v1/configs/:key` — store runtime config for agents
- `/api/v1/agentic/*` — discover, query, run, agent, batch, status (12 endpoints in `routes_agentic.go`)
- **Knowledge base:** `/api/v1/agentic/kb` — public (unauthenticated) routes: `/topics`, `/articles`, `/articles/:id[/:sub_id]`, `/guide` (`routes_agentic.go:43-49`); CLI surface `af kb topics|search|read|guide|batch`
- **Serverless agents:** `af register-serverless --url <invocation-url>` — agents that don't run the SDK loop; the CP calls the URL directly (`internal/cli/nodes.go:34-42`)

## ARD — Agent Resource Discovery

ARD publishes a machine-readable catalog of every agent node's reasoners (name, schema, tags, endpoints):

- **Default artifact type:** `application/openapi+json` (`internal/ard/ard.go:454,861`)
- `application/mcp-server+json` is a configurable `DefaultType` — an ARD catalog entry can point at an MCP server artifact, but is not the default
- Public discovery (`/ard/discover`-style routes) is unauthenticated so mesh peers can enumerate agents; management routes are authenticated
- Execution (`POST /api/v1/execute/:target`) consults ARD for the target's contract (`routes_core.go:106` `ExecuteHandlerWithARD`)

## Node package system

Installing an agent is a package operation, not a manual setup:

- **Manifest:** `agentfield-package.yaml` — `PackageMetadata` with `config_version` (schema version, distinct from the node's `version:`), start command, dependencies, and `user_environment` declarations (`internal/packages/installer.go:100,124`)
- **Sources:** local path, GitHub URL, or git repo (installer resolves subdirectories, node identity, `go_runtime`/`pyinterp` dependency checks)
- **Secrets:** encrypted store at `~/.agentfield/secrets/` — `secrets/global.enc` (shared) and `secrets/<node>.enc` (node-scoped); generated key on first use; injected into the node environment at launch (`internal/packages/secrets.go:19-20,113`; `env_resolver.go`)
- **Lifecycle:** `af install`, `af run`, `af call`, `af uninstall`, `af stop`, `af ps`, `af logs`
- `show-requirements <path-or-git-url>` inspects a manifest before installing

## Identity & authorization deep dive

### DID IAM

- Every agent node holds a W3C DID; verification method is `Ed25519VerificationKey2020` (`routes_did.go:313`); default method `did:key`, BIP32 derivation (`config.yaml: features.did`)
- Resolution order: `did:web` (database) first, `did:key` (in-memory) fallback (`routes_did.go:277`)
- Request signing: `timestamp[:nonce]:SHA256(body)` payload, 300s timestamp window, base64 signature, signature-replay cache (`did_auth.go:203-263`)
- 10 error codes (see Authentication table) returned as `{error, message, details?}` JSON

### Tag-based policies

- `ACCESS` / `DENY` rules keyed on caller tags → target tags, with `allow_functions` / `deny_functions` glob patterns and constraint predicates (e.g. `amount <= 10000`) (`config.yaml: features.did.authorization.access_policies`)
- Enforced by `PermissionCheckMiddleware` on `/api/v1/execute/*` — infrastructure-level, not prompt-level
- Denied calls trigger permission-request workflows (tag approval), gated by `X-Admin-Token`
- Default-approval mode per tag rule (`default_mode: auto` vs `manual` for sensitive tags)

### Verifiable Credentials

- VC per execution and per workflow; persisted with configurable `storage_mode` (inline), optional input/output hashing (`hash_sensitive_data`)
- Offline verification: `af vc verify audit.json` (or `af verify`) with `--resolve-web` / `--did-resolver` options; signature + workflow-VC verification paths in `cli/vc.go:291,325`
- Key rotation: auto-rotate every 90 days (`config.go:327`); keystore encrypted with AES-256-GCM (`encryption.go`); backups = copy `~/.agentfield/data/keys/`

## gRPC admin surface

- `AdminReasonerService` (protobuf in `pkg/adminpb`) registered on `:8180` (`server.go:712-738`)
- Port = HTTP port + 100 (`server.go:469`), overridable via config
- API-key unary interceptor when `AGENTFIELD_API_KEY` is set (`middleware/grpc_auth.go`)
- Example RPC: `ListReasoners` returns registered reasoners (`server.go:743`)

## Skillkit & bundled skills

- 3 bundled skills under `internal/skillkit/skill_data/`: `agentfield`, `agentfield-personal`, `agentfield-use`
- `agentfield` is the Claude Code / Codex slash-command skill that scaffolds a Docker Compose stack
- CLI: `af skill catalog|install|list|print|uninstall|update|path`

## Integrations & migrations

- `integrations/` — ready-made agent packages: `databricks`, `linear`, `sentry`, `snowflake` (mirrored as trigger sources)
- `control-plane/migrations/` — 38 Goose migrations (`000_migration_runner.sql` → schema bootstrap for did_registry, agent_dids, executions, etc.)
- Auto-migration on startup for PostgreSQL when enabled (`AGENTFIELD_STORAGE_POSTGRES_ENABLE_AUTO_MIGRATION=true`)

## Execution model

- **Sync:** `POST /api/v1/execute/:target` — waits for the agent's response (permission-checked, ARD-aware)
- **Async:** `POST /api/v1/execute/async/:target` — returns immediately; result delivered via webhook (HMAC-SHA256 signed) and/or SSE stream; completion dispatched through the in-process `completionQueue` channel (`execute.go:174`, `server.go:414` `QueueSize: 1000`)
- **Streaming:** `GET /api/v1/executions/:execution_id/events` (SSE) — execution progress events as the DAG advances
- **Workflow DAGs:** parent executions spawn child executions; `POST /api/v1/workflows/:workflowId/cancel-tree` cancels a whole subtree (`routes_core.go:134`)
- **HITL:** `pause` → `request-approval` (execution-scoped and agent-scoped variants) → `approval-status` poll → `resume` or `approval-response`; CP only manages state — agents handle external approval-service communication directly (`routes_core.go:136-154`)
- **Cancellation:** CP dispatches a cancel callback to the worker over `Authorization: Bearer <internal-token>` (`cancel_dispatcher.go:213`); workers with `RequireOriginAuth` accept it
- **Restart:** `POST /api/v1/executions/:execution_id/restart` re-runs a finished execution with the same payload
- **Traffic weight:** `PUT /api/v1/connector/reasoners/:id/versions/:version/weight` shifts `traffic_weight` across reasoner versions (`connector/handlers.go:72,447-454`) — canary/blue-green without redeploys
- **Redeploy detection:** each agent process carries a unique `agent_instance_id` (`agent.py:754`); a new UUID means the node was redeployed, invalidating stale leases

## Storage

| Backend | Vector support | Use |
|---------|---------------|-----|
| **SQLite + BoltDB** | Embedded | Local dev (`AGENTFIELD_STORAGE_MODE=local`), no external dependencies |
| **PostgreSQL 15+** | pgvector (`pkg/types/vector_store_postgres.go`) | Production; auto-migration via Goose |
| **Connector** | n/a | Air-gapped deployments, token-authenticated |

Memory (KV + vector), executions, DID registry, triggers, knowledge, and secrets all persist through the storage provider interface (`internal/storage/`). There is no external queue dependency — async buffering is in-process.

## Configuration reference

`control-plane/config/agentfield.yaml` is the canonical file; every key is overridable by a `AGENTFIELD_*` environment variable (Viper, `cmd/af/main.go:226-277`), with env vars taking precedence. The docs (`docs/ENVIRONMENT_VARIABLES.md`) enumerate the 43 documented variables. Key surfaces:

| Area | Config key | Env var |
|------|-----------|---------|
| Server | `server.port` / `ui.enabled` | `AGENTFIELD_PORT`, `AGENTFIELD_UI_ENABLED` |
| Storage | `storage.mode` / postgres URL | `AGENTFIELD_STORAGE_MODE`, `AGENTFIELD_STORAGE_POSTGRES_*` |
| API auth | `api.auth.api_key` | `AGENTFIELD_API_KEY` |
| DID IAM | `features.did.*` (method, key_algorithm, key_rotation_days, keystore, authorization) | `AGENTFIELD_DID_*` |
| Authorization | `features.did.authorization` (admin_token, internal_token, timestamp_window_seconds, access_policies) | `AGENTFIELD_AUTHORIZATION_*` |
| MCP | `features.mcp.enabled` (default true) | `AGENTFIELD_MCP_ENABLED` |
| Connector | `features.connector.{enabled,token,capabilities}` | `AGENTFIELD_CONNECTOR_*` |
| Execution | `agentfield.execution_queue.{queue_size, agent_call_timeout}` | `AGENTFIELD_EXECUTION_*` |
| ARD | `agentfield.ard.publish.default_type` (default `application/openapi+json`) | `AGENTFIELD_ARD_*` |
| Tracing | `features.tracing.{enabled,exporter,endpoint}` (OpenTelemetry OTLP) | `AGENTFIELD_TRACING_*` |

Config file resolution order: `$AGENTFIELD_CONFIG_FILE` → `~/.agentfield/agentfield.yaml` → `<exec-dir>/config/agentfield.yaml` → `./config/agentfield.yaml` → `.` (Viper `AddConfigPath` order in `main.go:249-256`).

## Getting started

```python
# agent.py — a single-file AgentField node
from agentfield import AgentField
from pydantic import BaseModel

app = AgentField("my-agent")

class Summary(BaseModel):
    headline: str
    score: float

@app.reasoner(tags=["nlp"])
async def summarize(text: str) -> Summary:
    return await app.ai(f"Summarize: {text}", schema=Summary)

@app.skill()
async def ping() -> str:
    return "pong"
```

```bash
af init my-project && cd my-project   # scaffold a node package
af dev --watch .                       # run with auto-restart
af call my-agent.summarize '{"text": "hello world"}'   # sync call
af ps                                  # list registered nodes
af vc verify audit.json                # verify the execution receipt
```

Run `af` with no subcommand to start the control-plane server (`af server`), then install this package on another machine with `af install <path-or-git-url>` — the CP discovers the node, publishes its ARD catalog, and `POST /api/v1/execute/my-agent.summarize` becomes callable (also via MCP `execute_reasoner`).

## Web UI

Embedded React client (`control-plane/web/client/`, Vite + Tailwind + Radix) served by the CP:

- **API v1** (`/api/ui/v1`): agents, nodes, executions, workflows, reasoners, dashboard, DID, VC, authorization; plus `/api/ui/v1/queue/status` and `/api/ui/v1/llm/health` operational endpoints (`routes_ui.go:199-200`)
- **API v2** (`/api/ui/v2`): workflow-runs list/detail + golden-run save (`routes_ui.go:281-286`)
- Static assets mounted via `registerUIStatic`; the UI is a lightweight convenience layer — the CLI and REST API are the full-power surface

## Observability & monitoring

| Surface | Endpoint | Notes |
|---------|----------|-------|
| Prometheus metrics | `GET /metrics` (root, `routes_core.go:21`) | promhttp handler, unauthenticated |
| Health probe | `GET /health` (root, `routes_core.go:22`) | load-balancer ready check |
| Queue status | `GET /api/ui/v1/queue/status` | in-process execution queue depth |
| LLM health | `GET /api/ui/v1/llm/health` | upstream model reachability |
| Execution timeline | SSE on execution events | per-execution event stream |
| Tracing | OpenTelemetry OTLP export (`features.tracing`) | `otlp-http`/`otlp-grpc`, optional |
| Logs | Structured JSON (zerolog) | `af logs <node>` tails node output |

Per-run cost and usage accounting flows from the SDK (`cost_tracker.py`, `usage.go`) into the UI/desktop surfaces.

## Deployment

| Mode | Requirements | Config |
|------|-------------|--------|
| **Local dev** | `af server` or `af dev` — SQLite + BoltDB, no external dependencies | `AGENTFIELD_STORAGE_MODE=local` |
| **Docker Compose** | `deployments/docker/docker-compose.yml` — pgvector/pg16 + control plane + demo agents | Env vars in compose file |
| **Helm** | `deployments/helm/agentfield/` — Kubernetes with full values.yaml | 30+ configurable params |
| **Quadlet (rootless)** | `assets/deployment/agentfield-quadlet.md` — PostgreSQL `.container` + `.volume` + `.network` units | `EnvironmentFile=` for secrets |
| **Production (cloud)** | PostgreSQL 15+, auto-migration with Goose (38 migrations in `control-plane/migrations/`) | `AGENTFIELD_STORAGE_POSTGRES_ENABLE_AUTO_MIGRATION=true` |
| **Air-gapped** | Outbound WebSocket only via Connector API — a token-authenticated REST surface, not a separate service | `AGENTFIELD_AUTHORIZATION_CONNECTOR_TOKEN=` / `features.connector.{enabled,token,capabilities}` |

Config via `control-plane/config/agentfield.yaml` (features: `did`, `tracing`, `connector`, …) or 43 `AGENTFIELD_*` environment variables — env vars take precedence (`cmd/af/main.go:226-277` Viper). `features.mcp.enabled` / `AGENTFIELD_MCP_ENABLED` toggles the embedded MCP server (default on).

### Production Operations

| Operation | Detail |
|-----------|--------|
| **Scaling** | Horizontal (stateless CP), no shared state coordination needed |
| **DID key rotation** | Auto-rotation every 90 days (`config.go:327`), AES-256-GCM encrypted keystore (`encryption.go`), backup = copy `~/.agentfield/data/keys/` (no export CLI) |
| **Agent updates** | Traffic weight routing (`PUT /connector/reasoners/:id/versions/:version/weight`), A/B testing, blue-green. `agent_instance_id` (per-process UUID, `agent.py:754`) detects redeploy |
| **Monitoring** | `/metrics` (Prometheus) + `/health` at root (`routes_core.go:21-22`); `/api/ui/v1/queue/status`, `/api/ui/v1/llm/health` (`routes_ui.go:199-200`), `/dashboard/*` |
| **Backup** | PostgreSQL: `pg_dump`, SQLite: `cp`. DID keys backed up separately (copy keystore dir) |
| **Troubleshooting** | 11 common scenarios documented in `domains/deployment/agentfield-deployment.md` |

## Related

| Repo | What it adds |
|------|-------------|
| [[sec-af]] | AI-native security auditor — adversarial multi-reasoner DAG |
| [[af-deep-research]] | Deep research engine — recursive agent spawning |
| [[af-reactive-atlas-mongodb]] | Reactive MongoDB intelligence layer |
| [[SWE-AF]] | Autonomous engineering team — factory-scale agent orchestration |

## Compatibility

| System | Integration path | Status |
|--------|-----------------|--------|
| [[hermes-agent]] | AgentField ships an embedded MCP server (`POST /mcp`, 5 tools) — Hermes can register it as an MCP endpoint directly, or use the bridge server in `assets/mcp-servers/agentfield-mcp-server.md`. AgentField `app.harness()` could dispatch to Hermes for LLM execution | Pattern documented |
| [[openclaw]] | MCP bridge runs alongside OpenClaw gateway. OpenClaw's rate limiting + circuit breaking add layer on top of AgentField DID identity | Pattern documented |
| [[n8n]] | Complementary: n8n handles deterministic workflows and 400+ integrations; AgentField handles AI decision orchestration and IAM. Bridge: n8n webhook → AgentField REST API; AgentField agent → n8n workflow via webhook | Complementary |
| [[mission-control]] | Mission Control connects via generic REST adapter. AgentField API exposes `/api/v1/nodes`, `/api/v1/executions`, `/api/v1/workflows` that Mission Control panels consume | ⚠️ Needs verification |

## Fork Considerations

| Factor | Assessment |
|---------|-----------|
| **License** | Apache 2.0 — permissive |
| **Size** | Moderate (Go + Python + TS + React + Electron) |
| **Activity** | Active development (`0.1.118-rc.3`), corporate backing |
| **Unique value** | IAM for agents (DID/VC), embedded MCP server, harness orchestration, cross-agent mesh, traffic-weighted canaries, node package system |
| **Fork cost** | Moderate — Go monorepo with 3 SDKs + desktop app |

## Related

- [[agentfield-architecture]] -- system architecture
- [[agentfield-api]] -- REST API reference
- [[agentfield-deployment]] -- deployment guide
- [[agentfield-quadlet]] -- Quadlet deployment
- [[agentfield-mcp-server]] -- MCP bridge server
- [[hermes-profiles]] -- AgentField platform profile
- [[agentfield.codegraph-verify]] -- codegraph verification
- [[hermes-profiles]] -- SWE-AF profile
- [[hermes-profiles]] -- SEC-AF profile
- [[hermes-profiles]] -- Deep Research profile
- [[hermes-profiles]] -- Reactive MongoDB profile

## Cross-project

- [[hermes-agent]] — Agent platform with MCP bridge to AgentField
- [[openclaw]] — Agent platform with MCP bridge to AgentField
- [[mission-control]] — Dashboard that can consume AgentField REST API
- [[podman]] — Container runtime for AgentField deployment
- [[n8n]] — Complementary workflow engine for AI orchestration
- [[buildah]] — Image builder in AgentField CI/CD pipeline
- [[nix-podman-stacks]] — Declarative container management for AgentField
- [[gogs]] — Self-hosted Git service for agent workflow repos
- [[sablier]] — Scale-to-zero for AgentField services
- [[tank-os]] — Bootc OS for AgentField deployment
