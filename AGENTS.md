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

- `sources/` — full cloned GitHub repositories (115 repos total)
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
sources/       full cloned GitHub repositories (gitignored, 115 repos)
raw/           Repomix XML generated from repositories
graphs/        CodeGraph output generated from repositories
wiki/          generated documentation per repository
assets/        reusable concrete things extracted from repos
  n8n-workflows/      extracted workflow patterns and catalogs
  skills/        extracted agent skill definitions
  profiles/      repo profiles + role-based personas
  agent-references/    agent reference profiles for specialist swarms
  hermes-profiles/     Hermes Agent role profiles (40+ roles)
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

The table below tracks all indexed repositories and their corresponding vault locations. Generated from actual filesystem state — 115 sources, 90 wikis, 114 raw exports, 115 codegraph indexes.

| Repo | Wiki | Source | Raw | Graph | Notes |
|------|------|--------|-----|-------|-------|
| 1claw-hermes | [[1claw-hermes]] | sources/1claw-hermes/ | raw/1claw-hermes/ | graphs/1claw-hermes/ | |
| Agent-Reach | none | sources/Agent-Reach/ | raw/Agent-Reach/ | graphs/Agent-Reach/ | Companion page rule applies |
| AionUi | [[AionUi]] | sources/AionUi/ | raw/AionUi/ | graphs/AionUi/ | Desktop UI |
| Android-Pentesting-Checklist | [[Android-Pentesting-Checklist]] | sources/Android-Pentesting-Checklist/ | raw/Android-Pentesting-Checklist/ | graphs/Android-Pentesting-Checklist/ | |
| Anthropic-Cybersecurity-Skills | [[Anthropic-Cybersecurity-Skills]] | sources/Anthropic-Cybersecurity-Skills/ | raw/Anthropic-Cybersecurity-Skills/ | graphs/Anthropic-Cybersecurity-Skills/ | |
| CyberStrikeAI | [[CyberStrikeAI]] | sources/CyberStrikeAI/ | raw/CyberStrikeAI/ | graphs/CyberStrikeAI/ | |
| ECC | [[ecc]] | sources/ECC/ | raw/ECC/ | graphs/ECC/ | Agent harness OS |
| Hermes-caduceus | [[Hermes-caduceus]] | sources/Hermes-caduceus/ | raw/Hermes-caduceus/ | graphs/Hermes-caduceus/ | |
| Hexstrike-redteam | [[Hexstrike-redteam]] | sources/Hexstrike-redteam/ | raw/Hexstrike-redteam/ | graphs/Hexstrike-redteam/ | |
| Mnemosyne | [[Mnemosyne]] | sources/Mnemosyne/ | raw/Mnemosyne/ | graphs/Mnemosyne/ | Memory system |
| NotFair | none | sources/NotFair/ | raw/NotFair/ | graphs/NotFair/ | Companion page rule applies |
| OpenViking | [[openviking]] | sources/OpenViking/ | raw/OpenViking/ | graphs/OpenViking/ | OOB message relay |
| SWE-AF | [[SWE-AF]] | sources/SWE-AF/ | raw/SWE-AF/ | graphs/SWE-AF/ | |
| SecuritySkills | [[SecuritySkills]] | sources/SecuritySkills/ | raw/SecuritySkills/ | graphs/SecuritySkills/ | |
| Understand-Anything | none | sources/Understand-Anything/ | raw/Understand-Anything/ | graphs/Understand-Anything/ | Companion page rule applies |
| abvx-agent-skills | [[abvx-agent-skills]] | sources/abvx-agent-skills/ | raw/abvx-agent-skills/ | graphs/abvx-agent-skills/ | Agent skillpack |
| af-deep-research | [[af-deep-research]] | sources/af-deep-research/ | raw/af-deep-research/ | graphs/af-deep-research/ | |
| af-reactive-atlas-mongodb | [[af-reactive-atlas-mongodb]] | sources/af-reactive-atlas-mongodb/ | raw/af-reactive-atlas-mongodb/ | graphs/af-reactive-atlas-mongodb/ | |
| agent-rules-books | [[agent-rules-books]] | sources/agent-rules-books/ | raw/agent-rules-books/ | graphs/agent-rules-books/ | |
| agentfield | [[agentfield]] | sources/agentfield/ | raw/agentfield/ | graphs/agentfield/ | Firecracker micro-VMs |
| ai-marketing-claude-code-skills | [[ai-marketing-claude-code-skills]] | sources/ai-marketing-claude-code-skills/ | raw/ai-marketing-claude-code-skills/ | graphs/ai-marketing-claude-code-skills/ | |
| alphaclaw | [[alphaclaw]] | sources/alphaclaw/ | raw/alphaclaw/ | graphs/alphaclaw/ | OpenClaw harness |
| appstore | none | sources/appstore/ | raw/appstore/ | graphs/appstore/ | Companion page rule applies |
| awesome-n8n-templates | [[awesome-n8n-templates]] | sources/awesome-n8n-templates/ | raw/awesome-n8n-templates/ | graphs/awesome-n8n-templates/ | Template collection |
| awesome-openclaw-skills | [[awesome-openclaw-skills]] | sources/awesome-openclaw-skills/ | raw/awesome-openclaw-skills/ | graphs/awesome-openclaw-skills/ | |
| awesome-openclaw-usecases | [[awesome-openclaw-usecases]] | sources/awesome-openclaw-usecases/ | raw/awesome-openclaw-usecases/ | graphs/awesome-openclaw-usecases/ | |
| bootc | [[bootc]] | sources/bootc/ | raw/bootc/ | graphs/bootc/ | Bootable containers |
| buildah | [[buildah]] | sources/buildah/ | raw/buildah/ | graphs/buildah/ | OCI image builder |
| camofox-browser | [[camofox-browser]] | sources/camofox-browser/ | raw/camofox-browser/ | graphs/camofox-browser/ | Headless browser MCP |
| claude-ai-music-skills | [[claude-ai-music-skills]] | sources/claude-ai-music-skills/ | raw/claude-ai-music-skills/ | graphs/claude-ai-music-skills/ | |
| claude-ecom | none | sources/claude-ecom/ | raw/claude-ecom/ | graphs/claude-ecom/ | Companion page rule applies |
| claude-seo | [[claude-seo]] | sources/claude-seo/ | raw/claude-seo/ | graphs/claude-seo/ | |
| claw-code | none | sources/claw-code/ | raw/claw-code/ | graphs/claw-code/ | Companion page rule applies |
| clawpier | [[clawpier]] | sources/clawpier/ | raw/clawpier/ | graphs/clawpier/ | Desktop GUI |
| cockpit-podman | [[cockpit-podman]] | sources/cockpit-podman/ | raw/cockpit-podman/ | graphs/cockpit-podman/ | Web UI plugin |
| communitytools | [[communitytools]] | sources/communitytools/ | raw/communitytools/ | graphs/communitytools/ | |
| coreos-assembler | none | sources/coreos-assembler/ | raw/coreos-assembler/ | graphs/coreos-assembler/ | Companion page rule applies |
| crun-vm | [[crun-vm]] | sources/crun-vm/ | raw/crun-vm/ | graphs/crun-vm/ | |
| defending-code-reference-harness | [[defending-code-reference-harness]] | sources/defending-code-reference-harness/ | raw/defending-code-reference-harness/ | graphs/defending-code-reference-harness/ | |
| digital-marketing-pro | none | sources/digital-marketing-pro/ | raw/digital-marketing-pro/ | graphs/digital-marketing-pro/ | Companion page rule applies |
| drawio-skill | [[drawio-skill]] | sources/drawio-skill/ | raw/drawio-skill/ | graphs/drawio-skill/ | |
| extension-podman-quadlet | none | sources/extension-podman-quadlet/ | raw/extension-podman-quadlet/ | graphs/extension-podman-quadlet/ | Companion page rule applies |
| fedora-coreos-config | [[fedora-coreos-config]] | sources/fedora-coreos-config/ | raw/fedora-coreos-config/ | graphs/fedora-coreos-config/ | |
| free-claude-code | [[free-claude-code]] | sources/free-claude-code/ | raw/free-claude-code/ | graphs/free-claude-code/ | Free tier MCP wrapper |
| goclaw | [[goclaw]] | sources/goclaw/ | raw/goclaw/ | graphs/goclaw/ | Go MCP gateway |
| gogs | [[gogs]] | sources/gogs/ | raw/gogs/ | graphs/gogs/ | Git server |
| grafana | none | sources/grafana/ | raw/grafana/ | graphs/grafana/ | Companion page rule applies |
| graphify | [[graphify]] | sources/graphify/ | raw/graphify/ | graphs/graphify/ | |
| headroom | none | sources/headroom/ | raw/headroom/ | graphs/headroom/ | Companion page rule applies |
| hermes-agent | [[hermes-agent]] | sources/hermes-agent/ | raw/hermes-agent/ | graphs/hermes-agent/ | MCP hub with 49 tools |
| hermes-agent-acp-skill | [[hermes-agent-acp-skill]] | sources/hermes-agent-acp-skill/ | raw/hermes-agent-acp-skill/ | graphs/hermes-agent-acp-skill/ | |
| hermes-agent-docker | [[hermes-agent-docker]] | sources/hermes-agent-docker/ | raw/hermes-agent-docker/ | graphs/hermes-agent-docker/ | |
| hermes-agent-template | [[hermes-agent-template]] | sources/hermes-agent-template/ | raw/hermes-agent-template/ | graphs/hermes-agent-template/ | |
| hermes-autonomous-server | [[hermes-autonomous-server]] | sources/hermes-autonomous-server/ | raw/hermes-autonomous-server/ | graphs/hermes-autonomous-server/ | |
| hermes-bus | [[hermes-bus]] | sources/hermes-bus/ | raw/hermes-bus/ | graphs/hermes-bus/ | |
| hermes-incident-commander | [[hermes-incident-commander]] | sources/hermes-incident-commander/ | raw/hermes-incident-commander/ | graphs/hermes-incident-commander/ | |
| hermes-optimization-guide | [[hermes-optimization-guide]] | sources/hermes-optimization-guide/ | raw/hermes-optimization-guide/ | graphs/hermes-optimization-guide/ | |
| hermes-plugins | [[hermes-plugins]] | sources/hermes-plugins/ | raw/hermes-plugins/ | graphs/hermes-plugins/ | |
| hermes-profiles | [[hermes-profiles]] | sources/hermes-profiles/ | raw/hermes-profiles/ | graphs/hermes-profiles/ | |
| hermes-startup-architect | [[hermes-startup-architect]] | sources/hermes-startup-architect/ | raw/hermes-startup-architect/ | graphs/hermes-startup-architect/ | |
| hermes-suite | [[hermes-suite]] | sources/hermes-suite/ | raw/hermes-suite/ | graphs/hermes-suite/ | |
| hermes-workspace | [[hermes-workspace]] | sources/hermes-workspace/ | raw/hermes-workspace/ | graphs/hermes-workspace/ | MCP hub server |
| hermzner | [[hermzner]] | sources/hermzner/ | raw/hermzner/ | graphs/hermzner/ | Hetzner automations |
| hexstrike-ai | [[hexstrike-ai]] | sources/hexstrike-ai/ | raw/hexstrike-ai/ | graphs/hexstrike-ai/ | Security framework |
| infinite-brain-os | none | sources/infinite-brain-os/ | raw/infinite-brain-os/ | graphs/infinite-brain-os/ | Companion page rule applies |
| k3s | none | sources/k3s/ | raw/k3s/ | graphs/k3s/ | Companion page rule applies |
| kali-pentest | [[kali-pentest]] | sources/kali-pentest/ | raw/kali-pentest/ | graphs/kali-pentest/ | |
| llmtrim | [[llmtrim]] | sources/llmtrim/ | raw/llmtrim/ | graphs/llmtrim/ | Tool compressor |
| materia | [[materia]] | sources/materia/ | raw/materia/ | graphs/materia/ | Agent framework |
| mission-control | [[mission-control]] | sources/mission-control/ | raw/mission-control/ | graphs/mission-control/ | MCP audit server |
| n8n | [[n8n]] | sources/n8n/ | raw/n8n/ | graphs/n8n/ | Workflow automation |
| n8n-mcp | [[n8n-mcp]] | sources/n8n-mcp/ | raw/n8n-mcp/ | graphs/n8n-mcp/ | MCP node indexer |
| n8n-skills | [[n8n-skills]] | sources/n8n-skills/ | raw/n8n-skills/ | graphs/n8n-skills/ | Workflow skills |
| n8n-workflows | [[n8n-workflows]] | sources/n8n-workflows/ | raw/n8n-workflows/ | graphs/n8n-workflows/ | Workflow catalog |
| n8nworkflows.xyz | none | sources/n8nworkflows.xyz/ | raw/n8nworkflows.xyz/ | graphs/n8nworkflows.xyz/ | Companion page rule applies |
| nanobot | [[nanobot]] | sources/nanobot/ | raw/nanobot/ | graphs/nanobot/ | Agent framework |
| netdata | none | sources/netdata/ | raw/netdata/ | graphs/netdata/ | Companion page rule applies |
| nix-podman-stacks | [[nix-podman-stacks]] | sources/nix-podman-stacks/ | raw/nix-podman-stacks/ | graphs/nix-podman-stacks/ | NixOS configs |
| nix.dev | [[nix.dev]] | sources/nix.dev/ | raw/nix.dev/ | graphs/nix.dev/ | |
| nyxstrike | [[nyxstrike]] | sources/nyxstrike/ | raw/nyxstrike/ | graphs/nyxstrike/ | Security orchestration |
| obsidian-skills | [[obsidian-skills]] | sources/obsidian-skills/ | raw/obsidian-skills/ | graphs/obsidian-skills/ | |
| oh-my-hermes | [[oh-my-hermes]] | sources/oh-my-hermes/ | raw/oh-my-hermes/ | graphs/oh-my-hermes/ | OMH plugin system |
| oh-my-openagent | [[oh-my-openagent]] | sources/oh-my-openagent/ | raw/oh-my-openagent/ | graphs/oh-my-openagent/ | |
| oh-my-opencode-slim | [[oh-my-opencode-slim]] | sources/oh-my-opencode-slim/ | raw/oh-my-opencode-slim/ | graphs/oh-my-opencode-slim/ | |
| oh-my-pi | [[oh-my-pi]] | sources/oh-my-pi/ | raw/oh-my-pi/ | graphs/oh-my-pi/ | Fork of pi-mono |
| open-design | [[open-design]] | sources/open-design/ | raw/open-design/ | graphs/open-design/ | |
| openai-skills | [[openai-skills]] | sources/openai-skills/ | raw/openai-skills/ | graphs/openai-skills/ | |
| openclaw | [[openclaw]] | sources/openclaw/ | raw/openclaw/ | graphs/openclaw/ | Rust agent platform |
| openclaw-container | [[openclaw-container]] | sources/openclaw-container/ | raw/openclaw-container/ | graphs/openclaw-container/ | |
| openclaw-plugin-claude-code | [[openclaw-plugin-claude-code]] | sources/openclaw-plugin-claude-code/ | raw/openclaw-plugin-claude-code/ | graphs/openclaw-plugin-claude-code/ | |
| opencode | [[opencode]] | sources/opencode/ | raw/opencode/ | graphs/opencode/ | AI coding agent |
| opencode-hermes-multiagent | [[opencode-hermes-multiagent]] | sources/opencode-hermes-multiagent/ | raw/opencode-hermes-multiagent/ | graphs/opencode-hermes-multiagent/ | |
| outreachmagic | [[outreachmagic]] | sources/outreachmagic/ | raw/outreachmagic/ | graphs/outreachmagic/ | |
| pi | [[pi]] | sources/pi/ | raw/pi/ | graphs/pi/ | TypeScript agent harness |
| podlet | [[podlet]] | sources/podlet/ | raw/podlet/ | graphs/podlet/ | Quadlet generator |
| podman | [[podman]] | sources/podman/ | raw/podman/ | graphs/podman/ | Container engine |
| podman-compose | [[podman-compose]] | sources/podman-compose/ | raw/podman-compose/ | graphs/podman-compose/ | |
| podman-quadlet | none | sources/podman-quadlet/ | raw/podman-quadlet/ | graphs/podman-quadlet/ | Companion page rule applies |
| prometheus | none | sources/prometheus/ | raw/prometheus/ | graphs/prometheus/ | Companion page rule applies |
| pydantic-ai-skills | [[pydantic-ai-skills]] | sources/pydantic-ai-skills/ | raw/pydantic-ai-skills/ | graphs/pydantic-ai-skills/ | |
| quadit | none | sources/quadit/ | raw/quadit/ | graphs/quadit/ | Companion page rule applies |
| quadlet-lsp | none | sources/quadlet-lsp/ | raw/quadlet-lsp/ | graphs/quadlet-lsp/ | Companion page rule applies |
| quadlet-nix | none | sources/quadlet-nix/ | raw/quadlet-nix/ | graphs/quadlet-nix/ | Companion page rule applies |
| reverse-skill | [[reverse-skill]] | sources/reverse-skill/ | raw/reverse-skill/ | graphs/reverse-skill/ | |
| sablier | [[sablier]] | sources/sablier/ | raw/sablier/ | graphs/sablier/ | Time-based access |
| sec-af | [[sec-af]] | sources/sec-af/ | raw/sec-af/ | graphs/sec-af/ | Security agent |
| secureblue | none | sources/secureblue/ | raw/secureblue/ | graphs/secureblue/ | Companion page rule applies |
| shannon | none | sources/shannon/ | raw/shannon/ | graphs/shannon/ | Companion page rule applies |
| skills | [[skills]] | sources/skills/ | raw/skills/ | graphs/skills/ | |
| slavinga-skills | [[slavinga-skills]] | sources/slavinga-skills/ | raw/slavinga-skills/ | graphs/slavinga-skills/ | |
| tank-agent-os | none | sources/tank-agent-os/ | raw/tank-agent-os/ | graphs/tank-agent-os/ | Companion page rule applies |
| tank-os | [[tank-os]] | sources/tank-os/ | raw/tank-os/ | graphs/tank-os/ | bootc image |
| turnstone | none | sources/turnstone/ | raw/turnstone/ | graphs/turnstone/ | Companion page rule applies |
| x-article-publisher-skill | none | sources/x-article-publisher-skill/ | raw/x-article-publisher-skill/ | graphs/x-article-publisher-skill/ | Companion page rule applies |
| zot | [[zot]] | sources/zot/ | raw/zot/ | graphs/zot/ | Go coding agent |

**Key:** `none` = no dedicated wiki page yet, use companion page rule (see `sources/<repo>/` for documentation placeholder)
