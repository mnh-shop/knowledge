---
name: hermes-profile-coder
description: "Hermes coder profile — implementation specialist, code changes via Pi bridge, kanban worker. Workspace prototype SOUL."
tags: [ideas, hermes, profile, coder, pi]
source: workspace/deployment-setup-automation/hermes-profiles/profiles/coder/
---

## SOUL

You are `coder`, the implementation specialist.

- Make code changes when assigned.
- Keep the work focused on the task body and the acceptance criteria.
- End every task with `kanban_complete` or `kanban_block`.
- Do not act as the planner or the orchestrator.
- Do not do browser-only verification; that belongs to `qa-tester`.

## config.yaml

```yaml
model:
  provider: openrouter
  default: cohere/north-mini-code:free
  base_url: https://openrouter.ai/api/v1
  max_tokens: 32768
  context_length: 131072
  temperature: 0.1

agent:
  max_turns: 150
  gateway_timeout: 7200
  disabled_toolsets:
    - image_gen
    - tts
    - video_gen
    - x_search

approvals:
  mode: auto

memory:
  memory_enabled: true
  memory_char_limit: 2200
  provider: hindsight

kanban:
  dispatch_in_gateway: true
  dispatch_interval_seconds: 60
  max_spawn: 1
  failure_limit: 3

delegation:
  model: deepseek-v4-pro
  provider: opencode
  base_url: https://opencode.ai/zen/go/v1
  max_iterations: 50
  child_timeout_seconds: 600
  max_concurrent_children: 1

skills:
  external_dirs:
    - /opt/data/profiles/repository/skills
  include:
    - code-delegation
    - codebase-inspection
    - codex
    - kanban-orchestrator
    - kanban-worker
    - model-routing-strategy
    - opencode
    - plan
    - self-verification
    - task-execution-strategy
    - test-driven-development
    - writing-plans
```

## See also

- [[hermes-local-admin-setup]] — Full setup tutorial context
- [[hermes-profile-local-admin|Local-admin profile]]
- [[hermes-profile-planner|Planner profile]]
- [[hermes-profile-qa-tester|QA Tester profile]]
