---
name: sablier-deployment
tags: [acp, container, deployment, docker, event-bus, git, golang, monitoring, plugin-sdk, podman, quadlet, reverse-proxy, sablier, scale-to-zero, systemd, webhook]
description: Sablier Deployment Guide
source: sources/sablier/
---

# Sablier Deployment Guide

**Source:** `sources/sablier/`
**Raw:** `raw/sablier/sablier.xml` (1.1M)
**Codegraph:** `graphs/sablier/` (6.5M)

Guide for deploying Sablier as a scale-to-zero daemon with Podman, Docker, or Kubernetes, including reverse proxy integration.

---

## Quick Start

### Docker
```bash
docker run -p 10000:10000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  sablierapp/sablier:latest start --provider.name=docker
```

### Podman
```bash
podman run -p 10000:10000 \
  -v /run/podman/podman.sock:/run/podman/podman.sock:Z \
  sablierapp/sablier:latest start --provider.name=podman
```

### Verify
```bash
curl http://localhost:10000/health
# {"status":"ok"}
```

---

## Configuration

Sablier uses Viper for configuration with precedence: Config file -> Environment variables -> CLI arguments.

### Configuration File
Search paths: `/etc/sablier/`, `$XDG_CONFIG_HOME/`, `$HOME/.config/`, `.`.

Full sample config: `sablier.sample.yaml` in the source repo.

### Key Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SABLIER_PROVIDER_NAME` | - | Selects provider (docker, podman, dockerswarm, kubernetes, proxmoxlxc) |
| `SABLIER_PROVIDER_PODMAN_URI` | `unix:///run/podman/podman.sock` | Podman socket URI |
| `SABLIER_SESSIONS_DEFAULT_DURATION` | `5m` | Default session TTL |
| `SABLIER_STRATEGY_BLOCKING_DEFAULT_TIMEOUT` | `1m` | Max wait for container readiness |
| `SABLIER_WEBHOOKS_ENDPOINTS_0_URL` | - | Webhook target URL |

### Config File Example (YAML)
```yaml
provider:
  name: podman
  podman:
    uri: unix:///run/podman/podman.sock

sessions:
  default-duration: 5m
  expiration-interval: 20s

strategy:
  blocking:
    default-timeout: 1m
    refresh-frequency: 5s
  dynamic:
    default-theme: hacker-terminal
    show-details-by-default: true

server:
  port: 10000
  metrics:
    enabled: true

webhooks:
  endpoints:
    - url: https://uptime.example.com/api/push/xxx
      events: [started, stopped]
```

---

## Podman Rootless Deployment

### Socket Path
Rootless Podman exposes its socket at `/run/user/$UID/podman/podman.sock`. Sablier expects it at `/run/podman/podman.sock` (Docker client default). Map it:

```bash
podman run -p 10000:10000 \
  -v /run/user/1000/podman/podman.sock:/run/podman/podman.sock:Z \
  sablierapp/sablier:latest start --provider.name=podman
```

Or configure a custom URI:
```bash
podman run -p 10000:10000 \
  -v /run/user/1000/podman/podman.sock:/run/user/1000/podman/podman.sock:Z \
  -e SABLIER_PROVIDER_PODMAN_URI=unix:///run/user/1000/podman/podman.sock \
  sablierapp/sablier:latest start --provider.name=podman
```

### Managed Workload Labels
Each container managed by Sablier needs labels:

```bash
podman run -d \
  --label sablier.enable=true \
  --label sablier.group=myapp \
  --label sablier.running-hours="Mon-Fri 09:00-17:00" \
  nginx:latest
```

---

## Reverse Proxy Integration

### Traefik (via Docker provider)

**docker-compose.yml:**
```yaml
services:
  sablier:
    image: sablierapp/sablier:latest
    command: start --provider.name=docker
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    ports:
      - "10000:10000"

  whoami:
    image: traefik/whoami
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.whoami.rule=Host(`whoami.localhost`)"
      - "traefik.http.routers.whoami.middlewares=sablier@docker"
      - "traefik.http.services.whoami.loadbalancer.server.port=80"
      - "sablier.enable=true"
      - "sablier.group=whoami"
```

