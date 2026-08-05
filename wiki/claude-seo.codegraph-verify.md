---
name: claude-seo-codegraph-verify
tags: [claude-seo, codegraph-verify, claude-code, seo]
description: "Codegraph Verification: claude-seo"
source: sources/claude-seo/
---

# Codegraph Verification: claude-seo

**Date:** 2026-07-30

## Claim 1: 25 sub-skills and 18 specialist agents, plugin version 2.2.4
- **Wiki says:** Claude SEO runs 25 sub-skills and 18 specialist agents in parallel; plugin manifest is v2.2.4.
- **Source evidence:** `skills/` contains exactly 25 subdirectories: `seo`, `seo-audit`, `seo-backlinks`, `seo-cluster`, `seo-competitor-pages`, `seo-content`, `seo-content-brief`, `seo-dataforseo`, `seo-drift`, `seo-ecommerce`, `seo-flow`, `seo-geo`, `seo-google`, `seo-hreflang`, `seo-image-gen`, `seo-images`, `seo-local`, `seo-maps`, `seo-page`, `seo-plan`, `seo-programmatic`, `seo-schema`, `seo-sitemap`, `seo-sxo`, `seo-technical`. `agents/` contains 18 files including `seo-flow.md`. README.md:3-5: "It runs 25 sub-skills and 18 specialist agents in parallel." `.claude-plugin/plugin.json` declares `"version": "2.2.4"` and describes the same 25/18 breakdown.
- **Verdict:** ✅ CORRECT
- **Fix needed:** Wiki version corrected from 2.2.0 → 2.2.4; `seo-content-brief` and `seo-flow` added to skill tree.

## Claim 2: Pure Python scripts + Markdown skills stack — no web/database layer
- **Wiki says:** The real stack is 53 Python scripts plus Markdown skills; no Postgres/Redis/Docker/React/Vue/Tailwind/Chart.js frontend, no server components.
- **Source evidence:** `scripts/` contains exactly 53 `.py` files (verified via `ls scripts/*.py | wc -l`). Repo-wide grep for `Postgres|Redis|Docker|Tailwind|Chart.js|RBAC|TLS 1.3|SOC 2|ISO 27001` returns 0 hits in README.md/CLAUDE.md/AGENTS.md/CHANGELOG.md. The only "React/Vue" mentions are README.md:323 and README.md:463, both about SPA auto-detection for `render_page.py` — not a tech stack. `pyproject.toml` + `requirements.txt` list Python-only dependencies (matplotlib, weasyprint, playwright, google-api-python-client).
- **Verdict:** ✅ CORRECT
- **Fix needed:** Fabricated System Requirements / Performance / Monitoring / Security-compliance sections removed from wiki.

## Claim 3: Falsifiable recommendations with primary-source grounding from Google guidance
- **Wiki says:** Every audit produces a prioritized action plan with falsifiable recommendations grounded in primary-source guidance from Google. Every recommendation carries an explicit "how would we know this failed?" check.
- **Source evidence:** README.md:20 "AI-search first. Aligned with Google's AI Optimization Guide." README.md:22: "Falsifiable, not promotional. Every recommendation carries the first-principle observation it rests on, its dependency relationships, an explicit 'how would we know this failed?' check, and a leading indicator." README.md:3: "grounded in primary-source guidance from Google."
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Cross-harness plugin with tool-equivalence table
- **Wiki says:** The plugin works across multiple agent harnesses via AGENTS.md portability guidance and a tool-equivalence mapping.
- **Source evidence:** AGENTS.md:3-5 names Cursor, Cursor Cloud Agents, Google Antigravity, Gemini CLI, Grok Build, OpenAI Codex CLI, Cline, and Aider ("and any other agent harness"). AGENTS.md:39-51 provides the Claude Code → Codex/Cline/Aider/Cursor-Antigravity tool-equivalence table covering Read/Write/Edit/Bash/Glob/Grep/WebFetch. `scripts/portability_check.py` validates SKILL.md frontmatter compatibility across harnesses. The `.claude-plugin/plugin.json` `mcpServers`/skills wiring enables Claude Code auto-discovery.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (harness count updated to 8 — includes Grok Build).

## Claim 5: SSRF-safe fetching with DNS-pinned URL validation
- **Wiki says:** All scripts that accept user URLs use SSRF-safe validation blocking private IPs, loopback, metadata endpoints, and DNS rebinding.
- **Source evidence:** `scripts/url_safety.py` implements `validate_url_strict()` plus pinned safe-request helpers (validate, DNS-pin, safe fetch). `scripts/fetch_page.py` and `scripts/render_page.py` (SPA-aware headless renderer) use it. CLAUDE.md:204: "URL validation: All scripts that connect to user-supplied URLs must use `scripts/url_safety.py` (`validate_url_strict()` plus the pinned safe request helpers). This blocks private IPs, loopback, metadata endpoints, redirect rebinding, and DNS rebinding." README.md:330 reports the url_safety suite runs 91 SSRF/DNS-rebinding bypass cases.
- **Verdict:** ✅ CORRECT
- **Fix needed:** Wiki citation corrected from CLAUDE.md:219-222 → CLAUDE.md:204 (the earlier line range pointed at the PDF-review section).

## Claim 6: Private/public dual-remote topology with release-gate workflow
- **Wiki says:** The project is mirrored across two GitHub remotes — public (AgriciDaniel/claude-seo) and private (AI-Marketing-Hub/claude-seo) — with a release-gate ceremony to prevent accidental public pushes.
- **Source evidence:** CLAUDE.md:256-307 documents the dual-remote topology: "origin" (public, `AgriciDaniel/claude-seo`) and "aimh" (private, `AI-Marketing-Hub/claude-seo`). Promotion workflow: merge v2 to main, tag locally, push tag+main to `aimh` first then `origin`, then `gh release create --repo AgriciDaniel/claude-seo`. CLAUDE.md safety rule: "Never push to `origin/main` autonomously. The public is release-only." README.md:14-16 confirms two versions: public MIT (`AgriciDaniel/claude-seo`) vs. community private mirror (`AI-Marketing-Hub/claude-seo`).
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: PostToolUse validation hook and test suite
- **Wiki says:** Hooks enforce schema validation after Edit/Write; the suite carries 313 test functions.
- **Source evidence:** `hooks/hooks.json` registers a `PostToolUse` hook matching `Edit|Write` that runs `hooks/run-python-hook.js` → `hooks/validate-schema.py` with the edited file path. `grep -rn "def test" tests/` yields 313 test functions. README.md:8 badges 410 passing tests; README.md:330 traces growth from 39 (v1.9.9) to 410 across the v2 line.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: Eight extension integrations (not three)
- **Wiki says:** `extensions/` ships 8 optional add-on install helpers.
- **Source evidence:** `extensions/` contains 8 directories: `ahrefs`, `banana`, `bing-webmaster`, `dataforseo`, `firecrawl`, `profound`, `seranking`, `unlighthouse`. README.md:401 references the Banana extension via the Claude Banana Creative Director pipeline.
- **Verdict:** ✅ CORRECT
- **Fix needed:** Wiki extension list corrected from 3 → 8.

## Related

- [[claude-seo]] -- Main wiki entry
- [[claude-ai-music-skills]] -- Claude AI Music Skills
- [[ai-marketing-claude-code-skills]] -- AI marketing skills

## Cross-project

- [[claude-ai-music-skills.codegraph-verify]] -- Music skills verification
- [[n8n-mcp.codegraph-verify]] -- n8n MCP verification
