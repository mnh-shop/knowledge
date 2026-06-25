---
name: swe-af-profile
tags: [swe-af, profile, typescript, swe, engineering-factory, multi-agent]
description: Agent profile for SWE-AF — autonomous software engineering factory agents with multi-agent coordination and self-healing capabilities
---

# SWE-AF Agent Profile

## Overview

SWE-AF agents are autonomous software engineering agents that operate within the SWE-AF (Autonomous Software Engineering Factory) runtime on AgentField. They specialize in collaborative, adaptive software development with coordination across multiple agents, git worktrees, and self-healing capabilities.

## Agent Roles and Responsibilities

### Core SWE-AF Agents

#### 1. **Product Manager (PM)**
- **Primary Function**: Convert high-level goals into structured Product Requirements Documents (PRDs)
- **Key Capabilities**: 
  - Goal scoping and validation
  - Acceptance criteria formulation
  - Risk and assumption tracking
  - Architecture context extraction
- **Output**: PRD with validated description, acceptance criteria, must-have/nice-to-have lists

#### 2. **Architect**
- **Primary Function**: Generate technical architecture based on PRD
- **Key Capabilities**:
  - System design and component mapping
  - File change impact analysis
  - Interface definition
  - Decision documentation with rationale
- **Output**: Architecture document with components, interfaces, decisions

#### 3. **Tech Lead**
- **Primary Function**: Review architecture against PRD and identify issues
- **Key Capabilities**:
  - Architecture review and validation
  - Scope gap identification
  - Complexity assessment
  - Revision coordination with Architect
- **Output**: Review result with approval status and feedback

#### 4. **Sprint Planner**
- **Primary Function**: Decompose work into dependency-sorted issues
- **Key Capabilities**:
  - Topological sorting of issues
  - File conflict detection
  - Parallel execution level assignment
  - Issue guidance generation for downstream agents
- **Output**: List of PlannedIssue objects with dependencies and guidance

#### 5. **Issue Writer**
- **Primary Function**: Create detailed issue specifications for coder agents
- **Key Capabilities**:
  - Rich issue description generation
  - Acceptance criteria mapping from PRD
  - Testing strategy formulation
  - File modification/change tracking
- **Output**: Issue-*.md files for each planned issue

#### 6. **Coder**
- **Primary Function**: Implement code based on issue specifications
- **Key Capabilities**:
  - Code generation in isolated worktrees
  - Test writing and augmentation
  - Git operations (commit, push, branch management)
  - Code review preparation
- **Output**: CoderResult with files_changed, test results, summary

#### 7. **QA Tester**
- **Primary Function**: Test coder's implementation and augment test suite
- **Key Capabilities**:
  - Test execution and results analysis
  - Coverage gap identification
  - Test writing for uncovered scenarios
  - Failure diagnosis and reporting
- **Output**: QAResult with test outcomes and coverage information

#### 8. **Code Reviewer**
- **Primary Function**: Quality and security review of implemented code
- **Key Capabilities**:
  - Independent test execution
  - Code quality assessment
  - Security vulnerability detection
  - Requirements alignment verification
- **Output**: CodeReviewResult with approval status and debt items

#### 9. **QA Synthesizer**
- **Primary Function**: Merge QA and review feedback into final decision
- **Key Capabilities**:
  - Synthesize feedback from QA and reviewer
  - Make Fix/Approve/Block decisions
  - Identify stuck scenarios
  - Orchestrate next actions
- **Output**: QASynthesisResult with action decision

#### 10. **Issue Advisor**
- **Primary Function**: Analyze coding failures and decide adaptation strategies
- **Key Capabilities**:
  - Failure root cause analysis
  - Adaptation strategy selection
  - Work splitting recommendations
  - Debt management advice
- **Output**: IssueAdvisorDecision with action and modifications

#### 11. **Replanner**
- **Primary Function**: Restructure remaining DAG when failures escalate
- **Key Capabilities**:
  - DAG-level decision making
  - New issue generation
  - Scope reduction when necessary
  - Emergency abort when recovery impossible
- **Output**: ReplanDecision with restructuring plan

