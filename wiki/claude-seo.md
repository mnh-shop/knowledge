---
name: claude-seo
tags: [claude-seo, agent, skill, seo, marketing, ai-llm, automation, cli, python]
description: "Claude SEO: Comprehensive SEO analysis agent skill for Claude Code with 25 sub-skills and 18 parallel agents"
source: sources/claude-seo/
verification_date: 2026-07-12
verified_by: codegraph-verify
updated: 2026-07-30
---

# Claude SEO: Universal SEO Analysis Skill

## Project Overview

**Claude SEO** is an open-source SEO analysis plugin for [Claude Code](https://claude.ai/claude-code) that runs 25 sub-skills and 18 specialist agents in parallel across technical SEO, content quality (E-E-A-T), Schema.org markup, AI search optimization (GEO), local SEO, e-commerce, and international SEO. Every audit produces a prioritized action plan with falsifiable recommendations grounded in primary-source guidance from Google.

## What it is

Claude SEO transforms Claude Code into a comprehensive SEO analysis platform. Instead of manually running separate SEO tools or analyzing website performance, users simply specify what they want to audit or optimize, and Claude SEO coordinates a network of specialized agents to provide deep insights and actionable recommendations.

## Architecture

### Core Components

| Component | Purpose | Key Features |
|-----------|---------|-------------|
| **25 Sub-skills** | Specialized SEO analysis skills | Technical, content, schema, local, international optimization |
| **18 Specialist Agents** | Parallel execution team | Domain experts for each SEO area |
| **Knowledge Base** | On-demand information | 14 `references/` directories (~99 files) for SEO best practices |
| **Integration Layer** | System coordination | Workflow orchestration and parallel processing |
| **Result Synthesis** | Action planning | Prioritized recommendations with falsifiable evidence |

The real technology stack is deliberately simple: **pure Python scripts** (`scripts/`, 53 `.py` files) executed by the agent harness, plus **Markdown skills** (`skills/`, `agents/`) that Claude Code auto-discovers. There is no web frontend, no database, and no server component — everything runs inside the agent's own tool loop.

### Agent Team

#### Technical SEO Agents
- **seo-technical** – Crawlability, indexability, site structure optimization
- **seo-sitemap** – XML sitemap analysis/generation
- **seo-performance** – Core Web Vitals, page speed optimization
- **seo-images** – Image optimization, accessibility
- **seo-google** – Google API integration (CrUX, GSC, GA4)

#### Content SEO Agents
- **seo-content** – E-E-A-T framework, readability analysis
- **seo-visual** – Content visualization, readability scoring
- **seo-cluster** – Semantic topic clustering and content architecture

#### Technical Implementation

```
claude-seo/
  CLAUDE.md                          # Project instructions (this file)
  CONTRIBUTORS.md                    # Community credits (Pro Hub Challenge)
  AGENTS.md                          # Multi-platform agent instructions (Cursor, Antigravity)
  .claude-plugin/
    plugin.json                    # Plugin manifest (v2.2.4)
    marketplace.json               # Marketplace catalog for distribution
  skills/                            # 25 sub-skills (auto-discovered)
    seo/                           # Main orchestrator skill
      SKILL.md                     # Entry point, routing table, core rules
      references/                  # On-demand knowledge files
    seo-audit/SKILL.md            # Full site audit with parallel agents
    seo-page/SKILL.md            # Deep single-page analysis
    seo-technical/SKILL.md       # Technical SEO (9 categories)
    seo-content/SKILL.md         # E-E-A-T and content quality
    seo-schema/SKILL.md          # Schema.org detection, validation, generation
    seo-sitemap/SKILL.md         # XML sitemap analysis/generation
    seo-images/SKILL.md          # Image optimization, SERP analysis, file optimization
    seo-geo/SKILL.md             # AI search / GEO optimization
    seo-local/SKILL.md           # Local SEO (GBP, citations, reviews, map pack)
    seo-maps/SKILL.md            # Maps intelligence (geo-grid, GBP audit, reviews, competitors)
    seo-plan/SKILL.md            # Strategic SEO planning
    seo-programmatic/SKILL.md    # Programmatic SEO at scale
    seo-competitor-pages/SKILL.md # Competitor comparison pages
    seo-hreflang/SKILL.md       # International SEO / hreflang audit
    seo-google/SKILL.md         # Google SEO APIs (references/)
    seo-backlinks/SKILL.md      # Backlink profile analysis
    seo-cluster/SKILL.md         # Semantic topic clustering (by Lutfiya Miller)
    seo-sxo/SKILL.md             # Search Experience Optimization (by Florian Schmitz)
    seo-drift/SKILL.md           # SEO drift monitoring (by Dan Colta)
    seo-ecommerce/SKILL.md      # E-commerce SEO (by Matej Marjanovic)
    seo-dataforseo/SKILL.md     # DataForSEO MCP for live SEO data
    seo-image-gen/SKILL.md      # AI image generation for SEO assets
    seo-content-brief/SKILL.md  # Content brief generation for a topic
    seo-flow/SKILL.md            # FLOW framework prompts (Find, Leverage, Optimize, Win, Local)
  agents/                          # 18 subagents (auto-discovered)
    seo-technical.md             # Crawlability, indexability, security
    seo-content.md               # E-E-A-T, readability, thin content
    seo-schema.md                # Structured data validation
    seo-sitemap.md               # Sitemap quality gates
    seo-performance.md           # Core Web Vitals, page speed
    seo-visual.md                # Screenshots, mobile rendering
    seo-geo.md                   # AI crawler access, GEO, citability
    seo-local.md                 # GBP, NAP, citations, reviews, local schema
    seo-maps.md                  # Geo-grid, GBP audit, reviews, competitor radius
    seo-google.md                # Google API analyst (CrUX, GSC, GA4)
    seo-backlinks.md             # Backlink profile analyst (Moz, Bing, CC, verify)
    seo-dataforseo.md            # DataForSEO data analyst
    seo-image-gen.md             # SEO image audit analyst
    seo-cluster.md               # Semantic clustering analysis
    seo-sxo.md                   # Search experience optimization
    seo-drift.md                 # SEO drift monitoring
    seo-ecommerce.md             # E-commerce SEO analysis
    seo-flow.md                  # FLOW framework stage prompts
  hooks/                           # Quality gate hooks
    hooks.json                   # PostToolUse schema validation
  scripts/                         # Python execution scripts (53 .py files)
    google_auth.py               # Credential management (OAuth, SA, API key, 4-tier detection)
    backlinks_auth.py            # Backlink API credential management (Moz, Bing)
    moz_api.py                   # Moz Link Explorer API (DA/PA, spam, domains, anchors)
    bing_webmaster.py            # Bing Webmaster Tools API (links, competitor comparison)
    commoncrawl_graph.py         # Common Crawl web graph parser (PageRank, in-degree)
    verify_backlinks.py          # Backlink existence verification crawler
    pagespeed_check.py           # PSI v5 + CrUX API
    crux_history.py              # CrUX History API (25-week trends)
    gsc_query.py                 # Search Console (queries, pages, sitemaps, sites)
    gsc_inspect.py               # URL Inspection (single + batch)
    indexing_notify.py           # Indexing API v3 (URL_UPDATED/URL_DELETED)
    ga4_report.py                # GA4 organic traffic reports
    google_report.py             # PDF/HTML report generator (WeasyPrint + matplotlib)
    youtube_search.py            # YouTube Data API v3
    nlp_analyze.py               # Cloud Natural Language API
    keyword_planner.py           # Google Ads Keyword Planner
    fetch_page.py                # Page fetcher with UA rotation (SSRF-safe)
    parse_html.py                # HTML parser for SEO elements
    capture_screenshot.py        # Playwright screenshots
    analyze_visual.py            # Visual analysis helper
    drift_baseline.py            # SEO drift baseline capture
    drift_compare.py             # SEO drift comparison engine (17 rules)
    drift_report.py              # SEO drift HTML report generator
    drift_history.py             # SEO drift history query
    dataforseo_costs.py          # DataForSEO cost estimation and budget tracking
    dataforseo_merchant.py       # Google Shopping / Amazon data fetching
    dataforseo_normalize.py      # DataForSEO response normalization utility
    sync_flow.py                 # FLOW prompt library sync (GitHub API, CC BY 4.0, --dry-run, --ref)
    url_safety.py                # Canonical URL/SSRF safety module (validate, DNS-pin, safe fetch)
    render_page.py               # Shared headless renderer (SPA-aware, Playwright)
    lcp_subparts.py              # LCP subparts breakdown via CrUX API
    preload_check.py             # Speculation Rules / bfcache / prerender / preload detector
    agent_ux_check.py            # Agent-friendly page auditor
    content_quality.py           # QRG-aligned content quality detector
    content_humanize.py          # AI-pattern remover (rewrites AI-typical phrasing)
    content_verify.py            # Claim extractor + citation-gap detector
    schema_generate.py           # JSON-LD generators for high-leverage schema types
    schema_ecommerce_validate.py # Product schema validator (merchant-listing requirements)
    iptc_ai_label.py             # IPTC DigitalSourceType audit/injection for AI imagery
    parasite_risk.py             # Parasite-SEO risk scanner
    gbp_deprecation_lint.py      # GBP feature-deprecation linter
    domain_history.py            # Expired-domain heritage check
    seo_updates.py               # Primary-source Google updates query tool
    indexnow_submit.py           # IndexNow submitter
    ucp_check.py                 # UCP (Universal Commerce Protocol) profile auditor
    unlighthouse_run.py          # Unlighthouse CLI wrapper (site-wide Lighthouse)
    validate_backlink_report.py  # Backlink report validation
    portability_check.py         # Cross-platform portability lint for SKILL.md files
    release_sign.py              # SHA-256 manifest generator for release signing
    verify_release.py            # Verify checkout integrity against a release manifest
  schema/                          # Schema.org JSON-LD templates
  extensions/                      # Optional add-on install helpers (8)
    dataforseo/                  # DataForSEO MCP install scripts
    firecrawl/                   # Firecrawl MCP install scripts
    banana/                      # Banana MCP install scripts
    ahrefs/                      # Ahrefs integration
    bing-webmaster/              # Bing Webmaster Tools
    profound/                    # Profound SEO data
    seranking/                   # SE Ranking integration
    unlighthouse/                # Unlighthouse site-wide audits
  docs/                            # Extended documentation
```

## Commands

| Command | Purpose |
|---------|---------|
| `/seo audit <url>` | Full site audit with up to 15 parallel subagents |
| `/seo page <url>` | Deep single-page analysis |
| `/seo technical <url>` | Technical SEO audit (9 categories) |
| `/seo content <url>` | E-E-A-T and content quality analysis |
| `/seo content-brief <topic>` | Generate a content brief for a topic |
| `/seo schema <url>` | Schema.org detection, validation, generation |
| `/seo sitemap <url>` | XML sitemap analysis or generation |
| `/seo images <url or optimize>` | Image SEO: on-page audit, SERP analysis, file optimization |
| `/seo geo <url>` | AI search / Generative Engine Optimization |
| `/seo plan <type>` | Strategic SEO planning by industry |
| `/seo programmatic` | Programmatic SEO analysis and planning |
| `/seo competitor-pages` | Competitor comparison page generation |
| `/seo local <url>` | Local SEO analysis (GBP, citations, reviews, map pack) |
| `/seo maps [command] [args]` | Maps intelligence (geo-grid, GBP audit, reviews, competitors) |
| `/seo hreflang <url>` | International SEO / hreflang audit |
| `/seo google [command] [url]` | Google SEO APIs (GSC, PageSpeed, CrUX, Indexing, GA4) |
| `/seo backlinks <url>` | Backlink profile analysis (free: Moz, Bing, CC; premium: DataForSEO) |
| `/seo backlinks setup` | Setup instructions for free backlink APIs |
| `/seo backlinks verify <url>` | Verify known backlinks still exist |
| `/seo cluster <seed-keyword>` | SERP-based semantic clustering and content architecture |
| `/seo sxo <url>` | Search Experience Optimization: page-type analysis, personas |
| `/seo drift baseline <url>` | Capture SEO baseline for change monitoring |
| `/seo drift compare <url>` | Compare current state to stored baseline |
| `/seo drift history <url>` | Show drift history over time |
| `/seo ecommerce <url>` | E-commerce SEO: product schema, marketplace intelligence |
| `/seo flow <url>` | Apply the FLOW framework: stage prompts and structured search-and-conversion output |
| `/seo firecrawl [command] <url>` | Full-site crawling and site mapping (extension) |
| `/seo dataforseo [command]` | Live SEO data via DataForSEO MCP (extension) |
| `/seo image-gen [use-case] <desc>` | AI image generation for SEO assets (extension) |

## Development Rules

- Keep SKILL.md files under 500 lines / 5000 tokens
- Reference files should be focused and under 200 lines
- Scripts must have docstrings, CLI interface, and JSON output
- Follow kebab-case naming for all skill directories
- Agents invoked via Agent tool, never via Bash
- Python dependencies install into `~/.claude/skills/seo/.venv/`
- Test with `python3 -m pytest tests/` after changes (if applicable)

## Security Rules

- **Never commit credentials**: `.env`, `client_secret*.json`, `oauth-token.json`, `service_account*.json` are all in `.gitignore`
- **URL validation**: All scripts that accept user URLs must call `validate_url_strict()` from `scripts/url_safety.py` before making API calls. This blocks private IPs, loopback, metadata endpoints, redirect rebinding, and DNS rebinding (SSRF protection).
- **OAuth tokens**: Never store `client_secret` in the token file. Read it from the client_secret.json file at runtime.
- **No hardcoded paths**: Use `os.path.dirname(os.path.abspath(__file__))` for relative paths, never `/home/username/...`
- **Config location**: `~/.config/claude-seo/google-api.json` and `~/.config/claude-seo/backlinks-api.json` (user-space, not in repo)

## Report Generation Rules

- **All SEO reports must use `scripts/google_report.py`** as the canonical report generator
- **Dependencies**: `matplotlib>=3.8.0` (charts) + `weasyprint>=61.0` (HTML-to-PDF), both in `requirements.txt`
- **Format**: A4 PDF via WeasyPrint + matplotlib charts at 200 DPI
- **Style**: Clean white title page with navy (#1e3a5f) accent, Times New Roman body font
- **Color palette**: Navy #1e3a5f (headers), dark gold #b8860b (accents), forest green #2d6a4f (pass), warm amber #d4740e (warnings), deep red #c53030 (fail), warm cream #faf9f7 (backgrounds)
- **Structure**: Title page → TOC with scores → Executive Summary → Data sections → Recommendations → Methodology
- **Charts**: 85% width, max-height 120mm, figure captions on every chart, saved to `charts/` at 200 DPI
- **No `page-break-inside: avoid`** on any element (causes white gaps in WeasyPrint)
- **Post-generation review**: `_review_pdf()` runs automatically, checking for empty images, thin sections, duplicates
- **Before presenting any PDF to the user**: verify the review passes (`"status": "PASS"`)
- **Cross-skill enforcement**: After completing ANY analysis command (audit, page, technical, content, schema, geo, local, maps), offer: "Generate a PDF report? Use `/seo google report`"
- **Google logo** appears on title page when using Google API data ("Powered by Google APIs")

## Ecosystem

Part of the Claude Code skill family (per README.md companion-tool table):
- [Claude Banana](https://github.com/AgriciDaniel/banana-claude) — standalone image gen (bundled as extension here)
- [Claude Blog](https://github.com/AgriciDaniel/claude-blog) — companion blog engine, consumes SEO findings
- [Codex SEO](https://github.com/AgriciDaniel/codex-seo) — Codex-first port with TOML agents, plugin packaging, deterministic runners
- [AI Marketing Claude](https://github.com/zubair-trabzada/ai-marketing-claude) — community marketing suite (copy, emails, ads, funnels, CRO)

## Key Principles

1. **Progressive Disclosure**: Metadata always loaded, instructions on activation, resources on demand
2. **Industry Detection**: Auto-detect SaaS, e-commerce, local, publisher, agency
3. **Parallel Execution**: Full audits spawn up to 15 specialist agents simultaneously
4. **Extension System**: DataForSEO MCP for live data, Firecrawl MCP for site crawling, Banana MCP for AI image generation
5. **AI-search first**: Question-based citability scoring and primary-source evidence, aligned with Google's AI Optimization Guide

## Repository Topology (public + private)

This project is mirrored across two GitHub remotes that share git history.
Both originate from the same local checkout; neither is a GitHub fork of
the other (different orgs, no parent/child relationship in the GitHub UI).

| Remote | URL | Visibility | Role |
|---|---|---|---|
| `origin` | `https://github.com/AgriciDaniel/claude-seo` | **Public** | Published distribution. Users discover, clone, and install from here. `main` only reflects released history. |
| `aimh` | `https://github.com/AI-Marketing-Hub/claude-seo` | **Private** | Working repo inside the AI Marketing Hub org. Daily development. v2 branch + post-release work lives here before promotion to public. |

### Workflow

Daily development:
- Work on `v2` (or feature branches off `v2`) locally.
- `git push aimh <branch>` to publish work-in-progress to the private repo
  (Dependabot, Actions, and CI run there).

Promoting to public on release:
1. Merge `v2` into local `main` when ready to release (fast-forward).
2. Tag the release locally (`git tag -a vX.Y.Z`).
3. Push the tag and main to **both** remotes in this order:
   - First: `git push aimh main && git push aimh vX.Y.Z`
   - Then: `git push origin vX.Y.Z && git push origin main`
   - The "tag before merge" sequence (see `feedback_push_caution` memory)
     applies on `origin` to avoid the `curl|bash` outage window where
     users pull a tag that doesn't yet point at code on `main`.
4. `gh release create vX.Y.Z --repo AgriciDaniel/claude-seo` (public-only).
5. `/release-blog` to publish the release post.

### Safety rules

- **Never push to `origin/main` autonomously.** The public is release-only;
  pushes are user-authorized per-release.
- **`aimh` accepts day-to-day pushes.** No release-gate ceremony required
  for the private remote.
- **Tags push to private first.** Current released tags through v2.2.4 are on
  both remotes; the private-first order protects the public release window.
- **History stays shared.** Never rewrite history on either remote with
  force-push unless explicitly authorized for that specific operation.

### Verifying the topology

```bash
# Both remotes configured
git remote -v        # expects: origin (public) + aimh (private)

# Both share main HEAD
git ls-remote --heads aimh main
git ls-remote --heads origin main   # origin = aimh/main + 1 public-branding commit (intentional; see docs/WORKFLOW-public-private.md)
```

Full workflow reference: `docs/WORKFLOW-public-private.md`.

## Report Blog Post

After cutting a new release (git tag + `gh release create`), run:

```
/release-blog
```

This generates a blog post on https://claude-seo.md/blog/, handles cover image generation, SEO metadata, FAQ schema, internal linking, sitemap/llms.txt updates, Vercel deployment, and Google indexing.

## Integration with Claude Code

### Skill Discovery

Skills are automatically discovered based on:

- **Context Analysis** – Identifying topic domains (technical, content, local, etc.)
- **Intent Detection** – Recognizing what type of SEO task you're performing
- **Skill Matching** – Selecting the most appropriate skill for the situation

### Usage Examples

```
/claude-seo audit https://example.com
```

```
/seo page https://example.com/blog/post
```

```
/seo technical https://example.com
```

```
/seo content https://example.com
```

## Key Features

### Parallel Execution

Claude SEO leverages AI power by running up to 15 specialist agents simultaneously for comprehensive SEO analysis.

### Specializations

- **Technical SEO Agent** – Crawlability, indexability, site architecture
- **Content SEO Agent** – E-E-A-T compliance, readability, content quality
- **Schema Agent** – Structured data validation and generation
- **Google Agent** – Search Console, PageSpeed, CrUX analysis
- **Backlink Agent** – Link profile analysis and competitor research

### Data Sources

- **Free APIs:** Google, Moz, Bing, Common Crawl
- **Premium APIs:** DataForSEO for comprehensive backlink data
- **Local Files:** Site crawling and analysis

### Scripts-era Utilities

Recent releases added dedicated one-shot utilities alongside the audit commands:

- **`seo_updates.py`** – primary-source Google updates query tool (tracks algorithm/guidance changes)
- **`ucp_check.py`** – UCP (Universal Commerce Protocol) profile auditor
- **`portability_check.py`** – cross-platform portability lint for SKILL.md files, validating frontmatter compatibility across agent harnesses
- **`domain_history.py`** – expired-domain heritage check
- **`parasite_risk.py`** – parasite-SEO risk scanner

### Supported Formats

- **Web:** HTML sites, SPAs (Next.js/React/Vue auto-detected), static sites
- **Enterprise:** Large-scale SEO audits
- **International:** Multi-language, multi-region SEO
- **E-commerce:** Product catalog optimization

## Licensing

This project is licensed under the MIT License (see `LICENSE`). Maintained by [@AgriciDaniel](https://github.com/AgriciDaniel) with contributions from the AI Marketing Hub Pro Hub Challenge and open-source PRs (see `CONTRIBUTORS.md`).

## Change Log (real releases)

- **v2.2.4 (2026-07-20)** – Community maintenance release: managed cross-platform Python runtime (`claude-seo run`, `/seo setup`, `/seo doctor`), SSRF-safe sitemap discovery, GSC query fixes, Bing Webmaster endpoint fixes, DataForSEO agent tool scoping, OAuth token persistence on Windows, SPA rendering improvements. Full suite: 410 passing tests.
- **v2.2.0 (2026-06-12)** – Security + portability: installer credential-injection fix, SSRF authority-confusion bypass closed, Google API keys moved to the `X-Goog-Api-Key` header, secret-scan CI gate, Windows/macOS fixes.
- **v2.1.0 (2026-05-25)** – Feature release in the v2 line.
- **v2.0.0 (2026-05-17)** – Major rewrite: parallel agent execution, 25 sub-skills, SPA-aware rendering.
- **v1.9.9 (2026-05-11)** – Test suite grew from 39 to 410 tests across the v2 line; url_safety suite runs 91 SSRF/DNS-rebinding bypass cases.

## References

### Source Documentation

- **GitHub Repository:** https://github.com/AgriciDaniel/claude-seo
- **Project Site:** https://claude-seo.md
- **Codex Port:** https://github.com/AgriciDaniel/codex-seo

### External Resources

- **Google SEO Guidelines:** https://developers.google.com/search/docs/fundamentals/seo-starter-guide
- **Google AI Optimization Guide:** https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- **Schema.org:** https://schema.org/
- **Google Search Central:** https://developers.google.com/search
- **Moz Beginner's Guide:** https://moz.com/learn/seo
- **W3C HTML Validation:** https://validator.w3.org/
- **Google Search Console:** https://search.google.com/search-console
- **Google Analytics:** https://analytics.google.com/

---

*This wiki entry is generated from the source repository and follows the Claude SEO project's documentation standards.*

---

**Last Updated:** 2026-07-30
**Verification:** Source code verified against `sources/claude-seo/`
**Version:** 2.2.4
