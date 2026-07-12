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

The repository ships as a single product in two editions: **Ultimate** (OpenCode plugin, `packages/omo-opencode/`) and **Light** (Codex CLI plugin, `packages/omo-codex/`, distributed as `lazycodex-ai`). A massive multi-harness refactor is in progress to support OpenCode, Codex, Pi, Claude Code, and others through a layered architecture of 18 Core pure-TS packages + 3 MCP packages + adapters.

**Source evidence:** `AGENTS.md` lines 49-51 ("Ships in two editions of one product: Ultimate (omo for OpenCode) and Light (omo for Codex CLI).") Lines 3-4 ("MASSIVE MULTI-HARNESS AGENT OS REFACTOR IN PROGRESS"). `README.md` lines 112-129 (edition comparison table). `package.json` lines 8-32 (37 workspace packages including `omo-opencode`, `omo-codex`, `omo-senpi`). `AGENTS.md` lines 185-200 (CODEX LIGHT EDITION section with full lazycodex architecture).

## Claim-2: 54-62 lifecycle hooks across 5-tier composition with 14 OpenCode hook handlers

The plugin implements 54-62 lifecycle hooks composed across five tiers: Session (24), ToolGuard (18), Transform (7), Continuation (7), Skill (2). Team Mode adds +4 event handlers for 62 max. Fourteen hook handlers are wired into OpenCode's plugin interface including `config`, `tool`, `chat.message`, `event`, `tool.execute.before`, `tool.execute.after`, and experimental hooks for compacting and auto-continue.

**Source evidence:** `AGENTS.md` lines 121-141 (14 hook handlers table with names, OpenCode hooks, and purposes). Lines 252-258 (architecture invariants: "5-tier hook composition: Session (24) + ToolGuard (18) + Transform (7) + Continuation (7) + Skill (2) = 58 composed hook slots"). Lines 64-65 (hooks across 61 dirs).

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
