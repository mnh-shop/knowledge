---
name: oh-my-hermes-codegraph-verify
tags: [hermes-agent, multi-agent, orchestration, planning, plugin, plugin-sdk, python, oh-my-hermes, wiki]
description: "Codegraph Verification: oh-my-hermes — validating wiki claims against indexed source code symbols"
source: sources/oh-my-hermes/
---

# Codegraph Verification: oh-my-hermes

**Date:** 2026-07-12

## Claim 1: Plugin manifest — tools and hooks surface
- **Wiki says:** OMH provides a Hermes plugin at `plugins/omh/` (installs to `~/.hermes/plugins/omh/`, requires Python 3.10+ and `pyyaml`) exposing the `omh_state` + `omh_gather_evidence` tools and the `pre_llm_call` / `on_session_end` / `pre_tool_call` hooks.
- **Source evidence:**
  - `plugins/omh/plugin.yaml:6-8` — `provides_tools: [omh_state, omh_gather_evidence]`
  - `plugins/omh/plugin.yaml:10-13` — `provides_hooks: [pre_llm_call, on_session_end, pre_tool_call]`
  - `plugins/omh/__init__.py` + `plugins/omh/tools/state_tool.py:132` + `tools/evidence_tool.py:79` — handler functions registered as the tool implementations
  - `README.md:43-44` — plugin installs to `~/.hermes/plugins/omh/` (Python 3.10+ and `pyyaml`); wiki Requirements section matches
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Role injection via `pre_llm_call` + 15 shared role prompts
- **Wiki says:** Fifteen shared role prompts (Planner, Architect, Critic, Executor, Verifier, Analyst, Security Reviewer, Test Engineer, Code Reviewer, Debugger, Triage Maintainer, Triage Skeptic, Researcher, Research Synthesist, Research Verifier) live in `references/role-*.md`; the `pre_llm_call` hook detects `[omh-role:NAME]` markers in `user_message` and injects the matching role into the subagent's system context.
- **Source evidence:**
  - `plugins/omh/references/` contains exactly 15 `role-*.md` files (analyst, architect, code-reviewer, critic, debugger, executor, planner, research-synthesist, research-verifier, researcher, security-reviewer, test-engineer, triage-maintainer, triage-skeptic, verifier)
  - `plugins/omh/omh_roles.py:20` — `ROLE_MARKER_RE = [omh-role:([a-zA-Z0-9_-]+)]`
  - `plugins/omh/hooks/llm_hooks.py:19,34-41` — on first turn, extracts the marker and appends `[OMH Role: {name}]` + role prompt to `context`
  - `plugins/omh/hooks/llm_hooks.py:55-88` — additionally injects active-mode awareness (phase/age) on subsequent turns
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: `pre_tool_call` is a non-blocking warning, not a validation gate
- **Wiki says:** The `pre_tool_call` hook "warns (non-blocking) on unknown `[omh-role:NAME]` markers in `delegate_task` goals — defense-in-depth typo check, not a gate." (Previously worded as "validates"; corrected.)
- **Source evidence:**
  - `plugins/omh/hooks/tool_hooks.py:4-9` — module docstring: "The hook is non-blocking: it warns but does not prevent the delegate_task call."
  - `plugins/omh/hooks/tool_hooks.py:43-45` — `debug_print` + `logger.warning` for unknown role: "warning only (non-blocking)"
  - `plugins/omh/hooks/tool_hooks.py:50-56` — returns only an injected `[OMH WARNING]` context string; the `delegate_task` call proceeds
  - `plugins/omh/hooks/tool_hooks.py:20-21` — no-op for any tool other than `delegate_task`
- **Verdict:** ✅ CORRECT (after wiki wording fix)
- **Fix needed:** Wiki now frames it as warn-only; no gate semantics claimed.

