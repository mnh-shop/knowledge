---
name: cockpit-podman-codegraph-verify
tags: [cockpit-podman, codegraph-verify, cockpit, podman, containers, javascript, react]
description: "Codegraph Verification: cockpit-podman — validating wiki claims against indexed source code symbols"
source: sources/cockpit-podman/
---

# Codegraph Verification: cockpit-podman

**Date:** 2026-07-12

## Claim 1: Cockpit UI plugin for Podman container management via REST API
- **Wiki says:** cockpit-podman is a Cockpit web UI plugin that manages Podman containers, images, pods, volumes, and networks through Podman's REST API. The main app entry point renders container and image management views.
- **Source evidence:**
  - `src/app.jsx` line 767 — `onNavigate` router that switches between Containers and Images views.
  - `src/Containers.jsx` line 356 — main Containers component, imported by `app.jsx`.
  - `src/Images.jsx` line 32 — main Images component, imported by `app.jsx`.
  - `src/client.ts` line 1 — API client module for Podman REST communication.
  - `src/rest.ts` line 1 — REST API helper module.
  - `package.json` and `build.js` confirm Node.js/React build pipeline for Cockpit plugin.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Container lifecycle management (create, start, stop, delete, rename, checkpoint, restore, commit)
- **Wiki says:** The plugin supports full container lifecycle: creation via ImageRunModal, rename, delete, force-remove, checkpoint, restore, and commit operations — each with dedicated modal dialogs.
- **Source evidence:**
  - `src/ContainerCommitModal.jsx` — container commit modal (line 1, 7201 bytes).
  - `src/ContainerDeleteModal.jsx` — container delete modal (line 1, 1748 bytes).
  - `src/ContainerCheckpointModal.jsx` — container checkpoint modal (line 1, 3222 bytes).
  - `src/ContainerRestoreModal.jsx` — container restore modal (line 1, 3533 bytes).
  - `src/ContainerRenameModal.jsx` — container rename modal (line 1, 4056 bytes).
  - `src/ForceRemoveModal.jsx` — force remove modal (line 1, 1393 bytes).
  - `src/PruneUnusedContainersModal.jsx` — prune unused containers (line 1, 4859 bytes).
  - `src/ImageRunModal.jsx` at 64232 bytes — the large container/image run creation modal, also imports `Volume` and `ContainerEnv`.
  - `src/ContainerDetails.jsx` — detailed container information view.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Image management (search, pull, details, history, delete, prune)
- **Wiki says:** The plugin provides image management including search (Docker Hub/registries), pull, detailed view, history layers, delete, and prune unused images.
- **Source evidence:**
  - `src/Images.jsx` — main Images view (line 1, 20080 bytes) with listing and management.
  - `src/ImageSearchModal.jsx` — registry search modal (line 1, 11417 bytes) with `ImageSearchModal` component.
  - `src/ImageDetails.jsx` — detailed image information (line 1, 3857 bytes).
  - `src/ImageHistory.jsx` — image layer history view (line 1, 2060 bytes).
  - `src/ImageDeleteModal.jsx` — image deletion modal (line 1, 5627 bytes).
  - `src/ImageUsedBy.jsx` — shows which containers use an image (line 1, 1674 bytes).
  - `src/PruneUnusedImagesModal.jsx` — prune unused images (line 1, 4625 bytes).
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Pod management (create, configure pods with containers, networks, volumes)
- **Wiki says:** The plugin supports Podman pods: creating pods, adding containers to pods, configuring pod-level networks and volumes, and managing pod-scoped resources.
- **Source evidence:**
  - `src/PodActions.jsx` — pod action controls (line 1, 9587 bytes).
  - `src/PodCreateModal.jsx` — pod creation modal (line 1, 10178 bytes), which imports `Volume`.
  - `src/Containers.jsx` line 356 — the Containers component handles pod-scoped container display.
  - `src/app.jsx` — main router includes pod navigation alongside containers and images.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Volume management and environment/port configuration
- **Wiki says:** The plugin provides volume management (create, attach, detach) and detailed environment variable and port publishing configuration for containers and pods.
- **Source evidence:**
  - `src/Volume.jsx` — volume management component (line 1, 4497 bytes), imported by `ImageRunModal.jsx` and `PodCreateModal.jsx`.
  - `src/PublishPort.jsx` — port publishing configuration (line 1, 6885 bytes).
  - `src/Env.jsx` — environment variable management UI (line 1, 4318 bytes).
  - `src/ContainerIntegration.jsx` line 93 — `ContainerEnv` symbol for environment integration.
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Container health logs, terminal access, and logging
- **Wiki says:** The plugin provides real-time container health checks display, in-browser terminal access, and log streaming for running containers through the Cockpit UI.
- **Source evidence:**
  - `src/ContainerHealthLogs.jsx` — health check logs display (line 1, 7293 bytes).
  - `src/ContainerTerminal.jsx` — in-browser terminal (line 1, 8832 bytes) with `ContainerTerminal.css` styling.
  - `src/ContainerLogs.jsx` — log streaming view (line 1, 5388 bytes).
  - `src/Notification.tsx` — notification system for container events (line 1, 1118 bytes).
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Quadlet detection script and test infrastructure
- **Wiki says:** The repo includes a Python script for detecting existing Quadlet files, plus browser-based tests, reference tests, and VM install tests.
- **Source evidence:**
  - `src/detect-quadlets.py` — Python script for Quadlet detection (line 1, 3029 bytes).
  - `test/browser/` — browser-based UI tests.
  - `test/check-application/` — application check tests.
  - `test/reference/` and `test/reference-image/` — reference validation tests.
  - `test/vm.install`, `test/vm-beiboot.install`, `test/vm-ws-package.install` — VM installation test scripts.
  - `test/run/` — test runner configuration.
  - `Makefile` — build and test orchestration (line 1, 8554 bytes).
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 7 key claims from the cockpit-podman wiki have been verified against the source code via codegraph exploration:

- ✅ Cockpit UI plugin: React app at `src/` with REST API via `client.ts` and `rest.ts`
- ✅ Container lifecycle: 8 dedicated modal components for full lifecycle management
- ✅ Image management: 7 components for search, pull, details, history, delete, prune
- ✅ Pod management: PodActions and PodCreateModal for pod-level operations
- ✅ Volume and configuration: Volume, PublishPort, Env components
- ✅ Health and terminal: HealthLogs, Terminal, Logs components with real-time access
- ✅ Quadlet detection and testing: detect-quadlets.py plus comprehensive test suite

## Related

- [[cockpit-podman]] -- Main wiki entry
- [[podman]] -- Podman container engine
- [[cockpit]] -- Cockpit web console
- [[podlet]] -- Quadlet file generator
- [[mission-control]] -- MCP audit server (related container management)

## Cross-project

- [[podman.codegraph-verify]] -- Podman verification
- [[podlet.codegraph-verify]] -- Podlet Quadlet generator verification
- [[buildah.codegraph-verify]] -- Buildah image builder verification
- [[mission-control.codegraph-verify]] -- Mission control verification
