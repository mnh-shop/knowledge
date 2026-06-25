---
title: OpenClaw Container Deployment
author: Claude Code
date: 2026-06-25
project: openclaw-container
tags: [ai-llm, cli, container, containerization, containers, docker, git, messaging, monitoring, openclaw, plugin-sdk, podman, security, storage, virtualization, whisper.cpp]
status: active
last_updated: 2026-06-25
---

# OpenClaw Container Deployment

Secure, isolated OpenClaw deployment using Podman with network-level security restrictions and audio transcription capabilities.

## Overview

OpenClaw Container provides a production-ready deployment of OpenClaw using containerization technologies (Podman) with advanced security features:

- **Network Isolation**: Restrict internet access to only required services (Telegram, Brave, Jira, Google APIs)
- **Audio Transcription**: Separate whisper.cpp service for audio processing
- **Persistent Storage**: All data persists on host through secure mounts
- **Auto-Scaling**: Container-based deployment with automatic restarts
- **Security-First Design**: Firewall policies and SELinux-compatible mounts

## Architecture Overview

### Container Structure

```
┌─────────────────────────────────────────────────────┐
│                    Host                             │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │ Podman VM (macOS)                           │  │
│  │                                               │  │
│  │  ┌──────────────┐    ┌──────────────┐       │  │
│  │  │ openclaw-    │    │ whisper-     │       │  │
│  │  │ gateway      │───▶│ service      │       │  │
│  │  │              │    │              │       │  │
│  │  │ - OpenClaw   │    │ - whisper.cpp│       │  │
│  │  │ - CLI tools  │    │ - HTTP API   │       │  │
│  │  │ - whisper    │    │ - ffmpeg     │       │  │
│  │  │   wrapper    │    │              │       │  │
│  │  └──────────────┘    └──────────────┘       │  │
│  │         │                                    │  │
│  │         ▼                                    │  │
│  │  ┌──────────────┐                           │  │
│  │  │ litellm-     │                           │  │
│  │  │ proxy        │                           │  │
│  │  │ (external)   │                           │  │
│  │  └──────────────┘                           │  │
│  └──────────────────────────────────────────────┘  │
│         │                                          │
│         ▼                                          │
│  ~/.openclaw/ (persistent data)                   │
└─────────────────────────────────────────────────────┘
```

### Key Components

#### 1. OpenClaw Gateway Container (`openclaw-gateway`)
- **Purpose**: Main OpenClaw service with CLI tools
- **Technology**: Node.js 22 on Debian
- **Exposed**: Port 18789 (accessible from host)
- **Network**: Dual-homed (accessible from both external and internal networks)
- **Key Features**:
  - CLI tool wrapper for whisper integration
  - Network traffic filtering and logging
  - Full OpenClaw functionality

#### 2. Whisper Service (`whisper-service`)
- **Purpose**: Audio transcription API
- **Technology**: Python 3.11 + whisper.cpp
- **Exposed**: HTTP API on port 8080
- **Network**: Internal services only (no internet access)
- **Performance**: Supports multiple workers with 2-minute timeout

#### 3. LiteLLM Proxy
- **Purpose**: External API proxy for Claude models
- **Network**: Google Vertex AI dedicated network
- **Existing**: Already deployed, referenced by OpenClaw

#### 4. Network Architecture

**OpenClaw Networks:**
- `openclaw-external` (10.92.0.0/24): Primary internet access
  - Services: Telegram APIs, Brave API, Red Hat Jira, Google Vertex AI
  - Blocking: All other internet traffic
- `internal-services` (10.93.0.0/24): Container isolation
  - Access: OpenClaw ↔ Whisper ↔ LiteLLM only
  - Security: No external internet access
- `google-vertex` (10.89.0.0/24): Litellm external access
  - Purpose: Google Cloud/Vertex AI only

## Container Definitions

### OpenClaw Gateway Container

**Dockerfile**: `openclaw.Containerfile`

**Base Image**: `node:22-bookworm-slim`

**Installed Tools**:
- GitHub CLI (`gh`)
- Google Cloud SDK (`gcloud`)
- yq (YAML processor)
- Jira CLI
- trash-cli
- openclaw (version 2026.2.23)
- ffmpeg, git, curl, jq, rsync

**Security Features**:
- Runs as root inside container (security provided by rootless Podman)
- All config files read-only (except credentials needing refresh)
- SSH keys explicitly NOT mounted
- Bound to all interfaces (`--bind lan`) for host access

