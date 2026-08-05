---
name: shannon
tags: [shannon, ai-agents, agent-runtime, orchestration, multi-agent]
description: "AI agent runtime and orchestration platform"
source: sources/shannon/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Shannon

| Field | Value |
|---|---|
| **Origin** | [FosanzDev/Shannon](https://github.com/FosanzDev/Shannon) |
| **Source** | `sources/shannon/` |
| **Repomix** | `raw/shannon/shannon.xml` |
| **Codegraph** | `graphs/shannon/` |

## Overview

Shannon is an autonomous, white-box AI penetration tester for web applications and APIs, developed by [Keygraph](https://keygraph.io). It analyzes source code, identifies attack paths, and executes real exploits to prove vulnerabilities before they reach production. The repository provides Shannon Open Source — the standalone pentester CLI that runs locally via npx or git — alongside the Keygraph platform, a commercial continuous pentesting product that wraps Shannon in a full AppSec lifecycle.

Shannon closes a critical security gap: modern development teams ship code continuously with tools like Claude Code and Cursor, but traditional penetration testing happens once a year. This leaves 364 days of unexamined vulnerability surface. Shannon provides on-demand, automated pentesting that can run against every build or release, producing only proof-by-exploitation findings — vulnerabilities with working, reproducible proof-of-concept steps rather than speculative warnings.

The project began as a standalone CLI tool and now ships in two modes: **npx mode** (`npx @keygraph/shannon start`) for zero-install use, and **local mode** (cloned repository with `./shannon start`) for development and custom builds. Both modes run the same multi-agent pentesting pipeline, orchestrated by Temporal for durable workflow execution with crash recovery.

## Key Capabilities

- **Proof-by-Exploitation Reports** — Shannon only reports vulnerabilities it can actively exploit. Every finding includes reproducible proof-of-concept steps, eliminating the false-positive noise of traditional static analysis
- **White-Box Attack Planning** — Source-code analysis guides dynamic testing, focusing the pentest on realistic attack paths rather than spraying generic payloads
- **Autonomous Execution** — A single command launches reconnaissance, vulnerability analysis, exploitation, and report generation — no manual intervention required
- **OWASP-Focused Coverage** — Targets exploitable Injection (SQL, NoSQL, command), XSS, SSRF, Broken Authentication, and Broken Authorization vulnerabilities. Sample reports against OWASP Juice Shop (20+ findings), c{api}tal API (15+ critical/high findings), and OWASP crAPI (15+ findings) demonstrate the coverage
- **Authenticated Testing** — YAML configuration files describe login flows, test credentials, TOTP, email-based login flows, focus areas, and rules of engagement. Browser sessions are persisted and reused across vulnerability agents
- **Resumable Workspaces** — Named workspaces with session.json checkpointing enable interrupted scans to resume without re-running completed agents. Workspace state includes deliverables, agent logs, prompts, and browser artifacts
- **Multi-Provider AI Support** — Officially supported with Claude models (Opus 4.6/4.7/4.8 with adaptive thinking), with documented support for AWS Bedrock and custom Anthropic-compatible endpoints
- **Durable Workflow Execution** — Temporal orchestrates the five-phase pipeline with crash recovery, activity heartbeats, intelligent retry (3 attempts per agent), and parallel execution (5 concurrent agents in vulnerability/exploitation phases)

## Architecture

### Monorepo Layout

Shannon is structured as two packages in a pnpm Turborepo monorepo:

```
apps/cli/        — @keygraph/shannon (npm-published CLI, Docker orchestration only)
apps/worker/     — @shannon/worker (Temporal worker + pipeline logic, private)
```

**CLI Package** — Contains only Docker orchestration logic, no business logic or prompts. Handles infrastructure lifecycle (Docker Compose for Temporal, ephemeral worker containers), credential resolution (env vars → `~/.shannon/config.toml`), and workspace management. Auto-detects npx mode vs. local mode based on the `SHANNON_LOCAL=1` environment variable.

**Worker Package** — Contains the full pentesting pipeline. Runs on the **pi harness** (`@earendil-works/pi-agent-core`, `pi-ai`, `pi-coding-agent` ^0.79.1 — see `apps/worker/package.json:22-24`) via `apps/worker/src/ai/pi/pi-executor.ts` (`runPiPrompt` → `createAgentSession`, retry disabled so Temporal owns retry). Adaptive thinking (pi's `medium` level) is enabled only on Opus 4.6/4.7/4.8; every other model runs with thinking `off`. Since pi ships no JSON-schema output or `Task`/`TodoWrite` built-ins, structured queues are captured via a `submit_exploitation_queue` custom tool, and `task` (child sessions) + `todo_write` are provided as custom tools; the per-phase collectors are pi custom tools defined with TypeBox `defineTool` in `apps/worker/src/collectors/`. Browser automation via a Playwright CLI skill (`pi-executor.ts:56-64`) with session isolation. TOTP generation via `apps/worker/src/scripts/generate-totp.ts`.

### Five-Phase Pipeline

```
        ┌──────────────────────┐
        │   Pre-Reconnaissance │
        │   (source code scan) │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │   Reconnaissance     │
        │   (attack surface    │
        │   mapping)           │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────┴───────────┐
        │          │           │
        ▼          ▼           ▼
  ┌───────────┐ ┌───────────┐ ┌───────────┐
  │ Vuln      │ │ Vuln      │ │   ...     │
  │(Injection)│ │  (XSS)    │ │           │
  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
        │              │             │
        ▼              ▼             ▼
  ┌───────────┐ ┌───────────┐ ┌───────────┐
  │ Exploit   │ │ Exploit   │ │   ...     │
  │(Injection)│ │  (XSS)    │ │           │
  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
        │              │             │
        └──────┬───────┴─────────────┘
               │
               ▼
        ┌──────────────────────┐
        │      Reporting       │
        └──────────────────────┘
```

1. **Pre-Reconnaissance** — Identifies frameworks, entry points, data flows, and likely attack surfaces from the repository source code
2. **Reconnaissance** — Explores the live running application and correlates runtime behavior with code-level context
3. **Vulnerability Analysis** — Runs 5 parallel specialized agents for Injection, XSS, SSRF, Authentication (Broken Authentication), and Authorization (Broken Authorization)
4. **Exploitation** — 5 parallel agents attempt real proof-of-concept attacks; only confirmed exploits advance to reporting. If exploitation is disabled, findings are rendered deterministically from queue data without an LLM in the loop
5. **Reporting** — Compiles validated findings, evidence, and remediation guidance into an executive-level Markdown security assessment report

### Technical Architecture

Infrastructure runs via Docker Compose (Temporal server on port 7233/8233). Workers are ephemeral `docker run --rm` containers, one per scan, each with a per-invocation task queue and isolated volume mounts. The worker image is pulled from Docker Hub (`keygraph/shannon:latest`) in npx mode or built locally (`shannon-worker`) in development mode. The worker image is a 2-stage build: pnpm builder stage + Chainguard Wolfi runtime stage (Dockerfile:6,44).

Configuration uses YAML files with JSON Schema validation, supporting auth settings (MFA/TOTP), URL/code rule scoping (`rules.avoid`/`rules.focus`), run-scope steering (`vuln_classes`, `exploit`), free-form `rules_of_engagement`, and report filters (`min_severity`, `min_confidence`). Code path avoid rules are enforced via the `@gotgenes/pi-permission-system` extension (`apps/worker/package.json:25`): `syncCodePathDenyRules` writes a global `path` deny config once per workflow (`apps/worker/src/ai/pi/permission-system.ts:syncPermissionSystemConfig`), and the pi executor loads the extension when that config is present (`apps/worker/src/ai/pi/pi-executor.ts`), so denies fire across every tool and child `task` session. `vuln_classes`/`exploit` scope is locked into `session.json` on first run; resumes with a different scope fail fast.

Key source subdirectories of the worker package:

| Directory | Purpose |
|---|---|
| `apps/worker/src/ai/pi/` | pi harness integration: `pi-executor.ts`, `permission-system.ts`, `task-tool.ts`, `session-tools.ts` |
| `apps/worker/src/collectors/` | Per-phase pi custom tools: `pre-recon-collector.ts`, `recon-collector.ts`, `vuln-collector.ts`, `exploit-collector.ts`, `schema.ts` |
| `apps/worker/src/ai/` | `models.ts` (ModelRegistry, adaptive-thinking gating), `queue-schemas.ts`, `submit-tool.ts`, extensions |
| `apps/worker/src/temporal/` | Workflows, activities, worker, pipeline state, workspaces |
| `apps/worker/src/services/` | Business logic (Temporal-agnostic): `reporting.ts`, `agent-execution.ts`, `pre-recon-renderer.ts`, `recon-renderer.ts`, `validate-authentication.ts` |
| `apps/worker/src/session-manager.ts` | Agent definitions (`AGENTS` record, agent1..agent5) and session state |
| `apps/worker/prompts/` | 14 phase prompt templates + `shared/` partials + `pipeline-testing/` variants |
| `apps/worker/configs/` | `example-config.yaml` + `config-schema.json` |

## Documentation

| Guide | Purpose |
|---|---|
| [Development](docs/development.md) | Source build, CLI commands, output paths |
| [Configuration](docs/configuration.md) | Authenticated testing, login flows, rules of engagement |
| [AI Providers](docs/ai-providers.md) | Anthropic, AWS Bedrock, custom Anthropic-compatible endpoints |
| [Platforms](docs/platforms.md) | Windows/WSL2, Linux, macOS, Docker networking |
| [Workspaces](docs/workspaces.md) | Named workspaces, resuming interrupted scans |
| [Safety](docs/safety.md) | Authorized-use requirements, limitations, cost |
| [Keygraph Platform](docs/keygraph-platform.md) | Commercial continuous pentesting/AppSec platform around Shannon |
| [Coverage & Roadmap](docs/coverage-roadmap.md) | Current exploitability coverage and planned direction |

## Related

- [[hermes-agent]] — Multi-platform agent gateway with subagent delegation that could orchestrate Shannon scans
- [[openclaw]] — Personal AI assistant with agent workspace isolation, complementary to Shannon's security focus
- [[turnstone]] — Self-hosted agent orchestration harness with rigorous safety gating, a kindred approach to agent control
- [[nanobot]] — Agent framework for building autonomous workers that could wrap Shannon's pipeline
- [[pi]] — TypeScript agent harness that Shannon now runs on (beta via `npx @keygraph/shannon@beta`); Shannon's worker depends on `@earendil-works/pi-coding-agent` ^0.79.1
- [[materia]] — Podman Quadlet GitOps deployment tool (not an agent framework); relevant to Shannon only as container deployment infrastructure
