---
name: Hermes-caduceus-codegraph-verify
tags: [codegraph-verify, hermes-caduceus, hermes-agent]
description: "Codegraph Verification: Hermes-caduceus"
source: sources/Hermes-caduceus/
date: 2026-07-12
---

# Codegraph Verification: Hermes-caduceus

**Date:** 2026-07-12

## Claim 1: Caduceus deep-planning mode with live todo list and verification
- **Wiki says:** Caduceus adds a deep-planning mode to Hermes Agent. With `/caduceus on`, the agent plans with a live todo list, drives one step at a time, and verifies before claiming done.

- **Source evidence:** `README.md` lines 47-48 describe the deep-planning layer: "Plans with a live `todo` list and drives it one step at a time, verifies before claiming done, and right-sizes trivial asks (no ceremony)." The mode is toggled with `/caduceus on`, is "off by default, session-scoped, additive, fully reversible" (line 23-24). The `install_caduceus.py` line 10-11 states: "leaves Caduceus OFF by default (opt-in via `/caduceus on`)." `README.md` lines 38-40 explain the three composable layers: "Each turns on only when you need it — and the whole mode is a no-op when it's off." Source file `agent/caduceus.py` (listed in `install_caduceus.py` line 51 manifest) implements the deep-planning loop logic.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: The Loom — deterministic multi-agent workflow engine
- **Wiki says:** The Loom is a deterministic async workflow engine with `agent()`, `parallel()`, and `pipeline()` primitives, structured output, shared budgets, and per-run caching with resume.

- **Source evidence:** `README.md` lines 61-67 document The Loom: "You don't write scripts yourself; the agent authors a small Python workflow and runs it on the Loom — with structured output, a shared token budget, and per-run caching + resume (edit the script, re-run, unchanged calls return instantly)." The feature table (lines 46-51) lists the Loom as the second layer with primitives `agent()` / `parallel()` / `pipeline()`. The `install_caduceus.py` manifest (lines 54-66) lists all workflow engine modules in `agent/workflow/`: `dsl.py` (primitives), `engine.py` (execution engine), `budget.py` (shared budgets), `events.py` (event model), `journal.py` (run journal), `runner.py` (workflow runner), `reliability.py` (reliability), `sandbox.py` (sandbox), `scheduler.py` (scheduling), `structured.py` (structured output). Source file `tools/workflow_tool.py` exposes the workflow tool to the agent.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Auto Router routes workers to cheapest capable model
- **Wiki says:** The Auto Router scores each worker on capability (not price) and routes it to the cheapest configured model that can do that subtask. The orchestrator always keeps the session model.

- **Source evidence:** `README.md` lines 69-75 document the Auto Router: "With many models configured, you don't want to pay frontier prices on trivial subtasks. The Auto Router scores each **worker** on capability (never price) and sends it to the cheapest model that clears the bar. The **orchestrator always keeps your session model**." The feature table (line 50) documents it as the third layer: "Routes each delegated worker to the cheapest configured model that can do *that* subtask." Toggle command is `/caduceus auto on`. Source file `agent/auto_router.py` is listed in `install_caduceus.py` line 52 manifest. A router architecture image is referenced at `docs/caduceus/assets/caduceus-router.png`.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Local GPU workers for running workflows on local models
- **Wiki says:** Caduceus supports hot-swappable local GPU workers that run workflow tasks on local models, parallelized to the model's serving slots, while the orchestrator stays on the cloud model.

- **Source evidence:** `README.md` line 51 documents Local GPU workers as the fourth layer: "Run workflow workers on local models on your GPU — hot-swapped on demand, parallelized to the model's serving slots; the orchestrator stays on your cloud model." Toggle command is `/local on`. Source file `agent/local_manager.py` is listed in `install_caduceus.py` line 53 manifest. Dedicated documentation at `docs/caduceus/LOCAL.md` provides a full user guide for local GPU worker setup. The `docs/caduceus/` user guide directory includes full LOCAL.md documentation.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Orchestration Theater live UI in Hermes Desktop
- **Wiki says:** When a workflow runs, the Hermes Desktop app opens a live Orchestration Theater showing phase lanes, per-agent model badges, token burn, live concurrency, and a shared budget gauge.

- **Source evidence:** `README.md` lines 55-59 document the Orchestration Theater: "Say **'workflow'** and Caduceus fans out across subagents on the Loom. The **Hermes Desktop** app opens a live **Orchestration Theater** — phase lanes, per-agent model badges (orchestrator gold, workers blue), token burn, live concurrency, and a shared budget gauge." The `install_caduceus.py` manifest (lines 82-93) lists desktop UI components: `apps/desktop/src/app/shell/caduceus-menu-panel.tsx`, `apps/desktop/src/components/workflow/AgentCard.tsx`, `apps/desktop/src/components/workflow/TheaterPanels.tsx`, `apps/desktop/src/components/workflow/WorkflowTheater.tsx`, and store files `apps/desktop/src/store/caduceus.ts` and `apps/desktop/src/store/workflow.ts`. A theater screenshot is referenced at `docs/caduceus/assets/caduceus-theater.png`.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Safe, reversible install with full backup/restore
- **Wiki says:** The Caduceus installer backs up every file it touches, writes a restore manifest, and can be fully undone with `--uninstall`. It is idempotent and pure stdlib.

- **Source evidence:** `install_caduceus.py` lines 7-11: "This script overlays the Caduceus files from THIS checkout onto a target `hermes-agent` install, backing up every file it touches so the change is fully reversible. It is **safe**: it backs up before writing, writes a restore manifest, never deletes anything it didn't add, leaves Caduceus OFF by default (opt-in via `/caduceus on`), and is idempotent. Pure standard library — nothing to pip." Line 20 documents `--uninstall`: "restore the most recent backup." `README.md` line 35: "The installer auto-detects your Hermes install, backs up every file it touches, and can be fully undone with `--uninstall`." `BUILT_FOR_VERSION = "0.15.1"` (line 42) and `BASE_COMMIT = "b34ee8074"` (line 43) document the exact Hermes version the overlay targets.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: 357 passing tests across the codebase
- **Wiki says:** Caduceus ships with 357 passing tests, including new workflow engine tests, desktop UI tests, and integration tests.

- **Source evidence:** README badge at line 10 shows `tests-357_passing-22C55E`. `README.md` line 24 states "fully tested (357 passing tests)." The `install_caduceus.py` manifest (lines 94-103) includes test files and test fixtures. `HERMES_CORE_TOOLS` in `toolsets.py` lines 31-60 show the caduceus workflow tool integrated into the core toolset. Test infrastructure follows Hermes's existing `scripts/run_tests.sh` and `tests/conftest.py` patterns documented in `AGENTS.md`.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[Hermes-caduceus]] -- Main wiki entry
- [[hermes-agent]] -- Upstream Hermes Agent
- [[hermes-workspace]] -- Hermes Workspace
- [[hermes-bus]] -- Hermes Bus

## Cross-project

- [[hermes-agent.codegraph-verify]] -- Hermes Agent verification
- [[hermes-workspace.codegraph-verify]] -- Hermes Workspace verification
- [[hermes-bus.codegraph-verify]] -- Hermes Bus verification
