---
name: secureblue
tags: [secureblue, fedora, bootc, security, hardening, immutable-os]
description: "Hardened Fedora Atomic images for security-focused deployments"
source: sources/secureblue/
---

# Secureblue

| Field | Value |
|---|---|
| **Origin** | [secureblue/secureblue](https://github.com/secureblue/secureblue) |
| **Source** | `sources/secureblue/` |
| **Repomix** | `raw/secureblue/secureblue.xml` |
| **Codegraph** | `graphs/secureblue/` |

## Overview

Secureblue provides hardened Fedora Atomic (Silverblue/Kinoite/Sericea) images with security-focused kernel parameters, system configurations, and default application profiles. It builds on Fedora's immutable desktop and server base images, applying a comprehensive set of hardening measures — including SELinux policy tightening, kernel lockdown, sysctl hardening, MAC address randomization, and firewall defaults — to create a "batteries-included" secure OS image suitable for both desktop and server deployments.

## Key Features

- **Kernel Hardening** — Applied kernel parameters including lockdown mode, KASLR, module signing enforcement, and restricted BPF
- **SELinux Policy Hardening** — Tightened default policies beyond Fedora's targeted policy
- **Network Hardening** — Default firewall rules, DNS-over-TLS, MAC randomization, and mDNS blocking
- **Application Sandboxing** — Hardened browser profiles (Firefox, Chromium) and Flatpak permission defaults
- **Audit & Compliance** — Configured auditd rules and compliance scanning with OpenSCAP profiles
- **Boot Integrity** — Secure boot support with signed kernels and initramfs verification

## Architecture

Secureblue follows the bootc image model: hardened configurations are layered onto Fedora Atomic base images as OCI container images. Users rebase (switch) their existing Fedora Atomic installation to a Secureblue-derived image, receiving hardening updates through the normal ostree update mechanism. The project maintains distinct image variants for desktop (Silverblue/Kinoite), server, and cloud deployment targets.

## Related

- [[bootc]] — OS update mechanism used to deliver and maintain Secureblue images
- [[tank-os]] — Fedora bootc image for agent deployment (complementary hardened images)
- [[fedora-coreos-config]] — Fedora CoreOS configuration that shares the ostree/bootc paradigm
- [[podman]] — Container runtime for running workloads on Secureblue systems
