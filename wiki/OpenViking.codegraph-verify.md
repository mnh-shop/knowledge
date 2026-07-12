---
title: OpenViking.codegraph-verify
description: "Source-level verification of OpenViking — Context Database for AI Agents"
date: 2026-07-12
tags: [openviking, codegraph-verify, forensics, data, AI, context-database]
verified_by: codegraph-explore
source: sources/OpenViking/
---

# OpenViking — CodeGraph Verification

**Claim-1: OpenViking is an open-source Context Database designed specifically for AI Agents, using a file-system paradigm to unify memories, resources, and skills.**

- **Evidence:** `README.md` line 48 states "OpenViking is an open-source **Context Database** designed specifically for AI Agents." Line 50 confirms it "abandons the fragmented vector storage model of traditional RAG and innovatively adopts a **'file system paradigm'** to unify the structured organization of memories, resources, and skills." The virtual filesystem hierarchy (`viking://resources/`, `viking://user/`, `viking://skills/`) is documented at lines 707-731 with a complete tree diagram.
- **Source path:** `sources/OpenViking/README.md`

**Claim-2: OpenViking implements a tiered context loading system (L0/L1/L2) to reduce token consumption in agent prompts.**

- **Evidence:** `README.md` lines 733-758 describe the three-tier architecture: "L0 (Abstract): A one-sentence summary for quick retrieval and identification. L1 (Overview): Contains core information and usage scenarios for Agent decision-making during the planning phase. L2 (Details): The full original data, for deep reading by the Agent when absolutely necessary." A concrete example with `.abstract` and `.overview` files is shown at lines 744-758.
- **Source path:** `sources/OpenViking/README.md`

**Claim-3: OpenViking provides a Directory Recursive Retrieval strategy combining vector search with hierarchical filesystem navigation for improved retrieval accuracy.**

- **Evidence:** `README.md` lines 762-770 detail the 5-step "Directory Recursive Retrieval Strategy": intent analysis, initial positioning via vector search, refined exploration within the high-score directory, recursive drill-down into subdirectories, and result aggregation. This contrasts with flat vector search used by Naive RAG.
- **Source path:** `sources/OpenViking/README.md`

**Claim-4: OpenViking achieves substantial accuracy improvements across multiple agent integrations in benchmark evaluations.**

- **Evidence:** `README.md` lines 634-640 present a benchmark table on the LoCoMo dataset: OpenClaw accuracy improved from 24.20% to 82.08% (+3.39×), Hermes from 33.38% to 82.86% (+2.48×), and Claude Code from 57.21% to 80.32% (+1.40×). Lines 643-647 show token reduction of up to 91.0% for OpenClaw and latency reductions of up to 66.10%. Additional benchmarks on tau2-bench (lines 651-656) and HotpotQA (lines 659-670) confirm gains across retail (+6.87pp), airline (+11.87pp), and multi-hop QA (91% accuracy at top-20).
- **Source path:** `sources/OpenViking/README.md`

**Claim-5: OpenViking includes a Rust-based core (RAGFS) with Python SDK, CLI tools, and multiple caching backends.**

- **Evidence:** `Cargo.toml` lines 2-13 define a workspace with 7 crate members including `ragfs` (core), `ragfs-cache-redis`, `ragfs-python`, `ov_cli`, and experimental caches like `ragfs-cache-mooncake` and `ragfs-cache-yuanrong`. `pyproject.toml` confirms Python packaging with 60+ dependencies for document parsing (PDF, DOCX, XLSX, PPTX), tree-sitter language parsers, web scraping (Scrapy), and model integration (OpenAI, Volcengine). The CLI is installable via `npm i -g @openviking/cli` or `cargo install ov_cli`.
- **Source path:** `sources/OpenViking/Cargo.toml`, `sources/OpenViking/pyproject.toml`

**Claim-6: OpenViking provides automatic session management with self-iterating memory extraction for both user preferences and agent experience.**

- **Evidence:** `README.md` lines 779-785 describe the "memory self-iteration loop" that asynchronously analyzes task execution results and user feedback at the end of each session. It maintains two parallel memory paths: "User Memory Update" for preferences and "Agent Experience Accumulation" for operational tips and tool usage patterns. The v3 memory extraction pipeline is always active; the legacy `memory.version` setting is deprecated (line 346).
- **Source path:** `sources/OpenViking/README.md`

**Related:** [[OpenViking]], [[Mnemosyne]], [[ECC]], [[CyberStrikeAI]]
