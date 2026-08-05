---
name: defending-code-reference-harness
description: "Reference implementation for autonomous vulnerability discovery and remediation using Claude Code agents"
tags: [defending-code-reference-harness, security, harness, reference, multi-agent, agent, claude-code, python]
source: sources/defending-code-reference-harness/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Defending Code Reference Harness

A reference implementation for autonomous vulnerability discovery and remediation using Claude Code agents. Based on Anthropic's learnings from partnering with security teams at several organizations since launching the Claude Mythos Preview. The harness provides an automated recon → find → verify → report → patch pipeline for finding memory-safety bugs in C/C++ codebases.

## Overview

Created by Anthropic, this reference implementation demonstrates how to use Claude agents for automated vulnerability discovery and remediation. The pipeline runs Claude agents inside gVisor-isolated containers with egress restricted to the Claude API, using ASAN (AddressSanitizer) to instrument and crash C/C++ binaries. It enforces a two-container trust boundary between find and grade agents — only proof-of-concept bytes cross the boundary, defeating reward-hacking via pre-positioned state. Beyond the preventive pipeline, the repo also ships a **Detection & Response track** (`dnr_harness/`, `/dnr-hunt` + `/dnr-respond` skills, `targets/dnrcanary/`, `docs/detection-response.md`) for hunting a live attacker in logs — roughly a third of the repository's scope (README.md:40-45). The accompanying blog post (available in `docs/blog-post.md`) and cookbook tutorial on the Anthropic platform provide deeper context and best practices. A managed product version (Claude Security) is also available.

**Note:** This repo is not maintained and is not accepting contributions. It is published as an open-source reference (not a product) based on general best practices.

## Key Features

