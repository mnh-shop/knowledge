---
name: podman-quadlet-examples
tags: [podman, quadlet, golang, container-engine, daemonless, rootless, oci]
description: "Podman Quadlet Examples -- Production-Ready Configurations"
---
# Podman Quadlet Examples -- Production-Ready Configurations
**Source:** `sources/podman/`

All files in this collection are **complete, working configurations** for deploying services via Quadlet under rootless Podman. Each service uses rootless-compatible settings: `UserNS=keep-id`, `PublishPort=127.0.0.1:`, `Notify=healthy`, `DropCapability=all`.

---

## Shared Network

This network is referenced by all services. Create it first.

```ini
# ~/.config/containers/systemd/stack.network
[Network]
NetworkName=stack
Driver=bridge
Subnet=10.89.0.0/24
Gateway=10.89.0.1
Label=org.stack=primary
```

Install: `systemctl --user daemon-reload` (network auto-created when first container starts).

---

## OpenClaw API Gateway

```ini
# ~/.config/containers/systemd/openclaw.container
[Unit]
Description=OpenClaw API Gateway
After=network-online.target
Wants=network-online.target

[Container]
Image=ghcr.io/openclaw/openclaw:latest
ContainerName=openclaw
PublishPort=127.0.0.1:18789:18789
PublishPort=127.0.0.1:18790:18790
Volume=%h/.openclaw:/data:Z
UserNS=keep-id
HealthCmd=curl -sf http://localhost:18789/health || exit 1
HealthInterval=30s
HealthRetries=3
HealthStartPeriod=30s
HealthTimeout=10s
Notify=healthy
Label=org.openclaw.service=gateway
Label=org.openclaw.stack=primary
AutoUpdate=registry
Network=stack.network
Pull=newer
Retry=3
RetryDelay=5s
DropCapability=all
AddCapability=CAP_NET_BIND_SERVICE
NoNewPrivileges=true
RunInit=true
ReadOnly=true
ReadOnlyTmpfs=true
StopSignal=SIGTERM
StopTimeout=30

[Service]
Restart=on-failure
RestartSec=30s
TimeoutStartSec=900
TimeoutStopSec=60

[Install]
WantedBy=default.target
```

### Secret Drop-In

```ini
# ~/.config/containers/systemd/openclaw.container.d/10-secrets.conf
# NOT committed to version control.
# Create secrets:
#   podman secret create openclaw-api-key /path/to/api-key.txt
#   podman secret create openclaw-config /path/to/config.yaml

[Container]
Secret=openclaw-api-key,type=env,target=OPENCLAW_API_KEY
Secret=openclaw-config,type=mount,target=/data/config.yaml,mode=0440
```

---

## Hermes AI Agent

```ini
# ~/.config/containers/systemd/hermes.container
[Unit]
Description=Hermes AI Agent Service
After=network-online.target
Wants=network-online.target

[Container]
Image=docker.io/nousresearch/hermes-agent:main
ContainerName=hermes
PublishPort=127.0.0.1:8081:8080
Volume=%h/.hermes:/data:Z
UserNS=keep-id
HealthCmd=curl -sf http://localhost:8080/health || exit 1
HealthInterval=30s
HealthRetries=3
HealthStartPeriod=30s
HealthTimeout=10s
Notify=healthy
Label=org.hermes.service=agent
Label=org.hermes.stack=primary
AutoUpdate=registry
Network=stack.network
Pull=newer
Retry=3
RetryDelay=5s
DropCapability=all
NoNewPrivileges=true
RunInit=true
ReadOnly=true
ReadOnlyTmpfs=true
StopTimeout=30
Environment=HERMES_HOST=0.0.0.0
Environment=HERMES_PORT=8080
Environment=HERMES_LOG_LEVEL=info

[Service]
Restart=on-failure
RestartSec=30s
TimeoutStartSec=900
TimeoutStopSec=60

[Install]
WantedBy=default.target
```

### Secret Drop-In

```ini
# ~/.config/containers/systemd/hermes.container.d/10-secrets.conf
# Create secrets:
#   podman secret create hermes-api-key --env HERMES_API_KEY=...
#   podman secret create hermes-openai-key --env OPENAI_API_KEY=...

[Container]
Secret=hermes-api-key,type=env,target=HERMES_API_KEY
Secret=hermes-openai-key,type=env,target=OPENAI_API_KEY
Secret=hermes-anthropic-key,type=env,target=ANTHROPIC_API_KEY
```

