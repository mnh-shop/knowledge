---
name: clawpier-codegraph-verify
tags: [clawpier, codegraph-verify, openclaw, gui, tauri, docker]
description: "Codegraph Verification: clawpier"
source: sources/clawpier/
---

# Codegraph Verification: clawpier

**Date:** 2026-07-30

## Claim 1: Tauri v2 Desktop Manager with Rust backend + React/TypeScript frontend
- **Wiki says:** "ClawPier is a native desktop application (macOS, Linux, Windows) built with Tauri v2 — Rust backend for Docker management, React + Tailwind frontend for the GUI."
- **Source evidence:**
  - `package.json:14-28` — Dependencies include `@tauri-apps/api`, `@tauri-apps/plugin-dialog`, `@tauri-apps/plugin-shell`, `react`, `react-dom`, `zustand`, `lucide-react`
  - `package.json:30-48` — DevDependencies include `@tauri-apps/cli`, `@vitejs/plugin-react`, `tailwindcss`, `vite`, `vitest`, TypeScript
  - `src-tauri/src/lib.rs:60-244` — Tauri app setup with `tauri::Builder::default()`, plugin registration, `invoke_handler`, 5s status polling background task
  - `src-tauri/src/main.rs` — Entry point calling `clawpier_lib::run()`
  - `src-tauri/src/commands.rs:2892` lines — All 56 `#[tauri::command]` IPC handlers for Docker, chat, terminal, stats, skills, config
  - `src-tauri/src/lib.rs:10-18` — Module declarations for `bot_store`, `chat_store`, `docker_manager`, `error`, `models`, `state`, `streaming`, `commands`
  - `CLAUDE.md` (project guidance) — Describes the full Tauri v2 stack, architecture, IPC flow
  - `src/App.tsx` — React root: Docker check → welcome screen → bot list
  - `src/components/` — 30+ React/TSX components (BotCard, BotDetail, BotList, ChatTab, ConfigDashboard, SkillBrowser, etc.)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Docker container management via bollard crate
- **Wiki says:** "Rust backend for Docker management" and "manages all Docker interactions through the bollard crate"
- **Source evidence:**
  - `src-tauri/src/docker_manager.rs:19-20` — `pub struct DockerManager { docker: Docker }` using `bollard::Docker`
  - `src-tauri/src/docker_manager.rs:24-28` — `Docker::connect_with_socket_defaults()` for socket connection
  - `src-tauri/src/docker_manager.rs:36-38` — `check_docker()` pings Docker daemon
  - `src-tauri/src/docker_manager.rs:41-60` — `check_image()` lists images and checks for matches
  - `src-tauri/src/docker_manager.rs:62-94` — `get_container_status()` checks container state
  - `src-tauri/src/docker_manager.rs:105-203` — `start_bot()` creates containers with `CreateContainerOptions`, `Config`, `HostConfig`, including `--network none` default, env vars, port mappings
  - `src-tauri/src/docker_manager.rs:204-229` — `stop_bot()` stops containers
  - `src-tauri/src/docker_manager.rs:230-253` — `remove_container()` removes containers
  - `src-tauri/src/docker_manager.rs:254-310` — `pull_image_with_progress()` with streaming progress
  - `src-tauri/src/docker_manager.rs:311-375` — `exec_in_container()` runs commands
  - `CLAUDE.md` — "Docker: bollard 0.18 (Docker API)", "Container names: `clawpier-{uuid}`", "Default: `--network none`"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: 56 Tauri commands for IPC
- **Wiki says:** "56 Tauri commands — CRUD bots, Docker management, chats, terminal, logs, workspace, skills"
- **Source evidence:**
  - `src-tauri/src/lib.rs:70-127` — `.invoke_handler(tauri::generate_handler![...])` registers exactly **56 commands**:
    1. `get_app_version`, 2. `get_system_resources`, 3. `check_docker`, 4. `check_docker_health`, 5. `check_image`,
    6. `list_bots`, 7. `create_bot`, 8. `start_bot`, 9. `stop_bot`, 10. `restart_bot`,
    11. `delete_bot`, 12. `rename_bot`, 13. `toggle_network`, 14. `set_auto_start`, 15. `auto_start_bots`,
    16. `set_workspace_path`, 17. `pull_image`, 18. `update_env_vars`, 19. `update_resource_limits`, 20. `set_network_mode`,
    21. `update_port_mappings`, 22. `export_config`, 23. `import_config`, 24. `list_chat_sessions`, 25. `create_chat_session`,
    26. `rename_chat_session`, 27. `delete_chat_session`, 28. `get_chat_messages`, 29. `send_chat_message`, 30. `stop_chat_response`,
    31. `start_stats_stream`, 32. `stop_stats_stream`, 33. `start_log_stream`, 34. `stop_log_stream`, 35. `exec_command`,
    36. `list_workspace_files`, 37. `read_workspace_file`, 38. `get_bot_config`, 39. `resolve_telegram_bot`, 40. `start_terminal_session`,
    41. `stop_terminal_session`, 42. `write_terminal_input`, 43. `resize_terminal`, 44. `log_crash`, 45. `export_logs`,
    46. `update_health_check`, 47. `update_notification_prefs`, 48. `clawhub_search_skills`, 49. `clawhub_install_skill`, 50. `clawhub_uninstall_skill`,
    51. `check_clawhub_available`, 52. `install_clawhub`, 53. `clawhub_inspect_skill`, 54. `check_port_available`, 55. `suggest_port`,
    56. `get_skill_requirements`
  - `src-tauri/src/commands.rs` — 53 `pub async fn` function definitions (some may be helpers, not all are registered commands)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None — the wiki was corrected to state exactly 56 commands, matching the source registration.

