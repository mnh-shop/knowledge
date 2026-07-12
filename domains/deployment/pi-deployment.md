---
name: pi-deployment
tags: [pi, deployment, agent, typescript, npm, pnpm, tui, cli, acp, mcp, provider]
description: Deploy Pi TypeScript agent harness — npm/pnpm, TUI desktop config, provider setup, skill installation
source: sources/pi/
---

# Pi Agent Harness Deployment Guide

Deployment and operations guide for Pi — a self-extensible TypeScript coding agent harness and orchestration toolkit with multi-provider LLM support and interactive TUI.

## Overview

Pi is published as npm packages under the `@earendil-works` scope. Deployment is via npm/pnpm global install, with optional systemd service for persistent modes. The interactive TUI is the primary interface, with ACP and one-shot modes for editor and CI integration.

| Deployment Mode | Runtime | Use Case |
|-----------------|---------|----------|
| **npm global** | Node.js 22+ | Interactive TUI, one-shot CLI |
| **pnpm global** | Node.js 22+ | Interactive TUI, one-shot CLI |
| **From source** | TypeScript monorepo | Development, custom builds |
| **ACP server** | Node.js daemon | Editor integration |

## Requirements

### Runtime

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Node.js | 22+ | 22 LTS or 24 |
| Package manager | npm 10+ / pnpm 9+ | pnpm 9+ |
| OS | Linux, macOS, Windows | macOS or Linux |
| RAM | 512 MB | 2 GB+ with TUI + sessions |
| Storage | 100 MB | 1 GB+ for session history |
| Terminal | xterm-256color, tmux compatible | kitty, iTerm2, Ghostty |

### Network Ports

| Port | Service | Default Bind | Purpose |
|------|---------|--------------|---------|
| — | ACP server | Stdio | Agent Client Protocol (stdio transport) |
| — | MCP server | Stdio | MCP tool provider (stdio transport) |

### Dependencies

- **Runtime**: Node.js 22+ (npm/pnpm)
- **Build**: Node.js 22+, npm/pnpm, TypeScript
- **LLM API keys**: Anthropic, OpenAI, Google, Bedrock, DeepSeek, or any supported provider
- **Optional**: Docker (for containerized sandbox), Gondolin (micro-VM isolation)

## Deployment Steps

### npm Global Install

```bash
# Install the coding agent CLI
npm install -g @earendil-works/pi-coding-agent

# Run interactively
pi

# One-shot mode
pi -p "Explain the architecture"
```

### pnpm Global Install

```bash
# Install via pnpm
pnpm add -g @earendil-works/pi-coding-agent

# Verify
pi --version
```

### From Source

```bash
git clone https://github.com/earendil-works/pi-mono.git
cd pi-mono

# Install dependencies (ignore postinstall scripts)
npm install --ignore-scripts

# Build all packages
npm run build

# Run test harness
./pi-test.sh
```

### systemd Service (Optional)

For persistent ACP server or daemon mode:

```bash
mkdir -p ~/.config/systemd/user/

cat > ~/.config/systemd/user/pi-acp.service << 'EOF'
[Unit]
Description=Pi ACP Server
After=network-online.target

[Service]
Type=simple
ExecStart=/usr/local/bin/pi --mode acp
Restart=on-failure
RestartSec=10s
Environment=ANTHROPIC_API_KEY=%C

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now pi-acp.service
```

### TUI Desktop Integration

```bash
# Create desktop entry for TUI
cat > ~/.local/share/applications/pi.desktop << 'EOF'
[Desktop Entry]
Name=Pi Agent
Comment=Pi coding agent harness
Exec=pi
Terminal=true
Type=Application
Categories=Development;
EOF
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes* | Anthropic API key |
| `OPENAI_API_KEY` | No | OpenAI API key |
| `GOOGLE_API_KEY` | No | Google Gemini API key |
| `PI_DATA_DIR` | No | Data directory (default `~/.pi`) |
| `PI_LOG_LEVEL` | No | Log level |

\* At least one LLM provider API key required.

### Provider Setup

Pi auto-discovers providers from environment variables. Provider-specific configuration can be set in `~/.pi/config.json`:

```json
{
  "provider": "anthropic",
  "model": "claude-sonnet-4-20250514",
  "providers": {
    "openai": {
      "apiKey": "${OPENAI_API_KEY}",
      "model": "gpt-4o"
    }
  }
}
```

### Skill Installation

Pi supports extensibility via `~/.pi/extensions/`. Drop-in JavaScript/TypeScript modules with skill implementations:

```bash
mkdir -p ~/.pi/extensions
# Place .js or .mjs files in ~/.pi/extensions/
```

## Related

- [[pi]] — Wiki entry
- [[oh-my-pi]] — Rust-enhanced Pi fork with IDE features
- [[nanobot]] — Python agent framework
- [[hermes-agent]] — Python agent with ACP/MCP support
- [[domains/deployment/oh-my-pi-deployment.md]] — oh-my-pi deployment guide
- [[domains/deployment/nanobot-deployment.md]] — NanoBot deployment guide
- [[domains/deployment/hermes-agent-deployment.md]] — Hermes Agent deployment guide