**static.yml (Traefik config):**
```yaml
experimental:
  plugins:
    sablier:
      moduleName: github.com/sablierapp/sablier
      version: v1.7.0
```

**dynamic.yml:**
```yaml
http:
  middlewares:
    sablier:
      plugin:
        sablier:
          sablierUrl: http://sablier:10000
          group: whoami
          sessionDuration: 5m
          timeout: 1m
          dynamic:
            displayName: whoami
            theme: hacker-terminal
            refreshFrequency: 5000
            showDetails: true
```

### Caddy (via Docker provider)

Build custom Caddy with Sablier module:
```bash
xcaddy build --with github.com/sablierapp/caddy-sablier
```

**Caddyfile:**
```caddy
whoami.localhost {
    route {
        sablier {
            sablier_url http://sablier:10000
            group whoami
            session_duration 5m
            timeout 1m
            dynamic {
                display_name "whoami"
                theme hacker-terminal
                refresh_frequency 5000
                show_details true
            }
        }
        reverse_proxy whoami:80
    }
}
```

### Nginx (Proxy-WASM)

1. Download the Proxy-WASM plugin binary from the [sablier-proxywasm-plugin](https://github.com/sablierapp/sablier-proxywasm-plugin) releases
2. Install Nginx with `ngx_wasm_module` support (OpenResty or custom build with wasm support)
3. Load the WASM filter in the Nginx configuration:

```nginx
# nginx.conf
http {
    wasm_module /path/to/sablier-proxywasm-plugin.wasm;

    server {
        listen 80;
        server_name whoami.localhost;

        location / {
            wasm_proxy_wasm sablier_proxywasm_plugin '{
                "sablier_url": "http://sablier:10000",
                "group": "whoami",
                "session_duration": "5m",
                "timeout": "1m",
                "strategy": "blocking"
            }';
            proxy_pass http://whoami:80;
        }
    }
}
```

### Envoy (Proxy-WASM)

1. Download the Proxy-WASM plugin binary from [sablier-proxywasm-plugin](https://github.com/sablierapp/sablier-proxywasm-plugin)
2. Configure Envoy with the WASM http filter:

```yaml
# envoy.yaml
static_resources:
  listeners:
  - name: listener_0
    address: { socket_address: { address: 0.0.0.0, port_value: 80 } }
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          codec_type: AUTO
          stat_prefix: ingress_http
          route_config:
            name: local_route
            virtual_hosts:
            - name: backend
              domains: ["*"]
              routes:
              - match: { prefix: "/" }
                route: { cluster: whoami_service }
          http_filters:
          - name: envoy.filters.http.wasm
            typed_config:
              "@type": type.googleapis.com/udpa.type.v1.TypedStruct
              type_url: type.googleapis.com/envoy.extensions.filters.http.wasm.v3.Wasm
              value:
                config:
                  name: sablier_plugin
                  root_id: sablier_root_id
                  vm_config:
                    runtime: envoy.wasm.runtime.v8
                    code:
                      local: { filename: /etc/envoy/sablier-proxywasm-plugin.wasm }
                  configuration:
                    "@type": type.googleapis.com/google.protobuf.StringValue
                    value: |
                      {
                        "sablier_url": "http://sablier:10000",
                        "group": "whoami",
                        "session_duration": "5m",
                        "timeout": "1m",
                        "strategy": "blocking"
                      }
          - name: envoy.filters.http.router
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router
  clusters:
  - name: whoami_service
    connect_timeout: 0.25s
    type: STRICT_DNS
    lb_policy: ROUND_ROBIN
    load_assignment:
      cluster_name: whoami_service
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address:
                address: whoami
                port_value: 80
  - name: sablier_service
    connect_timeout: 0.25s
    type: STRICT_DNS
    lb_policy: ROUND_ROBIN
    load_assignment:
      cluster_name: sablier_service
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address:
                address: sablier
                port_value: 10000
```

### Apache APISIX

Configure an APISIX route with the Sablier plugin:

```yaml
routes:
  - uri: /*
    host: whoami.localhost
    plugins:
      sablier:
        sablier_url: http://sablier:10000
        group: whoami
        session_duration: 5m
        timeout: 1m
        strategy: blocking
    upstream:
      nodes:
        "whoami:80": 1
```

---

## Kubernetes Deployment

### Helm Chart
```bash
helm repo add sablierapp https://sablierapp.github.io/helm-charts
helm install sablier sablierapp/sablier
```

### RuntimeClass
Instance names use `namespace_type_name` format (e.g. `default_deployment_nginx`).
Supported resource types: Deployments, StatefulSets, CNPG clusters.
Scales via replicas to 0/1+.

---

## File-Backed Persistence

For session state recovery across restarts, store sessions to disk:

```bash
sablier start --storage.file /data/sablier-sessions.json
```

Optional, stateless by default (no recovery on restart).

---

## Monitoring

### Health Check
```bash
GET /health
# {"status":"ok"}
```

### Prometheus Metrics
```yaml
server:
  metrics:
    enabled: true
```
Available at `GET /metrics`.

### SSE Events
```bash
GET /api/events
```
Server-sent events stream for real-time session state changes.

---

## Health Check Configuration

Sablier determines container readiness based on the provider's inspection:

### Docker/Podman Container Health

If a container has a HEALTHCHECK instruction in its Dockerfile or `--health-cmd` at runtime:

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
```

Sablier will check `Container.State.Health.Status` and only report `ready` when the status is `healthy`.

If no health check is defined, Sablier reports `ready` as soon as the container state is `running`.

### `sablier.ready-after` Grace Period

For services that bind ports before they can actually serve traffic (e.g., JVM applications, database containers):

```yaml
services:
  myapp:
    image: myapp:latest
    labels:
      - "sablier.enable=true"
      - "sablier.group=myapp"
      - "sablier.ready-after=30s"  # extra 30s settling time after container is "ready"
```

The grace period counts from when the instance first becomes ready in a session. It does not reset on subsequent requests. This is enforced by `InstanceInfo.IsReady()`:

```go
func (instance InstanceInfo) IsReady() bool {
    if instance.Status != InstanceStatusReady {
        return false
    }
    if instance.ReadyAfter == 0 || instance.ReadyAt == nil {
        return true
    }
    return time.Since(*instance.ReadyAt) >= instance.ReadyAfter
}
```

### Blocking Strategy Timeout

Configured via `strategy.blocking.default-timeout` (default 1m). The polling checks at `BlockingRefreshFrequency` (default 5s). If the timeout expires before the container is healthy, the API returns an error:

```json
{"error": "request timeout", "code": 408}
```

---

## Agent Service Integration

### Stopping Hermes Workspace on Idle

Label the Hermes workspace container:

```yaml
services:
  hermes-workspace:
    image: ghcr.io/hermesapp/workspace:latest
    labels:
      - "sablier.enable=true"
      - "sablier.group=hermes"
      - "sablier.ready-after=10s"
```

Configure the reverse proxy plugin to target the `hermes` group with a session duration of 30m:

```yaml
# Traefik middleware
sablier:
  sablierUrl: http://sablier:10000
  group: hermes
  sessionDuration: 30m
  timeout: 2m
```

### Starting OpenClaw on First Request

Label the OpenClaw ACP container:

```yaml
services:
  openclaw-acp:
    image: ghcr.io/agentfield/openclaw-acp:latest
    labels:
      - "sablier.enable=true"
      - "sablier.group=openclaw"
      - "sablier.running-hours=09:00-22:00"  # keep warm during business hours
```

### Keeping n8n Warm During Business Hours

```yaml
services:
  n8n:
    image: n8nio/n8n:latest
    labels:
      - "sablier.enable=true"
      - "sablier.group=n8n"
      - "sablier.running-hours=08:00-20:00"
    environment:
      - TZ=Europe/London
```

The `sablier.running-hours` label ensures n8n is automatically started at 08:00 and stays running until 20:00. Outside these hours, it stops after the default idle timeout.

### Scale Mode for Agent Services (Zero Cold Start)

For agent services that need sub-second response times:

```yaml
services:
  mission-control:
    image: ghcr.io/agentfield/mission-control:latest
    labels:
      - "sablier.enable=true"
      - "sablier.group=agentfield"
      - "sablier.idle.replicas=1"     # keep running when idle
      - "sablier.idle.cpu=0.1"        # throttle to 0.1 CPU
      - "sablier.idle.memory=64m"     # throttle to 64 MB
      - "sablier.active.cpu=1.0"      # restore to 1 CPU on request
      - "sablier.active.memory=256m"  # restore to 256 MB on request
```

---

## Resource Savings Analysis

### VPS Scenario: 3 Managed Services on 2 vCPU / 4 GB VPS

| Service | Running (Active) | Stopped (Idle) | Scale Mode Idle | Savings (Stop) | Savings (Scale) |
|---------|-----------------|----------------|-----------------|----------------|-----------------|
| Hermes Workspace | 128 MB / 0.3 CPU | 0 | 64 MB / 0.1 CPU | 128 MB | 64 MB |
| n8n | 256 MB / 0.5 CPU | 0 | 64 MB / 0.1 CPU | 256 MB | 192 MB |
| OpenClaw ACP | 64 MB / 0.2 CPU | 0 | 64 MB / 0.1 CPU | 64 MB | 0 MB |
| **Total** | **448 MB / 1.0 CPU** | **0 MB / 0 CPU** | **192 MB / 0.3 CPU** | **448 MB (peak)** | **256 MB (idle)** |

### Practical Observations

- **Cold-start latency**: 3-10 seconds for Docker/Podman with cached images, 15-30 seconds for first pull
- **Memory fragmentation**: Stopped containers release all memory to the OS, benefiting other running services
- **CPU savings**: Near-zero CPU when all services are stopped. Scale mode still uses ~0.3 CPU total at idle
- **Disk**: Container layers remain cached. Only the writable layer is discarded. Next start is fast
- **Sablier itself**: ~20 MB disk, ~8 MB RSS, near-zero CPU when no sessions are active

---

## Labels Reference

| Label | Description |
|-------|-------------|
| `sablier.enable` | Enable Sablier management for this container (true/false) |
| `sablier.group` | Group name for the container |
| `sablier.running-hours` | Active hours window, e.g. "Mon-Fri 09:00-17:00" |
| `sablier.ready-after` | Grace period after health check passes before ready (e.g. "30s") |
| `sablier.idle.replicas` | 0 = stop (default), >= 1 = keep running (scale mode) |
| `sablier.idle.cpu` | CPU limit when idle (e.g. "0.1") |
| `sablier.idle.memory` | Memory limit when idle (e.g. "64m") |
| `sablier.active.replicas` | Replica count when active (default 1) |
| `sablier.active.cpu` | CPU limit when active (e.g. "2.0") |
| `sablier.active.memory` | Memory limit when active (e.g. "512m") |

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Container won't stop | `sablier.enable=true` missing | Add label to container |
| Blocking request times out | Container not healthy within timeout | Increase `--strategy.blocking.default-timeout` |
| `connection refused` on Sablier | Sablier not running or wrong port | Check `systemctl --user status sablier` |
| Proxy plugin error 500 | Sablier URL wrong in plugin config | Verify `sablierUrl` matches Sablier endpoint |
| Scale mode not working | Idle replicas not set | Set `sablier.idle.replicas=1` |
| Webhook not firing | URL or auth wrong | Check Sablier logs for webhook errors |
| `permission denied` on Podman socket | Socket mount has wrong SELinux context | Use `:Z` flag on volume mount |

## Related

- [[sablier-architecture]] -- Architecture overview, session lifecycle, provider details
- [[sablier-quadlet]] -- Quadlet configs for rootless Podman with Traefik integration
- [[sablier]] -- Main wiki page for Sablier
