---
name: crun-vm
tags: [bootc, container, crun-vm, docker, k8s, kubernetes, oci-runtime, podman, qemu, rust, systemd, vfio, virtualization, vm]
description: "crun-vm reference — OCI runtime shim running QEMU/KVM VMs as containers: command matrix, CPU/domain config, deployment modes, bootc pipeline, vfio, engine detection, env vars"
source: sources/crun-vm/
---

# crun-vm Reference

**Source:** `sources/crun-vm/`
**Wiki:** [[crun-vm]]
**Related:** [Deployment Guide](../deployment/crun-vm-deployment.md), [Architecture](../architecture/crun-vm-architecture.md)

crun-vm is an OCI runtime that runs QEMU/KVM virtual machines as OCI containers, so VMs are managed with the same tooling as containers (Podman, Docker, CRI-O). It is a **thin shim**: it intercepts `create`, rewrites the OCI `config.json` to describe a VM host, and delegates most lifecycle operations to the real OCI runtime `crun`.

**License:** GPL-2.0-or-later (`Cargo.toml:6`, `README.md:93`, `LICENSE:1`).

## Command Matrix

Dispatch in `src/lib.rs`:

| OCI Command | Behavior | Source |
|-------------|----------|--------|
| `create` | All the work: load config.json, engine detection, custom options, private dir, domain XML, first-boot config, SSH keys, spec rewrite, `crun create` | `mod.rs:32-100` |
| `start` | Passthrough to crun | `lib.rs:48-51` |
| `state` | Passthrough to crun | `lib.rs:48-51` |
| `kill` | Passthrough to crun (SIGTERM from engine → entrypoint trap → graceful `virsh shutdown`) | `lib.rs:48-51`, `embed/entrypoint.sh:110-111` |
| `exec` | Rewrites exec args → SSH into the VM via `/crun-vm/exec.sh` (flags `--as <user>` default root, `--container` for the container shell, `--timeout`) | `exec.rs:44-57`, `embed/exec.sh` |
| `delete` | `crun delete`, then unmounts crun-vm mounts (`.ssh`, image overlay) | `delete.rs:21-41` |
| `run` | **Rejected** | `lib.rs:61` |
| `checkpoint` | **Rejected** | `lib.rs:58` |
| `events` | **Rejected** | `lib.rs:59` |
| `pause` | **Rejected** | `lib.rs:64` |
| `ps` | **Rejected** | `lib.rs:65` |
| `resume` | **Rejected** | `lib.rs:66` |
| `update` | **Rejected** | `lib.rs:67` |
| `features` | **Rejected** | `lib.rs:60` |
| `list` | **Rejected** | `lib.rs:62` |
| `spec` | **Rejected** | `lib.rs:68` |

All 10 rejected commands hit the "not a command we support" branch in `lib.rs:57-69`.

## Domain Configuration (`src/commands/create/domain.rs`)

| Aspect | Value | Source line |
|--------|-------|-------------|
| Domain type | `kvm` (default) / `qemu` (`--emulated`) | 40-43 |
| **CPU mode** | **`<cpu mode="maximum">`** (maximum host CPU model — NOT host-passthrough) | 48 |
| Machine | `q35` (x86/x86_64), libvirt default otherwise | 62 |
| Firmware | EFI; secure-boot disabled | 66-73 |
| ACPI | Enabled (needed for fw_cfg + graceful shutdown) | 75 |
| Serial / console | Both PTY | 97-105 |
| vCPUs | `cpu.quota/period` rounded up, else host CPU count | 308-332 |
| Memory | `memory.limit` from OCI spec, default 2 GiB | 335-348 |
| Main disk | virtio-blk, driver `qemu`, format from image (qcow2) | 111-120 |
| Cloud-init ISO | Separate virtio-blk disk | 142-150 |
| Network | `type="user"` interface, passt backend, virtio model, TCP+UDP port forwarding | 153 |
| virtiofs | Per-mount `<filesystem type="mount">`, virtiofs driver, chroot sandbox via `/crun-vm/virtiofsd.sh` | 160-177 |
| Ignition | fw_cfg entry `opt/com.coreos/config` → `/crun-vm/first-boot/ignition.ign` | 80-86 |

## Inside the Container Image

The VM host environment lives **inside the container image**, not on the outer host. `embed/entrypoint.sh` (PID 1) runs: `virtlogd --daemon` → `virtqemud`/`libvirtd --daemon` → `virsh define /crun-vm/domain.xml` → `virsh start domain --console` in the background, trapping SIGTERM for graceful `virsh shutdown` (lines 33-41, 88-90, 110-111). `embed/virtiofsd.sh` wraps `/usr/libexec/virtiofsd --modcaps=-mknod:-setfcap`. So the image must ship QEMU, libvirt, passt, virtiofsd, genisoimage, ssh, and crun.

