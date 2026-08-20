---
name: OpenShell
tags: [agent-sandbox, nvidia, rust, sandbox, security, policy, reference]
description: "Wiki entry for OpenShell — NVIDIA safe runtime for autonomous AI agents"
source: sources/OpenShell/
verification_date: 2026-08-12
verified_by: codegraph-verify
---

# OpenShell

|| Field | Value |
||---|---|
|| **Origin** | [NVIDIA/OpenShell](https://github.com/NVIDIA/OpenShell) |
|| **License** | Apache-2.0 |
|| **Version** | `0.0.0` (workspace, `Cargo.toml`) |
|| **Source** | `sources/OpenShell/` |
|| **Language** | Rust (monorepo, 16 crates) |
|| **CBM index** | `Users-admin-repos-knowledge-sources-OpenShell` (30,399 nodes, 105,168 edges est.) |

## What is it?

OpenShell is the safe, private runtime for autonomous AI agents. It provides sandboxed execution environments that protect data, credentials, and infrastructure — governed by declarative YAML policies that prevent unauthorized file access, data exfiltration, and uncontrolled network activity.

Built agent-first: ships with agent skills for everything from gateway troubleshooting to policy generation.

Alpha software — single-player mode: one developer, one environment, one gateway.

## Architecture

Rust monorepo with 16 crates:

| Crate | Purpose |
|-------|---------|
| `openshell-cli` | User-facing CLI binary |
| `openshell-server` | Gateway server, control-plane API, auth |
| `openshell-sandbox` | Container supervision, policy-enforced egress |
| `openshell-policy` | Filesystem, network, process, inference constraints |
| `openshell-router` | Privacy-aware LLM routing |
| `openshell-bootstrap` | Gateway registration metadata, mTLS |
| `openshell-ocsf` | OCSF v1.7.0 event types |
| `openshell-otel` | OTLP trace provider |
| `openshell-core` | Shared types, config, error handling |
| `openshell-sdk` | Async Rust gateway client (gRPC, TLS, OIDC) |
| `openshell-tui` | Ratatui dashboard |
| `openshell-driver-*` | K8s secrets, Vault, K8s, Docker, VM compute drivers |
| `openshell-prover` | Policy verification and proof generation |
| `openshell-supervisor-*` | Middleware, network, process supervisors |
| `openshell-vfio` | PCI/GPU passthrough |

Python SDK in `python/openshell/`. Protobuf definitions in `proto/`. Deploy configs in `deploy/`.

## Key Features

- **Sandboxed execution** — agents run in containers with policy-enforced constraints
- **Declarative YAML policies** — filesystem, network, process, inference constraints
- **Privacy-aware LLM routing** — router selects providers based on data sensitivity
- **OCSF logging** — standardized security event formatting
- **Agent skills** — built-in skills for troubleshooting, policy generation, etc.
- **Vouch system** — first-time external contributors must be vouched

## Value for coding agents

OpenShell is relevant as a reference for secure agent deployment. It demonstrates how to build policy-enforced sandboxes for AI agents and provides a model for multi-crate Rust architectures with agent skills.
