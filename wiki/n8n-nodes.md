---
name: n8n-nodes
description: "n8n node ecosystem — workflow automation nodes spanning AI/LLM, HTTP, database, file, messaging, and SaaS integrations"
source: sources/n8n/
tags: [fair-code, integration, mcp, n8n, workflow-automation]
---

# n8n Nodes

## Overview

n8n provides a comprehensive node ecosystem spanning AI/LLM, HTTP, database, file, messaging, and SaaS integrations. Nodes are the fundamental building blocks of n8n workflows, providing triggers, actions, and transformations that enable users to connect disparate services and automate complex workflows without writing extensive code.

Each node in n8n represents a discrete operation or integration point — whether that's receiving a webhook trigger, querying a database, calling an API, processing data through AI models, or sending a message to Slack. The node-based architecture follows a visual programming paradigm where users can chain nodes together to create sophisticated automation pipelines.

## Key Features

### Node Categories

- **Trigger Nodes**: Start workflows automatically on events (webhooks, schedules, polling)
- **AI/LLM Nodes**: Integrate with language models (OpenAI, Anthropic, Google, Ollama)
- **Database Nodes**: Connect to PostgreSQL, MySQL, MongoDB, SQLite, and other data stores
- **HTTP/API Nodes**: Make REST requests, handle authentication, process responses
- **Messaging Nodes**: Slack, Discord, Telegram, email (SMTP), SMS integrations
- **File System Nodes**: Read/write files, manipulate directories, handle uploads/downloads
- **SaaS Integrations**: 400+ services including GitHub, GitLab, Trello, Notion, Airtable
- **Utility Nodes**: Function, Set, IF, Merge, Split for data manipulation and routing

### Core Capabilities

- **Visual Configuration**: Drag-and-drop interface with parameter forms for each node type
- **Code When Needed**: JavaScript/Python execution within Function nodes for custom logic
- **Expression Language**: n8n's templating system for dynamic data referencing
- **Credential Management**: Secure storage and injection of API keys and authentication
- **Error Handling**: Retry policies, error branches, and fail-safe configurations
- **Community Extensions**: npm-installable nodes that extend the core functionality

### Node Types

- **Regular Nodes**: Execute once per workflow run
- **Trigger Nodes**: Start workflow execution on events
- **Poller Nodes**: Periodically check for changes (pull-based)
- **Hybrid Nodes**: Can act as both trigger and action

## Detailed Architecture

### Node Structure

Each n8n node consists of:

1. **Node Type Definition**: Declares what the node does and its category
2. **Parameters**: User-configurable options (credentials, operations, data mappings)
3. **Credentials**: Secure authentication handling for service integrations
4. **Execution Logic**: The code that runs when the node is executed
5. **Output**: Data passed to downstream nodes via n8n's linking system

### Data Flow

Nodes receive input data through the `items` array, where each item represents a record to process. The output flows to connected nodes, enabling:

- **Linear flows**: Data passes through nodes sequentially
- **Parallel branches**: Multiple nodes can run simultaneously
- **Merge operations**: Combine data from multiple branches
- **Conditional routing**: IF/Switch nodes direct data based on values

### Property System

Each node has a properties array defining:

- **Display options**: Conditional visibility and UI behavior
- **Type validation**: String, number, boolean, object, array types
- **Default values**: Preset configurations for ease of use
- **Placeholders**: Example values in the UI
- **Options**: Predefined choices for dropdowns and selections

## Community Ecosystem

### Community Nodes

The community contributes over 1,000 additional nodes through:

- **npm packages**: `@n8n/nodes-*` scoped packages
- **Custom integrations**: Nodes for niche services and tools
- **AI tool bridges**: Specialized nodes for AI agent workflows
- **Industry-specific**: Healthcare, finance, manufacturing extensions

### Contributing Nodes

Developers can create custom nodes using:

```typescript
// Node structure example
export class MyCustomNode implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'My Custom Node',
    name: 'myCustomNode',
    group: ['transform'],
    version: 1,
    description: 'Description of what this node does',
    defaults: { name: 'myCustomNode' },
    inputs: ['main'],
    outputs: ['main'],
    properties: [...]
  }
}
```

## Related Documentation

- [[n8n]] — Overall n8n platform documentation and architecture
- [[n8n-mcp]] — MCP server providing AI-assisted n8n workflow authoring
- [[n8n-workflows]] — Workflow templates and patterns
- [[awesome-n8n-templates]] — Curated collection of workflow templates

## In This Vault

- [[../sources/n8n-mcp/CLAUDE.md]] — n8n-MCP development instructions
- Nodes are indexed in the n8n-MCP SQLite database at `sources/n8n-mcp/data/nodes.db`

## Source

This documentation references the n8n node ecosystem. For source code and implementation details, see the n8n repository at `sources/n8n/`.