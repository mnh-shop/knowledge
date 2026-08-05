---
name: goclaw-docs-codegraph-verify
tags: [goclaw, docs, documentation, cloudflare, wrangler, trilingual, wiki, spa, i18n, llms]
description: "Codegraph Verification: goclaw-docs — validating wiki claims against indexed source code symbols"
source: sources/goclaw-docs/
---

# Codegraph Verification: goclaw-docs

**Date:** 2026-07-30

## Claim 1: MIT license (corrects prior wiki)
- **Wiki says:** License is MIT.
- **Source evidence:**
  - `package.json` line 12: `"license": "MIT"` — the only license declaration in the repo; no LICENSE file or other license metadata exists in `package.json`
  - Prior wiki entry stated "Not specified" — **incorrect**, corrected in the rewrite
- **Verdict:** ✅ CORRECT (prior wiki claim FIXED)
- **Fix needed:** None (wiki updated)

## Claim 2: Trilingual English/Vietnamese/Chinese with i18n mirror scheme
- **Wiki says:** Full EN + VI + ZH mirrors; nav titles trilingual in `js/docs-app.js`; language persisted in localStorage.
- **Source evidence:**
  - `README.md` line 4: "Trilingual: English + Vietnamese (Tiếng Việt) + Chinese (中文)"
  - `build-llms.js` lines 29-33: `LANGUAGES` array with three configs — `{ base: ROOT }`, `{ base: path.join(ROOT, 'vi') }`, `{ base: path.join(ROOT, 'zh') }`
  - `js/docs-app.js` line 81: `let currentLang = localStorage.getItem('goclaw-docs-lang') || 'en';`
  - `js/docs-app.js` lines 98+: `DOC_MAP` entries use `docEntry(section, file, 'EN title', 'VI title', 'ZH title')` — trilingual titles per key
  - `vi/` and `zh/` directories contain 130 `.md` files each
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Content scale — ~424 .md files (EN 134, VI 130, ZH 130, archive ~30)
- **Wiki says:** 122 EN content pages across 13 sections + 9 templates + 3 root docs = 134 EN; VI 130; ZH 130; archive ~30; ≈424 total (426 incl. 2 `.claude/` skill docs).
- **Source evidence:**
  - Section counts measured on disk: getting-started 6, core-concepts 6, agents 8, providers 26, channels 15, agent-teams 6, advanced 27, deployment 7, recipes 5, showcases 1, reference 8, troubleshooting 7 = **122**
  - `reference/templates/` = 9 `.md` files (EN) vs 8 in `vi/` and `zh/` mirrors (no `capabilities.md`)
  - Root `.md`: `README.md`, `CONTRIBUTING.md`, `CLAUDE.md` = 3
  - `vi/` = 130 files, `zh/` = 130 files (verified via find); `archive/` = 30 files
  - `README.md` lines 180-199 Structure tree documents the per-section page counts
- **Verdict:** ✅ CORRECT (prior "200+ pages" was imprecise; exact counts now documented)
- **Fix needed:** None

