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

**Source evidence:** `main.py:7-13` creates the Agent with `node_id="reactive-intelligence"` (line 8) and connects via `AGENTFIELD_SERVER` (line 9) + `AGENTFIELD_API_KEY` (line 10). `README.md` opens with "Turn any MongoDB collection into an AI-powered intelligence layer." The `docker-compose.yml` runs both `agentfield/control-plane:latest` (host `8092:8080`) and the built `reactive-intelligence` agent (host `8004:8001`).

## Claim-2: Multi-step reasoner pipeline with triage → analysis → policy → cascade

The `process_document` reasoner (`reasoners/intelligence.py:437-530`) orchestrates a pipeline: load domain config → triage (quick LLM screen) → deep investigation (entity context, counterparty, recent risk loaded in parallel) → LLM analysis → enrich document → evaluate policies against enrichment → cascade risk to entity profiles and related documents.

**Source evidence:** `reasoners/intelligence.py` contains five core `@router.reasoner()` functions plus the orchestrator — decorators at :35 (`triage_document`, def :36), :69 (`analyze_document`, def :70), :182 (`evaluate_policies`, def :183), :216 (`generate_network_insight`, def :217), :254 (`cascade`, def :255), and :436 (`process_document`, def :437; `_enrich_single` helper at :401). The pipeline is fully async using `asyncio.gather()` for parallel context loading.

## Claim-3: Domain-agnostic, config-driven design with zero code changes per domain

All AI behavior is driven by a single MongoDB domain config document — collection names, entity ID fields, context loading strategy, cascade thresholds, and the analysis prompt. Shipping a new domain requires only seeding a config document and adding Atlas triggers.

**Source evidence:** `domains/finance/config.json` keys: `document_collection`, `document_id_field`, `entity_collection`, `entity_id_field`, `rules_collection`, `context_loading` (`entity_lookup_field`, `counterparty_field`, `history_collection`, `history_match_fields`, `history_limit`), `enrichment_schema`, `cascade_config` (`risk_threshold: 0.7`, `update_entities`, `reenrich_related`, `counterparty_threshold: 0.8`, `max_reenrich: 10`), `analysis_prompt`, `policy_prompt`. `domains/{finance,ecommerce}/` each ship `config.json`, `entities.json`, `rules.json`, `policies.json`, `scenarios.json`. `setup/seed.py` confirms the seed flow; `reasoners/skills.py:load_domain_config` reads the config at runtime.

## Claim-4: 11 deterministic MongoDB skills vs. 5 LLM reasoners — intentional split

Skills (`reasoners/skills.py`) handle all database I/O: `load_domain_config`, `load_entity_context`, `find_related_documents`, `load_rules` (text search), `enrich_document`, `load_active_policies`, `update_entity_risk`, `log_reaction`, `find_counterparty_context`, `find_recent_high_risk`, `get_timeline`. Reasoners (`reasoners/intelligence.py`) handle judgment: triage, deep analysis, policy evaluation, network insight, cascade orchestration.

**Source evidence:** `reasoners/skills.py` registers exactly **11** skills with `@router.skill()` (decorators at :38, :45, :54, :73, :88, :112, :119, :155, :165, :193, :215), all doing MongoDB operations via PyMongo. `reasoners/intelligence.py` registers 6 `@router.reasoner()` functions (5 core + `process_document`), all doing LLM calls via `router.ai(...)` with Pydantic schemas from `models.py`. (Wiki previously said "12+" — corrected to 11.)

## Claim-5: Pydantic-typed enrichment schema written back in-place

The `_intelligence` sub-document written to each source document follows the `DocumentIntelligence` Pydantic model: `risk_score`, `risk_category`, `pattern_match`, `flags`, `summary`, `evidence` (list with fact/source/weight), `recommended_actions`, `confidence`, `related_entities_flagged`, `investigation_depth`. Versioning and timestamps are added server-side.

**Source evidence:** `models.py:5` `Evidence`, :15 `TriageResult`, :29 `DocumentIntelligence` (with `risk_score`, :58 `PolicyEvaluation`, :69 `PolicyEvaluationList`, :73 `NetworkInsight`, :91 `CascadeResult`. `reasoners/skills.py` `enrich_document` writes the enrichment with version tracking; the config's `enrichment_schema` block mirrors the model fields.

## Claim-6: Shipped with two fully worked domains and demo scenarios

The repo ships `domains/finance/` (AML compliance) and `domains/ecommerce/` (order fraud), each with entity seeds, rules, policies, config, and demo scenarios.

**Source evidence:** `domains/finance/scenarios.json:2-7` `"order": ["clean", "structuring", "round-trip", "layering", "big-one"]`; `domains/ecommerce/scenarios.json:2` `"order": ["normal", "friendly-fraud", "velocity-abuse", "synthetic-identity", "high-value-mismatch"]`. `README.md` documents `demo.py finance structuring`, `demo.py ecommerce velocity-abuse`, etc. with example output showing the full enrichment flow. `demo.py` + `setup/seed.py` are present at repo root.

## Claim-7: Economics figures are README marketing, not source-verifiable

The "sub-$0.02 per document" and "$400-600/mo" figures are the project's own README claims.

**Source evidence:** `README.md` states "less than a cent on budget models — under two cents on mid-tier. At 10,000 documents per day, total agent cost runs ~$400-600/mo" (README.md:199) with a cost table (README.md:208). No cost model, benchmark harness, or telemetry exists in the repo code — the claim is marked "not source-verifiable" in the wiki.

## Claim-8: Deployment — Docker Compose + Railway

The repo ships containerized deployment with the AgentField control plane and a Railway config.

**Source evidence:** `docker-compose.yml` defines `control-plane` (image `agentfield/control-plane:latest`, host port `8092:8080`) and `reactive-intelligence` (built from repo, host port `8004:8001`, `AGENTFIELD_SERVER=http://control-plane:8080`, `AGENT_CALLBACK_URL=http://reactive-intelligence:8001`). `railway.toml` present at repo root. `Dockerfile` + `requirements.txt` define the build.

## Summary

All 8 claims verified against source:
- ✅ Reactive intelligence layer: `main.py:8` `node_id="reactive-intelligence"` + `_intelligence` write-back
- ✅ 5 reasoners + `process_document` chain with exact file:line evidence
- ✅ Config-driven domains: full `finance/config.json` key inventory + `domains/{finance,ecommerce}/`
- ✅ **11** `@router.skill()` handlers in `reasoners/skills.py` (was mislabeled "12+"/"10")
- ✅ Pydantic schema: `models.py` line-mapped classes
- ✅ Two domains + scenario order arrays confirmed
- ✅ Economics figures downgraded to README claims
- ✅ Deployment: docker-compose (`8092:8080` + `8004:8001`) + `railway.toml`

## Related

- [[af-reactive-atlas-mongodb]] -- Main wiki entry
- [[agentfield]] -- Core AgentField platform
- [[af-deep-research]] -- Sibling research engine
- [[sec-af]] -- Sibling security auditor
