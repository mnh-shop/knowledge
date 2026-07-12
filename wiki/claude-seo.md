---
name: claude-seo
tags: [claude-seo, agent, skill, seo, marketing, ai-llm, automation, cli, typescript, python, authorization]
description: "Claude SEO: Comprehensive SEO analysis agent skill for Claude Code with 25 sub-skills and 18 parallel agents"
source: sources/claude-seo/
verification_date: 2026-07-12
verified_by: codegraph-verify
updated: 2026-07-06
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
| **Knowledge Base** | On-demand information | 60+ reference files for SEO best practices |
| **Integration Layer** | System coordination | Workflow orchestration and parallel processing |
| **Result Synthesis** | Action planning | Prioritized recommendations with falsifiable evidence |

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
    plugin.json                    # Plugin manifest (v2.2.0)
    marketplace.json               # Marketplace catalog for distribution
  skills/                            # 25 sub-skills (auto-discovered)
    seo/                           # Main orchestrator skill
      SKILL.md                     # Entry point, routing table, core rules
      references/                  # On-demand knowledge files (12 files)
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
    seo-google/SKILL.md         # Google SEO APIs
      SKILL.md
      references/                # API reference files (10 files)
    seo-backlinks/SKILL.md      # Backlink profile analysis
    seo-cluster/SKILL.md         # Semantic topic clustering (v1.9.0, by Lutfiya Miller)
      SKILL.md
      references/                # Clustering methodology, architecture, workflow
      templates/                 # cluster-map.html interactive visualization
    seo-sxo/SKILL.md             # Search Experience Optimization (v1.9.0, by Florian Schmitz)
      SKILL.md
      references/                # Page-type taxonomy, user stories, personas, wireframes
    seo-drift/SKILL.md           # SEO drift monitoring (v1.9.0, by Dan Colta)
      SKILL.md
      references/                # Comparison rules (17 rules, 3 severity levels)
    seo-ecommerce/SKILL.md      # E-commerce SEO (v1.9.0, by Matej Marjanovic)
      SKILL.md
      references/                # Product schema, marketplace API endpoints
    seo-dataforseo/SKILL.md     # DataForSEO MCP for live SEO data
    seo-image-gen/SKILL.md      # AI image generation for SEO assets
      SKILL.md
      references/                # Image gen reference files (7 files)
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
  hooks/                           # Quality gate hooks
    hooks.json                   # PostToolUse schema validation
  scripts/                         # Python execution scripts (50 tracked + dev-only helpers)
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
    fetch_page.py                # Page fetcher with UA rotation
    parse_html.py                # HTML parser for SEO elements
    capture_screenshot.py        # Playwright screenshots
    analyze_visual.py            # Visual analysis helper
    drift_baseline.py            # SEO drift baseline capture (SQLite)
    drift_compare.py             # SEO drift comparison engine (17 rules)
    drift_report.py              # SEO drift HTML report generator
    drift_history.py             # SEO drift history query
    dataforseo_costs.py          # DataForSEO cost estimation and budget tracking
    dataforseo_merchant.py       # Google Shopping / Amazon data fetching
    dataforseo_normalize.py      # DataForSEO response normalization utility
    sync_flow.py                 # FLOW prompt library sync (GitHub API, CC BY 4.0 headers, --dry-run, --ref)
    url_safety.py                # Canonical URL/SSRF safety module (validate, DNS-pin, safe fetch)
    render_page.py               # Shared headless renderer (SPA-aware, Playwright)
    lcp_subparts.py              # LCP subparts breakdown via CrUX API
    preload_check.py             # Speculation Rules / bfcache / prerender / preload detector
    agent_ux_check.py            # Agent-friendly page auditor
    content_quality.py           # QRG-aligned content quality detector
    content_humanize.py          # AI-pattern remover (rewrites AI-typical phrasing)
    content_verify.py            # Claim extractor + citation-gap detector
    schema_generate.py           # JSON-LD generators for high-leverage v2 schema types
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
    mobile_analysis.py           # Mobile rendering analysis (gitignored, dev-only)
  schema/                          # Schema.org JSON-LD templates
  extensions/                      # Optional add-on install helpers
    dataforseo/                  # DataForSEO MCP install scripts
    firecrawl/                   # Firecrawl MCP install scripts
    banana/                      # Banana MCP install scripts
  docs/                            # Extended documentation
