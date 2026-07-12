---
name: software-engineering-skills
description: "235+ software engineering skills for coding, debugging, architecture, testing, and domain-specific healthcare patterns across all agentic harnesses"
tags: [software-engineering, swe, skills, mcp]
metadata:
  type: catalog
---

# Software Engineering Skills

Skills for code generation, debugging, architecture, testing, and development workflows.

**Total skills:** 235+ across 25+ repos

---

## Skill Sources

| Repo | Count | Harness Support |
|------|-------|-----------------|
| `sources/hermes-agent/skills/` | 72 skills in 18 categories | hermes-agent |
| `sources/abvx-agent-skills/skills/` | 55 skills | All skills-harnesses |
| `sources/ECC/skills/` | 285+ skills + hooks | ECC, hermes-agent |
| `sources/hermes-profiles/skills/` | 40 skills | hermes-agent |
| `sources/openclaw/skills/` | 10+ core skills | openclaw |
| `sources/SWE-AF/skills/` | 5+ skills | agentfield |
| `sources/goclaw/skills/` | 5 skills | goclaw |
| `sources/pydantic-ai-skills/examples/skills/` | 5 skills | pydantic-ai |

---

## Skill Categories

### Debugging & Diagnosis

| Skill | Source | Harness | Description |
|-------|--------|---------|-------------|
| diagnose | abvx-agent-skills | All | Systematic debugging with hypothesis ledger |
| repo-debugging-ledger | abvx-agent-skills | All | Debug repos with checked locations discipline |
| recovery-loop-3strike | abvx-agent-skills | All | Bounded recovery from failures |
| repo-issue-triage | abvx-agent-skills | All | Triage bugs/enhancements |
| debugger | hermes-profiles | hermes-agent | Root cause analysis framework |
| systematic-debugging | hermes-profiles | hermes-agent | Debugging methodologies |
| graph-guided-code-reading | abvx-agent-skills | All | Navigate codebases using dependency graph |
| python-debugpy | hermes-agent | hermes-agent | Python debugpy integration for remote debugging |
| node-inspect-debugger | hermes-agent | hermes-agent | Node.js inspect debugger integration |

### Execution & Verification

| Skill | Source | Harness | Description |
|-------|--------|---------|-------------|
| test-driven-execution | abvx-agent-skills | All | Red-green-refactor for agents |
| delivery-preflight-gate | abvx-agent-skills | All | Preflight before implementation |
| delivery-baseline-audit | abvx-agent-skills | All | Verify deliverables exist |
| phase-spec-execution | abvx-agent-skills | All | Explicit phases with criteria |
| grilling | abvx-agent-skills | All | Stress-test plans/designs |
| rapid-grilling | abvx-agent-skills | All | Lightweight product validation |
| browser-verification | abvx-agent-skills | All | Browser-based testing and verification |
| eval-harness | ECC | ECC | Evaluation harness for testing agent workflows |
| healthcare-eval-harness | ECC | ECC | Healthcare-specific agent evaluation |
| spike | hermes-agent | hermes-agent | Time-boxed technical spikes for research and validation |

### Code Quality

| Skill | Source | Harness | Description |
|-------|--------|---------|-------------|
| architecture-deepening-review | abvx-agent-skills | All | Find deepening opportunities |
| complexity-optimizer | abvx-agent-skills | All | Performance hotspots review |
| overengineering-review | abvx-agent-skills | All | Kill needless complexity |
| minimal-diff-builder | abvx-agent-skills | All | Smallest correct diff |
| system-zoom-out | abvx-agent-skills | All | Higher-level abstraction view |
| code-review | ECC | ECC, hermes | Code and architecture review |
| agent-architecture-audit | ECC | ECC | Architecture audit for agent systems |
| simplify-code | hermes-agent | hermes-agent | Code simplification and complexity reduction |
| requesting-code-review | hermes-agent | hermes-agent | Structured code review requests and feedback |

### Agent Management

| Skill | Source | Harness | Description |
|-------|--------|---------|-------------|
| agent-self-evaluation | ECC | ECC | Self-evaluation and improvement for agents |
| skill-comply | ECC | ECC | Skill compliance verification |
| skill-stocktake | ECC | ECC | Inventory and audit installed skills |
| skill-scout | ECC | ECC | Discover and recommend relevant skills |

