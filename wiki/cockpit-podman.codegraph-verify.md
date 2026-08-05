---
name: cockpit-podman-codegraph-verify
tags: [cockpit-podman, codegraph-verify, cockpit, podman, containers, javascript, react]
description: "Codegraph Verification: cockpit-podman — validating wiki claims against indexed source code symbols"
source: sources/cockpit-podman/
---

# Codegraph Verification: cockpit-podman

**Date:** 2026-07-30

## Claim 1: Cockpit UI plugin speaking Podman REST API v3.4.0 over Unix sockets
- **Wiki says:** cockpit-podman is a Cockpit web UI module that manages Podman containers, images, pods, and quadlets through Podman's REST API over Unix sockets (client.ts + rest.ts), versioned at `/v3.4.0/`.
- **Source evidence:**
  - `src/client.ts` line 7: `export const VERSION = "/v3.4.0/";`
  - `src/client.ts` line 19: `con.monitor(\`${VERSION}libpod/events\`, callback);` — endpoint table in the wiki matches `client.ts` lines 19-159 (events, stats, containers/*, pods/*, images/*, commit, exec, prune, resize, healthcheck)
  - `src/rest.ts` line 30: `const PODMAN_SYSTEM_ADDRESS = "/run/podman/podman.sock";`
  - `src/rest.ts` lines 35-49: three connection types — `$XDG_RUNTIME_DIR/podman/podman.sock` (uid=null, line 40), `/run/podman/podman.sock` with `superuser: "require"` (line 46), `/run/user/${uid}/podman/podman.sock` with `superuser: "require"` (line 49)
  - `src/app.jsx` — root Application component; `src/Containers.jsx` line 356, `src/Images.jsx` line 32
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Container lifecycle management (create, start, stop, delete, rename, checkpoint, restore, commit)
- **Wiki says:** Full container lifecycle via dedicated modal dialogs — ImageRunModal (create), rename, delete, force-remove, checkpoint, restore, commit.
- **Source evidence:**
  - `src/ContainerCommitModal.jsx` — commit modal (line 1, 7201 bytes)
  - `src/ContainerDeleteModal.jsx` — delete modal (line 1, 1748 bytes)
  - `src/ContainerCheckpointModal.jsx` — checkpoint modal (line 1, 3222 bytes)
  - `src/ContainerRestoreModal.jsx` — restore modal (line 1, 3533 bytes)
  - `src/ContainerRenameModal.jsx` — rename modal (line 1, 4056 bytes)
  - `src/ForceRemoveModal.jsx` — force-remove modal (line 1, 1393 bytes)
  - `src/PruneUnusedContainersModal.jsx` — prune unused containers (line 1, 4859 bytes)
  - `src/ImageRunModal.jsx` — create-container dialog (64232 bytes), imports `Volume` and `ContainerEnv`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Image management (search, pull, details, history, delete, prune)
- **Wiki says:** Image search/pull from registries, detailed view, layer history, delete, and prune-unused operations.
- **Source evidence:**
  - `src/Images.jsx` — main Images view (20080 bytes)
  - `src/ImageSearchModal.jsx` — registry search modal (11417 bytes)
  - `src/ImageDetails.jsx` — image details (3857 bytes); `src/ImageHistory.jsx` — layer history (2060 bytes)
  - `src/ImageDeleteModal.jsx` — deletion (5627 bytes); `src/ImageUsedBy.jsx` — dependent containers (1674 bytes)
  - `src/PruneUnusedImagesModal.jsx` — prune dialog (4625 bytes), **kept in the DOM** to stay in sync with reality: `src/Images.jsx` lines 337-345 render it inline rather than via `Dialogs.show`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Pod management (create, configure, lifecycle)
- **Wiki says:** Pod creation with ports/volumes plus start/stop/restart/pause/delete actions.
- **Source evidence:**
  - `src/PodActions.jsx` — pod lifecycle actions (9587 bytes)
  - `src/PodCreateModal.jsx` — pod creation (10178 bytes), imports `Volume`
  - `src/Containers.jsx` line 356 — pod-scoped container display
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Volume management, environment, and port publishing configuration
- **Wiki says:** Volume management plus environment variable and port publishing editors for containers and pods.
- **Source evidence:**
  - `src/Volume.jsx` — volume editor (4497 bytes), imported by `ImageRunModal.jsx` and `PodCreateModal.jsx`
  - `src/PublishPort.jsx` — port publishing (6885 bytes)
  - `src/Env.jsx` — environment variables (4318 bytes)
  - `src/ContainerIntegration.jsx` line 93 — `ContainerEnv` symbol
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Multi-user orchestration, cgroup scan, terminal, logs, and modal patterns
- **Wiki says:** Cross-user container discovery via cgroup scan, owner filtering, serialized event updates, xterm.js WebGL terminal, Dialogs.show-based modals, 500ms debounced validation.
- **Source evidence:**
  - `src/app.jsx` lines 706-708: `find /sys/fs/cgroup` for `libpod.*scope` / `podman-*.scope` (with `libpod-payload*`), resolving numeric owners
  - `src/app.jsx` line 82: `this.pendingUpdateContainer = {};` and lines 252-266: per-container promise chaining to serialize out-of-order events
  - `src/ContainerTerminal.jsx` line 165: `this.term.loadAddon(new WebglAddon());`
  - `src/Containers.jsx` line 70: `Dialogs.show(<ForceRemoveModal ...>` — Cockpit `Dialogs` API
  - `src/util.tsx` line 185: `export const validationDebounce = debounce(500, ...)`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Quadlet integration via systemd generator + D-Bus + systemctl lifecycle
- **Wiki says:** Quadlet `.container`/`.pod` detection from `/run/systemd/generator`, D-Bus `Reloading` subscription, and systemctl-driven lifecycle for quadlet units.
- **Source evidence:**
  - `src/detect-quadlets.py` — Python scanner for quadlet units (3029 bytes)
  - `src/app.jsx` line 462: `let path = "/run/systemd/generator";` (with `$XDG_RUNTIME_DIR/systemd/generator` fallback at line 466)
  - `src/app.jsx` line 580: `client.subscribe({ interface: "org.freedesktop.systemd1.Manager", member: "Reloading" }, ...)`
  - `src/app.jsx` line 628: `"systemctl", ...` — quadlet lifecycle goes through systemctl
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: PatternFly 6.6.0, esbuild + wasm fallback, quality gates, packaging, test infra
- **Wiki says:** PatternFly v6.6 design system; esbuild bundler with esbuild-wasm fallback; ruff/mypy/pyright/vulture/codespell quality gates; RPM/DEB/Arch packaging; browser/VM test infrastructure.
- **Source evidence:**
  - `package.json` lines 41-45: `@patternfly/patternfly`, `@patternfly/react-core`, `@patternfly/react-icons`, `@patternfly/react-styles`, `@patternfly/react-table`, `@patternfly/react-tokens` — all `6.6.0` (fixed from 6.5)
  - `build.js` line 22: `return (await import(useWasm ? 'esbuild-wasm' : 'esbuild')).default;` (with distro-package fallback at line 31); line 97: `const context = await esbuild.context({`; lines 105, 169: minify/metafile + `runtime-npm-modules.txt` dependency tracking
  - `pyproject.toml` — ruff, mypy, pyright, vulture (min confidence 80), codespell
  - `packaging/cockpit-podman.spec.in` (RPM), `packaging/debian/` (DEB), Arch PKGBUILD
  - `test/browser/`, `test/check-application/`, `test/reference/` + `test/reference-image/`, `test/vm.install`, `test/vm-beiboot.install`, `test/vm-ws-package.install`, `test/run/`
- **Verdict:** ✅ CORRECT (fixed: PatternFly 6.5 → 6.6.0)
- **Fix needed:** Version bumped in the wiki dependencies section.

## Summary

All 8 key claims from the cockpit-podman wiki have been verified against the source:
- ✅ REST API v3.4.0 over Unix sockets — client.ts:7, rest.ts:30,35-49
- ✅ Container lifecycle — 8 modal components
- ✅ Image management — 7 components incl. DOM-kept PruneUnusedImagesModal (Images.jsx:337-345)
- ✅ Pod management — PodActions, PodCreateModal
- ✅ Volume/env/port editors — Volume, Env, PublishPort
- ✅ Multi-user cgroup scan + WebGL terminal + 500ms validation — app.jsx:706-708, ContainerTerminal.jsx:165, util.tsx:185
- ✅ Quadlet integration — detect-quadlets.py, app.jsx:462,580,628
- ✅ PatternFly 6.6.0, esbuild/wasm, quality gates, packaging, tests — package.json:41-45, build.js:22,97,105,169

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
