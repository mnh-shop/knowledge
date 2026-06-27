---
name: oh-my-openagent
description: "OpenAgent-compatible extensible agent runtime with MCP support and multi-model architecture"
tags: [wiki, agent-runtime, mcp, multi-provider, typescript]
source: sources/oh-my-openagent/
---

# oh-my-openagent

**oh-my-openagent** (OmO) is an OpenCode plugin that extends the harness with 11 discipline agents, 53-60 lifecycle hooks, a 3-tier MCP system, Hashline LINE#ID edit tool, IntentGate keyword detector, Team Mode (parallel multi-agent coordination), and full Claude Code compatibility. Ships in two editions: **Ultimate** (OpenCode plugin) and **Light** (Codex CLI edition via `lazycodex-ai`).

## Description

OmO transforms OpenCode from a single-agent harness into a multi-agent operating system. The main orchestrator (Sisyphus) delegates to specialists (Hephaestus, Oracle, Librarian, Explore, etc.) based on task category, routing automatically to the best model for each job. It features a 5-tier hook composition system with 53-60 hooks, 20-39 config-gated tools, built-in MCPs for web search (Exa), docs (Context7), code search (Grep.app), LSP, and Codegraph, plus skill-embedded MCPs that spin up on demand.

Built and maintained by Jobdori (an AI assistant running on a customized OpenClaw fork) in real-time, live in the project's Discord community.

## Key Features

- **11 Discipline Agents** — Sisyphus (orchestrator, Claude Opus/Kimi K2.6/GLM 5.1), Hephaestus (deep worker, GPT-5.5), Oracle (architecture/debugging), Librarian (docs/code search), Explore (fast codebase grep), Atlas (research), Prometheus (strategic planner), Metis (plan consultant), Momus (critic), Multimodal Looker (vision), Sisyphus Junior (subagent router). Each tuned to its model's specific strengths.
- **Team Mode** (v4.0, opt-in) — Lead agent + up to 8 parallel members, real-time tmux visualization, dedicated `team_*` tools. Powers `hyperplan` (5 hostile critics) and `security-research` (3 hunters + 2 PoC engineers).
- **`ultrawork` / `ulw`** — Single-word command that activates every agent and drives tasks to completion. Available in both Ultimate and Light editions.
- **IntentGate** — Analyzes true user intent before classifying or acting. Recognizes `ultrawork`/`ulw`, `search`, `analyze`, `team` modes.
- **Hash-Anchored Edit Tool (Hashline)** — Every read output tagged with `LINE#ID` content hashes; edit validates hash before applying. Zero stale-line errors. Grok Code Fast benchmark: 6.7% → 68.3% success rate from the edit tool change alone.
- **LSP Integration** — Diagnostics, navigation, symbols, workspace rename via built-in MCP. Same LSP server in both editions.
- **AST-Grep** — Pattern-aware code search and rewriting across 25+ languages (Ultimate edition).
- **3-Tier MCP System** — Tier 1: Built-in MCPs (Exa, Context7, Grep.app, LSP, Codegraph). Tier 2: `.mcp.json` Claude Code compatibility with `${VAR}` env expansion. Tier 3: Skill-embedded MCPs via SKILL.md frontmatter with OAuth 2.0 + PKCE + DCR step-up.
- **5-Tier Hook Composition** — Session (23) + ToolGuard (17) + Transform (4) + Continuation (7) + Skill (2) = 53 base hooks. With Team Mode: +1 ToolGuard, +2 Transform, +4 event handlers = 60 total.
- **Prometheus Planner** — Interview-mode strategic planning before any execution. Asks questions, identifies scope, and builds a verified plan before a single line of code is touched.
- **Ralph Loop / `/ulw-loop`** — Self-referential loop. Doesn't stop until 100% done. Durable multi-goal orchestration with evidence audit backed by `.omo/ulw-loop/`.
- **Todo Enforcer** — Detects agent idle and yanks it back to task.
- **Comment Checker** — Blocks AI slop comment patterns in generated code.
- **Rules Injection** — `AGENTS.md` and `.omo/rules/**` auto-loaded into agent context at every prompt.
- **Background Agents** — Fire 5+ specialists in parallel with configurable concurrency limits per provider/model.
- **Claude Code Compatibility** — Every hook, command, skill, MCP, and plugin works unchanged.
- **Deep Initialization (`/init-deep`)** — Auto-generates hierarchical `AGENTS.md` files throughout the project tree.
- **Multi-Level Config** — Walked configs (closer wins) merged onto user config, with defaults from Zod v4 schema. JSONC with comments and trailing commas.
- **Telemetry** — Anonymous DAU/WAU/MAU tracking via PostHog (opt-out via `OMO_DISABLE_POSTHOG=1`).
- **Codex CLI Light Edition** — 8 portable components (rules, comment-checker, git-bash, LSP, ultrawork, ulw-loop, start-work continuation, telemetry) wired to Codex lifecycle events.

## Architecture

The project is organized as a monorepo with 37+ workspace packages, layered as Core → MCP → Skills → Adapters → Platform/Web.

