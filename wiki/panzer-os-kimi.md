---
name: panzer-os-kimi
tags: [agentfield, bootc, container, deployment, fedora, goclaw, hermes-agent, multi-agent, orchestration, podman, postgres, quadlet, systemd, wiki, panzer-os-kimi]
description: "Rootless-first modular multi-agent OS (v3.0.0) for AI agent stacks on Podman Quadlets — shared 3-instance Postgres spine, three dispatch lanes, three zones, zero-trust networking"
source: sources/panzer-os-kimi/
verification_date: 2026-07-30
verified_by: codegraph-verify
---

# Panzer OS — Multi-Agent OS

> Indexed here as `panzer-os-kimi`; the upstream repository is `mnh-shop/panzer-os.git` (the "kimi" suffix is a knowledge-index rename only).

| Field | Value |
|---|---|
| **Origin** | [mnh-shop/panzer-os](https://github.com/mnh-shop/panzer-os.git) — `git@github.com:mnh-shop/panzer-os.git`; images at `ghcr.io/mnh-shop/*` |
| **Version** | v3.0.0 |
| **License** | Private-first. Some files derive from upstream open-source projects and retain their original notices. |
| **Stack** | Shell, Python, Podman/Quadlets, systemd, PostgreSQL 18+pgvector, bootc |
| **Deployment** | Podman Quadlets on single VPS (default) or multi-host via NetBird mesh |
| **Source** | `sources/panzer-os-kimi/` |

## What is it?

A rootless-first, modular multi-agent operating system for deploying AI agent stacks at scale on Podman Quadlets (README.md:9-10). It provides a durable **three-instance PostgreSQL spine with pgvector**, three **independent dispatch lanes** (AgentField reasoners, hermes-agent stacks, goclaw lower-layer stacks), a fleet of hardened coding execution harnesses, and an ecosystem of specialized reasoners — all running rootless under a dedicated `panzer` user with zero-trust networking (README.md:27-34).

Built on bootc (bootable containers), the entire stack — OS, runtimes, agent services, databases, and networking — packages as a single deployable OCI image that can be built into raw/QCOW2 VM disk images for bare-metal-style VM deployment (bootc/ Containerfile; Makefile bootc-* targets).

## Key Features

- **Three Dispatch Lanes:** AgentField (AF reasoners, on-demand), Hermes Agent (L2 kanban orchestrator + L1 workers), GoClaw (per-tenant gateway + catalog agents) — sharing **only** Postgres, never routing through each other (README.md:28-29, 167-180).
- **Shared Postgres Spine (×3, not per-lane):** Meta (control-plane), Operational (workload), Knowledge (RAG) — shared across lanes with schema isolation, never mixed (README.md:96, 154-156).
- **Rootless-First:** No root daemons, no privileged containers. Everything under the dedicated `panzer` user via systemd user units (Quadlets) (README.md:33-34, 152-153).
- **Zero-Trust Networking:** All published ports loopback-bound; egress controlled by nftables allowlist. L0 harnesses never join the spine networks (README.md:33-34, 324-333).
- **bootc-Powered:** Built as a bootc OCI image; produces raw disk images (canonical) and QCOW2 via qemu-img conversion (Makefile bootc-raw-image / bootc-qcow2-image).
- **Multi-Host Mesh:** Optional NetBird WireGuard mesh VPN for worker hosts when more resources are needed (README.md:158-159, 412-414).
- **OpenRouter FREE Models Only:** All LLM calls route through `central-freellmapi` → OpenRouter `:free` models; paid model calls prohibited (README.md:342-346).
- **systemd Integration:** All services managed as systemd user services via Quadlet `.container` files with health checks, auto-restart, and dependency ordering (README.md:428-435).

## Architecture — Three Zones

| Zone | Name | State | Trust | Examples |
|------|------|-------|-------|----------|
| **A** | Spine | Always running | Tightly controlled — no direct external exposure | 3× Postgres, central-agentfield, goclaw-as-meta-partner, goclaw-librarian, central-freellmapi, tuwunel, knowledge-mcp, hermes-admin-mcp, pg-admin-mcp, panzer-control-mcp |
| **B** | Dispatch | On-demand | Ephemeral, per-workload | hermes-agent@stack, goclaw@stack, AF nodes |
| **C** | Execution | On-demand (singletons) | Fully isolated — `NoNewPrivileges`, egress firewalls | panzer-opencode-runtime, panzer-pi-runtime, panzer-zot-runtime, searxng, osint-mcp-server, playwright-mcp, docs-mcp, service-gator, llm-wiki |

(README.md:258-264 — note Zone B is **Dispatch**, matching the zones table.)

```
┌──────────────────────────────────────────────────────────────┐
│                  Panzer OS (bootc, rootless)                 │
│                                                              │
│  Zone A — Spine (always running)                             │
│    central-meta-postgres:35432   (control plane DB)          │
│    central-operational-postgres:15432 (workload DB)          │
│    central-knowledge-postgres:25432 (knowledge/RAG DB)       │
│    central-freellmapi:3001 → OpenRouter :free                │
│    goclaw-as-meta-partner + goclaw-librarian                 │
│    tuwunel (Matrix/Conduit) · knowledge-mcp                  │
│                                                              │
│  Zone B — Dispatch (on-demand, per-workload)                 │
│    hermes-agent@stack · goclaw@stack · AF nodes              │
│                                                              │
│  Zone C — Execution (on-demand singletons, hardened)         │
│    L0 runtimes (opencode · pi · zot) → MCP tool servers      │
│                                                              │
│  NetBird WireGuard mesh (optional multi-host)                │
│  Podman Quadlets + systemd user services (panzer user)       │
└──────────────────────────────────────────────────────────────┘
```

**Key relationship:** Postgres is shared across lanes (schema-isolated). The three lanes never route through each other — AF ecosystem instances register with AgentField for tracking only (README.md:96, 156, 175-178).

## Three Dispatch Lanes

| Lane | Job | Task Ingress |
|------|-----|-------------|
| **AgentField (+ AF ecosystem)** | Node registry, heartbeats, DID/VC identity, async execution for AF reasoners | `POST /api/v1/execute/async/<node>.<reasoner>` (REST API) |
| **Hermes-agent** | L2 kanban orchestrator + L1 workers per stack; human via Matrix | Matrix room (tuwunel) or `hermes-admin-mcp` |
| **GoClaw lower layer** | Per-tenant agent gateway + catalog agents | `POST /v1/chat/completions` (REST webhook — consumes MCP, does not expose task MCP) |

(README.md:167-180)

## PostgreSQL Architecture

Three instances because three fundamentally different data concerns (README.md:234-245):

| Instance | Port | Purpose |
|----------|------|---------|
| `central-meta-postgres` | 35432 | Control plane — `agentfield`, `panzer_ledger`, `panzer_registry`, `goclaw_meta` |
| `central-operational-postgres` | 15432 | Workload — `goclaw` (tenant_* schemas), `n8n`, `panzer_profiles` |
| `central-knowledge-postgres` | 25432 | RAG/embeddings — `panzer_knowledge*`, `goclaw_librarian` |

All run `pgvector/pgvector:0.8.4-pg18-bookworm`. Published ports are loopback-bound (`127.0.0.1` only). Multi-tenant isolation for goclaw: each stack gets a dedicated PostgreSQL role (`goclaw_<stack>_rw`) and schema (`tenant_<stack>`) with `search_path` isolation.

**Why three — not mergeable:** control + workload (a runaway tenant query could block agentfield heartbeats), workload + knowledge (50K embedding rows compete with kanban writes for buffer cache), control + knowledge (different backup cadence and data volume) (README.md:247-251).

## Networking — Zero-Trust

- **No network exposure to host** — all published ports loopback-bound
- **Egress control** via nftables allowlist (approved destinations only)
- **L0 harnesses never join `meta-internal` or `knowledge-internal`** — tools via `panzer-mcp-tools`, LLM egress only
- **Knowledge reachable only through `knowledge-mcp`** — no direct Postgres access from dispatch/execution zones
- **Per-stack tenant isolation** — dedicated role + schema per goclaw stack
- **Secrets** via Podman secrets, synced from `~/.config/panzer-os/secrets/`
- Container security: `NoNewPrivileges=true`, `DropCapability=ALL`, `UserNS=keep-id` or explicit UID mapping

(README.md:324-333)

Ten dedicated Podman networks by trust zone: `meta-internal` (172.20.5.0/24), `knowledge-internal` (172.20.7.0/27), `panzer-data` (172.20.4.0/28, cross-zone DB bridge), `panzer-hermes` (172.20.3.0/24), `panzer-goclaw` (172.20.6.0/24), `panzer-harness` (172.20.10.0/28), `panzer-af` (172.20.13.0/28), `panzer-mcp-tools` (172.20.11.0/24), `panzer-search-backend` (172.20.12.0/28), `panzer-ui` (172.20.20.0/28) (README.md:309-321).

## Boot Flow (bootc)

1. Fedora bootc kernel boots → systemd init
2. Cloud-init runs → `panzer-firstboot.service`
3. Seeds `panzer.env` → creates `panzer` user
4. `sync-podman-secrets` → re-seeds Podman secrets
5. Spine Quadlets auto-start (`WantedBy=default.target`)
6. `panzer-egress-nftables` → applies egress firewall rules
7. Workload Plane stacks start on-demand via `panzer-deploy`
8. L0 runtimes start on-demand when hermes workers need them

(README.md:363-403)

## Deployment

### Build the bootc image (Makefile targets)

```bash
make bootc-build          # Build bootc OCI image (podman build -f bootc/Containerfile .)
make bootc-raw-image      # bootc install to-disk --via-loopback → /var/tmp/panzer-os.raw (Linux, sudo)
make bootc-qcow2-image    # qemu-img convert raw → /var/tmp/panzer-os.qcow2 (requires qemu-img)
make bootc-disk-image     # Alias for bootc-raw-image (backward compat)
```

`all` = `build-coding lint` — it builds local coding harness images and runs the lint suite; there is **no** plain `build`, `build-qcow2`, `build-iso`, or ISO installer target (Makefile:36, 66-287). QCOW2 is a qemu-img conversion of the canonical raw output, not a native bootc output.

### Deploy on a VPS

```bash
git clone --branch main git@github.com:mnh-shop/panzer-os.git
cd panzer-os
bash install.sh --mode quadlet    # interactive; or --non-interactive --yes
# Then the unified operator CLI:
scripts/panzerctl help
scripts/panzerctl status
scripts/panzerctl deploy
scripts/panzerctl stack up hermes@<name>   # or goclaw@<name>
scripts/panzerctl stack down <name>
scripts/panzerctl provision research       # tool MCP servers (searxng, docs-mcp, ...)
```

Deploy wizard (preferred over hand-starts):

```bash
scripts/panzer-deploy hermes|goclaw|agentfield [--stack <template>] [--instance NAME]
```

**Key principle: provision ≠ register.** A provisioned stack has a DB schema and secrets; a registered stack has working agents — both required. A running container with unregistered agents is an empty gateway (README.md:463-475).

**Dual deployment paths** (AGENTS.md): Path 1 — via goclaw meta agents (MCP): `goclaw-fleet-manager → panzer-control-mcp.deployment_propose`; Path 2 — via scripts (fallback, no meta dependency): `bash scripts/panzer-deploy goclaw --stack <template> --instance <name> --yes`. Both are production requirements, not alternatives.

### Resource budget (8GB VPS)

Spine ~2GB · Hermes stacks ~1GB each · Goclaw stacks ~500MB each · Hardened runtimes ~1GB each · Tool MCP servers ~500MB total (README.md:416-417).

### Multi-host scaling

Single-host first (default). For more resources: `bash install.sh --mode worker --mesh-join-token <token>` joins a NetBird mesh; worker stacks reach spine Postgres via mesh DNS → direct TCP over WireGuard (README.md:412-414).

## Repository Structure

- `scripts/` — 61 operator scripts; `panzerctl` unified CLI, `panzer-deploy` wizard, `panzer-*.sh` deploy/register/backup/rotate helpers (plus `scripts/lib/` deploy libraries)
- `deploy/` — `first-slice.yaml` + generated `docker-compose.yml`, `init-db.sh`, `seed-secrets.sh`, `setup-volumes.sh`, `setup.yaml`, `schemas/`, `state/`
- `services/` — **17 service categories**: agentfield, backup, dashboard, execution, goclaw, hermes, llm-gateway, log-collector, matrix, mcp, n8n, netbird, observability, postgres, quadlet, shared, templates
- `bootc/` — Containerfile, cloud-init, kernel-cmdline, modprobe, sysctl, rootfs overlay
- `assets/` — goclaw catalogs, hermes stacks/profiles, skills; `secrets/` — secret reference
- `docs/canonical/` — ARCHITECTURE, WORKLOAD-LANES, POSTGRES-SCHEMA, NETWORKING, DEPLOYMENT-WORKFLOW, GOCLAW-REFERENCE, LLM-ROUTING, and more

## Agent Operating Policy

- **CBM-first gate:** HARD RULE — `codebase-memory-mcp` must be queried before grep/glob/read for any structural code question (AGENTS.md).
- **OpenRouter FREE models only:** `:free` suffix required; never paid models; never report "key exhausted" for free models (AGENTS.md).
- **Definition of success:** container boot ≠ working — a goclaw instance is working only when agents are registered (`GET /v1/agents` non-empty), skills resolve, and a real task produces a real agent run.

## Related

- [[tank-os]] — Simpler single-service bootc OS image (OpenClaw)
- [[agentfield]] — AF reasoner control plane (one dispatch lane)
- [[hermes-agent]] — Python MCP hub agent (one dispatch lane)
- [[goclaw]] — Go enterprise agent gateway (one dispatch lane)
- [[netbird]] — WireGuard mesh for multi-host networking
- [[podman]] / [[podman-quadlet]] — Container runtime and systemd integration
- [[bootc]] — Bootable container technology powering the OS image
