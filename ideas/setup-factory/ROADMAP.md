---
name: setup-factory-roadmap
description: "Setup Factory build roadmap — current state, phases, build order, and future goals. Workspace prototype."
tags: [ideas, deployment, setup-factory, roadmap]
source: workspace/deployment-setup-automation/setup-factory/ROADMAP.md
---

> **⚠️ Workspace prototype planning document — not a committed plan.**
> Current state as of 2026-06-25. Many items may be superseded by production work.

# Roadmap

## Current state (2026-06-25)

### What's been built (✅ done)

- **5 base images:** setup-factory/python-base:3.13 (344MB), af-deep-research:3.13 (514MB), swe-af:3.13 (2.71GB), hermes-agent-lightweight:3.13 (663MB), browser-worker (copied from upstream)
- **10 service modules** with full Containerfiles + fragments: hermes-agent-lightweight, af-deep-research, swe-af, browser-worker, postgres, redis, n8n, agentfield, openclaw, alphaclaw
- **4 RAM preset YAMLs** (floor, minimum, standard, performance) with mutual exclusion enforcement
- **7 new docs:** DEPLOYMENT-PITFALLS.md, RAM-SIZING.md, NIX.md, CLAUDE-CODE-TELEGRAM.md, secrets.md, HOST-SETUP.md, deployment-differences.md, methods.md, agentfield.md
- **Renderer + secrets pipeline:** render-stack.sh, secrets-init.sh, secrets-gen.sh, secrets-helpers.sh
- **Rootless verifier:** test-rootless.sh (6 tests)
- **Per-flavor skill map:** 13 core + 4 flavor-specific skills (from exp-10)
- **ROADMAP updated** with 5 future goals (NixOS, OCI artifacts, multi-instance, bootc, agentfield as control plane)

### What's in progress (⏳ running)

- **bin/setup-pi** — Pi setup script (uncommitted, in bin/)
- **free-claude-code-telegram module** — service module (uncommitted, in docs/)
- **browser-worker module** — copied from upstream (uncommitted, in services/browser-worker/)
- **Test scripts (fix-38)** — results pending, will feed into next roadmap update

### What's pending (❌ not started)

