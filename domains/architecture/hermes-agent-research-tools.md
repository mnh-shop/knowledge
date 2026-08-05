---
name: hermes-agent-research-tools
tags: [curator, data-generation, hermes-agent, reinforcement-learning, research, trajectories, training-data]
description: "Hermes Agent research/data-gen tooling: batch_runner, mini_swe_runner, trajectory_compressor, toolset_distributions, and the skill-usage Curator"
source: sources/hermes-agent/
---

# Hermes Agent Research & Data-Generation Tools

Hermes ships a set of **data-generation tools** at the repo root for producing
agent trajectories used in reinforcement-learning / model training, plus a
**curator** subsystem that turns real skill-usage telemetry into a
self-maintaining skill library. These are separate from the runtime agent —
they drive the same core agent (via `run_agent.py` / `AIAgent`) but exist to
emit training data.

## Data-Gen Pipeline

```
prompts (JSONL)
   │
   ▼
batch_runner.py  ──parallel multiprocessing over prompts──►  trajectories.jsonl
   │                                                              │
   └── toolset_distributions.py (which toolsets per prompt)      │
                                                                  ▼
mini_swe_runner.py  ──SWE tasks via local/docker/modal envs──►  Hermes-format
                                                                  trajectories
                                                                  │
                                                                  ▼
trajectory_compressor.py  ──token-budget compression─────────►  compressed
                                                                  trajectories
```

| Tool | Role |
|------|------|
| `batch_runner.py` | Parallel batch processing across a dataset with checkpointing + resume |
| `mini_swe_runner.py` | SWE-bench-style runner producing Hermes-format trajectories via execution environments |
| `trajectory_compressor.py` | Post-processes trajectories to a token budget while preserving training signal |
| `toolset_distributions.py` | Declarative toolset→probability distributions for data-gen runs |
| `datagen-config-examples/` | Example configs (`web_research.yaml`, `trajectory_compression.yaml`, `example_browser_tasks.jsonl`, `run_browser_tasks.sh`) |

## `batch_runner.py`

Parallel batch runner for running the agent across a dataset:

- Dataset loading and batching; multiprocessing parallelism.
- **Checkpointing** for fault tolerance and resumption (`--resume`).
- Trajectory saving in the proper format (from/value pairs).
- **Tool-usage statistics** aggregated across all batches.

```bash
python batch_runner.py --dataset_file=data.jsonl --batch_size=10 --run_name=my_run
python batch_runner.py --dataset_file=data.jsonl --batch_size=10 --run_name=my_run --resume
python batch_runner.py --dataset_file=data.jsonl --batch_size=10 --run_name=my_run --distribution=image_gen
```

Note: `hermes_bootstrap` must be the **first import** (UTF-8 stdio on
Windows; no-op on POSIX) — see [[hermes-agent-deployment]] for the bootstrap
rationale.

## `mini_swe_runner.py`

SWE runner that uses Hermes' built-in execution environments (`local`,
`docker`, `modal`) and emits trajectories in the Hermes-Agent format,
compatible with `batch_runner.py` and `trajectory_compressor.py`
(from/value pairs with `<tool_call>`/`<tool_response>` XML):

```bash
python mini_swe_runner.py --task "Create a hello world Python script" --env local
python mini_swe_runner.py --task "List files in /tmp" --env docker --image python:3.11-slim
python mini_swe_runner.py --prompts_file prompts.jsonl --output_file trajectories.jsonl --env docker
```

## `trajectory_compressor.py`

Compresses completed trajectories within a target token budget while
preserving training signal:

1. **Protect** first turns (system, human, first gpt, first tool).
2. **Protect** last N turns (final actions and conclusions).
3. Compress **middle** turns only, starting from the 2nd tool response.
4. Compress only as much as needed to fit the target.
5. Replace the compressed region with a **single human summary message**.
6. Keep remaining tool calls intact (model continues working after summary).

