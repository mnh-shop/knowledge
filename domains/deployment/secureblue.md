---
name: secureblue-deployment
tags: [atomic, bootc, bluebuild, deployment, fedora, hardening, immutable-os, security, secureblue, selinux]
description: "Secureblue deployment — variant matrix, hardening map, signing pipeline, update model, recipe chain architecture"
source: sources/secureblue/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Secureblue Deployment

**Source:** `sources/secureblue/`
**Raw:** `raw/secureblue/secureblue.xml`
**Codegraph:** `graphs/secureblue/`

Deployment and image-architecture guide for secureblue — a security-focused Fedora Atomic OS distribution built with BlueBuild and shipped as bootable OCI containers (bootc images). Users rebase an existing Fedora Atomic installation onto a secureblue image and receive hardening updates through the normal ostree/bootc update mechanism.

## Variant Matrix

Secureblue builds 24 recipes across six families. NVIDIA recipes chain off each family's `main-hardened` image; ZFS variants exist for the IoT and SecureCore families only.

| Family | Base Image | `image-version` | Recipes (`recipes/`) |
|---|---|---|---|
| **Silverblue** | `quay.io/fedora-ostree-desktops/silverblue` | 44 | `main`, `nvidia-open`, `nvidia` |
| **Kinoite** | `quay.io/fedora-ostree-desktops/kinoite` | 44 | `main`, `nvidia-open`, `nvidia` |
| **Sericea** | `quay.io/fedora-ostree-desktops/sway-atomic` | 44 | `main`, `nvidia-open`, `nvidia` |
| **Cosmic** | `quay.io/fedora-ostree-desktops/cosmic-atomic` | 44 | `main`, `nvidia-open`, `nvidia` |
| **SecureCore** (server) | `quay.io/fedora/fedora-coreos` | next | `main`, `nvidia-open`, `nvidia`, `zfs-main`, `zfs-nvidia-open`, `zfs-nvidia` |
| **IoT** (edge) | `quay.io/fedora/fedora-iot` | 44 | `main`, `nvidia-open`, `nvidia`, `zfs-main`, `zfs-nvidia-open`, `zfs-nvidia` |

All recipes declare `platforms: [linux/amd64, linux/arm64]` and are published to `ghcr.io/secureblue/*`.

## Recipe Chain Architecture

Each recipe composes a module stack in order — common → variant → desktop/server → proprietary → selinux → final:

```
recipe-silverblue-main.yml
├── common/common-modules.yml        # script + files + packages + justfiles + kernel signing
│   ├── common/common-packages.yml   # dnf install/remove (hardened_malloc, dnsconfd-unbound, ...)
│   ├── common/common-scripts.yml    # set-ld-preload, setup-dnsconfd, disableresolved, ...
│   └── installandsignkernel.sh      # sbsign kernel (KERNEL_PRIVKEY secret) + secureblue-signing module
├── common/silverblue-modules.yml    # variant-specific files/scripts/justfiles
├── common/desktop-modules.yml       # system/desktop files + desktop-packages + desktop-scripts
├── common/proprietary-modules.yml   # NVIDIA proprietary driver path
├── common/selinux-modules.yml       # installselinuxpolicies.sh + set-selinux-booleans.sh
└── common/final-modules.yml         # addimageinfo, regenerateinitramfs, removesuid, removesudo, ensuresudoabsent, ...
```

Module types used (`common-modules.yml`): `script`, `files`, `dnf`, `justfiles`, and the local `secureblue-signing` type. Files live under `files/system/` with a `usr`/`etc` split plus `server/`, `desktop/`, per-desktop-family (`silverblue/`, `kinoite/`, `sericea/`, `cosmic/`), `nvidia/`, and `zfs/` overlay trees.

## Hardening Map

