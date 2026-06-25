---
name: sec-af-profile
tags: [sec-af, profile, python, security, auditor, adversarial, ai-llm, automation, agent-profile, cli, docker, git, messaging, monitoring, optimization, orchestration, plugin-sdk]
description: Agent profile for SEC-AF — AI-native security auditor agent built on AgentField for adversarial security analysis
---

# SEC-AF Agent Profile

**Source:** `sources/sec-af/`
**Raw:** `raw/sec-af/sec-af.xml` (1.3M)
**Codegraph:** `graphs/sec-af/` (3.2M)

## What SEC-AF Is

SEC-AF is an **AI-native security auditor agent** built on the AgentField platform that performs adversarial security analysis to prove actual exploitability rather than just detecting patterns. It represents the security analysis specialization within the broader AgentField ecosystem.

## Agent Capabilities

### Core Expertise
- **Adversarial Security Analysis**: Uses the HUNT vs PROVE architecture to verify exploitability
- **Multi-Reasoner Coordination**: Manages a DAG of 200+ focused AI agents working in parallel
- **Deep Code Analysis**: Traces data flows from sources to sinks, proving or disproving vulnerabilities
- **Real Adversary Simulation**: Constructs concrete attack scenarios to test defenses
- **Compliance Mapping**: Maps findings to PCI-DSS, SOC2, OWASP, HIPAA, ISO27001 controls

### Key Skills
1. **Technology Stack Detection**: Analyzes codebases to identify frameworks, languages, and patterns
2. **Vulnerability Hunting**: Runs 10+ specialized hunters (injection, auth, crypto, XSS, etc.)
3. **Exploit Verification**: Four-agent adversarial chain for each finding (tracer, sanitizer, exploit hypothesize, verdict)
4. **Budget Management**: Cost-controlled execution with configurable depth profiles
5. **Integration Ready**: Can be called from Hermes, OpenClaw, n8n, or any AgentField-compatible system

## Configuration Reference

### Required Environment Variables
```bash
# API Keys
OPENROUTER_API_KEY=your_api_key_here

# AgentField Connection (for distributed orchestration)
AGENTFIELD_URL=http://localhost:8080
AGENTFIELD_API_KEY=your_agentfield_api_key

# Cost Control
MAX_COST_USD=1.0
MAX_PROVERS=30
MAX_DURATION_SECONDS=3600
```

### Configuration Options

#### Depth Profiles (DESIGN.md §9)
- **QUICK**: Basic injection/auth/crypto hunting
- **STANDARD**: Full suite of 10+ strategies with deep verification
- **THOROUGH**: Comprehensive analysis including language-specific protections

#### Scan Types
```json
{
  "scan_types": ["sast", "sca", "secrets", "config"],
  "severity_threshold": "low",
  "compliance_frameworks": ["PCI-DSS", "OWASP"]
}
```

#### Output Formats
- JSON: Machine-readable findings
- SARIF: GitHub Code Scanning integration
- Report: HTML human-readable analysis

## How to Trigger SEC-AF Audits

### 1. Via AF CLI
```bash
af call sec-af.audit \
  --in '{"repo_url": "https://github.com/example/repo"}' \
  --depth "standard" \
  --compliance_frameworks ["OWASP", "PCI-DSS"]
```

### 2. Direct API Call
```bash
curl -X POST http://localhost:8080/api/v1/execute/async/sec-af.audit \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "repo_url": "https://github.com/example/repo",
      "depth": "standard",
      "scan_types": ["sast", "sca"],
      "compliance_frameworks": ["OWASP"]
    }
  }'
```

### 3. As a SUB-REASONER
```python
# Within an AgentField workflow
await app.reasoner(name="sec-af.audit")(
    repo_url="github.com/example/repo",
    depth="thorough",
    max_cost_usd=2.0
)
```

## Integration Patterns

