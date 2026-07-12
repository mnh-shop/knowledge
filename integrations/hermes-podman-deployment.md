---
name: hermes-podman-deployment
type: integration
tags: [hermes-agent, podman, integration, deployment, quadlet]
description: "Deploy Hermes Agent under rootless Podman Quadlet with systemd auto-update, health checks, secrets injection, and persistent volumes"
---

# Integration: Hermes Agent — Podman Quadlet Deployment

## Overview

Hermes Agent runs as a rootless Podman container managed by Quadlet — systemd's native container unit format. This gives Hermes automatic restart, dependency ordering, resource limits, and `podman auto-update` integration for daily image upgrades. The single `.container` unit uses an environment file for API keys, bind-mounted config, and health check polling.

## Architecture

```
systemd --user
  hermes-auto-update.timer (daily)
    └─ hermes-agent.container
         Image: hermes-agent:latest
         Ports: 8642 (API), 9119 (dashboard)
         Vol:   ~/.hermes → /opt/data
         Env:   ~/.config/hermes/agent.env (chmod 600)
         Health: GET /health every 10s
         Label: io.containers.autoupdate=registry
```

## Configuration

`~/.config/containers/systemd/hermes-agent.container`:
```ini
[Unit]
Description=Hermes Agent
After=network-online.target
[Container]
Image=docker.io/nousresearch/hermes-agent:latest
ContainerName=hermes
Exec=gateway run
Environment=HERMES_DASHBOARD=1 API_SERVER_ENABLED=true API_SERVER_PORT=8642
EnvironmentFile=%h/.config/hermes/agent.env
Volume=%h/.hermes:/opt/data:Z
PublishPort=127.0.0.1:8642:8642 PublishPort=127.0.0.1:9119:9119
Label=io.containers.autoupdate=registry
HealthCmd=curl -fsS http://localhost:8642/health || exit 1
HealthInterval=10s HealthRetries=5
[Service]
Type=forking
Restart=on-failure
[Install]
WantedBy=default.target
```

Auto-update timer (`hermes-auto-update.timer`):
```ini
[Timer]
OnCalendar=daily
Persistent=true
[Install]
WantedBy=timers.target
```

### Deployment
```bash
mkdir -p ~/.config/containers/systemd ~/.hermes ~/.config/hermes
echo "ANTHROPIC_API_KEY=sk-ant-..." > ~/.config/hermes/agent.env
chmod 600 ~/.config/hermes/agent.env
podman pull docker.io/nousresearch/hermes-agent:latest
systemctl --user daemon-reload && systemctl --user start hermes-agent.service
systemctl --user enable --now hermes-auto-update.timer
curl -s http://127.0.0.1:8642/health
```

## Related

- [[hermes-agent]] — Core agent runtime deployment target
- [[podman]] — Rootless container engine underlying Quadlet
- [[podlet]] — Quadlet file generator from podman run/compose
- [[hermes-agent-docker]] — Docker Compose alternative deployment
- [[assets/deployment/hermes-agent-quadlet.md]] — Full Quadlet reference
