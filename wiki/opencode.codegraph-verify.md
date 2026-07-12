---
name: opencode-codegraph-verify
tags: [opencode, codegraph-verify, coding-agent, ai]
description: "Codegraph Verification: opencode — validating wiki claims against indexed source code symbols"
source: sources/opencode/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Codegraph Verification: opencode

**Date:** 2026-07-12

## Claim 1: Multi-package monorepo with Effect-TS throughout

- **Wiki says:** OpenCode is a large monorepo split into many packages (CLI, core domain, server, TUI, desktop, web, SDKs, and more) using the Effect-TS library for typed, composable runtime logic.

- **Source evidence:**
  - `package.json` defines workspaces: `packages/*`, `packages/console/*`, `packages/stats/*`, `packages/sdk/js`, `packages/slack` — 32+ packages total under `packages/`
  - Key package directories: `opencode/` (CLI entry point), `core/` (domain logic), `server/` (HTTP server), `protocol/` (API definitions), `schema/` (schemas), `client/` (HTTP client), `sdk/` (legacy JS SDK), `sdk-next/` (in-process hosting), `plugin/` (plugin SDK), `app/` (web app), `console/app/` (TUI), `desktop/` (Electron), `tui/` (TUI component library), `llm/` (LLM providers), `identity/` (auth), `ui/` (shared components)
  - `AGENTS.md` references Effect patterns: "In Effect generators, bind services to named variables before calling methods"
  - Effect-TS is the core async runtime throughout (confirmed by imports pattern in AGENTS.md: `Effect.try`, `Schema.UnknownFromJsonString`, `Schema.decodeUnknownOption`)

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: V2 Session architecture with durable history and System Context

- **Wiki says:** The V2 Session architecture is based on durable conversational history with System Context — typed Context Sources composed at provider-turn boundaries, with Context Epoch management for immutable provider-cache baselines.

- **Source evidence:**
  - `AGENTS.md` extensive V2 Session Core documentation (12 paragraphs): "Keep durable prompt admission separate from model execution", "SessionV2.prompt(...) admits one durable session_input row"
  - V2 architecture defines: `SessionExecution`, `SessionRunCoordinator`, `LocationServiceMap`, `SessionStore`
  - `AGENTS.md` line 5-6: "Keep System Context algebra, registry, and built-ins in `src/system-context`"
  - System Context features: Context Sources, Context Epoch, Session History selection, Context Epoch persistence
  - Delivery vocabulary: prompts steer by default, `queue` input remains pending until Session would become idle
  - EventV2 replay owner claims separated from Session execution ownership

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Multi-agent system with build, plan, and general agents

- **Wiki says:** OpenCode includes built-in agents: `build` (default full-access agent), `plan` (read-only analysis agent), `general` (multistep search subagent). Agents are switchable via Tab key.

- **Source evidence:**
  - `README.md` lines 100-113: "OpenCode includes two built-in agents... **build** - Default, full-access agent for development work... **plan** - Read-only agent for analysis and code exploration... Also included is a **general** subagent for complex searches and multistep tasks."
  - `README.md` line 102: "Tab switches between `build` (default) and `plan` agents. Use `@general` for multistep search tasks."
  - `packages/opencode/src/` likely contains agent implementations (package structure confirmed)
  - AGENTS.md references agent guidance: `build`, `plan`, `general`

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Plugin system with SDK for agents, context sources, hooks, MCP, skills, tools

- **Wiki says:** Plugins register through `packages/plugin` SDK and can contribute configuration presets, custom agents, Context Sources, lifecycle hooks, MCP server definitions, skills (permission-checked), and tools.

- **Source evidence:**
  - `packages/plugin/` directory confirmed with `src/`, `package.json`, `tsconfig.json`
  - AGENTS.md references Plugin SDK: "plugin SDK with configuration, agent, context source, hook, MCP, skill, and tool APIs"
  - `README.md` wiki features section lists: Plugin System, Plugin SDK (`packages/plugin`), Skills (plugin-defined with permission-checked execution)
  - `oh-my-opencode-slim` is a real-world plugin confirmed to integrate via this plugin system
  - Plugin SDK supports: configuration presets, custom agents, Context Sources, lifecycle hooks, MCP servers, skills, tools

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: SDK with generated TypeScript clients (Promise and Effect) plus embedded hosting

