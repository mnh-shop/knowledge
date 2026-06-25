---
name: agent-skills-catalog
description: "Full catalog of all agent skills grouped by 12 capability domains, covering 66 skills"
tags: [agent-skills, catalog, documentation, skills-platform, acp, ai-llm, automation, docker, git, mcp, optimization, orchestration, plugin-sdk, security, storage, webhook]
---

# Agent Skills Catalog

> Full catalog of all agent skills grouped by capability domain.
> Tags: [agent-skills]

---

## 1. Agent Architecture & Design

Skills for designing, structuring, and maintaining agent harnesses, skill packs, and agent-facing context.

| Skill | Description | Source | Tags |
|---|---|---|---|
| agents-best-practices | Design, audit, or improve agentic systems and agent harnesses. Covers MVP blueprints, tool design, permission models, planning loops, context compaction, memory, skills, connectors, observability, evals, and safety. | abvx-agent-skills | [agent-architecture, harness-design, best-practices] |
| role-skill-pack-design | Design role-specific or workflow-specific agent skill packs. Define base-vs-difference layers, pack boundaries, references, triggers, and rollout order. | abvx-agent-skills | [agent-architecture, skill-design, roles] |
| project-context-bootstrap | Bootstrap usable project context before deep implementation work. Detect stack, summarize understanding, propose compact context artifacts. | abvx-agent-skills | [agent-architecture, context-setup, onboarding] |
| lean-context-layout | Restructure agent-facing docs so always-loaded context stays small and the rest loads on demand. | abvx-agent-skills | [agent-architecture, token-efficiency, docs] |
| durable-context-maintenance | Keep repo-local agent context accurate after code and workflow changes. Refresh durable context, split groups only when needed. | abvx-agent-skills | [agent-architecture, context-maintenance, docs] |
| compaction-survival | Preserve working state across long sessions and context compaction by checkpointing decisions, edited files, blockers, and unresolved errors. | abvx-agent-skills | [agent-architecture, context-management, session-survival] |
| handoff | Create compact handoff documents for another agent, session, or human to continue work. Capture operational state, not transcripts. | abvx-agent-skills | [agent-architecture, handoff, collaboration] |
| workflow-policy-layering | Separate workflow instructions from safety, authority, escalation, and validation rules. | abvx-agent-skills | [agent-architecture, safety, policy] |

---

## 2. Agent Evolution & Skill Creation

Skills for creating, evolving, auditing, and publishing reusable agent skills.

| Skill | Description | Source | Tags |
|---|---|---|---|
| skillopt-evolve-skills | Evolve skills and agent instructions with a SkillOpt-style loop. Define bounded edits, validate against scenarios, maintain rejected-edit buffer. | abvx-agent-skills | [skill-evolution, skill-development, improvement] |
| book-to-skill | Convert books, papers, long documents, or prior reading notes into compact reusable agent skills with frameworks, mental models, checklists. | abvx-agent-skills | [skill-creation, knowledge-extraction, documentation] |
| private-vs-publishable-skill-audit | Audit a private skill, prompt pack, or assistant workflow before publishing it. Mark private vs mixed vs reusable content. | abvx-agent-skills | [skill-audit, publishing, private-to-public] |

---

## 3. Execution & Workflow Orchestration

Skills for planning, organizing, and executing multi-step work with verification gates.

| Skill | Description | Source | Tags |
|---|---|---|---|
| brief-first-execution | Create a single working brief before substantial implementation, audit, or migration work. Reduces drift with scope, non-goals, verification, done criteria. | abvx-agent-skills | [execution, planning, workflow] |
| phase-spec-execution | Execute large tasks through explicit phases with acceptance criteria, required commands, and state updates. Keep phases falsifiable and end-to-end. | abvx-agent-skills | [execution, phasing, verification] |
| dynamic-workflow-packets | Plan and run large tasks with compact dynamic workflow packets, risk gates, integration, and verification. Supports coding, research, job search, audits. | abvx-agent-skills | [workflow, orchestration, packets, risk-gates] |
| loopops-protocol | Design and evolve agent skills into cost-bounded loops, workflows, scripts, and memory updates. Artifact ladder: prompt -> skill -> checklist -> script -> workflow -> loop. | abvx-agent-skills | [workflow, loop-design, automation] |
| test-driven-execution | Execute feature work and bug fixes with a tracer-bullet red-green-refactor loop. Prefer public interfaces, vertical slices, behavior-focused tests. | abvx-agent-skills | [tdd, testing, execution] |
| delivery-preflight-gate | Run a baseline preflight before long implementation or autonomous execution to avoid thrashing against a broken repo state. | abvx-agent-skills | [verification, preflight, quality-gate] |
| delivery-baseline-audit | Audit claimed delivery against the starting baseline and the current working tree. Verify deliverables actually exist. | abvx-agent-skills | [verification, audit, delivery] |

