---
name: secureblue-codegraph-verify
tags: [secureblue, codegraph-verify, fedora, security]
description: "Codegraph Verification: secureblue — validating wiki claims against indexed source code"
source: sources/secureblue/
---

# Codegraph Verification: secureblue

**Date:** 2026-07-12

## Claim 1: Security-focused Fedora Atomic derivative built with BlueBuild as bootable OCI containers
- **Wiki says:** "Secureblue provides hardened Fedora Atomic images built using BlueBuild and shipped as OCI bootable containers."

- **Source evidence:**
  - `docs/README.md:16` — "secureblue is a a security-focused desktop and server Linux operating system. It is built using [BlueBuild](https://blue-build.org/) and shipped as a set of [OCI](https://opencontainers.org/) [bootable containers](https://github.com/bootc-dev/bootc), using [Fedora Atomic Desktop](https://fedoraproject.org/atomic-desktops/)'s base images as a starting point."
  - `pyproject.toml:1-7` — `name = "secureblue"`, `version = "4.9"`, `description = "secureblue is a security-focused desktop and server Linux operating system."`, maintainer RoyalOughtness
  - `recipes/general/recipe-silverblue-main.yml:9-11` — `base-image: quay.io/fedora-ostree-desktops/silverblue`, `image-version: 44`
  - `pyproject.toml:15` — `Repository = "https://github.com/secureblue/secureblue"`

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Variant families: Silverblue, Kinoite, Sericea, Cosmic, SecureCore, IoT (incl. NVIDIA-open and ZFS)
- **Wiki says:** "SecureCore (server, CoreOS-based) and IoT (edge) variant families, plus desktop families, with NVIDIA proprietary/open and ZFS variants."

- **Source evidence:**
  - `recipes/general/` — 12 recipes: silverblue/kinoite/sericea/cosmic × (`main`, `nvidia-open`, `nvidia`); NVIDIA recipes chain off the `*-main-hardened` images (e.g. `recipe-silverblue-nvidia-open.yml` base `ghcr.io/secureblue/silverblue-main-hardened`)
  - `recipes/securecore/recipe-securecore-main.yml:9-11` — `base-image: quay.io/fedora/fedora-coreos`, `image-version: next`
  - `recipes/securecore/` — 6 recipes: `main`, `nvidia-open`, `nvidia`, `zfs-main`, `zfs-nvidia-open`, `zfs-nvidia`
  - `recipes/iot/recipe-iot-main.yml:9-11` — `base-image: quay.io/fedora/fedora-iot`, `image-version: 44`
  - `recipes/iot/` — 6 recipes: `main`, `nvidia-open`, `nvidia`, `zfs-main`, `zfs-nvidia-open`, `zfs-nvidia`
  - All recipes declare `platforms: [linux/amd64, linux/arm64]`

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: SELinux hardening with custom policies and boolean adjustments
- **Wiki says:** "SELinux boolean adjustments (deny_ptrace=on, container_allow_ptrace=off) and custom policy modules."

- **Source evidence:**
  - `files/scripts/set-selinux-booleans.sh:9` — `setsebool -P deny_ptrace=on container_allow_ptrace=off`
  - `files/scripts/installselinuxpolicies.sh` — Installs custom SELinux policy modules
  - `files/selinux/` — Custom SELinux policy source directory
  - `recipes/common/selinux-modules.yml` — Composes `installselinuxpolicies.sh` + `set-selinux-booleans.sh` into the module chain
  - `recipes/common/common-modules.yml:25` — Includes `selinux-modules.yml` via `from-file`; all six recipe families reference it

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Kernel signing with SecureBoot and module signing
- **Wiki says:** "Secure boot support with signed kernels and module signing configuration."

