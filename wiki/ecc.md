---
name: ECC
description: "The agent harness operating system — 67 agents, 281 skills, 94 command shims, 21 hooks, cross-harness support"
tags: [wiki, ECC, claude-code, plugin, code-assistant, python, javascript, typescript, golang, security, skills-platform, harness]
source: sources/ECC/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# ECC (Ergonomic Code Copilot / Everything Claude Code)

ECC is the agent harness operating system — a production-ready Claude Code plugin providing 67 specialized agents, 281 skills, 94 command shims, 21 hook automations, and 122 rules across multiple AI agent harnesses. Works with Claude Code, Cursor, OpenCode, Codex (macOS app + CLI), Gemini CLI, Zed, GitHub Copilot, and others.

- **Version**: 2.1.0 (stable, Jun 2026) | **License**: MIT
- **Stars**: 211.9K+ — live badge served by `api.ecc.tools`, unverifiable in source (mark as external metric)

## Key Features

- **67 specialized agents** — planner, architect, tdd-guide, code-reviewer, security-reviewer, and language-specific reviewers for TypeScript, Python, Go, Rust, Java, Kotlin, C++, Django, Spring Boot, Laravel, Next.js, Swift, and more
- **281 workflow skills** — TDD, security review, verification loops, continuous learning (v2 instinct-based), cost-aware LLM pipelines, autonomous loops, and domain-specific patterns
- **94 legacy command shims** — `commands/` slash commands kept as a compatibility layer
- **21 hook automations** — Session persistence, strategic compaction, quality gates, GateGuard security guards, cost tracking, MCP health monitoring
- **Cross-harness support** — 11 install targets (README.md:253-266): Cursor (15 hook events), OpenCode, Gemini, Zed, Antigravity, Qwen, Hermes, OpenClaw, Kimi, CodeBuddy, JoyCode — plus built-in GitHub Copilot support
- **122 rules across 22 packs** — `common/` plus 21 language packs: TypeScript, Python, Go, Swift, PHP, ArkTS, C++, C#, Dart, F#, Java, Kotlin, Perl, Ruby, Rust, Vue, React, React Native, Angular, Nuxt, Web
- **AgentShield security scanner** — 1282 tests, 98% coverage, 102 static analysis rules; 3-Opus red-team/blue-team/auditor pipeline on `--opus` mode (pipeline lives in the external `agentshield` repo)
- **Desktop dashboard** — Tkinter-based GUI (956 lines; `npm run dashboard` or `python3 ./ecc_dashboard.py`)
- **Selective install architecture** — Manifest-driven install with 7 profiles (minimal, opencode, core, developer, security, research, full) and component targeting via `npx ecc consult`

## What's New in 2.1

- **Plan Canvas** — `/plan` now ends with a browser-based confirm gate: click elements or select text to attach numbered annotations, chat with the agent from a side rail, and Approve/Request-changes map directly onto the CONFIRM gate. Mermaid diagrams, tables, and task lists render natively. Harness- and model-agnostic: a plain CLI + JSON protocol (`ecc-plan-canvas`). (README.md:643-654)
- **Unified Memory Vault / `ecc memory`** — one local, inspectable Markdown format for durable context and handoffs shared across Claude, Codex, Hermes, OpenClaw, Kimi, and other harnesses. Project/team memories live under `.ecc/memory/`, user memories under `~/.ecc/memory/`. The optional `ecc-memory-mcp` stdio server exposes the same bounded save/search/read/doctor surface without enabling itself by default. (README.md:663-665, 815-829)
- **Itô RFQ bridge** — `ecc ito find` invokes the explicitly configured canonical Itô CLI and submits a live authenticated RFQ (it does not reserve capacity). The passive sponsorship link never invokes an RFQ; credential-bearing CLI shims are rejected outright. (README.md:466)
- **Kimi harness** — new `--target kimi` install target via the Moonshot AI partnership; Hermes and OpenClaw also joined the install-target matrix in 2.1
- **Hook runtime controls** — `ECC_HOOK_PROFILE=minimal|standard|strict` and `ECC_DISABLED_HOOKS=...` gate hooks at runtime without editing hook files. (README.md:723, 1348-1351)
- **GateGuard path exemptions** — `GATEGUARD_EXEMPT_GLOBS` plus configurable instinct injection (count + confidence threshold)

