---
name: firecracker-codegraph-verify
tags: [firecracker, codegraph-verify, vmm, virtualization, microvm, kvm, rust, aws, serverless]
description: "Codegraph Verification: firecracker — validating wiki claims against indexed source code"
source: sources/firecracker/
---

# Codegraph Verification: firecracker

**Date:** 2026-07-12

## Claim 1: Rust VMM by AWS powering Lambda/Fargate, minimal device model, <125ms boot

- **Wiki says:** "open-source VMM built by Amazon Web Services to power AWS Lambda and AWS Fargate" with a minimal device model and "<125ms" boot
- **Source evidence:**
  - `README.md:14-19` — "purpose-built for creating and managing secure, multi-tenant container and function-based services that provide serverless operational models"
  - `README.md:33-36` — "developed at Amazon Web Services to accelerate the speed and efficiency of services like AWS Lambda and AWS Fargate"
  - `src/firecracker/Cargo.toml:7` — "Firecracker enables you to deploy workloads in lightweight virtual machines, called microVMs..."
  - `SPECIFICATION.md:37` — "It takes `<= 125 ms` to go from receiving the Firecracker InstanceStart API call to the start of the Linux guest user-space `/sbin/init` process"
  - `FAQ.md:63` — minimal device model: "only 6 emulated devices are available: virtio-net, virtio-balloon, virtio-block, virtio-vsock, serial console, and a minimal keyboard controller"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: REST/HTTP control API via micro_http (OpenAPI) — no JSON-RPC

- **Wiki says:** API server `micro_http`; the control plane is a REST/HTTP API
- **Source evidence:**
  - `src/firecracker/swagger/firecracker.yaml:1-10` — `swagger: "2.0"`, "RESTful public-facing API. The API is accessible through HTTP calls on specific URLs carrying JSON modeled data. The transport medium is a Unix Domain Socket."
  - `src/vmm/Cargo.toml:40` — `micro_http = { git = "https://github.com/firecracker-microvm/micro-http" }`
  - `grep -ri jsonrpc src/ docs/` — **zero matches**: no JSON-RPC anywhere in the codebase
- **Verdict:** ✅ CORRECT (previously mislabeled JSON-RPC in wiki diagram; fixed)
- **Fix needed:** None (diagram corrected to `API -->|REST/HTTP JSON over UDS| VMM`)

## Claim 3: KVM via kvm-bindings/kvm-ioctls

- **Wiki says:** "Firecracker uses KVM ... via `kvm-bindings` and `kvm-ioctls` crates"
- **Source evidence:**
  - `src/vmm/Cargo.toml:36` — `kvm-bindings = { version = "0.14.0", features = ["fam-wrappers", "serde"] }`
  - `src/vmm/Cargo.toml:37` — `kvm-ioctls = "0.25.0"`
  - `src/vmm/src/vstate/kvm.rs:4` — `use kvm_bindings::KVM_API_VERSION;`
  - `src/vmm/src/vstate/kvm.rs:5` — `use kvm_ioctls::Kvm as KvmFd;`
  - `src/vmm/src/vstate/kvm.rs:29` — `let kvm_fd = KvmFd::new().map_err(KvmError::Kvm)?;` — opens `/dev/kvm`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Virtio device model — block (io_uring + vhost-user), net (TAP), plus virtio-PCI hotplug

- **Wiki says:** virtio block/net/vsock/balloon/rng/pmem; block has io_uring and vhost-user; net is TAP-backed; virtio-PCI hotplug is available as a Developer Preview
- **Source evidence:**
  - `src/vmm/src/devices/virtio/mod.rs:15-31` — `pub mod balloon; pub mod block; pub mod net; pub mod vsock; pub mod rng; pub mod pmem; pub mod vhost_user;`
  - `src/vmm/src/devices/virtio/block/virtio/io/async_io.rs:14-16` — `use crate::io_uring::operation::{Cqe, OpCode, Operation};` — io_uring async I/O backend
  - `src/vmm/src/devices/virtio/block/vhost_user/mod.rs:8` — `use self::device::VhostUserBlock;` — vhost-user block backend
  - `src/vmm/src/devices/virtio/net/device.rs:256` — `pub tap: Tap,` — TAP-backed network device
  - `README.md:119-120` — "`[Developer Preview]` Hot-plug and hot-unplug virtio PCI devices while the VM is running"
  - `docs/device-hotplug.md:1-11` — hotplugging attaches/detaches `virtio-block`, `virtio-pmem`, `virtio-net` on a running microVM; `docs/device-hotplug.md:18-19` — requires `--enable-pci`
