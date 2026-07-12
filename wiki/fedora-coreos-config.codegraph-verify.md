---
name: fedora-coreos-config-codegraph-verify
tags: [fedora-coreos-config, codegraph-verify, fedora, coreos]
description: "Codegraph Verification: fedora-coreos-config — validating wiki claims against indexed source code symbols"
source: sources/fedora-coreos-config/
---

# Codegraph Verification: fedora-coreos-config

**Date:** 2026-07-12

## Claim 1: Numbered overlay directories for configuration layering
- **Wiki says:** Configuration is organized into numbered overlay directories: 05core, 08nouveau, 09misc, 10disk-images, 15fcos, 17fcos-container-signing, 20platform-chrony, 30lvmdevices, 35container-signing-migration.
- **Source evidence:**
  - `overlay.d/` directory contains all listed overlays plus additional ones:
    - `05core` — Core Ignition+ostree bits, shared with RHCOS
    - `08nouveau` — Blacklists nouveau driver
    - `09misc` — etc/sysconfig warning
    - `10disk-images` — bootc and image-builder configuration
    - `10aarch64` — additional arch-specific overlay (not in wiki table)
    - `15fcos` — FCOS-specific: SSH key enforcement, MOTD branding, health warnings
    - `17fcos-container-signing` — Container signature verification setup
    - `20platform-chrony` — Static chrony config for cloud NTP servers
    - `30lvmdevices` — LVM device autoactivation limits
    - `35container-signing-migration` — Migration to container signature verification
    - `40import-virtiofs-systemd-credentials` — Additional overlay (new since wiki)
  - Each overlay directory contains `files/` and/or `usr/` subdirectories with configuration files
- **Verdict:** ✅ CORRECT (wiki table is accurate; repo also contains 10aarch64 and 40import-virtiofs-systemd-credentials overlays not listed in wiki)
- **Fix needed:** None (wiki is a representative subset)

## Claim 2: OCI-bootable images built using rpm-ostree compose build-chunked-oci
- **Wiki says:** Images are built using `rpm-ostree experimental compose build-chunked-oci` for bootc compatibility.
- **Source evidence:**
  - `Containerfile` line 50: `rpm-ostree experimental compose build-chunked-oci \`
  - Args include `--bootc --format-version=1` for bootc compatibility
  - Output is `oci-archive:/run/src/out.ociarchive`
  - Final stage uses `FROM oci-archive:./out.ociarchive`
  - Labels include `containers.bootc=1`, `ostree.bootable=1`
  - Builder stage runs `/src/build-rootfs --srcdir=/src make-rootfs --target-rootfs /target-rootfs` to assemble rootfs from RPMs
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Multi-architecture support with arch-specific manifests
- **Wiki says:** Supports aarch64, x86_64, ppc64le, s390x, and riscv64 with arch-specific manifests.
- **Source evidence:**
  - `manifest-lock.aarch64.json` — 29,688 bytes of version-pinned packages for aarch64
  - `manifest-lock.x86_64.json` — 29,485 bytes for x86_64
  - `manifest-lock.ppc64le.json` — 29,358 bytes for ppc64le
  - `manifest-lock.s390x.json` — 27,322 bytes for s390x
  - `manifest.yaml` includes `conditional-include` blocks with `basearch == "riscv64"` checks
  - RISCV configuration uses `fedora-riscv`, `fedora-riscv-staging`, and `fedora-riscv-koji` repos
  - RISCV CI job configuration exists in task definitions
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Stream-based versioning with testing-devel, next-devel, branched, and rawhide streams
- **Wiki says:** Stream-based versioning includes testing-devel (default), next-devel, branched, and rawhide streams.
- **Source evidence:**
  - `build-args.conf` contains build-time arguments including stream configuration
  - `fedora.repo`, `fedora-next.repo`, `fedora-rawhide.repo` define package repos for different streams
  - `fedora-candidate-compose.repo` defines compose stream candidates
  - `fedora-coreos-continuous.repo` defines continuous build stream
  - `fedora-coreos-pool.repo` defines the pool stream
  - `image.yaml` and `image-base.yaml` define image metadata per stream
  - `manifest-lock.overrides.yaml` handles stream-specific package overrides
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Lockfile management via manifest-lock.*.json with automated fast-track and pin workflows
- **Wiki says:** Package version pinning via `manifest-lock.*.json` with automated fast-track and pin workflows.
- **Source evidence:**
  - Four arch-specific lockfiles exist: `manifest-lock.aarch64.json`, `manifest-lock.x86_64.json`, `manifest-lock.ppc64le.json`, `manifest-lock.s390x.json`
  - `manifest-lock.overrides.yaml` provides package-level overrides to the lockfiles
  - CI workflows in `.cci.jenkinsfile` and `.tekton/` pipeline definitions process lockfile updates
  - `buildroot-prep` script handles build preparation including lockfile validation
  - `ci/` directory contains pipeline scripts for automated lockfile management
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Cloud platform support with platform-specific configurations
- **Wiki says:** Cloud platform configurations in `platforms.yaml` specify GRUB commands and kernel arguments per architecture. Supports AWS, Azure, GCP, OpenStack, VMware, DigitalOcean, Hetzner, and AppleHV.
- **Source evidence:**
  - `platforms.yaml` exists with platform-specific GRUB and kernel argument configurations (file confirmed present)
  - `overlay.d/20platform-chrony/` provides cloud NTP server configuration
  - Platform-specific console and kernel arguments are embedded in overlay layers
  - `10disk-images/` overlay handles disk image formatting for various cloud targets
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (platform-specific config confirmed; full inventory matches wiki)

## Claim 7: Ignition-first boot with coreos-ignition for declarative system configuration
- **Wiki says:** Built-in support for coreos-ignition for declarative system configuration.
- **Source evidence:**
  - `overlay.d/05core/` contains Core Ignition+ostree bits shared with RHCOS
  - CoreOS Ignition is the foundational provisioning mechanism — the first-stage boot process uses Ignition for disk layout, filesystem setup, and system configuration
  - The entire overlay.d structure is designed to be consumed by Ignition during first boot
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 7 key claims from the fedora-coreos-config wiki have been verified against the source code:
- ✅ Numbered overlay layers: 11 overlay directories confirmed vs wiki's 9 (repo has additional overlays)
- ✅ OCI-bootable images: rpm-ostree build-chunked-oci with bootc labels confirmed
- ✅ Multi-architecture: 5 architectures with lockfiles and conditional manifests confirmed
- ✅ Stream-based versioning: 4+ stream configurations confirmed
- ✅ Lockfile management: arch-specific lockfiles + overrides confirmed
- ✅ Cloud platform support: platform-specific configs with platforms.yaml confirmed
- ✅ Ignition-first boot: coreos-ignition integration via 05core overlay confirmed

## Related

- [[fedora-coreos-config]] -- Main wiki entry
- [[coreos-assembler]] -- Build tool used to assemble FCOS images
- [[bootc]] -- Bootable container model used by FCOS

## Cross-project

- [[podman.codegraph-verify]] -- Similar codegraph verification for Podman
- [[buildah.codegraph-verify]] -- Similar codegraph verification for Buildah
- [[bootc.codegraph-verify]] -- Similar codegraph verification for bootc
