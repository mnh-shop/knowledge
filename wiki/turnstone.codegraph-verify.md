---
name: turnstone-codegraph-verify
tags: [turnstone, codegraph-verify, agent, framework]
description: "Codegraph Verification: turnstone — validating wiki claims against indexed source code symbols"
source: sources/turnstone/
---

# Codegraph Verification: turnstone

**Date:** 2026-07-12

## Claim 1: Formal agent-harness theory documented in PRIMER.md and HYPOTHESIS.md
- **Wiki says:** "Implements a formal theory of agent harnesses documented in `PRIMER.md` and `HYPOTHESIS.md`. Core principle: the model proposes; the gate disposes — every model output is treated as a suggestion that must pass through deterministic gating."
- **Source evidence:**
  - `PRIMER.md` — 24,740 bytes plain-language companion to the formal harness theory
  - `HYPOTHESIS.md` — 102,477 bytes formal definition of agent harness invariants, symbols, certificates, falsifiers, and citations
  - `lint_hypothesis.py` — 9,171 bytes consistency linter for HYPOTHESIS.md
  - `turnstone/core/session.py:3067` — References HYPOTHESIS.md effect-record disposition semantics
  - `turnstone/core/session.py:6363` — Effect disposition appendix: "unknown, never none"
  - `turnstone/core/trajectory.py:47` — "unknown vs none split is the load-bearing one (HYPOTHESIS.md)"
  - `tests/test_cancel.py:905` — Test references HYPOTHESIS.md effect-record appendix
  - `README.md:24` — Links to PRIMER.md as the entry point
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Intent Validation Judge with heuristic and LLM-based verdicts
- **Wiki says:** "An LLM judge grades every tool call with a risk assessment and evidence before execution. The judge can only veto (tighten), never approve (widen). Judgments are drawn from a fixed, shell-owned menu of refusal reasons."
- **Source evidence:**
  - `turnstone/core/judge.py` — 1,785 lines of Intent validation: `IntentVerdict` dataclass (line 43) with verdict_id, call_id, risk_level, confidence, recommendation, reasoning, evidence
  - `turnstone/core/judge.py:56` — `tier` field: "heuristic" | "llm" | "arbitrated"
  - `turnstone/core/judge.py:80` — `JudgeConfig` class for judge configuration
  - `turnstone/core/output_guard_judge.py` — Output guard judge for model outputs
  - `turnstone/core/output_guard.py` — Output guard framework
  - `turnstone/core/tool_advisory.py` — Tool advisory system for risk assessment
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: MCP support with native deferred loading and BM25 fallback
- **Wiki says:** "MCP Support — External tool servers via native deferred loading (Anthropic/OpenAI style) or BM25 fallback for tool discovery."
- **Source evidence:**
  - `turnstone/core/mcp_client.py` — 7,287 lines: Full MCP client implementation with `ClientSession`, `StdioServerParameters`, `streamablehttp_client`, async-to-sync bridging via daemon thread event loop
  - `turnstone/core/mcp_registry.py` — 570 lines: MCP Registry API client for server discovery at `registry.modelcontextprotocol.io`
  - `turnstone/core/mcp_oauth.py` — MCP OAuth support with `TokenLookupResult`, `get_user_access_token_classified`
  - `turnstone/core/mcp_http_parsers.py` — HTTP transport parsers for MCP protocol
  - `turnstone/core/mcp_crypto.py` — MCP cryptographic operations
  - `turnstone/core/bm25.py` — BM25 fallback for tool discovery when native loading unavailable
  - `turnstone/core/tool_search.py` — Tool search and discovery
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Multi-node cluster with rendezvous routing proxy (HRW hashing)
- **Wiki says:** "Rendezvous routing proxy (HRW hashing) that maps workstreams to server nodes deterministically without stored bucket state. A node join or drop only re-routes keys affected by the change."
- **Source evidence:**
  - `turnstone/core/rendezvous.py` — HRW (Highest Random Weight) hashing implementation for rendezvous routing
  - `turnstone/console/router.py` — Console routing proxy for multi-node cluster
  - `turnstone/console/coordinator_client.py` — Coordinator client for node communication
  - `turnstone/console/coordinator_adapter.py` — Coordinator adapter
  - `turnstone/console/server.py:1` — 14,577 lines console server with cluster management
  - `turnstone/console/session_factory.py` — Session factory for multi-node sessions
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Built-in tool suite with 29 tool definitions
- **Wiki says:** "Built-in Tool Suite — Shell execution, file manipulation, web search, web browsing, memory management, notification dispatch, and autonomous sub-agent spawning."
- **Source evidence:**
  - `turnstone/tools/` — 29 JSON tool definitions: `bash.json`, `write_file.json`, `read_file.json`, `edit_file.json`, `diff_file.json`, `web_fetch.json`, `web_search.json`, `search.json`, `memory.json`, `recall.json`, `notify.json`, `spawn_workstream.json`, `spawn_batch.json`, `close_workstream.json`, `close_all_children.json`, `delete_workstream.json`, `list_workstreams.json`, `list_nodes.json`, `send_to_workstream.json`, `watch.json`, `inspect_workstream.json`, `cancel_workstream.json`, `wait_for_workstream.json`, `open_preview.json`, `read_resource.json`, `skills.json`, `task_agent.json`, `tasks.json`, `use_prompt.json`
  - `turnstone/core/tools.py` — Tool loading system: `_load_tools()` loads all `.json` files from `turnstone/tools/`
  - `turnstone/core/tools.py:35` — Returns `(tool_defs, metadata)` with full OpenAI function-calling schemas
  - `turnstone/core/mcp_client.py` — MCP tool integration for external servers
