---
name: n8n-mcp-api
description: "n8n-mcp API — MCP tools exposed, search/query endpoints, node indexing, template system"
source: sources/n8n-mcp/
tags: [n8n-mcp, api, n8n, mcp]
---

# n8n-MCP API

n8n-MCP exposes its API through the **Model Context Protocol (MCP)** — tools and resources for AI assistants to discover, query, and configure n8n's 1,845+ node ecosystem. Also provides HTTP transport and a SQLite query interface.

## Overview

An MCP server bridging n8n's node ecosystem with AI assistants. Indexes every n8n node's parameters, operations, and documentation into a searchable SQLite database with FTS5. Supports stdio and HTTP transport.

## API Surface

**MCP Discovery Tools:**
| Tool | Description |
|------|-------------|
| `n8n_list_available_tools` | List all 1,845 indexed nodes |
| `n8n_search_nodes` | FTS5 full-text search across nodes |
| `n8n_get_node_essentials` | Fast essential parameters |
| `n8n_get_node_info` | Full node info with all properties |
| `n8n_list_ai_tools` | List 265+ AI-capable tool variants |

**MCP Configuration & Validation Tools:**
| Tool | Purpose |
|------|---------|
| `n8n_validate_node_operation` | Validate full node config |
| `n8n_validate_workflow` | Complete workflow validation |
| `n8n_generate_workflow` | Generate workflow from description |

**MCP Management Tools (via n8n HTTP):**
`n8n_create_workflow` (POST /rest/workflows), `n8n_read_workflow`, `n8n_activate_workflow`, `n8n_execute_workflow`, `n8n_health_check`

**MCP Resources:**
| URI Pattern | Content |
|-------------|---------|
| `n8n://docs/{nodeType}` | Full node documentation |
| `n8n://essentials/{nodeType}` | Essential parameters |

**SQLite Database API:** `data/nodes.db` with FTS5 search. Repository: `searchNodes()`, `getNode()`, `listAiTools()`. **Template API:** 2,352+ templates from `api.n8n.io`.

## Authentication

No auth for MCP stdio mode. HTTP transport supports bearer token auth. n8n management tools require n8n API key.

## Usage

```json
// MCP tool call example
{
  "method": "tools/call",
  "params": {
    "name": "n8n_search_nodes",
    "arguments": { "query": "slack send message" }
  }
}
```

```bash
# Start stdio MCP server
npm start

# Start HTTP MCP server
npm run start:http

# Rebuild node database from n8n packages
npm run rebuild
```

## Related

- [[domains/api/INDEX|api]]
- [[n8n-mcp]] — Full project documentation
- [[n8n]] — n8n workflow platform
- [[mcp]] — Model Context Protocol ecosystem
- [[n8n-workflows]] — Workflow catalog
