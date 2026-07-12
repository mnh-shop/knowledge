---
name: outreachmagic-codegraph-verify
tags: [outreachmagic, codegraph-verify, outreach, automation]
description: "Codegraph Verification: outreachmagic — validating wiki claims against indexed source code symbols"
source: sources/outreachmagic/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Codegraph Verification: outreachmagic

**Date:** 2026-07-12

## Claim 1: Webhook-to-local-SQLite-database architecture syncing 8+ sales sequencers

- **Wiki says:** Outreach Magic syncs webhooks from 8+ sales sequencers (Smartlead, Instantly, HeyReach, PlusVibe, EmailBison, Prosp, MasterInbox, Calendly) into a local SQLite database that agents can query directly.

- **Source evidence:**
  - `README.md` line 5: "Sync Smartlead, Instantly, HeyReach, PlusVibe, EmailBison, Prosp, MasterInbox, and Calendly into one local SQLite database your agent can query directly."
  - `README.md` line 13-15: "Every sequencer sends webhooks to api.outreachmagic.io. Those events sync to your agent's local database."
  - `skills/outreachmagic/scripts/pipeline.py` — main pipeline module with SQLite database management
  - `skills/outreachmagic/scripts/relay_ingest.py` — webhook event ingestion
  - `skills/outreachmagic/scripts/schema.py` — database schema definitions
  - `skills/outreachmagic/scripts/db_conn.py` — database connection management
  - `skills/outreachmagic/scripts/platform_registry.py` — platform (sequencer) registry
  - Multiple sequencer references confirmed across tests: `test_plusvibe_dedup.py`, `test_plusvibe_bugfix.py`, `test_lead_source_relay_sync.py`

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Three companion skills shipped from one monorepo (outreachmagic, email-finder, lead-enrich)

- **Wiki says:** The project ships as three companion skills: main **outreachmagic** skill (pipeline.py with SQLite DB), **email-finder** (waterfall email discovery), and **lead-enrich** (people research via Serper.dev). Single source of truth is `skill-suite.json`.

- **Source evidence:**
  - `skill-suite.json` defines all three skills with their paths, public repos, version sources, and install pins:
    - `outreachmagic`: path `skills/outreachmagic`, public repo `outreachmagic/outreachmagic`, tag prefix `v`
    - `email-finder`: path `skills/email-finder`, public repo `outreachmagic/email-finder`, tag prefix `email-finder-v`
    - `lead-enrich`: path `skills/lead-enrich`, public repo `outreachmagic/lead-enrich`, tag prefix `lead-enrich-v`
  - `skills/outreachmagic/scripts/pipeline.py` (37 scripts total in outreachmagic skill)
  - `skills/email-finder/scripts/email_finder.py` confirmed (referenced in AGENTS.md)
  - `skills/lead-enrich/scripts/enrich.py` confirmed (referenced in AGENTS.md)
  - AGENTS.md line 13: "Single source of truth: `skill-suite.json` — install pins, manifest file lists, public repos."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Cross-agent synchronization — events sync across Claude Code, Cursor, Hermes

- **Wiki says:** Events sync across multiple AI agents (Claude Code, Cursor, Hermes) so no data gets lost when switching between sessions. All agents share the same database state via shared `data_root` configuration.

- **Source evidence:**
  - `README.md` line 5: "Sync... into one local SQLite database" — single shared database
  - `README.md` line 33: "Cursor · Claude Code · Hermes Agent" — three supported platforms
  - `SKILL.md` line 42-43: "Root directory for shared data. Defaults to agent home (~/.hermes). Point to ~/.claude or ~/.cursor to share one DB across agents."
  - `platforms/` directory contains: `claude-code/`, `cursor/`, `hermes/`, `common/`, `overlays/` — platform-specific install and integration wrappers
  - `install.sh` — cross-platform installer for all three
  - Platform overlays adapt the skill for each agent platform

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Lead enrichment via Serper.dev and email waterfall finder

- **Wiki says:** The `lead-enrich` companion skill provides structured people intelligence via Serper.dev API. The `email-finder` companion skill cascades through trykitt, Icypeas, MillionVerifier, and Scrubby APIs for email discovery.

