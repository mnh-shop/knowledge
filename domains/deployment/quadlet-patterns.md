---
name: quadlet-patterns
description: General Quadlet deployment patterns for rootless Podman -- systemd-native container lifecycle
tags: [podman, quadlet, systemd, patterns]
---

# Quadlet Deployment Patterns

## What is Quadlet?

Quadlet is a Podman 4.0+ feature (now stable in Podman 5+) that converts specially-named files (`.container`, `.volume`, `.network`, `.secret`, `.pod`, `.kube`, `.build`, `.image`, `.artifact`) into systemd unit files. This gives rootless containers the same service lifecycle management as native applications: `systemctl --user start/stop/restart/enable`, `journalctl --user -u`, dependency ordering, health check integration, and auto-start on login.

The `podman-system-generator` runs at every `systemctl --user daemon-reload`, scanning the Quadlet search paths and translating each file into one or more transient systemd services. No Docker Compose daemon or separate process supervisor is needed.

For a deep-dive on the Podman architecture underneath Quadlet, see [[podman-architecture]].

---

## Search Paths

| Scope | Search Path | Target |
|-------|-------------|--------|
| Rootless (user) | `~/.config/containers/systemd/` | `systemctl --user` |
| Rootless (system-configured) | `/etc/containers/systemd/users/<UID>/` | User units for a specific UID |
| Rootful (system) | `/etc/containers/systemd/` | `systemctl` (system-wide) |

Files placed in subdirectories (e.g. `~/.config/containers/systemd/openclaw/`) are also picked up if you symlink or use `systemctl --user link`.

---

## Rootless vs Rootful

### Rootless (default, recommended)

- No daemon, no `sudo` needed.
- Runs under `systemctl --user`; starts at user login.
- Requires `sudo loginctl enable-linger $USER` to survive logout.
- Ports below 1024 require lowering `ip_unprivileged_port_start` or using a reverse proxy.
- Volumes use `pasta` or `slirp4netns` for networking.
- All quadlet files in this knowledge base are rootless unless noted.

### Rootful (system services)

- Runs under `systemctl` system-wide.
- Requires `sudo` to place files in `/etc/containers/systemd/`.
- Can bind ports below 1024 directly.
- Uses `WantedBy=multi-user.target` in `[Install]`.

**Recommendation:** Prefer rootless for all services. Use rootful only when binding privileged ports (<1024) or when system-level isolation is mandated.

See [[podman-deployment]] for the full rootless setup procedure.

---

## Volume Patterns

Quadlet supports several volume patterns for persistent data.

### Pattern 1: Bind Mount (direct path)

```ini
Volume=%h/.openclaw:/home/node/.openclaw:Z
```

- `%h` expands to the user's home directory.
- `:Z` relabels for SELinux (remove on non-SELinux systems like macOS).
- Data is directly on the host filesystem for easy backup and inspection.
- Preferred for data that needs to be shared with other tools or backed up via standard tooling.

### Pattern 2: Named Quadlet Volume

```ini
# ~/.config/containers/systemd/myapp.volume
[Volume]
Label=myapp
```

Reference in the `.container` file:

```ini
Volume=myapp.volume:/var/lib/myapp:Z
```

Quadlet automatically creates the named volume and adds a `Wants`/`After` dependency on `myapp-volume.service`. Volumes are stored under `~/.local/share/containers/storage/volumes/` by default.

### Pattern 3: Volume from Image Seed

```ini
[Volume]
VolumeName=seeded-config
Driver=image
Image=docker.io/myorg/config-image:latest
```

Useful when a base configuration is distributed as an OCI image.

### Pattern 4: tmpfs (in-memory)

```ini
[Volume]
VolumeName=tmp-cache
Device=tmpfs
Type=tmpfs
Options=size=100M
```

### Pattern 5: Inline Tmpfs in Container

For writable directories in read-only containers:

```ini
Tmpfs=/tmp:size=64M
Tmpfs=/app/.next/cache:size=128M
```

### SELinux Flags

- `:z` -- shared across multiple containers.
- `:Z` -- private to this container (relabels host dir).
- `:U` -- recursively chown volume contents to container UID.

**See concrete examples:**
- [[assets/deployment/podman-quadlet-examples.md]] -- The `.volume` reference section documents six volume variants (named, explicit label, uid/gid, image-seeded, tmpfs, bind-mount).
- [[assets/deployment/agentfield-quadlet.md]] -- Uses `.volume` units for PostgreSQL and control-plane data.
- [[assets/deployment/hermes-agent-quadlet.md]] -- Both bind mounts and named volumes with trade-off analysis.

---

