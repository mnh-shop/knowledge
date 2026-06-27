---
name: af-deep-research-architecture
tags: [af-deep-research, architecture, cli, container, deep-research, docker, orchestration, plugin-sdk, recursive-agents, research, security, typescript]
description: Architecture of AF Deep Research — autonomous research backend with recursive agent spawning and self-correcting loops
source: sources/af-deep-research/
---

# AF Deep Research Architecture

**Source:** `sources/af-deep-research/`
**License:** Apache 2.0  
**Repository:** github.com/Agent-Field/af-deep-research  
**Stack:** Python + AgentField SDK + LiteLLM  

## Overview

AF Deep Research is a **recursive research engine** that self-corrects through iterative cycles. It spawns parallel agents, evaluates quality against thresholds, generates new sub-queries for gaps, and repeats — orchestrating approximately **10,000 logical agent invocations per research query**. Built on the AgentField "sub-repo" SDK, it's an AI backend not a chat interface.

## Recursive Research Loop

### Core Architecture Flow:
1. **Query Classification** → Determine research domain (Market_Intelligence, Entity_Analysis, Competitive_Analysis, Technology_Assessment, Strategic_Assessment)
2. **Fan-out** → Generate adaptive search streams (parallel parallel research angles)
3. **Execute** → Parallel intelligence stream execution with web search, evidence extraction, and entity extraction
4. **Network Analysis** → Build entity/relationship graph with consolidation and deduplication
5. **Synthesis** → Generate hypotheses, assess research completeness, identify gaps
6. **Quality Assessment** → Evaluate confidence, adequacy, critical gaps
7. **Gap-Filling** → Generate targeted sub-queries for missing insights
8. **Loop Decision** → Continue if quality thresholds not met, otherwise terminate

### Key Components:

#### Meta-Intelligence Layer (reasoners/)
- **Meta-Reasoning Controller** - Central strategy selection based on learning insights and performance history
- **Adaptive Reasoning Strategist** - Dynamic strategy adaptation during execution
- **Dynamic Prompt Constructor** - Context-aware prompt building and evolution  
- **Context-Aware Scheduler** - Intelligent workflow execution with resource optimization
- **Meta-Learning Coordinator** - Cross-session learning and improvement

#### Universal Research Orchestrator (research_orchestrator.py)
- Implements **Dynamic Hierarchy of Execution (DHE)** with complexity-based branching
- Quality-driven recursive loops with adaptive re-execution
- Parallel execution for complex queries
- Meta-learning feedback loops for continuous improvement

#### Universal Reasoners (universal_reasoners.py) 
- **Query Analysis Reasoner** - Analyzes intent, complexity, and research requirements  
- **Domain Strategy Reasoner** - Creates domain-specific search and analysis approaches
- **Research Execution Reasoner** - Executes actual research using search engines
- **Quality Control Reasoner** - Assesses research quality and completeness
- **Synthesis Reasoner** - Synthesizes findings into coherent, comprehensive responses
- **Research Validation Reasoner** - Validates synthesis against original sources

#### Dynamic Models (dynamic_models.py)
- Reasoning strategies, prompt templates, research contexts
- Memory states, learning insights, adaptation decisions
- Quality metrics, search strategies, workflow steps
- Execution status, evidence models, entity/relationship schemas

#### Reasoning Infrastructure (dynamic_infrastructure.py)
- Dynamic prompt builders and strategy registry reasoners
- Learning and adaptation capabilities
- Memory state management across workflow executions

## How It Uses AgentField Reasoners + Skills

### AgentField Integration:
- Built as a **sub-repo** within the AgentField ecosystem
- Uses `@app.reasoner()` decorators for AI reasoning functions
- Leverages `app.ai()` for LLM calls and `app.call()` for cross-agent routing
- Implements AgentField's harness orchestration patterns
- Follows cross-agent mesh architecture with service discovery

### Reasoner Usage Patterns:
1. **Parallel Execution** - Multiple reasoners run concurrently using `app.call()` with async workflow
2. **Memory Persistence** - Research state stored in Brain memory across iterations
3. **Dynamic Strategy Selection** - Meta-reasoners adapt based on performance and learning insights
4. **Cross-Agent Communication** - Reasoners coordinate via AgentField's control plane

## Quality Threshold Mechanism

### Multi-Level Quality Gates:
1. **Source Validation** (`source_strictness: "strict/mixed/permissive"`)
2. **Evidence Quality** - Source reliability, consistency, and verification scores
3. **Network Completeness** - Entity coverage, relationship depth, and connection quality
4. **Hypothesis Confidence** - Research thesis supporting strength vs. counter risks
5. **Iteration-Based Stopping** - Continues while confidence < 0.8 or evidence inadequate

### Quality Metrics:
- **confidence_score** (0.0-1.0): Overall research confidence
- **evidence_adequacy** ('sufficient/moderate/insufficient'): Evidence strength
- **critical_gaps_present** (bool): Major knowledge gaps remain
- **final_quality_score**: Final threshold for human review

## Package/Module Structure

