---
name: af-reactive-atlas-mongodb-architecture
tags: [af-reactive-atlas-mongodb, architecture, python, mongodb, reactive, real-time, atlas-triggers]
description: Architecture of AF Reactive Atlas MongoDB — intelligence layer turning MongoDB collections into self-assessing systems via Atlas Triggers
---

# AF Reactive Atlas MongoDB Agent Profile

**Source:** `sources/af-reactive-atlas-mongodb/`
**Raw:** `raw/af-reactive-atlas-mongodb/af-reactive-atlas-mongodb.xml` (192K)
**Codegraph:** `graphs/af-reactive-atlas-mongodb/` (456K)

**This agent profile describes the Reactive Atlas MongoDB intelligence layer — an AgentField-based AI agent that turns MongoDB collections into intelligent, self-assessing systems through real-time change-triggered reasoning.**

## Agent Identity

### What It Is

**AF Reactive Atlas MongoDB** is an AI-powered intelligence layer that operates on the AgentField framework and specializes in transforming MongoDB collections into intelligent data stores through reactive enrichment.

**Core Mission:** "Turn any MongoDB collection into an AI-powered intelligence layer."

**Unique Value Proposition:** Zero-code AI behavior for MongoDB collections. MongoDB Atlas Triggers call [[agentfield]] on insert — documents arrive raw and leave enriched with risk scores, pattern detection, evidence chains.

### Agent Classification

- **Type:** Reactive Intelligence Agent
- **Framework:** AgentField SDK
- **Specialization:** Document Enrichment and Risk Assessment
- **Integration Pattern:** Event-Driven, Change-Triggered
- **Output Mode:** Document Mutation (_intelligence field)

## Agent Configuration

### Node Configuration

