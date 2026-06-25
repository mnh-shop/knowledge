---
name: af-deep-research-profile
description: AF Deep Research — Agent Profile
tags: [af-deep-research, agent-profile, ai-llm, cli, deep-research, docker, optimization, orchestration, profile, recursive-agents, research, security, typescript, virtualization, webhook]
---

# ---

# AF Deep Research — Agent Profile

**License:** Apache 2.0 (fully permissive — best for forking/redistribution)  
**Source:** `sources/af-deep-research/`  
**What's in it:** A recursive research engine that orchestrates ~10,000+ logical agent invocations per query  
**Uses:** Production AI research backend (not chat) with self-correcting loops and gap-filling

## What it is

A **meta-level research system** that performs comprehensive multi-stream intelligence gathering. It dynamically classifies queries, executes parallel research streams, and iteratively refines hypotheses to produce well-sourced analytical packages for any domain.

**Key differentiators:**
- **Recursive intelligence loops**: Spawns parallel agents → evaluates → finds gaps → generates sub-queries → repeats
- **Two-tier filtering**: Hash dedup → semantic dedup → relevance scoring (hyper-relevant content only)  
- **Cross-stream synthesis**: Detects and analyzes connections between parallel research angles
- **Quality-driven termination**: Continues until confidence thresholds met, not fixed iterations
- **Philosophical lenses**: `balanced` / `bull` / `bear` perspective control

## Integration Architecture

### Core Components:
- **Meta-Intelligence Layer**: High-level strategy, coordination, and adaptation control
- **Universal Research Orchestrator**: Implements Dynamic Hierarchy of Execution (DHE)
- **Universal Reasoners**: Query analysis, strategy creation, execution, quality control, synthesis, validation
- **Dynamic Models**: Reasoning strategies, prompts, contexts, memory states, quality metrics
- **Reasoning Infrastructure**: Prompt builders, strategy registry, learning adaptation, memory management

### AgentField Integration:
- Built as a **sub-repo** in the AgentField ecosystem  
- Uses `@app.reasoner()` decorators for AI reasoning functions
- Leverages `app.ai()` for LLM calls and `app.call()` for cross-agent routing
- Implements AgentField's harness orchestration patterns
- Follows cross-agent mesh architecture with service discovery

## Reasoner Architecture

### Meta-Intelligence Layer Reasoners:
1. **Meta-Reasoning Controller** - Central orchestrator for research strategy decisions
   - Analyzes research requests and selects optimal high-level approach
   - Considers query complexity, time constraints, quality targets, learning insights
   - Integrates with AgentField's workflow DAG patterns

2. **Adaptive Reasoning Strategist** - Dynamic strategy adaptation during execution
   - Monitors research progress and triggers strategy adaptations
   - Uses meta-reasoning insights for optimization decisions

3. **Dynamic Prompt Constructor** - Context-aware prompt building and evolution
   - Builds optimized prompts based on reasoning type and context
   - Incorporates learning insights from previous research

4. **Context-Aware Scheduler** - Intelligent execution flow management
   - Optimizes resource allocation and parallel execution
   - Ensures efficient workflow progression based on constraints

5. **Meta-Learning Coordinator** - Cross-session learning and improvement
   - Extracts insights from research sessions to improve future performance
   - Stores performance data for future strategy selection

### Universal Reasoners:
1. **Query Analysis Reasoner** - Analyzes intent, complexity, and research requirements
2. **Domain Strategy Reasoner** - Creates domain-specific research strategies
3. **Research Execution Reasoner** - Executes actual research using search engines
4. **Quality Control Reasoner** - Assesses research quality and completeness
5. **Synthesis Reasoner** - Synthesizes findings into coherent responses
6. **Research Validation Reasoner** - Validates synthesis against original sources

## Data Models

