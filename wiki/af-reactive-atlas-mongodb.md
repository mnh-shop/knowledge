---
name: af-reactive-atlas-mongodb
tags: [af-reactive-atlas-mongodb, wiki, python, mongodb, reactive, real-time, atlas-triggers, automation, monitoring, ai-llm, dashboard, docker, event-bus, git, plugin-sdk, security, storage]
description: Wiki entry for AF Reactive Atlas MongoDB — real-time intelligence layer for MongoDB via Atlas Triggers (Apache 2.0)
---

# AF Reactive Atlas MongoDB

| Field | Value |
|---|---|
| **Origin** | [Agent-Field/af-reactive-atlas-mongodb](https://github.com/Agent-Field/af-reactive-atlas-mongodb) |
| **License** | Apache 2.0 |
| **Stack** | Python + MongoDB Atlas + AgentField SDK |
| **Source** | `sources/af-reactive-atlas-mongodb/` |
| **Wanted** | Real-time intelligence layer for MongoDB via Atlas Triggers |

## What it is

**Zero-code AI behavior for MongoDB collections.** MongoDB Atlas Triggers call [[agentfield]] on insert — documents arrive raw and leave enriched with risk scores, pattern detection, evidence chains.

Updated on 2026-06-24 to reflect current architecture and capabilities.

## Architecture

- **Trigger-based**: MongoDB Atlas Triggers → AgentField execution on document insert
- **Cascade reasoning**: Risk scores update entities, re-analyze related documents
- **Document enrichment**: `_intelligence` field written back in-place
- **Reaction timeline**: Full audit trail of every AI decision
- **Zero polling**: Change detection via Atlas native triggers

## Key Components

### Core Files

**Main Application:**
- `main.py` - AgentField router setup for the reactive intelligence agent
- `models.py` - Pydantic models: DocumentIntelligence, Evidence, TriageResult, PolicyEvaluation, etc.

**Reasoners:**
- `reasoners/intelligence.py` - Complete reasoning engine: triage_document, analyze_document, evaluate_policies, generate_network_insight, cascade
- `reasoners/router.py` - AgentRouter defining the "reactive-intelligence" agent
- `reasoners/skills.py` - Skills: load_domain_config, load_entity_context, enrich_document, find_related_documents, load_rules, load_active_policies, etc.
- `reasoners/__init__.py` - Package initialization

**Domains:**
- `domains/finance/` - Financial transaction intelligence (AML compliance)
  - config.json, entities.json, rules.json, policies.json, scenarios.json
- `domains/ecommerce/` - E-commerce order intelligence (fraud detection)
  - config.json, entities.json, rules.json, policies.json, scenarios.json

**Demo & Setup:**
- `demo.py` - Reactive Atlas demo runner with scenarios
- `setup/seed.py` - Seed domain data (entities, rules, policies)
- `Dockerfile`, `docker-compose.yml` - Container deployment

### Integration Patterns

**With 4 Core Systems:**
1. **MongoDB Atlas** - Change detection via Triggers, data storage
2. **AgentField** - AI reasoning framework, skill execution, agent mesh
3. **Cloud Infrastructure** - Docker Compose, Railway deployment
4. **Observability** - Reaction timeline, execution tracing, dashboards

## Economics

- **Sub-$0.02 per document**
- **No new infrastructure** (uses existing Atlas clusters)
- **$400–600/mo for 10,000 documents/day**

## Use Cases

This pattern works anywhere documents arrive and need intelligent assessment. The engine is domain-agnostic — the config document makes it specific.

| Domain | Collection | What the AI does | Why rules engines fail |
|---|---|---|---|
| **Financial compliance** | `transactions` | AML pattern detection, structuring identification, counterparty risk propagation | Structuring is a *pattern* across transactions, not a property of one |
| **E-commerce fraud** | `orders` | Velocity abuse, synthetic identity signals, friendly fraud detection | Account takeover looks different every time; the *combination* of signals matters |

## Reactive Pipeline

**Change Detection → Reasoning → Enrichment → Write-back**

**What happens on every insert:**

1. **Atlas Trigger** fires and passes the full document to AgentField
2. **Domain resolution** — the collection name maps to a domain config document in MongoDB
3. **Triage** — quick LLM assessment: is this document worth investigating?
4. **Deep investigation** — entity profile, counterparty context, transaction history, relevant rules loaded in parallel
5. **LLM reasoning** — the domain-specific prompt produces a structured `DocumentIntelligence` judgment with evidence chain
6. **In-place enrichment** — `_intelligence` is written back to the source document
7. **Policy evaluation** — plain-English policies are checked against the enrichment
8. **Cascade** — if risk exceeds the threshold, linked entity profiles are updated, related documents are re-analyzed
9. **Audit trail** — every decision is logged to `reaction_timeline`

## Config-Driven Behavior

All AI behavior lives in a single MongoDB document. This is the entire configuration for the finance domain:

```json
{
  "domain": "finance",
  "document_collection": "transactions",
  "entity_collection": "accounts",
  "rules_collection": "compliance_rules",
  "context_loading": {
    "entity_lookup_field": "account_id",
    "counterparty_field": "counterparty_id",
    "history_match_fields": ["account_id", "counterparty_id"]
  },
  "cascade_config": {
    "risk_threshold": 0.7,
    "update_entities": true,
    "reenrich_related": true
  },
  "analysis_prompt": "You are a financial crime analyst performing AML risk assessment..."
}
```

### What fields control behavior:

- **`document_collection`** + **`entity_collection`** — which collections to read from and write to
- **`context_loading`** — how to assemble context (which fields link documents to entities)
- **`cascade_config`** — when and how to propagate risk
- **`analysis_prompt`** — the domain-specific instructions the LLM follows
- **`rules_collection`** — which rules the AI reasons over (loaded via text search)

**Change the config document in MongoDB and the AI behavior changes immediately. No code. No redeploy.**

## Deployment

### Docker Compose

```yaml
services:
  control-plane:
    image: agentfield/control-plane:latest
    environment:
      AGENTFIELD_HTTP_ADDR: 0.0.0.0:8080
      AGENTFIELD_STORAGE_MODE: local
    ports:
      - "8092:8080"
    volumes:
      - agentfield-data:/data
    restart: unless-stopped

  reactive-intelligence:
    build: .
    environment:
      AGENTFIELD_SERVER: http://control-plane:8080
      AGENT_CALLBACK_URL: http://reactive-intelligence:8001
      PORT: "8001"
      AI_MODEL: ${AI_MODEL:-openrouter/minimax/minimax-m2.5}
    ports:
      - "8004:8001"
    depends_on:
      control-plane:
        condition: service_started
    restart: unless-stopped
```

### Railway

The repository includes `railway.toml` for easy deployment to Railway platform.

## Agent Profile

This is an **AgentField Reactive Atlas agent** — a MongoDB intelligence layer that sits on AgentField's agent mesh and specializes in document enrichment through change-triggered reasoning.

### Configuration

- **Node ID:** "reactive-intelligence"
- **Tags:** ["reactive-intelligence"]
- **Skills:** 12+ skills for domain operations (config loading, entity context, enrichment, timeline logging)
- **Reasoners:** 5 core reasoning functions (triage, analysis, policy evaluation, network insight, cascade)

### Document Enrichment Triggers

- **Atlas Trigger** fired on insert/update operations
- **Collection-aware** — domain resolution via `domainMap` mapping
- **Skip if already enriched** — checks for `_intelligence` field

### Integration Patterns

**With AgentField's Cross-Agent Mesh:**

1. **Router-based** — Uses `AgentRouter` with ["reactive-intelligence"] tag
2. **Skill composition** — Deterministic database operations via skills
3. **LLM judgment** — Contextual interpretation via reasoners
4. **Execution tracing** — Full audit trail via `reaction_timeline`
5. **Event-driven** — Reactive to database changes, not polling

## Comparison to Traditional Approaches

| Approach | Reactive Atlas | Traditional ETL | Rules Engine |
|---|---|---|---|
| **Trigger source** | MongoDB Atlas Triggers | Cron jobs | Polling |
| **Change detection** | Native Atlas | Custom logic | External watches |
| **AI integration** | Built-in LLM reasoning | Separate enrichment service | Hardcoded logic |
| **Latency** | Seconds | Minutes/hours | Real-time |
| **Audit trail** | Automatic | Manual | Limited |
| **Config changes** | Live updates | Redeploy | Code changes |

**Traditional ETL/rules engines require polling, code changes, and separate infrastructure. Reactive Atlas uses MongoDB's native change detection and is fully config-driven.**

## Demo Scenarios

### Finance Domain

```bash
python3 demo.py finance structuring    # 5 cash deposits just under $10K
python3 demo.py finance round-trip     # circular A->B->C->A transfer
python3 demo.py finance layering       # US->HK->KY->CH SWIFT chain
python3 demo.py finance big-one        # single $500K+ Cayman wire
python3 demo.py finance clean          # 3 normal transfers (baseline)
```

### E-commerce Domain

```bash
python3 demo.py ecommerce velocity-abuse       # 5 rapid orders, rotating addresses
python3 demo.py ecommerce synthetic-identity   # new accounts, mismatched signals
python3 demo.py ecommerce friendly-fraud       # high returns history + expensive items
python3 demo.py ecommerce high-value-mismatch  # cross-border electronics, new account
python3 demo.py ecommerce normal               # 3 legitimate orders (baseline)
```

Both run on the same agent, same skills, same reasoning loop. The only difference is the config document in MongoDB.

## What to watch

**In Atlas UI** (`cloud.mongodb.com`):

- `transactions` and `orders` — each document gains `_intelligence` within 10-15 seconds of insert
- `reaction_timeline` — every AI decision logged with timestamps, scores, and triggered policies
- `accounts` and `customers` — risk profiles update when cascade fires

**In AgentField UI** (`http://localhost:8092`):

- Each insert creates a visible execution trace for `process_document`
- Shows skill calls: config load, entity lookup, rule retrieval, LLM reasoning, enrichment write, policy evaluation, cascade

## Build Your Own Domain

Adding a new domain requires **zero Python code changes**. The engine is fully config-driven.

```
domains/yourname/
  config.json        # What to watch, how to reason, when to cascade
  entities.json      # Seed entities (accounts, customers, devices)
  rules.json         # Domain rules the AI reasons over
  policies.json      # Plain-English policies evaluated after enrichment
  scenarios.json     # Demo scenarios with document templates
```

```bash
python3 setup/seed.py yourname        # seed the domain
python3 demo.py yourname yourscenario # run a scenario
```

Add your collection to the Atlas Trigger's `domainMap` and you're live.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- Python 3.10+
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register) account (free M0 tier is sufficient)
- [OpenRouter](https://openrouter.ai) API key
- [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) (free tunnel)

## Quick Start

```bash
git clone https://github.com/Agent-Field/af-reactive-atlas-mongodb.git && cd af-reactive-atlas-mongodb
cp .env.example .env          # Add OPENROUTER_API_KEY, MONGODB_URI
docker compose up -d
```

Starts AgentField control plane (`http://localhost:8092`) + Reactive Intelligence agent.

## License

Apache 2.0 · [See what else we're building →](https://github.com/Agent-Field)

---

**File source:** `sources/af-reactive-atlas-mongodb/`

**Updated:** 2026-06-24 to reflect current architecture with AgentField integration, reactive pipelines, and 4-core systems compatibility.

## Related

- [[af-reactive-atlas-mongodb-architecture]] -- architecture documentation
- [[af-reactive-atlas-mongodb-profile]] -- agent profile
- [[agentfield]] -- core AgentField platform
- [[agentfield-profile]] -- AgentField platform profile
- [[agentfield-deployment]] -- deployment guide

## Cross-project

- [[SWE-AF]] -- Sibling autonomous engineering factory on AgentField
- [[sec-af]] -- Sibling security auditor on AgentField
- [[af-deep-research]] -- Sibling research engine on AgentField
- [[hermes-agent]] -- Potential agent integration for document analysis
- [[openclaw]] -- Potential agent integration for document analysis
- [[n8n]] -- Workflow integration with MongoDB intelligence
- [[gogs]] -- Git service for domain configuration storage