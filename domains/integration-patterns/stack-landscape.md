---
name: stack-landscape
tags: [acp, ai-llm, architecture, bootc, cli, container, dashboard, deployment, desktop-app, docker, git, integration, landscape, mcp, nix, orchestration, plugin-sdk, podman, quadlet, security, shared, systemd, virtualization, webhook]
description: Full system landscape mapping across 23 repositories organized in 6 functional layers with compatibility matrix
---

# Stack Landscape — 23 Repos Across 6 Layers

**Source:** `domains/integration-patterns/`

This document maps all 23 repositories in the knowledge system across functional layers,
showing what each provides and how they combine.

## Four Core Systems

| System | Layer | Role | Interfaces |
|---|---|---|---|
| [[hermes-agent]] | Agent Platform | Self-improving AI agent with gateway (REST API, CLI, MCP, ACP) | REST (gateway), MCP (serve), ACP (agent), CLI, webhooks |
| [[openclaw]] | Agent Platform | Personal AI assistant with gateway (ACP, MCP, 30+ channels) | REST (RPC), MCP (3 servers), ACP (stdio bridge), CLI |
| [[agentfield]] | Control Plane | Rule-based agent orchestration with DID-based IAM | REST (5 auth levels), MCP (bridge), SDK |
| [[n8n]] | Workflow Engine | Node-based workflow automation, 400+ integrations | REST, MCP (server), webhooks, GraphQL |

## Hermes Ecosystem

| System | Layer | Role | Interfaces |
|---|---|---|---|
| [[hermes-workspace]] | Dev Platform | Web/desktop command center for Hermes, swarm orchestration, MCP hub | REST, MCP (hub), CLI |
| [[hermes-startup-architect]] | Agent Skill | Hermes skill: startup idea → 8-file research kit | Skill (Hermes internal) |
| [[hermes-agent-docker]] | Packaging | Minimal Docker image for Hermes Agent | Docker |
| [[hermes-suite]] | Packaging | All-in-one container with gateway + dashboard + webui | Docker/Podman |
| [[hermzner]] | Deployment | Terraform + Ansible blueprint: hardened Hermes on Hetzner | Terraform, Ansible |

## OpenClaw Ecosystem

| System | Layer | Role | Interfaces |
|---|---|---|---|
| [[tank-os]] | Deployment | Fedora bootc appliance, deploys OpenClaw as rootless Podman | bootc, Podman, Quadlet |
| [[clawpier]] | Desktop Tool | Tauri desktop app for managing OpenClaw/Hermes in Docker sandboxes | Tauri IPC, Docker |

## AgentField Ecosystem

| System | Layer | Role | Interfaces |
|---|---|---|---|
| [[sec-af]] | Agent (Security) | AI-native adversarial security auditor (4-agent verification chain) | AgentField app |
| [[SWE-AF]] | Agent (Engineering) | Autonomous engineering team runtime (25+ specialized agents) | AgentField app |
| [[af-deep-research]] | Agent (Research) | Recursive research engine (DHE, 10k+ agent invocations) | AgentField app |
| [[af-reactive-atlas-mongodb]] | Agent (Data) | Real-time MongoDB intelligence layer (Atlas Triggers → AgentField) | MongoDB Atlas Trigger |

## Management & Dashboards

| System | Layer | Role | Interfaces |
|---|---|---|---|
| [[mission-control]] | Dashboard | Web-based AI agent orchestration dashboard (multi-system adapter) | REST, MCP, webhooks |

## Infrastructure Tooling

| System | Layer | Role | Interfaces |
|---|---|---|---|
| [[podman]] | Container Runtime | Daemonless rootless container engine | CLI (podman), REST (API v5), Quadlet, systemd |
| [[buildah]] | Image Builder | Daemonless OCI image builder | CLI, script, Dockerfile |
| [[podlet]] | Dev Tool | Generate Quadlet files from podman run/compose/existing objects | CLI |
| [[crun-vm]] | Runtime Shim | Run QEMU VMs as OCI containers | OCI runtime (crun shim) |
| [[sablier]] | Proxy | Scale-to-zero reverse proxy plugin for container runtimes | REST, Traefik/Caddy/Nginx plugin |
| [[nix-podman-stacks]] | Declarative Config | Nix/Home Manager module for declarative Quadlet stacks | Nix, Home Manager |

## Git & Collaboration

| System | Layer | Role | Interfaces |
|---|---|---|---|
| [[gogs]] | Git Service | Lightweight self-hosted Git service (Go) | REST API, SSH, Git, webhooks |

## Overlaps and Gaps

### Hermes vs OpenClaw

Both are agent gateways — they compete in capability but differ in architecture:
- **Hermes** is Python-based with a REST gateway, MCP serve, and ACP agent
- **OpenClaw** is TypeScript-based with 3 MCP servers, ACP stdio bridge, 30+ channels, and RPC-based API
- Both have similar agent capabilities (tools, skills, memory, multi-platform)
- [[clawpier]] manages both runtimes in Docker containers

### n8n + Agents

n8n complements both agent gateways:
- Webhook triggers from agents
- MCP tools exposed to agents
- Workflow steps that invoke agents for AI decisions
- The bridge is well-established in both directions

### AgentField vs Agent Gateways

AgentField is a **control plane**, not an agent itself:
- It orchestrates multi-agent workflows deterministically (rule-based DAGs)
- Hermes and OpenClaw gateways handle individual agent interactions
- They complement: gateways handle agents, AgentField orchestrates them
- Communication via MCP bridge or REST API

### Missing Bridges

| Bridge | Status | Notes |
|---|---|---|
| n8n → ClawPier | Not built | Could webhook trigger ClawPier bot actions? |
| Gogs → Hermes/OpenClaw | Not built | Git could become an agent tool (code search, PR review) |
| Gogs → n8n | Available | Webhook triggers |
| Gogs → SWE-AF | Not built | SWE-AF could use Gogs as code repository backend |
| ClawPier → n8n | Not built | Could trigger n8n webhooks for bot events |

## Related

- [[hermes-agent]] — Agent platform
- [[hermes-workspace]] — Dev platform with swarm
- [[hermes-startup-architect]] — Agent skill
- [[hermes-agent-docker]] — Docker packaging
- [[hermes-suite]] — All-in-one container
- [[n8n]] — Workflow engine
- [[agentfield]] — Control plane
- [[sec-af]] — Security auditor
- [[SWE-AF]] — Engineering runtime
- [[af-deep-research]] — Research engine
- [[af-reactive-atlas-mongodb]] — Reactive DB layer
- [[openclaw]] — Agent gateway
- [[clawpier]] — Desktop manager
- [[hermzner]] — Hetzner deploy
- [[tank-os]] — Bootc appliance
- [[mission-control]] — Dashboard
- [[crun-vm]] — VM runtime
- [[podman]] — Container engine
- [[sablier]] — Scale-to-zero
- [[buildah]] — Image builder
- [[podlet]] — Quadlet generator
- [[nix-podman-stacks]] — Nix stacks
- [[gogs]] — Git service
