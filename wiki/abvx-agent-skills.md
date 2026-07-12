---
name: abvx-agent-skills
title: ABVX Agent Skills
description: "Small auditable skillpack for coding agents — smaller diffs, evidence-based debugging, compact shell output, verification steps"
source: sources/abvx-agent-skills/
authors:
  - admin1
date: 2026-06-25
tags: [cli, git, skills, plugin, python, abvx-agent-skills, agent, automation]
---

# ABVX Agent Skills

ABVX Agent Skills is a small, auditable skillpack for coding agents that helps them write smaller diffs, debug from evidence, compact noisy shell output, and verify work before saying done. Contains skills organized by job functions like token economy, debugging, frontend development, and more.

## Description

This project provides compact `SKILL.md` workflows with clear triggers, attribution, risk notes, and validation. Unlike prompt dumps, these are portable, versioned agent capabilities meant to be previewed, inspected, and loaded on demand through the Agent Skills progressive-disclosure model.

The repository assumes that many public AI skills are net-negative. The bar here is not novelty or stars, but whether a skill adds usable structure without degrading behavior. Skills are organized by job function: token economy for saving context, debugging for evidence-based fixes, frontend verification for real browser behavior checks, and LoopOps for workflow evolution.

## Key Features

- **Minimal diffs**: The `minimal-diff-builder` skill helps agents implement the smallest correct fix without unnecessary refactoring or abstraction creep
- **Evidence-based debugging**: The `diagnose` skill ensures agents reproduce failures and verify results rather than guessing fixes
- **Shell output compaction**: Skills like `shell-output-compaction` and `rtk-assisted-shell` prevent logs and diffs from burning context
- **Frontend verification**: `browser-verification` and `design-critique-polish` check real browser behavior, layout, states, and console errors
- **Progressive disclosure**: Skills can be previewed before installing via `gh skill preview` command
- **LoopOps framework**: Decides when repeated prompts should become checklists, skills, scripts, or bounded loops

## Catalog

Browse the searchable catalog at [lab.abvx.xyz/tools/abvx-agent-skills/](https://lab.abvx.xyz/tools/abvx-agent-skills/). The repository also includes a scan-friendly text catalog in [CATALOG.md](CATALOG.md) for browsing and indexing.

## Quick Start

Preview a skill before installing:

```bash
gh skill preview markoblogo/abvx-agent-skills minimal-diff-builder
```

Install a skill to your agent:

```bash
gh skill install markoblogo/abvx-agent-skills minimal-diff-builder --agent codex --scope user
```

Then use the skill in conversation:

```text
Use minimal-diff-builder. Implement the smallest correct fix for this issue.
```

## Job-Based Skill Selection

| Job | Skill | When to use |
|---|---|---|
| Write smaller patches | `minimal-diff-builder` | Agent keeps refactoring too much or adding unwanted abstractions |
| Debug from evidence | `diagnose` | Agent guesses fixes without reproducing failures |
| Save tokens | `rtk-assisted-shell`, `shell-output-compaction` | Logs and diffs are burning context |
| Verify frontend | `browser-verification`, `design-critique-polish` | Need real browser behavior checks |

## LoopOps Framework

LoopOps is the framework layer that decides when repeated prompts should remain prompts and when they should become checklists, skills, scripts, or bounded loops. The promotion ladder progresses from:

- Prompt → Checklist
- Checklist → Skill
- Skill → Script
- Script → Bounded Loop

Key LoopOps skills include `loopops-protocol`, `dynamic-workflow-packets`, and `skillopt-evolve-skills`.

## Philosophy

Video context: [I scraped AI skills from GitHub and tested whether they actually help models](https://youtu.be/F73_ofen8rI)

This repository takes a skeptical stance toward many public AI skills, focusing on whether a skill adds usable structure without degrading behavior rather than novelty or popularity.

## Related

- [[skills]] — Agent skills platform and progressive-disclosure model
- [[hermes-agent]] — Compatible agent runtime for skill execution