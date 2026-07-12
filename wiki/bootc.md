---
name: bootc
tags: [bootc, container, oci, ostree, transactional, os-updates, container-image, wiki]
description: bootc does transactional, in-place OS updates using OCI container images
source: sources/bootc/
---

# bootc — Bootable Container OS

| Field | Value |
|---|---|
| **Origin** | [containers/bootc](https://github.com/containers/bootc) |
| **License** | Apache 2.0 / MIT dual-license |
| **Stack** | Rust, ostree |
| **Source** | `sources/bootc/` |

## What it is

bootc provides **transactional, in-place operating system updates** using standard OCI/Docker container images. It applies the container "layers" model to entire bootable operating systems, enabling OS updates to be managed like container image updates.

The container image contains a complete Linux kernel (in `/usr/lib/modules`) and userspace. At runtime, the system boots directly from these images — systemd acts as pid1 without any container runtime wrapper.

## Key Features

- **Transactional updates** — A/B style upgrades backed by ostree, with automatic rollback on failure
- **OCI image format** — Uses standard container images from any OCI-compliant registry
- **Staged updates** — Download-only mode (`--download-only`) for preparing updates without applying them
- **In-place upgrades** — Updates applied to the running system without requiring reinstall
- **Kernel-in-image** — The container image includes the kernel for direct boot capability
- **Registry-agnostic** — Works with any container registry supporting OCI

## How it Works

bootc uses ostree under the hood to implement an A/B partition style upgrade system. Changes are staged and applied on reboot, keeping the running system intact until the next boot.

```bash
bootc upgrade           # Fetch and stage updates
bootc upgrade --apply   # Apply immediately
bootc status            # Show current boot image and update status
```

## Related

- [[podman]] — OCI runtime that can run bootc-built container images
- [[buildah]] — OCI image builder for creating bootc container images
- [[hermes-agent]] — Agent platform deployable as bootc container images
- [[openclaw]] — Agent platform deployable as bootc container images
- [[tank-os]] — Fedora bootc image for agent deployment
- [[goclaw]] — Agent gateway deployable via bootc
- [[crun-vm]] — OCI runtime integration for VM-based bootc deployments

## Cross-project

- [[hermzner]] — Hetzner deployment with bootc OS images
- [[agentfield]] — Control plane deployable via bootc