---

## n8n Workflow Automation

### Volume Definition

```ini
# ~/.config/containers/systemd/n8n.volume
[Volume]
VolumeName=n8n-data
Label=org.n8n.service=workflow-engine
Label=org.n8n.stack=primary
```

### Container Definition

```ini
# ~/.config/containers/systemd/n8n.container
[Unit]
Description=n8n Workflow Automation Platform
After=network-online.target
Wants=network-online.target

[Container]
Image=docker.io/n8nio/n8n:latest
ContainerName=n8n
PublishPort=127.0.0.1:5678:5678
Volume=n8n.volume:/home/node/.n8n:Z
UserNS=keep-id
HealthCmd=curl -sf http://localhost:5678/healthz || exit 1
HealthInterval=30s
HealthRetries=3
HealthStartPeriod=30s
HealthTimeout=10s
Notify=healthy
Label=org.n8n.service=workflow
Label=org.n8n.stack=primary
AutoUpdate=registry
Network=stack.network
Pull=newer
Retry=3
RetryDelay=5s
DropCapability=all
NoNewPrivileges=true
RunInit=true
ReadOnly=false
StopTimeout=30
Environment=N8N_PORT=5678
Environment=N8N_HOST=localhost
Environment=N8N_PROTOCOL=http
Environment=N8N_METRICS=false
Environment=N8N_SKIP_WEBHOOK_DEREGISTRATION_SHUTDOWN=true

[Service]
Restart=on-failure
RestartSec=30s
TimeoutStartSec=900
TimeoutStopSec=60

[Install]
WantedBy=default.target
```

### Secret Drop-In

```ini
# ~/.config/containers/systemd/n8n.container.d/10-secrets.conf
# Create secrets:
#   podman secret create n8n-encryption-key --env N8N_ENCRYPTION_KEY=<key>
#   podman secret create n8n-basic-auth-user --env N8N_BASIC_AUTH_USER=admin
#   podman secret create n8n-basic-auth-pass --env N8N_BASIC_AUTH_PASSWORD=<pw>

[Container]
Secret=n8n-encryption-key,type=env,target=N8N_ENCRYPTION_KEY
Secret=n8n-basic-auth-user,type=env,target=N8N_BASIC_AUTH_USER
Secret=n8n-basic-auth-pass,type=env,target=N8N_BASIC_AUTH_PASSWORD
```

---

## Mission Control Dashboard

### Volume Definition

```ini
# ~/.config/containers/systemd/mission-control.volume
[Volume]
VolumeName=mission-control-data
Label=org.missioncontrol.service=dashboard
Label=org.missioncontrol.stack=primary
```

### Container Definition

```ini
# ~/.config/containers/systemd/mission-control.container
[Unit]
Description=Mission Control Dashboard
After=network-online.target
Wants=network-online.target

[Container]
Image=ghcr.io/builderz-labs/mission-control:latest
ContainerName=mission-control
PublishPort=127.0.0.1:3000:3000
Volume=mission-control.volume:/data:Z
UserNS=keep-id
HealthCmd=curl -sf http://localhost:3000/api/health || exit 1
HealthInterval=30s
HealthRetries=3
HealthStartPeriod=30s
HealthTimeout=10s
Notify=healthy
Label=org.missioncontrol.service=dashboard
Label=org.missioncontrol.stack=primary
AutoUpdate=registry
Network=stack.network
Pull=newer
Retry=3
RetryDelay=5s
DropCapability=all
NoNewPrivileges=true
RunInit=true
ReadOnly=false
StopTimeout=30
Environment=PORT=3000
Environment=MISSION_CONTROL_HOST=0.0.0.0
Environment=LOG_LEVEL=info

[Service]
Restart=on-failure
RestartSec=30s
TimeoutStartSec=900
TimeoutStopSec=60

[Install]
WantedBy=default.target
```

### Secret Drop-In

```ini
# ~/.config/containers/systemd/mission-control.container.d/10-secrets.conf
# Create secrets:
#   podman secret create mc-jwt-secret --env JWT_SECRET=<random>
#   podman secret create mc-admin-key --env ADMIN_API_KEY=<key>

[Container]
Secret=mc-jwt-secret,type=env,target=JWT_SECRET
Secret=mc-admin-key,type=env,target=ADMIN_API_KEY
```

---

## Agentfield Platform

### Volume Definition

