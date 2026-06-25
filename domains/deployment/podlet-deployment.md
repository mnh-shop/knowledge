---
name: podlet-deployment
tags: [acp, ai-llm, container, conversion, deployment, docker, git, podlet, podman, quadlet, quadlet-generator, rust, storage, systemd]
description: "Podlet Deployment Guide"
source: sources/podlet/
---

# Podlet Deployment Guide
**Source:** `sources/podlet/`

## Installation

### From Cargo (Recommended for Development)

```bash
cargo install podlet
```

This compiles from source and installs to `~/.cargo/bin/podlet`. Requires Rust toolchain.

### Homebrew

```bash
brew install podlet
```

### From Prebuilt Binaries

Download the latest release from <https://github.com/containers/podlet/releases>:

```bash
# Download and extract
curl -LO https://github.com/containers/podlet/releases/latest/download/podlet-x86_64-apple-darwin.tar.gz
tar xzf podlet-x86_64-apple-darwin.tar.gz
sudo mv podlet /usr/local/bin/
```

Available architectures: `x86_64-unknown-linux-gnu`, `aarch64-unknown-linux-gnu`, `x86_64-apple-darwin`, `aarch64-apple-darwin`.

### Container Image

```bash
podman pull ghcr.io/containers/podlet:latest
podman run --rm ghcr.io/containers/podlet podman run quay.io/podman/hello
```

### From Source

```bash
git clone https://github.com/containers/podlet.git
cd podlet
cargo build --release
sudo cp target/release/podlet /usr/local/bin/
```

---

## Usage Patterns

### Pattern 1: Quick Check (stdout)

Convert a `podman run` command to Quadlet format and review output before writing:

```bash
podlet podman run -d --name openclaw-acp \
  -p 8080:8080 \
  -v openclaw-data:/data \
  --restart unless-stopped \
  ghcr.io/openclaw/acp:latest
```

Output:
```ini
# ServiceName=openclaw-acp
[Container]
ContainerName=openclaw-acp
Image=ghcr.io/openclaw/acp:latest
PublishPort=8080:8080
Volume=openclaw-data:/data

[Service]
Restart=always
```

### Pattern 2: Write to Unit Directory (Production)

Convert and deploy directly into the Quadlet unit directory for immediate systemd integration:

```bash
# Non-root user
podlet -u podman run -d --name openclaw-acp \
  -p 8080:8080 \
  -v openclaw-data:/data \
  --restart unless-stopped \
  ghcr.io/openclaw/acp:latest

# Reload and start
systemctl --user daemon-reload
systemctl --user start openclaw-acp.service

# Root
sudo podlet -u podman run -d --name openclaw-acp \
  -p 8080:8080 \
  -v openclaw-data:/data \
  ghcr.io/openclaw/acp:latest

sudo systemctl daemon-reload
sudo systemctl start openclaw-acp.service
```

### Pattern 3: Write to Custom Output Directory

```bash
mkdir -p ./quadlets
podlet -f ./quadlets podman run ...
```

### Pattern 4: Single .quadlets File

For distributing a complete service definition as one file:

```bash
podlet --quadlets-file my-stack podman run ...
# Creates: ./my-stack.quadlets
```

### Pattern 5: Compose to Quadlet

Convert a Docker Compose file to multiple Quadlet files:

```bash
# Default: separate .container, .volume, .network files
podlet -u compose docker-compose.yml

# As a pod: one .pod + multiple linked .container files
podlet -u compose --pod docker-compose.yml

# As Kubernetes: .kube file + Kubernetes YAML
podlet -u compose --kube docker-compose.yml
```

### Pattern 6: Generate from Running Objects

```bash
# From a running container
podlet generate container my-container
podlet -u generate container my-container

# From a running pod (generates .pod + .container per non-infra container)
podlet -u generate pod my-pod

# From a network
podlet -u generate network my-network

# From a volume
podlet -u generate volume my-volume

# From an image
podlet -u generate image my-image
```

---

## Integration with Agent Deployment Workflow

Our standard workflow for deploying agent services with Quadlet via Podlet:

### Step 1: Prototype with podman run

```bash
# Test the container with all options
podman run -d --name hermes-agent \
  -e AGENT_MODE=production \
  -e DB_HOST=localhost \
  -v hermes-config:/etc/hermes:ro \
  -v hermes-data:/var/lib/hermes \
  -p 9000:9000 \
  --restart unless-stopped \
  --secret db-credentials,type=env,target=DB_CREDS \
  ghcr.io/hermes/agent:latest
```