## Network Patterns

### Pattern 1: Host Networking

```ini
Network=host
```

- Direct port access, no port mapping overhead.
- Simpler SSE/push streaming (no proxy buffering issues).
- No network isolation between containers; port conflicts possible.
- Cannot use `PublishPort=` alongside `Network=host`.

Used by [[assets/deployment/hermes-agent-quadlet.md]] and [[assets/deployment/hermes-workspace-quadlet.md]] for SSE stability.

### Pattern 2: Bridge Network (Quadlet `.network`)

```ini
# ~/.config/containers/systemd/mynet.network
[Network]
NetworkName=mynet
Driver=bridge
Subnet=10.89.0.0/24
Gateway=10.89.0.1
```

Reference in containers:

```ini
Network=mynet.network
```

- Containers resolve each other by container name via aardvark-dns.
- Requires `PublishPort=` for external access.
- Container must bind to `0.0.0.0` inside (not `127.0.0.1`) for bridge networking.
- Use `NetworkAlias=my-alias` for additional DNS names.

### Pattern 3: Internal-Only Network

```ini
[Network]
NetworkName=internal
Internal=true
```

No external access. All traffic stays within the bridge. Used by [[assets/deployment/mission-control-quadlet.md]] for the hardened profile overlay.

### Pattern 4: Container Network Sharing

```ini
Network=container:openclaw-gateway
```

Shares the network namespace of an existing container. Used by [[assets/deployment/openclaw-quadlet.md]] for the CLI sidecar.

### Pattern 5: Slirp4netns vs Pasta

Rootless Podman networking changed between Podman 4 and 5:

| Feature | Slirp4netns (Podman 4 default) | Pasta (Podman 5 default) |
|---------|-------------------------------|--------------------------|
| Performance | Slower (user-space NAT) | Faster (tap-based) |
| Port forwarding | `-p` works | `-p` works |
| ICMP/ping | Not supported | Supported |
| Performance impact | ~50% throughput loss | Near-native throughput |
| Command override | `--network slirp4netns` | `--network pasta` |

Quadlet uses whatever Podman's default network backend is. No Quadlet-specific key exposes this -- configure via `containers.conf` or Podman's default.

### Network on macOS

On macOS (via Podman Machine), all networking passes through the Linux VM. Port forwarding works identically to Linux, but the VM-level `gv-proxy` handles the host-VM bridge. The `.network` Quadlet files create networks inside the VM.

**See full network examples:**
- [[assets/deployment/podman-quadlet-examples.md]] -- `.network` reference with IPv6, dual-stack, and internal network variants.
- [[assets/deployment/agentfield-quadlet.md]] -- Multi-service bridge network (`agentfield.network`).
- [[assets/deployment/sablier-quadlet.md]] -- Shared network pattern for scale-to-zero.

---

## Pod Patterns

A `.pod` Quadlet creates a Podman pod -- a group of containers sharing the same network namespace (they can reach each other on `localhost`).

```ini
# ~/.config/containers/systemd/myapp.pod
[Pod]
PodName=myapp
PublishPort=127.0.0.1:3000:3000
PublishPort=127.0.0.1:8642:8642
Network=stack.network
```

Containers join the pod:

```ini
[Container]
Pod=myapp.pod
# No PublishPort needed -- handled by pod
```

### Pod vs Bridge Network

| Aspect | Pod | Bridge Network |
|--------|-----|---------------|
| Inter-container communication | `localhost` | DNS by container name |
| Port isolation | Pod-level `PublishPort` | Per-container `PublishPort` |
| Network isolation | Containers see all localhost ports | Only published ports |
| Use case | Tightly coupled services | Loosely coupled microservices |

**Pod examples:**
- [[assets/deployment/openclaw-quadlet.md]] -- Pod with gateway + CLI + optional services.
- [[assets/deployment/hermes-agent-quadlet.md]] -- Pod mode for agent + PostgreSQL.
- [[assets/deployment/hermes-workspace-quadlet.md]] -- Pod approach for workspace + agent.
- [[assets/deployment/podman-quadlet-examples.md]] -- Pod pattern with `ExitPolicy=continue` and `UserNS=keep-id`.

---

## Secrets and Environment Management

### Pattern 1: Podman Secrets (recommended)

```bash
echo "sk-ant-..." | podman secret create my-api-key -
```

Reference in Quadlet (preferably in a **drop-in file**):

```ini
Secret=my-api-key,type=env,target=API_KEY
```

Options:
- `type=env` -- inject as environment variable.
- `type=mount` -- mount as file at `/run/secrets/<name>` (or custom `target=` path).
- `mode=`, `uid=`, `gid=` -- for `type=mount` only.

