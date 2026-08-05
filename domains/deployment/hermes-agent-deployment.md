---
name: hermes-agent-deployment
tags: [acp, agent-gateway, ansible, cli, container, dashboard, deployment, docker, git, hermes-agent, mcp, messaging, monitoring, multi-platform, nix, podman, quadlet, security, storage, systemd, terraform, typescript]
description: Hermes Agent deployment and operations guide for the multi-platform personal AI agent
source: sources/hermes-agent/
---

# Hermes Agent Deployment Guide

Deployment and operations guide for Hermes Agent -- a multi-platform personal AI agent by Nous Research.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Windows and Termux Support](#windows-and-termux-support)
- [Rootless Podman Quadlet Setup](#rootless-podman-quadlet-setup)
- [Systemd Service Management](#systemd-service-management)
- [Container Internals (s6-overlay)](#container-internals-s6-overlay)
- [Configuration](#configuration)
- [Model Provider API Keys](#model-provider-api-keys)
- [MCP Server Configuration](#mcp-server-configuration)
- [ACP Configuration](#acp-configuration)
- [Secrets Management](#secrets-management)
- [Health Checks and Monitoring](#health-checks-and-monitoring)
- [SSH Tunnel Access](#ssh-tunnel-access)
- [Hermzner Reference Deployment](#hermzner-reference-deployment)
- [Environment Variables Reference](#environment-variables-reference)
- [Updates and Maintenance](#updates-and-maintenance)
- [Scale-to-Zero with Chronos](#scale-to-zero-with-chronos)
- [Troubleshooting](#troubleshooting)
- [Key Source Files](#key-source-files)

---

## Overview

Hermes Agent can be deployed in several configurations, from a simple local CLI to a full production stack with messaging gateway, MCP bridge, ACP adapter, and multi-platform support:

| Deployment Mode | What Runs | Use Case |
|-----------------|-----------|----------|
| **CLI only** | `hermes` binary, SQLite DB | Local development, test |
| **Quadlet (recommended)** | Rootless Podman container + systemd | Production single-server |
| **Docker Compose** | Agent + workspace containers | Development, workspace integration |
| **Hermzner** | Terraform + Ansible on Hetzner | Turnkey production deployment |
| **NixOS module** | Nix-managed agent service | NixOS systems |
| **Custom** | Build your own automation | Custom infrastructure |

---

## Prerequisites

### Runtime Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **Python** | 3.11+ | 3.12+ |
| **OS** | Linux (primary), macOS, Windows | Linux for production |
| **Storage** | 2 GB for image + state | 10 GB+ for sessions, memory, workspace |
| **RAM** | 2 GB | 4 GB+ with gateway + MCP + ACP |
| **Podman** | 4.0+ (for Quadlet deployment) | 5.0+ |
| **Docker** | 24.0+ (for Compose deployment) | 27.0+ |

### Network Ports

| Port | Service | Default Bind | Purpose |
|------|---------|--------------|---------|
| 8642 | Gateway HTTP API | `127.0.0.1` | REST API for workspace and tools |
| 9119 | Dashboard | `127.0.0.1` | Web dashboard |
| 18789 | Gateway WebSocket | `127.0.0.1` | Messaging bus for live events |

### Access Requirements

- **Outbound HTTPS**: Required for all model provider APIs (Anthropic, OpenAI, etc.)
- **Tailscale** (recommended): Secure tunnel for SSH and dashboard access
- **SSH server**: For remote management

---

## Installation

### Quick Install (End User)

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

This script installs the `hermes` binary and performs first-time setup.

### Install from Source

```bash
# Clone the repository
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# Install with uv (recommended)
uv sync --all-extras

# Or with pip
pip install -e ".[all]"
```

### Windows Quick Install

```powershell
# PowerShell one-liner (README.md:50)
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

### Clone Setup Script

For a manual clone, `setup-hermes.sh` performs the platform-detected setup
(desktop/server vs Android/Termux): creates a Python 3.11 venv, installs the
platform-appropriate dependency set, and creates `.env` from the template if
absent. It uses `uv` on desktop/server and stdlib `venv` + pip on Termux.

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
./setup-hermes.sh
```

### Nix Flake

Hermes ships a Nix flake (`flake.nix`) plus a `nix/` module tree
(`nixosModules.nix`, `hermes-agent.nix`, `desktop.nix`, `tui.nix`, `web.nix`,
`python.nix`, `devShell.nix`, `checks.nix`, `overlays.nix`, `packages.nix`,
`lib.nix`, `configMergeScript.nix`):

```bash
nix develop            # development shell
nix build .#hermes     # build the agent package
```

The `nixosModules.nix` provides a NixOS module for Nix-managed service
deployment.

### Docker Image

The official Docker image is available at `docker.io/nousresearch/hermes-agent`.

```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```

### Post-Install

```bash
# Run diagnostics
hermes doctor

# Run first-time setup (interactive -- configures provider, model, channels)
hermes setup

# Verify health
hermes gateway health
```

---

## Windows and Termux Support

### Native Windows Install

Windows is a first-class install target. The PowerShell one-liner
(`install.ps1`) installs the binary natively — no WSL required (though WSL is
supported and used by the dashboard's PTY-based embedded TUI, which requires a
POSIX PTY).

The Windows path relies on `hermes_bootstrap.py`, which must be the **very
first import** in every entrypoint — it configures UTF-8 stdio so Unicode
output survives Windows' legacy codepage. POSIX is unaffected (no-op there).
Any runner that skips the bootstrap risks mojibake on Windows terminals.

### Android / Termux

| Artifact | Purpose |
|----------|---------|
| `constraints-termux.txt` | Termux-specific dependency pins for the Android setup path |
| `setup-hermes.sh` | Detects Android/Termux and uses stdlib `venv` + pip instead of uv |
| `hermes_cli/psutil_android.py` | Android-aware psutil shims |

### CJK Full-Text Search (`native/fts5_cjk`)

Hermes ships a prebuilt CJK tokenizer extension for SQLite FTS5 in
`native/fts5_cjk/` — required for Chinese/Japanese/Korean full-text session
search on platforms where the stock SQLite build lacks the extension. It is
bundled for native installs; the Docker image instead builds a pinned SQLite
from source (see `Dockerfile`) to avoid distro WAL-reset bugs.

### Multi-Profile Isolation

Hermes supports **profiles** — fully isolated instances, each with its own
`HERMES_HOME` (config, API keys, memory, sessions, skills, gateway). The
profile override is applied in `hermes_cli/main.py` (`_apply_profile_override`)
before any module imports; all `get_hermes_home()` calls
(`hermes_constants.py`) scope to the active profile automatically.

```bash
# Run with a specific profile
hermes -p client-a

# Create a profile during setup
hermes setup --profile client-b

# Profile registry (HOME-anchored, visible from any profile)
hermes profile list
```

Profile roots live at `~/.hermes/profiles/<name>` and are HOME-anchored (not
HERMES_HOME-anchored) so `hermes -p x profile list` sees every profile. This
is what enables the multi-agent kanban worker fleets and per-client
gateway deployments.

---

## Rootless Podman Quadlet Setup

The recommended production deployment uses Rootless Podman with Quadlet for systemd-native lifecycle management. See the [[assets/deployment/hermes-agent-quadlet.md]] asset for complete Quadlet configuration examples.

### Quick Start

```bash
# 1. Create Quadlet directory
mkdir -p ~/.config/containers/systemd/

# 2. Create configuration directory
mkdir -p ~/.config/hermes

# 3. Write the agent.env file with API keys
cat > ~/.config/hermes/agent.env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-...
EOF
chmod 600 ~/.config/hermes/agent.env

# 4. Create Quadlet .container file
cat > ~/.config/containers/systemd/hermes-agent.container << 'EOF'
[Unit]
Description=Hermes Agent
After=network-online.target
Wants=network-online.target

[Container]
Image=docker.io/nousresearch/hermes-agent:latest
ContainerName=hermes
Exec=gateway run
Network=host

Environment=HERMES_DASHBOARD=1
Environment=HERMES_DASHBOARD_HOST=127.0.0.1
Environment=HERMES_DASHBOARD_PORT=9119
Environment=API_SERVER_HOST=127.0.0.1
Environment=API_SERVER_ENABLED=true
EnvironmentFile=%h/.config/hermes/agent.env

Volume=%h/.hermes:/opt/data:Z

HealthCmd=curl -fsS http://localhost:8642/health && curl -fsS http://localhost:9119/api/status || exit 1
HealthInterval=10s
HealthTimeout=5s
HealthRetries=5
HealthStartPeriod=30s

[Service]
Type=forking
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=default.target
EOF

# 5. Reload systemd and start
systemctl --user daemon-reload
systemctl --user start hermes-agent.service
systemctl --user enable hermes-agent.service

# 6. Verify
systemctl --user status hermes-agent.service
journalctl --user -u hermes-agent.service -f
```

### Docker Compose Alternative

For development or workspace integration, use Docker Compose:

```yaml
services:
  hermes-agent:
    image: docker.io/nousresearch/hermes-agent:latest
    container_name: hermes-agent
    command: gateway run
    network_mode: host
    environment:
      - HERMES_DASHBOARD=1
      - HERMES_DASHBOARD_HOST=127.0.0.1
      - HERMES_DASHBOARD_PORT=9119
      - API_SERVER_HOST=127.0.0.1
      - API_SERVER_ENABLED=true
    env_file:
      - ~/.config/hermes/agent.env
    volumes:
      - ~/.hermes:/opt/data
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://localhost:8642/health"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    restart: unless-stopped
```

---

## Systemd Service Management

Beyond Quadlet, Hermes manages its own systemd/launchd gateway service units
directly via the CLI (`hermes_cli/gateway.py`).

### Gateway Service Lifecycle

```bash
# Install the gateway as a service (user scope by default)
hermes gateway install

# System-wide (root): writes /etc/systemd/system/hermes-gateway.service
sudo hermes gateway install --system

# Control the service
hermes gateway start | stop | restart | status

# Remove the unit
hermes gateway uninstall
```

Key behaviors:

- Unit name is `hermes-gateway.service` for the default profile and
  `hermes-gateway-<profile>.service` for named profiles, so multiple profile
  gateways can coexist without fighting over the same bot credentials
  (legacy `hermes.service` units are detected and cleaned up).
- Install/uninstall is profile-aware: it will refuse to install over a
  different profile's active service and surfaces which scope/unit is
  currently running.
- On systemd hosts the gateway uses `Restart=always`; macOS falls back to
  launchd (the same `GatewayProcessManager` abstracts both).
- For rootless container deployments, prefer Quadlet (previous section);
  `hermes gateway install` is for native/bare-metal installs.

---

## Container Internals (s6-overlay)

The Docker image (`Dockerfile`) is s6-overlay supervised. PID 1 is `/init`
(s6-overlay), which runs the `cont-init.d` scripts (chown, profile reconcile,
dashboard toggle) and then brings up the supervision tree in `docker/s6-rc.d/`:

| Unit | Service |
|------|---------|
| `main-hermes` | Main gateway agent process |
| `dashboard` | Web dashboard (only when `HERMES_DASHBOARD=1`) |
| `user` | User session supervisor |

Supporting scripts in `docker/`:

| File | Purpose |
|------|---------|
| `entrypoint.sh` | Container entrypoint chain |
| `main-wrapper.sh` | Wraps the main gateway process (default ENTRYPOINT tail) |
| `stage2-hook.sh` | Remaps the internal `hermes` user to `HERMES_UID`/`HERMES_GID` |
| `hermes-exec-shim.sh` | `hermes exec` shim |
| `tini-shim.sh` | tini re-exec shim |
| `cont-init.d/` | One-shot init scripts (chown, profile reconcile, dashboard toggle) |

```bash
# Run with host UID/GID so container-written files stay owned by you
HERMES_UID=$(id -u) HERMES_GID=$(id -g) docker compose up -d

# Or via podman
HERMES_UID=$(id -u) HERMES_GID=$(id -g) podman compose up -d
```

**Do not bypass `/init`** — the compose file's security notes warn that
overriding the entrypoint skips cont-init setup (chown, profile reconcile,
dashboard toggle) and the gateway will not work correctly. `docker-compose.yml`
is the Linux stack; `docker-compose.windows.yml` is the Windows variant. Both
mount `~/.hermes` as `/opt/data`.

## Configuration

### Config File Architecture

Hermes manages configuration files under `~/.hermes/` (or `$HERMES_HOME`):

| File | Format | Purpose |
|------|--------|---------|
| `config.yaml` | YAML | Agent configuration: provider, model, MCP servers, custom providers |
| `.env` | KEY=value | API keys and environment settings |
| `auth-profiles.json` | JSON | Multiple API credential sets for different profiles |

### Config Directory Layout

```
~/.hermes/
  config.yaml           # Agent configuration
  .env                  # Environment variables (API keys)
  auth-profiles.json    # Auth profiles (multi-provider credentials)
  state.db              # SQLite session database (SessionDB)
  sessions.json         # Session index for MCP bridge
  channel_directory.json # Platform channel registry
  workspace-overrides.json # UI-managed config overrides
  sessions/              # Session transcripts
  memory/               # Long-term memory store
  logs/                 # Rolling logs
```

### Core Config Settings (config.yaml)

```yaml
# Model provider
provider: anthropic
model: claude-sonnet-4-20250514

# MCP servers
mcp_servers:
  filesystem:
    command: npx
    args: ["-y", "@anthropic/mcp-filesystem", "."]
  brave-search:
    command: npx
    args: ["-y", "@anthropic/mcp-brave-search"]
    env:
      BRAVE_API_KEY: "${BRAVE_API_KEY}"

# Custom providers
custom_providers: {}

# Memory settings
memory:
  backend: sqlite  # or mnemosyne
  enabled: true

# Gateway settings
gateway:
  dashboard: true
  dashboard_host: "127.0.0.1"
  dashboard_port: 9119
  api_server_host: "127.0.0.1"
  api_server_enabled: true
```

---

## Model Provider API Keys

API keys are read from environment variables and should never be committed to version control. Store them in `~/.config/hermes/agent.env` (mode 0600) for Quadlet deployments.

### Supported Providers

| Provider | Env Variable | Required |
|----------|-------------|----------|
| Anthropic | `ANTHROPIC_API_KEY` | Yes (for primary model) |
| OpenAI | `OPENAI_API_KEY` | Optional |
| Google Gemini | `GEMINI_API_KEY` | Optional |
| AWS Bedrock | `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` | Optional |
| OpenRouter | `OPENROUTER_API_KEY` | Optional |
| NovitaAI | `NOVITA_API_KEY` | Optional |
| NVIDIA NIM | `NVIDIA_API_KEY` | Optional |

### Setting Up API Keys

```bash
# Create env file with minimal permissions
mkdir -p ~/.config/hermes
cat > ~/.config/hermes/agent.env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-<your-key>
OPENAI_API_KEY=sk-<your-key>
GEMINI_API_KEY=<your-key>
EOF
chmod 600 ~/.config/hermes/agent.env
```

### Model Selection

```bash
# Switch model at runtime
hermes model claude-sonnet-4-20250514

# Use provider:model syntax
hermes model openai:gpt-4o

# List available models
hermes model list
```

### Using Auth Profiles

For multiple API credential sets (different projects, clients):

```bash
# Create an auth profile
hermes setup --profile client-a

# Use a specific profile
hermes --profile client-a

# Switch profiles
hermes config set profile client-a
```

---

## MCP Server Configuration

Hermes is both an MCP **client** (consuming MCP servers as tool providers) and an MCP **server** (serving as a messaging bridge). See [[domains/mcp/hermes-mcp-implementation.md]] for the full implementation reference.

### Configuring MCP Servers (Client Side)

MCP servers are configured in `config.yaml` under `mcp_servers`:

```yaml
mcp_servers:
  # Stdio transport
  filesystem:
    command: npx
    args: ["-y", "@anthropic/mcp-filesystem", "."]
    env:
      FOO: bar

  # HTTP transport
  my-remote-server:
    url: "https://mcp.example.com/sse"
    headers:
      Authorization: "Bearer ${MCP_TOKEN}"

  # Environment variables in config
  brave-search:
    command: npx
    args: ["-y", "@anthropic/mcp-brave-search"]
    env:
      BRAVE_API_KEY: "${BRAVE_API_KEY}"  # resolves from env
```

MCP servers can also be registered dynamically from ACP clients at session creation time (passed as `mcp_servers` parameter to `session/new`).

### Running the MCP Server (Bridge Side)

```bash
# Start the MCP messaging bridge
hermes mcp serve

# With verbose logging
hermes mcp serve --verbose
```

The MCP bridge exposes 10 tools (matching OpenClaw's 9-tool surface + 1 extra) for listing/sending conversations across all connected platforms.

**Client config** (for Claude Code, Cursor, Codex):

```json
{
  "mcpServers": {
    "hermes": {
      "command": "hermes",
      "args": ["mcp", "serve"]
    }
  }
}
```

### Optional MCP Servers

Hermes ships optional MCP server manifests in `optional-mcps/`:

| Manifest | Service |
|----------|---------|
| `linear/manifest.yaml` | Linear (project management) |
| `n8n/manifest.yaml` | n8n (workflow automation) |
| `unreal-engine/manifest.yaml` | Unreal Engine integration |

These are not installed by default -- use the manifest to configure them when needed.

---

## ACP Configuration

Hermes implements the Agent Communication Protocol (ACP) for editor integration. See [[assets/acp-agents/hermes-acp-agent.md]] for the full ACP agent reference.

### Running the ACP Server

```bash
# Start the ACP server
hermes acp serve

# Or directly via Python
python -m acp_adapter
```

### ACP Registry

The agent is registered in `acp_registry/agent.json` for ACP discovery:

```json
{
  "id": "hermes-agent",
  "name": "Hermes Agent",
  "version": "0.17.0",
  "repository": "https://github.com/NousResearch/hermes-agent",
  "distribution": {
    "uvx": {
      "package": "hermes-agent[acp]==0.17.0",
      "args": ["hermes-acp"]
    }
  }
}
```

### Supported ACP Clients

| Client | How to Connect |
|--------|---------------|
| **Zed** | Register via ACP agent registry |
| **Claude Code (ACP mode)** | Configure ACP endpoint |
| **Codex** | ACP-compatible by default |
| **OpenCode** | ACP-compatible by default |
| **Pi** | ACP-compatible by default |

### ACP Session Modes

| Mode | `SessionMode` | Behavior |
|------|--------------|----------|
| `default` | `ask` | Ask before file edits |
| `accept_edits` | `workspace_session` | Auto-allow workspace + /tmp edits |
| `don't_ask` | `session` | Auto-allow all (except sensitive paths) |

---

## Secrets Management

### Storage Locations

| Content | Location | Notes |
|---------|----------|-------|
| API keys | `~/.config/hermes/agent.env` | Environment file, mode 0600 |
| Config secrets | `config.yaml` inline | `${VAR}` references resolved at runtime |
| Auth profiles | `~/.hermes/auth-profiles.json` | Multiple credential sets |
| MCP server tokens | `config.yaml` | `${VAR}` references |
| Session data | `~/.hermes/state.db` | SQLite database |

### Best Practices

1. **Never commit secrets to version control.** Add `agent.env` to `.gitignore`.
2. **Use `EnvironmentFile=`** with Quadlet for clean secret injection (file must be mode 0600).
3. **Minimal secret surface.** Only set the API keys your deployment uses.
4. **Rotate API keys regularly.** Use provider dashboards to regenerate tokens.
5. **For production**, consider using systemd credential files or a secrets manager (SOPS, pass, 1Password).

### Quadlet Secret Injection

For Quadlet deployments, use the `Secret=` directive for additional secrets:

```ini
# Reference a Podman secret
Secret=hermes-anthropic-key,type=env,target=ANTHROPIC_API_KEY
```

Create the secret:

```bash
echo "sk-ant-..." | podman secret create hermes-anthropic-key -
```

---

## Health Checks and Monitoring

### Health Endpoints

| Endpoint | Service | Response |
|----------|---------|----------|
| `http://localhost:8642/health` | Gateway API | `{"status":"ok"}` |
| `http://localhost:9119/api/status` | Dashboard | `{"status":"running"}` |

### Health Check Commands

```bash
# Via curl
curl -fsS http://localhost:8642/health

# Via Hermes CLI
hermes gateway health

# Via podman (from host)
podman healthcheck run hermes
```

### Quadlet Health Check

Included in the .container file:

```ini
HealthCmd=curl -fsS http://localhost:8642/health && curl -fsS http://localhost:9119/api/status || exit 1
HealthInterval=10s
HealthTimeout=5s
HealthRetries=5
HealthStartPeriod=30s
```

### Monitoring

```bash
# Systemd service status
systemctl --user status hermes-agent.service

# Journal logs (follow)
journalctl --user -u hermes-agent.service -f

# Journal logs (last 50 lines)
journalctl --user -u hermes-agent.service -n 50 --no-pager

# Podman logs
podman logs hermes

# Container resource usage
podman stats hermes
```

### Gateway Health & Diagnostics Export (OTLP)

Hermes can export gateway health metrics and redacted diagnostics over OTLP
to an operator-configured endpoint. The export surface is **content-free by
construction** — no prompts, messages, tool args/results, or usage analytics.
The implementation lives in `hermes_cli/observability/` (OTLP
metrics/traces/logs relay, `relay_runtime.py`, `shared_metrics.py`) with a
versioned schema at `hermes_cli/observability/schemas/hermes.shared_metrics.v1.schema.json`.

```bash
# Inspect monitoring export state and redaction posture
hermes monitoring status
```

Configured under the `monitoring.*` keys in `config.yaml` (`hermes_cli/config_defaults.py`).
See [[hermes-agent-observability]] for the full reference, including the
optional `langfuse` and `nemo_relay` observability plugins
(`plugins/observability/`).

### Usage Insights

```bash
# Token usage, costs, tool patterns, and activity trends over the last 30 days
hermes insights [--days 30] [--source telegram]

# Billing: plan / top-up view, dollars-only (also /usage and /subscription in TUI)
hermes usage
hermes subscription
hermes topup
```

### Diagnostics

```bash
# Full diagnostics
hermes doctor

# Gateway connectivity probe
hermes gateway probe

# Session status
hermes sessions list
```

---

## SSH Tunnel Access

For secure access to the Hermes dashboard and API from remote hosts, use SSH tunnels:

### Dashboard Tunnel

```bash
# Forward dashboard port to localhost
ssh -L 9119:127.0.0.1:9119 hermes@<remote-host> -N

# Open in browser
open http://127.0.0.1:9119
```

### API Tunnel

```bash
# Forward API port to localhost
ssh -L 8642:127.0.0.1:8642 hermes@<remote-host> -N

# Test API access
curl http://127.0.0.1:8642/health
```

### Combined Tunnel

```bash
ssh -L 9119:127.0.0.1:9119 -L 8642:127.0.0.1:8642 hermes@<remote-host> -N
```

### Tailscale Alternative

When using Tailscale (as in the Hermzner deployment), direct connections work without SSH tunnels:

```bash
# Connect via Tailscale IP
ssh hermes@100.x.x.x

# Access dashboard directly
open http://100.x.x.x:9119
```

---

## Hermzner Reference Deployment

Hermzner (`sources/hermzner/`) provides a production-grade deployment pipeline for running Hermes on Hetzner Cloud. It is the recommended reference for deploying Hermes Agent to production infrastructure.

### Architecture

```
Deployer Host
    │
    ├── Terraform: Provisions Hetzner VPS
    │   - Server type: cx23 (default)
    │   - OS: Ubuntu 24.04
    │   - Location: fsn1
    │
    ├── Ansible: Configures and deploys
    │   - 7 roles: security, docker, quadlet, hermes, hermes-backup, tailscale, verify
    │   - Rootless Podman Quadlet for agent runtime
    │   - Tailscale for network isolation
    │   - SSH hardening, firewall, fail2ban
    │   - Automated backups (daily at 02:00)
    │
    └── Verification:
        - 11 assertion smoke test
        - Health endpoint validation
        - Tailscale connectivity check
```

### Key Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `server_type` | `cx23` | Hetzner server type |
| `os_type` | `ubuntu-24.04` | OS image |
| `hermes_image_ref` | `ghcr.io/hermes-agent/hermes-agent:latest@sha256:...` | Pinned container image |
| `hermes_dashboard_enabled` | `true` | Enable web dashboard |
| `hermes_runtime_backend` | `quadlet` | Runtime backend (quadlet or compose) |
| `public_ssh_policy` | `disabled_after_tailscale` | SSH access policy after Tailscale connects |
| `backup_encryption_enabled` | `false` | Enable age-encrypted backups |

### Deploying with Hermzner

```bash
# Prerequisites
export HCLOUD_TOKEN="<hetzner-api-token>"
export TAILSCALE_AUTH_KEY="tskey-auth-<key>"

# Clone
git clone <hermzner-repo>
cd sources/hermzner

# Configure
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# Edit terraform.tfvars with your SSH key

# Deploy
./deploy.sh
```

The deploy script runs a 7-phase pipeline: prerequisites → Terraform → inventory → SSH readiness → Ansible → verification → summary.

### Post-Deployment

```bash
# Deploy output shows:
Server IP:      123.123.123.123
Tailscale IP:   100.x.x.x
SSH Tunnel (dashboard): ssh -L 9119:127.0.0.1:9119 hermes@100.x.x.x
SSH Tunnel (API):       ssh -L 8642:127.0.0.1:8642 hermes@100.x.x.x

# Verify
ssh -L 8642:127.0.0.1:8642 hermes@100.x.x.x -N &
curl http://127.0.0.1:8642/health
```

---

## Environment Variables Reference

### Core Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | -- | Anthropic API key (primary provider) |
| `OPENAI_API_KEY` | -- | OpenAI API key |
| `GEMINI_API_KEY` | -- | Google Gemini API key |
| `HERMES_HOME` | `~/.hermes` | Hermes config and state directory |
| `HERMES_DASHBOARD` | `0` | Enable web dashboard (`1` or `true`) |
| `HERMES_DASHBOARD_HOST` | `127.0.0.1` | Dashboard bind address |
| `HERMES_DASHBOARD_PORT` | `9119` | Dashboard HTTP port |
| `API_SERVER_HOST` | `127.0.0.1` | Gateway API bind address |
| `API_SERVER_PORT` | `8642` | Gateway API port |
| `API_SERVER_ENABLED` | `false` | Enable REST API server |
| `API_SERVER_KEY` | -- | API authentication token |

### Gateway Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HERMES_API_URL` | `http://127.0.0.1:8642` | Gateway URL (for external consumers) |
| `HERMES_API_TOKEN` | -- | Gateway bearer auth token |
| `HERMES_PASSWORD` | -- | Dashboard session password |
| `HERMES_WORKSPACE_PORT` | `3000` | Workspace Web UI port |
| `HERMES_ALLOW_INSECURE_REMOTE` | `0` | Bypass password guard on non-loopback |
| `TRUST_PROXY` | `0` | Trust `X-Forwarded-For` headers |
| `COOKIE_SECURE` | `auto` | Force Secure flag on cookies |

### Channel / Platform Variables

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `DISCORD_BOT_TOKEN` | Discord bot token |
| `SLACK_BOT_TOKEN` | Slack bot token |
| `SLACK_APP_TOKEN` | Slack app-level token |
| `WHATSAPP_ACCESS_TOKEN` | WhatsApp Cloud API token |
| `WHATSAPP_PHONE_NUMBER_ID` | WhatsApp sender phone number ID |
| `MATRIX_ACCESS_TOKEN` | Matrix access token |
| `SIGNAL_SERVICE` | Signal service endpoint |
| `QQ_APP_ID` | QQ bot app ID |
| `QQ_APP_TOKEN` | QQ bot token |

### MCP / ACP Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_PORT` | -- | Override MCP server listen port |
| `MCP_HOST` | `127.0.0.1` | MCP server bind address |
| `ACP_PORT` | -- | Override ACP server listen port |
| `ACP_HOST` | `127.0.0.1` | ACP server bind address |

### Environment Variables from Source

See `hermes_cli/main.py` for the full list of configurable environment variables. Key ones:

| Variable | Default | Description |
|----------|---------|-------------|
| `HERMES_UID` | -- | Container UID remapping (Docker entrypoint) |
| `HOME` | `/root` | Home directory |
| `TZ` | `UTC` | Timezone |
| `NODE_ENV` | `production` | Node.js environment |
| `STREAM_ACCEPTED_TIMEOUT_MS` | `120000` | SSE accepted state timeout |
| `STREAM_HANDOFF_TIMEOUT_MS` | `300000` | SSE handoff timeout |

---

## Updates and Maintenance

### Updating via Hermes CLI

```bash
# Auto-update (managed installs: git-reset + uv pip install -e .)
hermes update

# Check version
hermes --version
```

### Uninstalling

```bash
# Remove the hermes binary and managed install
hermes uninstall
```

The uninstaller (`hermes_cli/uninstall.py`) removes the managed installation;
profile data in `~/.hermes/` is preserved by default unless explicitly removed.

### Updating Quadlet Deployment

```bash
# Pull the latest image
podman pull docker.io/nousresearch/hermes-agent:latest

# Restart the service
systemctl --user restart hermes-agent.service

# Verify
systemctl --user status hermes-agent.service
```

### Backup

```bash
# Backup hermes state directory
tar -czf hermes-backup-$(date +%Y%m%d).tar.gz ~/.hermes/ ~/.config/hermes/

# Hermzner automated backup
# Runs daily at 02:00 via cron
# Archives: /home/hermes/backups/hermes-backup-*.tar.gz[.age]
```

### Restoring from Backup

```bash
# Stop the service
systemctl --user stop hermes-agent.service

# Restore state
tar -xzf hermes-backup-*.tar.gz -C ~/

# Restart
systemctl --user start hermes-agent.service
```

---

## Scale-to-Zero with Chronos

For hosted/cloud deployments where an idle gateway should not burn a VM,
Hermes ships a **Chronos** cron provider (`plugins/cron_providers/chronos/`)
that lets the gateway **scale to zero** while still firing scheduled jobs.

### How It Works

Chronos delegates the "wake me at time T" trigger to Nous infrastructure:

1. The agent computes each job's next-fire time and asks NAS to arm a one-shot.
2. The machine stays off (scaled to zero).
3. NAS calls the agent back at fire time over an **authenticated webhook** —
   the machine wakes only on a NAS→agent fire.

The full contract is documented in `docs/chronos-managed-cron-contract.md`.

### Enabling

Chronos is inert unless selected as the scheduler provider:

```yaml
# config.yaml
cron:
  provider: chronos        # scheduler provider (Axis B), not inference
```

The agent only arms *next-fire* triggers — never a periodic wake loop, which
would negate scale-to-zero.

### Relationship to the Built-in Ticker

Without a provider set, the built-in in-process scheduler ticks every 60s
inside the gateway (there is no standalone cron daemon). Chronos replaces that
tick loop with NAS-mediated one-shot arming, so the container can be fully
stopped between fires. See [[hermes-agent-cron]] for the scheduler internals.

---

## Troubleshooting

### Container Not Starting

```bash
# Check systemd unit status
systemctl --user status hermes-agent.service

# View journal logs
journalctl --user -u hermes-agent.service -n 50 --no-pager

# Check podman container
podman ps -a --filter name=hermes
podman logs hermes
podman inspect hermes | jq '.[0].State.Status'
```

### Health Check Failures

```bash
# Check endpoints manually
curl -v http://localhost:8642/health
curl -v http://localhost:9119/api/status

# Verify service is listening
ss -tlnp | grep -E '8642|9119'

# Check podman health check status
podman healthcheck run hermes
```

### API Key Issues

```bash
# Verify environment file exists and has correct permissions
ls -la ~/.config/hermes/agent.env
test -r ~/.config/hermes/agent.env && echo "readable"

# Verify keys are loaded (inside container)
podman exec hermes env | grep -E 'API_KEY|TOKEN'

# Test provider connectivity
podman exec hermes hermes doctor
```

### MCP Server Not Connecting

```bash
# Verify MCP server is running
podman exec hermes hermes mcp status

# Check MCP server logs
journalctl --user -u hermes-agent.service | grep -i mcp

# Test MCP server directly
podman exec hermes hermes mcp serve --verbose
```

### Gateway Not Reaching Platforms

```bash
# Check platform configuration
podman exec hermes hermes gateway status

# Check platform-specific env vars
podman exec hermes env | grep -E 'TELEGRAM|DISCORD|SLACK'

# Verify network connectivity
podman exec hermes curl -s https://api.telegram.org
```

### Port Conflicts (Host Networking)

```bash
# Check what's using the ports
sudo lsof -i :8642
sudo lsof -i :9119

# If ports are in use, configure alternatives:
# Environment=API_SERVER_PORT=8643
# Environment=HERMES_DASHBOARD_PORT=9120
```

### Permission Issues

```bash
# Volume mount permissions
ls -la ~/.hermes/
chmod 755 ~/.hermes/

# Environment file permissions
chmod 600 ~/.config/hermes/agent.env

# SELinux (if enabled)
ls -Z ~/.hermes/
restorecon -R ~/.hermes/
```

### SSH Tunnel Issues

```bash
# Test tunnel connection (verbose)
ssh -v -L 9119:127.0.0.1:9119 hermes@<remote-host> -N

# Check for existing tunnels
lsof -i :9119

# Use different local port if 9119 is taken
ssh -L 9118:127.0.0.1:9119 hermes@<remote-host> -N
```

---

## Key Source Files

| File | Purpose |
|------|---------|
| `hermes_cli/main.py` | CLI entry point (~12k lines, god file) |
| `gateway/run.py` | Gateway bootstrap |
| `gateway/config.py` | Platform configuration |
| `agent/conversation_loop.py` | Agent conversation loop |
| `mcp_serve.py` | MCP messaging bridge |
| `acp_adapter/server.py` | ACP adapter |
| `tools/mcp_tool.py` | MCP client (MCPServerTask) |
| `Dockerfile` | Container image (pinned SQLite build, s6-overlay) |
| `docker-compose.yml` | Docker Compose configuration |
| `docker-compose.windows.yml` | Windows Docker Compose variant |
| `docker/` | s6-overlay units, entrypoint, cont-init scripts |
| `flake.nix` | Nix flake |
| `nix/` | NixOS module tree, packages, overlays |
| `setup-hermes.sh` | Clone setup script (desktop/server + Termux) |
| `hermes_bootstrap.py` | UTF-8 stdio bootstrap (Windows, first import) |
| `constraints-termux.txt` | Termux dependency pins |
| `native/fts5_cjk/` | CJK FTS5 SQLite extension for native installs |
| `hermes_constants.py` | `get_hermes_home()` profile-aware paths |
| `hermes_cli/gateway.py` | `hermes gateway install/uninstall` systemd/launchd mgmt |
| `hermes_cli/observability/` | OTLP metrics/traces/logs relay + shared metrics schema |
| `plugins/cron_providers/chronos/` | Scale-to-zero NAS-mediated cron provider |
| `hermes_cli/uninstall.py` | `hermes uninstall` |

---

## Related

- [[hermes-agent]] -- Wiki entry
- [[hermes-agent-architecture]] -- System architecture
- [[hermes-agent-quadlet]] -- Quadlet deployment asset
- [[hermes-agent-docker]] -- Docker packaging
- [[hermes-agent-docker-deployment]] -- Docker deployment guide
- [[hermes-acp-agent]] -- ACP agent asset
- [[hermes-mcp-serve]] -- MCP server asset
- [[hermes-gateway-platforms]] -- Gateway platforms asset

## Related

- [[wiki/hermes-agent.md]] -- Wiki entry
- [[domains/architecture/hermes-agent-architecture.md]] -- System architecture
- [[domains/mcp/hermes-mcp-implementation.md]] -- MCP implementation
- [[domains/acp/hermes-acp-implementation.md]] -- ACP implementation
- [[domains/api/hermes-gateway-api.md]] -- Gateway API reference
- [[assets/agent-references/hermes-agent-reference.md]] -- Agent profile
- [[assets/mcp-servers/hermes-mcp-serve.md]] -- MCP server asset
- [[assets/acp-agents/hermes-acp-agent.md]] -- ACP agent asset
- [[assets/api-clients/hermes-gateway-platforms.md]] -- Gateway platforms
- [[assets/deployment/hermes-agent-quadlet.md]] -- Quadlet deployment asset
- [[domains/deployment/hermzner-deployment.md]] -- Hermzner deployment guide
- [[assets/deployment/hermzner-terraform-ansible.md]] -- Hermzner infra-as-code
- [[hermes-workspace]] -- Workspace deployment
- [[hermes-agent-configuration]] -- Config reference
- [[hermes-agent-cron]] -- Cron scheduler architecture
- [[hermes-agent-kanban]] -- Multi-agent kanban architecture
- [[hermes-agent-observability]] -- Observability architecture
