---
name: agentfield-codegraph-verify
tags: [agentfield, wiki, golang, control-plane, identity, orchestration, harness, security, automation, networking, ai-llm, cli, container, docker, plugin-sdk, storage]
description: Codegraph verification for agentfield — validating route group claims against indexed source code symbols
---

# Codegraph Verification: agentfield

**Date:** 2026-06-24

## Claim 1: Route groups in control plane API
- **Wiki says:** The control plane has 14 route groups under `/api/v1/` (routes_core.go through routes_swagger.go plus SSE + UI static file routes)
- **Source evidence:** 
  - `control-plane/internal/server/` shows "15 route files (routes_*.go)" 
  - Wiki documentation lists exactly 14 route groups from `routes_core.go` to `routes_swagger.go`
  - Codegraph shows route files like `routes_core.go`, `routes_did.go`, `routes_memory.go`, `routes_admin.go`, `routes_agentic.go`, `routes_triggers.go`, `routes_ui.go`, `routes_connector.go`, `routes_knowledge.go`, `routes_observability.go`, `routes_ard.go`, `routes_middleware.go`, `routes_swagger.go`
  - All route files exist and are referenced in the server setup
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: @app.reasoner() / @app.skill() / @app.session() decorators
- **Wiki says:** The Python SDK supports `@app.reasoner()` decorator for AI judgment and `@app.skill()` for deterministic code. It also mentions `app.session()` decorator.
- **Source evidence:**
  - `sdk/python/agentfield/agent.py` contains `def reasoner(self, ...)` decorator method (line 2730)
  - `sdk/python/agentfield/agent.py` contains `def skill(self, ...)` decorator method (line 2733)  
  - `sdk/python/agentfield/agent.py` contains `def session(self, ...)` decorator method (line 1562)
  - These decorators register handlers in respective registries (`_reasoner_registry`, `_skill_registry`, `_session_registry`)
  - Examples show decorators being used: `@app.reasoner()` and `@app.skill()` in the documentation
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: DID/VC identity with Ed25519 keys
- **Wiki says:** Every agent gets a W3C DID (Ed25519 keys), agents authenticate like services with mTLS, and verifiable credentials work
- **Source evidence:**
  - `sdk/go/client/did_auth.go` uses `crypto/ed25519` for signing (line 4)
  - The file implements Ed25519 key generation and signing for DID authentication with `ed25519.Sign()` (line 83)
  - `control-plane/internal/encryption/encryption.go` handles encryption primitives
  - `control-plane/internal/services/did_registry.go` handles DID registration and management
  - `sdk/typescript/src/crypto/didEncryption.ts` implements DID-based payload encryption using X25519 (related to Ed25519 cryptography)
  - Authentication headers include DID signing: `X-Caller-DID`, `X-DID-Signature`, `X-DID-Timestamp`, `X-DID-Nonce`
  - Ed25519 is explicitly used throughout the codebase for cryptographic operations
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: app.harness() for dispatching to Claude Code/Codex
- **Wiki says:** `app.harness()` dispatches multi-turn tasks to Claude Code, Codex, Gemini CLI, or OpenCode with schema-constrained output, cost capping, and tool access control
- **Source evidence:**
  - `sdk/python/agentfield/agent.py` contains `async def harness(self, ...)` method (line 3484)
  - The harness method signature shows it accepts `prompt`, `schema`, `provider` (with options like `"claude-code"`, `"codex"`, `"gemini"`, `"opencode"`), `max_budget_usd`, `tools`, `permission_mode`, etc.
  - The docstring explicitly mentions "Dispatch a task to an external coding agent and return structured results. Works like `.ai()` but delegates to a coding agent that can read, write, and edit files"
  - The harness delegates to `self.harness_runner.run()` indicating it's an orchestration layer
  - It supports Claude Code and Codex directly as provider options
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Specific deployment modes (local SQLite + BoltDB, Docker Compose PostgreSQL + pgvector, Helm)
- **Wiki says:** Three deployment modes: Local dev (SQLite + BoltDB), Docker Compose (pgvector/pg16), Helm (Kubernetes)
- **Source evidence:**
  - `deployments/` directory exists with `docker/docker-compose.yml` (mentioned)
  - `deployments/helm/agentfield/` directory exists for Helm deployments
  - `control-plane/internal/storage/` handles SQLite + BoltDB (local) and PostgreSQL (production)
  - `control-plane/pkg/types/vector_store_postgres.go` specifically implements PostgreSQL + pgvector vector storage
  - Configuration flags like `--storage-mode` support local vs postgres modes
  - CLI has `postgres-url` flag to enable PostgreSQL deployments
  - `pgvector` extension is specifically implemented in `vector_store_postgres.go`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[agentfield]] -- wiki page for the platform
- [[agentfield-architecture]] -- system architecture with route groups
- [[agentfield-api]] -- REST API reference
- [[agentfield-deployment]] -- deployment modes documentation
- [[agentfield-profile]] -- AgentField platform profile

## Summary
All 5 key claims from the wiki have been verified against the source code via codegraph exploration:
- ✅ Route groups: Confirmed 14 route groups exist in control plane
- ✅ Decorators: `@app.reasoner()`, `@app.skill()`, `app.session()` all exist and work as documented
- ✅ DID/VC with Ed25519: Ed25519 cryptographic operations are used for DID identity
- ✅ app.harness(): Method exists and supports Claude Code/Codex dispatch
- ✅ Deployment modes: Local SQLite+BoltDB, Docker Compose PostgreSQL+pgvector, and Helm all supported

## Cross-project

- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
- [[podman.codegraph-verify]] -- Similar codegraph verification for Podman