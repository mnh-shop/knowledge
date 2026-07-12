---
name: memory
description: "Persistent index of cross-vault relationships: deployment mappings, cross-repo compatibility, and graph location notes"
tags: [acp, ai-llm, ansible, architecture, container, dashboard, deployment, desktop-app, docker, git, index, landscape, mcp, nix, orchestration, plugin-sdk, podman, quadlet, shared, systemd, terraform, virtualization, webhook]
---

# MEMORY.md

This knowledge folder is a simple GitHub-only knowledge system for coding agents.

It exists to help agents understand repositories, architecture, APIs, MCP, ACP, deployment, reusable assets, and integrations between systems.

This is not a general note vault.
This is not a broad research archive.
This is not a Johnny Decimal system.
This is not a place for random notes, task packs, reports, or registry experiments.
This is not an ideas folder.

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

## Main rule

Keep the structure simple.

Allowed top-level folders:

```text
sources/
raw/
graphs/
wiki/
assets/
domains/
integrations/
ideas/
```

Do not add new top-level folders unless the user explicitly asks.

## `ideas/`

Purpose:

Practical brainstorming space for the user and agents.

This folder is for developing possible use cases, setups, deployment ideas, product ideas, agent workflows, and practical build directions.

Agents should only look here when the user explicitly asks for:

* brainstorming
* idea development
* use case generation
* setup planning
* deployment planning
* practical project concepts
* "what could we build with this?"
* "how could we use these repos together?"

Rules:

* Ignore `ideas/` by default.
* Do not use `ideas/` as source truth.
* Do not use `ideas/` for architecture facts.
* Do not use `ideas/` for API facts.
* Do not use `ideas/` for MCP/ACP facts.
* Do not use `ideas/` for deployment facts.
* Do not use `ideas/` for integration evidence.
* Only read or write `ideas/` when the user specifically asks for idea work.

Use `ideas/` for practical brainstorming like:

```text
ideas/travel-agent-sales-automation.md
ideas/osint-research-system.md
ideas/multi-agent-dev-workbench.md
ideas/github-repo-intelligence-pipeline.md
ideas/vps-deployment-setups.md
ideas/n8n-agent-workflows.md
```

`ideas/` is allowed to be speculative.

Everything else should remain evidence-grounded.

## Coverage status

| Wiki entry | Architecture | MCP | API/ACP | Deploy | Profile |
|---|---|---|---|---|---|
| [[hermes-agent]] | ✅ | ✅ | ✅ | ✅ | ✅ |
| [[hermes-workspace]] | ✅ (2) | ✅ | ✅ | ✅ | ✅ |
| [[hermes-startup-architect]] | ❌ | — | — | ❌ | ✅ |
| [[n8n]] | ✅ (2) | ✅ | ✅ | ✅ | ✅ |
| [[agentfield]] | ✅ | ✅ | ✅ | ✅ | ✅ |
| [[sec-af]] | ❌ | — | ❌ | ❌ | ❌ |
| [[af-deep-research]] | ❌ | — | ❌ | ❌ | ❌ |
| [[af-reactive-atlas-mongodb]] | ❌ | — | ❌ | ❌ | ❌ |
| [[SWE-AF]] | ❌ | — | ❌ | ❌ | ❌ |
| [[openclaw]] | ✅ | ✅ | ✅ | ✅ | ✅ |
| [[hermzner]] | ✅ | — | — | ✅ | ❌ |
| [[tank-os]] | ✅ | — | — | ✅ | ❌ |
| [[mission-control]] | ✅ | — | ✅ | ✅ | ✅ |
| [[crun-vm]] | ✅ | — | — | ✅ | ❌ |
| [[podman]] | ✅ | — | — | ✅ | ✅ |
| [[sablier]] | ✅ | — | — | ✅ | ❌ |
| [[buildah]] | ✅ | — | — | ✅ | ✅ |
| [[podlet]] | ✅ | — | — | ✅ | ❌ |
| [[nix-podman-stacks]] | ✅ | — | — | ❌ | ❌ |
| [[clawpier]] (NEW) | ✅ | — | — | ✅ | ✅ |
| [[gogs]] (NEW) | ✅ | — | ✅ | ✅ | ❌ |
| [[hermes-agent-docker]] (NEW) | ❌ | — | — | ✅ | ❌ |
| [[hermes-suite]] (NEW) | ✅ | — | — | ✅ | ❌ |
| [[awesome-openclaw-skills]] (NEW) | ❌ | — | — | ❌ | ❌ |
| [[llmtrim]] (NEW) | ✅ | — | — | ❌ | ❌ |
| [[nanobot]] (NEW) | ✅ | — | — | ❌ | ❌ |
| [[nix.dev]] (NEW) | ❌ | — | — | ❌ | ❌ |
| [[opencode-hermes-multiagent]] (NEW) | ❌ | — | — | ❌ | ❌ |

