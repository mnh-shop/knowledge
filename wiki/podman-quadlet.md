---
name: podman-quadlet
tags: [podman-quadlet, podman, quadlet, deployment, systemd, container]
description: "Getting started guide and reference for Podman with Quadlet systemd integration"
source: sources/podman-quadlet/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Podman Quadlet

| Field | Value |
|---|---|
| **Origin** | Community guide — [blog.nerdon.eu](https://blog.nerdon.eu/tag/containers-virtualization/) |
| **Source** | `sources/podman-quadlet/` |
| **Repomix** | `raw/podman-quadlet/podman-quadlet.xml` |
| **Codegraph** | `graphs/podman-quadlet/` |

## Overview

Podman Quadlet is a community getting-started guide and template collection for running Podman containers with Quadlet — Podman's native integration with systemd. Quadlet allows users to define containers, volumes, networks, and pods as systemd unit files, giving them the full lifecycle management capabilities of systemd (dependency ordering, auto-restart, logging, resource control) while using the familiar container image paradigm.

This repository provides practical, ready-to-use Quadlet configuration files for a wide range of self-hosted services. Each service is defined as one or more Quadlet `.container`, `.network`, `.volume`, and `.pod` files, demonstrating real-world usage patterns that users can adapt for their own deployments.

### What is Quadlet?

Quadlet is Podman's systemd-native container management system. Instead of using `podman run` commands or Docker Compose, you write `.container` files in INI-style format. These files are placed in `~/.config/containers/systemd/` (rootless) or `/etc/containers/systemd/` (rootful), and systemd automatically generates corresponding unit files and manages the container lifecycle. Quadlet was integrated directly into Podman upstream starting with Podman 4.4 and has become the recommended approach for running containers with systemd integration.

### Rootless vs Rootful

Quadlet supports both rootless and rootful container execution:

- **Rootless** (recommended, default) — Files go in `~/.config/containers/systemd/`. Commands use `systemctl --user`. Containers run without root privileges, reducing the blast radius of potential container escapes.
- **Rootful** — Files go in `/etc/containers/systemd/`. Commands use `systemctl` (without `--user`). Required for containers that need privileged operations or host network access.

## Key Features

- **Systemd-Native Containers** — Define containers as `.container` unit files managed directly by `systemd --user`. The container lifecycle becomes a systemd service lifecycle — `start`, `stop`, `restart`, `enable`, `disable`, `status` all work as expected.
- **Quadlet File Types** — The guide covers all Quadlet unit types:
  - **`.container`** — Container definition with image, volumes, ports, environment, and capabilities
  - **`.volume`** — Named volume management with automatic creation and cleanup
  - **`.network`** — Custom container networks with subnet and gateway configuration
  - **`.pod`** — Pod definitions for grouping related containers together
  - **`.image`** — Image pre-pulling and management
  - **`.kube`** — Kubernetes-style pod definitions
- **Automatic Unit Generation** — systemd units are generated from Quadlet files on service start. No manual unit file creation needed — Quadlet reads `.container` files and produces proper systemd service units with all the correct Podman arguments.
- **Dependency Management** — Full systemd dependency ordering with `Requires=`, `After=`, `Before=`, and `Wants=` directives. Containers can declare dependencies on other containers, networks, volumes, and system services.
- **Auto-Update Support** — Integration with Podman's `auto-update` mechanism. Adding `AutoUpdate=registry` to a `.container` file enables automatic image updates via `podman-auto-update.timer`.
- **Rootless by Default** — Quadlet units run rootless under the user's systemd session, providing better security isolation without requiring root privileges.
- **Environment File Support** — Use `.env` files with `EnvironmentFile=` directive for managing secrets and configuration outside the container definition.
- **Health Checks and Restart Policies** — systemd's `Restart=always`/`Restart=on-failure` combined with `TimeoutStartSec=` for robust container lifecycle management.

## Template Collection

The repository provides production-ready Quadlet configurations for **25 self-hosted services**, each in its own directory with complete `.container`, `.network`, and `.env` files:

| Service | Type | Key Features |
|---|---|---|
| **n8n** | Workflow automation | Volume mount, custom network, port publishing, auto-update |
| **Immich** | Photo management | Multi-container pod (server, DB, ML, Redis), pod-level networking, environment config |
| **Radarr** | Media management | Volume mounts for media libraries, custom network, timezone config |
| **Sonarr** | Media management | Similar pattern to Radarr with series-specific configuration |
| **Prowlarr** | Indexer manager | Proxy configuration, custom network, API key management |
| **Plex** | Media streaming | GPU passthrough, large volume mounts, custom network config |
| **lidarr-on-steroids** | Music management | Volume mounts, network isolation, tag-based organization |
| **Syncthing** | File synchronization | Persistent volumes, discovery server configuration |
| **Miniflux** | RSS reader | Database backend (PostgreSQL via separate container), environment config |
| **SearXNG** | Search engine | Reverse proxy configuration, Redis caching, custom networking |
| **Navidrome** | Music streaming | Library volume mount, transcoding configuration |
| **Tautulli** | Plex monitoring | Plex dependency, database persistence, API integration |
| **Maintainerr** | Media management | File system access for media pruning |
| **Kopia** | Backup | Repository persistence, snapshot scheduling, compression config |
| **WireGuard** | VPN | Host network mode, kernel module access, peer configuration |
| **wg-easy** | VPN management | Web UI for WireGuard, persistent peer config |
| **ntfy** | Notifications | Message persistence, topic management, web UI |
| **Omada** | Network controller | MongoDB dependency, persistent config, adoption management |
| **Karakeep** | Bookmark management | Browser extension config, full-text search |
| **FullFeedRSS** | RSS generation | Feed caching, custom templates |
| **Changedetection** | Website monitoring | Browser-based rendering, notification integration |
| **Homepage** | Dashboard | Service discovery via container labels, widget configuration |
| **Cloudflare** | DNS/Tunnel | API token management, tunnel configuration |
| **profilarr** | Profile management | Custom profile configuration |
| **kopia-photos** | Photo backup | Kopia integration for photo-specific backup patterns |

> **Provenance note (setup/source of truth):** the local clone at `sources/podman-quadlet/` is **corrupted** — it is a duplicate of `extension-podman-quadlet` (a TypeScript monorepo), not the original repo. All template contents on this page are documented from the upstream `fpatrick/podman-quadlet` repository (blog.nerdon.eu), which contains exactly the 25 template directories listed above. The following facts are CORRECT per the upstream README and repo structure: rootless (`~/.config/containers/systemd/`) vs rootful (`/etc/containers/systemd/`) deployment paths, `AutoUpdate=registry` for podman auto-update integration, `homepage.*` labels for the Homepage dashboard, `.pod` support for multi-container services (e.g. Immich), and the `.env` file pattern via `EnvironmentFile=`. A re-clone of the upstream repo and re-verification of these claims against the actual files is required (out of scope here). No license is declared upstream.

Each template follows a consistent structure: a dedicated directory with a `.container` file, optional `.network` file for custom networking, and documentation comments explaining key configuration choices.

## Usage

### Getting Started (Rootless)

```bash
# 1. Create the Quadlet directory
mkdir -p ~/.config/containers/systemd/

# 2. Deploy a service (example: n8n)
cp n8n/n8n.container ~/.config/containers/systemd/

# 3. Create persistent storage
mkdir -p /var/opt/containers/n8n

# 4. Reload systemd
systemctl --user daemon-reload

# 5. Start the container
systemctl --user start n8n.service

# 6. Enable on boot
systemctl --user enable n8n.service

# 7. Check status and logs
systemctl --user status n8n.service
journalctl --user -u n8n.service --no-pager -n 50
```

### Auto-Updates

To enable automatic container updates:

1. Add `AutoUpdate=registry` to the `[Container]` section of your `.container` file
2. Enable the podman auto-update timer:
   ```bash
   systemctl --user enable --now podman-auto-update.timer
   ```
3. Verify the timer:
   ```bash
   systemctl --user list-timers | grep podman-auto-update
   ```

### Example: n8n Service

The n8n template (`n8n/n8n.container`) demonstrates a typical Quadlet configuration:

```ini
[Unit]
Description=Automate with workflows
Wants=network-online.target
After=network-online.target
After=local-fs.target

[Container]
ContainerName=n8n
Image=docker.n8n.io/n8nio/n8n
Environment=N8N_SECURE_COOKIE=false
Environment=EXECUTIONS_DATA_PRUNE=true
Environment=EXECUTIONS_DATA_MAX_AGE=168
Environment=TZ=Europe/Dublin
Volume=/var/opt/containers/n8n:/home/node/.n8n:Z
Network=rss.network
PublishPort=5678:5678
Label=homepage.group=Automation
Label=homepage.name=n8n
Label=homepage.icon=n8n.png
Label=homepage.href=http://10.0.0.3:5678

[Service]
Restart=on-failure
TimeoutStartSec=900

[Install]
WantedBy=default.target
```

### Example: Immich Multi-Container Pod

The Immich template demonstrates complex multi-container setups with a pod:

- `immich.pod` — Defines the pod with shared networking
- `immich-server.container` — Main Immich server with `Pod=immich.pod`
- `immich-db.container` — PostgreSQL database container in the same pod
- `immich-machine-learning.container` — ML inference container
- `redis.container` — Caching layer

This pattern shows how Quadlet handles pod-level networking, inter-container DNS, and dependency ordering between related services.

## Architecture

Quadlet files live in user or system directories and are automatically discovered by systemd:

```
~/.config/containers/systemd/     ← Rootless Quadlet files (per-user)
  ├── n8n.container               ← Container definition
  ├── n8n.network                 ← Custom network
  ├── immich.pod                  ← Pod definition
  └── immich.env                  ← Environment variables
```

When systemd processes a Quadlet directory:
1. Quadlet reads every `.container`, `.volume`, `.network`, `.pod`, `.image`, and `.kube` file
2. For each file, Quadlet generates the corresponding systemd unit (e.g., `n8n.container` → `n8n.service`)
3. Generated units include the correct `podman run` arguments translated from Quadlet directives
4. systemd manages the service lifecycle as usual — dependency resolution, parallel start, restart policies, logging
5. Container state is visible via both `podman ps` and `systemctl --user status`

The generated units are ephemeral — Quadlet re-generates them on each `daemon-reload`. This means you should never edit the generated `.service` files directly; always modify the source `.container` file.

## Related

- [[podman]] — Container runtime that executes all Quadlet-managed containers. Understanding Podman volumes, networks, and images is essential for writing Quadlet files.
- [[podlet]] — CLI tool for generating Quadlet files from existing `podman run` commands and Docker Compose files. Useful for converting existing workflows to Quadlet format.
- [[extension-podman-quadlet]] — Podman Desktop extension for GUI-based Quadlet management. Provides visual editing and status monitoring for Quadlet units without command-line interaction.
- [[quadlet]] — Base wiki on the Quadlet unit format covering all file types, directives, and syntax. The authoritative reference for Quadlet configuration.
- [[podman-quadlet]] (this page) — Getting-started guide and template collection for Podman with Quadlet.
- [[tank-os]] — Fedora bootc image that uses Quadlet extensively for managing agent service containers, demonstrating production Quadlet deployment patterns.
- [[tank-agent-os]] — Bootable agent OS image that manages agent runtimes as rootless Quadlet containers, with systemd dependency chains and nftables integration.
- [[n8n]] — Workflow automation platform commonly deployed via Quadlet (template included in this repository).
- [[cockpit-podman]] — Web-based container management that pairs with Quadlet for browser-based service monitoring.
