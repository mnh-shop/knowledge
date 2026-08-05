---
name: panzer-os-kimi-codegraph-verify
tags: [panzer-os, kimi, quadlet, podman, rootless, multi-agent, ai, deployment, wiki]
description: "Codegraph Verification: panzer-os-kimi — validating corrected wiki claims against indexed source (mnh-shop/panzer-os)"
source: sources/panzer-os-kimi/
---

# Codegraph Verification: panzer-os-kimi

**Date:** 2026-07-30

## Claim 1: Upstream origin is mnh-shop/panzer-os.git (not sallyom)
- **Wiki says:** Origin is `mnh-shop/panzer-os` — git remote `git@github.com:mnh-shop/panzer-os.git`; images `ghcr.io/mnh-shop/*`.
- **Source evidence:**
  - `README.md` line 104: "git clone --branch main git@github.com:mnh-shop/panzer-os.git"
  - `README.md` lines 437-438: "Every hermes stack shares one `ghcr.io/mnh-shop/hermes-agent` image. Every goclaw stack shares one `ghcr.io/mnh-shop/goclaw` image."
  - `docs/canonical/INSTALL-ONBOARDING.md` lines 49, 150: install bootstrap via `https://raw.githubusercontent.com/mnh-shop/panzer-os/main/install.sh`
  - `git remote -v` shows `git@github.com:mnh-shop/panzer-os.git`
- **Verdict:** ✅ CORRECT (wiki previously cited `sallyom/panzer-os-kimi` — corrected; "kimi" suffix exists only in the knowledge-index rename)
- **Fix needed:** None (already applied)

## Claim 2: Rootless-first multi-agent OS on Podman Quadlets, v3.0.0
- **Wiki says:** v3.0.0 rootless-first modular multi-agent OS for AI agent stacks on Podman Quadlets.
- **Source evidence:**
  - `README.md` line 9: "**v3.0.0** — Rootless-first, modular multi-agent operating system"
  - `README.md` line 10: "for deploying AI agent stacks at scale on Podman Quadlets"
  - `README.md` line 33: "Everything runs under a dedicated `panzer` user. No root daemons. No privileged containers."
  - `VERSION` file: `3.0.0`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: bootc build targets are `bootc-build` / `bootc-raw-image` / `bootc-qcow2-image` / `bootc-disk-image` — no plain `build`/`build-qcow2`/`build-iso`
- **Wiki says:** Deployment uses `make bootc-build`, `make bootc-raw-image`, `make bootc-qcow2-image`, `make bootc-disk-image`; `all: build-coding lint`; no ISO target exists.
- **Source evidence:**
  - `Makefile` line 66: "bootc-build:" → `podman build $(BOOTC_PLATFORM_ARGS) -t $(BOOTC_IMAGE) -f bootc/Containerfile .`
  - `Makefile` line 229: "bootc-raw-image:" → `bootc install to-disk --generic-image --via-loopback`
  - `Makefile` line 262: "bootc-qcow2-image:" → `qemu-img convert -f raw -O qcow2`
  - `Makefile` line 287: "bootc-disk-image: bootc-raw-image" (alias)
  - `Makefile` line 36: "all: build-coding lint"
  - No `build`, `build-qcow2`, or `build-iso` targets exist anywhere in the Makefile
- **Verdict:** ✅ CORRECT (wiki previously claimed `make build` / `make build-qcow2` / `make build-iso` — corrected)
- **Fix needed:** None (already applied)

## Claim 4: Postgres is shared across lanes (schema-isolated) — three concerns, not three lanes
- **Wiki says:** Three Postgres instances — Meta (control-plane), Operational (workload), Knowledge (RAG) — shared across lanes with schema isolation; each goclaw stack gets its own role + `tenant_<stack>` schema.
- **Source evidence:**
  - `README.md` line 96: "Postgres is shared across lanes (schema-isolated)."
  - `README.md` lines 154-156: "Three Postgres instances, three concerns. Meta (control-plane), Operational (workload), Knowledge (RAG). Never mixed." / "Three independent lanes. AgentField, hermes, goclaw — share ONLY Postgres."
  - `README.md` lines 234-245: ports 35432/15432/25432, `pgvector/pgvector:0.8.4-pg18-bookworm`, goclaw role `goclaw_<stack>_rw` + schema `tenant_<stack>` with `search_path` isolation
  - `docs/canonical/POSTGRES-SCHEMA.md` lines 103-108: `CREATE SCHEMA tenant_<stack>`, `ALTER ROLE goclaw_<stack>_rw SET search_path TO tenant_<stack>,public`