❌ = not yet done  ·  (N) = multiple architecture docs ·  — = N/A

**115 repos total — all 115 have wiki entries.** Wiki coverage is now complete.

## Cross-repo compatibility

Each repo is checked against the 4 core systems ([[hermes-agent]], [[openclaw]], [[agentfield]], [[n8n]]) to see what can combine. This section grows as we analyze more repos — compatibility is noted in each repo's wiki entry via internal links.

| Repo | Hermes | OpenClaw | Agentfield | n8n | Notes |
|---|---|---|---|---|---|
| [[hermes-agent]] | — | Similar architecture | ✅ MCP bridge | ✅ Webhook triggers | Core agent platform |
| [[hermes-workspace]] | Direct UI | Could wrap | Could wrap | — | Swarm + MCP Hub |
| [[hermes-startup-architect]] | Hermes skill | — | — | — | Not a service |
| [[hermes-agent-docker]] | Packages Hermes | N/A | N/A | N/A | Docker packaging |
| [[hermes-suite]] | All-in-one bundle | N/A | N/A | N/A | 3-in-1 container |
| [[n8n]] | Webhook consumer/provider | — | Could orchestrate? | — | Workflow engine |
| [[agentfield]] | ✅ MCP bridge | ✅ MCP bridge | — | Complementary | Control plane |
| [[sec-af]] | MCP? | MCP? | Built on it | Could trigger from? | Security auditor |
| [[af-deep-research]] | MCP? | MCP? | Built on it | Could trigger from? | Research engine |
| [[af-reactive-atlas-mongodb]] | MCP? | MCP? | Built on it | Could trigger from? | Reactive DB layer |
| [[SWE-AF]] | MCP? | MCP? | Built on it | Could trigger from? | Engineering factory |
| [[openclaw]] | Competing | — | ✅ MCP bridge | ✅ MCP tools → n8n | Full agent gateway |
| [[clawpier]] | ✅ manages bots | ✅ manages bots | — | — | Desktop manager |
| [[hermzner]] | Deploys Hermes | N/A | N/A | N/A | Hermes on Hetzner only |
| [[tank-os]] | N/A | Deploys OpenClaw | N/A | N/A | OpenClaw bootc appliance |
| [[mission-control]] | ✅ adapter | ✅ native | ✅ generic REST | ✅ webhooks | Management dashboard |
| [[crun-vm]] | Runtime for all | Runtime for all | Runtime for all | Runtime for all | Low-level OCI runtime |
| [[podman]] | Container runtime | Container runtime | Container runtime | Container runtime | Foundation layer |
| [[sablier]] | Scale-to-zero | Scale-to-zero | Scale-to-zero | Scale-to-zero | Proxy plugin for all |
| [[buildah]] | Image builder | Image builder | Image builder | Image builder | Image builder for all |
| [[podlet]] | Dev tool | Dev tool | Dev tool | Dev tool | Quadlet file generator |
| [[nix-podman-stacks]] | Nix mgmt | Nix mgmt | Nix mgmt | ✅ has n8n module | Nix/Home Manager stacks |
| [[gogs]] | Git backend | Git backend | Git backend | ✅ webhooks | Git service for all |
| [[awesome-openclaw-skills]] | Reference | Skills listed | — | — | Skill marketplace for OpenClaw |
| [[llmtrim]] | ✅ proxy | ✅ proxy | — | — | Compresses Hermes, n8n, OpenClaw LLM calls |
| [[nanobot]] | Similar arch | Similar arch | ✅ MCP bridge | ✅ Webhook triggers | Competing Python agent framework |
| [[nix.dev]] | — | — | — | ✅ nix module | Nix documentation reference |
| [[opencode-hermes-multiagent]] | Direct config | — | — | — | Multi-agent pipeline for Hermes |

