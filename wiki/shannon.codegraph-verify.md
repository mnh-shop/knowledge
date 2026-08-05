---
name: shannon-codegraph-verify
tags: [shannon, codegraph-verify, agent, runtime]
description: "Codegraph Verification: shannon — validating wiki claims against indexed source code symbols"
source: sources/shannon/
---

# Codegraph Verification: shannon

**Date:** 2026-07-12

## Claim 1: Five-phase pentesting pipeline orchestrated by Temporal
- **Wiki says:** "Temporal orchestrates the five-phase pipeline with crash recovery, activity heartbeats, intelligent retry (3 attempts per agent), and parallel execution (5 concurrent agents in vulnerability/exploitation phases). Pipeline: Pre-Reconnaissance → Reconnaissance → Vulnerability Analysis (5 parallel agents) → Exploitation (5 parallel agents) → Reporting."
- **Source evidence:**
  - `apps/worker/src/temporal/workflows.ts` — Main `pentestPipelineWorkflow` workflow definition
  - `apps/worker/src/temporal/activities.ts` — Activity wrappers with heartbeat, retry, and container lifecycle
  - `apps/worker/src/temporal/worker.ts` — Combined worker + client entry point with per-invocation task queue
  - `apps/worker/src/temporal/pipeline.ts` — Pipeline state management (`PipelineInput`, `PipelineState`, `PipelineSummary`, `PipelineProgress`)
  - `apps/worker/src/temporal/shared.ts` — Shared types, interfaces, query definitions
  - `apps/worker/src/temporal/activity-logger.ts` — `TemporalActivityLogger` implementation
  - `apps/worker/src/temporal/summary-mapper.ts` — Maps `PipelineSummary` to `WorkflowSummary`
  - `apps/worker/src/temporal/workflow-errors.ts` — Workflow error handling
  - `apps/worker/src/temporal/workspaces.ts` — Workspace listing and management
  - `apps/worker/prompts/` — 14 phase prompt templates covering all 5 phases (`pre-recon-code.txt`, `recon.txt`, `vuln-injection.txt`, `vuln-xss.txt`, `vuln-auth.txt`, `vuln-authz.txt`, `vuln-ssrf.txt`, `exploit-injection.txt`, `exploit-xss.txt`, `exploit-auth.txt`, `exploit-authz.txt`, `exploit-ssrf.txt`, `report-executive.txt`, `validate-authentication.txt`) plus `shared/` partials and `pipeline-testing/` variants (16 total file groups)
- **Verdict:** ✅ CORRECT (9 temporal modules + 14 phase prompts + shared/pipeline-testing variants confirmed)
- **Fix needed:** None

## Claim 2: Proof-by-exploitation reporting with zero false positives
- **Wiki says:** "Proof-by-Exploitation Reports — Shannon only reports vulnerabilities it can actively exploit. Every finding includes reproducible proof-of-concept steps, eliminating the false-positive noise of traditional static analysis."
- **Source evidence:**
  - `apps/worker/src/services/reporting.ts` — Report assembly service (compiles findings into `comprehensive_security_assessment_report.md`)
  - `apps/worker/src/services/findings-renderer.ts` — Converts exploitation queue data to findings (deterministic when exploitation disabled — no LLM in the loop)
  - `apps/worker/prompts/report-executive.txt` — Executive-level report prompt template
  - `apps/worker/src/paths.ts` — `FINAL_REPORT_FILENAME` constant for report output
  - `CLAUDE.md` — Documents: "Shannon only reports vulnerabilities it can actively exploit"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Temporal durable workflow execution with crash recovery
