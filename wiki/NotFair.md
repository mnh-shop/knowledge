---
name: NotFair
tags: [notfair, ai-agents, automation, workflow, intelligent-automation]
description: "AI-powered intelligent automation platform for business workflows"
source: sources/NotFair/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# NotFair

| Field | Value |
|---|---|
| **Origin** | [notfair-ai/NotFair](https://github.com/notfair-ai/NotFair) |
| **Source** | `sources/NotFair/` |
| **Repomix** | `raw/NotFair/NotFair.xml` |
| **Codegraph** | `graphs/NotFair/` |

## Overview

NotFair (formerly Toprank) is an AI-powered intelligent automation platform for digital marketing operations, delivered as a Claude Code plugin with companion MCP servers and a web application at [notfair.co](https://notfair.co). It gives AI agents direct access to Google Search Console, Google Ads, and Meta Ads (Facebook + Instagram) data, enabling automated audit, optimization, and management of advertising and SEO campaigns from within the agent's conversation.

The platform is structured as a collection of host-agnostic skills — skill definitions that work identically across Claude Code, Codex, Hermes, and other AI coding agents. Each skill is a `SKILL.md` file accompanied by reference documents, optional scripts, and eval tests. The companion web app shares the same engine, so audits run from the CLI produce identical results to those run through the browser UI.

What distinguishes NotFair from traditional ad management tools is its **agent-native architecture**: rather than providing yet another dashboard with charts and filters, NotFair presents actionable insights directly in the conversational interface, allowing the agent to both identify problems and execute fixes — pausing wasteful campaigns, adding negative keywords, adjusting bids, or rewriting SEO meta tags — all through the same chat session.

## Key Features

- **Google Ads Management** — Full account audit scoring 7 health dimensions (conversion tracking, keyword health, search term quality, impression share, spend efficiency), campaign management including bid/budget adjustments, keyword and negative keyword management, RSA copy generation with A/B testing, and landing page quality scoring
- **Meta Ads Management** — Account audit tuned for Meta's platform with Pixel and CAPI health, attribution, campaign structure, creative health, audience strategy, spend efficiency, and scaling readiness. Supports ROAS analysis, creative fatigue diagnosis, Learning Phase triage, and audience overlap detection
- **SEO Audit Suite** — Full-site SEO analysis using Google Search Console data, keyword research with intent classification and topic clusters, content creation following E-E-A-T guidelines, meta tag optimization with CTR estimates, JSON-LD structured data generation (FAQ, HowTo, Article, Product, LocalBusiness), and broken link scanning
- **Generative Engine Optimization (GEO)** — The `geo-optimizer` skill audits content with a 0–100 GEO Score, rewrites for AI citation across ChatGPT, Claude, Perplexity, Gemini, and Google AI Overviews, and produces per-engine optimization strategies
- **Cross-Model Review** — A Gemini-powered second-opinion skill that can review decisions (pass/fail gate), challenge proposals (adversarial stress test), or provide open consultation, with particular strength in Google Ads and SEO decisions
- **MCP Server Architecture** — All major capabilities are exposed as standalone MCP servers over streamable HTTP: `NotFair-GoogleAds` (~100 tools), `NotFair-MetaAds` (focused marketing API surface), and `NotFair-SearchConsole`. These servers can be used from any MCP client without installing the CLI plugin
- **Weekly Review Pattern** — Agents can score every recent campaign change (wins, losses, too-new-to-judge) for recurring Monday-morning review workflows

## Architecture

NotFair is structured as a Claude Code plugin with host-agnostic skills. The top-level layout separates marketing channels into category directories, each containing one or more skill subdirectories:

```
notfair/
├── .claude-plugin/       — Plugin metadata, marketplace registration
├── .mcp.json             — Auto-configured MCP server definitions
├── google-ads/
│   ├── audit/            — Account audit + business context (run first)
│   ├── manage/           — Campaign management + weekly reviews
│   ├── copy/             — RSA copy generator + A/B testing
│   └── landing/          — Landing page quality scoring
├── meta-ads/
│   ├── audit/            — Meta-specific account audit
│   ├── manage/           — Campaign management (ROAS, creative fatigue)
│   └── shared/           — Preamble, math, policy registry
├── seo/
│   ├── seo-analysis/     — Full SEO audit with GSC data
│   ├── content-writer/   — E-E-A-T content creation
│   ├── keyword-research/ — Keyword discovery + topic clusters
│   ├── meta-tags-optimizer/ — Title tags, meta descriptions, OG
│   ├── schema-markup-generator/ — JSON-LD structured data
│   ├── seo-page/         — Per-URL deep analysis
│   ├── broken-link-checker/ — 404/5xx scanner
│   ├── geo-optimizer/    — GENERATIVE ENGINE OPTIMIZATION
│   └── setup-cms/        — WordPress, Strapi, Contentful, Ghost connectors
├── gemini/               — Cross-model review via Gemini CLI
├── notfair-upgrade-skill/ — Self-updater
└── VERSION               — Current: 0.25.6
```

Skills use a connector placeholder pattern (`~~category`) to remain tool-agnostic — they work with any MCP server providing the required capability. If a connector is unavailable, skills degrade gracefully (e.g., SEO analysis can run a technical crawl without GSC data).

The MCP servers are registered natively in `.mcp.json` as streamable HTTP servers at `https://notfair.co/api/mcp/`. Authentication uses OAuth 2.1 with dynamic client registration — on first connection, Claude Code opens a browser for sign-in at notfair.co, and the resulting token is stored in the OS keychain.

## Connector Architecture

NotFair's skill system uses a category-based tool resolution pattern:

| Category | Placeholder | Default Server | Degradation |
|---|---|---|---|
| Google Ads | `~~google-ads` | NotFair-GoogleAds MCP | Falls back to any Google Ads MCP |
| Meta Ads | `~~meta-ads` | NotFair-MetaAds MCP | Falls back to any Meta Marketing API MCP |
| Search Console | `~~search-console` | NotFair-SearchConsole MCP | Technical crawl only (no GSC data) |
| CMS | `~~cms` | Direct API (WordPress, Strapi, etc.) | — |

## Installation

Installation is a two-command process in Claude Code:

```
/plugin marketplace add nowork-studio/notfair
/plugin install notfair@nowork-studio
```

All skills are then available as `/notfair:*` commands. Google Ads and Meta Ads MCP servers authenticate via OAuth on first use. The plugin was renamed from `toprank@nowork-studio` in v0.24.0, with preserved runtime state directory for backward compatibility.

## Related

- [[openclaw]] — Personal AI agent platform with complementary workflow capabilities that can integrate NotFair-style marketing skills
- [[n8n]] — Open-source workflow automation platform, a general-purpose alternative for deterministic automation pipelines
- [[hermes-agent]] — Multi-platform agent gateway with skill-based execution that can consume NotFair MCP servers
- [[nanobot]] — Agent orchestration framework for constructing autonomous marketing and analysis workers
- [[outreachmagic]] — AI-powered outreach automation, complementary to NotFair's ad management focus
- [[openai-skills]] — Another skill collection for AI agent platforms, similar host-agnostic pattern