— = likely not applicable or not yet known · ? = hypothetical, needs verification

## Current intended structure

```text
knowledge/
├── AGENTS.md
├── MEMORY.md
├── sources/
├── raw/
├── graphs/
├── wiki/
├── assets/
│   ├── profiles/
│   ├── skills/
│   ├── mcp-servers/
│   ├── acp-agents/
│   ├── api-clients/
│   ├── deployment/
│   ├── adapters/
│   └── workflows/
├── domains/
│   ├── architecture/
│   ├── api/
│   ├── mcp/
│   ├── acp/
│   ├── deployment/
│   └── integration-patterns/
├── integrations/
└── ideas/
```

## Wiki entries
- [hermes-agent](wiki/hermes-agent.md) — Self-improving AI agent (Nous Research)
- [hermes-workspace](wiki/hermes-workspace.md) — Web/desktop command center for Hermes, with swarm orchestration
- [hermes-startup-architect](wiki/hermes-startup-architect.md) — Hermes skill: startup idea → 8-file research kit
- [n8n](wiki/n8n.md) — n8n: workflow automation platform (fair-code), 400+ integrations
- [agentfield](wiki/agentfield.md) — AgentField: open-source AI control plane (Apache 2.0)
- [sec-af](wiki/sec-af.md) — SEC-AF: AI-native security auditor (built on AgentField)
- [af-deep-research](wiki/af-deep-research.md) — AF Deep Research: recursive research engine (built on AgentField)
- [af-reactive-atlas-mongodb](wiki/af-reactive-atlas-mongodb.md) — AF Reactive Atlas MongoDB: real-time intelligence layer (built on AgentField)
- [SWE-AF](wiki/SWE-AF.md) — SWE-AF: autonomous engineering team runtime (built on AgentField)
- [openclaw](wiki/openclaw.md) — OpenClaw: personal AI assistant (MIT), full agent gateway with ACP + MCP + 30+ channels
- [hermzner](wiki/hermzner.md) — Hermzner: hardened Hermes Agent on Hetzner (Terraform + Ansible)
- [tank-os](wiki/tank-os.md) — Tank OS: Fedora bootc image running OpenClaw as rootless Podman
- [mission-control](wiki/mission-control.md) — Mission Control: self-hosted AI agent orchestration dashboard (MIT)
- [crun-vm](wiki/crun-vm.md) — OCI runtime shim: run QEMU VMs as containers via podman/docker/k8s
- [podman](wiki/podman.md) — Podman: daemonless rootless container engine (Apache 2.0)
- [sablier](wiki/sablier.md) — Sablier: scale-to-zero reverse proxy plugin (Go, Apache 2.0)
- [buildah](wiki/buildah.md) — Buildah: daemonless OCI image builder (Go, Apache 2.0)
- [podlet](wiki/podlet.md) — Podlet: Quadlet file generator (Rust, Apache 2.0)
- [nix-podman-stacks](wiki/nix-podman-stacks.md) — Declarative Podman Quadlet stacks via Nix/Home Manager
- [clawpier](wiki/clawpier.md) — Tauri desktop manager for OpenClaw/Hermes Docker containers
- [gogs](wiki/gogs.md) — Gogs: self-hosted Git service (Go, MIT)
- [hermes-agent-docker](wiki/hermes-agent-docker.md) — Minimal Docker image for Hermes Agent
- [hermes-suite](wiki/hermes-suite.md) — All-in-one Hermes container (gateway + dashboard + webui)
- [awesome-openclaw-skills](wiki/awesome-openclaw-skills.md) — Curated list of 5300+ community-built OpenClaw skills
- [llmtrim](wiki/llmtrim.md) — Local LLM request compression proxy (Rust)
- [nanobot](wiki/nanobot.md) — Ultra-lightweight open-source AI agent (Python)
- [nix.dev](wiki/nix.dev.md) — Official Nix documentation site
- [opencode-hermes-multiagent](wiki/opencode-hermes-multiagent.md) — Multi-agent pipeline for Hermes/OpenCode
- [Android-Pentesting-Checklist](wiki/Android-Pentesting-Checklist.md) — Comprehensive Android security testing guide
- [Anthropic-Cybersecurity-Skills](wiki/Anthropic-Cybersecurity-Skills.md) — 817+ cybersecurity skills for Claude Code
- [CyberStrikeAI](wiki/CyberStrikeAI.md) — AI-powered cybersecurity testing framework (Go, Apache 2.0)
- [ECC](wiki/ECC.md) — Agent harness OS: 67 agents, 271 skills, cross-harness support
- [Hexstrike-redteam](wiki/Hexstrike-redteam.md) — AI-driven adversarial red team automation (Go)
- [OpenViking](wiki/OpenViking.md) — Open-source data forensics platform
- [SecuritySkills](wiki/SecuritySkills.md) — 45 framework-grounded security skills for AI coding agents
- [agent-rules-books](wiki/agent-rules-books.md) — Curated library of AI agent behavioral rules
- [communitytools](wiki/communitytools.md) — Docker-powered community infrastructure tools
- [defending-code-reference-harness](wiki/defending-code-reference-harness.md) — Reference harness for securing AI coding environments
- [fedora-coreos-config](wiki/fedora-coreos-config.md) — Fedora CoreOS configuration repository
- [hermes-profiles](wiki/hermes-profiles.md) — 38 curated Hermes Agent profiles for specialist swarms
- [hexstrike-ai](wiki/hexstrike-ai.md) — AI-powered penetration testing automation framework
- [kali-pentest](wiki/kali-pentest.md) — Kali Linux penetration testing environment automation
- [outreachmagic](wiki/outreachmagic.md) — AI-powered experimental outreach engine
- [reverse-skill](wiki/reverse-skill.md) — 15 reverse engineering skills for pentesters and RE analysts

