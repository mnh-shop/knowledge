---
name: free-claude-code-deployment
tags: [free-claude-code, deployment, mcp, proxy]
description: free-claude-code — Deployment
source: sources/free-claude-code/
---

# free-claude-code — Deployment

**Source:** `sources/free-claude-code/` · `sources/free-claude-code/server.py` · `sources/free-claude-code/cli/entrypoints.py`

## Overview

free-claude-code (FCC) is a local proxy that routes Anthropic Messages API traffic (from Claude Code CLI/VS Code/JetBrains ACP) and OpenAI Responses API traffic (from Codex CLI/VS Code) to 17+ provider backends. It runs as a FastAPI application served via Uvicorn, with optional CLI launchers and messaging bridges.

The standard deployment is a **local user-space process** (no container required), but it can be containerized with Docker/Podman for server-side or team deployments. The proxy binds to `127.0.0.1:8082` by default and exposes an Admin UI at `/admin`.

## Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 256 MB | 512 MB |
| CPU | 1 core | 1 core |
| Python | 3.12+ | 3.14 |
| Runtime | Uvicorn (via `uv` or pip) | Docker/Podman for containerized |
| Disk | 200 MB | 1 GB (log + cache) |

## Deployment Steps

### 1. Quick Start (User-Space, No Container)

```bash
# Install via script (macOS/Linux)
curl -fsSL "https://github.com/Alishahryar1/free-claude-code/blob/main/scripts/install.sh?raw=1" | sh

# Start the proxy
fcc-server
```

The proxy starts on `http://127.0.0.1:8082`. Open the Admin UI at `http://127.0.0.1:8082/admin` to configure providers.

### 2. Run from Source

```bash
git clone https://github.com/Alishahryar1/free-claude-code.git
cd free-claude-code

# Install dependencies
uv sync

# Start the server
uv run uvicorn server:app --host 0.0.0.0 --port 8082 --timeout-graceful-shutdown 5
```

### 3. Client Launchers

Once the proxy is running, launch coding agents through it:

```bash
# Claude Code via FCC
fcc-claude

# Codex via FCC
fcc-codex
```

These launchers automatically configure:
- `ANTHROPIC_BASE_URL` → local proxy
- Gateway model discovery (190k-token auto-compact window)
- Codex: ephemeral `fcc` provider with `wire_api = "responses"`

### 4. Docker Compose

```yaml
version: '3.8'
services:
  free-claude-code:
    build:
      context: https://github.com/Alishahryar1/free-claude-code.git
      dockerfile: Dockerfile  # If using custom image; otherwise use published image
    image: ghcr.io/alishahryar1/free-claude-code:latest
    container_name: fcc-proxy
    restart: unless-stopped
    ports:
      - "8082:8082"
    environment:
      # Provider API keys
      - NVIDIA_API_KEY=${NVIDIA_API_KEY:-}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY:-}
      - GEMINI_API_KEY=${GEMINI_API_KEY:-}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY:-}
      - MISTRAL_API_KEY=${MISTRAL_API_KEY:-}
      - CODESTRAL_API_KEY=${CODESTRAL_API_KEY:-}
      - OPENCODE_ZEN_API_KEY=${OPENCODE_ZEN_API_KEY:-}
      - OPENCODE_GO_API_KEY=${OPENCODE_GO_API_KEY:-}
      - WAFER_API_KEY=${WAFER_API_KEY:-}
      - KIMI_API_KEY=${KIMI_API_KEY:-}
      - CEREBRAS_API_KEY=${CEREBRAS_API_KEY:-}
      - GROQ_API_KEY=${GROQ_API_KEY:-}
      - FIREWORKS_API_KEY=${FIREWORKS_API_KEY:-}
      # Model routing
      - MODEL_OPUS=${MODEL_OPUS:-}
      - MODEL_SONNET=${MODEL_SONNET:-}
      - MODEL_HAIKU=${MODEL_HAIKU:-}
      - MODEL=${MODEL:-}
    volumes:
      - fcc_data:/app/data
      - fcc_config:/app/config
    healthcheck:
      test: ["CMD", "curl", "-f", "http://127.0.0.1:8082/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  fcc_data:
    driver: local
  fcc_config:
    driver: local
```

### 5. Podman Quadlet

Save as `~/.config/containers/systemd/fcc-proxy.container`:

```ini
[Container]
Image=ghcr.io/alishahryar1/free-claude-code:latest
ContainerName=fcc-proxy
PublishPort=8082:8082
Volume=fcc-data:/app/data
Volume=fcc-config:/app/config
Environment=NVIDIA_API_KEY=%%NVIDIA_API_KEY%%
Environment=OPENROUTER_API_KEY=%%OPENROUTER_API_KEY%%
Environment=GEMINI_API_KEY=%%GEMINI_API_KEY%%
Environment=MODEL_OPUS=%%MODEL_OPUS%%
Environment=MODEL_SONNET=%%MODEL_SONNET%%
Environment=MODEL_HAIKU=%%MODEL_HAIKU%%
Environment=MODEL=%%MODEL%%
HealthCmd=curl -f http://127.0.0.1:8082/v1/health
HealthInterval=30s
HealthRetries=3
AutoUpdate=registry

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now fcc-proxy.service
```

### 6. Provider Configuration

FCC routes requests through a `ModelRouter` that resolves incoming model names. Configuration is done via the Admin UI (`/admin`) or environment variables:

| Variable | Description |
|----------|-------------|
| `MODEL_OPUS` | Override model for `opus` tier requests |
| `MODEL_SONNET` | Override model for `sonnet` tier requests |
| `MODEL_HAIKU` | Override model for `haiku` tier requests |
| `MODEL` | Fallback model for all other requests |

Each provider key is set as its corresponding environment variable (e.g., `NVIDIA_API_KEY`, `OPENROUTER_API_KEY`).

### 7. Architecture

```
┌──────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│  Claude Code  │────>│                      │────>│  NVIDIA NIM     │
│  (Anthropic   │     │                      │     │  OpenRouter     │
│   Messages)   │     │    Free Claude Code  │     │  Gemini         │
├──────────────┤     │    (FastAPI/Uvicorn)  │     │  DeepSeek       │
│  Codex        │────>│                      │────>│  Mistral        │
│  (OpenAI      │     │  ModelRouter →       │     │  Groq           │
│   Responses)  │     │  ProviderTransport   │     │  ... 17+ more   │
└──────────────┘     └──────────────────────┘     └─────────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  Admin UI    │
                     │  /admin      │
                     └──────────────┘
```

### 8. Advanced: Messaging Bridges

FCC supports optional Discord and Telegram bridges that turn chat messages into managed Claude Code CLI sessions:

```yaml
# docker-compose addition
environment:
  - DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN:-}
  - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-}
  - VOICE_NOTE_TRANSCRIPTION=${VOICE_NOTE_TRANSCRIPTION:-false}
```

## Persistent Storage

| Path | Contents |
|------|----------|
| `/app/data/` | Provider config, logs, session state |
| `/app/config/` | Provider catalog overrides, custom settings |

## Related

- [[free-claude-code]] — FCC wiki entry (architecture, providers, features)
- [[opencode]] — AI coding agent that can be configured as an FCC provider
- [[claude-code]] — Anthropic's coding CLI (primary FCC client)
- [[zot]] — OCI registry for storing and distributing FCC container images
- [[hermes-agent]] — Alternative agent gateway that can use FCC as a provider route
