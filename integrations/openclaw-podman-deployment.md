---
name: openclaw-podman-deployment
type: integration
tags: [openclaw, podman, integration, deployment, quadlet]
description: "Deploy OpenClaw under rootless Podman Quadlet with multi-channel support, port mapping, GPU passthrough, volume persistence, and auto-update"
---

# Integration: OpenClaw — Podman Quadlet Deployment

## Overview

OpenClaw deployed as a rootless Podman Quadlet service exposes two ports — gateway API (18789) and HTTP API (18790) — with optional GPU passthrough for local LLM inference. Multi-channel support (Discord, Telegram, CLI) uses an environment file. Auto-update via `podman auto-update` with a daily timer keeps the image current.

## Architecture

```
openclaw-auto-update.timer (daily)
  └─ openclaw-gateway.container
       Ports: 18789, 18790
       Vol:   ~/.openclaw → /home/node/.openclaw
       Env:   channels.env (Discord, Telegram)
       Device: /dev/dri (optional)
```

## Configuration

`~/.config/containers/systemd/openclaw-gateway.container`:
```ini
[Unit]
Description=OpenClaw Gateway
After=network-online.target
[Container]
Image=ghcr.io/openclaw/openclaw:latest
ContainerName=openclaw
Exec=node openclaw.mjs gateway --port 18789 --bind lan
PublishPort=127.0.0.1:18789:18789 PublishPort=127.0.0.1:18790:18790
Volume=%h/.openclaw:/home/node/.openclaw:Z
Environment=NODE_ENV=production
EnvironmentFile=%h/.config/openclaw/channels.env
User=1000
Label=io.containers.autoupdate=registry
# Device=/dev/dri
HealthCmd=node -e "fetch('http://127.0.0.1:18789/healthz').then(r=>process.exit(r.ok?0:1))"
HealthInterval=180s HealthRetries=3
[Service]
Restart=always
[Install]
WantedBy=default.target
```

Auto-update timer:
```ini
# openclaw-auto-update.timer
[Timer]
OnCalendar=daily
Persistent=true
[Install]
WantedBy=timers.target
```

### Deployment
```bash
mkdir -p ~/.config/containers/systemd ~/.openclaw ~/.config/openclaw
cat > ~/.config/openclaw/channels.env << 'EOF'
DISCORD_BOT_TOKEN=...
TELEGRAM_BOT_TOKEN=...
EOF
chmod 600 ~/.config/openclaw/channels.env
podman pull ghcr.io/openclaw/openclaw:latest
systemctl --user daemon-reload && systemctl --user start openclaw-gateway.service
systemctl --user enable --now openclaw-auto-update.timer
curl -s http://127.0.0.1:18789/healthz
```

## Related

- [[openclaw]] — Multi-channel agent gateway
- [[podman]] — Rootless container runtime
- [[tank-os]] — Bootable OS image with OpenClaw
- [[podlet]] — Quadlet file generator