- ARM64 cross-compile for hermes-agent-lightweight (Pi 3B+ ARM64 builds via OrbStack VMs)
- Test bin/setup-pi in OrbStack ARM64 VMs (Pi dev, RasPiOS Lite, Alpine)
- Render + deploy + verify the full pipeline (per lib-2's test plan)
- Document the verified pipeline in docs/DEPLOY-ON-PI.md
- Per-flavor skill artifacts (OCI, deferred earlier)

### Next steps (priority order)

1. Wait for current tasks to land (bin/setup-pi, free-claude-code-telegram module, browser-worker module, test scripts)
2. Commit + push everything to origin/main
3. Run the test scripts (already in progress, fix-38)
4. Apply any fixes from test results
5. ARM64 cross-compile for hermes-agent-lightweight
6. Test bin/setup-pi in OrbStack ARM64 VMs
7. Render + deploy + verify (lib-2's test plan)
8. Document DEPLOY-ON-PI.md

## Status

| Phase | Deliverable | Status |
|---|---|---|
| 0 | Cancel fix-2, update deepwork plan with expanded knowledge sources | done |
| 1 | Schema + catalogs: manifest v1, services, presets (RAM/arch/OS/isolation), blueprints, compatibility rules, validator | done |
| 2 | Onboarding script: interactive wizard with live RAM table, arch auto-detect, dependency resolution | in progress |
| 3 | Service modules: one folder per service (postgres, redis, n8n, agentfield, hermes-agent, openclaw, alphaclaw, af-deep-research, swe-af, browser-worker) with fragments per runtime | done |
| 4 | Runtime renderers: docker-compose, podman-compose, podman-quadlet (via podlet), bootc (tank-os-style), bare-metal | done |
| 5 | Deployment scripts: deploy-docker, deploy-podman, deploy-quadlet, deploy-bootc, deploy-bare-metal, secrets-init, verify, drift, teardown | done |
| 6 | Flavors: osint, swe, research, browser-automation as additive overlays | done |
| 7 | Examples: mac-arm64, linux-amd64, linux-arm64-pi-lite, agentfield-only, fedora-atomic-hardened | done |
| 8 | CI: validate-manifest, render-smoke, security-scan, examples-suite | pending |
| 9 | Docs: architecture, host-classes, os-support, runtime-targets, isolation-levels, flavor-system, security-model, quadlet-migration, fedora-atomic-notes, ubuntu-debian-notes, verification | pending |
| 10 | Polish: v0.1.0 release, migration guides from h-coderstack-docker and agent-control-stack | pending |

## Phase 1 deliverable (detailed)

- Schema v1 with isolation, deviceBudgetOverride, services.<name>.mode, imageSource
- RAM model: floor / minimum / standard / performance + device-budgets.yaml
- Isolation presets: standard / hardened / tank-style-rootless
- 11 blueprint templates in manifests/blueprints/
- Compatibility rules: rules/compatibility.yaml (16 rules)
- Validator: rules/validator.sh (executable)
- Secret scanner: rules/secret-scanner.sh (executable)
- Parity checker: rules/parity-checker.sh (executable)

## Axes of variation

| Axis | Values | Count |
|---|---|---|
| Host | macos-arm64, linux-arm64, linux-amd64 | 3 |
| OS | ubuntu, debian, fedora-atomic, macos | 4 |
| Runtime | docker-compose, podman-compose, podman-quadlet, bootc, bare-metal | 5 |
| Isolation | standard, hardened, tank-style-rootless | 3 |
| RAM preset | floor, minimum, standard, performance | 4 |
| Blueprint | 11 named templates | 11 |
| Flavor | osint, swe, research, browser-automation | 4 (multi-select) |
| Exposure | localhost-only, tailscale, ssh-tunnel, reverse-proxy | 4 |

## Locked decisions

- Auto-detect arch (uname -m) in the wizard, user can override
- SQLite vs Postgres is a choice the wizard presents, not an automatic strip-down
- Heavy lanes (af-deep-research, swe-af) are shown in the wizard on small devices, marked "won't fit"
- Orchestrator model for the user's opencode runtime: opencode-go/minimax-m3 with variant: high

## YAGNI (deferred to v2)

- Kube/.kube Quadlet output
- Sablier scale-to-zero
- Reverse proxy scaffolding (Caddy/Traefik)
- Multi-region / multi-host manifests
- Windows / WSL2
- A second model router
- Auto-promotion of overnight candidates
- Nix / sops-nix integration

## Risk list

1. Real-looking secrets in h-coderstack-docker/.env — scrub on move
2. Two competing manifest kinds in the seed — deprecate explicitly
3. Validator absent — ship fixtures with first commit
4. Quadlet output complexity — podlet for bulk, hand-author the awkward 3-4
5. Fedora Atomic gotchas — document before declaring supported
6. macOS cannot run Quadlet — hard rule in validator
7. Examples are instances, not canonical — render on demand
8. Secret handling split — compose uses env, quadlet uses Secret=
9. No drift detection — ship apply→snapshot loop with first quadlet
10. Field naming divergence — one canonical name, migration table
11. setup-artifact.rtf (296 KB) — move to sources/, hash, never edit
12. Repo is not yet a Git repo — initial commit is docs + schema only
13. Knowledge references will drift — references/ are pinned snapshots
14. DOCKER_DEFAULT_PLATFORM hard-coded in example — let preset drive it
15. OSINT vs browser-automation — keep separate flavours

## Build order

Same as the phase table at the top.

## Future Goals & Ideas

Items here are brainstorming — not committed, not scheduled. Capture the
"what if" thinking so future work has a starting point.

### 💡 NEXT: NixOS deployment

Research done: /tmp/exp-nixos-build.md + docs/NIX.md

Declarative, reproducible, atomic upgrades via `nixos-rebuild`. Python
ecosystem has excellent Nix support, which makes hermes-agent (with
its 30+ pinned Python deps in pyproject.toml) an especially good fit —
we could derive a Nix expression from pyproject.toml automatically.

Concrete next step: a Nix flake at `setup-factory/nix/` that produces a
NixOS module declaring all 11 services with their flavors + RAM
presets. State under `/var/lib/setup-factory/` (or $HOME for
rootless). Image: `docker.io/setup-factory/nixos:latest` or
`ghcr.io/mnh-shop/setup-factory-nixos:latest`.

Status: not started. Blocked on: NixOS knowledge in the team.

### 💡 IDEA: Per-flavor skill artifacts (OCI)

Per exp-10's per-flavor skill bundles (osint/swe/research/browser-automation),
turn each into an OCI artifact (`setup-factory/hermes-skills-swe:2026.06.25`,
etc.) so the hermes-agent-lightweight image can self-install on first run.

Image becomes minimal (~200-250MB, no skills baked in). First-run script
reads $HERMES_FLAVOR, pulls the matching artifact, extracts to
$HERMES_HOME/skills/. Renderer passes the flavor as an env var from
the manifest.

Status: deferred (after deployment verification is solid).

### 💡 IDEA: Multi-instance rootless podman support

subuid exhaustion at 6-10 instances is a known limit (see
docs/DEPLOYMENT-PITFALLS.md pitfall #2). Need:
- Per-instance state dirs: `~/.local/share/${STACK}/${SVC}/`
- Per-instance secret names: `${STACK}_${SVC}_${KEY}`
- Per-instance port allocation (port-offset or random)
- subuid isolation strategies (e.g., one user per stack)

Status: design not started. Needed for horizontal scaling.

### 💡 IDEA: bootc production deployment (Fedora Atomic)

Bake setup-factory into a bootc image. Atomic upgrades via
`bootc switch --apply`. State must live under $HOME or in named volumes
(per AGENTS.md). Per-user/per-machine secrets via the tank-os
`tank-openclaw-secrets` pattern (we have tank-os in our knowledge
base — see /Users/admin1/Documents/knowledge/sources/tank-os/).

Image target: Fedora 41 Atomic + bootc + the 3 owned services.

Status: AGENTS.md mentions bootc as a target. Not yet a renderer output.

### 💡 IDEA: agentfield as a control plane

agentfield (control plane + Go/Python/TS SDKs) is a natural fit for
orchestrating our other agents (af-deep-research, swe-af, hermes-agent).
Question: can we register hermes-agent as an agentfield sub-agent?
Would let us run multi-agent workflows (e.g., swe-af delegates research
to af-deep-research, all visible in agentfield's UI).

Status: architectural question, needs evaluation. agentfield is already
in our service catalog (docker.io/agentfield/control-plane:latest).