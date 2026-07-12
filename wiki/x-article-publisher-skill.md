---
name: x-article-publisher-skill
tags: [x-article-publisher-skill, skill, automation, twitter, social-media]
description: "Claude Code skill for publishing articles to X/Twitter"
source: sources/x-article-publisher-skill/
---

# X Article Publisher Skill

| Field | Value |
|---|---|
| **Origin** | [omarmoataz/x-article-publisher-skill](https://github.com/omarmoataz/x-article-publisher-skill) |
| **Source** | `sources/x-article-publisher-skill/` |
| **Repomix** | `raw/x-article-publisher-skill/x-article-publisher-skill.xml` |
| **Codegraph** | `graphs/x-article-publisher-skill/` |

## Overview

The X Article Publisher Skill is a Claude Code skill that enables AI agents to publish articles, threads, and content directly to X/Twitter. It provides a structured skill definition that Claude Code can invoke to compose and post content, manage threads, schedule posts, and analyze engagement metrics — all from within the agent's workflow.

## Key Features

- **Content Publishing** — Post single tweets and threaded content to X/Twitter
- **Article Threading** — Automatically split long-form content into coherent tweet threads
- **Scheduling** — Queue posts for future publication
- **Media Attachment** — Attach images, videos, and links to posts
- **Engagement Analytics** — Retrieve post performance metrics (likes, retweets, impressions)
- **Template Support** — Pre-defined posting templates for different content types

## Architecture

The skill is defined as a Claude Code skill package containing prompt templates, tool configurations, and authentication handlers. It wraps the X/Twitter API v2 endpoints behind a skill interface that agents can call using natural language commands or programmatic skill invocation.

## Related

- [[outreachmagic]] — Marketing outreach automation platform
- [[skills]] — General agent skill system reference
- [[claude-seo]] — SEO skills for Claude Code (complementary marketing)
- [[ai-marketing-claude-code-skills]] — AI marketing skills collection
