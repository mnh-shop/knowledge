---
name: panzer-os-kimi-architecture
tags: [agentfield, architecture, bootc, deployment, goclaw, hermes-agent, multi-agent, networking, podman, postgres, quadlet, systemd, panzer-os-kimi]
description: "Panzer OS Architecture — operational core of the rootless multi-agent OS: three-zone topology, shared Postgres spine, 10-network CIDR map, panzerctl/deploy wizard, registrar model, day-2 ops"
source: sources/panzer-os-kimi/
---

# Panzer OS Architecture

## Overview

Panzer OS (indexed as `panzer-os-kimi`; upstream `mnh-shop/panzer-os.git`) is a rootless-first, modular multi-agent operating system for deploying AI agent stacks at scale on Podman Quadlets (README.md:9-10). Everything runs under a dedicated `panzer` user via systemd user units — no root daemons, no privileged containers (README.md:33-34). The full stack packages as a bootc OCI image that boots into raw/QCOW2 VM disk images.

## Architecture Principles

- **Rootless everywhere.** All services under a dedicated `panzer` user via systemd user units (Quadlets) (README.md:152-153).
- **Three Postgres instances, three concerns.** Meta (control-plane), Operational (workload), Knowledge (RAG). Never mixed (README.md:154-155).
- **Three independent lanes.** AgentField, hermes, goclaw — share ONLY Postgres. Never route through each other. AF ecosystem registers for tracking only (README.md:156-157).
- **Single-host first, multi-host optional.** Default on one VPS; NetBird mesh VPN for worker hosts (README.md:158-159).
- **One image per family.** Every hermes stack shares one image; every goclaw stack shares one. Stacks differ by config, secrets, and volumes (README.md:160-161).
- **Provision ≠ register.** A provisioned stack has a DB schema and secrets; a registered stack has working agents. Both are required (README.md:474-475).

## Three-Zone Architecture

The system organizes into zones reflecting increasing isolation (README.md:258-264):

| Zone | Name | State | Trust | Examples |
|------|------|-------|-------|----------|
| **A** | Spine | Always running | Tightly controlled — no direct external exposure | 3× Postgres, central-agentfield, goclaw-as-meta-partner, goclaw-librarian, central-freellmapi, tuwunel, knowledge-mcp, hermes-admin-mcp, pg-admin-mcp, panzer-control-mcp |
| **B** | Dispatch | On-demand | Ephemeral, per-workload | hermes-agent@stack, goclaw@stack, AF nodes |
| **C** | Execution | On-demand (singletons) | Fully isolated — `NoNewPrivileges`, egress firewalls | panzer-opencode-runtime, panzer-pi-runtime, panzer-zot-runtime, searxng, osint-mcp-server, playwright-mcp, docs-mcp, service-gator, llm-wiki |

Zone A hosts the spine (always-running control plane); Zone B hosts per-workload dispatch stacks (hermes/goclaw/AF); Zone C hosts hardened singleton execution runtimes and MCP tool servers.

## 10-Network CIDR Topology Map

Ten dedicated Podman networks by trust zone (README.md:309-321):

| Network | CIDR | Zone | Key Rule |
|---------|------|------|----------|
| `meta-internal` | 172.20.5.0/24 | A | Spine control plane — **NO goclaw@ stacks, NO harnesses** |
| `knowledge-internal` | 172.20.7.0/27 | A | Knowledge tier — **NO agents**, only librarian + knowledge-mcp |
| `panzer-data` | 172.20.4.0/28 | — | Cross-zone DB access bridge (sanctioned) |
| `panzer-hermes` | 172.20.3.0/24 | B | hermes stacks, tuwunel, hermes-admin-mcp |
| `panzer-goclaw` | 172.20.6.0/24 | B | goclaw stacks, meta-partner reachability |
| `panzer-harness` | 172.20.10.0/28 | C | Hardened coding runtimes |
| `panzer-af` | 172.20.13.0/28 | B | AF reasoner isolation |
| `panzer-mcp-tools` | 172.20.11.0/24 | C | MCP tool servers (docs-mcp, service-gator, knowledge-mcp) |
| `panzer-search-backend` | 172.20.12.0/28 | C | searxng, osint-mcp-server, playwright-mcp |
| `panzer-ui` | 172.20.20.0/28 | — | Web UIs — agentfield, n8n, dashboard, pgweb |

## Zero-Trust Networking

