---
name: secureblue-codegraph-verify
tags: [secureblue, codegraph-verify, fedora, security]
description: "Codegraph Verification: secureblue — validating wiki claims against indexed source code"
source: sources/secureblue/
---

# Codegraph Verification: secureblue

**Date:** 2026-07-12

## Claim 1: Security-focused Fedora Atomic derivative built with BlueBuild as bootable OCI containers
- **Wiki says:** "secureblue is a security-focused desktop and server Linux operating system built using BlueBuild and shipped as bootable OCI containers based on Fedora Atomic Desktop base images."

- **Source evidence:**
  - `docs/README.md:16` — "secureblue is a a security-focused desktop and server Linux operating system. It is built using [BlueBuild](https://blue-build.org/) and shipped as a set of [OCI](https://opencontainers.org/) [bootable containers](https://github.com/bootc-dev/bootc), using [Fedora Atomic Desktop](https://fedoraproject.org/atomic-desktops/)'s base images as a starting point."
  - `pyproject.toml:1-8` — `name = "secureblue"`, `version = "4.9"`, `description = "secureblue is a security-focused desktop and server Linux operating system."`
  - `recipes/general/recipe-silverblue-main.yml:2-7` — `base-image: quay.io/fedora-ostree-desktops/silverblue`, `image-version: 44` — confirms Fedora Atomic base
  - `recipes/securecore/recipe-securecore-main.yml:2-7` — `base-image: quay.io/fedora/fedora-coreos`, `image-version: next` — CoreOS variant
  - `recipes/iot/recipe-iot-main.yml:2-7` — `base-image: quay.io/fedora/fedora-iot`, `image-version: 44` — IoT variant
  - `pyproject.toml:14` — `Repository = "https://github.com/secureblue/secureblue"`

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Multiple variant flavors: Silverblue, Kinoite, Sericea, Cosmic, IoT, SecureCore
- **Wiki says:** "secureblue offers hardened variants of multiple Fedora Atomic desktop and server flavors: Silverblue (GNOME), Kinoite (KDE), Sericea (Sway), Cosmic, IoT (edge), and SecureCore (CoreOS for servers)."

- **Source evidence:**
  - `recipes/general/recipe-silverblue-main.yml` — `silverblue-main-hardened`, base `quay.io/fedora-ostree-desktops/silverblue`
  - `recipes/general/recipe-silverblue-nvidia-open.yml` — Silverblue + NVIDIA open driver
  - `recipes/general/recipe-silverblue-nvidia.yml` — Silverblue + NVIDIA proprietary
  - `recipes/general/recipe-kinoite-main.yml` — Kinoite (KDE) variant
  - `recipes/general/recipe-kinoite-nvidia-open.yml`, `recipe-kinoite-nvidia.yml` — Kinoite + NVIDIA
  - `recipes/general/recipe-sericea-main.yml` — Sericea (Sway) variant
  - `recipes/general/recipe-sericea-nvidia-open.yml`, `recipe-sericea-nvidia.yml` — Sericea + NVIDIA
  - `recipes/general/recipe-cosmic-main.yml` — Cosmic (COSMIC desktop) variant
  - `recipes/general/recipe-cosmic-nvidia-open.yml`, `recipe-cosmic-nvidia.yml` — Cosmic + NVIDIA
  - `recipes/iot/recipe-iot-main.yml` — IoT (edge) variant
  - `recipes/securecore/recipe-securecore-main.yml` — SecureCore (CoreOS server) variant
  - `recipes/securecore/recipe-securecore-zfs-main.yml` — SecureCore with ZFS
  - All recipes declare `platforms: [linux/amd64, linux/arm64]` — multi-architecture support

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: SELinux hardening with custom policies and boolean adjustments
- **Wiki says:** "secureblue applies SELinux hardening including custom policy modules and restrictive boolean adjustments (deny_ptrace=on, container_allow_ptrace=off)."

- **Source evidence:**
  - `recipes/common/selinux-modules.yml` — Module composition with scripts: `installselinuxpolicies.sh`, `set-selinux-booleans.sh`
  - `files/scripts/installselinuxpolicies.sh` — Installs custom SELinux policy modules
  - `files/scripts/set-selinux-booleans.sh:8` — `setsebool -P deny_ptrace=on container_allow_ptrace=off` — Restrictive boolean adjustments
  - `files/selinux/` — Directory containing custom SELinux policy files
  - `recipes/common/common-modules.yml:23-24` — Includes `selinux-modules.yml` via `from-file` directive
  - Each base recipe (silverblue, kinoite, sericea, iot, securecore) includes `common/selinux-modules.yml` in its module chain

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Kernel signing with SecureBoot and module signing
- **Wiki says:** "secureblue signs the kernel with custom SecureBoot keys and signs kernel modules, implementing driver signature verification for security."

