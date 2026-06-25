---
name: podlet-mcp-implementation
description: "Podlet — no MCP implementation (CLI tool, no server)"
source: sources/podlet/
tags: [cli, container, mcp, podlet, podman, quadlet, rust]
---

# Podlet — MCP Implementation

**Conclusion: Podlet does not implement the Model Context Protocol (MCP).**

Podlet is a Rust CLI tool for converting Docker Compose files and `podman run` commands into Quadlet systemd unit files. It has no HTTP server, no daemon mode, and no MCP surface.

## What Podlet Does Instead

- **Pure CLI conversion pipeline**: Docker Compose → Quadlet, `podman run` → `.container` files
- **Output to stdout or files** — no server, no protocol
- **D-Bus integration** only for systemd unit conflict detection, not MCP

For MCP-based container management, use a wrapper that calls Podlet's CLI and exposes the results through an MCP server (e.g., Podman's REST API via an MCP adapter).

## Related

- [[podlet-architecture]] — Conversion pipeline architecture
- [[podlet-deployment]] — Installation and usage
- [[podman-mcp-implementation]] — Podman REST API (can be wrapped as MCP)
