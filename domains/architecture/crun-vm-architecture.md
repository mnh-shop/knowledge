---
name: crun-vm-architecture
tags: [architecture, bootc, cli, container, container-runtime, crun-vm, docker, oci-runtime, podman, qemu, quadlet, rust, security, systemd, virtualization, vm]
description: crun-vm Architecture
source: sources/crun-vm/
---

# crun-vm Architecture

**Source:** `sources/crun-vm/`
**Raw:** `raw/crun-vm/crun-vm.xml` (140K)
**Codegraph:** `graphs/crun-vm/` (848K)

**Version**: 0.3.0  
**Language**: Rust  
**License**: GPL-2.0-or-later  
**Source**: https://github.com/containers/crun-vm

---

## Overview

crun-vm is an OCI runtime that acts as a thin shim between the OCI runtime protocol and QEMU/libvirt. It intercepts the `create` and `exec` OCI commands from Podman, Docker, or CRI-O/Kubernetes, while delegating all other commands (`start`, `state`, `kill`, `delete`) to `crun` -- the standard OCI runtime from the containers project.

crun-vm is NOT a full runtime. It is a preprocessor that modifies the OCI `config.json` before passing control to `crun` (the real OCI runtime). The binary intercepts at the `liboci-cli` level, handling `create` and `exec` itself while forwarding everything else to `crun`.

---

## Key Source Files

| File | Purpose |
|------|---------|
| `src/main.rs` | Entry point, delegates to `crun_vm::main` |
| `src/lib.rs` | Command dispatch: create, delete, exec implemented; start/state/kill forwarded to crun; others rejected |
| `src/commands/create/mod.rs` | 818 lines -- the bulk of the logic: 12 setup functions called in sequence |
| `src/commands/create/domain.rs` | Libvirt XML generation (307 lines) |
| `src/commands/create/first_boot.rs` | cloud-init/Ignition config generation (470 lines) |
| `src/commands/create/custom_opts.rs` | CLI option parser for crun-vm-specific flags |
| `src/commands/create/engine.rs` | Engine detection (Podman/Docker/Kubernetes) |
| `src/commands/exec.rs` | Exec command implementation |
| `src/commands/delete.rs` | Cleanup of crun-vm mounts |
| `src/util.rs` | Utilities: SELinux, bind/overlay mounts, VM image info, crun delegation |
| `embed/entrypoint.sh` | Container entrypoint (113 lines) |
| `embed/exec.sh` | SSH-based exec into VM (67 lines) |
| `embed/virtiofsd.sh` | virtiofsd wrapper (7 lines) |
| `embed/bootc/prepare.sh` | bootc VM image generation (140 lines) |
| `embed/bootc/entrypoint.sh` | bootc install helper (56 lines) |
| `embed/bootc/config.json` | OCI config for krun-based bootc-install container |
| `Cargo.toml` | Dependencies: liboci-cli, oci-spec, clap, minidom, serde, rust-embed, nix, regex |

---

## OCI Lifecycle Mapping

### Commands Handled by crun-vm

**create** -- FULLY CUSTOM. Intercepted by crun-vm. Does NOT call crun's create. Instead, modifies the OCI spec extensively (new container root, embedded entrypoint, VM image mounts, SSH keys, domain XML, first-boot config, security changes), then delegates only the final container creation step to `crun` using the modified spec. For bootc containers, additionally spawns an async bootc-install process via `krun`.

**exec** -- MODIFIED then delegated. crun-vm intercepts to rewrite the exec process config: if `--container` flag is NOT set, replaces the command with a call to `/crun-vm/exec.sh <timeout> <user> <original_command>` -- which uses SSH to connect into the VM. Also fixes SELinux labels. Then delegates actual exec to `crun`.

**delete** -- WRAPPED. First calls `crun` to actually delete the container, then cleans up crun-vm-specific mounts: the .ssh overlay mount, the VM image overlay mount, and the image directory bind mount.

**start** -- DELEGATED to `crun` with no modification.
**state** -- DELEGATED to `crun`.
**kill** -- DELEGATED to `crun`.

