---
name: k3s-ha
tags: [k3s, kubernetes, ha, high-availability, etcd, kine, sqlite, datastore, certificates, encryption, deployment]
description: "K3s high-availability deployment — embedded etcd topology, external datastore options via Kine, token/certificate management, and secret encryption"
source: sources/k3s/
---

# K3s High Availability

This guide covers the high-availability (HA) options for a K3s cluster: the embedded etcd topology, external datastore backends via Kine, and the token/certificate/encryption operations surface that HA clusters depend on.

## HA Topologies

### 1. Embedded etcd (multi-server)

K3s can run its own etcd cluster **inside the server processes** instead of a standalone etcd deployment. The in-repo implementation lives in `pkg/etcd/`:

- `pkg/etcd/etcd.go` — embedded etcd server bootstrap and runtime
- `pkg/etcd/etcdproxy.go` — proxying the datastore endpoint through the server
- `pkg/etcd/member_controller.go` — etcd member management (add/remove servers)
- `pkg/etcd/apiaddresses_controller.go` — advertises server API addresses to agents
- `pkg/etcd/metadata_controller.go` — metadata reconciliation across the etcd cluster
- `pkg/etcd/resolver.go` — datastore endpoint resolution for HA
- `pkg/etcd/snapshot/` + `pkg/etcd/s3/` — etcd snapshotting to local disk or S3-compatible storage
- `cmd/etcdsnapshot/main.go` — `k3s etcd-snapshot` CLI (save/restore/delete/prune snapshots)

> **Note:** The in-repo README only states "Managing an embedded etcd cluster" as a maintained function (README.md:58). The three-or-more-server topology and quorum guidance are documented in the external docs at docs.k3s.io; this wiki entry treats the multi-node topology as external-doc-based, backed by the `pkg/etcd/` member controller code.

### 2. External datastore via Kine

Kine (`github.com/k3s-io/kine`) is a datastore shim that translates the Kubernetes datastore API to a pluggable backend. It is wired in at `pkg/daemons/config/types.go:12` (`github.com/k3s-io/kine/pkg/endpoint` import) and `pkg/cluster/storage.go`.

Supported backends per README.md:31:

| Backend | Notes |
|---|---|
| **SQLite** (default) | Single-server default; file-based, no separate DB process |
| **etcd3** | External etcd cluster as the datastore |
| **MariaDB / MySQL** | External SQL database |
| **PostgreSQL** | External SQL database |

External datastore clusters point every server node at the same backend via the `--datastore-endpoint` server flag; there is no embedded etcd quorum to maintain, at the cost of operating a separate database.

## Token & Certificate Management

HA clusters need coordinated tokens and certificates across server nodes.

- **`k3s token`** (`cmd/token/main.go`) — manage the agent join token. The server writes `K3S_TOKEN` to `/var/lib/rancher/k3s/server/node-token` (README.md:162); workers join with `K3S_URL` + `K3S_TOKEN` (README.md:163-168).
- **`k3s certificate`** (`cmd/cert/main.go`) — rotate/renew the self-signed certificates K3s generates for cluster components (TLS is automatic by default, README.md:55).
- **`k3s encrypt`** (`cmd/encrypt/main.go`) — enable/disable at-rest encryption of Kubernetes secrets; implementation in `pkg/cluster/encrypt.go`.

## Deployment Checklist

1. Decide topology: embedded etcd (multi-server) vs external datastore (Kine → MySQL/Postgres/etcd3).
2. Provision servers: `curl -sfL https://get.k3s.io | sh -s - server --cluster-init` for the first embedded-etcd node; subsequent servers join with `--server` + `--token`.
3. Validate quorum and member health via `k3s etcd-snapshot` and the member controller logs.
4. Enable `k3s encrypt` if at-rest secret encryption is required.
5. Test snapshot restore from `pkg/etcd/s3/` (S3-compatible target) as part of DR drills.

## Related

- [[k3s]] — Main wiki entry
- [[k3s-edge-networking]] — Edge networking deep-dive
- [[k3s-day2]] — Day-2 operations guide