| Layer | Mechanism | Source |
|---|---|---|
| **Kernel args** | `lockdown=confidentiality`, `module.sig_enforce=1`, `init_on_alloc=1`, `init_on_free=1`, `slab_nomerge`, `vsyscall=none`, `pti=on`, `mitigations=auto,nosmt`, IOMMU/SEV | `files/system/usr/lib/bootc/kargs.d/10-secureblue.toml`, `set_kargs_hardening.py` |
| **Sysctl** | TCP syncookies/rfc1337, rp_filter, redirects off, martian logging, ipv6 privacy | `files/system/usr/lib/sysctl.d/55-hardening.conf` (+ `server/usr/lib/sysctl.d/56-server-hardening.conf` for SecureCore/IoT) |
| **SELinux** | `deny_ptrace=on`, `container_allow_ptrace=off`; custom policy modules | `set-selinux-booleans.sh:9`, `installselinuxpolicies.sh`, `files/selinux/` |
| **DNS** | NetworkManager `dns=dnsconfd` → unbound (`dnsconfd-unbound`) with DNSSEC root-key bootstrap; LLMNR off, systemd-resolved disabled, avahi/mDNS disabled | `NetworkManager/conf.d/dnsconfd.conf:3`, `setup-dnsconfd.sh`, `secureblue-unbound-key.service`, `10-disable-llmnr.conf` |
| **Firewall** | firewalld `DefaultZone=FedoraWorkstation` (desktop) / `DefaultZone=FedoraServer` (SecureCore, IoT) | `setfirewalldefaultzone.sh:9`, `setserverdefaultzone.sh:9` |
| **Memory** | hardened_malloc LD_PRELOAD system-wide (`libhardened_malloc.so libno_rlimit_as.so`), SUID exclusions, core dumps disabled | `common-packages.yml:10`, `profile.d/hardened_malloc.sh`, `system.conf.d/40-hardened_malloc.conf`, `removesuid.sh`, `60-disable-coredump.conf` |
| **Privilege** | SUID removal + sudo removal (`ensuresudoabsent.sh` in final stage) | `removesuid.sh`, `removesudo.sh`, `final-modules.yml:12-15` |
| **USB** | USBGuard authorization control (desktop + server) | `desktop-packages.yml:13-14`, `server-modules.yml:12` |
| **Services** | CUPS disabled (desktop), Bluetooth/webcam deny toggles, ptrace scope, userns remapping, audit checks | `disablecups.sh`, `bluetooth_main.py`, `webcam_main.py`, `set_ptrace.py`, `set_container_userns.py`, `audit_secureblue.py` |
| **PAM** | `pwquality.conf`, `faillock.conf`, hardened logindefs | `files/system/etc/security/` |

Optional hardening toggles (not enabled by default) are exposed via `ujust` — e.g. `toggle-mac-randomization` (`files/justfiles/common/toggles.just:202`), 32-bit emulation off, `nosmt=force`, and unstable kargs — applied through `set_kargs_hardening.py`.

## Signing & Provenance Pipeline

- **Kernel signing** — `installandsignkernel.sh` installs the secureblue-patched kernel from the secureblue COPR, strips existing signatures (`sbattach --remove`) and re-signs with the secureblue key (`sbsign`), verifying with `sbverify`. The private key is injected at build time as the `KERNEL_PRIVKEY` env secret (mounted to `/tmp/certs/private_key.priv`). Kernel modules are signed by `signmodules.sh` (openssl cms + `sign-file`) and checked by `sign-check.sh`.
- **Image signing policy** — the local `secureblue-signing` BlueBuild module installs `modules/secureblue-signing/policy.json` (containers/image policy: default `reject`, `sigstoreSigned` allowlist for blue-build, ublue-os, fedora-ostree-desktops, redhat registries, etc.) and `registry-config.yaml` (`use-sigstore-attachments: true` for the secureblue repo). `sbsigntools`, `crane`, and `slsa-verifier` are installed via `common-packages.yml:31,40-41`.
- **Provenance verification** — `files/system/usr/libexec/secureblue/verify-provenance.sh` resolves the booted `ghcr.io/secureblue/*` image, maps its tag to a source branch, and runs `slsa-verifier verify-image` against SLSA build provenance.

## Update Model

- `rpm-ostreed.conf:2` — `AutomaticUpdatePolicy=stage`: updates are downloaded and staged automatically, applied on next boot.
- `rpm-ostreed-automatic.timer` enabled via `40-secureblue.preset:9` (daily 04:00, `Persistent=true`, `RandomizedDelaySec=10m`).
- **Desktop variants only**: `upgrade-on-boot.service` (`35-secureblue-desktop.preset`) applies staged updates at boot unless suppressed via the `/var/lib/secureblue/always-upgrade-on-boot.stamp` toggle (`set_always_upgrade_on_boot.py`).
- SecureCore disables `zincati.service` and the CoreOS migration MOTD (`30-securecore.preset`); IoT/edge inherit the same server preset.

## Deploying

```bash
# Rebase an existing Fedora Atomic desktop onto secureblue
sudo rpm-ostree rebase ostree-image-signed:ghcr.io/secureblue/silverblue-main

# Server / edge
sudo rpm-ostree rebase ostree-image-signed:ghcr.io/secureblue/securecore-main
sudo rpm-ostree rebase ostree-image-signed:ghcr.io/secureblue/iot-main
```

Secureboot kernels are signed with the secureblue key; the container signature policy only allows sigstore-signed images from trusted registries (`modules/secureblue-signing/policy.json`).

## Related

- [[secureblue]] -- Wiki overview of the project
- [[tank-os-deployment]] -- Sibling Fedora bootc image family for agent deployment
- [[bootc]] -- Bootable container technology underlying the images
- [[fedora-coreos-config]] -- FCOS base configuration for the SecureCore variant
