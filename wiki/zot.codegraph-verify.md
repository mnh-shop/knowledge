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
  - `go.mod:1` module: `github.com/patriceckhart/zot`, `go.mod:3` — `go 1.25.0`
  - `README.md:9` — Go version badge: "Go 1.25+"
  - `go.mod` dependencies are minimal: `chroma/v2` (syntax highlighting), `uuid`, `runewidth`, `fuzzy` (fuzzy matching), `golang.org/x/image`, `golang.org/x/sys`, `golang.org/x/term` — no databases, no large frameworks
  - `cmd/zot/main.go` — single binary entry point
  - `Makefile:8-9` — `build:` target producing `./bin/zot`
  - `README.md:20` — "one static binary"
  - No database imports in go.mod (no SQLite, Postgres, etc.)
  - Single binary build model confirmed by `go install` and `install.sh` install methods
  - `install.sh` and `install.ps1` — one-liner install scripts downloading a single binary

- **Verdict:** ✅ CORRECT
- **Fix needed:** Go version corrected from "Go 1.22" to **Go 1.25.0** (`go.mod:3`, README badge "Go 1.25+").

## Claim 2: 25+ LLM providers including subscription-based and direct API access

- **Wiki says:** Zot supports 25+ LLM providers including Anthropic, OpenAI Chat/Codex/Responses, DeepSeek, Google Gemini/Vertex, GitHub Copilot, Amazon Bedrock, Azure OpenAI, Groq, Cerebras, xAI, Together AI, Hugging Face, OpenRouter, Mistral, Z.AI, Xiaomi, MiniMax, Fireworks, Vercel AI Gateway, OpenCode, Cloudflare AI, Ollama, and Kimi/Moonshot.

- **Source evidence:**
  - `packages/provider/` directory contains provider implementations with 45 `.go` files
  - Files found: `anthropic.go`, `openai.go`, `openai_codex.go`, `openai_responses.go`, `gemini.go`, `google_vertex.go`, `github_copilot.go`, `amazon_bedrock.go`, `azure_openai.go`, `llamacpp.go`, `model_router.go`, `provider.go`, `catalog_builtin.go`, `discover.go`, `extra_models.go`, `extra_providers.go`
  - `packages/provider/catalog_builtin.go` — built-in provider catalog
  - `packages/provider/models.go` — model definitions
  - README badge (line 10): "30+ providers"; README line 21 lists providers; README lines 415-416 document the "Providers" catalog split into subscription-capable, direct API, cloud/platform, and local/compatible providers
  - Subscription-capable providers: Anthropic Claude, OpenAI Codex/ChatGPT, Kimi Code, GitHub Copilot, xAI SuperGrok/X Premium
  - Auth flow in `packages/provider/auth/` for OAuth and API key management
  - Local/self-hosted support via Ollama and OpenAI-compatible endpoints (`--base-url`), llama.cpp router mode

- **Verdict:** ✅ CORRECT
- **Fix needed:** Provider count updated to **30+** (README badge), catalog taxonomy cited.

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
  - `packages/agent/tools/` — tool implementations: `read.go`, `write.go`, `edit.go`, `bash.go`, `sandbox.go`, `permissions.go`, `swarm_spawn.go`, `telegram_send.go`
  - README "Tools" section listing `read`, `write`, `edit`, `bash` (line 21: "four tools (read, write, edit, bash)")
  - README lines 402-404: `/jail` sandbox description: "`read`, `write`, and `edit` resolve their target path (including through symlinks) and refuse anything outside the sandbox. `bash` refuses obvious escape patterns (`sudo`, `rm -rf /`, leading `cd /`, `cd ..`, `cd ~`, `chmod -R`, `dd of=/`, and similar)" — plus "This is a guardrail against accidents, not a hard security boundary"
  - `packages/agent/tools/sandbox.go:56` — `"jailed: path %q is outside sandbox root %q (use /unjail to disable)"`; `:119` — `"jailed: command contains banned pattern %q (use /unjail to disable)"`; `:294` — `"jailed: cd outside sandbox root is not allowed (use /unjail to disable)"`
  - README:382 — `jail_by_default` setting: "start every new agent with tools confined to its working directory. Off by default. The setting applies to interactive, print, JSON, RPC, and background-agent runs, persists as `jail_by_default`"
  - Jail toggle via `/jail` and `/unjail` slash commands
  - File picker (`@` key) for filesystem navigation
  - Tool rendering supports `box` and `flat` modes
  - `ZOT_FLAT_TOOLS` env var for rendering customization

- **Verdict:** ✅ CORRECT
- **Fix needed:** Added `jail_by_default` setting + exact `sandbox.go` line evidence.

## Claim 5: Extension system via subprocess JSON-RPC protocol

- **Wiki says:** Zot can be extended in any language via subprocess + JSON-RPC protocol. Extensions register slash commands, expose tools to the model, intercept tool calls, gate turns, and rewrite assistant output. Hot-reload with `/reload-ext`.

