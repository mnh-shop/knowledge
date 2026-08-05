---
name: bootc-codegraph-verify
tags: [bootc, codegraph-verify, container, oci]
description: "Codegraph Verification: bootc — validating wiki claims against indexed source code"
source: sources/bootc/
---

# Codegraph Verification: bootc

**Date:** 2026-07-12

## Claim 1: Transactional in-place OS updates using OCI/Docker container images
- **Wiki says:** "bootc is a tool for transactional, in-place operating system updates using standard OCI/Docker container images as the transport and delivery format. The container image includes a Linux kernel (in e.g. `/usr/lib/modules`) which is used to boot. At runtime on a target system, the base userspace is not itself running in a container by default — systemd acts as pid1."

- **Source evidence:**
  - `README.md:4` — "Transactional, in-place operating system updates using OCI/Docker container images."
  - `README.md:8-12` — "The original Docker container model of using 'layers' to model applications has been extremely successful. This project aims to apply the same technique for bootable host systems - using standard OCI/Docker containers as a transport and delivery format for base operating system updates."
  - `README.md:14-17` — "The container image includes a Linux kernel (in e.g. `/usr/lib/modules`), which is used to boot. At runtime on a target system, the base userspace is *not* itself running in a 'container' by default... systemd acts as pid1 as usual."
  - `crates/lib/src/lib.rs:5-7` — `#![doc = "Bootable container tool"]` — "This crate builds on top of ostree's container functionality to provide a fully 'container native' tool for using bootable container images."
  - `Cargo.toml:1-3` — Workspace with `members = ["crates/*"]` confirming Rust project structure centered on container-based OS update logic.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: CLI subcommands: upgrade, switch, rollback, edit, status, usr-overlay, install, container, image, loader-entries
- **Wiki says:** "bootc provides CLI subcommands: `upgrade` (alias `update`), `switch`, `rollback`, `edit`, `status`, `usr-overlay`, `install`, `container`, `image`, and `loader-entries`."

- **Source evidence:**
  - `crates/lib/src/cli.rs:888-889` — `Upgrade(UpgradeOpts)` with `#[clap(alias = "update")]` — the upgrade verb with alias.
  - `crates/lib/src/cli.rs:900` — `Switch(SwitchOpts)` — target a new container image reference.
  - `crates/lib/src/cli.rs:924` — `Rollback(RollbackOpts)` — change bootloader entry ordering.
  - `crates/lib/src/cli.rs:934` — `Edit(EditOpts)` — "Apply full changes to the host specification."
  - `crates/lib/src/cli.rs:938` — `Status(StatusOpts)` — display bootc system state.
  - `crates/lib/src/cli.rs:942-943` — `UsrOverlay(UsrOverlayOpts)` with `#[clap(alias = "usroverlay")]` — transient overlayfs on `/usr`.
  - `crates/lib/src/cli.rs:948` — `Install(InstallOpts)` — install the running container to a target.
  - `crates/lib/src/cli.rs:951` — `Container(ContainerOpts)` — container-build-time operations.
  - `crates/lib/src/cli.rs:956` — `Image(ImageOpts)` — operations on container images.
  - `crates/lib/src/cli.rs:961` — `LoaderEntries(LoaderEntriesOpts)` — Boot Loader Specification (BLS) entry operations.
  - Upgrade flags: `--check` (`cli.rs:97-98`, conflicts with `apply`), `--apply` (`cli.rs:103-104`, conflicts with `check`), `--download-only` (`cli.rs:117-118`, conflicts with check/apply), `--from-downloaded` (`cli.rs:125-126`, applies a staged deployment without fetching).
  - `crates/lib/src/cli.rs:369-371` — `ContainerOpts::Lint` — "Perform relatively inexpensive static analysis checks as part of a container build" (`bootc container lint`, invoked via `RUN bootc container lint` in a build).
  - **No `cancel` subcommand exists** — a full-tree grep for a `cancel` verb returns only `gio::Cancellable` (async cancellation plumbing) and an "Edit cancelled" message; there is no `Cancel` variant in the `Opt` enum.
  - `crates/cli/src/main.rs:15` — `bootc_lib::cli::run_from_iter(std::env::args())` — thin CLI wrapper delegating to the library.

- **Verdict:** ⚠️ CORRECT with corrections — wiki previously listed a non-existent `cancel` command and omitted `edit`/`usr-overlay`/`loader-entries`.
- **Fix needed:** Remove `cancel`; add `edit`, `usr-overlay`, `loader-entries` (applied to wiki).

## Claim 3: Multi-backend storage with OSTree and composefs support
- **Wiki says:** "bootc supports two storage backends: OSTree (default) and composefs (experimental). The unified storage model spans three content stores: containers-storage, composefs object store, and ostree bare repo, sharing blocks via reflink."

