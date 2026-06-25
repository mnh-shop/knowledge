---
name: agentfield-quadlet
tags: [agentfield, quadlet, podman, deployment]
description: Rootless Podman Quadlet deployment configuration for AgentField control plane with PostgreSQL, volume, and network units
---

# AgentField Quadlet Deployment
**Source:** `sources/agentfield/`

**Type:** Deployment asset (rootless Podman Quadlet)  
**Status:** Reference configuration  

---

## Why Quadlet Works Well for AgentField

1. **Single Go binary** -- the `af` CLI / `agentfield-server` has no runtime dependencies (embeds SQLite, BoltDB, and web UI). Zero install complexity.
2. **Distroless base image** -- the Docker Compose uses `gcr.io/distroless/base-debian12`, inherently Quadlet-friendly.
3. **No Redis/external queue** -- all state in SQLite or PostgreSQL. No sidecar dependency.
4. **Prometheus metrics** -- `/metrics` endpoint ready for monitoring.
5. **Health endpoints** -- `/api/v1/health` ready for Quadlet health checks.

---

## Option A: Local Mode (SQLite) -- Simplest

Single `.container` file, no database dependency.

### `~/.config/containers/systemd/agentfield.container`

```
[Unit]
Description=AgentField Control Plane
After=network-online.target
Wants=network-online.target

[Container]
Image=ghcr.io/agent-field/agentfield:latest
# Or use a locally-built binary directly:
# Exec=/usr/local/bin/agentfield-server
# (requires building the binary or mounting it in)

# Persist SQLite database, keys, and config
Volume=%h/agentfield/data:/data:Z

Environment=AGENTFIELD_STORAGE_MODE=local
Environment=AGENTFIELD_PORT=8080
Environment=AGENTFIELD_HOME=/data
Environment=AGENTFIELD_CONFIG_FILE=/dev/null
Environment=AGENTFIELD_API_KEY=your-api-key

PublishPort=8080:8080

# Health check -- /api/v1/health responds 200
HealthCmd=curl --fail http://localhost:8080/api/v1/health || exit 1
HealthInterval=15s
HealthRetries=3

[Service]
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

---

## Option B: PostgreSQL Mode -- Two Containers

### Network Definition

### `~/.config/containers/systemd/agentfield.network`

```
[Network]
Description=AgentField internal network
Subnet=10.89.0.0/24
```

### `~/.config/containers/systemd/agentfield-postgres.container`

```
[Unit]
Description=AgentField PostgreSQL with pgvector
After=network-online.target
Requires=agentfield.network

[Container]
Image=docker.io/pgvector/pgvector:pg16
Volume=%h/agentfield/pgdata:/var/lib/postgresql/data:Z
Environment=POSTGRES_USER=agentfield
Environment=POSTGRES_PASSWORD=agentfield
Environment=POSTGRES_DB=agentfield
PublishPort=5432:5432
Network=agentfield.network

HealthCmd=pg_isready -U agentfield
HealthInterval=5s
HealthRetries=10

[Service]
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

### `~/.config/containers/systemd/agentfield.container`