### Commands NOT Implemented

Returns "Unknown command" error: `run`, `checkpoint`, `events`, `features`, `list`, `pause`, `ps`, `resume`, `update`, `spec`.

---

## Create Flow (12 Steps)

When `crun-vm create` is called, the following sequence runs:

1. **Parse OCI spec** (`config.json`) from the bundle path
2. **Detect container engine** (Podman/Docker/Kubernetes) via heuristics
3. **Extract crun-vm-specific options** from the process args
4. **Detect if the image is a bootc bootable container** (`/usr/lib/bootc/install` exists)
5. **Set up new container root** with a custom entrypoint (`entrypoint.sh`)
6. **Configure VM image binding** (overlay or persistent)
7. **Set up mounts** -- directories become virtiofs, files/block devices become virtio-blk
8. **Generate a libvirt domain XML** for QEMU
9. **Configure cloud-init/Ignition** for first-boot (SSH keys, passwords, mount config)
10. **Adjust security** (SELinux labels, capabilities, seccomp)
11. **Hand off to `crun`** to actually create the container
12. **For bootc containers**, spawn an async `bootc/prepare.sh` via `krun` to generate the VM image

---

## QEMU / Libvirt Configuration (domain.rs)

### Domain Type
- Default: `type="kvm"` (hardware-accelerated)
- With `--emulated`: `type="qemu"` (software emulation, no KVM required)

### CPU / Memory
- CPU mode: `host-passthrough` with `mode="maximum"` -- passes host CPU features directly
- vCPU count: from OCI spec's `linux.resources.cpu.quota/period` ratio (rounded up), or host CPU count via `num_cpus` crate
- Memory: from OCI spec's `linux.resources.memory.limit`, or defaults to 2 GiB (2^31 bytes)
- CPU pinning: respects `linux.resources.cpu.cpus` for cpuset

### Firmware / OS
- `os firmware="efi"` -- always uses UEFI firmware
- Secure boot explicitly disabled: `<feature enabled="no" name="secure-boot"/>`
- Machine type: `q35` for x86/x86_64, libvirt default for other architectures

### Features
- ACPI enabled (required for fw_cfg)
- FW_CFG sysinfo for Ignition config: `opt/com.coreos/config`

### Memory Backing (when virtiofs mounts exist)
- `<source type="memfd"/>` -- anonymous memory file descriptor for shared memory
- `<access mode="shared"/>` -- required for virtiofsd shared file system

### Disks
1. **Primary disk (VM image)**: `type="file" device="disk"` with virtio-blk. Driver: `qemu` with format from `qemu-img info`. Source file from `/crun-vm/image/image` (or overlay for non-persistent mode).
2. **Block device mounts**: Each block device or regular file passed via `--device`/`--volume`/`--blockdev` becomes a virtio-blk disk, serial number `crun-vm-block-{i}` for stable device identification in the guest.
3. **Cloud-init ISO**: Points at `/crun-vm/first-boot/cloud-init.iso` with `volid cidata`.

### Networking
- Single interface: `<interface type="user">` with `backend type="passt"` and `model type="virtio"`
- Port forwarding: passt handles TCP and UDP via `<portForward proto="tcp">` and `<portForward proto="udp">`
- No filterref, no bridge, no macvtap

### Serial Console
- `<serial type="pty">` and `<console type="pty">` -- allows `virsh console` access

### Virtio-fs (Directory Mounts)
- For each directory bind mount from the container, creates a `<filesystem type="mount">` entry
- Driver type: `virtiofs`, binary path: `/crun-vm/virtiofsd.sh`
- Sandbox mode: `chroot`

### XML Overlay Merge
- Supports merging overlay XML files via `--merge-libvirt-xml <file>` (multiple allowed)
- Uses minidom to merge child elements by name

---

## Networking Architecture

crun-vm uses **passt** (Plug A Simple Socket Transport) for all VM networking. Passt is a userspace network proxy that translates between the host's network stack and the VM's virtual NIC, with zero configuration.

