---
name: swe-af-architecture
tags: [agentfield, engineering, swe, architecture]
---

# SWE-AF Architecture Documentation

## Overview

SWE-AF (Autonomous Software Engineering Factory) is an autonomous engineering team runtime built on AgentField. It transforms a single API call into a coordinated factory of specialized agents that plan, code, test, and ship complex software end-to-end.

## Core Architecture Principles

### 1. **Factory Pattern over Wrapper Pattern**
SWE-AF is not a single-agent wrapper. It's a coordinated control stack where each agent role operates independently yet collaboratively, forming the engineering strategy rather than just following prompts.

### 2. **Adaptive Control Loops**
Three nested loops provide real-time adaptation to task difficulty:

- **Inner Loop**: Single issue execution and retries
- **Middle Loop**: Issue Advisor adaptation (split, retry modified, retry approach, accept with debt)
- **Outer Loop**: DAG-level replanning when failures escalate

### 3. **Per-Issue Git Worktrees**
Isolated workspaces prevent branch collisions when executing hundreds of parallel agent instances across multiple repositories.

## System Architecture

### Control Plane

SWE-AF runs as an AgentField node with a custom router that exposes multiple REST endpoints:

```
af (control plane)               ← Orchestrates agent fleet
  │ swe-planner (node)            ← Registers and routes calls
    ├─ /api/v1/execute/async/build ← Entry point for full builds
    ├─ /api/v1/execute/async/plan  ← Planning only
    ├─ /api/v1/execute/async/execute ← Execute prebuilt plan
    └─ /api/v1/execute/async/resume_build ← Resume crashed builds
```

### Agent Roles and Flow

```
Goal → PM → Architect ↔ Tech Lead → Sprint Planner → Issues → Coders → QA/Reviewers → Merger/Verifier → PR
```

### Key Components

#### 1. **Planning Pipeline** (`swe_af/reasoners/pipeline.py`)
- `run_product_manager`: Goal → PRD
- `run_architect`: PRD → Architecture
- `run_tech_lead`: Architecture → Review (loop with architect)
- `run_sprint_planner`: Architecture → Issues (dependency-sorted, topologically leveled)

#### 2. **Execution Pipeline** (`swe_af/execution/dag_executor.py`)
- `run_dag`: Coordinated execution across parallel levels
- `run_workspace_setup`: Creates isolated git worktrees
- `run_coder`: Issue implementation with test writing
- `run_qa`: Test augmentation and execution
- `run_code_reviewer`: Quality/security review
- `run_qa_synthesizer`: Decides fix/approve/block
- `run_issue_advisor`: Failure analysis and adaptation
- `run_replanner`: DAG restructuring

#### 3. **Post-Execution Gates** (`swe_af/execution/`)
- `run_merger`: Branch merging with conflict resolution
- `run_integration_tester`: Cross-feature integration testing
- `run_verifier`: Final acceptance criteria verification
- `run_github_pr`: PR creation and CI monitoring

#### 4. **Support Systems**
- `run_git_init`: Repository initialization with worktree setup
- `run_ci_watcher`: GitHub CI monitoring with polling
- `run_ci_fixer`: Automated CI fix-and-repush loop
- `run_pr_resolver`: Open PR resolution (merges + fixes + comments)

## Technical Details

### 1. **DAG Execution Model**

Issues are organized into parallel execution levels based on dependencies:

```python
levels = [
    ["issue-1", "issue-2"],  # Level 0: Can run in parallel
    ["issue-3"],            # Level 1: Waits for dependencies in level 0
    ["issue-4", "issue-5"], # Level 2: Waits for issue-3
]
```

Each level executes concurrently, but issues within a level can run in parallel up to `max_concurrent_issues`.

### 2. **Worktree Isolation**

For each issue, a dedicated git worktree is created:

```
repo/
├── .git/
├── .worktrees/                              ← Worktrees directory
│   ├─ issue/01-add-auth/                      ← Issue A worktree
│   │   ├── .git/                            ← Dedicated worktree git
│   │   └── src/                             ← Isolated workspace
│   └─ issue/02-refactor-auth/                ← Issue B worktree
│       ├── .git/
│       └── src/
└── main/                                    ← Integration branch
    └── src/                                 ← Shared base code
```

### 3. **Model Configuration**

SWE-AF uses a flat role-based model configuration:

```json
{
  "runtime": "claude_code",
  "models": {
    "default": "sonnet",
    "pm": "haiku",
    "architect": "haiku", 
    "tech_lead": "haiku",
    "sprint_planner": "haiku",
    "coder": "opus",
    "qa": "haiku",
    "code_reviewer": "haiku",
    "replan": "haiku",
    "verifier": "haiku"
  }
}
```