```ini
# ~/.config/containers/systemd/agentfield.volume
[Volume]
VolumeName=agentfield-config
Label=org.agentfield.service=platform
Label=org.agentfield.stack=primary
```

### Container Definition

```ini
# ~/.config/containers/systemd/agentfield.container
[Unit]
Description=Agentfield Platform
After=network-online.target
Wants=network-online.target

[Container]
Image=ghcr.io/agent-field/agentfield:latest
ContainerName=agentfield
PublishPort=127.0.0.1:3001:3001
Volume=agentfield.volume:/config:Z
UserNS=keep-id
HealthCmd=curl -sf http://localhost:3001/health || exit 1
HealthInterval=30s
HealthRetries=3
HealthStartPeriod=30s
HealthTimeout=10s
Notify=healthy
Label=org.agentfield.service=platform
Label=org.agentfield.stack=primary
AutoUpdate=registry
Network=stack.network
Pull=newer
Retry=3
RetryDelay=5s
DropCapability=all
NoNewPrivileges=true
RunInit=true
ReadOnly=false
StopTimeout=30
Environment=AGENTFIELD_PORT=3001
Environment=AGENTFIELD_HOST=0.0.0.0
Environment=LOG_LEVEL=info

[Service]
Restart=on-failure
RestartSec=30s
TimeoutStartSec=900
TimeoutStopSec=60

[Install]
WantedBy=default.target
```

### Secret Drop-In

```ini
# ~/.config/containers/systemd/agentfield.container.d/10-secrets.conf
# Create secrets:
#   podman secret create agentfield-db-url --env DATABASE_URL=<postgres://...>
#   podman secret create agentfield-api-key --env API_KEY=<key>

[Container]
Secret=agentfield-db-url,type=env,target=DATABASE_URL
Secret=agentfield-api-key,type=env,target=API_KEY
```

---

## Sablier Scale-Up-on-Demand

Sablier intercepts traffic and starts containers on-demand, then stops them after an idle period. It requires access to the Podman API socket.

```ini
# ~/.config/containers/systemd/sablier.container
[Unit]
Description=Sablier Scale-Up-on-Demand Container Manager
Wants=podman.socket
After=podman.socket
After=network-online.target
Wants=network-online.target

[Container]
Image=ghcr.io/sablierapp/sablier:latest
ContainerName=sablier
PublishPort=127.0.0.1:10000:10000
# Bind the rootless Podman API socket into the container
Volume=/run/user/%U/podman/podman.sock:/var/run/docker.sock:Z
UserNS=keep-id
Environment=SABLIER_DOCKER_HOST=unix:///var/run/docker.sock
Environment=SABLIER_API_PORT=10000
Environment=SABLIER_LOG_LEVEL=info
Environment=SABLIER_NAMESPACE_PROVIDER=podman
HealthCmd=curl -sf http://localhost:10000/health || exit 1
HealthInterval=30s
HealthRetries=3
HealthStartPeriod=15s
HealthTimeout=10s
Notify=healthy
Label=org.sablier.service=scaler
Label=org.sablier.stack=primary
AutoUpdate=registry
Network=stack.network
Pull=newer
Retry=3
RetryDelay=5s
DropCapability=all
NoNewPrivileges=true
RunInit=true
ReadOnly=false
StopTimeout=30

[Service]
Restart=on-failure
RestartSec=30s
TimeoutStartSec=900
TimeoutStopSec=60

[Install]
WantedBy=default.target
```

### Secret Drop-In

```ini
# ~/.config/containers/systemd/sablier.container.d/10-secrets.conf
# Prerequisite:
#   podman secret create sablier-auth-token --env SABLIER_AUTH_TOKEN=<token>

[Container]
Secret=sablier-auth-token,type=env,target=SABLIER_AUTH_TOKEN
```

---

## Multi-Service Orchestration

### Pattern 1: Shared Network (DNS-Based Discovery)

All services join `stack.network` via `Network=stack.network`. They resolve each other by container name through aardvark-dns:

- `http://openclaw:18789/` -- OpenClaw API
- `http://hermes:8080/` -- Hermes Agent
- `http://n8n:5678/` -- n8n workflow engine
- `http://mission-control:3000/` -- Mission Control dashboard
- `http://agentfield:3001/` -- Agentfield platform
- `http://sablier:10000/` -- Sablier management API

### Pattern 2: Explicit Service Dependencies

Use standard systemd `[Unit]` dependencies:

