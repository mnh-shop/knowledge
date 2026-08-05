---
name: k3s-codegraph-verify
tags: [k3s, codegraph-verify, kubernetes, orchestration]
description: "Codegraph Verification: K3s — validating wiki claims against indexed source code symbols"
source: sources/k3s/
---

# Codegraph Verification: K3s

**Date:** 2026-07-12

## Claim 1: Single binary less than 100 MB with server/agent/kubectl/crictl
- **Wiki says:** K3s packages all Kubernetes components into a single binary less than 100 MB, with `k3s server`, `k3s agent`, bundled `kubectl`, `crictl`, `ctr`, `containerd`, and the `k3s-killall.sh` / `k3s-uninstall.sh` utilities.
- **Source evidence:**
  - `README.md:13` — "all in a binary less than 100 MB" (the ~60 MB figure is NOT in the repo; the README claims only "< 100 MB" and "half the memory")
  - `cmd/server/`, `cmd/agent/` — server and agent subcommands
  - `cmd/kubectl/`, `cmd/crictl/`, `cmd/ctr/`, `cmd/containerd/` — bundled client/CLI commands
  - `cmd/k3s/` — main k3s binary entry point
  - `README.md:156` — install.sh installs utilities `kubectl`, `crictl`, `k3s-killall.sh`, `k3s-uninstall.sh`
  - `install.sh` — one-line installation script
- **Verdict:** ✅ CORRECT (binary size corrected from "~60MB" to "less than 100 MB")

## Claim 2: SQLite via Kine with optional etcd/MariaDB/MySQL/Postgres
- **Wiki says:** SQLite is the default state store via Kine (a datastore shim), with optional etcd, MariaDB, MySQL, and PostgreSQL support.
- **Source evidence:**
  - `README.md:31` — "It adds support for sqlite3 as the default storage backend. Etcd3, MariaDB, MySQL, and Postgres are also supported."
  - `pkg/daemons/config/types.go:12` — imports `github.com/k3s-io/kine/pkg/endpoint` (datastore endpoint wiring)
  - `pkg/cluster/storage.go` + `pkg/cluster/cluster.go` — cluster storage and datastore bootstrap
  - `pkg/etcd/` — full embedded etcd integration: `etcd.go`, `etcdproxy.go`, `member_controller.go`, `metadata_controller.go`, `resolver.go`, `s3/` snapshot support, `snapshot/` management
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Flannel-based default CNI with WireGuard, Klipper-lb, and netpol
- **Wiki says:** Default CNI is Flannel with WireGuard encryption support; Klipper-lb provides the embedded service load balancer and Kube-router the netpol controller.
- **Source evidence:**
  - `pkg/agent/flannel/flannel.go:47-50` — backend constants `BackendVXLAN = "vxlan"`, `BackendHostGW = "host-gw"`, `BackendWireguardNative = "wireguard-native"`, `BackendTailscale = "tailscale"`
  - `pkg/agent/flannel/setup.go:50-52` — `wireguardNativeBackend` flannel config: `"Type": "wireguard"`, `"PersistentKeepaliveInterval": 25`; wired at `setup.go:254`
  - `pkg/agent/loadbalancer/` — Klipper-lb embedded load balancer (`loadbalancer.go`, `httpproxy.go`, `servers.go`)
  - `pkg/agent/netpol/netpol.go` — kube-router netpol controller
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Tunnel proxy for agent-to-server connectivity
- **Wiki says:** K3s eliminates the need to expose a port on worker nodes for the kubelet API by tunneling through a websocket connection to the control plane.
- **Source evidence:**
  - `README.md:35` — "It eliminates the need to expose a port on Kubernetes worker nodes for the kubelet API by exposing this API to the Kubernetes control plane nodes over a websocket tunnel."
  - `pkg/agent/tunnel/tunnel.go` — tunnel proxy implementation for agent-server communication
  - `pkg/agent/proxy/apiproxy.go` — agent-side API proxy over the tunnel
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Auto-deploying manifests from manifests/
- **Wiki says:** K3s automatically deploys Kubernetes resources from local manifests in real-time as they change. Bundled components are defined in `manifests/`.
- **Source evidence:**
  - `manifests/` — `coredns.yaml`, `traefik.yaml`, `local-storage.yaml`, `ccm.yaml`, `metrics-server/`, `rolebindings.yaml`, `runtimes.yaml`
  - `pkg/deploy/` — auto-deploy controller that watches `manifests/` for changes
  - `README.md:57` — "Auto-deploying Kubernetes resources from local manifests in realtime as they are changed."
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Bundled containerd/runc plus cridockerd shim
- **Wiki says:** K3s ships Containerd and runc as the OCI runtime; the optional cridockerd shim provides a Docker-compatible runtime alternative.
- **Source evidence:**
  - `pkg/containerd/` — containerd configuration and lifecycle management
  - `cmd/containerd/` — containerd command wrapping; `pkg/agent/cri/` — CRI integration
  - `pkg/agent/cridockerd/cridockerd.go` (+ `config_linux.go`, `config_windows.go`, `nocridockerd.go`) — dockerd shim alternative runtime
  - `README.md:39` — "Containerd & runc" listed in bundled technologies
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Operations surface — encrypt/token/cert/etcd-snapshot, channels, rootless, build
- **Wiki says:** K3s provides `k3s encrypt` (secret encryption), `k3s token` / `k3s certificate` management, `k3s etcd-snapshot`, version channels via `channel.yaml`, rootless systemd unit, and a documented build process.
- **Source evidence:**
  - `cmd/encrypt/main.go` — secret encryption subcommand; `pkg/cluster/encrypt.go` — encryption config implementation
  - `cmd/token/main.go`, `cmd/cert/main.go` — token and certificate management subcommands
  - `cmd/etcdsnapshot/main.go` — etcd snapshot management; `pkg/etcd/snapshot/` — snapshot implementation
  - `channel.yaml` — version channels (stable/latest/testing/per-minor with `latestRegexp`/`excludeRegexp`)
  - `updatecli/` — release automation (`updatecli.d/`, `values.yaml`, `scripts/`)
  - `k3s-rootless.service` — rootless systemd unit alongside `k3s.service`
  - `BUILDING.md`, `ADOPTERS.md` — build documentation and adoption list
