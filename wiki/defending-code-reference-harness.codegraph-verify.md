---
name: defending-code-reference-harness-codegraph-verify
tags: [defending-code-reference-harness, codegraph-verify, security, reference]
description: "Codegraph Verification: defending-code-reference-harness — validating wiki claims against indexed source code symbols"
source: sources/defending-code-reference-harness/
---

# Codegraph Verification: defending-code-reference-harness

**Date:** 2026-07-12

## Claim 1: Reference implementation for autonomous vulnerability discovery by Anthropic
- **Wiki says:** A reference implementation for autonomous vulnerability discovery and remediation with Claude, based on learnings from partnering with security teams since launching Claude Mythos Preview.
- **Source evidence:**
  - `README.md` line 3-5: "A reference implementation for autonomous vulnerability discovery and remediation with Claude, based on our learnings from partnering with security teams at several organizations since launching Claude Mythos Preview"
  - `README.md` line 6: Associated blog post at `https://claude.com/blog/using-llms-to-secure-source-code`
  - `README.md` line 12: "This repo is not maintained and is not accepting contributions."
  - `pyproject.toml` exists confirming Python packaging
  - Anthropic is the author (noted in `CLAUDE.md` and `README.md` attribution)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Multi-stage autonomous pipeline with 7 stages (Build, Recon, Find, Grade, Judge, Report, Patch)
- **Wiki says:** The reference pipeline walks through seven stages: Build, Recon, Find, Verify (Grade), Dedupe (Judge), Report, and Patch. Each stage runs in isolated gVisor containers.
- **Source evidence:**
  - `README.md` lines 178-203: Each of the 7 stages documented in detail
  - `README.md` line 179: "Build: Compiles the target into a Docker image with ASAN"
  - `README.md` line 182: "Recon: A lightweight agent reads the source inside a network-isolated container"
  - `README.md` line 187: "Find: N agents run in parallel, each in its own isolated container"
  - `README.md` line 192: "Verify: A separate grader agent reproduces each crash in a fresh container"
  - `README.md` line 195: "Dedupe: A judge agent compares verified crashes against bugs already reported"
  - `README.md` line 198: "Report: A report agent writes a structured exploitability analysis per unique bug"
  - `README.md` line 200: "Patch: A patch agent writes a proposed fix, and a grader agent confirms"
  - `docs/pipeline.md` lines 42-93 provide deep-dive for each stage
  - `harness/` directory contains the pipeline implementation
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Interactive Claude Code skills for the full vulnerability workflow
- **Wiki says:** Nine interactive skills shipped in `.claude/skills/`: /quickstart, /threat-model, /vuln-scan, /triage, /patch, /customize (preventive track) plus /dnr-hunt, /dnr-respond, /verify (Detection & Response track).
- **Source evidence:**
  - `.claude/skills/quickstart/SKILL.md` exists
  - `.claude/skills/threat-model/SKILL.md` exists
  - `.claude/skills/vuln-scan/SKILL.md` exists
  - `.claude/skills/triage/SKILL.md` exists
  - `.claude/skills/patch/SKILL.md` exists
  - `.claude/skills/customize/SKILL.md` exists
  - `.claude/skills/dnr-hunt/SKILL.md` + `README.md` exist — "no-alert entry; sweep the corpus and generate alerts"
  - `.claude/skills/dnr-respond/SKILL.md` + `README.md` exist — "lead in hand: verdict, blast radius, response plan"
  - `.claude/skills/verify/SKILL.md` exists
  - `.claude/skills/_lib/` is a shared library, not a skill (9 skill dirs total)
  - `README.md` lines 30-39: "Claude Code skills: /quickstart, /threat-model, /vuln-scan, /triage, /patch, /customize"
  - `README.md` lines 40-45: "Detection & response: the /dnr-hunt and /dnr-respond skills plus dnr_harness/, their autonomous mirror (dnr-pipeline)... Demo target: targets/dnrcanary/... docs/detection-response.md"
  - `CLAUDE.md` describes the skill-based workflow for scoping, static review, and post-run triage
  - `README.md` lines 106-128 show the full day-1 workflow using these skills end-to-end
- **Verdict:** ✅ CORRECT (count corrected from 6 to 9)
- **Fix needed:** None — wiki updated to 9 skills

## Claim 4: gVisor sandboxing with dual-container trust boundary
- **Wiki says:** The pipeline runs agents inside gVisor containers with egress restricted to the Claude API. Find and grade agents run in separate containers with only PoC bytes crossing the boundary.
- **Source evidence:**
  - `README.md` lines 41-50: Security warning about sandboxing: "The autonomous reference pipeline executes target code, so it refuses to run outside of a gVisor sandbox unless explicitly overridden"
  - `README.md` line 9: gVisor reference in setup: `./scripts/setup_sandbox.sh # installs gVisor, builds the agent images, and verifies isolation`
  - `scripts/setup_sandbox.sh` exists
  - `CLAUDE.md` "Architecture" section: "Two-container trust boundary. Find and grade run in separate containers built from the same image. Only the PoC bytes cross."
  - `CLAUDE.md`: "The agent runs inside the sandbox, not on the host. bin/vp-sandboxed sets the runtime/proxy env and execs the pipeline; each find/grade/report agent then runs claude -p inside its own gVisor container"
  - `docs/security.md` and `docs/agent-sandbox.md` provide detailed sandbox documentation
  - `bin/vp-sandboxed` exists as the sandboxed entry point
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Five shipped targets including canary and real-world CVE targets
- **Wiki says:** Ships five targets: canary (fast smoke test), drlibs, alsa, htslib (real-world CVE demo targets with pinned vulnerable commits), and dnrcanary (Detection & Response demo target).
- **Source evidence:**
  - `targets/canary/README.md` exists — canary is described as single-file C program with 3 deliberately planted bugs
  - `targets/canary/THREAT_MODEL.md` exists with planted vulnerabilities (entry.c:25 heap-buffer-overflow, entry.c:38 stack-buffer-overflow, entry.c:58 heap-use-after-free)
  - `targets/drlibs/README.md` exists
  - `targets/alsa/README.md` exists
  - `targets/htslib/README.md` exists
  - `targets/dnrcanary/README.md` exists — vulnerable Flask storefront + week of web logs with planted attack campaign, benign traffic, and a noisy dead end; ships `generate_logs.py` (gitignored output), `grade.py`, `ground_truth.yaml`, `alerts.jsonl`, `config.yaml`, `example_skill_runs/`
  - `CLAUDE.md`: "Shipped targets: canary is the fast-iteration smoke test (~6min, 3 planted bugs). drlibs, alsa, and htslib are real-world CVE demo targets — pinned to vulnerable commits, with per-target READMEs documenting the CVEs and expected find times"
  - `README.md` lines 40-45: "Demo target: targets/dnrcanary/"