---

## 4. Token & Cost Efficiency

Skills for minimizing token waste in agent sessions through output shaping, context layout, and measurement.

| Skill | Description | Source | Tags |
|---|---|---|---|
| token-efficient-execution | Reduce token waste in long coding-agent sessions by avoiding repeated reads, noisy output, oversized context, broad rewrites. | abvx-agent-skills | [token-efficiency, cost-optimization, execution] |
| token-frugal-mode | Reduce output-token usage without losing technical accuracy. Lite/full/ultra compression modes for agent responses. | abvx-agent-skills | [token-efficiency, compression, cost-optimization] |
| token-usage-audit | Audit where tokens are wasted across startup context, shell output, repeated file reads, bloated agent docs, compaction loss. | abvx-agent-skills | [token-efficiency, audit, optimization] |
| shell-output-compaction | Reduce shell and tool-output token waste by preferring targeted commands, diff-only views, error-first logs, narrow slices. | abvx-agent-skills | [token-efficiency, shell, output-compaction] |
| rtk-assisted-shell | Reduce shell output token waste on git, file reads, searches, test runs, linters, logs by routing through RTK-style filtering. | abvx-agent-skills | [token-efficiency, shell, rtk] |

---

## 5. Code Quality & Architecture Review

Skills for reviewing, simplifying, and improving code structure, complexity, and maintainability.

| Skill | Description | Source | Tags |
|---|---|---|---|
| architecture-deepening-review | Review codebase for architecture deepening opportunities: shallow modules, weak seams, scattered domain logic, low testability, high coupling. | abvx-agent-skills | [code-review, architecture, refactoring] |
| complexity-optimizer | Analyze or improve codebase complexity and performance hotspots without broad rewrites. Report, implement, or audit modes. | abvx-agent-skills | [complexity, performance, optimization] |
| overengineering-review | Review code or diffs for needless complexity, replaceable dependencies, dead flexibility, wrappers over stdlib. | abvx-agent-skills | [code-review, simplification, overengineering] |
| minimal-diff-builder | Build the smallest correct code diff without overengineering, broad refactors, unnecessary dependencies, or speculative abstractions. | abvx-agent-skills | [code-quality, minimal-diff, stdlib-first] |
| system-zoom-out | Go up one layer of abstraction and explain how local code fits into the larger system. Modules, entrypoints, dependencies, domain language. | abvx-agent-skills | [architecture, code-reading, onboarding] |

---

## 6. Debugging & Diagnosis

Skills for disciplined debugging with hypothesis ledgers, reproduction loops, and bounded retry strategies.

| Skill | Description | Source | Tags |
|---|---|---|---|
| diagnose | Debug coding failures through reproduction, ranked hypotheses, narrow fixes, and verification. Build smallest useful pass/fail signal first. | abvx-agent-skills | [debugging, diagnosis, hypothesis-testing] |
| repo-debugging-ledger | Debug repositories with a hypothesis ledger, checked locations, and loop-breaking discipline. Prevent circular hypotheses and unverified fixes. | abvx-agent-skills | [debugging, hypothesis-ledger, forensics] |
| recovery-loop-3strike | Recover from failed execution with a bounded three-step loop: retry, focused fix-spec, then honest handoff. | abvx-agent-skills | [debugging, recovery, retry-strategy] |
| repo-issue-triage | Triage bugs, enhancements, and backlog items through a small state machine. Works with or without a formal issue tracker. | abvx-agent-skills | [triage, issue-management, backlog] |

---

## 7. Product & Planning

Skills for turning ideas into product requirements, issue breakdowns, and grounded plans.

| Skill | Description | Source | Tags |
|---|---|---|---|
| spec-to-prd | Turn the current conversation, repo understanding, and clarified decisions into a PRD. Prefer repo/domain language, explicit scope, implementation decisions. | abvx-agent-skills | [product, prd, specification] |
| plan-to-issues | Break a PRD, plan, or spec into independently executable vertical slices. Prefer thin end-to-end slices, explicit blockers, neutral output. | abvx-agent-skills | [product, planning, issues, breakdown] |
| doc-grounded-grilling | Stress-test a plan, feature, or design against the repo's existing docs, domain language, ADRs, and context files. | abvx-agent-skills | [planning, validation, domain-language] |
| rapid-grilling | Lightweight grilling session for brainstorming, product clarification, and early design shaping. Ask one question at a time, recommend answers. | abvx-agent-skills | [planning, brainstorming, product-discovery] |

