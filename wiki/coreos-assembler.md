---
name: coreos-assembler
tags: [coreos-assembler, fedora, bootc, image-builder, ostree, container-linux]
description: "Build pipeline and tooling for creating Fedora CoreOS images and derivatives"
source: sources/coreos-assembler/
---

# coreos-assembler

| Field | Value |
|---|---|
| **Origin** | [coreos/coreos-assembler](https://github.com/coreos/coreos-assembler) |
| **Source** | `sources/coreos-assembler/` |
| **Repomix** | `raw/coreos-assembler/coreos-assembler.xml` |
| **Codegraph** | `graphs/coreos-assembler/` |

## Overview

coreos-assembler (also known as `cosa`) is the build pipeline and tooling used to create Fedora CoreOS (FCOS) images and derivative operating systems. It orchestrates the full image build lifecycle — from package selection and composition through OSTree commit creation and final disk image generation. The tool runs inside a containerized build environment, ensuring reproducible and auditable OS image builds.

## Key Features

- **Containerized Build Environment** — Self-contained build pod with all dependencies bundled in a container image
- **OSTree Commit Generation** — Composes package sets into versioned, atomic OSTree commits
- **Disk Image Assembly** — Produces raw disk images, QCOW2, ISO, and cloud-init-enabled images
- **Live ISO Creation** — Builds live ISO images suitable for PXE boot and bare-metal provisioning
- **Update Stream Management** — Generates update metadata for over-the-air OS update delivery
- **CI Integration** — Designed for automated pipeline runs; used in Fedora CoreOS CI for continuous release builds

## Architecture

coreos-assembler runs as a privileged container (the "build pod") that mounts host-level storage and KVM devices for accelerating QEMU-based image operations. Builds are defined by a YAML manifest specifying the package set, filesystem layout, and image format. The pipeline produces structured output artifacts — OSTree commits, disk images, and update metadata — that are pushed to distribution infrastructure for consumption by end systems.

## Related

- [[fedora-coreos-config]] — Configuration repository for Fedora CoreOS image definitions
- [[bootc]] — Transactional OS updates using OCI container images (successor paradigm)
- [[tank-os]] — Fedora bootc image for agent deployment
- [[podman]] — Container runtime used to run coreos-assembler build pods
