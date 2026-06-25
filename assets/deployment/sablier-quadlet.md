---
name: sablier-quadlet
tags: [sablier, quadlet, golang, scale-to-zero, reverse-proxy, lifecycle, systemd, container, automation, acp, ai-llm, cli, dashboard, deployment, docker, event-bus, git, monitoring, plugin-sdk, security, storage, webhook]
description: Sablier Quadlet Deployment (Rootless Podman)
---

# Sablier Quadlet Deployment (Rootless Podman)

**Source:** `sources/sablier/`
**Raw:** `raw/sablier/sablier.xml` (1.1M)
**Codegraph:** `graphs/sablier/` (6.5M)

This document provides Quadlet `.container` files for deploying Sablier as a rootless Podman service via systemd user units, along with integrated reverse proxy and agent service examples.

---

## Configuration Variants

Choose the appropriate configuration for your deployment:

1. **Standalone**: Sablier alone, accessible on port 10000. Configure plugins externally.
2. **Sablier + Traefik**: Full integrated setup with Traefik reverse proxy and Yaegi plugin.
3. **Agent service with idle timeout**: An agent service (Hermes, n8n) managed by Sablier with idle timeouts.

---

## Variant 1: Standalone Sablier Service

Create `~/.config/containers/systemd/sablier.container`:

```ini
[Unit]
Description=Sablier scale-to-zero service
After=network-online.target
Wants=network-online.target

[Container]
Image=docker.io/sablierapp/sablier:latest
Exec=start --provider.name=podman

# Expose Sablier API (only needed if proxy is on another host/network)
PublishPort=10000:10000

# Mount the rootless Podman socket
Volume=/run/user/%U/podman/podman.sock:/run/podman/podman.sock:Z

# Session configuration
Environment=SABLIER_SESSIONS_DEFAULT_DURATION=5m
Environment=SABLIER_SESSIONS_EXPIRATION_INTERVAL=20s
Environment=SABLIER_STRATEGY_BLOCKING_DEFAULT_TIMEOUT=1m
Environment=SABLIER_STRATEGY_BLOCKING_DEFAULT_REFRESH_FREQUENCY=5s

# Shared network with proxy and managed services
Network=sablier-net

# Keep state across restarts (optional)
Volume=sablier-data:/data:Z
Environment=SABLIER_STORAGE_FILE=/data/sablier-sessions.json

# Logging
Environment=SABLIER_LOGGING_LEVEL=info

# Optional: enable Prometheus metrics
# Environment=SABLIER_SERVER_METRICS_ENABLED=true

# Optional: enable OpenTelemetry tracing
# Environment=SABLIER_TRACING_ENABLED=false
# Environment=SABLIER_TRACING_ENDPOINT=http://jaeger:4318

[Service]
Restart=always
RestartSec=10s

[Install]
WantedBy=default.target
```

### Enable and Start

```bash
# Create the shared network first
podman network create sablier-net

# Reload systemd user unit files
systemctl --user daemon-reload

# Enable to start on login
systemctl --user enable sablier

# Start now
systemctl --user start sablier

# Check status
systemctl --user status sablier

# View logs
journalctl --user -u sablier -f
```

### Verify

```bash
curl http://localhost:10000/health
# Expected: 200 OK
```

---

## Variant 2: Sablier + Traefik Integrated Setup

### sablier-traefik.network (Podman network)

Create `~/.config/containers/systemd/sablier-traefik.network`:

```ini
[Network]
Description=Shared network for Sablier and Traefik
```

### sablier.container