### Step 2: Convert with Podlet

```bash
# Generate Quadlet and review
podlet podman run -d --name hermes-agent \
  -e AGENT_MODE=production \
  -e DB_HOST=localhost \
  -v hermes-config:/etc/hermes:ro \
  -v hermes-data:/var/lib/hermes \
  -p 9000:9000 \
  --restart unless-stopped \
  --secret db-credentials,type=env,target=DB_CREDS \
  ghcr.io/hermes/agent:latest
```

### Step 3: Refine and Write

```bash
# Add systemd unit metadata with --unit flags
podlet -u \
  --unit Description="Hermes Agent Service" \
  --unit Wants=network-online.target \
  --unit After=network-online.target \
  --install WantedBy=multi-user.target \
  podman run ... [same args]
```

### Step 4: Add systemd Drop-ins (Optional)

Create `/etc/systemd/system/hermes-agent.service.d/override.conf` for environment-specific overrides without touching the generated Quadlet file:

```ini
[Service]
Environment=LOG_LEVEL=debug
RestartSec=30s
```

### Step 5: Test Without Deployment

```bash
podlet podman run ... | podman-run-from-quadlet --dry-run
# Or just inspect the .container file before dropping into the unit directory
```

---

## Converting Agent Containers to Quadlet Services

### Single Agent Container

```bash
# Create Quadlet in user unit directory
podlet -u podman run -d --name openclaw-agent \
  -e ACP_SERVER=https://acp.example.com:8443 \
  -e AGENT_ID=agent-01 \
  -v agent-config:/etc/openclaw:ro \
  -v agent-data:/var/lib/openclaw \
  -p 8181:8181 \
  --restart unless-stopped \
  ghcr.io/openclaw/agent:latest

# Enable and start
systemctl --user daemon-reload
systemctl --user enable --now openclaw-agent.service
```

### Multi-Container Hermes Stack with Pod

```bash
# Convert compose file as a pod
podlet -u compose --pod docker-compose-hermes.yaml

# This generates:
#   hermes.pod          - Pod port mappings
#   hermes-agent.container - Agent with Pod=hermes.pod
#   hermes-db.container    - Database with Pod=hermes.pod

# Start the whole stack
systemctl --user start hermes-pod.service
# This starts all containers in the pod
```

### With Secrets

```bash
# First create the secret
podman secret create postgres-credentials ./creds.json

# Reference it in Quadlet
podlet -u podman run -d --name hermes-db \
  -e POSTGRES_DB=hermes \
  --secret postgres-credentials,type=env,target=POSTGRES_CREDS \
  docker.io/library/postgres:16
```

---

## Best Practices

1. **Always review generated Quadlet files** before deploying. Podlet handles most cases correctly, but Quadlet format has nuances.

2. **Use `--split-options` or `--split-options JoinOption`** when you want readable multi-line Quadlet files instead of joined lines.

3. **Specify Podman version with `--podman-version`** when targeting older systems. Default targets the latest.

4. **Use `--absolute-host-paths`** when deploying to different machines to avoid broken relative paths.

5. **Combine with systemd drop-ins** for environment-specific overrides. The generated Quadlet file stays clean, and deployment-specific settings go in `/etc/systemd/system/<name>.service.d/`.

6. **Use `--skip-services-check`** only when you're confident there are no naming conflicts, or in CI/CD where D-Bus may not be available.

7. **Generate from running containers** (`podlet generate container <name>`) as a migration tool for existing deployments. This is invaluable when moving from manual `podman` to Quadlet-managed services.

8. **For compose files with unsupported features**, pre-process the compose file or use `podlet podman run` directly for each service.

9. **Name things deliberately**: Quadlet uses the filename (minus extension) as the service name. Use `--name` to control filenames.

10. **Keep generated files in version control**: Store `.container`, `.pod`, `.kube`, `.volume`, `.network` files in your repo alongside compose files for reproducibility.

## Related

- [[podlet-architecture]] -- Conversion pipeline and flag-to-Quadlet mapping
- [[podlet-quadlet-examples]] -- Detailed conversion examples for common scenarios
- [[podlet]] -- Wiki overview, key features, and source file roles
