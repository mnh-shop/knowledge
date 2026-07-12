---
title: oh-my-opencode-slim.codegraph-verify
date: 2026-07-12
tags: [oh-my-opencode-slim, codegraph-verify, opencode, plugins]
related: [[oh-my-opencode-slim]], [[opencode]], [[oh-my-hermes]], [[customize-opencode]]
source: sources/oh-my-opencode-slim/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# oh-my-opencode-slim — CodeGraph Verification

## Claim-1: Seven specialized agents themed as "The Pantheon" with orchestrator-first architecture

The plugin defines seven named agents with thematic identities: Orchestrator (master delegator), Explorer (codebase reconnaissance), Oracle (strategic advisor/debugger), Council (multi-LLM consensus), Librarian (external knowledge), Designer (UI/UX), and Fixer (fast implementation). The Orchestrator schedules work as background tasks to specialists and reconciles results — a scheduler-first multi-agent workflow system.

**Source evidence:** `README.md` lines 310-605 (Meet the Pantheon section with seven agents, each having role, prompt file reference, default model, recommended models, and model guidance). Lines 197-224 (V2 background agents: "the Orchestrator now dispatches specialists as background tasks, tracks task/session IDs, waits for completion events, and reconciles results"). `src/agents/` directory listing shows `orchestrator.ts`, `explorer.ts`, `oracle.ts`, `council.ts`, `librarian.ts`, `designer.ts`, `fixer.ts`, `observer.ts`.

## Claim-2: Two-installed presets (openai and opencode-go) with per-agent model routing

The installer generates two configuration presets. The `openai` preset uses GPT-5.5 for orchestrator/oracle/fixer, GPT-5.4-mini for librarian/explorer/designer. The `opencode-go` preset routes through OpenCode Go provider: GLM 5.2 for orchestrator, Qwen3.7-max for oracle, DeepSeek v4 Flash for librarian/explorer/fixer, Kimi K2.7 Code for designer. Each agent has individually scoped skill and MCP permissions.

**Source evidence:** `README.md` lines 144-167 (full preset configuration examples with model per agent, skill arrays, MCP arrays using `["*", "!context7"]` syntax). Lines 113-119 (preset switching guide with `--preset=opencode-go` flag). `package.json` lines 2-4 (name `oh-my-opencode-slim`, version 2.1.0, "lightweight agent orchestration plugin for OpenCode - a slimmed-down fork of oh-my-opencode").

## Claim-3: V2 features include background orchestration, Companion, Deepwork, Reflect, Worktrees

V2 introduced five major features: (1) **Background agents** — Orchestrator dispatches specialists as background tasks; (2) **Companion** — optional floating desktop status window showing live agent activity; (3) **Deepwork** — structured workflow for large/risky multi-file work with persistent plan files and Oracle review gates; (4) **Reflect** — reviews repeated work patterns and suggests reusable skills/configs; (5) **Worktrees** — Git worktree management as isolated coding lanes under `.slim/worktrees/`.

**Source evidence:** `README.md` lines 197-303 (V2 features section covering Background Agents lines 219-224, Companion lines 227-245, Deepwork lines 248-261, Reflect lines 264-285, Worktrees lines 288-291, and the bundled oh-my-opencode-slim skill lines 294-306). Docs directory listing shows `docs/v2-background-orchestration.md`, `docs/companion.md`, `docs/skills.md`.

## Claim-4: Council multi-LLM consensus agent with parallel model orchestration

The Council agent runs multiple models in parallel, gathers competing judgments, and distills a single verdict. Councillors come from `council.presets` configuration. Orchestrator does not auto-call Council to avoid high cost; it is designed for manual use (e.g., `@council compare these two architectures`). Config-driven setup with a dedicated guide at `docs/council.md`.

**Source evidence:** `README.md` lines 437-482 (Council: "The Council is not a lone being but a chamber of minds summoned when one answer is not enough"). Lines 439-441 (NOTICE: "Why doesn't Orchestrator auto-call Council more often? This is intentional... auto-delegation is kept strict because it is usually the highest-cost path"). `README.md` line 661 (docs table: "Run multiple models in parallel and synthesize a single answer with `@council`"). `src/agents/council.ts` (agent factory file). `src/council/` directory confirmed as council manager.

## Claim-5: Multiplexer integration for live agent monitoring via Tmux/Zellij/Herdr

The Multiplexer integration automatically opens each background agent in a dedicated Tmux, Zellij, or Herdr pane so specialists can be watched live while the Orchestrator continues coordinating. Session lifecycle management includes graceful shutdown (Ctrl+C before kill-pane), session abort timing, and event handler wiring for pane cleanup.

**Source evidence:** `README.md` lines 139-141 ("highly recommended to enable and configure Multiplexer Integration. It automatically opens each agent in a dedicated Tmux, Zellij, or Herdr pane"). `AGENTS.md` lines 53-72 (Tmux Session Lifecycle Management section with lifecycle flow diagram, graceful shutdown code showing `send-keys "C-c"` before `kill-pane`, session abort timing rules). `src/multiplexer/` directory confirms multiplexer session management. `src/utils/tmux.ts` for tmux utilities.

## Claim-6: Optional Observer agent for multimodal read-only analysis

Observer is a dedicated read-only visual analysis agent that interprets images, screenshots, PDFs, and diagrams. Returns structured observations without loading raw file bytes into the main context. Disabled by default; enabled with `"disabled_agents": []` and a vision-capable model. The `opencode-go` preset enables it automatically with `opencode-go/kimi-k2.6`.

**Source evidence:** `README.md` lines 609-647 (Optional Agents section: Observer — "Read-only visual analysis - interprets images, screenshots, PDFs, and diagrams. Disabled by default"). Line 628 (opencode-go preset enables it: `--preset=opencode-go` enables it with `opencode-go/kimi-k2.6`). `src/agents/observer.ts` (observer agent factory file confirmed in agents directory listing).

## Claim-7: Companion desktop overlay for live agent visibility

Companion is a floating desktop status window that shows which agents are currently active, including parallel background specialists. Configurable positions, sizes, and install settings. Disabled by default during interactive install; enable with `--companion=yes`. Has its own documentation at `docs/companion.md` and manifest at `src/companion/companion-manifest.json`.

**Source evidence:** `README.md` lines 227-245 (Companion section with animated GIF showing "Left bottom visual companion", defaults to `no` during install, `--companion=yes` to enable). `README.md` line 244: "See [Companion](docs/companion.md) for configuration, positions, sizes, and install details". `package.json` line 43 (`src/companion/companion-manifest.json` included in published package `files`). `src/companion/` directory confirmed in source tree.
