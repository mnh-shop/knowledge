---
name: podlet-quadlet-examples
tags: [podlet, quadlet, rust, quadlet-generator, systemd, conversion, container, developer-tools, acp, ai-llm, cli, deployment, docker, storage]
description: "Podlet Quadlet Examples"
---

# Podlet Quadlet Examples
**Source:** `sources/podlet/`

## Example 1: Converting `podman run` for OpenClaw to Quadlet

### Source Command

```bash
podman run -d --name openclaw-acp \
  -p 8080:8080 \
  -p 8443:8443 \
  -v openclaw-config:/etc/openclaw:ro \
  -v openclaw-data:/var/lib/openclaw \
  -e ACP_AUTH_MODE=mtls \
  -e ACP_LOG_LEVEL=info \
  -e ACP_DB_URL=postgres://user:pass@db:5432/acp \
  --restart unless-stopped \
  --secret acp-tls-certs,type=mount,target=/etc/openclaw/tls \
  --network openclaw-net \
  --label com.openclaw.service=acp \
  ghcr.io/openclaw/acp:latest \
  --server-threads 8
```

### Podlet Command

```bash
podlet podman run -d --name openclaw-acp \
  -p 8080:8080 \
  -p 8443:8443 \
  -v openclaw-config:/etc/openclaw:ro \
  -v openclaw-data:/var/lib/openclaw \
  -e ACP_AUTH_MODE=mtls \
  -e ACP_LOG_LEVEL=info \
  -e ACP_DB_URL=postgres://user:pass@db:5432/acp \
  --restart unless-stopped \
  --secret acp-tls-certs,type=mount,target=/etc/openclaw/tls \
  --network openclaw-net \
  --label com.openclaw.service=acp \
  ghcr.io/openclaw/acp:latest \
  --server-threads 8
```

### Generated File: `openclaw-acp.container`

```ini
[Unit]
Description=OpenClaw ACP Service

[Container]
ContainerName=openclaw-acp
Environment=ACP_AUTH_MODE=mtls ACP_LOG_LEVEL=info ACP_DB_URL=postgres://user:pass@db:5432/acp
Exec=--server-threads 8
Image=ghcr.io/openclaw/acp:latest
Label=com.openclaw.service=acp
Network=openclaw-net
PublishPort=8080:8080
PublishPort=8443:8443
Secret=acp-tls-certs,type=mount,target=/etc/openclaw/tls
Volume=openclaw-config:/etc/openclaw:ro
Volume=openclaw-data:/var/lib/openclaw

[Service]
Restart=always

[Install]
WantedBy=default.target
```

### Deployment

```bash
# Write directly to Quadlet unit directory
podlet -u -s Environment -s Label podman run -d --name openclaw-acp \
  -p 8080:8080 \
  -p 8443:8443 \
  -v openclaw-config:/etc/openclaw:ro \
  -v openclaw-data:/var/lib/openclaw \
  -e ACP_AUTH_MODE=mtls \
  -e ACP_LOG_LEVEL=info \
  -e ACP_DB_URL=postgres://user:pass@db:5432/acp \
  --restart unless-stopped \
  --secret acp-tls-certs,type=mount,target=/etc/openclaw/tls \
  --network openclaw-net \
  --label com.openclaw.service=acp \
  ghcr.io/openclaw/acp:latest \
  --server-threads 8

# The -s flag splits Environment= and Label= onto separate lines for readability
# Reload and start
systemctl --user daemon-reload
systemctl --user enable --now openclaw-acp.service
```

---

## Example 2: Converting Docker Compose for Hermes + Database

### Source: `docker-compose-hermes.yaml`

```yaml
version: "3.8"
name: hermes-stack

services:
  hermes-db:
    image: postgres:16
    environment:
      POSTGRES_DB: hermes
      POSTGRES_USER: hermes
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d:ro
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U hermes"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - hermes-net
    restart: unless-stopped

  hermes-agent:
    image: ghcr.io/hermes/agent:latest
    depends_on:
      hermes-db:
        condition: service_healthy
    environment:
      AGENT_MODE: production
      DB_HOST: hermes-db
      DB_PORT: 5432
      DB_NAME: hermes
      DB_USER: hermes
      DB_PASSWORD: ${DB_PASSWORD}
    volumes:
      - hermes-config:/etc/hermes:ro
      - hermes-data:/var/lib/hermes
    ports:
      - "9000:9000"
      - "9090:9090"
    secrets:
      - db-credentials
    networks:
      - hermes-net
    restart: unless-stopped

volumes:
  pgdata:
  hermes-config:
  hermes-data:

networks:
  hermes-net:
    driver: bridge

secrets:
  db-credentials:
    file: ./secrets/db_credentials.json
```

