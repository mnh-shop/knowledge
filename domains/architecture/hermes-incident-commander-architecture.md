---
name: hermes-incident-commander-architecture
tags: [hermes-incident-commander, architecture, hermes-agent, incident, sre, rl-training]
description: "Autonomous SRE agent — DETECT→TRIAGE→DIAGNOSE→REMEDIATE→VERIFY→DOCUMENT→LEARN pipeline, Atropos RL training environment, 5 incident scenarios"
source: sources/hermes-incident-commander/
verification_date: 2026-07-12
verified_by: fixer
---

# Hermes Incident Commander — Architecture

**Source:** `sources/hermes-incident-commander/`

## Overview

Hermes Incident Commander is an autonomous Site Reliability Engineering (SRE) agent built on Hermes Agent. It extends Hermes with a complete incident response lifecycle — detect, triage, diagnose, remediate, verify, document, and learn — that runs autonomously against Linux/Docker production environments. Every resolved incident teaches the system to handle similar situations faster through automatic skill creation and persistent infrastructure memory. The system ships with a standalone CLI demo, a Hermes skill module, and an Atropos-compatible reinforcement learning environment with 5 incident scenarios.

## Architecture

The core incident response loop follows a strict **DETECT→TRIAGE→DIAGNOSE→REMEDIATE→VERIFY→DOCUMENT→LEARN** pipeline. Each stage is a discrete step with defined inputs, outputs, and success criteria. The RL training environment wraps this loop in a sandboxed Docker terminal backend with a 6-component reward function.

```
┌──────────────────────────────────────────────────────────────────┐
│                     INCIDENT RESPONSE PIPELINE                    │
│                                                                   │
│  DETECT ──→ TRIAGE ──→ DIAGNOSE ──→ REMEDIATE ──→ VERIFY          │
│    │           │            │            │           │             │
│    ▼           ▼            ▼            ▼           ▼             │
│  System     Severity    Root        Tiered      Re-run            │
│  vitals     classify    cause       self-heal   diagnostics       │
│  (CPU,      (P0-P3)     analysis    (1/2/3)     (before/after)     │
│  mem,                    per                     └──────┬──────────┘
│  disk,                  category                         │
│  logs)                                                   │
│                                           ┌───────────────▼────────┐
│                                         DOCUMENT         LEARN     │
│                                         Post-incident    Create    │
│                                         report with      prevention│
│                                         timeline,        SKILL.md  │
│                                         root cause,      + update  │
│                                         remediation      MEMORY.md │
└──────────────────────────────────────────────────────────────────┘
```

### Pipeline Stages

1. **DETECT** — Gather system vitals immediately (CPU, memory, disk, failed systemd units, recent error logs). Runs all diagnostics in parallel via Hermes parallel subagent spawning.
2. **TRIAGE** — Classify severity P0 (total outage) through P3 (warning threshold). Announces severity via Hermes Gateway (Telegram/Discord/Slack) within 60 seconds.
3. **DIAGNOSE** — Root cause analysis by category: high CPU (strace, lsof), memory pressure (/proc/meminfo, OOM scores), disk full (du, large logs, deleted files), service crash (journalctl), Docker issues (stats, logs). For multi-service environments, spawns subagents to investigate nginx, database, application, and other layers simultaneously.
4. **REMEDIATE** — Tiered self-healing: Tier 1 (safe, no approval — clear temp files, restart non-critical services, kill runaway processes), Tier 2 (moderate — restart critical services, rollback deploy, after 30s warning), Tier 3 (destructive — data deletion, node termination, requires explicit approval).
5. **VERIFY** — Re-run diagnostics, compare before/after metrics, confirm resolution only when all previously failed checks pass.
6. **DOCUMENT** — Write structured post-incident report to `~/.hermes/incidents/<timestamp>-<slug>.md` with timeline, root cause, remediation steps, and metrics.
7. **LEARN** — Analyze root cause, create new prevention `SKILL.md` if pattern is novel, update `MEMORY.md` with new topology and failure correlation knowledge.

### RL Training Environment

The `environments/incident_env.py` (577 lines) wraps the incident loop in an Atropos-compatible reinforcement learning environment with:

- **5 incident scenarios**: `svc-crash-nginx` (P0/service), `disk-full-logs` (P1/disk), `memory-leak-process` (P1/memory), `cpu-runaway-process` (P2/cpu), `failed-systemd-unit` (P2/service)
- **IncidentScenario dataclass**: Each scenario defines `id`, `severity`, `category`, `system_state` (Docker sandbox setup commands), `success_criteria` (shell commands for 1.0 reward), `partial_criteria` (commands for partial credit), and `description`
- **6-component reward function**: Resolution speed, correctness, tier-appropriateness, documentation quality, skill-learned flag, no unnecessary destruction
- **Three operating modes**: `serve` (RL training loop via Atropos), `evaluate` (model evaluation), `process` (SFT data generation)

### Scheduled Monitoring

Three-tier cron-based monitoring in natural language: critical health check every 5 minutes (alerts on P0/P1), comprehensive system audit every hour (full pipeline), daily morning briefing (trend analysis, capacity planning).

## Key Components

| Component | Path | Role |
|-----------|------|------|
| **Standalone demo** | `demo/demo_incident.py` | CLI demo requiring only `ANTHROPIC_API_KEY` — 5 built-in scenarios |
| **RL environment** | `environments/incident_env.py` | Atropos-compatible env — scenario definitions, reward function, Docker sandbox |
| **RL config** | `environments/incident_config.yaml` | Training hyperparameters and scenario selection |
| **Hermes skill** | `skills/incident-commander/SKILL.md` | Hermes skill module for full integration |
| **Test suite** | `tests/test_incident_env.py` | Pytest suite covering scenarios, rewards, skill file generation |
| **Documentation** | `docs/SETUP.md`, `docs/WRITEUP.md` | Installation guide and technical writeup |

### Incident Scenarios

| ID | Severity | Category | Description |
|----|----------|----------|-------------|
| `svc-crash-nginx` | P0 | service | nginx crashed, website unreachable |
| `disk-full-logs` | P1 | disk | 95% disk usage from exploded log files |
| `memory-leak-process` | P1 | memory | Mystery process eating 150MB+ |
| `cpu-runaway-process` | P2 | cpu | 95% CPU from runaway computation |
| `failed-systemd-unit` | P2 | service | Custom worker service in failed state |

## Related

- [[hermes-incident-commander]] — Wiki entry with full interface reference
- [[hermes-agent]] — Core agent platform that hosts the skill
- [[defending-code-reference-harness]] — Reference harness for defense coding patterns
- [[mission-control]] — MCP audit server for monitoring agent behavior
- [[hermes-workspace]] — Workspace command center for multi-agent deployment
