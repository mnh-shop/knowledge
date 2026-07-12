---
name: memory
description: "Vault architecture, deployment principles, directory structure, domain documentation index, and assets catalog — root reference for the knowledge base"
tags: [index, reference, architecture, deployment, landscape]
---

# MEMORY.md

Persistent index of vault structure, deployment architecture, cross-repo compatibility principles, and catalog of domain documentation and reusable assets.

This is **not** a general note vault, a broad research archive, or a place for random notes.

## Target platforms

- **Development:** macOS (Apple Silicon, Podman Machine via vfkit)
- **Production:** Linux (Debian 12 or Fedora) on a VPS or bare metal
- **Never run autonomous AI agents directly on the host OS** — always isolate inside at least one boundary (VM or rootless container)

## Architecture principle

The deployment architecture follows a **defense-in-depth layering** model:

```
macOS/Linux host
  ├─ SSH tunnel (access)
  └─ (macOS) Podman Machine → Linux VM
     └─ Rootless Podman (Quadlet systemd units)
        ├─ OpenClaw or Hermes agent gateway
        ├─ service-gator MCP proxy (API key isolation)
        ├─ n8n workflow engine
        ├─ Agentfield orchestration
        └─ Mission Control dashboard
```

On a VPS: the cloud provider's VM boundary replaces Podman Machine.
On bare metal: optionally add crun-vm for nested VM isolation (requires /dev/kvm).

Key rule: **No AI agent code ever runs directly on the host OS.** The host runs only hypervisor/virtualization + SSH. All agent code runs inside rootless Podman containers inside a Linux VM.

## Vault structure

### Allowed top-level folders

```
sources/       Layer 1: Git clones (gitignored, 115 repos)
raw/           Layer 1: Repomix XML (gitignored, regeneratable)
graphs/        Layer 1: CodeGraph DBs (gitignored, regeneratable)
wiki/          Layer 2: One page per source repo (127 pages)
assets/        Layer 3: Reusable artifacts — skills, profiles, deploy templates
domains/       Layer 2: Cross-repo deep-dive docs (6 dimensions)
integrations/  Layer 3: System-to-system integration docs
memory/        Layer 3: Session memory and vault metadata
ideas/         Brainstorming space (ignored by default)
tests/         Validation scripts
```

### assets/ structure

```
assets/
├── INDEX.md                    Master catalog
├── agent-references/           20 agent reference profiles
├── hermes-profiles/            40 Hermes Agent role profiles
├── deployment/                 10 quadlet guides + 94 quadlet files
├── skills/                     67 skill categories across 867 files
├── n8n-workflows/              Sweep catalog of 9,655 workflows
├── mcp-servers/                4 MCP server references
├── acp-agents/                 2 ACP agent references
└── api-clients/                1 API client reference
```

### domains/ structure

```
domains/
├── architecture/       34 files — system design, component relationships
├── api/                21 files — REST/HTTP API references
├── mcp/                20 files — MCP server implementations
├── acp/                16 files — Agent Communication Protocol
├── deployment/         22 files — deployment and operations
└── integration-patterns/  16 files — cross-system stacks
```

### Companion page rule

Pages without a corresponding `sources/<name>/` directory are intentional **companion pages**:

| Pattern | Examples | Purpose |
|---------|----------|---------|
| `*.codegraph-verify.md` | agentfield.codegraph-verify, hermes-agent.codegraph-verify | Verification documentation for parent repo's wiki claims |
| Curated collections | cockpit, mcp, n8n-nodes, n8n-workflow-catalog, quadlet | Meta-docs grouping related repos under a functional concept |

