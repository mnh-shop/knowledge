---
name: secureblue
tags: [secureblue, fedora, bootc, security, hardening, immutable-os, bluebuild, atomic]
description: "Hardened Fedora Atomic images built with BlueBuild for security-focused desktop and server deployments"
source: sources/secureblue/
verification_date: 2026-07-12
verified_by: codegraph-verify
source_reference: sources/secureblue/docs/README.md, sources/secureblue/recipes/, sources/secureblue/files/
---

# Secureblue

| Field | Value |
|---|---|
| **Origin** | [secureblue/secureblue](https://github.com/secureblue/secureblue) |
| **License** | Apache-2.0 |
| **Stack** | BlueBuild (OCI image builder), Fedora Atomic base, Python (tooling), Shell (hardening scripts) |
| **Version** | 4.9 |
| **Source** | `sources/secureblue/` |
| **Repomix** | `raw/secureblue/secureblue.xml` |
| **Codegraph** | `graphs/secureblue/` |

## Overview

Secureblue provides hardened Fedora Atomic (Silverblue, Kinoite, Sericea, Cosmic, IoT, SecureCore) images with security-focused kernel parameters, system configurations, and default application profiles. It is built using [BlueBuild](https://blue-build.org/) and shipped as a set of OCI bootable containers, using Fedora Atomic Desktop's base images as a starting point. Hardened configurations are layered onto Fedora Atomic base images as OCI container images; users rebase their existing Fedora Atomic installation to a secureblue-derived image, receiving hardening updates through the normal ostree update mechanism.

Secureblue applies a comprehensive set of hardening measures — including SELinux policy tightening, kernel lockdown, sysctl hardening, firewall zone defaults, JIT hardening, and hardware module blacklisting — to create a "batteries-included" secure OS image suitable for both desktop and server deployments. The project maintains distinct image variants for desktop (Silverblue, Kinoite, Sericea, Cosmic), edge (IoT), and server (SecureCore) deployment targets, with separate NVIDIA (proprietary and open) and ZFS variants.

The project is maintained by RoyalOughtness and the secureblue community, with OpenSSF Best Practices and Scorecard badges, and automated CI/CD pipelines for building, integration testing, and vulnerability scanning (Trivy).

## Key Features

- **Kernel Hardening** — Applied kernel parameters including `lockdown=confidentiality`, module signature enforcement (`module.sig_enforce=1`), memory zeroing (`init_on_alloc=1`/`init_on_free=1`), `slab_nomerge`, `vsyscall=none`, CPU mitigations (`mitigations=auto,nosmt`, `spectre_v2=on`, `l1tf=full,force`), and kernel module blacklisting for unnecessary or dangerous modules (Firewire, Thunderbolt DMA via dracut config).
- **SELinux Policy Hardening** — Tightened default policies beyond Fedora's targeted policy. Includes custom policy modules and labeled file system configurations.
- **Network Hardening** — Default firewall zones via firewalld (FedoraWorkstation on desktop variants, FedoraServer on server/IoT variants), DNS through dnsconfd with unbound as the local resolver (`dnsconfd-unbound`), mDNS/avahi disabled, LLMNR disabled via systemd-resolved.
- **Application Sandboxing** — Hardened browser profiles (Firefox, Chromium), Flatpak permission restrictions, and system-wide JIT hardening via hardened_malloc LD_PRELOAD in `/etc/profile.d/`.
- **Audit & Compliance** — Configured auditd rules and audit checks (`audit_secureblue.py`). Regular vulnerability scanning via Trivy in CI.
- **Boot Integrity** — Secure boot support with signed kernels and initramfs verification. Kernel signing scripts and module signing configuration.
- **Memory Hardening** — Hardened memory allocator enabled system-wide, core dump disabled (`60-disable-coredump.conf`), ASLR enabled, and kernel address space layout randomization.
- **USB Device Control** — USBGuard integration for USB device authorization control on desktop and server variants.
- **Password Policy** — Hardened `pwquality.conf` settings, `faillock.conf` for account lockout after failed attempts, and restricted `limits.d/` configuration.
- **Container Security** — Hardened containers configuration: user namespace remapping (`set_container_userns.py`), unconfined userns restrictions, and locked-down registries configuration.
- **Printer Restrictions** — CUPS disabled by default on hardened configurations to reduce attack surface.
- **Provenance Verification** — Verified container provenance via cosign signature verification (`verify-provenance.sh`).
- **Automatic Updates** — Updates staged automatically via rpm-ostreed (`AutomaticUpdatePolicy=stage`, `rpm-ostreed-automatic.timer` enabled); desktop variants additionally apply staged updates at boot via `upgrade-on-boot.service`.
- **Bluetooth Hardening** — Bluetooth service disabled by default via hardened profile, with toggle script available (`bluetooth_main.py`).
- **Webcam Denial** — Webcam access denied by default on hardened desktop profiles, with toggle script (`webcam_main.py`).
- **BIOS/Firmware Protection** — BIOS password enforcement scripts for supported hardware.

## Image Variants

Secureblue produces image variants through BlueBuild recipe files under `recipes/general/`, `recipes/iot/`, and `recipes/securecore/`. NVIDIA variants chain off each family's `main-hardened` image (proprietary driver via `*-nvidia`, open driver via `*-nvidia-open`); ZFS variants are provided for the IoT and SecureCore families.

| Variant Family | Base Image | Recipes (`recipes/`) |
|---|---|---|
| **Silverblue** | `quay.io/fedora-ostree-desktops/silverblue` | `main`, `nvidia-open`, `nvidia` |
| **Kinoite** | `quay.io/fedora-ostree-desktops/kinoite` | `main`, `nvidia-open`, `nvidia` |
| **Sericea** | `quay.io/fedora-ostree-desktops/sway-atomic` | `main`, `nvidia-open`, `nvidia` |
| **Cosmic** | `quay.io/fedora-ostree-desktops/cosmic-atomic` | `main`, `nvidia-open`, `nvidia` |
| **SecureCore** (server) | `quay.io/fedora/fedora-coreos` | `main`, `nvidia-open`, `nvidia`, `zfs-main`, `zfs-nvidia-open`, `zfs-nvidia` |
| **IoT** (edge) | `quay.io/fedora/fedora-iot` | `main`, `nvidia-open`, `nvidia`, `zfs-main`, `zfs-nvidia-open`, `zfs-nvidia` |

Desktop families (Silverblue, Kinoite, Sericea, Cosmic) layer `silverblue-modules.yml`/`kinoite-modules.yml`/`sericea-modules.yml`/`cosmic-modules.yml` plus `desktop-modules.yml`; SecureCore and IoT use `server-modules.yml`. All families share the common module chain (`common-modules.yml`, `common-packages.yml`, `common-scripts.yml`, `selinux-modules.yml`, `final-modules.yml`).

## Architecture

Secureblue follows the **bootc image model**: hardened configurations are layered onto Fedora Atomic base images as OCI container images. The build pipeline uses BlueBuild, which processes recipe YAML files that declare:

1. **Base image** — Fedora Atomic variant (e.g., quay.io/fedora-ostree-desktops/silverblue)
2. **Modules** — Stack of configuration steps executed sequentially:
   - `type: script` — Shell scripts for system modifications
   - `type: files` — File overrides placed into the system (under `files/system/`)
   - `type: dnf` — Package installs/removals
   - `type: justfiles` — Just task runner commands for user-facing operations
   - `type: secureblue-signing` — Kernel/module signing
3. **Secrets** — Kernel signing keys mounted as files during build

The recipe module stack is additive: common modules run first (shared across all variants), then variant-specific modules apply customizations. Users rebase their existing Fedora Atomic installation to a secureblue-derived image and receive hardening updates through the normal **ostree** update mechanism — atomic, rollback-capable system updates.

System configuration files are organized under `files/system/`:
- `system/usr/` — System binaries, libraries, and shared data
- `system/etc/` — System configuration files
- `system/server/` — Server-specific files
- `system/desktop/` — Desktop-specific files (skeleton, udev rules, systemd presets)
- `system/silverblue/`, `system/kinoite/`, `system/sericea/`, `system/cosmic/` — Variant-specific configurations

## Security Hardening Details

The hardening is implemented through a combination of kernel arguments, sysctl parameters, systemd units, SELinux policies, PAM configuration, and runtime scripts:

- **Kernel arguments** — Applied via `files/system/usr/lib/bootc/kargs.d/10-secureblue.toml` (consumed by `set_kargs_hardening.py`/`kargs_hardening_common`): `lockdown=confidentiality`, `module.sig_enforce=1`, `init_on_alloc=1`/`init_on_free=1`, `slab_nomerge`, `vsyscall=none`, `pti=on`, `mitigations=auto,nosmt`, IOMMU/SEV settings
- **Sysctl hardening** — Network security parameters (`55-hardening.conf`), kernel pointer hiding, restricted dmesg, ptrace scope limited (`set_ptrace.py`)
- **Systemd services** — Automatic updates (`rpm-ostreed-automatic.timer`, desktop `upgrade-on-boot.service`), hardened dnsconfd/unbound service units, tmpfiles for secure directories
- **Firewall** — firewalld `DefaultZone=FedoraWorkstation` on desktop variants (`setfirewalldefaultzone.sh`), `DefaultZone=FedoraServer` on server/IoT variants (`setserverdefaultzone.sh`)
- **dnsconfd DNS** — NetworkManager `dns=dnsconfd` (`NetworkManager/conf.d/dnsconfd.conf`), unbound as the local resolver (`dnsconfd-unbound`) with DNSSEC root-key bootstrap (`secureblue-unbound-key.service`); LLMNR disabled (`resolved.conf.d/10-disable-llmnr.conf`), avahi/mDNS disabled
- **Hardened malloc** — System-wide via `hardened_malloc.sh` in profile.d and `system.conf.d/40-hardened_malloc.conf`
- **Container user namespace** — User namespace remapping and unconfined userns restrictions

## Usage / Integration

- **Bootc-based deployment** — Secureblue uses the [[bootc]] mechanism for image delivery and atomic updates. Rebase an existing Fedora Atomic system: `sudo rpm-ostree rebase ostree-image-signed:ghcr.io/secureblue/silverblue-main`.
- **With [[podman]]** — Run hardened container workloads on secureblue systems using [[podman]] with user namespace remapping and locked-down registries.
- **Server automation** — [[fedora-coreos-config]] shares the ostree/bootc paradigm and can serve as a complementary base for custom secureblue server variants.
- **Image building** — [[coreos-assembler]] provides the underlying image assembly tooling for producing bootable OCI images; secureblue uses this infrastructure via the BlueBuild + bootc pipeline.
- **Companion hardened images** — [[tank-os]] is another Fedora bootc image family for agent-oriented deployments, sharing the same bootc foundation.
- **NVIDIA GPU support** — Secureblue produces NVIDIA driver-enabled variants for desktop and server deployments requiring GPU acceleration.
- **ZFS filesystem** — ZFS-enabled variants available for systems requiring advanced storage features on top of hardened configurations.

## Related

- [[bootc]] — OCI bootable container mechanism used to deliver and maintain Secureblue images
- [[tank-os]] — Fedora bootc image for agent deployment (complementary hardened images)
- [[fedora-coreos-config]] — Fedora CoreOS configuration sharing ostree/bootc paradigm
- [[coreos-assembler]] — Image assembly tooling for producing bootc-compatible OS images
- [[podman]] — Container runtime for running workloads on Secureblue systems
- [[cockpit-podman]] — Web UI for managing Podman containers on Secureblue server deployments
