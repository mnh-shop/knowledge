---
name: firecracker-snapshotting
tags: [diff-snapshot, firecracker, kvm, microvm, rebase-snap, restore, snapshot, snapshot-editor, virtualization, vmm]
description: "Firecracker snapshot/restore — snapshot format, full and diff snapshots with CRC, rebase-snap and snapshot-editor workflow"
source: sources/firecracker/
---

# Firecracker Snapshotting

**Source:** `sources/firecracker/`
**Wiki:** [[firecracker]]

Firecracker supports pausing a running microVM, serializing its full state to disk, and later resuming it — enabling fast scale-out, pre-warming, and deterministic replay. The machinery lives in `src/vmm/src/snapshot/`, with companion tool crates `rebase-snap` and `snapshot-editor`.

## Snapshot Format

`src/vmm/src/snapshot/mod.rs:1-10` documents the persistent storage format: each snapshot consists of a magic ID, a version string, the serialized state, and an optional CRC64 checksum for integrity verification (`src/vmm/src/snapshot/crc.rs`).

Serialization is driven by the `Persist` trait (`src/vmm/src/snapshot/persist.rs:7-24`):

```rust
pub trait Persist<'a> {
    type State;
    type ConstructorArgs;
    type Error;
    fn save(&self) -> Self::State;                                   // persist.rs:19
    fn restore(constructor_args: Self::ConstructorArgs,
               state: &Self::State) -> Result<Self, Self::Error>;    // persist.rs:21-23
}
```

Every snapshotable component (vCPUs, memory, virtio devices, rate limiters, MMDS) implements `Persist`; e.g. `rate_limiter/persist.rs:16` exposes serializable `TokenBucketState`.

## Full vs Diff Snapshots

| Type | Captures | Use case |
|------|----------|----------|
| **Full** | Complete guest memory + device state | First snapshot of a microVM; self-contained restore |
| **Diff** | Incremental changes since a base snapshot (dirty pages tracked via KVM) | Frequent checkpointing of a long-running VM with low per-snapshot cost |

Diff snapshots are not self-contained — they must be applied on top of the full snapshot they were taken against.

## Tooling Workflow

Firecracker ships two dedicated crates for managing snapshot files:

### rebase-snap (`src/rebase-snap/`)

Rebases diff snapshots onto full snapshots, producing a new full snapshot. Typical workflow:

1. Take a **full snapshot** of a pre-warmed microVM (the "golden" state)
2. Run the workload, periodically capturing **diff snapshots**
3. `rebase-snap` merges a diff onto the golden full snapshot → new standalone full snapshot
4. Restore from the rebased full snapshot — no dependency on the original diff chain

### snapshot-editor (`src/snapshot-editor/`)

Inspects and edits snapshot files — e.g. viewing/repairing metadata or fixing inconsistencies before a restore. Useful for debugging corrupt or hand-modified snapshots.

## Restore

Restoring creates a new Firecracker process from the saved state via the `Persist::restore` path: a fresh VMM is constructed, then each component is rehydrated from its serialized state. Because restore is a normal API-driven operation, restored microVMs can themselves be snapshotted again.

## Requirements & Caveats

- **Memory size must match**: the microVM must be configured with the same memory size (and, for diff snapshots, the same base snapshot) as when the snapshot was taken
- **Kernel/rootfs must be available**: snapshots capture VM state, not the kernel image or root filesystem — those must be supplied at restore time
- **CPU compatibility**: restoring across hosts requires compatible CPU features (see CPU template fingerprinting, `src/vmm/src/cpu_config/`)
- **Rate limiter state** is preserved through `TokenBucketState`, so throttle configuration survives snapshot/restore

## Related

- [[firecracker]] — Main wiki entry
- [Devices](firecracker-devices.md) — what gets serialized (devices, rate limiters, MMDS)
- [Prod Setup](../deployment/firecracker-prod-setup.md) — operational context for snapshot/restore
- [[rebase-snap]] — diff-snapshot rebasing tool