#### 12. **Merger**
- **Primary Function**: Integrate completed branches into main codebase
- **Key Capabilities**:
  - Git branch merging with conflict resolution
  - Integration testing coordination
  - Workflow state management
  - Cross-feature interaction validation
- **Output**: MergeResult with merged branches and test needs

#### 13. **Integration Tester**
- **Primary Function**: Verify integration of merged features
- **Key Capabilities**:
  - Cross-feature testing
  - Integration test writing
  - Conflict resolution validation
  - End-to-end scenario testing
- **Output**: IntegrationTestResult with test outcomes

#### 14. **Verifier**
- **Primary Function**: Final acceptance criteria verification against PRD
- **Key Capabilities**:
  - PRD alignment checking
  - Acceptance criteria validation
  - Suggested fixes generation
  - Success/failure determination
- **Output**: VerificationResult with pass/fail status

#### 15. **Git Initialization Agent**
- **Primary Function**: Set up git worktrees for parallel execution
- **Key Capabilities**:
  - Repository initialization
  - Branch structure creation
  - Worktrees directory setup
  - .gitignore optimization
- **Output**: GitInitResult with branch configuration

#### 16. **Workspace Setup Agent**
- **Primary Function**: Create individual worktrees for each issue
- **Key Capabilities**:
  - Parallel worktree creation
  - Branch isolation management
  - Resource allocation coordination
- **Output**: WorkspaceSetupResult with created worktrees

#### 17. **GitHub PR Agent**
- **Primary Function**: Create and manage GitHub pull requests
- **Key Capabilities**:
  - Git push operations
  - PR creation and body drafting
  - CI monitoring and fix coordination
  - Status update management
- **Output**: GitHubPRResult with PR URL and status

#### 18. **CI Watcher Agent**
- **Primary Function**: Monitor CI checks on PRs
- **Key Capabilities**:
  - Polling and status tracking
  - Conclusive verdict determination
  - Head SHA anchoring for stale state avoidance
- **Output**: CIWatchResult with final status

#### 19. **CI Fixer Agent**
- **Primary Function**: Fix failing CI checks and repush
- **Key Capabilities**:
  - Failure diagnosis
  - Legitimate fix generation
  - Anti-workaround enforcement
  - Commit and push coordination
- **Output**: CIFixResult with fix outcome

#### 20. **PR Resolver Agent**
- **Primary Function**: Resolve open PRs (merges + fixes + comments)
- **Key Capabilities**:
  - In-progress merge completion
  - CI failure resolution
  - Review comment addressing
  - Coordinated workflow management
- **Output**: PRResolveResult with all resolutions

#### 21. **Environment Scout Agent**
- **Primary Function**: Negotiate scoped credentials with user
- **Key Capabilities**:
  - Service discovery and credential requirement identification
  - HAX form generation and processing
  - Scoped/temporary token negotiation
  - Secure credential storage
- **Output**: ScoutResult with negotiated credentials (excluded from logs)

#### 22. **Retry Advisor Agent**
- **Primary Function**: Advise on whether to retry after coding failures
- **Key Capabilities**:
  - Failure diagnosis and context analysis
  - Retry strategy recommendations
  - Confidence scoring for retry decisions
- **Output**: RetryAdvice with should_retry decision

#### 23. **Fix Generator Agent**
- **Primary Function**: Generate targeted fix issues from verification failures
- **Key Capabilities**:
  - Failed criteria analysis
  - Multi-repo target_repo assignment
  - Fix issue generation with context
- **Output**: FixGeneratorOutput with fix issues and debt items

#### 24. **Repo Finalizer Agent**
- **Primary Function**: Clean up repository after verification
- **Key Capabilities**:
  - Artifact removal
  - .gitignore fortification
  - Workspace cleanup
- **Output**: RepoFinalizeResult with cleanup summary

#### 25. **Resolution Agent**
- **Primary Function**: Final resolve agent for complex PR fixes
- **Key Capabilities**:
  - In-progress merge completion
  - CI failure and review comment addressing
  - Coordinated fix-and-repush workflow
  - Thread reply and thread resolution