- **Source evidence:**
  - `crates/lib/src/store/mod.rs:1-20` — "The [`Storage`] type holds references to three different types of storage that together implement the unified storage model." Documents the three-store architecture: bootc-owned containers-storage, composefs object store, and ostree bare repo with `FICLONE` ioctl for block sharing.
  - `crates/lib/src/lib.rs:13-14` — Module `deploy` covers both OSTree and composefs deployment paths.
  - `crates/lib/src/lib.rs:42,66` — Module `bootc_composefs` is described as "Composefs backend implementation (experimental)".
  - `crates/lib/src/deploy.rs:1-30` — Comments document three pull paths: Unified + reflinks, Non-unified + reflinks, and No reflinks (ext4) using `pull_via_composefs_unified`, `pull_via_composefs`, and legacy `ostree_container::store::ImageImporter`.
  - `Justfile:38-39` — `variant := env("BOOTC_variant", "ostree")` and `bootloader := env("BOOTC_bootloader", "grub")` — Build system supports both ostree and composefs variants.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: System installation modes: to-disk, to-filesystem, to-existing-root, reset
- **Wiki says:** "bootc install writes a container image to a block device in a bootable way. Supports `to-disk` (full partitioning via Discoverable Partitions Specification), `to-filesystem` (using externally-prepared filesystems), `to-existing-root` (install alongside the running host root), and `reset` (nondestructive reinstall inside an existing bootc system)."

- **Source evidence:**
  - `crates/lib/src/cli.rs:290-343` — `enum InstallOpts` with variants: `ToDisk` (:302, `InstallToDiskOpts`), `ToFilesystem` (:309, `InstallToFilesystemOpts`), `ToExistingRoot` (:316, `InstallToExistingRootOpts`), `Reset` (:322, `InstallResetOpts`, hidden), `Finalize` (:326), `EnsureCompletion` (:337), `PrintConfiguration` (:343, outputs merged install config as JSON).
  - `crates/lib/src/cli.rs:2111-2120` — Dispatch arms: `install_to_disk`, `install_to_filesystem`, `install_to_existing_root`, `install_reset`, `print_configuration`.
  - `crates/lib/src/install.rs:1-35` — Module doc: "Writing a container to a block device in a bootable way". Lists steps: preparing environment, setting up storage (partitioning or using external filesystems), deploying the image, installing bootloader (bootupd/systemd-boot/zipl), finalizing.
  - `crates/lib/src/install.rs:15-35` — Documents `to-disk`: "Creates a complete bootable system on a block device" with ESP, BIOS boot partition, Boot partition, and Root partition using Discoverable Partitions Specification.
  - `crates/lib/src/install.rs:31-35` — Documents `to-filesystem`: uses externally-prepared filesystems (RAID, LVM, LUKS).
  - `crates/lib/src/podman.rs:9` — `pub(crate) const CONTAINER_STORAGE: &str = "/var/lib/containers"` — Runtime storage path for `bootc install`.

- **Verdict:** ⚠️ PARTIAL — wiki previously mentioned only `to-disk` (and verify page only `to-disk` + `to-filesystem`).
- **Fix needed:** Add `to-existing-root` and `reset` modes (applied to wiki).

## Claim 5: Bootloader management with GRUB, systemd-boot, and UKI support
- **Wiki says:** "bootc manages bootloader configuration across GRUB, systemd-boot, and UKI (Unified Kernel Image) formats, with support for SecureBoot keys and kernel argument management."

- **Source evidence:**
  - `crates/lib/src/lib.rs:24` — Module `bootloader` — "Bootloader configuration (GRUB, systemd-boot, UKI)"
  - `crates/lib/src/bootloader.rs:1-30` — Implements `mount_esp_part`, constants for `EFI_DIR`, `BOOTUPD_UPDATES`, `SYSTEMD_KEY_DIR`. Handles ESP partition mounting for bootloader cleanup and reinstallation.
  - `crates/lib/src/bootloader.rs:42-48` — `const KERNEL_INSTALL_CONF_ROOT: &str = "/tmp"` — bootctl integration workaround for systemd's path handling.
  - `crates/lib/src/bootloader.rs:50` — `const BOOTCTL_RANDOM_SEED_MIN_VERSION: u32 = 257` — systemd-boot version awareness.
  - `crates/lib/src/bootloader.rs:54-68` — `mount_esp_part` function: "Mount the first ESP found among backing devices at /boot/efi."
  - `crates/lib/src/bootloader.rs:20` — References `bootc_composefs::boot::SecurebootKeys` — SecureBoot key management for signed UKI.
  - `crates/lib/src/lib.rs:26` — Module `bootc_kargs` — "Kernel argument management"
  - `Justfile:39` — `bootloader := env("BOOTC_bootloader", "grub")` — build time bootloader selection.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Systemd service units for fetch-apply-updates, finalize-staged, and status
