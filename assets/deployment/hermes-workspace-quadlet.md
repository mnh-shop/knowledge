---
name: hermes-workspace-quadlet
tags: [agent-gateway, container, dashboard, deployment, docker, hermes-agent, messaging, multi-platform, podman, quadlet, security, systemd, typescript]
description: Rootless Podman Quadlet deployment configuration for Hermes Workspace with companion Hermes Agent as systemd services
---

# Hermes Workspace — Rootless Podman Quadlet
**Source:** `sources/hermes-workspace/`

## Overview

Deploy hermes-workspace with its companion hermes-agent as rootless Podman Quadlet services managed by systemd. Two `.container` files define the stack, or optionally a pod for bridge networking isolation.

## Requirements

- Podman 4.0+ (rootless)
- systemd --user
- curl (for health checks)
- `~/.config/containers/systemd/` directory

## Architecture

```
systemd --user
    |
    |-- hermes-agent.service    (docker.io/nousresearch/hermes-agent:latest)
    |-- hermes-workspace.service (ghcr.io/outsourc-e/hermes-workspace:latest)
    |
    |-- Shared volume: ~/.hermes    (config, profiles, memory, sessions)
    |-- Workspace volume: ~/hermes-workspace-files
```

## Agent Quadlet

File: `~/.config/containers/systemd/hermes-agent.container`

```ini
[Unit]
Description=Hermes Agent Gateway + Dashboard
After=network-online.target
Wants=network-online.target

[Container]
Image=docker.io/nousresearch/hermes-agent:latest
ContainerName=hermes-agent
Exec=gateway run
Network=host

Environment=HERMES_DASHBOARD=1
Environment=HERMES_DASHBOARD_HOST=127.0.0.1
Environment=HERMES_DASHBOARD_PORT=9119
Environment=API_SERVER_HOST=127.0.0.1
Environment=API_SERVER_ENABLED=true
Environment=HERMES_UID=%U

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
```

## Workspace Quadlet

File: `~/.config/containers/systemd/hermes-workspace.container`

```ini
[Unit]
Description=Hermes Workspace Web UI
After=network-online.target hermes-agent.service
Wants=network-online.target
Requires=hermes-agent.service

[Container]
Image=ghcr.io/outsourc-e/hermes-workspace:latest
ContainerName=hermes-workspace
Network=host

Environment=HERMES_API_URL=http://127.0.0.1:8642
Environment=HERMES_DASHBOARD_URL=http://127.0.0.1:9119
Environment=HOST=127.0.0.1
Environment=PORT=3000
Environment=NODE_ENV=production
Environment=HERMES_PASSWORD=<your-strong-secret>

# Optional: API token when agent has API_SERVER_KEY set
# Environment=HERMES_API_TOKEN=<same-as-api-server-key>

# Optional: for TLS termination behind reverse proxy
# Environment=COOKIE_SECURE=1
# Environment=TRUST_PROXY=1

Volume=%h/.hermes:/home/workspace/.hermes:Z
Volume=%h/hermes-workspace-files:/workspace:Z

HealthCmd=curl -fsS http://127.0.0.1:3000/ >/dev/null || exit 1
HealthInterval=30s
HealthTimeout=5s
HealthStartPeriod=20s
HealthRetries=3

[Service]
Type=forking
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=default.target
```

## Alternative: Pod Approach (Bridge Networking)

Use this when you want Docker-style DNS resolution between containers instead of host networking.

### Pod Definition

File: `~/.config/containers/systemd/hermes.pod`

```ini
[Unit]
Description=Hermes Stack Pod
After=network-online.target
Wants=network-online.target

[Pod]
PodName=hermes
PublishPort=127.0.0.1:3000:3000
PublishPort=127.0.0.1:8642:8642
Network=bridge

[Install]
WantedBy=default.target
```

### Modified Container Files

Add `Pod=hermes.pod` to the `[Container]` section of both `.container` files. Workspace can then reach agent at `http://hermes-agent:8642` via Docker DNS.

In the workspace Quadlet, update:
```ini
Environment=HERMES_API_URL=http://hermes-agent:8642
Environment=HERMES_DASHBOARD_URL=http://hermes-agent:9119
```

The agent's `API_SERVER_HOST` must be `0.0.0.0` (or omitted) to bind within the pod.

## Setup Steps

```bash
# 1. Create env file for agent API keys
mkdir -p ~/.config/hermes
cat > ~/.config/hermes/agent.env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
# Add any additional provider keys
EOF
chmod 600 ~/.config/hermes/agent.env

# 2. Create Quadlet files
mkdir -p ~/.config/containers/systemd
# Copy the .container files from above into this directory

# 3. Create workspace data directory
mkdir -p ~/hermes-workspace-files

# 4. Reload systemd and start
systemctl --user daemon-reload
systemctl --user start hermes-agent.service
systemctl --user start hermes-workspace.service

# 5. Enable auto-start at login
systemctl --user enable hermes-agent.service
systemctl --user enable hermes-workspace.service

# 6. Verify
systemctl --user status hermes-agent.service
systemctl --user status hermes-workspace.service
journalctl --user -u hermes-workspace.service -f
```

## Important Considerations

### tmux Requirement for Swarm

The swarm worker orchestration system relies on tmux running inside the container. The `node:22-slim` image does NOT include tmux. Options:
- Install tmux in a custom Dockerfile.
- Run workers outside the container (connect to the same `~/.hermes/profiles/` directory).
- Deploy the workspace outside the container (direct Node.js or via Nix) for full swarm support.

### Python Requirement

Needed for the PTY terminal helper (`scripts/pty-helper.py`). The Dockerfile includes Python 3. If using a different image, ensure python3 is available.

### Shared hermes Data

The workspace needs read/write access to `~/.hermes/` (profiles, config, memory). Both containers must share the same volume. The `:Z` flag enables SELinux labeling for Podman.

### UID/GID Mapping

Rootless Podman maps host UID to container UID. The entry point script auto-remaps UID/GID via `HERMES_UID`/`HERMES_GID`. The workspace container user is `workspace` (UID 10010).

### Secrets Management

For production, use systemd credential files or `EnvironmentFile=` pointing to a secure location (e.g., `sops`-encrypted or `pass`-managed) rather than inline `Environment=` directives with secrets.

### SSE Stability

The workspace uses SSE (Server-Sent Events) for streaming. Host networking is recommended to avoid proxy-level connection drops. If using bridge networking, ensure the reverse proxy has proper SSE configuration: no buffering, `Connection: keep-alive`.

## Updating

```bash
# Pull latest images
podman pull docker.io/nousresearch/hermes-agent:latest
podman pull ghcr.io/outsourc-e/hermes-workspace:latest

# Restart services
systemctl --user restart hermes-agent.service
systemctl --user restart hermes-workspace.service
```

## Troubleshooting

```bash
# View logs
journalctl --user -u hermes-workspace.service -f
journalctl --user -u hermes-agent.service -f

# Check container state
podman ps -a --pod

# Test networking (host mode)
curl -s http://127.0.0.1:8642/health
curl -s http://127.0.0.1:3000/

# Test networking (pod mode)
podman exec hermes-workspace curl -s http://hermes-agent:8642/health

# Restart after config change
systemctl --user restart hermes-workspace.service
```

## Related

- [[hermes-workspace]] -- Wiki entry for Hermes Workspace
- [[hermes-workspace-deployment]] -- Deployment guide
- [[hermes-workspace-architecture]] -- System architecture
- [[hermes-agent-quadlet]] -- Hermes Agent Quadlet deployment
- [[hermes-agent-deployment]] -- Agent deployment guide