- **Verdict:** ✅ CORRECT (4th target count corrected to 5)
- **Fix needed:** None — wiki updated to five targets

## Claim 6: Resume-on-error with up to 20 retries per agent
- **Wiki says:** Rate limits and API errors don't kill runs. Each agent is one long-lived session; errors trigger retry with backoff, conversation context is restored via --resume, up to 20 resumes per agent.
- **Source evidence:**
  - `docs/pipeline.md` lines 165-174: "Hitting a rate limit or other error mid-run does not lose work... relaunch the agent with the Claude CLI's --resume <session_id>, which restores the full conversation so the agent can continue from the failed turn. This repeats up to 20 times before the run is marked as failed."
  - `CLAUDE.md` lines on rate limits: "A 429 or 5xx mid-run is retried inside the CLI first, and if the CLI gives up the pipeline backs off (exp, cap 300s) and relaunches with --resume <session_id> — full conversation context restored"
  - `CLAUDE.md`: "Up to 20 resumes per agent (agent.py:run_agent)"
  - `CLAUDE.md`: "The per-agent resume count is printed to stdout alongside the [find:N] done ... summary line"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Detection & Response track (dnr_harness/, dnrcanary target, docs/detection-response.md)
- **Wiki says:** The repo ships a Detection & Response track alongside the preventive pipeline — `/dnr-hunt` + `/dnr-respond` skills, their autonomous mirror `dnr-pipeline`, demo target `targets/dnrcanary/`, and `docs/detection-response.md` (README.md:40-45).
- **Source evidence:**
  - `README.md` lines 40-45: "**Detection & response**: the `/dnr-hunt` and `/dnr-respond` skills plus `dnr_harness/`, their autonomous mirror (`dnr-pipeline`). Everything else in this repo is preventive; this track assumes an attacker is already in the logs — hunt the corpus, scope the damage, and propose a response. Demo target: `targets/dnrcanary/`. See docs/detection-response.md"
  - `dnr_harness/` contains 6 modules: `__init__.py`, `agent_image.py`, `cli.py`, `config.py`, `prompts.py`, `system_prompt.py` — `cli.py:453` `def main()` with `prog="dnr-pipeline"` and a `run` subcommand ("hunt + grade, one or more runs"); invocation: `bin/vp-sandboxed dnr-pipeline run targets/dnrcanary --model <m> [--runs N --parallel]`
  - `targets/dnrcanary/` exists with `generate_logs.py`, `grade.py`, `ground_truth.yaml`, `config.yaml`, `alerts.jsonl`
  - `docs/detection-response.md` exists — documents the hunt→respond→triage→patch chain and the dnrcanary scenario ("vulnerable Flask storefront plus one week of web logs containing a planted attack campaign, benign traffic, and a noisy dead end"; logs generated locally and gitignored)
  - `docs/best-practices.md` links the DNR best practices the skills implement
- **Verdict:** ✅ CORRECT (track was absent from wiki; now added)
- **Fix needed:** None — wiki expanded to cover the D&R track

## Summary

All 7 key claims from the defending-code-reference-harness wiki have been verified against the source code:
- ✅ Anthropic reference implementation: Confirmed via README and attribution
- ✅ 7-stage pipeline: Build, Recon, Find, Grade, Judge, Report, Patch confirmed
- ✅ 9 interactive skills: /quickstart, /threat-model, /vuln-scan, /triage, /patch, /customize, /dnr-hunt, /dnr-respond, /verify all present (count corrected from 6)
- ✅ gVisor sandboxing: Dual-container trust boundary confirmed with sandbox scripts
- ✅ Five shipped targets: canary, drlibs, alsa, htslib, dnrcanary all present with CVE/demo documentation (count corrected from 4)
- ✅ Resume-on-error: 20 retry limit with --resume context restoration confirmed
- ✅ Detection & Response track: dnr_harness/ (dnr-pipeline), dnrcanary target, and docs/detection-response.md confirmed — repo scope is ~1/3 D&R, now reflected in the wiki

## Related

- [[defending-code-reference-harness]] -- Main wiki entry
- [[SecuritySkills]] -- Security assessment skills
- [[reverse-skill]] -- Reverse engineering skill
- [[Anthropic-Cybersecurity-Skills]] -- Anthropic cybersecurity skill collection

## Cross-project

- [[SWE-AF.codegraph-verify]] -- SWE agent framework codegraph verification
- [[sec-af.codegraph-verify]] -- Security agent framework codegraph verification
- [[anthropic-cybersecurity.codegraph-verify]] -- Anthropic cybersecurity codegraph verification