- **Output**: PRResolveResult with comprehensive resolutions

## Agent Configuration

### Model Assignment
Each agent role can be assigned different models based on requirements:

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
    "verifier": "haiku",
    "git": "haiku",
    "merger": "haiku"
  }
}
```

### Permission Modes
- **auto**: Automatic permission handling with user prompts
- **bypass**: Skip permission checks for trusted environments
- **review**: Require explicit approval for file modifications
- **none**: No permissions requested (use with caution)

### Runtime Options
- **claude_code**: Anthropic Claude models via Claude Code CLI
- **open_code**: OpenRouter/OpenAI/Google/Anthropic via OpenCode runtime
- **codex**: OpenAI Codex CLI for production environments

## Agent Collaboration Patterns

### 1. **Pipeline Orchestration**
```
Goal → PM → Architect → Tech Lead → Sprint Planner → Issues → Coders → QA/Reviewers → Merger/Verifier → PR
```

### 2. **Adaptive Response Pattern**
```
Coder Failure → Issue Advisor Analysis → Retry Modified ACs
                ↘ Split Work
                ↘ Retry Approach  
                ↘ Accept with Debt
                ↘ Escalate to Replanner
```

### 3. **Error Recovery Pattern**
```
Inner Loop (Coder Retry)
  ↓
Middle Loop (Issue Advisor)
  ↓
Outer Loop (Replanner)
  ↓
DAG Restructuring or Abort
```

## Agent Capabilities Matrix

| Capability | Implementation | Dependencies |
|------------|----------------|--------------|
| **Code Generation** | Coder, Issue Writer | Issue specs, Architecture |
| **Testing** | QA, Code Reviewer, Verifier | Coder output, PRD |
| **Git Operations** | Git Init, Workspace Setup, Merger | Worktrees, CI integration |
| **Adaptation** | Issue Advisor, Replanner | Failure context, DAG state |
| **Coordination** | Router, Note function | Shared state, Communication |
| **Verification** | Verifier, Integration Tester | Completed issues, PRD |

## Agent Communication Protocols

### 1. **Router-based Calls**
All agent invocations go through the AgentField router:

```python
result = await router.call(
    "swe-planner.run_coder",
    issue=issue_spec,
    worktree_path=worktree,
    model=config.coder_model
)
```

### 2. **Structured Logging**
Each agent logs with tags for filtering and monitoring:

```python
router.note(
    f"Coder starting: {issue_name} (iteration {iteration})",
    tags=["coder", "start", issue_name]
)
```

### 3. **Checkpoint Protocol**
Agents participate in checkpoint/save operations:

```python
def _save_checkpoint(dag_state, note_fn):
    path = _checkpoint_path(dag_state)
    if not path:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(dag_state.model_dump(), f, indent=2, default=str)
    if note_fn:
        note_fn(f"Checkpoint saved: level={dag_state.current_level}", tags=["execution", "checkpoint"])
```

## Agent Profile Configuration

### Fast Mode vs Planning Mode

**Fast Mode (`swe_af/fast/`)**:
- Single LLM call for planning
- Sequential execution (no DAG)
- No replanning
- Optimized for speed
- Roles: Git Init, Coder, QA, Verifier, Merger, PR

**Planning Mode (`swe_af/reasoners/`)**:
- Full multi-agent pipeline
- DAG-based execution
- Adaptive replanning
- Optimized for adaptability
- Roles: PM, Architect, Tech Lead, Sprint Planner, all execution agents

### Environment Variables

```bash
# AgentField connection
AGENTFIELD_SERVER=http://localhost:8080
AGENTFIELD_API_KEY=your-api-key

# Model configuration  
SWE_DEFAULT_RUNTIME=claude_code
SWE_DEFAULT_MODEL=sonnet

# Git credentials
GH_TOKEN=github-personal-access-token

# HAX credentials (for human-in-the-loop)
HAX_API_KEY=hax-api-key
HAX_SDK_URL=http://localhost:3000/api/v1

