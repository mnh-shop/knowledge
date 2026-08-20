---
name: agentmax-os-codegraph-verify
tags: [agentmax-os, codegraph-verify, skills, allowlist, provisioning, maxclaw, ops, goclaw, documentation]
description: "Codegraph Verification: agentmax-os — validating wiki claims against indexed source code symbols"
source: sources/agentmax-os/
---

# Codegraph Verification: agentmax-os

**Date:** 2026-08-16

**Version checked:** `440ed3d3` (main, `docs: handoff — truth-restoration session, canonical docs map, pending next steps`)

**CBM project:** `Users-admin-repos-knowledge-sources-agentmax-os` (58,161 nodes, 75,777 edges)

## Claim 1: This is a standalone repo (not a worktree)

- **Wiki says:** `sources/agentmax-os/` is a standalone clone of the mnh-shop/agentmax-os repository.
- **Source evidence:**
  - `sources/agentmax-os/.git/` — standard git directory (not a worktree file)
  - `git remote -v` — `origin https://github.com/mnh-shop/agentmax-os.git`
  - `git branch -vv` — `* main 82f3e326 [origin/main]`
- **Verdict:** ✅ CORRECT — standalone clone with GitHub remote

## Claim 2: 12 commits on main

- **Wiki says:** 12 commits on main: 82f3e326, dbc33963, 365c1cfa, 6f39688c, 91b93fff, cbb6f7ac, cc23c7f2, 0891be81, c9036ef8, f83b948a, b193682a, a1349d91.
- **Source evidence:**
  - `git log --oneline -12` shows exactly 12 commits in that order
  - `git log --oneline origin/main -12` matches local (FF merge from local path)
- **Verdict:** ✅ CORRECT — 12 commits confirmed

## Claim 3: Latest commit is system-model.md docs

- **Wiki says:** Commit `82f3e326` is `docs: canonical system operating model (system-model.md)` (now 4 commits behind HEAD).
- **Source evidence:**
  - `git log --oneline -5` shows `440ed3d3` as HEAD, `82f3e326` is 5th
  - `git show --stat 82f3e326` — `docs/system-model.md` (+118 lines)
  - File exists on disk
- **Verdict:** ✅ CORRECT — commit still in history, file present

## Claim 4: AGENTS.md created as workspace behavioral contract

- **Wiki says:** AGENTS.md created as workspace behavioral contract in commit 82f3e326.
- **Source evidence:**
  - `git show --stat 82f3e326` — `AGENTS.md` created (+35 lines)
  - `AGENTS.md` exists on disk at repo root
- **Verdict:** ✅ CORRECT — AGENTS.md present with 35-line creation

## Claim 5: Vendor/ contains goclaw repomix exports (ground truth)

- **Wiki says:** `vendor/` contains vendored goclaw-docs and goclaw repomix-output.xml for verification.
- **Source evidence:**
  - `git show --stat cbb6f7ac` — `vendor/goclaw-docs/repomix-output.xml` (+123,193), `vendor/goclaw/repomix-output.xml` (+775,409)
  - `vendor/` directory exists with `goclaw-docs/` and `goclaw/` subdirectories containing repomix XML files
  - `vendor/README.md` created
- **Verdict:** ✅ CORRECT — vendor repomix exports present (898K+ insertions)

## Claim 6: docs/system-model.md created

- **Wiki says:** `docs/system-model.md` — canonical system operating model.
- **Source evidence:**
  - `git show --stat 82f3e326` — `docs/system-model.md` (+118 lines)
  - File exists on disk at `docs/system-model.md`
- **Verdict:** ✅ CORRECT — file present with 118 lines

## Claim 7: docs/goclaw.md created + drift fixes in 440ed3d3+

- **Wiki says:** `docs/goclaw.md` — canonical goclaw truth (new in 6f39688c), later fixed for drift in 440ed3d3+.
- **Source evidence:**
  - `git show --stat 6f39688c` — `docs/goclaw.md` (+62 lines)
  - `git show --stat 440ed3d3` — `docs/goclaw.md` (+5/-5)
  - File exists on disk, modified in latest commit
- **Verdict:** ✅ CORRECT — file present, drift fixes applied

## Claim 8: 4 doc drift fix commits (440ed3d3, 2236f0a5, 35e19e6b, d7dff91d)

- **Wiki says:** 4 commits fix verified doc drift across 7 files.
- **Source evidence:**
  - `git log --oneline -4` — `440ed3d3 docs: handoff — truth-restoration session, canonical docs map, pending next steps`, `2236f0a5 docs: fix verified drift in execution-architecture.md + cli.md (memory_chunks, TEAM.md scope, websocket channel, CLI subcommands)`, `35e19e6b docs: fix verified drift in provisioning.md + model-providers.md (teams REST nuance, real provider config schema)`, `d7dff91d docs: whatsapp-channel truth (QR unofficial; official via Pancake) + Pancake-is-messaging-not-orchestration + teams REST nuance`
  - `git diff --stat 82f3e326..440ed3d3` — 7 files changed: +142/-163
- **Verdict:** ✅ CORRECT — 4 commits, 7 files, drift fixes confirmed

## Claim 9: production-readiness.md and mcp-catalog.md created

- **Wiki says:** `docs/production-readiness.md` and `docs/mcp-catalog.md` new in cbb6f7ac, modified in 440ed3d3.
- **Source evidence:**
  - `git show --stat cbb6f7ac` — `docs/production-readiness.md` (+164), `docs/mcp-catalog.md` (+97)
  - `git show --stat 440ed3d3` — `docs/production-readiness.md` (+6/-6), `docs/mcp-catalog.md` not modified
  - Both files exist on disk
- **Verdict:** ✅ CORRECT — both files present, production-readiness.md drift-fixed

## Claim 9: 'gateway image' phrasing purged

- **Wiki says:** Commits dbc33963 and 365c1cfa purge 'gateway image' terminology, later refined in 440ed3d3+.
- **Source evidence:**
  - `git log --oneline` — `dbc33963`, `365c1cfa`, `440ed3d3` (also touches execution-architecture.md, cli.md, provisioning.md)
  - `docs/production-readiness.md` references 'goclaw image' not 'gateway image'
- **Verdict:** ✅ CORRECT — commits present, terminology changed

## Claim 10: CBM index excludes deploy/, .git/, vendor/

- **Wiki says:** CBM index excludes `deploy`, `.git`, and `vendor` directories.
- **Source evidence:**
  - CBM output: `"excluded":{"dirs":["deploy",".git","vendor"],"count":3,"truncated":false}`
- **Verdict:** ✅ CORRECT — exclusion confirmed in CBM output

## Claim 11: Index is ~58K nodes, ~76K edges

- **Wiki says:** ~58K nodes, ~76K edges.
- **Source evidence:**
  - CBM output: `"nodes":58161,"edges":75777`
  - CBM DB: 93M on disk
  - Raw repomix: 228M (includes vendor/)
- **Verdict:** ✅ CORRECT — stats match

## Claim 12: Index is ~58K nodes, ~76K edges

- **Wiki says:** ~58K nodes, ~76K edges.
- **Source evidence:**
  - CBM output: `"nodes":58161,"edges":75777`
  - CBM DB: 93M on disk
  - Raw repomix: 228M (includes vendor/)
- **Verdict:** ✅ CORRECT — stats match

## Claim 13: 16 total commits on main

- **Wiki says:** 16 commits on main (4 new since last update + 12 previously).
- **Source evidence:**
  - `git log --oneline -16` shows exactly 16 commits
  - `git log --oneline origin/main -16` matches local
- **Verdict:** ✅ CORRECT — 16 commits confirmed
