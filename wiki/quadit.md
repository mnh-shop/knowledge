---
name: quadit
tags: [quadit, quadlet, cli, deployment, container, systemd]
description: "CLI toolkit for managing Podman Quadlet units"
source: sources/quadit/
---

# Quadit

| Field | Value |
|---|---|
| **Origin** | [ubiquitous-factory/quadit](https://github.com/ubiquitous-factory/quadit) |
| **Source** | `sources/quadit/` |
| **Repomix** | `raw/quadit/quadit.xml` |
| **Codegraph** | `graphs/quadit/` |

## Overview

Quadit is a GitOps-focused toolkit for managing Podman Quadlet units on Linux, written in Rust. It focuses on managing Quadlet files and running containers in rootless mode using a pure pull model — no inbound access to the device is required. This makes it particularly well-suited for **remote edge** scenarios where devices are behind NAT, firewalls, or otherwise inaccessible from the management plane.

The core workflow is opinionated: Quadit watches a YAML configuration file (local or fetched from a URL) that describes target repositories and schedules. On each schedule tick, it clones/pulls the Git repository, determines whether any Quadlet files have changed, deploys updated files to `~/.config/containers/systemd/`, runs `systemctl --user daemon-reload`, and restarts affected services. This creates a fully automated GitOps loop for container lifecycle management on edge devices.

Quadit is an opinionated reimplementation of [fetchit](https://github.com/containers/fetchit), adding support for user-scoped Quadlets (not available in fetchit), systemd stop/start operations, and native support for `.container`, `.volume`, `.network`, `.pod`, and `.kube` file types. Its minimal Rust footprint makes it suitable for low-resource edge devices. The project is sponsored by [Mehal Technologies](https://mehal.tech).

## Key Features

- **GitOps Deployment Model** — Pure pull-based architecture: devices check Git repositories on cron-like schedules and apply changes without any inbound connectivity
- **User Quadlet Support** — Supports rootless user-level Quadlet files (unlike fetchit), deploying to `~/.config/containers/systemd/` with `systemctl --user` lifecycle management
- **Cron-Scheduled Sync** — Each target in the config has its own cron expression (`schedule`) defining how often to check the repository for changes
- **Multi-Target Config** — Single `config.yaml` can define multiple Git repositories, each with multiple target paths and independent schedules
- **Boot URL Bootstrap** — Remote `config.yaml` URL via `BOOT_URL` environment variable for zero-touch provisioning; device pulls its configuration from a remote source on first run
- **Config Reload** — `configReload` section enables live config reload from a URL at a configurable interval, automatically restarting sync jobs when the config changes
- **Delta Deployment** — Only deploys Quadlet files that differ from the currently deployed versions (byte-level comparison), avoiding unnecessary systemd restarts
- **Systemd Commands** — Supports explicit `systemd_commands` in config for stopping/restarting specific services outside of the file-change detection loop
- **Containerized Deployment** — Ships as a container image (`ghcr.io/ubiquitous-factory/quadit`) with a provided `.container` Quadlet file for self-hosted deployment via Quadlet itself
- **Supported File Types** — All standard Quadlet types: `.container`, `.volume`, `.network`, `.pod`, `.kube`
- **Environment Configurable** — 10 environment variables for configuring paths, log levels, and behavior without modifying the config file
- **Low Resource Footprint** — Written in Rust to minimize binary size, memory usage, and power consumption for always-on edge devices
- **Directory-Level Processing** — When a `targetPath` points to a directory instead of a file, Quadit iterates through all top-level Quadlet files in that directory

## Architecture

Quadit is structured as a set of coordinated Rust modules:

```
src/
├── main.rs              — Entry point: environment init, log setup, service launch
├── lib.rs               — Module declarations
├── service_manager.rs   — Core orchestration loop: boot, config load, git loop
├── git_manager.rs       — Git sync per cron schedule: clone/pull, diff detection
├── file_manager.rs      — File operations: deploy, compare, validate file types
├── config_quadit.rs     — config.yaml deserialization (serde + YAML)
├── config_git.rs        — Per-target Git config structure
├── config_reload.rs     — Live config reload configuration
├── config_commands.rs   — Systemd command configuration
```

### Service Lifecycle

1. **Boot** — On startup, checks `BOOT_URL` env var. If set, fetches the remote `config.yaml` and writes it locally before proceeding.
2. **Config Load** — Reads `~/.quadit/config.yaml` (or `/opt/config/config.yaml` in container mode) and deserializes into `ConfigQuadit` structure containing target configs, reload config, and systemd commands.
3. **Job Scheduling** — For each `targetConfigs` entry, a `GitManager` job is created with the specified cron schedule. Each job clones its repo into a UUID-named directory under `jobs/`.
4. **Sync Loop** — On each schedule tick, the job runs `quaditsync::GitSync::sync()` to fetch the latest commits. If new commits exist, it processes the target path.
5. **File Comparison** — `FileManager::is_unit_file_deployed()` performs a byte-level comparison between the repo file and the deployed file in `~/.config/containers/systemd/`.
6. **Deployment** — If files differ, `FileManager::deploy_unit_file()` copies the file, `ServiceManager::daemon_reload()` triggers systemd reload, and `ServiceManager::restart()` restarts the service.
7. **Config Reload** — If `configReload` is configured, a background loop periodically fetches the remote `config.yaml`, compares it with the local copy, and restarts all sync jobs if changes are detected.

### Container vs. Local Mode

Quadit runs in two modes determined by the `LOCAL` environment variable:

| Aspect | Container Mode (`LOCAL=no`) | Local Mode (`LOCAL=yes`) |
|---|---|---|
| Config path | `/opt/config/config.yaml` | `~/.quadit/config.yaml` |
| Deploy path | `/opt/containers/` | `~/.config/containers/systemd/` |
| Runtime path | `/opt/` via container volume | User home directory |
| Socket access | Mounted `podman.sock` | Direct host access |

## Usage

### Quick Install (Edge Device)

```bash
# SELinux context for container cgroup management
sudo setsebool -P container_manage_cgroup true

# Create config directory
mkdir ~/.quadit

# Fetch sample config
curl -o ~/.quadit/config.yaml \
  https://raw.githubusercontent.com/ubiquitous-factory/quadit/main/samples/config.yaml

# Create Quadlet directory and deploy quadit as a Quadlet service
mkdir -p ~/.config/containers/systemd
curl -o ~/.config/containers/systemd/quadit.container \
  https://raw.githubusercontent.com/ubiquitous-factory/quadit/main/deploy/quadit.container

# Enable user lingering and start the service
loginctl enable-linger $USER
systemctl --user daemon-reload
systemctl --user start quadit
```

### Sample config.yaml

```yaml
configReload:
  configURL: "https://raw.githubusercontent.com/ubiquitous-factory/ai-remote-edge/main/deploy/config.yaml"
  interval: 1000
targetConfigs:
  - url: "https://github.com/ubiquitous-factory/quadit"
    targetPath: "samples/helloworld"
    branch: "main"
    schedule: "*/1 * * * *"
```

### Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `BOOT_URL` | (empty) | Remote URL for initial config.yaml bootstrap |
| `LOCAL` | `no` | Run in local user mode vs container mode |
| `LOG_LEVEL` | `info` | Log verbosity: error, warn, info, debug, trace |
| `JOB_PATH` | `/tmp` (container) | Root path for job working directories |
| `JOB_FOLDER` | `jobs` | Subfolder name for job checkouts |
| `PODMAN_UNIT_PATH` | `$HOME/.config/containers/systemd` | Target directory for deployed Quadlet files |
| `SYSTEMCTL_PATH` | `/usr/bin/systemctl` | Path to systemctl binary |

## Related

- [[podlet]] — Quadlet file generator CLI (complementary tool)
- [[podman-quadlet]] — Official Quadlet getting started and reference
- [[podman]] — Container runtime for Quadlet units
- [[extension-podman-quadlet]] — Desktop GUI for Quadlet management
- [[quadlet-lsp]] — Language server for editing Quadlet files