### Core Package Structure:
- **main.py** - Entry point, Agent instantiation, and API server
- **reasoners/** - Meta-intelligence and universal reasoner modules
- **skills/** - Search capabilities and utility functions
- **packages/** - Third-party dependencies and module arrangements
- **assets/** - Architecture diagrams and UI components
- **tests/** - Unit and integration tests
- **docs/** - Documentation and generation scripts

### Key Files:
- **doc_generation_pipeline.py** - Intelligent document publishing pipeline
- **temporal_context.py** - Temporal context injection for reasoners  
- **utils.py** - Search utilities and compatibility functions
- **research_package.py** - Research result serialization

## Research Result Format

### UniversalResearchPackage Schema:
```json
{
  "query": "Original research question",
  "core_thesis": "Central hypothesis",
  "key_discoveries": ["Findings 1", "Finding 2"],
  "confidence_assessment": "Iterative analysis across X cycles...
  "entities": [
    {"name": "Company", "type": "Organization", "summary": "Description"}
  ],
  "relationships": [
    {"source_entity": "AMD", "target_entity": "NVIDIA", "description": "Competes with",
     "relationship_type": "Competes_With"}
  ],
  "observed_causal_chains": ["Chain 1", "Chain 2"],
  "hypothesized_implications": ["Risk 1", "Opportunity 2"],
  "next_inquiry_probes": [{"question": "Gap question", "rationale": "Why needed"}],
  "source_articles": [{"id": 1, "title": "Source", "url": "", "content": ""}],
  "article_evidence": [{"article_id": 1, "facts": ["Fact 1"], "quotes": ["Quote 1"]}]
}
```

### API Response Structure:
- **mode**: "general" - Research mode used
- **version**: "5.0-Iterative-Meta" - System version
- **research_package**: Complete structured research data
- **metadata**: Timing and performance statistics

## Performance Characteristics

### Scale and Throughput:
- **10,000+ agent invocations** per research query
- **Concurrent execution** of 2-4 parallel search streams
- **Iterative refinement** with adaptive strategy selection
- **16+ minute workflows** for complex queries
- **SSE streaming** for real-time progress updates

### Efficiency Features:
- **Two-tier filtering**: Hash dedup → semantic dedup → relevance scoring
- **Cross-stream synthesis**: Detects patterns between parallel research angles
- **Network consolidation**: Merges duplicate entities and relationships
- **Meta-learning**: Improves strategy selection over time
- **Parallel execution**: Optimizes resource utilization for complex queries

## Comparison to Other Research Tools

### Traditional Research Tools:
- **Perplexity/ChatGPT**: One-shot generation, single query, prose output
- **Complex**: Manual query iteration, limited scaling, unstructured output

### AF Deep Research:
- **Process**: Fan out → filter down → synthesize → find gaps → fan out again
- **Coverage**: Multiple parallel streams, each exploring different angles
- **Output**: Structured JSON with typed entities, mapped relationships, cited evidence
- **Quality**: Two-tier filtering ensures only hyper-relevant content reaches models
- **Relationships**: Multi-pass extraction: explicit → implied → indirect → emergent patterns
- **Scaling**: Width AND depth scale with query complexity
- **Integration**: REST API, SSE streaming, webhook-ready
- **Deployment**: Self-host with local LLMs, air-gapped option

### Key Differentiators:
1. **Self-Correcting Loops**: Asks "what am I missing?" at each iteration
2. **Cross-Agent Mesh**: Coordinates multiple AI agents via AgentField control plane
3. **Philosophical Lenses**: `balanced`, `bull`, or `bear` perspective control
4. **Quality-Driven**: Continues until confidence thresholds met, not fixed iteration count
5. **Network Intelligence**: Builds and refines entity/relationship graphs dynamically

## Deployment Architecture

### Environment Variables:
- `OPENROUTER_API_KEY`: LLM inference provider
- `JINA_API_KEY/TAVILY_API_KEY`: Search provider API keys  
- `AGENTFIELD_SERVER`: Control plane connection
- `DEFAULT_MODEL`: LLM model selection
- `TEMPERATURE`: Generation randomness

### Container Stack:
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
    depends_on: [agentfield]
```

### Deployment Options:
- **Docker Compose**: Local development with AgentField control plane
- **Direct Python**: Synchronous execution without control plane
- **Air-gapped**: Local Ollama with `OLLAMA_BASE_URL` environment variable
- **Cloud Ready**: Stateless design for horizontal scaling

## Compatibility with 4 Core AgentField Systems

### SDK Integration:
1. **Python SDK**: Fully integrated with AgentField's reasoner/skill patterns
2. **Go SDK**: Cross-language agent coordination support  
3. **TypeScript SDK**: Web UI and Node.js agent support
4. **Harness Orchestration**: Integration with Claude Code, Codex, Gemini CLI tools

### System Features:
- **REST API**: Every reasoner exposed as HTTP endpoint with cryptographic provenance
- **Cross-Agent Routing**: Zero-trust agent-to-agent communication through control plane
- **W3C DID Identity**: Verifiable credentials for all agents and executions
- **Tag-Based IAM**: Fine-grained access control and policy management
- **Workflow DAG**: Complex orchestration with dependency tracking
- **Memory Persistence**: Research state and learning insights across sessions
- **Audit Trails**: Cryptographically-signed execution records for compliance

### Usage Patterns:
```bash
# One-call DX via af CLI
af call meta_deep_research.execute_deep_research --in '{"query": "What companies are investing in AI chips?"}'

# Or direct HTTP
curl -X POST http://localhost:8080/api/v1/execute/async/meta_deep_research.execute_deep_research \
  -H "Content-Type: application/json" \
  -d '{"input": {"query": "What companies are investing in AI chips?"}}'
```

## Conclusion

AF Deep Research represents the next evolution in autonomous research systems, combining AgentField's production infrastructure with advanced recursive research algorithms. It transforms complex knowledge discovery into a structured, quality-assured process that scales intelligently with query complexity, delivering production-ready research packages suitable for integration into downstream analytics, decision support, and intelligence systems.

## Related

- [[af-deep-research]] -- wiki page for this agent
- [[af-deep-research-profile]] -- agent profile
- [[agentfield]] -- core AgentField platform
- [[agentfield-architecture]] -- platform architecture
- [[agentfield-deployment]] -- deployment guide