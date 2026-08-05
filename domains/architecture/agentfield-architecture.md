---
name: agentfield-architecture
tags: [agentfield, architecture, cli, control-plane, docker, golang, harness, identity, mcp, orchestration, plugin-sdk, quadlet, security, storage, systemd]
description: "AgentField architecture: AI control plane orchestrating agent nodes via Python/Go/TS SDKs, harness providers, DID identity, and in-process execution"
source: sources/agentfield/
---

# AgentField: AI Control Plane Architecture
**Source:** `sources/agentfield/` (v0.1.118-rc.3, Apache-2.0)

**Status:** Active research target  
**License:** Apache 2.0  
**Repository:** github.com/agent-field/agentfield  
**SDK Languages:** Python (primary), Go, TypeScript  
**Control Plane:** Go (Gin framework)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Execution & Concurrency Model](#2-execution--concurrency-model)
3. [Binaries & Build](#3-binaries--build)
4. [Server & API Surface](#4-server--api-surface)
5. [SDKs](#5-sdks)
6. [Harness Orchestration](#6-harness-orchestration)
7. [Identity and IAM (DID/VC)](#7-identity-and-iam-didvc)
8. [Memory System](#8-memory-system)
9. [Node Package System](#9-node-package-system)
10. [Desktop, Skills & Integrations](#10-desktop-skills--integrations)
11. [Configuration System](#11-configuration-system)
12. [Deployment Architecture](#12-deployment-architecture)
13. [Key Source Files](#13-key-source-files)
14. [Note on docs/ARCHITECTURE.md](#14-note-on-docsarchitecturemd)

---

## 1. Architecture Overview

AgentField is an open-source AI control plane for building and operating production-grade multi-agent systems. The project provides infrastructure that makes agents callable as REST APIs with routing, async execution, memory, cryptographic identity, tag-based IAM, harness orchestration, and observability.

**AgentField does not virtualize agent execution.** A full-source verification found no hypervisor or VM-sandbox isolation code anywhere in the repository — agents are ordinary processes (Python/Go/TypeScript nodes) that register with the control plane and receive execution requests over HTTP. "Sandboxing" appears nowhere in the design; the isolation model is cryptographic identity + authorization, not process virtualization. (Correcting an earlier framing of this doc that claimed otherwise.)

It competes with frameworks like LangChain on the "what runs it" axis rather than the "how you write it" axis — AgentField cares about execution, orchestration, and governance, not agent implementation patterns.

**Key differentiators:**
- Every agent execution is a REST POST endpoint with cryptographic provenance
- Cross-agent calls route through the control plane (never direct agent-to-agent HTTP)
- W3C DID + Verifiable Credential identity for every agent, reasoner, and execution
- Harness system treats LLM CLI tools (Claude Code, Codex, Gemini, OpenCode) as autonomous computational units
- Stateless horizontally-scalable Go backend with agents connecting from anywhere
- Embedded MCP server at `POST /mcp` (5 tools, enabled by default)

---

## 2. Execution & Concurrency Model

The execution engine is **in-process and in-memory**, not PostgreSQL-backed.

### Completion Queue

Asynchronous executions finish through an in-process completion queue (`control-plane/internal/handlers/execute.go`):

```go
// execute.go:174
completionQueue chan completionJob
```

- A single worker goroutine drains the channel (`ensureCompletionWorker()`, execute.go:2933-2937)
- Queue size defaults to **2048**, overridable via `AGENTFIELD_EXEC_COMPLETION_QUEUE` (execute.go:2932)
- `enqueueCompletion()` is non-blocking: if the queue is full it returns `"completion queue is full"` (execute.go:2957-2961)

### Concurrency Limiter

`control-plane/internal/handlers/execution_guards.go` gates every execution via `CheckExecutionPreconditions()`:
- **LLM health circuit breaker** — refuses execution when the LLM backend circuit is open (503 `llm_unavailable`, execution_guards.go:90-118)
- **Per-agent concurrency limit** — `AgentConcurrencyLimiter.Acquire(agentNodeID)` (defined in `control-plane/internal/handlers/agent_concurrency.go:37-38`), refusal returns 429 `concurrency_limit`
- Errors carry a stable machine `ErrorCategory`: `llm_unavailable`, `concurrency_limit`, `agent_timeout`, `agent_error`, `agent_unreachable`, `bad_response`, `internal_error` (execution_guards.go:127-136)

### Persistence: PostgreSQL, not a distributed queue

State persists in **PostgreSQL** (pg16 + pgvector) via GORM — 38 Goose-managed SQL migrations in `control-plane/migrations/` (000–037+). There is **no Redis, no external queue, no lease-based scheduler**:

- Node **presence** uses a short lease: `DefaultLeaseTTL = 5 * time.Minute` (`control-plane/internal/handlers/nodes_rest.go:17-18`), renewed by `POST /nodes/:node_id/heartbeat` and `PATCH /nodes/:node_id/status` (NodeStatusLeaseHandler, routes_core.go:57)
- The action-claim mechanism is explicitly unfinished — `ClaimActionsHandler` comment (nodes_rest.go:194-195):

  > "Currently the scheduler backend is under construction, so this returns an empty queue but still renews leases."

- Execution results/status/events are stored in PostgreSQL and streamed via in-memory event bus + SSE, not pulled from a queue.

---

## 3. Binaries & Build

The control plane builds **4 binaries**, all under `control-plane/cmd/`:

| Binary | Purpose |
|--------|---------|
| `af` | Unified CLI. **Bare `af` (no subcommand) = server mode** (`cmd/af/main.go`, root command `Run: runServerFunc`). Subcommands: `server`, `dev`, `init`, `run`, `call`, `wait`, `tail`, `skill`, `catalog`, `install`, `doctor`, `harness` |
| `agentfield-server` | Standalone server binary (Docker/distroless deployments), `cmd/agentfield-server/main.go` |
| `af-tray` | macOS menu-bar app: fleet status, 24h usage chart (`chart_render.go`), Claude Code quota read from Keychain (`claude_quota_darwin.go`), launchd autostart/bootstrap (`launchd_darwin.go`) |
| `x25519gen` | X25519 keypair generator for DID key-agreement keys (`cmd/x25519gen/main.go`) |

`control-plane/build-single-binary.sh` produces self-contained platform binaries that **embed the web UI** via Go `//go:embed` (web/client → dist; build flags `-tags "embedded sqlite_fts5"`).

---

## 4. Server & API Surface

The server (`control-plane/internal/server/server.go`) is a single Go process that serves:

- **REST API** at `/api/v1` — 10 route groups, ~127 registered routes across 13 `routes_*.go` files (Core 53, Memory 14, Triggers 18, Agentic 12, DID 9, Observability 7, Admin 6, ARD 5, Knowledge 3, MCP 3)
- **gRPC admin** `AdminReasonerService` on **HTTP port + 100 = 8180** (`server.go:469` `adminPort := cfg.AgentField.Port + 100`, `server.go:712-738` `startAdminGRPCServer`, proto at `control-plane/proto/admin/reasoner_admin.proto`), API-key protected via `middleware/grpc_auth.go`
- **Embedded MCP server** at `POST /mcp` (`routes_mcp.go:40-69`), streamable-HTTP JSON-RPC 2.0, enabled by default (`features.mcp.enabled`, default true), 5 tools (see [[agentfield-api]] §MCP)
- **UI API** at `/api/ui/v1` (88 routes) + `/api/ui/v2` (3: workflow-runs list/detail/golden) (`routes_ui.go:50, 281-286`)
- **Public endpoints** at root: `/metrics` (Prometheus), `/health` (`routes_core.go:21-22`), `/.well-known/did.json`, `/.well-known/ai-catalog.json`, `/debug/pprof` (admin-gated), and the `/ui/` SPA
- **Knowledge base** at `/api/v1/agentic/kb` (topics/articles/guide, registered on the root router, `routes_agentic.go:40-49`)

Route files: `routes_admin.go`, `routes_agentic.go`, `routes_ard.go`, `routes_connector.go`, `routes_core.go`, `routes_did.go`, `routes_knowledge.go`, `routes_mcp.go`, `routes_memory.go`, `routes_middleware.go`, `routes_observability.go`, `routes_triggers.go`, `routes_ui.go`.

### MCP (correction from prior docs)

The embedded MCP server was **removed** in PR #359 ("Refactor: remove all MCP code from codebase") and **re-added in PR #817**. Current state: fully present, on by default, 5 tools (`discover_agents`, `get_reasoner_schema`, `execute_reasoner`, `get_run`, `wait_run`; `docs/mcp-integration.md`), disabled via `AGENTFIELD_MCP_ENABLED=false` / `features.mcp.enabled: false`, in which case `/mcp` returns 404.

---

## 5. SDKs

Three SDKs implement the agent runtime under `sdk/`:

### Python SDK (`sdk/python/agentfield/`, 54 top-level modules)

Most mature. Key modules: `agent.py` (Agent class: decorators, call(), pause(), run(), harness), `agent_ai.py` (LLM via LiteLLM), `agent_discovery.py`, `agent_field_handler.py` (registration/heartbeat/lifecycle), `agent_pause.py`, `agent_registry.py`, `agent_serverless.py`, `agent_workflow.py`, `did_manager.py`, `vc_generator.py`, `memory.py` + `memory_events.py`, `multimodal.py` / `multimodal_response.py`, `sessions.py`, `triggers.py`, `tool_calling.py`, `client.py`, `harness/` (4 providers), `verification.py`.

The Python agent is a FastAPI subclass: decorators compile to REST endpoints.

```python
app = agentfield.Agent("my-agent")

@app.reasoner()        # Register a reasoning function as an API endpoint
@app.skill()           # Register a deterministic skill as an API endpoint
@app.session()         # Register a multi-turn session handler
@app.on_change()       # Reactive memory event listener
```

How `@app.reasoner()` works:
1. Wraps the user function in a `tracked_func` integrated with workflow tracking
2. Generates type-hint-driven JSON schemas on demand (avoids Pydantic model creation per handler — saves ~1.5-2 KB per handler)
3. Creates FastAPI `@post(endpoint_path)` routes
4. Stores input type tuples `(type, default)` for lightweight runtime validation via `_validate_handler_input()`
5. Auto-exposes every reasoner as a REST POST endpoint, also callable via `POST /api/v1/execute/{agent}.{id}`

`app.ai()` provides structured LLM calling via LiteLLM (multi-provider): `schema=MyPydanticModel` typed returns, streaming, multimodal, tool use via `tools="discover"`.

### Go SDK (`sdk/go/`)

Packages: `agent/` (registration, DID, harness, memory, lifecycle, cancel), `client/`, `types/`, `ai/`, `harness/`, `did/`, `inputs/`. Mirrors the Python primitives with native Go types.

```go
agent := agent.NewAgent("my-agent")
agent.Reasoner("analyze", func(ctx context.Context, input AnalyzeInput) (*AnalyzeOutput, error) {
    result, err := agent.AI(ctx, input.Text, agent.WithProvider("claude"))
    return result, err
})
```

### TypeScript SDK (`sdk/typescript/src/`)

Modules: `agent/`, `harness/`, `did/`, `memory/`, `workflow/`, `crypto/`, plus `ai/`, `approval/`, `router/`, `session.ts`, `sessionTransport.ts`, `triggers/`, `usage/`, `verification/`, `observability/`.

```typescript
const agent = new Agent({ name: "my-agent" });
agent.reasoner({ id: "analyze" }, async (input: { text: string }) => {
  const result = await agent.ai(input.text, { provider: "anthropic" });
  return result;
});
```

---

## 6. Harness Orchestration

The harness system treats LLM CLI tools as autonomous computational units. `app.harness(prompt, provider=...)` dispatches multi-turn tasks to external coding-agent CLIs.

### Supported Providers (4)

| Provider | Mechanism | Lazy Import | Provider File |
|----------|-----------|-------------|---------------|
| `claude-code` | `claude_agent_sdk` Python package | Yes | `harness/providers/claude.py` |
| `codex` | `codex exec --json` subprocess | No | `harness/providers/codex.py` |
| `gemini` | `gemini -p` subprocess | No | `harness/providers/gemini.py` |
| `opencode` | `opencode run --format json` subprocess | No | `harness/providers/opencode.py` |

Factory: `harness/providers/_factory.py` (`SUPPORTED_PROVIDERS`), base class `_base.py`.

### Harness Runner Pipeline

`HarnessRunner` wraps all providers with a common pipeline:
- Transient error detection + exponential backoff (±25% jitter, 3 retries)
- Schema validation retry loop (2 retries for output JSON compliance)
- Cost capping (`max_budget_usd`)
- Turn limiting (`max_turns`)
- Tool access control
- System prompt injection

### Output Recovery Pipeline (3 layers)

1. **`_ai_schema_repair()`** — Cheap LLM call (90s timeout) reformats malformed JSON into valid schema before an expensive full rerun
2. **Schema validation retry** — Retry with a diagnostic follow-up prompt if repair fails
3. **Full harness re-run** — Complete re-execution if both repair and retry fail

### Adding New Providers

1. Create `harness/providers/mytool.py` implementing `async def execute(prompt, options) -> RawResult`
2. Add the name to `SUPPORTED_PROVIDERS` in `_factory.py`
3. Add an import + branch in `build_provider()`

The Go SDK mirrors this via `sdk/go/harness/` (`harness.NewRunner()`, `agent.Harness()`).

---

## 7. Identity and IAM (DID/VC)

AgentField implements a complete W3C DID + Verifiable Credential identity system.

### DID Hierarchy

```
Platform DID (control plane itself)
  |-- Node DID (per agent node)
       |-- Function DID (per reasoner/skill)
```

### Key Generation & Crypto

- **Algorithm:** Ed25519 signing keys per component (`did_auth.go:172-175` signs `{timestamp}:{SHA256(body)}` with the caller's Ed25519 key)
- **Key derivation:** BIP32 (config: `features.did.derivation_method: "BIP32"`)
- **Keystore encryption:** AES-256-GCM at rest (`config/agentfield.yaml` `keystore.encryption: "AES-256-GCM"`; `control-plane/internal/encryption/encryption.go:5, 21, 51-58` — 32-byte key from PBKDF2)
- **Key rotation:** 90 days default (`config.go:327` `KeyRotationDays int ... default:"90"`)
- **Key-agreement:** X25519 (`x25519gen` binary generates keypairs; JWE over X25519 in SDK crypto, `sdk/python/agentfield/crypto.py`)
- **DID methods:** `did:key` (config default) with `did:web` resolution endpoints (`/.well-known/did.json`, `/agents/:agentID/did.json`)

### Authentication Flow (Cross-Agent Calls)

Every cross-agent call carries DID auth headers:
- `X-Caller-DID` — the caller's DID
- `X-DID-Signature` — Ed25519 signature over `{timestamp}:{SHA256(body)}`
- `X-DID-Timestamp` — signing timestamp

### Replay Protection

Global replay cache with TTL equal to the timestamp window (default **300s**, `did_auth.go:145-149` `TimestampWindowSeconds`). Error codes (did_auth.go:188-298): `invalid_did_format`, `did_auth_required`, `invalid_timestamp`, `timestamp_expired`, `body_read_error`, `body_too_large`, `invalid_signature_encoding`, `replay_detected`, `verification_error`, `invalid_signature`.

### Permission Model (Two-Step)

**Step 1: Tag Approval** — agents propose tags at registration; control plane evaluates against rules (`auto`/`manual`/`forbidden` modes, sensitive tags like `financial`/`payments` require manual review); admin approves/rejects via API.

**Step 2: Policy Evaluation** — tag-based access policies with function-level allow/deny lists (`allow_functions: ["query_*"]`), parameter constraints, priority-based first-match-wins (`config/agentfield.yaml` `features.did.authorization.access_policies`).

### VC Generation

`vc_generator.py` (Python SDK) + Go equivalents generate signed Ed25519 W3C VCs. VC hierarchy: Platform VC → Node VC → Function VC. Agent tags travel as `AgentTagVC`. SDKs cache policies, revocation lists, and admin public keys locally for decentralized verification (5-min refresh via `localVerifier.NeedsRefresh()` in Go SDK).

### Default Deny

Fail-closed: no matching policy = deny; expired/revoked VCs block calls; `pending_approval` agents return 503.

---

## 8. Memory System

Cross-agent memory with 4 scopes:

| Scope | Visibility | Lifetime | Use Case |
|-------|-----------|----------|----------|
| `global` | All agents | Forever | Shared knowledge base |
| `session` | Within a session | Session duration | Conversation context |
| `actor` | Specific agent | Agent lifetime | Agent-specific state |
| `workflow` | Within a workflow | Workflow duration | Execution context |

### Memory Operations

- KV store per scope (`POST /memory/set`, `/get`, `/delete`, `/list`)
- Vector store (pgvector) with cosine similarity search (`/memory/vector/*`)
- Event-based subscriptions via `@app.on_change()`; SSE/WebSocket streams at `/api/v1/memory/events/sse` and `/events/ws` (`routes_memory.go:50-51`), plus `/events/history` (`:52`)
- All memory operations go through the control plane (not agent-local)

---

## 9. Node Package System

Nodes are distributed as installable packages, managed by `control-plane/internal/packages/`:

- **Manifest:** `agentfield-package.yaml` (e.g. `integrations/linear/agentfield-package.yaml`, `databricks`, `snowflake`) with a `config_version` schema
- **Commands:** `af install <package-path>` (`cli/commands/install.go:43`), `af run` (`cli/agent_commands.go:260`), `af call <node>.<reasoner>` (`cli/call.go:48`), `af uninstall`
- **Secrets:** encrypted at rest with AES-256-GCM via `encryption.EncryptionService` — `secrets/global.enc` (shared) and `secrets/<node>.enc` (per-node) under `~/.agentfield` (`packages/secrets.go:19-22, 83-104`)
- **Env resolution:** `packages/env_resolver.go` resolves `user_environment` vars (prompt + store in encrypted secret store, `Resolve()`/`lookup()`/`promptAndStore()`)
- **Runner:** `packages/runner.go` + `pyinterp.go`/`gointerp.go` execute installed nodes

---

## 10. Desktop, Skills & Integrations

### Desktop App (`desktop/`)

Electron app (`electron.vite.config.ts`, `src/main|preload|renderer|shared`):
- Screens: Agents list, Secrets, Activity, Install flow, Settings (`desktop/src/renderer/src/components/`)
- Autostart + launchd integration for local agent nodes
- Contracts with `af install/run/stop` to manage node lifecycle from the UI

### Skills (`skillkit/`)

3 embedded skills in `control-plane/internal/skillkit/skill_data/`: `agentfield`, `agentfield-personal`, `agentfield-use`. Installed via `af skill install --target <claude-code|codex|gemini|opencode|aider|windsurf|cursor>`. Embedded into the binary via `//go:embed` (`embed.go`), synced by `scripts/sync-embedded-skills.sh`.

### Integrations & Examples

- `integrations/`: databricks, linear, sentry, snowflake (each ships an `agentfield-package.yaml`)
- `examples/`: python_agent_nodes, go_agent_nodes, ts_agent_nodes, go_harness_demo, triggers-demo, triggers-demo-ts, ts-node-examples, benchmarks, e2e_resilience_tests
- `docs/`: 11 guides including `mcp-integration.md`, `harness-providers.md`, `installing-agent-nodes.md`, `VC_AUTHORIZATION_ARCHITECTURE.md`, `ENVIRONMENT_VARIABLES.md`

---

## 11. Configuration System

- **YAML:** `control-plane/config/agentfield.yaml` with sections `agentfield` (port, execution queue), `ui`, `api` (auth: api_key/admin_token/internal_token), `telemetry` (tracing/OTel), `logging`, `storage`, `features` (did incl. keystore + authorization, mcp, connector)
- **Env vars:** 43 `AGENTFIELD_*` variables documented in `control-plane/.env.example`; `AGENTFIELD_CONFIG_FILE` overrides the config path
- **Loading:** Viper with prefix `AGENTFIELD` and `.` → `_` key replacement (`cmd/af/main.go:226-277` `loadConfig`), `AutomaticEnv`, plus explicit binds (e.g. `AGENTFIELD_API_KEY` / `AGENTFIELD_API_AUTH_API_KEY`)
- **Config storage API:** runtime config overrides via `/api/v1/configs` CRUD (`config_storage.go`)

---

## 12. Deployment Architecture

### Local Mode (`af dev` / bare `af`)

Single process, zero external dependencies: Gin HTTP on :8080, embedded React UI, in-process execution queue, DID keystore, and either SQLite or the pure-Go `modernc.org/sqlite` driver. Data under `~/.agentfield/`.

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

- PostgreSQL 16 with pgvector extension; GORM ORM; 38 Goose migrations run automatically at startup
- Stateless control plane → horizontal scaling by adding replicas
- Helm chart in `deployments/helm/`; Docker Compose in `deployments/docker/`
- Execution state lives in PostgreSQL; the completion queue is per-process in-memory (see §2)

---

## 13. Key Source Files

| File | Purpose |
|------|---------|
| `control-plane/internal/handlers/execute.go` | Execution engine: completion queue (line 174), async worker pool, cancel/pause/resume/restart |
| `control-plane/internal/handlers/execution_guards.go` | Concurrency limiter + LLM health circuit breaker |
| `control-plane/internal/handlers/nodes_rest.go` | Node registration/heartbeat, presence lease (DefaultLeaseTTL=5min, line 17-18), ClaimActionsHandler ("scheduler backend is under construction", line 194) |
| `control-plane/internal/server/server.go` | Server wiring: Gin router, gRPC admin on port+100 (line 469), services, startup |
| `control-plane/internal/server/routes_mcp.go` | Embedded MCP server at POST /mcp (lines 40-69), 5 tools |
| `control-plane/internal/server/routes_*.go` (13 files) | REST route groups |
| `control-plane/internal/server/middleware/did_auth.go` | DID auth: headers, 300s window (line 145), error codes (188-298) |
| `control-plane/internal/encryption/encryption.go` | AES-256-GCM keystore encryption (PBKDF2, 32-byte key) |
| `control-plane/internal/config/config.go` | Config structs, key rotation 90 days (line 327), MCPConfig (254-275) |
| `control-plane/internal/packages/` | Node package system: installer, secrets (AES-256-GCM), env_resolver, runner |
| `control-plane/internal/ard/ard.go` | ARD catalog, default `application/openapi+json` (lines 454, 861) |
| `control-plane/internal/skillkit/` | Embedded skills (agentfield, agentfield-personal, agentfield-use) + installers |
| `control-plane/cmd/af/main.go` | Unified CLI + server mode; Viper config loading (226-277) |
| `control-plane/cmd/af-tray/` | macOS menu-bar app (launchd, Claude quota, 24h charts) |
| `control-plane/cmd/x25519gen/main.go` | X25519 keypair generator |
| `control-plane/build-single-binary.sh` | Single-binary build with embedded web UI (go:embed) |
| `sdk/python/agentfield/` (54 modules) | Python SDK: agent, agent_ai, did_manager, vc_generator, memory, harness/, triggers, sessions, multimodal, tool_calling, agent_serverless |
| `sdk/go/` | Go SDK: agent/, client/, types/, ai/, harness/, did/ |
| `sdk/typescript/src/` | TS SDK: Agent, harness, DID, memory, workflow, crypto |
| `desktop/` | Electron desktop app |
| `control-plane/migrations/` | 38 Goose SQL migrations (pg16 + pgvector) |
| `control-plane/config/agentfield.yaml` | Default config: agentfield/ui/api/telemetry/logging/storage/features |
| `control-plane/.env.example` | 43 AGENTFIELD_* environment variables |
| `docs/ARCHITECTURE.md` | **STALE** — see §14 |

---

## 14. Note on docs/ARCHITECTURE.md

The in-repo `docs/ARCHITECTURE.md` is **out of date**: it references nonexistent packages `internal/workflows`, `internal/repositories`, and `pkg/db` (lines 19-21, 50-51, 90). The actual code lives in `internal/handlers/`, `internal/server/`, `internal/services/`, `internal/packages/`, and `migrations/`. **Trust the code, not that document.** This wiki page is written from the code.

---

## Related

- [[agentfield]] -- wiki page for the platform
- [[agentfield-api]] -- REST API reference
- [[agentfield-deployment]] -- deployment guide
- [[agentfield-quadlet]] -- Quadlet deployment
- [[agentfield-mcp-server]] -- MCP bridge server
- [[hermes-profiles]] -- AgentField platform profile
- [[agentfield.codegraph-verify]] -- codegraph verification
- [[SWE-AF]] -- autonomous engineering factory
- [[sec-af]] -- security auditor agent
- [[af-deep-research]] -- deep research engine
- [[af-reactive-atlas-mongodb]] -- reactive MongoDB intelligence