### 4. **Checkpoint and Resume**

DAG execution is checkpointed at level boundaries to support resume after crashes:

```
.artifacts/
├── execution/
│   └── checkpoint.json            ← Current DAG state
├── plan/
│   ├── prd.md
│   ├── architecture.md
│   └── issues/                      ← Issue specifications
└── verification/                   ← Acceptance criteria results
```

### 5. **Multi-Repo Support**

SWE-AF can orchestrate changes across multiple repositories:

```json
{
  "repos": [
    {
      "repo_url": "https://github.com/org/main-app",
      "role": "primary"
    },
    {
      "repo_url": "https://github.com/org/shared-lib", 
      "role": "dependency"
    }
  ]
}
```

Roles:
- `primary`: Changes drive the build, failures block progress
- `dependency`: Libraries/services modified, failures captured but don't block

## Runtime Configuration

### ExecutionConfig (`swe_af/execution/schemas.py`)

```python
class ExecutionConfig(BaseModel):
    runtime: Literal["claude_code", "open_code", "codex"] = "claude_code"
    models: dict[str, str] | None = None
    
    # Inner loop control
    max_retries_per_issue: int = 1
    max_coding_iterations: int = 5
    agent_max_turns: int = 150
    
    # Middle loop control
    max_advisor_invocations: int = 2
    enable_issue_advisor: bool = True
    
    # Outer loop control
    max_replans: int = 2
    enable_replanning: bool = True
    level_failure_abort_threshold: float = 0.8
    
    # Git workflow
    agent_timeout_seconds: int = 2700
    check_ci: bool = True
    max_ci_fix_cycles: int = 2
```

### BuildConfig (`swe_af/execution/schemas.py`)

```python
class BuildConfig(BaseModel):
    # Runtime selection
    runtime: Literal["claude_code", "open_code", "codex"] = "claude_code"
    models: dict[str, str] | None = None
    
    # Pipeline configuration
    max_review_iterations: int = 2
    max_plan_revision_iterations: int = 2
    max_verify_fix_cycles: int = 1
    
    # Git workflow
    enable_github_pr: bool = True
    check_ci: bool = True
    ci_wait_seconds: int = 1500
    ci_poll_seconds: int = 30
    
    # Learning and adaptation
    enable_learning: bool = False
    enable_issue_advisor: bool = True
    enable_replanning: bool = True
    
    # Advanced settings
    max_concurrent_issues: int = 3  # Parallel execution limit per level
    approval_expires_in_hours: int = 72  # HAX plan approval timeout
```

## Fast Mode (`swe_af/fast/`)

Speed-optimized variant with single-pass planning:

- **No PM**: Single LLM call decomposes goal into flat tasks
- **Sequential execution**: Tasks run one by one (not DAG-based)
- **No replanning**: Fixed scope for performance-critical workflows
- **Trade-offs**: Less adaptive, much faster for simple changes

Use Fast mode when you need speed over adaptability, e.g., for routine bug fixes or documentation updates.

## Comparison with Other Frameworks

| Feature | SWE-AF | SWE-agent | OpenHands |
|---------|--------|-----------|-----------|
| **Architecture** | Factory pattern with coordinated roles | Single coder wrapper | Single coder loop |
| **Planning** | Multi-agent (PM + Architect + Tech Lead + Sprint Planner) | No dedicated planner | Basic planning |
| **Adaptation** | Three-level control loops (issue + DAG-level) | Limited retries | Limited adaptation |
| **Parallelism** | Per-issue git worktrees, hundreds of agents | Limited parallelism | Limited parallelism |
| **Git Workflow** | Native worktrees + CI integration | GitHub Actions integration | Git operations |
| **Testing** | Multi-stage (coder + QA + reviewer + verifier) | Basic testing | Test generation |
| **Reliability** | Checkpointed execution + resume | Basic checkpointing | Limited recovery |

## Performance Characteristics

### Benchmark Results

**Node.js CLI Todo App Benchmark:**

| Runtime | Cost | Time | Score |
|---------|------|------|-------|
| SWE-AF (Claude haiku) | ~$20 | 30-40 min | **95/100** |
| SWE-AF (MiniMax M2.5) | ~$6 | 43 min | **95/100** |
| Claude Code (sonnet) | ? | ? | **73/100** |
| Codex (o3) | ? | ? | **62/100** |
| Claude Code (haiku) | ? | ? | **59/100** |

**Key Improvements:**
- 253.8x faster than CPython subprocess for Python compilation
- 88.3x-602.3x steady-state execution improvement
- 95/100 quality score with Claude haiku-class models

