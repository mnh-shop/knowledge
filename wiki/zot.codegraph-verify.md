---
name: zot-codegraph-verify
tags: [zot, codegraph-verify, go, coding-agent]
description: "Codegraph Verification: zot — validating wiki claims against indexed source code symbols"
source: sources/zot/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Codegraph Verification: zot

**Date:** 2026-07-12

## Claim 1: Single static Go binary with zero runtime dependencies

- **Wiki says:** Zot is an ultra-lightweight Go coding agent harness producing a single static binary (~20MB) with zero runtime dependencies. No database required.

- **Source evidence:**
  - `go.mod` module: `github.com/patriceckhart/zot`, Go 1.22
  - `go.mod` dependencies are minimal: `chroma/v2` (syntax highlighting), `uuid`, `runewidth`, `fuzzy` (fuzzy matching), `golang.org/x/image`, `golang.org/x/sys`, `golang.org/x/term` — no databases, no large frameworks
  - `cmd/zot/main.go` — single binary entry point
  - `Makefile` has `build` target producing `./bin/zot`
  - `README.md` line 13: "one static binary"
  - No database imports in go.mod (no SQLite, Postgres, etc.)
  - Single binary build model confirmed by `go install` and `install.sh` install methods
  - `install.sh` and `install.ps1` — one-liner install scripts downloading a single binary

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: 25+ LLM providers including subscription-based and direct API access

- **Wiki says:** Zot supports 25+ LLM providers including Anthropic, OpenAI Chat/Codex/Responses, DeepSeek, Google Gemini/Vertex, GitHub Copilot, Amazon Bedrock, Azure OpenAI, Groq, Cerebras, xAI, Together AI, Hugging Face, OpenRouter, Mistral, Z.AI, Xiaomi, MiniMax, Fireworks, Vercel AI Gateway, OpenCode, Cloudflare AI, Ollama, and Kimi/Moonshot.

- **Source evidence:**
  - `packages/provider/` directory contains provider implementations with 39 files
  - Files found: `anthropic.go`, `openai.go`, `openai_codex.go`, `openai_responses.go`, `gemini.go`, `google_vertex.go`, `github_copilot.go`, `amazon_bedrock.go`, `azure_openai.go`, `provider.go`, `catalog_builtin.go`, `discover.go`, `extra_models.go`, `extra_providers.go`
  - `packages/provider/catalog_builtin.go` — built-in provider catalog
  - `packages/provider/models.go` — model definitions
  - README confirms all listed providers in "Providers" section (lines 332-339)
  - Subscription-capable providers: Anthropic Claude, OpenAI Codex/ChatGPT, Kimi Code, GitHub Copilot
  - Auth flow in `packages/provider/auth/` for OAuth and API key management
  - Local/self-hosted support via Ollama and OpenAI-compatible endpoints

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Four run modes (interactive TUI, print, JSON streaming, RPC daemon)

- **Wiki says:** Zot has four run modes: Interactive TUI (`zot`), Print mode (`zot -p`), JSON streaming (`zot --json`), and RPC daemon (`zot rpc`) for embedding in any language.

- **Source evidence:**
  - `packages/tui/` — Interactive TUI implementation with 36 files (editor, render, markdown, image support, theme, input, etc.)
  - `packages/agent/modes/` — mode-specific implementations
  - `packages/agent/rpc.go` — RPC mode implementation
  - `packages/agent/cli.go` — CLI entry with mode dispatch
  - README lines 123-134: `zot` (interactive TUI), `zot -p` (print), `zot --json` (JSON streaming), `zot rpc` (RPC daemon)
  - README lines 170-176: Full description of all four modes
  - `docs/rpc.md` — RPC wire format documentation
  - `examples/rpc/` directory with Python, Node, shell, Go reference clients
  - `packages/agent/sdk/` — Go in-process embedding SDK

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Four core tools (read, write, edit, bash) with sandbox jail mechanism

- **Wiki says:** Zot ships with four built-in tools (`read`, `write`, `edit`, `bash`) and a `/jail` sandbox that confines tools to the session cwd, blocking escape patterns.