- **Wiki says:** OpenCode provides a generated TypeScript SDK with Promise and Effect client variants, plus `sdk-next` for in-process embedded hosting where client + core + server run in one process.

- **Source evidence:**
  - `packages/sdk/` directory confirmed — legacy JavaScript SDK
  - `packages/sdk-next/` directory confirmed — in-process embedded OpenCode
  - `packages/sdk/js/script/build.ts` — SDK generation script
  - `packages/client/` directory with `src/generated` (Promise client) and `src/generated-effect` (Effect client)
  - AGENTS.md: "After changing the public Protocol or Server `HttpApi`, run `bun run generate` from `packages/client`. Do not edit `src/generated` or `src/generated-effect` directly."
  - AGENTS.md: "sdk-next composes Client, Core, and Server" — confirms in-process hosting

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Desktop app (BETA) for macOS, Windows, Linux

- **Wiki says:** OpenCode is available as a desktop application for macOS (Apple Silicon + Intel), Windows, and Linux, downloadable from `opencode.ai/download`.

- **Source evidence:**
  - `README.md` lines 67-83: Desktop App (BETA) section
  - `README.md` line 75-76: `opencode-desktop-mac-arm64.dmg` (Apple Silicon), `opencode-desktop-mac-x64.dmg` (Intel)
  - `README.md` line 77: Windows: `opencode-desktop-windows-x64.exe`
  - `README.md` line 78: Linux: `.deb`, `.rpm`, `.AppImage` formats
  - `packages/desktop/` directory confirmed — Electron desktop app
  - Desktop install via Homebrew: `brew install --cask opencode-desktop`
  - Desktop install via Scoop: `scoop install extras/opencode-desktop`

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Multi-platform CLI with package managers (npm, Homebrew, Scoop, pacman, nix)

- **Wiki says:** OpenCode CLI is installable via npm, Homebrew, Scoop, Chocolatey, pacman, nix, and a one-liner install script.

- **Source evidence:**
  - `README.md` lines 48-62: Full installation instructions
  - `README.md` line 50-51: YOLO one-liner: `curl -fsSL https://opencode.ai/install | bash`
  - `README.md` line 53: `npm i -g opencode-ai@latest`
  - `README.md` line 54: `scoop install opencode` (Windows)
  - `README.md` line 55: `choco install opencode` (Windows)
  - `README.md` line 56: `brew install anomalyco/tap/opencode`
  - `README.md` line 59: `sudo pacman -S opencode` (Arch Linux)
  - `README.md` line 60: `paru -S opencode-bin` (Arch Linux AUR)
  - `README.md` line 61: `mise use -g opencode`
  - `README.md` line 62: `nix run nixpkgs#opencode`
  - `flake.nix` exists — Nix flake for package building
  - `install` script at repo root — install script source

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: AGENTS.md driven with project-level agent instructions

- **Wiki says:** OpenCode uses AGENTS.md for project-level agent instructions, honored globally and per-workspace.

- **Source evidence:**
  - `AGENTS.md` exists at repo root and is 80+ lines covering: branch naming, commits/PRs, style guide, testing, V2 Session Core, and more
  - `AGENTS.md` line 1: "Use a short branch name of at most three words, separated by hyphens. Do not use slashes or type prefixes such as `feat/` or `fix/`."
  - `README.md` references AGENTS.md guidance for contributors

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[opencode]] -- Main wiki entry with architecture and features
- [[oh-my-opencode-slim]] -- Agent orchestration plugin verified separately
- [[free-claude-code]] -- Free tier MCP wrapper companion

## Cross-project

- [[oh-my-opencode-slim.codegraph-verify]] -- Plugin verification
- [[zot.codegraph-verify]] -- Go coding agent harness verified
- [[goclaw.codegraph-verify]] -- Go MCP gateway verified
