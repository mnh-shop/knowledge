---
name: 1claw-hermes-codegraph-verify
tags: [codegraph-verify, 1claw-hermes, hermes-agent, mcp]
description: "Codegraph Verification: 1claw-hermes"
source: sources/1claw-hermes/
date: 2026-07-12
---

# Codegraph Verification: 1claw-hermes

**Date:** 2026-07-12

## Claim 1: Hermes MCP shroud integration via config patching
- **Wiki says:** The package provides Hermes MCP integration via `patchHermesConfig()`, registering 1Claw under `mcp_servers.oneclaw` with stdio (default) or HTTP transport. Shroud TEE proxy routes LLM calls through a sidecar process.

- **Source evidence:** `README.md` lines 92-97 define `patchHermesConfig()` which "registers 1Claw under `mcp_servers.oneclaw`" with tools `mcp_oneclaw_*`. Lines 122-124 describe the Shroud sidecar pattern: "run the 1Claw Shroud sidecar on your machine, point Hermes at `localhost`, and let the sidecar inject headers and forward to `https://shroud.1claw.xyz`." Source file `src/mcp/hermes-config.ts` implements `patchHermesConfig()` with both stdio and HTTP transport options. Source file `src/shroud/index.ts` (line 11) exports `createShroudClient()` which returns an OpenAI-compatible client pointed at the Shroud TEE proxy. Source file `src/shroud/sidecar.ts` provides the `startSidecarAndWait()` function for programmatic sidecar lifecycle management. Source file `src/mcp/index.ts` (lines 12-23) implements `buildMcpEntry()` constructing JWT Bearer + vault ID header authorization.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Setup automation via bootstrap CLI and `pnpm setup`
- **Wiki says:** The package provides a comprehensive bootstrap and setup automation flow: enrollment, API key injection, Hermes config patching, sidecar installation and startup.

- **Source evidence:** `package.json` lines 15-19 define CLI aliases as npm scripts: `bootstrap`, `bootstrap:enroll`, `bootstrap:complete`, `setup`. `README.md` lines 12-20 document the two-phase bootstrap flow: `pnpm bootstrap enroll` sends email + agent name, then `pnpm bootstrap complete` reads `ONECLAW_AGENT_API_KEY` from `.env`. Lines 129-141 document `pnpm setup --provider google` which in one command reads the API key, patches Hermes YAML config for MCP, patches the model provider to point at the sidecar, downloads and starts the sidecar binary, and waits for `/healthz`. Source file `src/bootstrap.ts` implements `needsBootstrap()`, `bootstrapEnroll()`, and `completeBootstrapFromEnv()`. Source file `src/setup.ts` implements the unified CLI. Source file `src/bootstrap-cli.ts` implements the TTY/non-TTY CLI handler. Source file `src/dotenv-path.ts` implements dotenv resolution with ONECLAW_ENV_FILE, cwd walk, and package fallback.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Subagent identity lifecycle with scoped access
- **Wiki says:** The package supports ephemeral subagent identity provisioning with scoped policy-based access to vault secrets.

- **Source evidence:** `README.md` lines 310-353 document `provisionSubagent()`, `deprovisionSubagent()`, and `SubagentRegistry`. The API accepts a name and `ephemeralReadPolicy()` returning a scoped identity. Source file `src/subagents/index.ts` implements the identity lifecycle with `SubagentRegistry` tracking all live identities and cleanup on `SIGTERM`. Source file `src/subagents/policy.ts` implements `PolicyBuilder` with fluent methods: `allowPath()`, `readOnly()`, `expireAfter()`, `allowChains()`, `capValue()`, and `build()`. Source file `src/client.ts` provides a singleton `@1claw/sdk` wrapper with auto token refresh for subagent-scoped calls. Test file `test/subagents.test.ts` validates provisioning, policy application, and cleanup flows.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: On-chain transaction signing through Intents API with guardrails
- **Wiki says:** The package provides Intents API integration for on-chain transaction signing with client-side guardrail validation.

- **Source evidence:** `README.md` lines 355-368 document `submitIntent()`, `validateIntent()`, and guardrail types. The flow accepts `{ to, value, chain }` intent objects, validates against `agentPolicy`, and submits via the 1Claw Intents API. Source file `src/intents/index.ts` implements `submitIntent()` returning `explorerUrl`. Source file `src/intents/guardrails.ts` implements `validateIntent()` with machine-readable error codes: `CHAIN_NOT_ALLOWED`, `VALUE_EXCEEDS_CAP`, `ADDRESS_NOT_ALLOWED`. Errors are typed as `GuardrailViolationError` in `src/errors.ts`. Test file `test/intents.test.ts` validates guardrail enforcement.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Audit log query helpers with cursor-based streaming
- **Wiki says:** The package provides audit log query helpers with cursor-based streaming for event history.

- **Source evidence:** `README.md` lines 370-378 document `recentEvents(20)` and `streamEvents(new Date("2026-01-01"))`. Source file `src/audit/index.ts` implements both synchronous batch and async streaming interfaces for audit log retrieval. The events return fields including `action`, `path`, and `outcome`. The architecture diagram in `README.md` lines 396-422 lists "Audit log query helpers with cursor-based streaming" under `src/audit/index.ts`.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: CMO talent subsystem for automated social media content
- **Wiki says:** The package contains a "CMO talent" subsystem for automated social media content generation and posting to X/Twitter and Telegram.

- **Source evidence:** Source files under `src/talents/cmo/` include: `persona.md` (brand voice definition), `style-notes.md` (writing style guide), `products.md` (product catalog), `campaign.md` (campaign templates), `draft-generator.ts` (content generation), `x-poster.ts` (X/Twitter posting via `twitter-api-v2`), `snap-poster.ts` (Telegram posting), `cli.ts` (CLI entry point), and `index.ts` (orchestration). The `build` script in `package.json` line 13 copies these Markdown files to `dist/talents/cmo/`. Test files `test/cmo.test.ts`, `test/snap-poster.test.ts`, `test/x-poster.test.ts` validate the subsystem. The `package.json` dependency `"twitter-api-v2": "^1.29.0"` confirms X/Twitter API integration.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[1claw-hermes]] -- Main wiki entry
- [[hermes-agent]] -- Hermes Agent upstream
- [[mcp]] -- Model Context Protocol
- [[hermes-workspace]] -- Hermes Workspace

## Cross-project

- [[hermes-agent.codegraph-verify]] -- Hermes Agent verification
- [[hermes-workspace.codegraph-verify]] -- Hermes Workspace verification
