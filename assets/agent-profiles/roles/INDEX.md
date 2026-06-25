---
tags: [use-cases, agent-profiles]
---

# OpenClaw Use Case Patterns Catalog

A curated index of 42 real-world use case patterns for OpenClaw agents, grouped by domain. Each entry describes the pattern, key capabilities, and primary integrations.

Source: `sources/awesome-openclaw-usecases/usecases/` (42 files)

---

## Productivity & Tasks

### 1. Autonomous Project Management with Subagents
**File:** `autonomous-project-management.md`
**What it does:** Decentralized project management pattern where subagents work autonomously on tasks, coordinating through a shared `STATE.yaml` file rather than a central orchestrator. Supports parallel execution, self-documenting state, and thin main-agent overhead.
**Key integrations:** `sessions_spawn` / `sessions_send`, Git, file system (STATE.yaml)
**Based on:** Nicholas Carlini's autonomous coding agent approach

### 2. Inbox Declutter
**File:** `inbox-declutter.md`
**What it does:** Automatically reads newsletter emails from the past 24 hours and compiles a digest of the most important bits with links. Learns preferences over time for better curation.
**Key integrations:** Gmail OAuth (gog CLI), cron

### 3. Personal Knowledge Base (RAG)
**File:** `knowledge-base-rag.md`
**What it does:** Builds a searchable knowledge base from URLs dropped into Telegram or Slack. Auto-ingests articles, tweets, YouTube transcripts, and PDFs. Supports semantic search across all saved content.
**Key integrations:** knowledge-base skill, `web_fetch`, Telegram/Slack

### 4. Second Brain
**File:** `second-brain.md`
**What it does:** Zero-friction memory capture system via text message (Telegram, iMessage, Discord). Backed by a custom Next.js dashboard with global search (Cmd+K). No folders or tags -- just text and search.
**Key integrations:** Telegram, iMessage, Discord, Next.js (auto-built by agent)

### 5. Semantic Memory Search
**File:** `semantic-memory-search.md`
**What it does:** Adds vector-powered semantic search on top of OpenClaw's markdown memory files using memsearch. Combines dense vectors + BM25 full-text with RRF reranking. SHA-256 content hashing prevents re-embedding unchanged files.
**Key integrations:** memsearch (Python CLI), Milvus vector DB, OpenAI/Google/Voyage/Ollama embeddings

### 6. Todoist Task Manager: Agent Task Visibility
**File:** `todoist-task-manager.md`
**What it does:** Syncs agent internal reasoning and progress logs directly to Todoist for visibility into long-running workflows. Creates tasks in sections (In Progress, Waiting, Done), posts plan in descriptions, and streams sub-step completions as comments.
**Key integrations:** Todoist REST API, bash scripts (todoist_api.sh, sync_task.sh, add_comment.sh)

### 7. Automated Meeting Notes & Action Items
**File:** `meeting-notes-action-items.md`
**What it does:** Converts meeting transcripts into structured summaries with action items, then automatically creates tasks in Jira, Linear, Todoist, or Notion with assigned owners and deadlines. Posts summaries to Slack/Discord.
**Key integrations:** Jira, Linear, Todoist, Notion, Slack, Discord, Otter.ai, Fireflies.ai

### 8. Project State Management (Event-Driven)
**File:** `project-state-management.md`
**What it does:** Replaces Kanban with an event-driven system that logs progress, blockers, decisions, and pivots conversationally. Captures context behind every state change. Auto-generates daily standup summaries with linked git commits.
**Key integrations:** PostgreSQL/SQLite, GitHub CLI, Discord/Telegram

### 9. Local CRM Framework with DenchClaw
**File:** `local-crm-framework.md`
**What it does:** One-command (`npx denchclaw`) install of a full local CRM platform with DuckDB database, web UI, browser automation, and multiple views (Table, Kanban, Calendar, Timeline). Natural language CRM management.
**Key integrations:** DenchClaw, DuckDB, Chromium browser automation, Chrome profile cloning, Telegram

### 10. Personal CRM with Automatic Contact Discovery
**File:** `personal-crm.md`
**What it does:** Daily cron scans Gmail and Google Calendar for new contacts and interactions. Stores structured contact data. Provides daily meeting prep briefings with relationship context. Natural language query interface.
**Key integrations:** gog CLI (Gmail, Calendar), SQLite, Telegram

### 11. Habit Tracker & Accountability Coach
**File:** `habit-tracker-accountability-coach.md`
**What it does:** Proactive daily check-ins via Telegram or SMS for user-defined habits. Tracks streaks, adapts tone based on performance, and generates weekly reports with pattern analysis.
**Key integrations:** Telegram, Twilio SMS, cron, Google Sheets (optional)