### Scalability

- **Agent Scale**: Hundreds to thousands of concurrent agent invocations
- **DAG Scale**: Complex dependency graphs with adaptive replanning
- **Multi-Repo Scale**: Coordinated changes across multiple repositories
- **Time Scale**: Builds spanning minutes to hours for complex software

## Deployment

### Local Development

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

af                 # starts AgentField control plane on :8080
python -m swe_af   # registers node id "swe-planner"
```

### Railway Deployment

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/swe-af)

```bash
curl -X POST https://<control-plane>.up.railway.app/api/v1/execute/async/swe-planner.build \
  -H "Content-Type: application/json" \
  -H "X-API-Key: this-is-a-secret" \
  -d '{"input": {"goal": "Add JWT auth", "repo_url": "https://github.com/user/my-repo"}}'
```

### Docker Deployment

```bash
docker compose up -d
```

### Scale Workers

```bash
docker compose up --scale swe-agent=3 -d
```

## API Reference

### Core Endpoints

```bash
# Full build: plan -> execute -> verify
POST /api/v1/execute/async/swe-planner.build
# Body: {"input": {"goal": "...", "repo_url": "...", "config": {...}}}

# Plan only
POST /api/v1/execute/async/swe-planner.plan

# Execute a prebuilt plan  
POST /api/v1/execute/async/swe-planner.execute

# Resume after interruption
POST /api/v1/execute/async/swe-planner.resume_build
```

### Streaming API

The build endpoint supports SSE streaming for real-time progress:

```bash
curl -X POST http://localhost:8080/api/v1/execute/async/swe-planner.build \
  -H "Content-Type: application/json" \
  -d '{"input": {"goal": "Build auth system", "repo_url": "https://github.com/user/my-repo"}}' \
  | jq -r 'select(.event) | .event + ": " + (.data | tostring)'
```

## Monitoring and Debugging

### Log Structure

Each agent logs with structured tags for filtering:

```python
router.note(
    f"Issue {issue_name} completed: {len(files_changed)} files changed",
    tags=["coder", "complete", issue_name]
)
```

### Debug Endpoints

```bash
# Check execution status
curl http://localhost:8080/api/v1/executions/<execution_id>

# Retrieve logs for specific agent
# (via AgentField control plane or application logs)
```

## Extensibility

SWE-AF can be extended through AgentField's plugin system:

1. **New Agent Roles**: Implement new reasoners and register them on the router
2. **Custom Prompts**: Override system prompts in `swe_af/prompts/`
3. **Integration Points**: Customize GitHub PR handling, CI integration
4. **RuntimeAdapters**: Support new AI providers beyond Claude, OpenRouter, Codex

## Future Directions

1. **Model Integration**: Support for more AI providers and models
2. **Continuous Learning**: Cross-build knowledge accumulation
3. **Automated Testing**: Built-in test generation and maintenance
4. **Performance Optimization**: More efficient worktree management
5. **Security Hardening**: Security reviews as part of the pipeline

## Troubleshooting

### Common Issues and Solutions

**CI watcher keeps polling without resolution:**
- Check GitHub token permissions
- Verify branch visibility and workflow triggers
- Ensure `gh` CLI is authenticated

**Worktree creation failures:**
- Ensure git user identity is configured
- Check available disk space
- Verify git operations have proper permissions

**Memory exhaustion during large builds:**
- Tune `max_concurrent_issues` to control parallelism
- Increase `agent_max_turns` for complex tasks
- Monitor AgentField control plane memory usage

**Plan execution failures:**
- Check artifact directory permissions
- Verify model API keys are set correctly
- Review build configuration for role-specific model mapping

## Conclusion

SWE-AF represents a significant step toward autonomous software engineering, moving beyond single-agent wrappers to true factory-scale orchestration. By combining multiple specialized agents with adaptive control loops, git worktree isolation, and comprehensive testing, SWE-AF achieves enterprise-grade reliability and performance that outperforms individual AI coding assistants.

The architecture successfully balances adaptability with speed, offering both a full-featured build pipeline (SWE-planner) and a speed-optimized variant (SWE-fast) for different scenarios. The factory pattern, while complex, enables SWE-AF to handle tasks that would be impossible for single-agent systems, making it suitable for building complex software systems at scale.

## Related

- [[SWE-AF]] -- wiki page for this agent
- [[swe-af-profile]] -- agent profile
- [[agentfield]] -- core AgentField platform
- [[agentfield-architecture]] -- platform architecture
- [[agentfield-deployment]] -- deployment guide

---

*This document is generated from the SWE-AF v1.0.0 source code and represents the current architectural design as of June 2026.*