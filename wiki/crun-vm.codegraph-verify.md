---
name: crun-vm-codegraph-verify
tags: [codegraph-verify, crun-vm, podman, oci, rust]
description: "Codegraph Verification: crun-vm"
source: sources/crun-vm/
---

# Codegraph Verification: crun-vm

**Date:** 2026-07-12

## Claim 1: OCI runtime shim that runs VM images as containers
- **Wiki says:** crun-vm is an OCI Runtime that enables Podman, Docker, and Kubernetes to run QEMU-compatible Virtual Machine (VM) images instead of regular container processes.

- **Source evidence:** `README.md` lines 2-4 state: "crun-vm is an OCI Runtime that enables Podman, Docker, and Kubernetes to run QEMU-compatible Virtual Machine (VM) images." The `Cargo.toml` shows dependencies on `oci-spec` (runtime spec) and `liboci-cli` (OCI CLI interface). `src/lib.rs` lines 12-21 implement the OCI CLI: `liboci_cli::StandardCmd` handles `Create`, `Delete`, `Start`, `State`, `Kill`; `liboci_cli::CommonCmd` handles `Exec`. The `create` command sets up a VM image and generates a libvirt domain XML (`src/commands/create/domain.rs`).

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Detects and integrates with three container engines (Podman, Docker, Kubernetes)
- **Wiki says:** crun-vm auto-detects whether it is running under Podman, Docker, or Kubernetes and adapts its behavior accordingly.

- **Source evidence:** `src/commands/create/engine.rs` lines 12-16 define the `Engine` enum: `Podman`, `Docker`, `Kubernetes`. The `Engine::detect()` method (lines 27-106) autodetects by checking for: Kubernetes secrets mounts and managed `/etc/hosts` (line 38-59), `.dockerenv` file existence (line 64-73), and `.containerenv` file combined with overlay bundle path pattern (line 77-100). The `README.md` confirms support for all three engines, including examples with `podman run --runtime crun-vm` and `podman exec`.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Runs QEMU VMs via libvirt domain XML with KVM acceleration
- **Wiki says:** crun-vm generates libvirt domain XML to launch QEMU VM images, using KVM by default (falling back to emulated QEMU). It supports virtiofs mounts, disk passthrough, port forwarding via passt, and cloud-init/Ignition first-boot configuration.

- **Source evidence:** `src/commands/create/domain.rs` line 15-17 define `set_up_libvirt_domain_xml()` which generates domain XML. Lines 40-43 set the domain type to `kvm` by default or `qemu` for emulated mode. The XML generation includes: virtio-block disks for the VM image (line 111-120), additional block devices (122-140), virtiofs shared filesystem mounts (160-177), network via passt (152-158), cloud-init ISO (142-150), Ignition config via fw_cfg (78-86), and CPU/memory sizing from the container spec. Port forwarding uses passt (line 153), with a `rlmit_nofile` bump to 262144 (create/mod.rs lines 789-802) to support many passt connections.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Supports SSH exec into VMs (`podman exec --as <user>`)
- **Wiki says:** crun-vm allows `podman exec` to SSH into running VMs, supporting `--as` to specify the user and `--timeout` for connection limits.

- **Source evidence:** `src/commands/exec.rs` implements `exec()` (lines 13-41) which processes `liboci_cli::Exec` commands. It parses custom `ExecArgs` (lines 44-57) with `--as` (default "root"), `--container`, and `--timeout` flags. The `build_command()` function (lines 59-103) translates `podman exec` args into SSH commands, constructing: `ssh -p <port> -o StrictHostKeyChecking=no -i <key> <user>@<host> <cmd>`. The `README.md` example shows `podman exec -it --latest -- --as fedora` for exec access. An SSH key pair is generated during container creation (`create/mod.rs` lines 725-779) via `ssh-keygen`.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Supports bootable (bootc) containers as VM images
- **Wiki says:** crun-vm can run bootc (bootable container) images as VMs, installing them to a disk image on first boot via `bootc install`.

- **Source evidence:** `src/commands/create/mod.rs` lines 153-191 implement `is_bootc_container()` which checks for `/usr/lib/bootc/install` directory. Lines 289-295 handle bootc image setup differently: "the image will be generated later." Lines 100-127 on first create start an async `prepare.sh` process for bootc containers: `std::process::Command::new(bootc_dir.join("prepare.sh"))` spawns a background process that "blocks until our container's entrypoint actually starts running" (line 110-111). The `README.md` line 46-49 provides a bootc example: `podman run --runtime crun-vm -it quay.io/crun-vm/example-fedora-bootc:40`.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Cloud-init and Ignition first-boot configuration
- **Wiki says:** crun-vm supports passing cloud-init and Ignition configuration to VMs at first boot for hostname, SSH keys, password, and mount configuration.

- **Source evidence:** `src/commands/create/mod.rs` lines 690-719 implement `set_up_first_boot_config()` which creates both cloud-init and Ignition configs. `FirstBootConfig` (lines 695-701) carries `hostname`, `container_public_key`, `password`, and `mounts`. `apply_to_cloud_init_config()` generates a cloud-init ISO at `crun-vm/first-boot/cloud-init.iso`. `apply_to_ignition_config()` writes an Ignition file at `crun-vm/first-boot/ignition.ign`. Both are injected into the VM: Ignition via fw_cfg (domain.rs lines 78-86: `opt/com.coreos/config`), cloud-init as a virtio-block disk (domain.rs lines 142-150). `CustomOptions` (custom_opts.rs) includes `cloud_init: Option<PathBuf>` and `ignition: Option<PathBuf>` fields for user-provided config files.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Supports block device passthrough, directory mounting, and port forwarding
- **Wiki says:** crun-vm can pass block devices through to VMs, mount host directories into VMs via virtiofs, and forward ports from the host to VMs.

- **Source evidence:** `src/commands/create/mod.rs` handles all three: **Block devices** — `set_up_blockdevs()` (lines 544-588) processes `--blockdev` with source/target/format for block passthrough; `set_up_devices()` (lines 504-542) handles `--device` block devices. **Directory mounts** — `set_up_mounts()` (lines 408-501) converts bind mounts into virtiofs mounts: "path_in_container" and "path_in_guest" (lines 443-452). **Port forwarding** — domain.rs lines 152-158 configure the virtio-net interface with passt backend and TCP/UDP port forwarding, and `adjust_container_rlimits_and_resources()` (create/mod.rs:782-817) bumps `RLIMIT_NOFILE` to 262144 for passt.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Related

- [[crun-vm]] -- Main wiki entry
- [[podman]] -- Podman container engine
- [[sablier]] -- Scale-to-zero proxy
- [[podlet]] -- Quadlet file generation

## Cross-project

- [[podman.codegraph-verify]] -- Podman verification
- [[buildah.codegraph-verify]] -- Buildah verification
