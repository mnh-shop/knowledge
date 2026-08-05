---
name: materia-codegraph-verify
tags: [materia, codegraph-verify, gitops, quadlet, podman, golang, deployment, infrastructure]
description: "Codegraph Verification: materia — validating wiki claims against indexed source code"
source: sources/materia/
---

# Codegraph Verification: materia

**Date:** 2026-07-12

## Claim 1: GitOps lifecycle manager for Podman Quadlets
- **Wiki says:** "Materia is a GitOps tool for managing services and applications deployed as Podman Quadlets. It handles the full lifecycle of components: polling remote sources, installing Quadlets and data files with templating, starting services, updating versions, and cleaning up removed components."
- **Source evidence:**
  - `internal/materia/materia.go:35-53` — `Materia` struct composing `Host`, `Source`, `Manifest`, `Executor`, `Planner`, `Notifier`, `Vault`, `Hostname`, `Roles`, `Lock`, `Rollback` (plus unexported `macros`, `snippets`, `OutputDir`)
  - `internal/materia/materia.go` — `Plan()` and `Clean()`/`CleanComponent()` methods for lifecycle management
  - `pkg/planner/planner.go` — `Planner.Plan()` comparing installed vs assigned components to generate action plans
  - `pkg/executor/execute.go` — `Executor` running action plans against the host
  - `pkg/executor/quadlet.go` — Quadlet file installation and management
  - `pkg/executor/unit.go` — Systemd unit operations (start, stop, restart, enable, disable)
  - `pkg/executor/component.go` — Component-level execution
  - `pkg/executor/host.go` — Host-level execution
- **Verdict:** ✅ CORRECT (Notifier and Lock fields now documented in wiki)
- **Fix needed:** None

## Claim 2: Component model with lifecycle state machine
- **Wiki says:** "Component struct represents a deployable unit with 9 fields — Name, Instance, Overrides, Settings, Resources, State, Defaults, ServiceConfigs, Version. ComponentLifecycle states: StateUnknown .. StateNeedRemoval."
- **Source evidence:**
  - `pkg/components/component.go:26-36` — `Component` struct with exactly 9 exported fields: `Name`, `Instance`, `Overrides`, `Settings`, `Resources`, `State`, `Defaults`, `ServiceConfigs`, `Version`
  - `pkg/components/component.go:41-49` — `ComponentLifecycle` enum: `StateUnknown`, `StateStale`, `StateFresh`, `StateOK`, `StateMayNeedUpdate`, `StateNeedUpdate`, `StateNeedRemoval`, `StateRemoved`
  - `pkg/components/componentlifecycle_string.go` — Stringer for lifecycle states
  - `pkg/components/resourceset.go` — `ResourceSet` with add/delete/list operations
  - `pkg/components/resource.go` — `Resource` type definition
  - `pkg/components/resourcetype_string.go` — Resource type enum
  - `pkg/components/repository.go` — Component repository
  - `pkg/components/service_config_set.go` — Service configuration set for components
- **Verdict:** ✅ CORRECT (earlier wiki listed only 6 of the 9 fields; Overrides, Defaults, ServiceConfigs were missing)
- **Fix needed:** Applied — wiki now lists all 9 fields

## Claim 3: Multi-source retrieval (git, OCI, file) with sync and rollback
- **Wiki says:** "SourceManager handles multiple source types (git, OCI, file) for component retrieval. Supports remote components with subpath configuration. Provides sync and rollback capabilities."
- **Source evidence:**
  - `pkg/sourceman/sourceman.go` — `SourceManager` implementation
  - `internal/source/` — Source type implementations: `git/`, `oci/`, `file/` subdirectories
  - `pkg/manifests/materia.go:26-29` — `RemoteComponentConfig` with `GitSource *git.Config`, `OciSource *oci.Config`, `FileSource *filesource.Config`, and `Subpath string`
  - `internal/materia/source_manager.go` — Source management integration in the core engine
  - `internal/materia/materia.go` — `Rollback` field and rollback support via `internal/materia/rollback.go`
  - `pkg/manifests/materia.go:32-38` — `MateriaManifest` with `Remotes map[string]RemoteComponentConfig`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Action-based execution with 16 named actions + ActionUnknown
- **Wiki says:** "Action types include: Install, Remove, Update, Start, Stop, Restart, Reload, Enable, Disable, Ensure, Setup, Cleanup, Mount, Import, Dump, Execute. Plus `ActionUnknown` sentinel."
- **Source evidence:**
  - `pkg/actions/actions.go:16-37` — Action type enum: `ActionUnknown` (sentinel, iota 0) followed by exactly 16 named actions: `ActionInstall`, `ActionRemove`, `ActionUpdate`, `ActionStart`, `ActionStop`, `ActionRestart`, `ActionReload`, `ActionEnable`, `ActionDisable`, `ActionEnsure`, `ActionSetup`, `ActionCleanup`, `ActionMount`, `ActionImport`, `ActionDump`, `ActionExecute`
  - `pkg/actions/actions.go:39-49` — Methods `IsServiceAction()`, `IsResourceAction()`, `IsHostAction()` for action categorization
  - `pkg/actions/actiontype_string.go` — Stringer for action types (generated via `stringer`)
  - `pkg/executor/` — Action execution handlers in sub-files: `quadlet.go` (resource actions), `service_helpers.go` (service actions), `host.go` (host actions), `files.go` (file operations), `secret.go` (secret management), `scripts.go` (script execution), `volume.go` (volume management)
