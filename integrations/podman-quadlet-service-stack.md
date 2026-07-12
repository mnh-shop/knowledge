---
name: podman-quadlet-service-stack
type: integration
tags: [podman, quadlet, deployment, integration, container, hermes-agent, n8n, postgres, redis, systemd]
description: "Integration: Complete agent service stack with Podman Quadlet -- Hermes + n8n + Postgres + Redis"
---

# Integration: Podman Quadlet Service Stack

**Sources**: `sources/podman/`, `sources/n8n/`, `sources/hermes-agent/`

## Overview

A complete agent service stack running entirely under rootless Podman Quadlet units -- no Docker Compose, no orchestrator. Four services (Hermes Agent, n8n, PostgreSQL, Redis) each have their own `.container` unit, wired together through Quadlet's `Requires=`/`BindsTo=` dependency system and a shared Podman network.

This is the **production baseline** for agent deployments: Hermes provides the agent gateway, n8n handles workflow automation, PostgreSQL gives durable storage, and Redis provides caching and queue backends.

## Architecture

```
    ┌─────────────────────────────────────────────┐
    │         podman-quadlet (rootless)            │
    │                                              │
    │  ┌──────────┐   ┌──────────┐                │
    │  │ Hermes   │──▶│ Postgres │                │
    │  │ :9090    │   │ :5432    │                │
    │  └──────────┘   └──────────┘                │
    │       │                                      │
    │       ▼          ┌──────────┐                │
    │  ┌──────────┐   │  Redis   │                │
    │  │   n8n    │──▶│ :6379    │                │
    │  │ :5678    │   └──────────┘                │
    │  └──────────┘                                │
    │                                              │
    │  Network: agent-stack-net (bridge)           │
    └─────────────────────────────────────────────┘
```

## Quadlet Units

Place all `.container`, `.volume`, and `.network` files in `~/.config/containers/systemd/`.

### 1. Shared Network & Volumes

```ini
# agent-stack-net.network
[Network]
Description=Agent stack internal network
Internal=true
```

```ini
# postgres-data.volume
[Volume]
Description=PostgreSQL persistent storage
```

```ini
# n8n-data.volume
[Volume]
Description=n8n persistent storage
```

### 2. PostgreSQL

```ini
# postgres.container
[Unit]
Description=PostgreSQL for agent stack
After=network-online.target
Wants=network-online.target

[Container]
Image=docker.io/postgres:18
ContainerName=postgres
Network=agent-stack-net.network
Volume=postgres-data.volume:/var/lib/postgresql/data:Z
Environment=POSTGRES_DB=hermes
Environment=POSTGRES_USER=hermes
Environment=POSTGRES_PASSWORD_FILE=/run/secrets/db_password

[Service]
Restart=always
ExecStartPre=-/bin/bash -c "echo '${DB_PASSWORD}' > /run/secrets/db_password"

[Install]
WantedBy=default.target
```

### 3. Redis

```ini
# redis.container
[Unit]
Description=Redis for agent stack
After=network-online.target postgres.service

[Container]
Image=docker.io/redis:7-alpine
ContainerName=redis
Network=agent-stack-net.network

[Service]
Restart=always

[Install]
WantedBy=default.target
```

### 4. Hermes Agent

```ini
# hermes.container
[Unit]
Description=Hermes AI agent gateway
After=network-online.target postgres.service redis.service
BindsTo=postgres.service redis.service

[Container]
Image=ghcr.io/nousresearch/hermes-agent:latest
ContainerName=hermes
Network=agent-stack-net.network
PublishPort=127.0.0.1:9090:9090
Volume=%h/.hermes:/home/user/.hermes:Z
Environment=HERMES_DB_DSN=postgres://hermes:${DB_PASSWORD}@postgres:5432/hermes
Environment=HERMES_REDIS_URL=redis://redis:6379

[Service]
Restart=always

[Install]
WantedBy=default.target
```

### 5. n8n

```ini
# n8n.container
[Unit]
Description=n8n workflow automation
After=network-online.target postgres.service redis.service
BindsTo=postgres.service redis.service

[Container]
Image=docker.n8n.io/n8nio/n8n:latest
ContainerName=n8n
Network=agent-stack-net.network
Volume=n8n-data.volume:/home/node/.n8n:Z
PublishPort=127.0.0.1:5678:5678
Environment=DB_TYPE=postgresdb
Environment=DB_POSTGRESDB_HOST=postgres
Environment=DB_POSTGRESDB_PORT=5432
Environment=DB_POSTGRESDB_DATABASE=n8n
Environment=DB_POSTGRESDB_USER=n8n
Environment=DB_POSTGRESDB_PASSWORD_FILE=/run/secrets/db_password
Environment=N8N_ENCRYPTION_KEY_FILE=/run/secrets/n8n_encryption_key

[Service]
Restart=always
ExecStartPre=-/bin/bash -c "echo '${N8N_ENCRYPTION_KEY}' > /run/secrets/n8n_encryption_key"

[Install]
WantedBy=default.target
```

## Activation

```bash
# Reload systemd --user unit files
systemctl --user daemon-reload

# Start the entire stack (order resolved by Quadlet dependencies)
systemctl --user start postgres.service redis.service
systemctl --user start hermes.service n8n.service

# Verify
systemctl --user status postgres redis hermes n8n
podman ps --all
```

Secrets are injected via files (`/run/secrets/`) to avoid env-var leakage in `systemctl show`. Use a `.env` file or a password manager to populate `$DB_PASSWORD` and `$N8N_ENCRYPTION_KEY`.

## Related

- [[podman]] -- Rootless container runtime: the foundation layer
- [[podlet]] -- Generate Quadlet files from `podman run` or compose files
- [[n8n]] -- Workflow automation engine with 400+ integrations
- [[hermes-agent]] -- Self-improving AI agent with multi-platform messaging
