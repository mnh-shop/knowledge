---
name: agentfield-codegraph-verify
tags: [agentfield, cli, control-plane, docker, golang, grpc, harness, identity, mcp, orchestration, plugin-sdk, storage, wiki]
description: Codegraph verification for agentfield — validating route groups, embedded MCP server, DID auth, memory scopes, and CLI surfaces against indexed source code symbols
source: sources/agentfield/
---

# Codegraph Verification: agentfield

**Date:** 2026-07-12
**Version verified:** `0.1.118-rc.3` (from `VERSION`)

## Claim 1: Control plane exposes 10 route groups under /api/v1 with ~127 endpoint registrations (13 route files, no routes_swagger.go)
- **Wiki says:** 10 groups registered under `/api/v1` (core, memory, knowledge, did, observability, admin, connector, agentic, triggers, ard) with ~127 endpoint registrations across 13 route files; `routes_ui.go` serves browser UI APIs; there is no `routes_swagger.go`
- **Source evidence:**
  - `control-plane/internal/server/server.go:873-885` — `setupRoutes()` registers exactly 10 groups under `agentAPI := s.Router.Group("/api/v1")`: `registerCoreRoutes`, `registerMemoryRoutes`, `registerKnowledgeRoutes`, `registerDIDRoutes`, `registerObservabilityRoutes`, `registerAdminRoutes`, `registerConnectorRoutes`, `registerAgenticRoutes`, `registerTriggerRoutes`, `registerARDRoutes`
  - `ls control-plane/internal/server/` shows 13 non-test route files: `routes_admin.go`, `routes_agentic.go`, `routes_ard.go`, `routes_connector.go`, `routes_core.go`, `routes_did.go`, `routes_knowledge.go`, `routes_mcp.go`, `routes_memory.go`, `routes_middleware.go`, `routes_observability.go`, `routes_triggers.go`, `routes_ui.go` — no `routes_swagger.go` exists
  - Direct endpoint registrations count to ~127: `routes_core.go` 53, `routes_triggers.go` 18, `routes_memory.go` 14, `routes_agentic.go` 12, `routes_did.go` 9, `routes_observability.go` 7, `routes_admin.go` 6, `routes_ard.go` 5, `routes_knowledge.go` 3
  - `routes_connector.go` registers a feature-gated `/connector` group; `routes_ui.go:50,281` register `/api/ui/v1` and `/api/ui/v2`; `routes_core.go:21-22` registers root `/metrics` and `/health`
- **Verdict:** ✅ CORRECT (supersedes the earlier 14-groups / 15-route-files / `routes_swagger.go` claim)
- **Fix needed:** Applied to wiki

## Claim 2: Embedded MCP server is live at POST /mcp with 5 tools (not removed)
- **Wiki says:** AgentField ships an embedded MCP server at `POST /mcp` (streamable HTTP, JSON-RPC 2.0), enabled by default, exposing 5 tools: `discover_agents`, `get_reasoner_schema`, `execute_reasoner`, `get_run`, `wait_run`
- **Source evidence:**
  - `control-plane/internal/server/routes_mcp.go:40-69` — `registerMCPRoutes()` registers `s.Router.POST("/mcp", handler)`, GET returns 405, OPTIONS answers preflight; disabled only via `AGENTFIELD_MCP_ENABLED=false` (line 42: `s.config.Features.MCP.IsEnabled()`)
  - `control-plane/internal/config/config.go:261-268` — `MCPConfig.Enabled` defaults true ("Enabled turns the /mcp endpoint on. Default: true")
  - `control-plane/internal/handlers/mcp.go:721-800` — `mcpToolCatalog()` lists exactly the 5 tools with JSON Schemas (names at lines 721, 750, 782; `discover_agents`/`execute_reasoner`/`wait_run` dispatch at 214, 218, 222)
  - `docs/mcp-integration.md` — documents endpoint `POST http://localhost:8080/mcp`, streamable HTTP, "On by default"
