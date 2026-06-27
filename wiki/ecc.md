---
name: ecc
description: "Claude Code plugin system — 67 agents, 271 skills, 92 commands, cross-harness support"
tags: [wiki, claude-code, plugin, code-assistant, python, javascript]
source: sources/ECC/
---

# ECC (Ergonomic Code Copilot / Everything Claude Code)

ECC is a harness-native operator system for agentic work. It is a production-ready Claude Code plugin that provides 67 specialized agents, 271 skills, 92 commands, and 20+ hook automations across multiple AI agent harnesses. Works across Claude Code, Cursor, OpenCode, Codex (macOS app + CLI), Gemini CLI, Zed, GitHub Copilot, Antigravity, JoyCode, Qwen CLI, and other AI agent harnesses.

- **Version**: 2.0.0 (stable, Jun 2026)
- **License**: MIT
- **Stars**: 211.9K+ | **Forks**: 32.5K+ | **Contributors**: 230+
- **Website**: [ecc.tools](https://ecc.tools)
- **Discord**: [Join](https://discord.gg/36yGMHGFbR)

## Key Features

- **67 specialized agents** — planner, architect, tdd-guide, code-reviewer, security-reviewer, and language-specific reviewers for TypeScript, Python, Go, Rust, Java, Kotlin, C++, C, F#, PyTorch, MLE, and more
- **271 workflow skills** — Primary workflow surface covering TDD, security review, verification loops, continuous learning (v2 instinct-based), cost-aware LLM pipelines, skill stocktake, autonomous loops, and domain-specific patterns (Django, Spring Boot, Laravel, Next.js, Swift, Quarkus, Perl, NestJS, etc.)
- **92 legacy command shims** — Maintained slash-entry compat surface (e.g. `/plan`, `/code-review`, `/build-fix`, `/security-scan`, `/multi-plan`) while migration to skills-first is underway
- **20+ hook automations** — Session persistence, strategic compaction, quality gates, GateGuard security guards, cost tracking, MCP health monitoring, context monitor
- **Cross-harness support** — Native plugins/configs for Claude Code, Cursor (with **15 hook events** — more than Claude Code's 8), OpenCode, Codex, Gemini CLI, Zed, JoyCode, Qwen CLI; instruction layer for GitHub Copilot
- **250+ multi-language rules** — Always-follow guidelines in `common/` plus language-specific packs for TypeScript, Python, Go, Swift, PHP, ArkTS, C++, Rust, Kotlin, Java, Perl
- **AgentShield security scanner** — Built-in security auditing with 1282 tests, 98% coverage, 102 static analysis rules; 3-Opus red-team/blue-team/auditor pipeline on `--opus` mode
- **Desktop dashboard** — Tkinter-based GUI (`npm run dashboard` or `python3 ./ecc_dashboard.py`), dark/light theme, search and filter across agents, skills, commands, rules, settings
- **Continuous Learning v2** — Instinct-based pattern extraction with confidence scoring, import/export, evolution into skills
- **Selective install architecture** — Manifest-driven install with profiles (minimal, core, developer, security, research, full) and component targeting via `npx ecc consult`
- **ECC Pro** — Hosted GitHub App for private repos, $19/seat/mo with free tier
- **ECC v2.0.0 Rust control-plane** — Alpha prototype (`ecc2/`) with commands: dashboard, start, sessions, status, stop, resume, daemon

## Architecture

ECC follows a plugin-first architecture with these core directories:

| Directory | Contents |
|-----------|----------|
| `agents/` | 67 specialized subagents (Markdown with YAML frontmatter: name, description, tools, model) |
| `skills/` | 271 workflow skills (canonical workflow surface; sections: When to Use, How It Works, Examples) |
| `commands/` | 92 slash commands (maintained compat shim; new workflow lands in skills/ first) |
| `hooks/` | 20+ trigger-based automations (PreToolUse, PostToolUse, Stop, SessionStart, PreCompact) |
| `rules/` | Always-follow guidelines: `common/` + language-specific packs (TypeScript, Python, Go, Swift, PHP, ArkTS, C++, Rust, Kotlin, Java, Perl) |
| `scripts/` | Cross-platform Node.js utilities (lib/ utils + package-manager, hook implementations, setup-package-manager) |
| `mcp-configs/` | 14 MCP server configurations (GitHub, Supabase, Vercel, Railway, etc.) |
| `contexts/` | Dynamic system prompt injection contexts (dev, review, research) |
| `tests/` | Test suite mirroring scripts/ structure |
| `ecc2/` | Rust control-plane prototype (alpha) with worktree lifecycle service, session manager, `orch-*` orchestrator family |
| `.claude-plugin/` | Plugin manifest (`plugin.json`) and marketplace catalog (`marketplace.json`) |
| `legacy-command-shims/` | Opt-in archive for retired shims (`/tdd`, `/eval`, `/verify`, `/e2e`, `/orchestrate`) |
| `examples/` | Real-world CLAUDE.md examples (SaaS Next.js/Supabase/Stripe, Go microservice, Django REST, Laravel, Rust Axum) |

### Plugin System

Claude Code v2.1+ auto-loads `hooks/hooks.json` from installed plugins by convention. Do **not** add a `"hooks"` field to `.claude-plugin/plugin.json` — this causes a duplicate detection error.

### Cross-Harness DRY Pattern

Cursor has more hook events (15) than Claude Code (8). The `.cursor/hooks/adapter.js` module transforms Cursor's stdin JSON to Claude Code's format, allowing `scripts/hooks/*.js` to be reused without duplication across all supported harnesses.

### Selective Install

The manifest system (`manifests/`) defines modules with dependencies, conflicts, and descriptions. The install pipeline uses `install-plan.js` + `install-apply.js` for targeted component installation with incremental state tracking.

### MCP Connector Policy

ECC ships exactly one default connector (`chrome-devtools`). Everything else is a skill wrapping a CLI/REST API or an opt-in catalog entry. Filter ECC-generated MCP configs during install/sync with `ECC_DISABLED_MCPS`.

## Quick Start

```bash
# Install as Claude Code plugin (recommended)
/plugin marketplace add https://github.com/affaan-m/ECC
/plugin install ecc@ecc

# Copy rules manually (plugin path cannot distribute rules automatically)
mkdir -p ~/.claude/rules/ecc
cp -R rules/common ~/.claude/rules/ecc/
cp -R rules/typescript ~/.claude/rules/ecc/  # pick your stack

# Use the consultant for targeted installs
npx ecc consult "security reviews" --target claude

# Or minimal no-hooks install
./install.sh --profile minimal --target claude

# Launch the desktop dashboard
npm run dashboard

# Run security scan
npx ecc-agentshield scan

# Check installed state
node scripts/ecc.js list-installed
node scripts/ecc.js doctor

# Reset / uninstall
node scripts/uninstall.js --dry-run
node scripts/uninstall.js
```

Do **not** stack install methods: `/plugin install` first, then `./install.sh --profile full` afterward causes duplicate skills and runtime behavior. Use exactly one path.

### Reset / Uninstall

If ECC feels duplicated or broken, do not reinstall on top — remove ECC-managed files:

```bash
node scripts/ecc.js list-installed
node scripts/ecc.js doctor
node scripts/ecc.js uninstall --dry-run
node scripts/ecc.js uninstall
```

## Harness Support

ECC provides adapter configs for all major AI coding tools:

| Feature | Claude Code | Cursor | Codex CLI | OpenCode | GitHub Copilot | Zed | Antigravity |
|---------|-------------|--------|-----------|----------|----------------|-----|-------------|
| Agents | 67 | Shared (AGENTS.md) | Shared (AGENTS.md) | 12 | N/A | Shared | Shared |
| Commands | 92 | Shared | Instruction | 35 | 5 prompts | Shared | Shared |
| Skills | 271 | Shared | 32 (native) | 37 | Via instructions | Shared | Shared |
| Hooks | 8 types | 15 types | None yet | 11 types | None | N/A | N/A |
| Rules | 34+ | 34 (YAML frontmatter) | Instruction | 13 instr. | 1 always-on | Flattened | Flattened |

## Ecosystem Tools

- **Skill Creator** — `/skill-create` analyzes git history locally to generate SKILL.md files; the ECC Tools GitHub App provides advanced features (10K+ commits, auto-PRs, team sharing)
- **AgentShield** — Security auditor with 1282 tests, 98% coverage; scans CLAUDE.md, settings.json, MCP configs, hooks, agent definitions; 3-Opus red-team pipeline on `--opus` mode; integrates as `/security-scan`
- **Continuous Learning v2** — Instinct-based learning (`/instinct-status`, `/instinct-import`, `/instinct-export`, `/evolve`) with confidence scoring, 30-day TTL, and global/project instinct scoping

## Token Optimization

Recommended settings for `~/.claude/settings.json`:

```json
{
  "model": "sonnet",
  "env": {
    "MAX_THINKING_TOKENS": "10000",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50",
    "CLAUDE_CODE_SUBAGENT_MODEL": "haiku"
  }
}
```

Keep under 10 MCPs enabled and under 80 tools active. Each MCP tool description consumes tokens from the 200K window.

## Related

- [[hermes-agent]] — Operator control-plane that integrates with ECC Hermes setup
- [[hermes-agent-docker]] — Containerized Hermes deployment
- **Claude Code** — The harness ECC primarily targets
- [[goclaw]] — Go agent orchestration platform, complementary to ECC
- [[clawpier]] — Pier protocol for agent communication
- **AgentShield** — Security auditor for AI agent configurations (part of ECC repo)

## Links

- Website: https://ecc.tools
- GitHub: https://github.com/affaan-m/ECC
- npm: https://www.npmjs.com/package/ecc-universal
- npm (AgentShield): https://www.npmjs.com/package/ecc-agentshield
- GitHub App: https://github.com/apps/ecc-tools
- Discord: https://discord.gg/36yGMHGFbR
- Shorthand Guide: https://x.com/affaan/status/2012378465664745795
- Longform Guide: https://x.com/affaan/status/2014040193557471352
- Security Guide: https://x.com/affaan/status/2033263813387223421
- AgentShield: https://github.com/affaan-m/agentshield
- Source: `sources/ECC/`
