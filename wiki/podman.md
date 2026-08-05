---
name: podman
tags: [cli, container, daemonless, docker, oci, podman, quadlet, rootless, security, storage, systemd, virtualization, wiki, golang]
description: "Podman — Container Management Tool"
source: sources/podman/
verification_date: 2026-07-12
verified_by: codegraph-verify
---
# Podman — Container Management Tool

| Field | Value |
|---|---|
| **Origin** | [containers/podman](https://github.com/containers/podman) |
| **License** | Apache 2.0 |
| **Stack** | Go (v6 line), libpod, netavark, passt |
| **Source** | `sources/podman/` |
| **Wanted** | Rootless container runtime — the backbone of all agent deployment stacks |

## What it is

Podman is a daemonless container engine for managing OCI containers and pods. Key differentiators: **rootless by default** (no daemon, no setuid binaries), Docker-compatible CLI, systemd integration via Quadlet, and pod support.

For the agent deployment stack, Podman is the **foundation layer** — everything runs inside rootless Podman containers managed by systemd Quadlet units.

## Rootless Architecture

Rootless Podman eliminates the need for a setuid binary. The architecture:

### User Namespace Mapping

When a non-root user runs `podman`, the Go runtime calls `BecomeRootInUserNS()` in `pkg/rootless/rootless_linux.go`. This:
1. Re-executes the podman binary inside a new user namespace
2. Maps the host user (UID `N`) to root (UID 0) inside the namespace
3. Maps `N+1` through `N+65536` as subordinate UIDs inside the namespace
4. Uses `/etc/subuid` and `/etc/subgid` for the subordinate ID range

Inside the namespace, the process has full root privileges — but only within its own user namespace. On the host, it runs as the unprivileged user with no special capabilities.

### Process Model

- **No daemon** — each `podman` command runs as a child process in the user namespace
- **`podman system service`** — optional REST API (used by docker-compose-compatible tools)
- **`conmon`** — container monitor process (handles I/O, exit codes)
- **`pause` process** — holds the user namespace open (required for cgroups v2)

### Requirements

- **Linux kernel 4.18+** (user namespaces, cgroups v2) — per upstream docs; not directly verifiable from in-repo code
- **cgroups v2** (verify with `podman info --format '{{.Host.CgroupsVersion}}'`) — per upstream docs
- **`/etc/subuid` and `/etc/subgid`** configured with subordinate ID ranges
- **`fuse-overlayfs`** or native `overlay` for storage (native overlay requires kernel 5.11+)
- **`pasta`** for rootless networking (slirp4netns support removed in v6)
- **`systemd --user`** sessions (for linger/Quadlet)

## Quadlet — Systemd Integration

Quadlet runs Podman containers as systemd services using `.container`, `.volume`, `.network`, `.pod`, `.kube`, `.image`, `.build`, and `.artifact` unit files (quadlet.go:1532-1546) placed in `~/.config/containers/systemd/`.

### Example: OpenClaw Quadlet

```ini
# ~/.config/containers/systemd/openclaw.container
[Unit]
Description=OpenClaw AI agent gateway
After=network-online.target
Wants=network-online.target

[Container]
Image=ghcr.io/openclaw/openclaw:latest
ContainerName=openclaw
Pull=newer
RunInit=true
UserNS=keep-id
User=%U
Volume=%h/.openclaw:/home/node/.openclaw:Z
PublishPort=127.0.0.1:18789:18789
HealthCmd=curl -f http://localhost:18789/health
HealthInterval=30s
HealthRetries=3
Notify=healthy

[Service]
Restart=on-failure
TimeoutStartSec=300

[Install]
WantedBy=default.target
```

Key Quadlet features:
- **`UserNS=keep-id`** — container runs with the host user's UID (required for file permissions on mounted volumes)
- **`Volume=...:Z`** — SELinux relabel (auto-fixes permission issues)
- **`Notify=healthy`** — healthcheck integration with systemd
- **`Secret=`** — Podman secret injection (as env var or file mount)
- **`Drop-in directories`** — `openclaw.container.d/` for secret-only configs (keeps secrets out of version control)

### Quadlet Lifecycle

```bash
systemctl --user daemon-reload    # Reload Quadlet files
systemctl --user enable openclaw  # Enable on boot
systemctl --user start openclaw   # Start immediately
systemctl --user status openclaw  # Check status
journalctl --user -u openclaw -f  # Tail logs
```

### Podman Secrets

Secrets are stored as encrypted files in `~/.local/share/containers/storage/secrets/`:

```bash
# Create
printf '%s' "$ANTHROPIC_API_KEY" | podman secret create anthropic_api_key -

# Use in Quadlet (drop-in file to keep secrets out of the main unit)
cat > ~/.config/containers/systemd/openclaw.container.d/10-secrets.conf << 'EOF'
[Container]
Secret=anthropic_api_key,type=env,target=ANTHROPIC_API_KEY
Secret=openai_api_key,type=mount,target=/run/secrets/openai_api_key,uid=1000,mode=0400
EOF
```

Available as `type=env` (environment variable) or `type=mount` (file mount).

### Podman Machine (macOS)

Podman Machine creates a Linux VM on macOS via **vfkit** (Apple Virtualization.framework):

```bash
podman machine init --cpus 4 --memory 8192
podman machine start
eval $(podman machine env)  # Sets DOCKER_HOST-compatible env vars
```

- **Architecture:** `aarch64` (Apple Silicon) or `x86_64` (Intel)
- **Rootless by default** inside the VM
- **Rootful mode** available: `podman machine set --rootful` (needed for bootc-image-builder)
- **Networking:** gvproxy for port forwarding between host and VM
- **File sharing:** virtiofs mounts for sharing host directories

### Networking (Rootless)

| Mode | Default? | Description |
|---|---|---|
| **pasta** | ✅ (default since Podman 5.0) | User-mode networking, no `tap` device needed; `pasta.Setup()` in `libpod/networking_pasta_linux.go` / vendored `go.podman.io/common/libnetwork/pasta/`; copies the host IP, supports port forwarding |
| **slirp4netns** | ❌ removed in v6 | Support removed — containers still configured with it fail with "slirp4netns support has been removed, run `podman system migrate`" (`libpod/networking_linux.go:33-34`) |
| **bridge** | ✅ (rootless via netavark + rootlessport) | Rootless bridge networks use the `rootlessport` userspace proxy for port forwarding (netavark handles bridging) |

For Quadlet port publishing in rootless mode:
```ini
PublishPort=127.0.0.1:18789:18789  # Bind loopback (any address works; see below)
```
Rootless port publishing is handled by the `rootlessport` proxy in the host network namespace, so binding to `0.0.0.0` (e.g. `-p 0.0.0.0:x:y` / `PublishPort=0.0.0.0:18789:18789`) works without root. The real rootless restriction is that containers cannot bind ports **below 1024** (no `CAP_NET_BIND_SERVICE`; `rootless.md:5-7`, adjustable via `net.ipv4.ip_unprivileged_port_start`).

### Security Model

- **Rootless:** Container runs with the user's UID, not root
- **Capabilities:** Minimal default set (no `CAP_SYS_ADMIN`, no `CAP_NET_ADMIN`)
- **Seccomp:** Default seccomp profile blocks ~50 syscalls
- **Read-only rootfs:** Quadlet supports `--read-only` flag
- **No-new-privileges:** Always enabled
- **User namespace isolation:** Root in container ≠ root on host
- **Podman Secrets:** Encrypted storage, not accessible to other users

### Limitations of Rootless

| Limitation | Impact |
|---|---|
| Ports < 1024 cannot be bound | Kernel blocks `CAP_NET_BIND_SERVICE`-less processes; raise `net.ipv4.ip_unprivileged_port_start` or use a proxy/redir (rootless.md) |
| `--network=host` merges with the host namespace | Supported rootless since modern Podman (podman-run.1.md.in:957) — use with care |
| No `--privileged` capability additions | Some containers expecting full root access fail |
| cgroups v2 mandatory | Kernel must support cgroups v2 |
| Limited `--device` passthrough | Most device passthrough requires root |
| Storage driver may not support native overlay | Older kernels fall back to fuse-overlayfs (slower) |
| No macvlan/ipvlan | Complex networking setups require root |

## Deployment Role

Podman is the **foundation runtime** for the entire agent deployment stack:

- **macOS dev:** Podman Machine → Linux VM → rootless Podman → agent containers
- **Linux dev:** Direct → rootless Podman → agent containers
- **VPS (no nested virt):** Direct → rootless Podman → agent containers (the VPS is already a VM boundary)
- **Bare metal with nested virt:** Direct → rootless Podman via crun-vm for extra isolation

## Related

- [[crun-vm]] — OCI runtime integration for running VMs as containers
- [[tank-os]] — Fedora bootc image running OpenClaw via rootless Podman Quadlets
- [[hermzner]] — Hermes on Hetzner with rootless Podman Quadlets
- [[buildah]] — OCI image builder (Podman delegates `podman build` to it)
- [[podlet]] — Quadlet file generator (convert `podman run` → .container units)
- [[nix-podman-stacks]] — Nix-native Quadlet management

## Related

- [[podman-architecture]] — 3-layer architecture, rootless re-exec mechanism, container lifecycle flow
- [[podman-deployment]] — Quadlet, secrets, auto-updates, Podman Machine, troubleshooting
- [[podman-quadlet-examples]] — .container/.volume/.network/.pod/.kube/.build/.image patterns
- [[hermes-profiles]] — Skills, integration knowledge, SSH tunnel patterns
- [[podman.codegraph-verify]] — Codegraph verification of architecture claims

## Cross-project

- [[hermes-agent]] — Agent platform running inside Podman containers
- [[openclaw]] — Agent platform running inside Podman containers
- [[agentfield]] — Control plane deployed via rootless Podman
- [[mission-control]] — Dashboard deployed in Podman containers
- [[n8n]] — Workflow automation running in Podman containers
- [[sablier]] — Scale-to-zero daemon for Podman containers
- [[gogs]] — Self-hosted Git service deployable via Podman
- [[goclaw]] — Go-based agent gateway deployable via Podman