```ini
[Unit]
Description=Sablier scale-to-zero service
After=network-online.target
Wants=network-online.target

[Container]
Image=docker.io/sablierapp/sablier:latest
Exec=start --provider.name=podman

# Do not publish ports externally; Traefik connects via internal network
# PublishPort=10000:10000

Volume=/run/user/%U/podman/podman.sock:/run/podman/podman.sock:Z

# Session: 5min idle, 5 sec expiry polling
Environment=SABLIER_SESSIONS_DEFAULT_DURATION=5m
Environment=SABLIER_SESSIONS_EXPIRATION_INTERVAL=5s
Environment=SABLIER_STRATEGY_BLOCKING_DEFAULT_TIMEOUT=1m

Network=sablier-traefik.network

# State persistence
Volume=sablier-data:/data:Z
Environment=SABLIER_STORAGE_FILE=/data/sablier-sessions.json

# Metrics
Environment=SABLIER_SERVER_METRICS_ENABLED=true

[Service]
Restart=always
RestartSec=10s

[Install]
WantedBy=default.target
```

### traefik.container (Traefik with Sablier plugin)

Create `~/.config/containers/systemd/traefik.container`:

```ini
[Unit]
Description=Traefik reverse proxy with Sablier plugin
After=sablier.service network-online.target
Wants=sablier.service network-online.target
BindsTo=sablier.service

[Container]
Image=docker.io/traefik:v3.0
PublishPort=80:80
PublishPort=443:443
# Dashboard port (optional, secure in production)
# PublishPort=8080:8080

Network=sablier-traefik.network

# Traefik static config
Volume=%T/containers/systemd/traefik.yml:/etc/traefik/traefik.yml:Z

# Traefik dynamic config (Sablier middleware definitions)
Volume=%T/containers/systemd/traefik-dynamic.yml:/etc/traefik/dynamic.yml:Z

[Service]
Restart=always
RestartSec=10s

[Install]
WantedBy=default.target
```

### Static config: `traefik.yml`

```yaml
# ~/.config/containers/systemd/traefik.yml
experimental:
  plugins:
    sablier:
      moduleName: github.com/sablierapp/sablier
      version: v1.7.0

entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"

providers:
  file:
    filename: /etc/traefik/dynamic.yml
    watch: true
  # Uncomment to use Docker/Podman provider for automatic service discovery
  # docker:
  #   endpoint: unix:///var/run/docker.sock
  #   exposedByDefault: false
```

### Dynamic config: `traefik-dynamic.yml`

```yaml
# ~/.config/containers/systemd/traefik-dynamic.yml
http:
  routers:
    whoami:
      rule: "Host(`whoami.localhost`)"
      service: whoami-service
      middlewares:
        - sablier-whoami

  services:
    whoami-service:
      loadBalancer:
        servers:
          - url: "http://whoami:80"

  middlewares:
    sablier-whoami:
      plugin:
        sablier:
          sablierUrl: "http://sablier:10000"
          group: "whoami"
          sessionDuration: "5m"
          timeout: "1m"
```

### Managed service: `whoami.container`

```ini
[Unit]
Description=whoami demo service (Sablier-managed)
After=sablier.service
Wants=sablier.service

[Container]
Image=docker.io/traefik/whoami:latest
Network=sablier-traefik.network

Label=sablier.enable=true
Label=sablier.group=whoami
Label=sablier.ready-after=3s

[Service]
Restart=always

[Install]
WantedBy=default.target
```

---

## Variant 3: Agent Service with Idle Timeout Annotations

This configuration demonstrates an agent service (e.g., n8n) that stops when idle and starts on first request.

### Agent service: `n8n-agent.container`

```ini
[Unit]
Description=n8n agent (Sablier-managed scale-to-zero)
After=sablier.service
Wants=sablier.service

[Container]
Image=docker.io/n8nio/n8n:latest
Network=sablier-net
PublishPort=5678:5678

# Required: opt into Sablier management
Label=sablier.enable=true
Label=sablier.group=n8n-agents

# After container starts, wait 15s before considering it ready
# (n8n needs time to initialize database connections)
Label=sablier.ready-after=15s

# Keep n8n running during business hours (09:00-22:00 local time)
# Outside these hours, it stops after the session duration expires
Label=sablier.running-hours=09:00-22:00

# Optional: use scale mode instead of stop (zero cold-start)
# Label=sablier.idle.replicas=1
# Label=sablier.idle.cpu=0.1
# Label=sablier.idle.memory=64m
# Label=sablier.active.cpu=0.5
# Label=sablier.active.memory=256m

# Environment
Environment=TZ=Europe/London

# Data persistence
Volume=n8n-data:/home/node/.n8n:Z

[Service]
Restart=always

[Install]
WantedBy=default.target
```

