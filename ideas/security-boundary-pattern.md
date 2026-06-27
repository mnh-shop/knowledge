---
name: security-boundary-pattern
description: "Security boundary rule: autonomous AI agents never run on host OS — always inside VM with rootless Podman. Workspace prototype concept."
tags: [ideas, deployment, security, architecture, podman]
source: workspace/deployment-setup-automation/deployment-architecture.md
---

> **⚠️ Idea / Prototype — this is a design axiom from prototyping work.**
> Not yet validated across all target environments. The vault's `sources/`
> directory remains the single source of truth.
>
> See `domains/deployment/` and `domains/architecture/` for current production
> deployment reference.

## Rule

Autonomous AI agents must never run directly on the host operating system. They have tool access, code execution, web search, and filesystem access — if compromised, they can exfiltrate credentials, modify files, or pivot to other systems.

**The rule:** Host OS runs only hypervisor + SSH. Everything else runs in rootless Podman containers inside a dedicated Linux VM.

## Three deployment modes

- **macOS (dev):** macOS → Podman Machine (vfkit/Apple HV) → Linux VM → rootless Podman → agents
- **Linux VPS (prod):** Cloud hypervisor → Linux VM → rootless Podman → agents
- **Bare metal (max isolation):** Host → crun-vm KVM → Linux VM → rootless Podman → agents

**crun-vm constraint:** Requires /dev/kVM — NOT available on budget VPS (Hetzner CX, DigitalOcean). Use the cloud VM boundary as your isolation layer instead. See [[crun-vm]].

## Related vault pages

- [[podman]] — Quadlet systemd integration as the deployment mechanism
- [[tank-os]] — Fedora bootc reference example of the pattern
- [[crun-vm]] — KVM runtime for bare-metal isolation