## Deployment Modes

### Podman / Docker (`docs/2-podman-docker.md`)

The primary path:

```bash
podman run --runtime crun-vm -it quay.io/containerdisks/fedora:40
podman exec -it --latest -- --as fedora sh
```

### systemd / Quadlet (`docs/3-systemd.md`)

VMs are defined as systemd services via Podman Quadlet — system containers and VMs share the same deployment tooling (`systemctl start/restart vm-foo`).

### Kubernetes / CRI-O (`docs/4-kubernetes.md`)

crun-vm acts as a `RuntimeClass` handler on CRI-O, running VMs as regular pods. Limitations: bootc containers are Podman/Docker-only; `--rootfs` persistent mode unavailable; Pod resource limits are cleared (QEMU uses host resources directly).

## Engine Detection

`Engine::detect()` (`engine.rs:27-106`) identifies the engine in order:

1. **Kubernetes** — mounts under `/var/run/secrets/kubernetes.io` or `/etc/hosts` starting with "Kubernetes-managed hosts file"
2. **Docker** — `.dockerenv` present in the container root
3. **Podman** — `/run/.containerenv` (or `/var/run/.containerenv`) mount + bundle path matching `/overlay-containers/<id>/userdata`

Unknown engines are rejected.

## bootc / krun Pipeline

Bootable containers are detected by `/usr/lib/bootc/install` (`mod.rs:158`):

1. `create` spawns `embed/bootc/prepare.sh` **asynchronously** — it blocks until the container entrypoint starts, then runs `bootc install` under **krun** (isolated sandbox) to build the VM disk image (`mod.rs:102-120`)
2. The generated disk becomes the VM's main storage; size overridable via `--bootc-disk-size` (`mod.rs:121,170-186`)
3. Restrictions: **Podman/Docker only** (`mod.rs:161-162`), **incompatible with `--emulated`** (`mod.rs:166`), requires KVM passthrough

## Options & Environment

| Option / Annotation | Purpose |
|---|---|
| `--merge-libvirt-xml <path>` | Merge a libvirt XML overlay into the generated domain (`custom_opts.rs:71`) — the hook for VFIO passthrough and domain customizations |
| `--print-libvirt-xml` | Print generated domain XML, exit (`mod.rs:254`) |
| `--print-config-json` | Print rewritten OCI config.json, exit (`mod.rs:256`) |
| `--bootc-disk-size <size>` | Disk size for bootc images (`mod.rs:121`) |
| `--rootfs <dir>` | Persistent mode — VM state survives restarts (qcow2 overlay, SSH keys, domain.xml, first-boot config) |
| `--cloud-init <file>` / `--ignition <file>` | User-provided first-boot config files (`custom_opts.rs`) |
| `CRUN_VM_EXEC_TIMEOUT` | Default for the exec SSH-connect timeout when `--timeout` not given (`exec.rs:72-75`) |
| `custom.boot.containers/machine-type`, `/passt-args` | Machine type and passt argument overrides |

## VFIO Passthrough

When a merged libvirt XML sets up VFIO devices, crun-vm auto-discovers char devices under `/dev/vfio/` and bind-mounts + adds them to the container (`mod.rs:655`), so the QEMU process can access them.

## Security Adjustments

- **CAP_SYS_CHROOT** inserted for passt's `--sandbox=chroot` (`mod.rs:666`)
- **Seccomp relaxation**: Docker's default profile blocks `mount`/`pivot_root`/`umount2`/`unshare`; crun-vm pushes `SCMP_ACT_ALLOW` for them, with a `TODO: This doesn't seem reasonable at all` (`mod.rs:674-691`)
- **RLIMIT_NOFILE** forced to 262144 hard+soft for passt socket fan-out (`mod.rs:782-817`)
- **CPU/memory cgroup limits cleared** — QEMU uses host resources directly (`mod.rs:811-816`)
- `/dev/kvm` required unless `--emulated`; bind-mounted + char-dev-added when present (`mod.rs:644-649`)

## Related

- [[crun-vm]] — Main wiki entry
- [Deployment Guide](../deployment/crun-vm-deployment.md) — full ops guide
- [Architecture](../architecture/crun-vm-architecture.md) — deep dive
- [[firecracker]] — Alternative microVM technology
- [[bootc]] — Bootable container standard
- [[podman]] — Primary container engine