**Key Environment Variables**:
```bash
ENV OPENCLAW_CONFIG_PATH=/app/openclaw-data/openclaw.json
ENV OPENCLAW_STATE_DIR=/app/openclaw-data
```

**Entry Point**:
```bash
cmd ["openclaw", "gateway", "--bind", "lan"]
```

### Whisper Service Container

**Dockerfile**: `whisper.Containerfile`

**Base Image**: `python:3.11-slim`

**Build Process**:
1. Install ffmpeg and wget
2. Clone whisper.cpp from GitHub
3. Build from source with all dependencies
4. Install Flask and gunicorn

**Network**: Internal services only (no internet access)

**Health Endpoint**: `http://whisper-service:8080/health`

**API Endpoints**:
- `POST /v1/audio/transcriptions`: OpenAI-compatible endpoint
- `POST /transcribe`: Legacy endpoint
- `GET /health`: Health check

### Volume Mount Strategy

**Simplification Philosophy**: Single base mount + read-only overlays

**Base Mount** (`rw`):
```bash
-v ~/.openclaw:/app/openclaw-data:rw,z
```

**Protected Overlays** (`ro`):
```bash
-v ~/.openclaw/openclaw.json:/app/openclaw-data/openclaw.json:ro,z
-v ~/.openclaw/credentials:/app/openclaw-data/credentials:ro,z
-v ~/.openclaw/exec-approvals.json:/app/openclaw-data/exec-approvals.json:ro,z
```

**Other RW Mounts**:
- Workspace, logs, skills, cron, memories, subagents, telegram, scripts, settings, devices, delivery-queue, media

**OAuth Credentials** (`rw` for refresh):
- Google Cloud: `~/.config/gcloud:/root/.config/gcloud:rw`
- GitHub: `~/.config/gh:/root/.config/gh:rw`

### SELinux Labels

All mounts use `:z` flag for SELinux compatibility:
- Without `:z`: Files appear as `nobody:nogroup` with `nfs_t` context → permission denied
- With `:z`: Files get `container_file_t` context → accessible

## Deployment Process

### Prerequisites

**Required:**
- litellm-proxy container already running
- Podman machine running
- `~/.openclaw/` directory with your config
- `LITELLM_API_KEY` environment variable set

### One-Time Setup

```bash
cd /Users/acorvin/dev/openclaw-container

# 1. Create networks
./setup-networks.sh

# 2. Apply firewall policies
podman machine ssh podman-machine-default < setup-firewall-policies.sh

# 3. Update configuration
# Change litellm baseUrl to: "http://litellm-proxy:4000"
# Change whisper to HTTP: "http://whisper-service:8080/transcribe"

# 4. Build images
./build-images.sh

# 5. Stop native OpenClaw
pkill -f openclaw-gateway

# 6. Start containers
export LITELLM_API_KEY="your-key"
./start-containers.sh
```

### Daily Operations

**Check Status**:
```bash
podman ps | grep -E "openclaw|whisper"
podman inspect openclaw-gateway | jq '.NetworkSettings.Networks | keys'
```

**View Logs**:
```bash
podman logs openclaw-gateway --tail 50
podman logs whisper-service
```

**Restart Containers**:
```bash
podman restart openclaw-gateway
```

**Test Whisper Service**:
```bash
podman exec openclaw-gateway curl http://whisper-service:8080/health
```

**Check Blocked Traffic**:
```bash
podman machine ssh "sudo journalctl -k --since '10 minutes ago' | grep openclaw-blocked"
```

## Configuration Changes

### Before migration, edit `~/.openclaw/openclaw.json`:

**Change 1: Litellm URL**
```json
"models": {
  "providers": {
    "litellm": {
      "baseUrl": "http://litellm-proxy:4000",  // was: http://localhost:4000
      ...
    }
  }
}
```

**Change 2: Whisper Tool**
```json
"tools": {
  "media": {
    "audio": {
      "enabled": true,
      "models": [
        {
          "type": "http",                                    // was: "cli"
          "url": "http://whisper-service:8080/transcribe",  // new
          "method": "POST"
        }
      ]
    }
  }
}
```

## Security Features

### Network Isolation

**✅ Protected**:
- OpenClaw can only reach: Telegram, Brave, Jira, Google APIs
- Whisper has no internet access (internal-only)
- LiteLLM restricted to Google Cloud (existing policy)
- All unauthorized traffic blocked and logged

**🛡️ Active Blocking**:
- Port 22 (SSH) blocked - no SSH keys mounted
- All other outbound traffic blocked
- Continuous monitoring of blocked connections

### Mount Security

