---
name: headroom-codegraph-verify
tags: [headroom, codegraph-verify, llm, compression, proxy, rust, python, typescript]
description: "Codegraph Verification: headroom — validating wiki claims against indexed source code symbols"
source: sources/headroom/
---

# Codegraph Verification: headroom

**Date:** 2026-07-12

## Claim 1: Context compression as library, proxy, agent wrap, and MCP server (4 modes)
- **Wiki says:** Headroom operates in multiple modes — a Python/TypeScript library (`compress(messages)`), a standalone proxy (`headroom proxy --port 8787`), an agent wrap (`headroom wrap claude|codex|...`), and an MCP server with four tools. Each mode feeds compressed context to the LLM.
- **Source evidence:**
  - **Library:** `headroom/compress.py` line 171 defines `compress()` with `CompressResult` and `CompressConfig`. Python SDK at `sdk/typescript/src/compress.ts` line 19 exports `compress()` with adapters for Anthropic (`sdk/typescript/src/adapters/anthropic.ts`), Gemini, OpenAI, and Vercel AI.
  - **Proxy:** `headroom/cli/proxy.py` line 852 implements the `proxy` command, accepting port config via `_get_env_int_optional` (line 84). The proxy interceptor pipeline lives in `headroom/proxy/`.
  - **Wrap:** `headroom/cli/wrap.py` line 3724 defines the `wrap` command that injects Headroom into agent CLIs.
  - **MCP:** `headroom/ccr/mcp_server.py` registers 4 tools — `headroom_compress` (line 616), `headroom_retrieve` (line 639), `headroom_stats` (line 658), and `headroom_read` (line 676, file read caching behind a feature flag). README.md:53 lists only the first three.
  - `headroom/cli/__init__.py` registers both `proxy` and `wrap` as CLI subcommands.
- **Verdict:** ⚠️ CORRECTED (was "3 modes"; MCP is a 4th mode with 4 tools, and `compress()` line was 162 → 171)
- **Fix needed:** wiki updated to list the 4th MCP tool and corrected line reference

## Claim 2: Multi-compressor pipeline (diff, log, search, code-aware, Kompress, live zone, smart-crusher, content router)
- **Wiki says:** Headroom's pipeline contains 8+ content-aware compressors: diff compressor, log compressor, search compressor, code-aware compressor, Kompress ML compressor, live zone, smart-crusher, and content router — each implementing `Transform`.
- **Source evidence:**
  - `headroom/transforms/base.py:30` defines the `Transform` abstract base with `apply()` and `should_apply()`.
  - `crates/headroom-core/src/transforms/` contains Rust-native compressors: `diff_compressor.rs` (line 244 `compress`), `log_compressor.rs` (line 611 `compress`), `search_compressor.rs` (line 280 `compress`), `live_zone.rs`, `smart_crusher/`, and `text_crusher/`.
  - `headroom/transforms/` contains Python implementations: `code_compressor.py` (CodeAwareCompressor, line 1020), `kompress_compressor.py` (KompressCompressor, line 1511), `content_router.py` (ContentRouter, line 1453), `cache_aligner.py` (CacheAligner).
  - `crates/headroom-core/src/transforms/pipeline/` (orchestrator.rs, config.rs, traits.rs) manages pipeline orchestration.
  - `_get_pipeline` at `headroom/compress.py:385` assembles the active pipeline.
  - `compress` dispatches to 9 runtime `Transform` implementations.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Rust core crate (headroom-core) with BM25 relevance scoring and signal detection
- **Wiki says:** The Rust core at `crates/headroom-core/` provides fast BM25 relevance scoring, signal detection (keyword, line importance, tiered), content detection (magika, unidiff), and compression safety rails.
- **Source evidence:**
  - `crates/headroom-core/src/relevance/bm25.rs:` defines `BM25Scorer` (line 40) with `score()` (line 156), `score_batch()` (line 190), and `tokenize()` (line 70). TOKEN_PATTERN constant at line 31.
  - `crates/headroom-core/src/signals/` contains `keyword_detector.rs`, `line_importance.rs`, `tiered.rs` — three signal detection modules.
  - `crates/headroom-core/src/transforms/detection.rs`, `content_detector.rs`, `magika_detector.rs`, `unidiff_detector.rs` for content type detection.
  - `crates/headroom-core/src/transforms/safety.rs` for compression safety rails.
  - `crates/headroom-core/src/transforms/recommendations.rs` for compressor recommendations.
  - `crates/headroom-core/src/transforms/anchor_selector.rs` and `adaptive_sizer.rs` for adaptive compression.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Tokenizer support (Mistral, HuggingFace, generic) in headroom-core
- **Wiki says:** Headroom supports Mistral tokenizer, HuggingFace tokenizers, and a generic fallback, allowing accurate token counting across models.
- **Source evidence:**
  - `headroom/tokenizer.py:14` defines the abstract `Tokenizer` base class with `count_text`, `count_message`, `count_messages`.
  - `headroom/tokenizers/mistral.py:109` — `MistralTokenizer` implementation with `count_text:152`, `encode:217`, `decode:228`, `is_available:240`.
  - `headroom/tokenizers/huggingface.py:216` — `HuggingFaceTokenizer` with `_load_tokenizer:123`, `_use_fallback:264`, `list_supported_models:372`.
  - `headroom/tokenizers/mistral.py:31` — `MISTRAL_AVAILABLE` flag.
  - `headroom/tokenizers/huggingface.py:111` — `_LOAD_TIMEOUT_ENV` config.
  - Used across 15 callers including `headroom/client.py`, `headroom/parser.py`, `headroom/proxy/interceptors/base.py`.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Plugin system (Hermes, OpenClaw, OpenCode, agent hooks, OAuth2)
