---
name: x-article-publisher-skill-codegraph-verify
tags: [x-article-publisher-skill, codegraph-verify, skill, x-twitter]
description: "Codegraph Verification: x-article-publisher-skill — validating wiki claims against indexed source code"
source: sources/x-article-publisher-skill/
date: 2026-07-12
---

# Codegraph Verification: x-article-publisher-skill

**Date:** 2026-07-12

## Claim 1: Claude Code skill for publishing Markdown articles to X (Twitter) Articles
- **Wiki says:** "The X Article Publisher Skill is a Claude Code skill that automates publishing Markdown articles to X (Twitter) Articles with one command."

- **Source evidence:**
  - `skills/x-article-publisher/SKILL.md` line 1-4: frontmatter with `name: x-article-publisher` and description: "Publish Markdown articles to X (Twitter) Articles editor with proper formatting. Use when user wants to publish a Markdown file/URL to X Articles."
  - `README.md` line 5: "Publish Markdown articles to X (Twitter) Articles with one command. Say goodbye to tedious rich text editing."
  - `.claude-plugin/plugin.json` — Plugin manifest with name `x-article-publisher`, version `1.1.0`, description confirming the same purpose.
  - `docs/GUIDE.md` — Detailed usage guide for the skill.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Block-index image positioning with reverse insertion order
- **Wiki says:** "v1.1+: Images are placed at precise positions using element indices rather than fragile text matching. Images are inserted from highest to lowest block index to prevent position shifts."

- **Source evidence:**
  - `README.md` lines 60-67: "What's New in v1.1.0" table documents: "Image positioning: Text matching (fragile) → Block index (precise)" and "Insertion order: Sequential → Reverse (high→low)."
  - `README.md` lines 67-73: "Why Block-Index?" section explains: "Previously, images were positioned by matching surrounding text — this failed when... Now, each image has a `block_index` indicating exactly which block element it follows."
  - `skills/x-article-publisher/SKILL.md` line 29: `parse_markdown.py` returns "content_images" and "**dividers** (with block_index for positioning)."
  - `skills/x-article-publisher/scripts/parse_markdown.py` — Python script that extracts content_images with block_index for precise positioning.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Three Python helper scripts for markdown parsing, clipboard, and table-to-image
- **Wiki says:** "The project is structured with a skill directory containing the main SKILL.md instructions and Python helper scripts for Markdown parsing, cross-platform clipboard operations, and table-to-image rendering."

- **Source evidence:**
  - `skills/x-article-publisher/scripts/` directory contains exactly 3 Python scripts: `parse_markdown.py`, `copy_to_clipboard.py`, `table_to_image.py`.
  - `skills/x-article-publisher/SKILL.md` lines 22-46 document each script with usage examples:
    - `parse_markdown.py` (line 24): "Parse Markdown and extract structured data" — JSON output with title, cover_image, content_images, dividers, html, total_blocks.
    - `copy_to_clipboard.py` (line 31): "Copy image or HTML to system clipboard (cross-platform)" — supports image (macOS pyobjc-framework-Cocoa, Windows pywin32+clip-util) and HTML modes.
    - `table_to_image.py` (line 41): "Convert Markdown table to PNG image" using Pillow.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Cover image extraction and separate content image positioning
- **Wiki says:** "First image in the Markdown is automatically extracted and uploaded as the article cover. Content images are separated with precise positioning."

- **Source evidence:**
  - `skills/x-article-publisher/SKILL.md` line 28: `parse_markdown.py` returns JSON with "title, cover_image, content_images, dividers" — confirming separation of cover from content images.
  - `README.md` line 52: "Block-Index Positioning (v1.1): Precise image placement using element indices."
  - `skills/x-article-publisher/scripts/parse_markdown.py` — Implements the extraction and separation logic.
  - `README.md` lines 113-121: Supported Markdown table shows `![](img.jpg)` with note "First = cover" confirming cover extraction.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Safe by design — saves as draft only, never auto-publishes
- **Wiki says:** "Only saves articles as drafts in the X Articles editor. Never publishes automatically, giving the user final review before going live."

- **Source evidence:**
  - `README.md` line 55: "Safe by Design: Only saves as draft, never publishes automatically."
  - `README.md` lines 42-45: Architect diagram shows pipeline end: "X Articles Editor (browser automation) → Draft Saved (never auto-publishes)."
  - `skills/x-article-publisher/SKILL.md` — Skill instructions for interacting with X Articles editor explicitly work through the draft save workflow, not publish.
  - The SKILL.md documentation for the Playwright MCP interactions targets the X Articles editor interface for draft saving, confirming no auto-publish behavior.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Cross-platform clipboard (macOS and Windows) with platform-specific packages
- **Wiki says:** "Supports both macOS (pyobjc-framework-Cocoa) and Windows (pywin32 + clip-util). Linux support is in progress."

- **Source evidence:**
  - `skills/x-article-publisher/SKILL.md` lines 15-17: Prerequisites document platform-specific packages: "macOS: `pip install Pillow pyobjc-framework-Cocoa`", "Windows: `pip install Pillow pywin32 clip-util`."
  - `skills/x-article-publisher/scripts/copy_to_clipboard.py` — Cross-platform clipboard implementation with platform detection.
  - `.claude-plugin/plugin.json` line 21: `"platforms": ["macos"]` — confirming macOS as primary supported platform, with Windows as documented secondary. Linux not listed, confirming "in progress" status.
  - README.md line 37: "Cross-Platform (v1.2) — Supports both macOS and Windows. Linux support is in progress."

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Divider support and Mermaid diagram conversion
- **Wiki says:** "v1.2: Markdown `---` dividers are detected and inserted via the X Articles Insert menu. Mermaid diagram support via optional `mmdc` CLI."

- **Source evidence:**
  - `README.md` line 7: "v1.2.0 — Now with divider support, table-to-image, Mermaid support, and cross-platform clipboard."
  - `README.md` lines 32-33: "Divider Support (v1.2) — Markdown `---` dividers are detected and inserted via the X Articles Insert menu."
  - `README.md` line 34: "Mermaid Diagram Support (v1.2) — Optional integration with `mmdc` CLI for converting Mermaid diagrams to images before upload."
  - `skills/x-article-publisher/SKILL.md` line 18: Mermaid prerequisite: "For Mermaid diagrams: `npm install -g @mermaid-js/mermaid-cli`."
  - `skills/x-article-publisher/SKILL.md` line 29: `parse_markdown.py` returns "dividers (with block_index for positioning)" confirming divider support.
  - `README.md` lines 113-124: Supported Markdown table shows `---` with note "Via Insert menu (v1.2)" and "Mermaid → PNG images via mmdc CLI (v1.2)."

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