- **Verdict:** ✅ CORRECT

## Summary

All 7 key claims from the K3s wiki have been verified against the source via file:line evidence:
- ✅ Single binary < 100 MB (README.md:13) with server/agent/kubectl/crictl in `cmd/` confirmed
- ✅ SQLite via Kine (`pkg/daemons/config/types.go:12`) with etcd in `pkg/etcd/` confirmed
- ✅ Flannel backends incl. WireGuard (`pkg/agent/flannel/flannel.go:47-50`, `setup.go:50-52`) confirmed
- ✅ Tunnel proxy (`pkg/agent/tunnel/` + `pkg/agent/proxy/apiproxy.go`) confirmed
- ✅ Auto-deploying manifests (`manifests/` + `pkg/deploy/`) confirmed
- ✅ Containerd runtime + cridockerd shim (`pkg/agent/cridockerd/`) confirmed
- ✅ Ops surface: `cmd/encrypt`, `cmd/token`, `cmd/cert`, `cmd/etcdsnapshot`, `channel.yaml`, `updatecli/`, `k3s-rootless.service`, `BUILDING.md`, `ADOPTERS.md` confirmed

## Related

- [[k3s]] -- Main wiki entry
- [[k3s-ha]] -- HA deployment deep-dive
- [[k3s-edge-networking]] -- Edge networking deep-dive
- [[k3s-day2]] -- Day-2 operations guide

## Cross-project

- [[prometheus.codegraph-verify]] -- Similar codegraph verification for Prometheus
- [[netdata.codegraph-verify]] -- Similar codegraph verification for Netdata
- [[podman.codegraph-verify]] -- Similar codegraph verification for Podman
