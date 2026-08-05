---
name: herdr
tags: [cli, multiplexer, rust, terminal, tui, workspace-manager, ai-coding-agent, wiki, herdr]
description: "Terminal-based agent multiplexer and workspace manager for AI coding agents — tmux-style panes with detach/reattach in Rust"
source: sources/herdr/
verification_date: 2026-07-30
verified_by: codegraph-verify
---

# Herdr — Agent Multiplexer

| Field | Value |
|---|---|
| **Origin** | [cgwalters/herdr](https://github.com/cgwalters/herdr) |
| **License** | Not specified |
| **Stack** | Rust, crossterm, TUI |
| **Deployment** | Standalone binary (`curl/sh` install), Homebrew, Nix |
| **Source** | `sources/herdr/` |

## What is it?

A terminal-based agent multiplexer and workspace manager purpose-built for AI coding agents. Written in Rust, it provides tmux-style split panes, session detach/reattach, and a socket API for programmatic control — designed to manage multiple AI coding agent sessions side by side in the terminal.

Think of it as tmux specifically tailored for the AI coding workflow: run Claude Code in one pane, a terminal in another, and a file editor in a third, all within a single terminal window with keyboard-driven navigation.

## Key Features

- **tmux-Style Panes:** Split terminal into multiple resizable panes, each running a different agent or tool.
- **Detach/Reattach:** Detach from a session and reattach later — persistent workspace state across terminal closures.
- **Socket API:** Programmatic control via Unix domain socket for external tooling and automation.
- **Rust Performance:** Fast startup, minimal memory footprint, native binary with no runtime dependencies.
- **Agent-Focused Design:** Built specifically for AI coding agent workflows, not general-purpose terminal multiplexing.
- **Multiple Install Paths:** Binary distribution via curl/sh, Homebrew tap, or Nix package.

## Tech Stack

| Component | Technology |
|---|---|
| **Language** | Rust |
| **Terminal** | crossterm (cross-platform terminal library) |
| **UI** | TUI (Terminal User Interface) |
| **IPC** | Unix domain socket API |

## Deployment

### Quick Install (curl/sh)

```bash
curl -fsSL https://raw.githubusercontent.com/cgwalters/herdr/main/install.sh | bash
```

### Homebrew

```bash
brew tap cgwalters/herdr
brew install herdr
```

### Nix

```bash
nix profile install github:cjwalters/herdr
```

### From Source

```bash
git clone https://github.com/cgwalters/herdr.git
cd herdr
cargo build --release
# Binary at target/release/herdr
```

## Related

- [[opencode]] — AI coding agent that herdr can multiplex alongside other tools
- [[hermes-agent]] — Agent platform that could be managed within herdr sessions
- [[claw-code]] — Another agent tool that pairs with herdr's multiplexing
