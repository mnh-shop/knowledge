---
name: OpenViking
description: "Context Database for AI Agents — filesystem-paradigm memory, resource, and skill management with tiered retrieval"
source: sources/OpenViking/
tags: [OpenViking, agent, ai-agents, cli, mcp, python, rust, typescript, storage]
---

# OpenViking — Context Database for AI Agents

| Field | Value |
|---|---|
| **Origin** | [volcengine/OpenViking](https://github.com/volcengine/OpenViking) |
| **License** | AGPL-3.0 (main project); Apache 2.0 (crates, examples) |
| **Stack** | Python 3.10+, Rust (RAGFS, CLI), TypeScript (web-studio) |
| **Source** | `sources/OpenViking/` |

## Description

OpenViking is an open-source **Context Database** designed specifically for AI Agents, developed by ByteDance/Volcengine. It replaces traditional fragmented vector storage with a **filesystem paradigm** (`viking://` URIs) to unify the structured organization of memories, resources, and skills. It features a three-tier context loading system (L0/L1/L2), directory-recursive retrieval combining vector search with hierarchical navigation, and automated session management with memory self-iteration. The project includes a Python server, a Rust CLI (`ov_cli`), an SDK, and a web studio UI.

The project is backed by academic research published as the **VikingMem** paper (accepted by VLDB 2026).

## Key Features

- **Filesystem Management Paradigm** — Unified context as a virtual filesystem (`viking://` URIs) for memories, resources, and skills
- **Tiered Context Loading** — L0 (abstract), L1 (overview), L2 (full detail) loaded on demand to reduce token consumption
- **Directory Recursive Retrieval** — Intent analysis, initial vector positioning, refined secondary retrieval, recursive drill-down, and result aggregation
- **Observable Retrieval Trajectory** — Full preservation of retrieval decision paths for debugging and optimization
- **Automatic Session Management** — Archives conversations, compresses content, extracts long-term memories
- **Multi-Provider VLM Support** — Volcengine (Doubao), OpenAI, OpenAI Codex (OAuth), Kimi Coding, GLM/Z.AI Coding Plan, Ollama (local)
- **Multi-Provider Embedding Support** — Volcengine, OpenAI, Azure, Jina, Ollama, Voyage, DashScope, MiniMax, Cohere, VikingDB, Gemini, LiteLLM, local
- **VikingBot** — Built-in AI agent framework for conversational interaction
- **OpenViking Personal** — Hosted commercial version (free tier for up to 50 files)

## Architecture

OpenViking follows a **three-tier context loading model** (L0/L1/L2):
- **L0 (`.abstract`)**: ~100 tokens for quick relevance checks
- **L1 (`.overview`)**: ~2k tokens with structure and key points  
- **L2**: Full content loaded on demand

**Storage paradigm**: Uses `viking://` virtual filesystem URIs to organize memories, resources, and skills hierarchically.

### Core Components

- **Python server** (`openviking/`): FastAPI-based HTTP server, VikingFS storage backend
- **Rust CLI** (`ov_cli`): `ov` command for resource management and search
- **RAGFS** (`crates/ragfs`): Core filesystem engine with caching adapters
- **VikingBot** (`bot/`): Built-in AI agent framework
- **Web Studio** (`web-studio/`): Browser-based UI

## Deployment

```bash
pip install openviking
openviking-server init && openviking-server doctor
openviking-server  # launches server
ov add-resource https://github.com/volcengine/OpenViking  # add via CLI
```

## Evaluation

| Scenario | Result |
|---|---|
| **User Memory (LoCoMo)** | 24.2% -> 82.08% accuracy (+3.39x) |
| **Agent Memory (tau2-bench)** | +6.87pp retail, +11.87pp airline |
| **Knowledge QA (HotpotQA)** | 91% accuracy at 0.23s latency |

Published as **VikingMem** (VLDB 2026).

## Related

- [[hermes-agent]] — AI agent with MCP integration
- [[openclaw]] — Agent gateway tested with OpenViking
- [[nanobot]] — Foundational agent framework
- [[mcp]] — Model Context Protocol integration

## Links

- **GitHub**: [volcengine/OpenViking](https://github.com/volcengine/OpenViking)
- **Website**: [openviking.ai](https://www.openviking.ai)
- **Paper**: [VikingMem (arXiv:2605.29640)](https://arxiv.org/abs/2605.29640)
