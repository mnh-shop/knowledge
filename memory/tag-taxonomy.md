---
name: tag-taxonomy
description: Complete taxonomy of ecosystem, language, and classification tags in the knowledge vault
tags: [index, reference, taxonomy]
metadata:
  type: reference
---

# Tag Taxonomy

There are **3 tag categories** in the knowledge vault:

## 1. Ecosystem Tags (76 total)

All source repo directory names are valid ecosystem tags. Found in SCHEMA.md lines 103-117.

```
1claw-hermes, AionUi, ECC, Hermes-caduceus, Mnemosyne, OpenViking,
SWE-AF, abvx-agent-skills, af-deep-research, af-reactive-atlas-mongodb,
agent-rules-books, agentfield, alphaclaw, awesome-n8n-templates,
Android-Pentesting-Checklist, Anthropic-Cybersecurity-Skills,
awesome-openclaw-skills, awesome-openclaw-usecases, bootc, buildah,
camofox-browser, clawpier, cockpit-podman, crun-vm, CyberStrikeAI,
drawio-skill, defending-code-reference-harness, fedora-coreos-config,
free-claude-code, goclaw, gogs, graphify, hermes-agent,
hermes-agent-acp-skill, hermes-agent-docker, hermes-agent-template,
hermes-autonomous-server, hermes-bus, hermes-incident-commander,
hermes-optimization-guide, hermes-plugins, hermes-profiles,
hermes-startup-architect, hermes-suite, hermes-workspace, hermzner,
Hexstrike-redteam, hexstrike-ai, kali-pentest, llmtrim, materia,
mission-control, n8n, n8n-mcp, n8n-skills, n8n-workflows, nanobot,
nix-podman-stacks, nix.dev, nyxstrike, obsidian-skills, oh-my-hermes,
oh-my-openagent, oh-my-opencode-slim, oh-my-pi, open-design, openclaw,
openclaw-container, openclaw-plugin-claude-code, opencode,
opencode-hermes-multiagent, outreachmagic, pi, podlet,
podman, podman-compose, pydantic-ai-skills, reverse-skill, sablier,
SecuritySkills, sec-af, skills, tank-os, zot
```

## 2. Language Tags (6 total)

Based on actual file counts (>20 files or >10% of code):

- `python` — Python repos
- `typescript` — TypeScript repos (includes TS/JS for Obsidian)
- `golang` — Go repos
- `rust` — Rust repos
- `javascript` — JavaScript repos
- `nix` — Nix / NixOS repos

## 3. Classification Tags (~140 total)

General purpose — describe what the project IS or DOES.

See SCHEMA.md lines 148-166 for full list. Key deployment-related tags:

- `bootc` — Image-based OS, Fedora CoreOS, upgrade-to-container
- `quadlet` — systemd-native container management
- `podman` — Container engine (daemonless, rootless)
- `docker` — Container compatibility/competition
- `systemd` — systemd service management
- `container` — Container runtime/deployment
- `oci` — OCI image spec compliance
- `oci-runtime` — OCI runtime (crun, runc)
- `virtualization` — VM/container boundaries
- `vm` — QEMU, KVM, virtualization
- `rootless` — Rootless container operations

Key harness-related tags:

- `agent-profile` — Hermes profile specialization (SOUL.md + AGENTS.md + profile.yaml)
- `harness` — Agent harness platform
- `agent-gateway` — Gateway/hub pattern
- `agent-manager` — Desktop/manager application
- `skills-platform` — Skill catalog/repository

### Companion Page Rule (rule #2)

Pages without their own `sources/` directory use the **parent repo's ecosystem tag**:

- `wiki/quadlet.md` → uses `podman` (source: sources/podman/)
- `wiki/n8n-nodes.md` → uses `n8n` (source: sources/n8n/)
- `wiki/n8n-workflow-catalog.md` → uses `n8n-workflows`
- `wiki/cockpit.md` → uses `cockpit-podman`