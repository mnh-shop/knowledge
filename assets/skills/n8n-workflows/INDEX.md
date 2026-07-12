---
name: n8n-workflows
description: "188 workflow automation patterns spanning 90+ categories via n8n-mcp skills integration"
tags: [n8n-workflows, n8n-skills, skills, mcp, automation, workflow-automation]
metadata:
  type: catalog
---

# n8n Workflows

Workflow automation patterns for n8n platform, accessible via n8n-mcp MCP tools.

**Total workflows:** 188+ in n8n-workflows repository  
**Skill count:** 14 native n8n-mcp skills in `sources/n8n-skills/`

---

## n8n-mcp Skills

| Skill | Description |
|-------|-------------|
| using-n8n-mcp-skills | Router skill — always consult first |
| n8n-mcp-tools-expert | MCP tool usage, node discovery, credentials |
| n8n-workflow-patterns | Architectural patterns (webhook, batch, scheduled, AI agent) |
| n8n-node-configuration | Operation-aware node setup |
| n8n-expression-syntax | Expression syntax and data mapping |
| n8n-validation-expert | Error interpretation and fixing |
| n8n-code-javascript | Code node JavaScript patterns |
| n8n-code-python | Code node Python patterns |
| n8n-code-tool | Custom Code Tool for AI agents |
| n8n-error-handling | Retries, error outputs, 4xx/5xx shapes |
| n8n-binary-and-data | Files, images, binary data handling |
| n8n-subworkflows | Reusable sub-workflow design |
| n8n-agents | AI agent / LLM-with-tools patterns |
| n8n-multi-instance | Multiple n8n instance management |

---

## Workflow Categories (90+)

From `sources/n8n-workflows/context/def_categories.json`:

### AI & Automation
- AI Agent Development
- Business Process Automation
- Technical Infrastructure & DevOps

### Data & Storage
- Data Processing & Analysis
- Cloud Storage & File Management

### Communication
- Communication & Messaging
- Social Media Management

### Business
- CRM & Sales
- Marketing & Advertising Automation
- Financial & Accounting
- Project Management

### Creative
- Creative Design Automation
- Creative Content & Video Automation

### Technical
- Web Scraping & Data Extraction
- E-commerce & Retail

---

## Harness Compatibility

| Harness | Support | Notes |
|---------|---------|-------|
| **n8n** | Native | MCP server integration |
| **Hermes Agent** | Full | MCP bridge |
| **OpenClaw** | Full | MCP bridge |
| **AgentField** | Full | Via ECC hooks |
| **ECC** | Full | Native MCP integration |
| **opencode** | Full | MCP tools |

---

## Related

- [[skills-catalog]] — Main catalog
- [[n8n]] — Workflow automation platform
- [[n8n-mcp]] — MCP server for n8n
- [[n8n-skills]] — Skill repository