---
name: panzer-os
tags: [agent-os, multi-agent, postgres, pgvector, podman, quadlet, goclaw, hermes, agentfield, rootless, deployment]
description: "Wiki entry for panzer-os — rootless-first multi-agent operating system for deploying AI agent stacks at scale"
source: sources/panzer-os/
verification_date: 2026-08-12
verified_by: codegraph-verify
---

# panzer-os

|| Field | Value |
||---|---|
|| **Origin** | [mnh-shop/panzer-os](https://github.com/mnh-shop/panzer-os) |
|| **License** | See repo LICENSE |
|| **Version** | `v3.0.0` (README.md) |
|| **Source** | `sources/panzer-os/` |
|| **Branches** | `main`, `kimi/production-grade`, `livevps-beta`, `panzer-os-beta`, `quadlet-deploy-overhaul`, `live-test/quadlet-reconcile` |
|| **CBM index** | `Users-admin-repos-knowledge-sources-panzer-os` (~267K nodes, ~398K edges est.); also `panzer-os-kimi` and `panzer-os-livevps-beta` as separate worktree indexes |

## What is it?

panzer-os is a rootless-first, modular multi-agent operating system for deploying AI agent stacks at scale on Podman Quadlets. It provides a durable three-instance PostgreSQL spine with pgvector, three independent workload lanes (AgentField reasoners, hermes-agent stacks, goclaw lower-layer stacks), a fleet of hardened coding execution harnesses, and a **multi-tenant goclaw control plane** — all running rootless under Podman Quadlets with zero-trust networking.

The goclaw-meta instance is a **multi-tenant agent platform** (not a fixed-agent gateway): 4 fixed agents (fleet-commander + 3 deployers) in the master tenant, plus dynamic per-project coordinators in isolated tenants.

## Architecture

```
Operator (Telegram / opencode)
  └─ goclaw-meta (fleet-commander + deployers + fleet-manager)
       ├─ GoClaw lower layer (many instances, per-project tenants)
       ├─ Hermes-agent stacks (orchestrator + L1 workers per stack)
       └─ AgentField (1 CP spine + many reasoner nodes)
```

### Three lower-layer lanes

| Lane | What | Scale |
|------|------|-------|
| GoClaw lower layer | Multiple independent goclaw instances with catalogs (devops, research, coding) | Many instances, per-project tenants |
| Hermes-agent stacks | Orchestrator + L1 workers per stack (kanban) | Many stacks |
| AgentField | 1 control plane + reasoner nodes | Scale nodes independently |

Lanes NEVER call each other directly. Cross-lane work is mediated by per-project coordinators on meta.

### PostgreSQL spine

Three-instance PostgreSQL with pgvector, all running `pgvector/pgvector:0.8.4-pg18-bookworm`. Multi-tenant isolation for goclaw: each stack gets a dedicated PostgreSQL role (`goclaw_<stack>_rw`) and schema (`tenant_<stack>`) with `search_path` isolation.

### Deployment

- Podman Quadlets (rootless, systemd --user)
- `panzer` user (UID 1000) — no root daemons, no privileged containers
- Loopback-bound networking, nftables egress allowlist
- Secrets from `/home/panzer/.config/panzer-os/secrets/*.txt`, mirrored to podman secrets

## Key scripts

- `panzer-preinstall.sh` — fresh install (platform detection, packages, user creation UID 1000, repo cloning)
- `panzer-install.sh` — installation handler
- `panzer-provision-harness-pool.sh` — provision execution harnesses
- `sync-podman-secrets` — sole mutation authority for secrets

## Value for coding agents

panzer-os is the primary deployment target for this knowledge system. It demonstrates rootless multi-agent orchestration with PostgreSQL+pgzipalot, goclaw meta-control-plane, and Podman Quadlet-based deployment. The `docs/canonical/` directory contains the full architecture documentation.
