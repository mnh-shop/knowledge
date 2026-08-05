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

**Supporting detail:** MCP Integration is presented in the README feature table (line 68) but is listed under "What's Next" in the technical writeup (`docs/WRITEUP.md` line 127: "Cloud-native integrations via MCP servers (AWS CloudWatch, GCP Cloud Monitoring)") — planned/aspirational, not yet implemented.

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

**Supporting detail:** The demo CLI ships exactly **three** scenarios — `disk-full-logs`, `svc-crash-nginx`, `cpu-runaway-process` (`demo/demo_incident.py` DEMO_SCENARIOS lines 166-233; argparse `--scenario` choices at lines 400-403). Lines 225-237 of the README document the test suite: `pytest tests/ -v`; the suite (`tests/test_incident_env.py`, 365 lines) contains **four** test classes — `TestScenarioDefinitions` (line 94), `TestRewardFunction` (line 163), `TestSkillFile` (line 280), and `TestDemoScript` (line 326). Skill installation at README lines 160-169: `cp -r skills/incident-commander ~/.hermes/skills/`.

## Claim-4: Includes Atropos RL training environment for SRE tasks

The project includes a reinforcement learning training environment with multi-component reward function for training models on SRE incident response.

**Source evidence:** README lines 181-192 (RL training):
```bash
# Generate SFT training data
python environments/incident_env.py process --config environments/incident_config.yaml
# Full RL training (requires VLLM)
python environments/incident_env.py serve --config environments/incident_config.yaml
```

**Supporting detail:** The CLI subcommands are `serve | process | evaluate` (`environments/incident_env.py` argparse choices at lines 570-573); smoke-test runs via the `--smoke-test` flag (line 566) or automatically when hermes-agent is not installed (lines 575-577). The environment uses a **six-component** reward — Resolution (50%), RCA Quality (15%), Report Quality (15%), Skill Created (10%), Response Speed (5%), Tool Efficiency (5%) — confirmed in `environments/incident_config.yaml` reward_weights lines 41-47 and README lines 200-208. Sandboxing uses `terminal_backend: docker` (incident_config.yaml line 9) with GRPO training via Atropos (incident_env.py lines 377-381).

## Claim-5: Five training scenarios spanning P0-P2 severity

The RL environment defines five incident scenarios covering different severity levels and categories. Note the standalone demo CLI ships only a 3-scenario subset of this set.

**Source evidence:** `environments/incident_env.py` INCIDENT_SCENARIOS (line 59 onward) defines `svc-crash-nginx`, `disk-full-logs`, `memory-leak-process`, `cpu-runaway-process`, and `failed-systemd-unit`; README lines 212-221:
| ID | Severity | Category | Description |
|---|---|---|---|
| `svc-crash-nginx` | P0 | service | nginx crashed, website unreachable |
| `disk-full-logs` | P1 | disk | 95% disk usage from exploded log files |
| `memory-leak-process` | P1 | memory | Mystery process eating 150MB+ |
| `cpu-runaway-process` | P2 | cpu | 95% CPU from runaway computation |
| `failed-systemd-unit` | P2 | service | Custom worker service in failed state |

**Supporting detail:** The demo (`demo/demo_incident.py` DEMO_SCENARIOS, lines 166-233) contains only `disk-full-logs`, `svc-crash-nginx`, and `cpu-runaway-process` — the two RL-only scenarios are `memory-leak-process` and `failed-systemd-unit`.

## Claim-6: Architecture follows DETECT → TRIAGE → DIAGNOSE → REMEDIATE → VERIFY → DOCUMENT → LEARN pipeline

The incident response follows a structured pipeline documented as a Mermaid flowchart.

**Source evidence:** `skills/incident-commander/SKILL.md` lines 23-27 (Core Incident Loop):
```
DETECT → TRIAGE → DIAGNOSE → REMEDIATE → VERIFY → DOCUMENT → LEARN
```

**Supporting detail:** README lines 74-106 (Mermaid flowchart):
```
DETECT["🔍 DETECT"] → TRIAGE["⚖️ TRIAGE"] → DIAGNOSE["🔬 DIAGNOSE"] → REMEDIATE["🔧 REMEDIATE"] → VERIFY["✅ VERIFY"] → LEARN["🧠 LEARN"]
```
CRON triggers DETECT; TRIAGE and VERIFY push alerts to GATEWAY (Telegram/Discord/Slack). The project structure at README lines 112-140 shows directories: `skills/`, `environments/`, `demo/`, `tests/`, `docs/`.

## Claim-7: Self-improving — creates prevention skills and learns from each incident

After each novel incident, the system writes a prevention playbook skill and updates its memory, getting better at the specific infrastructure over time.

**Source evidence:** README lines 246-248:
> "**Self-improving.** The longer Hermes runs, the better it gets at your specific infrastructure. This is Hermes's core promise - 'the agent that grows with you' - demonstrated concretely."

**Supporting detail:** The LEARN phase writes post-incident reports to `~/.hermes/incidents/`, creates prevention `SKILL.md` files, updates `MEMORY.md`, and searches past incidents via FTS5 for pattern matching.

## Claim-8: Docs — SETUP.md and WRITEUP.md with measured GRPO results

The repository ships `docs/SETUP.md` (installation guide) and `docs/WRITEUP.md` (technical writeup with measured results from testing against the 5 RL scenarios).

**Source evidence:** `docs/WRITEUP.md` lines 115-120 (Results):
> - P0 service crash: resolved in 4–7 turns
> - P1 disk full: identified and cleaned in 5–8 turns
> - P2 runaway process: killed and documented in 3–5 turns
> - Post-incident reports written in 100% of successful runs
> - Prevention skills created in ~60% of runs (agent sometimes skips if pattern is too simple)

**Supporting detail:** `docs/SETUP.md` covers demo quick-start (lines 3-18), full Hermes setup with gateway (lines 22-94), and RL training via `process`/`serve` (lines 97-131). MCP cloud integrations appear under "What's Next" in `docs/WRITEUP.md` (lines 124-127), confirming they are planned rather than implemented.

## Dependency Map

```
hermes-incident-commander
  └─► hermes-agent (underlying agent harness — provides memory, cron, gateway, skills, subagents)
  └─► defending-code-reference-harness (related security/infrastructure defense domain)
  └─► mission-control (related MCP audit/monitoring infrastructure)
```