```
[Unit]
Description=AgentField Control Plane (PostgreSQL)
After=network-online.target
After=agentfield-postgres.service
Requires=agentfield-postgres.service

[Container]
Image=ghcr.io/agent-field/agentfield:latest
Volume=%h/agentfield/data:/data:Z
Environment=AGENTFIELD_STORAGE_MODE=postgres
Environment=AGENTFIELD_STORAGE_POSTGRES_URL=postgres://agentfield:agentfield@agentfield-postgres:5432/agentfield?sslmode=disable
Environment=AGENTFIELD_PORT=8080
Environment=AGENTFIELD_HOME=/data
Environment=AGENTFIELD_CONFIG_FILE=/dev/null
Environment=AGENTFIELD_API_KEY=your-api-key
Environment=AGENTFIELD_AUTHORIZATION_ADMIN_TOKEN=your-admin-token
Environment=AGENTFIELD_STORAGE_POSTGRES_ENABLE_AUTO_MIGRATION=true

PublishPort=8080:8080
Network=agentfield.network

HealthCmd=curl --fail http://localhost:8080/api/v1/health || exit 1
HealthInterval=15s
HealthRetries=3

[Service]
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

---

## Option B1: PostgreSQL with .volume and Secret Injection

A refined PostgreSQL deployment using Quadlet `.volume` units for persistent storage and environment files for secure credential injection.

### `~/.config/containers/systemd/agentfield.network`

```
[Network]
Description=AgentField internal network
Subnet=10.89.0.0/24
```

### `~/.config/containers/systemd/agentfield-postgres.volume`

```
[Volume]
Description=AgentField PostgreSQL data volume
```

### `~/.config/containers/systemd/agentfield-postgres.container`

```
[Unit]
Description=AgentField PostgreSQL with pgvector
After=network-online.target
Requires=agentfield.network agentfield-postgres.volume

[Container]
Image=docker.io/pgvector/pgvector:pg16
Volume=agentfield-postgres.volume:/var/lib/postgresql/data:Z
Environment=POSTGRES_USER=agentfield
Environment=POSTGRES_PASSWORD=agentfield
Environment=POSTGRES_DB=agentfield
PublishPort=5432:5432
Network=agentfield.network

HealthCmd=pg_isready -U agentfield
HealthInterval=5s
HealthRetries=10

[Service]
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

### `~/.config/containers/systemd/agentfield-data.volume`

```
[Volume]
Description=AgentField control plane data volume
```

### Secret File: `~/.config/containers/systemd/agentfield.env`

```
AGENTFIELD_STORAGE_MODE=postgres
AGENTFIELD_STORAGE_POSTGRES_URL=postgres://agentfield:agentfield@agentfield-postgres:5432/agentfield?sslmode=disable
AGENTFIELD_PORT=8080
AGENTFIELD_HOME=/data
AGENTFIELD_CONFIG_FILE=/dev/null
AGENTFIELD_API_KEY=prod-api-key-here
AGENTFIELD_AUTHORIZATION_ADMIN_TOKEN=prod-admin-token-here
AGENTFIELD_AUTHORIZATION_INTERNAL_TOKEN=prod-internal-token-here
AGENTFIELD_STORAGE_POSTGRES_ENABLE_AUTO_MIGRATION=true
AGENTFIELD_UI_ENABLED=true
AGENTFIELD_UI_MODE=embedded
AGENTFIELD_TELEMETRY_ENABLED=false
```

### `~/.config/containers/systemd/agentfield.container`

```
[Unit]
Description=AgentField Control Plane (PostgreSQL)
After=network-online.target agentfield-postgres.service
Requires=agentfield-postgres.service agentfield-data.volume
Wants=agentfield.network

[Container]
Image=ghcr.io/agent-field/agentfield:latest
Volume=agentfield-data.volume:/data:Z
EnvironmentFile=%h/.config/containers/systemd/agentfield.env
PublishPort=8080:8080
Network=agentfield.network

HealthCmd=curl --fail http://localhost:8080/health || exit 1
HealthInterval=15s
HealthRetries=3

[Service]
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

## Option C: Agent Nodes as Quadlets

Each ecosystem agent (SWE-AF, sec-af, af-deep-research, etc.) runs as its own Quadlet unit.

### Template: `~/.config/containers/systemd/af-swe.container`

```
[Unit]
Description=SWE-Agent for AgentField
After=agentfield.service
Requires=agentfield.service

[Container]
Image=ghcr.io/agent-field/swe-af:latest
Environment=AGENTFIELD_URL=http://agentfield:8080
Environment=AGENTFIELD_API_KEY=your-api-key
Environment=AGENT_CALLBACK_URL=http://af-swe:8002
Environment=PORT=8002
Environment=OPENAI_API_KEY=...
PublishPort=8002:8002