- **Verdict:** ✅ CORRECT (wiki's "no PCIe topology" claim removed — PCI hotplug is a Developer Preview feature)
- **Fix needed:** None

## Claim 5: Jailer — chroot/cgroups/namespaces/privilege drop; NO seccomp module; cgroup v1 AND v2 (default v1)

- **Wiki says:** "creates a chroot jail, applies cgroup constraints (v1 or v2, v1 by default), drops privileges, and joins new PID/net/mount namespaces"; jailer does not apply seccomp
- **Source evidence:**
  - `src/jailer/src/main.rs:15-20` — modules are `cgroup`, `chroot`, `env`, `resource_limits` — **no seccomp module exists** in `src/jailer/src/`
  - `docs/jailer.md:39-42` — "`--cgroup-version` ... The default value is "1" ... Supported options are "1" for cgroup-v1 and "2" for cgroup-v2"
  - `src/jailer/src/cgroup.rs:46-127` — hierarchy discovery handles both v1 mount points and the v2 unified hierarchy (`get_v2_hierarchy_path`, `get_v1_hierarchy_path`)
  - `README.md:129-131` — jailer "applies a cgroup/namespace isolation barrier and then drops privileges"
- **Verdict:** ✅ CORRECT (wiki previously claimed "cgroup/v2" and a separate jailer seccomp filter; both fixed)
- **Fix needed:** None

## Claim 6: Seccomp is thread-category-based; seccompiler generates BPF at build time

- **Wiki says:** "filters are organized by thread category (vmm, api, vcpu)"; seccompiler generates optimized BPF at compile time; capability dropping is the jailer's role
- **Source evidence:**
  - `src/firecracker/src/seccomp.rs:11-12` — `const THREAD_CATEGORIES: [&str; 3] = ["vmm", "api", "vcpu"];`
  - `src/firecracker/src/seccomp.rs:26` — `pub type BpfThreadMap = HashMap<String, Arc<BpfProgram>>;` — per-thread-category filter map
  - `src/firecracker/Cargo.toml:37-39` — `[build-dependencies] seccompiler = { path = "../seccompiler" }`
  - `src/seccompiler/src/bin.rs` — CLI binary calling `compile_bpf()` to emit `seccomp_binary_filter.out`
- **Verdict:** ✅ CORRECT (wiki previously said "capability-based seccomp"; reworded to thread-category-based, matching the source)
- **Fix needed:** None

## Claim 7: Snapshot/restore with full + diff snapshots, rebase-snap and snapshot-editor

- **Wiki says:** "A running microVM can be paused, serialized to disk, and later resumed... Supports both full snapshots and diff snapshots"
- **Source evidence:**
  - `src/vmm/src/snapshot/persist.rs:7-24` — `pub trait Persist<'a>` with `fn save(&self) -> Self::State;` and `fn restore(constructor_args, state) -> Result<Self, Self::Error>;`
  - `src/vmm/src/snapshot/mod.rs:1-10` — module docs: "implements a persistent storage format for Firecracker state snapshots" with magic_id, version string, state, optional CRC64
  - `src/vmm/src/snapshot/crc.rs` — CRC64 integrity checking
  - `src/rebase-snap/` — separate crate for rebasing diff snapshots onto full snapshots
  - `src/snapshot-editor/` — separate crate for editing snapshot files
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: Kernel support policy 5.10 / 6.1 / 6.18; MMDS with session-token auth

- **Wiki says:** supported host/guest kernels are 5.10 / 6.1 / 6.18; MMDS serves `169.254.169.254` and supports token auth
- **Source evidence:**
  - `docs/kernel-policy.md:26-30` — host kernels: v5.10, v6.1, v6.18 (4K page size)
  - `docs/kernel-policy.md:34-38` — guest kernels: v5.10, v6.1, v6.18 (4K page size)
  - `src/vmm/src/mmds/mod.rs:440` — MMDS request handling for `http://169.254.169.254/`
  - `src/vmm/src/mmds/token.rs:31` — `pub const PATH_TO_TOKEN: &str = "/latest/api/token";`
  - `docs/mmds/mmds-user-guide.md:262-278` — token request must hit `/latest/api/token` with `X-metadata-token-ttl-seconds`, subsequent `GET`s present the token via `X-metadata-token`
- **Verdict:** ✅ CORRECT (wiki's "Linux kernel ≥ 4.14" requirement replaced with the actual support policy)
- **Fix needed:** None

## Summary

All 8 claims from the Firecracker wiki verified against source:

- ✅ **Serverless provenance:** AWS Lambda/Fargate, minimal device model, <125ms boot
- ✅ **REST/HTTP API:** OpenAPI spec, micro_http over UDS, zero JSON-RPC
- ✅ **KVM integration:** `kvm-bindings`/`kvm-ioctls` confirmed in `vmm/Cargo.toml` and `vstate/kvm.rs`
- ✅ **Virtio devices + PCI hotplug:** block (io_uring + vhost-user), net (TAP), Developer-Preview hotplug via `--enable-pci`
- ✅ **Jailer:** chroot/cgroups(v1+v2)/namespaces/privilege drop — no seccomp module, capability dropping is its role
- ✅ **Seccomp:** thread-category-based (vmm/api/vcpu) with build-time BPF via seccompiler
- ✅ **Snapshot/restore:** `Persist` trait, diff snapshots, rebase-snap/snapshot-editor
- ✅ **Kernel policy + MMDS:** 5.10/6.1/6.18 host+guest kernels; MMDS token auth at `/latest/api/token`

The codebase is a well-structured Rust workspace with strong security practices — every component (Jailer, thread-category seccomp, cgroups, minimal device model) contributes to the defense-in-depth isolation model required for multi-tenant serverless workloads.

## Related

- [[firecracker]] -- Main wiki entry
- [[kata-containers]] -- Alternative microVM runtime
- [[flintlock]] -- MicroVM lifecycle manager using Firecracker
- [[agentfield]] -- Firecracker micro-VM platform
- [[crun-vm]] -- OCI runtime for Firecracker
- [[seccomp]] -- Seccomp security concept
