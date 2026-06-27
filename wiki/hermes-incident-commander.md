---
name: hermes-incident-commander
description: "Autonomous SRE agent for Hermes: detects, diagnoses, and heals production infrastructure with self-improving skills and RL training"
source: sources/hermes-incident-commander/
tags: [agent, hermes-agent, cli, developer-tools, docker, event-bus, mcp, messaging, monitoring, skills-platform, storage, python]
---

# Hermes Incident Commander

**Source:** `sources/hermes-incident-commander/`

Hermes Incident Commander is an autonomous Site Reliability Engineering (SRE) agent built on top of [Hermes Agent](hermes-agent.md). It extends Hermes with a complete incident response lifecycle -- detect, triage, diagnose, remediate, verify, document, and learn -- that runs autonomously against Linux/Docker production environments. Every resolved incident teaches the system to handle similar situations faster through automatic skill creation and persistent memory.

Developed for the NousResearch "Show us what Hermes Agent can do" challenge. Licensed MIT.

## Key Features

- **Autonomous Incident Response Loop**: Full detect -> triage -> diagnose -> remediate -> verify -> document -> learn cycle, with tiered remediation actions (safe auto-fix, moderate warn-then-proceed, destructive require-approval).
- **Self-Improving Skills**: After every novel incident, automatically writes a new prevention `SKILL.md` into `~/.hermes/skills/` containing early warning signs, automated checks, and a proven remediation playbook. Hermes gets measurably better at each stack over time.
- **Persistent Infrastructure Memory**: Builds a system-specific knowledge base in `MEMORY.md` including service dependency topology, failure correlation patterns, time-of-day incident patterns, and remediation success rates.
- **Parallel Subagent Investigation**: For multi-service environments, spawns subagents to simultaneously investigate nginx, database, application, and other layers -- then synthesizes findings to identify root cause.
- **Multi-Platform Incident Notifications**: Real-time alerts via Telegram, Discord, or Slack through the Hermes Gateway. P0/P1 alerts within 60 seconds of detection, progress updates during active incidents, resolution notices with MTTR.
- **Scheduled Monitoring via Cron**: Three-tier monitoring in natural language -- critical health check every 5 minutes (alerts on P0/P1), comprehensive system audit every hour, daily morning briefing with trend analysis.
- **RL Training Environment**: Full Atropos-compatible reinforcement learning environment with 5 incident scenarios, multi-component reward function, Docker sandboxing, and GRPO training loop (see [[#Architecture]] below).
- **Searchable Incident History**: Uses Hermes Session Search (FTS5) to find prior incidents matching the current error pattern.

## Architecture

The core incident response loop follows a strict pipeline:

```
DETECT -> TRIAGE -> DIAGNOSE -> REMEDIATE -> VERIFY -> DOCUMENT -> LEARN
```

1. **DETECT** -- Gather system vitals immediately: CPU, memory, disk, failed systemd units, recent error logs. Runs all diagnostics in parallel.
2. **TRIAGE** -- Classify severity P0 (total outage) through P3 (warning threshold). Announces severity via gateway immediately.
3. **DIAGNOSE** -- Root cause analysis by category: high CPU (strace, lsof), memory pressure (/proc/meminfo, OOM scores), disk full (du, large logs, deleted files), service crash (journalctl), Docker issues (stats, logs).
4. **REMEDIATE** -- Tiered self-healing: Tier 1 (safe, no approval: clear temp files, restart non-critical services, kill runaway processes), Tier 2 (moderate: restart critical services, rollback deploy, after warn-30s), Tier 3 (destructive: data deletion, node termination -- explicit approval required).
5. **VERIFY** -- Rerun diagnostics, compare before/after metrics, confirm resolution only when all previously failed checks pass.
6. **DOCUMENT** -- Write structured post-incident report to `~/.hermes/incidents/<timestamp>-<slug>.md` with timeline, root cause, remediation steps, and metrics.
7. **LEARN** -- Analyze root cause, create new prevention skill if pattern is novel, update MEMORY.md with new topology and correlation knowledge.

The RL training environment (see [[domains/architecture/hermes-incident-commander]]) wraps this loop in a sandboxed Docker terminal backend, scoring agent performance with a 6-component reward function.

## Interfaces

| Interface | Description |
|-----------|-------------|
| **CLI (Demo)** | `python demo/demo_incident.py --scenario <name>` -- standalone demo requiring only `ANTHROPIC_API_KEY`. Five built-in scenarios. |
| **Hermes Skill** | `skills/incident-commander/SKILL.md` -- installed into `~/.hermes/skills/` for full Hermes integration. Loaded via `/skills` in the Hermes CLI. |
| **RL Training Environment** | `python environments/incident_env.py [process|serve|smoke] --config ...` -- Atropos-compatible environment for SFT data generation and GRPO training. |
| **Hermes Gateway** | Telegram/Discord/Slack notifications for incident alerts, progress updates, and resolution notices. Configured via `hermes gateway setup`. |
| **Hermes Cron** | Natural-language scheduling for health checks, audits, and briefings. Jobs created automatically from conversation. |
| **Hermes Session Search** | FTS5 full-text search across past incidents and conversations. "Have we seen this error before?" |
| **MCP Integration** | Cloud provider APIs (AWS CloudWatch, GCP Cloud Monitoring, etc.) for auto-scaling and cloud-native remediation -- listed as future/planned. |

## Project Structure

```
hermes-incident-commander/
├── demo/
│   └── demo_incident.py          # Standalone CLI demo (Anthropic API only)
├── docs/
│   ├── SETUP.md                  # Installation guide
│   └── WRITEUP.md                # Technical writeup for Hermes challenge
├── environments/
│   ├── incident_config.yaml      # RL training configuration (Atropos)
│   └── incident_env.py           # Atropos RL environment for incident response
├── skills/
│   └── incident-commander/
│       └── SKILL.md              # Hermes-compatible skill definition
├── tests/
│   └── test_incident_env.py      # Pytest suite (scenarios, rewards, skill file)
├── README.md
├── requirements.txt
└── LICENSE                       # MIT
```

## Incident Scenarios

| ID | Severity | Category | Description |
|----|----------|----------|-------------|
| `svc-crash-nginx` | P0 | service | nginx crashed, website unreachable |
| `disk-full-logs` | P1 | disk | 95% disk usage from exploded log files |
| `memory-leak-process` | P1 | memory | Mystery process eating 150MB+ |
| `cpu-runaway-process` | P2 | cpu | 95% CPU from runaway computation |
| `failed-systemd-unit` | P2 | service | Custom worker service in failed state |

## Related

- [[hermes-agent]] -- The underlying agent platform by NousResearch
- [[hermes-suite]] -- Collection of all Hermes-related projects
- [[hermes-workspace]] -- Workspace setup for Hermes development
- [[hermes-startup-architect]] -- Another Hermes skill focused on infrastructure design
- [[clawpier]] -- Adjacent tooling for container management
- [[openclaw]] -- Container lifecycle tooling