- **Verdict:** ✅ CORRECT (wiki previously claimed "one DB per agent lane" — corrected)
- **Fix needed:** None (already applied)

## Claim 5: Zone B is Dispatch
- **Wiki says:** Three-zone architecture — Zone A Spine (always running), Zone B Dispatch (on-demand), Zone C Execution (on-demand singletons).
- **Source evidence:**
  - `README.md` lines 258-264 (zones table): Zone A "Spine — Always running", Zone B "Dispatch — On-demand, Ephemeral, per-workload", Zone C "Execution — On-demand (singletons), Fully isolated — `NoNewPrivileges`, egress firewalls"
  - `README.md` lines 278-282 (mermaid): "Zone B — Dispatch" with `panzer-hermes`, `panzer-goclaw`, `panzer-af` networks
- **Verdict:** ✅ CORRECT (wiki previously said Zone B "Workload" — corrected to Dispatch per the zones table)
- **Fix needed:** None (already applied)

## Claim 6: AgentField is described as "on-demand reasoners" — no Firecracker micro-VM claim in this repo
- **Wiki says:** AgentField nodes are "on-demand reasoners"; no Firecracker micro-VM claim is made by panzer-os.
- **Source evidence:**
  - `README.md` line 67 (mermaid): "AgentField Nodes<br/>on-demand reasoners"
  - `README.md` lines 171, 226: AF lane = async execution via `POST /api/v1/execute/async/<node>.<reasoner>`, "Reasoner runs internally", "Pollable result via execution ID"
  - No occurrence of "Firecracker" or "micro-VM" anywhere in the repository
- **Verdict:** ✅ CORRECT (wiki previously claimed AgentField runs in "Firecracker micro-VMs" — softened; that capability is not claimed in this source)
- **Fix needed:** None (already applied)

## Claim 7: Zero-trust networking + OpenRouter FREE models + NetBird mesh
- **Wiki says:** Loopback-bound networking with nftables egress allowlist; OpenRouter `:free` models only; NetBird WireGuard mesh for multi-host.
- **Source evidence:**
  - `README.md` lines 33-34: "All networking is loopback-bound. Egress is controlled by nftables allowlist."
  - `README.md` lines 324-333: security model — no host exposure, nftables allowlist, knowledge via `knowledge-mcp` only, Podman secrets from `~/.config/panzer-os/secrets/`
  - `README.md` lines 342-346: "All models use OpenRouter `:free` suffix. Paid model calls are prohibited."
  - `README.md` lines 158-159, 412-414: "NetBird mesh VPN for worker hosts"; `install.sh --mode worker --mesh-join-token <token>`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: Dual deployment paths + CBM-first gate policy
- **Wiki says:** Lower-layer stacks deploy via goclaw meta agents (MCP) or shell scripts; workspace enforces codebase-memory-mcp-first.
- **Source evidence:**
  - `AGENTS.md`: "**Path 1 — Via goclaw meta agents (MCP):**" and "**Path 2 — Via scripts (fallback, no meta dependency):**" with `bash scripts/panzer-deploy goclaw --stack <template> --instance <name> --yes`
  - `AGENTS.md`: "## HARD RULE: codebase-memory-mcp FIRST (gate, not preference)"
  - `README.md` lines 463-475: stack lifecycle "provision → start → register (registrar)"; "**Key principle: provision ≠ register.**"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 8 claims from the corrected panzer-os-kimi wiki verified against source:
- ✅ Origin `mnh-shop/panzer-os` (git remote, README, install bootstrap, ghcr.io images)
- ✅ v3.0.0 rootless-first on Podman Quadlets
- ✅ bootc-* Make targets; no `build`/`build-qcow2`/`build-iso`/ISO target
- ✅ Postgres shared across lanes (schema-isolated) — three concerns, not three lanes
- ✅ Zone B = Dispatch (zones table README.md:258-264)
- ✅ AgentField "on-demand reasoners" — no Firecracker claim in repo
- ✅ Zero-trust networking, OpenRouter `:free` only, NetBird mesh
- ✅ Dual deployment paths + CBM-first gate

## Related

- [[panzer-os-kimi]] -- Main wiki entry

## Cross-project

- [[goclaw.codegraph-verify]] -- Similar codegraph verification for GoClaw
- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for Hermes Agent
- [[agentfield.codegraph-verify]] -- Similar codegraph verification for AgentField
