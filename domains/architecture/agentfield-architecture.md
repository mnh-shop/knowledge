---
name: agentfield-architecture
tags: [agentfield, architecture, cli, control-plane, docker, golang, harness, identity, orchestration, plugin-sdk, quadlet, security, storage, systemd, virtualization]
description: "AgentField architecture: AI control plane with micro-VM sandboxing, identity management, and pipeline orchestration"
source: sources/agentfield/
---

# AgentField: AI Control Plane Architecture
**Source:** `sources/agentfield/`

**Status:** Active research target  
**License:** Apache 2.0  
**Repository:** github.com/agent-field/agentfield  
**SDK Languages:** Python (primary), Go, TypeScript  
**Control Plane:** Go (Gin framework)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Three-Tier Architecture](#2-three-tier-architecture)
3. [SDK Decorator Pattern](#3-sdk-decorator-pattern)
4. [Cross-Agent Mesh](#4-cross-agent-mesh)
5. [Harness Orchestration](#5-harness-orchestration)
6. [Identity and IAM (DID/VC)](#6-identity-and-iam-didvc)
7. [Memory System](#7-memory-system)
8. [Deployment Architecture](#8-deployment-architecture)
9. [Key Source Files](#9-key-source-files)

---

## 1. Architecture Overview

AgentField is an open-source AI control plane for building and operating production-grade multi-agent systems. The project provides infrastructure that makes agents callable as REST APIs with routing, async execution, memory, cryptographic identity, tag-based IAM, harness orchestration, and observability.

It competes with frameworks like LangChain on the "what runs it" axis rather than the "how you write it" axis -- AgentField cares about execution, orchestration, and governance, not agent implementation patterns.

**Key differentiators:**
- Every agent execution is a REST POST endpoint with cryptographic provenance
- Cross-agent calls route through the control plane (never direct agent-to-agent HTTP)
- W3C DID + Verifiable Credential identity for every agent, reasoner, and execution
- Harness system treats LLM CLI tools (Claude Code, Codex, Gemini, OpenCode) as autonomous computational units
- Stateless horizontally-scalable Go backend with agents connecting from anywhere

---

## 2. Three-Tier Architecture

```
+--------------------------------------------------------------+
|                    Tier 3: Web UI                             |
|         React/TypeScript embedded in Go binary               |
|        Monitoring, workflow DAGs, audit trails, IAM          |
+--------------------------------------------------------------+
                            |
                            v
+--------------------------------------------------------------+
|                 Tier 1: Control Plane (Go)                    |
|    Central orchestration, execution, governance layer         |
|    - Gin HTTP server on :8080                                |
|    - Execution queue (goroutine worker pool, 16 workers)     |
|    - DID services (keystore, registry, VC chain)              |
|    - Tag-based IAM (PDP)                                     |
|    - Workflow DAG engine                                     |
|    - Webhook/trigger dispatchers                             |
|    - OpenTelemetry tracing, Prometheus metrics               |
|    - gRPC admin server on :8180                              |
+--------------------------------------------------------------+
          |                    |                    |
          v                    v                    v
+------------------+ +------------------+ +------------------+
|    Tier 2:       | |    Tier 2:       | |    Tier 2:       |
|   Python SDK     | |     Go SDK       | |  TypeScript SDK  |
|   65 modules     | |   Mirror API     | |   Browser/Node   |
|  FastAPI-based   | |   Native Go      | |   Agents         |
+------------------+ +------------------+ +------------------+
```

### Tier 1: Control Plane

Single Go binary (`cmd/af`) that runs as:
- `af server` -- production daemon mode
- `af dev` -- local development mode with hot-reload and SQLite
- `af init <name>` -- scaffold new agent projects

The control plane is **stateless for horizontal scaling** -- add more replicas backed by the same PostgreSQL.

### Tier 2: SDKs

Three SDKs implement the agent runtime:
- **Python SDK** (65 modules, most mature) -- agents are FastAPI subclasses
- **Go SDK** -- native Go agents using the same architectural patterns
- **TypeScript SDK** -- browser and Node.js agents

All SDKs implement the same core primitives: reasoners, skills, sessions, memory, DID identity, harness dispatch, and call routing.

### Tier 3: Web UI

React/TypeScript UI embedded in the Go binary via Go's `embed` package:
- Workflow DAG visualization
- Agent management dashboard
- Execution audit trail viewer
- Tag and policy management for IAM

---

## 3. SDK Decorator Pattern

The Python SDK uses decorators as its primary developer surface, compiling to REST endpoints on a FastAPI subclass.

### Core Decorators

```python
app = agentfield.Agent("my-agent")

@app.reasoner()        # Register a reasoning function as an API endpoint
@app.skill()           # Register a deterministic skill as an API endpoint
@app.session()         # Register a multi-turn session handler
@app.on_change()       # Reactive memory event listener
```

### How `@app.reasoner()` Works

1. Wraps the user function in a `tracked_func` that integrates with the workflow handler
2. Generates type-hint-driven JSON schemas on demand (avoids expensive Pydantic model creation per handler -- saves ~1.5-2 KB per handler)
3. Creates FastAPI `@post(endpoint_path)` routes
4. Stores input type tuples `(type, default)` for lightweight runtime validation via `_validate_handler_input()`
5. Auto-exposes every reasoner as a REST POST endpoint at `/reasoners/{id}` and `/api/v1/execute/{agent}.{id}`

### The `app.ai()` Method

Provides structured LLM calling using LiteLLM for multi-provider support (Anthropic, OpenAI, Google, etc.):
- `schema=MyPydanticModel` returns typed Pydantic instances
- Supports streaming, multimodal inputs, and tool use via `tools="discover"`

### Additional SDK Methods

- `app.note()` -- Add execution audit notes
- `app.pause()` -- Human-in-the-loop approval gate
- `app.discover()` -- Query agent/reasoner capabilities across the mesh
- `app.call("node_id.reasoner_name", input={...})` -- Cross-agent call routing

### TypeScript SDK Equivalent

```typescript
const agent = new Agent({ name: "my-agent" });
agent.reasoner({ id: "analyze" }, async (input: { text: string }) => {
  const result = await agent.ai(input.text, { provider: "anthropic" });
  return result;
});
```

### Go SDK Equivalent

```go
agent := agent.NewAgent("my-agent")
agent.Reasoner("analyze", func(ctx context.Context, input AnalyzeInput) (*AnalyzeOutput, error) {
    result, err := agent.AI(ctx, input.Text, agent.WithProvider("claude"))
    return result, err
})
```

---

## 4. Cross-Agent Mesh

### Call Routing

`app.call("node_id.reasoner_name", input={...})` routes all cross-agent calls **through the control plane** (never direct agent-to-agent HTTP), ensuring every edge is recorded for:
- Workflow DAGs
- Cryptographic provenance chains (VC chain per execution)
- Live observability (OpenTelemetry spans)

### Execution Flow

```
Agent A                    Control Plane                  Agent B
   |                            |                            |
   |--- app.call("B.fn") ------>|                            |
   |                            |--- POST /execute/B.fn ---->|
   |                            |<--- result ----------------|
   |<--- result ----------------|                            |
```

### Key Design Decisions

- **No local shortcut**: `app.call()` has no synchronous shortcut even for same-process target functions. All calls go through the control plane's execution gateway at `POST /api/v1/execute/{target}`.
- **Async execution**: `is_async` mode fires a POST to the async execute endpoint, then polls `GET /api/v1/executions/{id}` in a wait loop.
- **Pause propagation**: Cross-reasoner pause propagation propagates WAITING status up the call tree via `notify_awaiter_status()` -- without this, 3+-deep pause chains would time out at wallclock.
- **Session restoration**: `resume_session_id` supports multi-turn harness sessions across service restarts.
- **Instance tracking**: Agent instances carry an `agent_instance_id` (per-process UUID) so the control plane can detect mid-flight redeploys and fail in-flight executions from previous OS processes.

### Discovery

`app.discover()` queries `GET /api/v1/discovery/capabilities` with tag/name/health filters to find agents and their reasoners/skills across the mesh, returning `AgentCapability` and `ReasonerCapability` objects.

---

## 5. Harness Orchestration

The harness system treats LLM CLI tools as autonomous computational units. `app.harness(prompt, provider=...)` dispatches multi-turn tasks to external coding-agent CLIs.

### Supported Providers (4 current)

| Provider | Mechanism | Lazy Import | 
|----------|-----------|-------------|
| `claude-code` | `claude_agent_sdk` Python package | Yes |
| `codex` | `codex exec --json` subprocess | No |
| `gemini` | `gemini -p` subprocess | No |
| `opencode` | `opencode run --format json` subprocess | No |

### Harness Architecture

```python
class HarnessProvider:
    async def execute(self, prompt: str, options: dict) -> RawResult:
        """Base class for harness providers. Located in
        harness/providers/_base.py."""

class HarnessRunner:
    """Wraps all providers with a common pipeline."""
    - Transient error detection + exponential backoff (±25% jitter, 3 retries)
    - Schema validation retry loop (2 retries for output JSON compliance)
    - Cost capping (max_budget_usd)
    - Turn limiting (max_turns)
    - Tool access control
    - System prompt injection
```

### Output Recovery Pipeline (3 layers)

1. **`_ai_schema_repair()`** -- Cheap LLM call (90s timeout) that reformats malformed JSON output into valid schema before doing the expensive full rerun
2. **Schema validation retry** -- Retry with diagnostic followup prompt if `_ai_schema_repair` fails
3. **Full harness re-run** -- Complete re-execution if both repair and retry fail

### Adding New Providers

1. Create `harness/providers/mytool.py` with a class implementing `async def execute(prompt, options) -> RawResult`
2. Add the name to `SUPPORTED_PROVIDERS` in `_factory.py`
3. Add an import + branch in `build_provider()`

The Go SDK mirrors this architecture via `harness.NewRunner()` and `agent.Harness()`.

---

## 6. Identity and IAM (DID/VC)

AgentField implements a complete W3C DID + Verifiable Credential identity system.

### DID Hierarchy

```
Platform DID (auto-generated)
  |-- Node DID (per agent node)
       |-- Function DID (per reasoner/skill)
```

### DID Types

- **`did:web`** (primary) -- Supports revocation. Hosted at resolution URLs by the control plane.
- **`did:key`** (fallback) -- Self-contained but non-revocable.

### Cryptographic Stack

- Algorithm: Ed25519
- Key derivation: BIP32
- Keystore encryption: AES-256-GCM at rest
- Auto-registration: `POST /api/v1/did/register` returns a `DIDIdentityPackage` with per-component keys

### Authentication Flow (Cross-Agent Calls)

Every cross-agent call carries DID auth headers:
- `X-Caller-DID` -- The caller's DID
- `X-DID-Signature` -- Ed25519 signature over `{timestamp}:{SHA256(body)}`
- `X-DID-Timestamp` -- Signing timestamp

### Replay Protection

In-memory signature cache with TTL equal to the timestamp window (default 300s).

### Permission Model (Two-Step)

**Step 1: Tag Approval**
- Agents propose tags at registration
- Control plane evaluates against configured rules (auto/manual/forbidden)
- Admin approves/rejects via API

**Step 2: Policy Evaluation**
- Tag-based access policies with function-level allow/deny lists
- Parameter constraints on allowed values
- Priority-based first-match-wins evaluation

### VC Hierarchy (3-Tier)

```
Platform VC (highest level governance)
  |-- Node VC (per-agent policies)
       |-- Function VC (per-reasoner/skill permissions)
```

All tags are:
- Normalized (lowercased, deduplicated)
- Travel as `AgentTagVC` -- signed Ed25519 W3C Verifiable Credentials
- Decentralized verification: SDKs cache policies, revocation lists, and admin public keys locally (5-min refresh)

### Default Deny

Fail-closed by default:
- No matching policy = deny (with optional `DefaultDeny` config)
- Expired/revoked VCs block calls
- `pending_approval` agents return 503

---

## 7. Memory System

AgentField provides cross-agent memory with 4 scopes:

| Scope | Visibility | Lifetime | Use Case |
|-------|-----------|----------|----------|
| `global` | All agents | Forever | Shared knowledge base |
| `session` | Within a session | Session duration | Conversation context |
| `actor` | Specific agent | Agent lifetime | Agent-specific state |
| `workflow` | Within a workflow | Workflow duration | Execution context |

### Memory Operations

- KV store per scope
- Vector search (cosine distance, pgvector or BoltDB)
- Event-based subscriptions via `@app.on_change()`
- Reactive listeners fire when memory is written in watched keys

### Memory Endpoints

- `POST /api/v1/executions/note` -- Add execution audit notes
- All memory operations go through the control plane (not agent-local)

---

## 8. Deployment Architecture

### Local Mode (`af dev` / `af server`)

```
+------------------------------------------+
|  Single Go Process                        |
|  +-----------+  +-----------+             |
|  | SQLite    |  | BoltDB    |             |
|  | (relational)|  | (KV store) |           |
|  +-----------+  +-----------+             |
|  +------------------------------------+   |
|  | Go Server                           |   |
|  | - Gin HTTP on :8080                |   |
|  | - Embedded React UI at /ui/        |   |
|  | - Execution queue (goroutines)     |   |
|  | - DID services                     |   |
|  | - Web UI embedded via Go embed     |   |
|  +------------------------------------+   |
+------------------------------------------+
```

- No external dependencies (no PostgreSQL, no Redis)
- Data path: `~/.agentfield/data/`
- Hot-reload via Air

### Production Mode (PostgreSQL)

```
+------------------------------------------+
|  Load Balancer                            |
+------+-----------------------------------+
       |
+------v-----------+     +------------------+
|  Control Plane   |     |  Control Plane   |
|  Replica 1       |     |  Replica 2       |
|  (stateless)     |     |  (stateless)     |
+------------------+     +------------------+
       |                        |
       +----------+-------------+
                  |
         +--------v--------+
         |  PostgreSQL 16   |
         |  + pgvector      |
         +-----------------+
                  |
         +--------v--------+
         |  Agent Nodes     |
         |  (Python/Go/TS)  |
         +-----------------+
```

- PostgreSQL 16 with pgvector extension
- DB migrations managed by Goose, run automatically before server start
- Stateless control plane design means horizontal scaling by adding replicas
- Helm chart for Kubernetes with configurable replicas, persistent volumes, ingress

### Storage Abstraction

The Go server initializes a `StorageFactory` abstracting SQLite vs PostgreSQL:
- Works with `gorm.io/gorm` as primary ORM layer
- Supports both `github.com/mattn/go-sqlite3` (CGO) and `modernc.org/sqlite` (pure Go)
- No Redis, no RabbitMQ, no external queue -- execution queue is in-process (goroutine-based worker pool)

---

## 9. Key Source Files

| File | Purpose |
|------|---------|
| `sdk/python/agentfield/agent.py` (5391 lines) | Python SDK Agent class: decorators, call(), pause(), run(), harness, workflow tracking |
| `sdk/python/agentfield/agent_ai.py` | Python LLM integration via LiteLLM, structured output, streaming, multimodal |
| `sdk/python/agentfield/did_manager.py` | Python DID identity package, agent registration, execution context creation |
| `sdk/python/agentfield/vc_generator.py` | Python Verifiable Credential generation and verification |
| `sdk/python/agentfield/memory.py` | Cross-agent memory with 4 scopes |
| `sdk/python/agentfield/harness/` | Harness orchestration: runner, providers, schema validation |
| `sdk/python/agentfield/agent_field_handler.py` | AgentField server communication: registration, heartbeat, lifecycle |
| `sdk/python/agentfield/client.py` | API client: execution, memory, discovery, approvals |
| `sdk/go/agent/` | Go SDK: registration, DID, harness, memory, lifecycle, cancel |
| `sdk/go/harness/` | Go harness: runner, Claude Code/Codex/OpenCode/Gemini providers |
| `sdk/go/did/` | Go DID: manager, client, VC generator, types |
| `sdk/typescript/src/` | TypeScript SDK: Agent, harness, DID, memory, workflow, crypto |
| `control-plane/cmd/af/main.go` | Unified CLI binary |
| `control-plane/internal/server/server.go` | Go server: Gin router, services, DID, storage, triggers, dispatchers |
| `control-plane/internal/server/routes_core.go` | Core REST routes |
| `control-plane/internal/services/` | Go services: DID, VC, tags, policies, status, health, webhooks, triggers |
| `control-plane/internal/skillkit/skill_data/agentfield/SKILL.md` | The /agentfield Claude Code skill (255-line architectural specification) |
| `deployments/docker/docker-compose.yml` | Docker Compose: PostgreSQL + control-plane + demo agents |
| `deployments/helm/` | Helm chart for Kubernetes deployment |

## Related

- [[agentfield]] -- wiki page for the platform
- [[agentfield-api]] -- REST API reference
- [[agentfield-deployment]] -- deployment guide
- [[agentfield-quadlet]] -- Quadlet deployment
- [[agentfield-mcp-server]] -- MCP bridge server
- [[agentfield-profile]] -- AgentField platform profile
- [[agentfield.codegraph-verify]] -- codegraph verification
- [[SWE-AF]] -- autonomous engineering factory
- [[sec-af]] -- security auditor agent
- [[af-deep-research]] -- deep research engine
- [[af-reactive-atlas-mongodb]] -- reactive MongoDB intelligence
