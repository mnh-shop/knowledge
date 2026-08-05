---
name: crun-vm-codegraph-verify
tags: [codegraph-verify, crun-vm, podman, oci, rust]
description: "Codegraph Verification: crun-vm"
source: sources/crun-vm/
---

# Codegraph Verification: crun-vm

**Date:** 2026-07-12

## Claim 1: Thin OCI runtime shim — create does the work, lifecycle ops delegate to crun
- **Wiki says:** crun-vm is a thin OCI runtime shim that rewrites config.json to set up a QEMU/KVM VM; `create` does the work, `start`/`state`/`kill` pass through to crun.

- **Source evidence:** `src/lib.rs:44-51` — `StandardCmd::Create` → `commands::create::create()`, `StandardCmd::Delete` → `commands::delete::delete()`, while `Start | State | Kill` → `crun(&raw_args)` ("not a command we implement ourselves, pass it on to crun"). `src/commands/create/mod.rs:32-100` — `create()` loads `config.json`, calls `Engine::detect()`, creates the private directory (`crun-vm-<id>`), rewrites the spec, saves it, and calls `crun(raw_args)` ("actually create container").

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Rejected commands — run/checkpoint/events/pause/ps/resume/update/features/list/spec
- **Wiki says:** `run`, `checkpoint`, `events`, `pause`, `ps`, `resume`, `update`, `features`, `list`, `spec` are all rejected (not implemented).

- **Source evidence:** `src/lib.rs:57-69` — `liboci_cli::CommonCmd::Checkpointt | Events | Features | List | Pause | Ps | Resume | Run | Update | Spec` all fall into the "not a command we support" branch → `bail!("Unknown command")`. Only `CommonCmd::Exec` (line 52) is implemented.

- **Verdict:** ✅ CORRECT (wiki previously listed only 7 of the 10; `features`, `list`, `spec` added)
- **Fix needed:** None

## Claim 3: Engine detection heuristics (Podman / Docker / Kubernetes)
- **Wiki says:** crun-vm auto-detects the container engine: Kubernetes via secrets mounts/managed `/etc/hosts`, Docker via `.dockerenv`, Podman via `.containerenv` + overlay bundle path.

- **Source evidence:** `src/commands/create/engine.rs:27-106` — `Engine::detect()` checks (1) mounts under `/var/run/secrets/kubernetes.io` or `/etc/hosts` containing "Kubernetes-managed hosts file" (lines 38-59), (2) `.dockerenv` in the original root (lines 64-73), (3) `/run/.containerenv` or `/var/run/.containerenv` plus bundle path matching `/overlay-containers/([^/]+)/userdata` (lines 77-100). Unknown → `bail!` (line 105-106).

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Libvirt domain XML — kvm default, `<cpu mode="maximum">`, q35, EFI secure-boot disabled, ACPI, PTY
- **Wiki says:** domain type `kvm` (or `qemu` with `--emulated`); CPU mode `maximum`; machine q35 (x86_64); EFI firmware with secure-boot disabled; ACPI enabled; PTY serial + console; vCPUs from CPU quota; memory from OCI limit default 2GiB.

- **Source evidence:** `src/commands/create/domain.rs:40-43` — domain type `"kvm"`/`"qemu"`; `domain.rs:48` — `se(w, "cpu", &[("mode", "maximum")])`; `domain.rs:62` — `("machine", "q35")` for x86/x86_64; `domain.rs:66-73` — `("firmware", "efi")` + `feature secure-boot enabled="no"`; `domain.rs:75` — `features` → `acpi`; `domain.rs:97-105` — serial and console both `type="pty"`; `domain.rs:308-332` — `get_vcpu_count()` from `cpu.quota()/period()` rounded up, else host CPU count; `domain.rs:335-348` — `get_memory_size()` from `memory.limit()`, default `2u64.pow(31)` (2 GiB).

- **Verdict:** ✅ CORRECT (wiki previously said "host-passthrough"; corrected to `mode="maximum"`)
- **Fix needed:** None

## Claim 5: Virtualization software lives INSIDE the container image (embedded entrypoint + wrapper scripts)
- **Wiki says:** QEMU, libvirt, passt, virtiofsd must exist inside the container image — crun-vm's embedded scripts launch them from the container root, not from the outer host.

- **Source evidence:** `embed/entrypoint.sh:33-41` — starts `virtlogd --daemon`, then `virtqemud --daemon` (fallback `libvirtd --daemon`); `embed/entrypoint.sh:88-90` — `virsh --connect "qemu+unix:///session"` defines `/crun-vm/domain.xml`; `embed/entrypoint.sh:110-111` — `virsh start domain --console` in background with a SIGTERM trap → graceful shutdown. `embed/virtiofsd.sh` — wrapper calling `/usr/libexec/virtiofsd --modcaps=-mknod:-setfcap`. All paths are container-root paths.

