---
title: hermes-incident-commander
subtitle: CodeGraph Verification
date: 2026-07-12
tags: [hermes-incident-commander, codegraph-verify, hermes-agent, incident]
suffix: .codegraph-verify
source: sources/hermes-incident-commander/
related: [[hermes-incident-commander]], [[hermes-agent]], [[defending-code-reference-harness]], [[mission-control]]
verified-by: codegraph-explore
---

# hermes-incident-commander — CodeGraph Verification

**Verification date:** 2026-07-12
**Verified by:** codegraph-explore
**Source reference:** `sources/hermes-incident-commander/`

## Claim-1: Autonomous SRE agent detecting, diagnosing, and healing production infrastructure

This project implements an autonomous incident management agent that detects production incidents, classifies severity, runs parallel diagnostics, applies fixes, and writes post-incident reports.

**Source evidence:** README lines 1-6:
> "**An autonomous SRE agent that detects, diagnoses, and heals production infrastructure - then learns from every incident it resolves.**\n\nBuilt on [Hermes Agent](https://hermes-agent.nousresearch.com) by NousResearch.\nSubmitted for the *'Show us what Hermes Agent can do'* challenge."

**Supporting detail:** Lines 44-51 document the full pipeline: "Hermes detects the incident and classifies severity (P0/P1/P2/P3) / Runs parallel diagnostics across CPU, memory, disk, and services / Identifies root cause with explicit reasoning / Applies the safest effective fix / Verifies the fix worked / Writes a structured post-incident report to `~/.hermes/incidents/` / Creates a **new prevention skill** in `~/.hermes/skills/`."

## Claim-2: Uses every major Hermes Agent feature

The project integrates Persistent Memory, Skill Auto-Creation, Cron Scheduler, Gateway (Telegram/Discord), Subagent Spawning, Session Search (FTS5), `execute_code`, and MCP Integration.

**Source evidence:** README lines 59-69 (feature table):
| Hermes Feature | How It's Used |
|---|---|
| **Persistent Memory** | Builds a system topology map over time. Learns which services fail together, time-of-day patterns, and which remediations work on YOUR infrastructure. |
| **Skill Auto-Creation** | After every novel incident, writes a new `SKILL.md` prevention playbook. Hermes gets measurably better at your stack over weeks. |
| **Cron Scheduler** | Every 5 min: critical health check. Every hour: full audit. Daily 08:00: morning briefing to Telegram. |
| **Subagent Spawning** | For multi-service environments, spawns parallel subagents to investigate nginx, database, and application layers simultaneously. |

## Claim-3: Ships with working demo, test suite, and installable skill

The repository contains a complete, runnable project with demo scenarios, pytest tests, and a skill file ready for installation into Hermes.

**Source evidence:** README lines 27-52 (demo commands):
```bash
pip install anthropic rich
export ANTHROPIC_API_KEY=sk-ant-...
python demo/demo_incident.py --scenario disk-full-logs
python demo/demo_incident.py --scenario svc-crash-nginx
python demo/demo_incident.py --scenario cpu-runaway-process
```

**Supporting detail:** Lines 225-237 document the test suite: `pytest tests/ -v` with specific test classes (`TestScenarioDefinitions`, `TestRewardFunction`, `TestSkillFile`). Lines 160-169 document skill installation: `cp -r skills/incident-commander ~/.hermes/skills/`.

## Claim-4: Includes Atropos RL training environment for SRE tasks

The project includes a reinforcement learning training environment with multi-component reward function for training models on SRE incident response.

**Source evidence:** README lines 181-192 (RL training):
```bash
# Generate SFT training data
python environments/incident_env.py process --config environments/incident_config.yaml
# Full RL training (requires VLLM)
python environments/incident_env.py serve --config environments/incident_config.yaml
```

**Supporting detail:** The reward function (lines 198-208) has five components: Resolution (50%), RCA Quality (15%), Report Quality (15%), Skill Created (10%), Response Speed (5%), Tool Efficiency (5%). Source files at `environments/incident_env.py` and `environments/incident_config.yaml` confirmed on disk.

## Claim-5: Five training scenarios spanning P0-P2 severity

The repository defines five incident scenarios covering different severity levels and categories.

**Source evidence:** README lines 212-221:
| ID | Severity | Category | Description |
|---|---|---|---|
| `svc-crash-nginx` | P0 | service | nginx crashed, website unreachable |
| `disk-full-logs` | P1 | disk | 95% disk usage from exploded log files |
| `memory-leak-process` | P1 | memory | Mystery process eating 150MB+ |
| `cpu-runaway-process` | P2 | cpu | 95% CPU from runaway computation |
| `failed-systemd-unit` | P2 | service | Custom worker service in failed state |

## Claim-6: Architecture follows DETECT → TRIAGE → DIAGNOSE → REMEDIATE → VERIFY → LEARN pipeline

The incident response follows a structured pipeline documented as a Mermaid flowchart.

**Source evidence:** README lines 74-106 (Mermaid flowchart):
```
DETECT["🔍 DETECT"] → TRIAGE["⚖️ TRIAGE"] → DIAGNOSE["🔬 DIAGNOSE"] → REMEDIATE["🔧 REMEDIATE"] → VERIFY["✅ VERIFY"] → LEARN["🧠 LEARN"]
```

**Supporting detail:** CRON triggers DETECT; TRIAGE and VERIFY push alerts to GATEWAY (Telegram/Discord/Slack). The project structure at lines 112-140 shows directories: `skills/`, `environments/`, `demo/`, `tests/`, `docs/`.

## Claim-7: Self-improving — creates prevention skills and learns from each incident

After each novel incident, the system writes a prevention playbook skill and updates its memory, getting better at the specific infrastructure over time.

**Source evidence:** README lines 246-248:
> "**Self-improving.** The longer Hermes runs, the better it gets at your specific infrastructure. This is Hermes's core promise - 'the agent that grows with you' - demonstrated concretely."

**Supporting detail:** The LEARN phase writes post-incident reports to `~/.hermes/incidents/`, creates prevention `SKILL.md` files, updates `MEMORY.md`, and searches past incidents via FTS5 for pattern matching.

## Dependency Map

```
hermes-incident-commander
  └─► hermes-agent (underlying agent harness — provides memory, cron, gateway, skills, subagents)
  └─► defending-code-reference-harness (related security/infrastructure defense domain)
  └─► mission-control (related MCP audit/monitoring infrastructure)
```
