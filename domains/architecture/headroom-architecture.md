---
name: headroom-architecture
tags: [headroom, architecture, llm, compression, context, proxy, mcp, memory, rust, python]
description: Architecture of Headroom — AI context compression layer reducing LLM token usage 60-95% via multi-compressor pipeline
source: sources/headroom/
---

# Headroom Architecture

## Overview

Headroom is a **context compression layer for AI agents** that reduces token usage by 60–95% without sacrificing answer quality. It compresses everything an AI agent reads — tool outputs, logs, RAG chunks, files, and conversation history — before it reaches the LLM. Headroom operates as a library (Python/TypeScript), a local proxy, an agent wrapper, an MCP server, and a cross-agent memory store. All processing is entirely local; data never leaves the user's machine.

## Architecture

```
Agent / App (Claude Code, Cursor, Codex, LangChain, Agno, etc.)
        │  prompts · tool outputs · logs · RAG chunks · files
        ▼
┌──────────────────────────────────────────────────────────┐
│  Headroom  (local — data stays on your machine)           │
│                                                           │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐   │
│  │ CacheAligner│  │ ContentRouter│  │ Live-Zone       │   │
│  │ KV cache    │  │ selects best │  │ compresses only │   │
│  │ stabilization│  │ compressor   │  │ new bytes       │   │
│  └─────────────┘  └──────┬───────┘  └────────────────┘   │
│                          │                                │
│           ┌──────────────┼──────────────┐                 │
│           ▼              ▼              ▼                 │
│  ┌────────────┐ ┌────────────┐ ┌──────────────┐          │
│  │SmartCrusher│ │  CodeComp  │ │ Kompress-v2  │          │
│  │ JSON 60-95%│ │   AST-aware│ │  ML text (HF)│          │
│  └────────────┘ └────────────┘ └──────────────┘          │
│  ┌────────────┐ ┌──────────────────────┐                  │
│  │ ImageComp  │ │  CCR (Reversible)    │                  │
│  │ ML 40-90%  │ │  store+retrieve      │                  │
│  └────────────┘ └──────────────────────┘                  │
│  ┌──────────────────────────────────────┐                 │
│  │  Cross-Agent Memory (shared store)   │                 │
│  └──────────────────────────────────────┘                 │
└──────────────────────────────────────────────────────────┘
        │  compressed prompt  +  retrieval tool
        ▼
LLM provider (Anthropic · OpenAI · Bedrock · Gemini · …)
```

### Compression Pipeline

The **ContentRouter** detects content type and selects the optimal compressor:

- **SmartCrusher** — Universal JSON compression for arrays, nested objects, tool outputs. Achieves 60–95% reduction on structured data like code search results and API responses.
- **CodeCompressor** — AST-aware compression for Python, JS/TS, Go, Rust, Java, C/C++, Perl. Strips boilerplate while preserving semantics (15–20% reduction).
- **Kompress-v2-base** — HuggingFace ML model trained on agentic traces for prose, conversation, and unstructured text.
- **ImageCompressor** — ML-based image reduction (40–90%) via trained router.

### Lifecycle & Pipeline Extensions

Headroom exposes a stable request lifecycle: `Setup → Pre-Start → Post-Start → Input Received → Input Cached → Input Routed → Input Compressed → Input Remembered → Pre-Send → Post-Send → Response Received`. Pipeline extensions (`on_pipeline_event(...)`) can observe or customize any stage.

## Key Components

- **CacheAligner** — Stabilizes prefix tokens so provider KV caches (Anthropic, OpenAI) actually hit, reducing per-turn input costs. Critical for long-running sessions.
- **Live-Zone Compression** — Compresses only fresh bytes while keeping frozen prefix byte-identical, preserving provider-side KV cache.
- **CCR (Context Compression with Retrieval)** — Reversible compression: originals cached locally with configurable TTL. LLM can call `headroom_retrieve` when full detail is needed.
- **Cross-Agent Memory** — Shared deduplicated context store across Claude, Codex, Gemini, and other agents with agent provenance tracking.
- **Rust core** (`crates/`) — High-performance compression primitives: `headroom-core`, `headroom-proxy`, `headroom-py` (Python bindings).
- **`headroom learn`** — Mines failed agent sessions, writes corrections to agent config files. Learns optimal verbosity from user interaction patterns.

### Integration Modes

| Mode | Usage | Zero Code Change |
|------|-------|:---:|
| Library | `compress(messages)` in Python/TS | ❌ |
| Proxy | `headroom proxy --port 8787` | ✅ |
| Agent Wrap | `headroom wrap claude\|opencode\|...` | ✅ |
| MCP Server | `headroom_compress` / `headroom_retrieve` tools | ✅ |

### Compression Benchmarks

| Workload | Before (tokens) | After (tokens) | Savings |
|----------|:-:|:-:|:-:|
| Code search (100 results) | 17,765 | 1,408 | **92%** |
| SRE incident debugging | 65,694 | 5,118 | **92%** |
| GitHub issue triage | 54,174 | 14,761 | **73%** |
| Codebase exploration | 78,502 | 41,254 | **47%** |

## Related

- [[headroom]] — Wiki overview of the project
- [[llmtrim]] — Tool compressor (complementary approach)
- [[hermes-agent]] — MCP hub integrating Headroom's tools
- [[openclaw]] — Rust agent platform with native Headroom plugin support
- [[opencode]] — AI coding agent wrappable by Headroom
- [[n8n]] — Workflow automation using Headroom MCP tools
