---
name: v1-stack-architecture
description: "Security-boundary agentic architecture — layered orchestration with Hermes, OpenClaw, n8n, and AgentField. Workspace prototype."
tags: [ideas, deployment, setup-factory, architecture, security, hermes, agentfield, n8n, openclaw]
source: workspace/deployment-setup-automation/setup-factory/manifests/userspace/v1-stack-README.md
---

> **⚠️ Idea / Prototype — not production-grade.**
> This V1 stack architecture is a design exploration from the setup-factory workspace.
> Not yet battle-tested.

## Architecture Overview

```
User (Telegram)
   ↓
hermes-lightweight (security boundary, 5 profiles)
   ├── producer-1 profile → opencode-producer-1 (opencode + oh-my-opencode-slim)
   ├── producer-2 profile → opencode-producer-2 (opencode, openai-focused)
   ├── producer-3 profile → free-claude-code-producer (FCC + claude-code)
   ├── critical-reviewer profile → review-tool (oh-my-pi)
   └── librarian profile → librarian-kb (RAG over postgres)
   ↓
agentfield (control plane, web UI on :8080)
   ├── kanban: profiles as lanes, tasks as cards
   ├── agent registry: all services register here
   └── DID/VC identity for approvals
```

## Services (10 images, ~3.9GB RAM)

| Service | Image | Memory | Role |
|---|---|---|---|
| hermes-lightweight | setup-factory/hermes-lightweight:3.13 | 200MB | Security boundary, Telegram front door, 5 profiles |
| opencode-producer-1 | setup-factory/opencode-producer-1:3.13 | 500MB | Producer harness (7 agents, 7 skills, council) |
| opencode-producer-2 | setup-factory/opencode-producer-2:3.13 | 500MB | Producer harness (openai-focused) |
| free-claude-code-producer | setup-factory/free-claude-code-producer:3.13 | 400MB | Producer harness (Claude ecosystem) |
| review-tool | setup-factory/review-tool:3.13 | 384MB | Critical reviewer (oh-my-pi) |
| librarian-kb | setup-factory/librarian-kb:3.13 | 300MB | Knowledge base (RAG over postgres) |
| openclaw | docker.io/openclaw/openclaw:latest | 300MB | TypeScript agent gateway |
| n8n | docker.io/n8nio/n8n:latest | 500MB | Workflow automation + HITL approval |
| postgres | pgvector/pgvector:pg16 | 300MB | State (pgvector for librarian-kb) |
| agentfield | docker.io/agentfield/control-plane:latest | 500MB | Control plane + web UI (kanban) |

## Deployment

### Prerequisites

- Docker or rootless Podman
- `yq` for manifest validation
- Secrets file at `~/.config/setup-factory/secrets.env` (mode 0600)

### Quick Start

```bash
# 1. Initialize secrets
./scripts/secrets-init.sh v1-stack

# 2. Validate manifest
./rules/validator.sh manifests/userspace/v1-stack.yaml

# 3. Deploy with Docker
./scripts/deploy-docker.sh v1-stack

# Or deploy with Podman (rootless)
./scripts/deploy-podman.sh v1-stack
```

### Access Points

- **AgentField (kanban)**: http://localhost:8080
- **n8n (workflows)**: http://localhost:5678
- **OpenClaw (gateway)**: http://localhost:18789
- **Hermes (Telegram)**: Configured via `TELEGRAM_BOT_TOKEN`

## Kanban Usage

- **Profiles are lanes**: producer-1 (blue), producer-2 (green), producer-3 (purple), critical-reviewer (red), librarian (orange)
- **Tasks are cards**: Each task shows status, assignee, and progress
- **Drag to reassign**: Move tasks between profile lanes
- **HITL checkpoints**: Approve plans, reviews, and merges via Telegram slash commands

## See also

- [[setup-factory/README|Setup Factory overview]]
- [[setup-factory/ROADMAP|Roadmap]]