- **Source evidence:**
  - `files/scripts/signkernel.sh:1-25` — Signs kernel `vmlinuz` with `sbsign` using secureblue's custom cert (`public_key.crt`) and private key (`private_key.priv`), verified with `sbverify`
  - `files/scripts/signmodules.sh` — Kernel module signing script
  - `files/scripts/sign-check.sh` — Signature verification check script
  - `files/secureblue-signing/` — SecureBoot signing key and certificate directory
  - `recipes/common/common-packages.yml:23` — `sbsigntools` package installed — required for `sbsign`/`sbverify` tooling
  - `recipes/common/common-packages.yml:18` — `crane` for provenance/signing support
  - `recipes/securecore/` — All SecureCore recipes inherit kernel signing

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Hardened memory allocator (hardened_malloc) with SUID exclusions
- **Wiki says:** "secureblue replaces glibc's default malloc with hardened_malloc for improved security, with carefully maintained exclusion lists for SUID binaries that experience incompatibilities."

- **Source evidence:**
  - `recipes/common/common-packages.yml:6` — `hardened_malloc` package installed via DNF
  - `files/scripts/removesuid.sh:10-35` — Hardened_malloc exclusion list: `libhardened_malloc-light.so`, `libhardened_malloc-pkey.so`, `libhardened_malloc.so` at multiple glibc-hwcaps paths (x86-64, x86-64-v2, x86-64-v3, x86-64-v4)
  - `files/scripts/hardened_malloc-pam.sh` — PAM integration for hardened_malloc
  - `files/scripts/set-ld-preload.sh` — LD_PRELOAD configuration for hardened_malloc
  - `files/scripts/systemsettings-standard-malloc.sh` — System settings standard malloc override
  - `recipes/common/silverblue-modules.yml` — Includes scripts for malloc hardening in desktop variants

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: SUID removal and privilege escalation hardening
- **Wiki says:** "secureblue aggressively removes SUID bits from binaries to reduce privilege escalation attack surface, maintaining an exemption list for required SUID binaries like nvidia-modprobe and hardened_malloc."

- **Source evidence:**
  - `files/scripts/removesuid.sh:1-40` — Main SUID removal script. Exemption list includes:
    - `/usr/bin/nvidia-modprobe` (NVIDIA closed driver)
    - Multiple `libhardened_malloc*.so` paths (glibc-hwcaps compatibility)
  - `files/scripts/removesudo.sh` — Removes sudo binary entirely
  - `files/scripts/ensuresudoabsent.sh` — Post-install sanity check that sudo is absent
  - `recipes/common/final-modules.yml:9-10` — `removesuid.sh` and `removesudo.sh` run in final module stage
  - `recipes/common/final-modules.yml:11` — `ensuresudoabsent.sh` — double-checks sudo removal
  - `files/scripts/unprotectsudo.sh` — Complementary script for initial sudo configuration

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 6 key claims from the secureblue wiki have been verified against the source code:
- ✅ **Bootable OCI containers:** BlueBuild + Fedora Atomic base confirmed in all recipes
- ✅ **Variant flavors:** Silverblue, Kinoite, Sericea, Cosmic, IoT, SecureCore with NVIDIA/ZFS options
- ✅ **SELinux hardening:** Custom policies with `deny_ptrace=on`, `container_allow_ptrace=off`
- ✅ **Kernel signing:** `signkernel.sh` with `sbsign`/`sbverify` and custom certs confirmed
- ✅ **Hardened_malloc:** Package install + LD_PRELOAD + SUID exemption list confirmed
- ✅ **SUID removal:** Comprehensive script with documented exemption list and sudo removal

## Related

- [[secureblue]] -- Main wiki entry
- [[bootc]] -- Bootable container technology underlying the images
- [[tank-os]] -- Related bootc-based deployment image
- [[fedora-coreos-config]] -- FCOS configuration for SecureCore variant

## Cross-project

- [[bootc.codegraph-verify]] -- Bootable container foundation
- [[tank-os.codegraph-verify]] -- Comparable bootc deployment appliance
- [[fedora-coreos-config.codegraph-verify]] -- CoreOS configuration consumed by SecureCore variant