- **Source evidence:**
  - `files/scripts/installandsignkernel.sh:10-26` — Installs the secureblue kernel from the secureblue COPR, then `sbattach --remove` + `sbsign` with the secureblue cert (`../system/usr/share/pki/akmods/certs/akmods-secureblue.der` → `public_key.crt`, `/tmp/certs/private_key.priv`), verified with `sbverify`
  - `files/scripts/signmodules.sh:27-34` — Signs kernel modules with `openssl cms` + `sign-file`, then runs `sign-check.sh`
  - `files/scripts/sign-check.sh:14-31` — Verifies module signatures via `extract-module-sig.pl` + `openssl cms -verify`
  - `modules/secureblue-signing/module.yml:1-4` — `secureblue-signing` BlueBuild module type "install[ing] the required signing policies for cosign image verification with rpm-ostree and bootc"
  - `modules/secureblue-signing/policy.json:1-186` — Container signature policy: default reject, `sigstoreSigned` allowlist for blue-build/cli, ublue-os, quay.io/fedora-ostree-desktops, etc.
  - `modules/secureblue-signing/registry-config.yaml:1-3` — Enables `use-sigstore-attachments` for `ghcr.io/IMAGENAME`
  - `recipes/common/common-packages.yml:31` — `sbsigntools`; `common-packages.yml:40-41` — `crane` + `slsa-verifier` (provenance deps)
  - `recipes/common/common-modules.yml:38-44` — Kernel signing runs with `KERNEL_PRIVKEY` env secret mounted to `/tmp/certs/private_key.priv`

- **Verdict:** ✅ CORRECT
- **Fix needed:** Evidence updated — `signkernel.sh` was renamed/merged into `installandsignkernel.sh`; signing policy lives in `modules/secureblue-signing/`.

## Claim 5: Kernel argument hardening
- **Wiki says:** "Kernel arguments: lockdown=confidentiality, module.sig_enforce=1, init_on_alloc/free, slab_nomerge, vsyscall=none."

- **Source evidence:**
  - `files/system/usr/lib/bootc/kargs.d/10-secureblue.toml:5-40` — `lockdown=confidentiality`, `module.sig_enforce=1`, `init_on_alloc=1`, `init_on_free=1`, `slab_nomerge`, `vsyscall=none`, `pti=on`, `mitigations=auto,nosmt`, `l1tf=full,force`, `spectre_v2=on`, `iommu=force`, `kvm_amd.sev*`, `hash_pointers=always`
  - `files/system/usr/libexec/secureblue/set_kargs_hardening.py` — ujust-backed tool that applies the `DEFAULT_KARGS` from `kargs_hardening_common`
  - `files/system/usr/libexec/secureblue/kargs_hardening_common/__init__.py:13-14,36-37` — Loads `10-secureblue.toml` as `DEFAULT_KARGS`; `module.sig_enforce=1` constant

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: DNS via dnsconfd with unbound as the local resolver; LLMNR disabled
- **Wiki says:** "DNS through dnsconfd with unbound as the local resolver (dnsconfd-unbound); LLMNR disabled."

- **Source evidence:**
  - `recipes/common/common-packages.yml:12` — `dnsconfd-unbound` package installed
  - `files/scripts/setup-dnsconfd.sh:9-15` — Installs the NetworkManager dnsconfd config and fixes `/etc/resolv.conf` ownership to `dnsconfd:root`
  - `files/system/etc/NetworkManager/conf.d/dnsconfd.conf:3` — `dns=dnsconfd` (NetworkManager delegates to `com.redhat.dnsconfd`)
  - `files/system/usr/lib/systemd/system-preset/40-secureblue.preset:6,10` — `dnsconfd.service` and `secureblue-unbound-key.service` enabled
  - `files/system/usr/lib/systemd/system/secureblue-unbound-key.service` — Bootstraps `/var/lib/unbound/root.key` so `dnsconfd-unbound` can run with DNSSEC validation
  - `files/system/etc/systemd/resolved.conf.d/10-disable-llmnr.conf:2` — `LLMNR=false`
  - `files/system/usr/lib/systemd/system-preset/40-secureblue.preset:42` — `systemd-resolved.service` disabled (DNS handled by dnsconfd, not resolved)

- **Verdict:** ✅ CORRECT
- **Fix needed:** Evidence updated — DNS stack is `dnsconfd` + `dnsconfd-unbound`, not a plain unbound install.

