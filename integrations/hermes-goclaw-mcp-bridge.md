---
name: hermes-goclaw-mcp-bridge
type: integration
tags: [hermes-agent, goclaw, integration, mcp]
description: "Hermes Agent ← MCP bridge → GoClaw gateway — Hermes consumes GoClaw's MCP server for Go-native tools"
---

# Integration: Hermes Agent ↔ GoClaw MCP Bridge

## Overview

Hermes Agent connects to GoClaw as an MCP client via SSE transport. GoClaw exposes Go-native tools (filesystem, process, network, crypto) through the Model Context Protocol, making them available to Hermes agents without per-tool wrappers. Both run as rootless Podman containers on a shared Quadlet network.

**Transport**: GoClaw implements SSE MCP transport. Hermes connects, receives tool listings, and invokes tools via HTTP POST to GoClaw's message endpoint. Tool surface: ~15-20 Go standard-library tools (fs.Read, exec.Run, crypto.Sign, etc.).

## Architecture

```
Hermes (:8642)  ──SSE──►  GoClaw (:9091)
  MCP client              MCP server
  tool discovery          Go native tools
  POST /mcp/message       fs, exec, crypto
```

## Configuration

`~/.config/containers/systemd/goclaw.container`:
```ini
[Unit]
Description=GoClaw MCP Gateway
After=network-online.target
[Container]
Image=ghcr.io/goclaw/goclaw:latest
ContainerName=goclaw
Network=agent-stack-net.network
PublishPort=127.0.0.1:9091:9091
Exec=goclaw serve --port 9091 --transport sse
[Service]
Restart=always
[Install]
WantedBy=default.target
```

Add to Hermes `config.yaml`:
```yaml
mcp_servers:
  goclaw:
    url: "http://goclaw:9091/mcp"
    transport: sse
```

### Deployment
```bash
mkdir -p ~/.config/containers/systemd
podman pull ghcr.io/goclaw/goclaw:latest
systemctl --user daemon-reload && systemctl --user start goclaw.service
systemctl --user restart hermes-agent.service
curl -s http://127.0.0.1:8642/health
```

## Related

- [[hermes-agent]] — MCP client consuming GoClaw's tool surface
- [[goclaw]] — Go-native MCP gateway with standard library tools
- [[openclaw]] — Rust-based agent platform, alternative to GoClaw
- [[domains/mcp/mcp-implementation-patterns]] — MCP transport and protocol patterns
