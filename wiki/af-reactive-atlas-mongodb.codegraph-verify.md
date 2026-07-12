---
title: "af-reactive-atlas-mongodb — CodeGraph Verification"
tags: [af-reactive-atlas-mongodb, codegraph-verify, agentfield, mongodb]
related: [[af-reactive-atlas-mongodb]], [[agentfield]], [[af-deep-research]], [[sec-af]]
verification_date: 2026-07-12
verified_by: CodeGraph & manual source audit
source_ref: sources/af-reactive-atlas-mongodb/
graph_ref: graphs/af-reactive-atlas-mongodb/
---

# af-reactive-atlas-mongodb — CodeGraph Verification

## Claim-1: AgentField-powered reactive intelligence layer for MongoDB Atlas

The project connects MongoDB Atlas Triggers to an AgentField reasoner network to enrich documents in-place with `_intelligence` fields containing risk scores, pattern detection, evidence chains, and recommended actions.

**Source evidence:** `main.py` creates the Agent with `node_id="reactive-intelligence"` and connects to `AGENTFIELD_SERVER`. `README.md` opens with "Turn any MongoDB collection into an AI-powered intelligence layer." The trigger function in the README calls AgentField's async execute API on insert. The `docker-compose.yml` runs both `agentfield/control-plane:latest` and the built `reactive-intelligence` agent.

## Claim-2: Multi-step reasoner pipeline with triage → analysis → policy → cascade

The `process_document` reasoner (`reasoners/intelligence.py:437-589`) orchestrates a pipeline: load domain config → triage (quick LLM screen) → deep investigation (entity context, counterparty, recent risk loaded in parallel) → LLM analysis → enrich document → evaluate policies against enrichment → cascade risk to entity profiles and related documents.

**Source evidence:** `reasoners/intelligence.py` contains five `@router.reasoner()` functions: `triage_document`, `analyze_document`, `evaluate_policies`, `generate_network_insight`, and `cascade`. The `process_document` at line 437 chains them with `router.app.call()`. The pipeline is fully async using `asyncio.gather()` for parallel context loading.

## Claim-3: Domain-agnostic, config-driven design with zero code changes per domain

All AI behavior is driven by a single MongoDB domain config document — collection names, entity ID fields, context loading strategy, cascade thresholds, and the analysis prompt. Shipping a new domain requires only seeding a config document and adding Atlas triggers.

**Source evidence:** `reasoners/intelligence.py:446-448` loads `domain_config` from `load_domain_config`. The config fields (`document_collection`, `entity_collection`, `context_loading`, `cascade_config`, `analysis_prompt`) control all branching. The README devotes "Config is the product" section and shows `domains/finance/` and `domains/ecommerce/` as zero-code domain additions. `setup/seed.py` confirms the seed flow.

## Claim-4: 10 deterministic MongoDB skills vs. 5 LLM reasoners — intentional split

Skills (`reasoners/skills.py`) handle all database I/O: `load_domain_config`, `load_entity_context`, `find_related_documents`, `load_rules` (text search), `enrich_document`, `load_active_policies`, `update_entity_risk`, `log_reaction`, `find_counterparty_context`, `find_recent_high_risk`, `get_timeline`. Reasoners (`reasoners/intelligence.py`) handle judgment: triage, deep analysis, policy evaluation, network insight, cascade orchestration.

**Source evidence:** `reasoners/skills.py` registers 11 skills with `@router.skill()`, all doing MongoDB operations via PyMongo. `reasoners/intelligence.py` registers 5 reasoners with `@router.reasoner()`, all doing LLM calls via `router.ai(...)` with Pydantic schemas from `models.py`.

## Claim-5: Pydantic-typed enrichment schema written back in-place

The `_intelligence` sub-document written to each source document follows the `DocumentIntelligence` Pydantic model: `risk_score`, `risk_category`, `pattern_match`, `flags`, `summary`, `evidence` (list with fact/source/weight), `recommended_actions`, `confidence`, `related_entities_flagged`, `investigation_depth`. Versioning and timestamps are added server-side.

**Source evidence:** `models.py:29-55` defines `DocumentIntelligence` with all typed fields including `Evidence` sub-model (line 5-12), `TriageResult` (line 15-26), `PolicyEvaluation` (line 58-66), `NetworkInsight` (line 73-88), and `CascadeResult` (line 91-101). `skills.py:89-109` (`enrich_document`) writes the enrichment with version tracking.

## Claim-6: Shipped with two fully worked domains and demo scenarios

The repo ships `domains/finance/` (AML compliance) with 5 scenarios (structuring, round-trip, layering, big wire, clean) and `domains/ecommerce/` (order fraud) with 5 scenarios (velocity abuse, synthetic identity, friendly fraud, high-value mismatch, normal). Each domain has entity seeds, rules, policies, and config.

**Source evidence:** `ls domains/` shows `finance/` and `ecommerce/`. `README.md` documents `demo.py finance structuring`, `demo.py ecommerce velocity-abuse`, etc. with example output showing the full enrichment flow.
