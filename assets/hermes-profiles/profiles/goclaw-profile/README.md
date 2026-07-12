# GoClaw Profile

GoClaw profile provides specialized guidance for working with the GoClaw AI agent gateway.

## Overview

GoClaw is a Go-based AI agent gateway that provides:

- **Agent Lifecycle Management**: Create, configure, and manage AI agents
- **Tool Execution**: Execute tools across multiple agent types
- **MCP Client/Server**: Connect to external MCP servers or expose GoClaw tools
- **ACP Orchestration**: Manage external AI agents via JSON-RPC
- **REST API**: Comprehensive HTTP API for agent management

## Skills Dependencies

| Skill | Provides |
|-------|----------|
| `artifact-pyramids` | Progressive disclosure output format |
| `backend-engineering` | API patterns, service architecture, database access, integration, error handling methodology |
| `goclaw-integration` | GoClaw-specific MCP/ACP client-server implementation |

## Output Format

Artifact pyramid. Response is the absolute path to `00-index.md`.

## Installation

```bash
git clone https://github.com/nextlevelbuilder/goclaw-profiles.git ~/goclaw-profiles
ln -s ~/goclaw-profiles/profiles/goclaw-profile ~/.goclaw/profiles/
goclaw --profile goclaw-profile
goclaw status
```

## Key Features

### Agent Management
- Create and configure AI agents with specific roles
- Manage agent lifecycles (start, stop, restart)
- Configure agent workspaces and prompts
- Export/import agent configurations

### Integration Capabilities
- MCP client connectivity to external tools
- MCP server functionality for internal tool exposure
- ACP orchestration for external agent management
- REST API for programmatic control

### Deployment Options
- **Native**: systemd Quadlet deployment
- **Docker**: Docker Compose deployment
- **Kubernetes**: Helm chart support
- **Cloud**: Managed service deployment

## Configuration

Profile configuration is managed through:

```yaml
# ~/.goclaw/profiles/goclaw-profile/config.yaml
name: goclaw-profile
mode: production
monitoring: enabled
audit: enabled
```

## Commands

### Agent Operations
```bash
# Create agent
goclaw agent create --name my-agent --role orchestrator

# List agents
goclaw agent list

# Start agent
goclaw agent start my-agent

# Execute tool
goclaw agent execute my-agent --skill api-call --input '{"url": "https://api.example.com"}'

# Check status
goclaw agent status my-agent
```

### Integration Operations
```bash
# Connect MCP server
goclaw mcp connect --server external-mcp-server --name mcp-bridge

# Expose tools as MCP server
goclaw mcp serve --agent my-agent

# ACP agent orchestration
goclaw acp orchestrate --agent gemini --prompt "Analyze this data"

# Health check
goclaw health check

# Start auto-updates
goclaw auto-update enable
```

## Monitoring

Profile enables comprehensive monitoring:

- **Health Checks**: `/healthz` endpoint monitoring
- **Run Traces**: Timeline-based execution tracking
- **Audit Logs**: Cryptographic audit trail for all operations
- **Performance Metrics**: Resource usage and agent performance

## Security

Profile includes security features:

- **IAM Integration**: DID/VC identity management
- **API Key Management**: Secure credential storage
- **Authorization**: Role-based access control
- **Encryption**: All communication encrypted

## Integration Patterns

### MCP Bridge Pattern
```bash
goclaw mcp serve --agent api-agent --output mcp-bridge
```

### External Agent Pattern
```bash
goclaw acp orchestrate --agent claude --workspace ./agents/claude
```

### Tool Discovery Pattern
```bash
# Discover available tools via GoClaw's tools registry
goclaw tools discover --tags "api,rest,webhook"

# Execute discovered tools
goclaw tools execute "api-call" --params '{"url": "https://example.com"}'
```

## Related

- [[goclaw]] — GoClaw main documentation
- [[goclaw-api]] — REST API reference
- [[goclaw-mcp]] — MCP integration details
- [[goclaw-acp]] — ACP orchestration documentation
- [[goclaw-deployment]] — Deployment guides