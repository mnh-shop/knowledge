---
name: setup-factory
description: "Manifest-driven stack generator for agent infrastructure deployment — Docker, Podman, Quadlet, bootc. Workspace prototype."
tags: [ideas, deployment, setup-factory, docker, podman, quadlet, bootc]
source: workspace/deployment-setup-automation/setup-factory/
---

> **⚠️ Idea / Prototype — not production-grade.**
> Setup Factory is a workspace prototype for a manifest-driven stack generator.
> Not yet battle-tested. The vault's `sources/` and `domains/deployment/` remain
> the single source of truth for production deployment knowledge.

## What this is

A generator that turns one manifest into a complete, runnable stack for one of three runtimes:

- Docker Compose
- rootless Podman Compose
- rootless Podman Quadlet (Linux only)

## What this is not

- Not a product. Stacks are assembled by the operator from a manifest.
- Not a Kubernetes operator. Multi-host orchestration is out of scope for v1.
- Not a SaaS. The generator runs locally and produces local artifacts.

## Layout

```
manifests/        canonical manifests, schema, blueprints, migration docs
services/         one folder per service module
presets/          RAM / arch / OS presets
flavours/         additive overlays (osint, swe, research, browser-automation)
outputs/          generators for Docker, podman-compose, Quadlet
rules/            declarative compatibility rules and validator
scripts/          onboard, render, apply, verify, drift
docs/             architecture, host classes, Fedora Atomic notes, security
examples/         full end-to-end instances
references/       pinned snapshots of external docs
sources/          immutable original evidence
```

## Service catalog

| Service | Description |
|---|---|
| `postgres` | PostgreSQL database for durable state |
| `redis` | Redis for n8n queue mode |
| `n8n` | Workflow automation (sqlite or postgres mode) |
| `agentfield` | AgentField runtime (sqlite or postgres mode) |
| `hermes-agent` | Hermes agent gateway |
| `goclaw` | Go-based agent gateway (minimal) |
| `openclaw` | TypeScript agent gateway (full-featured) |
| `alphaclaw` | Operations wrapper for openclaw |
| `af-deep-research` | Deep research extension for AgentField |
| `swe-af` | SWE extension for AgentField |
| `browser-worker` | Browser automation worker |

## Quick start

```bash
./scripts/onboard.sh                    # interactive wizard
./scripts/render-stack.sh <stack>       # render all enabled outputs
./scripts/deploy-docker.sh <stack>      # deploy via Docker Compose
./scripts/deploy-podman.sh <stack>      # deploy via Podman Compose
./scripts/deploy-quadlet.sh <stack>     # deploy via Podman Quadlet
./scripts/deploy-bootc.sh <stack>       # deploy via bootc
./scripts/verify.sh <stack>             # health + structural checks
```

## See also

- [[setup-factory/v1-stack-architecture|V1 Stack Architecture]] — Security-boundary agentic stack
- [[setup-factory/ROADMAP|Roadmap]] — Current state, phases, and build plan
