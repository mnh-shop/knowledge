---
name: hermes-incident-commander-architecture
description: "RL training environment design for Hermes Incident Commander: reward function, incident scenarios, Atropos integration, and sandboxed execution"
tags: [architecture, docker, messaging, monitoring, optimization, plugin-sdk, skills-platform]
---

# Hermes Incident Commander -- RL Training Environment Architecture

## Overview

The RL training environment in `environments/incident_env.py` is the most architecturally deep component of Hermes Incident Commander. It integrates with the [[../../hermes-agent|Hermes Agent]] Atropos framework to create a reinforcement learning loop for autonomous incident response, enabling GRPO (Group Relative Policy Optimization) training of LLM-based SRE agents.

## Architecture Diagram

```
  IncidentCommanderEnv (HermesAgentBaseEnv)
  │
  ├── IncidentScenario definitions (5 scenarios)
  │   ├── svc-crash-nginx     (P0, service)
  │   ├── disk-full-logs      (P1, disk)
  │   ├── memory-leak-process (P1, memory)
  │   ├── cpu-runaway-process (P2, cpu)
  │   └── failed-systemd-unit (P2, service)
  │
  ├── _setup_environment()
  │   └── injects broken system state into Docker sandbox
  │       └── via ctx.terminal() bash commands
  │
  ├── run_agent_loop()        # from HermesAgentBaseEnv
  │   ├── agent runs tool-calling loop (terminal, file, web, delegate)
  │   └── returns AgentResult (messages, tool_calls, turn count)
  │
  ├── _compute_reward()
  │   ├── 1. Resolution score      (50%) -- verify success criteria
  │   ├── 2. RCA quality score     (15%) -- keyword match on reasoning
  │   ├── 3. Report quality score  (15%) -- post-mortem file written?
  │   ├── 4. Skill created score   (10%) -- prevention skill generated?
  │   ├── 5. Response speed score   (5%) -- faster turns = higher score
  │   └── 6. Tool efficiency score  (5%) -- fewer unnecessary calls
  │
  ├── evaluate()
  │   └── runs all scenarios with configurable weights
  │       └── returns mean_reward + critical_reward (P0/P1 only)
  │
  └── CLI entry points
      ├── process   -- generate SFT training trajectories (ShareGPT JSONL)
      ├── serve     -- run full GRPO training loop via Atropos
      └── smoke     -- run smoke test to verify environment works
```

## Key Components

### IncidentScenario Dataclass

Each scenario defines:
- `system_state`: Dict of bash commands to set up the broken environment (e.g., create large files, start CPU-hungry process, stop nginx)
- `success_criteria`: List of bash commands that must succeed (exit 0) to confirm resolution
- `partial_criteria`: List of bash commands whose success indicates partial recovery
- `severity` / `category`: Used for reward weighting and scenario sampling

### Reward Function Detail

The reward is computed as a weighted sum of 6 components, defined in `incident_config.yaml`:

| Component | Weight | Computation |
|-----------|--------|-------------|
| Resolution | 0.50 | (passed_success / total_success) * 0.50 + (passed_partial / total_partial) * 0.0 (partial counts only in resolution context) |
| RCA Quality | 0.15 | Keyword hit rate on terms like "root cause", "because", "triggered by", "led to", "caused by", "resulted in" -- capped at 1.0 |
| Report Quality | 0.15 | Boolean: was a structured post-incident report written to `~/.hermes/incidents/`? |
| Skill Created | 0.10 | Boolean: did the agent create new prevention skill files? + 0.05 if skill-related keywords appear in conversation |
| Response Speed | 0.05 | Linear ramp: full bonus at <=8 turns, zero at >=20 turns |
| Tool Efficiency | 0.05 | Linear ramp: full bonus at <=15 tool calls, zero at >=30 calls |

Severity weighting amplifies rewards for harder scenarios: P0 = 3.0x, P1 = 2.0x, P2 = 1.5x, P3 = 1.0x.

### Training Configuration

```yaml
environment:
  terminal_backend: docker      # Sandboxed execution environment
  enabled_toolsets: [terminal, file, web, delegate]
  max_turns: 30                 # Episode truncation limit
training:
  num_workers: 4                # Parallel rollout workers
  batch_size: 16
  rollouts_per_eval: 50
  save_trajectory: true
  export_sharegpt: true         # Outputs ShareGPT-format JSONL
model:
  model_name: openrouter/nousresearch/hermes-3-llama-3.1-405b
  server_type: openai
```

### Terminal Backend

Currently supports Docker (sandboxed containers for scenario injection and verification). The `terminal_backend` config key allows swapping to Modal or SSH for multi-node scenarios. The backend must support running arbitrary bash commands and returning structured results.

## Data Flow

1. Trainer (Atropos) calls `IncidentCommanderEnv.get_next_item()` which samples a scenario weighted by severity
2. `_setup_environment()` runs injection commands in the sandbox via `ctx.terminal()`
3. Agent runs its tool-calling loop against the broken environment (up to 30 turns)
4. `_compute_reward()` executes verification commands and analyzes the conversation
5. Scores are packaged with trajectory data for Atropos GRPO training
6. Results logged to Weights & Biases (if configured)

## Related

- [[../../hermes-incident-commander|Hermes Incident Commander]] -- Project overview
- [[../../hermes-agent|Hermes Agent]] -- Underlying agent platform by NousResearch