## Related

**Vault Structure:**
- [Vault Structure Recommendations](domains/integration-patterns/vault-structure-recommendations.md) — Agent context retrieval improvements
- [Tag Taxonomy](memory/tag-taxonomy.md) — Complete ecosystem/language/classification tags

**General Architecture:**
- [Deployment Architecture](domains/architecture/deployment-architecture.md) — Defense-in-depth: host → VM → rootless Podman → agents
- [Stack Landscape](domains/integration-patterns/stack-landscape.md) — Full system landscape mapping

**AgentField:**
- [Architecture: agentfield](domains/architecture/agentfield-architecture.md)
- [API: agentfield](domains/api/agentfield-api.md) — 14 route groups, 5-layer auth, DID IAM, SDK-generated APIs
- [Deployment: agentfield](domains/deployment/agentfield-deployment.md) — Docker Compose, Helm, production operations

**Hermes Agent:**
- [Architecture: hermes-agent](domains/architecture/hermes-agent-architecture.md)
- [MCP: hermes-agent](domains/mcp/hermes-mcp-implementation.md)
- [ACP: hermes-agent](domains/acp/hermes-acp-implementation.md)
- [Gateway API: hermes-agent](domains/api/hermes-gateway-api.md)

**Hermes Workspace:**
- [Architecture: hermes-workspace](domains/architecture/hermes-workspace-architecture.md)
- [Swarm Architecture: hermes-workspace](domains/architecture/hermes-workspace-swarm-architecture.md)
- [MCP Hub: hermes-workspace](domains/mcp/hermes-workspace-mcp-hub.md)

