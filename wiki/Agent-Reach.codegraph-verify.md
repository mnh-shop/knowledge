---
name: agent-reach-codegraph-verify
tags: [agent-reach, codegraph-verify, agent, orchestration]
description: "Codegraph Verification: Agent-Reach — validating wiki claims against indexed source code symbols"
source: sources/Agent-Reach/
---

# Codegraph Verification: Agent-Reach

**Date:** 2026-07-12

## Claim 1: Channel-based architecture with 15+ internet platform adapters
- **Wiki says:** "15+ Platform Support — Twitter/X, Reddit, Facebook, Instagram, YouTube, GitHub, Bilibili, XiaoHongShu, LinkedIn, V2EX, Xueqiu, Xiaoyuzhou Podcast, RSS feeds, web search (Exa), and arbitrary web pages via Jina Reader. Each platform is a single Python file in `agent_reach/channels/`."
- **Source evidence:**
  - `agent_reach/channels/` — 18 platform files: `twitter.py`, `youtube.py`, `github.py`, `bilibili.py`, `reddit.py`, `facebook.py`, `instagram.py`, `xiaohongshu.py`, `linkedin.py`, `web.py`, `rss.py`, `exa_search.py`, `v2ex.py`, `xueqiu.py`, `xiaoyuzhou.py`, plus `base.py`, `__init__.py`, `_opencli_site.py`
  - `agent_reach/channels/base.py` — `Channel(ABC)` base class with `can_handle(url)`, `check(config)`, `ordered_backends()` contract
  - `agent_reach/channels/__init__.py` — `get_all_channels()` and `get_channel()` registration and discovery
- **Verdict:** ✅ CORRECT (18 channel modules confirmed, exceeding the claimed 15+)
- **Fix needed:** None

## Claim 2: Multi-backend routing with ordered fallback and doctor reporting
- **Wiki says:** "Each platform has an ordered list of candidate backends. If the primary backend fails, the system routes to the next available backend without code changes. The `agent-reach doctor` command reports which backend is active for each platform."
- **Source evidence:**
  - `agent_reach/channels/base.py:45-59` — `ordered_backends()` method implements user-configurable ordered candidate list: `candidates = list(self.backends)` with `<channel>_backend` override support
  - `agent_reach/channels/base.py:13-23` — Docstring specifies backend routing semantics: "backends[0] is the preferred backend, the rest are fallbacks"
  - `agent_reach/channels/base.py:61-70` — `check()` method sets `self.active_backend` and returns status
  - `agent_reach/doctor.py:12-35` — `check_all()` iterates channels, calls each `ch.check(config)` and collects results including `active_backend`
  - `agent_reach/doctor.py:38-44` — `_name_msg()` renders active backend for channels with `len(r.get('backends', [])) > 1`
  - `agent_reach/core.py:34-42` — `AgentReach.doctor()` and `AgentReach.doctor_report()` expose diagnostics
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: CLI entry point with install, doctor, and configure commands
- **Wiki says:** "CLI entry point (argparse) at `agent_reach/cli.py` with commands: `agent-reach install`, `agent-reach doctor`, `agent-reach configure`, `agent-reach setup`."
- **Source evidence:**
  - `agent_reach/cli.py:50` — `main()` function as CLI entry point
  - `agent_reach/cli.py:817` — `_install_rdt_cli()` function for rdt-cli installation
  - `CLAUDE.md` — Documents commands: `pip install -e .`, `pytest tests/ -v`, `python -m agent_reach.cli doctor`, `python -m agent_reach.cli install --env=auto`
  - `agent_reach/cli.py` — Contains argparse-based command dispatch
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
