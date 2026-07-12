---
name: crun-vm-api
description: "crun-vm API surface — OCI runtime spec, QEMU integration, VM lifecycle, configuration"
source: sources/crun-vm/
tags: [crun-vm, api, oci, container]
---

# crun-vm — API Reference

crun-vm is an OCI runtime that runs containers as lightweight virtual machines using QEMU. It implements the OCI Runtime Specification, allowing container engines like Podman to launch VM-isolated workloads transparently. Its API surface is the OCI runtime contract: `state`, `create`, `start`, `stop`, `delete`, plus extended configuration via container annotations and config.json bindings.

## Key API Facts

| Feature | Detail |
|---------|--------|
| **Interface** | OCI Runtime Specification (`runtime-spec`) |
| **Binary** | `/usr/libexec/crun-vm/crun-vm` (installed as OCI runtime) |
| **Hypervisor** | QEMU microVM process per container |
| **Process model** | Container init runs inside QEMU guest via custom init |
| **Storage** | Rootfs mounted via 9p/virtio-fs |
| **Configuration** | Standard `config.json` + crun-vm-specific annotations |

## OCI Runtime Commands

crun-vm implements the standard OCI Runtime CLI:

| Command | Arguments | Description |
|---------|-----------|-------------|
| `state <container-id>` | — | Return container state JSON (created/running/stopped) |
| `create <container-id>` | `--bundle <path>` | Create a VM container from bundle directory |
| `start <container-id>` | — | Start the VM (boot QEMU) |
| `stop <container-id>` | `--timeout <seconds>` | Stop the VM gracefully (ACPI shutdown) |
| `delete <container-id>` | `--force` | Remove the VM container artifacts |
| `kill <container-id> <signal>` | — | Send signal to VM init process |
| `exec <container-id> <cmd>` | — | Execute command inside running VM |
| `list` | — | List all VM containers |

## QEMU Integration

Each container gets a dedicated QEMU microVM. Configuration is passed through `config.json` annotations:

| Annotation | Value | Effect |
|------------|-------|--------|
| `com.crun-vm.kernel` | Path | Linux kernel binary (required) |
| `com.crun-vm.initrd` | Path | Initramfs image |
| `com.crun-vm.cmdline` | String | Kernel command-line parameters |
| `com.crun-vm.memory` | String | Guest memory size (e.g., `"512M"`) |
| `com.crun-vm.cpus` | Integer | Number of vCPUs |
| `com.crun-vm.console` | `stdio`/`socket`/`none` | Console backend |
| `com.crun-vm.network` | JSON | Network device configuration |
| `com.crun-vm.rootfs` | Path | Root filesystem (9p/virtio-fs) |
| `com.crun-vm.firmware` | Path | UEFI firmware binary (optional) |

## State Lifecycle

```
created ──► running ──► stopped
   │                      │
   └────── delete ◄───────┘
```

- **created**: Bundle validated, QEMU ready but not started
- **running**: QEMU guest booted, container init running
- **stopped**: Guest shut down (ACPI or forced), QEMU exited

State is stored in `/run/containers/storage/` under the container ID, with JSON state files conforming to the OCI runtime spec.

## VM Configuration in config.json

Standard OCI `config.json` fields used by crun-vm:

```
{
  "ociVersion": "1.0.2",
  "root": { "path": "rootfs" },        // mounted via 9p/virtio-fs
  "process": {
    "args": ["/sbin/init"],              // guest init process
    "env": ["PATH=/usr/bin"],            // guest environment
    "terminal": true
  },
  "mounts": [
    { "destination": "/proc", "type": "proc" },
    { "destination": "/sys",  "type": "sysfs" }
  ],
  "annotations": {
    "com.crun-vm.kernel":  "/path/to/vmlinuz",
    "com.crun-vm.memory":  "512M",
    "com.crun-vm.cpus":    "2"
  }
}
```

## Integration with Container Engines

crun-vm is registered as an OCI runtime in container engine configuration:

```toml
# /usr/share/containers/containers.conf
[runtime]
default = "crun-vm"
```

```bash
# Podman usage
podman run --runtime crun-vm --rm alpine:latest echo "hello from VM"
```

Podman, Buildah, and other OCI-compatible engines launch crun-vm transparently when configured as the runtime.

## Authentication

crun-vm has no built-in authentication. It is invoked as root (or via sudo) by the container engine. Security boundaries:

- **Root requirement**: `/run/containers/storage/` ownership, KVM device access
- **KVM group**: Operator must be in the `kvm` group for `/dev/kvm` access
- **No network API**: crun-vm is a CLI binary, not a network daemon

## Usage

```bash
# Manual OCI lifecycle (without container engine)
crun-vm create my-vm --bundle /path/to/bundle
crun-vm start my-vm
crun-vm exec my-vm /bin/sh
crun-vm stop my-vm --timeout 10
crun-vm delete my-vm
```

## Related

- [[crun-vm]] — Source repository and wiki
- [[podman]] — Primary container engine that uses crun-vm
- [[sablier]] — Time-based container lifecycle (can integrate with VM runtimes)
- [[podlet]] — Quadlet generator (runtime-agnostic, can target crun-vm)
