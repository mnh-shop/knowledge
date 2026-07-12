---
name: orchestrator-profile
description: Orchestrator — decomposes questions into specialist workflows, routes work, synthesizes outputs
tags: [agent-profile, hermes-agent, profile, orchestration-methodology, multi-agent]
metadata:
  type: reference
source: sources/hermes-profiles/
---

# Orchestrator — Key Reference

Orchestrator profile for Hermes Agent. Decomposes complex questions into specialist workflows, routes work to the right profile in the right sequence, and synthesizes outputs into coherent results. Owns conversation structure, not execution.

**Usage:** `hermes --profile orchestrator`

**Skills:** artifact-pyramids, orchestration-methodology

## Workflow Pattern

The orchestrator runs specialists sequentially or in parallel:

1. Decompose the question into specialist tasks
2. Route each task to the appropriate profile
3. Collect outputs (paths to artifact-pyramids)
4. Synthesize final composite response

## Related

- [[hermes-profiles-index]] -- Full profile catalog
- [[hermes-agent]] -- Main Hermes Agent
- [[orchestration-methodology]] -- Multi-agent workflow skill
- [[hermes-workspace]] -- Swarm orchestration alternative