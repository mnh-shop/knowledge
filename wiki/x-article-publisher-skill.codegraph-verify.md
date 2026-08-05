---
name: x-article-publisher-skill-codegraph-verify
tags: [x-article-publisher-skill, codegraph-verify, skill, x-twitter]
description: "Codegraph Verification: x-article-publisher-skill — validating wiki claims against indexed source code"
source: sources/x-article-publisher-skill/
date: 2026-07-12
---

# Codegraph Verification: x-article-publisher-skill

**Date:** 2026-07-12 (re-verified 2026-07-30)

## Claim 1: Origin — wshuyi, not omarmoataz
- **Wiki says:** The project originates from `wshuyi/x-article-publisher-skill` (the wiki header was corrected — the old header claimed `omarmoataz`, contradicting its own install section).
- **Source evidence:**
  - `git remote -v`: `origin https://github.com/wshuyi/x-article-publisher-skill.git` (fetch/push).
  - `README.md:105-109` (Method 1 — Git Clone): "`git clone https://github.com/wshuyi/x-article-publisher-skill.git`".
  - `README.md:113-121` (Method 2 — Plugin Marketplace): "`/plugin marketplace add wshuyi/x-article-publisher-skill`".
  - `.claude-plugin/plugin.json`: `"author": { "name": "wshuyi" }` and `"repository": "https://github.com/wshuyi/x-article-publisher-skill"`.
  - No occurrence of `omarmoataz` anywhere in the source tree.
- **Verdict:** ✅ CORRECT (origin corrected)
- **Fix needed:** None

## Claim 2: Claude Code skill for publishing Markdown articles to X (Twitter) Articles
- **Wiki says:** "The X Article Publisher Skill is a Claude Code skill that automates publishing Markdown articles to X (Twitter) Articles with one command."
- **Source evidence:**
  - `skills/x-article-publisher/SKILL.md:1-4`: frontmatter with `name: x-article-publisher` and description "Publish Markdown articles to X (Twitter) Articles editor with proper formatting."
  - `README.md:5`: "Publish Markdown articles to X (Twitter) Articles with one command. Say goodbye to tedious rich text editing."
  - `README.md:51`: "**Rich Text Paste**: Convert Markdown to HTML, paste via clipboard — all formatting preserved".
  - `docs/GUIDE.md` — detailed usage guide.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Version nuance — features v1.2.0, manifest still 1.1.0
- **Wiki says:** The feature set is v1.2.0 (README.md:7, changelog at README.md:297), while `.claude-plugin/plugin.json` still declares 1.1.0 — a manifest lag.
- **Source evidence:**
  - `README.md:7`: "**v1.2.0** — Now with divider support, table-to-image, Mermaid support, and cross-platform clipboard".
  - `README.md:297` (Changelog): "### v1.2.0 (2025-01)" followed by divider/table/Mermaid/Windows bullets (lines 298-302).
  - `.claude-plugin/plugin.json`: `"version": "1.1.0"` — the manifest has not been bumped to 1.2.0.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Block-index image positioning with reverse insertion order
- **Wiki says:** "Images are placed at precise positions using element indices rather than fragile text matching, inserted from highest to lowest block index."
- **Source evidence:**
  - `README.md:60-67` ("What's New in v1.1.0"): "Image positioning: Text matching (fragile) → Block index (precise)" and "Insertion order: Sequential → Reverse (high→low)."
  - `README.md:67-73` ("Why Block-Index?"): "Previously, images were positioned by matching surrounding text — this failed when… Now, each image has a `block_index` indicating exactly which block element it follows. This is deterministic and reliable."
  - `README.md:53-54`: "**Block-Index Positioning** (v1.1): Precise image placement using element indices, not text matching"; "**Reverse Insertion**: Insert images from highest to lowest index to avoid position shifts".
  - `skills/x-article-publisher/scripts/parse_markdown.py` — extracts content_images with block_index.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Three Python helper scripts
