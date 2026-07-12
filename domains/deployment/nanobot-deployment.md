---
name: nanobot-deployment
tags: [nanobot, deployment, agent, docker, python, podman, quadlet, systemd, messaging, channels]
description: Deploy NanoBot agent framework — Docker/Podman, configuration, channel setup, LLM provider config
source: sources/nanobot/
---

# NanoBot Deployment Guide

Deployment and operations guide for NanoBot — an ultra-lightweight personal AI agent framework with multi-platform chat channels, tools, memory, and WebUI.

## Overview

NanoBot runs as a Python asyncio gateway process that connects LLM providers to 17+ chat channels. Deployment options range from a simple `pip install` to Docker/Podman containerization with systemd or LaunchAgent lifecycle management.

| Deployment Mode | Runtime | Use Case |
|-----------------|---------|----------|
| **pip install** | Native Python | Local development, single-user |
| **Docker/Podman** | Containerized | Production, multi-user, isolated |
| **Quadlet (Linux)** | systemd + Podman | Rootless production on Linux |
| **LaunchAgent (macOS)** | Native service | macOS desktop deployment |

## Requirements

### Runtime

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.11+ | 3.12+ |
| OS | Linux, macOS, Windows | Linux for production |
| RAM | 1 GB | 2 GB+ with WebUI + channels |
| Storage | 500 MB | 5 GB+ for sessions and memory |
| Docker/Podman | Docker 24+ / Podman 4+ | Podman 5+ for Quadlet |

### Network Ports

| Port | Service | Default Bind | Purpose |
|------|---------|--------------|---------|
| 8000 | Gateway HTTP | `127.0.0.1` | WebUI and API server |
| — | WebSocket | Dynamic | Multiplexed WebUI protocol |
| — | Channel webhooks | Configurable | Per-channel HTTP callbacks |

### Dependencies

- **Python packages**: `nanobot-ai` (PyPI), `pip install nanobot-ai`
- **Optional**: Redis (for channel message queuing), PostgreSQL (alternate session store)
- **LLM API keys**: Anthropic, OpenAI, or any supported provider

## Deployment Steps

### Quick Start (pip)

```bash
# Install
pip install nanobot-ai

# Start the gateway
nanobot gateway

# WebUI available at http://localhost:8000/webui/
```

### Docker Deployment

```bash
# Pull image
docker pull hkuds/nanobot:latest

# Run with API key
docker run -d \
  --name nanobot \
  -p 8000:8000 \
  -v nanobot_data:/app/data \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  hkuds/nanobot:latest
```

### Docker Compose

```yaml
services:
  nanobot:
    image: hkuds/nanobot:latest
    container_name: nanobot
    ports:
      - "127.0.0.1:8000:8000"
    volumes:
      - nanobot_data:/app/data
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - NANOBOT_CHANNELS=telegram,discord
    restart: unless-stopped

volumes:
  nanobot_data:
```

### Rootless Podman Quadlet

Create `~/.config/containers/systemd/nanobot.container`:

```ini
[Unit]
Description=NanoBot Agent
After=network-online.target
Wants=network-online.target

[Container]
Image=docker.io/hkuds/nanobot:latest
ContainerName=nanobot
PublishPort=127.0.0.1:8000:8000
Volume=nanobot-data:/app/data:Z
Environment=ANTHROPIC_API_KEY=%C
Environment=NANOBOT_CHANNELS=telegram

[Volume]
VolumeName=nanobot-data

[Service]
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user start nanobot.service
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes* | Anthropic API key |
| `OPENAI_API_KEY` | No | OpenAI API key |
| `NANOBOT_CHANNELS` | No | Comma-separated channel list |
| `NANOBOT_DATA_DIR` | No | Data directory (default `/app/data`) |
| `NANOBOT_LOG_LEVEL` | No | Log level (INFO, DEBUG, etc.) |

\* At least one LLM provider API key required.

### Channel Configuration

Channels are configured via environment variables or `config.yaml`:

```bash
# Telegram
TELEGRAM_BOT_TOKEN=<bot-token>

# Discord
DISCORD_BOT_TOKEN=<bot-token>

# Slack
SLACK_BOT_TOKEN=<bot-token>
```

### LLM Provider Setup

Providers are auto-detected from API key environment variables. Supported: Anthropic, OpenAI, Azure, Bedrock, GitHub Copilot, Gemini, DeepSeek, and more.

## Related

- [[nanobot]] — Wiki entry
- [[hermes-agent]] — Competing Python agent framework
- [[pi]] — TypeScript agent harness
- [[materia]] — GitOps Quadlet manager
- [[domains/deployment/hermes-agent-deployment.md]] — Hermes Agent deployment guide
- [[domains/deployment/pi-deployment.md]] — Pi deployment guide