### Core Schema:
- **ResearchContext**: Query, context_type, complexity, time_available, quality_target
- **MemoryState**: Current workflow state, strategy, findings_count, quality_score
- **LearningInsight**: Extracted insights for future improvement
- **AdaptationDecision**: Strategy changes based on performance and learning
- **QualityMetrics**: Overall_quality, confidence_score, improvement_needed
- **ResearchResults**: Search results, analysis, execution_quality
- **SynthesisData**: Generated insights, key_findings, confidence_level

### Integration Features:
- **Entity/Relationship Types**: Company, Investor, Founder, Technology, Market_Trend, Metric
- **Relationship Types**: Competes_With, Invests_In, Partners_With, Founded_By, Acquires
- **ResearchPackage**: Complete output with entities, relationships, evidence, document, metadata

## Performance & Scale

### Processing Characteristics:
- **10,000+ agent invocations** per research query
- **2-4 parallel research streams** per query
- **Iterative refinement** with adaptive strategy selection
- **16+ minute workflows** for complex queries
- **SSE streaming** for real-time progress updates

### Key Efficiency Features:
- **Two-tier filtering**: Hash dedup → semantic dedup → relevance scoring
- **Cross-stream synthesis**: Pattern detection across parallel research angles
- **Network consolidation**: Merge duplicate entities and relationships
- **Meta-learning**: Continuous improvement of strategy selection
- **Parallel execution**: Optimized resource utilization for complex queries

## Configuration & Parameters

### Research Parameters:
```json
{
  "query": "Original research question",
  "mode": "general",
  "research_focus": 3,        // Depth (1-5)
  "research_scope": 3,        // Breadth (1-5) 
  "max_research_loops": 3,   // Maximum iterations
  "tension_lens": "balanced", // Perspective (balanced/bull/bear)
  "source_strictness": "mixed" // Source quality filtering
}
```

### Deployment Environment:
- `OPENROUTER_API_KEY`: LLM inference provider
- `JINA_API_KEY/TAVILY_API_KEY`: Search provider API keys
- `AGENTFIELD_SERVER`: Control plane connection
- `DEFAULT_MODEL`: LLM model selection
- `TEMPERATURE`: Generation randomness
- `OLLAMA_BASE_URL`: Local LLM deployment

### Search Provider Registry:
Supports multiple providers with automatic fallback:
- **Jina AI**: Primary search provider
- **Tavily**: Alternative search provider
- **Firecrawl**: Web scraping capability
- **Serper**: Search API alternative

## Usage & Integration

### Programmatic API:
```python
# Using the af CLI (one-call DX)
af call meta_deep_research.execute_deep_research --in '{"query": "What companies are investing in AI chips?"}'

# Direct HTTP
import requests

response = requests.post(
    'http://localhost:8080/api/v1/execute/async/meta_deep_research.execute_deep_research',
    headers={'Content-Type': 'application/json'},
    json={'input': {'query': 'Your research question'}}
)

# Stream progress via SSE
# Watch the workflow live at: http://localhost:8080/ui
```

### Response Format:
Returns structured **UniversalResearchPackage** with:
- **entities**: Typed objects (Company, Investor, Technology, etc.)
- **relationships**: Entity connections and mappings
- **article_evidence**: Facts and quotes with source attribution
- **document**: Hierarchical sections with inline citations
- **metadata**: iterations_completed, final_quality_score, etc.

## Deployment & Environment

### Docker Compose:
```yaml
services:
  agentfield:
    image: agentfield/control-plane:latest
    ports: ["8080:8080"]
    volumes: ["agentfield-data:/data"]
    
  deep-research:
    build: .
    ports: ["8001:8001"]
    environment:
      - AGENTFIELD_SERVER=http://agentfield:8080
      - DEFAULT_MODEL=openrouter/deepseek/deepseek-chat-v3.1
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    depends_on: [agentfield]
```

### Local Development:
```bash
# Create virtual environment and install dependencies
python -m venv .venv && source .venv/bin/activate
pip install -e .

# Set writable working directory (default requires root)
export PR_AF_WORKDIR=/tmp/pr-af-workdir

# Configure environment and start
python3 main.py
```

