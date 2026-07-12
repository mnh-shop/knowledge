---
name: Agent-Reach
tags: [agent-reach, agent, ai-agents, orchestration, multi-agent]
description: "Multi-agent orchestration and communication framework"
source: sources/Agent-Reach/
---

# Agent-Reach

| Field | Value |
|---|---|
| **Origin** | [Agent-Reach/Agent-Reach](https://github.com/Agent-Reach/Agent-Reach) |
| **Source** | `sources/Agent-Reach/` |
| **Repomix** | `raw/Agent-Reach/Agent-Reach.xml` |
| **Codegraph** | `graphs/Agent-Reach/` |

## Overview

Agent-Reach is a capability layer that gives AI agents read and search access to 15+ internet platforms through a unified installation, routing, and diagnostics toolchain. Rather than wrapping platform APIs behind a custom interface, Agent-Reach acts as a **glue layer**: it installs, configures, and health-checks upstream open-source CLI tools — `yt-dlp`, `twitter-cli`, `bili-cli`, `gh CLI`, `OpenCLI`, `feedparser`, and others — then lets agents call those tools directly. This design avoids the abstraction overhead and maintenance burden of a custom wrapper layer while providing zero-configuration setup, multi-backend failover routing, and a built-in diagnostic engine (`agent-reach doctor`) that reports the active backend for every platform.

The project originated to solve a practical problem: AI agents (Claude Code, OpenClaw, Cursor, Windsurf, and any agent that can run shell commands) consistently struggle with internet access because each platform has its own barrier — paid APIs, IP blocks, login requirements, and data cleaning. Agent-Reach collapses these into a single install step and ongoing maintenance that routes around platform changes automatically.

## Key Features

- **15+ Platform Support** — Twitter/X, Reddit, Facebook, Instagram, YouTube, GitHub, Bilibili, XiaoHongShu, LinkedIn, V2EX, Xueqiu, Xiaoyuzhou Podcast, RSS feeds, web search (Exa), and arbitrary web pages via Jina Reader
- **Multi-Backend Routing** — Each platform has an ordered list of candidate backends. If the primary backend fails (e.g., yt-dlp blocked by Bilibili's anti-scraping measures), the system routes to the next available backend without code changes. The `agent-reach doctor` command reports which backend is active for each platform
- **Zero API Fees** — All backends are free and open-source. The optional server proxy costs roughly $1/month
- **Self-Diagnosis** — `agent-reach doctor` probes every platform channel and reports the status of each, including which backend is currently active, what is misconfigured, and how to fix it
- **Cookie-Based Authentication** — For platforms requiring login (Twitter, XiaoHongShu, Reddit, Facebook, Instagram), the system supports browser-session reuse via OpenCLI or traditional Cookie-Editor export. Credentials are stored locally at `~/.agent-reach/config.yaml` with file permissions 600 and never transmitted
- **MCP Search Integration** — Search functionality is provided via Exa through MCP (via mcporter), with a free tier that requires no API key
- **Safe and Dry-Run Modes** — `--safe` mode prevents automatic system modifications; `--dry-run` previews all operations without making changes

## Architecture

Agent-Reach follows a channel-based architecture where each internet platform is represented by a single Python file in `agent_reach/channels/`. Each channel inherits from `BaseChannel` and implements a standard contract: `can_handle(url)`, `read(url)`, `search(query)`, and `check()` methods. The system does not wrap upstream tools — after installation and configuration, agents call the upstream CLI tools directly, with Agent-Reach serving as the installer, router, and diagnostician.

```
agent_reach/
├── cli.py           — CLI entry point (argparse)
├── core.py          — Core read/search routing logic
├── config.py        — Configuration management (YAML, environment variables)
├── doctor.py        — Diagnostics engine
├── channels/        — One file per platform
│   ├── twitter.py   → twitter-cli → OpenCLI → bird
│   ├── youtube.py   → yt-dlp
│   ├── github.py    → gh CLI
│   ├── bilibili.py  → bili-cli → OpenCLI → search API
│   ├── reddit.py    → OpenCLI → rdt-cli
│   ├── facebook.py  → OpenCLI (browser login session)
│   ├── instagram.py → OpenCLI (browser login session)
│   ├── xiaohongshu.py → OpenCLI → xiaohongshu-mcp → xhs-cli
│   ├── linkedin.py  → linkedin-mcp → Jina Reader
│   ├── web.py       → Jina Reader
│   ├── rss.py       → feedparser
│   ├── exa_search.py → Exa via mcporter
│   └── v2ex.py / xueqiu.py / xiaoyuzhou.py
├── integrations/    — MCP server integration
├── skill/           — Agent skill files for OpenClaw and other platforms
└── guides/          — Usage guides
```

The routing logic is designed for platform evolution: each channel file probes candidate backends in priority order, and the first one that passes a real functionality test (not just a "binary exists" check) is used. When a platform changes its anti-bot measures, the channel file is updated to reorder or replace backends — users detect the change via `agent-reach doctor` and remain unaffected.

## Installation

Installation is triggered by asking an AI agent to run a single command:

```
帮我安装 Agent Reach：https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
```

The agent then:
1. Installs the `agent-reach` Python package via pip (which includes yt-dlp, feedparser)
2. Detects and installs system dependencies (Node.js, gh CLI, mcporter)
3. Configures the Exa search engine through MCP (free, no API key required)
4. Detects the environment (local machine vs. server) and provides configuration guidance
5. Installs a SKILL.md in the agent's skills directory for automatic tool routing
6. Optionally configures login-required platforms interactively

Updates are equally simple — a single command triggers re-evaluation of all backends and re-installation of updated components.

## Platforms and Backend Selection

Agent-Reach maintains a curated set of backends per platform with a clear primary and fallback strategy:

| Platform | Primary Backend | Fallback | Notes |
|---|---|---|---|
| Web pages | Jina Reader | — | Free, no API key |
| YouTube | yt-dlp | — | 154K star project |
| Bilibili | bili-cli | OpenCLI | yt-dlp retired after Bilibili blocked it |
| Twitter/X | twitter-cli | OpenCLI | Cookie-based auth |
| GitHub | gh CLI | — | Official CLI tool |
| Reddit | OpenCLI | rdt-cli | Login required; anonymous API blocked |
| Web Search | Exa (via MCP) | — | AI semantic search, free tier |
| RSS | feedparser | — | Python ecosystem standard |
| LinkedIn | linkedin-mcp | Jina Reader | OAuth-based MCP server |

## Security Model

Agent-Reach takes a defense-in-depth approach to credentials:

- **Local storage only** — All cookies and tokens reside in `~/.agent-reach/config.yaml` with file permissions 600
- **Open-source transparency** — All code and dependencies are open-source and auditable
- **Safe mode** — `--safe` flag prevents automatic system-level changes
- **Dry-run** — `--dry-run` previews every operation without side effects
- **Pluggable channels** — Untrusted components can be replaced by swapping channel files

## Related

- [[hermes-agent]] — Multi-platform agent gateway that can consume Agent-Reach's installed tooling
- [[openclaw]] — Personal AI assistant that benefits from Agent-Reach's internet access capabilities
- [[turnstone]] — Self-hosted agent orchestration harness with tool-use capabilities
- [[shannon]] — AI agent runtime with multi-agent orchestration
- [[nanobot]] — Agent orchestration framework for constructing autonomous workers
- [[materia]] — Agent framework with composable pipelines that can incorporate agent reach tools