### With Hermes
```yaml
task: security_audit
agent: sec-af
parameters:
  repo: "{{ trigger.repository }}"
  depth: "standard"
  scan_types: ["sast", "sca"]
```

### With OpenClaw
```python
from agentfield import execute_with_claw

result = await execute_with_claw(
    task_type="security",
    agent="sec-af",
    target_repo="my-org/my-app",
    options={
        "scan_types": ["secrets", "config"],
        "compliance": ["SOC2", "HIPAA"]
    }
)
```

### With n8n
```json
{
  "agent": "sec-af",
  "action": "audit",
  "parameters": {
    "repo_url": "{{ $json.payload.repository }}",
    "max_cost_usd": 1.5,
    "scan_types": ["sast", "secrets"]
  },
  "callbacks": {
    "on_complete": "update_issue",
    "on_error": "notify_team"
  }
}
```

## Execution Flow

When an audit is triggered, SEC-AF executes this pipeline:

1. **Startup Phase**
   - Load AgentField environment
   - Initialize audit configuration from input
   - Set up cost tracking and progress reporting

2. **RECON Phase** (parallel - ~30 seconds)
   - Architecture mapping (what exists)
   - Dependency analysis (what's used)  
   - Configuration scanning (misconfigurations)

3. **HUNT Phase** (streaming - ~10 minutes)
   - AI gates select relevant strategies based on tech stack
   - 10+ hunters run in parallel (4 concurrent by default)
   - Incremental deduplication as findings arrive

4. **PROVE Phase** (streamed verification - ~45 minutes)
   - Each raw finding enters 4-agent adversarial chain
   - **Tracer**: Reconstructs data flows
   - **Sanitizer**: Evaluates mitigation effectiveness
   - **Exploit Hypothesizer**: Builds attack scenarios
   - **Verdict Agent**: Decides confirmed/likely/inconclusive/not_exploitable
   - **Chain Building**: Forms attack chains from related findings

5. **REMEDIATION Phase** (fix suggestions - ~5 minutes)
   - Generates fix recommendations for confirmed findings
   - Respects company standards and compliance requirements

6. **Output Generation** (~1 minute)
   - JSON findings for programmatic use
   - SARIF for GitHub Code Scanning
   - Human-readable reports
   - Compliance gap analysis

## Agent Interaction Model

### When to Use SEC-AF

**Use SEC-AF when you need:**
- Proof of exploitability, not just pattern matching
- Comprehensive adversarial security testing
- Integration with existing AgentField workflows
- Cost-controlled, depth-configurable audits
- Full observability of security findings lifecycle
- Compliance mapping and gap analysis

**Don't use SEC-AF when:**
- Quick pattern-based scanning is sufficient
- You need pure rule-based scanning with zero AI dependencies
- Budget constraints cannot accommodate even minimal AI costs
- The codebase is in an air-gapped environment without local LLMs

### Output Formats

SEC-AF agents output structured data through the AgentField control plane:

#### Standard Output Schema
```json
{
  "repository": "github.com/example/repo",
  "commit_sha": "abc123",
  "branch": "main",
  "depth_profile": "standard",
  "strategies_used": ["injection", "auth", "crypto"],
  "findings": [{
    "id": "SEC-AF-001",
    "title": "SQL Injection in User Query",
    "severity": "critical",
    "verdict": "confirmed",
    "evidence_level": 6,
    "cwe_id": "CWE-89",
    "proof": {
      "exploit_hypothesis": "Construct SQL injection payload",
      "verification_method": "composite_subagent_chain:sast",
      "data_flow_trace": [...],
      "exploit_payload": "' OR '1'='1"
    }
  }],
  "attack_chains": [...],
  "cost_usd": 0.45,
  "duration_seconds": 89
}
```

### Performance Characteristics

| Metric | Typical Values |
|--------|----------------|
| **Quick Depth** | 2-5 findings, $0.10-0.30 |
| **Standard Depth** | 20-30 findings, $0.18-$0.90 |
| **Thorough Depth** | 40-60 findings, $0.60-$1.20 |
| **Parallel Agents** | 10 hunters, 3-4 provers |
| **Wall Clock Time** | 60-90 minutes for full audit |

### Cost Optimization

SEC-AF includes several cost-control mechanisms:

1. **Depth Profiles**: QUICK costs minimal, THOROUGH maximizes thoroughness
2. **Budget Limits**: Configurable max_cost_usd, max_provers, max_duration
3. **Context Pruning**: Each agent receives only relevant information
4. **Parallel Efficiency**: Overlapping phases and concurrent execution
5. **Early Pruning**: Findings are filtered progressively through the pipeline

### Monitoring and Observability

SEC-AF creates a complete directed acyclic graph (DAG) of all security analysis:

- **Agent Calls**: 200-300 individual AI interactions per standard audit
- **Execution Timeline**: Real-time progress updates via structured logging
- **Cost Tracking**: Per-phase cost breakdowns and total spend
- **Findings Lifecycle**: Raw → Deduplicated → Verified → Remediated
- **Error Tracking**: Detailed error reporting for agent failures

## Relationship to AgentField Platform

SEC-AF is a **sub-repo** within the AgentField ecosystem:

- **Inheritance**: Shares the same multi-reasoner architecture as SWE-AF, SWE-AF, etc.
- **Integration**: Uses AgentField's harness system for agent coordination
- **Distribution**: Can be deployed as part of global AgentField workloads
- **Extensibility**: New vulnerability classes can be added without touching core pipeline
- **Orchestration**: Compatible with AgentField's distributed execution and scaling

## Technical Specifications

### Platform Requirements
- **Python**: 3.11+
- **Dependencies**: AgentField SDK, FastAPI, pydantic, asyncio
- **Infrastructure**: Requires AgentField control plane (optional for local deployment)
- **Memory**: 8GB+ for concurrent agent execution
- **Network**: OpenRouter API key required (optional for local LLM deployment)

### API Interface
```python
@app.reasoner(name="audit")
async def audit(
    repo_url: str,
    depth: str = "standard",
    branch: str = "main",
    # ... additional parameters
) -> dict[str, object]:
    """Run a complete security audit with adversarial verification."""
```

### Scalability
SEC-AF is designed for enterprise-scale security analysis:

- **Concurrent Limits**: Configurable hunter/prover limits (default: 4 hunters, 3 provers)
- **Memory Management**: Temporary execution directories for each agent
- **Distributed Ready**: Works across multiple machines in AgentField deployments
- **Checkpointing**: Supports resuming interrupted audits

## Current Limitations

- **DAST Integration**: DAST-like runtime verification is experimental
- **Protocol-level Detection**: GraphQL and other protocol-level attacks not yet supported
- **Cloud Environment Analysis**: Limited support for cloud-native security patterns
- **Machine Learning**: No automated model training or updating capabilities

## Future Roadmap

The SEC-AF team is actively working on:

1. **Protocol-level Testing**: GraphQL, gRPC, WebSocket security analysis
2. **Container Security**: Docker image and Kubernetes manifest analysis
3. **Compliance Automation**: Automated fix suggestions mapped to controls
4. **Integration Hubs**: Built-in integrations with major security tools
5. **Local Deployment Templates**: Minimal infrastructure requirements

## Contact and Support

For questions, issues, or support:

- **GitHub**: `github.com/Agent-Field/sec-af`
- **Documentation**: This profile and `docs/` directory
- **Community**: AgentField Slack/Discord channels
- **Production Support**: Enterprise subscription through AgentField

## Related

- [[sec-af]] -- wiki page for this agent
- [[sec-af-architecture]] -- architecture documentation
- [[agentfield]] -- core AgentField platform
- [[agentfield-profile]] -- AgentField platform profile
- [[swe-af-profile]] -- sibling SWE-AF profile