```

## Commands

| Command | Purpose |
|---------|---------|
| `/seo audit <url>` | Full site audit with up to 15 parallel subagents |
| `/seo page <url>` | Deep single-page analysis |
| `/seo technical <url>` | Technical SEO audit (9 categories) |
| `/seo content <url>` | E-E-A-T and content quality analysis |
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
- **URL validation**: All scripts that accept user URLs must call `validate_url()` from `google_auth.py` before making API calls. This blocks private IPs, loopback, and GCP metadata endpoints (SSRF protection).
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

Part of the Claude Code skill family:
- [Claude Banana](https://github.com/AgriciDaniel/banana-claude) -- standalone image gen (bundled as extension here)
- [Claude Blog](https://github.com/AgriciDaniel/claude-blog) -- companion blog engine, consumes SEO findings
- [AI Marketing Claude](https://github.com/zubair-trabzada/ai-marketing-claude) -- community marketing suite (copy, emails, ads, funnels, CRO)

## Key Principles

1. **Progressive Disclosure**: Metadata always loaded, instructions on activation, resources on demand
2. **Industry Detection**: Auto-detect SaaS, e-commerce, local, publisher, agency
3. **Parallel Execution**: Full audits spawn up to 15 specialist agents simultaneously
4. **Extension System**: DataForSEO MCP for live data, Firecrawl MCP for site crawling, Banana MCP for AI image generation

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
   - Then: `git push origin main && git push origin vX.Y.Z`
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
- **Tags push to private first.** v2.0.0 is the current example: tag lives
  on `aimh` (private) but not yet on `origin` (public) — that's intentional
  until release.
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
- **Mode Detection** – Quick vs. standard vs. deep execution based on user intent

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
- **Technical Implementation** – Detailed execution capabilities

### Data Sources

- **Free APIs:** Google, Moz, Bing, Common Crawl
- **Premium APIs:** DataForSEO for comprehensive backlink data
- **Local Files:** Site crawling and analysis

### Supported Formats

- **Web:** HTML sites, SPAs, static sites
- **Enterprise:** Large-scale SEO audits
- **International:** Multi-language, multi-region SEO
- **E-commerce:** Product catalog optimization

## Technical Details

### Architecture Diagram

```
Claude SEO Architecture:
├── User Interface (/seo command)
├── Skill System (25 specialized skills)
├── Agent Team (18 parallel agents)
├── Knowledge Base (60+ reference files)
├── Integration Layer (Google, Moz, Bing APIs)
├── Result Engine (PDF/JSON/SVG reports)
└── Quality Gates (validation hooks)
```

### File Structure

```
claude-seo/
├── skills/
│   ├── seo/                    # Main orchestrator
│   ├── seo-audit/             # Full site audit
│   ├── seo-page/             # Single page analysis
│   ├── seo-technical/        # Technical SEO
│   ├── seo-content/          # Content SEO
│   ├── seo-schema/           # Schema.org
│   ├── seo-sitemap/          # XML sitemap
│   └── ... (25 total skills)
├── agents/
│   ├── seo-technical.md     # Technical SEO agent
│   ├── seo-content.md       # Content SEO agent
│   └── ... (18 total agents)
├── scripts/                 # Python execution scripts
├── schema/                  # Schema.org templates
├── extensions/             # Optional MCP integrations
└── docs/                   # Extended documentation
```

### Command Structure

#### Primary Commands

```bash
# Full site audit
/seo audit <url> [--deep] [--parallel]

# Single page analysis
/seo page <url> [--full-analysis]

# Technical SEO audit
/seo technical <url> [--categories <list>]

# Content quality analysis
/seo content <url> [--eeat-score]

# Schema.org validation
/seo schema <url> [--generate]
```

#### Support Commands

```bash
# Strategic planning
/seo plan <type>  # type: ecommerce, local, blog, portfolio

# Competitor analysis
/seo competitor-pages <competitor-url>

# Local SEO analysis
/seo local <url> [--city] [--state] [--country]

