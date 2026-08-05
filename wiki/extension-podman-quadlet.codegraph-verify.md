---
name: extension-podman-quadlet-codegraph-verify
tags: [extension-podman-quadlet, codegraph-verify, podman, quadlet, vscode, extension, typescript]
description: "Codegraph Verification: extension-podman-quadlet — validating wiki claims against indexed source code"
source: sources/extension-podman-quadlet/
---

# Codegraph Verification: extension-podman-quadlet

**Date:** 2026-07-12

## Claim 1: Podman Desktop extension for listing, generating, editing, saving, deleting, and managing Quadlet files

- **Wiki says:** The extension lets users list, generate, edit, save, and delete Podman Quadlet files within a given Podman Machine — managing Quadlet units as systemd services from inside Podman Desktop's GUI. It does **not** implement `enable`/`disable` — the only occurrence is the error message "quadlet with id ... is a template that cannot be enabled" thrown when lifecycle actions are attempted on template Quadlets.

- **Source evidence:**
  - `packages/backend/src/extension.ts` activates the extension: `activate(extensionContext)` instantiates `MainService` with full Podman Desktop API access (lines 21-34)
  - `packages/backend/src/apis/quadlet-api-impl.ts` — API bridge exposing quadlet operations to the frontend. Full method surface (no enable/disable):
    - `all()` (line 33), `refresh()` (line 37)
    - `start()` (line 51), `stop()` (line 78), `restart()` (line 105)
    - `remove()` (line 132), `read()` (line 146), `writeIntoMachine()` (line 205), `readIntoMachine()` (line 218)
    - `createQuadletLogger()` (line 156), `disposeLogger()` (line 197), `getSynchronisationInfo()` (line 201), `templates()` (line 229)
    - Line 47: the only `enable` reference — `throw new Error(\`quadlet with id ${quadlet.id} is a template that cannot be enabled.\`)`
  - `packages/backend/src/services/quadlet-service.ts` — Core `QuadletService` (496 lines) implements the lifecycle:
    - `collectPodmanQuadlet()` (lines 171-230): Discovers all Quadlets from active Podman connections using `podman quadlet -dryrun`
    - `read()` (lines 460-477): Reads a Quadlet file's source content from the machine
    - `writeIntoMachine()` (lines 288-367): Writes Quadlet files to `~/.config/containers/systemd/` (rootless) or `/etc/containers/systemd/` (rootful), then calls `systemd daemon-reload` and re-collects
    - `remove()` (lines 369-454): Deletes Quadlet files from the machine and triggers daemon-reload
  - `packages/backend/src/services/systemd-service.ts` — Manages systemd operations: `daemonReload()` (line 76), `getActiveStatus()` (line 33), `start()` (line 99), `stop()` (line 138), `restart()` (line 176) — no `enable()`/`disable()` methods exist
  - The frontend (`packages/frontend/src/pages/`) provides the Svelte UI for quadlet management: `QuadletsList.svelte`, `QuadletDetails.svelte`, `QuadletGenerate.svelte`, `QuadletCompose.svelte`
  - `package.json` line 6: `"description": "Manage, generate Podman Quadlet"`

- **Verdict:** ✅ CORRECT (with correction applied: enable/disable is NOT implemented — removed from wiki)
- **Fix needed:** Applied — removed "enable"/"disable" from wiki table and key features; corrected frontend page names to `QuadletsList`/`QuadletDetails`/`QuadletGenerate`/`QuadletCompose`

## Claim 2: Generation from running containers (using podlet-js library)

- **Wiki says:** Quadlet files can be generated from existing running containers in Podman Desktop. The extension reads container inspect info and converts it to a Quadlet `.container` file, with editable output before loading into the machine.

- **Source evidence:**
  - `packages/podlet-js/src/containers/container-generator.ts` — `ContainerGenerator` class (82 lines) transforms `ContainerInspectInfo` + `ImageInspectInfo` into Quadlet INI:
    - Uses **11 builder classes** in a pipeline: `AddHost`, `Annotation`, `PublishPort`, `Image`, `Name`, `Entrypoint`, `Exec`, `Environment`, `ReadOnly`, `Mount`, `Restart`
    - `generate(options)` method (line 45) iterates builders, applies options (`startOnBoot`), and serializes to INI via `stringify` from `js-ini`
  - Builder implementations in `packages/podlet-js/src/containers/builders/`:
    - `add-host.ts`, `annotation.ts`, `entrypoint.ts`, `environment.ts`, `exec.ts`, `image.ts`, `mount.ts`, `name.ts`, `publish-port.ts`, `read-only.ts`, `restart.ts` — each implements the `ContainerQuadletBuilder` interface, extracting one property from `ContainerInspectInfo`
  - `packages/backend/src/apis/podlet-api-impl.ts` — API exposing podlet-js generation to the backend
  - `packages/backend/src/services/container-service.ts` — Retrieves container inspect info from the Podman API
  - `README.md` includes screenshots showing the "Generate Quadlet" button on the containers page and the editable output dialog
  - `packages/podlet-js/src/index.ts` exports 6 generators: `ContainerGenerator`, `PodGenerator`, `VolumeGenerator`, `NetworkGenerator`, `ImageGenerator`, `Compose`