## Claim 4: 10 skills at `plugins/omh/skills/` + standalone-dependency claim is PARTIAL
- **Wiki says:** Ten skills (deep-research, ralplan, ralplan-driver, deep-interview, ralph, ralph-driver, ralph-task, triage, triage-driver, autopilot) compose into deep-research (Phase −1) → interview → ralplan → autopilot → ralph → QA/validation. Skills live at `plugins/omh/skills/<name>/` (no top-level `skills/` directory), and the standalone claim is marked PARTIAL: `omh-autopilot` hard-requires the plugin.
- **Source evidence:**
  - `plugins/omh/skills/` contains exactly 10 skill directories, each with a `SKILL.md` — there is **no** top-level `skills/` directory in the repo
  - `plugins/omh/skills/omh-autopilot/SKILL.md:27` — "The `omh` plugin must be installed (`~/.hermes/plugins/omh/`)" — hard requirement, contradicts blanket "zero dependencies"
  - All 10 `SKILL.md` frontmatters declare `requires_toolsets: [terminal, omh]` (`omh-deep-research/SKILL.md:9` adds `web`; `omh-triage/SKILL.md:9` / `omh-triage-driver/SKILL.md:9` add `delegation`)
  - `plugins/omh/skills/omh-deep-research/SKILL.md:42-47` — `omh_state` is the "preferred path" with explicit manual-JSON fallback when the plugin is absent
  - `README.md:25-32` — recommended pipeline `deep-research → interview → ralplan → ralph`, with deep-research foldable as "Phase -1 of omh-autopilot"
  - `plugins/omh/skills/omh-autopilot/SKILL.md:34-41,156-196` — Phase 3 QA cycle + Phase 4 multi-reviewer validation round (fresh-session phase boundaries)
- **Verdict:** ⚠️ CORRECT after wiki correction (skills path fixed to `plugins/omh/skills/`; standalone claim now marked PARTIAL)
- **Fix needed:** Applied to wiki (Overview dependency note + Skills location + composition diagram).

## Claim 5: `omh_state` — 13 actions and the `.omh/` convention
- **Wiki says:** `omh_state` exposes exactly 13 actions — `init, read, write, clear, check, list, list_instances, cancel, cancel_check, lock, unlock, lock_check, load_role` — with singleton + per-instance state under `.omh/state/`, advisory locks, and `load_role` for explicit role loading. `.omh/` subdirs: `state|logs|progress` gitignored, `specs|plans|research` tracked.
- **Source evidence:**
  - `plugins/omh/tools/state_tool.py:52-58` — action enum lists exactly the 13 actions
  - `plugins/omh/tools/state_tool.py:143-152` — `load_role` returns the full role prompt from the catalog
  - `plugins/omh/omh_state.py:73` — `state_dir` default `.omh/state`; `omh_state.py:129-136` — singleton `{mode}-state.json` vs per-instance `{mode}--{slug}.json`
  - `plugins/omh/omh_state.py:437-484` — advisory locks via `O_EXCL` create-or-fail with stale-pid auto-release
  - `plugins/omh/templates/dot-omh-gitignore:3-10` — `state/`, `logs/`, `progress/` ignored; `specs/`, `plans/`, `research/` tracked
  - `plugins/omh/omh_state.py:40-57` — `state_init` seeds `README.md` + `.gitignore` from `templates/`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: `omh_delegate` prepare/finalize wrapper
