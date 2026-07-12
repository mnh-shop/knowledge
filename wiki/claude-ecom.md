---
name: claude-ecom
tags: [claude-ecom, claude-code, ecommerce, automation, shopify]
description: "E-commerce automation skills and tools for Claude Code"
source: sources/claude-ecom/
---

# Claude Ecom

| Field | Value |
|---|---|
| **Origin** | [nicholasgriffintn/claude-ecom](https://github.com/nicholasgriffintn/claude-ecom) |
| **Source** | `sources/claude-ecom/` |
| **Repomix** | `raw/claude-ecom/claude-ecom.xml` |
| **Codegraph** | `graphs/claude-ecom/` |

## Overview

Claude Ecom is an e-commerce data analytics toolkit designed for Claude Code that transforms raw order/sales CSV data into structured business reviews with KPI decomposition, prioritized findings, and concrete next actions. It follows a hybrid architecture where Python handles deterministic computation (KPIs, health checks, scoring) and Claude handles business interpretation and narrative generation.

The project ships as a Claude Code plugin (`claude-ecom@claude-ecom`) with a self-bootstrapping Python backend installed into `~/.local/share/claude-ecom/`. It can also run as a standalone CLI via `pip install claude-ecom`. Inspired by [claude-ads](https://github.com/AgriciDaniel/claude-ads).

## Key Features

- **Automated Business Reviews** — Single-command generation of comprehensive `REVIEW.md` reports that read like a consultant wrote them. Executive summary → multi-horizon dashboard → KPI trees with 🔴/🟢 signals → findings with "what / why / what to do" → prioritized action plan with deadlines, success metrics, and guardrails.
- **Multi-Horizon Analysis** — Automatically selects 30-day / 90-day / 365-day trailing windows. Each period gets its own review JSON and markdown report. Focused analysis available via `/claude-ecom:ecom review 30d` etc.
- **KPI Decomposition Engine** — Python engine (`review_engine.py`) computes trailing-window KPIs including revenue trends, order counts, AOV, customer acquisition, repeat purchase rates, and cohort behavior. Health checks classify signals as pass/watch/fail with impact estimation.
- **Natural Language Queries** — Ask questions like "how was retention last month?" and Claude invokes the skill automatically, routing the question through the Python compute engine.
- **Plugin-First Distribution** — Install as a Claude Code plugin via `/plugin marketplace add takechanman1228/claude-ecom` and `/plugin install claude-ecom@claude-ecom`. Includes SessionStart hook for auto-bootstrapping.
- **Comprehensive Health Checks** — Python module (`checks.py`) defines check result types with three categories (Revenue, Customer, Product) and semantic snake_case check IDs. Each check returns pass/watch/fail with impact scoring and action builders.
- **Cohort Analysis** — The `cohort.py` module provides retention cohort tracking to understand customer lifecycle behavior and repeat purchase patterns over time.

## Architecture

Claude Ecom follows a strict separation of concerns:

```
Orders CSV → Python Engine (deterministic) → review.json → Claude (interpretation) → REVIEW.md
```

The Python package (`claude_ecom/`) contains:
- **`cli.py`** — Click-based CLI with `ecom review` and `ecom validate` commands
- **`loader.py`** — CSV/Parquet data loading with flexible column name matching
- **`periods.py`** — Trailing window computation and data coverage utilities
- **`review_engine.py`** — Unified period-based review builder for 30d/90d/365d
- **`scoring.py`** — Health scoring, top issue identification, action candidate generation
- **`metrics.py`** — Core metric computations (revenue, orders, AOV, customer counts)
- **`pricing.py`** — Pricing analysis and discount impact evaluation
- **`product.py`** — Product-level performance analysis
- **`cohort.py`** — Customer retention cohort tracking

The skill layer (`skills/ecom/SKILL.md`) provides LLM instructions with 9 reference files loaded on-demand for business interpretation context.

## Usage

### Quick Start (Plugin)

```bash
# In Claude Code:
/plugin marketplace add takechanman1228/claude-ecom
/plugin install claude-ecom@claude-ecom

# Drop your orders CSV into the project and run:
/claude-ecom:ecom review
```

### CLI Only (No Claude Code)

```bash
pip install claude-ecom
ecom review orders.csv
```

### Commands

| Command | Description |
|---------|-------------|
| `/claude-ecom:ecom review` | Full business review — auto-selects 30d/90d/365d |
| `/claude-ecom:ecom review 30d` | Focus on 30-day trailing period |
| `/claude-ecom:ecom review How's retention?` | Ask a specific question |
| `ecom review orders.csv --period 90d` | CLI: 90-day period focus |

### Input Format

Any e-commerce/retail orders CSV with required columns: order ID, order date, customer ID/email, revenue (after discounts, before tax/shipping). Optional columns (quantity, SKU, discount amount) enable deeper analysis. Flexible column name matching means exact names aren't required.

### Roadmap

- Shopify API integration (skip CSV export)
- Weekly digest mode
- Multi-store comparison

## Related

- [[claude-seo]] — SEO optimization skills for Claude Code (complementary marketing automation)
- [[claude-ai-music-skills]] — AI music generation skills for Claude Code
- [[openai-skills]] — OpenAI skills collection with complementary automation patterns
- [[ai-marketing-claude-code-skills]] — AI marketing skills collection for Claude Code
- [[outreachmagic]] — Marketing outreach automation platform for go-to-market sequences
- [[skills]] — General agent skill system reference
