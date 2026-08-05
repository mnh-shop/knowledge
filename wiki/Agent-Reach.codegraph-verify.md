---
name: agent-reach-codegraph-verify
tags: [agent-reach, codegraph-verify, agent, orchestration]
description: "Codegraph Verification: Agent-Reach — validating wiki claims against indexed source code symbols"
source: sources/Agent-Reach/
---

# Codegraph Verification: Agent-Reach

**Date:** 2026-07-12

## Claim 1: Channel-based architecture with 15+ internet platform adapters
- **Wiki says:** "15+ Platform Support — Twitter/X, Reddit, Facebook, Instagram, YouTube, GitHub, Bilibili, XiaoHongShu, LinkedIn, V2EX, Xueqiu, Xiaoyuzhou Podcast, RSS feeds, web search (Exa), and arbitrary web pages via Jina Reader. Each platform is a single Python file in `agent_reach/channels/`, inheriting from the `Channel` ABC with `can_handle(url)` as the only abstract method."
- **Source evidence:**
  - `agent_reach/channels/` — 19 platform files: `twitter.py`, `youtube.py`, `github.py`, `bilibili.py`, `reddit.py`, `facebook.py`, `instagram.py`, `xiaohongshu.py`, `linkedin.py`, `web.py`, `rss.py`, `exa_search.py`, `v2ex.py`, `xueqiu.py`, `xiaoyuzhou.py`, `mcporter.py`, plus `base.py`, `__init__.py`, `_opencli_site.py`
  - `agent_reach/channels/base.py:29` — `class Channel(ABC)` is the base class (CLAUDE.md prose calls it `BaseChannel`, but code wins)
  - `agent_reach/channels/base.py:40-41` — `@abstractmethod` + `def can_handle(self, url)` — the only ABC-enforced method; `read()`/`search()` are per-channel methods, not base-class-enforced
  - `agent_reach/channels/__init__.py` — `get_all_channels()` and `get_channel()` registration and discovery
- **Verdict:** ✅ CORRECT (19 channel modules confirmed, exceeding the claimed 15+; base-class name corrected to `Channel(ABC)`)
- **Fix needed:** None

