---
name: deployment-domain
description: "Deployment and operations guides for repositories in the vault"
tags: [deployment, index, catalog]
---

# Deployment Domain Docs

Deployment guides, operations templates, and infrastructure configuration for each repository.

## By Repository

| Doc | Repo | Description |
|-----|------|-------------|
| [[agentfield-deployment|AgentField Deployment]] | agentfield | Rootless Podman Quadlet setup with NixOS |
| [[buildah-deployment|Buildah Deployment]] | buildah | Container build tooling deployment |
| [[clawpier-deployment|ClawPier Deployment]] | clawpier | Tauri desktop app deployment |
| [[crun-vm-deployment|crun-vm Deployment]] | crun-vm | VM runtime deployment guide |
| [[goclaw-deployment|GoClaw Deployment]] | goclaw | Go binary deployment, container images, Quadlet patterns |
| [[gogs-deployment|Gogs Deployment]] | gogs | Self-hosted Git service deployment |
| [[hermes-agent-deployment|Hermes Agent Deployment]] | hermes-agent | Multi-platform personal AI agent deployment |
| [[hermes-agent-docker-deployment|Hermes Agent Docker]] | hermes-agent-docker | Minimal Docker image packaging |
| [[hermes-optimization-guide-deployment|Hermes Optimization Guide]] | hermes-optimization-guide | systemd units, Docker Compose, Caddy, VPS bootstrap |
| [[hermes-suite-deployment|Hermes Suite Deployment]] | hermes-suite | All-in-one container deployment |
| [[hermes-workspace-deployment|Hermes Workspace Deployment]] | hermes-workspace | System requirements and runtime config |
| [[hermzner-deployment|Hermzner Deployment]] | hermzner | Deployment guide |
| [[mission-control-deployment|Mission Control Deployment]] | mission-control | Control plane deployment |
| [[n8n-deployment|n8n Deployment]] | n8n | Workflow automation deployment |
| [[openclaw-deployment|OpenClaw Deployment]] | openclaw | Agent platform deployment guide |
| [[podlet-deployment|Podlet Deployment]] | podlet | Quadlet management deployment |
| [[podman-deployment|Podman Deployment]] | podman | Container engine deployment |
| [[quadlet-patterns|Quadlet Patterns]] | podman | General Quadlet deployment patterns |
| [[sablier-deployment|Sablier Deployment]] | sablier | Dynamic container scaling deployment |
| [[tank-os-deployment|Tank OS Deployment]] | tank-os | Container OS deployment |

## Common Patterns

- **Rootless Podman + Quadlet** is the dominant deployment stack
- **systemd user services** for per-user container lifecycle
- **NixOS flakes** for reproducible infrastructure
- Several repos use Docker Compose for development environments
