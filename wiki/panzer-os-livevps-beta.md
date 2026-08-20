---
name: panzer-os-livevps-beta
tags: [agent-os, multi-agent, postgres, pgvector, podman, quadlet, goclaw, hermes, agentfield, rootless, deployment, livevps]
description: "Wiki entry for panzer-os livevps-beta worktree — rootless-first multi-agent operating system"
source: sources/panzer-os-livevps-beta/
verification_date: 2026-08-16
verified_by: codegraph-verify
---

# panzer-os-livevps-beta

||| Field | Value |
|||---|---|
||| **Origin** | [mnh-shop/panzer-os](https://github.com/mnh-shop/panzer-os) |
||| **Branch** | `livevps-beta` |
||| **Commit** | `7c4bb518` — `fix(lean-core): strip auto-start from all non-core quadlets incl operational-postgres/pg-github-backup (ora-5)` |
||| **License** | See repo LICENSE |
||| **Source** | `sources/panzer-os-livevps-beta/` |
||| **Type** | Git worktree of `panzer-os` (gitdir: `sources/panzer-os/.git/worktrees/panzer-os-livevps-beta`) |
||| **CBM index** | `Users-admin-repos-knowledge-sources-panzer-os-livevps-beta` (~172K nodes, ~307K edges) |

## What is it?

This is the `livevps-beta` branch of panzer-os, maintained as a git worktree alongside the main checkout. It tracks experimental/beta changes for live VPS deployment that are not yet merged into `main`.

## Relationship to main

- Shares the same git history as `sources/panzer-os/` (same repository, different worktree)
- `main` branch merges from `livevps-beta` via PRs (e.g. PR #14)
- This worktree tracks `origin/livevps-beta`; `main` tracks `origin/main`

## Latest changes (7c4bb518)

- Stripped auto-start from all non-core quadlets including `operational-postgres` and `pg-github-backup` (issue ora-5)
- Large-scale asset reorganization: renames of container/volume names from `central-*` prefixed to clean names across n8n, postgres, observability, agentfield, freellmapi services
- Addition of `alertmanager` quadlet service, `panzer-host-deploy-firewall` host service
- New `scripts/panzer-create-project.sh`
- Removal of many deprecated proposal docs and workflow catalog entries
- Renamed `services/agentfield/quadlet/central-agentfield.container` → `agentfield.container`

## CBM index

This worktree has its own separate CBM index distinct from `panzer-os` (main) and `panzer-os-kimi`. The index captures the `livevps-beta` branch state at commit `7c4bb518`.

## Verification

See [[panzer-os-livevps-beta.codegraph-verify]] for evidence-backed claims.
