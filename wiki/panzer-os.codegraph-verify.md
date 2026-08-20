---
name: panzer-os-codegraph-verify
tags: [panzer-os, codegraph-verify, agent-os, postgres, pgvector, podman, quadlet, goclaw]
description: "Codegraph Verification: panzer-os — validating wiki claims against indexed source code symbols"
source: sources/panzer-os/
---

# Codegraph Verification: panzer-os

**Date:** 2026-08-12

**Version checked:** `c60849ce` (main, Merge pull request #14 from mnh-shop/livevps-beta)

## Claim 1: Rootless-first multi-agent OS for deploying AI stacks at scale

- **Wiki says:** panzer-os is a rootless-first, modular multi-agent operating system for deploying AI agent stacks at scale on Podman Quadlets.
- **Source evidence:**
  - `README.md` — "panzer-os provides a complete runtime for autonomous AI agents: a durable three-instance PostgreSQL spine with pgvector, three independent workload lanes... all running rootless under Podman Quadlets with zero-trust networking"
  - `README.md` — "v3.0.0 — Rootless-first, modular multi-agent operating system"
- **Verdict:** ✅ CORRECT

## Claim 2: Three-instance PostgreSQL spine with pgvector

- **Wiki says:** Three-instance PostgreSQL with pgvector, all using `pgvector/pgvector:0.8.4-pg18-bookworm`.
- **Source evidence:**
  - `README.md` — "three-instance PostgreSQL spine with pgvector"
  - `README.md` — "All run pgvector/pgvector:0.8.4-pg18-bookworm"
  - `docs/canonical/POSTGRES-SCHEMA.md` — PostgreSQL schema documentation (referenced in AGENTS.md read order)
- **Verdict:** ✅ CORRECT

## Claim 3: Three independent workload lanes

- **Wiki says:** AgentField reasoners, hermes-agent stacks, goclaw lower-layer stacks — three lanes that never call each other directly.
- **Source evidence:**
  - `README.md` — "three independent workload lanes (AgentField reasoners, hermes-agent stacks, goclaw lower-layer stacks)"
  - `AGENTS.md` — "Three lower-layer systems (all orchestrated by meta)" with a table showing GoClaw lower layer, Hermes-agent stacks, AgentField
  - `AGENTS.md` — "Lanes never call each other directly. Cross-lane work is mediated by the per-project coordinator on meta"
- **Verdict:** ✅ CORRECT

## Claim 4: Multi-tenant goclaw control plane

- **Wiki says:** goclaw-meta is a multi-tenant agent platform with 4 fixed agents (fleet-commander + 3 deployers) in master tenant, plus dynamic per-project coordinators.
- **Source evidence:**
  - `README.md` — "The goclaw-meta instance is a multi-tenant agent platform (not a fixed-agent gateway). It runs 4 fixed agents (fleet-commander + 3 deployers) in the master tenant, plus dynamic per-project coordinators in isolated tenants"
  - `docs/canonical/META-CONTROL-PLANE.md` — complete control-plane architecture (referenced in AGENTS.md)
- **Verdict:** ✅ CORRECT

## Claim 5: Rootless deployment with Podman Quadlets

- **Wiki says:** All runs under `panzer` user (UID 1000), no root daemons, no privileged containers, loopback-bound networking.
- **Source evidence:**
  - `AGENTS.md` — "Rootless podman runs as user panzer (UID 1000). Root's podman is empty"
  - `AGENTS.md` — "All networking is loopback-bound. Egress is controlled by nftables allowlist"
  - `AGENTS.md` — "systemctl --user requires XDG_RUNTIME_DIR"
- **Verdict:** ✅ CORRECT

## Claim 6: Worktree-based branch structure

- **Wiki says:** Three branches tracked as separate checkouts: main (`sources/panzer-os`), kimi/production-grade (`sources/panzer-os-kimi`), livevps-beta (`sources/panzer-os-livevps-beta`).
- **Source evidence:**
  - `git branch -a` — branches: main, kimi/production-grade, livevps-beta, panzer-os-beta, quadlet-deploy-overhaul, live-test/quadlet-reconcile
  - `sources/panzer-os-kimi/` — separate checkout (worktree or clone)
  - `sources/panzer-os-livevps-beta/` — separate checkout (worktree or clone)
- **Verdict:** ✅ CORRECT — panzer-os has 3 separate CBM-indexed checkouts

## Claim 7: Canonical docs in docs/canonical/

- **Wiki says:** Full architecture documentation in `docs/canonical/` including META-CONTROL-PLANE.md, SYSTEM-MODEL.md, ARCHITECTURE.md, DEPLOYMENT.md, etc.
- **Source evidence:**
  - `AGENTS.md` read order: `docs/canonical/META-CONTROL-PLANE.md` → `docs/canonical/SYSTEM-MODEL.md` → ... → `docs/canonical/DEPLOYMENT.md`
  - `docs/canonical/` — directory with multiple architecture docs
- **Verdict:** ✅ CORRECT

## Claim 8: CBM index present

- **Wiki says:** CBM index exists with ~267K nodes and ~398K edges.
- **Source evidence:**
  - CBM project `Users-admin-repos-knowledge-sources-panzer-os` — exists
  - `sources/panzer-os/` — source tree with shell scripts, docs/canonical/, Podman configs
- **Verdict:** ✅ CORRECT