- **Wiki says:** The skill directory contains three Python scripts: `parse_markdown.py`, `copy_to_clipboard.py`, `table_to_image.py`.
- **Source evidence:**
  - `skills/x-article-publisher/scripts/` contains exactly 3 Python files: `parse_markdown.py`, `copy_to_clipboard.py`, `table_to_image.py`.
  - `README.md:253-254` (repo tree): "`copy_to_clipboard.py` # Cross-platform clipboard", "`table_to_image.py` # Markdown table → PNG (v1.2)".
  - `SKILL.md` "## Scripts" section documents each: `parse_markdown.py` returns JSON with title, cover_image, content_images, dividers, html, total_blocks; `copy_to_clipboard.py` copies image/HTML cross-platform; `table_to_image.py` converts Markdown tables to PNG via Pillow.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Cover vs content image separation
- **Wiki says:** The first image is extracted and uploaded as the article cover; content images are positioned separately with precise block-index placement.
- **Source evidence:**
  - `SKILL.md:28`: "Returns JSON with: title, cover_image, content_images, **dividers** (with block_index for positioning), html, total_blocks" — cover separated from content_images.
  - `README.md:182` (Supported Markdown): "`![](img.jpg)` | Images | **First = cover**".
  - `skills/x-article-publisher/scripts/parse_markdown.py` — implements the cover/content separation logic.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Safe by design — draft only; cross-platform clipboard
- **Wiki says:** The skill only saves drafts, never auto-publishes; clipboard works on macOS (pyobjc-framework-Cocoa) and Windows (pywin32 + clip-util).
- **Source evidence:**
  - `README.md:55`: "**Safe by Design**: Only saves as draft, never publishes automatically."
  - `README.md:52`: "**Smart Wait Strategy**: Conditions return immediately when met, no wasted wait time."
  - `SKILL.md:15-17`: "macOS: `pip install Pillow pyobjc-framework-Cocoa`", "Windows: `pip install Pillow pywin32 clip-util`".
  - `skills/x-article-publisher/scripts/copy_to_clipboard.py` — cross-platform clipboard implementation with platform detection.
  - `.claude-plugin/plugin.json`: `"platforms": ["macos"]` — macOS primary; Windows documented secondary.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: Divider + Mermaid support (v1.2) and plugin marketplace install
- **Wiki says:** Markdown `---` dividers are inserted via the X Articles Insert menu; Mermaid diagrams convert via `mmdc`; installation supports the `/plugin marketplace add` method.
- **Source evidence:**
  - `README.md:298-302` (v1.2.0 changelog): "**Divider support**: Detect `---` in Markdown, insert via X Articles menu"; "**Mermaid support**: Documentation for using `mmdc` to convert diagrams"; "**Windows support**: Cross-platform clipboard operations (pywin32 + clip-util)".
  - `README.md:182-184` (Supported Markdown): "`---` | Dividers | Via Insert menu (v1.2)"; "Tables | PNG images | Via table_to_image.py (v1.2)"; "Mermaid | PNG images | Via mmdc CLI (v1.2)".
  - `README.md:113-121` (Method 2 — Plugin Marketplace): "`/plugin marketplace add wshuyi/x-article-publisher-skill`", "`/plugin install x-article-publisher@wshuyi/x-article-publisher-skill`".
  - `SKILL.md:18`: "For Mermaid diagrams: `npm install -g @mermaid-js/mermaid-cli`".
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[x-article-publisher-skill]] -- Main wiki entry
- [[outreachmagic]] -- Marketing outreach platform
- [[skills]] -- General agent skill system
- [[reverse-skill]] -- Companion skill

## Cross-project

- [[skills.codegraph-verify]] -- Skills system verification
- [[reverse-skill.codegraph-verify]] -- Reverse skill verification
- [[outreachmagic.codegraph-verify]] — Outreach platform verification
