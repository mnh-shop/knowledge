---
name: panzer-os-livevps-beta-codegraph-verify
tags: [panzer-os, codegraph-verify, livevps-beta, agent-os, quadlet, deployment]
description: "Codegraph Verification: panzer-os-livevps-beta — validating wiki claims against indexed source code symbols"
source: sources/panzer-os-livevps-beta/
---

# Codegraph Verification: panzer-os-livevps-beta

**Date:** 2026-08-16

**Version checked:** `7c4bb518` (livevps-beta, `fix(lean-core): strip auto-start from all non-core quadlets...`)

**CBM project:** `Users-admin-repos-knowledge-sources-panzer-os-livevps-beta` (172,731 nodes, 307,510 edges)

## Claim 1: This is a git worktree of panzer-os tracking livevps-beta

- **Wiki says:** `sources/panzer-os-livevps-beta/` is a git worktree of the panzer-os repository, tracking `origin/livevps-beta`.
- **Source evidence:**
  - `sources/panzer-os-livevps-beta/.git` — contains `gitdir: /Users/admin/repos/knowledge/sources/panzer-os/.git/worktrees/panzer-os-livevps-beta`
  - `git branch -vv` — `* livevps-beta bd1190b7 [origin/livevps-beta: behind 47]` (pre-pull); post-pull: `7c4bb518 [origin/livevps-beta]`
  - `git remote -v` — `origin git@github.com:mnh-shop/panzer-os.git`
- **Verdict:** ✅ CORRECT — confirmed worktree of panzer-os tracking livevps-beta

## Claim 2: Latest commit strips auto-start from non-core quadlets

- **Wiki says:** Commit `7c4bb518` strips auto-start from all non-core quadlets including operational-postgres and pg-github-backup (ora-5).
- **Source evidence:**
  - `git log --oneline -1` — `7c4bb518 fix(lean-core): strip auto-start from all non-core quadlets incl operational-postgres/pg-github-backup (ora-5)`
  - CBM index excluded dirs: `["deploy", "docs/goclaw-docs/.claude"]` (count: 2)
- **Verdict:** ✅ CORRECT — commit message and scope match

## Claim 3: Large-scale service renames from central-* to clean names

- **Wiki says:** The worktree contains renames of container/volume names from `central-*` prefixed to clean names across multiple services.
- **Source evidence:**
  - `git diff main...livevps-beta` shows renames: `central-agentfield.container` → `agentfield.container`, `central-freellmapi.container` → `freellmapi.container`, `central-n8n.container` → `n8n.container`, `central-grafana.container` → `grafana.container`, `central-prometheus.container` → `prometheus.container`, `central-meta-postgres.container` → `meta-postgres.container`, `central-knowledge-postgres.container` → `knowledge-postgres.container`, `central-operational-postgres.container` → `operational-postgres.container`
  - Volume renames follow same pattern: `central-*-data.volume` → `*-data.volume`
- **Verdict:** ✅ CORRECT — renames confirmed in git history

## Claim 4: New alertmanager and firewall services added

- **Wiki says:** Addition of `alertmanager` quadlet service and `panzer-host-deploy-firewall` host service.
- **Source evidence:**
  - `services/observability/alertmanager/quadlet/alertmanager.container` — new file
  - `services/observability/alertmanager/quadlet/alertmanager-data.volume` — new file
  - `platform/host/systemd/system/panzer-host-deploy-firewall.service` — new file
  - `platform/host/libexec/panzer-host-deploy-firewall` — new file
  - `platform/host/libexec/99-panzer-netbird.conf` — deleted (replaced)
- **Verdict:** ✅ CORRECT — new observability and firewall services present

## Claim 5: CBM index is separate from main and kimi worktrees

- **Wiki says:** This worktree has its own separate CBM index distinct from `panzer-os` (main) and `panzer-os-kimi`.
- **Source evidence:**
  - CBM DB: `~/.cache/codebase-memory-mcp/Users-admin-repos-knowledge-sources-panzer-os-livevps-beta.db` (368M)
  - CBM DB for main: `~/.cache/codebase-memory-mcp/Users-admin-repos-knowledge-sources-panzer-os.db` (460M)
  - Different node counts: livevps-beta=172,731 vs main=267,663
- **Verdict:** ✅ CORRECT — separate DBs with different sizes and node counts

## Claim 6: Index excludes deploy/ and docs/goclaw-docs/.claude

- **Wiki says:** CBM index excludes `deploy` and `docs/goclaw-docs/.claude` directories.
- **Source evidence:**
  - CBM output: `"excluded":{"dirs":["deploy","docs/goclaw-docs/.claude"],"count":2,"truncated":false}`
- **Verdict:** ✅ CORRECT — exclusion confirmed in CBM output

## Claim 7: repo has scripts/panzer-create-project.sh

- **Wiki says:** New `scripts/panzer-create-project.sh` added.
- **Source evidence:**
  - `scripts/panzer-create-project.sh` — new file (create mode 100755 in git diff)
- **Verdict:** ✅ CORRECT — script present in worktree

## Claim 8: Worktree is behind main in merge direction

- **Wiki says:** `main` branch merges from `livevps-beta` via PRs (e.g. PR #14).
- **Source evidence:**
  - `sources/panzer-os/.git` main branch: `c60849ce Merge pull request #14 from mnh-shop/livevps-beta`
  - PR #14 merges livevps-beta into main
- **Verdict:** ✅ CORRECT — main has merge commit from livevps-beta