- **No network exposure to host** — all published ports loopback-bound (`127.0.0.1` only)
- **Egress control** via nftables allowlist (approved destinations only)
- **L0 harnesses never join `meta-internal` or `knowledge-internal`** — tools via `panzer-mcp-tools`, LLM egress only
- **Knowledge reachable only through `knowledge-mcp`** — no direct Postgres access from dispatch/execution zones
- **Per-stack tenant isolation** — dedicated role + schema per goclaw stack
- **Secrets** via Podman secrets, synced from `~/.config/panzer-os/secrets/`
- Container security: `NoNewPrivileges=true`, `DropCapability=ALL`, `UserNS=keep-id` or explicit UID mapping

(README.md:324-333)

## Shared Postgres Spine + Tenant Schema Isolation

Three instances for three data concerns (README.md:234-245):

| Instance | Port | Databases | Purpose |
|----------|------|-----------|---------|
| `central-meta-postgres` | 35432 | `agentfield`, `panzer_ledger`, `panzer_registry`, `goclaw_meta` | Control plane — spine services only |
| `central-operational-postgres` | 15432 | `goclaw` (tenant_* schemas), `n8n`, `panzer_profiles` | Workload — goclaw stacks, n8n, profiles |
| `central-knowledge-postgres` | 25432 | `panzer_knowledge*`, `goclaw_librarian` | RAG/embeddings — knowledge-mcp reads, librarian writes |

All run `pgvector/pgvector:0.8.4-pg18-bookworm`. Postgres is **shared across lanes (schema-isolated)** — not one DB per lane (README.md:96, 156).

**Goclaw tenant isolation** (`docs/canonical/POSTGRES-SCHEMA.md:103-108`): per stack — dedicated role `goclaw_<stack>_rw`, schema `tenant_<stack>`, `search_path` scoping, default privileges. DSN encodes scope: `postgres://goclaw_<stack>_rw:...@central-operational-postgres:5432/goclaw?sslmode=disable&search_path=tenant_<stack>,public`.

**Why three — not mergeable:** a runaway goclaw tenant query could block agentfield heartbeats (control+workload); 50K embedding rows compete with kanban writes for buffer cache (workload+knowledge); different backup cadence and data volume (control+knowledge) (README.md:247-251).

## Dispatch Lanes

| Lane | Job | Task Ingress |
|------|-----|-------------|
| **AgentField (+ AF ecosystem)** | Node registry, heartbeats, DID/VC identity, async execution for AF reasoners | `POST /api/v1/execute/async/<node>.<reasoner>` (REST API) |
| **Hermes-agent** | L2 kanban orchestrator + L1 workers per stack; human via Matrix | Matrix room (tuwunel) or `hermes-admin-mcp` |
| **GoClaw lower layer** | Per-tenant agent gateway + catalog agents | `POST /v1/chat/completions` (REST webhook — consumes MCP, does not expose task MCP) |

Lanes share ONLY Postgres; they never route through each other. AF ecosystem instances register with AgentField for tracking only — no dispatch relationship with hermes or goclaw (README.md:167-180).

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

## Resource Budget

**8GB VPS** (README.md:416-417): Spine ~2GB, Hermes stacks ~1GB each, Goclaw stacks ~500MB each, Hardened runtimes ~1GB each, Tool MCP servers ~500MB total.

**Scale-out triggers:** RAM < 8GB, > 4 concurrent hermes stacks, dedicated AF nodes, geographic distribution (README.md:419-420).

## Operator Tooling

### panzerctl — unified operator CLI (`scripts/panzerctl`)

Single entrypoint for all day-to-day operations; delegates to existing `scripts/panzer-*.sh` scripts ("a frontend, not a rewrite"). The `scripts/` tree holds 61 operator scripts — 29 top-level `panzer*.sh` plus 4 more in `scripts/lib/` — covering deploy, register, backup, migrate, rotate-secret, quadlet reconcile/rollback, log-collector, DR drill, topology audit, and live-spine checks.

```bash
scripts/panzerctl status               # System health overview
scripts/panzerctl deploy               # Staged deployment of all services
scripts/panzerctl stack up hermes@<name>
scripts/panzerctl stack up goclaw@<name>
scripts/panzerctl stack down <name>
scripts/panzerctl provision research   # Deploy tool MCP servers (searxng, docs-mcp, etc.)
scripts/panzerctl deploy n8n           # Deploy n8n workflow automation
```

### panzer-deploy — deployment wizard (`scripts/panzer-deploy`)