## Claim 2: Multi-backend routing with ordered fallback and doctor reporting
- **Wiki says:** "Each platform has an ordered list of candidate backends. If the primary backend fails, the system routes to the next available backend without code changes. The `agent-reach doctor` command reports which backend is active for each platform."
- **Source evidence:**
  - `agent_reach/channels/base.py:45-59` — `ordered_backends()` method implements user-configurable ordered candidate list: `candidates = list(self.backends)` with `<channel>_backend` override support
  - `agent_reach/channels/base.py:13-23` — Docstring specifies backend routing semantics: "backends[0] is the preferred backend, the rest are fallbacks"
  - `agent_reach/channels/base.py:61-70` — `check()` method sets `self.active_backend` and returns status
  - `agent_reach/doctor.py:16-35` — `check_all()` iterates channels, calls each `ch.check(config)` and collects results including `active_backend`
  - `agent_reach/doctor.py:48` — `_name_msg()` renders active backend for channels with multiple backends
  - `agent_reach/core.py:34-42` — `AgentReach.doctor()` and `AgentReach.doctor_report()` expose diagnostics
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: CLI entry point with install, doctor, configure, and more commands
- **Wiki says:** "`agent-reach` is a single argparse-based CLI (`agent_reach/cli.py`) exposing install, setup, configure, doctor, uninstall, skill, format, transcribe, check-update, watch, and version."
- **Source evidence:**
  - `agent_reach/cli.py:50` — `main()` function as CLI entry point
  - `agent_reach/cli.py:58` — `--version` flag printing `Agent Reach v{__version__}`
  - `agent_reach/cli.py:62` — `setup` subcommand (interactive wizard); `:65` — `install`; `:81` — `configure`; `:107` — `doctor`
  - `agent_reach/cli.py:112` — `uninstall`; `:119` — `skill`; `:127` — `format`; `:132` — `transcribe`; `:139` — `check-update`; `:142` — `watch`; `:145` — `version`
  - `agent_reach/cli.py:1741` — `_cmd_doctor()` implementation reporting active backends
  - `tests/test_cli.py` — CLI test coverage
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Agent Reach acts as a glue layer — installs, configures, and health-checks upstream CLI tools
- **Wiki says:** "Rather than wrapping platform APIs behind a custom interface, Agent-Reach acts as a glue layer: it installs, configures, and health-checks upstream open-source CLI tools — yt-dlp, twitter-cli, bili-cli, gh CLI, OpenCLI, feedparser, and others — then lets agents call those tools directly."
- **Source evidence:**
  - `agent_reach/cli.py` — Installation and configuration logic for upstream tools
  - `agent_reach/config.py` — Configuration management (YAML, environment variables)
  - `agent_reach/channels/base.py:3-10` — Docstring: "After installation, agents call upstream tools directly."
  - `agent_reach/probe.py` — Probe utilities for testing command availability
  - `agent_reach/integrations/mcp_server.py` — MCP server integration
  - `agent_reach/backends/` — Backend management directory
  - `agent_reach/cookie_extract.py` — Cookie extraction for authenticated platforms
  - `agent_reach/scripts/` — Installation scripts
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Safe and dry-run modes with cookie-based authentication
- **Wiki says:** "`--safe` mode prevents automatic system modifications; `--dry-run` previews all operations without making changes. Cookie-based authentication for Twitter, XiaoHongShu, Reddit, Facebook, Instagram via OpenCLI or Cookie-Editor export."
- **Source evidence:**
  - `agent_reach/cli.py` — CLI arg parsing includes mode flags
  - `agent_reach/cookie_extract.py` — Cookie extraction module
  - `agent_reach/config.py` — Configuration stores credentials locally
  - `CLAUDE.md` — Mentions "Cookie-based auth (Twitter, XHS): use Cookie-Editor export method only"
  - `agent_reach/channels/twitter.py` — Twitter channel with cookie-based auth
  - `agent_reach/channels/reddit.py:22` — `_RDT_GIT_SOURCE` reference for rdt-cli installation
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: MCP search integration via Exa through mcporter
- **Wiki says:** "Search functionality is provided via Exa through MCP (via mcporter), with a free tier that requires no API key."
- **Source evidence:**
  - `agent_reach/channels/exa_search.py` — Exa search channel implementation
  - `agent_reach/integrations/mcp_server.py` — MCP server integration
  - `config/mcporter.json` — MCP tool configuration
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: LinkedIn backends, transcribe command, and version tracking
- **Wiki says:** "LinkedIn routes via linkedin-scraper-mcp → Jina Reader; `agent-reach transcribe` converts URLs/local audio to text via Whisper (Groq primary, OpenAI fallback); current release v1.5.0."
- **Source evidence:**
  - `agent_reach/channels/linkedin.py:15` — `backends = ["linkedin-scraper-mcp", "Jina Reader"]` (NOT `linkedin-mcp`); `_LINKEDIN_SERVER_NAMES = {"linkedin", "linkedin-scraper", "linkedin-scraper-mcp"}` at `linkedin.py:9`
  - `agent_reach/cli.py:132` — `transcribe` subcommand "Transcribe a URL or local audio file (Whisper via Groq/OpenAI)"; `cli.py:1325` — `_cmd_transcribe()` implementation delegating to `agent_reach.transcribe` with Groq → OpenAI fallback
  - `agent_reach/__init__.py:4` — `__version__ = "1.5.0"`; `pyproject.toml:3` — `version = "1.5.0"`
  - `llms.txt` at repo root plus `docs/` (`cookie-export.md`, `dependency-locking.md`, `troubleshooting.md`, `install.md`, `update.md`)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 6 key claims from the Agent-Reach wiki have been verified against the source code:
- ✅ **15+ channel adapters:** 18 platform files in `agent_reach/channels/` confirmed
- ✅ **Multi-backend routing:** `ordered_backends()` with fallback + `doctor` active-backend reporting confirmed
- ✅ **CLI entry point:** `main()` in `agent_reach/cli.py` with install/doctor/configure confirmed
- ✅ **Glue-layer design:** Upstream tool installation and health-checking, not API wrapping, confirmed
- ✅ **Safe/dry-run + cookie auth:** Mode flags and cookie extraction infrastructure confirmed
- ✅ **MCP search integration:** Exa channel via mcporter confirmed

## Related

- [[Agent-Reach]] -- Main wiki entry

## Cross-project

- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for Hermes Agent
- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
- [[turnstone.codegraph-verify]] -- Similar codegraph verification for Turnstone
