---
name: outreachmagic-codegraph-verify
tags: [outreachmagic, codegraph-verify, outreach, automation]
description: "Codegraph Verification: outreachmagic — validating wiki claims against indexed source code symbols"
source: sources/outreachmagic/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Codegraph Verification: outreachmagic

**Date:** 2026-07-12 (re-verified 2026-07-30 against v1.5.0)

## Claim 1: Webhook-to-local-SQLite-database architecture syncing 8 sales sequencers
- **Wiki says:** Outreach Magic syncs webhooks from 8 sales sequencers (Smartlead, Instantly, HeyReach, PlusVibe, EmailBison, Prosp, MasterInbox, Calendly) into a local SQLite database that agents can query directly.
- **Source evidence:**
  - `README.md:5`: "Sync Smartlead, Instantly, HeyReach, PlusVibe, EmailBison, Prosp, MasterInbox, and Calendly into one local SQLite database your agent can query directly."
  - `README.md:13-15`: "Every sequencer sends webhooks to api.outreachmagic.io. Those events sync to your agent's local database… and it syncs across multiple agents so nothing gets lost."
  - `skills/outreachmagic/scripts/pipeline.py` — main pipeline module with SQLite database management and a CLI (`pipeline.py init | login | pull | show`) storing the DB under `~/.hermes/.../outreachmagic.db`.
  - `skills/outreachmagic/scripts/relay_ingest.py` — webhook event ingestion; `schema.py` — DB schema; `db_conn.py` — connection management; `platform_registry.py` — sequencer registry; `detect_platform.py` — platform detection.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Single-skill monorepo — skills/ contains only outreachmagic
- **Wiki says:** The monorepo ships exactly one skill (`skills/outreachmagic`); `email-finder` and `lead-enrich` live in separate external repos, and their logic is embedded in the main skill's scripts.
- **Source evidence:**
  - `skill-suite.json` contains a single `skills` entry: `"outreachmagic": { "path": "skills/outreachmagic", ... }` — no email-finder/lead-enrich entries.
  - `skills/` directory contains exactly one subdirectory: `outreachmagic`.
  - `install.sh:153`: `--with-lead-enrich|--with-email-finder|...` → "**warning: $1 is no longer supported (consolidated skill includes all capabilities)**".
  - `README.md:112`: "`skills/outreachmagic/scripts/`   # All 48+ scripts — pipeline, enrich, email_finder, etc."
  - Embedded logic confirmed on disk: `skills/outreachmagic/scripts/enrich.py`, `email_finder.py`, `icypeas.py`, `millionverifier.py`.
- **Verdict:** ✅ CORRECT (wiki tree rewritten — email-finder/lead-enrich are no longer shown inside the monorepo)
- **Fix needed:** None

## Claim 3: Cross-agent synchronization — events sync across Claude Code, Cursor, Hermes
- **Wiki says:** Events sync across multiple AI agents (Claude Code, Cursor, Hermes) via shared `data_root` configuration, so no data gets lost when switching sessions.
- **Source evidence:**
  - `SKILL.md:53-56`: "Root directory for shared data. Defaults to agent home (~/.hermes). Point to ~/.claude or ~/.cursor to share one DB across agents."
  - `platforms/` contains `claude-code/`, `cursor/`, `hermes/`, `common/`, `overlays/` — platform-specific install and integration wrappers.
  - `install.sh:122`: "Usage: install.sh --platform <hermes|cursor|claude>".
  - `README.md:3`: platform badges for Claude Code, Cursor, Hermes.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Serper enrichment + email waterfall (embedded)
- **Wiki says:** Serper.dev people research and the trykitt → Icypeas → MillionVerifier → Scrubby email waterfall are capabilities of the main skill (embedded scripts), not in-repo companion skills.
- **Source evidence:**
  - `README.md:69` capability table: "**Person research** | Find LinkedIn, job title, company domain by name + company via Serper" and "**Email finding and verification** | Waterfall find (trykitt → Icypeas). Verify via MillionVerifier. Deep verify catch-all/unknown via Scrubby."
  - `skills/outreachmagic/scripts/enrich.py` — Serper.dev integration.
  - `skills/outreachmagic/scripts/email_finder.py` — waterfall email discovery logic.
  - `skills/outreachmagic/scripts/icypeas.py`, `skills/outreachmagic/scripts/millionverifier.py` — waterfall providers.
  - Test coverage: `tests/test_email_finder.py`, `tests/test_apply_email_find_results.py`, `tests/test_lead_emails.py`, `tests/test_company_personalization.py`.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: CRM Sync to GoHighLevel and HubSpot
