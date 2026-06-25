---
name: crun-vm-deployment
tags: [crun-vm, deployment, rust, qemu, oci-runtime, vm, container-runtime, container, security, automation, acp, ai-llm, ansible, bootc, cli, docker, git, monitoring, quadlet, storage, systemd, terraform, virtualization]
description: crun-vm Deployment Guide
---

# crun-vm Deployment Guide

**Source:** `sources/crun-vm/`
**Raw:** `raw/crun-vm/crun-vm.xml` (140K)
**Codegraph:** `graphs/crun-vm/` (848K)

Comprehensive deployment and operations guide for crun-vm -- an OCI runtime shim that runs QEMU/KVM virtual machines as OCI containers.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Container Engine Integration](#container-engine-integration)
- [Container Images](#container-images)
- [OCI Spec Annotations](#oci-spec-annotations)
- [Networking](#networking)
- [Storage](#storage)
- [First-Boot Configuration](#first-boot-configuration)
- [Security Considerations](#security-considerations)
- [Performance Considerations](#performance-considerations)
- [macOS Development Workflow](#macos-development-workflow)
- [Troubleshooting](#troubleshooting)
- [Key Source Files](#key-source-files)

---

## System Requirements

### Hardware

| Requirement | Details | Notes |
|-------------|---------|-------|
| **KVM-capable CPU** | `/dev/kvm` must exist and be accessible | Hardware virtualization extensions required (Intel VT-x / AMD-V) |
| **RAM** | Minimum 4 GB total | VM gets 2 GiB by default + ~1-2 GB host overhead (QEMU + libvirtd + passt + virtiofsd) |
| **Disk** | Variable | VM image size depends on containerdisk or bootc image |
| **Architecture** | x86_64 (primary), aarch64 (supported) | x86_64 uses q35 machine type |
| **Nested virtualization** | Required for cloud VM deployment | GCE N2 with `--enable-nested-virtualization`, AWS bare metal, or Hetzner AX series |

### Kernel Requirements

| Requirement | Minimum | Notes |
|-------------|---------|-------|
| **Linux kernel** | 5.x | User namespaces, KVM device support |
| **User namespaces** | CONFIG_USER_NS=y | Required for rootless Podman operation |
| **KVM modules** | kvm + kvm_intel/kvm_amd | Verify with `lsmod | grep kvm` |

### Software Dependencies

```bash
# Fedora / RHEL
sudo dnf install crun crun-vm qemu-system-x86 qemu-img libvirt-daemon \
  libvirt-client virt-manager passt virtiofsd genisoimage openssh skopeo \
  libselinux-utils util-linux

# Debian / Ubuntu (build from source; no package available)
sudo apt install rustc cargo libselinux-dev qemu-system-x86 qemu-utils \
  libvirt-daemon-system libvirt-clients passt virtiofsd genisoimage \
  openssh-client skopeo coreutils

# Verify KVM access
ls -l /dev/kvm
test -r /dev/kvm && echo "KVM accessible" || echo "KVM not accessible"
grep -E '(vmx|svm)' /proc/cpuinfo
```

### Environments That Are NOT Supported

| Environment | Reason |
|-------------|--------|
| macOS | No `/dev/kvm`; HVF on Apple Silicon not supported by crun-vm |
| Budget VPS (Hetzner CX, DigitalOcean Droplets) | No nested virtualization / no `/dev/kvm` passthrough |
| Windows | Not supported |
| Containerd with runc | Only CRI-O is supported for Kubernetes; containerd is NOT supported |

---

## Installation

### Install via Package Manager

Fedora (primary distribution target):

```bash
sudo dnf install crun-vm
```

Other distributions may have crun-vm in community repos. Check your distribution's package manager.

### Build from Source

```bash
# Prerequisites for building
sudo dnf install -y rust cargo gcc

# Clone and build
git clone https://github.com/containers/crun-vm.git
cd crun-vm
cargo build --release

# Install the binary
sudo install -m 755 target/release/crun-vm /usr/local/bin/

# Verify
crun-vm --help
```

The binary is compiled with the Rust standard library statically linked. No Rust toolchain is needed at runtime.

### Runtime Dependencies on the Host

The following must be installed on the container host (they are NOT bundled by crun-vm):

| Binary | Package (Fedora) | Purpose |
|--------|------------------|---------|
| `crun` | `crun` | OCI runtime for lifecycle delegation |
| `qemu-system-x86_64` | `qemu-system-x86` | QEMU system emulator |
| `qemu-img` | `qemu-img` | VM image inspection and overlay creation |
| `libvirtd` / `virtqemud` | `libvirt-daemon` | Libvirt daemon |
| `virsh` | `libvirt-client` | Libvirt CLI |
| `virtlogd` | `libvirt-daemon` | Libvirt logging daemon |
| `passt` | `passt` | Userspace network proxy |
| `virtiofsd` | `virtiofsd` | virtio-fs shared filesystem daemon |
| `genisoimage` | `genisoimage` | cloud-init ISO generation |
| `ssh` | `openssh` | SSH for exec into VMs |
| `skopeo` | `skopeo` | Container image conversion (bootc) |
| `krun` | `crun-krun` | bootc-install sandbox (bootc only) |

### Post-Install Validation

```bash
# Verify the binary works
crun-vm --help

# Verify crun is available
which crun && crun --version

# Verify KVM
test -r /dev/kvm && echo "KVM ready"

# Quick test with a small image
podman run --runtime crun-vm --rm -it quay.io/containerdisks/fedora:40 echo "VM booted"
```

---

## Container Engine Integration

### Podman (Best Support)

Podman has the best crun-vm support. Register it as a runtime in `~/.config/containers/containers.conf` (rootless) or `/etc/containers/containers.conf` (rootful):

```ini
[engine.runtimes]
crun-vm = ["/usr/local/bin/crun-vm"]
```

Or pass it explicitly per-run:

```bash
# Basic: run a regular containerdisk image as a VM
podman run --runtime crun-vm --rm -it quay.io/containerdisks/fedora:40

# With port forwarding
podman run --runtime crun-vm --rm -it -p 2222:22 quay.io/containerdisks/fedora:40

# With directory mount (becomes virtiofs inside VM)
podman run --runtime crun-vm --rm -it -v /host/path:/vm/mount quay.io/containerdisks/fedora:40

# Run a bootc container as a bootable VM
podman run --runtime crun-vm --rm -it ghcr.io/tank-os/tank-os:latest

# Software emulation mode (no KVM required, much slower)
podman run --runtime crun-vm --emulated --rm -it quay.io/containerdisks/fedora:40

# Persistent mode (writable VM state survives restarts)
podman run --runtime crun-vm --rootfs /var/lib/crun-vm/my-vm --persistent --rm -it \
  quay.io/containerdisks/fedora:40

# With custom annotations
podman run --runtime crun-vm --annotation custom.boot.containers/machine-type="pc" \
  --rm -it quay.io/containerdisks/fedora:40
```

### Docker

Register the runtime in `/etc/docker/daemon.json`:

```json
{
  "runtimes": {
    "crun-vm": {
      "path": "/usr/local/bin/crun-vm"
    }
  }
}
```

Then restart Docker and use:

```bash
sudo systemctl restart docker
docker run --runtime crun-vm --rm -it quay.io/containerdisks/fedora:40
```

**Docker caveats:**
- Docker's default seccomp profile blocks syscalls required by passt (`mount`, `pivot_root`, `umount2`, `unshare`). crun-vm patches the seccomp profile to `SCMP_ACT_ALLOW` these syscalls (noted in source as a security concern).
- Docker's `--privileged` flag is explicitly rejected by crun-vm.
- Docker does not support rootless operation with custom runtimes as well as Podman.

### CRI-O / Kubernetes

CRI-O supports crun-vm via a RuntimeClass configuration.

**CRI-O configuration** at `/etc/crio/crio.conf.d/99-crun-vm.conf`:

```toml
[crio.runtime.runtimes.crun-vm]
runtime_path = "/usr/local/bin/crun-vm"
runtime_type = "oci"
```

**RuntimeClass definition**:

```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: crun-vm
handler: crun-vm
```

**Pod spec**:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: vm-pod
spec:
  runtimeClassName: crun-vm
  containers:
  - name: vm
    image: quay.io/containerdisks/fedora:40
```

**Kubernetes / CRI-O limitations:**
- Only CRI-O is supported. Containerd is NOT supported.
- `--rootfs` / persistent mode is NOT available in Kubernetes (Podman-only feature).
- bootc containers are NOT supported in Kubernetes (Podman/Docker only).
- Resource limits from the Pod spec are cleared -- QEMU uses host resources directly.

---

## Container Images

### Regular OCI Images (Containerdisks)

Standard VM disk images packaged as OCI container images:

| Source | Examples |
|--------|----------|
| **quay.io/containerdisks/** | fedora, ubuntu, alpine, debian, arch, centos-stream |
| **quay.io/tinkerbell/** | OSIE, Hook |
| Custom images | Any image containing a bootable disk image |

How it works (non-bootc mode):
1. crun-vm detects the VM disk image from the container image layers
2. Creates a qcow2 overlay for copy-on-write (or uses persistent mode)
3. Attaches the overlay as a virtio-blk disk to the QEMU VM
4. Emulates UEFI boot from the disk

### bootc Images (Bootable Containers)

Images that package a full OS using the `bootc` specification:

| Source | Examples |
|--------|----------|
| **quay.io/fedora/fedora-bootc** | Fedora 40, 41 |
| **ghcr.io/tank-os/tank-os** | Fedora-based agent appliance |

Detection: crun-vm checks for `/usr/lib/bootc/install` inside the container image. When detected:
1. Spawns an async bootc-install pipeline via `krun` during `create`
2. The pipeline converts the OCI image to a VM disk image using `bootc install to-disk`
3. The generated VM disk becomes the VM's main storage
4. On `--persistent` mode, the overlay is writable

**bootc restrictions:**
- Requires Podman or Docker (NOT Kubernetes / CRI-O)
- Requires KVM passthrough (incompatible with `--emulated` mode)
- Initial boot is significantly slower (30-120 seconds for bootc-install)
- Cached images reuse generated disks via label-based caching

### Containerfile Requirements

There is **no special base image requirement**. Any OCI image can be used as input. The container image does NOT need to include QEMU, libvirt, or any virtualization software -- crun-vm provides these via its embedded entrypoint and configuration.

The container image provides:
1. The VM disk image (extracted from layers for non-bootc images)
2. The bootc install tooling (for bootc images)
3. The operating system environment inside the VM

---

## OCI Spec Annotations

crun-vm supports custom OCI annotations to override VM configuration:

### Podman Annotations

```bash
# Machine type override (default: q35 for x86_64, libvirt default for others)
podman run --annotation custom.boot.containers/machine-type="pc" --runtime crun-vm ...

# Passt extra arguments
podman run --annotation custom.boot.containers/passt-args="--log-file /tmp/passt.log" \
  --runtime crun-vm ...

# Bootc disk size override (default: 2x image virtual size)
podman run --annotation custom.boot.containers/bootc-disk-size="20G" \
  --runtime crun-vm ...

# Merge additional libvirt XML
podman run --annotation custom.boot.containers/merge-libvirt-xml="/path/to/overlay.xml" \
  --runtime crun-vm ...
```

### Annotation Reference

| Annotation Key | Type | Default | Description |
|----------------|------|---------|-------------|
| `custom.boot.containers/passt-args` | string | (empty) | Extra command-line arguments passed to passt |
| `custom.boot.containers/machine-type` | string | `q35` (x86_64) | Libvirt machine type override (e.g. `pc`, `q35`) |
| `custom.boot.containers/bootc-disk-size` | string | auto (2x image) | Disk size for bootc VM images (e.g. `20G`, `40G`) |
| `custom.boot.containers/merge-libvirt-xml` | string | (empty) | Path to libvirt XML overlay file to merge |

### Docker / Kubernetes Annotations

Docker:

```bash
docker run --annotation custom.boot.containers/machine-type="q35" --runtime crun-vm ...
```

Kubernetes (in Pod metadata):

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: vm-pod
  annotations:
    custom.boot.containers/machine-type: "q35"
    custom.boot.containers/bootc-disk-size: "20G"
spec:
  runtimeClassName: crun-vm
  containers:
  - name: vm
    image: quay.io/containerdisks/fedora:40
```

---

## Networking

### Architecture

```
Host network → Container netns → passt → QEMU virtio-net → VM
```

crun-vm uses **passt** (Plug A Simple Transport Socket) for all VM networking. Passt is a userspace network proxy that translates between the container's network namespace and the VM's virtio NIC, with zero configuration.

### Port Forwarding

Uses the container engine's standard publish flag:

```bash
# TCP
podman run --runtime crun-vm --rm -it -p 2222:22 quay.io/containerdisks/fedora:40

# UDP
podman run --runtime crun-vm --rm -it -p 53:53/udp quay.io/containerdisks/fedora:40

# Multiple ports
podman run --runtime crun-vm --rm -it -p 8080:80 -p 2222:22 quay.io/containerdisks/fedora:40

# Range
podman run --runtime crun-vm --rm -it -p 8000-8010:8000-8010 quay.io/containerdisks/fedora:40
```

The container engine creates iptables rules. Passt reads these rules and forwards traffic into the VM's virtio-net interface.

### Rootless Interaction

- Under rootless Podman, passt connects through Podman's network namespace stack
- When under real root, passt runs as user nobody; crun-vm's entrypoint creates `/run/libvirt/qemu/passt` with `chmod o+w` to work around permission issues
- Passt uses `--sandbox=chroot` which requires `CAP_SYS_CHROOT` -- crun-vm adds this capability automatically

### Networking Limitations

| Limitation | Detail |
|------------|--------|
| **No host networking** | `--network host` is NOT supported with crun-vm |
| **No macvlan / ipvlan passthrough** | Only passt user-mode networking |
| **No SLiRP** | passt is the only backend |
| **Passt overhead** | User-mode networking is slower than kernel-level vhost/virtio-net |

### --emulated Mode

For environments without KVM acceleration (testing, CI):

```bash
podman run --runtime crun-vm --emulated --rm -it quay.io/containerdisks/fedora:40
```

Changes the QEMU domain type from `kvm` to `qemu` (TCG software emulation):

| Aspect | Default (KVM) | `--emulated` |
|--------|---------------|--------------|
| Speed | Near-native | ~10-100x slower |
| `/dev/kvm` | Required | Not required |
| bootc images | Supported | NOT supported (needs KVM for krun) |
| CPU features | host-passthrough | Emulated generic CPU |
| Use case | Production | Testing, CI, development |

---

## Storage

### Overlay Mode (Default)

By default, crun-vm creates a qcow2 overlay image providing copy-on-write semantics:

```
VM base image (read-only, from container image)
    ↓
qcow2 overlay (writeable, discarded on container delete)
```

The overlay is discarded when the container is deleted (`podman rm` or `podman run --rm`).

### Persistent Mode

Use `--rootfs` + `--persistent` to make changes survive container restarts:

```bash
# First run: initialize the persistent state directory
podman run --runtime crun-vm --rootfs /var/lib/crun-vm/my-vm --persistent --rm -it \
  quay.io/containerdisks/fedora:40

# Subsequent runs: reuse the same persistent storage
podman run --runtime crun-vm --rootfs /var/lib/crun-vm/my-vm --rm -it \
  quay.io/containerdisks/fedora:40
```

The `--rootfs` directory stores:
- The qcow2 overlay (image upper directory)
- SSH keys (`/root/.ssh/authorized_keys`)
- The libvirt domain XML (`domain.xml`)
- cloud-init/Ignition configuration (`first-boot/`)

### Directory Mounts (virtiofs)

Container volume mounts become virtiofs shared filesystems inside the VM:

```bash
podman run --runtime crun-vm --rm -it \
  -v /host/project:/mnt/project \
  quay.io/containerdisks/fedora:40
```

Each mount:
1. Gets a virtiofs filesystem entry in the libvirt domain XML
2. Uses `/usr/libexec/virtiofsd` (via embedded wrapper script)
3. Sandbox mode: chroot
4. Inside the VM, the mount appears as a virtio-fs filesystem

### Block Device Mounts (virtio-blk)

Block devices or regular files become virtio-blk disks:

```bash
# Mount a raw disk image
podman run --runtime crun-vm --device /dev/sdb quay.io/containerdisks/fedora:40

# Mount a regular file as a disk
podman run --runtime crun-vm --rm -it -v /path/to/disk.qcow2:/dev/vdc \
  quay.io/containerdisks/fedora:40
```

Block devices get serial number `crun-vm-block-{i}` for stable identification via udev rules in the guest.

### Disk Layout Inside the VM

| Device | Content | Type |
|--------|---------|------|
| `/dev/vda` | Primary VM disk | virtio-blk, qcow2 or raw |
| `/dev/vdb` | Cloud-init ISO | virtio-blk, ISO 9660 with `volid cidata` |
| `/dev/vdc`, `/dev/vdd`, ... | Block device mounts | virtio-blk, serial `crun-vm-block-N` |

---

## First-Boot Configuration

crun-vm generates cloud-init (or Ignition) configuration automatically during the `create` phase.

### Cloud-init (Standard)

Generated by `src/commands/create/first_boot.rs` and written to a cloud-init ISO:

- **SSH key injection**: A fresh SSH key pair is generated during `create`. The public key is injected via `ssh_authorized_keys`.
- **Root password**: Can be set via the OCI spec process args.
- **Custom user data**: Written to the cloud-init ISO at `/crun-vm/first-boot/cloud-init.iso`.
- **Mount configuration**: virtiofs mount entries for shared directories.

When running rootless Podman in the host user namespace, the host user's existing SSH key is mounted via overlay bind mount instead of generating a new one.

### Ignition (CoreOS variants)

When the container disk is detected as a Fedora CoreOS or RHEL CoreOS variant, crun-vm uses Ignition instead:

- Config is written to fw_cfg: `opt/com.coreos/config`
- Ignition config sets up SSH keys, users, storage, and systemd units
- Requires ACPI to be enabled (default)

### Exec via SSH

Once the VM is booted, `podman exec` works by SSH-ing into the VM:

```bash
# Exec into the VM (SSH-based, default)
podman exec -it <container> sh

# Exec into the container shell (NOT the VM)
podman exec -it --container <container> sh

# Exec as a specific user
podman exec -it --as admin <container> sh

# With a custom timeout for first connection
podman exec --timeout 60 <container> sh
```

The first SSH connection retries until the VM is booted (up to the timeout). The retry loop ignores transient errors: "Connection closed", "Connection refused", "Connection reset by peer", "System is booting up".

---

## Security Considerations

### Privileged Container Rejection

crun-vm explicitly rejects `--privileged` containers. Code path `ensure_unprivileged()` checks for `CAP_SYS_ADMIN` in ALL capability sets and returns:

> "crun-vm is incompatible with privileged containers"

### Capabilities Required

| Capability | Required By | Added By |
|------------|-------------|----------|
| `CAP_SYS_ADMIN` | libvirtd to manage QEMU | Must be present in OCI spec (for libvirtd) |
| `CAP_SYS_CHROOT` | passt's `--sandbox=chroot` | crun-vm auto-inserts into all capability sets |
| `CAP_NET_ADMIN` | passt network configuration | crun-vm (if not already present) |

### SELinux

- `fix_selinux_label()` maps `container_init_t` → `container_t` SELinux labels
- `bind_mount_dir_with_different_context()` uses overlayfs with `context=` mount option
- `set_file_context()` wraps `lsetfilecon()` for SELinux context setting
- Links against `libselinux`

On SELinux-enabled systems:

```bash
# Verify SELinux context on KVM device
ls -Z /dev/kvm

# Allow container use of KVM device
sudo setsebool -P container_use_devices on

# Use :Z flag on volume mounts for proper labeling
podman run --runtime crun-vm -v /host/data:/data:Z quay.io/containerdisks/fedora:40
```

### Seccomp (Docker Only)

crun-vm patches the Docker seccomp profile to allow syscalls required by passt:

| Syscall | Why passt needs it |
|---------|-------------------|
| `mount` | Namespace setup |
| `pivot_root` | Chroot sandbox |
| `umount2` | Namespace cleanup |
| `unshare` | Network namespace creation |

**Known security concern** (noted as a TODO in source): "This doesn't seem reasonable at all."

### Resource Controls

- Container CPU and memory resource limits are **intentionally cleared** -- QEMU uses host resources directly without cgroup restrictions
- `RLIMIT_NOFILE` forced to 262144 (hard and soft) -- required for QEMU
- KVM device (`/dev/kvm`) is bind-mounted from host and added to cgroup device whitelist
- VFIO devices from `/dev/vfio/` are auto-discovered and added

### Rootless Security

- Designed to work with rootless Podman
- `MNT_DETACH` unmount in `delete` ensures clean teardown without requiring root
- User namespaces isolate container from host privileges

---

## Performance Considerations

### Startup Time

| Operation | Regular Container | crun-vm VM |
|-----------|------------------|------------|
| Container start | < 100 ms | 5-30 seconds |
| Exec into container | < 50 ms | 1-5 seconds (SSH handshake) |
| bootc initial boot | N/A | 30-120 seconds (bootc-install) |

Boot time depends on:
- Guest OS boot speed (kernel + init system)
- QEMU initialization (UEFI firmware, device emulation)
- libvirtd startup inside the container
- For bootc: bootc-install pipeline (async during create)

### Memory Overhead

| Component | Estimated RAM |
|-----------|--------------|
| Guest OS (Fedora) | 512 MB - 1 GB |
| QEMU process | 200-500 MB |
| libvirtd + virtlogd | 50-100 MB |
| passt | ~10 MB |
| virtiofsd (per mount) | ~10-20 MB each |
| **Total baseline overhead** | **~1-2 GB** |

### CPU Allocation

- vCPU count: from OCI spec's `linux.resources.cpu.quota/period` ratio (rounded up), or host CPU count
- CPU pinning: respects `linux.resources.cpu.cpus` for cpuset
- Default: all host CPUs
- CPU mode: `host-passthrough` with `mode="maximum"` -- passes host CPU features directly

### Memory Allocation

- From OCI spec's `linux.resources.memory.limit`
- Default: 2 GiB (2^31 bytes)
- QEMU uses memory directly -- no cgroup restriction
- Overcommit: guest memory can exceed physical RAM

### General Guidelines

| Scenario | Recommendation |
|----------|---------------|
| CI testing | Use `--emulated` to avoid KVM requirement; expect 10x slower boots |
| Development | Pre-pull images, use rootless Podman |
| Production | Dedicated server with KVM passthrough, persistent mode |
| bootc workflows | Allow 2-5 minutes for initial create (bootc-install) |
| Multiple VMs | Each VM has independent ~1-2 GB overhead -- plan RAM accordingly |

---

## macOS Development Workflow

crun-vm does NOT run on macOS directly (requires `/dev/kvm`). Use **Podman Machine** to run a Linux VM on macOS that provides KVM for crun-vm:

### Setup

```bash
# Install Podman
brew install podman

# Create a Linux VM (adjust resources as needed)
podman machine init --cpus 4 --memory 8192 --disk-size 50

# Start the machine
podman machine start

# SSH into the machine to install crun-vm dependencies
podman machine ssh
sudo dnf install -y crun crun-vm qemu-system-x86 qemu-kvm libvirt-daemon \
  libvirt-client passt genisoimage qemu-img
exit
```

### Workflow

```bash
# From macOS host, all Podman commands run inside the machine VM
podman run --runtime crun-vm --rm -it quay.io/containerdisks/fedora:40

# Port forwarding works transparently
podman run --runtime crun-vm --rm -it -p 2222:22 quay.io/containerdisks/fedora:40
```

### Known macOS Caveats

- macOS needs Podman Machine 5.0+ for full rootless user namespace support
- File sharing between macOS host and crun-vm VM is a double hop: macOS host → Podman Machine (via virtiofs) → crun-vm VM (via virtiofs) -- noticeably slow
- Performance is intended for testing only, not production
- Apple Silicon (M1/M2/M3) hosts use `virtio` machine type for Podman Machine, not q35

---

## Troubleshooting

### KVM Passthrough Issues

**Symptom:** `Failed to find /dev/kvm` or `Could not access KVM kernel module`

```bash
# Check KVM availability
ls -l /dev/kvm
test -r /dev/kvm && echo "accessible" || echo "not accessible"

# Load kernel modules
sudo modprobe kvm
sudo modprobe kvm_intel   # or kvm_amd

# Verify CPU virtualization extensions
grep -E '(vmx|svm)' /proc/cpuinfo

# Check user belongs to kvm group (for rootless)
groups
sudo usermod -aG kvm $USER
# Log out and back in for group changes to take effect
```

### Permission Errors

**Symptom:** Permission denied on `/dev/kvm` or libvirt operations

```bash
# Fix KVM device permissions
sudo chmod 666 /dev/kvm

# Fix SELinux
sudo setsebool -P container_use_devices on

# Check passt PID directory
podman exec <container> ls -la /run/libvirt/qemu/
```

### libvirtd Startup Failure

**Symptom:** Container starts but VM never boots

```bash
# Check libvirtd logs inside the container
podman exec <container> journalctl -u libvirtd --no-pager

# Manually start libvirtd
podman exec <container> virtqemud --daemon

# Define and start the domain
podman exec <container> virsh define /crun-vm/domain.xml
podman exec <container> virsh start domain --console

# Check domain state
podman exec <container> virsh list
```

### SSH Exec Failures

**Symptom:** `podman exec` hangs or returns "Connection refused"

```bash
# Check if VM is booted
podman exec <container> virsh list

# Check console output
podman logs <container>

# Test SSH directly
podman exec <container> ssh -o StrictHostKeyChecking=no \
  -o UserKnownHostsFile=/dev/null -l root localhost whoami

# Increase exec timeout for slow-booting images
podman exec --timeout 120 <container> whoami

# Check SSH key setup
podman exec <container> ls -la /crun-vm/.ssh/
```

### Network Issues

**Symptom:** No network inside VM, port forwarding not working

```bash
# Check passt is running
podman exec <container> pgrep -a passt

# Verify port forwarding in domain XML
podman exec <container> virsh dumpxml domain | grep -A5 '<portForward'

# Check container network
podman exec <container> ip addr
podman exec <container> ping -c 1 8.8.8.8
```

### bootc Image Issues

**Symptom:** bootc container hangs during create

```bash
# Verify image contains bootc tools
podman run --rm <image> ls /usr/lib/bootc/

# Increase disk size for large images
podman run --annotation custom.boot.containers/bootc-disk-size="40G" \
  --runtime crun-vm --rm -it <bootc-image>

# Verify krun is available
which krun

# bootc is incompatible with --emulated mode -- ensure -e is not set
```

### Slow Boot Times

| Cause | Solution |
|-------|----------|
| Pre-pull image | `podman pull quay.io/containerdisks/fedora:40` beforehand |
| Using `--emulated` | Remove for production -- use real KVM |
| bootc initial boot | First boot is inherently slow; subsequent boots use cached image |
| Frequent restarts | Use `--persistent` mode to reuse state |
| Insufficient RAM | Increase host memory available to the VM |

### Cleanup

```bash
# Graceful shutdown
podman stop <container>

# Force kill
podman kill <container>

# Delete and clean up mounts
podman rm <container>
```

On delete, crun-vm: calls `crun` to delete the container, then unmounts crun-vm-specific mounts (.ssh overlay, VM image overlay, image directory bind mount). The entrypoint's SIGTERM handler gracefully shuts down the VM via `virsh shutdown`.

### Logs and Monitoring

```bash
# VM console output (virsh start --console runs in foreground of entrypoint.sh)
podman logs <container>

# Follow logs
podman logs -f <container>

# Attach to running VM console
podman attach <container>

# Inside container: libvirtd logs
podman exec <container> journalctl -u libvirtd --no-pager -n 50
```

---

## Key Source Files

| File | Purpose |
|------|---------|
| `src/commands/create/mod.rs` | 12-step create flow (818 lines) |
| `src/commands/create/domain.rs` | Libvirt XML generation (307 lines) |
| `src/commands/create/first_boot.rs` | cloud-init/Ignition config (470 lines) |
| `src/commands/create/custom_opts.rs` | CLI option parser for crun-vm-specific flags |
| `src/commands/create/engine.rs` | Engine detection (Podman/Docker/Kubernetes) |
| `src/commands/exec.rs` | SSH-based exec into VM |
| `src/commands/delete.rs` | Cleanup of crun-vm mounts |
| `src/util.rs` | SELinux, bind/overlay mounts, VM image info, crun delegation |
| `embed/entrypoint.sh` | Container entrypoint (libvirtd start, domain define, shutdown handler) |
| `embed/exec.sh` | SSH exec helper with retry loop |
| `embed/virtiofsd.sh` | virtiofsd wrapper script |
| `embed/bootc/prepare.sh` | bootc VM image generation (140 lines) |
| `embed/bootc/entrypoint.sh` | bootc install helper (56 lines) |

---

## Related

- [[crun-vm-architecture]] -- Full architecture reference
- [[crun-vm]] -- Wiki entry

---

## Related

- [[domains/architecture/crun-vm-architecture.md]] -- Full architecture documentation
- [[wiki/crun-vm.md]] -- Wiki entry
- [[podman]] -- Container engine crun-vm integrates with
- [[tank-os]] -- Fedora bootc image deployable via crun-vm
- [[hermzner]] -- Alternative deployment approach (Terraform + Ansible, no crun-vm)
- [[buildah]] -- Building container images for crun-vm
- [[podlet]] -- Generating Quadlet files for crun-vm deployments
