---
name: ECC
description: "The agent harness operating system — 67 agents, 271 skills, cross-harness support"
tags: [wiki, ECC, claude-code, plugin, code-assistant, python, javascript, typescript, golang, security, skills-platform, harness]
source: sources/ECC/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# ECC (Ergonomic Code Copilot / Everything Claude Code)

ECC is the agent harness operating system — a production-ready Claude Code plugin providing 67 specialized agents, 271 skills, 92 commands, and 20+ hook automations across multiple AI agent harnesses. Works with Claude Code, Cursor, OpenCode, Codex (macOS app + CLI), Gemini CLI, Zed, GitHub Copilot, and others.

- **Version**: 2.0.0 (stable, Jun 2026) | **License**: MIT
- **Stars**: 211.9K+ | **Website**: [ecc.tools](https://ecc.tools)

## Key Features

- **67 specialized agents** — planner, architect, tdd-guide, code-reviewer, security-reviewer, and language-specific reviewers for TypeScript, Python, Go, Rust, Java, Kotlin, C++, Django, Spring Boot, Laravel, Next.js, Swift, and more
- **271 workflow skills** — TDD, security review, verification loops, continuous learning (v2 instinct-based), cost-aware LLM pipelines, autonomous loops, and domain-specific patterns
- **20+ hook automations** — Session persistence, strategic compaction, quality gates, GateGuard security guards, cost tracking, MCP health monitoring
- **Cross-harness support** — Native plugins/configs for Claude Code, Cursor (15 hook events), OpenCode, Codex, Gemini CLI, Zed, JoyCode, Qwen CLI
- **250+ multi-language rules** — `common/` plus language packs for TypeScript, Python, Go, Swift, PHP, ArkTS, C++, Rust, Kotlin, Java, Perl
- **AgentShield security scanner** — 1282 tests, 98% coverage, 102 static analysis rules; 3-Opus red-team/blue-team/auditor pipeline on `--opus` mode
- **Desktop dashboard** — Tkinter-based GUI (`npm run dashboard` or `python3 ./ecc_dashboard.py`)
- **Selective install architecture** — Manifest-driven install with profiles (minimal, core, developer, security, research, full) and component targeting via `npx ecc consult`

## Architecture

| Directory | Contents |
|-----------|----------|
| `agents/` | 67 specialized subagents (Markdown with YAML frontmatter) |
| `skills/` | 271 workflow skills (primary workflow surface) |
| `commands/` | 92 slash commands (legacy compat shim) |
| `hooks/` | 20+ trigger-based automations (PreToolUse, PostToolUse, Stop, SessionStart) |
| `rules/` | Always-follow guidelines: `common/` + language-specific packs |
| `ecc2/` | Rust control-plane prototype (alpha) with `orch-*` orchestrator family |
| `scripts/` | Cross-platform Node.js utilities |

### Plugin System
Claude Code v2.1+ auto-loads `hooks/hooks.json` from installed plugins by convention. Do not add a `"hooks"` field to `.claude-plugin/plugin.json` — this causes duplicate detection errors.

### Cross-Harness DRY Pattern
Cursor hooks adapter transforms Cursor stdin JSON to Claude Code format, allowing `scripts/hooks/*.js` reuse without duplication.

## Skills & Tools

- **Skill Creator** — `/skill-create` analyzes git history to generate SKILL.md files; ECC Tools GitHub App adds advanced features
- **AgentShield** — Security auditor (`npx ecc-agentshield scan`) with `--opus` flag for 3-Opus adversarial pipeline
- **Continuous Learning v2** — Instinct-based pattern extraction (`/instinct-status`, `/instinct-import`, `/evolve`)
- **Worktree lifecycle service** — Git worktrees for parallel agent workflows (`ecc2/` alpha)

## Quick Start

```bash
# Install as Claude Code plugin (recommended)
/plugin marketplace add https://github.com/affaan-m/ECC
/plugin install ecc@ecc

# Copy rules manually
mkdir -p ~/.claude/rules/ecc
cp -R rules/common ~/.claude/rules/ecc/
cp -R rules/typescript ~/.claude/rules/ecc/

# Launch dashboard
npm run dashboard

# Security scan
npx ecc-agentshield scan
```

## Related

- [[hermes-agent]] — Operator control-plane that integrates with ECC
- [[agentfield]] — Shared agent catalog and governance
- [[openclaw]] — Companion runtime ecosystem
- [[goclaw]] — Go agent orchestration platform
- [[clawpier]] — Pier protocol for agent communication

## Links

- GitHub: https://github.com/affaan-m/ECC
- npm: https://www.npmjs.com/package/ecc-universal
- GitHub App: https://github.com/apps/ecc-tools
- AgentShield: https://github.com/affaan-m/agentshield
- Source: `sources/ECC/`