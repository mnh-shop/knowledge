---
name: podman-codegraph-verify
tags: [cli, container, daemonless, golang, oci, podman, quadlet, rootless, storage, systemd, virtualization, wiki]
description: "Codegraph Verification: podman"
source: sources/podman/
---
# Codegraph Verification: podman

**Date:** 2026-06-24

## Claim 1: BecomeRootInUserNS() function exists and does what the wiki says
- **Wiki says:** When a non-root user runs `podman`, the Go runtime calls `BecomeRootInUserNS()` in `pkg/rootless/rootless_linux.go`. This:
  1. Re-executes the podman binary inside a new user namespace
  2. Maps the host user (UID `N`) to root (UID 0) inside the namespace
  3. Maps `N+1` through `N+65536` as subordinate UIDs inside the namespace
  4. Uses `/etc/subuid` and `/etc/subgid` for the subordinate ID range

- **Source evidence:** `pkg/rootless/rootless_linux.go:215` defines `BecomeRootInUserNS()`; the implementation re-execs the binary inside a new user namespace (`reexec_in_user_namespace` at `pkg/rootless/reexec_in_user_namespace.go:34-35` forks via `syscall_clone(CLONE_NEWUSER | CLONE_NEWNS | SIGCHLD)`; the child sets itself root with `setresgid(0,0,0)`/`setresuid(0,0,0)` at `rootless_linux.go:442-466`). UID/GID mapping uses the `newuidmap`/`newgidmap` setuid helpers reading `/etc/subuid` and `/etc/subgid` (`rootless_linux.go:91-118`). The function maps the host user to root inside the namespace and maps subordinate IDs.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Quadlet files for services placed in ~/.config/containers/systemd/ (plus search dirs)
- **Wiki says:** Quadlet runs Podman containers as systemd services using `.container`, `.volume`, `.network`, and `.pod` unit files placed in `~/.config/containers/systemd/`.

- **Source evidence:** `pkg/systemd/quadlet/unitdirs.go:24-41` — `GetInstallUnitDirPath(rootless)` returns `$XDG_CONFIG_HOME/containers/systemd` (`~/.config/containers/systemd/`) for rootless; `GetUnitDirs()` also searches `$XDG_RUNTIME_DIR/containers/systemd`, `/etc/containers/systemd/users/${UID}`, `/usr/share/containers/systemd/users/${UID}`, and the system locations `/usr/share/containers/systemd` + `/etc/containers/systemd`. Drop-in directories (`openclaw.container.d/`) are constructed in `pkg/systemd/parser/unitfile.go:968-970`.

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Podman secrets stored in graphroot/secrets
- **Wiki says:** Secrets are stored as encrypted files in `~/.local/share/containers/storage/secrets/`.

- **Source evidence:** `libpod/runtime.go:1177-1178` — `GetSecretsStorageDir()` returns `filepath.Join(r.store.GraphRoot(), "secrets")`. For rootless users the graphroot resolves to `$XDG_DATA_HOME/containers/storage` (`~/.local/share/containers/storage/secrets/`).

- **Verdict:** ✅ CORRECT (exact path is `$graphroot/secrets`, which resolves to the location mentioned)
- **Fix needed:** None

## Claim 4: Podman Machine uses vfkit (Apple Virtualization.framework) + gvproxy + virtiofs
- **Wiki says:** Podman Machine creates a Linux VM on macOS via **vfkit** (Apple Virtualization.framework), with gvproxy networking and virtiofs file sharing; rootful mode via `podman machine set --rootful`.

- **Source evidence:**
  - `pkg/machine/apple/vfkit/rest.go`, `helper.go` — vfkit provider implementing the machine provider interface; `pkg/machine/apple/apple.go` defines `applehvMACAddress`
  - `pkg/machine/shim/gvproxy.go` — gvproxy networking between host and VM
  - `pkg/machine/vmconfigs/config.go:6,18` and `volumes.go:21` — virtiofs file sharing
  - `pkg/machine/shim/set.go:47-48` — `--rootful` option on `podman machine set`

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Networking — pasta is the rootless default; slirp4netns REMOVED in v6
- **Wiki says:** pasta is the default rootless networking mode; slirp4netns is not "an older, widely tested default" — in v6 its support is removed.