**Hermes Docker Packaging:**
- [Deployment: hermes-agent-docker](domains/deployment/hermes-agent-docker-deployment.md)

**Hermes Suite:**
- [Architecture: hermes-suite](domains/architecture/hermes-suite-architecture.md)
- [Deployment: hermes-suite](domains/deployment/hermes-suite-deployment.md)

**n8n:**
- [Architecture: n8n](domains/architecture/n8n-architecture.md)
- [Instance AI: n8n](domains/architecture/n8n-instance-ai.md)
- [API: n8n](domains/api/n8n-api.md)
- [MCP: n8n](domains/mcp/n8n-mcp.md)
- [Deployment: n8n](domains/deployment/n8n-deployment.md)

**OpenClaw:**
- [Architecture: openclaw](domains/architecture/openclaw-architecture.md)
- [API: openclaw](domains/api/openclaw-api.md) — 90+ RPC methods
- [MCP: openclaw](domains/mcp/openclaw-mcp-implementation.md) — 3 MCP server surfaces
- [ACP: openclaw](domains/acp/openclaw-acp-implementation.md) — stdio-to-Gateway bridge
- [Deployment: openclaw](domains/deployment/openclaw-deployment.md)

**ClawPier:**
- [Architecture: clawpier](domains/architecture/clawpier-architecture.md) — Tauri IPC architecture, 58 commands
- [Deployment: clawpier](domains/deployment/clawpier-deployment.md)

**Gogs:**
- [Architecture: gogs](domains/architecture/gogs-architecture.md) — Go-based self-hosted Git service
- [API: gogs](domains/api/gogs-api.md) — REST API reference
- [Deployment: gogs](domains/deployment/gogs-deployment.md)

**Mission Control:**
- [Architecture: mission-control](domains/architecture/mission-control-architecture.md)
- [API: mission-control](domains/api/mission-control-api.md)
- [Deployment: mission-control](domains/deployment/mission-control-deployment.md)

**Podman / Infrastructure:**
- [Architecture: podman](domains/architecture/podman-architecture.md) — 3-layer architecture, rootless re-exec, lifecycle
- [Deployment: podman](domains/deployment/podman-deployment.md) — Quadlet, secrets, auto-updates
- [Architecture: buildah](domains/architecture/buildah-architecture.md) — OCI image builder internals
- [Deployment: buildah](domains/deployment/buildah-deployment.md)
- [Architecture: podlet](domains/architecture/podlet-architecture.md) — Quadlet generator internals
- [Deployment: podlet](domains/deployment/podlet-deployment.md)
- [Architecture: crun-vm](domains/architecture/crun-vm-architecture.md) — QEMU OCI runtime shim
- [Deployment: crun-vm](domains/deployment/crun-vm-deployment.md)
- [Architecture: sablier](domains/architecture/sablier-architecture.md) — scale-to-zero internals
- [Deployment: sablier](domains/deployment/sablier-deployment.md)
- [Architecture: nix-podman-stacks](domains/architecture/nix-podman-stacks-architecture.md) — Nix module system
- [Architecture: tank-os](domains/architecture/tank-os-architecture.md)
- [Deployment: tank-os](domains/deployment/tank-os-deployment.md)
- [Architecture: hermzner](domains/architecture/hermzner-architecture.md)
- [Deployment: hermzner](domains/deployment/hermzner-deployment.md)
- [Deployment: hermes-workspace](domains/deployment/hermes-workspace-deployment.md)
- [Deployment: hermes-agent](domains/deployment/hermes-agent-deployment.md)

## Asset files

**Agent profiles (hermz runtime):**
- [Hermes Profiles Catalog](assets/hermes-profiles/) — 39 specialization profiles (orchestrator, backend-engineer, sre, security-engineer, etc.)

