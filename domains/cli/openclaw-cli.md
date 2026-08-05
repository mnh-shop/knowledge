---
name: openclaw-cli
tags: [acp, agent-gateway, cli, deployment, mcp, openclaw, personal-assistant, plugin-sdk, security, systemd, typescript]
description: OpenClaw CLI Reference
source: sources/openclaw/
---

# OpenClaw CLI Reference
**Source:** `sources/openclaw/`

OpenClaw ships a single `openclaw` CLI binary (Node ESM entry `openclaw.mjs`, run via `node` or `bun`). The root program exposes roughly 60 visible commands: ~22 core root commands (described in `src/cli/program/core-command-descriptors.ts`) plus ~41 sub-CLIs (described in `src/cli/program/subcli-descriptors.ts`). Sub-CLIs are lazily registered — root help shows descriptors only; the real command trees load on invocation. Two descriptors are gated out of the visible set by default: `claws` (experimental flag) and `qa` (private QA).

## Table of Contents

- [Entry Point](#entry-point)
- [Core Root Commands](#core-root-commands)
- [Sub-CLIs by Function](#sub-clis-by-function)
- [Protocol Bridges (mcp / acp / attach)](#protocol-bridges-mcp--acp--attach)
- [Notable Workflows](#notable-workflows)
- [Key Source Files](#key-source-files)

---

## Entry Point

- **Binary:** `openclaw.mjs` — validates the Node version (requires `22.22.3+`, `24.15+`, or `25.9+`; Node 26 recommended), then spawns the real CLI.
- **Run styles:** `openclaw <cmd>`, `pnpm openclaw <cmd>` (dev), or `pnpm dev`. The dist-backed wrapper is preferred over `node --import tsx src/index.ts` (tsx compiles all bundled plugins per process, ~220s).
- **Sub-CLI catalog:** `src/cli/program/subcli-descriptors.ts` — `SUB_CLI_DESCRIPTORS` powers root help placeholders and lazy registration (private `qa` is gated out of visible descriptors).
- **Core catalog:** `src/cli/program/core-command-descriptors.ts` — `CORE_CLI_COMMAND_DESCRIPTORS` for the ~22 core root commands (`claws` is gated unless experimental Claws are enabled).

---

## Core Root Commands

Defined in `src/cli/program/core-command-descriptors.ts`:

| Command | Description |
|---------|-------------|
| `setup` | Chat with OpenClaw; onboard when setup is incomplete |
| `onboard` | Guided setup for auth, models, Gateway, workspace, channels, and skills (`hasSubcommands: true`) |
| `configure` | Interactive configuration for credentials, channels, gateway, and agent defaults |
| `config` | Non-interactive config helpers: `get`/`set`/`patch`/`unset`/`file`/`schema`/`validate` |
| `claws` | Inspect and add experimental OpenClaw Claws (gated) |
| `backup` | Create and verify backup archives and SQLite snapshots |
| `migrate` | Import state from another agent system |
| `doctor` | Health checks + quick fixes for the gateway and channels (`--fix` applies repairs; `--lint` for stable automation output) |
| `dashboard` | Open the Control UI with your current token |
| `reset` | Reset local config/state (keeps the CLI installed) |
| `uninstall` | Uninstall the gateway service + local data (CLI remains) |
| `message` | Send, read, and manage messages and channel actions |
| `mcp` | Manage OpenClaw `mcp.servers` config and channel bridge (subcommands: `list`/`show`/`status`/`doctor`/`probe`/`add`/`set`/`configure`/`tools`/`login`/`logout`/`reload`/`unset`/`serve`) |
| `transcripts` | Inspect stored transcripts |
| `agent` | Run an agent turn via the Gateway (`--local` for embedded) |
| `agents` | Manage isolated agents (workspaces + auth + routing) |
| `status` | Show channel health and recent session recipients |
| `health` | Fetch health from the running gateway |
| `audit` | Inspect metadata-only run, tool, and message lifecycle records |
| `sessions` | List stored conversation sessions |
| `commitments` | List and manage inferred follow-up commitments |
| `tasks` | Inspect durable background tasks and TaskFlow state |

---

## Sub-CLIs by Function

From `src/cli/program/subcli-descriptors.ts` (42 descriptors, 41 visible after `qa` gating; described verbatim):

### Gateway & Service Management
| Command | Description |
|---------|-------------|
| `gateway` | Run, inspect, and query the WebSocket Gateway |
| `daemon` | Manage the Gateway service (launchd/systemd/schtasks) |
| `logs` | Tail gateway file logs via RPC |
| `system` | System tools (events, heartbeat, presence) |

### Models & Inference
| Command | Description |
|---------|-------------|
| `models` | Model discovery, scanning, and configuration |
| `promos` | Discover and claim promotional model offers from ClawHub |
| `infer` | Run provider-backed inference commands through a stable CLI surface |
| `capability` | Run provider capability commands (fallback alias: `infer`) |

### Approvals & Policy
| Command | Description |
|---------|-------------|
| `approvals` | Manage approval policy and pending requests |
| `exec-approvals` | Manage exec approvals (alias for `approvals`) |
| `exec-policy` | Show or synchronize requested exec policy with host approvals |

### Nodes, Devices & Fleet
| Command | Description |
|---------|-------------|
| `nodes` | Manage gateway-owned nodes (pairing, status, invoke, and media) |
| `devices` | Device pairing and auth tokens |
| `users` | Manage durable user profiles and email aliases |
| `node` | Run and manage the headless node host service |
| `worker` | Run the restricted cloud worker runtime |
| `sandbox` | Manage sandbox containers (Docker-based agent isolation) |
| `fleet` | Provision and manage isolated tenant cells (experimental) |
| `worktrees` | Create, inspect, restore, and clean up managed worktrees |

### Interactive Surfaces
| Command | Description |
|---------|-------------|
| `attach` | Attach Claude Code to a gateway session with scoped MCP tools |
| `tui` | Open a terminal UI connected to the Gateway |
| `terminal` | Open a local terminal UI (alias for `tui --local`) |
| `chat` | Open a local terminal UI (alias for `tui --local`) |

### Scheduling & Discovery
| Command | Description |
|---------|-------------|
| `cron` | Manage cron jobs (via Gateway) |
| `dns` | DNS helpers for wide-area discovery (Tailscale + CoreDNS) |
| `docs` | Search the live OpenClaw docs |
| `qa` | Run QA scenarios and launch the private QA debugger UI (gated) |
| `proxy` | Run the OpenClaw debug proxy and inspect captured traffic |

### Hooks, Pairing & Channels
| Command | Description |
|---------|-------------|
| `hooks` | Manage internal agent hooks |
| `webhooks` | Webhook helpers and integrations |
| `qr` | Generate a mobile pairing QR code and setup code |
| `clawbot` | Legacy clawbot command aliases |
| `pairing` | Secure DM pairing (approve inbound requests) |
| `plugins` | Manage OpenClaw plugins and extensions |
| `channels` | Manage connected chat channels and accounts |
| `directory` | Lookup contact and group IDs (self, peers, groups) for supported chat channels |

### Security, Secrets & Skills
| Command | Description |
|---------|-------------|
| `security` | Audit local config and state for common security foot-guns |
| `secrets` | Secrets runtime controls |
| `skills` | List and inspect available skills |

### Maintenance
| Command | Description |
|---------|-------------|
| `update` | Update OpenClaw and inspect update channel status |
| `completion` | Generate shell completion script |

---

## Protocol Bridges (mcp / acp / attach)

Three commands bridge OpenClaw to external agent protocols:

- **`openclaw mcp`** — Bidirectional MCP. `mcp serve` runs OpenClaw as an MCP server exposing Gateway-backed channel conversations over stdio; the other subcommands (`add`/`set`/`doctor`/`probe`/`login`/`configure`/`tools`/...) manage `mcp.servers` as an MCP client-side registry (`docs/cli/mcp.md:11-33`). `login` performs the MCP OAuth flow for HTTP servers.
- **`openclaw acp`** — Runs the ACP bridge backed by the Gateway (sub-CLI descriptor: "Run an ACP bridge backed by the Gateway"). Server flags (`src/cli/acp-cli.ts`): `--url`, `--token`/`--token-file`, `--password`/`--password-file`, `--session`, `--session-label`, `--require-existing`, `--reset-session`, `--no-prefix-cwd`, `--provenance <off|meta|meta+receipt>`, `--verbose`. Client flags: `--cwd`, `--server`, `--server-args`, `--server-verbose`. See [[domains/acp/openclaw-acp-implementation.md]].
- **`openclaw attach`** — Attach Claude Code to a gateway session with scoped MCP tools.

---

## Notable Workflows

### Guided Setup with Daemon Install

```bash
openclaw onboard --install-daemon
```

`onboard` drives auth, models, Gateway, workspace, channels, and skills setup. `--install-daemon` starts the managed gateway install path (launchd on macOS, systemd on Linux, Scheduled Tasks on Windows with per-user Startup-folder fallback). With `--install-daemon`, a SecretRef-managed `gateway.auth.token` is validated but not persisted as resolved plaintext in supervisor service environment metadata. Skip with `--no-install-daemon` / `--skip-daemon`; control the runtime with `--daemon-runtime <node>` (`docs/cli/onboard.md:272-338`).

### Diagnostics

```bash
openclaw doctor            # health checks for gateway + channels
openclaw doctor --fix      # apply supported repairs (config/state migrations)
openclaw security audit    # cold config/filesystem security audit
openclaw security audit --deep --fix   # add live Gateway probes + plugin collectors, apply safe fixes
openclaw security audit --json
```

`doctor --fix` also migrates older shipped config shapes into the current one and rotates reused secrets such as a `hooks.token` that duplicates a gateway auth value.

### Update Channels

```bash
openclaw update --channel stable            # default
openclaw update --channel extended-stable   # package-only
openclaw update --channel beta
openclaw update --channel dev
openclaw update --dry-run                   # preview without writing config or restarting
```

`--channel` sets the update channel and persists it after core update success; `--tag` overrides the package target for this update only (`docs/cli/update.md:25-49`).

### MCP / ACP Decisions

- External MCP client wants OpenClaw channel conversations → `openclaw mcp serve`
- Save third-party MCP servers for OpenClaw-managed agent runs → `openclaw mcp add` / `set` / `configure`
- OpenClaw should host the coding runtime itself and keep the agent session inside OpenClaw → `openclaw acp` (`docs/cli/mcp.md:22,51`)

---

## Key Source Files

| File | Purpose |
|------|---------|
| `openclaw.mjs` | Bin entry: Node version gate + spawn |
| `src/cli/program/core-command-descriptors.ts` | ~22 core root command descriptors |
| `src/cli/program/subcli-descriptors.ts` | ~42 sub-CLI descriptors (`SUB_CLI_DESCRIPTORS`) |
| `src/cli/program/command-registry.ts` / `command-tree.ts` | Lazy registration and command dispatch |
| `src/cli/mcp-cli.ts` | `openclaw mcp` client registry + `serve` |
| `src/cli/acp-cli.ts` | `openclaw acp` server/client flags |
| `src/cli/daemon-cli.ts` + `src/cli/daemon-cli/` | `openclaw daemon` launchd/systemd/schtasks management |
| `src/cli/gateway-cli.ts` + `src/cli/gateway-cli/` | `openclaw gateway` run/inspect/query (`gateway-cli/dev.ts`, `pre-bootstrap.ts`, etc.) |

## Related

- [[domains/architecture/openclaw-architecture.md]] -- Gateway architecture and agent system
- [[domains/mcp/openclaw-mcp-implementation.md]] -- MCP surfaces and client registry
- [[domains/acp/openclaw-acp-implementation.md]] -- ACP bridge architecture
- [[domains/security/openclaw-security.md]] -- Security audit surface (`openclaw security`)
- [[domains/api/openclaw-api.md]] -- Gateway API reference
- [[assets/deployment/openclaw-quadlet.md]] -- Quadlet deployment patterns