- **Verdict:** ✅ CORRECT (wiki previously said "installed on the container host"; corrected)
- **Fix needed:** None

## Claim 6: License is GPL-2.0-or-later
- **Wiki says:** crun-vm is released under GPL-2.0-or-later.

- **Source evidence:** `Cargo.toml:6` — `license = "GPL-2.0-or-later"`; `README.md:93` — "This project is released under the GPL 2.0 (or later) license."; `LICENSE:1` — "GNU GENERAL PUBLIC LICENSE / Version 2, June 1991".

- **Verdict:** ✅ CORRECT (wiki previously said Apache 2.0; corrected)
- **Fix needed:** None

## Claim 7: bootc support — `/usr/lib/bootc/install` detection, async prepare.sh, Podman/Docker only, not emulated
- **Wiki says:** bootc containers are detected by `/usr/lib/bootc/install`; an async `prepare.sh` builds the VM disk via krun; bootc requires Podman/Docker and KVM (no `--emulated`).

- **Source evidence:** `src/commands/create/mod.rs:158` — `is_bootc_container = original_root_path.join("usr/lib/bootc/install").is_dir()`; `mod.rs:161-162` — `ensure!(!is_bootc_container || engine == Podman || engine == Docker, "bootc containers are only supported with Podman and Docker")`; `mod.rs:166` — `ensure!(!is_bootc_container || !custom_options.emulated, "--emulated is incompatible with bootable containers")`; `mod.rs:102-120` — spawns `prepare.sh` asynchronously, "this process blocks until our container's entrypoint actually starts running"; `mod.rs:105` — krun used for the bootc-install sandbox (comment "run bootc-install under krun").

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: First-boot config, VFIO passthrough, seccomp/rlimit adjustments, exec timeout env
- **Wiki says:** cloud-init + Ignition first-boot config (fw_cfg `opt/com.coreos/config`); VFIO char devices auto-added; passt needs CAP_SYS_CHROOT plus seccomp relaxation for mount/pivot_root/umount2/unshare (marked TODO); RLIMIT_NOFILE forced to 262144; `CRUN_VM_EXEC_TIMEOUT` env default for exec.

- **Source evidence:** `src/commands/create/mod.rs:694-719` — `set_up_first_boot_config()` with `FirstBootConfig { hostname, container_public_key, password, mounts }`; `domain.rs:80-86` — fw_cfg entry `opt/com.coreos/config` → `/crun-vm/first-boot/ignition.ign`; `mod.rs:655` — `fs::read_dir("/dev/vfio")` adds bind mounts + char devices; `mod.rs:666` — inserts `Capability::SysChroot`; `mod.rs:674-691` — pushes seccomp `SCMP_ACT_ALLOW` for `mount`, `pivot_root`, `umount2`, `unshare` with "TODO: This doesn't seem reasonable at all"; `mod.rs:782-817` — `adjust_container_rlimits_and_resources()` sets `RLIMIT_NOFILE` hard+soft 262144 and clears CPU/memory cgroup resources; `src/commands/exec.rs:72-75` — `CRUN_VM_EXEC_TIMEOUT` env var parsed as the exec timeout default.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 8 claims from the crun-vm wiki verified against source:

- ✅ **Thin shim:** create rewrites the spec and delegates to crun; start/state/kill pass through (`src/lib.rs:44-51`)
- ✅ **Rejected commands:** full list of 10 confirmed (`src/lib.rs:57-69`)
- ✅ **Engine detection:** Kubernetes → Docker → Podman heuristics (`engine.rs:27-106`)
- ✅ **Domain XML:** kvm default, cpu `mode="maximum"`, q35, EFI secure-boot off, ACPI, PTY, quota-based vCPUs, 2GiB default memory (`domain.rs`)
- ✅ **Embedded tooling:** virtlogd/virtqemud/virsh/virtiofsd run from the container root (`embed/entrypoint.sh`, `embed/virtiofsd.sh`)
- ✅ **License:** GPL-2.0-or-later (`Cargo.toml:6`, `README.md:93`, `LICENSE:1`)
- ✅ **bootc pipeline:** detection, async prepare.sh, Podman/Docker-only, no emulation
- ✅ **Config/security extras:** first-boot config, VFIO, CAP_SYS_CHROOT + seccomp relaxation, rlimit 262144, exec timeout env

## Related

- [[crun-vm]] -- Main wiki entry
- [[podman]] -- Podman container engine
- [[sablier]] -- Scale-to-zero proxy
- [[podlet]] -- Quadlet file generation

## Cross-project

- [[podman.codegraph-verify]] -- Podman verification
- [[buildah.codegraph-verify]] -- Buildah verification
