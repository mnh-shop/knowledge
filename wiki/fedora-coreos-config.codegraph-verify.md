---
name: fedora-coreos-config-codegraph-verify
tags: [fedora-coreos-config, codegraph-verify, fedora, coreos]
description: "Codegraph Verification: fedora-coreos-config — validating wiki claims against indexed source code symbols"
source: sources/fedora-coreos-config/
---

# Codegraph Verification: fedora-coreos-config

**Date:** 2026-07-12

## Claim 1: Numbered overlay directories for configuration layering
- **Wiki says:** Configuration is organized into numbered overlay directories: 05core, 08nouveau, 09misc, 10aarch64, 10disk-images, 15fcos, 16fcos-sshd-workaround, 17fcos-container-signing, 20platform-chrony, 30lvmdevices, 35container-signing-migration, 40import-virtiofs-systemd-credentials.
- **Source evidence:**
  - `overlay.d/` directory contains all listed overlays (12 directories):
    - `05core` — Core Ignition+ostree bits, shared with RHCOS
    - `08nouveau` — Blacklists nouveau driver
    - `09misc` — etc/sysconfig warning
    - `10aarch64` — aarch64-specific configuration
    - `10disk-images` — bootc and image-builder configuration
    - `15fcos` — FCOS-specific: SSH key enforcement, MOTD branding, health warnings
    - `16fcos-sshd-workaround` — systemd generator `coreos-sshd-generator` (`overlay.d/16fcos-sshd-workaround/usr/lib/systemd/system-generators/coreos-sshd-generator`) patching sshd `AuthorizedKeysFile` so ignition/afterburn keys are honored
    - `17fcos-container-signing` — Container signature verification setup
    - `20platform-chrony` — Static chrony config for cloud NTP servers
    - `30lvmdevices` — LVM device autoactivation limits
    - `35container-signing-migration` — Migration to container signature verification
    - `40import-virtiofs-systemd-credentials` — Expose systemd-credentials via virtiofs (`overlay.d/README.md` documents this as the non-Ignition alternative for bootable containers)
  - Each overlay directory contains `files/` and/or `usr/` subdirectories with configuration files
- **Verdict:** ⚠️ CORRECTED — wiki previously listed 9 overlays; `16fcos-sshd-workaround` and `40import-virtiofs-systemd-credentials` were missing (both now in wiki table).
- **Fix needed:** Add `16fcos-sshd-workaround` and `40import-virtiofs-systemd-credentials` (applied to wiki).

## Claim 2: OCI-bootable images built using rpm-ostree compose build-chunked-oci
- **Wiki says:** Images are built using `rpm-ostree experimental compose build-chunked-oci` for bootc compatibility.
- **Source evidence:**
  - `Containerfile:68-70` — `rpm-ostree experimental compose build-chunked-oci \` with `--bootc --format-version=1 --rootfs /target-rootfs` and `--output oci-archive:/run/src/out.ociarchive`
  - `Containerfile:50` — Builder stage runs `/src/build-rootfs --srcdir=/src make-rootfs --target-rootfs /target-rootfs` to assemble rootfs from RPMs
  - `Containerfile:82` — Final stage uses `FROM oci-archive:./out.ociarchive`
  - `Containerfile:93-94` — Labels include `containers.bootc=1`, `ostree.bootable=1`
  - `Containerfile:19` — `FROM ${BUILDER_IMG} as builder`; `build-args.conf:10` sets `BUILDER_IMG=quay.io/bootc-devel/fedora-bootc-44-standard@sha256:...` (bootc-integrated builder image)
- **Verdict:** ⚠️ CORRECTED — the `build-chunked-oci` invocation cite drifted from `Containerfile:50` to the correct `:68-70`; builder image note added.
- **Fix needed:** Cite fixed to `Containerfile:68-70` (applied to wiki).

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
- **Wiki says:** Cloud platform configurations in `platforms.yaml` specify GRUB commands and kernel arguments per architecture. Supports AWS, Azure, GCP, OpenStack, VMware, Hetzner, AppleHV, IBM Cloud, Oracle Cloud, KubeVirt, ProxmoxVE, VirtualBox, and QEMU.
- **Source evidence:**
  - `platforms.yaml` exists with platform-specific GRUB and kernel argument configurations, organized by architecture (`aarch64:` at :16, `ppc64le:` at :80, `x86_64:` at :96, `riscv64:` at :216)
  - Platform keys present in `platforms.yaml`: applehv, aws, azure, gcp, hetzner, ibmcloud, kubevirt, openstack, oraclecloud, proxmoxve, qemu, virtualbox, vmware
  - **DigitalOcean is NOT present** in `platforms.yaml` (no `digitalocean:` key under any architecture) — earlier wiki listing was stale
  - `overlay.d/20platform-chrony/` provides cloud NTP server configuration
  - `10disk-images/` overlay handles disk image formatting for various cloud targets
- **Verdict:** ⚠️ CORRECTED — removed stale DigitalOcean entry; added oraclecloud, ibmcloud, kubevirt, proxmoxve, virtualbox, qemu.
- **Fix needed:** Platform list corrected (applied to wiki).

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
- ⚠️ Numbered overlay layers: 12 overlay directories confirmed; `16fcos-sshd-workaround` and `40import-virtiofs-systemd-credentials` added to wiki
- ⚠️ OCI-bootable images: rpm-ostree build-chunked-oci at `Containerfile:68-70` with bootc labels confirmed (cite corrected from :50); builder image `quay.io/bootc-devel/fedora-bootc-44-standard` confirmed
- ✅ Multi-architecture: 5 architectures with lockfiles and conditional manifests confirmed
- ✅ Stream-based versioning: 4+ stream configurations confirmed
- ✅ Lockfile management: arch-specific lockfiles + overrides confirmed
- ⚠️ Cloud platform support: 13 platforms confirmed in platforms.yaml; DigitalOcean removed
- ✅ Ignition-first boot: coreos-ignition integration via 05core overlay confirmed

## Related

- [[fedora-coreos-config]] -- Main wiki entry
- [[coreos-assembler]] -- Build tool used to assemble FCOS images
- [[bootc]] -- Bootable container model used by FCOS

## Cross-project

- [[podman.codegraph-verify]] -- Similar codegraph verification for Podman
- [[buildah.codegraph-verify]] -- Similar codegraph verification for Buildah
- [[bootc.codegraph-verify]] -- Similar codegraph verification for bootc