### Agent service: `openclaw-acp.container`

```ini
[Unit]
Description=OpenClaw ACP agent gateway (Sablier-managed)
After=sablier.service
Wants=sablier.service

[Container]
Image=ghcr.io/agentfield/openclaw-acp:latest
Network=sablier-net
PublishPort=8080:8080

Label=sablier.enable=true
Label=sablier.group=openclaw
Label=sablier.ready-after=5s
Label=sablier.running-hours=09:00-22:00

# Scale mode: keep at minimal resources when idle
Label=sablier.idle.replicas=1
Label=sablier.idle.cpu=0.1
Label=sablier.idle.memory=64m
Label=sablier.active.cpu=0.5
Label=sablier.active.memory=128m

[Service]
Restart=always

[Install]
WantedBy=default.target
```

### Agent service in scale mode: `hermes-workspace.container`

```ini
[Unit]
Description=Hermes Workspace (Sablier-managed, scale mode)
After=sablier.service
Wants=sablier.service

[Container]
Image=ghcr.io/hermes-workspace/hermes:latest
Network=sablier-net
PublishPort=3000:3000

Label=sablier.enable=true
Label=sablier.group=hermes

# Scale mode: container stays running but throttled when idle
# Zero cold-start latency at the cost of ~64MB idle RAM
Label=sablier.idle.replicas=1
Label=sablier.idle.cpu=0.1
Label=sablier.idle.memory=64m
Label=sablier.active.cpu=1.0
Label=sablier.active.memory=256m

# Grace period after health check
Label=sablier.ready-after=10s

[Service]
Restart=always

[Install]
WantedBy=default.target
```

---

## Podman Network Setup

Create a shared network for Sablier, reverse proxy, and managed services:

```bash
podman network create sablier-net
```

All Quadlets should use `Network=sablier-net` so the proxy can reach Sablier and the managed services by container name.

---

## Full Architecture Diagram

```
Internet
    |
    v
[Reverse Proxy Quadlet] (Caddy/Traefik with Sablier plugin)
    |                        |
    | GET /api/strategies/   | Forward request
    | blocking?group=myapp   | when ready
    |                        v
    v                   [Managed Service Quadlet]
[Sablier Quadlet]        (nginx, myapp, etc.)
    |                        ^
    | Start/Stop via         | Started/Stopped
    | Podman socket          | via Podman socket
    v                        |
[Podman Socket] ------------+
(/run/user/$UID/podman/podman.sock)
    |
    v
[Podman -- rootless container runtime]
```

### Data Flow

1. Request arrives at reverse proxy (port 80/443)
2. Proxy plugin checks if session is active via Sablier API (`http://sablier:10000`)
3. If not active, Sablier starts the container via rootless Podman socket
4. Sablier polls until healthy, returns `X-Sablier-Session-Status: ready`
5. Proxy forwards original request to the now-running container
6. Session timer starts; after `session_duration` of inactivity, Sablier stops the container
7. Webhook fires start/stop notifications (optional)

### Blocking Strategy Flow Detail

```
User/Client          Reverse Proxy          Sablier              Podman/Docker         Managed Container
    |                     |                    |                      |                      |
    |--- HTTP GET ------->|                    |                      |                      |
    |                     |--- GET /blocking ->|                      |                      |
    |                     |  ?group=myapp      |                      |                      |
    |                     |  &session_dur=5m   |                      |                      |
    |                     |  &timeout=1m      |                      |                      |
    |                     |                    |--- InstanceStart --->|                      |
    |                     |                    |                      |--- start container -->|
    |                     |                    |                      |<-- running -----------|
    |                     |                    |<-- InstanceInspect --|                      |
    |                     |                    |   (polling every 5s) |                      |
    |                     |                    |                      | (healthcheck)         |
    |                     |                    |                      |<-- healthy -----------|
    |                     |<-- 200 OK ---------|                      |                      |
    |                     |  X-Sablier-Status: |                      |                      |
    |                     |  ready             |                      |                      |
    |                     |                    |                      |                      |
    |                     |--- proxy to ------>|                      |                      |
    |                     |  running backend   |                      |                      |
    |<-- HTTP response ---|                    |                      |                      |
    |                     |                    |                      |                      |
    |  (5 minutes idle)   |                    |                      |                      |
    |                     |                    |--- InstanceStop ---->|                      |
    |                     |                    |                      |--- stop container --->|
```