- **Wiki says:** "Temporal orchestrates the five-phase pipeline with crash recovery, activity heartbeats, intelligent retry (3 attempts per agent), and parallel execution (5 concurrent agents in vulnerability/exploitation phases). Infra runs via Docker Compose (Temporal server on port 7233/8233). Workers are ephemeral `docker run --rm` containers."
- **Source evidence:**
  - `docker-compose.yml:11-12` — Temporal server on ports 7233 (gRPC) and 8233 (Web UI) with SQLite persistence
  - `Dockerfile:6` — Builder stage from `cgr.dev/chainguard/wolfi-base:latest`; `Dockerfile:44` — runtime stage, minimal Wolfi production image
  - `apps/cli/src/docker.ts` — Compose lifecycle, image pull/build, ephemeral `docker run` worker spawning
  - `apps/cli/infra/compose.yml` — Bundled Temporal compose file for npx mode
  - `apps/worker/src/temporal/activities.ts` — Heartbeat loop, error classification, output-validation retry (`attemptNumber`)
  - `apps/worker/src/temporal/workflows.ts:140` — "Credential rejection is not retryable; transient provider errors get 3 attempts"
  - `apps/worker/src/services/agent-execution.ts` — `AgentExecutionService` agent lifecycle; CLAUDE.md documents "automatic retry (3 attempts per agent)"
  - `apps/cli/src/commands/start.ts` — Run dispatch including `forwardEtcHostsFlags` for host networking
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Five OWASP vulnerability classes with parallel agents
- **Wiki says:** "Targets exploitable Injection (SQL, NoSQL, command), XSS, SSRF, Broken Authentication, and Broken Authorization vulnerabilities. 5 parallel agents in vulnerability analysis and 5 in exploitation."
- **Source evidence:**
  - `apps/worker/prompts/vuln-injection.txt` — Injection vulnerability agent prompt
  - `apps/worker/prompts/vuln-xss.txt` — XSS vulnerability agent prompt
  - `apps/worker/prompts/vuln-auth.txt` — Authentication vulnerability agent prompt
  - `apps/worker/prompts/vuln-authz.txt` — Authorization vulnerability agent prompt
  - `apps/worker/prompts/vuln-ssrf.txt` — SSRF vulnerability agent prompt
  - `apps/worker/prompts/exploit-injection.txt` — Injection exploit agent prompt
  - `apps/worker/prompts/exploit-xss.txt` — XSS exploit agent prompt
  - `apps/worker/prompts/exploit-auth.txt` — Authentication exploit agent prompt
  - `apps/worker/prompts/exploit-authz.txt` — Authorization exploit agent prompt
  - `apps/worker/prompts/exploit-ssrf.txt` — SSRF exploit agent prompt
  - `apps/worker/src/session-manager.ts:169-181` — Agent definitions in `AGENTS` record mapping `vuln-*`/`exploit-*` phases to `agent1..agent5` (5 parallel slots)
  - `apps/worker/src/types/agents.ts` — `AgentDefinition`, `AgentName` types
- **Verdict:** ✅ CORRECT (10 agent prompts across 5 vulnerability classes, 5 parallel agent slots confirmed)
- **Fix needed:** None

## Claim 5: Dual CLI mode (npx + local) with auto-detection
- **Wiki says:** "Two modes: npx mode (`npx @keygraph/shannon start`) for zero-install use, and local mode (cloned repository with `./shannon start`). Auto-detected based on the `SHANNON_LOCAL=1` environment variable."
- **Source evidence:**
  - `shannon` — Local entry point (`#!/usr/bin/env node`) that sets `SHANNON_LOCAL=1` then delegates to `apps/cli/dist/index.mjs`
  - `apps/cli/src/index.ts` — CLI dispatcher for `setup`, `start`, `stop`, `logs`, `workspaces`, `status`, `build`, `uninstall`, `version`
  - `apps/cli/src/mode.ts:15` — Mode auto-detection: `process.env.SHANNON_LOCAL === '1' ? 'local' : 'npx'`
  - `apps/cli/src/home.ts` — State directory management (`~/.shannon/` for npx, `./` for local)
  - `apps/cli/package.json` — Published as `@keygraph/shannon` on npm
  - `apps/cli/tsdown.config.ts` — tsdown bundler for single-file ESM output
  - `CLAUDE.md` — Documents dual-mode operation with comparison table
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: White-box attack planning with source code analysis
- **Wiki says:** "White-Box Attack Planning — Source-code analysis guides dynamic testing, focusing the pentest on realistic attack paths rather than spraying generic payloads."
- **Source evidence:**
  - `apps/worker/prompts/pre-recon-code.txt` — Pre-reconnaissance source code analysis prompt
  - `apps/worker/prompts/recon.txt` — Reconnaissance prompt for runtime exploration
  - `apps/worker/src/collectors/pre-recon-collector.ts` — Pre-recon data collection pi custom tool with `ArchitectureSchema` (moved from `mcp-server/` to `src/collectors/`)
  - `apps/worker/src/collectors/recon-collector.ts` — Recon data collection with `RoleArchitectureInput`, `InjectionSourcesInput`
  - `apps/worker/src/services/pre-recon-renderer.ts` — Deterministic pre-recon collector → Markdown renderer (no LLM)
  - `apps/worker/src/services/recon-renderer.ts` — Recon data rendering for agent context
  - `apps/worker/src/services/prompt-manager.ts` — Prompt variable substitution (`{{TARGET_URL}}`, `{{CONFIG_CONTEXT}}`)
  - `apps/cli/src/paths.ts` — Repo path resolution for source code access
- **Verdict:** ✅ CORRECT (collector paths updated from `mcp-server/` to `src/collectors/`)
- **Fix needed:** Applied — verify page and wiki now cite `src/collectors/` + `services/pre-recon-renderer.ts`

