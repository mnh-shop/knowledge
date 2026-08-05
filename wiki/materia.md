---
name: Materia
description: A GitOps tool for managing services and applications deployed as Podman Quadlets, handling full component lifecycle including install, update, and removal
source: sources/materia/
verification_date: 2026-07-12
verified_by: codegraph-verify
tags: [container, deployment, git, infrastructure-as-code, podman, quadlet, security, systemd, golang, materia]
---

# Materia

Materia is a GitOps tool for managing services and applications deployed as [Podman Quadlets](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html). It handles the full lifecycle of components: polling remote sources, installing Quadlets and data files with templating, starting services, updating versions, and cleaning up removed components.

## Architecture Overview

### Core Structure

The application is organized into several key packages:

#### `internal/materia/` - Core Engine
- **Materia struct**: The main orchestrator composing Host, Source, Manifest, Executor, Planner, Notifier, Vault, and Lock components, plus Hostname, Roles, and Rollback flags (`internal/materia/materia.go:35-53`)
- **Plan() method**: Generates action plans by comparing installed vs assigned components
- **Clean()/CleanComponent()**: Removal operations for stale or specific components
- **Rollback support**: `internal/materia/rollback.go` for failure rollback

#### `pkg/components/` - Component Model
- **Component struct**: Represents a deployable unit with 9 fields — Name, Instance, Overrides, Settings, Resources, State, Defaults, ServiceConfigs, Version (`pkg/components/component.go:26-36`)
- **ResourceSet**: Collection of Resources (Quadlet files, secrets, data) with add/delete/list operations
- **ComponentLifecycle states**: StateUnknown, StateStale, StateFresh, StateOK, StateMayNeedUpdate, StateNeedUpdate, StateNeedRemoval, StateRemoved

#### `pkg/planner/` - Planning Logic
- **Planner struct**: Generates action plans by comparing host and source component states
- Uses BuildComponentGraph (`pkg/planner/graph.go`) to create a ComponentTree for comparison
- Handles three scenarios: fresh installs, removals, and updates

#### `pkg/executor/` - Execution Engine
- **Executor struct**: Runs action plans against the host
- Executes resource actions (install/remove/update) and service actions (start/stop/restart)
- Supports volume backup/restore, secret management, network operations
- Execution handlers spread across `quadlet.go`, `unit.go`, `component.go`, `host.go`, `files.go`, `secret.go`, `scripts.go`, `volume.go`

#### `pkg/hostman/` - Host Management
- **HostManager**: Manages containers, services, and component repositories on the host
- Integrates ContainerManager, ServiceManager, and HostFactsManager
- Provides script and unit installation interfaces

#### `pkg/sourceman/` - Source Management
- **SourceManager**: Handles multiple source types (git, OCI, file) for component retrieval
- Supports remote components with subpath configuration (`pkg/manifests/materia.go:26-29`)
- Provides sync and rollback capabilities

#### `pkg/manifests/` - Manifest Configuration
- **MateriaManifest**: Top-level configuration defining Hosts, Roles, Snippets, and Remotes
- **ComponentManifest**: Per-component settings (Defaults, Settings, Snippets, Services, Scripts, Secrets)
- Supports override and extension manifests per host

#### `pkg/actions/` - Action Types
- Action types include: Install, Remove, Update, Start, Stop, Restart, Reload, Enable, Disable, Ensure, Setup, Cleanup, Mount, Import, Dump, Execute (`pkg/actions/actions.go:16-37`)
- Plus `ActionUnknown` sentinel; helpers `IsServiceAction()`, `IsResourceAction()`, `IsHostAction()` categorize actions

#### `pkg/api/` - Varlink API Layer
- Generated varlink interface `systems.primamateria.materia` exposing remote operations (sync, plan, execute) with typed error types like `SyncFailed`, `PlanFailed`, `ExecutionFailed` (`pkg/api/systemsprimamateriamateria.go`)

#### `pkg/notify/` - Notifier
- **Notifier**: Event notification component wired into the Materia struct (`pkg/notify/notify.go`, `notify_config.go`)

#### `pkg/lock/` - Locking
- **Locker**: Coordination lock with D-Bus backend (`pkg/lock/dbus.go`) and file-based fallback (`pkg/lock/file.go`)

#### `pkg/loader/` - Manifest Loading
- Loads manifests, Quadlets, resources, secrets, and templates from sources (`pkg/loader/main.go`, `manifest.go`, `quadlet.go`, `resource.go`, `secret.go`, `template.go`)

#### `pkg/services/` - Service Abstraction
- Service configuration sets, slices, states, and management (`pkg/services/services.go`, `service_set.go`, `service_state.go`, `services_config.go`)

#### `internal/facts/` - Host Facts
- **FactsProvider**: Host facts collection including network facts (`internal/facts/facts.go`, `network.go`)

#### `internal/macros/` - Templating
- **MacroMap / Snippet**: Templating macros and snippets used to render Quadlet/data files (`internal/macros/macro.go`, `snippet.go`)

## Key Interfaces

### HostManager
```go
type HostManager interface {
    ContainerManager
    components.ComponentReader
    components.ComponentWriter
    FactsProvider
    ServiceManager
    ListInstalledComponents() ([]string, error)
    InstallScript(context.Context, string, []byte) error
    RemoveScript(context.Context, string) error
    InstallUnit(context.Context, string, []byte) error
    RemoveUnit(context.Context, string) error
}
```
(Exact match at `internal/materia/host_manager.go:44-55`)

### SourceManager
```go
type SourceManager struct {
    components.ComponentReader
    sourceDir string
    remoteDir string
    sources []sourcePlan
}
```

### Attributes Engines
Multiple vault backends supported:
- Age encryption (age store)
- File-based attributes
- SOPS integration
- In-memory fallback

Vaults are composed with fallback by `setupVault()` (`internal/materia/materia.go:55`), selecting the active backend via the `Attributes` config field.

## Lifecycle Flow

1. **Sync**: SourceManager pulls latest component manifests from configured sources (git, OCI, file)
2. **Plan**: Materia compares installed components against assigned components
3. **Execute**: Executor runs actions in priority order (scripts, resources, services)
4. **Validate**: Optional validation of installed components
5. **Clean**: Remove unassigned components and clean caches

## Source Types

- **Git**: Clone/pull repositories with optional SSH authentication
- **OCI**: Pull from OCI registries
- **File**: Local filesystem sources

## Configuration

- Podman 5.4+ and Systemd v254+ required
- Supports root-full and rootless operation (`materia_config.go:49`, XDG user paths, `DefaultQuadletDir = /etc/containers/systemd`)
- D-Bus locking with file fallback for coordination
- Configurable rollback on failures
- **Containerized mode**: When running Materia itself in a container it uses the Podman remote API, so some features are limited by the host's Podman API version (e.g. volume backups need a host with the matching API level) — README note
- **Test infrastructure**: `virter/` directory contains virter-based integration test configuration (`virter_explore.toml`, auth, config) for exploring repos under test

## Links

## Related

- [[podman]] — Container runtime for Quadlet services
- [[quadlet]] — Systemd-native container management
- [[domains/deployment/INDEX|deployment]] — GitOps deployment patterns


- [Documentation](https://primamateria.systems)
- [Example Repository](https://github.com/stryan/materia_example_repo)
- [Workflow Diagram](./diagram.md)
