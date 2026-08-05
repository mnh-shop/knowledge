---
name: netbird-codegraph-verify
tags: [netbird, vpn, wireguard, go, networking, mesh, wiki]
description: "Codegraph Verification: netbird — validating wiki claims against indexed source code symbols"
source: sources/netbird/
---

# Codegraph Verification: netbird

**Date:** 2026-07-30

## Claim 1: License is BSD-3-Clause with an AGPL-3.0 exception for management/, signal/, relay/
- **Wiki says:** NetBird is BSD 3-Clause except `management/`, `signal/`, and `relay/` which are licensed under AGPL-3.0.
- **Source evidence:**
  - `README.md` line 136 states: "This repository is licensed under the BSD-3-Clause license, which applies to all parts of the repository except for the directories management/, signal/ and relay/. Those directories are licensed under the GNU Affero General Public License version 3.0 (AGPLv3). See the respective LICENSE files inside each directory."
  - `management/LICENSE` lines 1-3 — "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3, 19 November 2007"
  - `signal/LICENSE` lines 1-3 — "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3, 19 November 2007"
  - `relay/LICENSE` lines 1-3 — "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3, 19 November 2007"
- **Verdict:** ✅ CORRECT (fixed: previously stated plain BSD-3-Clause)
- **Fix needed:** License row updated to reflect the dual license split.

## Claim 2: Configuration-free peer-to-peer WireGuard mesh VPN
- **Wiki says:** NetBird creates a configuration-free peer-to-peer private mesh network using WireGuard tunnels, with no port forwarding or VPN gateways.
- **Source evidence:**
  - `README.md` line 45: "NetBird combines a configuration-free peer-to-peer private network and a centralized access control system in a single platform"
  - `README.md` line 47: "NetBird creates a WireGuard-based overlay network that automatically connects your machines over an encrypted tunnel, leaving behind the hassle of opening ports, complex firewall rules, VPN gateways"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: WireGuard underlay and Pion ICE NAT traversal
- **Wiki says:** All traffic is encrypted with WireGuard; NAT traversal uses Pion ICE (WebRTC stack).
- **Source evidence:**
  - `go.mod` lines 24-26: `golang.zx2c4.com/wireguard v0.0.0-20231211153847-12269c276173`, `golang.zx2c4.com/wireguard/wgctrl`, `golang.zx2c4.com/wireguard/windows v0.5.3`
  - `go.mod` line 92: `github.com/pion/ice/v4 v4.0.0-...` (plus stun/turn deps, lines 92-98)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Centralized granular access control with SSO/MFA identity providers
- **Wiki says:** NetBird applies granular access policies from a single place and integrates SSO/MFA via Google, GitHub, Azure AD, Okta, etc.
- **Source evidence:**
  - `README.md` line 49: "NetBird enables secure remote access by applying granular access policies while allowing you to manage them intuitively from a single place"
  - `idp/` directory — identity provider adapters (dex, sdk)
  - `client/internal/auth/` — client-side authentication flows
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Activity logging for audit trail
- **Wiki says:** NetBird provides a full audit trail of connections, policy changes, and administrative actions.
- **Source evidence:**
  - `management/server/activity/` directory — `codes.go`, `event.go`, `store` — server-side activity event model and storage
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Cross-platform clients including MDM, SSH, and eBPF firewall
- **Wiki says:** Native clients for Linux, macOS, Windows, iOS, and Android, plus MDM enrollment, SSH access, and an eBPF firewall.
- **Source evidence:**
  - `client/android/` and `client/ios/` — mobile clients
  - `client/netbird.wxs` (Windows MSI) and `client/installer.nsis` (Windows NSIS installer)
  - `client/embed` — macOS GUI embedding
  - `client/mdm` — mobile device management enrollment
  - `client/ssh` — SSH access management
  - `client/internal/ebpf/` — eBPF kernel firewall
- **Verdict:** ✅ CORRECT
- **Fix needed:** MDM/SSH/eBPF components were unlisted — now added to wiki.

## Claim 7: Beta Agent Network for AI-agent identity-aware access
- **Wiki says:** NetBird has a beta Agent Network feature providing keyless, identity-aware access for AI agents to LLM APIs and private resources.
- **Source evidence:**
  - `README.md` line 40: "🤖 NetBird Agent Network (Beta)"
  - `README.md` lines 41-43: "Identity-aware access control for AI agents — keyless access to LLM APIs and private resources over the encrypted NetBird tunnel. See `agent-network/`"
  - `agent-network/` directory present at repo root
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: Deployment via docker-compose.yml.tmpl template — no PostgreSQL, coturn included
- **Wiki says:** Self-hosted deployment uses `infrastructure_files/docker-compose.yml.tmpl` (envsubst-rendered), starting dashboard, signal, relay, management, and coturn; PostgreSQL is not part of the compose template. The Terraform provider and dashboard are external repos.
- **Source evidence:**
  - `infrastructure_files/docker-compose.yml.tmpl` line 13: `image: netbirdio/dashboard:$NETBIRD_DASHBOARD_TAG`; line 42: `netbirdio/signal:$NETBIRD_SIGNAL_TAG`; line 63: `netbirdio/relay:$NETBIRD_RELAY_TAG`; line 76: `netbirdio/management:$NETBIRD_MANAGEMENT_TAG`; line 102: `image: coturn/coturn:$COTURN_TAG` — five services, no PostgreSQL service anywhere in the file
  - `infrastructure_files/configure.sh` line 259: `envsubst <docker-compose.yml.tmpl >$artifacts_path/docker-compose.yml`
  - `infrastructure_files/setup.env.example` lines 6-10: `NETBIRD_DASHBOARD_TAG`, `NETBIRD_SIGNAL_TAG`, `NETBIRD_MANAGEMENT_TAG`, `COTURN_TAG`, `NETBIRD_RELAY_TAG`
  - `infrastructure_files/management.json.tmpl` line 45: `"Engine": "$NETBIRD_STORE_CONFIG_ENGINE"` — store engine configured externally
  - `README.md` line 61 links dashboard to `github.com/netbirdio/dashboard`; line 65 links the Terraform provider to `registry.terraform.io/providers/netbirdio/netbird` — both external
- **Verdict:** ✅ CORRECT (fixed: previously referenced non-existent `infrastructure/docker-compose.yml` and claimed PostgreSQL was part of the stack)
- **Fix needed:** Deployment command + service list corrected; external-repo flag added.

## Summary

All 8 key claims from the netbird wiki have been verified against the source:
- ✅ Dual license BSD-3 + AGPL-3.0 (management/signal/relay) — README.md:136 + LICENSE files
- ✅ Zero-config P2P WireGuard mesh — README.md:45,47
- ✅ WireGuard underlay + Pion ICE — go.mod:24-26, 92-98
- ✅ Granular access control + SSO/MFA — README.md:49, idp/, client/internal/auth
- ✅ Activity logging — management/server/activity/
- ✅ Cross-platform clients + MDM/SSH/eBPF — client/
- ✅ Beta Agent Network — README.md:40-43, agent-network/
- ✅ Compose template w/ coturn, no PostgreSQL; dashboard + Terraform are external repos

## Related

- [[netbird]] -- Main wiki entry

## Cross-project

- [[mcp-netbird.codegraph-verify]] -- Similar codegraph verification for MCP NetBird
- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for Hermes Agent