```bash
python trajectory_compressor.py --input=data/my_run
python trajectory_compressor.py --input=data/trajectories.jsonl --sample_percent=15
python trajectory_compressor.py --input=data/trajectories.jsonl --output=compressed.jsonl --target_max_tokens=16000
```

## `toolset_distributions.py`

Declarative distributions mapping **toolset name → selection probability (%)**
for any given prompt during batch runs. Probabilities are normalized if they
don't sum to 100.

```python
from toolset_distributions import get_distribution, list_distributions

dist = get_distribution("image_gen")   # {"image_gen": 60, "web": 40, ...}
all_dists = list_distributions()
```

Built-in distributions (verified keys): `default`, `image_gen`, `research`,
`science`, `development`, `safe`, `balanced`, `minimal`, `terminal_only`,
`terminal_web`, `creative`, `reasoning`, `browser_use`, `browser_only`,
`browser_tasks`, `terminal_tasks`, `mixed_tasks`. Each is validated against
`toolsets.py` (`validate_toolset`).

## Curator: Skill-Usage-Driven Skill Lifecycle

The Curator is a background skill-maintenance system that tracks usage on
agent-created skills and auto-archives stale ones. Users never lose skills —
archives go to `~/.hermes/skills/.archive/` and are restorable. This is the
"research" angle in production: it continuously emits real skill-usage data.

### Components

| Component | Purpose |
|-----------|---------|
| `agent/curator.py` | Review loop, auto-transitions, LLM review prompt |
| `agent/curator_backup.py` | Pre-run tar.gz snapshots |
| `hermes_cli/curator.py` | `hermes curator <verb>` CLI tree |
| `tools/skill_usage.py` | Sidecar usage telemetry `~/.hermes/skills/.usage.json` |

### CLI verbs (`hermes_cli/curator.py`, verified parsers)

`status`, `usage`, `run`, `pause`, `resume`, `pin`, `unpin`, `archive`,
`restore`, `list-archived`, `prune`, `backup`, `rollback`, `adopt`.

### Telemetry model (`tools/skill_usage.py`)

Per-skill counters in a **sidecar JSON** (`~/.hermes/skills/.usage.json`),
not frontmatter — keeps operational telemetry out of user-authored SKILL.md
content. Counters are bumped by the existing skill tools (`skill_view`,
`skill_manage`); bumps are best-effort (failures log at DEBUG and return
silently, so a broken sidecar never breaks the underlying tool call).

Tracked fields: `use_count`, `view_count`, `patch_count`, `last_activity_at`,
`state` (`active` / `stale` / `archived`), `pinned`.

Lifecycle states:

```
active  →  stale (unused > stale_after_days)  →  archived (unused > archive_after_days; moved to .archive/)
pinned  →  opt-out from auto transitions (orthogonal boolean)
```

### Invariants

- Curator only touches skills with `created_by: "agent"` provenance — bundled
  and hub-installed skills are off-limits.
- **Never deletes**; the max destructive action is archive.
- Pinned skills are exempt from every auto-transition and the LLM review pass.
- `skill_manage(action="delete")` refuses pinned skills; patch/edit/
  write_file/remove_file still go through so the agent can keep improving
  pinned skills.
- Atomic writes via `tempfile + os.replace` (same pattern as
  `.bundled_manifest`).

### Config (`curator:`)

`enabled`, `interval_hours`, `min_idle_hours`, `stale_after_days`,
`archive_after_days`, `backup.*` — full reference in
[[hermes-agent-configuration]]. The `auxiliary` config section pins the
LLM used for curator review work (per-task side-LLM overrides via
`agent/auxiliary_client.py::_resolve_auto`).

## Related

- [[hermes-agent-configuration]] -- `curator.*` and `auxiliary.*` config keys
- [[hermes-agent-observability]] -- ATOF/ATIF trajectory formats and NeMo Relay
- [[hermes-agent-architecture]] -- Core agent loop these tools drive