- **Verdict:** ✅ CORRECT (builder count corrected from 10 to 11)
- **Fix needed:** Applied — builder count was 10 in the wiki, corrected to 11 (matches the 11 files in `builders/`)

## Claim 3: Compose specification to Quadlet conversion (Container, Kube, Pod modes)

- **Wiki says:** The extension provides support for generating Quadlets from an existing Docker Compose specification. It reads the compose spec from a container's `com.docker.compose.project.config_files` label and generates Quadlet files in Container, Kube, or Pod mode.

- **Source evidence:**
  - `packages/podlet-js/src/compose/compose.ts` — `Compose` class that converts compose specs to Quadlet files (`toKubePlay()` at line 99, `getServices()` at line 41)
  - `packages/podlet-js/src/compose/models/` — Compose spec type models
  - `packages/backend/src/utils/constants.ts` line 13 — `export const COMPOSE_LABEL_CONFIG_FILES = 'com.docker.compose.project.config_files';`
  - `packages/backend/src/apis/podlet-api-impl.ts` — Exposes compose → quadlet generation to the API layer
  - `packages/backend/src/services/podlet-js-service.ts` — `compose()` method (line 197) delegates compose conversion
  - `README.md` lines 34-46 describes compose support:
    - "Podman Desktop group containers in the same compose project"
    - "determine which spec has been used by looking at the `com.docker.compose.project.config_files` containers label"
    - "Two type of Quadlet can be generated from a compose specification, `Container`, `Kube` or `Pod`"
  - `README.md` screenshots show the generate-from-compose flow with the three output mode options
  - `packages/podlet-js/src/compose/compose.spec.ts` — Unit tests for compose conversion

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Multi-package architecture with 4 internal packages (backend, frontend, podlet-js, shared) and 17 backend services

- **Wiki says:** The extension is built as a monorepo with 4 packages: `backend` (Node.js extension host), `frontend` (Svelte UI), `podlet-js` (Quadlet generation library), and `shared` (TypeScript type definitions and API contracts). The backend orchestrates 17 services plus PodmanService and helpers.

- **Source evidence:**
  - `package.json` line 77: `"workspaces": { "packages": ["packages/*", "tests/*"] }` — pnpm workspace monorepo
  - 4 packages in `packages/`:
    - **`packages/backend/`** (Node.js extension host): `extension.ts`, 17 service files (`main-service`, `quadlet-service`, `systemd-service`, `container-service`, `pod-service`, `volume-service`, `network-service`, `image-service`, `podlet-js-service`, `command-service`, `configuration-service`, `dialog-service`, `routing-service`, `webview-service`, `logger-service`, `provider-service`, `specifier-service`) plus `podman-service` and 4 helpers (`engine-helper`, `podman-helper`, `quadlet-helper`, `systemd-helper`), 12 API impl files (`quadlet-api-impl`, `podlet-api-impl`, `container-api-impl`, `pod-api-impl`, `volume-api-impl`, `network-api-impl`, `image-api-impl`, `configuration-api-impl`, `dialog-api-impl`, `logger-api-impl`, `provider-api-impl`, `routing-api-impl`), utils, models, integrations, assets (templates), workers (`podman-native-worker`, `podman-ssh-worker`, `podman-worker`)
    - **`packages/frontend/`** (Svelte 5 UI): `App.svelte`, pages (`QuadletsList`, `QuadletDetails`, `QuadletGenerate`, `QuadletCompose`), stores, API client, lib components, Tailwind CSS
    - **`packages/podlet-js/`** (Quadlet generation library): Container/Pod/Volume/Network/Image generators, Compose converter, builder pattern for INI properties
    - **`packages/shared/`** (API contracts): Core types like `Quadlet`, `QuadletInfo`, `ServiceQuadlet`, `Template`, `SynchronisationInfo`
  - `package.json` scripts confirm build order: `build:podlet-js` → `build:backend`, `build:shared`, `build:frontend`
  - Test scripts target each package independently: `test:podlet-js`, `test:backend`, `test:frontend`, `test:shared`

- **Verdict:** ✅ CORRECT (service count clarified to 17 + PodmanService/helpers, API impl count to 12)
- **Fix needed:** None

## Claim 5: Systemd service management (start, stop, restart, status)

- **Wiki says:** The extension manages Quadlet units as systemd services, providing start/stop/restart actions and active/inactive status display through the Podman Desktop interface. Enable/disable is **not** offered.

