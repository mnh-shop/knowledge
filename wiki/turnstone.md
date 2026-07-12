---
name: turnstone
tags: [turnstone, ai-agents, agent-framework, autonomous, orchestration]
description: "Agent framework for building and deploying autonomous AI workers"
source: sources/turnstone/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Turnstone

| Field | Value |
|---|---|
| **Origin** | [cf-toolsuite/turnstone](https://github.com/cf-toolsuite/turnstone) |
| **Source** | `sources/turnstone/` |
| **Repomix** | `raw/turnstone/turnstone.xml` |
| **Codegraph** | `graphs/turnstone/` |

## Overview

Turnstone is a self-hosted, local-first orchestration platform for tool-using AI agents. It gives LLMs real tools — shell, files, search, web, planning — and orchestrates multi-turn conversations where the model investigates, acts, and reports. Named after the Ruddy Turnstone (*Arenaria interpres*), a shorebird that flips stones to discover what's hiding underneath, the project emphasizes privacy, self-sovereignty, and rigorous agent-harness theory.

At its core, Turnstone implements a formal theory of agent harnesses documented in `PRIMER.md` and `HYPOTHESIS.md`. The core principle is that **the model proposes; the gate disposes** — every model output is treated as a suggestion that must pass through deterministic gating before any side effect executes. This architecture provides verifiable safety guarantees: replay invariance, deterministic tool approval, and a clear separation between untrusted content (model outputs, fetched pages) and control state (plans, permissions, authorization grants).

The platform is Apache 2.0 licensed (as of v1.6.0), runs entirely on hardware the user controls with no telemetry or phone-home, and supports OpenAI-compatible APIs (vLLM, llama.cpp, NIM), Anthropic Messages API, and Google Gemini, mixable freely per role.

## Key Features

- **Local-First and Private** — Runs entirely on your own hardware with no telemetry. Point it at local models (vLLM, llama.cpp) or commercial APIs you hold the keys to. Prompts and data never transit a third party you did not choose
- **Intent Validation (Judge)** — An LLM judge grades every tool call with a risk assessment and evidence before execution. The judge can only veto (tighten), never approve (widen). Judgments are drawn from a fixed, shell-owned menu of refusal reasons — never free-text prose — to prevent injection through the judge itself
- **MCP Support** — External tool servers via native deferred loading (Anthropic/OpenAI style) or BM25 fallback for tool discovery
- **Multi-Node Cluster** — Rendezvous routing proxy (HRW hashing) that maps workstreams to server nodes deterministically without stored bucket state. A node join or drop only re-routes keys affected by the change
- **Interactive Sessions** — Terminal CLI (REPL), browser UI with parallel workstreams, and a cluster dashboard with real-time view of every node and workstream
- **Built-in Tool Suite** — Shell execution, file manipulation, web search, web browsing, memory management, notification dispatch, and autonomous sub-agent spawning
- **Governance and RBAC** — Optional role-based access control, SSO (OIDC), tool-level policies, and audit logs, all stored in your own PostgreSQL database
- **Evaluation Harness** — `turnstone-eval` scores tool-use against expected actions, and `turnstone-optimizer` runs a UCB self-modify loop over the eval substrate to optimize prompts and tool configurations
- **Channel Integrations** — Discord and Slack adapters via `turnstone-channel` gateway

## Architecture

Turnstone's architecture follows a hub-and-spoke model with clearly separated components:

```
Components:
├── turnstone              — Terminal CLI (REPL)
├── turnstone-server       — Web UI + REST API + SSE event stream
├── turnstone-console      — Cluster dashboard + rendezvous routing proxy + admin panel
├── turnstone-channel      — Channel gateway (Discord, Slack adapters)
├── turnstone-admin        — User/token management CLI
├── turnstone-eval         — Headless eval harness for measuring tool-use performance
├── turnstone-optimizer    — Prompt/tool optimizer with UCB self-modification
└── turnstone-doctor       — LLM-backed cluster diagnostics (read-only)
```

The internal structure is modular:

```
turnstone/
├── api/           — REST API definitions
├── channels/      — Channel adapters (Discord, Slack)
├── console/       — Dashboard and admin panel
├── core/          — Engine: SessionUI, ChatSession, LLMProvider, state machines
├── deploy/        — Production Docker Compose deployment manifests
├── prompts/       — Prompt templates and system messages
├── sdk/           — Python SDK for programmatic access
├── tools/         — Built-in and MCP tool implementations
└── ui/            — Terminal and browser UI components
```

### The Harness Theory

Turnstone's architecture is grounded in a formal theory of agent harnesses. The key invariants:

1. **The model sees only what the prompt builder shows it** — never raw memory. A secret that never enters the prompt cannot leak through the model
2. **Model outputs are proposals, not actions** — every model output is a suggestion that must pass through deterministic gating
3. **Every side effect passes the gate** — there is no second path from model text to world action
4. **The harness flips no coins** — replay a step with the model's answer and tool results pinned, and behavior must be identical

Memory is partitioned into **data** (tool results, fetched pages, retrieved documents — content the world supplied) and **control** (the plan, permissions, what is authorized). Untrusted content always lands in data, never control. Only the owner can widen permissions — asking the owner is itself an ordinary tool call, and the owner's answer is the one kind of tool result allowed to change control.

### Deployment Models

**Single-node:** Client → Server (direct HTTP + SSE), no external dependencies beyond the database.

**Multi-node:** Client → Console (rendezvous routing proxy) → Server nodes. The console picks the target node for each workstream via HRW hashing over the live service registry — a pure function of `(ws_id, live_nodes)` that requires no stored bucket state.

**Docker deployment:** One-line install via `curl -fsSL https://raw.githubusercontent.com/turnstonelabs/turnstone/main/run.sh | bash` autodetects the distro, installs git + Docker if missing, generates secrets, and starts the full stack — PostgreSQL, console, Caddy, channel gateway, and 10 server nodes — with no `.env` required (ships with insecure dev defaults).

## Release Tracks

| Track | Install | Description |
|---|---|---|
| **Stable** | `pip install turnstone` | Production-grade, bugfixes only |
| **Experimental** | `pip install turnstone --pre` | New features, may have rough edges |
| **Docker** | `ghcr.io/turnstonelabs/turnstone:stable` | Container images for both tracks |

## Tools and MCP Integration

Built-in tools cover shell, files, search, web, memory, notifications, and autonomous sub-agents. External tools are integrated via MCP with native deferred loading — tools are fetched lazily when first needed rather than being pre-loaded into context. MCP tools are indexed through BM25 fallback for discovery when the Anthropic/OpenAI native loading mode is unavailable.

## Related

- [[hermes-agent]] — Production agent gateway with skill system and delegation, complementary to Turnstone's orchestration focus
- [[nanobot]] — Agent framework for building autonomous workers in a similar category to Turnstone's worker agents
- [[shannon]] — AI agent runtime and orchestration platform with multi-agent workflow capabilities
- [[materia]] — Agent framework with composable pipelines that shares Turnstone's emphasis on modular agent construction
- [[pi]] — TypeScript agent harness with similar tool-use abstraction patterns
- [[openclaw]] — Personal AI assistant that could integrate Turnstone's orchestration capabilities
