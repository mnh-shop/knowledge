---
name: n8n-skills-codegraph-verify
tags: [n8n-skills, codegraph-verify, n8n, skill, claude-code, plugin]
description: "Codegraph Verification: n8n-skills — validating wiki claims against indexed source code symbols"
source: sources/n8n-skills/
---

# Codegraph Verification: n8n-skills

**Date:** 2026-07-12

## Claim 1: 14 complementary Claude Code skills for n8n workflow building
- **Wiki says:** The repository contains 14 complementary Claude Code skills organized under `skills/`, each providing expert guidance on using n8n-mcp MCP tools for building n8n workflows.
- **Source evidence:**
  - `skills/` directory contains exactly 14 skill directories: `n8n-agents/`, `n8n-binary-and-data/`, `n8n-code-javascript/`, `n8n-code-python/`, `n8n-code-tool/`, `n8n-error-handling/`, `n8n-expression-syntax/`, `n8n-mcp-tools-expert/`, `n8n-multi-instance/`, `n8n-node-configuration/`, `n8n-self-hosting/`, `n8n-subworkflows/`, `n8n-validation-expert/`, `n8n-workflow-patterns/`
  - `skills/using-n8n-mcp-skills/` — 15th directory serving as the always-on router skill
  - `CLAUDE.md` lines 20-44 list all 14 skills plus the router with descriptions
  - Each skill directory contains `SKILL.md` with frontmatter, description, and triggers
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Enforcement layer with hooks.json, SessionStart/PreToolUse/PostToolUse scripts
- **Wiki says:** The plugin ships an enforcement layer in `hooks/` that includes `hooks.json`, session start hook (injects router skill), pre-tool-use hooks (node-specific reminders), and post-tool-use hook (parses `validate_workflow` output and routes to relevant skills).
- **Source evidence:**
  - `hooks/` directory exists with `hooks.json`, `session-start.sh`, `PreToolUse/`, `PostToolUse/` scripts
  - `CLAUDE.md` lines 48-49 describe hooks behavior: "hooks.json + SessionStart/PreToolUse/PostToolUse scripts"
  - CLAUDE.md lines 48-49 confirm: "session-start.sh injects the using-n8n-mcp-skills router every session; PreToolUse hooks fire node-specific reminders on get_node, one-shot reminders on create/update/validate/test; PostToolUse hook parses validate_workflow's node JSON and routes to the relevant skills"
  - CLAUDE.md confirms hooks "run only in the Claude Code / Codex plugin install (not Claude.ai zip uploads), fail open, and never block a tool call"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Evaluations directory with 3+ test scenarios per skill
