---
name: NemoClaw-codegraph-verify
tags: [NemoClaw, codegraph-verify, nvidia, openshell, agent-sandbox]
description: "Codegraph Verification: NemoClaw — validating wiki claims against indexed source code symbols"
source: sources/NemoClaw/
---

# Codegraph Verification: NemoClaw

**Date:** 2026-08-12

**Version checked:** `f712516ef` (main, fix(inference): admit a remediable storage conflict)

## Claim 1: NVIDIA reference stack for sandboxed AI agents

- **Wiki says:** NemoClaw is an NVIDIA open-source reference stack for running AI agents inside OpenShell sandboxes.
- **Source evidence:**
  - `README.md` — "NVIDIA NemoClaw is an open source reference stack for running supported AI agents more safely inside NVIDIA OpenShell sandboxes"
  - `package.json` — `name: "nemoclaw"`, `license: "Apache-2.0"`
- **Verdict:** ✅ CORRECT

## Claim 2: Supports OpenClaw, Hermes, and LangChain Deep Agents

- **Wiki says:** Supported agents are OpenClaw (default), Hermes, and LangChain Deep Agents Code.
- **Source evidence:**
  - `README.md` — "Supported agents: OpenClaw (default), Hermes, LangChain Deep Agents Code"
  - `nemoclaw/openclaw.plugin.json` — OpenClaw plugin definition
  - `nemoclaw/package.json` — plugin package configuration
- **Verdict:** ✅ CORRECT

## Claim 3: Dual-language TypeScript stack

- **Wiki says:** CLI and plugin in TypeScript with CJS launcher; blueprint in YAML.
- **Source evidence:**
  - `src/lib/` — TypeScript source for CLI
  - `nemoclaw/src/` — TypeScript plugin source
  - `bin/nemoclaw.ts` — CommonJS launcher
  - `nemoclaw-blueprint/` — YAML blueprint definitions
  - `tsconfig.json` — TypeScript config
- **Verdict:** ✅ CORRECT

## Claim 4: 7 disjoint Vitest test projects

- **Wiki says:** Testing uses 7 Vitest projects: cli, integration, installer-integration, package-contract, plugin, e2e-support, e2e-live.
- **Source evidence:**
  - `vitest.config.ts` — 7 project definitions
  - `package.json` — test scripts: `test`, `test:fast`, `test:changed`, `test:integration`, `test:live-e2e`, `test:package`
- **Verdict:** ✅ CORRECT

## Claim 5: OpenShell integration for security

- **Wiki says:** Uses OpenShell for sandbox policy enforcement and network isolation.
- **Source evidence:**
  - `README.md` — "running supported AI agents more safely inside NVIDIA OpenShell sandboxes"
  - `src/lib/policies/` — policy enforcement modules
  - `src/lib/messaging/` — messaging architecture with channel migration
- **Verdict:** ✅ CORRECT

## Claim 6: CBM index present and healthy

- **Wiki says:** CBM index has 64,014 nodes and 225,789 edges.
- **Source evidence:**
  - CBM project `Users-admin-repos-knowledge-sources-NemoClaw` — verified via `index_status`: nodes=64014, edges=225789, status=ready
  - Source tree: 54 directories, TypeScript + YAML, ~1.5MB source
- **Verdict:** ✅ CORRECT
