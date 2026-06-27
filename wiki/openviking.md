---
name: openviking
description: "Context Database for AI Agents — filesystem-paradigm memory, resource, and skill management with tiered retrieval"
tags: [wiki, ai-agents, python, rust, typescript, openviking]
source: sources/OpenViking/
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

### Core Components

```
openviking/                  # Python server package
├── async_client.py          # Singleton async client (embedded mode)
├── sync_client.py           # Synchronous client wrapper
├── client/                  # Client implementations (LocalClient, ServerClient)
├── server/                  # HTTP server (FastAPI-based)
├── storage/                 # VikingFS — virtual filesystem backend
├── service/                 # Business logic services
├── session/                 # Session management and memory iteration
├── retrieve/                # Retrieval engine (directory-recursive search)
├── parse/                   # Content parsing and extraction
├── resource/                # Resource management (files, URLs)
├── core/                    # Core abstractions (BaseClient, content types)
├── models/                  # Data models and schemas
├── crypto/                  # Encryption and security
├── privacy/                 # Privacy controls
├── telemetry/               # Operation telemetry
├── metrics/                 # Performance metrics
├── observability/           # Observability (OpenTelemetry, logging)
└── prompts/                 # LLM prompt templates

crates/                      # Rust sub-projects (Cargo workspace)
├── ov_cli/                  # CLI tool (npm/cargo installable)
├── ragfs/                   # Core filesystem engine
├── ragfs-cache-mooncake/    # Mooncake caching for RAGFS
├── ragfs-cache-redis/       # Redis caching for RAGFS
├── ragfs-cache-yuanrong/    # Yuanrong caching for RAGFS
├── ragfs-cache-yuanrong-sys/# Yuanrong system bindings
├── ragfs-python/            # Python bindings for RAGFS
└── ragfs-python-native/     # Native Python bindings for RAGFS

sdk/python/                  # Python SDK for programmatic access
examples/                    # Usage examples
web-studio/                  # Web-based UI
bot/                         # VikingBot agent framework
```

### Storage Paradigm — Viking URI

```
viking://
├── resources/               # Project docs, repos, web pages
│   ├── my_project/
│   │   ├── docs/
│   │   └── src/
├── user/                    # User preferences, habits
│   └── {user_id}/
│       ├── memories/
│       ├── resources/
│       ├── skills/
│       └── peers/
```

### Context Layers (L0/L1/L2)

```
viking://resources/my_project/
├── .abstract                # L0: ~100 tokens — quick relevance check
├── .overview                # L1: ~2k tokens — structure and key points
├── docs/
│   ├── .abstract
│   ├── .overview
│   ├── api/
│   │   ├── auth.md          # L2: full content — loaded on demand
│   │   └── endpoints.md
```

### Deployment Modes

- **Docker** — Official Dockerfile and `docker-compose.yml` for containerized deployment
- **Caddy** — Included `Caddyfile` for reverse proxy with TLS
- **ECS** — Recommended deployment on Volcengine Elastic Compute Service (veLinux)
- **Local** — `pip install openviking` and `openviking-server` CLI

## Quick Start

```bash
# Install Python server
pip install openviking --upgrade --force-reinstall

# Install Rust CLI (optional)
npm i -g @openviking/cli
# or: cargo install --git https://github.com/volcengine/OpenViking ov_cli

# Configure and validate
openviking-server init
openviking-server doctor

# Launch server
openviking-server

# Add resources and search
ov add-resource https://github.com/volcengine/OpenViking
ov ls viking://resources/
ov find "what is openviking"
```

For VikingBot (AI agent framework):

```bash
pip install "openviking[bot]"
openviking-server --with-bot
ov chat
```

## Evaluation Highlights

OpenViking 0.3.22 demonstrates significant improvements across three benchmarks:

| Scenario | Metric | Improvement |
|---|---|---|
| **User Memory (LoCoMo)** | OpenClaw +3.39x accuracy, -91% tokens | 24.2% -> 82.08% accuracy |
| **Agent Memory (tau2-bench)** | +6.87pp retail, +11.87pp airline | Task success improvement |
| **Knowledge QA (HotpotQA)** | 91% accuracy at 0.23s latency | top-20 retrieval |

## Related

- [[hermes-agent]] — AI agent with MCP integration, can use OpenViking for memory
- [[openclaw]] — Personal AI assistant agent gateway, tested with OpenViking memory
- [[nanobot]] — Foundational agent framework that VikingBot extends
- [[mcp]] — Model Context Protocol for tool integration
- [[mission-control]] — Agent orchestration that can integrate with OpenViking resources
- [[n8n]] — Workflow automation that can connect to OpenViking resources

## Links

- **GitHub**: [github.com/volcengine/OpenViking](https://github.com/volcengine/OpenViking)
- **Website**: [openviking.ai](https://www.openviking.ai)
- **Paper**: [VikingMem on arXiv](https://arxiv.org/abs/2605.29640) (VLDB 2026)
- **Docs**: [Full Documentation](https://www.openviking.ai/docs)
- **Discord**: [Join Discord](https://discord.com/invite/eHvx8E9XF3)
- **X/Twitter**: [@openvikingai](https://x.com/openvikingai)