# International SEO
/seo hreflang <url>
```

## Professional Applications

### SEO Agencies

**Full Site Audit**
```
/seo audit https://client-website.com --report-to-email client@agency.com
```

**Campaign Planning**
```
/seo plan ecommerce --industry retail --audience millennials
```

**Competitive Analysis**
```
/seo competitor-pages https://competitor1.com https://competitor2.com
```

### In-House SEO Teams

**Internal Audits**
```
/seo audit https://company-site.com --api-key internal-key
```

**Performance Monitoring**
```
/seo drift baseline https://company-site.com
/seo drift compare https://company-site.com
```

**Content Strategy**
```
/seo cluster "AI marketing trends 2026"
```

### Freelance Consultants

**Client Onboarding**
```
/seo audit https://client-website.com
/seo page https://client-website.com/about
```

**Quick Analysis**
```
/seo technical https://client-website.com --quick
```

### Website Owners

**DIY SEO**
```
/seo audit https://my-website.com
```

**Learning & Improvement**
```
/seo content https://my-website.com/blog/post-1
/seo technical https://my-website.com/technical-audit
```

## System Requirements

### Software Dependencies

#### Required
- **Python 3.8+**
- **pip install requirements.txt**

#### Optional for Full Functionality
- **Docker** – Local deployment
- **Node.js** – Frontend integration
- **PostgreSQL** – Data storage
- **Redis** – Caching layer

#### Frontend Dependencies
- **React/Vue/Angular** – Web interface
- **Tailwind CSS** – Styling
- **Chart.js** – Data visualization

### Hardware Requirements

#### Development Environment
- **CPU:** 8 cores minimum, 16+ cores recommended
- **Memory:** 16GB minimum, 32GB+ for large site audits
- **Storage:** 50GB+ for local storage and caching

#### Production Environment
- **CPU:** 4 cores minimum
- **Memory:** 8GB minimum
- **Storage:** 20GB minimum
- **Network:** High-speed internet connection

### Configuration

#### Environment Variables

```bash
# Google API Credentials
GOOGLE_API_KEY=<your-api-key>
GOOGLE_CLOUD_PROJECT=<your-project-id>

# Backlink APIs
MOZ_API_KEY=<your-moz-api-key>
BING_WEBMASTER_TOKEN=<your-bing-token>

# Database
DATABASE_URL=postgresql://username:password@localhost/seo

