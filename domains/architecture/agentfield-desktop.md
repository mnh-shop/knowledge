---
name: agentfield-desktop
tags: [agentfield, architecture, desktop, electron, golang, ipc, macos, monitor, orchestration, plugin-sdk, security, tray, typescript]
description: "AgentField Desktop architecture: Electron dashboard over the local control plane, af-as-contract CLI shell-out, and the af-tray macOS menu-bar companion"
source: sources/agentfield/
---

# AgentField Desktop Architecture
**Source:** `sources/agentfield/desktop/` + `control-plane/cmd/af-tray/`

**Status:** Active research target  
**License:** Apache 2.0  
**App:** Electron (electron-vite), TypeScript + React renderer  
**App ID:** `ai.agentfield.desktop`  
**Version (desktop package):** 0.1.0  
**Platform focus:** macOS (af-tray); Windows/macOS/Linux for the Electron app

---

## Table of Contents

1. [Overview](#1-overview)
2. [Screens and Views](#2-screens-and-views)
3. [af-as-Contract](#3-af-as-contract)
4. [Autostart and IPC](#4-autostart-and-ipc)
5. [af-tray (macOS Menu Bar)](#5-af-tray-macos-menu-bar)
6. [x25519gen (DID Interop Fixture)](#6-x25519gen-did-interop-fixture)
7. [Deployment Relationship](#7-deployment-relationship)
8. [Key Source Files](#8-key-source-files)

---

## 1. Overview

AgentField Desktop is a **read-only desktop dashboard** for the AgentField control plane and locally installed agent nodes (`desktop/package.json`: "Read-only desktop dashboard for the AgentField control plane and locally installed agent nodes"). It targets GitHub-comfortable developers whose primary jobs are installing agent nodes from GitHub and watching runs/cost — a local sub-harness for coding agents, not an infra admin console.

Key design decisions (per `DESIGN.md` / `PRODUCT.md` and repo AGENTS.md):
- Gold/amber accent theme; shared theme tokens rather than per-page styles
- Agents screen is a marketplace-style library (installed agents + add), not a bare list
- Activity is designed for high-volume, dense, filterable runs rather than large cards
- Cold-launch goes to Home when agents exist; Agents add-mode when the library is empty
- The `af` CLI is the single source of truth for the package registry — the app shells out rather than re-implementing parsing

The app bundles the `af` and `af-tray` binaries as `extraResources` (`vendor/` → `bin/`, filtered to `af`, `af.exe`, `af-tray`) and registers the `agentfield://` deep-link protocol (e.g. `agentfield://install` opens Agents add-mode).

## 2. Screens and Views

View routing lives in `desktop/src/renderer/src/App.tsx`; each view is a component under `desktop/src/renderer/src/components/`:

| View | Component | Purpose |
|------|-----------|---------|
| Home / Dashboard | `DashboardView` | Control-plane status, usage totals, dashboard metrics |
| Agents | `AgentsPanel` | Marketplace-style library: installed nodes + "+ Add agent" (library mode and add-mode, `DESIGN.md §4.11`) |
| Activity | `ActivityPanel` | Dense, filterable run history (per-row usage when the API allows) |
| Install | `InstallPanel` | Now maps to the Agents view with add-mode open (`App.tsx` view map: `install → Agents`) — the deep link stays valid |
| Settings | `SettingsPanel` | Autostart, control-plane port, CLI status/update |

Deep links, sidebar highlight (`install` is Agents territory), and cold-launch defaulting are all handled in `App.tsx`.

## 3. af-as-Contract

The desktop treats the `af` CLI as its contract for all node operations — it spawns the CLI instead of reimplementing registry parsing:

- **Install:** `af install <source>` for vetted catalog entries and `af install <source> --force` for reinstall-in-place; output streamed and sanitized into progress lines (`desktop/src/main/installer.ts`). Sources are validated by `parseRepoSource` before spawning.
- **Run/Stop:** `af run <name>` / `af stop <name>` drive agent lifecycle (`desktop/src/main/agents.ts`); `af skill`, `af list`, `af version` are used for skills, registry, and version checks.
- **CLI resolution:** `desktop/src/main/cli.ts` locates the `af` binary (bundled copy or `~/.agentfield/bin/af`), verifies it runs (`spawn(candidate.command, ['version'])`), and enforces a minimum version — "Oldest af this app can drive (needs `af run/stop <name>`, `af skill`)" (`cli.ts:35`).
- Spawns are shell-free (`windowsHide: true`, argv arrays), so no injection surface; child stdout/stderr are streamed and normalized.
- Secrets set through the app map onto the same encrypted `~/.agentfield` store (`af secrets`).

## 4. Autostart and IPC

### Autostart Plan (`desktop/src/main/autostart.ts`)

`autostartAgentPlan` decides at launch what to start:
1. If a control plane is already running on the configured port — adopt it (no restart).
2. If autostart is on and nothing is running — start the control plane itself.
3. Then start any registered agents (per `settings.autostartAgents`).

The app follows a single **active base URL** for the control plane (default `http://localhost:8080`), moved when autostart adopts or starts a control plane on another port — every consumer (snapshot polling, tray, open-web-ui, `AGENTFIELD_SERVER` for spawned `af`) reads it from `getBaseUrl()` (`desktop/src/main/agentfield.ts`).

### IPC Bridge

Sandboxed preload (`desktop/src/preload/index.ts`) exposes a typed `AgentFieldApi` via `contextBridge` over `ipcRenderer.invoke` channels:

`agentfield:snapshot`, `agentfield:catalog`, `agentfield:install`, `agentfield:install-source`, `agentfield:uninstall`, `agentfield:update`, `agentfield:install-progress` (event), `agentfield:agent-action`, `agentfield:start-control-plane`, `agentfield:env-reports`, `agentfield:secret-set` / `secrets-list` / `secret-revoke`, `agentfield:settings-get` / `settings-set`, `agentfield:cli-status` / `cli-update`, `agentfield:app-update-get` / `app-update-check`.

### Data Access

`desktop/src/main/agentfield.ts` is **the single data-access module** — everything that touches the AgentField installation (`~/.agentfield/installed.yaml`) or the control-plane HTTP API lives there. It deliberately avoids importing `electron` so it stays unit-testable under vitest. Secrets/keys/credentials are never stored in the app; they live in the CLI-managed encrypted store.

## 5. af-tray (macOS Menu Bar)

`control-plane/cmd/af-tray/` is a **separate Go binary** for the macOS menu bar, deliberately split from the main `af`/control-plane binary so the GUI/systray dependency never leaks into the server (`af-tray/main.go`). Headless runs (containers, VMs) detect the absence of a GUI session and exit cleanly; non-macOS builds compile to no-op stubs (`tray_other.go`).

Subcommands:
| Command | Purpose |
|---------|---------|
| `af-tray run` | Run the menu-bar tray (default) |
| `af-tray install` | Provision `~/Applications/AgentField.app` + launchd LaunchAgent autostart |
| `af-tray uninstall` | Remove the tray and autostart |
| `af-tray version` | Print version |

Capabilities:
- **Fleet status** — control-plane and node state surfaced from the tray menu
- **24h usage chart** — text-free image renderer drawing a compact 24h histogram plus proportional model/quota bars (`chart_render.go`)
- **Claude quota** — reads the user's Claude Code OAuth token out of the macOS keychain and queries the usage endpoint (`claude_quota_darwin.go`); the token is only ever handed to the quota fetcher
- **launchd autostart** — `launchd_darwin.go` registers a LaunchAgent (`agentfield-af-tray` label); the desktop's `tray-companion.ts` decides whether to provision/install/reload the launchd agent and manages the staged binary (clearing quarantine so launchd can exec it)

## 6. x25519gen (DID Interop Fixture)

`control-plane/cmd/x25519gen/` is a standalone interop fixture that derives an **X25519 key-agreement keypair** using the same HKDF derivation and JWK encoding the DID service uses, printing public/private JWKs as JSON. It exists so control-plane-derived JWKs can be cross-checked against the SDK crypto layer (encrypt to the public JWK, decrypt with the private JWK).

Derivation mirrors `DIDService.deriveX25519PrivateKeyAtEpoch`: HKDF-SHA256 with salt `agentfield-did-keyagreement-v1` and info `<derivationPath>/enc/<epoch>`, so keys rotate per epoch.

## 7. Deployment Relationship

```
+-----------------------------+          +-------------------------------------+
|  AgentField Desktop (Electron) |        |  local `af` / `af server`          |
|  Home / Agents / Activity /  |--HTTP-->|  control plane (Go, Gin)           |
|  Install / Settings          |  :8080  |  - REST API /api/v1/*              |
|  (bundled af + af-tray)      |         |  - gRPC AdminReasonerService :8180 |
+--------------+--------------+         |  - embedded web UI                 |
               |                          +----------------+------------------+
               | spawns `af install/run/stop`             | SQLite/Bolt (local)
               | (af-as-contract)                         | or PostgreSQL (pgvector)
               v                                           v
        ~/.agentfield                         +---------------------+
        - installed.yaml (registry)           | PostgreSQL control   |
        - data/keys/ (DID keystore)           | plane (production)   |
        - secrets/ (encrypted store)          +---------------------+
```

Agent nodes registered via `af install` + `af run` connect back to the control plane over HTTP (`AGENT_CALLBACK_URL`/`AGENT_PUBLIC_URL`); the desktop observes the whole thing through the same control-plane API the CLI uses. The desktop never talks to agents directly.

## 8. Key Source Files

| Path | Contents |
|------|----------|
| `desktop/package.json` | electron-vite build, electron-builder config, `agentfield://` protocol, bundled `af`/`af-tray` binaries |
| `desktop/src/main/index.ts` | Electron main process bootstrap (windows, tray, lifecycle) |
| `desktop/src/main/agentfield.ts` | Single data-access module (registry + control-plane HTTP) |
| `desktop/src/main/cli.ts` | `af` binary resolution and version gating |
| `desktop/src/main/installer.ts` | `af install` spawn/stream/close seam |
| `desktop/src/main/agents.ts` | Agent lifecycle via `af run/stop` |
| `desktop/src/main/autostart.ts` | Autostart plan for control plane + agents |
| `desktop/src/main/tray-companion.ts` | af-tray launchd provisioning management |
| `desktop/src/preload/index.ts` | Sandboxed contextBridge IPC API |
| `desktop/src/renderer/src/App.tsx` | View routing, deep links, cold-launch defaulting |
| `desktop/src/renderer/src/components/*` | DashboardView, AgentsPanel, ActivityPanel, InstallPanel, SettingsPanel |
| `control-plane/cmd/af-tray/*.go` | Menu-bar tray binary (fleet status, usage chart, Claude quota, launchd) |
| `control-plane/cmd/x25519gen/main.go` | DID X25519 key derivation interop fixture |

## Related

- [[agentfield]] -- wiki page for the platform
- [[agentfield-architecture]] -- system architecture
- [[agentfield-api]] -- REST/gRPC API the desktop consumes
- [[agentfield-cli]] -- `af` command reference (the desktop's contract)
- [[agentfield-deployment]] -- deployment guide including desktop/af-tray install
- [[hermes-profiles]] -- AgentField platform profile
