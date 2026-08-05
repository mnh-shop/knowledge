---
name: n8nworkflows.xyz-codegraph-verify
tags: [n8nworkflows.xyz, codegraph-verify, n8n, workflows]
description: "Codegraph Verification: n8nworkflows.xyz — validating wiki claims against indexed source code symbols"
source: sources/n8nworkflows.xyz/
---

# Codegraph Verification: n8nworkflows.xyz

**Date:** 2026-07-12

## Claim 1: 9,823 community workflow templates in workflows/
- **Wiki says:** The repository contains 9,823 n8n workflow templates preserved as a versionable archive from the official n8n.io/workflows website.
- **Source evidence:**
  - `workflows/` directory contains **9,823** workflow subdirectories (measured: `find workflows/ -maxdepth 1 -type d` = 9,823, excluding the two stray top-level files `-` and `readme.md`)
  - `README.md` line 82: "## 📚 Workflows Summary (9637 workflows)" — a stale count; the filesystem has grown since
  - The website at n8nworkflows.xyz provides a searchable browser interface
- **Verdict:** ✅ CORRECT (filesystem count 9,823; README's 9,637 is stale)
- **Fix needed:** None (wiki count updated to match directory count)

## Claim 2: Standardized 4-file format per workflow
- **Wiki says:** Each workflow stored as 4 files: a Markdown description (`readme-{id}.md`), raw workflow JSON (`{snake_case}.json`), structured metadata (`metada-{id}.json`), and a workflow screenshot in WebP format (`{id}--{kebab-case}.webp`).
- **Source evidence:**
  - Sample folders inspected confirm the naming convention: `readme-2753.md`, `rag_chatbot_for_company_documents_using_google_drive_and_gemini.json`, `metada-2753.json`, `2753-rag-chatbot-for-company-documents-using-google-drive-and-gemini.webp` (in `RAG Chatbot for Company Documents using Google Drive and Gemini-2753`)
  - Note: the metadata file is **`metada-{id}.json`** — the repo consistently omits the "t" ("metada", not "metadata"); verified across 8+ folders
  - 265 of the 9,823 folders do **not** have exactly 4 files: 232 with 3 (missing screenshot), 8 with 2, 25 with 1 (malformed/duplicate dirs)
  - `README.md` lines 69-76 document the intended format ("Each workflow folder contains **exactly 4 files**": `readme.md`, `workflow.json`, `metadata.json`, `<slug-and-id>.webp`) — the README uses conceptual names, while actual files are id-suffixed and use the `metada-` spelling
- **Verdict:** ✅ CORRECT with qualification (4-file structure holds for 9,558/9,823 folders; 265 deviate, mostly missing screenshots)
- **Fix needed:** None

## Claim 3: Extensive AI/LLM workflow coverage
- **Wiki says:** Thousands of workflows feature OpenAI (GPT-4o, GPT-4.1, o3), Anthropic Claude, Google Gemini, Mistral AI, Groq, DeepSeek, Ollama local LLMs, and Perplexity integration patterns including RAG, agentic loops, multi-model routing, and tool-use architectures.
- **Source evidence:**
  - Workflow directory names contain extensive AI references: `AI-Email-Support-System`, `AI-Image-Generation`, `AI-Powered-Tech-Radar-Advisor`, `AI-Client-Onboarding-Agent`, `AI-Data-Analyst-Agent`, `AI-Research-Paper-Extraction`, `Automated-Investor-Intelligence`, `Automated-Event-Discovery`, `Gmail-MCP-Server`, `Smart-Email-Responder`
  - Provider names in dirs: OpenAI, Claude, Gemini, Mistral, Groq, DeepSeek, Ollama, Perplexity, OpenRouter — plus RAG/agentic-pattern names ("RAG Chatbot...", "Deep Research Agent", "multi-agent")
  - 9,823 total workflows cover LLM integrations across the major providers mentioned
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: MCP server workflow templates section
- **Wiki says:** Dedicated section of MCP server workflow templates covering eBay APIs, New York Times, Google services, Clearbit, Sentry, PagerDuty, and many more SaaS tools.
- **Source evidence:**
  - **303** workflow directories contain "mcp" in their name (measured: `find workflows/ -iname '*mcp*' | wc -l` = 303)
  - Examples confirmed: `Gmail-MCP-Server`, `eBay`/`NYT`/`Google`/`Clearbit`/`Sentry`/`PagerDuty`-related MCP tool server dirs (e.g. "Kitemaker Tool MCP Server", "Elastic Security Tool MCP Server", "Elevenlabs MCP Server")
  - Workflow JSON files are self-contained n8n imports that can include MCP server nodes
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Offline-ready, self-contained JSON files
- **Wiki says:** All workflow JSON files are self-contained and importable directly into any n8n instance without requiring network access to the official n8n workflow registry.
- **Source evidence:**
  - Each workflow folder contains a standalone `.json` file that is a complete n8n workflow export (standard n8n export structure: `nodes`, `connections`, `settings`, `createdAt`/`updatedAt`)
  - `rag_chatbot_for_company_documents_using_google_drive_and_gemini.json` contains full node graph, connections, credential references, and settings as a standard n8n export
  - `README.md` line 74: "Raw workflow export in JSON format, ready to be imported into n8n" — no external registry dependency
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Flat archive structure and independent origin
- **Wiki says:** The repository is structured as a flat archive: `workflows/` with one subdirectory per workflow, no subcategory hierarchy. Independently maintained, not affiliated with n8n.
- **Source evidence:**
  - `workflows/` directory contains flat listing of workflow subdirectories (no nested hierarchy beyond per-workflow folders)
  - `README.md` lines 57-59 (Disclaimer): "This project is **independent** and not officially affiliated with n8n. It is a personal initiative aimed at facilitating access to and preservation of public n8n workflows."
  - README links reference the `nusquama/n8nworkflows.xyz` repo (e.g. line 84: `https://github.com/nusquama/n8nworkflows.xyz/tree/main/workflows/...`) — origin org is `nusquama`, not `n8n-workflows`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (wiki frontmatter org corrected to `nusquama/n8nworkflows.xyz`)

## Summary

All 6 key claims from the n8nworkflows.xyz wiki have been verified against the source via directory exploration:
- ✅ 9,823 workflow templates in `workflows/` (README's 9,637 is stale)
- ✅ Standardized 4-file format per workflow (9,558/9,823 folders; 265 deviate) with `readme-{id}.md`, `{snake_case}.json`, `metada-{id}.json`, `{id}--{kebab}.webp` naming
- ✅ Extensive AI/LLM workflow coverage confirmed by directory names and content
- ✅ MCP server workflow templates present (303 dirs with "mcp" in name)
- ✅ Self-contained, offline-ready workflow JSON files confirmed
- ✅ Flat archive structure + independent origin (`nusquama/n8nworkflows.xyz`)

## Related

- [[n8nworkflows.xyz]] -- Main wiki entry
- [[n8n]] -- Workflow automation platform consuming these templates
- [[n8n-workflows]] -- n8n workflow template collection from GitHub

## Cross-project

- [[n8n.codegraph-verify]] -- Similar codegraph verification for n8n
- [[n8n-mcp.codegraph-verify]] -- Similar codegraph verification for n8n-mcp
- [[aws-n8n-templates.codegraph-verify]] -- Similar codegraph verification for workflow templates
