---
name: camofox-browser-architecture
tags: [camofox-browser, architecture, browser, mcp, anti-detection, automation, session-isolation]
description: Architecture of Camofox Browser — C++ anti-detection browser automation server with 11 OpenClaw plugin tools and session isolation
source: sources/camofox-browser/
---

# Camofox Browser Architecture

## Overview

Camofox Browser is an **anti-detection browser automation server** for AI agents, powered by Camoufox — a Firefox fork with C++-level fingerprint spoofing. It wraps the Camoufox engine in a REST API designed for programmatic agent use: accessibility snapshots instead of raw HTML, stable element refs for interaction, session isolation per user, and search macros for common sites. Built by AskJo.ai, it also ships as an OpenClaw MCP plugin with 11 tools.

## Architecture

```
┌────────────────────────────────────────────────────────┐
│  camofox-browser (Express server, port 9377)           │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │ Config   │  │ Auth     │  │ Launcher             │  │
│  │ env+json │  │ Bearer   │  │ Camoufox child proc  │  │
│  └──────────┘  │ 3 key    │  └──────────────────────┘  │
│                │ levels   │                            │
│  ┌──────────┐  └──────────┘  ┌──────────────────────┐  │
│  │ Plugin   │                │ Session Manager      │  │
│  │ System   │◄──────────────►│ Map<userId, Context> │  │
│  │ EventBus │                │ tabGroups, lastAccess │  │
│  └──────────┘                └──────────────────────┘  │
│                                                         │
│  ┌──────────────────┐  ┌────────────────────────┐      │
│  │ Snapshot Engine  │  │ Browser Automation      │      │
│  │ accessibility    │  │ Playwright + Camoufox   │      │
│  │ tree + refs      │  │ navigation, click, type │      │
│  └──────────────────┘  │ scroll, evaluate, etc.  │      │
│                        └────────────────────────┘      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐      │
│  │ Proxy    │  │ Cookies  │  │ Downloads        │      │
│  │ rotation │  │ Netscape │  │ capture+retrieve  │      │
│  └──────────┘  │ file     │  └──────────────────┘      │
│                └──────────┘                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐      │
│  │ Metrics  │  │ Tracing  │  │ Persistence      │      │
│  │ Prometheus│  │ Playwright│  │ CRDT + optional  │      │
│  └──────────┘  │ traces   │  │ Redis            │      │
│                └──────────┘  └──────────────────┘      │
└────────────────────────────────────────────────────────┘
        │  REST (JSON) ─── OR ─── MCP (OpenClaw plugin)
        ▼
AI Agent / OpenClaw / HTTP client
```

### Core Concepts

- **Camoufox** — Firefox fork patching fingerprint vectors at C++ level (hardwareConcurrency, WebGL renderers, AudioContext, screen geometry, WebRTC). No JavaScript shims or wrappers detectable by anti-bot systems.
- **Element Refs** — API assigns stable identifiers (`e1`, `e2`, `e3`) to interactive elements in accessibility snapshots. Agents interact via refs, which survive page changes better than CSS selectors.
- **Session Isolation** — Each `userId` gets an isolated Playwright browser context with independent cookies, storage, and proxy settings. Sessions expire after configurable timeout.
- **Search Macros** — Built-in shortcuts: `@google_search`, `@youtube_search`, `@amazon_search`, `@reddit_search`, `@wikipedia_search`, `@twitter_search`, `@yelp_search`, etc.

## Key Components

### REST API Groups

| Group | Routes | Purpose |
|-------|--------|---------|
| **System** | `GET /health`, `GET /metrics`, `GET /stop` | Health, Prometheus, graceful shutdown |
| **Tabs** | `POST /tabs`, `GET /tabs`, `DELETE /tabs/:tabId` | Tab lifecycle |
| **Navigation** | `POST /tabs/:tabId/navigate`, `back`, `forward`, `refresh` | URL navigation |
| **Interaction** | `POST /tabs/:tabId/click\|type\|scroll\|press\|evaluate` | Element interaction |
| **Content** | `GET snapshot\|screenshot\|links\|images`, `POST extract` | Page content access |
| **Sessions** | `POST sessions/:userId/cookies`, `DELETE sessions/:userId` | Session management |
| **Browser** | `POST /browser/start\|stop\|restart` | Global browser lifecycle |

### Plugin System (29 lifecycle events)

Plugins export `register(app, ctx, pluginConfig)` and hook into 7 categories: browser lifecycle (launching/launched/restart/closed), session lifecycle (creating/created/destroying/destroyed), tab lifecycle, content, input, downloads, cookies/auth, and server lifecycle. Some hooks are mutable — plugins modify options by reference before core processing.

**Built-in plugins:** youtube (transcript extraction), persistence (CRDT-based session state with optional Redis), vnc (Xvfb + x11vnc + noVNC for interactive login).

### OpenClaw MCP Plugin (11 tools)

When installed via `openclaw plugins install @askjo/camofox-browser`, registers: `camofox_create_tab`, `camofox_snapshot`, `camofox_click`, `camofox_type`, `camofox_navigate`, `camofox_scroll`, `camofox_screenshot`, `camofox_close_tab`, `camofox_evaluate`, `camofox_list_tabs`, `camofox_import_cookies`. Auto-starts the server process and proxies tool calls to the REST API.

## Related

- [[camofox-browser]] — Wiki overview of the project
- [[mcp]] — Model Context Protocol used for tool integration
- [[hermes-agent]] — Agent platform that can consume Camofox MCP tools
- [[openclaw]] — Primary MCP agent runtime hosting the Camofox plugin
- [[clawpier]] — Desktop GUI agent platform compatible with Camofox
- [[goclaw]] — Go MCP gateway that can route to Camofox