# Development flags
SWE_AF_ENABLE_LEARNING=true
SWE_AF_ENABLE_DEBUG_LOGGING=true
```

## Agent Performance Characteristics

### 1. **Speed vs Adaptability Trade-offs**
- **Fast mode**: ~43 seconds, optimized for simple changes
- **Planning mode**: ~30-40 minutes, handles complex scenarios
- **Memory usage**: Varies by build size and agent count

### 2. **Scaling Properties**
- **Parallel execution**: Limited by `max_concurrent_issues` (default: 3)
- **Memory footprint**: Each agent maintains its own context
- **Network overhead**: AgentField control plane coordination

### 3. **Failure Recovery**
- **Inner loop**: Up to 5 coding iterations per issue
- **Middle loop**: Up to 2 advisor invocations per issue  
- **Outer loop**: Up to 2 replanning cycles for entire build
- **Checkpoint-based**: Resumes from last successful checkpoint

## Integration with External Systems

### 1. **GitHub Integration**
- PR creation and management
- CI monitoring and notification
- Status update posting
- Review comment handling

### 2. **HAX Integration**
- Human approval workflows
- Credential negotiation
- Plan review gates
- Change request processing

### 3. **AgentField Mesh**
- Fleet-wide coordination
- Load balancing across nodes
- Service discovery
- Message routing

## Testing and Validation

### 1. **Agent Testing**
Each agent has comprehensive test coverage:
- Unit tests for individual reasoners
- Integration tests for agent pipelines
- End-to-end tests for full builds
- Performance benchmarking

### 2. **Quality Gates**
- **Functional**: All acceptance criteria met
- **Structure**: Proper modular organization
- **Hygiene**: Clean status, proper .gitignore
- **Git**: Commit discipline and message quality
- **Quality**: Error handling, metadata, README

### 3. **Benchmarks**
- **95/100** with Claude haiku-class models (~$20)
- **95/100** with MiniMax M2.5 via OpenRouter (~$6)
- **253.8x** speedup over CPython for Python compilation
- **88.3x-602.3x** steady-state execution improvement

## Security Considerations

### 1. **Credential Management**
- Environment-scoped credentials via HAX
- Process-local memory storage
- Automatic cleanup after build completion
- No persistence in logs or artifacts

### 2. **Permission Boundaries**
- Role-based tool access
- Workspace isolation via git worktrees
- Review gates for production changes
- Anti-workaround enforcement in CI fixer

### 3. **Audit Trail**
- Structured logging with agent roles and actions
- Checkpoint-based state preservation
- DAG execution tracking
- Cross-agent dependency monitoring

## Future Extensibility

### 1. **New Agent Types**
- Specialized domain agents (security, performance, compliance)
- Custom review agents (architecture, design, UX)
- Maintenance agents (refactoring, optimization)

### 2. **Enhanced Coordination**
- Cross-build knowledge sharing
- Fleet-scale orchestration patterns
- Dynamic agent spawning and pooling
- Serverless agent execution

### 3. **Advanced Features**
- Continuous integration with CI/CD pipelines
- Automated documentation generation
- Requirements validation and compliance checking
- Performance profiling and optimization guidance

## Conclusion

SWE-AF agents represent a sophisticated, factory-scale autonomous software engineering system. Each agent specializes in a specific aspect of the development pipeline while maintaining loose coupling and strong coordination through AgentField's mesh architecture. The adaptive control loops, git worktree isolation, and comprehensive error recovery mechanisms enable SWE-AF to handle complex software engineering tasks with enterprise-grade reliability.

The agent profile encompasses not just individual agent capabilities, but the entire ecosystem of specialized agents that work together to transform high-level goals into production-ready code. This factory pattern achieves scalability and reliability that would be impossible with single-agent systems, making SWE-AF suitable for building complex software systems at scale.

## Related

- [[SWE-AF]] -- wiki page for this agent
- [[swe-af-architecture]] -- architecture documentation
- [[agentfield]] -- core AgentField platform
- [[agentfield-profile]] -- AgentField platform profile
- [[sec-af-profile]] -- sibling SEC-AF profile

---

*This agent profile reflects the SWE-AF v1.0.0 architecture and should be updated with new agent types and capabilities as the system evolves.*