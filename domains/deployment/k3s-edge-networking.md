---
name: k3s-edge-networking
tags: [k3s, kubernetes, networking, flannel, wireguard, tunnel, klipper-lb, loadbalancer, netpol, edge, deployment]
description: "K3s edge networking — websocket tunnel proxy, Flannel CNI with WireGuard, Klipper-lb service load balancer, and kube-router netpol"
source: sources/k3s/
---

# K3s Edge Networking

This guide covers the four networking subsystems K3s uses to make edge clusters work with minimal firewall openings and no managed CNI: the websocket tunnel proxy, Flannel + WireGuard pod networking, Klipper-lb, and the kube-router netpol controller.

## Tunnel Proxy (control-plane connectivity)

The agent-to-server tunnel is the key enabler for edge deployments: **worker nodes never need an inbound port**.

- `pkg/agent/tunnel/tunnel.go` — the tunnel proxy implementation; agents open an outbound websocket connection to the server.
- `pkg/agent/proxy/apiproxy.go` — the agent-side API proxy that routes kubelet/API traffic over the tunnel.
- README.md:35 — "It eliminates the need to expose a port on Kubernetes worker nodes for the kubelet API by exposing this API to the Kubernetes control plane nodes over a websocket tunnel."

Because only *outbound* connectivity from agents to the server is required, nodes behind NAT, cellular links, or locked-down firewalls can join the cluster.

## Flannel CNI with WireGuard

Flannel is the default CNI (README.md:40). K3s configures its backends in `pkg/agent/flannel/`:

- `pkg/agent/flannel/flannel.go:47-50` — backend constants: `BackendVXLAN = "vxlan"`, `BackendHostGW = "host-gw"`, `BackendWireguardNative = "wireguard-native"`, `BackendTailscale = "tailscale"`.
- `pkg/agent/flannel/setup.go:50-52` — the WireGuard native backend config: `"Type": "wireguard"` with `"PersistentKeepaliveInterval": 25`, selected at `setup.go:254`.

The `wireguard-native` backend encrypts cross-node pod traffic in-kernel (via the WireGuard kernel module), which is the zero-config encrypted transport for edge clusters. Other backends (VXLAN, host-gw, tailscale) can be selected with the `--flannel-backend` flag.

## Klipper-lb (embedded service load balancer)

`pkg/agent/loadbalancer/` implements the Klipper-lb embedded service load balancer provider (README.md:44):

- `loadbalancer.go` — the load balancer daemon and configuration
- `httpproxy.go` — HTTP proxy forwarding for `LoadBalancer` services
- `servers.go` — backend server (endpoint) tracking
- `config.go` — controller config; `metrics.go` — LB metrics

`Service` objects of type `LoadBalancer` get a local `svclb-*` DaemonSet pod on each node that forwards to the pod IPs — no external LB hardware or cloud controller required.

## kube-router netpol (NetworkPolicy)

`pkg/agent/netpol/netpol.go` runs the kube-router network policy controller (README.md:45), enforcing Kubernetes `NetworkPolicy` objects with iptables/nftables rules — the bundled host utilities (`k3s-root`, README.md:49) provide iptables/nftables, ebtables, ethtool, and socat.

## Edge Network Layout

```
Agent (edge node)                     Server (control plane)
┌──────────────────────┐   outbound   ┌──────────────────────┐
│ kubelet API ─────────┼── websocket ─┼─► tunnel proxy       │
│ (no inbound port)    │   tunnel     │   (pkg/agent/tunnel) │
│                      │              │                      │
│ Pod A ◄─┐            │              │                      │
│         │ WireGuard  │              │                      │
│ Pod B ◄─┘ (flannel   │              │                      │
│          native)     │              │                      │
│ svclb-* (klipper-lb) │              │                      │
│ netpol (kube-router) │              │                      │
└──────────────────────┘              └──────────────────────┘
```

## Related

- [[k3s]] — Main wiki entry
- [[k3s-ha]] — HA deployment deep-dive
- [[k3s-day2]] — Day-2 operations guide