HealthCmd=curl --fail http://localhost:8002/health || exit 1
HealthInterval=30s
HealthRetries=3

[Service]
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

Repeat for each ecosystem agent:

| Unit Name | Port | Callback URL | Purpose |
|-----------|------|-------------|---------|
| `af-swe` | 8002 | `http://af-swe:8002` | Software engineering agent |
| `sec-af` | 8003 | `http://sec-af:8003` | Security analysis agent |
| `af-deep-research` | 8004 | `http://af-deep-research:8004` | Deep research agent |
| `af-reactive-atlas-mongodb` | 8005 | `http://af-reactive-atlas-mongodb:8005` | Reactive agent with MongoDB |

All agents connect to `agentfield:8080` (container name resolution on Podman's default bridge). The control plane reaches back to `http://<agent-service-name>:<port>`.

---

## Key Quadlet Considerations

### Image Reference

| Image | Where |
|-------|-------|
| Official production | `ghcr.io/agent-field/agentfield:latest` (per Railway docs) |
| Local build | `localhost/agentfield-control-plane:latest` (build via `docker build -f deployments/docker/Dockerfile.control-plane .`) |

### Distroless Caveat

The distroless runtime image has no shell, so `curl`-based health checks won't work **inside** the container. However, Podman health checks with `HealthCmd=curl...` run from the host namespace via `podman healthcheck run`, so they work fine. Alternatively, switch to a `golang:1.25-alpine` runtime image for a shell.

### Auto-Migration

Set `AGENTFIELD_STORAGE_POSTGRES_ENABLE_AUTO_MIGRATION=true` to have the control plane run Goose migrations on startup. Without it, you must run migrations manually via the `af` CLI or the Goose binary.

### Data Persistence

Quadlet with rootless Podman stores volumes under `~/.local/share/containers/storage/volumes/` by default. Using bind mounts (`Volume=%h/agentfield/data:/data:Z`) makes data directly accessible and easier to back up. The `:Z` relabels for SELinux.

### No Daemon Dependency

The Quadlet runs under `systemd --user` and starts on user login. No system-level daemon configuration needed.

```
systemctl --user enable agentfield
systemctl --user start agentfield
systemctl --user status agentfield
systemctl --user daemon-reload  # after editing .container files
```

### Scaling

Each agent runs as its own Quadlet unit. An agent pod (multiple agents sharing state) would use a Pod Quadlet.

### Networking

Podman's default bridge (pasta/slirp4netns) assigns per-container IPs. Containers reach each other by name on the default network. For explicit networking, define a `.network` Quadlet file (as shown in Option B).

### Viewing Logs

```
journalctl --user -u agentfield
journalctl --user -u agentfield -f   # follow
journalctl --user -u agentfield --since "5 minutes ago"
```

---

## Option D: Complete Multi-Container Stack with Demo Agents

Full stack: PostgreSQL + Control Plane + Go Demo Agent + Python Demo Agent, each as a separate Quadlet unit with volumes and secret injection.

### Common Files

**`~/.config/containers/systemd/agentfield.network`**
```
[Network]
Description=AgentField internal network
Subnet=10.89.0.0/24
```

**`~/.config/containers/systemd/agentfield-postgres.volume`**
```
[Volume]
Description=AgentField PostgreSQL data volume
```

**`~/.config/containers/systemd/agentfield-data.volume`**
```
[Volume]
Description=AgentField control plane data volume
```

**`~/.config/containers/systemd/agentfield.env`**
```
AGENTFIELD_STORAGE_MODE=postgres
AGENTFIELD_STORAGE_POSTGRES_URL=postgres://agentfield:agentfield@agentfield-postgres:5432/agentfield?sslmode=disable
AGENTFIELD_PORT=8080
AGENTFIELD_HOME=/data
AGENTFIELD_CONFIG_FILE=/dev/null
AGENTFIELD_API_KEY=local-api-key
AGENTFIELD_STORAGE_POSTGRES_ENABLE_AUTO_MIGRATION=true
AGENTFIELD_UI_ENABLED=true
```

### PostgreSQL Container

**`~/.config/containers/systemd/agentfield-postgres.container`**
```
[Unit]
Description=AgentField PostgreSQL
After=network-online.target
Requires=agentfield.network agentfield-postgres.volume

[Container]
Image=docker.io/pgvector/pgvector:pg16
Volume=agentfield-postgres.volume:/var/lib/postgresql/data:Z
Environment=POSTGRES_USER=agentfield
Environment=POSTGRES_PASSWORD=agentfield
Environment=POSTGRES_DB=agentfield
Network=agentfield.network
HealthCmd=pg_isready -U agentfield
HealthInterval=5s
HealthRetries=10

[Service]
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

### Control Plane Container

**`~/.config/containers/systemd/agentfield.container`**
```
[Unit]
Description=AgentField Control Plane
After=network-online.target agentfield-postgres.service
Requires=agentfield-postgres.service agentfield-data.volume agentfield.network

[Container]
Image=ghcr.io/agent-field/agentfield:latest
Volume=agentfield-data.volume:/data:Z
EnvironmentFile=%h/.config/containers/systemd/agentfield.env
PublishPort=8080:8080
Network=agentfield.network
HealthCmd=curl --fail http://localhost:8080/health || exit 1
HealthInterval=15s
HealthRetries=3

[Service]
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

### Go Demo Agent Container

**`~/.config/containers/systemd/agentfield-demo-go.container`**
```
[Unit]
Description=AgentField Go Demo Agent
After=agentfield.service
Requires=agentfield.service agentfield.network

[Container]
Image=localhost/agentfield-demo-go-agent:latest
Environment=AGENTFIELD_URL=http://agentfield:8080
Environment=AGENT_NODE_ID=demo-go-agent
Environment=AGENT_LISTEN_ADDR=:8001
Environment=AGENT_PUBLIC_URL=http://agentfield-demo-go:8001
Environment=AGENTFIELD_API_KEY=local-api-key
PublishPort=8001:8001
Network=agentfield.network
HealthCmd=curl --fail http://localhost:8001/health || exit 1
HealthInterval=30s
HealthRetries=3

[Service]
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

### Python Demo Agent Container

**`~/.config/containers/systemd/agentfield-demo-python.container`**
```
[Unit]
Description=AgentField Python Demo Agent
After=agentfield.service
Requires=agentfield.service agentfield.network

[Container]
Image=localhost/agentfield-demo-python-agent:latest
Environment=AGENTFIELD_URL=http://agentfield:8080
Environment=AGENT_NODE_ID=demo-python-agent
Environment=PORT=8001
Environment=AGENT_CALLBACK_URL=http://agentfield-demo-python:8001
Environment=AGENTFIELD_API_KEY=local-api-key
PublishPort=8002:8001
Network=agentfield.network

[Service]
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

### Starting the Full Stack

```bash
# Enable all units
systemctl --user enable agentfield-postgres
systemctl --user enable agentfield
systemctl --user enable agentfield-demo-go
systemctl --user enable agentfield-demo-python

# Start (order: postgres -> control-plane -> agents)
systemctl --user start agentfield-postgres
# Wait for postgres health check to pass
systemctl --user start agentfield
# Wait for control plane health check to pass
systemctl --user start agentfield-demo-go
systemctl --user start agentfield-demo-python

# Check status
systemctl --user status agentfield
journalctl --user -u agentfield -f
```

## Secret Management

Quadlet supports several patterns for injecting secrets:

### Pattern 1: EnvironmentFile (recommended)

```
[Container]
EnvironmentFile=%h/.config/containers/systemd/agentfield.env
```

The `.env` file is a plain-text key=value file. Set permissions to 600:
```bash
chmod 600 ~/.config/containers/systemd/agentfield.env
```

### Pattern 2: Podman Secrets

```bash
podman secret create agentfield-api-key ~/secrets/agentfield-api-key.txt
podman secret create agentfield-admin-token ~/secrets/agentfield-admin-token.txt
```

Reference in `.container`:
```
[Container]
Secret=agentfield-api-key,type=env,target=AGENTFIELD_API_KEY
Secret=agentfield-admin-token,type=env,target=AGENTFIELD_AUTHORIZATION_ADMIN_TOKEN
```

### Pattern 3: Systemd Credentials (most secure)

```bash
systemd-credentials encrypt ~/secrets/agentfield-api-key.txt /etc/credstore/agentfield-api-key
```

Reference in `.container`:
```
[Container]
Set Environment=AGENTFIELD_API_KEY=%d/agentfield-api-key
```

### What Secrets Are Needed

| Secret | Source | Purpose |
|--------|--------|---------|
| `AGENTFIELD_API_KEY` | You generate | Authenticates API calls to control plane |
| `AGENTFIELD_AUTHORIZATION_ADMIN_TOKEN` | You generate | Protects admin endpoints |
| `AGENTFIELD_AUTHORIZATION_INTERNAL_TOKEN` | You generate | CP-to-agent request auth |
| PostgreSQL password | `POSTGRES_PASSWORD` env | Database auth |
| `AGENTFIELD_APPROVAL_WEBHOOK_SECRET` | You generate | HMAC key for approval webhooks |
| Agent LLM API keys | Per-provider | `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc. |

### .container vs .volume vs .network Cheat Sheet

| Quadlet Unit | Syntax | Purpose |
|-------------|--------|---------|
| `.network` | `[Network]` | Defines a Podman network (bridge) |
| `.volume` | `[Volume]` | Defines a named volume |
| `.container` | `[Container]` | Defines a container with image, env, ports |
| Service reference | `agentfield-postgres.service` | systemd unit name for dependency |

Accessed from another container on the same network by the `.container` filename (minus extension): e.g., container defined in `agentfield-postgres.container` is reachable at hostname `agentfield-postgres`.

## Comparison: Docker Compose vs. Quadlet

| Aspect | Docker Compose | Quadlet |
|--------|---------------|---------|
| Init system | Docker | systemd --user |
| Autostart | restart: unless-stopped | WantedBy=default.target |
| Health checks | compose healthcheck | HealthCmd / HealthInterval |
| Logging | docker logs | journalctl --user |
| Network | bridge driver | Podman default (pasta) |
| Build | built in compose | Pre-built image preferred |
| PostgreSQL | pgvector:pg16 | Same image |
| Data | named volumes | Bind mounts preferred |
| Agent callbacks | Compose network DNS | Podman container name DNS |
| Secret management | compose env vars | systemd EnvironmentFile= |

---

## Cross-Reference

- [AgentField Architecture](../../domains/architecture/agentfield-architecture.md)
- [AgentField API](../../domains/api/agentfield-api.md)
- [AgentField Deployment](../../domains/deployment/agentfield-deployment.md) -- broader deployment context including Docker Compose and Helm
- [AgentField MCP Server](../mcp-servers/agentfield-mcp-server.md)

## Related

- [[agentfield]] -- wiki page for the platform
- [[agentfield-architecture]] -- system architecture
- [[agentfield-api]] -- REST API reference
- [[agentfield-deployment]] -- deployment guide
- [[agentfield-mcp-server]] -- MCP bridge server
- [[agentfield-profile]] -- AgentField platform profile
- [[SWE-AF]] -- software engineering agent
- [[sec-af]] -- security analysis agent
- [[af-deep-research]] -- deep research agent
- [[af-reactive-atlas-mongodb]] -- reactive MongoDB agent