- **Wiki says:** `plugins/omh/omh_delegate.py` implements a prepare/finalize split: `prepare()` computes paths, writes a dispatched breadcrumb, injects the `<<<EXPECTED_OUTPUT_PATH>>>` contract; `finalize()` verifies the file exists and writes a completion breadcrumb. Artifacts land at `.omh/research/{mode}/{phase}[-r{round}][-{slug}]-{ts}.md`; breadcrumbs at `.omh/state/dispatched/{id}.{dispatched,completed}.json`.
- **Source evidence:**
  - `plugins/omh/omh_delegate.py:24` — artifact pattern documented; `omh_delegate.py:115-131` — `_compute_expected_path` implements it
  - `plugins/omh/omh_delegate.py:181-192` — `omh_delegate_prepare` (def + docstring) computes paths, writes `.dispatched.json` at `:242`
  - `plugins/omh/omh_delegate.py:220-221` — breadcrumb dir `.omh/state/dispatched`
  - `plugins/omh/omh_delegate.py:262-268` — `omh_delegate_finalize` verifies `expected_path.is_file()` (`:281`) and writes `.completed.json` (`:411-440`)
  - `plugins/omh/omh_delegate.py:149-168` — brutal-prose contract template appended to the goal
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: `omh_gather_evidence` safety rails
- **Wiki says:** The tool runs allowlisted build/test/lint commands with token-level allowlist matching, shell-metacharacter rejection, `shell=False`, output truncation (default 2000 chars / 50KB max) and timeout enforcement (default 120s / 300s max). Allowlist includes `npm test`, `cargo test`, `go test`, `python -m pytest`, `ruff check`.
- **Source evidence:**
  - `plugins/omh/tools/evidence_tool.py:28-35` — `_matches_allowlist` token-prefix check (blocks `npm testing-malicious`)
  - `plugins/omh/tools/evidence_tool.py:22` — `_SHELL_METACHAR_RE = [\n\r;&|$`<>(){}]`
  - `plugins/omh/tools/evidence_tool.py:25` — `_MAX_TRUNCATE = 50_000`; `:24` — `_MAX_TIMEOUT = 300`
  - `plugins/omh/tools/evidence_tool.py:84-85` — defaults `default_truncate: 2000`, `default_timeout: 120`
  - `plugins/omh/tools/evidence_tool.py:156-158` — `subprocess.run(..., shell=False)`
  - `plugins/omh/config.yaml:50-68` — allowlist entries: `cargo test` (:50), `go test` (:56), `python -m pytest` (:60), `ruff check` (:67)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: Repository layout — docs/, templates/, examples/, omh_config.py, ROADMAP.md
- **Wiki says:** The repo ships `docs/` with 6 guides (concepts, plugin, omh-delegate, omc-comparison, hermes-constraints, gaps) plus `docs/research/` and `docs/upstream-prs/`; `examples/plan-and-execute/`; `templates/` (dot-omh-readme.md, dot-omh-gitignore); `omh_config.py`; `ROADMAP.md`.
- **Source evidence:**
  - `docs/concepts.md`, `docs/plugin.md`, `docs/omh-delegate.md`, `docs/omc-comparison.md`, `docs/hermes-constraints.md`, `docs/gaps.md` — 6 guides present
  - `docs/research/` — 6 reference notes (hermes-multiagent, lobehub-skills-reference, omc-plugin-infrastructure, omc-ralph-reference, omc-skill-activation, omc-tools-analysis)
  - `docs/upstream-prs/per-tool-scoping.md` — proposed upstream change
  - `examples/plan-and-execute/demo.py` — worked example
  - `plugins/omh/templates/dot-omh-readme.md` + `plugins/omh/templates/dot-omh-gitignore` — `.omh/` seed files (referenced by `omh_state.py:37,46-49`)
  - `plugins/omh/omh_config.py:18-27,41-62` — config loader with `config.yaml` as single source of truth
  - `ROADMAP.md:3-7` — v1.0 skills-only → v2.0 plugin → v3.0 upstream PR
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 8 key claims from the Oh My Hermes wiki verified against source via codegraph exploration:
- ✅ Plugin manifest: `omh_state` + `omh_gather_evidence` tools, 3 hooks — confirmed
- ✅ Role injection + 15 shared role prompts — confirmed
- ✅ `pre_tool_call` non-blocking warning semantics — confirmed (wiki wording corrected)
- ⚠️ Skills location + standalone claim — path corrected to `plugins/omh/skills/`; autopilot requires plugin (PARTIAL)
- ✅ `omh_state` 13 actions + `.omh/` tracked/untracked convention — confirmed
- ✅ `omh_delegate` prepare/finalize split with breadcrumbs — confirmed
- ✅ `omh_gather_evidence` safety rails — confirmed
- ✅ Repository layout (docs/templates/examples/omh_config.py/ROADMAP) — confirmed

## Related

- [[oh-my-hermes]] -- Main wiki entry
- [[hermes-agent]] -- Core Hermes agent
- [[hermes-mcp-implementation]] -- MCP implementation Hermes integrates with

## Cross-project

- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for Hermes Agent
- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
- [[agentfield.codegraph-verify]] -- Similar codegraph verification for AgentField
- [[podman.codegraph-verify]] -- Similar codegraph verification for Podman