```ini
[Unit]
Description=My service that needs the database
Requires=redis.container
After=redis.container
BindsTo=redis.container
```

Quadlet auto-resolves `.container` suffixes to the generated `.service` names.

### Pattern 3: Pod (Co-Located Containers)

A `.pod` Quadlet groups containers into the same network namespace:

```ini
# my-app.pod
[Pod]
PodName=my-app
ExitPolicy=continue
Network=stack.network
PublishPort=127.0.0.1:3000:3000
UserNS=keep-id

# web.container (joins the pod)
[Container]
Image=my-web-app:latest
Pod=my-app.pod

# worker.container (joins the same pod)
[Container]
Image=my-worker:latest
Pod=my-app.pod
```

All containers in a pod can reach each other via `localhost`.

### Pattern 4: Volume Dependency

When a `.container` references `<name>.volume` in its `Volume=` key, Quadlet automatically:
1. Creates the named volume (via `<name>-volume.service`).
2. Adds `Wants` and `After` dependencies on the volume service.
3. Mounts the volume at the specified container path with SELinux label.

### Full Stack Layout

```
~/.config/containers/systemd/
  stack.network
  openclaw.container
  openclaw.container.d/10-secrets.conf
  hermes.container
  hermes.container.d/10-secrets.conf
  n8n.volume
  n8n.container
  n8n.container.d/10-secrets.conf
  mission-control.volume
  mission-control.container
  mission-control.container.d/10-secrets.conf
  agentfield.volume
  agentfield.container
  agentfield.container.d/10-secrets.conf
  sablier.container
  sablier.container.d/10-secrets.conf
```

### Start Everything at Boot

```bash
# All .container files have [Install] WantedBy=default.target
systemctl --user daemon-reload

# Or create a systemd target:
# ~/.config/systemd/user/stack.target
# [Unit]
# Description=Deployment Stack
# Wants=openclaw.service hermes.service n8n.service \
#        mission-control.service agentfield.service sablier.service

systemctl --user daemon-reload
systemctl --user enable --now stack.target
```

---

## Example .volume Quadlet Reference

```ini
# Minimal named volume
[Volume]

# Explicit name and labels
[Volume]
VolumeName=app-data
Label=org.app=my-service
Label=org.environment=production

# Volume with ownership
[Volume]
VolumeName=db-data
UID=1000
GID=1000
Label=org.app=database

# Volume seeded from an image
[Volume]
VolumeName=seeded-config
Driver=image
Image=docker.io/myorg/config-image:latest

# tmpfs volume (in-memory)
[Volume]
VolumeName=tmp-cache
Device=tmpfs
Type=tmpfs
Options=size=100M

# Host bind mount as volume
[Volume]
VolumeName=host-backup
Device=/mnt/backups
Type=none
Options=bind
```

Usage from a `.container` file:

```ini
[Container]
Volume=app-data.volume:/var/lib/app:Z
```

This automatically creates the volume and adds a dependency on `app-data-volume.service`.

### Managing Volumes

```bash
podman volume ls                              # List all volumes
podman volume inspect <name>                  # Inspect a volume

# Backup
podman volume export <name> > backup.tar

# Restore
podman volume rm <name>
podman volume create <name>
podman run --rm -v <name>:/data:Z -v $(pwd):/backup:Z \
  alpine tar xzf /backup/backup.tar -C /data

# Cleanup
podman volume prune
```

---

## Example .network Quadlet Reference

```ini
# Standard bridge network for service-to-service communication
[Network]
NetworkName=mynet
Driver=bridge
Subnet=10.90.0.0/24
Gateway=10.90.0.1
IPRange=10.90.0.0/28
Label=org.stack=primary
Label=org.environment=production

# Internal-only network (no external access)
[Network]
NetworkName=internal
Driver=bridge
Subnet=10.91.0.0/24
Internal=true

# IPv6 dual-stack
[Network]
NetworkName=dual-stack
Driver=bridge
Subnet=10.92.0.0/24
IPv6=true
```

Usage from a `.container` file:

```ini
[Container]
Network=mynet.network
NetworkAlias=my-alias
```

Quadlet auto-creates:
1. A Podman network named `systemd-mynet` (or whatever `NetworkName=` specifies).
2. A systemd service `mynet-network.service`.
3. A dependency from the container to the network service.

### Managing Networks

```bash
podman network ls                             # List all networks
podman network inspect mynet                  # Inspect a network
podman network rm mynet                       # Remove a network
```

