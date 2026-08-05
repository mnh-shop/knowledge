---
name: extension-podman-quadlet
tags: [extension-podman-quadlet, podman, quadlet, plugin, desktop, container]
description: "Podman Desktop extension for Quadlet container management"
source: sources/extension-podman-quadlet/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Extension Podman Quadlet

| Field | Value |
|---|---|
| **Origin** | [containers/podman-desktop-extension-podman-quadlet](https://github.com/containers/podman-desktop-extension-podman-quadlet) |
| **License** | Apache 2.0 (inferred) |
| **Stack** | TypeScript, Svelte 5, Podman Desktop API, podlet-js |
| **Source** | `sources/extension-podman-quadlet/` |
| **Repomix** | `raw/extension-podman-quadlet/extension-podman-quadlet.xml` |
| **Codegraph** | `graphs/extension-podman-quadlet/` |

## Overview

Extension Podman Quadlet is a [Podman Desktop](https://podman-desktop.io/) extension that provides a graphical interface for managing Quadlet container units. It bridges the gap between Podman Desktop's GUI and Quadlet's systemd-integrated container definitions, allowing users to create, edit, start, stop, and monitor Quadlet units without leaving the desktop environment.

The extension supports Podman version 5 and above. It is published as `ghcr.io/podman-desktop/pd-extension-quadlet:latest` and installable from the Podman Desktop Extensions page.

### Architecture

The extension is structured as a monorepo with four packages under `packages/`:

- **`backend/`** — Extension backend that registers with Podman Desktop's extension API. Written in TypeScript, it imports Podman Desktop APIs (`@podman-desktop/api`) for container engine access, provider management, process execution, CLI integration, window management, and extension context. The entry point `extension.ts` initializes a `MainService` which orchestrates all backend services.
- **`frontend/`** — Svelte 5-based UI rendered inside Podman Desktop as custom pages and views. Provides the visual dashboard, form-based editors, and status displays for Quadlet units.
- **`podlet-js/`** — A JavaScript/TypeScript library for generating Quadlet file content programmatically. Handles `.container`, `.volume`, `.network`, `.kube`, and `.pod` file generation with proper directive formatting.
- **`shared/`** — Shared types and API contracts between backend and frontend packages, ensuring type safety across the extension boundary.

### Backend Services

The backend (`packages/backend/src/services/`) provides a comprehensive set of services:

| Service | Responsibility |
|---|---|
| `MainService` | Orchestrates all services, manages extension lifecycle (activate/deactivate) |
| `QuadletService` | CRUD operations for Quadlet `.container`, `.volume`, `.network`, and `.pod` files |
| `SystemdService` | Start/stop/restart Quadlet units via `systemctl --user` |
| `ContainerService` | Container inspection, status checking, integration with Podman containers page |
| `PodService` | Pod-level operations and status |
| `VolumeService` | Volume management for Quadlet volumes |
| `NetworkService` | Network management for Quadlet networks |
| `ImageService` | Container image inspection and management |
| `PodletJsService` | Integration with the podlet-js library for file generation |
| `CommandService` | Command execution and parsing for podman CLI operations |
| `ConfigurationService` | Extension configuration management |
| `DialogService` | Native dialog interactions |
| `RoutingService` | Navigation and route management within Podman Desktop |
| `WebviewService` | Webview-based UI rendering |
| `LoggerService` | Structured logging |
| `ProviderService` | Podman provider registration and management |
| `SpecifierService` | Quadlet file specifier parsing and formatting |

The extension implements the Podman Desktop extension lifecycle through `activate()` and `deactivate()` hooks, connecting to the container engine, provider registry, process API, CLI API, commands API, and configuration API.

## Key Features

- **Quadlet Unit Management** — List, generate, edit, save, and delete Quadlet `.container`, `.volume`, `.network`, and `.pod` files, plus start/stop/restart and status via systemd. Files are stored in the standard Quadlet directories (`~/.config/containers/systemd/` for rootless, `/etc/containers/systemd/` for rootful).
- **Generation from Running Containers** — Convert an existing running container into a Quadlet `.container` file with one click. The generated output can be reviewed and edited before saving, with podlet-js formatting the directives correctly.
- **Compose-to-Quadlet Conversion** — Generate Quadlet files from Docker Compose specifications. The extension detects Compose projects from container labels (`com.docker.compose.project.config_files`) and can produce `Container`, `Kube`, or `Pod` type Quadlets from the compose definition.
- **Visual Editor** — Form-based editing of Quadlet unit directives with validation. Users fill in fields rather than hand-editing INI-style files, reducing syntax errors.
- **Status Dashboard** — Real-time view of Quadlet unit states (active, inactive, failed) with color-coded indicators in the Podman Desktop interface.
- **Journal Integration** — View container logs through the desktop interface via systemd journal integration, avoiding the need to drop to the terminal for `journalctl --user`.
- **Systemd Integration** — Start/stop/restart operations through systemd user services. The extension calls `systemctl --user` commands with proper error handling and output parsing.
- **Template Support** — Pre-configured Quadlet templates for common service patterns, making it easy to bootstrap new services without remembering the full Quadlet syntax.
- **Podlet-JS Library** — The `podlet-js` package provides programmatic Quadlet generation that can be used both by the extension and standalone by developers who want to generate Quadlet files in their own tooling.

### User Interface

The frontend is built with **Svelte 5** and uses **Tailwind CSS** for styling. Key UI components:

- **Quadlets List Page** (`QuadletsList.svelte`) — Shows all discovered Quadlet files with their status (active/inactive/failed), type (container/volume/network/pod), and systemd service state.
- **Quadlet Details Page** (`QuadletDetails.svelte`) — Per-unit detail view with status, logs, and lifecycle actions.
- **Quadlet Generate Page** (`QuadletGenerate.svelte`) — Wizard for generating Quadlets from running containers, with preview-and-edit steps before saving.
- **Quadlet Compose Page** (`QuadletCompose.svelte`) — Wizard for generating Quadlets from Compose files (Container, Kube, or Pod modes), with preview-and-edit steps before saving.
- **Quadlet Editor** — Form-based editor with sections for `[Unit]`, `[Container]`, `[Service]`, and `[Install]` directives, with field-level validation and inline help.
- **Status Dashboard** — Dashboard cards showing aggregate status across all Quadlet units with quick-action buttons.

### Development Stack

- **Language**: TypeScript throughout all packages
- **Frontend**: Svelte 5 with TypeScript, Vite bundler, Tailwind CSS
- **Backend**: Node.js 24+, Podman Desktop extension API
- **Testing**: Vitest for unit tests, Playwright for end-to-end tests
- **Build**: pnpm workspaces, concurrent builds for frontend + backend
- **Code Quality**: ESLint with TypeScript, Prettier for formatting, Svelte check for Svelte-specific validation

## Architecture

```
Podman Desktop
  └── Extension: extension-podman-quadlet
        ├── Backend (packages/backend/)
        │     ├── extension.ts          ← Activation/deactivation lifecycle
        │     ├── MainService           ← Service orchestrator
        │     ├── QuadletService         ← CRUD for Quadlet files
        │     ├── SystemdService         ← systemctl operations
        │     ├── ContainerService       ← Container inspection
        │     ├── PodletJsService        ← Quadlet generation
        │     └── ... (12+ other services)
        ├── Frontend (packages/frontend/)
        │     ├── App.svelte            ← Root Svelte component
        │     ├── pages/                ← QuadletsList, QuadletDetails, QuadletGenerate, QuadletCompose
        │     ├── lib/components/       ← Reusable Svelte components
        │     └── stores/              ← Reactive state management
        ├── Shared (packages/shared/)
        │     └── src/                  ← Shared types and API interfaces
        └── Podlet-JS (packages/podlet-js/)
              └── src/                   ← Quadlet file generation library
```

The extension plugs into Podman Desktop's extension API through the `activate()` hook which receives the `ExtensionContext`. It registers new pages and views within the existing dashboard, interacts with the host system's podman socket and systemd user manager to manage Quadlet units, and reads/writes Quadlet files from standard user quadlet directories.

Communication between the backend and frontend follows Podman Desktop's extension communication pattern: the backend exposes APIs that the frontend consumes via the extension's internal routing layer.

## Installation

```bash
# From Podman Desktop Extensions page, search for "Quadlet"
# Or install directly via CLI:
podman-desktop extension install ghcr.io/podman-desktop/pd-extension-quadlet:latest
```

**Requirements:** Podman version 5.0 or higher.

## Usage

1. **Generate a Quadlet from a running container:**
   - Navigate to the Containers page in Podman Desktop
   - Click the "Generate Quadlet" action on any running container
   - Review and edit the generated `.container` file
   - Save to activate the Quadlet

2. **Generate Quadlets from Docker Compose:**
   - Open the Quadlet extension page
   - Select "Generate from Compose"
   - Choose the Compose project (auto-detected from running containers)
   - Select output type: `Container`, `Kube`, or `Pod`
   - Save to activate

3. **Manage existing Quadlets:**
   - The Quadlet List shows all discovered `.container`, `.volume`, `.network`, and `.pod` files
   - Use the dashboard to start/stop/restart services, view logs, and check status

## Related

- [[podman]] — Container engine that executes Quadlet-managed container units. The extension interacts with Podman's container engine API and systemd integration.
- [[podlet]] — CLI tool for generating Quadlet files from container run commands. The extension's `podlet-js` package is a JavaScript port of this functionality.
- [[podman-quadlet]] — Getting-started guide and reference for running Podman containers with Quadlet. Provides the foundational documentation this extension builds upon.
- [[quadlet]] — Base wiki on the Quadlet unit format (`.container`, `.volume`, `.network`, `.pod`, `.kube` files). All file generation in the extension targets this format.
- [[podlet-js]] — JavaScript/TypeScript library for programmatic Quadlet file generation used as the core of this extension's generation pipeline.