### 12. Health & Symptom Tracker
**File:** `health-symptom-tracker.md`
**What it does:** Food and symptom logging via Telegram with 3x daily reminders. Weekly pattern analysis to identify potential trigger foods and time-of-day correlations.
**Key integrations:** Telegram, cron, markdown log file

### 13. Multi-Channel Personal Assistant
**File:** `multi-channel-assistant.md`
**What it does:** Consolidates tasks, calendar, email, file storage, and project management into a single AI assistant. Telegram topic-based routing for different contexts (config, updates, video-ideas, CRM, earnings, knowledge-base).
**Key integrations:** gog CLI (Google Workspace), Slack, Todoist, Asana, Telegram

---

## Content Creation & Media

### 14. AI Video Editing via Chat
**File:** `ai-video-editing.md`
**What it does:** Conversational video editing -- trim, cut, merge clips, add background music with audio ducking, generate subtitles (50+ languages), color grade, crop to vertical formats, batch process multiple files.
**Key integrations:** video-editor-ai skill, ai-subtitle-generator skill

### 15. Multi-Agent Content Factory
**File:** `content-factory.md`
**What it does:** Chained agents inside Discord handling research, writing, and visual assets. Research agent scans trending stories, Writing agent produces scripts/drafts, Thumbnail agent generates AI cover images. Runs automatically on schedule.
**Key integrations:** Discord, `sessions_spawn` / `sessions_send`, x-research-v2, knowledge-base, local image generation (Nano Banana)

### 16. Podcast Production Pipeline
**File:** `podcast-production-pipeline.md`
**What it does:** End-to-end podcast production from topic to publish-ready assets. Generates guest research, episode outlines, timestamped show notes, SEO descriptions, and social media promotion kits for X, LinkedIn, and Instagram.
**Key integrations:** Web search, file system, Slack/Discord/Telegram, `sessions_spawn`

### 17. YouTube Content Pipeline
**File:** `youtube-content-pipeline.md`
**What it does:** Automated content scouting and research pipeline for daily YouTube creators. Hourly cron scans breaking AI news across web and X/Twitter, maintains 90-day video catalog with semantic dedup, creates Asana cards with full outlines from shared links.
**Key integrations:** x-research-v2, knowledge-base, Asana, gog CLI (YouTube Analytics), SQLite with vector embeddings, Telegram, Slack

### 18. LaTeX Paper Writing
**File:** `latex-paper-writing.md`
**What it does:** Collaborative LaTeX writing assistant with instant PDF compilation (pdflatex/xelatex/lualatex). Starter templates for article, IEEE, beamer, Chinese article. Bibliography support with BibTeX/BibLaTeX.
**Key integrations:** latex-compiler skill, Prismer Docker container (TeX Live)

### 19. Market Research & Product Factory
**File:** `market-research-product-factory.md`
**What it does:** Mines Reddit and X for real user pain points using the Last 30 Days skill, surfaces product opportunities, then has OpenClaw build an MVP solution. Full research-to-product pipeline.
**Key integrations:** Last 30 Days skill, Telegram/Discord

---

## Communication

### 20. Custom Morning Brief
**File:** `custom-morning-brief.md`
**What it does:** Sends a fully customized morning briefing at a scheduled time via Telegram, Discord, or iMessage. Includes overnight news, to-do list review, creative output (full scripts/email drafts), and proactive task recommendations.
**Key integrations:** Telegram, Discord, iMessage, Todoist/Apple Reminders/Asana, x-research-v2

### 21. Multi-Agent Specialized Team (Solo Founder Setup)
**File:** `multi-agent-team.md`
**What it does:** Multiple specialized agents with distinct roles (Strategy Lead, Business Analyst, Marketing, Developer), personalities, and model assignments. Controlled through a single Telegram group with tag-based routing. Shared memory with private contexts per agent.
**Key integrations:** Telegram, `sessions_spawn` / `sessions_send`, mixed model providers (Claude Opus, Sonnet, Gemini, Codex), shared file system

### 22. Phone-Based Personal Assistant (ClawdTalk)
**File:** `phone-based-personal-assistant.md`
**What it does:** Turns any phone into a gateway to your AI assistant via voice calls. Access calendar reminders, Jira updates, and web search by calling a phone number. Hands-free voice interaction while driving or walking.
**Key integrations:** ClawdTalk, Telnyx, Google Calendar, Jira, web search

