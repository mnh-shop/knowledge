---
name: integration-patterns-domain
description: "Reference deployment stacks and integration patterns combining multiple systems"
tags: [index, integration-patterns, catalog]
---

# Integration Patterns Domain

Reference architectures and deployment stacks showing how multiple systems in the ecosystem work together. Each stack-reference doc covers system architecture, communication patterns, Quadlet dependencies, and environment configuration.

## Stack References

| Doc | Stack | Description |
|-----|-------|-------------|
| [[stack-reference-mission-control|Mission Control Stack]] | Mission Control + OpenClaw + Hermes | Dashboard monitoring agents with webhook alerting |
| [[stack-reference-openclaw-n8n|OpenClaw + n8n Stack]] | OpenClaw + n8n | Agent gateway combined with workflow engine |
| [[stack-landscape|Stack Landscape]] | Ecosystem-wide | Full ecosystem stack landscape with all systems, communication patterns, and deployment topology |

## Related Concepts

- [[openclaw-agent-gateway]] — OpenClaw as agent routing gateway
- [[hermes-notification-relay]] — Hermes as multi-platform notification relay
- [[mission-control-dashboard]] — Mission Control dashboard UI
- [[n8n-workflow-engine]] — n8n workflow automation engine
- [[quadlet-deployment-guide]] — General Quadlet deployment patterns
- [[mcp-server-setup]] — MCP server configuration
- [[telegram-bot-setup]] — Telegram bot integration
- [[podman-pod-stack]] — Podman pod-based deployment stacks

## Common Patterns

- OpenClaw as central agent gateway with MCP tool exposure
- n8n for workflow automation triggered by agents
- Mission Control for agent health monitoring and dashboard
- Hermes for multi-platform notification relay (Telegram, Slack, Email)
- Quadlet systemd units for container lifecycle management
