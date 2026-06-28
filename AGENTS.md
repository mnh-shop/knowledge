---
name: agents
description: "Agent implementation index: deployment targets, implementation status, and codegraph verification for all agent projects"
tags: [acp, ai-llm, architecture, cli, deployment, git, index, landscape, mcp, plugin-sdk, quadlet, shared, systemd]
---

# AGENTS.md

This is a GitHub-only knowledge system for coding agents.

## Principles

- **Never overengineer.** Favor the simplest solution that works. Add complexity only when it's proven necessary, not because it's anticipated.
- **Always interview and grill-me before building.** Before prototyping or implementing anything, run the `/interview` and `/grill-me` skills to validate the approach, understand constraints, and surface hidden requirements. No code before clarity.

## Focus

The focus is:

- architecture
- APIs
- MCP
- ACP
- deployment
- integrations between systems
- agentic loops

Do not create extra top-level folders.
Do not create folders unless the user asks or confirms when you ask.
Do not sort repositories by domain.
Do not duplicate repositories.

## Read-only directories

The following directories are **READ ONLY** — never modify, delete, or rename any file inside them:

- `sources/` — full cloned GitHub repositories (87 repos total)
- `raw/` — Repomix XML exports generated from repositories
- `graphs/` — CodeGraph database output from repositories

These directories contain reference data for analysis only. All editing happens in `wiki/`, `domains/`, `assets/`, `integrations/`, `memory/`, `ideas/`, and root files (AGENTS.md, MEMORY.md, README.md).

## Compatibility-first analysis

The long-term goal is reproducible deployment stacks combining Hermes, OpenClaw,
Agentfield, and n8n. Every repo should be checked for how it fits:

- **What does it provide?** (agent platform, CLI, skill, control plane, workflow engine, infra)
- **Interfaces:** MCP, REST API, CLI, webhooks, event bus, plugin system?
- **Compatibility:** Does it integrate with Hermes? OpenClaw? Agentfield? n8n?
- **Deployment:** What does it need to run? (config, database, ports, other services)

Seed `domains/integration-patterns/` with these cross-references — they're the
blueprint for deployment stacks.

## Structure

```text
sources/       full cloned GitHub repositories (gitignored, 87 repos)
raw/           Repomix XML generated from repositories
graphs/        CodeGraph output generated from repositories
wiki/          generated documentation per repository
assets/        reusable concrete things extracted from repos
  n8n-workflows/      extracted workflow patterns and catalogs
  skills/        extracted agent skill definitions
  profiles/      repo profiles + role-based personas (roles/)
  cross-refs/          integration cross-reference links
  deployment/          quadlet configs, infra templates
  mcp-servers/         MCP server references
  acp-agents/          ACP agent references
  api-clients/         API client references
domains/       cross-repo concept knowledge
integrations/  concrete system-to-system integration knowledge
```

## Wiki verification rule

**All wiki entries MUST be verified against source before publication.** Every wiki page must include:

- **Verification date** — When the content was last checked against source code
- **Verified by** — Who performed the verification (name or identifier)
- **Source reference** — Path in `sources/` that substantiates each claim

This prevents hallucinated content. When in doubt, check the canonical source or use `codegraph_explore` with `projectPath: "sources/<repo>"`.

## Agent knowledge lookup

All agents MUST use this knowledge base as the primary source for service facts. Do NOT dispatch @explorer for service information — the canonical source repositories are already indexed here.

| What | Path | How to use |
|---|---|---|
| **Canonical source code** | `knowledge/sources/<name>/` | CodeGraph-indexed. Use `codegraph_explore` with `projectPath: "knowledge/sources/<name>"` for source-level answers. |
| **CodeGraph indexes** | `knowledge/graphs/<name>/` | Separate `.codegraph/` per repo. Pass `projectPath: "knowledge/graphs/<name>"` to codegraph_explore when sources/ index is slow. |
| **Wiki summaries** | `knowledge/wiki/<name>.md` | LLM-synthesized page per repo (67-245 lines each). Read this FIRST before source exploration. |
| **Domain knowledge** | `knowledge/domains/` | Cross-cutting concepts: architecture, API, MCP, ACP, deployment, integration patterns. |
| **Deployable assets** | `knowledge/assets/` | Skills, n8n-workflows, MCP servers, profiles, deployment templates. |
| **Repomix XML extracts** | `knowledge/raw/<name>.xml` | Complete codebase summaries — use only when wiki and source exploration are insufficient. |

