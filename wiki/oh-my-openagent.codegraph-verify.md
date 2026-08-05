---
title: oh-my-openagent.codegraph-verify
date: 2026-07-12
tags: [oh-my-openagent, codegraph-verify, openagent, plugins]
related: [[oh-my-openagent]], [[oh-my-hermes]], [[oh-my-opencode-slim]], [[openclaw]]
source: sources/oh-my-openagent/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# oh-my-openagent — CodeGraph Verification

## Claim-1: Multi-harness Agent OS with dual-edition product model

The repository ships as a single product in two editions: **Ultimate** (OpenCode plugin, `packages/omo-opencode/`) and **Light** (Codex CLI plugin, `packages/omo-codex/`, distributed as `lazycodex-ai`). A massive multi-harness refactor is in progress to support OpenCode, Codex, Senpi, Pi, Claude Code, and others through a layered architecture of 19 Core pure-TS packages + 3 MCP packages + adapters. The monorepo declares **27 workspace packages** in package.json; `packages/` holds 43 directories including 12 `oh-my-opencode-<platform>-<arch>` platform binary distribution packages and the non-workspace `lsp-tools-mcp`/`lsp-daemon` MCP packages. Additional harness adapters ship as workspaces: `omo-senpi`, `senpi-task`, `pi-goal`, `pi-webfetch`.

**Source evidence:** `AGENTS.md` lines 49-51 ("Ships in two editions of one product: Ultimate (omo for OpenCode) and Light (omo for Codex CLI)." "…the OpenCode-facing shim over 19 Core packages + 3 MCP packages + the Codex adapter."). Line 78 ("19 Core (pure-TS) pkgs" — including `omo-config-core`). `README.md` lines 112-129 (edition comparison table). `package.json` lines 8-32 (27 workspace packages: `rules-engine` … `omo-opencode`, including `omo-senpi`, `senpi-task`, `pi-goal`, `pi-webfetch`). `packages/` listing: 43 dirs, 12 `oh-my-opencode-*` platform binaries. `AGENTS.md` lines 185-200 (CODEX LIGHT EDITION section with full lazycodex architecture). Marketing/docs are external — `README.md` lines 28-29 (sisyphuslabs.ai waitlist) and line 69 (omo.vibetip.help docs badge).

## Claim-2: 53-62 lifecycle hooks across 5-tier composition with 12 OpenCode hook handlers

The plugin implements 53-62 lifecycle hooks composed across five tiers: Session (24), ToolGuard (18), Transform (7), Continuation (7), Skill (2) = 58 composed hook slots. Five slots are config-gated null by default (team-tool-gating, team-mode-status-injector, team-mailbox-injector, monitor-status-injector, goal) → **53 active on default config**; Team Mode adds +4 direct event handlers → **62 max**. Twelve hook handlers are wired into OpenCode's plugin interface including `config`, `tool`, `chat.message`, `event`, `tool.execute.before`, `tool.execute.after`, and experimental hooks for compacting and auto-continue (+2 wired in testing). Tools are config-gated: 12 always-on registry tools up to 38 total (team-mode +12, monitor +4, task system +4, hashline +1, interactive_bash +1, look_at +1, goal +3).

**Source evidence:** `AGENTS.md` lines 134-148 (hook handlers table with names, OpenCode hooks, and purposes — 14 rows incl. `tool`, `chat.message`, `event`, `tool.execute.before/after`, `experimental.session.compacting`). Lines 121-141 and 264 ("5-tier hook composition: Session (24) + ToolGuard (18) + Transform (7) + Continuation (7) + Skill (2) = 58 composed hook slots… 53 active on default config… Team mode also adds +4 direct event handlers… → 62 max"). Line 64 (hooks across 62 dirs). Lines 61-62 (plugin-interface.ts: "12 OpenCode hook handlers (+2 wired in testing/create-plugin-module.ts)"). Line 132 ("tool | tool | 12-38 registered tools (config-gated: team-mode +12, monitor +4, task system +4, hashline +1, interactive_bash +1, look_at +1, goal +3)") and lines 152-153 (TOOL CATALOG: 12 always-on registry tools, up to 38 conditional).

## Claim-3: Three-tier MCP system with built-in, Claude Code, and skill-embedded servers

MCP servers are loaded from three tiers: (1) Built-in MCPs — 3 remote HTTP + 2 local stdio MCPs (LSP, codegraph) from `packages/omo-opencode/src/mcp/`; (2) Claude Code MCPs — `.mcp.json` with `${VAR}` env expansion and allowlist; (3) Skill-embedded MCPs — from SKILL.md YAML frontmatter, per-session isolated with OAuth 2.0 + PKCE + DCR step-up.

**Source evidence:** `AGENTS.md` lines 220-226 (three-tier MCP table with source, loader, mechanism). Lines 68 and 224 (5 built-in MCPs). Lines 247-250 (skill-embedded MCP: Tier-3 MCPs per-session, stdio + HTTP). `AGENTS.md` line 256 ("Per-session MCP isolation: Tier-3 MCP clients keyed by `${sessionID}:${skillName}:${serverName}`").

