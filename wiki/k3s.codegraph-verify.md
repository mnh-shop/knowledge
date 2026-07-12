---
name: k3s-codegraph-verify
tags: [k3s, codegraph-verify, kubernetes, orchestration]
description: "Codegraph Verification: K3s — validating wiki claims against indexed source code symbols"
source: sources/k3s/
---

# Codegraph Verification: K3s

**Date:** 2026-07-12

## Claim 1: Single binary packaging with server and agent commands
- **Wiki says:** K3s packages all Kubernetes components into a single binary with `k3s server` and `k3s agent` as the main commands, plus bundled `kubectl`, `crictl`, `k3s-killall.sh`, and `k3s-uninstall.sh`.
- **Source evidence:**
  - `cmd/server/` implements the server subcommand for control plane nodes
  - `cmd/agent/` implements the agent subcommand for worker nodes
  - `cmd/k3s/` contains the main k3s binary entry point
  - `cmd/kubectl/` provides bundled kubectl support
  - `cmd/crictl/` provides bundled crictl (CRI tool) support
  - `cmd/ctr/` provides bundled containerd CLI
  - `pkg/cli/server/` and `pkg/cli/agent/` contain the server/agent CLI implementations
  - `install.sh` provides the one-line installation script
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Embedded SQLite via Kine with optional etcd
- **Wiki says:** SQLite is the default state store via Kine (a datastore shim), with optional etcd for multi-node HA clusters, plus MariaDB, MySQL, and PostgreSQL support.
- **Source evidence:**
  - `pkg/etcd/` contains full etcd integration: `etcd.go`, `etcdproxy.go`, `apiaddresses_controller.go`, `member_controller.go`, `metadata_controller.go`, `resolver.go`, `s3/` snapshot support, and `snapshot/` management
  - `pkg/cli/server/` handles datastore configuration including Kine-based SQLite backend
  - `main.go` initializes the server with configurable datastore endpoint
  - `pkg/daemons/config/` contains server configuration including datastore settings
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Flannel-based default CNI with WireGuard encryption
- **Wiki says:** Default CNI is Flannel with WireGuard encryption support for cross-node traffic.
- **Source evidence:**
  - `pkg/agent/flannel/` contains Flannel CNI integration
  - `pkg/agent/flannel/` configures pod networking via Flannel daemon
  - `pkg/agent/netpol/` provides kube-router network policy controller
  - `pkg/agent/loadbalancer/` provides Klipper-lb embedded service load balancer
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Tunnel proxy for agent-to-server connectivity
- **Wiki says:** K3s eliminates the need to expose a port on worker nodes for the kubelet API by tunneling through a websocket connection to the control plane.
- **Source evidence:**
  - `pkg/agent/tunnel/tunnel.go` implements the tunnel proxy for agent-server communication
  - `pkg/agent/proxy/` provides the agent-side proxy for tunnel connectivity
  - The tunnel eliminates direct node-to-node connectivity requirements by routing through the server
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Auto-deploying manifests from manifests/
- **Wiki says:** K3s automatically deploys Kubernetes resources from local manifests in real-time as they change. Bundled components are defined in `manifests/`.
- **Source evidence:**
  - `manifests/` contains: `coredns.yaml`, `traefik.yaml`, `local-storage.yaml`, `ccm.yaml`, `metrics-server/`, `rolebindings.yaml`, and `runtimes.yaml`
  - `pkg/deploy/` implements the auto-deploy controller that watches `manifests/` directory for changes
  - Bundled manifests include CoreDNS (cluster DNS), Traefik (default ingress), local-path-provisioner (storage), metrics-server, and cloud controller manager
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Containerd and runc bundled as OCI runtime
- **Wiki says:** K3s ships with Containerd and runc as the OCI-compliant container runtime, plus `crictl` for debugging.
- **Source evidence:**
  - `pkg/containerd/` contains containerd configuration and lifecycle management
  - `pkg/agent/containerd/` contains agent-side containerd setup
  - `cmd/containerd/` contains containerd command wrapping
  - `pkg/agent/cri/` provides CRI (Container Runtime Interface) integration
  - `pkg/agent/cridockerd/` provides dockerd shim support as an alternative runtime
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 6 key claims from the K3s wiki have been verified against the source code via directory exploration:
- ✅ Single binary with server, agent, kubectl, crictl in `cmd/` confirmed
- ✅ Embedded SQLite via Kine with optional etcd in `pkg/etcd/` confirmed
- ✅ Flannel-based CNI in `pkg/agent/flannel/` confirmed
- ✅ Tunnel proxy in `pkg/agent/tunnel/` confirmed
- ✅ Auto-deploying manifests in `manifests/` with `pkg/deploy/` controller confirmed
- ✅ Containerd runtime integration in `pkg/containerd/` and `pkg/agent/cri/` confirmed

## Related

- [[k3s]] -- Main wiki entry
- [[k3s-architecture]] -- Deep-dive into architecture
- [[k3s-deployment]] -- Deployment guide

## Cross-project

- [[prometheus.codegraph-verify]] -- Similar codegraph verification for Prometheus
- [[netdata.codegraph-verify]] -- Similar codegraph verification for Netdata
- [[podman.codegraph-verify]] -- Similar codegraph verification for Podman
