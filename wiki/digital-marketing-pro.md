---
name: digital-marketing-pro
tags: [digital-marketing-pro, automation, ai-llm, marketing, seo, content-generation]
description: "AI-powered digital marketing automation platform"
source: sources/digital-marketing-pro/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Digital Marketing Pro

| Field | Value |
|---|---|
| **Origin** | [robertbretz/digital-marketing-pro](https://github.com/robertbretz/digital-marketing-pro) → maintained by [Indranil Banerjee](https://github.com/indranilbanerjee/digital-marketing-pro) |
| **Source** | `sources/digital-marketing-pro/` |
| **Repomix** | `raw/digital-marketing-pro/digital-marketing-pro.xml` |
| **Codegraph** | `graphs/digital-marketing-pro/` |

## Overview

Digital Marketing Pro (DM Pro) is an open-source AI marketing plugin shipping **158 skills, 25 specialist agents, a 12-Part Strategy Flow, and EU AI Act Article 50 readiness**. Built for marketing agencies managing 50–200 brands, in-house teams, and consultancies, it orchestrates multi-channel marketing campaigns using LLM-driven content generation, audience segmentation, and performance analytics.

The plugin installs on Claude Code, Anthropic Cowork, OpenAI Codex, Cursor 2.5+, GitHub Copilot CLI, Google Antigravity 2.0, Hermes Agent, and OpenClaw — plus 35+ additional platforms via the Agent Skills open standard. Created by [Indranil Banerjee](https://indranil.in) ([@askneelnow](https://x.com/askneelnow)), it is MIT-licensed with no telemetry and no seat fees.

DM Pro runs every brand engagement through the same **12-Part Strategy Flow**, producing ~50–60 canonical files per engagement in roughly 60 minutes on Claude Opus 4.7 at a cost of $15–40 in API spend. The methodology includes a Two-Views Model (v1 unbiased + v2 client-validated), Stone-vs-Opinion intake tagging, a Decision Matrix for selective re-runs, and a Living Project Instruction File that propagates corrections to all downstream skills.

## Key Features

- **12-Part Strategy Flow** — Canonical methodology producing the Four Core Documents across 61 explicit steps. Parts cover: Stone-vs-Opinion intake, unbiased market research, Business & SBU Analysis, Segmentation Framework, Brand Positioning, DMFlow, competitive/customer/market analysis, Client Validation, selective v2 re-runs, preparation docs, Growth Plan + Yearly Planner, channel strategy fan-out, execution artefacts, AI creative briefs, and continuous improvement.
- **158 Marketing Skills** — Comprehensive skill library covering SEO (tech audits, keyword clustering, AEO/GEO, backlink gap, content decay), content marketing (engine, briefs, repurposing), paid advertising (Google Ads, Meta Ads, campaign orchestration), social media (scheduling, content creation), email marketing (sequences, automation), analytics (attribution, performance reporting, anomaly detection), and compliance (C2PA metadata, EU AI Act, multi-jurisdiction privacy).
- **25 Specialist Agents** — Defined subagent roles for specialized marketing functions including competitor analysis, content strategy, SEO, paid media, social, analytics, compliance, and creative direction.
- **EU AI Act Article 50 Ready** — Built-in compliance infrastructure covering C2PA content provenance signing, deepfake disclosure clauses on AI creative briefs, multi-jurisdiction privacy checks (GDPR, CCPA, DPDPA, LGPD across 16 jurisdictions), and an operational readiness checklist for the August 2026 applicability date.
- **Cross-Platform Portability** — 8 native manifests (Claude Code, Cowork, Codex, Cursor, Copilot CLI, Antigravity, Hermes, OpenClaw) plus automatic compatibility with 35+ additional Agent Skills platforms including Goose, OpenHands, OpenCode, Junie, Gemini CLI, Roo Code, Mistral Vibe, and nanobot.
- **Multi-Brand Agency Support** — Per-brand state management, brand-switch workflow, agency dashboard with per-brand AI cost rollup, and team persistence via Cowork + Google Drive MCP routing.
- **Live API Execution** — 8 verified HTTP connectors executing against Slack, HubSpot, Klaviyo, SendGrid, Brevo, Customer.io, Mailchimp, and Ahrefs. 25 OAuth connectors available via MCP manifest. No third-party dependencies beyond stdlib.
- **Continuous Market Refresh** — Updated against actual ecosystem state including Google I/O releases, EU AI Act developments, Meta platform changes, model deprecations, and broad core algorithm updates. The model registry contains 47 verified entries with automatic fall-forward for deprecated model IDs.
- **Comprehensive Test Suite** — 123 passing stdlib unittest tests covering model resolution, connector execution, drive sync state, plugin metadata, skill line limits, Hermes adapter, OpenClaw manifest, and release consistency.

## Architecture

DM Pro follows a modular, pipeline-oriented architecture:

```
User Intent → Skill Router (SKILL.md directory tree) → Skill Execution → Canonical Output Files
                                                              │
                                              ┌───────────────┴───────────────┐
                                              │        Scripts Layer          │
                                              │  resolve_model.py             │
                                              │  connector_executor.py        │
                                              │  drive-sync-state.py          │
                                              │  embed-c2pa.py                │
                                              └───────────────────────────────┘
```

The project structure:

```
digital-marketing-pro/
├── skills/                    # 158 skill directories, each with SKILL.md
├── agents/                    # 25 specialist agent definitions
├── commands/                  # Claude Code slash commands
├── scripts/                   # 84 Python helpers
├── tests/                     # 123 stdlib unittest tests
├── references/                # 167 reference knowledge files
├── .claude-plugin/            # Claude Code manifest
├── .codex-plugin/             # OpenAI Codex manifest
├── .cursor-plugin/            # Cursor 2.5+ manifest
├── .github/plugin/            # GitHub Copilot CLI manifest
├── gemini-extension.json      # Google Antigravity manifest
├── plugin.yaml + __init__.py  # Hermes Agent native plugin
├── openclaw.plugin.json       # OpenClaw native manifest
└── settings.json.example      # Recommended user settings
```

Key architectural concepts:

- **Two-Views Model** — Every engagement carries v1 (unbiased market view) and v2 (client-validated view). Operating decisions reference v2; ideation references both.
- **Stone vs Opinion** — Every fact captured at intake is tagged with confidence level. "Stone" = client certainty. "Opinion" = becomes a research question.
- **Decision Matrix** — Maps client validation responses to which v1 documents need v2 re-runs, preventing over- and under-re-running.
- **Update-Back Rule** — Live operations surface corrections → source documents get versioned → Living Project Instruction File propagates changes downstream.
- **Living Project Instruction File** — Single source of truth per engagement that all skills read first.

## Usage

### Quick Start (Claude Code)

```bash
/plugin marketplace add indranilbanerjee/neels-plugins
/plugin install digital-marketing-pro@neels-plugins
```

### Non-Developer Path (Anthropic Cowork)

Open Anthropic Cowork → Settings → Plugins → Add Marketplace → paste `indranilbanerjee/neels-plugins` → Find "Digital Marketing Pro" → Install. Then ask in chat: "Let's set up a brand for ACME Corp" and "Run a full marketing engagement for ACME."

### Key Workflows

```
# New client onboarding (agency, week 1)
/digital-marketing-pro:brand-setup "ACME Corp"
/digital-marketing-pro:competitor-analysis
/digital-marketing-pro:engagement

# SEO sprint
/digital-marketing-pro:seo-plan
/digital-marketing-pro:keyword-cluster seeds.csv
/digital-marketing-pro:content-engine

# Pre-publish compliance gate
/digital-marketing-pro:check campaign.md --full
/digital-marketing-pro:c2pa-metadata hero.png

# Quarterly business review
/digital-marketing-pro:performance-report --period=Q2-2026
/digital-marketing-pro:attribution-report --period=Q2-2026
```

### Output Structure

All outputs land in `~/.claude-marketing/<brand-slug>/` organized by engagement part (01-client-inputs through 12-improvement), with the Living Project Instruction File (`PROJECT_INSTRUCTIONS.md`) as the single source of truth.

## Related

- [[outreachmagic]] — AI-powered outreach and lead generation automation for GTM sequences
- [[claude-seo]] — SEO-focused Claude Code skills and configurations
- [[ai-marketing-claude-code-skills]] — Marketing automation skills for Claude Code
- [[n8n]] — Workflow automation platform for integrating marketing pipelines
- [[hermes-agent]] — Agent platform with native plugin support for DM Pro skills
- [[openclaw]] — Rust agent platform with native DM Pro plugin manifest support
