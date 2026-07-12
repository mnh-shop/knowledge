---
name: awesome-openclaw-usecases-codegraph-verify
tags: [awesome-openclaw-usecases, codegraph-verify, openclaw, use-cases]
description: "Codegraph Verification: awesome-openclaw-usecases — validating wiki claims against indexed source code symbols"
source: sources/awesome-openclaw-usecases/
---

# Codegraph Verification: awesome-openclaw-usecases

**Date:** 2026-07-12

## Claim 1: Curated collection of 42+ real-life OpenClaw use cases
- **Wiki says:** Community collection of real-life use cases for OpenClaw, organized by category (Social Media, Creative & Building, Infrastructure & DevOps, Productivity, Research & Learning, Finance & Trading). Badge shows `usecases-42-blue`.
- **Source evidence:**
  - `README.md` badge: `![Use Cases](https://img.shields.io/badge/usecases-42-blue?style=flat-square)` — 42 use cases at time of badge
  - `README.md` line 24: "This is a community collection of real-life use cases for [OpenClaw](https://github.com/openclaw/openclaw)"
  - `/usecases/` directory contains 42 markdown files: `ai-video-editing.md` through `youtube-content-pipeline.md`
  - README organizes them into 6 categories: Social Media (5), Creative & Building (6), Infrastructure & DevOps (2), Productivity (20), Research & Learning (8), Finance & Trading (1)
  - `CONTRIBUTING.md` specifies guidelines for adding new use cases and the requirement that they be tested and verified in practice
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Each use case includes structured prompts, skills needed, and pain point
- **Wiki says:** Each use case covers pain point, what it does, prompts/config, skills needed, and related links.
- **Source evidence:**
  - `CONTRIBUTING.md` lines 6-11 require all contributions to cover: "**Pain Point** — What problem does this solve?", "**What It Does** — Brief explanation", "**Prompts** — The actual prompts/config you'd give OpenClaw", "**Skills Needed** — Which OpenClaw skills are required", "**Related Links** — Relevant docs, APIs, tools"
  - `usecases/multi-agent-team.md` contains all 5 sections: Pain Point (lines 8-13), What It Does (lines 16-22), Skills You Need (lines 112-117), full configuration examples for each agent with SOUL.md, AGENTS.md, and HEARTBEAT.md templates, and Related Links (lines 197-200)
  - `usecases/overnight-mini-app-builder.md`, `usecases/n8n-workflow-orchestration.md`, and others follow the same structure
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Multi-agent team orchestration pattern with shared memory and Telegram control plane
- **Wiki says:** Includes a multi-agent team pattern where specialized agents (strategy, business, marketing, dev) coordinate through shared memory and a single Telegram group chat.
- **Source evidence:**
  - `usecases/multi-agent-team.md` line 5: "This use case sets up multiple OpenClaw agents as a coordinated team, each specialized in a domain, communicating through shared memory and controlled via Telegram"
  - Defines 4 agent roles: Milo (Strategy Lead), Josh (Business & Growth), Marketing Agent, Dev Agent
  - Each agent has a `SOUL.md` personality definition, distinct model (`Claude Opus`, `Claude Sonnet`, `Gemini`), and `Telegram` channel
  - Line 137-158: Full `AGENTS.md — Telegram Routing` configuration with `@milo`, `@josh`, `@marketing`, `@dev` tag routing
  - Line 121-133: Shared memory structure with `GOALS.md`, `DECISIONS.md`, `PROJECT_STATUS.md`, and per-agent private contexts
  - Line 162-178: Scheduled daily tasks via `HEARTBEAT.md` schedule
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Strong security warning about third-party skill auditing
- **Wiki says:** Warning that OpenClaw skills and third-party dependencies referenced may have critical security vulnerabilities and have not been audited by the maintainer.
- **Source evidence:**
  - `README.md` lines 26-27: "> **Warning:** OpenClaw skills and third-party dependencies referenced here may have critical security vulnerabilities. Many use cases link to community-built skills, plugins, and external repos that have **not been audited by the maintainer of this list**. Always review skill source code, check requested permissions, and avoid hardcoding API keys or credentials. You are solely responsible for your own security."
  - The warning is the second block after the main description, giving it prominence
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: No crypto use cases accepted
- **Wiki says:** The project explicitly does not accept use cases related to cryptocurrency.
- **Source evidence:**
  - `CONTRIBUTING.md` line 22: "**No crypto-related use cases** — these will not be accepted."
  - `README.md` line 110: "> **Note:** We do not accept use cases related to crypto."
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Use cases integrate with external tools and platforms (n8n, Telegram, Discord, Todoist)
- **Wiki says:** Use cases demonstrate integration with third-party platforms including n8n, Telegram, Discord, and Todoist for workflow orchestration and multi-channel access.
- **Source evidence:**
  - `usecases/n8n-workflow-orchestration.md`: "Delegate API calls to n8n workflows via webhooks"
  - `usecases/content-factory.md`: "Run a multi-agent content pipeline in Discord"
  - `usecases/multi-agent-team.md`: Single Telegram group chat as control plane for all 4 agents
  - `usecases/todoist-task-manager.md`: "Maximize agent transparency by syncing reasoning and progress logs to Todoist"
  - `usecases/phone-based-personal-assistant.md`: "Access OpenClaw from any phone via voice call or SMS"
  - `usecases/multi-channel-customer-service.md`: "Unify WhatsApp, Instagram, Email, and Google Reviews in one AI-powered inbox"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 6 key claims from the awesome-openclaw-usecases wiki have been verified against the source code:
- ✅ 42+ curated use cases: Confirmed via badge and directory listing
- ✅ Structured format: Each use case follows pain-point → prompts → skills → links pattern
- ✅ Multi-agent patterns: Full team orchestration with SOUL.md, Telegram routing, shared memory
- ✅ Security warning: Prominent warning about third-party audits
- ✅ No crypto policy: Explicitly stated in both README and CONTRIBUTING
- ✅ External integrations: Verified n8n, Telegram, Discord, Todoist, phone, multi-channel integrations

## Related

- [[awesome-openclaw-usecases]] -- Main wiki entry
- [[openclaw]] -- OpenClaw agent platform
- [[awesome-openclaw-skills]] -- OpenClaw skills catalog
- [[openclaw-use-case-patterns]] -- Use case architecture patterns

## Cross-project

- [[openclaw.codegraph-verify]] -- OpenClaw codegraph verification
- [[hermes-agent.codegraph-verify]] -- Hermes agent codegraph verification
- [[n8n.codegraph-verify]] -- n8n workflow codegraph verification