- **Source evidence:**
  - `packages/agent/tools/` — tool implementations (read, write, edit, bash)
  - README lines 161-168: "Tools" section listing `read`, `write`, `edit`, `bash`
  - README lines 321-324: `/jail` sandbox description: "read, write, and edit resolve their target path... and refuse anything outside the sandbox. bash refuses obvious escape patterns: `sudo`, `rm -rf /`, leading `cd /`, `cd ..`, `cd ~`, `chmod -R`, `dd of=/`"
  - Jail toggle via `/jail` and `/unjail` slash commands
  - File picker (`@` key) for filesystem navigation
  - Tool rendering supports `box` and `flat` modes
  - `ZOT_FLAT_TOOLS` env var for rendering customization

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Extension system via subprocess JSON-RPC protocol

- **Wiki says:** Zot can be extended in any language via subprocess + JSON-RPC protocol. Extensions register slash commands, expose tools to the model, intercept tool calls, gate turns, and rewrite assistant output. Hot-reload with `/reload-ext`.

- **Source evidence:**
  - `packages/agent/ext/` — extension loading infrastructure
  - `packages/agent/extensions/` — extension management
  - `packages/agent/extproto/` — extension protocol definitions
  - `packages/agent/extcmd.go` — extension command handling
  - `packages/agent/extcmd_test.go` — extension tests
  - `packages/agent/extupdate.go` — extension update mechanism
  - README lines 670-702: Full extension documentation with install, list, doctor, logs, enable, disable, remove commands
  - README line 20: "extensions in any language via subprocess + json-rpc"
  - `docs/extensions.md` — extension development documentation
  - Theme-only extensions supported (README line 704)
  - Extension-registered commands appear under divider in slash command popup

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Swarm mode for multi-agent subprocess orchestration

- **Wiki says:** Zot has swarm mode with background subagents that run alongside the main session. Each is a separate zot subprocess with its own model loop, session file, and chat. Dashboard for monitoring, spawning, killing agents. Auto-swarm tool for model-driven delegation.

- **Source evidence:**
  - `packages/agent/swarm_agent.go` — swarm agent implementation
  - `packages/agent/swarm/` — swarm management
  - `packages/agent/swarm_agent_test.go` — swarm tests
  - README lines 252-296: Comprehensive `/swarm` documentation
  - Swarm dashboard with keyboard shortcuts (n, p, R, k, r, esc)
  - Auto-swarm toggle in `/settings` — main agent spawns sub-agents via built-in `swarm_spawn` tool
  - Per-agent state persistence across zot restarts via `$ZOT_HOME/swarm/agents/<id>/`
  - Session scoping: agents stamped with host session ID
  - Resumable agents via `/swarm resume`

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Built-in Telegram bot bridge

- **Wiki says:** Zot has a built-in Telegram bot with polling-based operation, per-chat queues, file upload support, and automatic token refresh.

- **Source evidence:**
  - README line 18: "built-in telegram bot"
  - README `/telegram` command: "Connect, disconnect, or show status of the Telegram bridge"
  - Telegram bridge auto-refreshes tokens once per turn for long-running bots
  - DMs from paired user become prompts; replies mirrored back to Telegram
  - Standalone daemon mode: `zot telegram --provider anthropic --model claude-opus-4-8`

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: SKILL.md support with file-based tool definitions

- **Wiki says:** Zot supports SKILL.md files for reusable instructions and collaborative workflows. Discovered at startup, hot-reloadable via `/skills` command.

- **Source evidence:**
  - `packages/agent/skills/` — skill discovery and loading
  - `packages/agent/systemprompt.go` — system prompt with skill manifest injection
  - README line 21: "reusable instructions via `SKILL.md` files; see [docs/skills.md](docs/skills.md)"
  - `docs/skills.md` — skill documentation
  - `/skills` slash command lists discovered skills with preview
  - `--no-skill` flag disables all skills
  - `$ZOT_HOME/SYSTEM.md` provides optional system prompt replacement
  - Skill system prompt addendum for auto-swarm delegation

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[zot]] -- Main wiki entry with features and architecture
- [[opencode]] — Go-based AI coding agent with multi-provider support
- [[goclaw]] — Go MCP gateway that can embed zot as RPC tool bridge

## Cross-project

- [[goclaw.codegraph-verify]] — Go MCP gateway verified
- [[opencode.codegraph-verify]] — OpenCode verified
- [[free-claude-code.codegraph-verify]] — Free tier MCP wrapper verified
