---
name: sec-af-architecture
tags: [sec-af, architecture, python, security, auditor, adversarial]
description: Architecture of SEC-AF — AI-native security auditor extending AgentField multi-reasoner for adversarial security analysis
---

# SEC-AF Architecture Documentation

**Source:** `sources/sec-af/`
**Raw:** `raw/sec-af/sec-af.xml` (1.3M)
**Codegraph:** `graphs/sec-af/` (3.2M)

## Overview

SEC-AF (Security Auditing with AgentField) is an AI-native security auditor built as a sub-repo within the AgentField platform. It extends the AgentField multi-reasoner architecture specifically for adversarial security analysis that goes beyond pattern detection to prove actual exploitability.

## Architecture Overview

### Core Architecture Patterns

SEC-AF leverages AgentField's **Composite Intelligence** philosophy through a **4-agent verification chain**:

1. **Tracer Agent** — Reconstructs source-to-sink data flows
2. **Sanitization Analyzer** — Identifies and evaluates security mitigations  
3. **Exploit Hypothesizer** — Constructs concrete attack scenarios
4. **Verdict Agent** — Weighs conflicting evidence to reach final verdict

This adversarial tension between HUNT vs PROVE phases drives the 94% noise reduction in findings.

### Signal Cascade Pipeline

SEC-AF implements a **progressive signal narrowing** approach:

- **Phase 1: RECON** (3-way parallel)
  - Architecture mapping (what code exists)
  - Dependency analysis (what's being used)
  - Configuration scanning (security misconfigurations)

- **Phase 2: HUNT** (streaming with incremental dedup)
  - 10+ strategy hunters activated by AI gates
  - Injection, Auth, Crypto, XSS, SSRF, etc.
  - Parallel processing with semaphore bounds

- **Phase 3: PROVE** (adversarial verification)
  - Each finding undergoes adversarial verification
  - Tracer → Sanitizer → Exploit → Verdict chain
  - Streaming verification with early pruning

- **Phase 4: REMEDIATION** (fix suggestion generation)

### Dynamic AI Gates

SEC-AF uses runtime adaptation through **AI routing gates**:

- **Strategy Selection Gate**: Routes reconnaissance output to appropriate hunt strategies
- **CWE Expansion Gate**: Dynamically broadens vulnerability targets based on tech stack
- **Reachability Gate**: Filters findings based on exploitable call paths
- **Context Pruning Gate**: Provides strategy-specific recon context (inject hunter vs crypto hunter)

### Technical Architecture

#### Data Flow Processing
- **RECON Stage**: 3 parallel processes (architecture/deps/config)
- **HUNT Stage**: Semaphore-bounded parallel hunters
- **PROVE Stage**: Further parallelization with 3 concurrent provers
- **STREAMING**: Each phase overlaps via asyncio.Queue consumption

#### Agent Communication
- All reasoner calls flow through AgentField control plane
- Creates a complete DAG for full observability
- Each agent call is a "atomic unit of intelligence" with flat Pydantic schemas

### Key Components

#### Reasoner DAG Structure
```
RECON (3-way parallel)
├── Architecture mapper
├── Dependency auditor  
└── Config scanner

HUNT (strategy hunters)
├── Injection hunter
├── Auth hunter
├── Crypto hunter
├── XSS hunter
├── 6+ additional hunters...

PROVE (4-agent chain per finding)
├── Tracer
├── Sanitization analyzer
├── Exploit hypothesizer
└── Verdict agent
```

#### Integration Systems

SEC-AF is compatible with the 4 core AgentField systems:

- **HARMONIZE**: Teams integration — shares findings with Team platforms
- **BRAHM**: Build pipeline integration — hooks into CI/CD systems
- **SKYHOOK**: Multi-cloud orchestration — deploys across cloud environments  
- **TEMPEST**: Security orchestration — integrates with existing security workflows

### Comparison to Other Security Tools

| Architecture Pattern | SEC-AF | Nullify | Snyk | Semgrep | CodeQL |
|---------------------|--------|---------|------|---------|--------|
| **AI Approach** | Multi-reasoner DAG | Autonomous workforce | AI-assisted | Rule-based | Rule-based |
| **Verification** | Adversarial PROVE phase | Exploit generation | Priority scoring | Pattern matching | Path queries |
| **Evidence** | Full proof chain | Exploit steps | No exploit proof | Limited flow | Basic flow |
| **Open Source** | ✅ Apache 2.0 | ❌ Proprietary | ❌ | LGPL/Prop | MIT/Prop |
| **Pricing** | $0.18-$0.90/audit | $6,000/mo | $25-105/mo | $30/mo | Free/committer |

### Testing Strategy

SEC-AF uses **integration-first testing**:

- **Unit Tests**: Component-level testing of agent functions
- **E2E Tests**: Full pipeline against test repositories
- **Benchmark Testing**: DVGA (Damn Vulnerable GraphQL Application) with documented results
- **Mutation Testing**: Checks API for breaking changes

### Deployment Integration

SEC-AF can be triggered via:

```bash
# AF CLI
af call sec-af.audit --in '{"repo_url": "https://github.com/example"}'

# Direct API call
curl -X POST http://localhost:8080/api/v1/execute/async/sec-af.audit \
  -H "Content-Type: application/json" \
  -d '{"input": {"repo_url": "..."}}'
```

### Performance Metrics

- **DVGA Benchmark**: 106 raw findings → 28 confirmed (94% noise reduction)
- **Agent Calls**: ~166-255 total for standard depth audit
- **DAG Edges**: 82 directed acyclic graph connections
- **Estimated Cost**: ~$0.18-$0.90 per 30 findings (Kimi K2.5)
- **Wall-clock**: ~78 minutes for standard DVGA audit

### Security Considerations

- **Air-gapped capability**: Local LLMs supported
- **Context minimization**: Each agent receives only what it needs
- **Budget controls**: Cost enforcement via DESIGN.md §9
- **Compliance mapping**: PCI-DSS, SOC2, OWASP, HIPAA, ISO27001 built-in

### Adding New Vulnerability Classes

To add a new vulnerability class:

1. Create a new hunter file in `src/sec_af/agents/hunt/`
2. Implement hunter strategy in `src/sec_af/reasoners/hunt.py`
3. Add prompts in `prompts/hunt/`
4. The orchestrator discovers and runs it automatically

This modularity enables continuous expansion of the security analysis capabilities without changes to the core pipeline.

## Related

- [[sec-af]] -- wiki page for this agent
- [[sec-af-profile]] -- agent profile
- [[agentfield]] -- core AgentField platform
- [[agentfield-architecture]] -- platform architecture
- [[agentfield-deployment]] -- deployment guide