### Podlet Commands

```bash
# Convert as separate Quadlet files (no pod)
podlet compose docker-compose-hermes.yaml

# Convert as a pod (all containers in one pod)
podlet compose --pod docker-compose-hermes.yaml

# Convert to Kubernetes YAML
podlet compose --kube docker-compose-hermes.yaml

# Write directly to unit directory with split options
podlet -u -s Environment compose docker-compose-hermes.yaml
```

### Generated Files (Default, No Pod)

**`hermes-db.container`**:
```ini
[Unit]
Description=Hermes DB Service

[Container]
ContainerName=hermes-db-pgdata
HealthCmd=CMD-SHELL pg_isready -U hermes
HealthInterval=10s
HealthRetries=5
HealthTimeout=5s
Image=postgres:16
Network=hermes-net
PublishPort=5432:5432
Volume=pgdata:/var/lib/postgresql/data
Volume=./init-scripts:/docker-entrypoint-initdb.d:ro

[Service]
Restart=always

[Install]
WantedBy=default.target
```

**`hermes-agent.container`**:
```ini
[Unit]
Description=Hermes Agent Service

[Container]
ContainerName=hermes-agent
Environment=AGENT_MODE=production DB_HOST=hermes-db DB_PORT=5432 DB_NAME=hermes DB_USER=hermes DB_PASSWORD=****
Image=ghcr.io/hermes/agent:latest
Network=hermes-net
PublishPort=9000:9000
PublishPort=9090:9090
Volume=hermes-config:/etc/hermes:ro
Volume=hermes-data:/var/lib/hermes
Secret=db-credentials,type=mount,target=/run/secrets/db-credentials

[Service]
Restart=always

[Install]
WantedBy=default.target
```

**`hermes-net.network`**:
```ini
[Network]
Driver=bridge

[Install]
WantedBy=default.target
```

**`pgdata.volume`**:
```ini
[Volume]

[Install]
WantedBy=default.target
```

**`hermes-config.volume`**:
```ini
[Volume]

[Install]
WantedBy=default.target
```

**`hermes-data.volume`**:
```ini
[Volume]

[Install]
WantedBy=default.target
```

### Generated Files (Pod Mode)

With `compose --pod`, you also get:

**`hermes-stack.pod`**:
```ini
[Pod]
PublishPort=5432:5432
PublishPort=9000:9000
PublishPort=9090:9090

[Install]
WantedBy=default.target
```

And each `.container` file gains `Pod=hermes-stack.pod`.

### Generated Files (Kube Mode)

With `compose --kube`, you get:

**`hermes-stack.kube`**:
```ini
[Kube]
Yaml=hermes-stack-kube.yaml

[Install]
WantedBy=default.target
```

Plus **`hermes-stack-kube.yaml`** with the full Kubernetes Pod spec.

### Deployment

```bash
# Deploy as separate services
podlet -u -s Environment compose docker-compose-hermes.yaml
systemctl --user daemon-reload
systemctl --user enable --now hermes-db.service
systemctl --user enable --now hermes-agent.service

# Or as a pod (start the whole stack as one unit)
podlet -u compose --pod docker-compose-hermes.yaml
systemctl --user daemon-reload
systemctl --user enable --now hermes-stack-pod.service
# Start with pod
systemctl --user start hermes-stack-pod.service
```

---

## Example 3: Generating from a Running Container

### Scenario: Existing container running via manual podman

```bash
# Current running container
podman ps --format "table {{.ID}} {{.Names}} {{.Image}} {{.Status}}"
CONTAINER ID  NAMES          IMAGE                              STATUS
a1b2c3d4e5f6  my-agent-v2   ghcr.io/myorg/agent:v2.1.0         Up 3 days

# Generate Quadlet from it
podlet generate container my-agent-v2
```

### What Happens Internally

1. Podlet runs `podman container inspect my-agent-v2`
2. Extracts `Config.CreateCommand` from the JSON output
3. Strips `podman run/create` prefix via `filter_container_create_command()`
4. Re-parses the remaining args through the same `ContainerParser` CLI parser
5. Maps to Quadlet format

### Generated File: `my-agent-v2.container`

```ini
# FileName=my-agent-v2
[Container]
ContainerName=my-agent-v2
Environment=LOG_LEVEL=info AGENT_ROLE=worker
Image=ghcr.io/myorg/agent:v2.1.0
Network=host
PublishPort=8080:8080
Volume=agent-config:/etc/agent:ro
Volume=agent-data:/var/lib/agent

[Service]
Restart=always
```

