---
name: bootc-architecture
tags: [bootc, architecture, container, oci, ostree, transactional, os-updates, immutable-os]
description: Architecture of bootc — transactional, in-place OS updates using standard OCI container images
source: sources/bootc/
---

# Bootc Architecture

## Overview

bootc provides **transactional, in-place operating system updates** using standard OCI/Docker container images. It applies the container "layers" model to entire bootable OS images — the container includes a Linux kernel (in `/usr/lib/modules`) and full userspace. At runtime, systemd acts as PID 1 directly with no outer container runtime wrapper. The project is a CNCF Sandbox project and the key component in the broader [bootable containers](https://containers.github.io/bootable/) initiative, backed by 13+ years of ostree production use powering Fedora, Red Hat, and derived distributions.

## Architecture

```
Image author builds OCI image (kernel + userspace + config)
        │  push to OCI registry
        ▼
Target system: bootc upgrade
        │  pull image → ostree stage
        ▼
Staged deployment (A/B partition via ostree)
        │  reboot
        ▼
Bootloader selects new deployment
        │  systemd PID 1
        ▼
Failure? → Automatic rollback to previous deployment
```

### Update Pipeline

1. **Image authoring** — Build an OCI container image containing kernel at `/usr/lib/modules/$kver/vmlinuz`, initramfs, userspace, and configuration. Image must have `LABEL containers.bootc=1` and a `/sysroot` directory.
2. **Registry push** — Image is pushed to any OCI-compliant registry (Quay.io, Docker Hub, GHCR).
3. **Staged upgrade** — Target runs `bootc upgrade` which pulls the image and creates a staged deployment via ostree, without modifying the running system.
4. **Activation** — On reboot, the bootloader selects the staged deployment. System boots directly into the new OS image.
5. **Rollback** — If boot fails, bootc's failure detection triggers automatic rollback. Manual rollback via `bootc rollback`.

### CLI Architecture

The primary interface is the `bootc` CLI (Rust, clap-based):

- **`bootc upgrade`** — Fetch and stage an update; `--apply` reboots immediately; `--download-only` pre-fetches without scheduling
- **`bootc switch <image>`** — Change tracked image source for blue/green or canary rollouts
- **`bootc status`** — Current boot image, staged deployment, and update status
- **`bootc rollback`** — Swap bootloader ordering to previous deployment
- **`bootc install`** / **`bootc install to-disk`** — Install bootc to a target disk
- **`bootc edit`** — Declarative configuration management
- **`bootc container lint`** — Validate an OCI image for bootc compatibility

A systemd timer (`bootc-fetch-apply-updates.timer`) provides automated periodic update checks.

### Build Architecture

The Rust workspace comprises 14 crates:

| Crate | Purpose |
|-------|---------|
| `lib/` | Core bootc logic |
| `cli/` | CLI argument parsing via clap |
| `ostree-ext/` | Ostree integration and extension |
| `mount/` | Filesystem mount management |
| `initramfs/` | Initramfs generation hooks |
| `blockdev/` | Block device handling for `bootc install` |
| `etc-merge/` | Configuration file merging across deployments |
| `kernel_cmdline/` | Kernel command-line management |

Deep integration with systemd — units for boot failure detection, destructive cleanup, root setup, and fetch-apply-update timers.

## Key Components

- **ostree backend** — A/B partition-style deployment system. The running system is never modified; new deployments are staged and activated on next boot.
- **composefs backend** (experimental) — Alternative storage providing verified images and reduced disk usage.
- **D-Bus API** — Programmatic control for management agents: `bootc switch`, `bootc upgrade`, `bootc status` without CLI.
- **SELinux integration** — File contexts loaded from image's `/etc/selinux/policy`, applied dynamically at boot time (not embedded in OCI tar layers).
- **Kernel-in-image model** — Kernel at `/usr/lib/modules/$kver/vmlinuz`, initramfs in same directory. Copied to `/boot` at deploy time.

## Related

- [[bootc]] — Wiki overview of the project
- [[podman]] — OCI runtime that builds and runs bootc images
- [[coreos-assembler]] — Build pipeline for Fedora CoreOS bootc images
- [[tank-os]] — Fedora bootc image for agent deployment (reference consumer)
- [[crun-vm]] — OCI runtime for VM-based bootc deployments
- [[buildah]] — OCI image builder for creating bootc-compatible images