```python
app = Agent(
    node_id="reactive-intelligence",
    agentfield_server=os.getenv("AGENTFIELD_SERVER", ""),
    api_key=os.getenv("AGENTFIELD_API_KEY"),
    ai_config=AIConfig(
        model=os.getenv("AI_MODEL", "openrouter/minimax/minimax-m2.5"),
    ),
)
```

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `AGENTFIELD_SERVER` | Yes | AgentField control plane URL |
| `AGENTFIELD_API_KEY` | Yes | Authentication key for AgentField |
| `AI_MODEL` | No | LLM model ID (default: openrouter/minimax/minimax-m2.5) |
| `AGENT_CALLBACK_URL` | No | Callback URL for AgentField (default: http://reactive-intelligence:8001) |

### Agent Tags and Skills

**Tags:** ["reactive-intelligence"]

**Skills (12 total):**
1. `load_domain_config` - Load domain configuration from MongoDB
2. `load_entity_context` - Fetch entity profiles
3. `find_related_documents` - Load historical context
4. `load_rules` - Retrieve domain rules via text search
5. `enrich_document` - Write `_intelligence` back to source document
6. `load_active_policies` - Load domain-scoped policies
7. `update_entity_risk` - Propagate risk changes to entities
8. `log_reaction` - Record audit trail events
9. `find_counterparty_context` - Follow the money
10. `find_recent_high_risk` - Scan for recently flagged documents
11. `get_timeline` - Retrieve reaction timeline events

## Intelligence Capabilities

### Core Reasoning Functions (5)

**1. Triage Document**
```python
@router.reasoner()
async def triage_document(
    document: dict[str, Any],
    domain_config: dict[str, Any],
) -> dict[str, Any]:
```

**Purpose:** Quick assessment to determine investigation depth
- **Input:** Raw document, domain configuration
- **Output:** TriageResult (priority, signals, investigation_needed, investigation_focus)
- **Triggers:** Amount anomalies, narrative red flags, jurisdiction risk

**2. Analyze Document**
```python
@router.reasoner()
async def analyze_document(
    document: dict[str, Any],
    domain_config: dict[str, Any],
    triage_signals: list[str] | None = None,
    counterparty_context: dict[str, Any] | None = None,
    recent_high_risk: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
```

**Purpose:** Deep analysis with loaded context and AI reasoning
- **Inputs:** Document, domain config, triage signals, entity context, rules, history
- **Output:** DocumentIntelligence with risk_score, evidence, recommendations
- **Process:** Parallel loading of entity/context/rules, structured LLM reasoning

**3. Evaluate Policies**
```python
@router.reasoner()
async def evaluate_policies(
    document: dict[str, Any],
    intelligence: dict[str, Any],
    policies: list[dict[str, Any]],
) -> dict[str, Any]:
```

**Purpose:** Plain-English policy evaluation against enrichment
- **Inputs:** Document, AI intelligence, policy list
- **Output:** PolicyEvaluationList with triggered status and actions
- **Process:** Judgment-based evaluation, not literal string matching

**4. Generate Network Insight**
```python
@router.reasoner()
async def generate_network_insight(
    document: dict[str, Any],
    intelligence: dict[str, Any],
    domain_config: dict[str, Any],
    related_high_risk: list[dict[str, Any]],
    entity_updates: list[str],
) -> dict[str, Any]:
```

**Purpose:** Network-level intelligence for cascade triggers
- **Inputs:** Document, intelligence, domain config, high-risk documents, entity updates
- **Output:** NetworkInsight with pattern, exposure, summary
- **Process:** Identifies chain/ring/hub/cluster/isolated patterns

**5. Cascade**
```python
@router.reasoner()
async def cascade(
    document: dict[str, Any],
    intelligence: dict[str, Any],
    domain_config: dict[str, Any],
) -> dict[str, Any]:
```

**Purpose:** Risk propagation and related document updates
- **Inputs:** Document, intelligence, domain config
- **Output:** CascadeResult with affected documents and network insight
- **Process:** Updates entity risk, re-enriches related docs, generates insights

### Integration Patterns

**With AgentField's Cross-Agent Mesh:**
- **Router-based:** Uses `AgentRouter` with ["reactive-intelligence"] tag
- **Skill composition:** Deterministic database operations
- **LLM judgment:** Contextual interpretation via reasoners
- **Execution tracing:** Full audit trail via `reaction_timeline`
- **Event-driven:** Reactive to database changes, not polling

## Domain-Specific Configuration

### Available Domains

**Finance Domain (AML Compliance)**
```json
{
  "domain": "finance",
  "display_name": "Financial Transaction Intelligence",
  "collection": "transactions",
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
  }
}
```

**E-commerce Domain (Fraud Detection)**
```json
{
  "domain": "ecommerce", 
  "display_name": "E-Commerce Order Intelligence",
  "collection": "orders",
  "entity_collection": "customers",
  "rules_collection": "fraud_rules",
  "context_loading": {
    "entity_lookup_field": "customer_id",
    "counterparty_field": null,
    "history_match_fields": ["customer_id"]
  },
  "cascade_config": {
    "risk_threshold": 0.7,
    "update_entities": true,
    "reenrich_related": true,
    "max_reenrich": 5
  }
}
```

## Document Enrichment Triggers

### Trigger Mechanism

**Atlas Trigger Lifecycle:**

1. **Change Detection** - MongoDB Atlas Triggers monitor collections
2. **Trigger Function** - Executed on document insert
3. **Enrichment Check** - Skip if `_intelligence` field exists
4. **Domain Resolution** - Map collection to domain config
5. **Agent Execution** - Call `reactive-intelligence.process_document`
6. **Enrichment Write** - Document mutated with `_intelligence`

**Trigger Function Example:**
```javascript
exports = async function(changeEvent) {
  const doc = changeEvent.fullDocument;
  if (!doc || doc._intelligence) return;

  const collection = changeEvent.ns.coll;
  const domainMap = { transactions: "finance", orders: "ecommerce" };
  const domain = domainMap[collection] || "finance";

  const response = await context.http.post({
    url: "https://YOUR_TUNNEL_URL/api/v1/execute/async/reactive-intelligence.process_document",
    headers: { "Content-Type": ["application/json"] },
    body: JSON.stringify({
      input: { document: doc, collection: collection, domain: domain }
    })
  });

  if (response.statusCode >= 400) {
    throw new Error(`AgentField returned ${response.statusCode}`);
  };
};
```

### Documents Processed

**Collection-to-Domain Mapping:**
- `transactions` → finance domain (AML compliance)
- `orders` → ecommerce domain (fraud detection)
- Any collection → configurable via `domainMap`

**Enrichment Trigger Conditions:**
- **Insert operations** — New documents
- **Skip existing** — Documents with `_intelligence` field
- **All domains** — Configured domains only
- **Public access** — HTTPS tunnel to local AgentField

## Agent Output Format

### Standard Enriched Document

**Input Document:**
```json
{
  "transaction_id": "txn_20240315_a8f3",
  "account_id": "acc_0028", 
  "amount": 9800,
  "type": "cash_deposit",
  "timestamp": "2024-03-15T14:23:07Z"
}
```

**Output Document:**
```json
{
  "transaction_id": "txn_20240315_a8f3",
  "account_id": "acc_0028",
  "amount": 9800,
  "type": "cash_deposit",
  "timestamp": "2024-03-15T14:23:07Z",
  "_intelligence": {
    "risk_score": 0.82,
    "risk_category": "high",
    "pattern_match": "structuring",
    "flags": ["STRUCT-001", "THRESH-001", "VELOCITY-002"],
    "summary": "Cash deposit of $9,800 is just below the $10,000 CTR threshold...",
    "evidence": [
      {"fact": "Amount $9,800 is 98% of $10,000 CTR threshold", "source": "rules", "weight": "strong"},
      {"fact": "4 similar deposits in 48h totaling $38,400", "source": "transaction_history", "weight": "strong"},
      {"fact": "Account is Panama-based trust with enhanced due diligence", "source": "entity_profile", "weight": "moderate"}
    ],
    "recommended_actions": ["hold", "escalate", "review_counterparty"],
    "confidence": 0.91,
    "related_entities_flagged": ["acc_0028"],
    "investigation_depth": "deep",
    "analyzed_at": "2024-03-15T14:23:07Z",
    "version": 1
  }
}
```

## Economics and Pricing

### Cost Structure

**Per Document Processing:**
- **Budget model:** <$0.01 per document
- **Mid-tier model:** <$0.01 per document  
- **High-volume:** < $0.02 per document

**Agent Steps Breakdown:**
- **Routine document:** 3 steps (~6K tokens) < $0.01
- **Flagged + cascade:** Up to 14 steps (~40K tokens) < $0.01

**Step-wise Costs:**
- **Triage:** Quick assessment (~500 tokens)
- **Analysis:** Entity context loading (~3.5K-12K tokens)
- **Policy evaluation:** Plain-English policies (~1.3K tokens)
- **Cascade:** Re-enrichment and network analysis

### Scaling Economics

**Monthly Agent Cost (assumes ~15% flag rate):**

| Documents/day | Budget model | Mid-tier model |
|---|---|---|
| 1,000 | ~$40 | ~$60 |
| 10,000 | ~$400 | ~$600 |
| 100,000 | ~$4,000 | ~$6,000 |

**Infrastructure Savings:**
- No new infrastructure (uses existing Atlas clusters)
- Zero deployment overhead after initial setup
- Configuration-driven behavior eliminates code changes

## Performance Characteristics

### Processing Latency

**Typical Processing Times:**
- **Triage:** < 1 second
- **Analysis:** 10-30 seconds (with context loading)
- **Enrichment:** < 1 second
- **Cascade:** 30-60 seconds (for high-risk documents)
- **Total:** 10-60 seconds from document insert

**Quality Metrics:**
- **Enrichment success rate:** > 95%
- **Error handling:** Graceful fallback to triage
- **Memory usage:** < 512MB per agent instance
- **CPU utilization:** < 50% on average

### Scalability

**Horizontal Scaling:**
- **Multiple agent instances** for concurrent processing
- **Load balancing** across Atlas Triggers
- **Queue-based processing** for burst handling
- **Auto-scaling** based on queue length

**Database Scaling:**
- **MongoDB Atlas** provides built-in scaling
- **Indexing** for fast document lookup
- **Read replicas** for improved performance
- **Sharding** for large datasets

## Compatibility and Integration

### Integration with 4 Core Systems

**1. MongoDB Atlas (Change Detection)**
- **Trigger configuration** in Atlas UI
- **Tunnel setup** with cloudflared
- **Collection mapping** for domain resolution
- **Change stream** monitoring

**2. AgentField (AI Framework)**
- **Agent mesh** integration
- **Skill composition** for deterministic operations
- **Router-based** reasoning architecture
- **Execution tracing** and observability

**3. Cloud Infrastructure**
- **Docker Compose** deployment
- **Railway platform** support
- **Environment variable** configuration
- **Public URL** management

**4. Observability Systems**
- **Reaction timeline** logging
- **Execution traces** in AgentField UI
- **Monitoring dashboards** for performance
- **Audit trails** for compliance

## Agent Workflow Examples

### Finance Domain Workflow

**Document Insert:**
```json
{
  "transaction_id": "__AUTO__",
  "account_id": "acc_0028",
  "amount": 9800,
  "type": "cash_deposit", 
  "geolocation": {"country": "US", "city": "Miami"}
}
```

**Agent Processing:**
1. **Atlas Trigger** detects insert
2. **Domain resolution** identifies finance domain
3. **Triage** detects structuring suspicion
4. **Deep investigation** loads entity context and rules
5. **AI analysis** produces risk score 0.82
6. **Enrichment** writes `_intelligence` field
7. **Policy evaluation** triggers high-value-kyc policy
8. **Cascade** updates entity risk profile
9. **Timeline logging** records full audit trail

### E-commerce Domain Workflow

**Document Insert:**
```json
{
  "order_id": "__AUTO__", 
  "customer_id": "cust_0034",
  "amount": 1250,
  "items": [{"name": "Drone Quadcopter", "category": "electronics"}],
  "shipping_address": {"country": "US", "city": "Newark"},
  "billing_address": {"country": "US", "city": "Jersey City"}
}
```

**Agent Processing:**
1. **Atlas Trigger** detects insert
2. **Domain resolution** identifies ecommerce domain
3. **Triage** flags identity/location mismatch
4. **Deep investigation** loads customer history and fraud rules
5. **AI analysis** produces risk score 0.85
6. **Enrichment** writes `_intelligence` field  
7. **Policy evaluation** triggers address-mismatch policy
8. **Cascade** recommends enhanced monitoring
9. **Timeline logging** records customer risk events

## Agent Profiling and Monitoring

### Profile Metrics

**Processing Metrics:**
- Documents processed per hour
- Average enrichment time per document
- Success/failure rates
- AI model token usage

**Quality Metrics:**
- Risk score distribution accuracy
- Policy trigger precision
- Evidence chain completeness
- Confidence score calibration

**Resource Metrics:**
- Memory usage patterns
- CPU utilization by reasoner
- Network bandwidth
- Database query performance

### Monitoring Integration

**Atlas UI Monitoring:**
- Collection enrichment status
- Timeline event counts
- Entity risk profile updates
- Cascade propagation statistics

**AgentField UI Monitoring:**
- Execution trace details
- Skill performance metrics
- Agent health and connectivity
- Error rate tracking

## Agent Behaviors and Characteristics

### Deterministic vs. Judgment-Based

**Deterministic Operations (Skills):**
- Database queries and updates
- MongoDB indexing and administration
- Document serialization and formatting
- Reaction timeline events
- Entity risk profile updates

**Judgment-Based Operations (Reasoners):**
- Risk assessment and scoring
- Pattern matching and detection
- Policy evaluation and interpretation
- Network intelligence generation
- Cascade decision making

### Event-Driven Architecture

**Trigger-Based Processing:**
- **Change detection** instead of polling
- **Reactive enrichment** instead of batch processing
- **Document mutation** instead of separate storage
- **Immediate updates** instead of async jobs

**Cross-Agent Collaboration:**
- **Agent mesh** for capability sharing
- **Skill composition** for complex operations
- **Execution coordination** for multi-step processes
- **Error recovery** for resilient operations

## Technical Specifications

### Agent Capabilities

**Input Formats:**
- JSON documents (standard MongoDB BSON)
- Variable-sized documents (10KB - 1MB)
- Nested objects and arrays
- Mixed data types (strings, numbers, objects, arrays)

**Output Formats:**
- Enriched documents with `_intelligence` field
- Standard Pydantic models (DocumentIntelligence, Evidence, etc.)
- Structured reasoning outputs
- Audit trail events

**Performance Targets:**
- **Enrichment latency:** 10-60 seconds
- **Throughput:** 1000+ documents per hour
- **Memory footprint:** < 512MB
- **CPU usage:** < 50%

### Compatibility Matrix

| System | Compatibility | Notes |
|---|---|---|
| MongoDB Atlas | Native | Triggers, change streams |
| AgentField | Required | Framework dependency |
| Docker | Optional | Local development |
| Railway | Optional | Cloud deployment |
| CI/CD | Optional | Automation support |
| Monitoring | Recommended | Dashboard integration |

## Configuration for Different Environments

### Development Environment

```yaml
environment:
  AGENTFIELD_SERVER: "http://localhost:8092"
  AGENTFIELD_API_KEY: "dev-key-123"
  AI_MODEL: "openrouter/minimax/minimax-m2.5"
  MONGODB_URI: "mongodb://localhost:27017"
  AGENTFIELD_URL: "http://localhost:8092"
```

**Development Features:**
- Debug logging enabled
- Console output for troubleshooting
- Local MongoDB connection
- Fast iteration cycles

### Production Environment

```yaml
environment:
  AGENTFIELD_SERVER: "https://agentfield.yourcompany.com"
  AGENTFIELD_API_KEY: "prod-key-456"
  AI_MODEL: "gpt-4o-mini"
  MONGODB_URI: "mongodb+srv://user:pass@cluster.mongodb.net/"
  AGENTFIELD_URL: "https://atlas.yourcompany.com"
  AGENTFIELD_PUBLIC_URL: "https://tunnel.yourcompany.com"
```

**Production Features:**
- Enhanced logging and monitoring
- Production MongoDB Atlas connection
- Secure tunnel configuration
- Full audit trail retention

## Agent Development and Maintenance

### Development Workflow

**Code Changes:**
1. Modify reasoner or skill code
2. Test with demo scenarios
3. Verify existing functionality
4. Update documentation
5. Deploy changes

**Testing Strategy:**
- Unit tests for individual skills
- Integration tests for reasoner chains
- End-to-end tests with Atlas Triggers
- Performance tests under load
- Security tests for input validation

### Maintenance Activities

**Routine Maintenance:**
- Monitor processing logs and metrics
- Update domain configurations as needed
- Review and optimize indexes
- Backup and restore operations

**Troubleshooting:**
- Monitor reaction timeline for errors
- Check AgentField UI for execution traces
- Review MongoDB Atlas Trigger status
- Validate environment variable settings

## Conclusion

**AF Reactive Atlas MongoDB** is a sophisticated AI agent that combines AgentField's reasoning capabilities with MongoDB Atlas's real-time change detection to create intelligent document processing systems.

**Key Strengths:**
- **Zero-code deployment** through configuration
- **Real-time enrichment** through reactive triggers
- **Contextual intelligence** through AI reasoning
- **Full auditability** through timeline logging
- **Cost-effective processing** through efficient tokenization

**Integration Benefits:**
- **Seamless MongoDB integration** through native Atlas features
- **Scalable architecture** for enterprise workloads
- **Zero maintenance overhead** after initial setup
- **Continuous learning** through enriched data

**Use Cases:**
- Financial compliance and AML
- E-commerce fraud detection
- Healthcare patient triage
- Content moderation
- IoT anomaly detection
- Supply chain monitoring

This agent represents a fundamental shift from traditional ETL and rules-based approaches to real-time, AI-driven intelligence for database systems.

## Related

- [[af-reactive-atlas-mongodb]] -- wiki page for this agent
- [[af-reactive-atlas-mongodb-profile]] -- agent profile
- [[agentfield]] -- core AgentField platform
- [[agentfield-architecture]] -- platform architecture
- [[agentfield-deployment]] -- deployment guide