## Claim-4: Hashline LINE#ID content-validated edit tool (Hash-Anchored Edits)

The plugin implements Hashline edits where every `Read` tool output is tagged with `LINE#ID` content hashes using characters from `ZPMQVRWSNKTXJBYH`. The `hashline_edit` tool validates the hash before applying any change — stale hash means rejection before corruption. Raised Grok Code Fast 1 benchmark from 6.7% to 68.3% success rate. Inspired by oh-my-pi.

**Source evidence:** `README.md` lines 315-332 (Hash-Anchored Edit Tool section: "Every line the agent reads comes back tagged with a content hash", "The agent edits by referencing those tags. If the file has changed since the last read, the hash won't match and the edit is rejected"). `AGENTS.md` line 255 ("Hashline edit + read pairing: Every Read tool output is tagged with LINE#ID content hashes; hashline_edit validates the hash before applying. Stale hash → reject."). `AGENTS.md` line 375 (Hashline chars: `ZPMQVRWSNKTXJBYH`).

## Claim-5: Team Mode — parallel multi-agent coordination (OFF by default)

Team Mode enables parallel multi-agent coordination modeled after Claude Code Agent Teams. Configurable via 11 fields in `team-mode.ts` schema. Member eligibility registry: eligible (sisyphus, atlas, sisyphus-junior), conditional (hephaestus), hard-reject (oracle, librarian, etc.). Storage layout uses `~/.omo/teams/{name}/` directories. Skills built on top: `hyperplan` (5 hostile critics) and `security-research` (3 hunters + 2 PoC engineers).

**Source evidence:** `AGENTS.md` lines 150-183 (TEAM MODE section: "OFF by default. Parallel multi-agent coordination."). Lines 155-171 (11-field schema). Lines 176-179 (member eligibility categories). Lines 181-183 (storage layout and implementation path). `README.md` lines 256-278 (Team Mode v4.0 description with `team_*` tools, `hyperplan`, `security-research` skills).

## Claim-6: IntentGate keyword detector with mode classification

The `keyword-detector` (IntentGate) classifies user intent into modes — `ultrawork`/`ulw`, `search`, `analyze`, `team` — and injects mode-specific prompts. The `ultrawork` (or `ulw`) shorthand activates every agent. Ultrawork skill pointer architecture uses a compact `<ultrawork-mode>` tag (<4096 bytes) for Codex truncation safety.

**Source evidence:** `README.md` lines 198-234 (ultrawork feature: "One word. Every agent activates. Doesn't stop until done."). `AGENTS.md` line 376 ("IntentGate (keyword-detector): classifies user intent (ultrawork/ulw, search, analyze, team) and injects mode-specific prompts."). `AGENTS.md` lines 130-131 (chat.message handler does "First-message variant, session setup, keyword detection"). `AGENTS.md` line 194 (Codex ultrawork skill pointer).

## Claim-7: Aggressive QA mandate with evidence-gated commits

The repository enforces an unusually strict QA policy: every change to code connected to OpenCode or Codex must run the matching QA skill (`opencode-qa` or `codex-qa`), write evidence to `.omo/evidence/`, and never commit or push without it. QA must be done in isolated XDG sandboxes to avoid polluting real config. Evidence files must document WHAT was tested, WHAT was observed, WHY it is enough, and WHAT was omitted.

**Source evidence:** `AGENTS.md` lines 7-37 (entire STOP section: "NO EVIDENCE FILE == NO QA == NO COMMIT == NO PUSH. ALWAYS. EVERY TIME. NO EXCEPTIONS."). Lines 15-20 (opencode-qa skill requirements with XDG sandbox isolation). Lines 22-27 (codex-qa skill requirements with isolated CODEX_HOME). Lines 29-36 (evidence recording format requirements).

## Claim-8: CLI surface — install/run/doctor/mcp-oauth/boulder/codex-ulw-loop, no sparkshell

The Commander.js CLI ships `install`, `run`, `doctor`, `mcp-oauth`, `boulder`, and `codex-ulw-loop` subcommands (plus `install-codex`, `install-senpi`, `config-migrate`). `sparkshell` was explicitly removed from the Codex cache installer (no reference remains under `packages/omo-codex/src/`). The Light edition wires 8 portable components to Codex lifecycle events: rules, comment-checker, git-bash, lsp, ultrawork, ulw-loop, start-work-continuation, telemetry.

**Source evidence:** `packages/omo-opencode/src/cli/` listing — `install.ts`, `run/`, `doctor/`, `mcp-oauth/`, `boulder/`, `codex-ulw-loop.ts`, `install-codex/`, `install-senpi/`; no sparkshell entry. `grep sparkshell packages/omo-codex/src/` → no matches (removed). `README.md` lines 215-216 (Light edition: "Portable OMO components (rules, comment-checker, git-bash, LSP, ultrawork, ulw-loop, start-work continuation, telemetry)… Install via `npx lazycodex-ai install`").
