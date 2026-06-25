---
name: podlet-acp-implementation
description: "Podlet — no ACP implementation (CLI tool, no agent protocol)"
source: sources/podlet/
tags: [acp, cli, container, podlet, podman, quadlet, rust]
---

# Podlet — ACP Implementation

**Conclusion: Podlet does not implement the Agent Client Protocol (ACP).**

Podlet is a Rust CLI tool for Quadlet file generation. It has no agent communication, no server, and no protocol surface beyond stdin/stdout for its own CLI pipeline.

## Related

- [[podlet-architecture]] — Architecture overview
- [[podlet-deployment]] — Deployment guide