- **Source evidence:**
  - `libpod/networking_linux.go:33-34` — `"slirp4netns support has been removed, run `podman system migrate` to update this container to use pasta"` (hard error for containers still configured with slirp4netns)
  - `libpod/networking_linux.go:36-37` — `ctr.config.NetMode.IsPasta()` → `r.setupPasta(...)`; setup delegated via `libpod/networking_pasta_linux.go` to `pasta.Setup()` in the vendored `go.podman.io/common/libnetwork/pasta/pasta_linux.go`
  - `rootless.md:13-14` — "As of Podman 5.0, pasta is the default networking tool"
  - Rootless bridge networks use `rootlessport` (`libpod/networking_rootlessport.go`), a userspace proxy that binds in the host network namespace

- **Verdict:** ⚠️ PARTIALLY CORRECT (wiki previously framed slirp4netns as "older default, widely tested" — corrected to "removed in v6")
- **Fix needed:** Applied — networking table rewritten; port-binding claim corrected (rootless restriction is ports < 1024, `rootless.md:5-7`; `-p 0.0.0.0:x:y` works via rootlessport in the host netns); rootless `--network=host` noted as supported (`podman-run.1.md.in:957`)

## Claim 6: 3-layer architecture: libpod → domain/infra → CLI
- **Wiki says:** Podman has a 3-layer architecture: libpod → domain/infra → CLI.

- **Source evidence:** The layered structure is confirmed in code:
  - **CLI Layer**: `cmd/podman/` — Cobra command parsing and dispatch (`cmd/podman/system/service.go:27-34` — `podman system service` runs the REST API server, confirming the daemonless API model)
  - **Domain/Infra Layer**: `pkg/domain/infra/` — engine factory with ABI (`abi/`, `runtime_abi.go`) and Tunnel (`tunnel/`, `runtime_tunnel.go`) engines over the REST API, plus `runtime_libpod.go` for direct libpod
  - **libpod Layer**: `libpod/` — container lifecycle, OCI runtime integration via `conmon` (`libpod/runtime.go:79,330-335`), networking, storage

- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Quadlet uses Pull= (not PullPolicy=) and supports .kube/.image/.build/.artifact units
- **Wiki says:** Quadlet example uses `PullPolicy=newer`; unit types are `.container`, `.volume`, `.network`, `.pod`.

- **Source evidence:**
  - `pkg/systemd/quadlet/quadlet.go:151` — `KeyPull = "Pull"`; `quadlet.go:701` — `KeyPull: "--pull"` maps the key to the podman `--pull` flag
  - `docs/source/markdown/podman-systemd.unit.5.md:405` — `| Pull=never | --pull never |` (no `PullPolicy=` key exists)
  - `quadlet.go:1532-1546` — service-name resolution handles `.container`, `.volume`, `.kube`, `.network`, `.image`, `.build`, `.artifact`, `.pod` suffixes
  - Quadlet keys `UserNS`/`Notify`/`Secret`/`RunInit`/`HealthCmd`/`Volume`/`User`/`PublishPort` defined at `quadlet.go:103-196`; `Secret=` injection as env or file per `podman-systemd.unit.5.md:926-929`

- **Verdict:** ❌ INCORRECT (before fix)
- **Fix needed:** Applied — example now uses `Pull=newer`; unit-type list expanded to include `.kube`, `.image`, `.build`, `.artifact`

## Summary

Key claims from the podman wiki verified against source:
- ✅ **Rootless re-exec:** `BecomeRootInUserNS` at `rootless_linux.go:215` with newuidmap/newgidmap + `/etc/subuid|subgid`
- ✅ **Quadlet dirs:** `unitdirs.go:24-41` search paths + `unitfile.go:968-970` drop-ins
- ✅ **Secrets:** `runtime.go:1177-1178` `$graphroot/secrets`
- ✅ **Machine:** vfkit + gvproxy + virtiofs + `--rootful`
- ✅ **Networking:** pasta default; slirp4netns **removed** in v6 (`networking_linux.go:33-34`)
- ✅ **3-layer arch:** `pkg/domain/infra/{abi,tunnel,runtime_abi,runtime_tunnel,runtime_libpod}.go`
- ✅ **Quadlet keys:** `Pull=` at `quadlet.go:151,701`; 8 unit types at `quadlet.go:1532-1546`

## Related

- [[podman]] -- Main wiki entry with overview and architecture
- [[podman-architecture]] -- Deep-dive into architecture
- [[podman-deployment]] -- Deployment guide with Quadlet lifecycle
- [[podman-quadlet-examples]] -- Production Quadlet file collection
- [[hermes-profiles]] -- Quick-reference profile card

## Cross-project

- [[agentfield.codegraph-verify]] -- Similar codegraph verification for AgentField
- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
