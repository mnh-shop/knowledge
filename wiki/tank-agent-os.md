---
name: tank-agent-os
tags: [tank-agent-os, bootc, agent, immutable-os, container, fedora]
description: "Bootable container OS image for running AI agents in production"
source: sources/tank-agent-os/
---

# Tank Agent OS

| Field | Value |
|---|---|
| **Origin** | [tank-OS/tank-agent-os](https://github.com/tank-OS/tank-agent-os) |
| **License** | MIT |
| **Stack** | Fedora bootc, rootless Podman, Quadlet, nftables, cloud-init |
| **Source** | `sources/tank-agent-os/` |
| **Repomix** | `raw/tank-agent-os/tank-agent-os.xml` |
| **Codegraph** | `graphs/tank-agent-os/` |

## Overview

**Tank Agent OS** is a bootable container OS image designed specifically for running **autonomous AI coding agents in production**. Built on Fedora bootc, it provides a minimal, immutable, self-updating operating system that boots directly into an agent runtime environment — eliminating the gap between containerized agent deployments and the host OS that runs them.

**The core philosophy:** an autonomous agent decides at runtime which services to call and which files to read, so containment must be a property of the *whole stack*, not a single control. Every outbound packet is forced through an audited egress proxy, OS-level nftables confine the agent's UID, and a root-owned instruction file hardens against prompt injection — all enforced by the OS, not by the agent's cooperation.

The threat model is the **lethal trifecta**: an agent that reads untrusted input, can call external services, and can be tricked into combining the two. tank-agent-os contains this through impact containment rather than detection.

**Who it is for:**
- Solo devs running agents 24/7 on a homelab who want a hard network boundary
- Security teams piloting agentic coding who can't trust a vendor sandbox they can't inspect
- Operators who want an audit log of every agent egress request that an auditor would accept

### Real-World Incidents Motivating This Project

| Incident | Mitigation |
|---|---|
| Claude Code deleted a home directory (`rm -rf $HOME` via tilde-expansion bug) | Rootless container UID, no write to host outside two declared paths, OS-level firewall |
| Cursor agent sandbox bypass via shell builtins (CVE-2026-22708) | Egress enforced in the kernel and on separate host, not in agent's process |
| Cline supply-chain incident ("Clinejection", Feb 2026) — malicious MCP payload | Agents reject MCP config from workspace; only root-owned, image-shipped config is honoured |

## Key Features

- **Three Pinned Agent Runtimes** — Supports `opencode` (default), `claw-code` (experimental, compiled from source), or **Claude Code** (downloaded with GPG-verified manifest). One agent per image — no runtime switching or runtime updates. The agent binary is SHA-256-pinned at build time.
- **Audited Egress Proxy** — Every outbound packet is forced through an allowlisted, logged proxy on a *separate host*. This provides a tamper-resistant audit log that survives VM compromise.
- **OS-Level Network Lockdown** — nftables rules confine the agent's UID to the egress proxy. The agent has no `CAP_NET_ADMIN` and cannot modify routing tables or firewall rules. A deny-all baseline applies even with no proxy configured.
- **Prompt-Injection Hardening** — A root-owned, read-only instruction file (`/etc/clawx/CLAUDE.md`) establishes a trust hierarchy: workspace content is data, not commands. The file is mounted read-only into the container and cannot be modified by the agent.
- **Mediated External Access** — `service-gator` gates all external API calls (GitHub, GitLab, Forgejo, JIRA) behind a per-repository `scopes.json` allowlist. The agent can only call tools for repositories explicitly listed.
- **Self-Hosted Web Search** — A bundled SearXNG + `mcp-searxng` pair provides web search without any cloud API key or external search-provider trust anchor.
- **Docs-Lookup MCP** — Scrapes and indexes developer documentation from specified sources, served to the agent over MCP. No runtime network access required for lookups.
- **LLM-Wiki MCP** — An agent-curated knowledge base where the agent distils sources into linked notes that grow and reuse across sessions. Complements RAG with structured, agent-written knowledge.
- **Skill Drop-In** — Drop a `SKILL.md` folder into `~/.clawx/skills/` — effective next session, no image rebuild needed.
- **Persistent Agent Memory** — Build-time opt-in (`--build-arg AGENT_MEMORY_PERSIST=true`). Off by default because persistent memory is a prompt-injection-persistence surface.
- **MCP Adoption Gate** — Every new MCP server ships with a written security audit in `audits/` using the [CSA mcpserver-audit](https://github.com/ModelContextProtocol-Security/mcpserver-audit) framework.

## Architecture

### System Design

```
tank-agent-os/
├── bootc/
│   ├── Containerfile              ← bootc OS image definition
│   ├── clawx-runtime/
│   │   └── Containerfile          ← Agent runtime container image
│   ├── rootfs/                    ← OS filesystem overlay (systemd units, nftables rules, sudoers)
│   ├── keys/                      ← GPG keys for signed release verification
│   └── patches/                   ← Patches applied to claw-code build
├── docs/                          ← Documentation (15 markdown files)
├── audits/                        ← MCP server security adoptions
└── tools/                         ← Utility scripts and unit tests
```

### Security Layers (Stacked Defense)

| Layer | Mechanism | Enforced By |
|---|---|---|
| **1 — Container Network Isolation** | Dedicated Podman bridge network (`clawx-isolated`), no ports published to host | Podman, container runtime |
| **2 — OS Firewall** | nftables rules on host OUTPUT chain block all outbound from agent UID except to proxy | Linux kernel, root-owned systemd service |
| **3 — Egress Proxy** | Separate host running HTTP proxy with allowlist enforcement and tamper-resistant audit logging | External infrastructure |
| **4 — Runtime Config Injection** | Proxy address, port, and CA cert injected at boot via cloud-init/root-owned files; not baked into image | cloud-init, systemd |
| **5 — Prompt Injection Hardening** | Root-owned instruction file (`CLAUDE.md`) establishes data-not-commands trust hierarchy; mounted read-only | OS permissions, container mount |
| **6 — Workspace Config Injection Protection** | Agents ignore workspace-provided MCP config (`--strict-mcp-config`), project-level settings (`--setting-sources user`), and patched config discovery | Per-agent invocation flags and patches |
| **7 — Supply Chain Pinning** | SHA-256 digest pins on every consumed image and binary; GPG verification for Claude Code releases | Build pipeline |

### Container Architecture

The agent runs as a **rootless Podman container** managed by a **Quadlet** unit installed at:

```
/etc/containers/systemd/users/1000/clawx.container
```

The bootc image installs:
- A `clawx` login user with UID/GID 1000 with systemd linger enabled
- The agent binary at `/usr/local/bin/agent` (pinned SHA-256 verified at build)
- A `clawx` wrapper script at `/usr/local/bin/clawx` for agent CLI operations
- The Quadlet unit that launches the agent container on boot
- nftables rules installed by `clawx-nftables.service` (runs before user session)

Mutable state lives at two paths:
- `/var/home/clawx/.clawx` — Agent runtime state, config, skills directory
- `/var/home/clawx/workspaces` — Git working trees for agent operations

### Build Pipeline

The build has two stages:

1. **Build clawx runtime container image** — Contains the agent runtime dependencies, MCP server binaries, and supporting tools:
   ```bash
   podman build -t <registry>/clawx-runtime:latest bootc/clawx-runtime
   podman push <registry>/clawx-runtime:latest
   ```

2. **Build the bootc OS image** — Embeds the agent binary (chosen via `AGENT_KIND`) and the runtime image reference:
   ```bash
   podman build \
     --build-arg AGENT_KIND=opencode \
     --build-arg CLAWX_RUNTIME_IMAGE=<registry>/clawx-runtime \
     -t localhost/tank-agent-os:opencode \
     -f bootc/Containerfile bootc
   ```

Agent variants are encoded in the image tag:
- `tank-agent-os:opencode` — Default (opencode binary)
- `tank-agent-os:claw` — Claw-code (compiled from source with patches)
- `tank-agent-os:claude` — Claude Code (GPG-verified upstream binary)
- `tank-agent-os:latest` — Alias for `:opencode`

### Supply Chain Security

| Agent | Build Method | Verification |
|---|---|---|
| `opencode` | Download upstream Bun-compiled binary | SHA-256 of tarball + binary |
| `claw-code` | Compile from source (Rust/cargo) with patches | SHA-256 of locally built binary |
| `Claude Code` | Download native binary | GPG signature over release manifest + SHA-256 of binary |

All builds produce a hash file at `/usr/local/share/tank-os/agent.sha256` for runtime verification:
```bash
sudo sha256sum -c /usr/local/share/tank-os/agent.sha256
```

## Usage

### Building the Image

```bash
# Clone the repository
git clone https://github.com/tank-OS/tank-agent-os.git
cd tank-agent-os

# Build the clawx runtime image
podman build -t my-registry/clawx-runtime:latest bootc/clawx-runtime

# Build the bootc OS image (opencode default)
podman build \
  --build-arg AGENT_KIND=opencode \
  --build-arg CLAWX_RUNTIME_IMAGE=my-registry/clawx-runtime \
  -t localhost/tank-agent-os:opencode \
  -f bootc/Containerfile bootc
```

### First Boot Configuration

After booting the VM, configure:

1. **Provider credentials** — Set via `AGENT_*` environment variables or `~/.clawx/agent.env`:
   ```
   AGENT_PROVIDER=ollama
   AGENT_BASE_URL=http://ollama.example.internal:11434/v1
   AGENT_MODEL=replace-with-ollama-model
   ```
2. **Proxy configuration** (optional but recommended) — Set proxy address and CA certificate via Podman secrets
3. **Service-gator scopes** — Configure `~/.clawx/.config/service-gator/scopes.json` for mediated external API access

### Day-2 Operations

```bash
# Upgrade OS image
sudo bootc upgrade --apply

# Rollback to previous deployment
sudo bootc rollback

# Upgrade agent binary (rebuild image, then:)
sudo bootc switch --apply <registry>/tank-agent-os:opencode-<sha>
```

### What The Agent Can And Cannot Do

| Action | Possible |
|---|---|
| Call service-gator (MCP tools) | Yes — via bridge network |
| Call model provider (LLM endpoint) | Yes — if proxy permits it |
| Call any host not in proxy allowlist | No — blocked by proxy before TLS |
| Access repo not listed in scopes.json | No — rejected by service-gator |
| Modify nftables rules | No — no CAP_NET_ADMIN |
| Modify its own instruction file | No — read-only mount, root-owned |
| Auto-update itself | No — update hosts excluded from proxy allowlist; config pins autoupdate: false |
| Write to workspace | Yes — `~/workspaces/` is the intended working area |
| Write outside mounts | No — container filesystem is isolated |
| Run code via workspace `.mcp.json` | No — only baked, root-owned MCP config is loaded |

### Recovery Model

tank-agent-os has **no backup-and-restore procedure** by design. The appliance is stateless:

| State | Recovered by |
|---|---|
| Code being worked on | Re-clone from external git remote |
| Agent runtime state | Regenerated on first boot |
| Provider keys/tokens | Re-created from operator credentials |
| The OS image | Re-pulled from registry |

Recovery is **rebuild, not restore**. `rebuild-vm.sh` is the recovery path for a corrupted VM.

## Related

- [[tank-os]] — Fedora bootc image for general deployment; the parent project whose appliance architecture tank-agent-os forks
- [[bootc]] — Bootable container technology underlying Tank Agent OS; provides the transactional, atomic OS update mechanism
- [[openclaw]] — Personal AI assistant deployable on Tank Agent OS; one of the agent runtime options
- [[podman]] — Container runtime used for the agent container and supporting services; supplies rootless container execution
- [[podman-quadlet]] — systemd-native container management used to define the agent container as a Quadlet unit
- [[extension-podman-quadlet]] — Podman Desktop extension for visual Quadlet management, useful for managing agent containers
- [[secureblue]] — Hardened Fedora Atomic images providing security-focused OS variants in the same bootc ecosystem
- [[fedora-coreos-config]] — Fedora CoreOS configuration; the base platform Fedora bootc images are built from
- [[service-gator]] — External API mediation tool used to gate the agent's API calls behind scopes allowlist
- [[nix-podman-stacks]] — Alternative deployment approach for agent workloads using NixOS-based stacks
- [[hermes-agent]] — Agent platform that could be deployed on Tank Agent OS as an alternative agent runtime
