---
name: oh-my-pi-deployment
tags: [oh-my-pi, deployment, agent, rust, bun, typescript, systemd, cli, mcp, acp]
description: Deploy oh-my-pi (pi-mono fork) — Rust binary, systemd service, configuration, ACP/MCP setup
source: sources/oh-my-pi/
---

# Oh My Pi Deployment Guide

Deployment and operations guide for oh-my-pi (omp) — a Rust + Bun coding agent fork of Pi with batteries-included coding workflow, 32 built-in tools, and ACP/MCP support.

## Overview

oh-my-pi ships as a native binary with an embedded Bun runtime. The primary deployment is direct binary installation, with systemd service support for persistent daemon modes (RPC and ACP servers).

| Deployment Mode | Runtime | Use Case |
|-----------------|---------|----------|
| **Binary install** | Native binary | Interactive TUI, one-shot CLI |
| **npm/Bun global** | Bun package | Development, CI pipelines |
| **systemd service** | systemd + binary | Persistent ACP/RPC server |
| **From source** | Bun + Rust build | Development, custom builds |

## Requirements

### Runtime

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| OS | macOS, Linux | Linux for production |
| Architecture | x86_64, aarch64 | aarch64 (Apple Silicon / ARM) |
| RAM | 1 GB | 4 GB+ with subagents |
| Storage | 200 MB binary | 1 GB+ for sessions, memory |
| Bun | 1.2+ (for source builds) | Latest stable |

### Network Ports

| Port | Service | Default Bind | Purpose |
|------|---------|--------------|---------|
| 18789 | ACP server | `127.0.0.1` | Agent Client Protocol |
| 8081 | RPC server | `127.0.0.1` | NDJSON RPC endpoint |
| — | MCP server | `127.0.0.1` | Stdio transport (no port) |

### Dependencies

- **Runtime**: None (self-contained binary)
- **Build**: Rust toolchain (nightly), Bun 1.2+, Node.js 22+
- **LLM API keys**: Anthropic, OpenAI, or any of 40+ supported providers
- **Optional**: ast-grep (for structural code search)

## Deployment Steps

### Quick Install (Binary)

```bash
# macOS or Linux
curl -fsSL https://omp.sh/install | sh

# Homebrew (macOS)
brew install can1357/tap/omp
```

### npm/Bun Global Install

```bash
# Via npm
npm install -g @oh-my-pi/pi-coding-agent

# Via Bun
bun install -g @oh-my-pi/pi-coding-agent
```

### Verify Installation

```bash
omp --version
omp --help
```

### systemd Service (ACP Server)

Create `/etc/systemd/user/omp-acp.service`:

```ini
[Unit]
Description=oh-my-pi ACP Server
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=%h/.local/bin/omp acp
Restart=on-failure
RestartSec=5s
Environment=ANTHROPIC_API_KEY=%C
Environment=OMP_DATA_DIR=%h/.omp

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now omp-acp.service
```

### From Source

```bash
git clone https://github.com/can1357/oh-my-pi.git
cd oh-my-pi
bun setup    # Install workspaces, build Rust N-API addon
bun dev      # Run from source
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes* | Primary LLM provider key |
| `OPENAI_API_KEY` | No | Fallback provider key |
| `OMP_DATA_DIR` | No | Data directory (default `~/.omp`) |
| `OMP_LOG_LEVEL` | No | Log level (info, debug, trace) |

\* At least one LLM API key required for operation.

### Provider Configuration

oh-my-pi supports 40+ providers configured via environment variables or the `~/.omp/config.json` file. Path-scoped models and fallback chains are supported for resilient routing.

### ACP/MCP Setup

ACP enables editor integration (Zed, Claude Code, OpenCode):

```bash
# Start ACP server
omp acp

# MCP server (stdio transport) — configured in editor MCP settings
# Command: omp mcp
```

## Related

- [[oh-my-pi]] — Wiki entry
- [[pi]] — Upstream Pi agent harness
- [[nanobot]] — Python agent framework
- [[hermes-agent]] — Python agent with ACP support
- [[domains/deployment/pi-deployment.md]] — Pi deployment guide
- [[domains/deployment/nanobot-deployment.md]] — NanoBot deployment guide