Companion pages derive their ecosystem tag from their parent repo (per SCHEMA.md tag rule #2).

## Domain documentation index

### Architecture

| Doc | Repo | Description |
|-----|------|-------------|
| [hermes-agent](domains/architecture/hermes-agent-architecture.md) | hermes-agent | Core agent architecture, tool system, MCP/ACP surfaces |
| [hermes-workspace](domains/architecture/hermes-workspace-architecture.md) | hermes-workspace | Web/desktop command center and swarm orchestration |
| [hermes-suite](domains/architecture/hermes-suite-architecture.md) | hermes-suite | All-in-one container architecture |
| [n8n](domains/architecture/n8n-architecture.md) | n8n | Workflow engine internals |
| [n8n Instance AI](domains/architecture/n8n-instance-ai.md) | n8n | Instance AI feature architecture |
| [agentfield](domains/architecture/agentfield-architecture.md) | agentfield | Firecracker micro-VM control plane |
| [openclaw](domains/architecture/openclaw-architecture.md) | openclaw | Rust agent gateway architecture |
| [clawpier](domains/architecture/clawpier-architecture.md) | clawpier | Tauri desktop app, 58 commands |
| [mission-control](domains/architecture/mission-control-architecture.md) | mission-control | Orchestration dashboard |
| [podman](domains/architecture/podman-architecture.md) | podman | 3-layer architecture, rootless re-exec |
| [buildah](domains/architecture/buildah-architecture.md) | buildah | OCI image builder internals |
| [podlet](domains/architecture/podlet-architecture.md) | podlet | Quadlet generator internals |
| [crun-vm](domains/architecture/crun-vm-architecture.md) | crun-vm | QEMU OCI runtime shim |
| [sablier](domains/architecture/sablier-architecture.md) | sablier | Scale-to-zero internals |
| [nix-podman-stacks](domains/architecture/nix-podman-stacks-architecture.md) | nix-podman-stacks | Nix module system |
| [tank-os](domains/architecture/tank-os-architecture.md) | tank-os | Bootc image for OpenClaw |
| [hermzner](domains/architecture/hermzner-architecture.md) | hermzner | Hermes on Hetzner |
| [deployment architecture](domains/architecture/deployment-architecture.md) | — | Cross-cutting: defense-in-depth layering |
| [gogs](domains/architecture/gogs-architecture.md) | gogs | Git service internals |

### API

| Doc | Repo | Description |
|-----|------|-------------|
| [hermes-gateway-api](domains/api/hermes-gateway-api.md) | hermes-agent | Gateway REST API |
| [hermes-workspace-api](domains/api/hermes-workspace-api.md) | hermes-workspace | Workspace API |
| [agentfield-api](domains/api/agentfield-api.md) | agentfield | 14 route groups, 5-layer auth |
| [n8n-api](domains/api/n8n-api.md) | n8n | REST API reference |
| [openclaw-api](domains/api/openclaw-api.md) | openclaw | 90+ RPC methods |
| [gogs-api](domains/api/gogs-api.md) | gogs | Git service REST API |
| [tank-os-api](domains/api/tank-os-api.md) | tank-os | Health/status endpoints |
| [zot-api](domains/api/zot-api.md) | zot | Go coding agent API |

### MCP

| Doc | Repo | Description |
|-----|------|-------------|
| [hermes-mcp-implementation](domains/mcp/hermes-mcp-implementation.md) | hermes-agent | MCP server for Hermes |
| [hermes-workspace-mcp-hub](domains/mcp/hermes-workspace-mcp-hub.md) | hermes-workspace | Workspace MCP hub |
| [openclaw-mcp-implementation](domains/mcp/openclaw-mcp-implementation.md) | openclaw | 3 MCP server surfaces |
| [n8n-mcp](domains/mcp/n8n-mcp.md) | n8n | MCP node integration |
| [goclaw-mcp-implementation](domains/mcp/goclaw-mcp-implementation.md) | goclaw | Go MCP gateway |
| [podlet-mcp-implementation](domains/mcp/podlet-mcp-implementation.md) | podlet | Quadlet MCP |
| [sablier-mcp-implementation](domains/mcp/sablier-mcp-implementation.md) | sablier | Scale-to-zero MCP |

### ACP

| Doc | Repo | Description |
|-----|------|-------------|
| [hermes-acp-implementation](domains/acp/hermes-acp-implementation.md) | hermes-agent | ACP for Hermes |
| [openclaw-acp-implementation](domains/acp/openclaw-acp-implementation.md) | openclaw | stdio-to-Gateway bridge |
| [agentfield-acp-implementation](domains/acp/agentfield-acp-implementation.md) | agentfield | ACP for AgentField |
| [nanobot-acp-implementation](domains/acp/nanobot-acp-implementation.md) | nanobot | ACP for NanoBot |
| [alphaclaw-acp-implementation](domains/acp/alphaclaw-acp-implementation.md) | alphaclaw | ACP for AlphaClaw |
| [oh-my-pi-acp-implementation](domains/acp/oh-my-pi-acp-implementation.md) | oh-my-pi | ACP for Pi |

### Deployment

| Doc | Repo | Description |
|-----|------|-------------|
| [hermes-agent-docker](domains/deployment/hermes-agent-docker-deployment.md) | hermes-agent-docker | Docker image |
| [hermes-agent](domains/deployment/hermes-agent-deployment.md) | hermes-agent | Production deployment |
| [hermes-workspace](domains/deployment/hermes-workspace-deployment.md) | hermes-workspace | Workspace deployment |
| [hermes-suite](domains/deployment/hermes-suite-deployment.md) | hermes-suite | All-in-one deployment |
| [openclaw](domains/deployment/openclaw-deployment.md) | openclaw | OpenClaw deployment |
| [agentfield](domains/deployment/agentfield-deployment.md) | agentfield | Docker Compose + Helm |
| [clawpier](domains/deployment/clawpier-deployment.md) | clawpier | Desktop app |
| [mission-control](domains/deployment/mission-control-deployment.md) | mission-control | Dashboard setup |
| [n8n](domains/deployment/n8n-deployment.md) | n8n | Workflow engine |
| [podman](domains/deployment/podman-deployment.md) | podman | Quadlet + secrets |
| [buildah](domains/deployment/buildah-deployment.md) | buildah | OCI builder |
| [podlet](domains/deployment/podlet-deployment.md) | podlet | Quadlet gen |
| [crun-vm](domains/deployment/crun-vm-deployment.md) | crun-vm | OCI runtime |
| [sablier](domains/deployment/sablier-deployment.md) | sablier | Scale-to-zero |
| [tank-os](domains/deployment/tank-os-deployment.md) | tank-os | Bootc image |
| [hermzner](domains/deployment/hermzner-deployment.md) | hermzner | Hetzner VPS |

### Integration patterns

| Doc | Description |
|-----|-------------|
| [stack-landscape](domains/integration-patterns/stack-landscape.md) | Full ecosystem stack landscape |
| [stack-reference-mission-control](domains/integration-patterns/stack-reference-mission-control.md) | Mission Control + OpenClaw + Hermes |
| [stack-reference-openclaw-n8n](domains/integration-patterns/stack-reference-openclaw-n8n.md) | OpenClaw + n8n workflow engine |
| [openclaw-agent-gateway](domains/integration-patterns/openclaw-agent-gateway.md) | Agent routing gateway pattern |
| [openclaw-goclaw-mcp-bridge](domains/integration-patterns/openclaw-goclaw-mcp-bridge.md) | OpenClaw ↔ GoClaw MCP bridge |
| [goclaw-n8n-mcp-bridge](domains/integration-patterns/goclaw-n8n-mcp-bridge.md) | GoClaw ↔ n8n MCP bridge |
| [hermes-notification-relay](domains/integration-patterns/hermes-notification-relay.md) | Multi-platform notification relay |
| [mission-control-dashboard](domains/integration-patterns/mission-control-dashboard.md) | Dashboard monitoring |
| [mcp-server-setup](domains/integration-patterns/mcp-server-setup.md) | General MCP setup |
| [n8n-workflow-engine](domains/integration-patterns/n8n-workflow-engine.md) | Workflow engine pattern |
| [podman-pod-stack](domains/integration-patterns/podman-pod-stack.md) | Pod deployment stacks |
| [quadlet-deployment-guide](domains/integration-patterns/quadlet-deployment-guide.md) | Quadlet deployment |
| [telegram-bot-setup](domains/integration-patterns/telegram-bot-setup.md) | Telegram bot integration |
| [vault-structure-recommendations](domains/integration-patterns/vault-structure-recommendations.md) | Agent context retrieval |
| [openclaw-use-case-patterns](domains/integration-patterns/openclaw-use-case-patterns.md) | 42 real-world OpenClaw use case patterns |

## Assets index

See `assets/INDEX.md` for the master catalog. Key resources:

| Asset | Location | Description |
|-------|----------|-------------|
| Agent references | `assets/agent-references/` | 20 platform reference cards (hermes, openclaw, n8n, podman, etc.) |
| Hermes profiles | `assets/hermes-profiles/` | 40 role profiles (backend-engineer, cpo, orchestrator, etc.) |
| Deployment (Quadlet) | `assets/deployment/` | 10 guides + 94 quadlet .container/.volume files |
| Skills | `assets/skills/` | 67 categories, 867 files across engineering, security, design |
| MCP servers | `assets/mcp-servers/` | 4 MCP server implementation references |
| ACP agents | `assets/acp-agents/` | 2 ACP agent references |
| API clients | `assets/api-clients/` | Gateway platform reference |
| n8n workflows | `assets/n8n-workflows/` | Sweep catalog of 9,655 workflows with tool breakdown |

## Related

- [AGENTS.md](AGENTS.md) — Agent instructions, repo index table, verification rules
- [SCHEMA.md](SCHEMA.md) — File conventions, tag taxonomy, update policies
- [README.md](README.md) — Vault overview for human readers
