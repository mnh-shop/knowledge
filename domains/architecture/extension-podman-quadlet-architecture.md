---
name: extension-podman-quadlet-architecture
tags: [extension-podman-quadlet, architecture, podman, quadlet, podman-desktop, svelte, typescript, plugin, systemd, vscode]
description: "Architecture of the Podman Desktop Quadlet extension — 17-service backend graph, podlet-js builder pipeline, compose detection, systemd daemon-reload lifecycle, and Podman worker abstraction"
source: sources/extension-podman-quadlet/
---

# Extension Podman Quadlet Architecture

**Source:** `sources/extension-podman-quadlet/`
**License:** Apache-2.0
**Repository:** github.com/containers/podman-desktop-extension-podman-quadlet

Extension Podman Quadlet is a [Podman Desktop](https://podman-desktop.io/) extension (Podman 5+, published as `ghcr.io/podman-desktop/pd-extension-quadlet:latest`) that brings Quadlet unit management into the desktop GUI. It is a pnpm monorepo of 4 packages — `backend` (extension host), `frontend` (Svelte 5 UI), `podlet-js` (Quadlet generation library), `shared` (API contracts) — requiring Node >= 24. The frontend uses Svelte 5.56.8, Tailwind CSS ^4.3.3, and Vite ^8.1.5; tests use Vitest and Playwright.

## Architecture Overview

```
Podman Desktop extension host
  ├── extension.ts ── activate()/deactivate() → MainService
  ├── MainService (service orchestrator)
  ├── 16 domain services (Quadlet, Systemd, Container, Pod, Volume,
  │      Network, Image, PodletJs, Command, Configuration, Dialog,
  │      Routing, Webview, Logger, Provider, Specifier)
  ├── PodmanService + helpers (engine-helper, podman-helper, quadlet-helper, systemd-helper)
  ├── 12 API impls (quadlet, podlet, container, pod, volume, network,
  │      image, configuration, dialog, logger, provider, routing)
  ├── Worker abstraction (podman-native-worker | podman-ssh-worker | podman-worker)
  └── Podlet-JS generation library (container-generator + 11 builders, compose)
```

## 1. Service Graph

The backend (`packages/backend/src/services/`) is orchestrated by `MainService`, which wires the full Podman Desktop extension API into 17 concrete services:

| Service | Responsibility |
|---|---|
| `MainService` | Lifecycle orchestration, service composition, activate/deactivate |
| `QuadletService` | Quadlet CRUD: `collectPodmanQuadlet()` (:171), `refreshQuadletsStatuses()` (:245), `writeIntoMachine()` (:288), `read()` (:460), `remove()` (:369) |
| `SystemdService` | `getActiveStatus()` (:33), `daemonReload()` (:76), `start()` (:99), `stop()` (:138), `restart()` (:176) |
| `ContainerService` | Container inspect for container→Quadlet generation |
| `PodService` | Pod-level inspect and status |
| `VolumeService` | Volume inspect for `.volume` generation |
| `NetworkService` | Network inspect for `.network` generation |
| `ImageService` | Image inspect for `.image` generation |
| `PodletJsService` | Bridges podlet-js generation (`compose()` at :197) into the backend |
| `CommandService` | Command execution/parsing for podman CLI operations |
| `ConfigurationService` | Extension configuration management |
| `DialogService` | Native dialog interactions |
| `RoutingService` | Navigation/route management within Podman Desktop |
| `WebviewService` | Webview-based UI rendering |
| `LoggerService` | Structured logging + journal log streaming |
| `ProviderService` | Podman provider/connection registry |
| `SpecifierService` | Quadlet file specifier parsing and formatting |

Alongside these, `PodmanService` resolves connections to `PodmanWorker` instances, and four stateless helpers (`engine-helper`, `podman-helper`, `quadlet-helper`, `systemd-helper`) centralize CLI/engine wiring. The frontend-facing surface is provided by 12 API implementation classes in `packages/backend/src/apis/` (`quadlet-api-impl`, `podlet-api-impl`, `container-api-impl`, `pod-api-impl`, `volume-api-impl`, `network-api-impl`, `image-api-impl`, `configuration-api-impl`, `dialog-api-impl`, `logger-api-impl`, `provider-api-impl`, `routing-api-impl`).

**Operations surface (what is actually implemented):** list (`all`), refresh, generate (via podlet-js), edit/save (`writeIntoMachine`/`readIntoMachine`), delete (`remove`), start, stop, restart, status (`getActiveStatus`), and journal log streaming. **Enable/disable is NOT implemented** — the only occurrence is the error string `"quadlet with id ${quadlet.id} is a template that cannot be enabled."` thrown in `quadlet-api-impl.ts:47` when lifecycle actions are attempted on template Quadlets.

## 2. Podlet-JS Builder Pipeline

`packages/podlet-js/src/containers/container-generator.ts` converts a running container into a Quadlet `.container` file:

- `generate(options)` at **line 45** instantiates **11 builder classes** and folds them over the inspect info via `reduce`, then serializes the resulting INI with `js-ini`'s `stringify`.
- The 11 builders (`packages/podlet-js/src/containers/builders/`):

| Builder | File | Extracts |
|---|---|---|
| `AddHost` | `add-host.ts` | `--add-host` entries |
| `Annotation` | `annotation.ts` | container annotations |
| `Entrypoint` | `entrypoint.ts` | entrypoint override |
| `Environment` | `environment.ts` | env vars |
| `Exec` | `exec.ts` | exec command |
| `Image` | `image.ts` | image reference |
| `Mount` | `mount.ts` | volume/bind mounts |
| `Name` | `name.ts` | container name |
| `PublishPort` | `publish-port.ts` | port mappings |
| `ReadOnly` | `read-only.ts` | read-only rootfs |
| `Restart` | `restart.ts` | restart policy |

Each builder implements the `ContainerQuadletBuilder` interface, extracting one property from `ContainerInspectInfo`. Analogous generators exist for pods (`PodGenerator`), volumes (`VolumeGenerator`), networks (`NetworkGenerator`), and images (`ImageGenerator`). All 6 generators (including `Compose`) are exported from `packages/podlet-js/src/index.ts`.

## 3. Compose Detection Flow

Compose-to-Quadlet conversion (`packages/podlet-js/src/compose/compose.ts` — `Compose` class, `getServices()` at :41, `toKubePlay()` at :99):

1. **Detection** — The backend identifies compose projects by the container label `com.docker.compose.project.config_files` (constant `COMPOSE_LABEL_CONFIG_FILES` at `packages/backend/src/utils/constants.ts:13`).
2. **Conversion** — `PodletJsService.compose()` (podlet-js-service.ts:197) hands the parsed compose spec to podlet-js, which produces either a **Container**, **Kube**, or **Pod** type Quadlet (`toKubePlay()` emits a Pod manifest; pod/container modes emit Quadlet units).
3. **Output** — Generated content is returned for preview/editing in the UI before `writeIntoMachine()` persists it.

## 4. Systemctl Daemon-Reload Lifecycle

All Quadlet file mutations flow through `QuadletService` and converge on systemd user services:

1. **Discovery** — `collectPodmanQuadlet()` (:171) shells out to `podman quadlet -dryrun` (with `-user` for rootless) and parses the JSON output (`QuadletDryRunParser`).
2. **Write** — `writeIntoMachine()` (:288) writes each file to the per-mode destination (rootful: `/etc/containers/systemd`, rootless: `~/.config/containers/systemd` — :326-328), then — unless `skipSystemdDaemonReload` — calls `SystemdService.daemonReload()` (:350) and re-collects Quadlets.
3. **Delete** — `remove()` (:369) deletes files and triggers the same daemon-reload (:437).
4. **Status** — `refreshQuadletsStatuses()` (:245) maps each Quadlet to its systemd service name and calls `systemd.getActiveStatus()` (`systemctl --user is-active --output=json`, systemd-service.ts:33), setting `quadlet.state` to `active`/`inactive` for the UI.
5. **Lifecycle actions** — start/stop/restart (`systemd-service.ts:99/:138/:176`) run `systemctl --user start|stop|restart` and refresh statuses afterward.

## 5. Worker Abstraction

All podman/systemd CLI execution is funneled through a worker abstraction in `packages/backend/src/utils/worker/`:

- **`podman-worker.ts`** — Abstract `PodmanWorker` base class defining the exec/execWithOutput/journalctlExec contract (abstract `exec()` entry point).
- **`podman-native-worker.ts`** — `PodmanNativeWorker` (line 30) executes commands **locally** via `processApi.exec()` (:59) — used when Podman runs natively on the host.
- **`podman-ssh-worker.ts`** — `PodmanSSHWorker` (line 25) tunnels commands over SSH to a remote Podman Machine using `ssh2` (`ConnectConfig`), with `PodmanSSH`/`PodmanSFTP` helpers (`utils/remote/`) for remote exec and file transfer — used when the engine lives inside a Podman Machine VM.

`PodmanService.getWorker(connection)` selects the appropriate worker per provider connection, so the same QuadletService/SystemdService code paths work against both local and SSH-managed engines (including `journalctlExec` log streaming used by `QuadletApiImpl.createQuadletLogger()`).

## Key Files

| File | Role |
|---|---|
| `packages/backend/src/extension.ts` | Activation lifecycle; instantiates `MainService` |
| `packages/backend/src/services/main-service.ts` | Service composition graph |
| `packages/backend/src/services/quadlet-service.ts` | Quadlet CRUD + daemon-reload lifecycle |
| `packages/backend/src/services/systemd-service.ts` | systemctl user-service operations |
| `packages/backend/src/apis/quadlet-api-impl.ts` | Frontend API surface (no enable/disable) |
| `packages/backend/src/utils/worker/podman-worker.ts` | Worker abstraction (native/SSH) |
| `packages/backend/src/assets/templates.json` | Template Quadlet definitions |
| `packages/podlet-js/src/containers/container-generator.ts` | Container→Quadlet pipeline (:45) |
| `packages/podlet-js/src/compose/compose.ts` | Compose→Quadlet conversion |
| `packages/frontend/src/pages/QuadletsList.svelte` | Quadlet list UI |

## Related

- [[extension-podman-quadlet]] — Wiki overview
- [[podman]] — Container engine
- [[podman-quadlet]] — Quadlet unit reference
- [[podlet-js]] — Generation library used by the extension
- [[podlet]] — Standalone Quadlet generator CLI
