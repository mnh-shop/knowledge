---
name: openclaw-container
description: "OpenClaw container deployment templates and patterns for AI agent infrastructure"
source: sources/openclaw-container/
verification_date: 2026-07-12
verified_by: codegraph-verify
tags: [cli, container, deployment, docker, git, messaging, monitoring, openclaw, podman, security, storage, virtualization, python, openclaw-container]
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
- **Network**: Pre-existing `google-vertex` network (10.89.0.0/24) — LiteLLM's own, not created by this repo
- **Existing**: Already deployed, referenced by OpenClaw

#### 4. Network Architecture

**Repo-owned networks** (created by `setup-networks.sh:11-21`):
- `openclaw-external` (10.92.0.0/24): Primary internet access
  - Services: Telegram APIs, Brave API, Red Hat Jira, Google APIs
  - Blocking: All other internet traffic
- `internal-services` (10.93.0.0/24): Container isolation
  - Access: OpenClaw ↔ Whisper ↔ LiteLLM only
  - Security: No external internet access

**Pre-existing (referenced, NOT created by this repo):**
- `google-vertex` (10.89.0.0/24): LiteLLM's existing network — `README.md:18` marks it "already deployed". This repo only joins containers onto `internal-services`; it never creates or manages `google-vertex`. Its purpose is Google Cloud/Vertex AI access for LiteLLM.

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

**As actually implemented** (`start-containers.sh:54-62`): there are **no additional per-subdirectory mounts**. The single `rw` base mount (`~/.openclaw:/app/openclaw-data:rw,z`) makes every `~/.openclaw/` subdirectory (workspace, logs, agents, cron, memories, subagents, telegram, scripts, settings, devices, delivery-queue, media, ...) writable at once; the three `ro` overlays protect only `openclaw.json`, `credentials/`, and `exec-approvals.json`. The README's per-directory mount table (workspace, logs, agents, cron, memories, subagents, telegram, scripts, settings, devices, delivery-queue, media, identity/) is the stale pre-simplification design — it does not match the running script.

**Whisper model mount** (whisper-service only, `start-containers.sh:10,30`):
```bash
-v ~/.local/share/whisper-cpp:/app/models:ro
```

**SSH keys are NOT mounted** (`start-containers.sh:121-124`) — the firewall blocks port 22 anyway; git and gh use HTTPS/OAuth instead.

**Optional credential mounts** (conditional on the host dir existing, `start-containers.sh:68-119`):
- `~/.config/gcloud:/root/.config/gcloud:rw` (Google OAuth token refresh)
- `~/.config/gh:/root/.config/gh:rw` (GitHub OAuth refresh)
- `~/.gitconfig:/root/.gitconfig:ro` (static)
- `~/.config/.jira:/root/.config/.jira:ro`, `~/.config/jira:/root/.config/jira:ro`, `~/.config/notion:/root/.config/notion:ro`, `~/.config/todoist:/root/.config/todoist:ro` (static)

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

Applied by `setup-firewall-policies.sh` (run inside the Podman VM). Two iptables chains on the FORWARD table:

**`PODMAN_ZONE_OPENCLAW`** (`setup-firewall-policies.sh:65-109`) — applies to the `openclaw-external` subnet (10.92.0.0/24):
- Allow DNS (UDP/TCP 53) + established/related (`:72-76`)
- Allow HTTPS (443) to Telegram (`:79-81`), Google (`:84-86`), Red Hat/Jira (`:89-91`), Brave (`:94-96`), GitHub (`:99-101`)
- Log (`openclaw-blocked:`) and DROP everything else (`:104-105`)
- Port 22 (SSH) not allowed — SSH keys are not mounted

**`PODMAN_ZONE_INTERNAL_SVC`** (`setup-firewall-policies.sh:114-132`) — applies to the `internal-services` subnet (10.93.0.0/24):
- Allow only intra-subnet traffic (10.93.0.0/24) + established (`:121-124`)
- Log (`internal-svc-blocked:`) and DROP everything else — no internet (`:127-128`)

**Persistence** — `install-persistent-firewall.sh` installs a systemd service inside the Podman VM:
- Applies the current policies first (`:11-12`), plus the pre-existing LiteLLM policies (`:15-17`)
- Saves the live rules to `/etc/podman-firewall-rules.v4` via `iptables-save` (`:45-47`)
- Installs restore script `/etc/podman-firewall-rules-restore.sh` (`:21-42`)
- Creates `podman-firewall.service` (oneshot, `iptables-restore` at boot, `WantedBy=multi-user.target`) (`:51-66`)
- Enables + starts the service (`:70-72`); re-run the script to re-save updated rules (`:90-91`)

### Deferred Features (Phase 2)

Per `README.md:178-188`:

- **Browser tool** — currently disabled in the container; requires a Chrome/Chromium install (~500MB). Deferred to a future phase if needed.
- **Google OAuth re-auth** — the current setup reuses existing tokens from `~/.openclaw/identity/` (covered by the base `~/.openclaw` rw mount); refresh tokens should auto-renew. If a full re-auth becomes necessary, it is deferred to Phase 2.

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

**See** [[openclaw-container.migration]] — the operations/troubleshooting companion (firewall persistence, OAuth re-auth, SELinux, volume mounts). Note: `MIGRATION-GUIDE.md` does **not** exist in this repo — it is a stale reference in `README.md:64,97,212,270`.

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

- `README.md`: User documentation and quick start (contains stale refs to a non-existent `MIGRATION-GUIDE.md` and a pre-simplification mount table)
- `CLAUDE.md`: AI-assistant context — architecture, volume/SELinux conventions, troubleshooting
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
- `~/.openclaw/*` → `/app/openclaw-data/*` (1 rw base + 3 ro overlays)
- `~/.local/share/whisper-cpp` → `/app/models` (ro, whisper-service only)
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

## Related

- [[openclaw]] — Parent project
- [[podman]] — Container runtime platform
- [[openclaw-container.migration]] — Operations/troubleshooting companion
- [[domains/deployment/INDEX|deployment]] — Container deployment patterns

## Related Resources

- [OpenClaw](https://github.com/accorvin/openclaw) - Main project repository
- [OpenClaw Documentation](https://docs.openclaw.app) - Project documentation
- [Litellm Proxy](https://github.com/BerriAI/litellm) - API proxy service