---

## Startup Order

Correct systemd ordering is critical:

```ini
# sablier.container
[Install]
WantedBy=default.target

# myapp.container
After=sablier.service
Wants=sablier.service

# caddy.container or traefik.container
After=sablier.service network-online.target
Wants=sablier.service network-online.target
BindsTo=sablier.service
```

- `BindsTo=sablier.service` on the proxy ensures the proxy stops if Sablier stops
- Managed services use `Wants` (not `BindsTo`) -- they can exist without Sablier running
- `After=network-online.target` ensures networking is up before the proxy binds ports

### Starting Sequence

```bash
# 1. Create shared network (if not already)
podman network create sablier-net

# 2. Reload systemd to pick up Quadlet files
systemctl --user daemon-reload

# 3. Start Sablier first
systemctl --user start sablier

# 4. Start managed services
systemctl --user start myapp

# 5. Start reverse proxy last (binding to Sablier via BindsTo)
systemctl --user start traefik
```

---

## Monitoring and Troubleshooting

### Health Check

```bash
curl http://localhost:10000/health
# Expect: 200 OK
```

### Logs

```bash
# Sablier logs
journalctl --user -u sablier -f

# Traefik logs
journalctl --user -u traefik -f

# Managed service logs
journalctl --user -u myapp -f
```

### Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Sablier starts but can't manage containers | Podman socket not mounted or wrong path | Check `Volume=/run/user/%U/podman/podman.sock:/run/podman/podman.sock:Z` |
| Container won't stop | `sablier.enable=true` missing | Add label to container |
| Blocking request times out | Container unhealthy or slow to start | Increase `timeout` or add `sablier.ready-after` |
| Traefik plugin error 500 | Traefik can't reach Sablier | Use `Network=sablier-traefik.network` in both containers |
| SELinux preventing socket access | Missing `:Z` flag on volume mount | Add `:Z` to socket volume mount |
| Scale mode not throttling | Idle replicas not set | Ensure `sablier.idle.replicas=1` |

---

## Resource Considerations (2GB CX23 VPS)

Using Sablier on a 2GB CX23 VPS:

- **Sablier itself**: ~20MB (scratch-based Docker image)
- **Caddy with Sablier plugin**: ~50MB
- **Traefik with Sablier plugin**: ~30MB
- **Managed services (stopped)**: 0MB
- **Managed services (running)**: 100-300MB each

With 3-4 managed services:
- All stopped: ~70MB total (Sablier + proxy)
- All running: ~500MB-1.3GB total

Scale mode alternative: keep containers at minimal CPU/RAM:
- Each service at idle: ~64MB + 0.1 CPU
- Zero cold-start latency
- Higher baseline memory but predictable response times

### Practical Assumptions

| Scenario | RAM Used | Notes |
|----------|----------|-------|
| All services stopped | ~50 MB | Only Sablier + proxy running |
| 1 agent active (n8n) | ~300 MB | n8n uses ~256 MB |
| 2 agents active | ~500 MB | Peak for casual use |
| All 3 agents active | ~800 MB | Peak for heavy use |
| Scale mode (all idle) | ~250 MB | Services throttled to 64 MB each |
| Scale mode (all active) | ~800 MB | Full resources restored |

## Related

- [[sablier-architecture]] -- Architecture overview, boot flow, provider layer
- [[sablier-deployment]] -- Deployment guide with Docker/Kubernetes/proxy configs
- [[sablier]] -- Main wiki page for Sablier