- **Verdict:** ✅ CORRECT (29 tool definitions confirmed)
- **Fix needed:** None

## Claim 6: Governance and RBAC with SSO (OIDC), audit logs, and PostgreSQL
- **Wiki says:** "Optional role-based access control, SSO (OIDC), tool-level policies, and audit logs, all stored in your own PostgreSQL database."
- **Source evidence:**
  - `turnstone/core/auth.py` — Authentication system
  - `turnstone/core/oidc.py` — OpenID Connect SSO integration
  - `turnstone/core/policy.py` — Tool-level policy engine
  - `turnstone/core/rule_registry.py` — Rule registry for access control
  - `turnstone/core/settings_registry.py` — Settings management
  - `turnstone/core/audit.py` — Audit logging module
  - `turnstone/core/tls.py` — TLS certificate management
  - `turnstone/core/tls_store.py` — TLS certificate store
  - `turnstone/admin.py` — Admin CLI for user/token management (580+ lines)
  - `compose.yaml` — Docker Compose with PostgreSQL configuration
  - `deploy/` — Production deployment manifests
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Multi-provider LLM support (OpenAI, Anthropic, Gemini, mixable per role)
- **Wiki says:** "Supports OpenAI-compatible APIs (vLLM, llama.cpp, NIM), Anthropic Messages API, and Google Gemini, mixable freely per role."
- **Source evidence:**
  - `turnstone/core/providers/` — 9 provider modules: `_anthropic.py`, `_google.py`, `_openai_chat.py`, `_openai_common.py`, `_openai_responses.py`, `_openai.py`, `_xai.py`, `_protocol.py`, `effort_ladder.py`
  - `turnstone/core/model_registry.py` — Model discovery and registry
  - `turnstone/core/providers/_protocol.py` — `LLMProvider` protocol interface
  - `turnstone/core/providers/effort_ladder.py` — Effort-based model selection
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 7 key claims from the Turnstone wiki have been verified against the source code:
- ✅ **Formal harness theory:** PRIMER.md (24KB) + HYPOTHESIS.md (102KB) + lint_hypothesis.py confirmed
- ✅ **Intent Validation Judge:** `core/judge.py` with heuristic/LLM/arbitrated tiers confirmed
- ✅ **MCP support:** 7,287-line `mcp_client.py` + registry + OAuth + BM25 fallback confirmed
- ✅ **Multi-node cluster:** Rendezvous HRW hashing in `core/rendezvous.py` + console router confirmed
- ✅ **Built-in tools:** 29 JSON tool definitions loaded by `core/tools.py` confirmed
- ✅ **Governance/RBAC:** OIDC, policy engine, audit logs, TLS, PostgreSQL confirmed
- ✅ **Multi-provider LLM:** 9 provider modules covering Anthropic, OpenAI, Google, xAI confirmed

## Related

- [[turnstone]] -- Main wiki entry

## Cross-project

- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for Hermes Agent
- [[nanobot.codegraph-verify]] -- Similar codegraph verification for Nanobot
- [[shannon.codegraph-verify]] -- Similar codegraph verification for Shannon
