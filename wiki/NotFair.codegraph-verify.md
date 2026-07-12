---
name: notfair-codegraph-verify
tags: [notfair, codegraph-verify, agent, automation]
description: "Codegraph Verification: NotFair — validating wiki claims against indexed source code symbols"
source: sources/NotFair/
---

# Codegraph Verification: NotFair

**Date:** 2026-07-12

## Claim 1: Google Ads management with full account audit and campaign management
- **Wiki says:** "Google Ads Management — Full account audit scoring 7 health dimensions, campaign management including bid/budget adjustments, keyword and negative keyword management, RSA copy generation with A/B testing, and landing page quality scoring."
- **Source evidence:**
  - `google-ads/audit/` — Account audit skill directory (SKILL.md + supporting files)
  - `google-ads/manage/` — Campaign management skill directory
  - `google-ads/copy/` — RSA copy generator and A/B testing skill
  - `google-ads/landing/` — Landing page quality scoring skill
  - `google-ads/shared/` — Shared preamble, math, and helper utilities
  - `AGENTS.md` — Documents all 4 Google Ads skills with intent-to-skill mapping
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Meta Ads management with platform-specific audit
- **Wiki says:** "Meta Ads Management — Account audit tuned for Meta's platform with Pixel and CAPI health, attribution, campaign structure, creative health, audience strategy, spend efficiency, and scaling readiness."
- **Source evidence:**
  - `meta-ads/audit/` — Meta-specific account audit skill
  - `meta-ads/manage/` — Campaign management skill (ROAS, creative fatigue, Learning Phase triage)
  - `meta-ads/shared/` — Shared preamble, math, and policy registry
  - `AGENTS.md` — Documents Meta Ads skills with intent routing
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Full SEO audit suite with 11 specialized skills
- **Wiki says:** "SEO Audit Suite — Full-site SEO analysis, keyword research with intent classification, content creation following E-E-A-T guidelines, meta tag optimization, JSON-LD structured data generation, broken link scanning, and Generative Engine Optimization (GEO)."
- **Source evidence:**
  - `seo/seo-analysis/` — Full SEO audit with GSC data (includes scripts for WordPress, PageSpeed, GSC)
  - `seo/content-writer/` — E-E-A-T content creation skill
  - `seo/content-planner/` — Content planning with GSC data
  - `seo/keyword-research/` — Keyword discovery with topic clusters
  - `seo/meta-tags-optimizer/` — Title tags, meta descriptions, Open Graph
  - `seo/schema-markup-generator/` — JSON-LD structured data
  - `seo/seo-page/` — Per-URL deep analysis
  - `seo/broken-link-checker/` — 404/5xx scanner
  - `seo/geo-optimizer/` — Generative Engine Optimization skill (0-100 GEO Score)
  - `seo/setup-cms/` — CMS connectors (WordPress, Strapi, Contentful, Ghost)
  - `seo/shared/` — Shared utilities
- **Verdict:** ✅ CORRECT (11 SEO skill directories confirmed)
- **Fix needed:** None

## Claim 4: Cross-model review via Gemini with pass/fail gate
- **Wiki says:** "A Gemini-powered second-opinion skill that can review decisions (pass/fail gate), challenge proposals (adversarial stress test), or provide open consultation."
- **Source evidence:**
  - `gemini/SKILL.md` — Gemini cross-model review skill definition
  - `gemini/evals/` — Evaluation tests for Gemini review skill
  - `AGENTS.md` — Documents Gemini as cross-model review: "Second opinion / review / challenge / consult via Google Gemini"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: MCP server architecture with 3 streamable HTTP servers
- **Wiki says:** "Three MCP servers over streamable HTTP: `NotFair-GoogleAds` (~100 tools), `NotFair-MetaAds`, and `NotFair-SearchConsole`. These servers can be used from any MCP client without installing the CLI plugin."
- **Source evidence:**
  - `.mcp.json` — Defines 3 MCP servers as streamable HTTP at `https://notfair.co/api/mcp/`:
    - `NotFair-GoogleAds` at `/api/mcp/google_ads`
    - `NotFair-MetaAds` at `/api/mcp/meta_ads`
    - `NotFair-SearchConsole` at `/api/mcp/google_search_console`
  - `server-google-ads.json` — Standalone Google Ads MCP server configuration
  - `server-meta-ads.json` — Standalone Meta Ads MCP server configuration
  - `.claude-plugin/` — Claude Code plugin metadata and marketplace registration
- **Verdict:** ✅ CORRECT (3 MCP servers confirmed with HTTP transport config)
- **Fix needed:** None

## Claim 6: Claude Code plugin with host-agnostic skills
- **Wiki says:** "Structured as a Claude Code plugin with host-agnostic skills. Each skill is a `SKILL.md` file accompanied by reference documents. Skills work identically across Claude Code, Codex, Hermes, and other AI coding agents."
- **Source evidence:**
  - `.claude-plugin/plugin.json` — Claude Code plugin registration metadata
  - `.claude-plugin/marketplace.json` — Marketplace listing configuration
  - `AGENTS.md` — Universal entry point for any AI agent, documents skill routing and conventions
  - `google-ads/audit/SKILL.md`, `seo/seo-analysis/SKILL.md`, etc. — Multiple SKILL.md files across skill directories
  - `CLAUDE.md` — Agent instructions for the repo itself
  - `VERSION` — Current version: 0.25.6
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 6 key claims from the NotFair wiki have been verified against the source code:
- ✅ **Google Ads management:** 4 skill directories (audit, manage, copy, landing) confirmed
- ✅ **Meta Ads management:** 2 skill directories (audit, manage) confirmed
- ✅ **SEO audit suite:** 11 subdirectories in `seo/` covering all claimed capabilities confirmed
- ✅ **Gemini cross-model review:** `gemini/SKILL.md` with eval tests confirmed
- ✅ **MCP server architecture:** 3 HTTP MCP servers defined in `.mcp.json` confirmed
- ✅ **Claude Code plugin:** `.claude-plugin/` + host-agnostic `AGENTS.md` routing confirmed

## Related

- [[NotFair]] -- Main wiki entry

## Cross-project

- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
- [[n8n.codegraph-verify]] -- Similar codegraph verification for n8n
- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for Hermes Agent
