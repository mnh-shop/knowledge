---
name: x-article-publisher-skill
tags: [x-article-publisher-skill, skill, automation, twitter, social-media]
description: "Claude Code skill for publishing articles to X/Twitter"
source: sources/x-article-publisher-skill/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# X Article Publisher Skill

| Field | Value |
|---|---|
| **Origin** | [omarmoataz/x-article-publisher-skill](https://github.com/omarmoataz/x-article-publisher-skill) |
| **Source** | `sources/x-article-publisher-skill/` |
| **Repomix** | `raw/x-article-publisher-skill/x-article-publisher-skill.xml` |
| **Codegraph** | `graphs/x-article-publisher-skill/` |

## Overview

The X Article Publisher Skill is a Claude Code skill that automates publishing Markdown articles to X (Twitter) Articles with one command. It solves the painful manual process of converting Markdown to X's rich text editor — eliminating 15–20 minutes of manual formatting per article through browser automation via Playwright MCP.

At version 1.2.0, the skill supports divider insertion, table-to-image conversion, Mermaid diagram rendering, cross-platform clipboard operations (macOS and Windows), and YAML frontmatter handling. The core workflow: parse a Markdown file into structured data, open the X Articles editor via browser automation, paste formatted content via clipboard, insert images at precise block-index positions, and save as a draft — never auto-publishing. This achieves a 10x efficiency improvement, reducing total article publishing time from 20–30 minutes to 2–3 minutes.

The project is structured as a Claude Code plugin with a skill directory (`skills/x-article-publisher/`) containing the main SKILL.md instructions and Python helper scripts for Markdown parsing, cross-platform clipboard operations, and table-to-image rendering.

## Key Features

- **Rich Text Paste** — Convert Markdown to HTML and paste via clipboard with all formatting preserved (H2 headers, bold, italic, hyperlinks, blockquotes, ordered/unordered lists). No manual reformatting required.
- **Block-Index Image Positioning** (v1.1+) — Images are placed at precise positions using element indices rather than fragile text matching. Each image gets a `block_index` indicating exactly which block element it follows — deterministic and reliable even with similar content.
- **Reverse Insertion Order** — Images are inserted from highest to lowest block index to prevent position shifts caused by earlier insertions shifting subsequent indices. This ensures all images land at their intended positions.
- **Smart Wait Strategy** — Browser wait conditions return immediately when the target condition is met, rather than waiting for a fixed timeout. The `time` parameter is a maximum, not a fixed delay.
- **Cover Image Support** — First image in the Markdown is automatically extracted and uploaded as the article cover. Content images are separated with precise positioning.
- **Divider Support** (v1.2) — Markdown `---` dividers are detected and inserted via the X Articles Insert menu, supporting section separation within articles.
- **Table-to-Image Conversion** (v1.2) — Python script (`table_to_image.py`) converts Markdown tables to PNG images using Pillow, since X Articles does not support native table rendering.
- **Mermaid Diagram Support** (v1.2) — Optional integration with `mmdc` CLI for converting Mermaid diagrams to images before upload.
- **YAML Frontmatter Handling** (v1.2) — Automatically strips YAML frontmatter from Markdown files, keeping only the article content for publishing.
- **Safe by Design** — Only saves articles as drafts in the X Articles editor. Never publishes automatically, giving the user final review before going live.
- **Cross-Platform** (v1.2) — Supports both macOS (pyobjc-framework-Cocoa) and Windows (pywin32 + clip-util). Linux support is in progress.

## Architecture

The publishing pipeline follows a 7-step workflow:

```
Markdown File
     ↓ [1/7] Python parsing
Structured Data (title, images with block_index, HTML)
     ↓ [2/7-6/7] Playwright MCP browser automation
X Articles Editor
     ↓ [7/7] Draft saved (never auto-publishes)
     ↓
✅ Review and publish manually
```

The project structure:

```
x-article-publisher-skill/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── skills/
│   └── x-article-publisher/
│       ├── SKILL.md             # Skill instructions
│       └── scripts/
│           ├── parse_markdown.py    # Extracts title, cover, images with block_index
│           ├── copy_to_clipboard.py # Cross-platform clipboard (macOS + Windows)
│           └── table_to_image.py    # Markdown table → PNG conversion (v1.2)
├── docs/
│   └── GUIDE.md                 # Detailed usage guide
├── README.md
└── LICENSE
```

## Usage

### Requirements

| Requirement | Details |
|-------------|---------|
| Claude Code | [claude.ai/code](https://claude.ai/code) |
| Playwright MCP | Browser automation for X Articles editor |
| X Premium Plus | Required for X Articles feature |
| Python 3.9+ | With Pillow and platform-specific clipboard packages |
| OS | macOS or Windows |

### Installation

**Method 1: Git Clone**

```bash
git clone https://github.com/wshuyi/x-article-publisher-skill.git
cp -r x-article-publisher-skill/skills/x-article-publisher ~/.claude/skills/
```

**Method 2: Plugin Marketplace**

```bash
/plugin marketplace add wshuyi/x-article-publisher-skill
/plugin install x-article-publisher@wshuyi/x-article-publisher-skill
```

### Commands

```
# Natural language
Publish /path/to/article.md to X

# Skill invocation
/x-article-publisher /path/to/article.md
```

### Supported Markdown

| Syntax | Result | Notes |
|--------|--------|-------|
| `# H1` | Article title | Extracted, not in body |
| `## H2` | Section headers | Native support |
| `**bold**` | Bold text | Native support |
| `*italic*` | Italic text | Native support |
| `[text](url)` | Hyperlinks | Native support |
| `> quote` | Blockquotes | Native support |
| `![](img.jpg)` | Images | First = cover |
| `---` | Dividers | Via Insert menu (v1.2) |
| Tables | PNG images | Via table_to_image.py (v1.2) |
| Mermaid | PNG images | Via mmdc CLI (v1.2) |

## Related

- [[outreachmagic]] — Marketing outreach automation platform for multi-channel campaigns
- [[skills]] — General agent skill system reference for Claude Code
- [[reverse-skill]] — Companion skill with complementary workflow automation patterns
- [[claude-seo]] — SEO skills for Claude Code (complementary content marketing)
- [[ai-marketing-claude-code-skills]] — Marketing skills collection with content distribution workflows