Podman secrets are NOT committed to images, NOT exported, and scoped to the container at creation time. They support `--replace` for rotation.

### Pattern 2: EnvironmentFile

```ini
EnvironmentFile=%h/.config/myapp/app.env
```

- Simple, single flat key=value file.
- Must be mode 0600 (`chmod 600`).
- Easy to backup but all secrets in one file.
- Path expansion via `%h`, `%u`, `%U` specifiers.

### Pattern 3: Drop-In Configuration Files

Quadlet supports systemd-style drop-in directories with `.d/` suffix:

```
~/.config/containers/systemd/myapp.container.d/
  10-secrets.conf      # Secret references
  20-networking.conf   # Override network settings
  30-debug.conf        # Debug logging overrides
```

Drop-ins are merged in lexicographic order. They are the **recommended** way to inject secrets because the base `.container` file can be committed to version control while drop-in files stay local.

### Pattern 4: Inline Environment (avoid for secrets)

```ini
Environment=LOG_LEVEL=info
Environment=TZ=UTC
```

Use for non-sensitive configuration only. Visible in `systemctl --user cat`.

**Secret management examples:**
- [[assets/deployment/openclaw-quadlet.md]] -- `.secret` Quadlet file + `Secret=` injection.
- [[assets/deployment/agentfield-quadlet.md]] -- Three secret patterns (EnvironmentFile, Podman secrets, systemd credentials).
- [[assets/deployment/hermes-agent-quadlet.md]] -- EnvironmentFile for API keys with `chmod 600`.
- [[assets/deployment/tank-os-quadlet.md]] -- Secret drop-in files generated by `sync-podman-secrets` bootstrap.
- [[assets/deployment/podman-quadlet-examples.md]] -- Secret drop-ins for every service in the stack.

---

## Systemd Integration

### Section Reference

**`[Unit]`** -- metadata and dependencies:

| Key | Purpose |
|-----|---------|
| `Description` | Human-readable name in `systemctl status` |
| `After=` | Start after these units (soft ordering) |
| `Wants=` | Soft dependency (unit starts even if dep fails) |
| `Requires=` | Hard dependency (unit stops if dep fails) |
| `BindsTo=` | Harder dependency (unit stops if bound unit stops) |
| `PartOf=` | Stop/restart with parent unit |

**`[Service]`** -- runtime behavior:

| Key | Purpose |
|-----|---------|
| `Restart` | `always`, `on-failure`, `no` |
| `RestartSec` | Delay between restarts |
| `TimeoutStartSec` | Max time to wait for container start (image pull) |
| `TimeoutStopSec` | Max time to wait for container stop |

**`[Install]`** -- activation:

| Key | Purpose |
|-----|---------|
| `WantedBy=default.target` | Auto-start at user login (rootless) |
| `WantedBy=multi-user.target` | Auto-start at system boot (rootful) |

### Restart Policies

| Policy | Behavior |
|--------|----------|
| `Restart=always` | Restart regardless of exit code |
| `Restart=on-failure` | Restart only on non-zero exit (preferred for most services) |
| `Restart=no` | Never restart (use for oneshot/ephemeral containers) |

### Dependency Patterns

**Hard dependency** (service A requires service B):

```ini
[Unit]
Requires=postgres.service
After=postgres.service
```

**Soft dependency** (service A wants service B but starts anyway):

```ini
[Unit]
Wants=network-online.target
After=network-online.target
```

**Binding dependency** (service A stops if bound unit stops -- used for Sablier + proxy):

```ini
[Unit]
BindsTo=sablier.service
```

### Health Check Integration

Quadlet health checks run from the **host namespace** (not inside the container), so `curl` and other tools are available even in distroless images.

```ini
[Container]
HealthCmd=curl -sf http://localhost:8080/health || exit 1
HealthInterval=30s
HealthTimeout=10s
HealthRetries=3
HealthStartPeriod=30s
HealthOnFailure=kill
Notify=healthy
```

`Notify=healthy` postpones systemd's `READY=1` until the container health check passes. This means `After=` and `Requires=` dependencies on this service also wait for health.

Self-healing pattern:

```ini
[Container]
HealthOnFailure=kill

[Service]
Restart=on-failure
```

When the container becomes unhealthy, Podman kills it. Systemd restarts it automatically.

### Template Units (Scalable Services)

Quadlet supports systemd template units via `@` in the filename:

```ini
# worker@.container
[Container]
Image=docker.io/myapp/worker:latest
ContainerName=worker-%i
PublishPort=127.0.0.1:%i:%i
Environment=WORKER_ID=%i
```