- **Source evidence:**
  - `README.md` line 138-143: Email finder uses "trykitt, Icypeas, MillionVerifier, and Scrubby", Lead enrich uses "Serper.dev"
  - `README.md` line 93: API keys include "Lead enrichment (Serper) and email waterfall finder (trykitt, Icypeas, MillionVerifier, Scrubby)"
  - `skills/lead-enrich/scripts/enrich.py` — Serper.dev integration
  - `skills/email-finder/scripts/email_finder.py` — email waterfall logic
  - Test files confirm: `test_email_finder.py`, `test_lead_enrich.py`, `test_apply_email_find_results.py`, `test_lead_emails.py`, `test_company_personalization.py`
  - AGENTS.md confirms companion repos: `outreachmagic/email-finder` and `outreachmagic/lead-enrich`

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Extensive pytest suite (74+ test files) covering pipeline, sync, CRM, billing

- **Wiki says:** The project includes a comprehensive pytest suite covering pipeline operations, sync, CRM, billing, install, platform registry, and security.

- **Source evidence:**
  - `tests/` directory contains 74 test files covering: `test_pipeline_auth_cli.py`, `test_campaign_stats_cli.py`, `test_crm_sync.py`, `test_billing_contract.py`, `test_install_release.py`, `test_platform_registry.py`, `test_skill_install_contract.py`, `test_update_manifest.py`, `test_security_install_docs.py`, `test_session_bug_report_20260611.py`, `test_relay_*` (multiple), `test_lead_*` (multiple), `test_email_finder.py`, `test_lead_enrich.py`
  - `pytest.ini` exists for pytest configuration
  - `scripts/run-tests.sh` — test runner script
  - `tests/conftest.py` — shared test fixtures
  - AGENTS.md references test gates: `make release-check` as full pre-tag gate
  - Tests cover billing contract validation (`tests/billing_contract.json`)

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: CRM Sync to GoHighLevel and HubSpot

- **Wiki says:** Push contacts, deals, and event history to GoHighLevel and HubSpot from the pipeline database. Salesforce planned.

- **Source evidence:**
  - `README.md` line 147: "Push contacts, deals, and event history to GoHighLevel and HubSpot from your pipeline. Salesforce planned."
  - `skills/outreachmagic/scripts/crm_drivers/` directory — CRM driver implementations
  - `skills/outreachmagic/scripts/crm_sync.py` — CRM sync engine
  - `tests/test_crm_sync.py` — CRM sync tests
  - `README.md` mentions GoHighLevel and HubSpot explicitly

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: CI/CD with manifest generation, release gates, and brand publishing

- **Wiki says:** CI publishes companion repos as read-only mirrors (`outreachmagic/email-finder`, `outreachmagic/lead-enrich`) and brand assets to `outreachmagic/brand`. Release workflow uses `make manifests && make release-check` gate.

- **Source evidence:**
  - `README.md` line 124-125: `make manifests`, `make release-check`
  - `Makefile` exists with `manifests` and `release-check` targets
  - AGENTS.md release workflow: `make release-check`, `git tag vX.Y.Z`, `git push origin main --tags`
  - AGENTS.md lines 68-70: "Logos live in `brand/` and publish to `outreachmagic/brand` via `publish-brand.yml`"
  - `skill-suite.json` defines public repos for each skill: `outreachmagic/outreachmagic`, `outreachmagic/email-finder`, `outreachmagic/lead-enrich`, `outreachmagic/brand`
  - Companion repos confirmed as read-only mirrors (README.md line 143)
  - `.github/` CI workflows directory confirmed
  - `scripts/generate_skill_manifest.py` — manifest generation

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[outreachmagic]] -- Main wiki entry with overview and architecture
- [[hermes-agent]] -- Skills system hosting Outreach Magic
- [[n8n]] -- Workflow automation complementing outreach

## Cross-project

- [[ai-marketing-claude-code-skills.codegraph-verify]] -- Marketing skills verified
- [[claude-seo.codegraph-verify]] -- SEO skills verified
- [[n8n.codegraph-verify]] -- Workflow automation verified
