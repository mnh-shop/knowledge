---
name: k3s
tags: [k3s, kubernetes, container, orchestration, edge, iot, lightweight, cncf, arm]
description: "CNCF-certified lightweight Kubernetes distribution for edge, IoT, CI, and resource-constrained environments"
source: sources/k3s/
verification_date: 2026-07-12
verified_by: codegraph-verify
source_reference: sources/k3s/README.md
---

# K3s

| Field | Value |
|---|---|
| **Origin** | [k3s-io/k3s](https://github.com/k3s-io/k3s) |
| **License** | Apache-2.0 |
| **Stack** | Go (core), Containerd, Flannel, CoreDNS, Traefik |
| **Source** | `sources/k3s/` |
| **Repomix** | `raw/k3s/k3s.xml` |
| **Codegraph** | `graphs/k3s/` |

## Overview

K3s is a lightweight, CNCF-certified Kubernetes distribution designed for resource-constrained environments including edge devices, IoT gateways, CI runners, ARM-based hardware, and development environments. It packages Kubernetes into a single binary under 100MB by removing in-tree storage drivers and cloud providers (which have out-of-tree CSI and CCM alternatives) and replaces etcd with SQLite as the default state store, with optional etcd, MariaDB, MySQL, and PostgreSQL support for high-availability deployments.

K3s is a **distribution**, not a fork — it maintains a small set of patches (well under 1000 lines) for K3s-specific use cases and contributes changes upstream whenever possible. It preserves full Kubernetes API compatibility and CNCF conformance while dramatically reducing the operational overhead and memory footprint of running a cluster. By running many Kubernetes components inside a single process, K3s eliminates duplicated overhead that each component would otherwise incur separately.

The project derives its name from "half the size of Kubernetes" — Kubernetes is 10 letters stylized as k8s, so "half" is 5 letters stylized as K3s (with the '3' representing an '8' cut in half vertically).

## Key Features

- **Single Binary Distribution** — All Kubernetes components packaged in a single ~60MB binary with no external OS dependencies beyond a sane kernel and cgroup mounts. Includes `kubectl`, `crictl`, `k3s-killall.sh`, and `k3s-uninstall.sh` utilities.
- **Embedded Database** — SQLite as the default state store via Kine (a datastore shim). Optional etcd for multi-node HA clusters, plus MariaDB, MySQL, and PostgreSQL support.
- **Automatic TLS** — Self-signed certificate generation and rotation for cluster communication, eliminating manual certificate management.
- **Helm Controller** — Built-in Helm chart operator for CRD-driven declarative application deployment without a separate Helm CLI.
- **Flannel-based Networking** — Default CNI with WireGuard encryption support for cross-node traffic. Replaceable with alternative CNI plugins.
- **Multi-Architecture** — Full support for amd64, arm64, armhf, and s390x — ideal for Raspberry Pi, ARM edge gateways, and embedded systems.
- **Built-in Service Load Balancer** — Klipper-lb as an embedded service load balancer provider for cluster-internal traffic distribution.
- **Network Policy Controller** — Kube-router netpol controller for Kubernetes NetworkPolicy enforcement.
- **Local Path Provisioner** — Built-in local-path-provisioner for provisioning persistent volumes using local node storage without external storage systems.
- **Kuberentes Conformance** — Fully CNCF-certified Kubernetes conformant — passes all upstream conformance tests.
- **Auto-Deploying Manifests** — Automatically deploys Kubernetes resources from local manifests in real-time as they are changed.
- **Tunnel Proxy** — Eliminates the need to expose a port on worker nodes for the kubelet API by tunneling through a websocket connection to the control plane.

## Bundled Technologies

K3s packages these technologies into a single cohesive distribution:

- **Containerd & runc** — OCI-compliant container runtime
- **Flannel** — Default CNI plugin for pod networking with WireGuard encryption
- **CoreDNS** — Cluster DNS service discovery
- **Metrics Server** — Resource usage metrics for `kubectl top` and HPA
- **Traefik** — Default ingress controller (can be disabled)
- **Klipper-lb** — Embedded service load balancer provider
- **Kube-router** — Network policy controller for NetworkPolicy enforcement
- **Helm-controller** — CRD-driven Helm chart deployment operator
- **Kine** — Datastore shim for SQLite/etcd/MySQL/PostgreSQL backend
- **Local-path-provisioner** — Local persistent volume provisioning
- **Host utilities** — iptables/nftables, ebtables, ethtool, socat

All bundled technologies can be disabled or swapped out for alternatives.

## Architecture

K3s simplifies Kubernetes by consolidating traditionally separate processes — kube-controller-manager, kube-scheduler, and kube-apiserver — into a single server binary. The server process manages TLS certificates, the embedded datastore, and the connection between worker and server nodes via a tunnel proxy (eliminating direct node-to-node connectivity requirements).

The agent process connects to the server through the tunnel proxy, which simplifies firewall configuration and network security by requiring only outbound connectivity from agents to the server. The embedded SQLite database (via Kine) replaces etcd for single-server setups, reducing memory and storage requirements by an order of magnitude.

For high-availability deployments, K3s supports embedded etcd clusters across three or more server nodes, or external etcd/PostgreSQL/MySQL databases. The HA setup provides automatic leader election, data replication, and seamless failover.

## Deployment

K3s is designed for rapid deployment with minimal prerequisites:

**Server (single node):**
```bash
curl -sfL https://get.k3s.io | sh -
# Kubeconfig written to /etc/rancher/k3s/k3s.yaml
# Node token at /var/lib/rancher/k3s/server/node-token
```

**Worker node join:**
```bash
curl -sfL https://get.k3s.io | K3S_URL=https://server:6443 K3S_TOKEN=XXX sh -
```

K3s maintains pace with upstream Kubernetes releases, aiming for patch releases within one week and new minor versions within 30 days. Release versioning reflects upstream Kubernetes: e.g., `v1.27.4+k3s1` maps to Kubernetes `v1.27.4` with K3s-specific patches.

## Usage / Integration

- **Edge Kubernetes** — Deploy [[prometheus]] on K3s for lightweight cluster monitoring at edge locations with minimal resource overhead.
- **Dashboarding** — Visualize K3s cluster telemetry via [[grafana]] dashboards using Prometheus as the metrics source.
- **Observability** — Monitor K3s nodes with [[netdata]] for per-second container and system metrics alongside Kubernetes control plane health.
- **Container runtime** — K3s ships with Containerd but can integrate with [[podman]] for specialized OCI-compliant workloads.
- **Scaling management** — Use the built-in Metrics Server with Horizontal Pod Autoscalers for workload scaling, complemented by [[headroom]] for context-optimized agent operations on clusters.
- **Bootc edge OS** — Run K3s on [[bootc]]-based immutable images for reliable, self-updating edge Kubernetes clusters.
- **Resource optimization** — Use [[headroom]] consumption analysis alongside K3s for lightweight resource management.
- **Zero-trust networking** — K3s's tunnel proxy and WireGuard integration provide secure multi-node communication without complex VPN setup.

## Use Cases

K3s is ideal for:
- **Edge computing** — Remote sites, retail stores, manufacturing floors with limited power and connectivity
- **IoT gateways** — ARM-based devices processing sensor data with local Kubernetes orchestration
- **CI/CD runners** — Lightweight ephemeral clusters for build and test pipelines
- **Development environments** — Local Kubernetes clusters for application development without cloud costs
- **Embedded K8s** — Bundling Kubernetes into appliances, devices, and software appliances
- **ARM clusters** — Raspberry Pi and other ARM-based multi-node clusters for edge computing

## Related

- [[podman]] — Container runtime that pairs with K3s for OCI-compliant workloads
- [[headroom]] — AI context compression for agent operations on and about K3s clusters
- [[prometheus]] — Metrics collection for monitoring K3s cluster health and workloads
- [[grafana]] — Dashboarding for K3s telemetry and workload observability
- [[bootc]] — Bootable container OS for running K3s at the edge
- [[netdata]] — Per-second infrastructure monitoring for K3s nodes
- [[mission-control]] — Centralized observability management for multi-cluster K3s deployments