- **Wiki says:** Push contacts, deals, and event history to GoHighLevel and HubSpot from the pipeline database. Salesforce planned.
- **Source evidence:**
  - `README.md:147`: "Push contacts, deals, and event history to GoHighLevel and HubSpot from your pipeline. Salesforce planned."
  - `skills/outreachmagic/scripts/crm_drivers/ghl.py` and `crm_drivers/hubspot.py` — CRM driver implementations (plus `base.py`, `__init__.py`).
  - `skills/outreachmagic/scripts/crm_sync.py` — CRM sync engine.
  - `tests/test_crm_sync.py` — CRM sync tests.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: 157 test files
- **Wiki says:** The project includes a comprehensive pytest suite with 157 test files.
- **Source evidence:**
  - `tests/` contains **157** `test_*.py` files plus `conftest.py` (fixtures) and `billing_contract.json` (fixture data).
  - Coverage includes: `test_pipeline_auth_cli.py`, `test_campaign_stats_cli.py`, `test_crm_sync.py`, `test_billing_contract.py`, `test_install_release.py`, `test_platform_registry.py`, `test_skill_install_contract.py`, `test_update_manifest.py`, `test_security_install_docs.py`, `test_session_bug_report_20260611.py`, `test_relay_*`, `test_lead_*`, `test_email_finder.py`, `test_lead_enrich.py`.
  - `pytest.ini` exists for pytest configuration; `scripts/run-tests.sh` is the test runner.
- **Verdict:** ✅ CORRECT (updated from stale 74+)
- **Fix needed:** None

## Claim 7: Cloud relay persistence, dashboard, device-login OAuth, batch jobs, billing
- **Wiki says:** The skill adds cloud backup direction, a local dashboard, browser device-login auth, batch pipeline jobs, and billing/credits handling.
- **Source evidence:**
  - `README.md:13-15`: "your enrichment results, email finds, and pipeline state are **backed up to the cloud** in return" — bidirectional relay persistence.
  - `skills/outreachmagic/scripts/dashboard.html` + `dashboard_server.py` (+ `dashboard_actions.py`, `dashboard_queries.py`) — local browser dashboard.
  - `skills/outreachmagic/scripts/pipeline.py:14`: "`pipeline.py login`  # Connect via browser (device auth)" — device-login OAuth flow.
  - `skills/outreachmagic/scripts/batch_runner.py`, `batch_sync_to_relay.py`; `pipeline.py:1820` `batch_lead_lookup` — batch pipeline jobs.
  - `skills/outreachmagic/scripts/api_key_pool.py:20,269` — Serper credit budget/insufficient-credits handling; `pipeline_cli.py:779,783` — credit-safe audit/dry-run flags; portal billing at `README.md:134` ([app.outreachmagic.io](https://app.outreachmagic.io)).
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: CI scoped to this repo; version 1.5.0
- **Wiki says:** The monorepo's CI (`.github/workflows/` = `release.yml`, `publish-org-profile.yml`, `skill-scan.yml`) handles releases, org-profile publishing, and skill scanning — no workflow publishes into the email-finder/lead-enrich companion repos. Current version is 1.5.0.
- **Source evidence:**
  - `.github/workflows/` contains exactly: `release.yml`, `publish-org-profile.yml`, `skill-scan.yml` — none reference the companion repos.
  - `skills/outreachmagic/scripts/VERSION` contains `1.5.0`.
  - `skill-suite.json` version source: `{ "source": "file", "path": "scripts/VERSION" }`.
- **Verdict:** ✅ CORRECT (softened — earlier claim of CI publishing companion mirrors removed)
- **Fix needed:** None

## Related

- [[outreachmagic]] -- Main wiki entry with overview and architecture
- [[hermes-agent]] -- Skills system hosting Outreach Magic
- [[n8n]] -- Workflow automation complementing outreach

## Cross-project

- [[ai-marketing-claude-code-skills.codegraph-verify]] -- Marketing skills verified
- [[claude-seo.codegraph-verify]] -- SEO skills verified
- [[n8n.codegraph-verify]] -- Workflow automation verified