---

---

## Example .kube Quadlet (Kubernetes-Style Deployment)

The `.kube` Quadlet runs `podman kube play` from a Kubernetes YAML file, converting a K8s Pod/Service spec into a systemd-managed container stack.

```ini
# ~/.config/containers/systemd/stack.kube
[Unit]
Description=Full Agent Stack (Kubernetes-style)
After=network-online.target
Wants=network-online.target

[Kube]
# Path to the Kubernetes YAML file
Yaml=%h/.config/containers/systemd/stack.yaml
# Additional podman kube play options
Network=stack.network
UserNS=keep-id
# Adopt existing containers on restart
ConfigMap=%h/.config/containers/systemd/stack-config.yaml
SetWorkingDirectory=true

[Install]
WantedBy=default.target
```

### Corresponding Kubernetes YAML

```yaml
# ~/.config/containers/systemd/stack.yaml
apiVersion: v1
kind: Pod
metadata:
  name: agent-stack
  labels:
    app: agent-stack
spec:
  containers:
    - name: openclaw
      image: ghcr.io/openclaw/openclaw:latest
      ports:
        - containerPort: 18789
        - containerPort: 18790
      volumeMounts:
        - name: data
          mountPath: /data
    - name: hermes
      image: docker.io/nousresearch/hermes-agent:main
      ports:
        - containerPort: 8080
      env:
        - name: HERMES_HOST
          value: "0.0.0.0"
        - name: HERMES_PORT
          value: "8080"
  volumes:
    - name: data
      hostPath:
        path: /home/user/.openclaw
```

### Kubernetes Pod + Service Example

```yaml
# ~/.config/containers/systemd/stack.yaml
apiVersion: v1
kind: Pod
metadata:
  name: n8n
  labels:
    app: n8n
spec:
  containers:
    - name: n8n
      image: docker.io/n8nio/n8n:latest
      ports:
        - containerPort: 5678
      env:
        - name: N8N_PORT
          value: "5678"
        - name: N8N_PROTOCOL
          value: "http"
---
apiVersion: v1
kind: Service
metadata:
  name: n8n
spec:
  ports:
    - port: 5678
      targetPort: 5678
```

Quadlet converts the Service definition into iptables/nftables port forwarding rules (rootful) or publishes ports via pasta (rootless). Each container in the Pod YAML maps to a systemd service unit under a generated `kube-pod-<name>.service`.

**Note:** Secrets from Kubernetes `env.valueFrom.secretKeyRef` are not automatically resolved by `podman kube play`. Use Quadlet drop-in files for secret injection:

```ini
# ~/.config/containers/systemd/stack.kube.d/10-secrets.conf
[Kube]
Secret=openclaw-api-key,type=env,target=OPENCLAW_API_KEY
```

---

## Example .build Quadlet (Build Then Run)

The `.build` Quadlet builds a container image from a Containerfile, then the resulting image is available for a `.container` unit to use.

```ini
# ~/.config/containers/systemd/agent-core.build
[Unit]
Description=Build agent-core image
After=network-online.target

[Build]
# Path to Containerfile or directory with Containerfile
File=%h/agent-core/Containerfile
# Image tag to produce
Tag=localhost/agent-core:latest
# Build context directory (default: File's parent directory)
ContextDir=%h/agent-core
# Build arguments
BuildArg=VERSION=1.0.0
BuildArg=GOFLAGS="-tags=containers_image_openpgp"
# Force rebuild even if image exists
ForceRM=true
# Labels for the built image
Label=org.agent.service=core
# Pull base image
Pull=true

[Install]
WantedBy=default.target
```

### Container That Uses the Built Image

```ini
# ~/.config/containers/systemd/agent-core.container
[Unit]
Description=Agent Core Service
After=agent-core.build
Requires=agent-core.build

[Container]
Image=localhost/agent-core:latest
ContainerName=agent-core
PublishPort=127.0.0.1:9090:9090
Volume=%h/agent-core/config:/config:Z
UserNS=keep-id
HealthCmd=curl -sf http://localhost:9090/health || exit 1
HealthInterval=30s
HealthRetries=3
Notify=healthy
DropCapability=all
NoNewPrivileges=true

[Service]
Restart=on-failure
TimeoutStartSec=900

[Install]
WantedBy=default.target
```

The `.container` file references `agent-core.build` in its `[Unit]` dependencies, ensuring the build completes before the container starts. The `.build` service type is `Type=oneshot` -- it runs once to build the image, then exits.

