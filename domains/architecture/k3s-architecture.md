---
name: k3s-architecture
tags: [k3s, architecture, kubernetes, orchestration]
description: "CNCF-certified lightweight Kubernetes distribution — single binary, embedded SQLite/etcd, edge deployment, consolidated control plane"
source: sources/k3s/
verification_date: 2026-07-12
verified_by: codegraph + wiki
---

# K3s — Architecture

**Source:** `sources/k3s/`

## Overview

K3s is a lightweight, CNCF-certified Kubernetes distribution for resource-constrained environments (edge devices, IoT, CI runners, ARM). It packages Kubernetes into a single ~60MB binary by consolidating control-plane components into one process, replacing etcd with SQLite as the default state store (via Kine), and removing in-tree storage drivers and cloud providers. It is a **distribution, not a fork** — fewer than 1,000 lines of patches over upstream Kubernetes.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        k3s server binary                         │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ kube-apiserver│  │kube-controller│  │   kube-scheduler     │   │
│  │  (embedded)   │  │  -manager    │  │    (embedded)       │   │
│  └──────┬───────┘  │  (embedded)  │  └──────────────────────┘   │
│         │          └──────────────┘                               │
│  ┌──────┴──────────────────────────────────────────────────┐     │
│  │                    Kine Datastore Shim                    │     │
│  │  ┌─────────┐  ┌────────┐  ┌──────────┐  ┌──────────┐   │     │
│  │  │ SQLite  │  │ etcd   │  │ MySQL    │  │PostgreSQL│   │     │
│  │  │(default)│  │ (HA)   │  │          │  │          │   │     │
│  │  └─────────┘  └────────┘  └──────────┘  └──────────┘   │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐    │
│  │Helm      │ │Metrics   │ │CoreDNS   │ │Traefik(optional) │    │
│  │Controller│ │Server    │ │          │ │Ingress           │    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                            │
                   Tunnel Proxy (WebSocket)
                            │
┌─────────────────────────────────────────────────────────────────┐
│                       k3s agent binary                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Containerd│  │  Kubelet │  │  Flannel │  │Klipper-lb│       │
│  │          │  │  (cri)   │  │  (CNI)   │  │(svc LB)  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│  │Kube-     │  │Local-Path│  │Tunnel    │                      │
│  │router    │  │Provisionr│  │Proxy Cli │                      │
│  │(netpol)  │  │(storage) │  │          │                      │
│  └──────────┘  └──────────┘  └──────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

### Single Binary Consolidation

K3s collapses traditionally separate Kubernetes control-plane processes — `kube-apiserver`, `kube-controller-manager`, `kube-scheduler` — into a single server process via the embedded executor (`pkg/executor/embed/`). The binary includes `kubectl`, `crictl`, and utility scripts (`k3s-killall.sh`, `k3s-uninstall.sh`).

### Datastore Abstraction (Kine)

The **Kine** shim provides a Kubernetes `storage.Interface` that translates etcd API calls to the configured backend. Options:
- **SQLite** (default): Single-node setups. Reduces memory/storage by 10x vs etcd.
- **etcd**: Multi-node HA with embedded etcd cluster (3+ servers).
- **MySQL / MariaDB**: External database HA.
- **PostgreSQL**: External database HA.

### Tunnel Proxy

Eliminates the need to expose kubelet ports on worker nodes. The agent connects to the server via a **WebSocket tunnel**, requiring only outbound connectivity from agents. Simplifies firewall configuration and network security.

## Key Components

### Server Package (`pkg/server/`)

The `PrepareServer` → `StartServer` sequence: sets up data directories, generates TLS certificates (auto-rotating), starts control-plane components via `control.Server()`, runs startup hooks (deploy, Helm charts, etc.), initializes controllers, and writes admin kubeconfig.

### Agent Package (`pkg/agent/`)

Manages the node agent lifecycle: configures Containerd, Kubelet (CRI), Flannel (CNI with optional WireGuard), tunnel proxy connection, load balancer, network policy controller, and templates for kubelet and kube-proxy configuration.

### Embedded Technologies

| Component | Role | Disableable |
|-----------|------|-------------|
| Containerd & runc | OCI container runtime | Yes |
| Flannel | Default CNI with WireGuard | Yes (swappable) |
| CoreDNS | Cluster DNS | Yes |
| Traefik | Default ingress controller | Yes |
| Klipper-lb | Service load balancer | Yes |
| Helm-controller | CRD-driven Helm chart operator | Yes |
| Kube-router | NetworkPolicy enforcement | Yes |
| Local-path-provisioner | Local persistent volumes | Yes |
| Metrics Server | Resource usage metrics | Yes |

### Auto-Deploying Manifests

K3s watches `$datadir/server/manifests/` and auto-deploys Kubernetes resources in real-time as files change — no manual `kubectl apply` required for bootstrap workloads.

## Related

- [[k3s]] — Wiki page with deployment and usage details
- [[podman]] — Alternative OCI runtime integrable with K3s
- [[headroom]] — AI context compression for agent operations on clusters
- [[prometheus]] — Metrics collection for K3s cluster monitoring
- [[grafana]] — Dashboarding for K3s workload observability
- [[bootc]] — Bootable container OS for edge K3s deployments
- [[mission-control]] — Multi-cluster observability management
- [[netdata]] — Per-second infrastructure monitoring for K3s nodes