```
oh-my-opencode/
├── packages/
│   ├── omo-opencode/          # OpenCode plugin adapter (formerly root src/)
│   │   └── src/
│   │       ├── index.ts       # Plugin entry; thin wrapper
│   │       ├── plugin-interface.ts  # 12 OpenCode hook handlers
│   │       ├── agents/        # 11 agent factories
│   │       ├── hooks/         # 53-60 lifecycle hooks across 60 dirs
│   │       ├── tools/         # 14 native tool dirs
│   │       ├── features/      # 23 feature modules (team-mode, background-agent, skill-mcp-manager, etc.)
│   │       ├── shared/        # Cross-cutting utilities
│   │       ├── config/        # Zod v4 schema system (36 schema files)
│   │       ├── cli/           # Commander.js CLI: install, run, doctor, mcp-oauth, boulder, sparkshell, ulw-loop
│   │       ├── mcp/           # 5 built-in MCPs (3 remote HTTP + 2 local stdio)
│   │       ├── plugin/        # OpenCode hook handlers + 6-phase config loading pipeline
│   │       └── openclaw/      # Bidirectional Discord/Telegram/HTTP/shell integration
│   ├── omo-codex/             # Codex CLI Light edition (lazycodex)
│   ├── utils/ model-core/ prompts-core/ rules-engine/ agents-md-core/
│   │   comment-checker-core/ hashline-core/ boulder-state/ telemetry-core/
│   │   lsp-core/ mcp-stdio-core/ tmux-core/ claude-code-compat-core/
│   │   skills-loader-core/ mcp-client-core/ openclaw-core/ team-core/
│   │   delegate-core/         # 18 Core (pure-TS) packages
│   ├── lsp-tools-mcp/ git-bash-mcp/ lsp-daemon/  # 3 MCP-layer packages
│   ├── shared-skills/         # Cross-harness SKILL.md bundle
│   └── web/                   # Marketing site (Next.js 15 + Cloudflare Workers)
├── bin/                       # Platform-detection JS shim (5 bin aliases)
├── script/                    # Build/publish automation
└── docs/                      # User-facing docs
```

**Initialization Flow:**

```
pluginModule.server(input, options)
  → installAgentSortShim()
  → initConfigContext()
  → logLegacyPluginStartupWarning()
  → migrateLegacyWorkspaceDirectory()
  → detectDuplicateOmoPlugin()
  → injectServerAuthIntoClient()
  → loadPluginConfig()
  → selectRuntimeSecuritySkills() + createRuntimeSkillSourceServer()
  → initI18n()
  → setAgentSortOrder()
  → initializeOpenClaw()
  → checkTeamModeDependencies()
  → startTmuxCheck()
  → createManagers()
  → createTools()
  → createHooks()
  → createPluginInterface()
  → createPluginDispose()
```

**Architecture Invariants:**

- Canonical agent order: Sisyphus → Hephaestus → Prometheus → Atlas (enforced by `installAgentSortShim()`)
- Hashline edit + read pairing: every `Read` tool output tagged with `LINE#ID` content hashes; edit validates hash before applying
- Per-session MCP isolation: Tier-3 MCP clients keyed by `${sessionID}:${skillName}:${serverName}`
- Two independent fallback systems: `model-fallback` (proactive, `chat.params`) vs `runtime-fallback` (reactive, `session.error`)
- OpenClaw bidirectional: outbound dispatchers fire on session events; inbound daemon polls Discord/Telegram and `send-keys` replies into tracked tmux pane
- All internal `session.prompt` / `session.promptAsync` calls must go through the shared `prompt-async-gate` — no raw prompt calls outside it

**Tool Catalog (config-gated):** 18 always-on (LSP, grep, glob, session, background, call_omo_agent, task, skill, skill_mcp) + 1-12 conditional (look_at, interactive_bash, task_system, hashline_edit, team_mode tools).

## Quick Start

```bash
# Ultimate edition (OpenCode)
bunx oh-my-openagent install

# Light edition (Codex CLI)
npx lazycodex-ai install

# Both editions
bunx oh-my-openagent install --platform=both

# Recommended: let an LLM agent install for you
# Paste into Claude Code, AmpCode, Cursor, or any agent:
# "Install and configure oh-my-openagent by following the instructions here:
#  https://raw.githubusercontent.com/code-yeongyu/oh-my-openagent/refs/heads/dev/docs/guide/installation.md"

# Start a session with ultrawork
Type `ultrawork` or `ulw` in the agent prompt

# Health diagnostics
bunx oh-my-opencode doctor

# Run a non-interactive session
bunx oh-my-opencode run <message>
```

## Domain Docs

- [[mcp]] — Model Context Protocol implementations  
- [[openclaw]] — Bidirectional Discord/Telegram integration

## Related

- [[opencode]] — The underlying OpenCode harness
- [[clawpier]] — Agent toolkit; OmO shares skill and MCP patterns
- [[hermes-agent]] — Hermes agent platform; compatible with OmO's Claude Code compatibility layer
- [[oh-my-pi]] — Pi coding agent plugin; Hashline edit tool is inspired by oh-my-pi's approach
- [[graphify]] — Knowledge graph generator; OmO bundles codegraph MCP for graph-based code queries
- [[mission-control]] — Mission control dashboard; OmO runs on OpenCode which mission-control integrates with

## Links

- Source: `/Users/admin1/Documents/knowledge/sources/oh-my-openagent/`
- GitHub: https://github.com/code-yeongyu/oh-my-openagent
- npm: https://www.npmjs.com/package/oh-my-opencode
- Documentation: https://omo.vibetip.help/docs
- Discord: https://discord.gg/PUwSMR9XNk
- Website (Sisyphus Labs): https://sisyphuslabs.ai
- LazyCodex: https://lazycodex.ai
