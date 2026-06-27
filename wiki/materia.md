---
name: Materia
description: A GitOps tool for managing services and applications deployed as Podman Quadlets, handling full component lifecycle including install, update, and removal
source: sources/materia/
tags: [container, deployment, git, infrastructure-as-code, podman, quadlet, security, systemd, golang]
---

# Materia

Materia is a GitOps tool for managing services and applications deployed as [Podman Quadlets](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html). It handles the full lifecycle of components: polling remote sources, installing Quadlets and data files with templating, starting services, updating versions, and cleaning up removed components.

## Architecture Overview

### Core Structure

The application is organized into several key packages:

#### `internal/materia/` - Core Engine
- **Materia struct**: The main orchestrator combining Host, Source, Manifest, Executor, Planner, and Vault components
- **Plan() method**: Generates action plans by comparing installed vs assigned components
- **Clean()/CleanComponent()**: Removal operations for stale or specific components

#### `pkg/components/` - Component Model
- **Component struct**: Represents a deployable unit with Name, Instance, Settings, Resources, State, and Version
- **ResourceSet**: Collection of Resources (Quadlet files, secrets, data) with add/delete/list operations
- **ComponentLifecycle states**: StateUnknown, StateFresh, StateOK, StateNeedUpdate, StateNeedRemoval

#### `pkg/planner/` - Planning Logic
- **Planner struct**: Generates action plans by comparing host and source component states
- Uses BuildComponentGraph to create a ComponentTree for comparison
- Handles three scenarios: fresh installs, removals, and updates

#### `pkg/executor/` - Execution Engine
- **Executor struct**: Runs action plans against the host
- Executes resource actions (install/remove/update) and service actions (start/stop/restart)
- Supports volume backup/restore, secret management, network operations

#### `pkg/hostman/` - Host Management
- **HostManager**: Manages containers, services, and component repositories on the host
- Integrates ContainerManager, ServiceManager, and HostFactsManager
- Provides script and unit installation interfaces

#### `pkg/sourceman/` - Source Management
- **SourceManager**: Handles multiple source types (git, OCI, file) for component retrieval
- Supports remote components with subpath configuration
- Provides sync and rollback capabilities

#### `pkg/manifests/` - Manifest Configuration
- **MateriaManifest**: Top-level configuration defining Hosts, Roles, Snippets, and Remotes
- **ComponentManifest**: Per-component settings (Defaults, Settings, Snippets, Services, Scripts, Secrets)
- Supports override and extension manifests per host

#### `pkg/actions/` - Action Types
- Action types include: Install, Remove, Update, Start, Stop, Restart, Reload, Enable, Disable, Setup, Cleanup, Mount, Import, Dump, Execute

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
- Supports root-full and rootless operation
- D-Bus locking for coordination
- Configurable rollback on failures

## Links

## Related

- [[podman]] — Container runtime for Quadlet services
- [[quadlet]] — Systemd-native container management
- [[deployment]] — GitOps deployment patterns


- [Documentation](https://primamateria.systems)
- [Example Repository](https://github.com/stryan/materia_example_repo)
- [Workflow Diagram](./diagram.md)