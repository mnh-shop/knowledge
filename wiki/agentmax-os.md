---
name: agentmax-os
tags: [agent-os, goclaw, bootc, quadlet, multi-agent, drone-defense, hitl, postgres, pgvector, podman, skills]
description: "Wiki entry for agentmax-os (goclaw-tank-os) — self-hosted rootless-Podman multi-agent gateway with 58 pre-built stacks"
source: sources/agentmax-os/
verification_date: 2026-08-16
verified_by: codegraph-verify
---

# agentmax-os

||| Field | Value |
|||---|---|
||| **Origin** | [mnh-shop/agentmax-os](https://github.com/mnh-shop/agentmax-os) |
||| **Version** | `0.2.0` (VERSION) |
||| **Commit** | `82f3e326` — `docs: canonical system operating model (system-model.md)` |
||| **License** | See repo LICENSE |
||| **Source** | `sources/agentmax-os/` |
||| **Branches** | `main` |
||| **CBM index** | `Users-admin-repos-knowledge-sources-agentmax-os` (~58K nodes, ~76K edges) |

## What is it?

agentmax-os (internally `goclaw-tank-os` per README) is a self-hosted, rootless-Podman multi-agent gateway built around goclaw. It provides a bootc-image or quadlet-based deployment path on Fedora/RHEL, a modular stack system with 58 pre-built agent teams, and a drone-defense / C-UAS stack set that is **detect-not-destroy** with a human-in-the-loop (HITL) approval gate on every consequential action.

## Architecture

```
bootc image ──► unit registry ──► stack catalogs ──► provisioner
(minimal base)   (80 units)        (58 stacks)        (install-stacks.py)

┌────────────────────────────────────────────────────────────────────┐
│ bootc image (Fedora 44) — minimal base, auto-start at boot          │
│   gateway (goclaw) + postgres (pgvector) + service-gator + mcpo     │
├────────────────────────────────────────────────────────────────────┤
│ unit registry  assets/registry/units/*.yaml  (80 units)             │
│   lazy on-demand MCP servers + tool containers, digest-pinned,      │
│   license-flagged (license / license_verified / copyleft_isolated)  │
├────────────────────────────────────────────────────────────────────┤
│ stack catalogs  assets/stacks/*/catalog.yaml  (58 stacks)           │
│   teams / agents / skills / prompts; declare required units by name │
├────────────────────────────────────────────────────────────────────┤
│ provisioner  assets/install-stacks.py                               │
│   license gate → skills gate → lazy render+start → ports/network    │
│   resolution → gateway MCP registration (dry-run first by default)  │
└────────────────────────────────────────────────────────────────────┘
```

- **14 fixed-subnet networks** (`*.network` quadlets, `10.89.x.0/24`): gateway, firecrawl, redteam, drone, print, fusion, target, interceptor, mfg, comms, firecontrol, intel, media, ops
- **Approval-gate HITL primitive** — `request_approval → resolve(PASS|HOLD|FAIL) → get_receipt`; receipts are append-only and sha256 hash-chained
- **Local-build convention** — each self-authored service lives under `bootc/<name>/`, builds to a `localhost/<name>` image, referenced with `pull: never`

## Deployment modes

1. **Quadlet mode** — rootless Podman on existing Fedora/RHEL host (`./install.sh --mode quadlet`)
2. **Bootc mode** — replaces the OS with a custom Fedora 44 image

## The defense stack set (7 stacks, shared HITL contract)

|| Stack | Purpose |
||---|---|
|| `drone-defense-lab` | Own-aircraft/facility SITL lab: ArduPilot mission dev, MAVLink/telemetry, geofencing, ADS-B + RF correlation, RID logging. Actuation off; detect-not-destroy. |
|| `parametric-print-ops` | Design → slice → print pipeline (OpenSCAD, mesh QA, PrusaSlicer, printer dispatch). Every printer action approval-gated. |
|| `airspace-picture-fusion` | Fuses PX4 SITL + radar + TAK COP + vision (YOLOX/ByteTrack) + Stone Soup into one receive-only own-facility airspace picture + alert bus. |
|| `targeting-coordination` | Human-on-the-loop targeting decision support: track correlation vs ROE, candidate target folders. No autonomous engagement. |
|| `interceptor-coordination` | Interceptor mission coordination: assignment to already-approved targets only; SITL-only guidance; EW deconfliction/avoidance only. |
|| `fire-control` | Fire-mission management + DEW aimpoint + BDA logging. Software-only: no actuation, no kinetic ballistics. |
|| `drone-manufacturing-ops` | Production MES over the print farm: queue/schedule, QC gate, BOM/parts ledger, serialized traceability. Every action approval-gated. |

**Shared HITL contract:** `approval-gate.request_approval` → human resolves with PASS receipt before anything consequential happens. No autonomous engagement, release, or fire; EW is deconfliction-only; fire control is software-only.

## License posture

Open-source-first (enforced in `assets/registry/licenses.yaml`): PX4 (BSD-3-Clause) over ArduPilot (GPL-3.0); YOLOX (Apache-2.0) + ByteTrack (MIT) over AGPL alternatives; Valkey (BSD-3-Clause) over Redis (RSAL/SSPL). Copyleft components run as isolated containers on their own network behind an API boundary (`copyleft_isolated`).

## Skills system

The project ships a large skills collection under `assets/skills/` organized by domain:

- **blueteam** — dcom-hunting, anomalous-auth, log-analysis, osquery-endpoint-monitoring, splunk-kql, threat-modeling
- **redteam** — bug-identification, ctf-osint, dns-c2-detection, forensics, org-attack-surface, osint-methodology, reconnaissance, techstack
- **journalism** — data-journalism, foia-requests, social-media-intelligence
- **swe** — emergency-rescue, swe-code-review

Latest commit (`a1349d91`) performs an allowlist burn-down: archives 3 skills, splits 20 oversized skills, and updates `assets/registry/oversized-skills-allowlist.txt`. Subsequent commits (`b193682a`) further deduplicate skills and remove leftover growth prompts.

## Documentation (9 new commits since a1349d91)

The last 9 commits focus heavily on canonical documentation and verification against vendor/ ground truth:

- **system-model.md** — canonical system operating model (`82f3e326`)
- **goclaw image phrasing** — purged 'gateway image' terminology throughout; it is the goclaw image (`dbc33963`, `365c1cfa`)
- **docs/goclaw.md** — canonical goclaw truth + AGENTS.md anti-drift facts + verified multi-tenant mechanics (`6f39688c`)
- **goclaw mirror bump** — v3.15.0-beta.193 → v3.15.0-beta.196 (`91b93fff`)
- **Hallucination fixes** — two verified hallucinations fixed against vendor/ repomix ground truth (`cbb6f7ac`)
- **production-readiness.md** — new production readiness doc (`cbb6f7ac`)
- **mcp-catalog.md** — new MCP catalog doc (`cbb6f7ac`)
- **vendor/** — vendored goclaw-docs and goclaw repomix-output.xml for ground-truth verification (`cbb6f7ac`)

## Key files

- `README.md` — full architecture doc, quickstart, stack descriptions
- `VERSION` — `0.2.0`
- `AGENTS.md` — workspace behavioral contract (new in 82f3e326)
- `assets/registry/licenses.yaml` — license enforcement catalog
- `assets/registry/oversized-skills-allowlist.txt` — skills allowlist
- `assets/install-stacks.py` — stack provisioner (dry-run default)
- `install.sh` — quadlet install handler
- `preinstall.sh` — platform detection + mode recommendation
- `deploy/` — Kubernetes ApplicationSet + containerdisk + base configs
- `bootc/` — 30+ self-authored bootc MCP/tool container definitions
- `vendor/` — vendored goclaw repomix exports (ground truth for verification)
- `docs/` — architecture-overview, provisioning, model-providers, execution-architecture, multi-tenant-architecture, quickstart-prebuilt, build, ops, wayfinder
- `docs/system-model.md` — canonical system operating model (new in 82f3e326)
- `docs/goclaw.md` — canonical goclaw truth (new in 6f39688c)
- `docs/production-readiness.md` — production readiness doc (new in cbb6f7ac)
- `docs/mcp-catalog.md` — MCP catalog (new in cbb6f7ac)
- `ops/` — backup + health systemd units (maxclaw-backup, maxclaw-health), ops README

## Key commits

- `440ed3d3` — docs: handoff — truth-restoration session, canonical docs map, pending next steps
- `2236f0a5` — docs: fix verified drift in execution-architecture.md + cli.md (memory_chunks, TEAM.md scope, websocket channel, CLI subcommands)
- `35e19e6b` — docs: fix verified drift in provisioning.md + model-providers.md (teams REST nuance, real provider config schema)
- `d7dff91d` — docs: whatsapp-channel truth (QR unofficial; official via Pancake) + Pancake-is-messaging-not-orchestration + teams REST nuance
- `82f3e326` — docs: canonical system operating model (system-model.md)
- `dbc33963` — docs: last 'gateway image' -> 'goclaw image' (production-readiness)
- `365c1cfa` — docs: purge 'gateway image' phrasing — it is the goclaw image (AGENTS.md naming rule)
- `6f39688c` — docs: canonical goclaw truth (docs/goclaw.md) + AGENTS.md anti-drift facts + verified multi-tenant mechanics
- `91b93fff` — chore: bump goclaw mirror pin v3.15.0-beta.193 → v3.15.0-beta.196
- `cbb6f7ac` — docs: fix two verified hallucinations against vendor/ repomix ground truth
- `cc23c7f2` — docs(client-delivery): apply lib-1 fact-check corrections + confirm tenant deletion
- `0891be81` — feat(ops): rename OS login goclaw -> maxclaw (uid 1000, home unchanged) + restore-drill evidence
- `c9036ef8` — fix(ops): backup script must cd /tmp before rootless podman
- `f83b948a` — feat(ops): adopt + harden live host backup/health units (env-based, no secrets)
- `b193682a` — fix(docs/hygiene): recover HANDOFF corruption, correct TESTING-MATRIX counts, dedupe skill, remove leftover growth prompts
- `a1349d91` — chore(skills): allowlist burn-down — archive 3, split 20 oversized skills

## CBM index

CBM index captures the `main` branch at commit `440ed3d3` with ~58K nodes and ~76K edges. Excludes `deploy/`, `.git/`, and `vendor/` (the vendored goclaw repomix exports).

## Verification

See [[agentmax-os.codegraph-verify]] for evidence-backed claims.
