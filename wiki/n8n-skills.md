---
title: n8n-Skills
description: Claude Code skills for building flawless n8n workflows using the n8n-mcp MCP server
date: 2026-06-25
type: skills
status: active
---

# n8n-Skills

## Overview

`n8n-skills` is a comprehensive collection of **14 complementary Claude Code skills** designed to teach AI assistants how to build production-ready n8n workflows using the [n8n-mcp](https://github.com/czlonkowski/n8n-mcp) MCP server. These skills provide expert guidance on using n8n-mcp tools effectively for workflow automation, from expression syntax to advanced AI agent configuration.

## What Makes This Special?

✅ **14 Specialized Skills** - From basic expression syntax to advanced self-hosting deployment
✅ **Always-On Enforcement** - Router skill and hooks layer surfaces guidance at decision moments
✅ **Production-Ready Patterns** - 10+ production-tested Code node patterns, 2,653+ workflow templates for examples
✅ **Error-Proof Development** - Comprehensive error catalogs, validation guides, and troubleshooting assistance

## The 14 Skills

1. **n8n Expression Syntax** - Correct n8n expression patterns and common gotchas
2. **n8n MCP Tools Expert** - Expert guide for using n8n-mcp tools effectively
3. **n8n Workflow Patterns** - 5 proven architectural patterns from real-world usage
4. **n8n Validation Expert** - Interpret validation errors and guide fixing
5. **n8n Node Configuration** - Operation-aware node configuration guidance
6. **n8n Code JavaScript** - Write effective JavaScript in n8n Code nodes
7. **n8n Code Python** - Python code for n8n Code nodes with limitations awareness
8. **n8n Code Tool** - AI-agent-callable Custom Code Tool development
9. **n8n Error Handling** - Make failures structured and recoverable
10. **n8n Binary & Data** - Handle files, images, and binary data correctly
11. **n8n Sub-workflows** - Build reusable, composable sub-workflows
12. **n8n AI Agents** - Design n8n AI agents the right way
13. **n8n Multi-Instance** - Target the right n8n instance when multiple are available
14. **n8n Self-Hosting** - Deploy production self-hosted n8n to Linux VMs

## Key Features

- **5,700+ Support Statistics** - 525+ n8n nodes supported, 5,700+ nodes discovered across 2,653+ workflow templates
- **Cross-Skill Integration** - Skills work together seamlessly for comprehensive workflow building
- **Proactive Guidance** - Always-on router and PreToolUse/PostToolUse hooks provide real-time assistance
- **Production Hardening** - Secure defaults, secret-free templates, and comprehensive deployment guidance
- **Evaluation-First** - Each skill includes 3+ evaluations for quality assurance

## Usage Examples

```text
"How do I write n8n expressions?"
→ Activates: n8n Expression Syntax

"Find me a Slack node"
→ Activates: n8n MCP Tools Expert

"Build a webhook workflow"
→ Activates: n8n Workflow Patterns

"Why is validation failing?"
→ Activates: n8n Validation Expert
```

## Skills Integration Workflow

When you ask: **"Build and validate a webhook to Slack workflow"**

1. **n8n Workflow Patterns** - Identifies webhook processing pattern
2. **n8n MCP Tools Expert** - Searches for webhook and Slack nodes
3. **n8n Node Configuration** - Guides node setup
4. **n8n Code JavaScript** - Helps process webhook data
5. **n8n Expression Syntax** - Assists with data mapping
6. **n8n Validation Expert** - Validates the final workflow

## Repository Structure

```
n8n-skills/
├── skills/                    # 14 individual skill implementations
├── hooks/                     # Enforcement layer: hooks.json + SessionStart/PreToolUse/PostToolUse
├── evaluations/               # Test scenarios for each skill (3+ per skill)
├── docs/                      # Installation, Usage, Development guides
└── dist/                      # Distribution packages
```

## Installation & Setup

### Claude Code (Recommended)
```bash
/plugin install czlonkowski/n8n-skills
```

### Claude.ai
1. Download individual skill folders from `skills/`
2. Zip each skill folder
3. Upload via Settings → Capabilities → Skills

## Important Notes

- This repository is part of the **n8n-mcp project**
- Triggers on its own description - not part of workflow-building router/hooks flow
- Hooks run only in Claude Code / Codex plugin install (not Claude.ai)
- MIT License - see LICENSE file for details

## Best Practices

- Use **skills progressively** - start with expression syntax, then MCP tools, then patterns
- **Cross-skill integration** is designed for comprehensive workflow building
- Leverage **Proactive Guidance** - skills surface at decision moments, not just on query
- **Test thoroughly** - each skill includes 3+ evaluations for quality assurance

## Getting Started

1. Install the plugin via Claude Code
2. Configure your n8n-mcp MCP server
3. Start building workflows! Skills will activate automatically when relevant

**Ready to build flawless n8n workflows? Get started now! 🚀**