---

## 8. UI/UX & Frontend Development

Skills for frontend design, implementation, critique, brand kits, animations, and visual artifacts.

| Skill | Description | Source | Tags |
|---|---|---|---|
| design-register-bootstrap | Establish frontend design context before implementation. Classify surface as brand or product before styling. | abvx-agent-skills | [design, ui, frontend, brand] |
| designmd-brand-kit | Create, inspect, and apply DESIGN.md brand kits for brand-aware frontend work. Extract tokens from URLs, screenshots, or CSS. | abvx-agent-skills | [design, brand-kit, design-tokens, frontend] |
| design-critique-polish | Critique and polish frontend interfaces before shipping. Hierarchy, typography, spacing, states, color, UX clarity. | abvx-agent-skills | [design, ui-review, critique, polish] |
| frontend-product-builder | Build or improve frontend pages with strong hierarchy, responsive layout, real visual assets, ergonomic controls. | abvx-agent-skills | [frontend, ui-development, product-ui] |
| frontend-taste-layer | Add a stronger anti-slop taste layer to frontend work. Avoid generic templates, weak typography, and uncommitted visuals. | abvx-agent-skills | [design, ui, taste, frontend] |
| browser-verification | Verify frontend changes in a real browser: layout, console errors, responsive states, screenshots, interactions. | abvx-agent-skills | [testing, browser, verification, frontend] |
| lottie-motion-builder | Build or refine small production-ready Lottie animations from SVGs, logos, UI states, loaders, and branded motion assets. | abvx-agent-skills | [animation, lottie, motion, frontend] |
| html-brief-artifact | Create a self-contained HTML brief for plans, status updates, PR summaries, incident notes, research explainers. | abvx-agent-skills | [documentation, html, artifact, communication] |
| html-diagram-artifact | Create a self-contained HTML artifact for architecture, stack, and system-flow explanation using SVG-first diagrams. | abvx-agent-skills | [documentation, html, diagram, architecture] |
| web-quality-audit | Audit and improve web quality across accessibility, performance, UX, privacy, and browser security. | abvx-agent-skills | [audit, accessibility, performance, security, privacy] |

---

## 9. Research & Code Reading

Skills for evidence-based research and efficient code navigation.

| Skill | Description | Source | Tags |
|---|---|---|---|
| evidence-ledger-research | Research and answer evidence-sensitive questions with source, date, unit, and operand discipline. Maintain evidence ledger for multi-step answers. | abvx-agent-skills | [research, evidence, fact-checking, analysis] |
| graph-guided-code-reading | Reduce repository-reading token waste by navigating code through symbols, entrypoints, dependencies, changed files, and blast radius. | abvx-agent-skills | [code-reading, navigation, efficiency] |

---

## 10. Utilities & Specialized Tools

| Skill | Description | Source | Tags |
|---|---|---|---|
| spreadsheet-workbook-forensics | Edit, repair, or generate spreadsheet workbooks with structure-preserving Python (openpyxl). Formulas, lookup tables, formatting preservation. | abvx-agent-skills | [spreadsheets, excel, openpyxl, data] |
| prototype-lab | Build throwaway prototypes to answer a specific product, UI, state-machine, data-model, or workflow question before committing production code. | abvx-agent-skills | [prototyping, experimentation, mvp] |

---

## 11. n8n Workflow Automation

Skills for building, configuring, validating, and deploying n8n automation workflows via the n8n-mcp server.

