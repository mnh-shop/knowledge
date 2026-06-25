---
name: tank-os-acp-implementation
description: "Tank OS — no ACP implementation (container OS, no agent protocol)"
source: sources/tank-os/
tags: [acp, container-os, tank-os]
---

# Tank OS — ACP Implementation

**Conclusion: Tank OS does not implement the Agent Client Protocol (ACP).**

Tank OS is a bootc-based container OS for running agent infrastructure. It provides the runtime environment (container orchestration via Quadlet, systemd services) but does not implement agent communication protocols itself.

## Related

- [[tank-os-architecture]] — Container OS architecture
- [[tank-os-deployment]] — Deployment guide
