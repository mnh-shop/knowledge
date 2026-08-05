---
title: OpenViking.codegraph-verify
description: "Source-level verification of OpenViking — Context Database for AI Agents"
date: 2026-07-12
tags: [openviking, codegraph-verify, forensics, data, AI, context-database]
verified_by: codegraph-explore
source: sources/OpenViking/
---

# OpenViking — CodeGraph Verification

**Claim-1: OpenViking is an open-source Context Database for AI Agents, using a file-system paradigm (`viking://` URIs) to unify memories, resources, and skills.**

- **Evidence:** `README.md` line 34 states "OpenViking is an open-source context database for AI agents. It stores memories, resources, and skills as one virtual filesystem under the `viking://` protocol". Line 42 confirms "Memories, resources, and skills each get a `viking://` URI." The virtual filesystem hierarchy (`viking://resources/`, `viking://user/{user_id}/memories/`, `skills/`, `peers/`) is diagrammed at lines 50-71.
- **Source path:** `sources/OpenViking/README.md`

**Claim-2: OpenViking implements a tiered context loading system (L0/L1/L2) to reduce token consumption in agent prompts.**

- **Evidence:** `README.md` line 34 describes content "processed into three tiers — L0 abstract, L1 overview, L2 details — and loaded on demand." Lines 73-77 define the tiers ("L0 (Abstract): a one-sentence summary for quick relevance checks", "L1 (Overview): core information and usage scenarios for planning", "L2 (Details): the full original data, read only when needed"). A concrete `.abstract`/`.overview` file example is shown at lines 79-91, with L0 ≈ 100 tokens and L1 ≈ 2k tokens.
- **Source path:** `sources/OpenViking/README.md`

**Claim-3: OpenViking provides directory-recursive retrieval (vector search + hierarchical drill-down) with observable retrieval trajectories.**

- **Evidence:** `README.md` line 44: "Directory recursive retrieval. Vector search first locates the highest-scoring directory, then drills down layer by layer, so results arrive with their surrounding context intact." Line 45: "Observable retrieval. Each query preserves its directory-browsing trajectory... you can see exactly which path produced it."
- **Source path:** `sources/OpenViking/README.md`

**Claim-4: OpenViking's benchmark results (LoCoMo, tau2-bench) are reported in the README; knowledge-base QA (incl. HotpotQA) is only covered in an external benchmark report.**

