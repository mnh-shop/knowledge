---
name: af-deep-research-codegraph-verify
tags: [af-deep-research, codegraph-verify, agentfield, research, python, fastapi]
description: "Codegraph Verification: AF Deep Research — validating wiki claims against indexed source code symbols"
source: sources/af-deep-research/
---

# Codegraph Verification: AF Deep Research

**Date:** 2026-07-12 (line numbers refreshed against `main.py` @ 3,167 lines)

## Claim 1: Recursive research engine with quality-driven iteration loops
- **Wiki says:** AF Deep Research is a recursive research engine that executes quality-driven iterative loops — it spawns parallel agents, evaluates findings against quality thresholds, generates sub-queries when gaps are detected, and continues iterating until quality criteria are met.
- **Source evidence:**
  - `main.py:35` `AI_CALL_CONCURRENCY_LIMIT = 20`, `main.py:36` `MAX_ARTICLES_PER_TASK = 10`, `main.py:37` `NUM_SEARCH_TERMS_PER_TASK = 3`, `main.py:38-39` `MAX_BLUEPRINT_EXECUTION_LOOPS = int(os.getenv("MAX_BLUEPRINT_EXECUTION_LOOPS", "3"))`
  - `main.py:988-1046`: `assess_research_completeness` (`@app.reasoner()` at :988, `def` at :989) evaluates confidence on a 0.0-1.0 scale
  - `main.py:1046-1122`: `identify_knowledge_gaps_batch` (`@app.reasoner()` at :1046, `def` at :1047) identifies gaps with priority levels
  - `main.py:1122-1179`: `generate_targeted_search_queries` (`@app.reasoner()` at :1122, `def` at :1123) creates gap-filling queries
  - `main.py:1179-1236`: `decide_iteration_continuation` (`@app.reasoner()` at :1179, `def` at :1180) decides whether to continue based on quality score, gaps, and iteration budget
  - `main.py:319-330`: `ResearchQualityScore` model with `confidence_score`, `evidence_adequacy`, `critical_gaps_present`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (line numbers updated from the stale 988/1046/1122/1179 refs that were previously off by one vs. the decorator/def split)

## Claim 2: AgentField-based architecture with @app.reasoner() meta-reasoners
- **Wiki says:** The research engine uses AgentField's `@app.reasoner()` decorators extensively — meta-reasoners for strategy selection, universal reasoners for execution. The app is instantiated as an `Agent` with `node_id="meta_deep_research"`.
- **Source evidence:**
  - `main.py:62-71`: `app = Agent(node_id="meta_deep_research", agentfield_server=os.getenv('AGENTFIELD_SERVER', ...), ...)` — `node_id` at :63, `AGENTFIELD_SERVER` at :64
  - `@app.reasoner()` decorators in `main.py` at :364 (`merge_entity_pair`), :402 (`detect_entity_duplicates_batch`), :547 (`detect_relationship_duplicates_batch`), :595 (`merge_relationship_pair`), :747 (`check_evidence_duplication`), :851 (`generate_adaptive_hypothesis`), :988, :1046, :1122, :1179, :1236, :1341, :1504, :1839, :2145, :2286, :2364, :2488, :2663, :2794, :2996, :3038 (22 total in a 3,167-line file)
  - `reasoners/meta_reasoners.py` — `create_meta_reasoners()` registers multiple `@app.reasoner()` functions
  - `reasoners/universal_reasoners.py` — `create_universal_reasoners()` registers universal reasoners
  - `reasoners/research_orchestrator.py` — main orchestrator coordinating all reasoners
  - `pyproject.toml` — dependency on the `agentfield` package
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Parallel search streams with 4 search providers (Jina, Tavily, Firecrawl, Serper)
- **Wiki says:** The system supports 4 search providers (Jina, Tavily, Firecrawl, Serper) with auto-detection and priority-based selection. Search streams run in parallel.
- **Source evidence:**
  - `skills/search/` provider modules: `base.py`, `registry.py`, `jina.py`, `tavily.py`, `firecrawl.py`, `serper.py` (verified by directory listing)
  - `main.py:76-115`: `search_web_for_content()` auto-detects available providers via `list_provider_status()` and falls back through priority order (Jina, Tavily, Firecrawl, Serper)
  - `.env.example`: `JINA_API_KEY`, `TAVILY_API_KEY`, `FIRECRAWL_API_KEY`, `SERPER_API_KEY` + optional `SEARCH_PROVIDER` override
  - `main.py:1237-1341`: `generate_adaptive_search_streams` generates `num_parallel_streams` (default 2) with multiple queries per stream
  - `main.py:1342-1504`: `execute_intelligence_stream_comprehensive` executes searches concurrently via `asyncio.gather`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Entity and relationship graph building with deduplication and consolidation
