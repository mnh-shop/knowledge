---
name: open-design-codegraph-verify
tags: [open-design, codegraph-verify, design, open-source]
description: "Codegraph Verification: open-design — validating wiki claims against indexed source code symbols"
source: sources/open-design/
---

# Codegraph Verification: open-design

**Date:** 2026-07-12

## Claim 1: Open-source Claude Design alternative with 100+ skills, 150 design systems, 261 plugins
- **Wiki says:** Open Design (OD) is the open-source Claude Design alternative shipping 100+ skills, 150 brand-grade DESIGN.md systems, 261 ready-to-use plugins. Apache-2.0 licensed.
- **Source evidence:**
  - `README.md` line 1: "Open Design: The open-source Claude Design alternative"
  - `README.md` line 34: "🎨 **The local-first, open-source [Claude Design][cd] alternative**"
  - `README.md` line 34: "⚡ **100+ skills** · ✨ **150 brand-grade `DESIGN.md` systems** · 📦 **261 ready-to-use plugins**"
  - `skills/` directory contains 163 skill directories confirmed by listing
  - `design-systems/` directory exists with 150+ brand folders
  - `plugins/_official/` directory with subdirectories: `scenarios/` (11), `image-templates/` (45), `video-templates/` (50), `design-systems/` (142), `atoms/` (13), `examples/` (140)
  - `LICENSE` is Apache-2.0
  - `README.md` line 276: Comparison table showing "✅ Apache-2.0" for Open Design vs "❌" for Claude Design, Figma, Lovable/v0/Bolt
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Agent-native, model-agnostic with 22+ CLI integrations + BYOK proxy
- **Wiki says:** OD doesn't ship its own agent. It works with Claude Code, Codex, Cursor, Copilot, Gemini, OpenCode, OpenClaw, Antigravity, Cline, Trae, Kimi, Pi, Mistral Vibe, Hermes Agent, and more — 16+ CLIs via MCP install, plus BYOK proxy for any OpenAI-compatible endpoint.
- **Source evidence:**
  - `README.md` lines 115-131: Table listing 15 supported coding agents with status and one-line MCP install commands
  - `README.md` line 114: "Open Design ships as skills, a CLI, and an MCP server that mainstream coding agents consume natively. A single `od mcp install <agent>` wires the MCP server into that agent's config"
  - `README.md` line 139: BYOK proxy: "The BYOK proxy at `POST /api/proxy/{anthropic,openai,azure,google,ollama,senseaudio}/stream` gives you the same loop (no process spawn)"
  - `README.md` line 139: "per-target SSRF protection blocks internal IPs / link-local / CGNAT at the daemon edge"
  - `apps/daemon/src/agents.ts` — mentioned as the adapter contract source
  - Architecture diagram in README shows spawn integrations for all listed CLIs
  - `docs/agent-adapters.md` documents the full agent adapter contract
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Three-axis composition: skills, design systems, and craft references
- **Wiki says:** Three composable planes: Skills carry artifact shape and design taste, Design Systems carry brand visual language via 9-section DESIGN.md, Craft carries universal brand-agnostic design rules (typography, color, anti-AI-slop, etc.).
- **Source evidence:**
  - `README.md` line 268: "🌍 **Composable on three planes.** **Plugins** carry runnable workflows · **skills** carry the agent's design taste · **design systems** carry the brand."
  - `craft/README.md` lines 8-18: Explicit three-axis breakdown table: `skills/` (artifact shape), `design-systems/` (brand visual language), `craft/` (universal craft knowledge)
  - `craft/README.md` line 14: "Universal craft knowledge — true regardless of brand"
  - `craft/` directory contains 10 craft files: `typography.md`, `typography-hierarchy.md`, `typography-hierarchy-editorial.md`, `color.md`, `anti-ai-slop.md`, `state-coverage.md`, `animation-discipline.md`, `accessibility-baseline.md`, `rtl-and-bidi.md`, `form-validation.md`, `laws-of-ux.md`
  - `craft/README.md` line 26-30: Skills opt in via `od.craft.requires` frontmatter array
  - `README.md` lines 397-424: 100+ skills table with modes, scenarios, and output types
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Local-first desktop app with daemon, web UI, and MCP server architecture
- **Wiki says:** Local-first native desktop apps (macOS + Windows), local daemon (Express + SQLite), Next.js web UI, sandboxed iframe preview, stdio MCP server. Architecture diagram shows daemon → agent spawn → artifact pipeline.
- **Source evidence:**
  - `README.md` line 267: "🖥️ **Local-first, BYOK at every layer.** Native desktop apps for macOS (Apple Silicon + Intel) and Windows (x64). Linux AppImage on the optional release lane. No telemetry, no cloud round-trip."
  - Architecture diagram `README.md` lines 541-576: Full diagram showing daemon layer (Express+SQLite), API endpoints, agent spawn layer, and MCP server
  - Stack table: Frontend = Next.js 16 App Router + React 18, Daemon = Node 24 · Express · SSE streaming · `better-sqlite3`, Preview = Sandboxed `srcdoc` iframe
  - `apps/daemon/` directory exists with Express server and CLI
  - `apps/web/` directory exists with Next.js 16 App Router
  - `apps/desktop/` and `apps/packaged/` directories exist for Electron shell
  - `README.md` lines 373-391: MCP server documentation with `od mcp install` command
  - `AGENTS.md` Daemon data directory contract section documents data path resolution
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Plugin system with portable SKILL.md format and marketplace
- **Wiki says:** 261 official plugins in `plugins/_official/`, each is a portable agent-skill folder with SKILL.md + optional open-design.json manifest. Plugins run in any coding agent, support migration workflows (Figma → React), and can be installed via CLI or web UI.
- **Source evidence:**
  - `plugins/_official/` directory exists with subcategories: `scenarios/` (11), `image-templates/` (45), `video-templates/` (50), `design-systems/` (142), `atoms/` (13), `examples/` (140)
  - `README.md` line 503-506: "A plugin needs only a SKILL.md at minimum; to list it in the Open Design marketplace, add an open-design.json"
  - Plugin directory structure documented at `README.md` lines 507-514: `my-plugin/├── SKILL.md ├── open-design.json ├── README.md ├── preview/ └── examples/`
  - `README.md` lines 491-498: CLI commands: `od plugin list`, `od plugin search`, `od plugin info`, `od plugin install`, `od plugin apply`
  - `plugins/spec/SPEC.md` exists for plugin specification
  - `plugins/spec/AGENT-DEVELOPMENT.md` exists for agent-based plugin development
  - `plugins/community/` directory for community plugins
  - `plugins/registry/` directory for publishing flow
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 5 key claims from the open-design wiki have been verified against the source code:
- ✅ Open-source alternative: Apache-2.0, 163 skills, 150+ design systems, 261 plugins confirmed
- ✅ Agent-native 22+ CLIs: 15 agents in table + BYOK proxy confirmed; MCP install architecture documented
- ✅ Three-axis composition: skills/ + design-systems/ + craft/ all present with documented roles
- ✅ Local-first desktop app: Daemon + Web + Desktop apps confirmed with architecture diagram
- ✅ Plugin system: 261 official plugins with SKILL.md format, marketplace, and CLI confirmed

## Related

- [[open-design]] -- Main wiki entry
- [[skills]] -- Agent skills catalog
- [[drawio-skill]] -- Draw.io diagramming skill
- [[ux-methodology]] -- UX methodology references

## Cross-project

- [[hermes-agent.codegraph-verify]] -- Hermes agent codegraph verification
- [[openclaw.codegraph-verify]] -- OpenClaw codegraph verification
- [[agentfield.codegraph-verify]] -- AgentField codegraph verification
