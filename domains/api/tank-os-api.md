---
name: tank-os-api
description: "Tank OS — no REST API (bootc-based container OS image)"
source: sources/tank-os/
tags: [api, container-os, tank-os]
---

# Tank OS — API Reference

**Conclusion: Tank OS does not expose a REST API or HTTP server.**

Tank OS is a bootc-based container OS image. It provides:
- Container runtime configuration via `bootc-config.toml`
- CLI tools for provisioning and model provider configuration
- Quadlet-style systemd unit deployment

All interaction with Tank OS is through:
- `bootc` for image management
- `podman` for container management
- Systemd for service management
- Quadlet files for container deployment

## Related

- [[tank-os-architecture]] — System architecture
- [[tank-os-deployment]] — Deployment guide
- [[tank-os-mcp-implementation]] — MCP assessment (service-gator sidecar)