- **Verdict:** ✅ CORRECT — the earlier wiki claim that MCP was removed from the codebase is **stale**; the embedded server was re-added (PR #817) and is now the primary MCP surface
- **Fix needed:** Applied to wiki

## Claim 3: DID auth headers, error codes, and internal-token transport
- **Wiki says:** DID auth uses `X-Caller-DID` + `X-DID-Signature` + `X-DID-Timestamp` + `X-DID-Nonce` with Ed25519 signing and 10 named error codes; the internal token travels as `Authorization: Bearer`, not in a dedicated internal-token header
- **Source evidence:**
  - `control-plane/internal/server/middleware/did_auth.go:170-175` — extracts `X-Caller-DID`, `X-DID-Signature`, `X-DID-Timestamp`, `X-DID-Nonce`
  - `did_auth.go:188-298` — error codes in order: `invalid_did_format`, `did_auth_required`, `invalid_timestamp`, `timestamp_expired`, `body_read_error`, `body_too_large`, `invalid_signature_encoding`, `replay_detected`, `verification_error`, `invalid_signature`
  - `control-plane/internal/server/routes_did.go:311-313` — DID documents carry `Ed25519VerificationKey2020` verification methods (W3C DID Ed25519 per agent)
  - `control-plane/internal/services/cancel_dispatcher.go:70-73` — "InternalToken is sent as Authorization: Bearer on the cancel callback"; line 213: `req.Header.Set("Authorization", "Bearer "+d.internalToken)`
- **Verdict:** ✅ CORRECT
- **Fix needed:** Applied to wiki (error-code list replaced; header transport corrected)

## Claim 4: Memory scopes are global/actor/session/workflow via similarity_search
- **Wiki says:** Memory offers 4 scopes — global, actor, session, workflow — and vector search is `similarity_search()`
- **Source evidence:**
  - `control-plane/internal/handlers/memory.go:402-418` — `resolveScope()` maps `X-Workflow-ID` → `workflow`, `X-Session-ID` → `session`, `X-Actor-ID` → `actor`, else default `global`
  - `control-plane/internal/handlers/vector_memory_test.go:142,231,280,329` — tests exercise `session`, `actor`, `workflow`, and `session` scope records/searches
  - `sdk/python/agentfield/memory.py:471` — `async def similarity_search(...)` (the method is `similarity_search`, not `.search()`)
- **Verdict:** ✅ CORRECT (replaces earlier "global/agent/session/run" claim)
- **Fix needed:** Applied to wiki

## Claim 5: Execution queue is in-process; "lease" is node presence only
- **Wiki says:** Async execution uses an in-process Go channel queue (`QueueSize: 1000`), not a PostgreSQL-backed durable queue with leases; the only "lease" is the 5-minute agent node presence TTL
- **Source evidence:**
  - `control-plane/internal/handlers/execute.go:174` — `completionQueue chan completionJob` (in-memory channel); line 2933 `completionQueue = make(chan completionJob, size)`
  - `control-plane/internal/server/server.go:414` — `QueueSize: 1000`
  - `control-plane/internal/handlers/nodes_rest.go:17-18` — `DefaultLeaseTTL = 5 * time.Minute` is the agent node presence lease returned on registration/heartbeat
- **Verdict:** ✅ CORRECT (fixes the "durable queue" claim)
- **Fix needed:** Applied to wiki

## Claim 6: gRPC AdminReasonerService on port 8180; 4 shipped binaries; CLI surface
- **Wiki says:** A gRPC `AdminReasonerService` listens on `:8180` (HTTP port + 100); the repo ships 4 binaries (`af`, `agentfield-server`, `af-tray`, `x25519gen`); the CLI is ~35 commands with `dev --watch` and no key-export subcommand
- **Source evidence:**
  - `control-plane/internal/server/server.go:469` — `adminPort := cfg.AgentField.Port + 100` (8080 → 8180); lines 712-738 `startAdminGRPCServer()` registers `adminpb.RegisterAdminReasonerServiceServer` with API-key interceptor; `middleware/grpc_auth.go` implements the interceptor
  - `control-plane/cmd/` contains `af`, `agentfield-server`, `af-tray`, `x25519gen` directories
  - `control-plane/internal/cli/commands/dev.go:59` — `cobraCmd.Flags().BoolVarP(&watch, "watch", "w", false, "Watch for file changes and auto-restart")` (the only watch flag)
  - `control-plane/internal/cli/vc.go:50-72` — only `verify <vc-file.json>` subcommand (+ `af verify` alias); no key-export command
  - `af-tray` surface confirmed in `control-plane/cmd/af-tray/` (chart_render.go:3-7 "24h timeline", claude_quota_darwin.go, launchd_darwin.go)
- **Verdict:** ✅ CORRECT
- **Fix needed:** Applied to wiki (gRPC + binaries + CLI inventory added)

## Claim 7: ARD default type, SSE endpoints, traffic weight, and SDK size
- **Wiki says:** ARD publishes `application/openapi+json` by default; real SSE surfaces are execution/workflow/memory event streams (no `/api/v1/events`); traffic weight is set via `PUT /connector/reasoners/:id/versions/:version/weight`; the Python SDK is 54 top-level modules / ~1.3MB
- **Source evidence:**
  - `control-plane/internal/ard/ard.go:454` — `DefaultType: firstNonEmpty(cfg.Publish.DefaultType, "application/openapi+json")`; line 861 default artifact type `application/openapi+json` (`application/mcp-server+json` is only a configurable `DefaultType`)
  - `control-plane/internal/server/routes_core.go:121,159` — `/api/v1/executions/:execution_id/events`, `/api/v1/workflow/executions/events`; `routes_memory.go:50-51` — `/api/v1/memory/events/ws` and `/api/v1/memory/events/sse` (no global `/api/v1/events`)
  - `control-plane/internal/handlers/connector/handlers.go:72` — `reasonerGroup.PUT("/reasoners/:id/versions/:version/weight", h.SetReasonerTrafficWeight)`
  - `sdk/python/agentfield/` — 54 top-level `*.py` modules (68 total including `harness/` and `fixtures/`), `du -sh` ≈ 1.3MB
- **Verdict:** ✅ CORRECT
- **Fix needed:** Applied to wiki

## Claim 8: Config, feature flags, triggers, and package system
- **Wiki says:** Config comes from `control-plane/config/agentfield.yaml` plus `AGENTFIELD_*` env vars with env precedence; `features.mcp.enabled` and `features.connector.{enabled,token,capabilities}` exist; trigger providers include GitHub/Slack/Stripe/GenericBearer/GenericHMAC; node packages use `agentfield-package.yaml` with an encrypted secrets store
- **Source evidence:**
  - `control-plane/cmd/af/main.go:226-277` — Viper setup: `viper.SetEnvPrefix("AGENTFIELD")`, config paths (`~/.agentfield`, `./config`, `.`), `config.ApplyEnvOverrides(&cfg)` after `ReadInConfig` (env precedence)
  - `control-plane/internal/config/config.go:261-268, 809-833` — `MCPConfig` (enabled default true) and `Connector` overrides (`AGENTFIELD_CONNECTOR_*`, capabilities map)
  - `control-plane/internal/sources/` — provider dirs: `github`, `slack`, `stripe`, `genericbearer`, `generichmac`, plus `cron`, `databricks`, `linear`, `sentry`, `snowflake`
  - `control-plane/internal/packages/installer.go:100,124` — `PackageMetadata` with `UserEnvironment UserEnvironmentConfig yaml:"user_environment"`; `internal/packages/secrets.go:19-20,113` — encrypted secrets at `~/.agentfield/secrets/<scope>.enc`
- **Verdict:** ✅ CORRECT
- **Fix needed:** Applied to wiki

## Related

- [[agentfield]] -- wiki page for the platform
- [[agentfield-architecture]] -- system architecture with route groups
- [[agentfield-api]] -- REST API reference
- [[agentfield-deployment]] -- deployment modes documentation
- [[hermes-profiles]] -- AgentField platform profile

## Summary
All 8 claims from the corrected wiki verified against source via codegraph + direct file inspection:
- ✅ Route groups: exactly 10 under `/api/v1`, ~127 registrations, 13 route files, no `routes_swagger.go`
- ✅ Embedded MCP server live at `POST /mcp` with 5 tools (previous "removed from codebase" claim is stale)
- ✅ DID auth headers/error codes; internal token is `Authorization: Bearer` (not a dedicated internal-token header)
- ✅ Memory scopes global/actor/session/workflow; method `similarity_search`
- ✅ In-process execution queue (`completionQueue`, `QueueSize: 1000`); lease = node presence only
- ✅ gRPC `AdminReasonerService` on `:8180`; 4 binaries; ~35 CLI commands; `dev --watch`, no key-export
- ✅ ARD default `application/openapi+json`; corrected SSE surfaces; traffic weight API; SDK 54 modules/1.3MB
- ✅ Config env precedence, `features.mcp`/`features.connector`, trigger providers, `agentfield-package.yaml` + encrypted secrets

## Cross-project

- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
- [[podman.codegraph-verify]] -- Similar codegraph verification for Podman
