---
name: NemoClaw
tags: [agent-sandbox, openshell, nvidia, typescript, cli, security, reference]
description: "Wiki entry for NemoClaw — NVIDIA reference stack for sandboxed AI agents in OpenShell"
source: sources/NemoClaw/
verification_date: 2026-08-12
verified_by: codegraph-verify
---

# NemoClaw

|| Field | Value |
||---|---|
|| **Origin** | [NVIDIA/NemoClaw](https://github.com/NVIDIA/NemoClaw) |
|| **License** | Apache-2.0 |
|| **Version** | `0.1.0` (`package.json`) |
|| **Source** | `sources/NemoClaw/` |
|| **Language** | TypeScript |
|| **CBM index** | `Users-admin-repos-knowledge-sources-NemoClaw` (64,014 nodes, 225,789 edges) |

## What is it?

NVIDIA NemoClaw is an open-source reference stack for running supported AI agents (OpenClaw, Hermes, LangChain Deep Agents) inside NVIDIA OpenShell sandboxes. It provides guided onboarding, managed inference, network policy, managed integrations, snapshots, and lifecycle operations through a CLI and agent-specific aliases.

## Architecture

Dual-language stack:

- **CLI and plugin**: TypeScript (`src/`, `nemoclaw/src/`) with CJS launcher in `bin/`
- **Blueprint**: YAML configuration (`nemoclaw-blueprint/`)
- **Docs**: Fern MDX for user-facing pages

Key modules:
- `src/lib/` — core CLI logic: onboard, credentials, inference, policies, preflight, runner
- `nemoclaw/src/blueprint/` — runner, snapshot, SSRF validation, state management
- `nemoclaw/src/commands/` — slash commands, migration state
- `nemoclaw/src/onboard/` — onboarding config

### Testing

Vitest with 7 disjoint projects: `cli`, `integration`, `installer-integration`, `package-contract`, `plugin`, `e2e-support`, `e2e-live`.

## Agent Integration

NemoClaw provides:
- OpenClaw plugin (`nemoclaw/openclaw.plugin.json`)
- Hermes support
- LangChain Deep Agents support
- Sandbox policy enforcement
- Network isolation via OpenShell
- Snapshot and lifecycle management

## Value for coding agents

NemoClaw is relevant as a reference for running AI agents in sandboxed environments. It demonstrates the OpenShell security model and provides a blueprint for agent-onboard and lifecycle management in constrained environments.
