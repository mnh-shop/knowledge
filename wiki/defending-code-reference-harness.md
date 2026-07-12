---
name: defending-code-reference-harness
description: "Reference implementation for autonomous vulnerability discovery and remediation using Claude Code agents"
tags: [defending-code-reference-harness, security, harness, reference, multi-agent, agent, claude-code, python]
source: sources/defending-code-reference-harness/
---

# Defending Code Reference Harness

A reference implementation for autonomous vulnerability discovery and remediation using Claude Code agents. Based on Anthropic's learnings from partnering with security teams at organizations since launching Claude Mythos Preview. The harness provides an automated recon → find → verify → report → patch pipeline for finding memory-safety bugs in C/C++ codebases.

## Key Features

- **6 interactive Claude Code skills**: `/quickstart`, `/threat-model`, `/vuln-scan`, `/triage`, `/patch`, `/customize` for scoped vulnerability analysis
- **Autonomous multi-agent pipeline**: Runs Claude agents inside gVisor-isolated containers with egress restricted to Claude API
- **Execution-verified findings**: Uses ASAN (AddressSanitizer) to instrument and crash C/C++ binaries, with 3/3 reproduction requirement
- **Parallel discovery**: Multiple agents explore different focus areas simultaneously without converging on the same bug
- **Duplicate detection**: Agent-judged deduping compares crashes semantically, not by string matching
- **Structured reporting**: Generates exploitability analysis including primitive class, reachability, escalation path, and severity

## Architecture

The pipeline executes in seven stages:
1. **Reconnaissance**: Agent reads source and proposes focus areas (input-parsing partitions)
2. **Find**: Parallel agents craft malformed inputs and crash the binary until 3/3 reproduction
3. **Verify**: Separate grader agent reproduces each crash in a fresh container
4. **Deduplication**: Judge agent compares crashes against found bugs to identify new/duplicate
5. **Report**: Structured exploitability analysis with severity rating
6. **Patch**: Agent generates fix, grader verifies build + original PoC no longer crashes + tests pass + re-attack clean
7. **Two-container trust boundary**: Find and grade run in separate containers; only PoC bytes cross

The harness enforces sandboxing via `bin/vp-sandboxed` which runs agents inside gVisor with `--runtime=runsc` and network egress locked to `api.anthropic.com:443`.

## Skills & Tools

**Interactive skills** (`.claude/skills/`):
- `/quickstart` — 30-second intro and guided first run
- `/threat-model` — Bootstrap, interview, or bootstrap-then-interview → `THREAT_MODEL.md`
- `/vuln-scan` — Static code review → `VULN-FINDINGS.json`
- `/triage` — Verify, dedupe, and rank findings across pipeline runs
- `/patch` — Generate and verify candidate fixes
- `/customize` — Port the pipeline to other languages/stacks

**Pipeline commands**: `vuln-pipeline run`, `vuln-pipeline recon`, `vuln-pipeline report`, `vuln-pipeline patch`, `vuln-pipeline dedup`

## Deployment / Use

Install and setup:
```bash
git clone https://github.com/anthropics/defending-code-reference-harness
cd defending-code-reference-harness

# Install Python deps
python3 -m venv .venv && .venv/bin/pip install -e .

# One-time sandbox setup (requires Docker, sudo)
./scripts/setup_sandbox.sh

# Run on canary target (fast smoke test)
bin/vp-sandboxed run canary --runs 3 --parallel
```

The harness ships with demo targets: `canary` (~6min, planted bugs), `drlibs` (real CVEs), `alsa`, and `htslib`. Add your own target by creating a `targets/<name>/` directory with `config.yaml`, `Dockerfile`, and `entry.c`.

## Related

- [[Anthropic-Cybersecurity-Skills]] — Structured cybersecurity skill library
- [[SecuritySkills]] — Security-focused agent skill ecosystem
- [[hermes-agent]] — Self-improving AI agent that can use these security workflows