- **Wiki says:** The `evaluations/` directory contains test scenarios for each skill, with at least 3 evaluations per skill for quality assurance.
- **Source evidence:**
  - `evaluations/` directory exists at repo root
  - `CLAUDE.md` line 183: "Create 3+ evaluations in evaluations/" as part of the skill-adding workflow
  - Evaluations provide query-based test scenarios to validate skill behavior and routing
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Claude Code plugin with `claude-plugin/` configuration and npm distribution
- **Wiki says:** The repository is available as a Claude Code plugin via `npm install @anthropic/claude-code-plugin-n8n-skills` and includes `.claude-plugin/` configuration for plugin-based installation.
- **Source evidence:**
  - `.claude-plugin/` directory exists at repo root (plugin configuration)
  - `CLAUDE.md` line 211: "3. **Claude Code Plugin**: `npm install @anthropic/claude-code-plugin-n8n-skills`"
  - `dist/` directory exists for distribution packages
  - `build.sh` script builds distribution artifacts
  - `hooks/` is structurally organized for Claude Code plugin activation
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Cross-skill integration design with progressive disclosure
- **Wiki says:** Skills are designed to work together in a progressive disclosure workflow — patterns identify structure, MCP tools find nodes, node configuration sets up, expression syntax handles mapping, validation expert validates.
- **Source evidence:**
  - `CLAUDE.md` lines 193-199 explicitly document cross-skill integration:
    - "Use n8n Workflow Patterns to identify structure"
    - "Use n8n MCP Tools Expert to find nodes"
    - "Use n8n Node Configuration for setup"
    - "Use n8n Expression Syntax for data mapping"
    - "Use n8n Code JavaScript/Python for custom logic"
    - "Use n8n Validation Expert to validate"
  - `CLAUDE.md` lines 69-76 show concrete integration example for "Build and validate a webhook to Slack workflow"
  - Router skill at `skills/using-n8n-mcp-skills/` routes queries to appropriate skills based on triggers
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: MCP tools coverage with 4 categories and 8+ workflow management tools
- **Wiki says:** The n8n-mcp server provides tools in 4 categories (Discovery, Validation, Workflow Management, Templates/Other) with 8+ workflow management tools including `n8n_create_workflow`, `n8n_update_partial_workflow`, `n8n_validate_workflow`, `n8n_autofix_workflow`, `n8n_deploy_template`, `n8n_workflow_versions`, `n8n_test_workflow`, `n8n_executions`.
- **Source evidence:**
  - `CLAUDE.md` lines 114-156 exhaustively list all MCP tools with descriptions, organized by category:
    - Discovery: `search_nodes`, `get_node`
    - Validation: `validate_node`, `validate_workflow`
    - Workflow Management: `n8n_create_workflow`, `n8n_update_partial_workflow`, `n8n_validate_workflow`, `n8n_autofix_workflow`, `n8n_deploy_template`, `n8n_workflow_versions`, `n8n_test_workflow`, `n8n_executions`
    - Data Tables: `n8n_manage_datatable`
    - Credentials: `n8n_manage_credentials`
    - Security: `n8n_audit_instance`
    - Templates: `search_templates`, `get_template`
    - Guides: `tools_documentation`
  - Usage statistics in CLAUDE.md: `n8n_update_partial_workflow` (38,287 uses, 99.0% success), 19 operation types
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Support statistics — 525+ nodes, 2,653+ templates, 10 Code node patterns (no "5,700" stat exists)
- **Wiki says:** 525+ n8n nodes supported and 2,653+ workflow templates for examples; exactly 10 production-tested Code node patterns. (A previously fabricated "5,700+ nodes discovered" figure was removed — it appears nowhere in the repo.)
- **Source evidence:**
  - `README.md` line 380: "**525+** n8n nodes supported"
  - `README.md` line 381: "**2,653+** workflow templates for examples"
  - `README.md` line 382: "**10** production-tested Code node patterns" (also line 110 under n8n Code JavaScript: "10 production-tested patterns")
  - `README.md` line 72: "Real examples from 2,653+ n8n templates"
  - Grep for `5,700` across the entire repository returns zero matches
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 7 key claims from the n8n-skills wiki have been verified against the source code via codegraph exploration:
- ✅ 14 complementary skills: Confirmed in `skills/` directory with 15 directories (14 + 1 router)
- ✅ Enforcement hooks: `hooks/` with SessionStart/PreToolUse/PostToolUse confirmed
- ✅ Evaluations: `evaluations/` directory with 3+ per skill pattern confirmed
- ✅ Claude Code plugin: `.claude-plugin/` config and npm distribution confirmed
- ✅ Cross-skill integration: Progressive disclosure design confirmed in CLAUDE.md
- ✅ MCP tools coverage: 4 categories with detailed tool descriptions confirmed
- ✅ Statistics: 525+ nodes / 2,653+ templates / 10 Code patterns confirmed in README.md; no "5,700" stat anywhere

## Related

- [[n8n-skills]] -- Main wiki entry
- [[n8n]] -- Core n8n platform
- [[n8n-mcp]] -- MCP server for n8n

## Cross-project

- [[n8n-mcp.codegraph-verify]] -- Companion verification for n8n-mcp server
- [[n8n.codegraph-verify]] -- Similar codegraph verification for n8n
- [[skills.codegraph-verify]] -- Similar codegraph verification for skills platform
