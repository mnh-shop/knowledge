---
name: outreachmagic
tags: [outreachmagic, skill, skills-platform, python, webhook, automation, integration]
description: "Skill suite for syncing sales sequencer webhooks (Smartlead, Instantly, HeyReach, etc.) into a local SQLite database with lead enrichment and email waterfall finder"
source: sources/outreachmagic/
---

# Outreach Magic

| Field | Value |
|---|---|
| **Origin** | [outreachmagic/outreachmagic](https://github.com/outreachmagic/outreachmagic) |
| **Source** | `sources/outreachmagic/` |
| **Repomix** | `raw/outreachmagic/outreachmagic.xml` |
| **Codegraph** | `graphs/outreachmagic/` |

## Overview

Outreach Magic is a skill suite that bridges sales outreach platforms with AI agents through webhook synchronization. The central insight: after sending a campaign, agents go blind. Outreach Magic fixes that by syncing every reply, bounce, click, stage change, and booked call from 8 sales sequencers (Smartlead, Instantly, HeyReach, PlusVibe, EmailBison, Prosp, MasterInbox, and Calendly) into a local SQLite database that agents can query directly.

The project ships as three companion skills: the main **outreachmagic** skill (pipeline.py with SQLite database, sync engine, campaign stats, and CRM drivers), the **email-finder** skill (waterfall email find + verify through trykitt, Icypeas, MillionVerifier, Scrubby), and the **lead-enrich** skill (people research by name/company via Serper.dev). The single source of truth is `skill-suite.json`, which defines install pins and manifest file lists.

Outreach Magic supports multiple agent platforms including Claude Code, Cursor, and Hermes Agent. The marketing site is at [outreachmagic.io](https://outreachmagic.io) with a portal at [app.outreachmagic.io](https://app.outreachmagic.io).

## Key Features

- **Pipeline Sync** — Webhooks from 8+ sales sequencers sync to a local SQLite database. Every reply, bounce, stage change, and booked call is captured in real-time.
- **Cross-Agent Synchronization** — Events sync across multiple AI agents so no data gets lost when switching between Claude Code, Cursor, or Hermes sessions. All agents share the same database state.
- **Lead Enrichment** — Research people by name and company via Serper.dev integration. The `lead-enrich` companion skill provides structured people intelligence.
- **Email Waterfall Finder** — Cascading email discovery and verification pipeline through trykitt, Icypeas, MillionVerifier, and Scrubby APIs. The `email-finder` companion skill handles progressive fallback through multiple email discovery services.
- **Natural Language Query Interface** — Agents can answer questions directly from the synced database: campaign stats, bounce analysis, best performing copy, deliverability insights, and detailed campaign exports.
- **CRM Sync** — Push contacts, deals, and event history to GoHighLevel and HubSpot from the pipeline database. Salesforce integration is planned.
- **Modular Companion Skills** — Three independently installable skills that work standalone or paired for enhanced deduplication and persistent storage.
- **Platform Flexibility** — Works across Claude Code, Cursor, and Hermes Agent with a universal install flow via `npx skills add outreachmagic/outreachmagic`.

## Architecture

Outreach Magic follows a webhook-to-local-database architecture:

```
Sequencer webhooks → api.outreachmagic.io → Your agent's local SQLite database → Query responses
                              ↑  ▲
                              │  │
            Cross-agent sync ensures no data is lost
```

The system components:

```
outreachmagic/
├── skills/
│   ├── outreachmagic/          # Main skill — pipeline.py, SQLite DB, sync, stats, CRM drivers
│   ├── email-finder/           # Email waterfall companion — trykitt, Icypeas, Scrubby
│   └── lead-enrich/            # Lead research companion — Serper.dev
├── install.sh                  # Cross-platform installer (Hermes, Cursor, Claude Code)
├── platforms/                  # Platform overlays and install wrappers
├── brand/                      # Logo SVGs
├── scripts/                    # Dev scripts — tests, manifests, sync, release check
├── tests/                      # pytest suite
├── docs/                       # Development docs — releasing, skill suite guide
└── skill-suite.json            # Single source of truth — install pins, manifest file lists
```

Data flow: Sequencers send webhooks to `api.outreachmagic.io` → events are processed and stored → agents poll or query their local SQLite database → agents provide natural language answers to campaign questions.

The companion repos (`outreachmagic/email-finder` and `outreachmagic/lead-enrich`) are read-only mirrors published by CI from the main monorepo. Development and all source code lives in the outreachmagic/outreachmagic monorepo.

## Usage

### Quick Start

```bash
npx skills add outreachmagic/outreachmagic
```

Or via agent prompt:

```
Fetch this file and follow its instructions to install the Outreach Magic skill suite on this machine:
https://raw.githubusercontent.com/outreachmagic/outreachmagic/main/AGENTS-INSTALL.md
```

### Example Prompts

Once installed, try these natural language queries:

```
Use outreach magic skill suite to show me the best performing copy
Use outreach magic skill suite to find job title, linkedin + email for Bill Smith at Acme Corp
Use outreach magic skill suite to analyse my most recent bounces for deliverability insights
Use outreach magic skill suite to do a detailed campaign stats export to Google Sheets
Tell me everything the outreach magic skill suite can do in natural language with example prompts
```

### Requirements

| Key | For | Required? |
|-----|-----|-----------|
| OM account | Portal access, billing, webhook URLs | Yes |
| Sequencer webhooks | Smartlead, Instantly, HeyReach, etc. | At least one |
| Companion API keys | Lead enrichment (Serper), email finder (trykitt, Icypeas, MillionVerifier, Scrubby) | When using those features |

### Development

```bash
git clone https://github.com/outreachmagic/outreachmagic
cd outreachmagic
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
bash scripts/run-tests.sh
make manifests
```

## Related

- [[hermes-agent]] — Skills system hosts the Outreach Magic skill suite
- [[n8n]] — Workflow automation for GTM sequences and CRM pipeline integrations
- [[agentfield]] — Multi-agent orchestration platform that can leverage Outreach Magic data
- [[claude-seo]] — SEO skills for Claude Code (complementary marketing automation)
- [[digital-marketing-pro]] — Multi-platform marketing automation with cross-channel campaigns
- [[ai-marketing-claude-code-skills]] — AI marketing skills collection for content and outreach
