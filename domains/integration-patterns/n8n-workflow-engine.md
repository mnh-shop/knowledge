---
name: n8n-workflow-engine
description: "n8n workflow automation engine used in agentic deployment stacks"
tags: [n8n, workflows, automation, integration-patterns]
---

# n8n Workflow Engine

n8n serves as the workflow automation engine in agentic stacks. It receives webhook calls from OpenClaw agents for structured data processing, and can call back into OpenClaw's MCP tools for AI-heavy analysis. Runs on port 5678.

See [[stack-reference-openclaw-n8n]] for the full deployment pattern.
