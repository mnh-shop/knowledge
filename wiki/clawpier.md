# ClawPier — Tauri Desktop App for Managing Sandboxed AI Agents

| Field | Value |
|---|---|
| **Origin** | [SebastianElvis/clawpier](https://github.com/SebastianElvis/clawpier) |
| **License** | MIT |
| **Stack** | Tauri v2 (Rust + React/TypeScript), Docker |
| **Source** | `sources/clawpier/` |
| **Wanted** | Desktop GUI to manage OpenClaw and Hermes agents inside Docker containers — sandboxed from the host |

## What it is

ClawPier is a native desktop application (macOS, Linux, Windows) for running OpenClaw and Hermes AI agents inside Docker containers. Every agent runs sandboxed by default (`--network none`), with network access opt-in per bot. Built with Tauri v2 — Rust backend for Docker management, React + Tailwind frontend for the GUI.

The key problem it solves: AI agents have OS-level access (email, files, messaging), and prompt injection can turn that into host compromise (CVE-2026-25253, CVSS 8.8). ClawPier's container-first design makes sandboxing the default.

## Features

- **Multi-agent support** — OpenClaw and Hermes agent runtimes, selectable per bot
- **Sandbox by default** — containers create with `--network none`; network opt-in per bot
- **Resource limits** — CPU/memory caps from the GUI (cgroups via Docker flags)
- **Bot management dashboard** — create, start, stop, restart, delete bots
- **Health checks** — configurable with automatic restart on failure
- **Auto-start** — bots start automatically when ClawPier launches
- **ClawHub skill browser** — browse 50+ bundled skills with readiness status, search ClawHub registry, one-click install/uninstall
- **Live terminal** — full PTY shell into any running container
- **Live logs** — real-time container log streaming with timestamps
- **File browser** — browse and preview files in bot's workspace
- **Resource monitoring** — live CPU, memory, network I/O per bot
- **Chat interface** — send messages to agents and view responses with session persistence
- **Config dashboard** — agent-specific config (model, provider, platforms, settings)
- **Notification center** — desktop notifications on bot status transitions (Running → Stopped/Error)
- **Import/export** — bot configs as JSON/YAML
- **Homebrew install** — available via `brew install --cask clawpier`

## Architecture

```
┌──────────────────────────────────────────────────┐
│                 Tauri Shell                       │
│  ┌─────────────────┐  ┌──────────────────────┐  │
│  │  React Frontend  │  │  Rust Backend         │  │
│  │  (Vite + TSX)    │◄─►  (Tauri IPC Bridge)  │  │
│  │                   │  │  58 Tauri commands   │  │
│  │  Components:      │  │                      │  │
│  │  • BotList/Card   │  │  Modules:            │  │
│  │  • BotDetail      │  │  • docker_manager    │  │
│  │  • ChatTab        │  │  • bot_store         │  │
│  │  • SkillBrowser   │  │  • chat_store        │  │
│  │  • FileBrowser    │  │  • streaming         │  │
│  │  • LogViewer      │  │  • state             │  │
│  │  • Terminal       │  │  • models            │  │
│  └─────────────────┘  └──────────┬───────────┘  │
└──────────────────────────────────┼──────────────┘
                                   │ Docker API (bollard)
                                   ▼
┌──────────────────────────────────────────────────┐
│              Docker Engine                       │
│  ┌──────────────────────────────────────────┐   │
│  │  Container 1: OpenClaw (--network none)  │   │
│  │  Container 2: Hermes   (--network custom)│   │
│  │  Container 3: OpenClaw (--network none)  │   │
│  └──────────────────────────────────────────┘   │
└──────────────────────────────────────────────────┘
```

### Rust Backend

The Tauri backend (`src-tauri/src/`) manages all Docker interactions through the bollard crate:

| Module | Purpose |
|---|---|
| `lib.rs` | App setup, IPC handler registration, background status polling (5s interval) |
| `commands.rs` | 58 Tauri commands — CRUD bots, Docker management, chats, terminal, logs, workspace, skills |
| `docker_manager.rs` | Docker API wrapper via bollard: pull images, create/start/stop/exec containers, stats streams |
| `bot_store.rs` | Bot profile persistence (local file-based on disk) |
| `chat_store.rs` | Chat session persistence |
| `models.rs` | Data types: BotProfile, BotStatus, AgentType, EnvVar, NetworkMode, PortMapping, ChatMessage, etc. |
| `state.rs` | Shared application state (`AppState` with tokio mutexes) |
| `streaming.rs` | Interactive terminal sessions, container stats and log streams |
| `error.rs` | Error types (`AppError` enum) |

Key dependencies: tauri 2, bollard 0.18 (Docker API), serde/serde_json/serde_yaml, tokio, reqwest, sysinfo, chrono, uuid.

### React Frontend

State management via zustand stores: `bot-store.ts`, `toast-store.ts`, `notification-store.ts`.

Custom hooks for real-time features: `use-container-stats`, `use-container-logs`, `use-interactive-terminal`, `use-chat`, `use-health-events`, `use-resource-alerts`, `use-skill-browser`.

Component design follows a "strictly increasing capability" pattern: UI progressively reveals more features as the user engages — bot cards expand to show detail panels, detail panels expand to show terminal/logs/files, etc.

## ClawHub

ClawPier includes a built-in skill browser (ClawHub) that connects to a community skill registry. Skills are OpenClaw skills that extend agent capabilities (web browsing, file operations, memory, search, etc.). The browser shows 50+ bundled skills with:
- Readiness status (dependencies met or missing)
- Search against the ClawHub registry
- One-click install/uninstall from the GUI
- Detail view with metadata, author, dependency info

## Installation

| Platform | Method |
|---|---|
| macOS (Apple Silicon) | `brew tap SebastianElvis/clawpier && brew install --cask clawpier` |
| macOS (DMG) | Download `.dmg` from [Releases](https://github.com/SebastianElvis/clawpier/releases) |
| Linux | `.AppImage` or `.deb` from Releases |
| Windows | `.exe` installer or `.msi` from Releases |

Prerequisite: Docker must be installed and running.

## Integration with Core Systems

- **OpenClaw** — Primary supported agent runtime. ClawPier pulls `ghcr.io/openclaw/openclaw:latest` and manages bot instances.
- **Hermes** — Secondary supported agent runtime. ClawPier pulls `nousresearch/hermes-agent:latest` and manages bot instances.
- **ClawHub** — Community skill registry for OpenClaw skills, accessible from the ClawPier GUI.

## Related

- [[openclaw]] — The primary agent runtime ClawPier manages
- [[hermes-agent]] — The secondary agent runtime ClawPier manages
- [[hermes-agent-docker]] — Alternative Docker packaging for Hermes (without the desktop GUI)
- [[hermes-suite]] — Alternative all-in-one Hermes container
- [[mission-control]] — Web-based alternative dashboard for agent orchestration
