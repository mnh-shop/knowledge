# Hermes Agent -- Rootless Podman Quadlet Deployment

**Type:** Deployment asset (rootless Podman Quadlet)  
**Status:** Reference configuration for production deployment  

This asset provides production-ready Quadlet configurations for deploying Hermes Agent under Rootless Podman with systemd-native lifecycle management.

Quadlet converts `.container`, `.volume`, `.network`, `.secret`, and `.kube` files into systemd unit files, giving Hermes Agent the same service management as a native application.

---

## Table of Contents

- [Why Quadlet for Hermes](#why-quadlet-for-hermes)
- [Prerequisites](#prerequisites)
- [Minimal Setup: Single Container](#minimal-setup-single-container)
- [Full Stack: Agent + PostgreSQL](#full-stack-agent--postgresql)
- [Secret Injection](#secret-injection)
- [Volume Definitions](#volume-definitions)
- [Network Definitions](#network-definitions)
- [Drop-in Configuration Pattern](#drop-in-configuration-pattern)
- [Health Check Configuration](#health-check-configuration)
- [All-in-One Directory Layout](#all-in-one-directory-layout)
- [Setup Steps](#setup-steps)
- [Migration from Docker Compose](#migration-from-docker-compose)
- [Troubleshooting Quadlet](#troubleshooting-quadlet)
- [Key Quadlet Keys Explained](#key-quadlet-keys-explained)

---

## Why Quadlet for Hermes

1. **Systemd-native lifecycle** -- `systemctl --user` manages restart, logging, dependencies. No Docker Compose daemon needed.
2. **Single image** -- `docker.io/nousresearch/hermes-agent:latest` is self-contained (agent, MCP bridge, ACP adapter, gateway, dashboard all in one image).
3. **Host networking** -- Hermes uses `Network=host` for direct port access on 8642 and 9119. No port mapping indirection.
4. **Environment file injection** -- `EnvironmentFile=` points to a mode-0600 file for clean API key management.
5. **Health checks** -- Quadlet `HealthCmd` monitors both gateway (`:8642/health`) and dashboard (`:9119/api/status`).
6. **Multi-service stack** -- Add PostgreSQL, Mnemosyne, or other services as independent Quadlet units.

---

## Prerequisites

```bash
# Podman 4.0+ with Quadlet support
podman version

# Enable podman-user service
systemctl --user enable --now podman.socket

# Verify Quadlet directory exists
mkdir -p ~/.config/containers/systemd/

# Verify systemd --user is available
systemctl --user list-units > /dev/null
```

---

## Minimal Setup: Single Container

The simplest Quadlet deployment runs Hermes Agent with host networking, SQLite state, and API keys from an environment file.

### `~/.config/containers/systemd/hermes-agent.container`

```ini
[Unit]
Description=Hermes Agent Gateway + Dashboard
Documentation=https://github.com/NousResearch/hermes-agent
After=network-online.target
Wants=network-online.target

[Container]
Image=docker.io/nousresearch/hermes-agent:latest
ContainerName=hermes
Exec=gateway run
Network=host

# Dashboard
Environment=HERMES_DASHBOARD=1
Environment=HERMES_DASHBOARD_HOST=127.0.0.1
Environment=HERMES_DASHBOARD_PORT=9119

# Gateway API
Environment=API_SERVER_HOST=127.0.0.1
Environment=API_SERVER_ENABLED=true
Environment=API_SERVER_PORT=8642

# Container UID mapping (rootless Podman)
Environment=HERMES_UID=%U

# API keys and secrets from env file
EnvironmentFile=%h/.config/hermes/agent.env

# Persistent state
Volume=%h/.hermes:/opt/data:Z

# Health check: monitor gateway + dashboard
HealthCmd=curl -fsS http://localhost:8642/health && curl -fsS http://localhost:9119/api/status || exit 1
HealthInterval=10s
HealthTimeout=5s
HealthRetries=5
HealthStartPeriod=30s

[Service]
Type=forking
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=default.target
```

### Environment File

`~/.config/hermes/agent.env`:

```bash
# Model provider API keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Optional: channel tokens
TELEGRAM_BOT_TOKEN=...
DISCORD_BOT_TOKEN=...

# Optional: secrets manager integration
# BRAVE_API_KEY=...
# GEMINI_API_KEY=...
```

**Important:** The env file must be mode 0600:

```bash
chmod 600 ~/.config/hermes/agent.env
```

---

## Full Stack: Agent + PostgreSQL

For production deployments requiring persistent state beyond SQLite, add PostgreSQL for session and memory storage.

### Network

`~/.config/containers/systemd/hermes.network`

```ini
[Network]
Description=Hermes internal network
Subnet=10.89.0.0/24
```

### PostgreSQL Container

`~/.config/containers/systemd/hermes-postgres.container`

```ini
[Unit]
Description=PostgreSQL for Hermes Agent
After=network-online.target
Requires=hermes.network

[Container]
Image=docker.io/postgres:16-alpine
ContainerName=hermes-postgres
Volume=%h/.hermes/pgdata:/var/lib/postgresql/data:Z
Network=hermes.network

Environment=POSTGRES_DB=hermes
Environment=POSTGRES_USER=hermes
Environment=POSTGRES_PASSWORD=hermes-secret-password

# Health check: pg_isready
HealthCmd=pg_isready -U hermes
HealthInterval=5s
HealthRetries=10

[Service]
Restart=always
RestartSec=5s

[Install]
WantedBy=default.target
```

### Agent Container (PostgreSQL mode)

`~/.config/containers/systemd/hermes-agent.container`

```ini
[Unit]
Description=Hermes Agent (PostgreSQL)
Documentation=https://github.com/NousResearch/hermes-agent
After=network-online.target hermes-postgres.service
Wants=network-online.target
Requires=hermes-postgres.service

[Container]
Image=docker.io/nousresearch/hermes-agent:latest
ContainerName=hermes
Exec=gateway run
Network=hermes.network

# PostgreSQL connection
Environment=HERMES_DB_URL=postgresql://hermes:hermes-secret-password@hermes-postgres:5432/hermes

# Dashboard
Environment=HERMES_DASHBOARD=1
Environment=HERMES_DASHBOARD_HOST=0.0.0.0
Environment=HERMES_DASHBOARD_PORT=9119

# Gateway API
Environment=API_SERVER_HOST=0.0.0.0
Environment=API_SERVER_ENABLED=true
Environment=API_SERVER_PORT=8642

# Container UID mapping
Environment=HERMES_UID=%U

# API keys
EnvironmentFile=%h/.config/hermes/agent.env

# Persistent state
Volume=%h/.hermes:/opt/data:Z

# Health checks
HealthCmd=curl -fsS http://localhost:8642/health || exit 1
HealthInterval=10s
HealthTimeout=5s
HealthRetries=5
HealthStartPeriod=30s

# Publish ports for external access
PublishPort=127.0.0.1:8642:8642
PublishPort=127.0.0.1:9119:9119

[Service]
Type=forking
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=default.target
```

**Important change with bridge networking:** When using `Network=hermes.network` instead of `Network=host`, the `API_SERVER_HOST` and `HERMES_DASHBOARD_HOST` must be `0.0.0.0` to bind within the pod network, and `PublishPort` is required for external access.

### Pod Mode (Alternative to Bridge Network)

Use a pod when you want Docker-style DNS resolution between containers under host networking.

`~/.config/containers/systemd/hermes.pod`

```ini
[Unit]
Description=Hermes Stack Pod
After=network-online.target
Wants=network-online.target

[Pod]
PodName=hermes
PublishPort=127.0.0.1:8642:8642
PublishPort=127.0.0.1:9119:9119
Network=bridge

[Install]
WantedBy=default.target
```

Then add `Pod=hermes.pod` to the `[Container]` section of both `.container` files.

---

## Secret Injection

Quadlet supports two patterns for secrets:

### Pattern 1: EnvironmentFile (Recommended for Simplicity)

Use `EnvironmentFile=` pointing to a mode-0600 file outside the container:

```ini
EnvironmentFile=%h/.config/hermes/agent.env
```

The `%h` specifier expands to the user's home directory.

### Pattern 2: Podman Secrets (Recommended for Multi-Key Management)

Each API key can be a separate Podman secret for fine-grained access control.

`~/.config/containers/systemd/hermes-anthropic-key.secret`

```ini
[Secret]
Label=hermes-anthropic-key
```

Create and inject:

```bash
# Create secrets
echo "sk-ant-..." | podman secret create hermes-anthropic-key -
echo "sk-..." | podman secret create hermes-openai-key -

# Reference in .container file
# Secret=hermes-anthropic-key,type=env,target=ANTHROPIC_API_KEY
# Secret=hermes-openai-key,type=env,target=OPENAI_API_KEY
```

### Secret Injection Comparison

| Method | Pros | Cons |
|--------|------|------|
| `EnvironmentFile=` | Simple, single file, easy to backup | All secrets in one file |
| `Secret=` (Podman secrets) | Per-secret ACL, encrypted at rest | More files to manage |
| `Environment=` inline | Visible in `systemctl cat` | Avoid for secrets |

---

## Volume Definitions

For explicit volume management with Quadlet:

`~/.config/containers/systemd/hermes-state.volume`

```ini
[Volume]
Label=hermes-state
```

Reference in the container definition:

```ini
Volume=hermes-state.volume:/opt/data:Z
```

Using a named volume instead of a bind mount (`%h/.hermes:/opt/data:Z`) provides:
- Automatic lifecycle management via `podman volume`
- Encryption support (when configured)
- Better isolation from host filesystem

However, bind mounts are preferred for:
- Direct backup access
- Easy inspection from the host
- Sharing state with other tools (e.g., hermes-workspace)

---

## Network Definitions

### Host Network (Default)

```ini
Network=host
```

**Pros:** No port mapping, direct access, simple configuration, SSE streaming works natively.  
**Cons:** No network isolation between containers, port conflicts possible.

### Bridge Network

```ini
Network=hermes.network
```

With a `.network` file:

```ini
[Network]
Subnet=10.89.0.0/24
```

**Pros:** Container isolation, DNS resolution between containers.  
**Cons:** Requires `PublishPort`, `API_SERVER_HOST=0.0.0.0`, SSE may need proxy configuration.

### Pod Network

Using a `.pod` file:

```ini
[Pod]
PodName=hermes
PublishPort=127.0.0.1:8642:8642
PublishPort=127.0.0.1:9119:9119
```

**Pros:** Containers share network namespace (localhost access), DNS resolution, port isolation.  
**Cons:** All containers in the pod see each other's ports.

---

## Drop-in Configuration Pattern

Quadlet supports systemd-style drop-in directories for modular configuration. Create a directory with `.container.d/` suffix:

```
~/.config/containers/systemd/hermes-agent.container.d/
  channels.conf          # Platform channel configuration
  mcp.conf               # MCP server configuration
  debugging.conf         # Debug logging overrides
```

Each file is a plain-text snippet that appends to the `[Container]` section:

**`channels.conf`**:
```ini
Environment=TELEGRAM_BOT_TOKEN=...
Environment=DISCORD_BOT_TOKEN=...
```

**`mcp.conf`**:
```ini
Environment=MCP_PORT=...
Environment=ACP_PORT=...
```

**`debugging.conf`**:
```ini
Environment=LOG_LEVEL=debug
Environment=HERMES_GATEWAY_STARTUP_TRACE=1
```

Drop-ins are merged in lexicographic order. They are a clean way to separate concerns without editing the main `.container` file.

---

## Health Check Configuration

Quadlet health checks run from the host namespace (not inside the container), so `curl` and other tools are available even in distroless images.

### Gateway + Dashboard Health Check

```ini
[Container]
HealthCmd=curl -fsS http://localhost:8642/health && curl -fsS http://localhost:9119/api/status || exit 1
HealthInterval=10s
HealthTimeout=5s
HealthRetries=5
HealthStartPeriod=30s
```

### PostgreSQL Health Check

```ini
HealthCmd=pg_isready -U hermes
HealthInterval=5s
HealthRetries=10
```

### Viewing Health Status

```bash
# Check overall service health
systemctl --user status hermes-agent.service

# Run health check manually
podman healthcheck run hermes

# View health check logs
podman inspect hermes | jq '.[0].State.Health'

# Disable health checks for debugging
# Comment out HealthCmd lines in .container file and daemon-reload
```

### Health Check Keys Explained

| Key | Value in Example | Meaning |
|-----|-----------------|---------|
| `HealthCmd` | `curl -fsS http://localhost:8642/health ...` | Command run from host to check liveness |
| `HealthInterval` | `10s` | Every 10 seconds |
| `HealthTimeout` | `5s` | Command must complete within 5 seconds |
| `HealthRetries` | `5` | Mark unhealthy after 5 consecutive failures |
| `HealthStartPeriod` | `30s` | Wait 30 seconds before first check (grace period for boot) |

---

## All-in-One Directory Layout

For organized multi-service deployments, create all Quadlet files in a subdirectory:

```
~/.config/containers/systemd/hermes/
  hermes.pod                      # Pod (optional)
  hermes-agent.container          # Main agent service
  hermes-postgres.container       # PostgreSQL (optional)
  hermes-anthropic-key.secret     # Podman secret (optional)
  hermes-openai-key.secret        # Podman secret (optional)
  hermes-network.network          # Bridge network (optional)
```

Then reference them from the main Quadlet directory or symlink:

```bash
mkdir -p ~/.config/containers/systemd/hermes
# Create files in hermes/
systemctl --user link ~/.config/containers/systemd/hermes/hermes-agent.container
```

Or use a single flat directory with well-named files:

```
~/.config/containers/systemd/
  hermes-agent.container
  hermes-postgres.container
  hermes.network
  hermes-anthropic-key.secret
  hermes-openai-key.secret
```

---

## Setup Steps

### Fresh Installation

```bash
# 1. Create config directories
mkdir -p ~/.config/hermes ~/.config/containers/systemd ~/.hermes

# 2. Write the environment file with API keys
cat > ~/.config/hermes/agent.env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
EOF
chmod 600 ~/.config/hermes/agent.env

# 3. Write the Quadlet .container file
# (copy the minimal template from above)

# 4. Pull the image
podman pull docker.io/nousresearch/hermes-agent:latest

# 5. Reload systemd and start
systemctl --user daemon-reload
systemctl --user start hermes-agent.service

# 6. Enable on boot
systemctl --user enable hermes-agent.service

# 7. Verify
systemctl --user status hermes-agent.service
journalctl --user -u hermes-agent.service -n 30 --no-pager
```

### First-Time Agent Setup

```bash
# After the service is running, configure channels
podman exec hermes hermes gateway enroll --platform telegram --token "<bot-token>"

# Or run the interactive setup wizard
podman exec -it hermes hermes setup

# Verify configuration
podman exec hermes hermes doctor
```

### Verification Commands

```bash
# Service status
systemctl --user status hermes-agent.service

# View generated systemd unit
systemctl --user cat hermes-agent.service

# Health check
curl -s http://localhost:8642/health
curl -s http://localhost:9119/api/status

# Container state
podman ps --filter name=hermes
podman inspect hermes | jq '.[0].State.Status'

# Logs
journalctl --user -u hermes-agent.service -f
podman logs hermes
```

---

## Migration from Docker Compose

If you have an existing Docker Compose deployment:

```bash
# 1. Stop Compose
docker compose down

# 2. Extract current configuration
docker compose config > /tmp/hermes-compose-config.yml

# 3. Create Quadlet files (see templates above)
#    - Copy environment variables from docker-compose.yml
#    - Convert volumes to Quadlet Volume= directives
#    - Convert ports to PublishPort= or use Network=host

# 4. Create environment file
cp ~/.config/hermes/agent.env ~/.config/hermes/agent.env.bak  # backup
# Ensure env file exists with correct permissions

# 5. Start
systemctl --user daemon-reload
systemctl --user start hermes-agent.service
systemctl --user enable hermes-agent.service

# 6. Verify
systemctl --user status hermes-agent.service
```

### Compose to Quadlet Mapping

| Docker Compose | Quadlet Equivalent |
|---------------|-------------------|
| `image:` | `Image=` |
| `container_name:` | `ContainerName=` |
| `ports:` | `PublishPort=` or `Network=host` |
| `environment:` | `Environment=` or `EnvironmentFile=` |
| `volumes:` | `Volume=` |
| `env_file:` | `EnvironmentFile=` |
| `command:` | `Exec=` |
| `healthcheck:` | `HealthCmd=`, `HealthInterval=`, etc. |
| `restart: unless-stopped` | `[Service] Restart=always` |
| `depends_on:` | `[Unit] Requires=` / `After=` |
| `networks:` | `Network=` or `Pod=` |

---

## Troubleshooting Quadlet

### Check Unit Status

```bash
systemctl --user status hermes-agent.service
systemctl --user list-units 'hermes*'
```

### View Generated Unit

Quadlet auto-generates systemd units from `.container` files:

```bash
systemctl --user cat hermes-agent.service
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Unit not found after creating .container | Run `systemctl --user daemon-reload` |
| `:Z` SELinux label fails | Remove `:Z` from volume mounts on non-SELinux systems (macOS) |
| Port 8642 already in use | Use `Network=host` and check `sudo lsof -i :8642` |
| Environment file not found | Verify `EnvironmentFile=%h/.config/hermes/agent.env` -- `%h` expands to `$HOME` |
| Secret not found | Verify with `podman secret inspect <name>` |
| Container not restarting | Check `journalctl --user -u hermes-agent.service` for errors |
| Health check failing | Run health command manually: `curl -fsS http://localhost:8642/health` |
| Volume permission denied | `chmod 755 ~/.hermes/` or `podman unshare chown 1000:1000 ~/.hermes/` |
| Image pull failures | Run `podman pull docker.io/nousresearch/hermes-agent:latest` manually first |
| host-gateway not resolving | With bridge networking, use container names for DNS instead |

### Log Management

```bash
# Follow systemd journal
journalctl --user -u hermes-agent.service -f

# Recent logs
journalctl --user -u hermes-agent.service -n 50 --no-pager

# Podman container logs
podman logs hermes

# Follow podman logs
podman logs -f hermes

# Journald by time range
journalctl --user -u hermes-agent.service --since "5 minutes ago"

# Increase podman log size (in containers.conf)
log_size_max = 10000000  # 10 MB default
```

### Debugging Quadlet Generation

```bash
# Test Quadlet generation without starting
/usr/lib/systemd/system-generators/podman-system-generator --user --dry-run

# View intermediate files
ls -la /run/user/$(id -u)/systemd/generator/
```

---

## Key Quadlet Keys Explained

### `[Unit]` Section

| Key | Example | Purpose |
|-----|---------|---------|
| `Description` | `Hermes Agent Gateway + Dashboard` | Human-readable name for `systemctl status` |
| `Documentation` | `https://github.com/...` | URL for `systemctl help` |
| `After` | `network-online.target` | Start only after these units are active |
| `Wants` | `network-online.target` | Soft dependency (unit starts even if target fails) |
| `Requires` | `hermes-postgres.service` | Hard dependency (unit stops if dependency fails) |

### `[Container]` Section

| Key | Example | Purpose |
|-----|---------|---------|
| `Image` | `docker.io/nousresearch/hermes-agent:latest` | Container image to run |
| `ContainerName` | `hermes` | Name for `podman ps` / `podman exec` |
| `Exec` | `gateway run` | Override the image's default `CMD` (not `ENTRYPOINT`) |
| `Network` | `host` | Network mode: `host`, bridge, or `pod-name.pod` |
| `Pod` | `hermes.pod` | Join an existing pod |
| `PublishPort` | `127.0.0.1:8642:8642` | Map container port to host port |
| `Environment` | `HERMES_DASHBOARD=1` | Set an environment variable |
| `EnvironmentFile` | `%h/.config/hermes/agent.env` | Load environment variables from file |
| `Volume` | `%h/.hermes:/opt/data:Z` | Bind mount or named volume |
| `Secret` | `hermes-key,type=env,target=ANTHROPIC_API_KEY` | Inject Podman secret as env var |
| `HealthCmd` | `curl -fsS http://localhost:8642/health ...` | Health check command |
| `HealthInterval` | `10s` | Run health check every N seconds |
| `HealthTimeout` | `5s` | Health check must complete within N seconds |
| `HealthRetries` | `5` | Mark unhealthy after N consecutive failures |
| `HealthStartPeriod` | `30s` | Delay before first health check |
| `AddHost` | `host.docker.internal:host-gateway` | Add extra host-to-IP mapping |
| `DropCapability` | `NET_RAW` | Remove capabilities (hardening) |
| `NoNewPrivileges` | `true` | Prevent privilege escalation |
| `User` | `1000` | Run as specific UID |
| `Group` | `1000` | Run as specific GID |

### `[Service]` Section

| Key | Example | Purpose |
|-----|---------|---------|
| `Type` | `forking` | Service type (default: `notify`) |
| `Restart` | `on-failure` | Restart policy: `always`, `on-failure`, `no` |
| `RestartSec` | `10s` | Wait N seconds before restarting |
| `TimeoutStartSec` | `120` | Max time to wait for container to start |

### `[Install]` Section

| Key | Example | Purpose |
|-----|---------|---------|
| `WantedBy` | `default.target` | Start this unit when the named target starts (auto-start at login) |

### `%` Specifiers (Path Expansion)

| Specifier | Expands To | Example |
|-----------|-----------|---------|
| `%h` | User's home directory | `/home/hermes` |
| `%u` | User name | `hermes` |
| `%U` | User UID | `1000` |
| `%t` | Runtime directory | `/run/user/1000` |

---

## Cross-References

- [[domains/deployment/hermes-agent-deployment.md]] -- Full deployment guide
- [[domains/architecture/hermes-agent-architecture.md]] -- Architecture overview
- [[domains/mcp/hermes-mcp-implementation.md]] -- MCP implementation
- [[domains/acp/hermes-acp-implementation.md]] -- ACP implementation
- [[domains/api/hermes-gateway-api.md]] -- Gateway API reference
- [[assets/agent-profiles/hermes-agent-profile.md]] -- Agent profile
- [[assets/mcp-servers/hermes-mcp-serve.md]] -- MCP bridge server
- [[assets/acp-agents/hermes-acp-agent.md]] -- ACP agent asset
- [[assets/api-clients/hermes-gateway-platforms.md]] -- Gateway platforms
- [[domains/deployment/hermzner-deployment.md]] -- Hermzner deployment guide
- [[assets/deployment/hermzner-terraform-ansible.md]] -- Hermzner infra-as-code
- [[assets/deployment/hermes-workspace-quadlet.md]] -- Hermes Workspace Quadlet
- [[hermes-workspace]] -- Workspace integration
