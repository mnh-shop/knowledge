---
name: n8n-podman-deployment
type: integration
tags: [n8n, podman, integration, deployment, quadlet]
description: "Deploy n8n under Podman Quadlet with PostgreSQL — container + volume + network units, auto-update, backup strategy, webhook exposure"
---

# Integration: n8n — Podman Quadlet Deployment with PostgreSQL

n8n and PostgreSQL run as rootless Podman Quadlet services on a shared internal network. PostgreSQL replaces SQLite for production durability. Port 5678 serves the n8n UI and webhooks. Both use named volumes, with a daily backup timer for PostgreSQL dumps.

```ini
# n8n-net.network
[Network]
Description=n8n internal network
Internal=true
```

`n8n-postgres.container`:
```ini
[Container]
Image=docker.io/postgres:18-alpine
ContainerName=n8n-postgres
Network=n8n-net.network
Volume=postgres-data.volume:/var/lib/postgresql/data:Z
Environment=POSTGRES_DB=n8n POSTGRES_USER=n8n
Environment=POSTGRES_PASSWORD_FILE=/run/secrets/n8n_db_password
ExecStartPre=-/bin/bash -c 'echo "${N8N_DB_PASSWORD}" > /run/secrets/n8n_db_password'
[Service]
Restart=always
```

`n8n.container`:
```ini
[Container]
Image=docker.n8n.io/n8nio/n8n:latest
ContainerName=n8n
Network=n8n-net.network
PublishPort=127.0.0.1:5678:5678
Volume=n8n-data.volume:/home/node/.n8n:Z
Volume=%h/.n8n/backups:/backups:Z
Environment=DB_TYPE=postgresdb DB_POSTGRESDB_HOST=n8n-postgres
Environment=DB_POSTGRESDB_DATABASE=n8n DB_POSTGRESDB_USER=n8n
Environment=DB_POSTGRESDB_PASSWORD_FILE=/run/secrets/n8n_db_password
Environment=N8N_ENCRYPTION_KEY_FILE=/run/secrets/n8n_encryption_key
ExecStartPre=-/bin/bash -c 'echo "${N8N_ENCRYPTION_KEY}" > /run/secrets/n8n_encryption_key'
After=n8n-postgres.service
[Service]
Restart=always
```

```ini
# n8n-backup.service
[Service]
Type=oneshot
ExecStart=podman exec n8n-postgres pg_dump -U n8n n8n > %h/.n8n/backups/n8n-$(date +%%Y%%m%%d).sql
# n8n-backup.timer
[Timer]
OnCalendar=03:00
Persistent=true
```

```bash
mkdir -p ~/.config/containers/systemd ~/.n8n/backups
echo "N8N_ENCRYPTION_KEY=$(openssl rand -hex 32)" >> ~/.config/n8n/secrets.env
echo "N8N_DB_PASSWORD=$(openssl rand -base64 24)" >> ~/.config/n8n/secrets.env
source ~/.config/n8n/secrets.env
podman pull docker.n8n.io/n8nio/n8n:latest docker.io/postgres:18-alpine
systemctl --user daemon-reload
systemctl --user start n8n-postgres.service n8n.service
systemctl --user enable --now n8n-backup.timer
curl -s http://127.0.0.1:5678/healthz
```

## Related

- [[n8n]] — Workflow automation engine
- [[podman]] — Rootless container runtime
- [[podlet]] — Quadlet file generator
- [[podman-quadlet-service-stack]] — Full agent stack with n8n + Postgres + Redis
