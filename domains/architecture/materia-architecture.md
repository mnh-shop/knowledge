---
name: materia-architecture
tags: [materia, architecture, agent, framework, gitops, quadlet, podman, golang, deployment]
description: Materia Architecture — GitOps Quadlet lifecycle manager with component state machine, vault engine, and D-Bus locking
source: sources/materia/
---

# Materia Architecture
**Source:** `sources/materia/`

Materia is a GitOps tool for managing services deployed as Podman Quadlets. It handles the full component lifecycle — polling sources, installing Quadlets and data files with templating, starting services, updating versions, and cleaning up removed components.

## Architecture

### Core Engine (`internal/materia/`)

The `Materia` struct orchestrates six subsystems: Host, Source, Manifest, Executor, Planner, and Vault. The `Plan()` method generates action plans by comparing installed vs assigned components. `Clean()`/`CleanComponent()` handle removal of stale components.

### Component State Machine (`pkg/components/`)

Components are the central deployable unit with fields for Name, Instance, Settings, Resources, State, and Version. Lifecycle states:

```
StateUnknown → StateFresh → StateOK → StateNeedUpdate → StateNeedRemoval
```

Each component carries a `ResourceSet` — Quadlet files, secrets, and data files with add/delete/list operations.

### Planner (`pkg/planner/`)

The Planner generates action plans by comparing host and source component states via `BuildComponentGraph`, producing a `ComponentTree` for comparison. Three scenarios: fresh installs, removals, and updates. Action types span Install, Remove, Update, Start, Stop, Restart, Reload, Enable, Disable, Setup, Cleanup, Mount, Import, Dump, Execute.

### Executor (`pkg/executor/`)

Runs action plans against the host — resource actions (install/remove/update Quadlet files, secrets, volumes, scripts, units) and service actions (start/stop/restart). Supports volume backup/restore, secret management via vault backends, and network operations.

### Host Management (`pkg/hostman/`)

HostManager is a composed interface wrapping ContainerManager, ComponentReader/Writer, FactsProvider, and ServiceManager. Manages containers, services, and component repositories on the host via Podman and systemd.

### Source Management (`pkg/sourceman/`)

Supports three source types for component retrieval:
- **Git** — Clone/pull repositories with optional SSH authentication
- **OCI** — Pull from OCI registries
- **File** — Local filesystem paths

Remote components support subpath configuration and rollback.

### Manifest System (`pkg/manifests/`)

`MateriaManifest` is the top-level configuration defining Hosts, Roles, Snippets, and Remotes. `ComponentManifest` defines per-component settings (Defaults, Settings, Snippets, Services, Scripts, Secrets). Supports override and extension manifests per host.

### Lifecycle Flow

1. **Sync** — SourceManager pulls latest component manifests
2. **Plan** — Materia compares installed vs assigned components
3. **Execute** — Executor runs actions in priority order (scripts → resources → services)
4. **Validate** — Optional validation of installed components
5. **Clean** — Remove unassigned components and caches

### Vault and Attributes

Multiple vault backends: Age encryption (age store), file-based attributes, SOPS integration, in-memory fallback. Attributes engines provide secret resolution for component configuration.

### D-Bus Locking (`pkg/lock/`)

D-Bus-based locking prevents concurrent Materia runs on the same host. File-based lock fallback available. Prevents conflicts during plan execution and cleanup.

## Key Components

| Package | Role |
|---------|------|
| `internal/materia/` | Main orchestrator — Materia struct, Plan/Clean methods |
| `pkg/components/` | Component model with lifecycle state machine |
| `pkg/planner/` | Action plan generation via component graph comparison |
| `pkg/executor/` | Action plan execution — files, services, volumes, secrets |
| `pkg/hostman/` | Host system management — containers, services, facts |
| `pkg/sourceman/` | Source retrieval — git, OCI, file |
| `pkg/manifests/` | Configuration schema — manifests, components, roles |
| `pkg/lock/` | D-Bus and file-based coordination locking |
| `pkg/actions/` | Typed action definitions for lifecycle operations |

## Related

- [[materia]] — Wiki entry
- [[nanobot]] — Lightweight agent framework
- [[pi]] — TypeScript agent harness
- [[hermes-agent]] — MCP hub agent
- [[podman]] — Container runtime
- [[quadlet]] — systemd-native container management