## Claim 7: Firewall default zones
- **Wiki says:** "firewalld DefaultZone=FedoraWorkstation on desktop variants, DefaultZone=FedoraServer on server/IoT variants."

- **Source evidence:**
  - `files/scripts/setfirewalldefaultzone.sh:9` — `sed -i 's/^DefaultZone=.*/DefaultZone=FedoraWorkstation/' /etc/firewalld/firewalld.conf`
  - `recipes/common/desktop-scripts.yml:19` — `setfirewalldefaultzone.sh` runs in the desktop module chain
  - `files/scripts/setserverdefaultzone.sh:9` — `sed -i 's/^DefaultZone=public/DefaultZone=FedoraServer/' /etc/firewalld/firewalld.conf`
  - `recipes/common/server-modules.yml:26` — `setserverdefaultzone.sh` runs for SecureCore/IoT (server) variants

- **Verdict:** ✅ CORRECT
- **Fix needed:** Evidence added — no "drop zone" default anywhere in the source.

## Claim 8: Automatic update model (stage + timer + upgrade-on-boot)
- **Wiki says:** "Updates staged automatically via rpm-ostreed (AutomaticUpdatePolicy=stage, rpm-ostreed-automatic.timer enabled); desktop variants apply staged updates at boot via upgrade-on-boot.service."

- **Source evidence:**
  - `files/system/etc/rpm-ostreed.conf:2` — `AutomaticUpdatePolicy=stage`
  - `files/system/usr/lib/systemd/system-preset/40-secureblue.preset:9` — `enable rpm-ostreed-automatic.timer`
  - `files/system/desktop/usr/lib/systemd/system-preset/35-secureblue-desktop.preset` — `enable upgrade-on-boot.service` (desktop only)
  - `files/system/desktop/usr/lib/systemd/system/upgrade-on-boot.service:11-12` — ExecCondition checks `/var/lib/secureblue/always-upgrade-on-boot.stamp` (or the `securebluecheckoutofdate` script), then runs `/usr/libexec/secureblue/upgrade-on-boot`
  - `files/system/etc/systemd/system/rpm-ostreed-automatic.timer.d/override.conf` — `OnCalendar=*-*-* 4:00:00`, `Persistent=true`, `RandomizedDelaySec=10m`

- **Verdict:** ✅ CORRECT
- **Fix needed:** Evidence added — wording is "stage + timer (+ upgrade-on-boot on desktop)", not a blanket "always-upgrade-on-boot mode".

## Summary

All 8 key claims from the secureblue wiki have been verified against the source code:
- ✅ **Bootable OCI containers:** BlueBuild + Fedora Atomic base confirmed in all recipes
- ✅ **Variant families:** Silverblue/Kinoite/Sericea/Cosmic + SecureCore + IoT with NVIDIA proprietary/open and ZFS options
- ✅ **SELinux hardening:** Custom policies with `deny_ptrace=on`, `container_allow_ptrace=off`
- ✅ **Kernel signing:** `installandsignkernel.sh` (sbsign/sbattach/sbverify), `signmodules.sh`, `sign-check.sh`, `modules/secureblue-signing` policy
- ✅ **Kernel args:** `10-secureblue.toml` with lockdown, sig_enforce, init_on_alloc/free, slab_nomerge, vsyscall=none
- ✅ **DNS:** dnsconfd + dnsconfd-unbound, LLMNR disabled, DNSSEC root-key bootstrap
- ✅ **Firewall zones:** FedoraWorkstation (desktop) / FedoraServer (server, IoT)
- ✅ **Updates:** `AutomaticUpdatePolicy=stage` + timer + desktop `upgrade-on-boot.service`

## Related

- [[secureblue]] -- Main wiki entry
- [[bootc]] -- Bootable container technology underlying the images
- [[tank-os]] -- Related bootc-based deployment image
- [[fedora-coreos-config]] -- FCOS configuration for SecureCore variant

## Cross-project

- [[bootc.codegraph-verify]] -- Bootable container foundation
- [[tank-os.codegraph-verify]] -- Comparable bootc deployment appliance
- [[fedora-coreos-config.codegraph-verify]] -- CoreOS configuration consumed by SecureCore variant
