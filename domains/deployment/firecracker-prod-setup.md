---
name: firecracker-prod-setup
tags: [cgroups, deployment, firecracker, jailer, kernel-policy, kvm, production, seccomp, security, virtualization, vmm]
description: "Firecracker production setup — jailer usage (cgroup v1/v2, chroot, netns, rlimits, capability drop), seccomp thread categories, kernel support policy, host hardening"
source: sources/firecracker/
---

# Firecracker Production Setup

**Source:** `sources/firecracker/`
**Wiki:** [[firecracker]]

Production Firecracker deployments follow a defense-in-depth model: jailer isolation, thread-category seccomp, minimal device model, and a hardened host. This doc covers the pieces needed to run microVMs safely in multi-tenant environments.

## The Jailer in Production

The jailer (`src/jailer/`) is a separate, statically-linked binary that sets up the isolation barrier **before** exec'ing Firecracker. Usage (`docs/jailer.md:14-30`):

```bash
jailer --id <id> --exec-file <firecracker> --uid <uid> --gid <gid> \
       [--cgroup-version 1|2] [--cgroup <file>=<value>] \
       [--parent-cgroup <path>] [--chroot-base-dir /srv/jailer] \
       [--netns <ns_path>] [--resource-limit <resource=value>] \
       [--new-pid-ns] -- <firecracker args...>
```

### What the jailer does

| Mechanism | Details | Source |
|-----------|---------|--------|
| **chroot** | Jails Firecracker under `<chroot-base-dir>/<exec_file_name>/<id>/root` | `src/jailer/src/chroot.rs` |
| **cgroups** | Creates a per-microVM cgroup named `<id>`; v1 **or** v2 hierarchy, **default v1** (`docs/jailer.md:39-42`); both hierarchy types handled in `cgroup.rs:46-127` | `src/jailer/src/cgroup.rs` |
| **Namespaces** | Joins a new PID namespace (`--new-pid-ns`) and/or an existing network namespace (`--netns`) | `src/jailer/src/env.rs` |
| **Privilege drop** | Switches to `--uid`/`--gid` before exec; README: "applies a cgroup/namespace isolation barrier and then drops privileges" (`README.md:129-131`) | `src/jailer/src/main.rs` |
| **rlimits** | `--resource-limit <resource=value>` bounds process resources | `src/jailer/src/resource_limits.rs` |

**The jailer does NOT apply seccomp.** There is no seccomp module in `src/jailer/src/` — seccomp is applied by the Firecracker process itself; capability dropping is the jailer's job.

### cgroup v1 vs v2

- `--cgroup-version 1` (default): creates the microVM cgroup within a v1 hierarchy; each controller is mounted per-hierarchy
- `--cgroup-version 2`: uses the unified hierarchy (e.g. `/sys/fs/cgroup/unified`); if no `--cgroup` params are given, the jailer moves the process to the existing `--parent-cgroup` instead of creating one (`docs/jailer.md:65-74`)

## Seccomp Levels (Thread Categories)

Seccomp filters are applied per **thread category**, not per capability. `src/firecracker/src/seccomp.rs:11-12`:

```rust
const THREAD_CATEGORIES: [&str; 3] = ["vmm", "api", "vcpu"];
```

Each category gets its own BPF program (`BpfThreadMap`, `seccomp.rs:26`), so the API thread, VMM thread, and vCPU threads each allow only the syscalls they legitimately need. Levels (`SeccompConfig`, `seccomp.rs:30-50`):

1. **Advanced** (default) — the most restrictive, generated filters
2. **Custom** — user-provided filter file via `--seccomp-filter`
3. **None** — `--no-seccomp` disables filtering entirely

Filters are compiled at build time by the `seccompiler` crate (`src/seccompiler/src/bin.rs`, wired as a build dependency in `src/firecracker/Cargo.toml:37-39`) and loaded at startup, so the runtime never compiles BPF.

## Kernel Support Policy

Firecracker is tightly coupled to both host and guest kernels. The officially supported, continuously-tested versions (`docs/kernel-policy.md:26-38`):

| Page size | Host kernels | Guest kernels |
|-----------|--------------|---------------|
| 4K | v5.10 (EOL 2024-01-31), v6.1 (EOL 2025-10-12), v6.18 (EOL 2028-05-28) | v5.10, v6.1 (EOL 2026-09-02), v6.18 (EOL 2028-06-01) |

Policy rules (`docs/kernel-policy.md:12-22`):

- A kernel version is supported for a **minimum of 2 years** once officially added
- **At least 2 major versions** are supported at any time; when a third is added, the oldest is deprecated
- Other versions may work but are not validated by the test suite — use at your own risk

Guest kernels are the Amazon Linux microVM kernels (`microvm-kernel-*` tags in the Amazon Linux linux repo), which may include Firecracker-specific backports.

## Host Hardening (`docs/prod-host-setup.md`)

The production host setup document is the reference for safe multi-tenant operation:

- **Seccomp**: Firecracker uses the most restrictive seccomp filters by default, limiting host syscalls to the required minimum
- **Kernel & microcode patching**: host and guest kernels and host microcode must be regularly patched per distribution security advisories (e.g. ALAS for Amazon Linux)
- **Jailer**: every microVM runs under the jailer's chroot/cgroup/namespace/privilege-drop barrier
- **Minimal device model**: no emulated BIOS/graphics, tiny guest-visible surface (`docs/design.md:75`)
- **MMDS auth**: if the metadata service is exposed, enable session-token authentication (`src/vmm/src/mmds/token.rs`)

The defense-in-depth stack is: **jailer + thread-category seccomp + cgroups + minimal device model + KVM isolation**.

## Build & Deploy

```bash
./tools/devtool build          # Docker-based build (tools/devtool:12-18)
build/cargo_target/x86_64-unknown-linux-musl/debug/firecracker
build/cargo_target/x86_64-unknown-linux-musl/debug/jailer
```

Test with `./tools/devtool test` — integration suite under `tests/integration_tests/` (functional, performance, security, style).

## Related

- [[firecracker]] — Main wiki entry
- [Devices](../virtualization/firecracker-devices.md) — the device model being isolated
- [Snapshotting](../virtualization/firecracker-snapshotting.md) — scale-out via pre-warmed snapshots
- [[seccomp]] — Seccomp security concept
- [[kvm]] — KVM virtualization technology
- [[crun-vm]] — OCI runtime that can drive Firecracker-style microVMs
