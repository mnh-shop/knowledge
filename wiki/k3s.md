---
name: k3s
tags: [k3s, kubernetes, container, orchestration, edge, iot, lightweight]
description: "Lightweight certified Kubernetes distribution for edge, IoT, and resource-constrained environments"
source: sources/k3s/
---

# K3s

| Field | Value |
|---|---|
| **Origin** | [k3s-io/k3s](https://github.com/k3s-io/k3s) |
| **Source** | `sources/k3s/` |
| **Repomix** | `raw/k3s/k3s.xml` |
| **Codegraph** | `graphs/k3s/` |

## Overview

K3s is a lightweight, CNCF-certified Kubernetes distribution designed for resource-constrained environments including edge devices, IoT gateways, and ARM-based hardware. It packages Kubernetes into a single binary under 100MB by removing optional components and replacing etcd with SQLite (with optional etcd support for HA deployments). K3s preserves full Kubernetes API compatibility while dramatically reducing the operational overhead of running a cluster.

## Key Features

- **Single Binary Distribution** — All Kubernetes components packaged in a single ~60MB binary with no external dependencies
- **Embedded Database** — SQLite as the default state store (optional etcd for multi-node HA clusters)
- **Automatic TLS** — Self-signed certificate generation and rotation for cluster communication
- **Helm Controller** — Built-in Helm chart operator for declarative application deployment
- **Flannel-based Networking** — Default CNI with WireGuard encryption support for cross-node traffic
- **Multi-Architecture** — Support for amd64, arm64, and armhf, making it ideal for Raspberry Pi and edge gateways

## Architecture

K3s simplifies Kubernetes by moving components that are traditionally separate processes (kube-controller-manager, kube-scheduler, kube-apiserver) into a single server process. Agents connect to the server over a tunnel proxy, eliminating the need for direct node connectivity. The embedded SQLite database replaces etcd for single-server setups, and the Helm controller enables operator-defined application lifecycles without a separate Helm CLI.

## Related

- [[podman]] — Container runtime that pairs with K3s for OCI-compliant workloads
- [[headroom]] — Auto-scaling management for Kubernetes deployments on K3s clusters
- [[prometheus]] — Metrics collection for monitoring K3s cluster health
- [[grafana]] — Dashboarding for K3s telemetry and workload observability
- [[bootc]] — Bootable container OS for running K3s at the edge
