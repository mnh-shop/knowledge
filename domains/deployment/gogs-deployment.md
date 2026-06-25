---
name: gogs-deployment
description: Gogs Deployment
source: sources/gogs/
tags: [ai-llm, container, deployment, docker, git, gogs, golang, podman, quadlet, self-hosted, ssh, storage, systemd, version-control, webhook]
---

# Gogs Deployment

| Field | Value |
|---|---|
| **Source** | `sources/gogs/` |
| **Type** | Self-hosted Git service (Go binary) |

## Deployment Options

### Standalone Binary

```bash
# Download from https://gogs.io
./gogs web

# Or specify config
./gogs web --config custom/app.ini
```

### Docker

```bash
# SQLite (simplest)
docker run --name=gogs \
  -p 10022:22 \
  -p 10880:3000 \
  -v gogs-data:/data \
  gogs/gogs

# With PostgreSQL
docker run --name=gogs-postgres \
  -e POSTGRES_DB=gogs \
  -e POSTGRES_USER=gogs \
  -e POSTGRES_PASSWORD=secret \
  postgres:16

docker run --name=gogs \
  --link gogs-postgres:db \
  -p 10022:22 \
  -p 10880:3000 \
  -v gogs-data:/data \
  gogs/gogs
```

### Reverse Proxy (Caddy/Nginx)

```nginx
# Caddyfile
git.example.com {
    reverse_proxy localhost:3000
}

# Nginx
server {
    listen 443 ssl;
    server_name git.example.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Configuration

Create `custom/app.ini`:

```ini
[server]
DOMAIN = git.example.com
HTTP_PORT = 3000
ROOT_URL = https://git.example.com/
SSH_DOMAIN = git.example.com
SSH_PORT = 22

[database]
DB_TYPE = postgres
HOST = 127.0.0.1:5432
NAME = gogs
USER = gogs
PASSWD = secret

[repository]
ROOT = /data/git/repositories
FORCE_PRIVATE = true

[mailer]
ENABLED = true
HOST = smtp.example.com:587
FROM = gogs@example.com
USER = gogs@example.com
PASSWD = secret

[service]
DISABLE_REGISTRATION = true
REQUIRE_SIGNIN_VIEW = true

[server]
OFFLINE_MODE = false
```

## Integration with Agent Stack

### As Git Backend for Agent Code

Gogs can host:
- Agent deployment configurations (Quadlet files, Docker Compose)
- Custom skills and tool definitions
- Workflow definitions for n8n
- Infrastructure-as-code for agent orchestration
- Agent memory/state backup vault

### Webhook-Triggered Workflows

Configure n8n webhook triggers on Gogs events:
- Push → deploy agent updates
- Pull request → review/merge gate
- Issue created → agent task assignment

### With Podman Quadlet

```systemd
[Unit]
Description=Gogs Git Service
After=network-online.target

[Container]
Image=docker.io/gogs/gogs:latest
ContainerName=gogs
PublishPort=10022:22
PublishPort=10880:3000
Volume=gogs-data:/data:Z

[Service]
Restart=always

[Install]
WantedBy=default.target
```

## Resource Requirements

- **Personal use:** Raspberry Pi or 1GB RAM VPS
- **Team (up to 50 users):** 2 CPU, 512MB–1GB RAM
- **Storage:** scales with repository data

## Backups

Backup `custom/app.ini` and the database + repository root:
```bash
# SQLite
cp /data/gogs/gogs.db /backup/
# PostgreSQL
pg_dump gogs > /backup/gogs.sql
# Repos
rsync -av /data/git/repositories/ /backup/repos/
```

## Related

- [[gogs]] — Wiki entry
- [[gogs-architecture]] — Architecture and component design
- [[gogs-api]] — REST API reference
