---
name: cockpit-podman
description: "Cockpit web UI module for managing Podman containers, images, pods, and quadlets"
source: sources/cockpit-podman/
tags: [cli, container, docker, git, monitoring, plugin-sdk, podman, quadlet, react, systemd, ui, virtualization, deployment, typescript]
---

# cockpit-podman
**License**: LGPL-2.1-or-later (c) 2017 Red Hat, Inc.

## Overview

cockpit-podman is a [Cockpit](https://cockpit-project.org/) web UI module for managing [Podman](https://podman.io/) containers. It provides a feature-rich graphical interface for containers, images, pods, and systemd-managed quadlets, all accessible from the Cockpit web console.

Built on the [Cockpit Starter Kit](https://github.com/cockpit-project/starter-kit), it communicates with Podman through its [REST API](https://docs.podman.io/en/latest/_static/api.html) over Unix sockets.

## Architecture

```
src/
  index.js           -- Bootstrap entry point; mounts React Application into DOM
  app.jsx            -- Root Application component; global state, event streaming, multi-user orchestration
  client.ts          -- Typed API client wrapping Podman REST API (v3.4.0)
  rest.ts            -- Low-level HTTP/Unix socket connection management
  util.tsx           -- Shared utilities: context, validation, shell quoting, state maps
  manifest.json      -- Cockpit plugin manifest (conditions, menu, capabilities)
  detect-quadlets.py -- Python scanner for systemd quadlet .container/.pod unit files
  podman.scss        -- Global styles for the podman UI

  Containers.jsx           -- Container list with pod grouping, filtering, actions
  ContainerDetails.jsx     -- Container detail panel (ID, image, networking, state)
  ContainerIntegration.jsx -- Ports, volumes, environment variables displays
  ContainerLogs.jsx        -- Log viewer using xterm.js
  ContainerTerminal.jsx    -- Interactive console via xterm.js + WebGL
  ContainerHealthLogs.jsx  -- Health check result log viewer
  ContainerHeader.tsx      -- Filter/search toolbar (owner, text filter)

  ContainerCheckpointModal.jsx  -- CRIU checkpoint modal
  ContainerCommitModal.jsx      -- Commit container to image modal
  ContainerDeleteModal.jsx      -- Container deletion confirmation
  ContainerRenameModal.jsx      -- Container rename dialog
  ContainerRestoreModal.jsx     -- CRIU restore modal
  ForceRemoveModal.jsx          -- Force-remove confirmation for running containers

  Images.jsx           -- Image list with pull/delete/prune/search actions
  ImageDetails.jsx     -- Image detail panel (config, author, ports)
  ImageHistory.jsx     -- Image layer history view
  ImageDeleteModal.jsx -- Image deletion modal
  ImageRunModal.jsx    -- Full create-container dialog (image selection, resources, health check)
  ImageSearchModal.jsx -- Search/download images from registries
  ImageUsedBy.jsx      -- Shows containers using an image
  PruneUnusedImagesModal.jsx    -- Prune unused images dialog

  PodActions.jsx       -- Pod lifecycle actions (start/stop/restart/pause/delete)
  PodCreateModal.jsx   -- Create pod with port mapping and volumes
  PruneUnusedContainersModal.jsx -- Prune unused containers dialog

  Env.jsx              -- Environment variable editor component
  PublishPort.jsx      -- Port mapping editor component
  Volume.jsx           -- Volume binding editor component
  Notification.tsx     -- Error notification component
```

## Key Data Flow

### Application Initialization (app.jsx)

1. On mount, `Application.componentDidMount()` runs:
   - Checks `XDG_RUNTIME_DIR` to initialize the user's podman connection
   - Detects SELinux availability via `selinuxenabled`
   - Scans `/sys/fs/cgroup` for scope files (`libpod.*scope`, `podman-*.scope`) to discover other users running containers
   - Sets up location change listener for URL navigation
2. `Application.init(uid, username)` connects to a podman instance via `rest.connect(uid)`:
   - Ensures `podman.socket` is started via `systemctl`
   - Fetches `GET /libpod/info` to get version, registries, cgroup version
   - Initializes images, containers, pods, and quadlets
   - Subscribes to systemd daemon-reload events (for quadlet re-detection)
   - Begins streaming container events via `GET /libpod/events`
   - Starts container stats streaming

### REST Connection Layer (rest.ts)

The `connect()` factory creates a `Connection` object wrapping a Cockpit HTTP channel to a Podman Unix socket:

| Connection Type | Socket Path | Superuser |
|-----------------|-------------|-----------|
| System (uid=0) | `/run/podman/podman.sock` | `require` |
| Session user (uid=null) | `$XDG_RUNTIME_DIR/podman/podman.sock` | none |
| Other user (uid=N) | `/run/user/N/podman/podman.sock` | `require` |

Each connection provides:
- `call()` -- HTTP request/response via Cockpit channel
- `monitor()` -- HTTP streaming (events, stats) with line-based JSON parsing
- `close()` -- tear down HTTP channel and any raw stream channels

### Event-Driven State (app.jsx)

The Application uses Podman's event stream to reactively update state:

```
handleImageEvent  → push/save/tag/pull/untag/remove/prune/build
handleContainerEvent → start/checkpoint/create/died/pause/remove/stop/commit, etc.
handlePodEvent    → create/kill/pause/start/stop/unpause/remove
```

Containers state updates are serialized per-container via `pendingUpdateContainer` promises to avoid race conditions from out-of-order event delivery.

## Client API (client.ts)

Versioned at **Podman REST API v3.4.0** (`/v3.4.0/`). Key endpoints:

| Function | API Path | Description |
|----------|----------|-------------|
| `getInfo()` | `libpod/info` | Podman version, registries, cgroup version (10s timeout) |
| `getContainers()` | `libpod/containers/json` | List all containers `?all=true` |
| `inspectContainer()` | `libpod/containers/{id}/json` | Full container details |
| `createContainer()` | `libpod/containers/create` | Create container (POST with JSON body) |
| `postContainer()` | `libpod/containers/{id}/{action}` | start/stop/restart/pause/unpause |
| `delContainer()` | `libpod/containers/{id}` | DELETE container (optional force) |
| `renameContainer()` | `libpod/containers/{id}/rename` | POST rename |
| `execContainer()` | `libpod/containers/{id}/exec` | Create exec session for console |
| `commitContainer()` | `libpod/commit` | Commit container to image |
| `getImages()` | `libpod/images/json` | List images (fetches extended info per-image) |
| `getPods()` | `libpod/pods/json` | List pods |
| `createPod()` | `libpod/pods/create` | Create pod |
| `postPod()` | `libpod/pods/{id}/{action}` | start/stop/restart/pause/unpause |
| `delPod()` | `libpod/pods/{id}` | DELETE pod |
| `pullImage()` | `libpod/images/pull` | Pull image (POST with reference) |
| `delImage()` | `libpod/images/{id}` | DELETE image |
| `untagImage()` | `libpod/images/{id}/untag` | Remove tag |
| `imageHistory()` | `libpod/images/{id}/history` | Layer history |
| `imageExists()` | `libpod/images/{id}/exists` | Check image existence |
| `containerExists()` | `libpod/containers/{id}/exists` | Check container existence |
| `pruneUnusedImages()` | `libpod/images/prune` | Prune unused (POST `?all=true`) |
| `runHealthcheck()` | `libpod/containers/{id}/healthcheck` | Run health check |
| `resizeContainersTTY()` | `libpod/containers/{id}/resize` or `libpod/exec/{id}/resize` | Resize terminal |
| `streamEvents()` | `libpod/events` | Monitor stream for all events |
| `streamContainerStats()` | `libpod/containers/stats` | Monitor stream for container CPU/memory stats |

## Multi-User Support

cockpit-podman displays containers, images, and pods across multiple users:

- **System (uid=0)** -- podman running as root
- **Current session user (uid=null)** -- user's rootless podman
- **Other users** -- auto-detected by scanning `/sys/fs/cgroup` for libpod/podman scope files

State is partitioned per-user. Event updates only touch the relevant user's data. A user filter (`ownerFilter`) can scope the view to a single user, and the owner column shows which user owns each resource.

## Quadlet Integration

Quadlets are systemd-native container/pod management units (`.container`/`.pod` files in `/run/systemd/generator`). cockpit-podman:

1. Runs `detect-quadlets.py` at startup to scan the generator directory
2. Mocks inactive quadlet containers/pods as stopped entities so users can see and manage them even when not running
3. Subscribes to systemd `Reloading` D-Bus signals (`org.freedesktop.systemd1.Manager`) to re-detect when quadlets change
4. Shows a "service" badge on quadlet-managed containers
5. Quadlet lifecycle actions go through `systemctl start/stop/restart` rather than the Podman API

The Python scanner parses each `.service` file for `SourcePath`, `ContainerName`/`PodName`, `Image`, `Exec`, and `Pod` keys to reconstruct the container/pod topology.

## Container States

From `src/util.tsx`, mapped from [Podman container state definitions](https://github.com/containers/podman/blob/main/libpod/define/containerstate.go):

- Exited, Paused, Stopped, Removing, Configured, Created, Restart, Running

Pod states from [Podman pod state definitions](https://github.com/containers/podman/blob/main/libpod/define/podstate.go):

- Created, Running, Stopped, Paused, Exited, Error

## UI Component Architecture

- **PatternFly v6** (React): Cards, modals, forms, tables, alerts, toolbar
- **xterm.js** with WebGL addon: Terminal emulator for container console and logs
- **Cockpit shared libraries**: `ListingTable`, `Dialogs`, `cockpit-components-dropdown`, `cockpit-components-dynamic-list`
- **Responsive design**: Mobile-aware layout with collapsible image section and adaptive terminal sizing

### Modal Dialogs

Modal dialogs use the Cockpit `Dialogs` API (`Dialogs.show(<Component />)`) rather than inline conditional rendering, with one exception: `PruneUnusedImagesModal` stays in the DOM to keep its unused-image list in sync with reality.

## Validation

Debounced validation (500ms) is used extensively in create/edit dialogs:

- `validationDebounce` wraps validation handlers
- `validationClear` removes individual field errors
- Container names validated against `/^[a-zA-Z0-9][a-zA-Z0-9_\\.-]*$/`
- Port mappings validated per-field (IP, hostPort, containerPort)
- Dynamic list forms each manage their own validation state

## Build System

- **esbuild** (with esbuild-wasm fallback for non-x64 architectures): Bundles JSX/TS/SCSS into `dist/`
- **esbuild plugins**: Sass compilation, Cockpit PO translation integration, rsync deployment, compression, cleanup
- **Makefile**: Full build/install/test lifecycle with Fedora/Debian/Arch packaging
- **Source maps**: Linked in development mode
- **Minification & compression**: Production only
- **Dependency tracking**: Runtime NPM module versions written to `runtime-npm-modules.txt`

## Internationalization

- `cockpit.gettext` for all user-visible strings
- PO templates generated from JS/HTML sources with `xgettext`
- Continuous translation via Weblate (PO template uploaded daily, synced weekly)
- Metainfo and manifest translations included

## Testing

- **Browser integration tests**: Python-based test runner (`test/check-application`) with Cockpit test infrastructure
- **Test VMs**: Automated VM image building with Fedora/Debian/Arch
- **Code quality checks** (`pyproject.toml`):
  - `ruff` -- comprehensive lint rules (flake8, pylint, isort, etc.)
  - `mypy` -- strict type checking
  - `pyright` -- strict type checking
  - `vulture` -- dead code detection (min confidence 80)
  - `codespell` -- spelling check

## Packaging

- **RPM**: Generated from `packaging/cockpit-podman.spec.in` with bundled NPM dependency tracking
- **DEB**: Maintained via `packaging/debian/` with generated changelog and copyright
- **Arch Linux**: PKGBUILD generated from template
- **Flatpak/cockpit**: No flatpak packaging; designed for system-level Cockpit plugin installation

## Dependencies

Key runtime dependencies from `package.json`:

- **React 18.3** + **React DOM 18.3**: UI framework
- **@patternfly/patternfly 6.5**: Design system and components
- **@xterm/xterm 6.0** + **@xterm/addon-webgl**: Terminal emulator
- **docker-names**: Random container name generation (e.g., "happy_curie")
- **esbuild**: Bundler
- **cockpit**: Cockpit bridge integration (runtime, not NPM)

## Related

- [[cockpit]] -- The Cockpit project this module extends
- [[podman]] -- The container engine managed by this UI
- [[quadlet]] -- The systemd-native container management integration