- **Wiki says:** "bootc ships systemd units for scheduled update fetching (`bootc-fetch-apply-updates.{service,timer}`), staged finalization (`bootc-finalize-staged.service`), status tracking (`bootc-status-updated.path`), destructive cleanup, and more."

- **Source evidence:**
  - `systemd/bootc-fetch-apply-updates.service` — Service unit for fetch-and-apply update operations
  - `systemd/bootc-fetch-apply-updates.timer` — Timer unit for scheduled update fetching
  - `systemd/bootc-finalize-staged.service` — Finalizes staged deployments on next boot
  - `systemd/bootc-status-updated.path` — Path unit monitoring status changes
  - `systemd/bootc-status-updated.target` — Target for status-updated completion
  - `systemd/bootc-status-updated-onboot.target` — Boot-time status trigger target
  - `systemd/bootc-destructive-cleanup.service` — Cleanup of previous deployments
  - `systemd/bootc-publish-rhsm-facts.service` — RHSM fact publishing integration
  - `systemd/bootc-sysusers-shadow-sync.service` — Sysusers/shadow password sync
  - Plus 1 embedded unit: `crates/lib/src/generator.rs:21` — `TRANSIENT_RELABEL_UNIT = "bootc-early-overlay-relabel.service"`, generated from `crates/lib/src/units/bootc-early-overlay-relabel.service` (:245).

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Multi-architecture build system with Justfile and Makefile
- **Wiki says:** "bootc's build system uses a Justfile layered on top of podman and make, supporting multiple architectures, container-based builds, composefs variants, and CI integration."

- **Source evidence:**
  - `Justfile:1-12` — "The default entrypoint to working on this project." Layering: Github Actions → Justfile → podman → make → rustc (line 8-10).
  - `Justfile:31-35` — Image name variables: `base_img := "localhost/bootc"`, `upgrade_img`, `upgrade_source_img`
  - `Justfile:38-49` — Build variant configuration: `variant := env("BOOTC_variant", "ostree")`, `bootloader := env("BOOTC_bootloader", "grub")`, `base := env("BOOTC_base", "quay.io/centos-bootc/centos-bootc:stream10")`
  - `Justfile:50-545` — Includes composefs, sealed UKI, test-tmt, and CI targets
  - `Makefile` — Present as lower-level build target for test and package workflows
  - `Cargo.toml:15-31` — Multiple Rust profiles: `release`, `thin` (size-optimized), `releaselto` (full LTO)
  - `ci/` — CI configuration directory
  - `bcvk.just` — Submodule justfile for bootc-variant-kernel workflows
  - `renovate.json` — Dependency update automation

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Additional Claim: 13 crates in the Rust workspace
- **Wiki says:** "The project ships as a Rust workspace (`crates/*`) with 13 crates."

- **Source evidence:**
  - `crates/` directory contains exactly 13 crates: `blockdev`, `cli`, `etc-merge`, `initramfs`, `lib`, `mount`, `ostree-ext`, `system-reinstall-bootc`, `sysusers`, `tests-integration`, `tmpfiles`, `utils`, `xtask`.
  - `Cargo.toml:1-3` — Workspace `members = ["crates/*"]` glob covers all 13.

- **Verdict:** ⚠️ CORRECTED — previously stated 14 crates and listed only 7.
- **Fix needed:** Count corrected to 13 with full crate list (applied to wiki).

## Summary

All claims from the bootc wiki have been verified against the source code:
- ✅ **Transactional OCI updates:** README and crate docs confirm the container-native approach
- ⚠️ **CLI subcommands:** corrected — `cancel` does not exist; `edit`, `usr-overlay`, `loader-entries` added
- ✅ **Multi-backend storage:** Three-store architecture documented with OSTree + composefs support
- ⚠️ **System installation:** expanded from `to-disk` only to `to-disk`/`to-filesystem`/`to-existing-root`/`reset`
- ✅ **Bootloader management:** GRUB, systemd-boot, UKI handling with SecureBoot and kernel args
- ✅ **Systemd units:** 9 unit files confirmed in `systemd/` + 1 embedded relabel unit
- ✅ **Build system:** Justfile + Makefile + Cargo layered build with multi-variant support
- ⚠️ **Crates:** corrected from 14 to 13 with full listing

## Related

- [[bootc]] -- Main wiki entry
- [[podman]] -- Container runtime
- [[coreos-assembler]] -- Fedora CoreOS build system
- [[tank-os]] -- Fedora bootc appliance for OpenClaw

## Cross-project

- [[buildah.codegraph-verify]] -- OCI image builder used by bootc builds
- [[podman.codegraph-verify]] -- Container runtime support
- [[tank-os.codegraph-verify]] -- Bootc-based deployment appliance
