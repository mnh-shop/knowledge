---
name: netbird
tags: [vpn, wireguard, mesh-network, golang, networking, security, iac, terraform, postgres, self-hosted, wiki, netbird]
description: "Configuration-free peer-to-peer private mesh VPN on WireGuard with centralized access control, SSO/MFA, and Terraform provider"
source: sources/netbird/
verification_date: 2026-07-30
verified_by: codegraph-verify
---

# NetBird — WireGuard Mesh VPN

| Field | Value |
|---|---|
| **Origin** | [netbirdio/netbird](https://github.com/netbirdio/netbird) |
| **License** | BSD 3-Clause — except `management/`, `signal/`, `relay/` which are AGPL-3.0 |
| **Stack** | Go, WireGuard, Pion ICE, Postgres |
| **Deployment** | Self-hosted Docker Compose or managed NetBird Cloud |
| **Source** | `sources/netbird/` |

## What is it?

A configuration-free peer-to-peer private mesh VPN built on WireGuard with centralized access control. NetBird creates a secure overlay network where every peer connects directly to every other peer (P2P mesh) using WireGuard tunnels, coordinated through a lightweight management server. No port forwarding, no complex VPN configuration — just install the agent and authenticate.

It provides an admin web UI for access policies, SSO/MFA integration, activity logging, and a Terraform provider for infrastructure-as-code management of network resources.

## Key Features

- **Zero Config Mesh VPN:** Peers discover each other automatically via the management service. NAT traversal uses Pion ICE (WebRTC stack) for direct P2P connections.
- **WireGuard Underlay:** All traffic is encrypted with WireGuard — modern, audited, high-performance cryptographic tunnels.
- **Centralized Access Control:** Define granular access policies per user, group, or peer via the admin web UI or API.
- **SSO / MFA:** Integrates with identity providers (Google, GitHub, Azure AD, Okta, etc.) for single sign-on and multi-factor authentication.
- **Activity Logging:** Full audit trail of connections, policy changes, and administrative actions.
- **Terraform Provider:** Manage NetBird resources as code — peers, groups, routes, policies, DNS settings, and users. ⚠️ External repo: `registry.terraform.io/providers/netbirdio/netbird` (not part of this monorepo).
- **Self-Hosted or Cloud:** Run your own management server via Docker Compose, or use the managed NetBird Cloud service.
- **Cross-Platform Clients:** Native clients for Linux, macOS, Windows, iOS, and Android — including MDM enrollment (`client/mdm`), SSH access (`client/ssh`), and an eBPF firewall (`client/internal/ebpf`).
- **Beta Agent Network:** Identity-aware access control for AI agents — keyless access to LLM APIs and private resources over the encrypted NetBird tunnel (`agent-network/`, `netbird.ai`).

## Tech Stack

| Component | Technology |
|---|---|
| **Language** | Go |
| **VPN Protocol** | WireGuard |
| **NAT Traversal** | Pion ICE (WebRTC) |
| **Database** | PostgreSQL |
| **Admin UI** | React-based web dashboard (⚠️ external repo `netbirdio/dashboard`, referenced only as a compose image) |
| **IaC** | Terraform provider (⚠️ external repo) |
| **Deployment** | Docker Compose (self-hosted) |

## Repository Components

| Component | Path | Purpose |
|---|---|---|
| Management server | `management/` | Access control, policy enforcement (AGPL-3.0) |
| Signal service | `signal/` | ICE negotiation / signaling (AGPL-3.0) |
| Relay | `relay/` | Fallback relay for blocked NATs (AGPL-3.0) |
| Client agent | `client/` | Cross-platform agent + UI, installers |
| MDM | `client/mdm` | Mobile device management enrollment |
| SSH | `client/ssh` | SSH access management |
| eBPF firewall | `client/internal/ebpf` | Kernel-level firewall rules |
| Combined binary | `combined/` | Single-binary build (agent + management in one) |
| Trusted proxy | `trustedproxy/` | Reverse proxy trusted by the management server |
| Upload server | `upload-server/` | File upload service |
| Compose template | `infrastructure_files/docker-compose.yml.tmpl` | Self-hosted deployment (envsubst-rendered) |
| Agent Network | `agent-network/` | Beta AI-agent identity-aware access |

**External repos (not in this monorepo):** the Terraform provider (`registry.terraform.io/providers/netbirdio/netbird`, linked from README.md:65) and the Admin UI dashboard (`github.com/netbirdio/dashboard`, linked from README.md:61) — the monorepo only references the dashboard as a compose image (`image: netbirdio/dashboard:$NETBIRD_DASHBOARD_TAG`).

## Deployment

### Self-Hosted (Docker Compose)

The canonical compose file is a **template** — `infrastructure_files/docker-compose.yml.tmpl` — rendered into a real `docker-compose.yml` via `envsubst` by `infrastructure_files/configure.sh` (configure.sh:259). Image tags are injected through environment variables defined in `setup.env.example` (`$NETBIRD_DASHBOARD_TAG`, `$NETBIRD_SIGNAL_TAG`, `$NETBIRD_MANAGEMENT_TAG`, `$NETBIRD_RELAY_TAG`, `$COTURN_TAG`).

```bash
git clone https://github.com/netbirdio/netbird.git
cd netbird/infrastructure_files
./getting-started.sh   # renders docker-compose.yml.tmpl via envsubst and starts the stack
```

The compose template starts five services: **dashboard** (admin UI), **signal**, **relay**, **management**, and **coturn** (STUN/TURN). PostgreSQL is **not** part of the compose template — the management server's store engine is configured separately via `$NETBIRD_STORE_CONFIG_ENGINE` (management.json.tmpl:45), so Postgres must be provisioned independently when an external database is required.

### NetBird Cloud

Prefer the managed service at [netbird.io](https://netbird.io) — no infrastructure to maintain.

### Client Installation

```bash
# Linux / macOS
curl -fsSL https://github.com/netbirdio/netbird/releases/latest/download/netbird_linux_amd64.tar.gz | tar -xz
sudo ./netbird up --management-url https://your-manager:443 --setup-key YOUR_KEY

# Or via package managers: brew, apt, yum, etc.
```

## Related

- [[docker-netbird]] — Rootless container networking setup using NetBird
- [[mcp-netbird]] — MCP server for managing NetBird infrastructure from AI coding agents
- [[netdata]] — Network monitoring for NetBird mesh nodes
- [[podman]] — Container runtime that benefits from NetBird mesh networking
- [[panzer-os-kimi]] — Multi-agent OS that uses NetBird for multi-host networking