## Claim 4: Section inventory — providers (26), channels (15), advanced (27), reference (8 + 9 templates)
- **Wiki says:** providers 26, channels 15, advanced 27, reference 8 + 9 templates.
- **Source evidence:**
  - `README.md` lines 37-62: 26 provider links (overview.md + 25 provider pages)
  - `README.md` lines 66-79: 14 channel links + `channels/INDEX.md` on disk = 15 files
  - `README.md` lines 91-117: 27 advanced-page links
  - `README.md` lines 143-160: 8 reference pages + 9 template links
  - `build-llms.js` lines 14-27: `SECTIONS` array lists the same 12 content sections in reading order
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: SPA shell — index.html sidebar, docs-app.js DOC_MAP routing, _redirects fallback
- **Wiki says:** `index.html` has 129 sidebar links; `js/docs-app.js` (857 lines) hash-key `DOC_MAP` routing with EN fallback; `_redirects` = `/* /index.html 200` SPA fallback.
- **Source evidence:**
  - `index.html`: 129 matches of `class="sidebar-link"` (grep count)
  - `js/docs-app.js` line 98: `const DOC_MAP = {` — hash key → `docEntry(section, file, en, vi, zh)`; file is 857 lines
  - `js/docs-app.js` lines 318-321: fetch with per-language path and English fallback (`Try current language first, fallback to English`)
  - `_redirects` (single line): `/* /index.html 200`
  - `404.html`, `robots.txt`, `css/styles.css` (900 lines) present
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Generation pipeline — build-llms.js, generate-llms-txt.sh, build-api-catalog.js
- **Wiki says:** `build-llms.js` → `llms-full.txt` ×3; `generate-llms-txt.sh` → `llms.txt`/`llms-full.txt` ×3 (6 outputs); `build-api-catalog.js` auto-generates `reference/api-endpoints-catalog.md` (362 endpoints) by grepping GoClaw source.
- **Source evidence:**
  - `build-llms.js` lines 1-3 header: "Concatenates all markdown docs into llms-full.txt"; lines 29-33 three language outputs; line 58 writes each `llms-full.txt`
  - `scripts/generate-llms-txt.sh` lines 2-3: "Generate llms.txt and llms-full.txt for EN, VI, and ZH"; lines 104-118 write 6 outputs
  - `scripts/build-api-catalog.js` lines 3-8 header: "Generates REST API endpoint catalog from goclaw source code… greps internal/http/*.go + internal/gateway/server.go"; `reference/api-endpoints-catalog.md` line 5: "**Total endpoints:** 362 — generated from goclaw `fabe86b3` on `2026-06-29`"
  - `package.json` lines 8-9: `"build:llms": "node build-llms.js"`, `"build:api-catalog": "node scripts/build-api-catalog.js"`
  - `scripts/audit-docs.sh` lines 2-3: audits `goclaw-source:` SHA metadata vs latest `../goclaw` commit
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Governance — CLAUDE.md triple-sync, source-of-truth, archive ban; recurring sync commits
- **Wiki says:** CLAUDE.md enforces (1) read actual `goclaw/` source, (2) archive ban, (3) TRIPLE-SYNC rule (README.md + docs-app.js DOC_MAP + index.html sidebar), (4) plan-driven restructure; git history shows recurring "docs: sync with goclaw … — EN+VI+ZH" commits (21 of 75).
- **Source evidence:**
  - `CLAUDE.md` line 4: "ALWAYS read actual `goclaw/` source code (sibling directory `../goclaw/`)"
  - `CLAUDE.md` line 5: "DO NOT reference, copy from, or base content on files in the `archive/` directory"
  - `CLAUDE.md` lines 12-16: "## DOC MAP — Triple Sync (CRITICAL)" listing README.md, js/docs-app.js DOC_MAP, index.html sidebar
  - `CLAUDE.md` line 9: plan path `../plans/260307-0238-goclaw-docs-restructure/`
  - `CONTRIBUTING.md` lines 5-27: page template (Title → Overview → Main Content → Examples → Common Issues → What's Next)
  - `git log`: 21 commits matching `docs: sync with goclaw` (e.g. `4b2b2b6 docs: sync with goclaw d85bf171..fabe86b3 (151 commits) — EN+VI+ZH (#67)`, `4e6958c docs: sync with goclaw v3.11.3 … (#62)`) out of 75 total
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: Cloudflare Pages deployment via wrangler
- **Wiki says:** `wrangler pages dev/deploy ./`; `wrangler.toml` sets name, compatibility_date, `pages_build_output_dir = "./"`; no build step.
- **Source evidence:**
  - `package.json` lines 6-7: `"dev": "npx wrangler pages dev ./"`, `"deploy": "npx wrangler pages deploy ./"`
  - `wrangler.toml` lines 1-3: `name = "goclaw-docs"`, `compatibility_date = "2026-02-26"`, `pages_build_output_dir = "./"`
  - `_redirects`: `/* /index.html 200` (SPA fallback on Pages)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 8 claims from the rewritten goclaw-docs wiki have been verified against the source:
- ✅ MIT license (prior "Not specified" corrected)
- ✅ Trilingual EN/VI/ZH with i18n mirror scheme
- ✅ Content scale: 122 EN content + 9 templates + 3 root; VI 130; ZH 130; archive ~30
- ✅ Section inventory (providers 26, channels 15, advanced 27, reference 8 + 9 templates)
- ✅ SPA shell (index.html 129 sidebar links, docs-app.js DOC_MAP, _redirects fallback)
- ✅ Generation pipeline (build-llms.js / generate-llms-txt.sh / build-api-catalog.js — 362 endpoints)
- ✅ Governance (CLAUDE.md triple-sync + source-of-truth + archive ban; 21 sync commits)
- ✅ Cloudflare Pages deployment via `wrangler pages deploy ./`

## Related

- [[goclaw-docs]] -- Main wiki entry

## Cross-project

- [[goclaw.codegraph-verify]] -- Similar codegraph verification for GoClaw
- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for Hermes Agent
