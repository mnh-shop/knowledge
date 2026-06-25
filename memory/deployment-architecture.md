---
name: deployment-architecture
description: Autonomous AI agents NEVER run on the host OS — always inside a VM with rootless Podman. macOS dev, Linux VPS prod.
metadata:
  type: reference
---

Autonomous AI agents must never run directly on the host operating system. They have tool access, code execution, web search, and filesystem access — if compromised, they can exfiltrate credentials, modify files, or pivot to other systems.

**The rule:** Host OS runs only hypervisor + SSH. Everything else runs in rootless Podman containers inside a dedicated Linux VM.

**Three deployment modes:**
- **macOS (dev):** macOS → Podman Machine (vfkit/Apple HV) → Linux VM → rootless Podman → agents
- **Linux VPS (prod):** Cloud hypervisor → Linux VM → rootless Podman → agents
- **Bare metal (max isolation):** Host → crun-vm KVM → Linux VM → rootless Podman → agents

**crun-vm constraint:** Requires /dev/kVM — NOT available on budget VPS (Hetzner CX, DigitalOcean). Use the cloud VM boundary as your isolation layer instead. See [[crun-vm]].

**Why:** This is documented in [[deployment-architecture]].

**How to apply:**
- When asked about deployment, always propose this layering
- Never suggest running agents directly on the host
- Reference [[podman]] Quadlet systemd integration as the deployment mechanism
- Use [[tank-os]] as a reference example of the pattern