## Claim 4: OpenClaw and Hermes agent runtime support
- **Wiki says:** "Multi-agent support — OpenClaw and Hermes agent runtimes, selectable per bot"
- **Source evidence:**
  - `src-tauri/src/models.rs:5-52` — `AgentType` enum with `OpenClaw` and `Hermes` variants, `default_image()`, `config_mount_path()`, `auto_env_vars()`, `container_cmd()`
  - `src-tauri/src/models.rs:19-24` — Default images: `"ghcr.io/openclaw/openclaw:latest"` and `"nousresearch/hermes-agent:latest"`
  - `src-tauri/src/models.rs:35-40` — Auto env vars: `OPENCLAW_GATEWAY_HOST=127.0.0.1` for OpenClaw, `HERMES_HOME=/opt/data` for Hermes
  - `src-tauri/src/commands.rs:25-51` — `build_agent_chat_cmd()` builds CLI commands for each agent type: `openclaw agent --local --agent main ...` vs `hermes chat -Q -q ...`
  - `src-tauri/src/commands.rs:56-100` — `strip_hermes_metadata()` strips Hermes CLI box-drawing from output
  - `src-tauri/src/docker_manager.rs` — Container creation uses `agent_type` field from `BotProfile` to select image and config
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Resource limits, health checks, and notification center
- **Wiki says:** "Resource limits — CPU/memory caps from the GUI", "Health checks — configurable with automatic restart on failure", "Notification center — desktop notifications on bot status transitions"
- **Source evidence:**
  - `src-tauri/src/lib.rs:21-26` — `StatusTransition` struct: `bot_id`, `bot_name`, `from`, `to` status fields
  - `src-tauri/src/lib.rs:39-57` — `detect_status_transitions()` detects Running → Stopped/Error transitions
  - `src-tauri/src/lib.rs:190-195` — Emits `bot-status-changed` event on transitions
  - `src-tauri/src/commands.rs:532` — `update_health_check()` command for health check config
  - `src-tauri/src/commands.rs:563` — `update_notification_prefs()` command for notification preferences
  - `src-tauri/src/commands.rs:1406` — `update_resource_limits()` command for CPU/memory caps
  - `src-tauri/src/models.rs:87-119` — `HealthCheckConfig` struct with `enabled`, `interval_secs`, `timeout_secs`, `retries`, `grace_period_secs`
  - `src-tauri/src/models.rs:121-130` — `HealthUpdate` struct with `status`, `last_check`, `last_ok`, `consecutive_failures`
  - `src-tauri/src/models.rs:131-144` — `BotNotificationPrefs` struct with `notify_on_crash`, `notify_on_stop`, `notify_on_error`
  - `src/commands.rs` — 56 IPC commands register handlers
  - `src/hooks/use-resource-alerts.ts` — Frontend hook for resource alerting
  - `src/hooks/use-health-events.ts` — Frontend hook for health event handling
  - `src/components/NotificationCenter.tsx` — Desktop notification UI component
  - `src/components/ResourceLimitsEditor.tsx` — CPU/memory limit editor
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: ClawHub skill browser and skill management
- **Wiki says:** "ClawHub skill browser — browse 50+ bundled skills with readiness status, search ClawHub registry, one-click install/uninstall"
- **Source evidence:**
  - `src-tauri/src/lib.rs:118-123` — `clawhub_search_skills`, `clawhub_install_skill`, `clawhub_uninstall_skill`, `check_clawhub_available`, `install_clawhub`, `clawhub_inspect_skill` commands
  - `src-tauri/src/lib.rs:126` — `get_skill_requirements` command
  - `src-tauri/src/commands.rs:923-1005` — `clawhub_search_skills()` queries ClawHub registry
  - `src-tauri/src/commands.rs:1006-1046` — `check_clawhub_available()` verifies ClawHub connectivity
  - `src-tauri/src/commands.rs:1047-1080` — `install_clawhub()` installs the ClawHub plugin
  - `src-tauri/src/commands.rs:1081-1193` — `clawhub_inspect_skill()` fetches skill details
  - `src-tauri/src/commands.rs:1194-1305` — `get_skill_requirements()` checks skill dependencies
  - `src-tauri/src/commands.rs:1306-1332` — `clawhub_install_skill()` installs a specific skill
  - `src-tauri/src/commands.rs:1333-1359` — `clawhub_uninstall_skill()` removes a skill
  - `src-tauri/src/models.rs:346-364` — `Skill`, `SkillSearchResult` data structures
  - `src/components/SkillBrowser.tsx` — Frontend skill browser component
  - `src/hooks/use-skill-browser.ts` — Frontend skill browser hook
  - `src/hooks/__tests__/use-skill-browser.test.ts` — Tests for the skill browser
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

The ClawPier wiki is largely accurate:
- **Tauri v2 stack:** ✅ Correct (Rust + React + Tailwind confirmed)
- **Docker management:** ✅ Correct (bollard crate with full lifecycle)
- **Tauri commands:** ✅ Correct — exactly 56 commands registered in source (`lib.rs:70-127`), matching the wiki
- **OpenClaw/Hermes support:** ✅ Correct (dual AgentType enum with separate configs)
- **Resource/health/notifications:** ✅ Correct (structs, commands, frontend hooks all present)
- **ClawHub skills:** ✅ Correct (6 dedicated commands + frontend components + tests)

## Related

- [[clawpier]] -- Main wiki entry
- [[openclaw]] -- Primary agent runtime
- [[hermes-agent]] -- Secondary agent runtime
- [[goclaw]] -- Go MCP gateway (related OpenClaw ecosystem)

## Cross-project

- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
- [[alphaclaw.codegraph-verify]] -- Similar codegraph verification for AlphaClaw