- **Verdict:** ✅ CORRECT (16 named actions + `ActionUnknown` sentinel — earlier verify page miscounted as "17 action types")
- **Fix needed:** Applied — verify page now states "16 named actions + ActionUnknown"

## Claim 5: Attributes/Vault engine with multiple backends
- **Wiki says:** "Attributes Engines: Multiple vault backends supported: Age encryption, File-based attributes, SOPS integration, In-memory fallback. Vaults composed with fallback by setupVault() selecting via the Attributes config field."
- **Source evidence:**
  - `internal/attributes/` — Attributes engine directory
  - `internal/attributes/age/` — Age encryption store (`age.NewAgeStore`)
  - `internal/attributes/file/` — File-based attributes store (`fileattrs.NewFileStore`)
  - `internal/attributes/sops/` — SOPS integration (`sops.NewSopsStore`)
  - `internal/attributes/mem/` — In-memory fallback store
  - `internal/materia/materia.go:55` — `setupVault()` function composing multiple vaults with fallback
  - `internal/materia/materia_config.go:50` — `Attributes string` config field selecting active backend
  - `internal/materia/attribute_engine.go` — `AttributesEngine` interface definition
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: D-Bus + file locking, rootless/root-full support, containerized Podman remote mode
- **Wiki says:** "Supports root-full and rootless operation, D-Bus locking with file fallback for coordination, Configurable rollback on failures, Containerized mode uses the Podman remote API."
- **Source evidence:**
  - `pkg/lock/dbus.go` — D-Bus locking backend
  - `pkg/lock/file.go` — File-based locking fallback
  - `pkg/lock/error.go` — Lock error types
  - `internal/materia/lock.go` — Lock integration in core engine
  - `internal/materia/materia_config.go:49` — `Rootless bool` config field for rootless mode
  - `internal/materia/materia_config.go:22-23` — `DefaultQuadletDir = "/etc/containers/systemd"` (system-wide) vs XDG user-mode paths for rootless
  - `internal/materia/materia.go` — `Rollback bool` field for failure rollback; `internal/materia/rollback.go` implementation
  - `README.md:42` — Containerized mode uses the Podman remote API; features limited by host Podman API version
  - `pkg/containers/` — Container management (volumes, networks, images) supporting both modes
  - `pkg/services/` — Service management abstraction
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Undocumented packages and tooling
- **Wiki says:** "Additional packages: pkg/api (varlink API layer), pkg/notify (Notifier), pkg/loader, pkg/services, internal/facts, internal/macros; virter/ test infrastructure."
- **Source evidence:**
  - `pkg/api/systemsprimamateriamateria.go` — Generated varlink interface `systems.primamateria.materia` with typed errors `SyncFailed`, `PlanFailed`, `ExecutionFailed`
  - `pkg/api/systems.primamateria.materia.varlink` — Varlink interface definition
  - `pkg/notify/notify.go` + `notify_config.go` — `notify.Notifier` wired into the Materia struct
  - `pkg/loader/` — `main.go`, `manifest.go`, `quadlet.go`, `resource.go`, `secret.go`, `template.go` (source loading)
  - `pkg/services/` — `services.go`, `service_set.go`, `service_slice.go`, `service_state.go`, `services_config.go`
  - `internal/facts/facts.go` + `network.go` — Host facts provider
  - `internal/macros/macro.go` + `snippet.go` — Templating macros and snippets (`macros.MacroMap`)
  - `virter/virter_explore.toml`, `virter/config.toml`, `virter/auth/` — virter-based integration test infrastructure
- **Verdict:** ✅ CORRECT
- **Fix needed:** None (all previously undocumented in the wiki)

## Summary

All 7 key claims from the Materia wiki have been verified against the source code:
- ✅ **GitOps lifecycle:** `Materia` struct with Plan/Execute/Clean, incl. Notifier + Lock fields, confirmed
- ✅ **Component model:** 9-field struct + full lifecycle state machine in `pkg/components/` confirmed
- ✅ **Multi-source retrieval:** Git, OCI, and file sources with subpath config confirmed
- ✅ **Action system:** 16 named actions + `ActionUnknown` sentinel with categorized execution handlers confirmed
- ✅ **Vault/Attributes:** Age, File, SOPS, and in-memory backends confirmed
- ✅ **Locking + modes:** D-Bus + file lock, rootless/root-full, containerized Podman remote API confirmed
- ✅ **Additional packages:** varlink API, Notifier, loader, services, facts, macros, virter confirmed

The codebase is a well-structured Go application implementing a clean GitOps cycle: sync sources → plan differences → execute actions → validate → clean. Its component model and action system provide the foundation for reliable Quadlet-based container deployment management.

## Related

- [[materia]] -- Main wiki entry
- [[materia-architecture]] -- System architecture
- [[podman]] -- Container runtime for Quadlet services
- [[quadlet]] -- Systemd-native container management

## Cross-project

- [[podman.codegraph-verify]] -- Container runtime foundation
- [[tank-os.codegraph-verify]] -- Deployment OS using Quadlet
- [[bootc]] -- Bootable container technology
- [[nanobot.codegraph-verify]] -- Agent framework with complementary deployment patterns
