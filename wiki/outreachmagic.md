---
name: outreachmagic
tags: [outreachmagic, skill, skills-platform, python, webhook, automation, integration]
description: "Skill suite for syncing sales sequencer webhooks (Smartlead, Instantly, HeyReach, etc.) into a local SQLite database with lead enrichment and email waterfall finder"
source: sources/outreachmagic/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Outreach Magic

| Field | Value |
|---|---|
| **Origin** | [outreachmagic/outreachmagic](https://github.com/outreachmagic/outreachmagic) |
| **Version** | 1.5.0 (`skills/outreachmagic/scripts/VERSION`) |
| **Source** | `sources/outreachmagic/` |
| **Repomix** | `raw/outreachmagic/outreachmagic.xml` |
| **Codegraph** | `graphs/outreachmagic/` |

## Overview

Outreach Magic is a skill suite that bridges sales outreach platforms with AI agents through webhook synchronization. The central insight: after sending a campaign, agents go blind. Outreach Magic fixes that by syncing every reply, bounce, click, stage change, and booked call from 8 sales sequencers (Smartlead, Instantly, HeyReach, PlusVibe, EmailBison, Prosp, MasterInbox, and Calendly) into a local SQLite database that agents can query directly.

The monorepo ships a **single skill** — `skills/outreachmagic` — containing the main `pipeline.py` with SQLite database, sync engine, campaign stats, and CRM drivers, plus the enrichment and email-finder logic **embedded** directly in its scripts (`enrich.py`, `email_finder.py`, `icypeas.py`, `millionverifier.py`). The **email-finder** and **lead-enrich** companion skills live in separate external repos and were historically installed via `install.sh --with-lead-enrich|--with-email-finder`; since v1.5.0 those flags are deprecated — "consolidated skill includes all capabilities" (install.sh:153). The single source of truth is `skill-suite.json`, which now lists one skill entry.

Outreach Magic supports multiple agent platforms including Claude Code, Cursor, and Hermes Agent. The marketing site is at [outreachmagic.io](https://outreachmagic.io) with a portal at [app.outreachmagic.io](https://app.outreachmagic.io).

## Key Features

- **Pipeline Sync** — Webhooks from 8+ sales sequencers sync to a local SQLite database. Every reply, bounce, stage change, and booked call is captured in real-time.
- **Cross-Agent Synchronization** — Events sync across multiple AI agents so no data gets lost when switching between Claude Code, Cursor, or Hermes sessions. All agents share the same database state.
- **Lead Enrichment** — Research people by name and company via Serper.dev integration. The enrichment logic (`enrich.py`) is embedded in the main skill, providing structured people intelligence.
- **Email Waterfall Finder** — Cascading email discovery and verification pipeline (trykitt → Icypeas, verify via MillionVerifier, deep-verify via Scrubby), embedded as `email_finder.py`, `icypeas.py`, and `millionverifier.py` in the main skill's scripts.
- **Cloud Relay Persistence** — Webhook events sync **down** from `api.outreachmagic.io` to the local database, while enrichment results, email finds, and pipeline state are backed **up** to the cloud in return (README.md:13-15). Nothing gets lost on either side.
- **Local Dashboard** — `dashboard.html` + `dashboard_server.py` serve a browser dashboard with per-workspace stats, campaign views, and actions backed by `dashboard_actions.py` / `dashboard_queries.py`.
- **Device-Login OAuth + Batch Jobs + Billing** — `pipeline.py login` connects via browser device auth (pipeline.py:14); batch pipeline jobs (`batch_runner.py`, `batch_sync_to_relay.py`, `pipeline.py batch_lead_lookup`) handle bulk lead uploads and relay sync; `api_key_pool.py` manages Serper credit budgets with billing via the portal at [app.outreachmagic.io](https://app.outreachmagic.io).
- **Natural Language Query Interface** — Agents can answer questions directly from the synced database: campaign stats, bounce analysis, best performing copy, deliverability insights, and detailed campaign exports.
- **CRM Sync** — Push contacts, deals, and event history to GoHighLevel and HubSpot from the pipeline database. Salesforce integration is planned.
- **Single Consolidated Skill** — `skill-suite.json` lists one skill entry (`skills/outreachmagic`); the email-finder waterfall and lead-enrich capabilities are embedded in its scripts rather than shipped as separate in-repo skills.
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
│   └── outreachmagic/          # Sole skill — pipeline.py, SQLite DB, sync, stats, CRM drivers
│       └── scripts/            # 48+ scripts — incl. embedded enrich.py, email_finder.py,
│                               # icypeas.py, millionverifier.py, dashboard_server.py
├── install.sh                  # Cross-platform installer (Hermes, Cursor, Claude Code)
├── platforms/                  # Platform overlays and install wrappers
├── brand/                      # Logo SVGs
├── scripts/                    # Dev scripts — tests, manifests, sync, release check
├── tests/                      # 157 pytest test files
├── docs/                       # Development docs — releasing, skill suite guide
└── skill-suite.json            # Single source of truth — one skill entry
```

Data flow: Sequencers send webhooks to `api.outreachmagic.io` → events are processed and stored → agents poll or query their local SQLite database → agents provide natural language answers to campaign questions.

The `email-finder` and `lead-enrich` companion skills live in **separate external repos** (`outreachmagic/email-finder`, `outreachmagic/lead-enrich`) — they are not inside this monorepo. Their logic is embedded in the main skill's scripts, and `install.sh` accepts their old `--with-lead-enrich` / `--with-email-finder` flags only to emit a deprecation warning. The monorepo's own CI (`.github/workflows/` = `release.yml`, `publish-org-profile.yml`, `skill-scan.yml`) handles releases, org-profile publishing, and skill scanning — no workflow in this repo publishes into the companion repos.

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