Start instances:

```bash
systemctl --user start worker@8080.service
systemctl --user start worker@8081.service
```

### `%` Specifiers (Path Expansion)

| Specifier | Expands To |
|-----------|-----------|
| `%h` | User's home directory |
| `%u` | User name |
| `%U` | User UID |
| `%G` | User GID |
| `%t` | Runtime directory (`/run/user/<UID>`) |
| `%i` | Template instance name |

### Systemd Integration Examples

- [[assets/deployment/sablier-quadlet.md]] -- Comprehensive example of `BindsTo`, `After`, and startup ordering with Sablier scale-to-zero.
- [[assets/deployment/podman-quadlet-examples.md]] -- Multi-service orchestration with shared network, pod, and volume dependency patterns.

---

## Migration from Docker Compose

| Docker Compose | Quadlet Equivalent |
|---------------|-------------------|
| `image:` | `Image=` |
| `container_name:` | `ContainerName=` |
| `ports:` | `PublishPort=` or `Network=host` |
| `environment:` | `Environment=` or `EnvironmentFile=` |
| `volumes:` | `Volume=` (bind mount or named) |
| `env_file:` | `EnvironmentFile=` |
| `command:` | `Exec=` |
| `healthcheck:` | `HealthCmd=`, `HealthInterval=`, etc. |
| `restart: unless-stopped` | `[Service] Restart=always` |
| `depends_on:` | `Requires=` / `After=` in `[Unit]` |
| `networks:` | `Network=` or `Pod=` |
| `secrets:` | `Secret=` in drop-in |

**Podlet** (`podlet`) can automate this conversion:
```bash
podlet compose docker-compose.yml
podlet podman run ...           # Convert a `podman run` command
podlet generate container ...   # Generate from a running container
```

See [[assets/deployment/podlet-quadlet-examples.md]] for conversion walkthroughs.

---

## Additional Quadlet Unit Types

### `.kube` -- Kubernetes-style deployment

Runs `podman kube play` from a Kubernetes YAML file. Supports Pod and Service specs.

See [[assets/deployment/podman-quadlet-examples.md]] for `.kube` examples.

### `.build` -- Build-then-run

Builds a Containerfile before the container starts. The `.build` service is `Type=oneshot`.

### `.image` -- Pre-pull image

Pulls an image during system activation. Ensures large images are downloaded before the container attempts to start.

### `.artifact` -- OCI artifact extraction

Downloads non-container OCI artifacts (ML models, config files) and extracts them on the filesystem.

---

## All Quadlet Asset Files

The following quadlet-specific asset files exist in this knowledge base:

| File | Service | Key Patterns |
|------|---------|-------------|
| [[assets/deployment/openclaw-quadlet.md]] | OpenClaw gateway | Pod, secrets, volume, multi-service orchestration, migration guide |
| [[assets/deployment/agentfield-quadlet.md]] | AgentField platform | Bridge network, PostgreSQL sidecar, `EnvironmentFile`, three secret patterns |
| [[assets/deployment/hermes-agent-quadlet.md]] | Hermes Agent | Host vs bridge networking, drop-ins, health checks, `%` specifiers |
| [[assets/deployment/hermes-workspace-quadlet.md]] | Hermes Workspace | Multi-container stack, pod vs host networking, shared volume |
| [[assets/deployment/mission-control-quadlet.md]] | Mission Control | Hardened profile, `DropCapability=all`, internal-only network |
| [[assets/deployment/sablier-quadlet.md]] | Sablier (scale-to-zero) | `BindsTo` dependency, shared network, Sablier labels, startup ordering |
| [[assets/deployment/tank-os-quadlet.md]] | Tank OS bootc image | System-level Quadlet (`/etc/containers/systemd/users/`), `ExecStartPre`, secret drop-in bootstrap |
| [[assets/deployment/podman-quadlet-examples.md]] | Multiple services | Shared network stack, all Quadlet types (`.volume`, `.network`, `.kube`, `.build`, `.image`, `.artifact`), template units |
| [[assets/deployment/podlet-quadlet-examples.md]] | Podlet conversion | Converting `podman run`, Docker Compose, and running containers |

---

## Related Documentation

- [[podman-deployment]] -- Full Podman deployment guide including Quadlet lifecycle, secret lifecycle, health checks, and auto-updates.
- [[podman-architecture]] -- Deep-dive into Podman's daemonless architecture.
- [[domains/architecture/deployment-architecture.md]] -- High-level deployment architecture across all stacks.
- [[domains/deployment/buildah-deployment.md]] -- Buildah image build patterns for feeding Quadlet deployments.