---

## Example .image Quadlet (Pre-Pull Image)

The `.image` Quadlet pulls an image during system activation, ensuring it is available locally before any container that needs it starts. Useful for large images that take time to download.

```ini
# ~/.config/containers/systemd/llama-cpp.image
[Unit]
Description=Pre-pull llama-cpp model image
After=network-online.target
Wants=network-online.target

[Image]
Image=docker.io/llama-cpp/llama-cpp:latest
# Pull all tags matching the pattern
AllTags=false
# Architecture override (useful for multi-arch images)
Arch=arm64
# OS override
OS=linux

[Install]
WantedBy=default.target
```

```ini
# ~/.config/containers/systemd/llama-cpp.container
[Unit]
Description=LLM Inference Container
After=llama-cpp.image
Requires=llama-cpp.image

[Container]
Image=docker.io/llama-cpp/llama-cpp:latest
ContainerName=llama-cpp
PublishPort=127.0.0.1:8080:8080
Volume=%h/models:/models:Z
UserNS=keep-id
DropCapability=all
NoNewPrivileges=true

[Service]
Restart=on-failure

[Install]
WantedBy=default.target
```

The `.image` service type is `Type=oneshot`. The `[Unit] Requires=llama-cpp.image` in the container ensures the image is pulled before the container attempts to start. If the pull fails, the container will not start.

---

## Template Units (Scalable Services)

Quadlet supports systemd template units via the `@` in the filename. Template units allow running multiple instances of the same service configuration.

### Container Template

```ini
# ~/.config/containers/systemd/worker@.container
[Unit]
Description=Worker instance %i
After=network-online.target
Wants=network-online.target

[Container]
Image=docker.io/myapp/worker:latest
ContainerName=worker-%i
# Each instance gets a different port via the template variable
PublishPort=127.0.0.1:%i:%i
UserNS=keep-id
HealthCmd=curl -sf http://localhost:%i/health || exit 1
HealthInterval=30s
HealthRetries=3
Notify=healthy
AutoUpdate=registry
DropCapability=all
NoNewPrivileges=true

# Template-specific environment variables
Environment=WORKER_ID=%i
Environment=WORKER_PORT=%i

[Service]
Restart=on-failure
TimeoutStartSec=900

[Install]
WantedBy=default.target
DefaultInstance=8080
```

### Start Multiple Instances

```bash
# Start specific instances
systemctl --user start worker@8080.service
systemctl --user start worker@8081.service
systemctl --user start worker@8082.service

# With DefaultInstance in [Install], the default starts at boot
# Override the default:
systemctl --user disable worker@8080.service
systemctl --user enable worker@9090.service
```

The `%i` specifier in the Quadlet file is replaced with the instance name. Template units are particularly useful for:
- Worker pools (varying only by port/instance ID)
- Multi-tenant services
- Canary deployments (run one new-instance alongside stable)

---

## Artifact Quadlet (OCI Artifacts)

The `.artifact` Quadlet pulls OCI artifacts (non-container data stored in OCI registries) and makes them available as files. Useful for distributing ML models, configuration files, or firmware as OCI artifacts.

```ini
# ~/.config/containers/systemd/model.artifact
[Unit]
Description=Download LLM model artifact
After=network-online.target

[Artifact]
Image=ghcr.io/myorg/models/llama:quantized-q4
# Extract to this directory (created if it doesn't exist)
OutputDir=%h/models/llama-q4
# Which paths from the artifact to extract
# (empty = extract all)
Paths=model.bin,tokenizer.json,config.json

[Install]
WantedBy=default.target
```

Artifact Quadlets are `Type=oneshot` -- they run once to download and extract the artifact, then exit. Containers can reference the artifact directory via bind mounts:

```ini
# ~/.config/containers/systemd/llm-server.container
[Unit]
Description=LLM Inference Server
After=model.artifact
Requires=model.artifact

[Container]
Image=docker.io/llama-cpp/llama-cpp:latest
Volume=%h/models/llama-q4:/models:Z
# ...
```

---

## Related

- [[podman]] -- Main wiki entry with overview and Quadlet integration
- [[podman-architecture]] -- Deep-dive architecture document
- [[podman-deployment]] -- Deployment guide with step-by-step instructions
- [[podman-profile]] -- Quick-reference profile card
- [[podman.codegraph-verify]] -- Codegraph verification of architecture claims
