---
title: "quadit — CodeGraph Verification"
tags: [quadit, codegraph-verify, quadlet, cli]
related: [[quadit]], [[podlet]], [[podman-quadlet]], [[quadlet]]
verification_date: 2026-07-12
verified_by: CodeGraph & manual source audit
source_ref: sources/quadit/
graph_ref: graphs/quadit/
---

# quadit — CodeGraph Verification

## Claim-1: Rust-based GitOps agent for rootless Podman quadlets

Quadit is a Rust binary that manages Podman quadlets via a pure-pull GitOps model. It runs as a systemd user service on edge devices, cloning quadlet `.container`, `.volume`, `.pod`, `.network`, and `.kube` files from git repos and deploying them to `~/.config/containers/systemd/`.

**Source evidence:** `Cargo.toml` declares the binary `quadit` with dependencies on `tokio-cron-scheduler`, `serde_yaml`, `reqwest`, `users`. `README.md` states "focused on managing quadlets and running containers in rootless mode using a gitops model" and shows deployment to `~/.config/containers/systemd/`. `main.rs` calls `ServiceManager::configured()` then `svc.run()`. `src/file_manager.rs:18` defines `SUPPORTED_FILES` as `["container", "volume", "pod", "network", "kube"]`.

## Claim-2: YAML-driven configuration with cron-scheduled git sync

The service reads a `config.yaml` with `targetConfigs` (each containing a git URL, target path, branch, and cron schedule). A `GitManager` schedules each config entry as a cron job using `tokio-cron-scheduler`, syncing the remote quadlet files to the local system at configured intervals.

**Source evidence:** `src/config_quadit.rs:9-13` defines `ConfigQuadit` struct with `target_configs: Vec<ConfigGit>`. `src/config_git.rs` contains the `ConfigGit` struct with `url`, `targetPath`, `branch`, `schedule` fields. `src/git_manager.rs` creates a `JobScheduler` and adds each target as a cron `Job`. `src/service_manager.rs:55-73` runs the main loop checking for config reloads.

## Claim-3: Config reload via remote polling with hot-swap

Quadit supports a `configReload` URL that is polled at a configurable interval (milliseconds). When the remote config differs from the local one, it is swapped atomically (with `.bak` backup), the git manager is stopped, and a new one is initialized from the updated config — enabling live reconfiguration without service restart.

**Source evidence:** `src/config_reload.rs:7-11` defines `ConfigReload` with `config_u_r_l: String` and `interval: u64`. `src/file_manager.rs:34-70` (`from_url`) fetches the config from URL, compares with existing via `are_identical()`, and copies if different with `.bak` rotation. `src/service_manager.rs:62-72` checks for changes and hot-reloads the `GitManager`.

## Claim-4: Full systemd unit lifecycle management with file integrity checking

The `ServiceManager` handles systemd operations: `restart`, `remove` (stop + delete file + daemon-reload), `daemon-reload`. The `FileManager` validates quadlet file types before deployment, checks whether a unit is already deployed via byte-level comparison (`are_identical`), and copies files only when they differ, minimizing systemd reloads.

**Source evidence:** `src/service_manager.rs:91-123` implements `restart()`, `remove()`, `daemon-reload()`, `systemctl()` with `--user` flag. `src/file_manager.rs:191-216` (`is_unit_file_deployed`) compares existing vs. new quadlet files. `src/file_manager.rs:244-268` (`are_identical`) does incremental byte comparison. `src/file_manager.rs:275-328` (`deploy_unit_file`) validates extension against `SUPPORTED_FILES` before copying.

## Claim-5: Rootless-first design with explicit root warning

Quadit is designed for rootless operation. At startup, `main.rs` checks if running as root (UID 0) and prints a large warning banner citing a GitHub issue. All systemd operations use `--user` flag. The config read path uses the user's home directory (`~/.quadit/`) when `LOCAL=yes`, or `/opt/config/` when containerized.

**Source evidence:** `src/main.rs:11-23` warns with "quadit running with root permissions" when `users::get_current_uid() == 0`. `src/service_manager.rs:114-122` always sets `--user` in systemctl calls. `src/file_manager.rs:123-151` (`quadit_home()`) uses `dirs::home_dir()` when local, `/opt/config` otherwise. `src/file_manager.rs:337-350` (`get_unit_path()`) uses `home_dir()/.config/containers/systemd` for local mode.
