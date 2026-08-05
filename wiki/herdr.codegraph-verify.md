---
name: herdr-codegraph-verify
tags: [herdr, terminal, tui, rust, agent, multiplexer, ratatui, wiki]
description: "Codegraph Verification: herdr — validating wiki claims against indexed source code symbols"
source: sources/herdr/
---

# Codegraph Verification: herdr

**Date:** 2026-07-30

## Claim 1: Terminal workspace manager for AI coding agents, single Rust binary
- **Wiki says:** Herdr is a terminal workspace manager for AI coding agents distributed as a single Rust binary.
- **Source evidence:**
  - `Cargo.toml` line 6 describes the project: `description = "terminal workspace manager for AI coding agents"`
  - `README.md` line 29 describes it as: "agent multiplexer that lives in your terminal"
  - `README.md` line 36 confirms: "one rust binary, no electron"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Version 0.7.5 with ratatui + crossterm
- **Wiki says:** Herdr is at version 0.7.5 and uses ratatui for TUI rendering with crossterm as the terminal backend.
- **Source evidence:**
  - `Cargo.toml` line 3: `version = "0.7.5"`
  - `Cargo.toml` line 34: `ratatui = { version = "0.30", features = ["unstable-rendered-line-info"] }`
  - `Cargo.toml` line 28: `crossterm = "0.29"`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: State separated from runtime + pure render
- **Wiki says:** Architectural principle: `AppState` is pure data separate from runtime, rendering is pure with no mutations during render.
- **Source evidence:**
  - `AGENTS.md` line 30 states: "**State is separated from runtime.** `AppState` is pure data, testable without PTYs or async. `PaneState` is separate from `PaneRuntime`."
  - `AGENTS.md` line 31 states: "**Render is pure.** `compute_view()` handles geometry and mutations. `render()` takes `&AppState` and only draws. Never mutate state during render."
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: portable-pty vendored fork + interprocess for IPC
- **Wiki says:** Uses a vendored fork of portable-pty and interprocess for IPC between server and client.
- **Source evidence:**
  - `Cargo.toml` line 32: `portable-pty = "=0.9.0"` (pinned version)
  - `Cargo.toml` line 48: `[patch.crates-io]` with `portable-pty = { path = "vendor/portable-pty" }` confirming vendored fork
  - `Cargo.toml` line 30: `interprocess = "2.4.2"` for IPC
  - `vendor/portable-pty/` directory exists with vendored fork
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Detach/reattach with session persistence
- **Wiki says:** Agents keep running when you detach; reattach from any terminal or over SSH with sessions that survive restarts.
- **Source evidence:**
  - `README.md` line 32 states: "**detach, agents keep running** — reattach from any terminal, or over ssh. sessions survive restarts."
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Keyboard and mouse both first-class
- **Wiki says:** Supports both tmux-style keyboard prefix keys and mouse interactions (click, drag, split).
- **Source evidence:**
  - `README.md` line 33 states: "**keyboard and mouse, both first-class** — tmux-style prefix keys *and* click, drag, split. pick per moment, not per tool."
  - `AGENTS.md` line 35 mentions "mouse-first TUI" in UI pattern guidance
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Server-owned runtime protocol migration
- **Wiki says:** Herdr is migrating toward a server-owned runtime protocol with the TUI as one client.
- **Source evidence:**
  - `AGENTS.md` line 38 states: "Herdr is migrating toward a server-owned runtime protocol with the TUI as one client. New work should not deepen the current server/TUI coupling."
  - `AGENTS.md` lines 40-47 classify features into shared runtime/session facts vs TUI presentation state
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: Vendored libghostty-vt with tracked patches
- **Wiki says:** The project vendors libghostty-vt with tracked patch files and a `.vendor.json` manifest.
- **Source evidence:**
  - `vendor/libghostty-vt/` directory exists (vendored dependency)
  - `vendor/libghostty-vt.vendor.json` records the upstream source commit
  - `vendor/libghostty-vt.patches.md` tracks local patches with metadata
  - `vendor/patches/libghostty-vt/` contains the individual patch files
  - `AGENTS.md` line 150 documents the "Vendored libghostty-vt" section with patch management procedures
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 8 key claims from the herdr wiki have been verified against the source code:
- ✅ Terminal workspace manager: Single Rust binary confirmed
- ✅ Version 0.7.5 + ratatui/crossterm: Confirmed in Cargo.toml
- ✅ State/runtime separation: Enforced in AGENTS.md principles
- ✅ Vendored portable-pty + interprocess: Confirmed in Cargo.toml dependencies
- ✅ Detach/reattach: Session persistence confirmed in README
- ✅ Keyboard + mouse: Both input modes confirmed
- ✅ Server-owned protocol migration: AGENTS.md boundary guardrail confirmed
- ✅ Vendored libghostty-vt: With tracked patches confirmed

## Related

- [[herdr]] -- Main wiki entry

## Cross-project

- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for Hermes Agent
- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
