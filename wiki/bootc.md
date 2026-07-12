---
name: bootc
tags: [bootc, container, oci, ostree, transactional, os-updates, container-image, wiki]
description: bootc does transactional, in-place OS updates using OCI container images
source: sources/bootc/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# bootc — Bootable Container OS

| Field | Value |
|---|---|
| **Origin** | [containers/bootc](https://github.com/containers/bootc) |
| **License** | Apache 2.0 / MIT dual-license |
| **Stack** | Rust, ostree, OCI/Docker |
| **Source** | `sources/bootc/` |

## Overview

bootc provides **transactional, in-place operating system updates** using standard OCI/Docker container images. It applies the container "layers" model to entire bootable operating systems, enabling OS updates to be managed like container image updates. The container image includes a complete Linux kernel (in `/usr/lib/modules`) and userspace. At runtime on a target system, the base userspace is *not* itself running in a container — systemd acts as pid1 directly, with no outer container runtime wrapper.

The project is a [CNCF Sandbox project](https://www.cncf.io/sandbox-projects/) and the key component in the broader [bootable containers](https://containers.github.io/bootable/) initiative. The underlying ostree project has over 13 years of production use powering operating system updates across Fedora, Red Hat, and many derived distributions. The CLI and API are considered stable — every existing system can be upgraded in place seamlessly across future changes.

### Adopters

Major adopters include **Red Hat** (Image Based Linux), **Universal Blue** (Aurora/Bazzite/Bluefin — "the reliability of a Chromebook with the flexibility of a traditional Linux desktop"), **HeliumOS** (atomic desktop OS), **AlmaLinux Atomic SIG**, **CIQ** (Rocky Linux), and **Caligra Workbench**. Indirect adopters via ostree include the **Fedora Atomic Desktops**, **Endless OS**, **Apertis**, and **Playtron GameOS**. See the project's [ADOPTERS.md](https://github.com/containers/bootc/blob/main/ADOPTERS.md) for the full list.

### Versioning

bootc follows [semantic versioning](https://semver.org/) standards since version 1.2.0. The project ships as a Rust workspace (`crates/*`) with 14 crate crates including `cli`, `lib`, `mount`, `ostree-ext`, `initramfs`, and `blockdev`.

## Key Features

- **Transactional A/B updates** — Backed by ostree, implementing an A/B partition style upgrade system. Changes are staged and the running system is not modified until the next boot, with automatic rollback on failure.
- **OCI image format** — Uses standard container images from any OCI-compliant registry (Quay.io, Docker Hub, GHCR, etc.). Any tool that can push/pull OCI images works with bootc.
- **Staged updates with `--download-only`** — Download updates without applying them, then verify with `bootc status --verbose` before committing. Apply via `bootc upgrade --from-downloaded` when the maintenance window opens.
- **`bootc switch` for blue/green deployments** — Change the tracked container image source to implement blue/green or canary rollouts: `bootc switch quay.io/examplecorp/os-prod-blue:latest`. Preserves `/etc` and `/var` state including SSH keys and home directories.
- **`bootc rollback`** — Swap the bootloader ordering to the previous deployment entry. Rollback is the primary recovery path.
- **Kernel-in-image** — The container image embeds the kernel at `/usr/lib/modules/$kver/vmlinuz` and the initramfs alongside it. bootc copies kernel/initramfs to `/boot` at deploy time.
- **Registry-agnostic** — Works with any OCI-compliant container registry. Supports authenticated registries, mirrors, and offline/air-gapped deployments.
- **Boot failure detection** — Automatic detection and rollback of failed boots, managed by systemd services.
- **composefs backend** (experimental) — Alternative storage backend providing verified images and reduced disk usage for the composefs-enabled deployments.

## Architecture

### CLI Commands

The primary user interface is the `bootc` CLI:

| Command | Description |
|---|---|
| `bootc upgrade` | Fetch and stage an update from the container image source |
| `bootc upgrade --apply` | Stage and immediately reboot into the update |
| `bootc upgrade --download-only` | Download the update without scheduling application |
| `bootc upgrade --check` | Check for available updates without side effects |
| `bootc switch <image>` | Change the tracked container image source |
| `bootc status` | Show current boot image, staged deployment, and update status |
| `bootc rollback` | Revert to the previous deployment |
| `bootc edit` | Declarative interface for configuration management |
| `bootc install` / `bootc install to-disk` | Install bootc to a target disk |
| `bootc usr-overlay` | Create a writable overlay on `/usr` (development) |
| `bootc container lint` | Validate a container image for bootc compatibility |

There is also a `bootc-fetch-apply-updates.timer` and corresponding systemd service for automated periodic update checks.

### Image Requirements

A bootc-compatible container image must satisfy:

- **`/sysroot` directory** — The mount point for the physical root, with permissions matching `/usr` (0755).
- **`LABEL containers.bootc=1`** — Required label so higher-level tooling can identify bootc-compatible images.
- **Kernel split** — Kernel at `/usr/lib/modules/$kver/vmlinuz`, initramfs at `initramfs.img` in the same directory. No content in `/boot` inside the image.
- **SELinux** — File contexts are loaded from the image's `/etc/selinux/policy` and applied dynamically at boot time.

Reference configuration is available in the bootc repository's [`baseimage/`](https://github.com/containers/bootc/tree/main/baseimage) directory.

### Update Pipeline

1. Image author builds an OCI container image containing kernel, userspace, and configuration.
2. Image is pushed to an OCI-compliant registry.
3. Target system runs `bootc upgrade` which pulls the image and creates a staged deployment via ostree.
4. On reboot, the bootloader selects the staged deployment.
5. If boot fails, bootc's failure detection triggers automatic rollback to the previous deployment.

### API Control

bootc exposes a D-Bus API for programmatic control, allowing management agents to invoke operations like `bootc switch`, `bootc upgrade`, and `bootc status` without direct CLI invocation. See the [bootc-via-api](https://github.com/containers/bootc/blob/main/docs/src/bootc-via-api.md) documentation.

### Build Pipeline

The project is written in Rust with a Cargo workspace of 14 crates. Notable crates include:

- `lib/` — Core library with the high-level bootc logic
- `cli/` — CLI argument parsing and dispatch via clap
- `ostree-ext/` — Ostree integration and extension functionality
- `mount/` — Filesystem mount management
- `initramfs/` — Initramfs generation hooks
- `blockdev/` — Block device handling for `bootc install`
- `etc-merge/` — Configuration file merging across deployments

Integration with systemd is deep — bootc ships multiple systemd units for boot failure detection, destructive cleanup, root setup, and fetch-apply-update timers.

### SELinux

bootc loads SELinux file contexts from the image's `/etc/selinux/policy` and applies labels dynamically at boot time — this is the only mechanism that works with generic bootc-unaware build tooling. Container runtimes like Podman apply a coarse SELinux policy to running containers; bootc images instead embed the full policy for direct-boot systems. File contexts are dynamically applied rather than embedded in OCI tar layers.

## Usage Examples

```bash
# Basic upgrade workflow
bootc upgrade                                  # Fetch and stage updates
bootc upgrade --apply                          # Stage and reboot immediately

# Controlled update with download-only
bootc upgrade --download-only                  # Pre-download without applying
bootc status --verbose                         # Verify Download-only: yes
bootc upgrade --from-downloaded                # Apply at scheduled time

# Blue/green deployment pattern
bootc switch quay.io/examplecorp/os-blue:latest

# Rollback to previous deployment
bootc rollback

# Check for updates without modifying state
bootc upgrade --check

# Validate a container image
bootc container lint --image quay.io/path/to/image
```

## Related

- [[podman]] — OCI runtime that builds and runs bootc container images; bootc images can be inspected and built with Podman
- [[buildah]] — OCI image builder for creating bootc-compatible container images
- [[tank-os]] — Fedora bootc image for agent deployment, demonstrating bootc as a deployment vehicle
- [[tank-agent-os]] — Bootable agent OS image built on Fedora bootc with hardened security
- [[fedora-coreos-config]] — Fedora CoreOS configuration repository; FCOS images can serve as bootc base images
- [[coreos-assembler]] — Build pipeline for Fedora CoreOS images; the toolchain that produces bootc-compatible OS images
- [[crun-vm]] — OCI runtime integration for VM-based bootc deployments, running bootc images in micro-VMs
- [[hermes-agent]] — Agent platform deployable as bootc container images
- [[openclaw]] — Agent platform deployable as bootc container images
- [[goclaw]] — Agent gateway deployable via bootc
- [[hermzner]] — Hetzner deployment automation using bootc OS images
- [[agentfield]] — Control plane deployable via bootc for multi-agent orchestration
- [[secureblue]] — Hardened Fedora Atomic images built on bootc technology

## Cross-project

- [[nix-podman-stacks]] — NixOS configurations for deploying bootc-based systems
- [[podman-quadlet]] — systemd-native container management that pairs with bootc for complete OS+workload lifecycle

