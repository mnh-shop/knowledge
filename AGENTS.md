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

- `sources/` — full cloned GitHub repositories (172 repos total)
- `raw/` — Repomix XML exports. Generated automatically by scripts/actualize-repos.py; never edit manually. (sources/ and graphs/ remain fully read-only; graphs/ is currently unused/empty.)
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
sources/       full cloned GitHub repositories (gitignored, 172 repos)
raw/           Repomix XML generated from repositories (172 repos)
graphs/        CodeGraph output generated from repositories
wiki/          generated documentation per repository
assets/        reusable concrete things extracted from repos
  INDEX.md            master catalog
  agent-references/   20 agent reference profiles for specialist swarms
  hermes-profiles/    40 Hermes Agent role profiles
  deployment/         10 quadlet guides + 47 deployable quadlet files
  skills/             67 categorized skill directories (867 files)
  n8n-workflows/      sweep catalog of 9,655 workflows with tool breakdown
  mcp-servers/        4 MCP server references
  acp-agents/         2 ACP agent references
  api-clients/        1 API client reference
domains/       cross-repo concept knowledge
integrations/  concrete system-to-system integration knowledge
```

## Wiki verification rule

**All wiki entries ARE verified against source.** Every wiki page carries `verification_date: 2026-07-12` and `verified_by: codegraph-verify` in its frontmatter. Each source repo also has a dedicated `<repo>.codegraph-verify.md` companion page with 5-8 evidence-backed claims citing specific source file paths and line numbers.

This prevents hallucinated content. When in doubt, read the companion verify page first, then use `codebase-memory-mcp_search_graph` with `project: "Users-admin-repos-knowledge-sources-<name>"` for deeper investigation.

## Agent knowledge lookup

All agents MUST use this knowledge base as the primary source for service facts. Do NOT dispatch @explorer for service information — the canonical source repositories are already indexed here.

| What | How to use |
|---|---|
| **Canonical source code** | `knowledge/sources/<name>/` — indexed by codebase-memory-mcp. Use `codebase-memory-mcp_search_graph` / `codebase-memory-mcp_get_code_snippet` with `project: "Users-admin-repos-knowledge-sources-<name>"` |
| **Wiki summaries** | `knowledge/wiki/<name>.md` — LLM-synthesized page per repo. Read this FIRST before graph search. |
| **Domain knowledge** | `knowledge/domains/` — cross-cutting concepts: architecture, API, MCP, ACP, deployment, integration patterns. |
| **Deployable assets** | `knowledge/assets/` — skills, n8n-workflows, MCP servers, profiles, deployment templates. |
| **Repomix XML extracts** | `knowledge/raw/<name>/repomix-output.xml` — complete codebase summaries; use only when graph search and wiki are insufficient. |
| **Verification pages** | `knowledge/wiki/<name>.codegraph-verify.md` — evidence-backed claim verification per source repo. |
| **Integration stacks** | `knowledge/integrations/` — concrete cross-system deployment docs (Hermes×OpenClaw×n8n×AgentField). |

Project names in codebase-memory-mcp are the absolute repo path with `/` replaced by `-` (e.g. `Users-admin-repos-knowledge-sources-hermes-agent`). To find the exact name, run `codebase-memory-mcp_list_projects` and grep for the repo name.

**Rule of thumb:** Read the wiki page first, then use the codebase-memory-mcp tools above (e.g. `codebase-memory-mcp_search_graph`) on the source repo for specifics. Do NOT dispatch @explorer for service facts — use the knowledge base.

## Repository index

The table below tracks all indexed repositories and their corresponding vault locations. Generated from actual filesystem state — 132 sources, 146 wikis, 141 codegraph-verify pages, 132 raw exports, 132 codegraph indexes.

| Repo | Wiki | Source | Raw | Graph | Notes |
|------|------|--------|-----|-------|-------|
| 1claw-hermes | [[1claw-hermes]] | sources/1claw-hermes/ | raw/1claw-hermes/ | graphs/1claw-hermes/ |  |
| 9router | [[9router]] | sources/9router/ | raw/9router/ | graphs/9router/ |  |
| ASMR-BBQ.SKILLS | [[ASMR-BBQ.SKILLS]] | sources/ASMR-BBQ.SKILLS/ | raw/ASMR-BBQ.SKILLS/ | graphs/ASMR-BBQ.SKILLS/ |  |
| Agent-Reach | [[Agent-Reach]] | sources/Agent-Reach/ | raw/Agent-Reach/ | graphs/Agent-Reach/ |  |
| AgentDock | [[AgentDock]] | sources/AgentDock/ | raw/AgentDock/ | graphs/AgentDock/ |  |
| AionUi | [[AionUi]] | sources/AionUi/ | raw/AionUi/ | graphs/AionUi/ |  |
| Android-Pentesting-Checklist | [[Android-Pentesting-Checklist]] | sources/Android-Pentesting-Checklist/ | raw/Android-Pentesting-Checklist/ | graphs/Android-Pentesting-Checklist/ |  |
| Anthropic-Cybersecurity-Skills | [[Anthropic-Cybersecurity-Skills]] | sources/Anthropic-Cybersecurity-Skills/ | raw/Anthropic-Cybersecurity-Skills/ | graphs/Anthropic-Cybersecurity-Skills/ |  |
| Claude-OSINT | [[Claude-OSINT]] | sources/Claude-OSINT/ | raw/Claude-OSINT/ | graphs/Claude-OSINT/ |  |
| Claude-Red | [[Claude-Red]] | sources/Claude-Red/ | raw/Claude-Red/ | graphs/Claude-Red/ |  |
| CyberStrikeAI | [[CyberStrikeAI]] | sources/CyberStrikeAI/ | raw/CyberStrikeAI/ | graphs/CyberStrikeAI/ |  |
| DESIGN-OPS | [[DESIGN-OPS]] | sources/DESIGN-OPS/ | raw/DESIGN-OPS/ | graphs/DESIGN-OPS/ |  |
| ECC | [[ECC]] | sources/ECC/ | raw/ECC/ | graphs/ECC/ |  |
| Electronic_Music_Mentor | [[Electronic_Music_Mentor]] | sources/Electronic_Music_Mentor/ | raw/Electronic_Music_Mentor/ | graphs/Electronic_Music_Mentor/ |  |
| Hermes-caduceus | [[Hermes-caduceus]] | sources/Hermes-caduceus/ | raw/Hermes-caduceus/ | graphs/Hermes-caduceus/ |  |
| MiniMax-AI-skills | [[MiniMax-AI-skills]] | sources/MiniMax-AI-skills/ | raw/MiniMax-AI-skills/ | graphs/MiniMax-AI-skills/ |  |
| Mnemosyne | [[Mnemosyne]] | sources/Mnemosyne/ | raw/Mnemosyne/ | graphs/Mnemosyne/ |  |
| MoneyPrinterV2 | [[MoneyPrinterV2]] | sources/MoneyPrinterV2/ | raw/MoneyPrinterV2/ | graphs/MoneyPrinterV2/ |  |
| NemoClaw | [[NemoClaw]] | sources/NemoClaw/ | raw/NemoClaw/ | graphs/NemoClaw/ |  |
| OneWave-claude-skills | [[OneWave-claude-skills]] | sources/OneWave-claude-skills/ | raw/OneWave-claude-skills/ | graphs/OneWave-claude-skills/ |  |
| OpenShell | [[OpenShell]] | sources/OpenShell/ | raw/OpenShell/ | graphs/OpenShell/ |  |
| OpenViking | [[OpenViking]] | sources/OpenViking/ | raw/OpenViking/ | graphs/OpenViking/ |  |
| SWE-AF | [[SWE-AF]] | sources/SWE-AF/ | raw/SWE-AF/ | graphs/SWE-AF/ |  |
| SecOpsAgentKit | [[SecOpsAgentKit]] | sources/SecOpsAgentKit/ | raw/SecOpsAgentKit/ | graphs/SecOpsAgentKit/ |  |
| SecuritySkills | [[SecuritySkills]] | sources/SecuritySkills/ | raw/SecuritySkills/ | graphs/SecuritySkills/ |  |
| Understand-Anything | [[Understand-Anything]] | sources/Understand-Anything/ | raw/Understand-Anything/ | graphs/Understand-Anything/ |  |
| abvx-agent-skills | [[abvx-agent-skills]] | sources/abvx-agent-skills/ | raw/abvx-agent-skills/ | graphs/abvx-agent-skills/ |  |
| af-deep-research | [[af-deep-research]] | sources/af-deep-research/ | raw/af-deep-research/ | graphs/af-deep-research/ |  |
| af-reactive-atlas-mongodb | [[af-reactive-atlas-mongodb]] | sources/af-reactive-atlas-mongodb/ | raw/af-reactive-atlas-mongodb/ | graphs/af-reactive-atlas-mongodb/ |  |
| agent-rules-books | [[agent-rules-books]] | sources/agent-rules-books/ | raw/agent-rules-books/ | graphs/agent-rules-books/ |  |
| agentfield | [[agentfield]] | sources/agentfield/ | raw/agentfield/ | graphs/agentfield/ |  |
| agentic-awesome-skills | [[agentic-awesome-skills]] | sources/agentic-awesome-skills/ | raw/agentic-awesome-skills/ | graphs/agentic-awesome-skills/ |  |
| agentmax-os | [[agentmax-os]] | sources/agentmax-os/ | raw/agentmax-os/ | graphs/agentmax-os/ |  |
| ai-agency-claude | [[ai-agency-claude]] | sources/ai-agency-claude/ | raw/ai-agency-claude/ | graphs/ai-agency-claude/ |  |
| ai-marketing-claude-code-skills | [[ai-marketing-claude-code-skills]] | sources/ai-marketing-claude-code-skills/ | raw/ai-marketing-claude-code-skills/ | graphs/ai-marketing-claude-code-skills/ |  |
| ai-sales-team-claude | [[ai-sales-team-claude]] | sources/ai-sales-team-claude/ | raw/ai-sales-team-claude/ | graphs/ai-sales-team-claude/ |  |
| ai-toolkit | [[ai-toolkit]] | sources/ai-toolkit/ | raw/ai-toolkit/ | graphs/ai-toolkit/ |  |
| ai-youtube-shorts-automation | [[ai-youtube-shorts-automation]] | sources/ai-youtube-shorts-automation/ | raw/ai-youtube-shorts-automation/ | graphs/ai-youtube-shorts-automation/ |  |
| alphaclaw | [[alphaclaw]] | sources/alphaclaw/ | raw/alphaclaw/ | graphs/alphaclaw/ |  |
| anthropics-skills | [[anthropics-skills]] | sources/anthropics-skills/ | raw/anthropics-skills/ | graphs/anthropics-skills/ |  |
| arc-kit | [[arc-kit]] | sources/arc-kit/ | raw/arc-kit/ | graphs/arc-kit/ |  |
| awesome-n8n-templates | [[awesome-n8n-templates]] | sources/awesome-n8n-templates/ | raw/awesome-n8n-templates/ | graphs/awesome-n8n-templates/ |  |
| awesome-openclaw-skills | [[awesome-openclaw-skills]] | sources/awesome-openclaw-skills/ | raw/awesome-openclaw-skills/ | graphs/awesome-openclaw-skills/ |  |
| awesome-openclaw-usecases | [[awesome-openclaw-usecases]] | sources/awesome-openclaw-usecases/ | raw/awesome-openclaw-usecases/ | graphs/awesome-openclaw-usecases/ |  |
| bootc | [[bootc]] | sources/bootc/ | raw/bootc/ | graphs/bootc/ |  |
| bradautomates-claude-video | [[bradautomates-claude-video]] | sources/bradautomates-claude-video/ | raw/bradautomates-claude-video/ | graphs/bradautomates-claude-video/ |  |
| brand-voice | [[brand-voice]] | sources/brand-voice/ | raw/brand-voice/ | graphs/brand-voice/ |  |
| brandkit-mcp | [[brandkit-mcp]] | sources/brandkit-mcp/ | raw/brandkit-mcp/ | graphs/brandkit-mcp/ |  |
| buildah | [[buildah]] | sources/buildah/ | raw/buildah/ | graphs/buildah/ |  |
| camofox-browser | [[camofox-browser]] | sources/camofox-browser/ | raw/camofox-browser/ | graphs/camofox-browser/ |  |
| claude-ads | [[claude-ads]] | sources/claude-ads/ | raw/claude-ads/ | graphs/claude-ads/ |  |
| claude-ai-music-skills | [[claude-ai-music-skills]] | sources/claude-ai-music-skills/ | raw/claude-ai-music-skills/ | graphs/claude-ai-music-skills/ |  |
| claude-code-plugins-plus-skills | [[claude-code-plugins-plus-skills]] | sources/claude-code-plugins-plus-skills/ | raw/claude-code-plugins-plus-skills/ | graphs/claude-code-plugins-plus-skills/ |  |
| claude-collider | [[claude-collider]] | sources/claude-collider/ | raw/claude-collider/ | graphs/claude-collider/ |  |
| claude-ecom | [[claude-ecom]] | sources/claude-ecom/ | raw/claude-ecom/ | graphs/claude-ecom/ |  |
| claude-plugin-marketplace | [[claude-plugin-marketplace]] | sources/claude-plugin-marketplace/ | raw/claude-plugin-marketplace/ | graphs/claude-plugin-marketplace/ |  |
| claude-seo | [[claude-seo]] | sources/claude-seo/ | raw/claude-seo/ | graphs/claude-seo/ |  |
| claude-skills-journalism | [[claude-skills-journalism]] | sources/claude-skills-journalism/ | raw/claude-skills-journalism/ | graphs/claude-skills-journalism/ |  |
| claw-code | [[claw-code]] | sources/claw-code/ | raw/claw-code/ | graphs/claw-code/ |  |
| clawpier | [[clawpier]] | sources/clawpier/ | raw/clawpier/ | graphs/clawpier/ |  |
| cockpit-podman | [[cockpit-podman]] | sources/cockpit-podman/ | raw/cockpit-podman/ | graphs/cockpit-podman/ |  |
| codexQIYU-image-workflow | [[codexQIYU-image-workflow]] | sources/codexQIYU-image-workflow/ | raw/codexQIYU-image-workflow/ | graphs/codexQIYU-image-workflow/ |  |
| codiverse-paper | [[codiverse-paper]] | sources/codiverse-paper/ | raw/codiverse-paper/ | graphs/codiverse-paper/ |  |
| communitytools | [[communitytools]] | sources/communitytools/ | raw/communitytools/ | graphs/communitytools/ |  |
| coreos-assembler | [[coreos-assembler]] | sources/coreos-assembler/ | raw/coreos-assembler/ | graphs/coreos-assembler/ |  |
| crun-vm | [[crun-vm]] | sources/crun-vm/ | raw/crun-vm/ | graphs/crun-vm/ |  |
| ctf-skills | [[ctf-skills]] | sources/ctf-skills/ | raw/ctf-skills/ | graphs/ctf-skills/ |  |
| cti-expert | [[cti-expert]] | sources/cti-expert/ | raw/cti-expert/ | graphs/cti-expert/ |  |
| davinci-resolve-mcp | [[davinci-resolve-mcp]] | sources/davinci-resolve-mcp/ | raw/davinci-resolve-mcp/ | graphs/davinci-resolve-mcp/ |  |
| deepseek-harness | [[deepseek-harness]] | sources/deepseek-harness/ | raw/deepseek-harness/ | graphs/deepseek-harness/ |  |
| defending-code-reference-harness | [[defending-code-reference-harness]] | sources/defending-code-reference-harness/ | raw/defending-code-reference-harness/ | graphs/defending-code-reference-harness/ |  |
| digital-marketing-pro | [[digital-marketing-pro]] | sources/digital-marketing-pro/ | raw/digital-marketing-pro/ | graphs/digital-marketing-pro/ |  |
| docker-netbird | [[docker-netbird]] | sources/docker-netbird/ | raw/docker-netbird/ | graphs/docker-netbird/ |  |
| drawio-skill | [[drawio-skill]] | sources/drawio-skill/ | raw/drawio-skill/ | graphs/drawio-skill/ |  |
| extension-podman-quadlet | [[extension-podman-quadlet]] | sources/extension-podman-quadlet/ | raw/extension-podman-quadlet/ | graphs/extension-podman-quadlet/ |  |
| fedora-coreos-config | [[fedora-coreos-config]] | sources/fedora-coreos-config/ | raw/fedora-coreos-config/ | graphs/fedora-coreos-config/ |  |
| firecracker | [[firecracker]] | sources/firecracker/ | raw/firecracker/ | graphs/firecracker/ |  |
| floci | [[floci]] | sources/floci/ | raw/floci/ | graphs/floci/ |  |
| free-claude-code | [[free-claude-code]] | sources/free-claude-code/ | raw/free-claude-code/ | graphs/free-claude-code/ |  |
| freellmapi | [[freellmapi]] | sources/freellmapi/ | raw/freellmapi/ | graphs/freellmapi/ |  |
| gemini-youtube-automation | [[gemini-youtube-automation]] | sources/gemini-youtube-automation/ | raw/gemini-youtube-automation/ | graphs/gemini-youtube-automation/ |  |
| generative-media-skills | [[generative-media-skills]] | sources/generative-media-skills/ | raw/generative-media-skills/ | graphs/generative-media-skills/ |  |
| goclaw | [[goclaw]] | sources/goclaw/ | raw/goclaw/ | graphs/goclaw/ |  |
| goclaw-docs | [[goclaw-docs]] | sources/goclaw-docs/ | raw/goclaw-docs/ | graphs/goclaw-docs/ |  |
| gogs | [[gogs]] | sources/gogs/ | raw/gogs/ | graphs/gogs/ |  |
| grafana | [[grafana]] | sources/grafana/ | raw/grafana/ | graphs/grafana/ |  |
| graphify | [[graphify]] | sources/graphify/ | raw/graphify/ | graphs/graphify/ |  |
| gtm-agents | [[gtm-agents]] | sources/gtm-agents/ | raw/gtm-agents/ | graphs/gtm-agents/ |  |
| haunchen-n8n-skills | [[haunchen-n8n-skills]] | sources/haunchen-n8n-skills/ | raw/haunchen-n8n-skills/ | graphs/haunchen-n8n-skills/ |  |
| headroom | [[headroom]] | sources/headroom/ | raw/headroom/ | graphs/headroom/ |  |
| herdr | [[herdr]] | sources/herdr/ | raw/herdr/ | graphs/herdr/ |  |
| hermes-agent | [[hermes-agent]] | sources/hermes-agent/ | raw/hermes-agent/ | graphs/hermes-agent/ |  |
| hermes-agent-docker | [[hermes-agent-docker]] | sources/hermes-agent-docker/ | raw/hermes-agent-docker/ | graphs/hermes-agent-docker/ |  |
| hermes-agent-template | [[hermes-agent-template]] | sources/hermes-agent-template/ | raw/hermes-agent-template/ | graphs/hermes-agent-template/ |  |
| hermes-autonomous-server | [[hermes-autonomous-server]] | sources/hermes-autonomous-server/ | raw/hermes-autonomous-server/ | graphs/hermes-autonomous-server/ |  |
| hermes-bus | [[hermes-bus]] | sources/hermes-bus/ | raw/hermes-bus/ | graphs/hermes-bus/ |  |
| hermes-incident-commander | [[hermes-incident-commander]] | sources/hermes-incident-commander/ | raw/hermes-incident-commander/ | graphs/hermes-incident-commander/ |  |
| hermes-optimization-guide | [[hermes-optimization-guide]] | sources/hermes-optimization-guide/ | raw/hermes-optimization-guide/ | graphs/hermes-optimization-guide/ |  |
| hermes-plugins | [[hermes-plugins]] | sources/hermes-plugins/ | raw/hermes-plugins/ | graphs/hermes-plugins/ |  |
| hermes-profiles | [[hermes-profiles]] | sources/hermes-profiles/ | raw/hermes-profiles/ | graphs/hermes-profiles/ |  |
| hermes-startup-architect | [[hermes-startup-architect]] | sources/hermes-startup-architect/ | raw/hermes-startup-architect/ | graphs/hermes-startup-architect/ |  |
| hermes-suite | [[hermes-suite]] | sources/hermes-suite/ | raw/hermes-suite/ | graphs/hermes-suite/ |  |
| hermes-workspace | [[hermes-workspace]] | sources/hermes-workspace/ | raw/hermes-workspace/ | graphs/hermes-workspace/ |  |
| hyperframes | [[hyperframes]] | sources/hyperframes/ | raw/hyperframes/ | graphs/hyperframes/ |  |
| infinite-brain-os | [[infinite-brain-os]] | sources/infinite-brain-os/ | raw/infinite-brain-os/ | graphs/infinite-brain-os/ |  |
| k3s | [[k3s]] | sources/k3s/ | raw/k3s/ | graphs/k3s/ |  |
| kalfa | [[kalfa]] | sources/kalfa/ | raw/kalfa/ | graphs/kalfa/ |  |
| kali-pentest | [[kali-pentest]] | sources/kali-pentest/ | raw/kali-pentest/ | graphs/kali-pentest/ |  |
| knowledge-work-plugins | [[knowledge-work-plugins]] | sources/knowledge-work-plugins/ | raw/knowledge-work-plugins/ | graphs/knowledge-work-plugins/ |  |
| lightrag | [[lightrag]] | sources/lightrag/ | raw/lightrag/ | graphs/lightrag/ |  |
| live-coding-music-mcp | [[live-coding-music-mcp]] | sources/live-coding-music-mcp/ | raw/live-coding-music-mcp/ | graphs/live-coding-music-mcp/ |  |
| llmtrim | [[llmtrim]] | sources/llmtrim/ | raw/llmtrim/ | graphs/llmtrim/ |  |
| marketingskills | [[marketingskills]] | sources/marketingskills/ | raw/marketingskills/ | graphs/marketingskills/ |  |
| materia | [[materia]] | sources/materia/ | raw/materia/ | graphs/materia/ |  |
| mcp-netbird | [[mcp-netbird]] | sources/mcp-netbird/ | raw/mcp-netbird/ | graphs/mcp-netbird/ |  |
| n8n-io-skills | [[n8n-io-skills]] | sources/n8n-io-skills/ | raw/n8n-io-skills/ | graphs/n8n-io-skills/ |  |
| n8n-mcp | [[n8n-mcp]] | sources/n8n-mcp/ | raw/n8n-mcp/ | graphs/n8n-mcp/ |  |
| n8n-skills | [[n8n-skills]] | sources/n8n-skills/ | raw/n8n-skills/ | graphs/n8n-skills/ |  |
| n8n-workflows | [[n8n-workflows]] | sources/n8n-workflows/ | raw/n8n-workflows/ | graphs/n8n-workflows/ |  |
| n8nworkflows.xyz | [[n8nworkflows.xyz]] | sources/n8nworkflows.xyz/ | raw/n8nworkflows.xyz/ | graphs/n8nworkflows.xyz/ |  |
| nanobot | [[nanobot]] | sources/nanobot/ | raw/nanobot/ | graphs/nanobot/ |  |
| netbird | [[netbird]] | sources/netbird/ | raw/netbird/ | graphs/netbird/ |  |
| netdata | [[netdata]] | sources/netdata/ | raw/netdata/ | graphs/netdata/ |  |
| nix-podman-stacks | [[nix-podman-stacks]] | sources/nix-podman-stacks/ | raw/nix-podman-stacks/ | graphs/nix-podman-stacks/ |  |
| nix.dev | [[nix.dev]] | sources/nix.dev/ | raw/nix.dev/ | graphs/nix.dev/ |  |
| nyxstrike | [[nyxstrike]] | sources/nyxstrike/ | raw/nyxstrike/ | graphs/nyxstrike/ |  |
| obsidian-skills | [[obsidian-skills]] | sources/obsidian-skills/ | raw/obsidian-skills/ | graphs/obsidian-skills/ |  |
| oh-my-hermes | [[oh-my-hermes]] | sources/oh-my-hermes/ | raw/oh-my-hermes/ | graphs/oh-my-hermes/ |  |
| oh-my-openagent | [[oh-my-openagent]] | sources/oh-my-openagent/ | raw/oh-my-openagent/ | graphs/oh-my-openagent/ |  |
| oh-my-pi | [[oh-my-pi]] | sources/oh-my-pi/ | raw/oh-my-pi/ | graphs/oh-my-pi/ |  |
| omagents | [[omagents]] | sources/omagents/ | raw/omagents/ | graphs/omagents/ |  |
| open-design | [[open-design]] | sources/open-design/ | raw/open-design/ | graphs/open-design/ |  |
| openai-skills | [[openai-skills]] | sources/openai-skills/ | raw/openai-skills/ | graphs/openai-skills/ |  |
| openclaw | [[openclaw]] | sources/openclaw/ | raw/openclaw/ | graphs/openclaw/ |  |
| openclaw-container | [[openclaw-container]] | sources/openclaw-container/ | raw/openclaw-container/ | graphs/openclaw-container/ |  |
| openclaw-plugin-claude-code | [[openclaw-plugin-claude-code]] | sources/openclaw-plugin-claude-code/ | raw/openclaw-plugin-claude-code/ | graphs/openclaw-plugin-claude-code/ |  |
| opencode | [[opencode]] | sources/opencode/ | raw/opencode/ | graphs/opencode/ |  |
| opencode-hermes-multiagent | [[opencode-hermes-multiagent]] | sources/opencode-hermes-multiagent/ | raw/opencode-hermes-multiagent/ | graphs/opencode-hermes-multiagent/ |  |
| osint-agent-skills | [[osint-agent-skills]] | sources/osint-agent-skills/ | raw/osint-agent-skills/ | graphs/osint-agent-skills/ |  |
| outreachmagic | [[outreachmagic]] | sources/outreachmagic/ | raw/outreachmagic/ | graphs/outreachmagic/ |  |
| panzer-os | [[panzer-os]] | sources/panzer-os/ | raw/panzer-os/ | graphs/panzer-os/ |  |
| panzer-os-kimi | [[panzer-os-kimi]] | sources/panzer-os-kimi/ | raw/panzer-os-kimi/ | graphs/panzer-os-kimi/ |  |
| panzer-os-kimi-wt | [[panzer-os-kimi-wt]] | sources/panzer-os-kimi-wt/ | raw/panzer-os-kimi-wt/ | graphs/panzer-os-kimi-wt/ |  |
| panzer-os-livevps-beta | [[panzer-os-livevps-beta]] | sources/panzer-os-livevps-beta/ | raw/panzer-os-livevps-beta/ | graphs/panzer-os-livevps-beta/ |  |
| persona-generator | [[persona-generator]] | sources/persona-generator/ | raw/persona-generator/ | graphs/persona-generator/ |  |
| pi | [[pi]] | sources/pi/ | raw/pi/ | graphs/pi/ |  |
| plugins-openai | [[plugins-openai]] | sources/plugins-openai/ | raw/plugins-openai/ | graphs/plugins-openai/ |  |
| podlet | [[podlet]] | sources/podlet/ | raw/podlet/ | graphs/podlet/ |  |
| podman | [[podman]] | sources/podman/ | raw/podman/ | graphs/podman/ |  |
| podman-compose | [[podman-compose]] | sources/podman-compose/ | raw/podman-compose/ | graphs/podman-compose/ |  |
| podman-quadlet | [[podman-quadlet]] | sources/podman-quadlet/ | raw/podman-quadlet/ | graphs/podman-quadlet/ |  |
| pr-af | [[pr-af]] | sources/pr-af/ | raw/pr-af/ | graphs/pr-af/ |  |
| prometheus | [[prometheus]] | sources/prometheus/ | raw/prometheus/ | graphs/prometheus/ |  |
| pydantic-ai-skills | [[pydantic-ai-skills]] | sources/pydantic-ai-skills/ | raw/pydantic-ai-skills/ | graphs/pydantic-ai-skills/ |  |
| quadit | [[quadit]] | sources/quadit/ | raw/quadit/ | graphs/quadit/ |  |
| quadlet-lsp | [[quadlet-lsp]] | sources/quadlet-lsp/ | raw/quadlet-lsp/ | graphs/quadlet-lsp/ |  |
| quadlet-nix | [[quadlet-nix]] | sources/quadlet-nix/ | raw/quadlet-nix/ | graphs/quadlet-nix/ |  |
| reddit-persona-generator | [[reddit-persona-generator]] | sources/reddit-persona-generator/ | raw/reddit-persona-generator/ | graphs/reddit-persona-generator/ |  |
| redhound-arsenal | [[redhound-arsenal]] | sources/redhound-arsenal/ | raw/redhound-arsenal/ | graphs/redhound-arsenal/ |  |
| reels-af | [[reels-af]] | sources/reels-af/ | raw/reels-af/ | graphs/reels-af/ |  |
| reverse-skill | [[reverse-skill]] | sources/reverse-skill/ | raw/reverse-skill/ | graphs/reverse-skill/ |  |
| sablier | [[sablier]] | sources/sablier/ | raw/sablier/ | graphs/sablier/ |  |
| sec-af | [[sec-af]] | sources/sec-af/ | raw/sec-af/ | graphs/sec-af/ |  |
| secureblue | [[secureblue]] | sources/secureblue/ | raw/secureblue/ | graphs/secureblue/ |  |
| shannon | [[shannon]] | sources/shannon/ | raw/shannon/ | graphs/shannon/ |  |
| skills | [[skills]] | sources/skills/ | raw/skills/ | graphs/skills/ |  |
| skills-workspace | [[skills-workspace]] | sources/skills-workspace/ | raw/skills-workspace/ | graphs/skills-workspace/ |  |
| superpowers | [[superpowers]] | sources/superpowers/ | raw/superpowers/ | graphs/superpowers/ |  |
| swe-cli-skills | [[swe-cli-skills]] | sources/swe-cli-skills/ | raw/swe-cli-skills/ | graphs/swe-cli-skills/ |  |
| tank-agent-os | [[tank-agent-os]] | sources/tank-agent-os/ | raw/tank-agent-os/ | graphs/tank-agent-os/ |  |
| tank-os | [[tank-os]] | sources/tank-os/ | raw/tank-os/ | graphs/tank-os/ |  |
| turnstone | [[turnstone]] | sources/turnstone/ | raw/turnstone/ | graphs/turnstone/ |  |
| video-editor-for-claude-code | [[video-editor-for-claude-code]] | sources/video-editor-for-claude-code/ | raw/video-editor-for-claude-code/ | graphs/video-editor-for-claude-code/ |  |
| x-article-publisher-skill | [[x-article-publisher-skill]] | sources/x-article-publisher-skill/ | raw/x-article-publisher-skill/ | graphs/x-article-publisher-skill/ |  |
| zot | [[zot]] | sources/zot/ | raw/zot/ | graphs/zot/ |  |
| Hexstrike-redteam | — | — | — | — | ~~Security framework~~ *deleted from vault* |
| Hexstrike-redteam-full | — | — | — | — | ~~Security framework~~ *deleted from vault* |

**Key:** 177 source repos (175 live + 2 deleted), 147 raw exports, 6 codegraph indexes (goclaw, goclaw-docs, agentmax-os, agentfield, hermes-agent, panzer-os).