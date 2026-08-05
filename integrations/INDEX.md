---
name: integrations-index
description: "Cross-system integration documentation index — deployment stacks, bridges, and workflow orchestration"
tags: [index, integration, catalog]
---

# Integrations Index

System-to-system integration documentation covering deployment stacks, MCP bridges, workflow orchestration, and monitoring pipelines across the AI agent ecosystem.

## Deployment Stacks

| Doc | Stack | Description |
|-----|-------|-------------|
| [[hermes-openclaw-deployment|Hermes + OpenClaw]] | Hermes + OpenClaw | Side-by-side Podman Quadlet with MCP bridge on shared network |
| [[hermes-podman-deployment|Hermes + Podman]] | Hermes + Podman | Rootless Podman Quadlet deployment with systemd auto-update |
| [[openclaw-podman-deployment|OpenClaw + Podman]] | OpenClaw + Podman | Rootless Podman Quadlet with multi-channel support and GPU passthrough |
| [[n8n-podman-deployment|n8n + Podman]] | n8n + Podman | n8n under Podman Quadlet with PostgreSQL, auto-update, backup |
| [[podman-quadlet-service-stack|Podman Quadlet Service Stack]] | Hermes + n8n + Postgres + Redis | Complete 4-service agent stack with Quadlet systemd units |
| [[nix-podman-stacks-n8n|Nix Podman Stacks + n8n]] | Nix + Podman + n8n | Declarative n8n module via nix-podman-stacks |

## MCP Bridges

| Doc | Stack | Description |
|-----|-------|-------------|
| [[hermes-goclaw-mcp-bridge|Hermes ↔ GoClaw]] | Hermes + GoClaw | Hermes consumes GoClaw MCP server for Go-native tools via SSE |
| [[openclaw-n8n-gateway|OpenClaw → n8n]] | OpenClaw + n8n | OpenClaw agent gateway routing to n8n workflows via MCP |
| [[openclaw-goclaw-mcp-bridge|OpenClaw ↔ GoClaw]] | OpenClaw + GoClaw | OpenClaw MCP bridge to GoClaw Go-native tools |
| [[goclaw-n8n-mcp-bridge|GoClaw ↔ n8n]] | GoClaw + n8n | GoClaw MCP bridge to n8n workflow engine |
| [[agentfield-n8n-workflow-trigger|AgentField → n8n]] | AgentField + n8n | AgentField triggering n8n workflows via webhook, n8n reporting back via API |
| [[agentfield-openclaw-stack|AgentField + OpenClaw]] | AgentField + OpenClaw | AgentField orchestrating OpenClaw agent gateways over MCP |

## Monitoring & Observability

| Doc | Stack | Description |
|-----|-------|-------------|
| [[hermes-mission-control-monitoring|Hermes → Mission Control]] | Hermes + Mission Control | Mission Control dashboard monitoring Hermes deployments |
| [[mission-control-n8n-monitoring|Mission Control → n8n]] | Mission Control + n8n | Mission Control monitoring n8n workflow executions and health |

## Messaging & Notification

| Doc | Stack | Description |
|-----|-------|-------------|
| [[hermes-telegram-whatsapp-messaging|Hermes Telegram + WhatsApp]] | Hermes + Telegram + WhatsApp | Multi-platform messaging via Hermes channels with notification routing |

## AI Pipelines

| Doc | Stack | Description |
|-----|-------|-------------|
| [[n8n-supabase-ai-pipeline|n8n + Supabase AI]] | n8n + Supabase | n8n AI agent workflows with Supabase pgvector for RAG pipelines |

## Desktop Integration

| Doc | Stack | Description |
|-----|-------|-------------|
| [[clawpier-desktop-integration|ClawPier + Hermes + OpenClaw]] | ClawPier + Hermes + OpenClaw | ClawPier desktop manager for Docker container lifecycle and agent monitoring |

## Security Monitoring

| Doc | Stack | Description |
|-----|-------|-------------|
| [[security-monitoring-stack|hexstrike + nyxstrike + SecuritySkills]] | hexstrike + nyxstrike + SecuritySkills | AI-powered security scanning pipeline under Podman with Prometheus |

## Patterns

- **MCP bridge pattern**: Agent A exposes MCP tools → Agent B consumes them over SSE/stdio
- **Quadlet service stack**: Multiple agents + services deployed as coordinated Podman Quadlet units with shared network
- **Webhook trigger pattern**: Agent triggers workflow via HTTP webhook, workflow reports results back
- **Dashboard monitoring pattern**: Mission Control or similar dashboard monitors agent health and workflow execution
- **Message relay pattern**: Hermes as multi-platform notification relay bridging agents to messaging platforms