## Architecture

| Directory | Contents |
|-----------|----------|
| `agents/` | 67 specialized subagents (Markdown with YAML frontmatter) |
| `skills/` | 281 workflow skills (primary workflow surface) |
| `commands/` | 94 slash commands (legacy compat shim) |
| `hooks/` | 21 trigger-based automations (hooks/hooks.json: PreToolUse 8, Stop 6, PostToolUse 2, SessionStart 2, PostToolUseFailure 1, PreCompact 1, SessionEnd 1) |
| `rules/` | 122 always-follow rules across 22 packs: `common/` + 21 language packs |
| `ecc2/` | Rust control-plane prototype (alpha, 16 `.rs` files, "ECC 2.0 Alpha" README) |
| `workflows/` | Workflow JS (e.g., `orch-review.workflow.js`) |
| `.agents/` | Shared payload directory for Codex: `plugins/marketplace.json` + `skills/*` with per-skill `agents/openai.yaml` |
| `manifests/` | Install manifests (`install-profiles.json`, `install-modules.json`, `install-components.json`) |
| `scripts/` | Cross-platform Node.js utilities |

Root files `SOUL.md`, `RULES.md`, and `agent.yaml` define agent identity and operating rules; `agent.yaml` declares the command/skill surface including the `multi-*` and `orch-*` families.

### 2.0 Control-Pane Substrate
ECC 2.0 graduated the cross-harness control plane: harness-neutral session adapters (`ecc.session.v1` covering Claude Code, Codex, OpenCode, dmux), MCP inventory (`ecc.mcp.v1` — one normalized view of MCP server configs across harnesses with fragmentation/drift detection and secret redaction), the worktree-lifecycle service (deterministic conflict prediction + safe GC for parallel agent worktrees), and the `orch-*` skill family.

### Plugin System
Claude Code v2.1+ auto-loads `hooks/hooks.json` from installed plugins by convention. Do not add a `"hooks"` field to `.claude-plugin/plugin.json` — this causes duplicate execution and cross-platform hook conflicts.

### Cross-Harness DRY Pattern
Cursor hooks adapter transforms Cursor stdin JSON to Claude Code format, allowing `scripts/hooks/*.js` reuse without duplication. The Cursor target ships 15 hook event types (`.cursor/hooks.json`).

## Skills & Tools

- **Skill Creator** — `/skill-create` analyzes git history to generate SKILL.md files; ECC Tools GitHub App adds advanced features
- **AgentShield** — Security auditor (`npx ecc-agentshield scan`) with `--opus --stream` flag for the 3-Opus adversarial pipeline (Attacker/Defender/Auditor)
- **Continuous Learning v2** — Instinct-based pattern extraction (`/instinct-status`, `/instinct-import`, `/evolve`)
- **`orch-*` orchestrator family** — a skill/workflow family (`orch-add-feature`, `orch-build-mvp`, `orch-change-feature`, `orch-fix-defect`, `orch-refine-code`, `orch-review`) with dynamic workflow team orchestration; driven by `workflows/orch-review.workflow.js` and declared in `agent.yaml`. NOT part of `ecc2/` — it lives in `skills/` + `workflows/` + `agent.yaml`
- **`multi-*` commands** — `/multi-plan`, `/multi-execute`, `/multi-backend`, `/multi-frontend`, `/multi-workflow` require the external `ccg-workflow` runtime (`npx ccg-workflow`); they are not included in the base install (README.md:441-448)
- **Worktree lifecycle service** — Git worktrees for parallel agent workflows (`ecc2/src/worktree/mod.rs`, Rust alpha)
- **`npx ecc consult`** — interactive component finder returning matching components, related profiles, and preview/install commands (`scripts/consult.js`)

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
