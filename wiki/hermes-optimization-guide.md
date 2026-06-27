---
name: hermes-optimization-guide
description: "26-part practical guide for the Nous Research Hermes Agent: setup, optimization, security, deployment, and local hardware across CLI, TUI, desktop, and 22+ chat platforms"
source: sources/hermes-optimization-guide/
tags: [acp, hermes-agent, cli, dashboard, desktop, developer-tools, docker, documentation, mcp, messaging, monitoring, multi-platform, optimization, plugin-sdk, security, storage, systemd, webhook]
---

# Hermes Optimization Guide

**Source:** `sources/hermes-optimization-guide/`

A comprehensive 26-part guide (25 numbered parts + one README-based SOUL.md section) for deploying, optimizing, and securing the [Nous Research Hermes Agent](https://github.com/NousResearch/hermes-agent). Model-agnostic -- the guide covers the harness, not specific weights. Current through Hermes Agent v0.16.0 (2026.6.5, "The Surface Release").

Unlike most guides, this one ships **working artifacts**: 13 installable skills, 5 opinionated config templates, Docker Compose stacks (Langfuse), systemd units, Caddyfile, cron schedules, a VPS bootstrap script, reference architectures, and even an interactive browser-based config wizard.

By Terp -- [Terp AI Labs](https://x.com/OnlyTerp).

## Key Features

- **26 guide parts** covering every aspect of a production Hermes deployment, from fresh install to multi-agent swarms
- **13 installable skills** in 3 categories (ops, dev, security) -- symlink into `~/.hermes/skills/` to activate
- **5 opinionated config templates**: minimum, telegram-bot, production, cost-optimized, security-hardened
- **4 reference architectures**: Homelab, Solo Developer ($25-70/mo), Small Agency, Road Warrior
- **One-command VPS bootstrap** (`scripts/vps-bootstrap.sh`) -- takes a fresh Debian 12 VPS to production: installs Hermes, Node.js, Caddy (auto-TLS), UFW, fail2ban, creates a `hermes` user, drops hardened systemd units, symlinks all skills, and seeds a cost-optimized config
- **Interactive config wizard** -- 8 questions in the browser, emits ready-to-drop `config.yaml`
- **Self-hosted Langfuse v3 stack** via Docker Compose (ClickHouse + MinIO + Redis)
- **6 Mermaid architecture diagrams**: top-level architecture, MCP integration flow, coding-agent delegation (OpenClaw), remote-sandbox sync, observability stack, security layers
- **Reproducible benchmarks** (cost + latency table across 12 models x 5 tasks)
- **CI pipeline**: markdown link check, yamllint, skill frontmatter validation, prettier (advisory)
- **Ecosystem directory** (`ECOSYSTEM.md`): curated MCP servers, coding-agent integrations, native Hermes plugins

## Architecture

The Hermes Agent is a **single-agent-through-multiple-surfaces** architecture. The guide documents the full stack:

```
Surfaces (Desktop app, CLI/TUI, Web admin panel, 22+ chat platforms)
    |
Gateway Router
    |
Model Router (cost + context + capability routing, fallback chains)
    |
Model Providers (cloud APIs, OpenAI-compatible, local: Ollama/LM Studio/llama.cpp, NVIDIA RTX/DGX Spark)
    |
Approval Layer (denylist, allowlist, quarantine, secrets redaction)
    |
Tools (Native tools, Nous Tool Gateway, MCP servers, Subagents, Coding Agents, Swarms)
    |
Memory (Vector DB, LightRAG knowledge graph, mem0 cloud)
    |
Audit Log (Local + Langfuse/Helicone/OpenTelemetry traces)
```

Key architectural patterns:
- **Model-agnostic harness** -- bring any weights; the guide is about infrastructure, not models
- **Surface parity** -- desktop, CLI, TUI, Telegram, and web dashboard all drive the same agent with shared config, sessions, skills, and memory
- **Approval-first security** -- multi-layer defense with denylists, allowlists, provenance labeling, MCP trust levels, and quarantine profiles
- **Three-tier memory**: persistent facts (memory), conversation recall (session_search), procedural memory (skill_manage) -- all local-first (SQLite + full-text search)
- **Durable execution via Kanban** -- work survives restarts, supports multi-agent swarms with root planner, parallel workers, gated verifier, and shared blackboard

## Guide Parts

| # | Part | Focus |
|---|------|-------|
| 1 | Setup | Install Hermes, configure provider, first-run walkthrough (includes Android/Termux) |
| -- | SOUL.md Personality | The Molty prompt, personality rules, how to fix a bland agent |
| 2 | OpenClaw Migration | Move skills, memory, config from predecessor agent framework |
| 3 | LightRAG | Graph RAG setup -- entity relationships, not just text similarity |
| 4 | Telegram Setup | Mobile access, voice memos, group chats |
| 5 | On-the-Fly Skills | Agent-curated reusable workflows |
| 6 | Context Compression | Silent context loss, compression thresholds, long session survival |
| 7 | Memory System | 3-tier architecture: persistent facts, conversation recall, procedural memory |
| 8 | Subagent Patterns | Orchestrator/worker delegation, ACP subagents, parallel execution |
| 9 | Custom Models | Grok OAuth, Bedrock, Azure, LM Studio, Gemini, Codex, OpenRouter routing, aliases, fallback chains |
| 10 | SOUL.md Anti-Patterns | What makes an agent annoying vs useful |
| 11 | Gateway Recovery | Crash detection, auto-recovery, health checks |
| 12 | Web Dashboard | Admin panel: channels, MCP catalog, credentials, webhooks, memory config, Debug Share |
| 13 | Tool Gateway | Nous-managed tools, `hermes proxy`, `x_search` |
| 14 | Fast Mode & Watchers | `/fast`, `/steer`, `/queue`, `watch_patterns`, `/compress` |
| 15 | New Platforms | Teams, LINE, SimpleX, Google Chat, QQBot, WeChat, Android/Termux |
| 16 | Backup & Debug | `hermes backup`/`import`, `/debug` bundler, `hermes debug share` |
| 17 | MCP Servers | stdio + HTTP transports, sampling, trust boundaries, writing custom servers |
| 18 | Coding Agents | Claude Code, Codex, Gemini CLI, OpenCode, Aider, Zed ACP, print-mode, Kanban, git isolation |
| 19 | Security Playbook | Prompt-injection defense, provenance labels, approval layers, secrets redaction, MCP trust model, hardline blocks |
| 20 | Observability & Cost | Langfuse, Helicone, OpenTelemetry/Phoenix, prompt caching, CDP spans, routing playbooks |
| 21 | Remote Sandboxes | SSH, Modal, Daytona, Vercel Sandbox, Fly Machines, E2B, diff-based sync-back |
| 22 | Latest Power Moves | Curator, TUI habits, context-file hygiene, plugins, dashboard Chat, cron chaining, 2026 upgrade checklist |
| 23 | Tenacity Stack | PyPI/lazy deps, `hermes proxy`, `/handoff`, durable Kanban, `/goal`, Checkpoints v2, no-agent cron, worker lanes, multi-agent swarms |
| 24 | Hermes Desktop App | Native macOS/Windows/Linux GUI, Cmd+K palette, drag-and-drop, model picker, remote gateway, voice, self-update |
| 25 | NVIDIA & Local Hardware | RTX/DGX Spark, OpenShell isolation, NemoClaw, model-agnostic local stack (Ollama/LM Studio/llama.cpp) |

## Templates

The repo ships production-grade infrastructure templates:

- **systemd**: hardened `hermes.service` (4G memory limit, strict system-call filtering, address-family restrictions, `ProtectSystem=strict`) and `hermes-dashboard.service` (1G memory limit)
- **Caddy**: auto-TLS reverse proxy with HSTS, basic auth for dashboard, body-size limits for webhooks, security headers
- **Docker Compose**: self-hosted Langfuse v3 stack (PostgreSQL + ClickHouse + MinIO + Redis) for LLM observability
- **cron**: 8 production cron jobs (nightly backup, weekly MCP audit, weekly bypass audit, weekly cost report, weekly dep audit, monthly secret rotation, daily injection sweep, disk watchdog)

## Skills

13 installable `SKILL.md` files organized by category:

- **ops**: `cost-report`, `daily-inbox-triage`, `hermes-weekly`, `nightly-backup`, `telegram-triage`, `weekly-dep-audit`
- **dev**: `meeting-prep`, `pr-review`, `release-notes`
- **security**: `audit-approval-bypass`, `audit-mcp`, `rotate-secrets`, `spam-trap`

## Interfaces

- **CLI** -- `hermes` command (chat, tools, config, cron, backup)
- **TUI** -- Terminal UI with live tool cards, steer, queueing, sticky composer
- **Web** -- Browser admin dashboard (hermes dashboard, port 8765)
- **Desktop** -- Native macOS/Windows/Linux GUI with streaming chat, command palette, drag-and-drop
- **Chat platforms** -- 22+ including Telegram, Discord, Slack, Teams, LINE, WeChat, iMessage, Google Chat, QQ, SimpleX, webhooks, ntfy
- **ACP** -- Agent Communication Protocol for subagent delegation
- **MCP** -- Model Context Protocol for external tool integration (stdio + HTTP transports)
- **API** -- OpenAI-compatible proxy (`hermes proxy`), REST webhooks, WebSocket remote backend
- **Cron** -- Agent-driven cron scheduler with `no_agent` mode for deterministic jobs

## Related

- [[hermes-agent]] -- The Nous Research Hermes Agent itself
- [[openclaw]] -- Predecessor agent framework (migration path documented in Part 2)
- [[n8n-workflows]] -- Alternative automation workflows
- [LightRAG](https://github.com/HKUDS/LightRAG) -- Graph RAG memory system
- [Langfuse](https://langfuse.com) -- LLM observability (self-hosted stack in templates)
- [[mcp]] -- Model Context Protocol ecosystem

## Tags

`documentation` `optimization` `ai-llm` `container` `systemd` `automation` `security` `developer-tools` `multi-platform` `cli` `rest-api` `mcp` `monitoring`
