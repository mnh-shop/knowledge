---
name: deployment-architecture
description: Defense-in-depth architecture for deploying autonomous AI agent stacks — macOS dev, Linux VM production, rootless Podman isolation
source: sources/nix-podman-stacks/
tags: [architecture, container, deployment, landscape, podman, quadlet, security, shared, systemd, virtualization]
  type: reference
---

# Deployment Architecture

## Principle

Autonomous AI agents **never run on the host OS**. Running agents with tool access, web search, code execution, and file system access directly on your machine or server is a security risk. Instead, isolate behind at least one boundary:

**macOS (dev):** macOS → Podman Machine (vfkit/Apple HV) → Linux VM → rootless Podman → agent containers

**Linux VPS (prod):** Cloud hypervisor → Linux VM → rootless Podman → agent containers

**Bare metal (max isolation):** Host → crun-vm nested KVM → Linux VM → rootless Podman → agent containers

## Why

- Agent compromise → contained within rootless Podman user namespace
- Container escape → contained within the Linux VM
- VM escape → requires hypervisor exploit (rare)
- Host OS remains clean: no agent code, no agent dependencies, no agent network listeners

## Target Platforms

- **Development:** macOS (Apple Silicon, Podman Machine v5+ via vfkit)
- **Production:** Linux (Debian 12 or Fedora) on VPS (Hetzner CX, etc.) or bare metal
- **Deployment:** Rootless Podman Quadlet units managed by systemd --user, with Podman secrets for API keys

## Stack Layers

| Layer | macOS | Linux VPS | Bare Metal |
|---|---|---|---|
| 1 - Hardware | Apple Silicon / Intel | Cloud hypervisor | Physical server |
| 2 - Host OS | macOS | Debian 12 minimal | Debian/Fedora |
| 3 - VM boundary | Podman Machine (vfkit) | Cloud VM boundary | crun-vm (KVM) |
| 4 - Guest OS | Fedora CoreOS (auto) | Debian 12 | Debian 12 |
| 5 - Container runtime | Rootless Podman | Rootless Podman | Rootless Podman |
| 6 - Agents | Quadlet units | Quadlet units | Quadlet units |

## API Key Security

AI agent API keys (Anthropic, OpenAI, etc.) stored in rootless Podman secrets (`~/.local/share/containers/storage/secrets/`). Service-gator MCP proxy sits between agents and external tools to enforce scoped access and prevent credential leakage.

## Constraints

- crun-vm requires /dev/kvm (not available on budget VPS — Hetzner CX, DigitalOcean, Linode)
- crun-vm is for bare metal or nested-virt-capable hosts only
- On VPS, the cloud VM boundary is the isolation layer — crun-vm not needed
- Rootless Podman ports bind to 127.0.0.1 only (access via SSH tunnel)

## Related

- [[crun-vm]] — OCI runtime for nested VM isolation
- [[podman]] — Rootless container engine
- [[tank-os]] — bootc appliance (exemplifies the pattern)
- [[hermzner]] — Hermes deployment (exemplifies VPS pattern)
