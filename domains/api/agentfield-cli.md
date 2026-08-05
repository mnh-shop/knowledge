---
name: agentfield-cli
tags: [agentfield, cli, api, automation, control-plane, golang, harness, identity, orchestration, plugin-sdk, security, session, webhook]
description: "AgentField af CLI reference: server/dev, node packages, execution, agent JSON mode, sessions, identity, secrets, skills, and ops commands"
source: sources/agentfield/
---

# AgentField CLI Reference (`af`)
**Source:** `sources/agentfield/control-plane/internal/cli/`

**Status:** Active research target  
**Binary:** `af` (alias `agentfield`), built from `control-plane/cmd/af`  
**Version:** 0.1.118-rc.3  
**Framework:** Cobra (Go) + Bubble Tea (interactive `init`)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Server / Dev / Init](#2-server--dev--init)
3. [Node and Package Management](#3-node-and-package-management)
4. [Execution](#4-execution)
5. [Agent JSON Mode](#5-agent-json-mode)
6. [Realtime Sessions](#6-realtime-sessions)
7. [Identity (DID/VC)](#7-identity-didvc)
8. [Secrets](#8-secrets)
9. [Skills](#9-skills)
10. [Ops and Misc](#10-ops-and-misc)
11. [Global Flags and Environment](#11-global-flags-and-environment)
12. [Key Source Files](#12-key-source-files)

---

## 1. Overview

The `af` binary is the single distribution artifact — it runs as a **server** (bare `af` or `af server`), an **agent-package runner** (`af dev`/`af run`), or a **CLI client** against a control plane.

- Root command: `af` with alias `agentfield` (`root.go:37-39`); **bare `af` defaults to server mode** (`root.go:57-58`)
- `af --version` prints version/commit/build info; `af version` is the subcommand form (`version.go:20`)
- **Agent mode:** `af agent help` emits a structured JSON command reference for programmatic use; every `af agent *` command emits `{ok, data, error:{code,message,hint}}` envelopes on stdout (`agent_commands.go:39`)
- Node lifecycle commands (`list`, `stop`, `logs`) accept `--json` for the same envelope format (`node_json.go`)

## 2. Server / Dev / Init

| Command | Description | Source |
|---------|-------------|--------|
| `af` (bare) | Run the server (default root behavior, backward compatible) | `root.go:57-58` |
| `af server` | Run the AgentField server explicitly (API + UI + execution engine) | `root.go:146-152` |
| `af dev [path]` | Run an agent package in development mode from `.` or a path (no install required); `--port/-p`, `--watch/-w` (auto-restart), `--verbose/-v` | `commands/dev.go:37-59` |
| `af init [project-name]` | Interactive Bubble Tea scaffold for a new agent project (language, author, agentfield.yaml template) | `init.go:217` |
| `af doctor` | Inspect the local environment for AgentField development capabilities (probes) | `doctor.go:117` |
| `af harness doctor` | Verify coding-agent harness provider binaries, versions, and authentication | `harness_doctor.go:61` |
| `af version` | Print version information | `version.go:20` |

## 3. Node and Package Management

| Command | Description | Source |
|---------|-------------|--------|
| `af install <package-path>` | Install an agent node package from a local directory, GitHub URL (`//<subdir>` + `@<ref>` supported, `--path` for subdir packages), or a registry name; `--force/-f`, `--json` | `commands/install.go:43-84` |
| `af run <agent-node-name>` | Start an installed node in the background, register it with the server; `--port/-p`, `--detach/-d` (default true), `--json` | `commands/run.go:44-69` |
| `af uninstall <package-name>` | Uninstall an agent node package | `uninstall.go:17` |
| `af stop <agent-node-name>` | Stop a running agent node | `stop.go:29` |
| `af ps` | List in-flight workflow runs | `ps.go:47` |
| `af list` | List installed agent node packages (human or `--json`) | `list.go:27` |
| `af ls [query]` | List reasoners (registered across nodes) | `ls_reasoners.go:44` |
| `af nodes` | Manage agent nodes | `nodes.go:18` |
| `af nodes register-serverless --url <invocation-url>` | Register a serverless agent by invocation URL (Lambda/Cloud Functions/Cloud Run) | `nodes.go:42-43` |
| `af logs <agent-node-name>` | View logs for an agent node | `logs.go:27` |
| `af config <package-name>` | Configure environment variables for an installed package (writes into the node's env) | `config.go:29` |
| `af show-requirements <path-or-git-url>` | Show the env vars a node needs **before** installing it | `show_requirements.go:47` |
| `af catalog` | Browse installable agent nodes from the registry | `catalog.go:81` |

## 4. Execution

| Command | Description | Source |
|---------|-------------|--------|
| `af call <node>.<reasoner>` | Trigger a reasoner; `--in` (inline JSON or `@file`), `--schema`, `--async` (return run_id), `--interactive/--no-interactive`, `--output/-o pretty\|json\|yaml`, `--field` (extract result field) | `call.go:48` |
| `af execution cancel\|pause\|resume\|restart <execution_id>` | Manage workflow executions on the control plane (human-oriented group) | `execution.go:18-57` |
| `af agent exec <verb> --id <exec_id>` | Agent-mode execution steering: `pause`, `resume`, `cancel`, `restart`, `approval-status`, `approve` (JSON envelopes, `--reason` for pause/cancel/approve) | `agent_exec.go:17-65` |
| `af wait <run_id>` | Block until a run reaches a terminal state, then print status and result | `wait.go:60` |
| `af tail <run_id>` | Attach to a running execution stream (follow live output) | `tail.go:25` |
| `af agent batch` | Execute batch API operations in agent mode | `agent_commands.go:419` |

## 5. Agent JSON Mode

`af agent` is the **machine-friendly JSON interface** over the `/api/v1/agentic` endpoints. Every subcommand emits `{ok, data, error}` envelopes; flags `--output/-o json|compact` and `--timeout/-t`.

| Command | Description | Source |
|---------|-------------|--------|
| `af agent status` | System status summary | `agent_commands.go:84` |
| `af agent discover` | Search the agentic API endpoint catalog | `agent_commands.go:99` |
| `af agent search <query>` | Rank installed reasoners by a free-text query (BM25) | `agent_commands.go:137` |
| `af agent query` | Run a unified resource query | `agent_commands.go:181` |
| `af agent run` | Fetch a run overview by ID | `agent_commands.go:260` |
| `af agent agent-summary` | Fetch an agent summary by ID | `agent_commands.go:279` |
| `af agent kb topics` | List knowledge-base topics | `agent_commands.go:321` |
| `af agent kb search` | Search KB articles | `agent_commands.go:337` |
| `af agent kb read` | Read a KB article by ID | `agent_commands.go:378` |
| `af agent kb guide` | Get a goal-oriented KB guide | `agent_commands.go:397` |
| `af agent batch` | Execute batch API operations | `agent_commands.go:419` |
| `af agent help` | Structured JSON help for agent mode | `agent_commands.go:442` |

## 6. Realtime Sessions

| Command | Description | Source |
|---------|-------------|--------|
| `af session start <node>.<session>` | Start a provider-backed realtime session | `session.go:57` |
| `af session offer <session_id>` | Create a realtime WebRTC offer through the control plane | `session.go:103` |
| `af session tool <session_id> <tool>` | Invoke a session tool via execute/async | `session.go:224` |
| `af session workflows <session_id>` | List workflows associated with a session | `session.go:276` |

## 7. Identity (DID/VC)

| Command | Description | Source |
|---------|-------------|--------|
| `af vc` | Verifiable Credential operations group | `vc.go:20` |
| `af vc verify <vc-file.json>` | Verify an AgentField Verifiable Credential (signature, DID, chain) | `vc.go:51` |
| `af verify` | Alias for `vc verify` | `verify_alias_test.go` / `NewVerifyAliasCommand` |

> **Note:** `af vc` exposes **only `verify`** — no export/import subcommand exists. Backing up DID keys means copying the keystore directory (`~/.agentfield/data/keys/`); see `domains/deployment/agentfield-deployment.md`.

## 8. Secrets

Encrypted secret store under `~/.agentfield` (`secrets.go:19`):

| Command | Description | Source |
|---------|-------------|--------|
| `af secrets set KEY [VALUE]` | Store a secret (prompt hidden if VALUE omitted) | `secrets.go:42` |
| `af secrets ls` | List stored secrets, values masked (alias: `list`) | `secrets.go:87` |
| `af secrets rm KEY` | Remove a stored secret (aliases: `remove`, `delete`) | `secrets.go:123` |

Secrets are AES-256-GCM encrypted at rest and injected into agent nodes via the `user_environment` section of `agentfield-package.yaml` (`required` entries with `type: secret`, `scope: global|node`).

## 9. Skills

`af skill` installs and manages AgentField skills across coding agents (Claude Code, Codex, Gemini, Aider, etc.):

| Command | Description | Source |
|---------|-------------|--------|
| `af skill catalog` | List skills bundled with this af binary | `skill.go:270` |
| `af skill install [skill-name]` | Install a skill into one or more coding-agent integrations | `skill.go:74` |
| `af skill list` | List installed skills and their target integrations | `skill.go:147` |
| `af skill update [skill-name]` | Re-install a skill at the binary's embedded version into every target | `skill.go:165` |
| `af skill uninstall [skill-name]` | Remove a skill from one or more targets | `skill.go:193` |
| `af skill print [skill-name]` | Print SKILL.md to stdout | `skill.go:223` |
| `af skill path` | Print the canonical skill store location (`~/.agentfield/skills`) | `skill.go:253` |

## 10. Ops and Misc

| Command | Description | Source |
|---------|-------------|--------|
| `af share [workflow-id]` | Export a workflow run as a self-contained shareable HTML file | `share_command.go:33` |
| `af harness` | Inspect and manage coding-agent harness providers | `harness_doctor.go:48` |
| `af doctor` | Local environment introspection (see §2) | `doctor.go:117` |

## 11. Global Flags and Environment

Persistent flags (`root.go:79-92`):

| Flag | Env | Purpose |
|------|-----|---------|
| `--config <path>` | `AGENTFIELD_CONFIG_FILE` | YAML config path |
| `--verbose/-v` | - | Verbose logging |
| `--open` | - | Open browser to UI (default true, server mode) |
| `--ui-dev` | - | Proxy to Vite UI dev server |
| `--backend-only` | - | Backend APIs only |
| `--port <n>` | `AGENTFIELD_PORT` | HTTP port override |
| `--no-vc-execution` / `--vc-execution` | - | Disable/force VC generation for executions |
| `--storage-mode <local\|postgres>` | `AGENTFIELD_STORAGE_MODE` | Storage backend override |
| `--postgres-url <dsn>` | `AGENTFIELD_POSTGRES_URL` | Implies `--storage-mode=postgres` |
| `--server/-s <url>` | `AGENTFIELD_SERVER` | Control plane URL (default `http://localhost:8080`) |
| `--api-key/-k <key>` | `AGENTFIELD_API_KEY` | API key for authenticated endpoints |

## 12. Key Source Files

All paths relative to `control-plane/internal/cli/` unless noted:

| File | Contents |
|------|----------|
| `root.go` | Root command, flags, command registration, config init (Viper) |
| `commands/dev.go`, `commands/install.go`, `commands/run.go` | Framework-migrated dev/install/run commands |
| `call.go`, `wait.go`, `tail.go`, `ps.go`, `execution.go`, `agent_exec.go` | Execution surface |
| `agent_commands.go` | Agent JSON mode (`status/discover/search/query/run/agent-summary/kb/batch/help`) |
| `session.go` | Realtime session commands |
| `vc.go` | VC verification (only) |
| `secrets.go` | Encrypted secret store |
| `skill.go` | Skill management across coding agents |
| `nodes.go`, `list.go`, `ls_reasoners.go`, `stop.go`, `logs.go`, `config.go`, `uninstall.go`, `catalog.go`, `show_requirements.go` | Node/package management |
| `init.go` | Interactive project scaffold (Bubble Tea) |
| `doctor.go`, `harness_doctor.go` | Environment and harness probes |
| `share_command.go` | Workflow share/export |

## Related

- [[agentfield]] -- wiki page for the platform
- [[agentfield-api]] -- REST/gRPC API reference (the CLI wraps `/api/v1/*`)
- [[agentfield-architecture]] -- system architecture
- [[agentfield-deployment]] -- deployment guide (server, containers, Helm)
- [[agentfield-desktop]] -- desktop app; shells out to `af install/run/stop`
- [[agentfield-quadlet]] -- Quadlet deployment
- [[SWE-AF]] / [[sec-af]] / [[af-deep-research]] -- ecosystem agent nodes installable via `af install`
