---
title: ABVX Agent Skills
authors:
  - admin1
date: 2026-06-25
description: ABVX Agent Skills is a small, auditable skillpack for coding agents that helps them write smaller diffs, debug from evidence, compact noisy shell output, and verify work before saying done. Contains skills organized by job functions like token economy, debugging, frontend development, and more.
tags: [ai-llm, cli, git, plugin-sdk]
  - agent-skills
  - coding-tools
  - debugging
  - automation
  - workflows
source: sources/abvx-agent-skills/
visibility: public
license: MIT
category: tools
publicationDate: 2026-06-25
related:
  - abvx-agent-skills/INDEX.md
  - abvx-agent-skills/skills/
---

# ABVX Agent Skills

ABVX Agent Skills is a curated skillpack designed for coding agents that emphasizes auditability, compact execution, and verification. Rather than creating verbose prompt dumps, these are focused `SKILL.md` workflows with clear triggers, attribution, risk notes, and validation gates.

## What This Pack Provides

- **Smaller diffs** - Skills like `minimal-diff-builder` and `overengineering-review` prevent excessive refactoring
- **Evidence-based debugging** - `diagnose` skill runs disciplined debugging loops with ranked hypotheses
- **Token-efficient execution** - Skills like `rtk-assisted-shell` and `shell-output-compaction` reduce context waste
- **Verification gates** - Skills ensure work is checked before completion (e.g., `browser-verification`)

## Skill Organization

Skills are grouped by functional areas:

### Token Economy & Context Control
- `rtk-assisted-shell`, `shell-output-compaction`, `token-efficient-execution`
- `token-frugal-mode`, `lean-context-layout`, `compaction-survival`

### Coding, Debugging & Architecture
- `diagnose`, `minimal-diff-builder`, `overengineering-review`
- `repo-debugging-ledger`, `complexity-optimizer`

### Frontend, UX & Product Surfaces
- `frontend-product-builder`, `design-critique-polish`
- `browser-verification`, `lottie-motion-builder`

### Research, Knowledge & Reusable Methods
- `evidence-ledger-research`, `loopops-protocol`
- `book-to-skill`, `role-skill-pack-design`

## Installation

### Quick Install (Recommended)
```bash
pip install abvx-agent-skills
abvx-skills install
```

### GitHub CLI
```bash
gh skill install markoblogo/abvx-agent-skills minimal-diff-builder --agent codex
```

## Usage Examples

**For saving tokens:**
```text
Use token-economy-skills to compact shell output and optimize context usage.
```

**For debugging:**
```text
Run the diagnose skill to systematically debug this issue from first principles.
```

**For frontend work:**
```text
Use browser-verification to validate real browser rendering before completion.
```

## Philosophy

ABVX prioritizes:
- **Compact context** - Always-loaded context stays small
- **Procedural rules** - Clear, actionable workflows over vague advice
- **Auditability** - Skills are easy to inspect in diffs
- **Verification** - Work is checked before completion

## Key Links

- **Live Catalog:** [lab.abvx.xyz/tools/abvx-agent-skills/](https://lab.abvx.xyz/tools/abvx-agent-skills/)
- **Documentation:** See `docs/` directory for guides and playbooks
- **Skills Directory:** `skills/` contains individual skill implementations
- **Validation:** Use `abvx-skills validate` for static validation

## Contributing

This repository follows the open Agent Skills shape:
- `SKILL.md` - Executable agent instructions
- `SKILL_CARD.md` - Use, attribution, risks, evaluation
- `agents/openai.yaml` - Codex UI metadata

Skills should have narrow triggers, clear behaviors, anti-patterns, and honest verification rather than broad motivational prose.

## Current Status

- Version: Published to PyPI
- Distribution: PyPI, Homebrew tap, conda-forge
- Validation: Passes static security audit and structural validation
- Benchmarks: Available in `benchmarks/` directory

## Related Resources

- [Solo Dev Quickstart](docs/solo-dev-quickstart.md)
- [Team Rollout Playbook](docs/team-rollout-playbook.md)
- [Skill Request Issues](https://github.com/markoblogo/abvx-agent-skills/issues/new?template=skill-request.yml)
- [Skill Autopsy Issues](https://github.com/markoblogo/abvx-agent-skills/issues/new?template=skill-autopsy.yml)

The ABVX Agent Skills pack is designed to make agent work more predictable, auditable, and efficient while maintaining flexibility for different use cases and team sizes.