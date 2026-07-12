---
name: headroom
tags: [headroom, context-compression, ai-agents, llm, tokens, proxy, mcp, memory]
description: "Context compression layer for AI agents — reduces LLM token usage 60-95% while preserving answer quality"
source: sources/headroom/
verification_date: 2026-07-12
verified_by: fixer (source analysis)
source_reference: sources/headroom/README.md
---

# Headroom

| Field | Value |
|---|---|
| **Origin** | [chopratejas/headroom](https://github.com/chopratejas/headroom) |
| **License** | Apache-2.0 |
| **Stack** | Python (core), TypeScript (SDK), Rust (memory), ONNX (ML compression) |
| **Source** | `sources/headroom/` |
| **Repomix** | `raw/headroom/headroom.xml` |
| **Codegraph** | `graphs/headroom/` |

## Overview

Headroom is a context compression layer for AI agents that reduces token usage by 60–95% without sacrificing answer quality. It compresses everything an AI agent reads — tool outputs, logs, RAG chunks, files, and conversation history — before it reaches the LLM. Headroom operates as a library, a local proxy, an agent wrapper, an MCP server, and a cross-agent memory store.

The core insight behind Headroom is that a large fraction of tokens sent to LLMs are redundant — verbose tool outputs, repetitive log lines, boilerplate file contents, and restated context. Headroom's **ContentRouter** detects the type of content, selects the best compressor (JSON crusher, AST-aware code compressor, ML text compressor, or image compressor), and produces a compressed representation. A reversible **CCR (Context Compression with Retrieval)** system caches the originals locally so the LLM can retrieve full details on demand.

Headroom runs **entirely locally** — all data stays on the user's machine. The proxy mode requires zero code changes: any OpenAI-compatible client can route through it. Agent wrapping via `headroom wrap <agent>` injects configuration for Claude Code, Codex, Cursor, Copilot CLI, Aider, OpenClaw, OpenCode, Cline, Continue, Goose, OpenHands, and many more.

## Key Features

- **Library Mode** — `compress(messages)` in Python or TypeScript, inline in any application. Integrates with Anthropic SDK, OpenAI SDK, Vercel AI SDK, LiteLLM, LangChain, and Agno.
- **Proxy Mode** — `headroom proxy --port 8787` runs a local HTTP proxy that intercepts and compresses all LLM traffic. Zero code changes, works with any OpenAI-compatible client.
- **Agent Wrapping** — `headroom wrap claude|copilot|codex|opencode|openclaw|cursor|aider|...` configures and launches a wrapped agent session with compression preconfigured.
- **MCP Server** — Provides `headroom_compress`, `headroom_retrieve`, and `headroom_stats` tools for any MCP client.
- **Content-Aware Compression** — ContentRouter automatically selects the optimal compressor:
  - **SmartCrusher** — universal JSON compression for arrays, nested objects, mixed types (60–95% reduction)
  - **CodeCompressor** — AST-aware compression for Python, JS/TS, Go, Rust, Java, C/C++, Perl (15–20% reduction)
  - **Kompress-v2-base** — HuggingFace model trained on agentic traces for prose and conversation
  - **Image compression** — 40–90% reduction via trained ML router
- **CacheAligner** — Stabilizes prefix tokens so provider KV caches (Anthropic, OpenAI) actually hit, reducing per-turn input costs.
- **Live-Zone Compression** — Compresses only new bytes (fresh tool output, latest conversation turn) while keeping frozen prefix byte-identical so provider-side cache is preserved and never busted.
- **Reversible Compression (CCR)** — Originals cached locally; LLM can call `headroom_retrieve` when full detail is needed. Originals are retrievable within configured TTL.
- **Cross-Agent Memory** — Shared context store across Claude, Codex, Gemini, and other agents with automatic deduplication and agent provenance tracking.
- **SharedContext** — Compressed context passing across multi-agent workflows and pipelines.
- **`headroom learn`** — Mines failed agent sessions, writes corrections to `CLAUDE.local.md`, `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`. Also learns optimal verbosity from user interaction patterns.
- **Output Token Reduction** — Trims what the model writes back via verbosity steering and effort routing, with measured savings and confidence intervals.
- **Output Savings Dashboard** — `headroom dashboard` and `headroom savings` provide live compression analytics, token savings, and dollar cost tracking (via LiteLLM pricing).
- **Pipeline Extensions** — Observable lifecycle with hooks for `on_pipeline_event(...)` to customize compression behavior.

## Architecture

```
 Agent / App (Claude Code, Cursor, Codex, LangChain, Agno, etc.)
       │  prompts · tool outputs · logs · RAG · files
       ▼
 ┌────────────────────────────────────────────────────┐
 │  Headroom   (local — data stays on your machine)   │
 │  ├─ CacheAligner       — stabilizes KV cache hits  │
 │  ├─ ContentRouter      — selects optimal compressor│
 │  ├─ SmartCrusher       — JSON compression          │
 │  ├─ CodeCompressor     — AST-aware code reduction  │
 │  ├─ Kompress-v2-base   — ML text compressor (HF)   │
 │  ├─ ImageCompressor    — ML image reduction        │
 │  ├─ CCR                — reversible storage cache  │
 │  └─ CrossAgent Memory  — shared deduplicated store │
 └────────────────────────────────────────────────────┘
       │  compressed prompt  +  retrieval tool
       ▼
 LLM provider (Anthropic · OpenAI · Bedrock · …)
```

Headroom exposes one stable request lifecycle: `Setup → Pre-Start → Post-Start → Input Received → Input Cached → Input Routed → Input Compressed → Input Remembered → Pre-Send → Post-Send → Response Received`. Pipeline extensions can observe or customize any stage.

Provider-specific behavior lives under `headroom/providers/` (Claude, Codex, Copilot, Gemini, OpenClaw) so core orchestration stays focused on lifecycle and sequencing.

## Compression Performance

| Workload | Before (tokens) | After (tokens) | Savings |
|---|---|---|---|
| Code search (100 results) | 17,765 | 1,408 | **92%** |
| SRE incident debugging | 65,694 | 5,118 | **92%** |
| GitHub issue triage | 54,174 | 14,761 | **73%** |
| Codebase exploration | 78,502 | 41,254 | **47%** |

Accuracy is preserved on standard benchmarks: GSM8K (±0.000), TruthfulQA (+0.030), SQuAD v2 (97% with 19% compression), BFCL (97% with 32% compression).

## Usage / Integration

- **With [[opencode]]** — `headroom wrap opencode` injects configuration and starts the proxy with OpenCode integration.
- **With [[openclaw]]** — `headroom wrap openclaw` installs Headroom as a ContextEngine plugin for the Rust agent platform.
- **With [[hermes-agent]]** — Hermes MCP hub can use Headroom's MCP server tools for context compression across 49+ tools.
- **With [[clawpier]] or [[goclaw]]** — Route MCP-based agent platforms through Headroom proxy for transparent compression.
- **With [[pip]] based agents** — Headroom wraps any OpenAI-compatible agent, including self-built Python agents using the `compress()` library function.
- **Multi-agent systems with [[n8n]]** — Use Headroom's MCP server tools within n8n workflows for compressed AI steps.
- **With [[oh-my-hermes]] plugins** — Compress agent context in OMH plugin system environments.
- **As standalone library** — `import headroom; compress(messages)` for Python or TypeScript applications.

**Quickstart:**
```bash
pip install "headroom-ai[all]"
headroom wrap claude                    # wrap Claude Code with compression
headroom proxy --port 8787              # run as proxy, zero code changes
headroom doctor                         # health check
headroom dashboard                      # live savings dashboard
```

## Related

- [[opencode]] — AI coding agent that can be wrapped by Headroom for compressed context
- [[openclaw]] — Rust agent platform with native Headroom plugin support
- [[hermes-agent]] — MCP hub that integrates with Headroom's MCP server tools
- [[clawpier]] — Desktop GUI agent platform compatible with Headroom compression
- [[goclaw]] — Go MCP gateway that can route through Headroom proxy
- [[n8n]] — Workflow automation that can use Headroom MCP tools for compressed AI steps
- [[oh-my-hermes]] — Plugin system for Hermes that can incorporate Headroom memory
- [[pi]] — TypeScript agent harness compatible with Headroom library mode