- **Wiki says:** The system builds entity/relationship graphs from research findings with parallel entity deduplication, relationship deduplication, evidence deduplication, and multi-pass relationship extraction.
- **Source evidence:**
  - `main.py:180` `EntityPair`, :188 `EntityPairList`, :241 `Entity`, :251 `Relationship` Pydantic models
  - `main.py:365-402`: `merge_entity_pair` reasoner — merges confirmed duplicates
  - `main.py:402-439`: `detect_entity_duplicates_batch` reasoner — AI-based duplicate detection in batches
  - `main.py:439-526`: `process_entity_consolidation_parallel` — orchestrates parallel dedup and merge
  - `main.py:547-586`: `detect_relationship_duplicates_batch` reasoner — relationship dedup
  - `main.py:595-635`: `merge_relationship_pair` reasoner — relationship merging
  - `main.py:640-748`: `process_relationship_consolidation_parallel` — parallel relationship consolidation
  - `main.py:747-783`: `check_evidence_duplication` + `main.py:783-852` `process_evidence_deduplication_parallel` — hash-based + AI similarity dedup for evidence
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: REST API, SSE streaming, and web UI for real-time progress
- **Wiki says:** The system exposes REST API endpoints for research execution with SSE streaming for real-time progress updates, and an optional web UI at `/ui` for live monitoring.
- **Source evidence:**
  - `main.py:286-300`: `ResearchResponse` schema includes `mode`, `version`, `research_package`, `metadata`
  - `README.md:71`: "Open [localhost:8080/ui](http://localhost:8080/ui) to watch the workflow live."
  - `README.md:251`: "**Stream progress:** `GET /api/ui/v1/workflows/{execution_id}/notes/events` (SSE)"
  - `README.md:232`: integration row — "REST API, SSE streaming" (webhook-ready is an upstream platform claim, not in repo)
  - `docker-compose.yml` + `railway.json` — containerized / Railway deployment
  - `Dockerfile:39` — healthcheck `CMD curl -f http://localhost:${PORT:-8001}/health || exit 1`
- **Verdict:** ✅ CORRECT (webhook-ready marked as platform-level claim in wiki)
- **Fix needed:** None

## Claim 6: 10,000+ agent invocations per research query
- **Wiki says:** The architecture orchestrates approximately 10,000+ logical agent invocations per research query using parallel execution and iterative refinement loops.
- **Source evidence:**
  - `README.md:15`: "The architecture orchestrates ~10,000 logical agent invocations per research."
  - `README.md:53`: "~10,000 agent invocations. Self-correcting research loops. One API call."
  - `main.py:35-39`: concurrency/loop budget constants (20 concurrent AI calls, 10 articles/task, 3 search terms/task, 3 execution loops)
  - `main.py:137-146`: `run_in_batches()` utility executes tasks in batches with `asyncio.gather`
  - `main.py:3039-3167`: `execute_deep_research` top-level entry orchestrating the full fan-out/filter/synthesize/gap loop
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Module structure — reasoners/ 7 modules, skills/ extras, packages/mcp
- **Wiki says:** `reasoners/` = 7 modules incl. `example_reasoner.py`; `skills/` also has `example_skill.py` + `jina_search.py`; `packages/` is an MCP package, not third-party deps.
- **Source evidence:**
  - `reasoners/` contains 7 modules + `__init__.py`: `meta_reasoners.py`, `universal_reasoners.py`, `research_orchestrator.py`, `dynamic_models.py`, `dynamic_infrastructure.py`, `research_package.py`, `example_reasoner.py` (verified by directory listing)
  - `skills/` contains `example_skill.py`, `jina_search.py`, and the `search/` provider package (verified by directory listing)
  - `packages/` contains a single subdirectory `packages/mcp/` — an MCP helper package, NOT third-party dependencies (verified by directory listing)
- **Verdict:** ✅ CORRECT after wiki fix (previous wiki text "packages/: third-party dependencies" was wrong)
- **Fix needed:** None

## Claim 8: Platform-level claims (W3C DID, zero-trust, tag-based IAM, cryptographic provenance) are NOT in this repo
- **Wiki says:** W3C DID identity, zero-trust routing, tag-based IAM, cryptographic provenance, and signed audit trails are marked as upstream AgentField platform claims, not verifiable from this repo.
- **Source evidence:**
  - No occurrence of `DID`, `zero-trust`, `provenance`, or `IAM` in `main.py` (3,167 lines) or `README.md` (verified by grep) — the repo only documents REST/SSE/UI and `AGENTFIELD_SERVER` control-plane connectivity
  - These features belong to the AgentField control-plane product, not to af-deep-research source
- **Verdict:** ✅ CORRECT — claims properly downgraded to "platform-level / upstream"
- **Fix needed:** None

## Summary

All 8 key claims from the AF Deep Research wiki have been verified against source:
- ✅ Recursive research engine: quality-driven loops confirmed (`main.py:35-39`, reasoners at :988/:1046/:1122/:1179)
- ✅ AgentField integration: 22 `@app.reasoner()` decorators + `node_id="meta_deep_research"` (`main.py:63`)
- ✅ Parallel search streams: 4 providers (Jina/Tavily/Firecrawl/Serper) confirmed in `skills/search/` + `main.py:76-115`
- ✅ Entity/relationship graphs: parallel dedup/consolidation reasoners confirmed in `main.py`
- ✅ REST API/SSE/UI: `ResearchResponse` (:286), `/ui` + SSE endpoint (README:71/:251)
- ✅ 10,000+ agent invocations: README:15/:53 + budget constants (:35-39)
- ✅ Module structure corrected: 7 reasoner modules, `example_skill.py`/`jina_search.py`, `packages/mcp`
- ✅ Platform claims (DID/zero-trust/IAM/provenance) re-marked as upstream, not in-repo

## Related

- [[af-deep-research]] -- Main wiki entry
- [[agentfield]] -- Core AgentField platform
- [[sec-af]] -- Sibling security auditor
- [[af-reactive-atlas-mongodb]] -- Sibling MongoDB intelligence

## Cross-project

- [[sec-af.codegraph-verify]] -- Companion verification for SEC-AF
- [[swe-af.codegraph-verify]] -- Companion verification for SWE-AF
- [[agentfield.codegraph-verify]] -- Similar codegraph verification for AgentField