### Local LLMs:
```bash
# Air-gapped deployment with local Ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
DEFAULT_MODEL=ollama/llama3.2
```

## Deployment Options

### Cloud & Production:
- **Docker Compose**: Local development with AgentField control plane
- **Air-gapped**: Local Ollama with `OLLAMA_BASE_URL` environment variable
- **Cloud Ready**: Stateless design for horizontal scaling with PostgreSQL
- **Security**: Cryptographically-verified execution receipts for compliance

### Integration Points:
- **REST API**: Full API access to research capabilities
- **SSE Streaming**: Real-time workflow progress updates
- **Webhook Support**: Integration with external systems
- **Analytics Ready**: Structured results suitable for downstream processing

## Comparison to Alternative Solutions

### Traditional Research Tools:
- **Perplexity/ChatGPT**: One-shot generation, single query, unstructured output
- **Semantic Scholar**: Academic-focused, limited query iteration, citation-only output

### AF Deep Research:
- **Process**: Fan out → filter down → synthesize → find gaps → fan out again
- **Coverage**: Multiple parallel streams exploring different angles
- **Output**: Structured JSON with typed entities, mapped relationships, cited evidence
- **Quality**: Hyper-relevant content through two-tier filtering
- **Relationships**: Multi-pass extraction (explicit → implied → indirect → emergent)
- **Scaling**: Width AND depth scale with query complexity
- **Integration**: REST API, SSE streaming, webhook-ready
- **Deployment**: Self-host with local LLMs, air-gapped option

### Key Differentiators:
1. **Meta-Intelligence**: High-level orchestration and adaptation beyond traditional research
2. **Cross-Agent Mesh**: Coordinates multiple AI agents via AgentField control plane
3. **Philosophical Lenses**: Different perspectives (bull/bear/balanced) for comprehensive analysis
4. **Quality-Driven**: Continues until confidence thresholds met, not fixed iterations
5. **Network Intelligence**: Builds and refines entity/relationship graphs dynamically

## Use Cases & Applications

### Business Intelligence:
- **Investment research**: Company analysis, competitive landscape, market trends
- **M&A due diligence**: Target assessment, financial analysis, risk evaluation
- **Competitive intelligence**: Market positioning, strategy analysis, competitive moves

### Technology Assessment:
- **AI/ML research**: Model evaluation, capability assessment, trend analysis
- **Security research**: Threat analysis, vulnerability assessment, risk evaluation
- **Innovation tracking**: Technology emergence, adoption patterns, disruption signals

### Market Intelligence:
- **Industry analysis**: Market size, growth trends, competitive dynamics
- **Regulatory research**: Policy analysis, compliance requirements, geopolitical impact
- **Supply chain analysis**: Vendor assessment, risk mitigation, continuity planning

### Academic Research:
- **Literature review**: Comprehensive source gathering and synthesis
- **Meta-analysis**: Evidence aggregation and systematic review
- **Research gap analysis**: Unanswered questions and future directions

## Conclusion

AF Deep Research combines AgentField's production infrastructure with advanced recursive research algorithms to deliver a production-ready AI research backend. It scales intelligently with query complexity, maintains high-quality standards through adaptive filtering, and produces structured research packages suitable for integration into downstream analytics and decision support systems.

**Built by AgentField team** — early preview, APIs may change, feedback welcome through Discord and GitHub.

## Related

- **Contract-AF**: Legal contract risk analyzer with recursive multi-agent pattern
- **AF Reactive Atlas MongoDB**: Turn any MongoDB collection into an AI intelligence layer
- **agentfield**: Main AgentField control plane and SDK
- **SWE-AF**: Software engineering analysis for pull requests
- **sec-af**: Security analysis and vulnerability assessment

## Related

- [[af-deep-research]] -- wiki page for this agent
- [[af-deep-research-architecture]] -- architecture documentation
- [[agentfield]] -- core AgentField platform
- [[agentfield-profile]] -- AgentField platform profile