### 23. Phone Call Notifications (clawr.ing)
**File:** `phone-call-notifications.md`
**What it does:** Agent calls your real phone number when something is urgent enough -- price alerts, urgent emails, appointment reminders. Two-way conversation, not a robocall. Works with heartbeat checks, cron, or event triggers.
**Key integrations:** clawr.ing skill, cron/heartbeat, 100+ country PSTN coverage

### 24. Event Guest Confirmation
**File:** `event-guest-confirmation.md`
**What it does:** Iterates through a guest list and calls each person using SuperCall with an AI persona (event coordinator). Confirms attendance, collects dietary needs and plus-ones, compiles results into a summary. Sandboxed voice agent prevents prompt injection.
**Key integrations:** SuperCall plugin, Twilio, OpenAI Realtime API, ngrok

### 25. Multi-Channel AI Customer Service Platform
**File:** `multi-channel-customer-service.md`
**What it does:** Unified AI-powered inbox across WhatsApp Business, Instagram DMs, Gmail, and Google Reviews. Auto-responds to FAQs and appointment requests, escalates complex issues. Test mode for client demos.
**Key integrations:** WhatsApp Business API, Instagram Graph API, gog CLI (Gmail), Google Business Profile API

---

## DevOps, Cloud & Infrastructure

### 26. Self-Healing Home Server & Infrastructure Management
**File:** `self-healing-home-server.md`
**What it does:** Persistent infrastructure agent with SSH access and automated cron jobs. Detects, diagnoses, and fixes issues autonomously (restart pods, scale resources, fix configs). Manages Terraform, Ansible, and Kubernetes manifests. Runs 15+ scheduled jobs including health monitoring, email triage, knowledge extraction, and security auditing.
**Key integrations:** SSH, kubectl, Terraform, Ansible, 1Password CLI, gog CLI, Obsidian, TruffleHog, K3s, Gitea

