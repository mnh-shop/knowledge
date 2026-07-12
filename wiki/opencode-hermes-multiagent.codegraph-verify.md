---
title: opencode-hermes-multiagent.codegraph-verify
date: 2026-07-12
tags: [opencode-hermes-multiagent, codegraph-verify, opencode, hermes-agent]
related: [[opencode-hermes-multiagent]], [[opencode]], [[hermes-agent]], [[oh-my-hermes]]
source: sources/opencode-hermes-multiagent/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# opencode-hermes-multiagent — CodeGraph Verification

## Claim-1: 17 specialized agents coordinated by a master orchestrator

The system defines 17 AI agents in a strict pipeline architecture. The master orchestrator (Hermes, model `openai/gpt-5.2-high`) routes requests, manages pipelines, and coordinates agents across six domains: research (3 agents), planning (2), implementation (4), quality (4), documentation (2), and infrastructure (2).

**Source evidence:** `README.md` lines 18-22 ("Hermes is a sophisticated multi-agent orchestration system designed for OpenCode AI. It coordinates 17 specialized AI agents"), lines 59-110 (agent tables listing all 17 agents with models and roles), and lines 26-55 (architecture diagram showing the master orchestrator delegating to six domains). The `opencode.json` file lines 3-22 define the hermes agent with `mode: "primary"` and all subagents declared with `mode: "subagent"`.

## Claim-2: Strict pipeline architecture with mandatory quality gates

Every pipeline enforces mandatory quality gates: `@reviewer` and `@tester` run after every code change. For security-related work, `@security` is mandatory. Seven named pipelines are documented: New Feature, New Feature (Security-Related), Bug Fix (Unknown Cause), Bug Fix (Known Cause), Refactoring, Performance Optimization, and Infrastructure Changes.

**Source evidence:** `README.md` lines 113-146 (seven pipeline definitions showing ordered agent sequences), lines 150-151 ("Mandatory Quality Gates: @reviewer and @tester run after every code change", "Security First: @security is mandatory for auth, user data, secrets").

## Claim-3: OpenCode platform plugin with configurable model routing

The system is an OpenCode AI plugin that uses `opencode.json` for configuration. Each agent is assigned a specific model with reasoning levels (low/medium/high/xhigh). The config includes multiple provider definitions (openai, google) with model capability mappings including context limits, output limits, and modality support.

**Source evidence:** `opencode.json` lines 1-2 (`$schema` reference to opencode.ai), lines 25-39 (finder agent with `google/gemini-3-flash`, tools restricted to `read/list/glob/grep`), lines 78-94 (architect with `gemini-claude-opus-4-5-thinking-medium`), lines 340-525 (provider model definitions for OpenAI GPT-5.2 variants and Google Gemini variants). `package.json` line 9 confirms `@opencode-ai/plugin: "1.0.218"` dependency.

## Claim-4: Agent tools are role-scoped per pipeline stage

Each agent has a carefully scoped toolset matching its role. The master orchestrator only has `task`, `todowrite`, `todoread` tools with all file/read/write/edit tools disabled. Research agents have `read/list/glob/grep` but no `write` tools. Implementation agents have full tool access including `bash/read/write/edit`. Quality agents (reviewer, security) are read-only with no `write` or `bash` access.

**Source evidence:** `opencode.json` lines 5-22 (hermes tools: only `task/todowrite/todoread`), lines 23-39 (finder: `read/list/glob/grep`, no write), lines 114-131 (coder: full `bash/read/write/edit/list/glob/grep/lsp`), lines 190-207 (reviewer: `read/list/glob/grep/lsp/todoread`, no write/bash), lines 247-264 (security: same read-only restriction as reviewer).

## Claim-5: Revision loops and conflict resolution with checkpoints

The system includes user confirmation checkpoints between phases, up to 3 revision iterations before escalation, full context passing between all agents, and priority-based conflict resolution (security > quality > implementation).

**Source evidence:** `README.md` lines 152-156 ("Checkpoints: User confirmation required between phases", "Revision Loops: Up to 3 iterations for fixes before escalation", "Context Passing: Full context flows between all agents", "Conflict Resolution: Priority-based resolution (security > quality > implementation)"). Lines 57-86 of the Russian section duplicate and confirm these features.

## Claim-6: Dual-language documentation (English/Russian) with mirror content

The README provides complete bilingual documentation with English and Russian sections containing mirrored content including architecture diagrams, agent tables, pipeline definitions, and installation instructions.

**Source evidence:** `README.md` line 5 (`**[English](#english) | [Русский](#russian)**`), lines 15-249 (English section), lines 251-483 (Russian section with identical structure). The Russian section lines 384-392 mirror the key features exactly including "Обязательные Проверки Качества" and "Безопасность Прежде Всего".

## Claim-7: Projects as template/inspiration for experimental agent orchestration

The repository is structured as a template or reference for multi-agent orchestration patterns. It includes MCP server configuration for `@researcher` (Context7 for library documentation, fetch for web pages). Files are organized as markdown agent definition files in a hierarchical directory structure ready for `cp -r agent ~/.config/opencode/`.

**Source evidence:** `README.md` lines 160-186 (installation instructions: `cp -r agent ~/.config/opencode/`, MCP server setup with `npx -y @upstash/context7-mcp`), lines 220-247 (project structure showing `agent/core/hermes.md` and hierarchical subagent directories). `opencode.json` lines 341-344 show plugin configuration for authentication providers.
