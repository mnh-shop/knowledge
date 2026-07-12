---
name: fedora-coreos-config
tags: [bootc, container, fedora, fedora-coreos-config, image-builder, immutable-os, linux, oci, qemu, security, virtualization, wiki]
description: "Base manifest configuration for Fedora CoreOS, defining bootable OCI images for immutable infrastructure"
source: sources/fedora-coreos-config/
---

# fedora-coreos-config

Base manifest configuration for Fedora CoreOS. Provides the declarative configuration used by coreos-assembler to build Fedora CoreOS, a container-centric Linux distribution designed for scalable infrastructure and aligned with the image-based update model.

| Field | Value |
|---|---|
| **Origin** | [coreos/fedora-coreos-config](https://github.com/coreos/fedora-coreos-config) |
| **License** | COPYING (BSD-style) |
| **Build Tool** | coreos-assembler, rpm-ostree |
| **Source** | `sources/fedora-coreos-config/` |
| **Related** | [[podman]], [[buildah]], [[nix-podman-stacks]] |

## What it is

fedora-coreos-config is the authoritative source repository for Fedora CoreOS configuration. It uses rpm-ostree to compose OCI-bootable images from RPM packages, following the bootc model where container images serve as the transport and delivery format for OS updates. The configuration is split into reusable layers for derivation by downstream projects like Fedora Silverblue.

## Key Features

- **OCI-bootable images** — Built using `rpm-ostree experimental compose build-chunked-oci` for bootc compatibility
- **Multi-architecture support** — aarch64, x86_64, ppc64le, s390x, and riscv64 with arch-specific manifests
- **Stream-based versioning** — testing-devel (default), next-devel, branched, and rawhide streams
- **Lockfile management** — Package version pinning via `manifest-lock.*.json` with automated fast-track and pin workflows
- **Platform customization** — Console and kernel arguments for AWS, Azure, GCP, Hetzner, VMware, and other cloud platforms
- **Ignition-first boot** — Built-in support for coreos-ignition for declarative system configuration
- **Container signing integration** — Configuration for quay.io container signature verification

## Architecture

### Overlay Layers

Configuration is organized into numbered overlay directories:

| Overlay | Purpose |
|---|---|
| 05core | Core Ignition+ostree bits, shared with RHCOS |
| 08nouveau | Blacklists nouveau driver for NVidia GPU compatibility |
| 09misc | etc/sysconfig warning |
| 10disk-images | bootc and image-builder configuration |
| 15fcos | FCOS-specific: SSH key enforcement, MOTD branding, health warnings |
| 17fcos-container-signing | Container signature verification setup |
| 20platform-chrony | Static chrony config for cloud NTP servers |
| 30lvmdevices | LVM device autoactivation limits |
| 35container-signing-migration | Migration to container signature verification |

### Image Building

The build process uses a multi-stage Containerfile:
1. Builder stage runs `build-rootfs` to assemble the rootfs from RPMs
2. `rpm-ostree compose build-chunked-oci` creates OCI archive with bootc metadata
3. Final stage produces a bootable OCI image with proper labels

### Platform Support

Cloud platform configurations in `platforms.yaml` specify GRUB commands and kernel arguments per architecture. Supports AWS, Azure, GCP, OpenStack, VMware, DigitalOcean, Hetzner, and AppleHV (macOS virtualization).

## Tests

- **kola tests** — Automated integration tests in `tests/kola/` using the kola framework
- **CoreOS CI** — Jenkins-based pipeline in `.cci.jenkinsfile`
- **Manual tests** — Procedures in `tests/manual/`

## Building Images

Use coreos-assembler to build Fedora CoreOS images:

```bash
# Clone and set up coreos-assembler
git clone https://github.com/coreos/coreos-assembler
cd coreos-assembler

# Build FCOS using this config
cosa fetch --repo=https://example.com/compose-root
cosa build
```

Custom derivatives can add this repo as a git submodule and include `ignition-and-ostree.yaml` in their own manifest.

## Related

- [[podman]] — Container runtime; rootless containers on FCOS for running services
- [[buildah]] — OCI image builder; builds FCOS images via the Containerfile
- [[nix-podman-stacks]] — Uses similar image-based deployment patterns for self-hosted infrastructure
- [[crun-vm]] — OCI runtime for VMs; relevant for FCOS virtualization use cases