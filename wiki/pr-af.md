---
name: pr-af
tags: [agentfield, cli, code-review, container, github, openrouter, pydantic, python, wiki, pr-af]
description: "Agentic code review system on AgentField — #1 on Martian Code-Review-Bench for open-source tools with multi-phase cognitive pipeline"
source: sources/pr-af/
verification_date: 2026-07-30
verified_by: codegraph-verify
---

# PR-AF — Agentic Code Review

| Field | Value |
|---|---|
| **Origin** | [Agent-Field/pr-af](https://github.com/Agent-Field/pr-af) |
| **License** | Apache 2.0 |
| **Stack** | Python 3.11+, AgentField SDK, FastAPI, Pydantic, OpenRouter (opt-in Go port) |
| **Deployment** | AgentField `af install`, GitHub Actions label trigger, Docker Compose, Railway |
| **Source** | `sources/pr-af/` |

## What is it?

An agentic code review system built on [[agentfield]] that achieved #1 ranking on the Martian Code-Review-Bench for open-source tools. It implements a multi-phase cognitive pipeline with evidence grounding — dynamically compiling review dimensions (4 per review) through semantic, mechanical, and systemic lenses before producing structured, actionable reviews.

Each review is grounded in specific code evidence with line-level citations, produced by a pipeline that decomposes the review task into focused sub-tasks handled by specialized sub-agents.

## Key Features

- **#1 Open-Source Code Reviewer:** Top-ranked open-source tool on the Martian Code-Review-Bench — 0.706 golden recall across 42 compared tools.
- **Multi-Phase Cognitive Pipeline:** Decomposes code review into a 7-phase pipeline — each phase handled by specialized modules before synthesis.
- **Evidence Grounding:** Every finding cites specific lines and files with verifiable evidence — no vague or hallucinated feedback.
- **Dynamic Review Dimensions:** The pipeline compiles review dimensions per PR, evaluating the diff through **semantic, mechanical, and systemic** lenses; output reports `review_dimensions: 4`.
- **AgentField Native:** Built on the AgentField SDK, leveraging its multi-agent orchestration and control plane.
- **GitHub Integration:** Primary trigger is a GitHub Actions workflow that fires on the `pr-af` label; also triggerable via `af call` or direct curl to the API.
- **Structured Output:** Produces structured review reports via Pydantic models for downstream processing.
- **Benchmark Package:** Full reproduction suite shipped at `benchmark/martian-code-review-bench` (results, judge verdicts, scripts); architecture deep-dive in `docs/ARCHITECTURE.md`.
- **Go Port (Opt-In):** Ships a separate Go implementation registering as `pr-af-go` on `:8007`, runnable alongside the default Python `pr-af` node.

## Tech Stack

| Component | Technology |
|---|---|
| **Language** | Python 3.11+ (default), Go (opt-in port) |
| **Agent Framework** | AgentField SDK |
| **Web Framework** | FastAPI |
| **Validation** | Pydantic |
| **AI Models** | OpenRouter (multi-provider access: DeepSeek-class, GLM-5.2, Opus-class) |
| **Deployment** | `af install`, GitHub Actions, Docker Compose, Railway |

## Deployment

### AgentField Install (Recommended)

```bash
af install https://github.com/Agent-Field/pr-af
af run pr-af
```

Installs PR-AF straight from GitHub into an existing AgentField control plane — no clone, no local setup. On first `af run` you're prompted for `OPENROUTER_API_KEY` and `GH_TOKEN`, stored encrypted and reused across nodes.

### GitHub Actions (label trigger)

The primary integration. Add `.github/workflows/pr-af-review.yml` — it triggers automatically whenever the **`pr-af`** label is added to a pull request, runs `docker compose up` plus `scripts/ci_runner.py`, and needs no extra config beyond the two secrets. Note: webhook signature verification code (`hmac`/`hashlib`) exists in `app.py`, but webhook triggers are not documented in the README — the label-triggered workflow and `af call`/curl are the documented entry points.

### Docker Compose

```bash
git clone https://github.com/Agent-Field/pr-af.git
cd pr-af
cp .env.example .env   # Add OPENROUTER_API_KEY, GH_TOKEN
docker compose up --build
```

Starts the AgentField control plane (`http://localhost:8080`) + PR-AF agent. Trigger a review:

```bash
curl -X POST http://localhost:8080/api/v1/execute/async/pr-af.review \
  -H "Content-Type: application/json" \
  -d '{"input": {"pr_url": "https://github.com/owner/repo/pull/123"}}'
```

### Railway

One-click deploy that bundles PR-AF + the AgentField control plane + PostgreSQL. Set two environment variables: `OPENROUTER_API_KEY` and `GH_TOKEN`.

### Go Port (opt-in)

The repo ships a Go port under `go/`. The **Python implementation is the default** (runs as `pr-af` on `:8004`); the Go port registers **separately** as `pr-af-go` on `:8007`, so both can run against one control plane simultaneously. Opt in by targeting the `-go` reasoner path, e.g. `POST /api/v1/execute/async/pr-af-go.review` (see `docker-compose.go.yml` and `go/README.md`).

### Configuration

Required environment variables:
- `OPENROUTER_API_KEY` — API key for OpenRouter AI model access (required)
- `GH_TOKEN` — GitHub personal access token with `repo` scope, for reading PRs and posting reviews

Additional knobs (`PR_AF_PROVIDER`, `PR_AF_MODEL`, `PR_AF_MAX_COST_USD`, etc.) live in `.env.example`.

## Related

- [[agentfield]] — The AgentField platform pr-af runs on (Firecracker micro-VM harness)
- [[SWE-AF]] — SWE-bench agent on AgentField, related code review ecosystem
- [[sec-af]] — Security-focused agent on AgentField, complementary to pr-af
- [[opencode]] — AI coding agent that can trigger pr-af reviews
- [[mission-control]] — MCP audit server that can track code review metrics
