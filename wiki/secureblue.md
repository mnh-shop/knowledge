---
name: secureblue
tags: [secureblue, fedora, bootc, security, hardening, immutable-os, bluebuild, atomic]
description: "Hardened Fedora Atomic images built with BlueBuild for security-focused desktop and server deployments"
source: sources/secureblue/
verification_date: 2026-07-12
verified_by: fixer (source analysis)
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

Secureblue provides hardened Fedora Atomic (Silverblue, Kinoite, Sericea, Server, Cosmic) images with security-focused kernel parameters, system configurations, and default application profiles. It is built using [BlueBuild](https://blue-build.org/) and shipped as a set of OCI bootable containers, using Fedora Atomic Desktop's base images as a starting point. Hardened configurations are layered onto Fedora Atomic base images as OCI container images; users rebase their existing Fedora Atomic installation to a secureblue-derived image, receiving hardening updates through the normal ostree update mechanism.

Secureblue applies a comprehensive set of hardening measures — including SELinux policy tightening, kernel lockdown, sysctl hardening, MAC address randomization, firewall defaults, JIT hardening, and hardware module blacklisting — to create a "batteries-included" secure OS image suitable for both desktop and server deployments. The project maintains distinct image variants for desktop (Silverblue, Kinoite, Sericea, Cosmic) and server deployment targets, with separate NVIDIA and ZFS variants.

The project is maintained by RoyalOughtness and the secureblue community, with OpenSSF Best Practices and Scorecard badges, and automated CI/CD pipelines for building, integration testing, and vulnerability scanning (Trivy).

## Key Features

- **Kernel Hardening** — Applied kernel parameters including lockdown mode (integrity/c confidentiality), KASLR, module signing enforcement, restricted BPF, and kernel module blacklisting for unnecessary or dangerous modules (Firewire, Thunderbolt DMA via dracut config).
- **SELinux Policy Hardening** — Tightened default policies beyond Fedora's targeted policy. Includes custom policy modules and labeled file system configurations.
- **Network Hardening** — Default firewall rules via firewalld with restrictive zone configuration, DNS-over-TLS via unbound, MAC address randomization (NetworkManager), mDNS blocking, DHCP hostname sending disabled, LLMNR disabled via systemd-resolved.
- **Application Sandboxing** — Hardened browser profiles (Firefox, Chromium), Flatpak permission restrictions, and system-wide JIT hardening via hardened_malloc LD_PRELOAD in `/etc/profile.d/`.
- **Audit & Compliance** — Configured auditd rules (`audit_secureblue.py`) and compliance scanning with OpenSCAP profiles. Regular vulnerability scanning via Trivy in CI.
- **Boot Integrity** — Secure boot support with signed kernels and initramfs verification. Kernel signing scripts and module signing configuration.
- **Memory Hardening** — Hardened memory allocator enabled system-wide, core dump disabled (`60-disable-coredump.conf`), ASLR enabled, and kernel address space layout randomization.
- **USB Device Control** — USBGuard integration for USB device authorization control on desktop and server variants.
- **Password Policy** — Hardened `pwquality.conf` settings, `faillock.conf` for account lockout after failed attempts, and restricted `limits.d/` configuration.
- **Container Security** — Hardened containers configuration: user namespace remapping (`set_container_userns.py`), unconfined userns restrictions, and locked-down registries configuration.
- **Printer Restrictions** — CUPS disabled by default on hardened configurations to reduce attack surface.
- **Provenance Verification** — Verified container provenance via cosign signature verification (`verify-provenance.sh`).
- **Automatic Updates** — Configured for automatic system updates via rpm-ostreed automatic service with always-upgrade-on-boot mode.
- **Bluetooth Hardening** — Bluetooth service disabled by default via hardened profile, with toggle script available (`bluetooth_main.py`).
- **Webcam Denial** — Webcam access denied by default on hardened desktop profiles, with toggle script (`webcam_main.py`).
- **BIOS/Firmware Protection** — BIOS password enforcement scripts for supported hardware.

## Image Variants

Secureblue produces multiple image variants through BlueBuild recipe files under `recipes/general/`:

| Variant | Base Image | Use Case |
|---|---|---|
| **Silverblue** | Fedora Silverblue | Hardened GNOME desktop |
| **Kinoite** | Fedora Kinoite | Hardened KDE desktop |
| **Sericea** | Fedora Sericea | Hardened Sway (Wayland) desktop |
| **Cosmic** | Fedora Cosmic | Hardened COSMIC desktop |
| **Server** | Fedora CoreOS-base | Hardened server |
| **NVIDIA variants** | Above + NVIDIA drivers | Desktop/server with NVIDIA GPUs |
| **ZFS variants** | Above + ZFS | Desktop/server with ZFS filesystem |

Each variant includes variant-specific module files (e.g., `silverblue-modules.yml`, `kinoite-modules.yml`, `server-modules.yml`) layered on top of shared common modules (`common-modules.yml`, `common-packages.yml`, `common-scripts.yml`, `selinux-modules.yml`).

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

- **Kernel arguments** — Applied via `kargs_hardening_common`: lockdown, slab/nettrace hardening, randomize layout, restrict BPF
- **Sysctl hardening** — Network security parameters, kernel pointer hiding, restricted dmesg, ptrace scope limited (`set_ptrace.py`)
- **Systemd services** — Automatic updates, resolved with DNSSEC, tmpfiles for secure directories
- **Firewall** — FedoraWorkstation zone permissive → drop zone on server, restrictive service definitions
- **Unbound DNS** — DNS-over-TLS resolver with DNSSEC validation, blocking mDNS/LLMNR
- **Hardened malloc** — System-wide via `hardened_malloc.sh` in profile.d
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
