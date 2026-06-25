---
name: swe-af
tags: [ai-llm, docker, engineering-factory, git, multi-agent, orchestration, python, security, swe, swe-af, webhook, wiki]
description: Wiki entry for SWE-AF — autonomous software engineering factory runtime built on AgentField (Apache 2.0)
---

# SWE-AF

| Field | Value |
|---|---|
| **Origin** | [Agent-Field/SWE-AF](https://github.com/Agent-Field/SWE-AF) |
| **License** | Apache 2.0 |
| **Stack** | Python + Go + AgentField SDK |
| **Source** | `sources/SWE-AF/` |
| **Wanted** | Autonomous software engineering factory — plans, codes, tests, and ships PRs |

## What it is

An autonomous engineering team runtime on AgentField. One API call spins up a coordinated factory of agents (product manager, architect, coder, QA, reviewer, merger, verifier, synthesizer) that plan, build, test, and ship code changes end-to-end.

Built on [[agentfield]] — extends AgentField's single-agent harness to factory-scale orchestration across multiple specialized roles.

## Architecture

- **Factory pattern**: Coordinated control stack with role-specific agents (PM → Architect ↔ Tech Lead → Sprint Planner → Coder → QA/Reviewer/Synthesizer → Merger/Verifier)
- **Adaptive control loops**: 
  - Inner loop: Single issue retries via Issue Advisor
  - Middle loop: Issue adaptation (split, retry modified, retry approach, accept with debt)
  - Outer loop: DAG-level replanning via replanner
- **Per-issue git worktrees**: Isolated workspaces prevent branch collisions when executing hundreds of parallel agent instances
- **Parallel execution**: Hundreds of agents via AgentField control plane
- **Self-healing pipeline**: Checkpoints, replanning, and recovery from crashes/interruptions

## Key Source Files

### Core Runtime (`swe_af/` module)
- **`swe_af/app.py`**: Main AgentField app with `build`, `plan`, `execute`, `resolve`, `resume_build` reasoners
- **`swe_af/execution/`**: DAG execution engine (`dag_executor.py`), schemas (`schemas.py`), fatal error handling
- **`swe_af/reasoners/`**: Agent pipeline (`pipeline.py`, `execution_agents.py`), planning pipeline (`product_manager`, `architect`, `tech_lead`, `sprint_planner`)
- **`swe_af/fast/`**: Speed-optimized build mode (`fast/app.py`, `fast/planner.py`), thin wrappers for execution
- **`swe_af/hitl/`**: Human-in-the-loop (HAX) integration, credential negotiation, approval workflows

### Supporting Infrastructure
- **`Dockerfile`**, **`docker-compose.yml`**: Local deployment with AgentField control plane
- **`pyproject.toml`**: Python package configuration
- **`Makefile`**: Development/test utilities
- **`requirements.txt`**, **`requirements-docker.txt`**: Dependencies
- **`railway.toml`**: Railway deployment configuration

## Deployment

### With Railway (fastest)
One-click deploy to Railway with PostgreSQL. Requires two environment variables:
- `CLAUDE_CODE_OAUTH_TOKEN` — Claude Code CLI token (Pro/Max subscription credits)
- `GH_TOKEN` — GitHub personal access token with `repo` scope

Trigger a build:
```bash
curl -X POST https://<control-plane>.up.railway.app/api/v1/execute/async/swe-planner.build \
  -H "Content-Type: application/json" \
  -H "X-API-Key: this-is-a-secret" \
  -d '{"input": {"goal": "Add JWT auth", "repo_url": "https://github.com/user/my-repo"}}'
```

### Local Development
```bash
cp .env.example .env
# Add your API keys: ANTHROPIC_API_KEY, OPENROUTER_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY
# Optionally add GH_TOKEN for PR workflow

docker compose up -d
```

Once deployed, trigger a build:
```bash
af                 # starts AgentField control plane on :8080
python -m swe_af   # registers node id "swe-planner"
```

Trigger a build:
```bash
curl -X POST http://localhost:8080/api/v1/execute/async/swe-planner.build \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{
  "input": {
    "goal": "Add JWT auth",
    "repo_url": "https://github.com/user/my-repo"
  }
}
JSON
```

## Cross-System Integration

SWE-AF, as an AgentField sub-repo, integrates with the broader AgentField ecosystem:

- **Hermes**: Can trigger SWE-AF builds as part of larger automation workflows
- **OpenClaw**: Can invoke SWE-AF builders for specialized engineering tasks within OpenClaw pipelines
- **n8n**: Can connect to SWE-AF's REST API for no-code workflow orchestration

### Integration Patterns
1. **Direct API calls**: Use `/api/v1/execute/async/swe-planner.build` with goal and repo configuration
2. **Webhook-driven triggers**: Hermes nodes can POST to SWE-AF's async endpoints
3. **n8n integrations**: Use n8n's HTTP Request node to trigger builds with various configurations

### Configuration Options
SWE-AF accepts standard AgentField configuration plus SWE-AF-specific fields:

```json
{
  "goal": "Build user authentication system",
  "repo_url": "https://github.com/user/my-repo",
  "config": {
    "runtime": "claude_code",
    "models": { "default": "sonnet", "coder": "opus", "qa": "opus" },
    "enable_learning": true,
    "max_coding_iterations": 5,
    "agent_max_turns": 150
  }
}
```

## Key Features

- **One-Call DX**: Single API endpoint spins up full engineering team
- **Multi-repo support**: Orchestrates changes across multiple repositories
- **GitHub integration**: Opens PRs, monitors CI, auto-fixes failing checks
- **Adaptive factory**: Hard-aware execution with advisor-driven adaptation
- **Continual learning**: Cross-issue shared memory for conventions and failure patterns
- **Factory-scale parallelism**: Hundreds of agents via AgentField control plane
- **Explicit compromise tracking**: Debt typing and severity rating for relaxed requirements
- **Long-run reliability**: Checkpointed execution supports resume after crashes
- **SSE streaming**: Real-time build progress via Server-Sent Events

## Example Use Case

**Rust-based Python compiler** built autonomously:
- 175 tracked autonomous agents across planning, coding, review, merge, and verification
- 253.8x geometric mean speedup over CPython subprocess execution
- 95/100 benchmark score with Claude haiku-class models
- Built entirely by SWE-AF in one API call

## Agent Roles

1. **Product Manager**: Scopes goals into PRD with acceptance criteria
2. **Architect**: Designs technical architecture before coding begins
3. **Tech Lead**: Reviews architecture, ensures implementation alignment
4. **Sprint Planner**: Decomposes work into dependency-sorted issues
5. **Issue Writer**: Writes detailed issue specifications for each task
6. **Coder**: Implements code, writes tests, commits to isolated worktree
7. **QA**: Tests coder's work, augments test suite
8. **Code Reviewer**: Quality/security review with independent test execution
9. **QA Synthesizer**: Decides fix/approve/block based on QA+review feedback
10. **Issue Advisor**: Analyzes coding failures, decides adaptation strategy
11. **Replanner**: Restructures remaining DAG when failures escalate
12. **Merger**: Merges completed branches into integration branch
13. **Integration Tester**: Verifies cross-feature interactions
14. **Verifier**: Final acceptance against PRD
15. **GitHub PR**: Pushes and creates PRs, monitors CI

## Benchmark

**95/100 with haiku and MiniMax**: SWE-AF scores 95/100 with Claude haiku-class routing (~$20) and MiniMax M2.5 via open runtime (~$6), outperforming Claude Code sonnet (73), Codex o3 (62), and Claude Code haiku (59).

See [`examples/agent-comparison/README.md`](examples/agent-comparison/README.md) for detailed benchmark methodology and reproduction.

## Related

- [[swe-af-architecture]] -- architecture documentation
- [[swe-af-profile]] -- agent profile
- [[agentfield]] -- core AgentField platform
- [[agentfield-profile]] -- AgentField platform profile
- [[agentfield-deployment]] -- deployment guide
- [[sec-af]] -- sibling security auditor agent
- [[af-deep-research]] -- sibling research engine
- [[af-reactive-atlas-mongodb]] -- sibling MongoDB intelligence agent

---

### Also built on AgentField

> **[SEC-AF](https://github.com/Agent-Field/sec-af)** — AI-native security auditor. 250 agents per audit, 94% noise reduction, every finding proven exploitable.
>
> **[Contract-AF](https://github.com/Agent-Field/contract-af)** — Legal contract risk analyzer. Agents spawn agents at runtime. Adversarial review catches what solo LLMs miss.

SWE-AF is built on [AgentField](https://github.com/Agent-Field/agentfield) as a first step from single-agent harnesses to autonomous software engineering factories.

## Cross-project

- [[agentfield]] -- Core platform SWE-AF is built on
- [[hermes-agent]] -- Can trigger SWE-AF builds via Hermes automation
- [[openclaw]] -- Can invoke SWE-AF builders via API
- [[n8n]] -- Can orchestrate SWE-AF builds via no-code workflows
- [[gogs]] -- Git operations in SWE-AF engineering pipeline
- [[sec-af]] -- Sibling security auditor on AgentField
- [[af-deep-research]] -- Sibling research engine on AgentField
- [[af-reactive-atlas-mongodb]] -- Sibling MongoDB intelligence on AgentField
- [[buildah]] -- Image building in engineering pipeline