| Skill | Description | Source | Tags |
|---|---|---|---|
| using-n8n-mcp-skills | Entry-point skill for the n8n-mcp-skills pack. Routes to the right specialist skill for building, editing, validating, testing, or debugging n8n workflows. | n8n-skills | [n8n, automation, workflow, mcp] |
| n8n-agents | Design n8n AI agents the right way. Covers AI Agent vs chain vs classifier, model/memory/tools slots, structured output, RAG, human review, chat topologies. | n8n-skills | [n8n, agents, ai, langchain] |
| n8n-binary-and-data | Handle files and binary data in n8n correctly. Covers $binary vs $json, reading/writing binary, Merge node, CDN/URL for chat surfaces. | n8n-skills | [n8n, binary-data, files, data-handling] |
| n8n-code-javascript | Write JavaScript code in n8n Code nodes. Covers $input/$json/$node, $helpers, DateTime, SplitInBatches, pairedItem, production patterns. | n8n-skills | [n8n, javascript, code-node, data-transformation] |
| n8n-code-python | Write Python code in n8n Code nodes. Covers _input/_json/_node syntax, standard library, Python limitations in n8n. | n8n-skills | [n8n, python, code-node] |
| n8n-code-tool | Write JavaScript or Python for the n8n Custom Code Tool (AI-agent-callable tool). Covers query input schema, string return, differences from Code node. | n8n-skills | [n8n, code-tool, ai-agent, custom-tool] |
| n8n-error-handling | Wire n8n error handling so failures are loud, structured, and recoverable. Covers error outputs, retries, Error Trigger, 4xx/5xx response shapes. | n8n-skills | [n8n, error-handling, reliability] |
| n8n-expression-syntax | Validate n8n expression syntax and fix common errors. Covers {{}} syntax, $json/$node variables, mapping data between nodes. | n8n-skills | [n8n, expressions, syntax, data-mapping] |
| n8n-mcp-tools-expert | Expert guide for using n8n-mcp MCP tools effectively. Tool selection guidance, parameter formats, common patterns, nodeType formats. | n8n-skills | [n8n, mcp, tools, expert-guide] |
| n8n-multi-instance | Use when n8n-mcp targets more than one n8n instance. Covers choosing/switching instances, verifying targets, recovering from misroutes. | n8n-skills | [n8n, multi-instance, environments] |
| n8n-node-configuration | Operation-aware node configuration guidance. Covers required fields, displayOptions, patch vs full update. | n8n-skills | [n8n, node-configuration, parameters] |
| n8n-self-hosting | Deploy production self-hosted n8n via Docker Compose behind Caddy reverse proxy with HTTPS. Single mode or queue mode with workers. | n8n-skills | [n8n, self-hosting, deployment, docker] |
| n8n-subworkflows | Build reusable, composable n8n sub-workflows. Covers typed inputs, all-vs-each execution, verb-first naming, stateless vs stateful design. | n8n-skills | [n8n, subworkflows, reusability, modularity] |
| n8n-validation-expert | Interpret n8n validation errors and guide fixing them. Knows false positives and real fixes for validate_node/validate_workflow errors. | n8n-skills | [n8n, validation, error-interpretation] |
| n8n-workflow-patterns | Proven workflow architectural patterns: webhook, API, database, AI agent, batch processing, scheduled automation. Speed optimization guidance. | n8n-skills | [n8n, workflow-patterns, architecture, optimization] |

---

## 12. Agent Communication Protocol (ACP)

Skills for ACP-style agent delegation and orchestration.

| Skill | Description | Source | Tags |
|---|---|---|---|
| hermes-acp-orchestrator | ACP-style delegation in Hermes with explicit agent routing to hermes, codex, or claude-code. Includes safe output limits, timeout-aware execution, parallel batch delegation. | hermes-agent-acp-skill | [acp, delegation, orchestration, hermes] |

---

## Quick Reference: Source Repositories

| Source | Location | Count |
|---|---|---|
| abvx-agent-skills | `/Users/admin1/Documents/knowledge/sources/abvx-agent-skills/skills/` | 50 skills |
| n8n-skills | `/Users/admin1/Documents/knowledge/sources/n8n-skills/skills/` | 15 skills |
| hermes-agent-acp-skill | `/Users/admin1/Documents/knowledge/sources/hermes-agent-acp-skill/SKILL.md` | 1 skill |
| **Total** | | **66 skills** |

---

## Domain Summary

| Capability Domain | Skill Count | Key Repositories |
|---|---|---|
| Agent Architecture & Design | 8 | abvx-agent-skills |
| Agent Evolution & Skill Creation | 3 | abvx-agent-skills |
| Execution & Workflow Orchestration | 7 | abvx-agent-skills |
| Token & Cost Efficiency | 5 | abvx-agent-skills |
| Code Quality & Architecture Review | 5 | abvx-agent-skills |
| Debugging & Diagnosis | 4 | abvx-agent-skills |
| Product & Planning | 4 | abvx-agent-skills |
| UI/UX & Frontend Development | 10 | abvx-agent-skills |
| Research & Code Reading | 2 | abvx-agent-skills |
| Utilities & Specialized Tools | 2 | abvx-agent-skills |
| n8n Workflow Automation | 15 | n8n-skills |
| Agent Communication Protocol | 1 | hermes-agent-acp-skill |