Thin dispatcher with two modes: interactive (menu-driven category selection) and CLI (`panzer-deploy hermes|goclaw|agentfield [--stack <template>] [--instance NAME]`). Subcommands delegate to `scripts/lib/panzer-deploy-<subcommand>.sh`.

### Staged Make targets

`make deploy-foundation` (Tier 0) → `deploy-meta` (Tier 1) → `deploy-n8n` (Tier 2, opt-in) → `deploy-hermes` (Tier 3, opt-in) → `deploy-harnesses` (Tier 4, opt-in) → `deploy-runtimes`/`deploy-research` (opt-in) → `deploy-all-required` (foundation through runtimes, skipping opt-ins).

## Registrar Model — provision ≠ register

Stack lifecycle: **provision** (DB role + schema + secrets + migrations) → **start** (container) → **register agents** (registrar). A running container with unregistered agents is an empty gateway — the registrar is what populates agents (README.md:463-475).

- Lower-layer goclaw stacks: `panzer-stack-up.sh` materialize phase runs the `localhost/goclaw-registrar:latest` image with the stack's gateway token and catalog
- Meta/librarian: `install.sh` + `panzer-register-goclaw-catalogs.sh meta|librarian`
- AF ecosystem: auto-registers via SDK on startup; also `POST /api/v1/nodes/register-serverless`

**Dual deployment paths** (AGENTS.md — both are production requirements): Path 1 — goclaw meta agents (MCP): `goclaw-fleet-manager → panzer-control-mcp.deployment_propose` → human approve → materialize. Path 2 — scripts (fallback): `bash scripts/panzer-deploy goclaw --stack <template> --instance <name> --yes`.

## Day-2 Operations

| Check | Command |
|-------|---------|
| Spine services | `systemctl --user list-units 'panzer-*' --no-pager` (expect all active) |
| Agent list (non-empty) | `curl -H "Authorization: Bearer \$TOKEN" -H "X-GoClaw-Tenant-Id: <id>" -H "X-GoClaw-User-Id: system" http://goclaw-<id>:18790/v1/agents` |
| Registrar image | `podman image exists localhost/goclaw-registrar:latest` |
| Database reachability | `pg_isready -h 127.0.0.1 -p 35432 -U panzer` (and 15432, 25432) |
| LLM key health | `bash scripts/openrouter-key-health.sh` |

(README.md:477-485)

## Services Map (17 categories)

`services/` organizes 17 categories: **agentfield, backup, dashboard, execution, goclaw, hermes, llm-gateway, log-collector, matrix, mcp, n8n, netbird, observability, postgres, quadlet, shared, templates**. Each category carries `quadlet/` subdirectories with `.container` / `.network` / `.volume` units. Service taxonomy, secrets reference, and image pins live in `docs/canonical/SERVICE-TAXONOMY.md`; the dependency graph in `docs/canonical/DEPLOYMENT-ORDER.md`.

## Secrets Handling

- Repo: `secrets/` reference dir; `deploy/seed-secrets.sh` generates tokens, DSNs, encryption keys at install
- Runtime: Podman secrets mounted into Quadlet containers via drop-in `.conf` files generated by `sync-podman-secrets`
- Reconciliation: `sync-podman-secrets` syncs `~/.config/panzer-os/secrets/*.txt` → Podman secrets; user-level `panzer-sync-secrets.service` recovers secrets after reboot
- Rotation: `scripts/panzer-rotate-secret.sh`; secret/role contract validated by `test-secret-contract` (Makefile)

## Agent Operating Policy (AGENTS.md)

- **CBM-first gate:** HARD RULE — `codebase-memory-mcp` must be queried before grep/glob/read for structural code questions; forbidden to fall back silently.
- **OpenRouter FREE models ONLY:** `:free` suffix required; paid models never; never report "key exhausted" for free models.
- **Definition of success:** boot ≠ working. A goclaw instance works only when agents are registered, skills resolve, and a real task produces a real agent run (200+ token substantive output).
- **Both deployment paths must be tested** — one path is not sufficient.

## Related

- [[panzer-os-kimi]] — Wiki overview of the project
- [[tank-os-architecture]] — Simpler single-service bootc + Quadlet pattern
- [[goclaw-architecture]] / [[goclaw-agents-deep-dive]] — GoClaw lane internals
- [[agentfield-architecture]] — AF reasoner control plane
- [[hermes-agent-architecture]] — Hermes lane internals
- [[bootc-architecture]] / [[podman-architecture]] / [[extension-podman-quadlet-architecture]] — Underlying infrastructure
