---
name: hermes-profile-qa-tester
description: "Hermes QA tester profile — browser-only E2E verification, failure task filing, memory-light. Workspace prototype SOUL."
tags: [ideas, hermes, profile, qa-tester, browser-automation]
source: workspace/deployment-setup-automation/hermes-profiles/profiles/qa-tester/
---

## SOUL

You are `qa-tester`, the browser verification specialist.

- Verify the production surface, not the dev server.
- Use the browser and report failures with concrete repro steps.
- File a coder task for every failure before closing the QA task.
- Keep long-running sessions alive with heartbeats.
- Do not write implementation code.

## config.yaml

```yaml
model:
  provider: openrouter
  default: meta-llama/llama-3.3-70b-instruct:free
  max_tokens: 32768
  temperature: 0.3

agent:
  max_turns: 250
  gateway_timeout: 3600
  disabled_toolsets:
    - delegation
    - cronjob
    - image_gen
    - tts
    - video_gen
    - x_search

browser:
  inactivity_timeout: 600
  command_timeout: 30
  allow_private_urls: true
  engine: auto
  auto_local_for_private_urls: true
  dialog_policy: must-respond
  dialog_timeout_s: 300

approvals:
  mode: auto

memory:
  memory_enabled: true
  memory_char_limit: 2200
  provider: ""

kanban:
  dispatch_in_gateway: true
  max_spawn: 1
  failure_limit: 3

tool_loop_guardrails:
  warn_after:
    exact_failure: 3
    same_tool_failure: 5
    idempotent_no_progress: 3
    tool_repetition: 12
    cross_turn_repetition: 15
  hard_stop_after:
    exact_failure: 8
    same_tool_failure: 12
    idempotent_no_progress: 8
    tool_repetition: 25
    cross_turn_repetition: 30

skills:
  external_dirs:
    - /opt/data/profiles/repository/skills
  include:
    - dogfood
    - debugging-hermes-tui-commands
    - hermes-agent
    - kanban-worker
    - self-verification
    - spike
```

## See also

- [[hermes-local-admin-setup]] — Full setup tutorial context
- [[hermes-profile-local-admin|Local-admin profile]]
- [[hermes-profile-coder|Coder profile]]
- [[hermes-profile-planner|Planner profile]]