- **Source evidence:**
  - `packages/agent/ext/` — extension loading infrastructure
  - `packages/agent/extensions/` — extension management (`manager`, `events`, `tool`, `proc`)
  - `packages/agent/extproto/` — extension protocol definitions
  - `packages/agent/extcmd.go:35` — `case "doctor":` and `:182` — "zot extension doctor" help text; `zot ext doctor` diagnoses load, registration, and conflict issues
  - `packages/agent/extcmd_test.go` — extension tests
  - `packages/agent/extupdate.go` — extension update mechanism
  - README:887 — "zot can be extended in any language via a subprocess + JSON-RPC protocol. Extensions can register slash commands, expose tools to the model, intercept tool calls (block or rewrite args), gate whole turns before the model is called, and rewrite the assistant's visible text before it reaches the user… Hot-reload any time with `/reload-ext`."
  - README extension management section: install, list, doctor, logs, enable, disable, remove commands
  - `docs/extensions.md` — extension development documentation
  - Theme-only extensions supported
  - Extension-registered commands appear under divider in slash command popup

- **Verdict:** ✅ CORRECT
- **Fix needed:** Added `zot ext doctor` (`extcmd.go:35`) and README:887 JSON-RPC evidence.

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
  - `packages/agent/skills/` — skill discovery and loading (`skills.go`, `builtin/`, `invocation.go`, `tool.go`)
  - `docs/skills.md:2-4` — "A skill is a reusable instruction set written as a single `SKILL.md` file with a YAML frontmatter header"; model invocation via a built-in `skill` tool loads the full body on demand
  - `examples/skills/` — bundled skill pack (`code-review`, `test-fix`)
  - `docs/superpowers/` — superpowers-style planning pack (`plans/`, `specs/` with dated design + plan docs)
  - `packages/agent/systemprompt.go` — system prompt with skill manifest injection
  - README line 21: "reusable instructions via `SKILL.md` files; see [docs/skills.md](docs/skills.md)"
  - `/skills` slash command lists discovered skills with preview
  - `--no-skill` flag disables all skills
  - `$ZOT_HOME/SYSTEM.md` provides optional system prompt replacement
  - Skill system prompt addendum for auto-swarm delegation

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 9: Zotfiles — portable agent packages (.zot files) with GitHub download support

- **Wiki says:** Zot ships portable agent packages (`.zot` files) bundling instructions, skills, assets, and metadata; run local dirs/archives or agent directories straight from GitHub without cloning.

- **Source evidence:**
  - `docs/zotfiles.md:1` — "A zotfile packages an agent's behavior into one portable `.zot` file. It can contain the agent's instructions, reusable skills, static assets, and metadata describing the runtime, model, operating-system, binary, and tool permissions it needs."
  - `docs/zotfiles.md:5` — "The current implementation supports creating, inspecting, verifying, and running local directories and `.zot` archives. It can also run an agent directory directly from a public GitHub repository without keeping a clone. Short names resolve local-first and then fall back to zot's official GitHub agent collection."
  - `docs/zotfiles.md:497-514` — accepted references: local paths, archives, short names, and "public GitHub agent-directory URLs"; GitHub downloads the repo archive to a temp dir, selects the agent subdirectory, validates and runs it, then removes the download
  - Manifest schema includes `zotfile`, `runtime.min_zot`, `model`, `permissions.fs/bash`, `requirements.os`, and `entry` (example at `docs/zotfiles.md:19-44`)
  - README "zotfile agents" section (following the Modes section at README:240)

- **Verdict:** ✅ CORRECT
- **Fix needed:** None (new claim added from `docs/zotfiles.md`)

## Claim 10: User/extension JSON themes and the `--no-yolo` per-tool confirmation gate

- **Wiki says:** Zot supports JSON theme files (user `$ZOT_HOME/themes/*.json` or bundled with extensions) overriding any subset of the built-in light/dark TUI theme, and a `--no-yolo` tool gate that confirms every tool call before it runs.

- **Source evidence:**
  - `docs/themes.md:1-2` — "zot themes are JSON files that override any subset of the built-in light/dark TUI theme. Nothing is required: a theme can change one color, only the spinner, only syntax highlighting, or all of them."
  - `docs/themes.md:9-11` — "User themes are discovered from: `$ZOT_HOME/themes/*.json`"; switch via `/settings` → "color theme", saved in `$ZOT_HOME/config.json`; extension-bundled themes discovered in-place from loaded extension directories
  - README:222 — `--no-yolo`: "Confirm every tool call before it runs (interactive TUI only). A dialog shows the tool name and a one-line preview of its args, while edit calls show the proposed diff in the tool panel, with four choices: yes, yes-always-this-tool-this-session, yes-always-this-session, no… Ignored with a stderr warning in print / json / rpc modes"
  - README:382 — `jail_by_default` setting (see Claim 4)

- **Verdict:** ✅ CORRECT
- **Fix needed:** None (new claims added from `docs/themes.md` and `README.md:222`)

## Related

- [[zot]] -- Main wiki entry with features and architecture
- [[opencode]] — Go-based AI coding agent with multi-provider support
- [[goclaw]] — Go MCP gateway that can embed zot as RPC tool bridge

## Cross-project

- [[goclaw.codegraph-verify]] — Go MCP gateway verified
- [[opencode.codegraph-verify]] — OpenCode verified
- [[free-claude-code.codegraph-verify]] — Free tier MCP wrapper verified