**Rule of thumb:** Read the wiki page first, then use CodeGraph on the source repo for specifics. Do NOT dispatch @explorer for service facts — use the knowledge base.

## Repository index

The table below tracks all indexed repositories and their corresponding vault locations. Use this to verify source references and ensure completeness.

| Repo | Wiki | Source | Raw | Graph | Notes |
|------|------|--------|-----|-------|-------|
| 1claw-hermes | none | sources/1claw-hermes/ | raw/1claw-hermes.xml | graphs/1claw-hermes/ | Companion page rule applies |
| abvx-agent-skills | [[abvx-agent-skills]] | sources/abvx-agent-skills/ | raw/abvx-agent-skills.xml | graphs/abvx-agent-skills/ | Agent skillpack |
| af-deep-research | none | sources/af-deep-research/ | raw/af-deep-research.xml | graphs/af-deep-research/ | Companion page rule applies |
| af-reactive-atlas-mongodb | none | sources/af-reactive-atlas-mongodb/ | raw/af-reactive-atlas-mongodb.xml | graphs/af-reactive-atlas-mongodb/ | Companion page rule applies |
| agent-rules-books | none | sources/agent-rules-books/ | raw/agent-rules-books.xml | graphs/agent-rules-books/ | Companion page rule applies |
| agentfield | [[agentfield]] | sources/agentfield/ | raw/agentfield.xml | graphs/agentfield/ | Firecracker micro-VMs |
| alphaclaw | [[alphaclaw]] | sources/alphaclaw/ | raw/alphaclaw.xml | graphs/alphaclaw/ | OpenClaw harness |
| awesome-n8n-templates | [[awesome-n8n-templates]] | sources/awesome-n8n-templates/ | raw/awesome-n8n-templates.xml | graphs/awesome-n8n-templates/ | Template collection |
| awesome-openclaw-skills | none | sources/awesome-openclaw-skills/ | raw/awesome-openclaw-skills.xml | graphs/awesome-openclaw-skills/ | Companion page rule applies |
| awesome-openclaw-usecases | none | sources/awesome-openclaw-usecases/ | raw/awesome-openclaw-usecases.xml | graphs/awesome-openclaw-usecases/ | Companion page rule applies |
| AionUi | [[AionUi]] | sources/AionUi/ | raw/AionUi.xml | graphs/AionUi/ | Desktop UI |
| bootc | [[bootc]] | sources/bootc/ | raw/bootc.xml | graphs/bootc/ | Bootable containers |
| buildah | [[buildah]] | sources/buildah/ | raw/buildah.xml | graphs/buildah/ | OCI image builder |
| camofox-browser | [[camofox-browser]] | sources/camofox-browser/ | raw/camofox-browser.xml | graphs/camofox-browser/ | Headless browser MCP |
| clawpier | [[clawpier]] | sources/clawpier/ | raw/clawpier.xml | graphs/clawpier/ | Desktop GUI |
| cockpit-podman | [[cockpit-podman]] | sources/cockpit-podman/ | raw/cockpit-podman.xml | graphs/cockpit-podman/ | Web UI plugin |
| communitytools | none | sources/communitytools/ | raw/communitytools.xml | graphs/communitytools/ | Companion page rule applies |
| crun-vm | none | sources/crun-vm/ | raw/crun-vm.xml | graphs/crun-vm/ | Companion page rule applies |
| defending-code-reference-harness | none | sources/defending-code-reference-harness/ | raw/defending-code-reference-harness.xml | graphs/defending-code-reference-harness/ | Companion page rule applies |
| drawio-skill | none | sources/drawio-skill/ | raw/drawio-skill.xml | graphs/drawio-skill/ | Companion page rule applies |
| ECC | [[ecc]] | sources/ECC/ | raw/ECC.xml | graphs/ECC/ | Email capture |
| fedora-coreos-config | none | sources/fedora-coreos-config/ | raw/fedora-coreos-config.xml | graphs/fedora-coreos-config/ | Companion page rule applies |
| free-claude-code | [[free-claude-code]] | sources/free-claude-code/ | raw/free-claude-code.xml | graphs/free-claude-code/ | Free tier MCP wrapper |
| goclaw | [[goclaw]] | sources/goclaw/ | raw/goclaw.xml | graphs/goclaw/ | Go MCP gateway |
| gogs | [[gogs]] | sources/gogs/ | raw/gogs.xml | graphs/gogs/ | Git server |
| graphify | none | sources/graphify/ | raw/graphify.xml | graphs/graphify/ | Companion page rule applies |
| hermes-agent | [[hermes-agent]] | sources/hermes-agent/ | raw/hermes-agent.xml | graphs/hermes-agent/ | MCP hub with 49 tools |
| hermes-agent-docker | none | sources/hermes-agent-docker/ | raw/hermes-agent-docker.xml | graphs/hermes-agent-docker/ | Companion page rule applies |
| hermes-agent-acp-skill | none | sources/hermes-agent-acp-skill/ | raw/hermes-agent-acp-skill.xml | graphs/hermes-agent-acp-skill/ | Companion page rule applies |
| hermes-agent-template | none | sources/hermes-agent-template/ | raw/hermes-agent-template.xml | graphs/hermes-agent-template/ | Companion page rule applies |
| hermes-autonomous-server | none | sources/hermes-autonomous-server/ | raw/hermes-autonomous-server.xml | graphs/hermes-autonomous-server/ | Companion page rule applies |
| hermes-bus | none | sources/hermes-bus/ | raw/hermes-bus.xml | graphs/hermes-bus/ | Companion page rule applies |
| hermes-incident-commander | none | sources/hermes-incident-commander/ | raw/hermes-incident-commander.xml | graphs/hermes-incident-commander/ | Companion page rule applies |
| hermes-optimization-guide | none | sources/hermes-optimization-guide/ | raw/hermes-optimization-guide.xml | graphs/hermes-optimization-guide/ | Companion page rule applies |
| hermes-plugins | none | sources/hermes-plugins/ | raw/hermes-plugins.xml | graphs/hermes-plugins/ | Companion page rule applies |
| hermes-profiles | none | sources/hermes-profiles/ | raw/hermes-profiles.xml | graphs/hermes-profiles/ | Companion page rule applies |
| hermes-startup-architect | none | sources/hermes-startup-architect/ | raw/hermes-startup-architect.xml | graphs/hermes-startup-architect/ | Companion page rule applies |
| hermes-suite | none | sources/hermes-suite/ | raw/hermes-suite.xml | graphs/hermes-suite/ | Companion page rule applies |
| hermes-workspace | [[hermes-workspace]] | sources/hermes-workspace/ | raw/hermes-workspace.xml | graphs/hermes-workspace/ | MCP hub server |
| Hexstrike-redteam | none | sources/Hexstrike-redteam/ | raw/Hexstrike-redteam.xml | graphs/Hexstrike-redteam/ | Companion page rule applies |
| hermzner | [[hermzner]] | sources/hermzner/ | raw/hermzner.xml | graphs/hermzner/ | Hetzner automations |
| hexstrike-ai | [[hexstrike-ai]] | sources/hexstrike-ai/ | raw/hexstrike-ai.xml | graphs/hexstrike-ai/ | Security framework |
| kali-pentest | none | sources/kali-pentest/ | raw/kali-pentest.xml | graphs/kali-pentest/ | Companion page rule applies |
| llmtrim | [[llmtrim]] | sources/llmtrim/ | raw/llmtrim.xml | graphs/llmtrim/ | Tool compressor |
| materia | [[materia]] | sources/materia/ | raw/materia.xml | graphs/materia/ | Agent framework |
| mission-control | [[mission-control]] | sources/mission-control/ | raw/mission-control.xml | graphs/mission-control/ | MCP audit server |
| Mnemosyne | [[Mnemosyne]] | sources/Mnemosyne/ | raw/Mnemosyne.xml | graphs/Mnemosyne/ | Memory system |
| n8n | [[n8n]] | sources/n8n/ | raw/n8n.xml | graphs/n8n/ | Workflow automation |
| n8n-mcp | [[n8n-mcp]] | sources/n8n-mcp/ | raw/n8n-mcp.xml | graphs/n8n-mcp/ | MCP node indexer |
| n8n-skills | [[n8n-skills]] | sources/n8n-skills/ | raw/n8n-skills.xml | graphs/n8n-skills/ | Workflow skills |
| n8n-workflows | [[n8n-workflows]] | sources/n8n-workflows/ | raw/n8n-workflows.xml | graphs/n8n-workflows/ | Workflow catalog |
| nanobot | [[nanobot]] | sources/nanobot/ | raw/nanobot.xml | graphs/nanobot/ | Agent framework |
| nix-podman-stacks | [[nix-podman-stacks]] | sources/nix-podman-stacks/ | raw/nix-podman-stacks.xml | graphs/nix-podman-stacks/ | NixOS configs |
| nix.dev | none | sources/nix.dev/ | raw/nix.dev.xml | graphs/nix.dev/ | Companion page rule applies |
| nyxstrike | [[nyxstrike]] | sources/nyxstrike/ | raw/nyxstrike.xml | graphs/nyxstrike/ | Security orchestration |
| obsidian-skills | none | sources/obsidian-skills/ | raw/obsidian-skills.xml | graphs/obsidian-skills/ | Companion page rule applies |
| oh-my-hermes | [[oh-my-hermes]] | sources/oh-my-hermes/ | raw/oh-my-hermes.xml | graphs/oh-my-hermes/ | OMH plugin system |
| oh-my-openagent | none | sources/oh-my-openagent/ | raw/oh-my-openagent.xml | graphs/oh-my-openagent/ | Companion page rule applies |
| oh-my-opencode-slim | none | sources/oh-my-opencode-slim/ | raw/oh-my-opencode-slim.xml | graphs/oh-my-opencode-slim/ | Companion page rule applies |
| oh-my-pi | [[oh-my-pi]] | sources/oh-my-pi/ | raw/oh-my-pi.xml | graphs/oh-my-pi/ | Fork of pi-mono |
| openclaw | [[openclaw]] | sources/openclaw/ | raw/openclaw.xml | graphs/openclaw/ | Rust agent platform |
| openclaw-container | none | sources/openclaw-container/ | raw/openclaw-container.xml | graphs/openclaw-container/ | Companion page rule applies |
| openclaw-plugin-claude-code | none | sources/openclaw-plugin-claude-code/ | raw/openclaw-plugin-claude-code.xml | graphs/openclaw-plugin-claude-code/ | Companion page rule applies |
| opencode | [[opencode]] | sources/opencode/ | raw/opencode.xml | graphs/opencode/ | AI coding agent |
| opencode-hermes-multiagent | none | sources/opencode-hermes-multiagent/ | raw/opencode-hermes-multiagent.xml | graphs/opencode-hermes-multiagent/ | Companion page rule applies |
| open-design | none | sources/open-design/ | raw/open-design.xml | graphs/open-design/ | Companion page rule applies |
| openviking | [[openviking]] | sources/OpenViking/ | raw/OpenViking.xml | graphs/OpenViking/ | OOB message relay |
| outreachmagic | none | sources/outreachmagic/ | raw/outreachmagic.xml | graphs/outreachmagic/ | Companion page rule applies |
| pi | [[pi]] | sources/pi/ | raw/pi.xml | graphs/pi/ | TypeScript agent harness |
| podlet | [[podlet]] | sources/podlet/ | raw/podlet.xml | graphs/podlet/ | Quadlet generator |
| podman | [[podman]] | sources/podman/ | raw/podman.xml | graphs/podman/ | Container engine |
| podman-compose | none | sources/podman-compose/ | raw/podman-compose.xml | graphs/podman-compose/ | Companion page rule applies |
| pydantic-ai-skills | none | sources/pydantic-ai-skills/ | raw/pydantic-ai-skills.xml | graphs/pydantic-ai-skills/ | Companion page rule applies |
| quadlet | [[quadlet]] | sources/quadlet/ | raw/quadlet.xml | graphs/quadlet/ | systemd generator |
| reverse-skill | none | sources/reverse-skill/ | raw/reverse-skill.xml | graphs/reverse-skill/ | Companion page rule applies |
| sablier | [[sablier]] | sources/sablier/ | raw/sablier.xml | graphs/sablier/ | Time-based access |
| sec-af | [[sec-af]] | sources/sec-af/ | raw/sec-af.xml | graphs/sec-af/ | Security agent |
| skills | none | sources/skills/ | raw/skills.xml | graphs/skills/ | Companion page rule applies |
| tank-os | [[tank-os]] | sources/tank-os/ | raw/tank-os.xml | graphs/tank-os/ | bootc image |
| zot | [[zot]] | sources/zot/ | raw/zot.xml | graphs/zot/ | Go coding agent |

**Key:** `none` = no dedicated wiki page, use companion page rule (see `sources/<repo>/` for documentation)

**In-scope repos with wiki pages (all have summaries):**
Primary agent repos (full wiki summaries): hermes-agent, openclaw, goclaw, zot, oh-my-hermes, agentfield, n8n, pi, oh-my-pi, tank-os, free-claude-code, n8n-mcp, n8n-workflows, abvx-agent-skills, nanobot, materia
