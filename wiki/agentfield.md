---
name: agentfield
tags: [agentfield, wiki, golang, control-plane, identity, orchestration, harness]
---

# AgentField

| Field | Value |
|---|---|
| **Origin** | [Agent-Field/agentfield](https://github.com/Agent-Field/agentfield) |
| **License** | Apache 2.0 |
| **Stack** | Go (control plane) + Python/Go/TypeScript SDKs + React UI |
| **Source** | `sources/agentfield/` |
| **CLAUDE.md** | `sources/agentfield/CLAUDE.md` |
| **Profile** | `assets/agent-profiles/agentfield-profile.md` |
| **API** | `domains/api/agentfield-api.md` — REST surface, 5-layer auth, DID IAM, SDK-generated APIs |
| **Deployment** | `domains/deployment/agentfield-deployment.md` — Docker Compose, Helm, production ops |
| **Quadlet** | `assets/deployment/agentfield-quadlet.md` — rootless Podman Quadlet units |
| **MCP** | `assets/mcp-servers/agentfield-mcp-server.md` — bridge server implementation |
| **Wanted** | AgentField is an **AI backend control plane** — deploy, observe, and prove AI agents in production |

## What it is

AgentField turns agent logic into production infrastructure. You write agent code in Python, Go, or TypeScript — AgentField turns it into REST endpoints with routing, coordination, memory, async execution, and cryptographic audit trails.

**Position vs alternatives:** AgentField positions itself as the control plane layer *under* agent frameworks (LangChain, CrewAI) and alongside workflow engines (n8n, Temporal). Key differentiator: IAM for agents (DID/VC identity), harness orchestration for coding agents, and cross-agent mesh with discovery.

## Key Features

### Build
- **Reasoners & Skills**: `@app.reasoner()` for AI judgment, `@app.skill()` for deterministic code
- **Structured output**: `app.ai(schema=MyModel)` → typed Pydantic/Zod output from any LLM (100+ via LiteLLM)
- **Harness orchestration**: `app.harness("Fix the bug")` dispatches multi-turn tasks to Claude Code, Codex, Gemini CLI, or OpenCode — with schema-constrained output, cost capping, tool access control
- **Cross-agent calls**: `app.call("other-agent.func")` routes through control plane with full tracing
- **Service discovery**: `app.discover(tags=["ml*"])` finds agents across the mesh; `tools="discover"` lets LLMs auto-invoke
- **Memory**: `app.memory.set()` / `.get()` / `.search()` — KV + vector search, 4 scopes (global, agent, session, run), no external dependencies

### Run
- **Sync/async execution**: REST endpoints for sync, fire-and-forget with webhooks/SSE for async
- **HITL**: `app.pause()` suspends for human approval — crash-safe, durable, audited
- **Canary deployments**: Traffic weight routing (5% → 50% → 100%), A/B testing, blue-green
- **Observability**: Automatic workflow DAGs, Prometheus metrics, structured logging, execution timeline
- **Durable queue**: PostgreSQL-backed with atomic lease-based processing

### Govern
- **Cryptographic identity**: Every agent gets a W3C DID (Ed25519 keys) — agents authenticate like services do with mTLS
- **Verifiable Credentials**: Tamper-proof receipt per execution — offline-verifiable via `af vc verify audit.json`
- **Policy enforcement**: Tag-based ACCESS/DENY rules, enforced by infrastructure, not prompts
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
  - REST API (60+ endpoints in 14 route groups under /api/v1/)
  - Execution engine (sync + async + SSE streaming)
  - Identity & policy (5-layer auth: API Key, DID, Admin Token, Internal Token, Connector Token)
  - Memory service (KV + vector, 4 scopes)
  - Event bus (SSE + WebSocket)
  - Web UI (embedded React, two API versions: /api/ui/v1 and /api/ui/v2)

Storage: PostgreSQL 15+ (production) or SQLite + BoltDB (local dev)
No external queue needed — state in SQLite or PostgreSQL
```

### Route Groups (from source)

| # | Route file | Endpoints |
|---|-----------|-----------|
| 1 | `routes_core.go` | Agent registration, execution (sync/async/stream), node management, session targets, health |
| 2 | `routes_did.go` | DID document resolution, VC issuance, policy distribution, revocation, issuer public key |
| 3 | `routes_memory.go` | KV memory CRUD, vector memory search, memory events (SSE + WebSocket) |
| 4 | `routes_admin.go` | Admin endpoints gated by AdminTokenAuth — tag approval, access policy management |
| 5 | `routes_agentic.go` | Agentic API: discover, query, run, agent, batch, status. Public KB routes (no auth) |
| 6 | `routes_triggers.go` | Public ingest at `/sources/:trigger_id` (unauthenticated), authenticated trigger CRUD |
| 7 | `routes_ui.go` | Browser-facing API v1 + v2: agents, nodes, executions, workflows, reasoners, dashboard, DID, VC |
| 8 | `routes_connector.go` | Connector API for air-gapped deployments |
| 9 | `routes_knowledge.go` | Knowledge store CRUD and search |
| 10 | `routes_observability.go` | Observability webhook settings |
| 11 | `routes_ard.go` | ARD (Agent Resource Discovery) public + authenticated routes |
| 12 | `routes_middleware.go` | Middleware composition |
| 13 | `routes_swagger.go` | Swagger/OpenAPI docs |
| 14-15 | SSE + UI static file routes | `/api/v1/events` SSE streaming, embedded React UI static files |

### Authentication (5-Layer, from source)

| Layer | Header/Mechanism | Purpose |
|-------|-----------------|---------|
| API Key | `X-API-Key` | Simple key auth for agents and clients |
| DID (decentralized) | `X-Caller-DID` + `X-DID-Signature` + `X-DID-Timestamp` + `X-DID-Nonce` | Ed25519-signed requests, 300s timestamp window, antireplay nonce |
| Admin Token | `X-Admin-Token` | Protects admin endpoints (access policies, tag approval) |
| Internal Token | `X-Internal-Token` | CP-to-agent internal request auth |
| Connector Token | `X-Connector-Token` | Air-gapped connector auth |

DID auth error codes: `did_auth_required`, `signature_required`, `signature_invalid`, `did_revoked`, `did_not_registered`, `policy_denied`.

### Key packages

| Package | Role |
|---------|------|
| `control-plane/cmd/af/` | Unified CLI (`af init`, `af server`, `af dev`, `af vc`) |
| `control-plane/cmd/agentfield-server/` | Standalone server |
| `control-plane/internal/server/` | HTTP server setup (Gin), 15 route files (`routes_*.go`) |
| `control-plane/internal/handlers/` | REST/gRPC handlers (per-domain subdirectories) |
| `control-plane/internal/services/` | Business logic (execution, registry, memory, identity, skillkit) |
| `control-plane/internal/storage/` | Multi-backend storage (SQLite + BoltDB, PostgreSQL, connector) |
| `control-plane/internal/events/` | Event bus + SSE streaming |
| `control-plane/internal/core/` | Domain models (agent, execution, session, workflow, memory) |
| `control-plane/internal/config/` | Configuration (Viper, structs: AgentFieldConfig, DIDConfig, etc.) |
| `control-plane/internal/encryption/` | DID/VC primitives (Ed25519, AES-256-GCM) |
| `control-plane/internal/application/` | Application service orchestration |
| `control-plane/internal/infrastructure/` | DB connection pooling, source plugins |
| `control-plane/internal/logger/` | Structured logging (zerolog) |
| `control-plane/internal/sources/` | Plugin source interface |
| `control-plane/internal/skillkit/` | Skill installation system |
| `control-plane/web/client/` | React admin UI (Vite + Tailwind + Radix) |
| `sdk/python/agentfield/` | Python SDK (FastAPI-based, 65 modules) |
| `sdk/go/` | Go SDK (agent builder, HTTP client, types) |

## Interfaces

| Interface | Details |
|-----------|---------|
| **REST API** | 60+ endpoints in 14 route groups under `/api/v1/` — execute (sync/async/stream), nodes, memory, DID/VC, admin, agentic, triggers, connectors, knowledge, observability, ARD, UI. Full spec in `domains/api/agentfield-api.md` |
| **CLI** | `af init`, `af server`, `af dev`, `af dev --hot-reload`, `af vc` (verify credentials) |
| **MCP** | **Removed from codebase in PR #359.** Bridge server in `assets/mcp-servers/agentfield-mcp-server.md` wraps REST API as MCP tools. ARD catalog retains `application/mcp-server+json` as artifact type for discovery |
| **/agentfield** | Claude Code / Codex slash command (skillkit) — prompts scaffold a full Docker Compose stack |
| **SDKs** | Python (FastAPI-based, 65 modules, 831KB), Go (agent builder + HTTP client), TypeScript |
| **SSE** | `/api/v1/events` for execution progress, `/api/v1/memory/events` for memory change notifications |
| **WebSocket** | Memory events at `/api/v1/memory/events/ws` |
| **Webhooks** | Async execution completion with HMAC-SHA256 signed callbacks |

## Deployment

| Mode | Requirements | Config |
|------|-------------|--------|
| **Local dev** | `af server` or `af dev` — SQLite + BoltDB, no external dependencies | `AGENTFIELD_STORAGE_MODE=local` |
| **Docker Compose** | `deployments/docker/docker-compose.yml` — pgvector/pg16 + control plane + demo agents | Env vars in compose file |
| **Helm** | `deployments/helm/agentfield/` — Kubernetes with full values.yaml | 30+ configurable params |
| **Quadlet (rootless)** | `assets/deployment/agentfield-quadlet.md` — PostgreSQL `.container` + `.volume` + `.network` units | `EnvironmentFile=` for secrets |
| **Production (cloud)** | PostgreSQL 15+, auto-migration with Goose | `AGENTFIELD_STORAGE_POSTGRES_ENABLE_AUTO_MIGRATION=true` |
| **Air-gapped** | Outbound WebSocket only via Connector API | `AGENTFIELD_AUTHORIZATION_CONNECTOR_TOKEN=` |

Config via `config/agentfield.yaml` or environment variables (env vars take precedence).

### Production Operations

| Operation | Detail |
|-----------|--------|
| **Scaling** | Horizontal (stateless CP), no shared state coordination needed |
| **DID key rotation** | Auto-rotation every 90 days, AES-256-GCM encrypted storage, backup via `af vc export-keys` |
| **Agent updates** | Canary traffic weight routing (5%→50%→100%), A/B testing, blue-green. `agent_instance_id` (per-process UUID) detects redeploy |
| **Monitoring** | `/metrics` (Prometheus), `/health` (JSON), `/queue/status`, `/llm/health`, `/dashboard/*` |
| **Backup** | PostgreSQL: `pg_dump`, SQLite: `cp`. DID keys backed up separately |
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
| [[hermes-agent]] | MCP bridge server wraps AgentField REST API as Hermes MCP tools. Hermes MCP config loads `agentfield_mcp_server.py`. AgentField `app.harness()` could dispatch to Hermes for LLM execution | Pattern documented in `assets/mcp-servers/agentfield-mcp-server.md` |
| [[openclaw]] | MCP bridge runs alongside OpenClaw gateway. OpenClaw's rate limiting + circuit breaking add layer on top of AgentField DID identity | Pattern documented |
| [[n8n]] | Complementary: n8n handles deterministic workflows and 400+ integrations; AgentField handles AI decision orchestration and IAM. Bridge: n8n webhook → AgentField REST API; AgentField agent → n8n workflow via webhook | Complementary |
| [[mission-control]] | Mission Control connects via generic REST adapter. AgentField API exposes `/api/v1/nodes`, `/api/v1/executions`, `/api/v1/workflows` that Mission Control panels consume | ⚠️ Needs verification |

## Fork Considerations

| Factor | Assessment |
|---------|-----------|
| **License** | Apache 2.0 — permissive |
| **Size** | Moderate (Go + Python + TS + React) |
| **Activity** | Active development, corporate backing? |
| **Unique value** | IAM for agents (DID/VC), harness orchestration, cross-agent mesh, canary deployments |
| **Fork cost** | Moderate — Go monorepo with 3 SDKs |

## Related

- [[agentfield-architecture]] -- system architecture
- [[agentfield-api]] -- REST API reference
- [[agentfield-deployment]] -- deployment guide
- [[agentfield-quadlet]] -- Quadlet deployment
- [[agentfield-mcp-server]] -- MCP bridge server
- [[agentfield-profile]] -- AgentField platform profile
- [[agentfield.codegraph-verify]] -- codegraph verification
- [[swe-af-profile]] -- SWE-AF profile
- [[sec-af-profile]] -- SEC-AF profile
- [[af-deep-research-profile]] -- Deep Research profile
- [[af-reactive-atlas-mongodb-profile]] -- Reactive MongoDB profile

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