### Planning & Requirements

| Skill | Source | Harness | Description |
|-------|--------|---------|-------------|
| brief-first-execution | abvx-agent-skills | All | Create brief before work |
| dynamic-workflow-packets | abvx-agent-skills | All | Dynamic workflow planning |
| loopops-protocol | abvx-agent-skills | All | Loop design patterns |
| plan-to-issues | abvx-agent-skills | All | Break spec into vertical slices |
| spec-to-prd | abvx-agent-skills | All | Turn decisions into PRD |
| spec-driven-development | hermes-profiles | hermes-agent | Formal spec pipeline |
| implementation-planner | hermes-profiles | hermes-agent | WBS and critical path |
| phase-spec-execution | hermes-agent | hermes-agent | Multi-phase task execution |
| html-brief-artifact | abvx-agent-skills | All | HTML brief artifact generation |
| plan | hermes-agent | hermes-agent | Multi-step planning and task decomposition |
| hermes-agent-skill-authoring | hermes-agent | hermes-agent | Authoring skills for Hermes Agent |

### Document & Data Processing

| Skill | Source | Harness | Description |
|-------|--------|---------|-------------|
| docx-processing | goclaw | goclaw | Word document handling |
| pdf-processing | goclaw | goclaw | PDF manipulation |
| pptx-processing | goclaw | goclaw | PowerPoint processing |
| xlsx-processing | goclaw | goclaw | Excel spreadsheet handling |
| html-diagram-artifact | abvx-agent-skills | All | HTML diagram generation and rendering |
| spreadsheet-workbook-forensics | abvx-agent-skills | All | Spreadsheet data analysis and forensics |

### GitHub & Code Management
| Skill | Source | Harness | Description |
|-------|--------|---------|-------------|
| codebase-inspection | hermes-agent | hermes-agent | Deep codebase inspection and analysis |
| github-auth | hermes-agent | hermes-agent | GitHub authentication workflows |
| github-code-review | hermes-agent | hermes-agent | GitHub-native code review workflows |
| github-issues | hermes-agent | hermes-agent | GitHub issue management and triage |
| github-pr-workflow | hermes-agent | hermes-agent | Pull request workflow automation |
| github-repo-management | hermes-agent | hermes-agent | GitHub repository administration |

### Developer Tools

| Skill | Source | Harness | Description |
|-------|--------|---------|-------------|
| bun-runtime | ECC | ECC | Bun runtime integration and workflows |
| nanoclaw-repl | ECC | ECC | NanoClaw REPL for skill development |

### Domain Patterns

| Skill | Source | Harness | Description |
|-------|--------|---------|-------------|
| healthcare-cdss-patterns | ECC | ECC | Clinical decision support system patterns |
| healthcare-emr-patterns | ECC | ECC | Electronic medical record pattern integration |

### Data Science
| Skill | Source | Harness | Description |
|-------|--------|---------|-------------|
| jupyter-live-kernel | hermes-agent | hermes-agent | Jupyter live kernel integration for data analysis |

---

## Harness Compatibility

| Harness | Native Format | Notes |
|---------|---------------|-------|
| **Hermes Agent** | SKILL.md with frontmatter, skills/ dirs | Progressive disclosure, 72 native skills |
| **OpenClaw** | skills/ directories | 10+ core skills + extensions |
| **GoClaw** | skills/ directories | Focus on document processing |
| **AgentField** | skill/ subdirectories | Harness orchestration |
| **ECC** | .claude/skills/ + hooks | Aggressive hook integration |
| **n8n** | MCP tools via n8n-mcp | Workflow automation |
| **opencode** | skills/ directories | Native skills |
| **pydantic-ai** | tool-calling | Wrap other skills |

---

## Related

- [[skills-catalog]] — Main catalog
- [[SWE-AF]] — SWE agent (AgentField-based)
- [[sec-af]] — Security auditor
- [[hermes-agent]] — Skill-native agent platform
- [[openclaw]] — Extension skills model