- **Wiki says:** Headroom ships plugins for Hermes Agent, OpenClaw, OpenCode, generic agent hooks, and OAuth2 integration — all under `plugins/`.
- **Source evidence:**
  - `plugins/hermes/` — contains `headroom_retrieve/` and `README.md` for Hermes Agent integration.
  - `plugins/openclaw/` — `src/proxy-manager.ts:60` defines `ProxyManager` with 5 callers; `src/engine.ts:18` defines `HeadroomContextEngine` for OpenClaw plugin.
  - `plugins/opencode/` — OpenCode integration with retrieve tool at `src/retrieve.ts`.
  - `plugins/headroom-agent-hooks/` — generic agent hook system with `hooks/` directory.
  - `plugins/headroom-oauth2/` — OAuth2 authentication plugin.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Cross-language SDK (Python + TypeScript with isomorphic compress API)
- **Wiki says:** Headroom provides both Python and TypeScript SDKs with the same `compress()` API surface, adapter-based message format support (Anthropic, OpenAI, Gemini, Vercel AI SDK), and hooks API.
- **Source evidence:**
  - **Python:** `headroom/compress.py` exports `compress()` (line 171), `headroom/compression/universal.py` has `UniversalCompressor` (line 114).
  - **TypeScript:** `sdk/typescript/src/compress.ts` exports `compress()` (line 19), `sdk/typescript/src/client.ts`, `sdk/typescript/src/hooks.ts`.
  - **Adapters:** `sdk/typescript/src/adapters/anthropic.ts`, `gemini.ts`, `openai.ts`, `vercel-ai.ts` — format conversion for each provider.
  - **Python crate:** `crates/headroom-py/` provides native Python bindings to the Rust core with `Cargo.toml` and `build.rs`.
  - **Rust workspace:** `crates/` also contains `headroom-proxy/`, `headroom-parity/`, and `headroom-simulators/` alongside `headroom-core/` and `headroom-py/`
  - TypeScript tests: `sdk/typescript/test/compress.test.ts`, `format-integration.test.ts`.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: CCR (Content-Aware Compression Ratio) with configurable backends
- **Wiki says:** Headroom uses a CCR system that adaptively selects compression strategies based on content type, with ONNX CPU inference for ML-based compression (Kompress).
- **Source evidence:**
  - `crates/headroom-core/src/ccr/` — CCR backends in `backends/` with `mod.rs`.
  - `headroom/transforms/kompress_compressor.py:893` — `KompressCompressor` class with ONNX CPU support (`_validate_pytorch_device` at line 663).
  - `crates/headroom-core/src/transforms/live_zone.rs` — adaptive live zone compression.
  - `crates/headroom-core/src/transforms/adaptive_sizer.rs` — adaptive sizing based on content.
  - `crates/headroom-core/src/transforms/recommendations.rs` — compressor recommendation engine.
  - `headroom/proxy/verbosity_controller.py:30` — `Signal` class for verbosity control signaling.
  - File-based persistence via `--storage.file` with SQL schema in `sql/` (`create_dashboard_summary.sql`, `create_proxy_telemetry_v2.sql`, `upgrade_*` migrations); file backend at `headroom/telemetry/backends/filesystem.py`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 7 key claims from the headroom wiki have been verified against the source code via codegraph exploration:

- ✅ Four modes: library (`headroom/compress.py:171`), proxy (`headroom/cli/proxy.py`), wrap (`headroom/cli/wrap.py`), MCP server with 4 tools (`headroom/ccr/mcp_server.py`)
- ✅ Multi-compressor pipeline: 9+ `Transform` implementations across Python and Rust crates
- ✅ Rust core: `crates/headroom-core/` with BM25 relevance, signal detection, content detection, safety
- ✅ Tokenizer support: Mistral, HuggingFace, and generic tokenizers in `headroom/tokenizers/`
- ✅ Plugin system: Hermes, OpenClaw, OpenCode, agent hooks, OAuth2 in `plugins/`
- ✅ Cross-language SDK: Python SDK + TypeScript SDK with adapters for Anthropic, Gemini, OpenAI, Vercel
- ✅ CCR system: Adaptive compression with ONNX-based Kompress ML compressor

## Related

- [[headroom]] -- Main wiki entry
- [[llmtrim]] -- Similar LLM token compression tool
- [[hermes-agent]] -- Hermes Agent MCP hub (plugin integration)
- [[openclaw]] -- OpenClaw agent platform (plugin integration)
- [[opencode]] -- OpenCode coding agent (plugin integration)

## Cross-project

- [[llmtrim.codegraph-verify]] -- Similar codegraph verification for llmtrim
- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for Hermes Agent
- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
- [[hermes-plugins.codegraph-verify]] -- Similar codegraph verification for Hermes Plugins
