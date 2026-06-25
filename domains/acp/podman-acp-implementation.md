---
name: podman-acp-implementation
description: "Podman — no ACP implementation (REST API server, not agent protocol)"
source: sources/podman/
tags: [acp, container, integration, podman]
---

# Podman — ACP Implementation

**Conclusion: Podman does not implement the Agent Client Protocol (ACP).**

Podman is a container engine with a REST API server (Docker-compatible + libpod native). It has no agent communication protocol — it's a daemon with a REST API, not an AI agent.

## Related

- [[podman-mcp-implementation]] — Podman REST API (the relevant protocol surface)
- [[podman-architecture]] — System architecture