### Implementation
- `<interface type="user">` with `<backend type="passt">` and `<model type="virtio">`
- TCP and UDP port forwarding: `<portForward proto="tcp">` and `<portForward proto="udp">`
- Port forwarding works via Podman/Docker's standard `-p`/`--publish` flag

### Rootless Interaction
- When running under rootless Podman, passt connects through the Podman network namespace stack
- Passt runs as user nobody in passt's sandbox when under real root, requiring workaround: creating `/run/libvirt/qemu/passt` with `chmod o+w` (done in entrypoint.sh)
- Passt uses `--sandbox=chroot` which requires `CAP_SYS_CHROOT` -- automatically added by crun-vm

### Seccomp Interaction
- Docker's default seccomp profile blocks `mount`, `pivot_root`, `umount2`, `unshare` -- all required by passt
- crun-vm patches the seccomp profile to `SCMP_ACT_ALLOW` these syscalls
- A TODO comment notes: "This doesn't seem reasonable at all"

### Limitations
- No host networking (`--network host`)
- No macvlan passthrough
- Only passt backend (no SLiRP, no tap, no bridge)
- Passt is inherently slower than macvtap/virtio-net with vhost

---

## bootc (Bootable Container) Support

bootc support converts OCI container images that package a full OS (via `bootc install`) into bootable VM disk images.

### Detection
- Checks if `/usr/lib/bootc/install` exists as a directory inside the container image's root
- Only supported with Podman and Docker engines (not Kubernetes)
- Flagged incompatible with `--emulated` mode (no KVM)

### Async VM Image Generation (prepare.sh)
1. Creates a named pipe (`mkfifo bootc_dir/progress`) -- entrypoint.sh blocks reading from this pipe
2. Gets `image_name` and `image_id` from container engine via inspect
3. Default disk size: 2x the container image's virtual size, rounded up to 1 MiB alignment; configurable via `--bootc-disk-size`
4. Checks for cached VM image via container labels (`crun-vm.from=<image_id>`, `crun-vm.size=<disk_size>`)
5. Cache hit: creates temporary container from cached image, exports, extracts `image.qcow2`
6. Cache miss: saves container image as docker-archive, adjusts krun config, runs `krun run` to launch a sandboxed container that calls the bootc-install helper
7. After krun completes successfully (`bootc-install-success` file exists), converts raw image to qcow2
8. Caches the qcow2 as a new containerdisk
9. Removes raw image, creates `success` sentinel file, closes named pipe

### bootc Install Helper (inside krun)
1. Monkey-patches `udevadm` to also run `partx --add /dev/loop0` -- because bootc's `udevadm settle` hangs without systemd
2. Writes default xfs root filesystem config if bootc install config directory is empty
3. Converts docker-archive to oci-archive via `skopeo copy`
4. Runs: `bootc install to-disk --source-imgref oci-archive:... --target-imgref ... --skip-fetch-check --generic-image --via-loopback --karg console=tty0 --karg console=ttyS0 /output/image.raw`
5. Creates `bootc-install-success` sentinel on success

