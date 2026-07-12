---
name: outreachmagic
tags: [outreachmagic, skill, skills-platform, python, webhook, automation, integration]
description: "Skill suite for syncing sales sequencer webhooks (Smartlead, Instantly, HeyReach, etc.) into a local SQLite database with lead enrichment and email waterfall finder"
source: sources/outreachmagic/
---

# Outreach Magic

A skill suite that bridges sales outreach platforms with AI agents through webhook synchronization. Syncs Smartlead, Instantly, HeyReach, PlusVibe, EmailBison, Prosp, and Calendly into a local SQLite database your agent can query directly.

## What It Does

Your agent goes blind after send. Outreach Magic fixes that by syncing every reply, bounce, click, stage change, and booked call from sales sequencers into a local database. No CSV stitching, no blind spots — webhooks flow to `api.outreachmagic.io`, then sync to your agent.

## Key Features

- **Pipeline sync** — Webhooks from 7+ sequencers sync to local SQLite database
- **Lead enrichment** — Research people by name/company via Serper.dev integration
- **Email waterfall finder** — Find and verify work emails via trykitt, Icypeas, MillionVerifier, Scrubby
- **Cross-agent sync** — Events sync across multiple agents so nothing gets lost
- **Query interface** — Ask for campaign stats, bounce analysis, best performing copy directly

## Skills Included

| Skill | Purpose |
|-------|---------|
| `outreachmagic` | Main skill — pipeline.py with SQLite DB, sync, stats, CRM drivers |
| `email-finder` | Waterfall find + verify work emails (companion skill) |
| `lead-enrich` | People research by name/company (companion skill) |

## Architecture Notes

```
Sequencer webhooks → api.outreachmagic.io → Your agent's SQLite database → Query responses
```

The single source of truth is `skill-suite.json` — install pins and manifest file lists. Companion repos (`email-finder`, `lead-enrich`) are read-only mirrors published by CI.

## Deployment / Use

**Install via npx:**
```bash
npx skills add outreachmagic/outreachmagic
```

**Required:**
- OM account (portal access, webhooks)
- At least one sequencer webhook configured

**Optional:**
- Companion API keys for lead enrichment (Serper) and email finding

## Related

- [[hermes-agent]] — Skills system hosts Outreach Magic skill suite
- [[n8n]] — Workflow automation for GTM sequences
- [[agentfield]] — Could orchestrate agents using Outreach Magic data