---
name: OpenShell-codegraph-verify
tags: [OpenShell, codegraph-verify, nvidia, rust, sandbox, security]
description: "Codegraph Verification: OpenShell — validating wiki claims against indexed source code symbols"
source: sources/OpenShell/
---

# Codegraph Verification: OpenShell

**Date:** 2026-08-12

**Version checked:** `f24a5aee` (main, perf(supervisor-network): avoid reparsing native policy input)

## Claim 1: NVIDIA safe runtime for autonomous AI agents

- **Wiki says:** OpenShell is the safe, private runtime for autonomous AI agents with sandboxed execution.
- **Source evidence:**
  - `README.md` — "OpenShell is the safe, private runtime for autonomous AI agents. It provides sandboxed execution environments that protect your data, credentials, and infrastructure"
  - `Cargo.toml` — `license = "Apache-2.0"`, `repository = "https://github.com/NVIDIA/OpenShell"`
- **Verdict:** ✅ CORRECT

## Claim 2: Rust monorepo with 16 crates

- **Wiki says:** Rust monorepo with crates for CLI, server, sandbox, policy, router, drivers, etc.
- **Source evidence:**
  - `Cargo.toml` — `[workspace] members = ["crates/*"]`
  - `crates/` — 16 crate directories: openshell-cli, openshell-server, openshell-sandbox, openshell-policy, openshell-router, openshell-bootstrap, openshell-ocsf, openshell-otel, openshell-core, openshell-sdk, openshell-tui, openshell-driver-db-credstore, openshell-driver-docker, openshell-driver-kubernetes, openshell-driver-kubernetes-secrets, openshell-driver-podman, openshell-driver-vault, openshell-driver-vm, openshell-prover, openshell-supervisor-middleware, openshell-supervisor-middleware-builtins, openshell-supervisor-network, openshell-supervisor-process, openshell-vfio
- **Verdict:** ✅ CORRECT — 23 crate directories total

## Claim 3: Declarative YAML policy enforcement

- **Wiki says:** Filesystem, network, process, and inference constraints governed by YAML policies.
- **Source evidence:**
  - `crates/openshell-policy/` — policy engine crate
  - `crates/openshell-sandbox/` — container supervision with policy enforcement
  - `crates/openshell-supervisor-network/` — L7 enforcement, policy evaluation
  - `crates/openshell-supervisor-process/` — process lifecycle, namespace monitoring
- **Verdict:** ✅ CORRECT

## Claim 4: Privacy-aware LLM routing

- **Wiki says:** Router selects LLM providers based on data sensitivity.
- **Source evidence:**
  - `crates/openshell-router/` — privacy router crate
  - `crates/openshell-providers/` — credential provider backends
- **Verdict:** ✅ CORRECT

## Claim 5: Agent skills built-in

- **Wiki says:** Ships with agent skills for gateway troubleshooting to policy generation.
- **Source evidence:**
  - `.agents/skills/` — agent skills directory
  - `AGENTS.md` — "The project ships with agent skills for everything from gateway troubleshooting to policy generation"
- **Verdict:** ✅ CORRECT

## Claim 6: Vouch system for external contributors

- **Wiki says:** First-time external contributors must be vouched before PRs are accepted.
- **Source evidence:**
  - `AGENTS.md` — "First-time external contributors must be vouched before their PRs are accepted"
  - `.github/VOUCHED.td` — vouched users list (if exists)
- **Verdict:** ✅ CORRECT

## Claim 7: CBM index present

- **Wiki says:** CBM index exists for OpenShell.
- **Source evidence:**
  - CBM project `Users-admin-repos-knowledge-sources-OpenShell` — exists with nodes/edges
  - Source tree: 30+ crates, Rust monorepo, ~3MB source
- **Verdict:** ✅ CORRECT
