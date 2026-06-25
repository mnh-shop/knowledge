---
name: clawpier-architecture
tags: [agent-manager, ai-llm, architecture, clawpier, container, desktop, desktop-app, docker, gui, monitoring, plugin-sdk, rust, security, tauri]
description: "ClawPier Architecture — Tauri Desktop Agent Manager"
source: sources/clawpier/
---
# ClawPier Architecture — Tauri Desktop Agent Manager

| Field | Value |
|---|---|
| **Origin** | [SebastianElvis/clawpier](https://github.com/SebastianElvis/clawpier) |
| **Source** | `sources/clawpier/` |
| **Stack** | Tauri v2 (Rust 2021), React 19 + TypeScript, Vite 6, Tailwind 4, Zustand, Docker (bollard 0.18) |
| **Runtime** | macOS, Linux, Windows (native desktop via Tauri) |

## Overview

ClawPier is a native desktop application built with Tauri v2 that manages OpenClaw and Hermes AI agent instances inside Docker containers. The architecture follows a strict separation: a Rust backend handles all Docker, filesystem, and process management via the bollard Docker SDK, while a React + TypeScript frontend provides the UI. IPC between them uses Tauri's invoke system.

## Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Presentation Layer                          │
│  React 19 + TypeScript + Vite 6 + Tailwind 4 + Zustand         │
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │ Bot Mgmt │ │ Chat     │ │ Monitor  │ │ Skill Browser    │  │
│  │ (lists,  │ │ (session │ │ (stats,  │ │ (ClawHub,        │  │
│  │  cards,  │ │  history,│ │  logs,   │ │  50+ skills,     │  │
│  │  detail) │ │  stream) │ │  health) │ │  install/mgmt)   │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────────┬─────────┘  │
│       │             │            │                 │           │
│       └─────────────┴────────────┴─────────────────┘           │
│                         │ Tauri IPC (invoke)                    │
└─────────────────────────┼───────────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────────┐
│                   Application Layer (Rust)                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │commands  │ │bot_store │ │chat_store│ │streaming         │  │
│  │.rs       │ │.rs       │ │.rs       │ │.rs               │  │
│  │58 IPC    │ │persist   │ │chat      │ │term sessions,    │  │
│  │handlers  │ │bot       │ │history   │ │stats/log streams │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────────┬─────────┘  │
│       │             │            │                 │           │
│       └─────────────┴────────────┴─────────────────┘           │
│                         │ bollard Docker SDK                    │
└─────────────────────────┼───────────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────────┐
│                 Infrastructure Layer                            │
│  ┌──────────────────────┴────────────────────────────────────┐  │
│  │                    Docker Engine                           │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │  │
│  │  │ OpenClaw Bot │ │ Hermes Bot   │ │ OpenClaw Bot │      │  │
│  │  │ (no network) │ │ (opt-in net) │ │ (no network) │      │  │
│  │  │ 1GB RAM      │ │ 2GB RAM      │ │ 512MB RAM    │      │  │
│  │  └──────────────┘ └──────────────┘ └──────────────┘      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Rust Backend Architecture

### Command Layer (`commands.rs`)

58 Tauri commands grouped by domain:

| Group | Commands | Count |
|---|---|---|
| **Docker status** | `check_docker`, `check_docker_health`, `check_image` | 3 |
| **Bot CRUD** | `list_bots`, `create_bot`, `start_bot`, `stop_bot`, `restart_bot`, `delete_bot`, `rename_bot` | 7 |
| **Bot config** | `toggle_network`, `set_auto_start`, `set_workspace_path`, `update_env_vars`, `update_resource_limits`, `set_network_mode`, `update_port_mappings`, `update_health_check`, `update_notification_prefs`, `get_bot_config` | 10 |
| **Config import/export** | `export_config`, `import_config` | 2 |
| **Chat** | `list_chat_sessions`, `create_chat_session`, `rename_chat_session`, `delete_chat_session`, `get_chat_messages`, `send_chat_message`, `stop_chat_response` | 7 |
| **Monitor** | `start_stats_stream`, `stop_stats_stream`, `start_log_stream`, `stop_log_stream`, `get_system_resources` | 5 |
| **Terminal** | `start_terminal_session`, `stop_terminal_session`, `write_terminal_input`, `resize_terminal` | 4 |
| **Workspace** | `list_workspace_files`, `read_workspace_file` | 2 |
| **Exec/debug** | `exec_command`, `log_crash`, `export_logs`, `resolve_telegram_bot` | 4 |
| **ClawHub** | `clawhub_search_skills`, `clawhub_install_skill`, `clawhub_uninstall_skill`, `check_clawhub_available`, `install_clawhub`, `clawhub_inspect_skill`, `get_skill_requirements` | 7 |
| **Port/network** | `check_port_available`, `suggest_port` | 2 |
| **App** | `get_app_version`, `auto_start_bots` | 2 |

### Docker Manager (`docker_manager.rs`)

Wraps the bollard crate for all Docker Engine API interactions:
- Container lifecycle: create (with security-opt, resource limits, network mode), start, stop, kill, remove
- Image operations: pull (streamed), inspect
- Exec: creates exec instances, runs commands, captures output
- Stats: streams container stats (CPU, memory, network I/O)
- Logs: streams container stdout/stderr with timestamps
- Health check: Docker ping + container inspect for health status

### State & Persistence

| Store | Implementation |
|---|---|
| `BotStore` | File-based JSON storage (`~/.clawpier/bots.json`) |
| `ChatStore` | File-based JSON storage per session (`~/.clawpier/chat/`) |
| `AppState` | In-memory shared state via Tokio mutexes (`Arc<TokioMutex<T>>`) |

### Background Polling Loop

On startup, `lib.rs` spawns an async task that polls Docker every 5 seconds:
1. Ping Docker for connectivity
2. Fetch status of all managed bots
3. Detect status transitions (Running → Stopped/Error triggers notifications)
4. Emit events via Tauri's event system (`bot-status-update`, `bot-status-changed`)
5. On 3 consecutive failures: emit `docker-connection-lost`, mark all bots as Error
6. On reconnect: emit `docker-connection-restored`

## React Frontend Architecture

### State Management (Zustand)

| Store | Key State |
|---|---|
| `bot-store.ts` | Bot list, selected bot, bot CRUD operations |
| `toast-store.ts` | Toast notifications |
| `notification-store.ts` | Desktop notification preferences |

### Custom Hooks

| Hook | Purpose |
|---|---|
| `use-container-stats` | Subscribe to real-time CPU/memory/network stream |
| `use-container-logs` | Subscribe to container stdout/stderr stream |
| `use-interactive-terminal` | Manage PTY terminal session lifecycle |
| `use-chat` | Chat message send/receive with streaming responses |
| `use-health-events` | Health check status events |
| `use-resource-alerts` | Alert on resource limit breaches |
| `use-skill-browser` | ClawHub skill registry browsing |
| `use-auto-restart` | Auto-restart event handling |
| `use-keyboard-shortcuts` | Keyboard shortcut registration |
| `use-status-notifications` | Bot status change → desktop notification |
| `use-bot-events` | Bot lifecycle events |
| `use-restart-progress` | Restart progress tracking |
| `use-zoom` | Zoom level management |
| `use-toast` | Toast queue management |

### Strictly Increasing Capability Pattern

Components are designed to reveal progressively more capability as the user engages:

1. **BotCard** → minimal status + quick actions
2. Click → **BotDetail** → full config, resource limits, env vars, port mappings
3. Detail → **ChatTab / Terminal / LogViewer / FileBrowser** → advanced interaction

### Key Components

| Component | Purpose |
|---|---|
| `BotCard`, `BotList`, `BotListHeader` | Bot management dashboard |
| `BotDetail`, `ConfigDashboard` | Bot configuration panels |
| `NewBotSheet` | Bot creation wizard |
| `ChatTab`, `ChatMessage` | Agent chat interface |
| `LogViewer` | Real-time log streaming |
| `Terminal` (via xterm.js) | PTY shell |
| `FileBrowser` | Workspace file exploration |
| `SkillBrowser` | ClawHub registry browser |
| `NetworkModePicker` | Network sandbox controls |
| `ResourceLimitsEditor` | CPU/RAM limit controls |
| `PortMappingEditor` | Port forwarding config |
| `EnvVarEditor` | Environment variable management |
| `NotificationCenter` | Desktop notification UI |
| `DockerConnectionBanner` | Docker connectivity status |

## Chat Architecture

When sending a message to a bot, ClawPier:

1. Builds the agent-specific CLI command (`build_agent_chat_cmd`)
   - **OpenClaw:** `openclaw agent --local --agent main --session-id clawpier-{id} --message "{msg}"`
   - **Hermes:** `hermes chat -Q -q "{msg}"`
2. Executes the command inside the bot's container via Docker exec
3. Streams output back to the frontend via Tauri events
4. Strips metadata — for Hermes, removes box-drawing headers and `session_id:` lines
5. Persists messages to the chat store

## Security Model

- Containers created with `--network none` by default
- Network access is opt-in: per-bot toggle with port mapping configuration
- Resource limits set via Docker cgroups (CPU shares, memory limits)
- No host filesystem access except configured workspace mount
- Docker socket access required (standard Tauri permission prompt)

## Related

- [[clawpier]] — Wiki entry
- [[clawpier-deployment]] — Deployment guide
- [[clawpier-profile]] — Agent profile
- [[openclaw]] — Primary agent runtime
- [[hermes-agent]] — Secondary agent runtime