### 27. OpenClaw + n8n Workflow Orchestration
**File:** `n8n-workflow-orchestration.md`
**What it does:** Proxy pattern where OpenClaw delegates all external API interactions to n8n workflows via webhooks. Credential isolation (API keys live in n8n's credential store), visual debugging, lockable workflows, and audit trail. Deterministic sub-tasks don't burn LLM tokens.
**Key integrations:** n8n API, Docker (openclaw-n8n-stack), 400+ n8n integrations

### 28. Dynamic Dashboard with Sub-agent Spawning
**File:** `dynamic-dashboard.md`
**What it does:** Live dashboard that spawns sub-agents to fetch data from multiple sources in parallel (APIs, databases, GitHub, social media). Aggregates into formatted updates on Discord or HTML. Historical trends in PostgreSQL with alert thresholds.
**Key integrations:** GitHub CLI, bird (Twitter), PostgreSQL, Discord, Canvas, cron

---

## Research & Knowledge

### 29. arXiv Paper Reader
**File:** `arxiv-paper-reader.md`
**What it does:** Fetches any arXiv paper by ID and converts LaTeX to clean text. Browse paper sections before reading, quick-scan abstracts across multiple papers, ask for summaries/comparisons/critiques. Results cached locally.
**Key integrations:** arxiv-reader skill (arxiv_fetch, arxiv_sections, arxiv_abstract)

### 30. HF Papers Research Discovery
**File:** `hf-papers-research-discovery.md`
**What it does:** Browse trending papers on Hugging Face sorted by upvotes, search by keyword, get full metadata (abstract, authors, GitHub repos, upvotes, AI summaries), read community discussions, deep-read full LaTeX source via arXiv.
**Key integrations:** hf-papers skill, arxiv-source skill

---

## Financial

### 31. AI-Powered Earnings Tracker
**File:** `earnings-tracker.md`
**What it does:** Weekly Sunday preview of upcoming earnings calendar for tech/AI companies. Scheduled one-shot cron jobs for each earnings date. After each report, searches for results and delivers formatted summary (beat/miss, revenue, EPS, AI highlights).
**Key integrations:** `web_search`, cron, Telegram

### 32. Polymarket Autopilot: Automated Paper Trading
**File:** `polymarket-autopilot.md`
**What it does:** Automated paper trading on Polymarket with configurable strategies (TAIL trend-following, BONDING contrarian, SPREAD arbitrage). Tracks portfolio performance, P&L, and win rate. Daily summaries with trade logs and market insights.
**Key integrations:** Polymarket API, PostgreSQL/SQLite, Discord, cron, sub-agent spawning

---

## Social Media & Marketing

### 33. X Account Analysis
**File:** `x-account-analysis.md`
**What it does:** Qualitative analysis of X account performance beyond basic analytics. Identifies patterns behind viral posts, topics driving engagement, and reasons for performance variance.
**Key integrations:** Bird skill (X/Twitter API)

### 34. X/Twitter Automation from Chat
**File:** `x-twitter-automation.md`
**What it does:** Full X/Twitter automation via chat -- post tweets, reply, like, retweet, follow, DM, search, extract data (followers/likers/retweeters), run giveaways with configurable filters, monitor accounts for new activity.
**Key integrations:** TweetClaw plugin (@xquik/tweetclaw), managed X API

### 35. Daily Reddit Digest
**File:** `daily-reddit-digest.md`
**What it does:** Daily digest of top performing posts from favorite subreddits. Browsing hot/new/top, search by topic, pull comment threads. Read-only -- no posting or voting. Learns preferences over time.
**Key integrations:** reddit-readonly skill, memory system

### 36. Daily YouTube Digest
**File:** `daily-youtube-digest.md`
**What it does:** Daily personalized summary of new videos from favorite YouTube channels. Fetches transcripts via TranscriptAPI.com and summarizes key insights. Supports channel-based and keyword-based digests. Deduplicates via seen-videos.txt.
**Key integrations:** youtube-full skill (TranscriptAPI.com)

### 37. Multi-Source Tech News Digest
**File:** `multi-source-tech-news-digest.md`
**What it does:** Four-layer data pipeline aggregating from 46 RSS feeds, 44 Twitter/X KOLs, 19 GitHub repos, and 4 web searches (Brave API). Quality-scoring with dedup, delivered to Discord, email, or Telegram. Fully customizable sources.
**Key integrations:** tech-news-digest skill, gog (optional), X Bearer Token, Brave Search API, GitHub token

---

## Development & Building

### 38. Pre-Build Idea Validator
**File:** `pre-build-idea-validator.md`
**What it does:** Before any code is written, scans 5 data sources (GitHub, Hacker News, npm, PyPI, Product Hunt) and returns a `reality_signal` score (0-100). High score = stop and differentiate, low score = proceed. Prevents solving already-solved problems.
**Key integrations:** idea-reality-mcp (MCP server)

### 39. Goal-Driven Autonomous Tasks (Overnight Mini-App Builder)
**File:** `overnight-mini-app-builder.md`
**What it does:** Brain dump goals once; agent autonomously generates, schedules, and completes 4-5 daily tasks that advance those goals. Builds surprise mini-app MVPs overnight. Includes Kanban board and append-only task log to avoid race conditions.
**Key integrations:** Telegram/Discord, `sessions_spawn`/`sessions_send`, Next.js, file system

### 40. Autonomous Educational Game Development Pipeline
**File:** `autonomous-game-dev-pipeline.md`
**What it does:** "Bugs First" policy game developer agent that autonomously manages the full lifecycle of HTML5 educational games. Produces 1 game or bugfix every 7 minutes. Round-robin queue balancing across age groups. Git workflow with feature branches.
**Key integrations:** Git, HTML5/CSS3/JS, development-queue.md, games-list.json, CHANGELOG.md

---

## Multi-Domain / Foundation

### 41. OpenClaw as Desktop Cowork (AionUi)
**File:** `aionui-cowork-desktop.md`
**What it does:** Desktop Cowork UI running OpenClaw alongside 12+ other agents (Claude Code, Codex, Qwen Code). Remote rescue via Telegram/WebUI when OpenClaw is down. MCP config once, shared by all agents. AionUi cron for 24/7 scheduled tasks.
**Key integrations:** AionUi, Telegram, WebUI, Lark, DingTalk, multiple model providers

### 42. Family Calendar Aggregation & Household Assistant
**File:** `family-calendar-household-assistant.md`
**What it does:** Aggregates all family calendars into a single morning briefing. Ambient message monitoring detects appointments in texts and auto-creates calendar events with driving buffers. Household inventory tracking with photo-based input via vision model. Deduplicated grocery coordination.
**Key integrations:** Google Calendar, Apple Calendar (EventKit), iMessage, Telegram/Slack, OCR/vision, file system

---

## Source Index

All patterns are documented in the `awesome-openclaw-usecases` collection:

```
sources/awesome-openclaw-usecases/usecases/
```

Each `.md` file contains the full pattern including pain point, what it does, skills needed, setup instructions, key insights, and related links.

Skill categories referenced by these use cases are cataloged at:

```
sources/awesome-openclaw-skills/categories/
```