- **Evidence:** `README.md` lines 95-103 present the benchmark section: line 95 references the external [benchmark report](https://blog.openviking.ai/post/openviking-benchmark-results/) "including knowledge-base QA" and points reproduction scripts to `./benchmark`; line 99's chart alt text gives LoCoMo accuracy (OpenClaw 24.20% → 82.08%, Hermes 33.38% → 82.86%, Claude Code 57.21% → 80.32%); line 102 reports input tokens down 34.3-91.0% and latency down 58.45-66.10%; line 103 reports tau2-bench task success +6.87pp (retail) and +11.87pp (airline). No HotpotQA / 91% / 0.23s figure exists anywhere in the repo — earlier wiki claims citing README lines 659-670 refer to a longer README that no longer exists.
- **Source path:** `sources/OpenViking/README.md`; external: `https://blog.openviking.ai/post/openviking-benchmark-results/`

**Claim-5: The Rust workspace has 8 entries — 4 crates in `members` plus 4 excluded experimental crates.**

- **Evidence:** `Cargo.toml` lines 2-13: `members = ["crates/ov_cli", "crates/ragfs", "crates/ragfs-cache-redis", "crates/ragfs-python"]` (4 members) and `exclude = ["crates/ragfs-cache-mooncake", "crates/ragfs-cache-yuanrong", "crates/ragfs-cache-yuanrong-sys", "crates/ragfs-python-native"]` (4 excluded) — 8 total. `crates/ragfs/Cargo.toml` description (line 9): "Rust implementation of AGFS - Aggregated File System for AI Agents". `crates/ov_cli/Cargo.toml` defines bin `ov` (lines 9-11). `pyproject.toml` line 204 maps the `ov` script to `openviking_cli.rust_cli:main` and line 207 maps `vikingbot` to `vikingbot.cli.commands:app`.
- **Source path:** `sources/OpenViking/Cargo.toml`, `sources/OpenViking/crates/ragfs/Cargo.toml`, `sources/OpenViking/crates/ov_cli/Cargo.toml`, `sources/OpenViking/pyproject.toml`

**Claim-6: OpenViking ships a FastAPI Python server, three language SDKs, a C++ ABI engine, a React web studio, and a multi-suite benchmark directory.**

- **Evidence:** `pyproject.toml` line 56 pins `fastapi>=0.128.0` (line 57 `uvicorn`), with the HTTP server in `openviking/server/routers/` (26 router modules incl. `filesystem.py`, `resources.py`, `search.py`, `sessions.py`, `skills.py`). `sdk/` contains `go/`, `python/`, `typescript/` client libraries. `src/` holds the C++ ABI engine (`CMakeLists.txt`, `abi3_engine_backend.cpp`, `abi3_x86_caps.cpp`, `index/`, `store/`), packaged as `storage/vectordb/engine/*.abi3.so` per `pyproject.toml` line 229. `web-studio/` is a Vite/TypeScript React app. `benchmark/` contains `locomo/`, `tau2/`, `RAG/`, `retrieval/`, `skillsbench/`, `longmemeval/`, `vectordb_perf/`, `cuvs/`, `custom/`.
- **Source path:** `sources/OpenViking/pyproject.toml`, `sources/OpenViking/openviking/server/routers/`, `sources/OpenViking/sdk/`, `sources/OpenViking/src/`, `sources/OpenViking/web-studio/`, `sources/OpenViking/benchmark/`

**Claim-7: OpenViking supports multiple VLM providers and 13 embedding providers.**

- **Evidence:** `README.md` line 118: "It supports Volcengine, OpenAI, Codex OAuth, Kimi, GLM, and local Ollama." Embedding providers live in `openviking/models/embedder/` — `volcengine_embedders.py`, `openai_embedders.py`, `jina_embedders.py`, `voyage_embedders.py`, `dashscope_embedders.py`, `minimax_embedders.py`, `cohere_embedders.py`, `vikingdb_embedders.py`, `gemini_embedders.py`, `litellm_embedders.py`, `local_embedders.py` — with an Azure alias inside `openai_embedders.py` (lines 143-146, `self._provider == "azure"`) and Ollama reachable through `litellm_embedders.py` (lines 26, 40, `ollama/nomic-embed-text`) — 13 total.
- **Source path:** `sources/OpenViking/README.md`, `sources/OpenViking/openviking/models/embedder/`

**Claim-8: OpenViking is backed by the VikingMem paper (VLDB 2026), auto-manages session memory, and is licensed AGPL-3.0 (main) / Apache 2.0 (crates, examples).**

- **Evidence:** `README.md` lines 199-203: "OpenViking open-sources a subset of the core capabilities described in the VikingMem paper... arXiv:2605.29640, 2026. Accepted by VLDB 2026." Line 46: "After a session commits, OpenViking asynchronously extracts user preferences and agent experience into long-term memory." License: `README.md` lines 232-239 — "Main Project: AGPLv3", "crates/ov_cli: Apache 2.0", "examples: Apache 2.0", with `LICENSE`, `crates/LICENSE`, `examples/LICENSE` present. `pyproject.toml` line 20 also sets `license = "AGPL-3.0"`.
- **Source path:** `sources/OpenViking/README.md`, `sources/OpenViking/pyproject.toml`, `sources/OpenViking/LICENSE`

**Related:** [[OpenViking]], [[Mnemosyne]], [[ECC]], [[CyberStrikeAI]]
