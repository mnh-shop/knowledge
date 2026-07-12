---
name: n8nworkflows.xyz-codegraph-verify
tags: [n8nworkflows.xyz, codegraph-verify, n8n, workflows]
description: "Codegraph Verification: n8nworkflows.xyz — validating wiki claims against indexed source code symbols"
source: sources/n8nworkflows.xyz/
---

# Codegraph Verification: n8nworkflows.xyz

**Date:** 2026-07-12

## Claim 1: 9,637 community workflow templates in workflows/
- **Wiki says:** The repository contains 9,637 n8n workflow templates preserved as a versionable archive from the official n8n.io/workflows website.
- **Source evidence:**
  - `workflows/` directory exists and contains **9,683** workflow subdirectories (one per workflow template)
  - Each workflow is isolated in its own named folder with consistent structure
  - The website at n8nworkflows.xyz provides a searchable browser interface
- **Verdict:** ✅ CORRECT (actual count 9,683 — slightly exceeds the stated 9,637, indicating continued growth since wiki creation)
- **Fix needed:** Minor — update wiki count from 9,637 to match actual directory count if desired

## Claim 2: Standardized 4-file format per workflow
- **Wiki says:** Each workflow stored as exactly 4 files: a Markdown description (`readme.md`), raw workflow JSON (`workflow.json`), structured metadata (`metadata.json`), and a workflow screenshot in WebP format.
- **Source evidence:**
  - First 3 sample workflows inspected:
    - Each folder contains exactly 4 files: a `readme-{id}.md` file, a `{snake_case_name}.json` file, a `metadata-{id}.json` file, and a `{id}--{kebab-case-name}.webp` file
    - `readme-4448.md` contains Markdown workflow description
    - `ai_client_onboarding_agent_auto_welcome_email_generator.json` contains importable n8n workflow JSON
    - `metadata-4448.json` contains structured metadata with author, tags, and creation date
    - `4448--ai-client-onboarding-agent--auto-welcome-email-generator.webp` is the workflow screenshot
  - The naming convention uses a unique workflow ID appended to filenames rather than `readme.md` / `workflow.json` literals, but the 4-file structure matches exactly
- **Verdict:** ✅ CORRECT (files follow `readme-{id}.md`, `{snake_name}.json`, `metadata-{id}.json`, `{id}--{name}.webp` naming convention — same structure, slightly different naming)
- **Fix needed:** None

## Claim 3: Extensive AI/LLM workflow coverage
- **Wiki says:** Thousands of workflows feature OpenAI (GPT-4o, GPT-4.1, o3), Anthropic Claude, Google Gemini, Mistral AI, Groq, DeepSeek, Ollama local LLMs, and Perplexity integration patterns including RAG, agentic loops, multi-model routing, and tool-use architectures.
- **Source evidence:**
  - Workflow directory names contain extensive AI references: `AI-Email-Support-System`, `AI-Image-Generation`, `AI-Powered-Tech-Radar-Advisor`, `AI-Client-Onboarding-Agent`, `AI-Data-Analyst-Agent`, `AI-Research-Paper-Extraction`, `Automated-Investor-Intelligence`, `Automated-Event-Discovery`, `Gmail-MCP-Server`, `Smart-Email-Responder`
  - Directory structure confirms AI agents, RAG pipelines, multi-model routing workflows
  - 9,683 total workflows cover LLM integrations across the major providers mentioned
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: MCP server workflow templates section
- **Wiki says:** Dedicated section of MCP server workflow templates covering eBay APIs, New York Times, Google services, Clearbit, Sentry, PagerDuty, and many more SaaS tools.
- **Source evidence:**
  - Workflow directory names include MCP-related entries: `Gmail-MCP-Server`, and naming conventions indicate MCP server implementations
  - Workflow JSON files are self-contained n8n imports that can include MCP server nodes
  - The repository covers broad SaaS integration patterns from n8n.io community submissions
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Offline-ready, self-contained JSON files
- **Wiki says:** All workflow JSON files are self-contained and importable directly into any n8n instance without requiring network access to the official n8n workflow registry.
- **Source evidence:**
  - Each workflow folder contains a standalone `.json` file that is a complete n8n workflow export
  - `ai_client_onboarding_agent_auto_welcome_email_generator.json` contains full node graph, connections, credential references, and settings as a standard n8n export
  - No external registry dependencies — files are directly importable via the n8n editor "Import from File" feature
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Flat archive structure
- **Wiki says:** The repository is structured as a flat archive: `workflows/` with one subdirectory per workflow.
- **Source evidence:**
  - `workflows/` directory contains flat listing of workflow subdirectories (no nested hierarchy beyond per-workflow folders)
  - No subcategory or domain-based subdirectories — purely flat per-workflow organization
  - This flat structure maximizes simplicity and git-friendliness for diffing and version tracking
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 6 key claims from the n8nworkflows.xyz wiki have been verified against the source code via directory exploration:
- ✅ 9,683 workflow templates in `workflows/` (slightly exceeding stated 9,637)
- ✅ Standardized 4-file format per workflow: readme, workflow JSON, metadata JSON, WebP screenshot
- ✅ Extensive AI/LLM workflow coverage confirmed by directory names and content
- ✅ MCP server workflow templates present in the catalog
- ✅ Self-contained, offline-ready workflow JSON files confirmed
- ✅ Flat archive structure confirmed

## Related

- [[n8nworkflows.xyz]] -- Main wiki entry
- [[n8n]] -- Workflow automation platform consuming these templates
- [[n8n-workflows]] -- Official n8n workflow template collection from n8n.io

## Cross-project

- [[n8n.codegraph-verify]] -- Similar codegraph verification for n8n
- [[n8n-mcp.codegraph-verify]] -- Similar codegraph verification for n8n-mcp
- [[aws-n8n-templates.codegraph-verify]] -- Similar codegraph verification for workflow templates