- **9 interactive Claude Code skills**: `/quickstart` (30-second intro and guided first run), `/threat-model` (bootstrap, interview, or bootstrap-then-interview → THREAT_MODEL.md), `/vuln-scan` (static code review → VULN-FINDINGS.json), `/triage` (verify, dedupe, and rank findings across pipeline runs), `/patch` (generate and verify candidate fixes → PATCHES/), `/customize` (port the pipeline to other languages/stacks), plus the Detection & Response track: `/dnr-hunt` (sweep the corpus for anything that shouldn't be there → alerts), `/dnr-respond` (lead/IOC in → verdict, blast radius, response plan out), and `/verify` (cross-check skill outputs)
- **Autonomous multi-agent pipeline**: Runs Claude agents inside gVisor-isolated containers (`--runtime=runsc`, network egress locked to `api.anthropic.com:443`) with 7 stages: build → recon → find → verify → dedupe → report → patch
- **Execution-verified findings**: Uses ASAN to instrument binaries; each finding requires 3/3 reproduction before submission
- **Parallel discovery**: Multiple agents explore different focus areas simultaneously using round-robin partitioning over target input-parsing subsystems, with `--auto-focus` for dynamic partitioning
- **Two-layer duplicate detection**: Runtime `<dup_check>` tag (agent judges semantically against `found_bugs.jsonl`) + report-gate judge agent (NEW/DUP_BETTER/DUP_SKIP verdicts with reasoning)
- **Structured exploitability reporting**: Generates reports with primitive class, reachability from attack surface, heap layout, escalation path, constraints, and severity rating; graded by a separate report-grader agent
- **Patch verification ladder**: T0 (apply + rebuild) → T1 (original PoC no longer crashes) → T2 (target test suite passes) → T3 re-attack (50-turn find-agent attacks patched binary)
- **Two-container trust boundary**: Find and grade run in separate gVisor containers; only PoC bytes cross. Prevents reward-hacking
- **Resilient execution**: Rate limits and API errors don't kill runs — automatic retries, exponential backoff (cap 300s), session resume with full context restoration (up to 20 resumes per agent)
- **Detection & Response track**: Everything else in the repo is preventive; this track assumes prevention failed and an attacker is already in the logs (README.md:40-45). Ships `/dnr-hunt` and `/dnr-respond` skills plus `dnr_harness/` — their autonomous mirror, `dnr-pipeline` (hunt + grade over `kind: dnr` targets) — and a dedicated demo target `targets/dnrcanary/` (a deliberately vulnerable Flask storefront with a week of generated web logs containing a planted attack campaign, benign traffic, and a noisy dead end; logs are gitignored and generated locally as a required first step). The chain is `/dnr-hunt → /dnr-respond → /triage → /patch`; outputs (`INCIDENTS.json`, incident report, response plan) land in `results/<target>/<timestamp>/`. See `docs/detection-response.md`

## Usage

### Quick start (interactive skills)

```bash
git clone https://github.com/anthropics/defending-code-reference-harness
cd defending-code-reference-harness
claude

# 30-sec intro + guided first run on the canary target
> /quickstart

# Build a threat model
> /threat-model bootstrap targets/canary

# Run a static scan scoped by that model
> /vuln-scan targets/canary

# Verify, dedupe, and rank findings
> /triage targets/canary/VULN-FINDINGS.json

# Generate candidate fixes
> /patch ./TRIAGE.json --repo targets/canary
```

**Detection & response track** (attacker already in the logs — generate the local log corpus first, then hunt):

```bash
# Generate the canary's web logs (gitignored; required first step)
python3 targets/dnrcanary/generate_logs.py --seed 42

# No alert in hand — sweep the corpus for anything that shouldn't be there
> /dnr-hunt targets/dnrcanary

# Lead in hand — hand off the incident id from the hunt, or pass an IOC directly
> /dnr-respond INC-2
> /dnr-respond 203.0.113.66 --logs targets/dnrcanary
```

### Autonomous pipeline

```bash
# One-time setup
python3 -m venv .venv && .venv/bin/pip install -e .
./scripts/setup_sandbox.sh   # installs gVisor, builds agent images

# Run pipeline on a demo target
bin/vp-sandboxed run drlibs --model claude-sonnet-4-6 --runs 3 --parallel --stream --auto-focus

# Generate candidate patches
bin/vp-sandboxed patch results/drlibs/<timestamp>/ --model claude-sonnet-4-6
```

### Pipeline subcommands

| Command | Purpose |
|---|---|
| `vuln-pipeline recon <target>` | Propose focus areas (input-parsing partitions) |
| `vuln-pipeline run <target>` | Find + grade pipeline, one run |
| `vuln-pipeline run <target> --runs N --parallel` | N concurrent finds over focus areas |
| `vuln-pipeline run <target> --stream` | Streaming mode: reports land as grades finish |
| `vuln-pipeline dedup <results>` | Group crashes by signature |
| `vuln-pipeline report <results>` | Exploitability analysis per unique crash |
| `vuln-pipeline patch <results>` | Generate + verify fixes per unique crash |
| `dnr-pipeline run <target>` | D&R track: hunt + grade, one or more runs (`dnr_harness/cli.py`) |

### Demo targets

The repo ships **five** targets — four preventive pipeline targets plus the D&R canary:

| Target | Description | Expected time |
|---|---|---|
| `canary` | Fast smoke test with planted bugs | ~6 min |
| `drlibs` | Real-world CVEs in a C library | ~30-60 min |
| `alsa` | Real-world CVEs in audio subsystem | ~30-60 min |
| `htslib` | CRAM container format, 10-CVE cluster | harder target |
| `dnrcanary` | D&R target: vulnerable Flask storefront + generated web logs with planted attack campaign | — (hunt/respond track) |

### Architecture

The agent tool set is fixed: find/grade/report agents get `Read`, `Write`, `Bash`; judge/compare/report-grader agents get no tools (everything in prompt). Each agent runs `claude -p` inside its own gVisor container via `bin/vp-sandboxed`, which sets the runtime/proxy env and execs the pipeline. Agent-spawning subcommands refuse to start outside the sandbox unless `--dangerously-no-sandbox` is passed. The D&R track is the autonomous mirror of the `/dnr-hunt` + `/dnr-respond` skills — `dnr_harness/` (6 modules: `__init__.py`, agent_image, cli, config, prompts, system_prompt) enforces the answer-key/ground-truth separation structurally by building the hunt container without the answer-key files. Tests are in `tests/` with `pytest` covering tag/XML parsing, artifact serialization, ASAN signature extraction, dedup, patch-grade ladder, and system-prompt construction.

## Related

- [[Anthropic-Cybersecurity-Skills]] — Structured cybersecurity skill library for AI agents with complementary playbooks
- [[SecuritySkills]] — Security-focused agent skill ecosystem for defensive workflows
- [[hermes-agent]] — Self-improving AI agent that can integrate these security workflows as skills
- [[openclaw]] — Locally-running AI assistant platform that can be configured with similar security tooling
- [[hermes-agent-acp-skill]] — ACP skill for Hermes that enables agent-to-agent security coordination
- [[sec-af]] — Security-focused agent framework for assessments and vulnerability discovery