### Pod Generation

```bash
# Generate a pod with all its containers
podlet generate pod my-pod

# This produces:
#   my-pod.pod           - Pod definition
#   my-pod-container1.container  - First non-infra container
#   my-pod-container2.container  - Second non-infra container
```

### Network/Volume/Image Generation

```bash
# From existing network
podlet generate network my-net
# -> my-net.network: [Network] Driver=bridge Subnet=10.0.0.0/24 Gateway=10.0.0.1

# From existing volume
podlet generate volume my-vol
# -> my-vol.volume: [Volume] Label=... Driver=local

# From existing image
podlet generate image my-image
# -> my-image.image: [Image] Image=my-image
```

---

## Example 4: Output Formats

### Individual Multi-File Output

When writing to a directory (the default for `--file <dir>` or `--unit-directory`), each Quadlet resource type gets its own file with the appropriate extension:

| Input | Output File(s) |
|-------|---------------|
| `podlet podman run ...` | `{name}.container` |
| `podlet podman pod create ...` | `{name}.pod` |
| `podlet podman kube play ...` | `{name}.kube` |
| `podlet podman network create ...` | `{name}.network` |
| `podlet podman volume create ...` | `{name}.volume` |
| `podlet podman build ...` | `{name}.build` |
| `podlet podman image pull ...` | `{name}.image` |
| `podlet podman artifact pull ...` | `{name}.artifact` |
| `podlet compose ...` | `{service}.container`, `{network}.network`, `{volume}.volume` |
| `podlet compose --pod ...` | Above + `{name}.pod` |


### Single-File .quadlets Output

With `--quadlets-file <name>`, all generated sections are concatenated into a single file with the `.quadlets` extension. Sections within share the same file:

```ini
# ServiceName=hermes-db
[Container]
ContainerName=hermes-db
Image=postgres:16

[Service]
Restart=always

[Install]
WantedBy=default.target

# ServiceName=hermes-agent
[Container]
ContainerName=hermes-agent
Image=ghcr.io/hermes/agent:latest

[Service]
Restart=always

[Install]
WantedBy=default.target
```

This is useful for:
- Distributing a complete stack as a single artifact
- CI/CD pipelines where multiple files are inconvenient
- Versioning the entire service definition
- Quick one-command deployment: `podlet --quadlets-file my-stack ... | sudo tee /etc/containers/systemd/my-stack.quadlets`

### stdout Output

Default behavior: prints `.quadlets` format to stdout. Useful for:
- Piping into other tools: `podlet podman run ... | grep Image=`
- Quick review: `podlet podman run ... | head -20`
- Dry-run inspection before writing files

---

## Example 5: Advanced Features

### Podman Version Targeting

```bash
# Target Podman v4.6 compatibility
podlet -p 4.6 podman run -d --name old-compat \
  --health-cmd "curl -f http://localhost/health" \
  --health-interval 30s \
  docker.io/library/nginx:alpine
```

When targeting v4.6, options added in later versions (like `HealthCmd=`, `HealthInterval=`) are converted to `PodmanArgs=` entries instead of native Quadlet keys.

### Option Splitting

```bash
# Without -s: joined into single lines
podlet podman run -e A=a -e B=b -e C=c image
# => Environment=A=a B=b C=c

# With -s: separate lines
podlet -s Environment podman run -e A=a -e B=b -e C=c image
# => Environment=A=a
#    Environment=B=b
#    Environment=C=c

# Multiple split options
podlet -s Environment,Label podman run -e A=a -l k=v -e B=b image
```

### Adding Systemd Unit Metadata

```bash
podlet \
  --unit Description="My Production Service" \
  --unit Documentation=https://docs.example.com \
  --unit Wants=network-online.target \
  --unit After=network-online.target \
  --install WantedBy=multi-user.target \
  podman run -d --name prod-app image
```

Produces:
```ini
[Unit]
Description=My Production Service
Documentation=https://docs.example.com
Wants=network-online.target
After=network-online.target

[Container]
...
```

### Service Name Override

```bash
# Override the default service name (default = container name)
podlet --service-name openclaw-acp \
  -u podman run -d --name openclaw-acp image

# Generates: openclaw-acp.container with ServiceName=openclaw-acp
```

## Related

- [[podlet-architecture]] -- Conversion pipeline and flag-to-Quadlet mapping behind the examples
- [[podlet-deployment]] -- Installation, usage patterns, and deployment best practices
- [[podlet]] -- Wiki overview, key features, and source file roles
