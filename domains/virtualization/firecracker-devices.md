---
name: firecracker-devices
tags: [device-model, firecracker, hotplug, io-uring, kvm, mmds, rate-limiting, vhost-user, virtio, virtualization, vmm]
description: "Firecracker device model — virtio devices, io_uring, vhost-user block, virtio-PCI hotplug, memory hotplug, MMDS token auth, rate limiting"
source: sources/firecracker/
---

# Firecracker Device Model

**Source:** `sources/firecracker/`
**Wiki:** [[firecracker]]

The device model is Firecracker's minimal-attack-surface approach to presenting I/O to microVMs: a small set of virtio devices, a lightweight metadata service, and token-bucket rate limiting. Everything here is in `src/vmm/src/devices/` unless noted.

## Device Inventory

All virtio devices are declared in `src/vmm/src/devices/virtio/mod.rs:15-31`:

| Device | Path | Notes |
|--------|------|-------|
| **Block** | `devices/virtio/block/` | File-backed virtio-blk; io_uring async backend; vhost-user block backend |
| **Net** | `devices/virtio/net/` | TAP-backed virtio-net (`net/device.rs:256` — `pub tap: Tap`) |
| **Vsock** | `devices/virtio/vsock/` | VM sockets, Unix domain socket backend for host-guest comms |
| **Balloon** | `devices/virtio/balloon/` | Memory balloon for guest memory reclaim |
| **RNG** | `devices/virtio/rng/` | Entropy device |
| **PMEM** | `devices/virtio/pmem/` | Persistent memory device |

The guest-visible model is deliberately minimal: no emulated BIOS, no graphics. Firecracker's own FAQ (`FAQ.md:63`) lists exactly six emulated devices: virtio-net, virtio-balloon, virtio-block, virtio-vsock, serial console, and a minimal keyboard controller.

## Block I/O Backends

### io_uring

The block device supports asynchronous I/O via the Linux `io_uring` interface. `src/vmm/src/devices/virtio/block/virtio/io/async_io.rs:14-16` imports the io_uring opcode machinery (`Cqe`, `OpCode`, `Operation`) and the `IoUring` wrapper (`src/vmm/src/io_uring/`). This replaces the synchronous read/write path for higher throughput and lower latency.

### vhost-user

A vhost-user block backend (`src/vmm/src/devices/virtio/block/vhost_user/mod.rs:8` — `VhostUserBlock`) allows offloading the virtio block queue processing to an external vhost-user daemon process, reducing the in-VMM emulation cost.

## Virtio-PCI Hotplug (Developer Preview)

PCI transport is **opt-in**: Firecracker must be started with `--enable-pci` (`docs/device-hotplug.md:18-19`). With PCI enabled, devices can be hot-plugged and hot-unplugged on a running microVM without reboot:

- Supported hotplug types: `virtio-block`, `virtio-pmem`, `virtio-net` (`docs/device-hotplug.md:9-14`)
- Uses the same API endpoints as pre-boot device configuration — the only difference is the request is issued after the VM started
- **No automatic guest notification**: after hotplug the guest must rescan the PCI bus; before unplug it must manually detach the device (`docs/device-hotplug.md:26-29`)
- MMIO transport does not support hotplug

`README.md:119-120` marks hotplug as `[Developer Preview]` — API/behavior may change.

## Memory Hotplug (virtio-mem)

`docs/memory-hotplug.md` documents memory hotplugging via the `virtio-mem` para-virtualized device:

- The device manages a contiguous guest memory region divided into fixed-size blocks; the host changes the target size to plug/unplug memory
- Firecracker adds "slots" — sets of contiguous blocks (usually 128MiB) protected from guest access when not allocated to prevent malicious guests touching the hotpluggable range
- Requires a guest kernel with `VIRTIO_MEM_F_UNPLUGGED_INACCESSIBLE` support (x86_64 minimum kernel 5.16)

## MMDS with Session-Token Auth

The MicroVM Metadata Service (`src/vmm/src/mmds/`) is reachable from the guest at the link-local `169.254.169.254` (`mmds/mod.rs:440`), mirroring the AWS EC2 metadata API so standard tooling works unchanged.

Token authentication (`src/vmm/src/mmds/token.rs`):

1. Guest issues `PUT /latest/api/token` (`token.rs:31` — `PATH_TO_TOKEN`) with an `X-metadata-token-ttl-seconds` or `X-aws-ec2-metadata-token-ttl-seconds` header (`docs/mmds/mmds-user-guide.md:262-264`)
2. MMDS returns a base64-encoded, AES-encrypted session token bound to the TTL (max 2^32 tokens per key, `token.rs:88-94`)
3. Subsequent `GET` requests must present the token via `X-metadata-token` / `X-aws-ec2-metadata-token` (`docs/mmds/mmds-user-guide.md:276-284`)
4. Invalid/missing tokens are tracked by the `mmds.rx_invalid_token` / `mmds.rx_no_token` metrics (`docs/mmds/mmds-user-guide.md:238-239`)

## Rate Limiting (TokenBucket)

`src/vmm/src/rate_limiter/mod.rs:56` defines the `TokenBucket` — a token bucket with configurable `size` (capacity), `initial_one_time_burst`, and `refill_time`. The rate limiter can constrain both bandwidth (bytes/sec) and operations-per-second independently per virtio device (block and net), configurable via the API (`README.md:110-111`). Refill runs on a 100ms timer (`rate_limiter/mod.rs:20`). `rate_limiter/persist.rs:16` (`TokenBucketState`) makes rate limiter state snapshotable.

## Control Plane

All device configuration happens through the REST/HTTP control API (OpenAPI spec `src/firecracker/swagger/firecracker.yaml`) served by `micro_http` over a Unix Domain Socket — there is no JSON-RPC anywhere in the codebase.

## Related

- [[firecracker]] — Main wiki entry
- [Snapshotting](firecracker-snapshotting.md) — how device state is serialized for snapshot/restore
- [Prod Setup](../deployment/firecracker-prod-setup.md) — deploying Firecracker in production
- [[virtio]] — Virtio device standard