## Claim 7: Resumable workspaces with session.json checkpointing
- **Wiki says:** "Named workspaces with session.json checkpointing enable interrupted scans to resume without re-running completed agents. Workspace state includes deliverables, agent logs, prompts, and browser artifacts."
- **Source evidence:**
  - `apps/worker/src/session-manager.ts` — Agent definitions and session state management
  - `apps/worker/src/temporal/workspaces.ts` — Workspace listing and inspection
  - `apps/worker/src/temporal/activities.ts:780-804` — `loadResumeState()` validates deliverable existence, restores git checkpoints, cleans up incomplete deliverables
  - `apps/worker/src/temporal/shared.ts` — `PipelineState` for session checkpoint data
  - `apps/worker/src/paths.ts` — Path resolution for workspace state files
  - `apps/worker/src/audit/utils.ts` — Audit path generation including `generateAuditPath()` and `generateInternalPath()`
  - `apps/cli/src/commands/start.ts` — `-w <name>` flag for named workspace (auto-resumes if exists)
  - `apps/worker/src/services/container.ts` — DI container with per-workflow scoping
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: Runs on the pi harness — no Claude Agent SDK, no Google Vertex AI
- **Wiki says:** "Worker Package runs on the pi harness (`@earendil-works/pi-agent-core`, `pi-ai`, `pi-coding-agent` ^0.79.1) via `apps/worker/src/ai/pi/pi-executor.ts`. Code path avoid rules are enforced via the `@gotgenes/pi-permission-system` extension. Officially supported Claude models (Opus 4.6/4.7/4.8 adaptive thinking), AWS Bedrock, and custom Anthropic-compatible endpoints."
- **Source evidence:**
  - `apps/worker/package.json:22-24` — Dependencies `@earendil-works/pi-agent-core`, `@earendil-works/pi-ai`, `@earendil-works/pi-coding-agent` all `^0.79.1`; `package.json:25` — `@gotgenes/pi-permission-system` `^10.9.0`. No Claude Agent SDK dependency anywhere
  - `apps/worker/src/ai/pi/pi-executor.ts:56-64` — `buildPlaywrightSkill()` injects the `playwright-cli` Skill for browser-using agents
  - `apps/worker/src/ai/pi/permission-system.ts` — `syncPermissionSystemConfig` writes global `path` deny config for the pi permission-system extension
  - `CLAUDE.md:130` — "`apps/worker/src/ai/pi/pi-executor.ts` — pi harness integration (retry disabled; Temporal owns retry)"
  - `CLAUDE.md:176` — "Harness-First — the pi harness (`@earendil-works/pi-coding-agent`) handles autonomous analysis"
  - `apps/worker/src/ai/models.ts:88` — `supportsAdaptiveThinking` matches `opus-4-[678]` (Opus 4.6/4.7/4.8 only); `models.ts:96-97` — adaptive thinking mapped to pi's `medium` level, everything else `off`
  - `docs/ai-providers.md:27` — AWS Bedrock section (small/medium/large model tiers); `docs/ai-providers.md:63` — "Custom Base URL … Anthropic-compatible endpoint" via `ANTHROPIC_BASE_URL`. No Google Vertex AI provider in code or docs (only a checklist option in `.github/ISSUE_TEMPLATE/bug_report.yml`)
  - Grep for `maxTurns` / "Claude Agent SDK": only `README.md:93` mentioning the `shannon-v1` branch ("last release built on the Claude Agent SDK") — the current repo does not use it
- **Verdict:** ✅ CORRECT (earlier wiki claims of "Claude Agent SDK with maxTurns: 10_000", "bypass-permissions mode", "~/.claude/settings.json deny lists", and "Google Vertex AI" were REMOVED)
- **Fix needed:** Applied — wiki now describes the pi harness, permission-system config, and provider matrix accurately

## Summary

All 8 key claims from the Shannon wiki have been verified against the source code:
- ✅ **Five-phase pipeline:** Temporal workflow with 9 modules + 14 phase prompts confirmed
- ✅ **Proof-by-exploitation:** Deterministic findings rendering + report assembly confirmed
- ✅ **Durable execution:** Temporal Docker Compose + 2-stage Wolfi worker image + 3-attempt retry confirmed
- ✅ **OWASP vulnerability classes:** 5 vuln + 5 exploit agent prompts, agent1..agent5 slots confirmed
- ✅ **Dual CLI mode:** `shannon` + `apps/cli/src/mode.ts:15` with SHANNON_LOCAL=1 auto-detection confirmed
- ✅ **White-box planning:** pre-recon/recon collectors in `src/collectors/` + deterministic renderers confirmed
- ✅ **Resumable workspaces:** session.json checkpointing, `loadResumeState()` at activities.ts:780-804, `-w` flag confirmed
- ✅ **pi harness migration:** `@earendil-works/pi-*` ^0.79.1 deps, `pi-executor.ts`, `permission-system.ts`, CLAUDE.md:130/176 confirmed; Claude Agent SDK, maxTurns, bypass-permissions, and Vertex AI claims removed

## Related

- [[shannon]] -- Main wiki entry
- [[pi]] -- TypeScript agent harness Shannon runs on

## Cross-project

- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for Hermes Agent
- [[turnstone.codegraph-verify]] -- Similar codegraph verification for Turnstone
- [[nanobot.codegraph-verify]] -- Similar codegraph verification for Nanobot
