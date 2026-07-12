---
name: claude-seo-codegraph-verify
tags: [claude-seo, codegraph-verify, claude-code, seo]
description: "Codegraph Verification: claude-seo"
source: sources/claude-seo/
---

# Codegraph Verification: claude-seo

**Date:** 2026-07-12

## Claim 1: 25 sub-skills and 18 specialist agents organized for parallel execution
- **Wiki says:** Claude SEO runs 25 sub-skills and 18 specialist agents in parallel across technical SEO, content quality (E-E-A-T), Schema.org markup, AI search optimization (GEO), local SEO, e-commerce, and international SEO.

- **Source evidence:** The `skills/` directory contains exactly 25 subdirectories: `seo` (orchestrator), `seo-audit`, `seo-backlinks`, `seo-cluster`, `seo-competitor-pages`, `seo-content`, `seo-content-brief`, `seo-dataforseo`, `seo-drift`, `seo-ecommerce`, `seo-flow`, `seo-geo`, `seo-google`, `seo-hreflang`, `seo-image-gen`, `seo-images`, `seo-local`, `seo-maps`, `seo-page`, `seo-plan`, `seo-programmatic`, `seo-schema`, `seo-sitemap`, `seo-sxo`, `seo-technical`. The `agents/` directory contains 18 agent configuration files including `seo-technical.md`, `seo-content.md`, `seo-schema.md`, `seo-sitemap.md`, `seo-performance.md`, `seo-visual.md`, `seo-geo.md`, `seo-local.md`, `seo-maps.md`, `seo-google.md`, `seo-backlinks.md`, `seo-dataforseo.md`, `seo-image-gen.md`, `seo-cluster.md`, `seo-sxo.md`, `seo-drift.md`, `seo-ecommerce.md`, `seo-flow.md`. README.md lines 3-5 state: "runs 25 sub-skills and 18 specialist agents in parallel." `plugin.json` declares `"version": "2.2.0"` with comprehensive keyword coverage spanning all these domains.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: 50+ Python execution scripts for SEO data analysis across free and premium APIs
- **Wiki says:** The system integrates with free (Google, Moz, Bing, Common Crawl) and premium (DataForSEO) APIs for comprehensive SEO data.

- **Source evidence:** The `scripts/` directory contains exactly 50 Python scripts: `google_auth.py`, `backlinks_auth.py`, `moz_api.py`, `bing_webmaster.py`, `commoncrawl_graph.py`, `verify_backlinks.py`, `pagespeed_check.py`, `crux_history.py`, `gsc_query.py`, `gsc_inspect.py`, `indexing_notify.py`, `ga4_report.py`, `google_report.py`, `youtube_search.py`, `nlp_analyze.py`, `keyword_planner.py`, `fetch_page.py`, `parse_html.py`, `capture_screenshot.py`, `drift_baseline.py`, `drift_compare.py`, `drift_report.py`, `drift_history.py`, `dataforseo_costs.py`, `dataforseo_merchant.py`, `dataforseo_normalize.py`, `content_quality.py`, `content_humanize.py`, `content_verify.py`, `schema_generate.py`, `lcp_subparts.py`, `preload_check.py`, `agent_ux_check.py`, `parasite_risk.py`, `gbp_deprecation_lint.py`, `domain_history.py`, `seo_updates.py`, `indexnow_submit.py`, `ucp_check.py`, `unlighthouse_run.py`, and 10 more. README.md lists free API integrations (Moz, Bing, Common Crawl) and premium (DataForSEO MCP). The `extensions/dataforseo/` directory confirms DataForSEO MCP integration.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Falsifiable recommendations with primary-source grounding from Google guidance
- **Wiki says:** Every audit produces a prioritized action plan with falsifiable recommendations grounded in primary-source guidance from Google. Every recommendation carries an explicit "how would we know this failed?" check.

- **Source evidence:** README.md lines 20-22 state: "Falsifiable, not promotional. Every recommendation carries the first-principle observation it rests on, its dependency relationships, an explicit 'how would we know this failed?' check, and a leading indicator." README.md line 4: "grounded in primary-source guidance from Google." The `skills/seo/SKILL.md` orchestrator skill routes to `seo-google/SKILL.md` which references `scripts/google_auth.py` for Google API authentication. README.md line 18 confirms primary-source evidence approach: "AI-search first. Aligned with Google's AI Optimization Guide."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Plugin manifest with cross-platform agent harness support (Cursor, Codex, Cline, Aider)
- **Wiki says:** The system works with Claude Code and other agent harnesses through cross-platform portability support.

- **Source evidence:** `.claude-plugin/plugin.json` configures Claude Code plugin discovery. `AGENTS.md` (the `AGENTS.md` file loaded as project instructions) provides a detailed cross-platform compatibility table covering Cursor, Cursor Cloud Agents, Google Antigravity, Gemini CLI, OpenAI Codex CLI, Cline, and Aider, with a mapping table for tool name equivalents (Read/Write/Edit/Bash/Glob/Grep/WebFetch across all 7 harnesses). `scripts/portability_check.py` validates SKILL.md frontmatter compatibility across harnesses. `AGENTS.md` line 4-5 states: "For Cursor, Cursor Cloud Agents, Google Antigravity, Gemini CLI, OpenAI Codex CLI, Cline, Aider, and any other agent harness."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: SSRF-safe page fetching with DNS-pinned URL validation
- **Wiki says:** All scripts include SSRF protection with URL validation blocking private IPs, loopback, and GCP metadata endpoints.

- **Source evidence:** `scripts/url_safety.py` implements canonical URL/SSRF safety with validate, DNS-pin, and safe fetch functions. `scripts/fetch_page.py` uses SSRF-safe fetching with UA rotation. `scripts/render_page.py` is a SPA-aware headless renderer. CLAUDE.md (the CLAUDE.md file — the one at repo root as Claude Code instructions) lines 219-222 define security rules: "URL validation: All scripts that accept user URLs must call validate_url() from google_auth.py before making API calls. This blocks private IPs, loopback, and GCP metadata endpoints (SSRF protection)." `README.md` line 39 states: "hardened SSRF/DNS-rebinding safe fetchers."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Private/public dual-remote topology with release-gate workflow
- **Wiki says:** The project is mirrored across two GitHub remotes — public (AgriciDaniel/claude-seo) and private (AI-Marketing-Hub/claude-seo) — with release-gate ceremony to prevent accidental public pushes.

- **Source evidence:** CLAUDE.md (at repo root) lines 256-307 document the dual-remote topology: "origin" (public, `AgriciDaniel/claude-seo`) and "aimh" (private, `AI-Marketing-Hub/claude-seo`). Line 265-267: "Daily development: Work on v2 (or feature branches off v2) locally. git push aimh <branch> to publish work-in-progress." Lines 272-277 define the promotion workflow: merge v2 to main, tag, push tag to both remotes (aimh first, then origin), then `gh release create`. Line 286: "Never push to origin/main autonomously. The public is release-only." The `README.md` section lines 14-16 confirm two versions (public MIT vs. community private mirror).

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[claude-seo]] -- Main wiki entry
- [[claude-ai-music-skills]] -- Claude AI Music Skills
- [[ai-marketing-claude-code-skills]] -- AI marketing skills
- [[openai-skills]] -- OpenAI skill collections

## Cross-project

- [[claude-ai-music-skills.codegraph-verify]] -- Music skills verification
- [[n8n-mcp.codegraph-verify]] -- n8n MCP verification