**✅ Read-Only Protection**:
- Config files: read-only
- Credentials: read-only (except OAuth tokens needing refresh)
- All data persists on host at `~/.openclaw/`

**✅ Auto-Start**: Containers set to `--restart=always`

### Firewall Policies

Applied by `setup-firewall-policies.sh`:
- Allowed from openclaw-external network:
  - HTTPS to GitHub (for gh CLI, git)
  - HTTPS to Red Hat/Jira (issues.redhat.com)
  - HTTPS to Google Vertex AI (via separate network)
  - DNS queries
  - Internal container communication
- Blocked: Port 22 (SSH)

## Monitoring

### Container Health

**Check gateway**:
```bash
curl http://localhost:18789/health
podman exec openclaw-gateway curl http://whisper-service:8080/health
podman exec openclaw-gateway curl http://litellm-proxy:4000/health
```

**Check network connectivity**:
```bash
podman inspect openclaw-gateway | jq '.NetworkSettings.Networks | keys'
# Should show: ["internal-services", "openclaw-external"]
```

### Blocked Traffic

```bash
podman machine ssh "sudo journalctl -k --since '10 minutes ago' | grep openclaw-blocked"
```

### Troubleshooting

**Quick Checks**:
```bash
# Container won't start
podman logs openclaw-gateway

# Can't reach other containers
podman network inspect internal-services

# Port not accessible
lsof -i :18789

# Firewall blocking too much
podman machine ssh "sudo iptables -L PODMAN_ZONE_OPENCLAW -n -v"
```

**See** `MIGRATION-GUIDE.md` for detailed troubleshooting steps.

## Success Criteria

After containerization, all of the following should be verified:

- [ ] Desktop app connects to containerized gateway
- [ ] Telegram messages work
- [ ] Claude models accessible via litellm
- [ ] Audio transcription functional
- [ ] Skills persist and execute
- [ ] Cron jobs run
- [ ] Memories saved and accessible
- [ ] Can create new skills
- [ ] Network isolation verified
- [ ] Auto-starts on reboot

## Files and Directories

### Main Scripts

- `README.md`: User documentation and quick start
- `MIGRATION-GUIDE.md`: Migration instructions
- `openclaw.Containerfile`: Gateway container definition
- `whisper.Containerfile`: Whisper service definition
- `whisper-api.py`: Whisper HTTP API
- `whisper-wrapper.sh`: Whisper CLI wrapper

### Deployment Scripts

- `build-images.sh`: Build both container images
- `start-containers.sh`: Start all containers
- `stop-containers.sh`: Stop and remove containers
- `setup-networks.sh`: Create podman networks
- `setup-firewall-policies.sh`: Configure iptables rules
- `install-persistent-firewall.sh`: Make firewall persistent via systemd

### Critical Configuration Files

**Network Zones** (`setup-networks.sh`):
- `openclaw-external`: 10.92.0.0/24
- `internal-services`: 10.93.0.0/24

**Volume Mappings** (`start-containers.sh`):
- `~/.openclaw/*` → `/app/openclaw-data/*`
- With proper SELinux labels (`:z` flag)

## Important Conventions

### Container User

Containers run as **root** (UID 0) inside container, but Podman rootless provides security isolation at VM level. Files created by container appear as UID 0 in podman VM.

### Path Mapping

**Host Paths** → **Container Paths**:
- `~/.openclaw/workspace` → `/app/openclaw-data/workspace`
- `~/.openclaw/openclaw.json` → `/app/openclaw-data/openclaw.json`

### Network Binding

Gateway binds to `0.0.0.0` inside container (via `--bind lan`) for host access. Port forwarding: `127.0.0.1:18789:18789` (localhost only on host).

### Whisper Integration

OpenClaw calls: `whisper -f /tmp/audio.ogg`
Wrapper intercepts and calls: `http://whisper-service:8080/transcribe`

## Version History

**v1.0** (2026-03-05)
- Initial containerization with openclaw-gateway + whisper-service
- Network security with iptables firewall
- Simplified volume mount structure
- SELinux compatibility with `:z` flags
- Timezone support
- CLI tools integration (gh, gcloud, jira, yq)

**Maintained By**: Alex Corvin (@accorvin)
**Repository**: https://github.com/accorvin/openclaw-container
**Last Updated**: 2026-03-05

## Related Resources

- [OpenClaw](https://github.com/accorvin/openclaw) - Main project repository
- [OpenClaw Documentation](https://docs.openclaw.app) - Project documentation
- [Litellm Proxy](https://github.com/BerriAI/litellm) - API proxy service