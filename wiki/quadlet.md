---
name: quadlet
description: "Quadlet — systemd-native container management for Podman"
source: sources/podman/
tags: [container, podman, systemd, deployment]
---

# Quadlet

**Quadlet** is a Podman 4.0+ feature that converts specially-named unit files into native systemd services. This gives rootless containers the same lifecycle management as traditional applications: `systemctl start/stop/restart`, `journalctl` logs, dependency ordering, health check integration, and automatic startup on boot or user login.

Quadlet files are declarative INI-style configuration files placed in standard systemd directories. The `podman-system-generator` scans these directories at boot and during `systemctl daemon-reload`, translating each file into transient systemd service units that Podman then executes.

## Description

Quadlet bridges the gap between container orchestration and traditional Linux service management. Instead of running containers manually or via a daemon like Docker Compose, Quadlet generates `.service` files that systemd manages directly. This approach provides:

- **No daemon requirement** — Podman runs containers on-demand via systemd generators
- **Native service lifecycle** — identical `systemctl` commands work for containers and system services
- **Rootless operation** — users can manage their own services via `systemctl --user` without `sudo`
- **Automatic dependency resolution** — containers can declare dependencies on other containers, volumes, and networks
- **Health check integration** — systemd health checks run from the host namespace, enabling monitoring even for distroless containers

Quadlet is particularly valuable for infrastructure-as-code deployments on single-node systems, replacing heavier orchestration tools like Docker Compose or Kubernetes for many use cases.

## Key Features

### Unit File Types

| Extension | Section | Purpose |
|-----------|---------|---------|
| `.container` | `[Container]` | Runs a container as a systemd service |
| `.pod` | `[Pod]` | Creates a Podman pod (shared network namespace) |
| `.volume` | `[Volume]` | Ensures a named volume exists |
| `.network` | `[Network]` | Creates a Podman network |
| `.image` | `[Image]` | Pre-pulls a container image |
| `.build` | `[Build]` | Builds an image from Containerfile |
| `.kube` | `[Kube]` | Deploys from Kubernetes YAML |
| `.artifact` | `[Artifact]` | Extracts OCI artifacts (ML models, configs) |

### Search Paths

Quadlet scans these directories in precedence order:

**Rootful (system-wide):**
- `/run/containers/systemd/` — temporary/test files
- `/etc/containers/systemd/` — administrator-defined
- `/usr/share/containers/systemd/` — distribution defaults

**Rootless (user):**
- `$XDG_RUNTIME_DIR/containers/systemd/`
- `~/.config/containers/systemd/` — user-defined (most common)
- `/etc/containers/systemd/users/${UID}/` — per-user system configuration
- `/etc/containers/systemd/users/` — all users

### Systemd Integration

Quadlet respects all standard systemd unit file sections:
- `[Unit]` — metadata and dependencies (`After=`, `Wants=`, `Requires=`, `BindsTo=`)
- `[Service]` — runtime behavior (`Restart=`, `TimeoutStartSec=`, `TimeoutStopSec=`)
- `[Install]` — auto-start (`WantedBy=default.target` for rootless, `multi-user.target` for rootful)

Template units (`foo@.container`) enable scalable service patterns where `%i` expands to the instance name.

### Resource Dependencies

Quadlet automatically creates systemd dependencies between related resources:
- Container `Volume=mydata.volume:/data` creates `Wants`/`After` on `mydata-volume.service`
- Container `Network=mynet.network` creates dependency on `mynet-network.service`
- Container `Pod=myapp.pod` links to the pod service

### Secret Management

Secrets integrate via:
- `Secret=` directive for Podman secrets
- `EnvironmentFile=` for key=value files
- Drop-in directories (`.container.d/10-secrets.conf`) for separating configuration from secrets

## In This Vault

- `domains/deployment/quadlet-patterns.md` — detailed deployment patterns including volume, network, pod, and secret management strategies
- [[cockpit-podman]] — Cockpit web UI for managing Quadlet services
- [[podman]] — Container engine that powers Quadlet
- [[podman-deployment]] — Full Podman deployment guide including Quadlet lifecycle and auto-updates

## Architecture

The `podman-system-generator` runs during `systemctl daemon-reload`, scanning Quadlet search paths. For each unit file found, it generates a corresponding `.service` file in the systemd generator output directory. When you run `systemctl start foo.service`, systemd executes the generated file, which contains Podman commands to create and run containers.

This generator-based approach means no separate process monitors containers — systemd itself becomes the orchestrator. Restart policies, failures, and health checks are all handled through systemd's established mechanisms.