### Persistent Overlay Mode
- When `--persistent` is set with `--rootfs`, the overlay is writable (upperdir at the image's parent)
- When NOT persistent: a qcow2 overlay image is created providing copy-on-write semantics

### Limitations
- bootc caching labels rely on container engine metadata
- Image generation is slow (involves full `bootc install to-disk` pipeline)
- Caching keyed by both image ID and disk size -- any change invalidates cache

---

## Exec Mechanism

When `podman exec` (or `docker exec`) is called:

1. crun-vm intercepts the OCI exec command
2. Parses the exec process config JSON (contains the command to run)
3. `build_command()` handles:
   - `--` prefix stripping (Podman inconsistency workaround)
   - crun-vm-specific exec options: `--as <user>` (default: root), `--container` (exec into container, not VM), `--timeout <secs>`
   - If `--container` flag is set: passes the original command through to `crun` unchanged
   - Otherwise: replaces the command with `/crun-vm/exec.sh <timeout> <user> <original_command>`
4. Fixes SELinux label (container_init_t -> container_t)
5. Delegates to `crun` which actually spawns the process in the container

### exec.sh (SSH Exec into VM)
1. Defines `__ssh()` helper: `ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -l <user> localhost <command>`
2. First-time connection retry loop:
   - Retries SSH repeatedly until success or timeout
   - Ignores transient errors: "Connection closed", "Connection refused", "Connection reset by peer", "System is booting up"
   - Respects timeout from `--timeout` flag; exits with code 255 on timeout
   - On success or SSH key failure: creates `ssh-successful` sentinel and continues
3. After first successful connection: runs the actual SSH command directly with `-o LogLevel=ERROR`

### SSH Key Setup (in create)
- Generates an SSH key pair via `ssh-keygen -q -f <dir>/id_rsa -N "" -C ""`
- Public key injected into cloud-init `ssh_authorized_keys` and `/root/.ssh/authorized_keys`
- Optionally uses host user's SSH key pair via overlay bind mount

---

## Security Architecture

### Privileged Container Rejection
- `ensure_unprivileged()` checks for `CAP_SYS_ADMIN` in ALL capability sets
- Returns error: "crun-vm is incompatible with privileged containers"

### SELinux
- `fix_selinux_label()` maps `container_init_t` to `container_t` SELinux labels
- `bind_mount_dir_with_different_context()` uses overlayfs with `context=` mount option
- `set_file_context()` wraps `lsetfilecon()` to set SELinux context
- Links against `libselinux`

### Capabilities
- `CAP_SYS_CHROOT` is automatically inserted into all capability sets -- required for passt's `--sandbox=chroot`
- A TODO comment questions whether users should configure this explicitly

### Seccomp Relaxation
- Docker's default seccomp profile blocks `mount`, `pivot_root`, `umount2`, `unshare`
- `linux_seccomp_syscalls_push_front()` inserts a new rule at position 0 to `SCMP_ACT_ALLOW` these 4 syscalls
- A TODO comment expresses concern about this approach

### Resource Management
- Container CPU and memory resource limits are intentionally cleared -- the QEMU process uses resources directly without cgroup restrictions
- RLIMIT_NOFILE forced to 262144 (hard and soft)
- KVM device is bind-mounted from host (`/dev/kvm`) and added to cgroup device whitelist
- VFIO devices from `/dev/vfio/` are also auto-discovered and added

### Rootless Operation
- Designed to work with rootless Podman
- `MNT_DETACH` unmount in delete ensures clean teardown without requiring root

---

## VM Lifecycle (Inside the Container)

The entrypoint script (`entrypoint.sh`) runs on container start:

1. Remove stale locks (`/var/lock`)
2. Create directories for libvirt
3. Configure `qemu.conf` (disable owner/dynamic_ownership, set user=root, disable cgroups)
4. Start `virtlogd --daemon`
5. Start `virtqemud --daemon` (or `libvirtd --daemon` for older versions)
6. Create passt PID directory with o+w permissions
7. For bootc containers: wait on named pipe for async image generation, then move image into place
8. Define libvirt domain from `/crun-vm/domain.xml` (virsh define)
9. Start VM with console attached (`virsh start domain --console`)
10. On SIGTERM: send `virsh shutdown domain`, wait for "shut off" state with retry

Key insight: crun-vm does NOT manage VM lifecycle directly. It creates a container that runs libvirtd + QEMU, and the VM lifecycle IS the container lifecycle. When the container is stopped, entrypoint.sh's SIGTERM handler gracefully shuts down the VM via `virsh shutdown`.

---

## Requirements

### Hardware
- **KVM-capable CPU** (hardware virtualization support) -- REQUIRED. `/dev/kvm` must exist and be accessible
- **Sufficient RAM**: VM gets at least 2 GiB by default, plus host overhead for QEMU, libvirtd, and the OCI container runtime (~1-2 GB additional)
- **Disk space**: VM image size depends on the containerdisk or bootc image
- **No macOS support**: requires `/dev/kvm` which is only available on Linux

### Software
- **Linux host** -- crun-vm is Linux-only
- **crun** -- the standard OCI runtime (required for start/state/kill/delete delegation)
- **crun-krun** -- for bootc container support
- **QEMU system emulator** (`qemu-system-x86_64`, `qemu-system-aarch64`, etc.)
- **qemu-img** -- for VM image info and overlay creation
- **libvirtd** or **virtqemud** -- the libvirt daemon for managing QEMU domains
- **virsh** -- libvirt CLI tool for domain operations
- **virtlogd** -- libvirt logging daemon
- **passt** -- userspace network proxy for VM networking
- **virtiofsd** -- virtio-fs shared filesystem daemon
- **genisoimage** -- for generating cloud-init ISO images
- **SSH** -- for exec-ing into VMs
- **skopeo** -- for bootc container image conversion
- **bash, coreutils, grep, util-linux** -- standard Linux utilities
- **libselinux** -- SELinux support

### Supported Container Engines
- **Podman** -- auto-detected, best support
- **Docker** -- supported with manual runtime configuration
- **CRI-O / Kubernetes** -- supported with RuntimeClass configuration

### Supported Architectures
- x86_64 (uses q35 machine type)
- aarch64 (uses libvirt default machine type)
- Others via libvirt defaults

---

## Limitations

### Deployment Model
- Bare-metal dedicated servers only (needs `/dev/kvm` with hardware passthrough)
- NOT compatible with Hetzner CX, DigitalOcean Droplets, or any budget VPS (no nested virt)
- Cannot run on macOS, Windows, or non-Linux hosts

### Performance
- **Slow startup**: 5-30 seconds for VM boot (vs. <1s for regular containers)
- **High memory overhead**: QEMU + libvirtd + virtiofsd + passt adds ~1-2 GB of baseline overhead
- **Passt networking overhead**: user-mode networking is slower than kernel-level vhost/virtio-net

### OCI Lifecycle Gaps
- Does NOT implement: `run`, `checkpoint`, `events`, `features`, `list`, `pause`, `ps`, `resume`, `update`, `spec`
- No checkpoint/restore (CRIU integration)
- No pause/resume support

### Networking
- No host networking mode (`--network host`)
- No macvlan passthrough
- Only passt backend

### Virtualization
- Single VM per container
- Only UEFI firmware (no legacy BIOS boot)
- Secure boot is explicitly disabled
- No live migration, no snapshot support
- No multi-monitor, no GPU passthrough out of the box

### Security Concerns (Noted as TODOs)
- Seccomp relaxation for passt is a blunt approach
- `CAP_SYS_CHROOT` is forced on all containers
- Symlink vulnerability noted in first_boot.rs
- Engine detection is heuristic-based, not secure

### Kubernetes
- Only works with CRI-O (not containerd)
- `--rootfs` is not supported (Podman-only feature)

### bootc
- Slow initial boot
- Only works with Podman and Docker (not Kubernetes)
- No `--emulated` mode support (requires KVM for krun)
- Caching is simple label-based

---

## Deployment Role

crun-vm fills the gap between "containers are lightweight but share the host kernel" and "VMs are isolated but heavy with their own management tooling." It lets operators deploy VMs using the same container-native workflows (Podman, Docker, Kubernetes, systemd Quadlet) they already use for containers.

### Use Cases
1. Running full OS environments when a container's kernel-sharing model is insufficient
2. Running bootc images as ephemeral VMs for testing bootable container images locally
3. Isolating legacy workloads that require a specific kernel or init system
4. Single-VM services managed identically to container services via systemd Quadlet

### Comparison with Alternatives
- **KubeVirt**: More featureful (live migration, snapshot, GPU passthrough), but requires significant infrastructure. crun-vm is simpler but far less capable.
- **QEMU/libvirt directly**: No container integration. crun-vm provides a thin layer that makes QEMU VMs look like OCI containers.
- **Firecracker / microVMs**: Faster boot, lower overhead, but limited device support. crun-vm provides full QEMU virtio device model.

## Related

- [[crun-vm]] -- Wiki overview of crun-vm
- [[crun-vm-deployment]] -- Deployment and operations guide