- **Source evidence:**
  - `packages/backend/src/services/systemd-service.ts` — Systemd management service:
    - `getActiveStatus()` (line 33): Queries `systemctl --user is-active --output=json` for each quadlet service
    - `daemonReload()` (line 76): Runs `systemctl --user daemon-reload` (or system-level)
    - `start()` (line 99), `stop()` (line 138), `restart()` (line 176)
    - No `enable()` or `disable()` methods — verified by full method listing of the class
  - `packages/backend/src/services/quadlet-service.ts`:
    - `refreshQuadletsStatuses()` (lines 245-275): Iterates known Quadlets, resolves service names, calls `systemd.getActiveStatus()`, and updates `quadlet.state` to `'active'` or `'inactive'`
    - `collectPodmanQuadlet()` uses `quadlet -dryrun` with `-user` flag for rootless or without for rootful
  - `packages/backend/src/utils/worker/podman-worker.ts` — Communication layer that runs podman machine commands
  - `packages/backend/src/services/podman-service.ts` — Podman connection management
  - Status display is returned as `QuadletInfo[]` via `all()` method (lines 54-69) and exposed to the frontend for rendering

- **Verdict:** ✅ CORRECT (enable/disable removed from claims — not implemented in source)
- **Fix needed:** Applied — wiki previously claimed enable/disable; corrected to start/stop/restart/status only

## Claim 6: Container generation from existing Podman objects (not just compose/containers)

- **Wiki says:** The extension can generate Quadlets from multiple existing Podman object types: containers, pods, volumes, networks, and images — each producing the corresponding `.container`, `.pod`, `.volume`, `.network`, or `.image` Quadlet file.

- **Source evidence:**
  - `packages/podlet-js/src/index.ts` exports 6 generators:
    - `ContainerGenerator` — `.container` files from running containers
    - `PodGenerator` — `.pod` files from running pods
    - `VolumeGenerator` — `.volume` files from existing volumes
    - `NetworkGenerator` — `.network` files from existing networks
    - `ImageGenerator` — `.image` files from images
    - `Compose` — compose-to-quadlet conversion
  - Each generator has dedicated source files:
    - `packages/podlet-js/src/pods/pod-generator.ts`
    - `packages/podlet-js/src/volumes/volume-generator.ts`
    - `packages/podlet-js/src/networks/network-generator.ts`
    - `packages/podlet-js/src/images/image-generator.ts`
    - `packages/podlet-js/src/containers/container-generator.ts`
  - Backend API implementations provide the data sources:
    - `packages/backend/src/apis/pod-api-impl.ts` — Pod inspect data
    - `packages/backend/src/apis/volume-api-impl.ts` — Volume inspect data
    - `packages/backend/src/apis/network-api-impl.ts` — Network inspect data
    - `packages/backend/src/apis/image-api-impl.ts` — Image inspect data
  - `packages/backend/src/services/` has corresponding service classes: `pod-service.ts`, `volume-service.ts`, `network-service.ts`, `image-service.ts`
  - `packages/podlet-js/src/pods/pod-generator.spec.ts`, and similar test files confirm each generator works

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 6 key claims from the extension-podman-quadlet wiki have been verified against the source code:

- ✅ **Quadlet lifecycle:** List, generate, edit, save, delete, start, stop, restart, status — confirmed via `QuadletService` and `SystemdService`; **enable/disable is NOT implemented** (only an error string in `quadlet-api-impl.ts:47`)
- ✅ **Container → Quadlet generation:** `ContainerGenerator` with 11 builder classes confirmed
- ✅ **Compose conversion:** `Compose` class with Container/Kube/Pod output modes confirmed; label constant at `utils/constants.ts:13`
- ✅ **Monorepo architecture:** 4 packages (backend, frontend, podlet-js, shared) with pnpm workspaces, 17 services + PodmanService/helpers, 12 API impls confirmed
- ✅ **Systemd service management:** start/stop/restart, active status, daemon-reload confirmed — no enable/disable
- ✅ **Multi-object generation:** Generators for containers, pods, volumes, networks, and images confirmed

The extension is a well-structured Podman Desktop extension that brings Quadlet management into the GUI — using a dedicated `podlet-js` library for Quadlet generation with clean separation of concerns across its backend/frontend/shared packages.

## Related

- [[extension-podman-quadlet]] -- Main wiki entry
- [[podman]] -- Podman container engine
- [[podman-quadlet]] -- Quadlet template collection
- [[podlet]] -- Standalone Quadlet generator CLI

## Cross-project

- [[podman.codegraph-verify]] -- Podman runtime verification
- [[podman-quadlet.codegraph-verify]] -- Quadlet template patterns
- [[podlet.codegraph-verify]] -- CLI Quadlet generator comparison