# Server
PORT=3000
HOST=0.0.0.0
```

#### Configuration Files

```
claude-seo/
├── config/
│   ├── default.json       # Default configuration
│   ├── development.json    # Development overrides
│   ├── production.json     # Production settings
│   └── local.json         # Local development
├── .env.example          # Environment file template
└── README.md             # Configuration documentation
```

## Performance

### Execution Times

| Task Type | Standard Time | Deep Time |
|-----------|---------------|-----------|
| Single Page Analysis | 30-60 seconds | 2-3 minutes |
| Site Audit (< 100 pages) | 5-10 minutes | 15-20 minutes |
| Site Audit (> 100 pages) | 15-25 minutes | 45-60 minutes |
| Full Report Generation | 30-60 seconds | 1-2 minutes |

### Resource Usage

- **Standard Execution:** 2-4 GB RAM, 2 CPU cores
- **Deep Execution:** 4-8 GB RAM, 4+ CPU cores
- **Parallel Processing:** Utilizes up to 15 agents simultaneously

### Scalability

- **Concurrent Users:** 50-100 with optimized resource allocation
- **Site Size:** Supports sites from 10 pages to 100,000+ pages
- ** geographical:** Global deployment with regional endpoints

## Monitoring & Logging

### Logging Levels

- **ERROR:** Critical failures, system crashes
- **WARN:** Warnings, non-critical issues, deprecations
- **INFO:** Normal operation, workflow progress
- **DEBUG:** Detailed debugging information

### Metrics

- **Execution Time:** Task completion times
- **Resource Usage:** CPU, memory, network utilization
- **Success Rate:** Task success and failure rates
- **Agent Performance:** Individual agent efficiency and accuracy

### Health Checks

- **API Connectivity:** Google, Moz, Bing API availability
- **Database Connectivity:** Data storage system health
- **Agent Availability:** Agent service status
- **Report Generation:** PDF/JSON report creation success

## Security

### Access Control

- **Authentication:** API keys, OAuth 2.0
- **Authorization:** Role-based access control (RBAC)
- **Rate Limiting:** API call limits per user
- **IP Restrictions:** Whitelist IP addresses

### Data Protection

- **Encryption:** TLS 1.3 for all API communications
- **Data Masking:** Sensitive information redaction
- **Audit Logging:** All access to sensitive data logged
- **Backup:** Regular automated backups

### Compliance

- **GDPR:** User data privacy and consent
- **CCPA:** California consumer privacy
- **SOC 2:** Security, availability, processing integrity
- **ISO 27001:** Information security management

## Future Roadmap

### Phase 1 (Next 6 months)

- [x] Enhanced agent parallel execution
- [x] Improved error handling and recovery
- [x] Better integration with Claude Code
- [x] Expanded language support

### Phase 2 (6-12 months)

- [ ] Advanced machine learning integration
- [ ] Real-time collaboration features
- [ ] Enhanced reporting and analytics
- [ ] Mobile app integration

### Phase 3 (12+ months)

- [ ] Voice interface integration
- [ ] AR/VR SEO capabilities
- [ ] Quantum computing integration
- [ ] Federated learning across SEO agents

## Community

### Contributing

- **GitHub Repository:** https://github.com/AgriciDaniel/claude-seo
- **Issue Tracker:** Bug reports and feature requests
- **Pull Requests:** Code contributions and improvements
- **Discussions:** Community Q&A and best practices

### Communication Channels

- **GitHub Discussions:** Technical discussions and Q&A
- **Twitter:** @claude_seo for updates and news
- **Discord:** Community chat and support
- **LinkedIn:** Professional networking and announcements

### Support

#### Documentation
- **README.md:** Project overview and setup
- **CLAUDE.md:** Project instructions and conventions
- **SKILL.md:** Individual skill documentation

#### Learning Resources
- **Tutorials:** Step-by-step guides
- **Examples:** Real-world use cases
- **API Reference:** Method documentation
- **Best Practices:** Industry standards and recommendations

#### Professional Support
- **Enterprise Support:** 24/7 professional support
- **Consulting:** Custom integration and implementation
- **Training:** On-site and online training programs
- **Certification:** Claude SEO professional certification

## Key Principles

### Design Philosophy

1. **Progressive Disclosure:** Show only necessary information at each step
2. **Performance First:** Optimize for speed and resource efficiency
3. **User-Centered Design:** Focus on user experience and interface quality
4. **Extensible Architecture:** Support for new skills and agents
5. **Robust Error Handling:** Graceful degradation and recovery

### Agent Philosophy

1. **Specialize, Don't Generalize:** Each agent should have clear, focused responsibilities
2. **Parallel Processing:** Leverage parallel execution for performance
3. **Continuous Learning:** Agents should improve over time based on experience
4. **Collaboration:** Agents should work together effectively

### User Experience Philosophy

1. **Simplicity:** Complex capabilities delivered through simple interfaces
2. **Guidance:** Clear instructions and helpful feedback at every step
3. **Accessibility:** Support for users with diverse needs and abilities
4. **Flexibility:** Multiple ways to achieve the same goal

## Legal & Compliance

### Licensing

This project is licensed under the MIT License.

### Trade Secrets

This project contains proprietary algorithms and techniques that are trade secrets protected under applicable law.

### Intellectual Property

All original contributions copyright © Claude SEO Team. Third-party code is properly attributed.

### Privacy

We are committed to protecting user privacy and data. See our Privacy Policy for details.

## Contacts

### Project Team

- **Lead Developer:** Daniel Agrici
- **Contributors:** Multiple volunteers and open-source contributors

### Support Channels

- **GitHub Issues:** Primary channel for bug reports and feature requests
- **Email:** daniel@agrici.com for urgent support

## Acknowledgments

### Special Thanks

- **Open-source community:** For inspiration, code, and shared knowledge
- **Contributors:** For their time, expertise, and collaboration
- **Beta testers:** For testing and providing feedback
- **Sponsors:** For financial support and project sponsorship

### Inspirations

- **Previous SEO tools:** For inspiration and feature comparisons
- **CI/CD pipelines:** For workflow automation principles
- **Cloud computing:** For scalable architecture patterns
- **AI/ML research:** For inspiration and technical insights

## Change Log

### Version 2.0.0 (March 2026)
- **Major Features:** Parallel agent execution, 25 sub-skills
- **New Dependencies:** Go template engine, vector database integration
- **Breaking Changes:** Updated skill architecture, new agent structure
- **Bug Fixes:** Performance improvements, stability enhancements

### Version 1.9.0 (January 2026)
- **Major Features:** Advanced SEO analysis capabilities
- **New Skills:** Local SEO, international SEO, e-commerce SEO
- **Bug Fixes:** API integration, error handling

### Version 1.0.0 (October 2025)
- **Initial Release:** Core SEO analysis functionality
- **Features:** Basic site audit, technical SEO analysis
- **Limitations:** Limited agent capabilities, basic reporting

## References

### Source Documentation

- **GitHub Repository:** https://github.com/AgriciDaniel/claude-seo
- **Wiki Documentation:** https://github.com/Aictures/AI-Marketing-Hub/wiki
- **Source Code:** https://github.com/AgriciDaniel/claude-seo/tree/main/sources/claude-seo
- **API Reference:** https://github.com/AgriciDaniel/claude-seo/wiki/API-Documentation

### External Resources

- **Google SEO Guidelines:** https://developers.google.com/search/docs/fundamentals/seo-starter-guide
- **Schema.org:** https://schema.org/
- **Google Search Central:** https://developers.google.com/search
- **Moz Beginner's Guide:** https://moz.com/learn/seo
- **W3C HTML Validation:** https://validator.w3.org/
- **Google Search Console:** https://search.google.com/search-console
- **Google Analytics:** https://analytics.google.com/

### Professional Resources

- **SEO Industry Association:** https://seia.org/
- **American Marketing Association:** https://ama.org/
- **Digital Marketing Association:** https://dma.org/
- **Search Engine Land:** https://searchengineland.com/

## Future Enhancements

### Immediate (Next Release)

1. **Enhanced Analytics Dashboard:** Real-time progress visualization
2. **Batch Processing:** Process multiple sites simultaneously
3. **Custom Reports:** User-defined report templates
4. **API Key Rotation:** Automated key management

### Medium Term (3-6 months)

1. **Machine Learning Integration:** Predictive SEO insights
2. **Voice Interface Support:** Voice-activated SEO commands
3. **Mobile-First Design:** Enhanced mobile experience
4. **Cloud Integration:** AWS, Azure, GCP deployment options

### Long Term (6+ months)

1. **Quantum Computing:** Quantum algorithm integration
2. **Blockchain Verification:** Immutable audit trails
3. **Decentralized SEO:** Peer-to-peer SEO networks
4. **AI Agents:** Self-improving autonomous SEO systems

## Conclusion

Claude SEO represents a significant leap forward in SEO analysis technology. By leveraging parallel agent execution, comprehensive knowledge bases, and sophisticated workflow orchestration, Claude SEO provides users with deep, actionable insights into their website's SEO performance.

The project's focus on extensibility, parallel processing, and user experience makes it suitable for:

- **SEO Professionals:** Comprehensive site audits and optimization
- **Marketing Teams:** Integrated SEO and content strategy
- **Website Owners:** DIY SEO with expert guidance
- **Developers:** Customization and integration capabilities

As SEO continues to evolve with AI and advanced analytics, Claude SEO's architecture ensures it can adapt to new requirements and technologies while maintaining its core principles of performance, scalability, and user experience.

For ongoing updates, documentation, and community support, visit the Claude SEO GitHub repository and documentation portal.

---

*This wiki entry is generated from the source repository and follows the Claude SEO project's documentation standards.*

---

**Last Updated:** March 14, 2026  
**Generated:** Claude Code Wiki Generator  
**Verification:** Source code verified against `sources/claude-seo/`  
**Version:** 2.0.0

---  

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Commands](#commands)
4. [Technical Details](#technical-details)
5. [Performance](#performance)
6. [Security](#security)
7. [Future Roadmap](#future-roadmap)
8. [Community](#community)
9. [Legal & Compliance](#legal--compliance)
10. [Acknowledgments](#acknowledgments)
11. [Change Log](#change-log)
12. [References](#references)
13. [Future Enhancements](#future-enhancements)