**Agent references (reference cards):**
- [Reference: hermes-agent](assets/agent-references/hermes-agent-reference.md)
- [Reference: hermes-workspace](assets/agent-references/hermes-workspace-reference.md)
- [Reference: n8n](assets/agent-references/n8n-agent-reference.md)
- [Reference: agentfield](assets/agent-references/agentfield-reference.md)
- [Reference: openclaw](assets/agent-references/openclaw-reference.md)
- [Reference: mission-control](assets/agent-references/mission-control-reference.md)
- [Reference: podman](assets/agent-references/podman-reference.md)
- [Reference: buildah](assets/agent-references/buildah-reference.md)
- [Reference: clawpier](assets/agent-references/clawpier-reference.md) — Desktop agent manager

**MCP servers:**
- [MCP server: hermes-mcp-serve](assets/mcp-servers/hermes-mcp-serve.md)
- [MCP server: agentfield (bridge)](assets/mcp-servers/agentfield-mcp-server.md)
- [MCP server: openclaw](assets/mcp-servers/openclaw-mcp-server.md)
- [MCP server: mission-control](assets/mcp-servers/mission-control-mcp-server.md)

**ACP agents:**
- [ACP agent: HermesACPAgent](assets/acp-agents/hermes-acp-agent.md)
- [ACP agent: openclaw](assets/acp-agents/openclaw-acp-agent.md)

**Deployment assets (Quadlet):**
- [Quadlet: agentfield](assets/deployment/agentfield-quadlet.md)
- [Quadlet: hermes-agent](assets/deployment/hermes-agent-quadlet.md)
- [Quadlet: hermes-workspace](assets/deployment/hermes-workspace-quadlet.md)
- [Quadlet: mission-control](assets/deployment/mission-control-quadlet.md)
- [Quadlet: openclaw](assets/deployment/openclaw-quadlet.md)
- [Quadlet: podman](assets/deployment/podman-quadlet-examples.md)
- [Quadlet: podlet](assets/deployment/podlet-quadlet-examples.md)
- [Quadlet: sablier](assets/deployment/sablier-quadlet.md)
- [Quadlet: tank-os](assets/deployment/tank-os-quadlet.md)
- [Terraform+Ansible: hermzner](assets/deployment/hermzner-terraform-ansible.md)

**Other:**
- [Gateway platforms: hermes-agent](assets/api-clients/hermes-gateway-platforms.md)
- [Startup Architect skill](assets/skills/hermes-startup-architect-skill.md)

**Skill Catalogs (by Use Case):**
- [Skills Catalog](assets/skills/) — Cross-harness skills organized by use case (1000+)
- [Cybersecurity Skills](assets/skills/cybersecurity/) — 900+ security across 4 sub-catalogs: [[ai-appsec]], [[cloud-infrastructure-security]], [[offensive-security]], [[governance-compliance-ir]]
- [Software Engineering Skills](assets/skills/software-engineering/) — 235+ dev/debug/architecture skills (new: 15 Hermes Agent native skills)
- [Research Skills](assets/skills/research/) — 45+ evidence gathering and synthesis skills (new: 5 Hermes Agent research skills)
- [Orchestration Skills](assets/skills/orchestration/) — 54+ multi-agent workflow patterns (new: 4 Hermes Agent agent orchestration skills)
- [Token Efficiency Skills](assets/skills/token-efficiency/) — 11+ token optimization skills
- [Product Management Skills](assets/skills/product-management/) — 45+ product planning skills (new: 15 Hermes productivity tools)
- [Content Creation Skills](assets/skills/content-creation/) — 95+ creative/generative skills (new: 22 Hermes Agent creative skills)
- [Infrastructure Skills](assets/skills/infrastructure/) — 35+ deployment/operations skills (new: 11 Hermes Agent MLOps/infra skills)
- [n8n Workflows](assets/skills/n8n-workflows/) — 188 workflow automation patterns
